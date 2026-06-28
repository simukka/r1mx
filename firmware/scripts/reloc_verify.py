#!/usr/bin/env python3
"""
reloc_verify.py — shared, transport-agnostic preflight that confirms the .text
relocation (`D_text`) a script is about to use against the LIVE camera, so a
wrong --reloc fails loudly instead of producing garbage (mis-resolved PCs,
breakpoints that never fire, watchpoints on the wrong address).

WHY A CLASS
-----------
Every script that maps live PCs <-> image offsets (upgrade_observe, task_walker,
upgrade_bypass_test, lockstep_diff, camera_probe) hardcodes / passes a reloc and
silently trusts it. RelocVerifier centralises the check so each can do, in
preflight:

    from reloc_verify import RelocVerifier, RelocError
    rv = RelocVerifier.from_rsp(rsp, manifest=MANIFEST, image=IMAGE)
    rv.assert_reloc(args.reloc)        # raises RelocError if it doesn't hold up

HOW IT VERIFIES (two independent signals, strongest first)
----------------------------------------------------------
It halts ONCE and takes a snapshot: the register set, plus candidate CODE
addresses (pc/lr/ctr and return addresses found on the stack) with a few words
read at each. Then, for a candidate reloc, with no further I/O:

  1. BYTE FINGERPRINT (conclusive): for any candidate code window that happened
     to be D-mappable (read back real bytes — not all-0/filler), check
     image[addr - reloc : ...] == the live bytes. One match proves the reloc.
     NOTE: on a healthy *idle* camera .text is usually I-side-only, so these
     windows often read as 0 and this signal is simply absent (not a failure) —
     see working-camera-reloc.

  2. SYMBOL RESOLUTION (corroborating): map each candidate through manifest.csv
     (FuncTable). With the correct reloc, candidates land cleanly inside known
     functions; a grossly wrong reloc scatters them into gaps / off the map.
     Weaker than the byte check (a dense manifest can absorb a wrong constant),
     so it requires several agreeing candidates.

`ok` = byte_confirmed OR (enough symbol hits). The authoritative *derivation*
(when you don't yet have a reloc) is still camera_probe.py --phases reloc; this
class VERIFIES a candidate and can pick the best of a small known set.

SAFETY: read-only — only halt/regs/mem reads + (optional) resume. No writes.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from task_walker import FuncTable  # noqa: E402  shared PC->function resolver

# Relocations seen in the wild (cam-working-01=0x10180, broken bench unit=0x10040,
# base-0). search() tries these by default; always re-derive for a new camera.
KNOWN_RELOCS = (0x10180, 0x10040, 0x0)

# Plausible .text address span (matches camera_probe's fingerprint bounds).
CODE_LO, CODE_HI = 0x1000, 0x00E00000


class RelocError(RuntimeError):
    """Raised by assert_reloc when the candidate reloc does not hold up."""


def _is_call(w: int) -> bool:
    """True if the 32-bit PPC word is a linking branch (a CALL) — i.e. the kind
    of instruction that precedes a valid return address. Covers bl/bla (op18),
    bcl/bcla (op16) and bclrl/bcctrl (op19 XL-form), all with LK=1."""
    op = w >> 26
    if op in (16, 18) and (w & 1):
        return True
    if op == 19 and (w & 1) and ((w >> 1) & 0x3ff) in (16, 528):
        return True
    return False


@dataclass
class RelocResult:
    reloc: int
    ok: bool
    byte_confirmed: bool
    call_hits: int            # return addrs landing right after a CALL in the image
    return_cands: int         # how many candidates are return addresses (lr/stack)
    symbol_hits: int
    candidates: int
    pc: int
    pc_func: str | None
    evidence: list[str] = field(default_factory=list)
    note: str = ""

    def __str__(self):
        if self.byte_confirmed:
            verdict = "CONFIRMED (byte fingerprint)"
        elif self.ok and self.call_hits:
            verdict = f"CONFIRMED ({self.call_hits}/{self.return_cands} return addrs post-call)"
        elif self.ok:
            verdict = "plausible (symbols only)"
        else:
            verdict = "REJECTED"
        s = (f"reloc 0x{self.reloc:08x}: {verdict} — "
             f"pc=0x{self.pc:08x} -> {self.pc_func or '?'}; "
             f"{self.symbol_hits}/{self.candidates} resolve, "
             f"{self.call_hits}/{self.return_cands} post-call")
        if self.note:
            s += f"  [{self.note}]"
        return s


@dataclass
class _Snapshot:
    regs: dict
    # (label, live_addr, bytes|None) — bytes is a few words read at the address,
    # or None if it wasn't D-mappable (so the byte fingerprint just skips it).
    candidates: list[tuple[str, int, bytes | None]]


class RelocVerifier:
    def __init__(self, func_table: FuncTable, *, read_regs, read_word,
                 read_block=None, halt=None, resume=None,
                 code_lo=CODE_LO, code_hi=CODE_HI, stack_words=48,
                 window_words=8, max_candidates=24):
        self.ft = func_table
        self._read_regs = read_regs
        self._read_word = read_word
        self._read_block = read_block
        self._halt = halt
        self._resume = resume
        self.code_lo, self.code_hi = code_lo, code_hi
        self.stack_words = stack_words
        self.window_words = window_words
        self.max_candidates = max_candidates

    # ----- adapters -------------------------------------------------------
    @classmethod
    def from_rsp(cls, rsp, func_table: FuncTable | None = None, *,
                 manifest=None, image=None, halt_timeout=10.0, **kw):
        """Build from an rsp.RSP client (XMD stub or QEMU). read_word raises on
        failure, so wrap to None; resume via continue."""
        from rsp import RSPError
        ft = func_table or _load_ft(manifest, image)

        def rword(a):
            try:
                return rsp.read_word(a)
            except (RSPError, ValueError):
                return None

        def rblock(a, n):
            try:
                return rsp.read_mem(a, n)
            except (RSPError, ValueError):
                return None

        return cls(ft, read_regs=rsp.regs, read_word=rword, read_block=rblock,
                   halt=lambda: rsp.interrupt(halt_timeout),
                   resume=lambda: rsp.send("c"), **kw)

    @classmethod
    def from_camera(cls, cam, func_table: FuncTable | None = None, *,
                    manifest=None, image=None, **kw):
        """Build from a camera_probe.Camera (xmd_rpc / Channel B). Reads are done
        while already halted to avoid the per-call stop/con resuming mid-snapshot."""
        ft = func_table or _load_ft(manifest, image)

        def rblock(a, n):
            words = cam.read_words(a, (n + 3) // 4, halted=True)
            if not words:
                return None
            return b"".join(v.to_bytes(4, "big") for _, v in words)[:n]

        return cls(ft, read_regs=cam.regs,
                   read_word=lambda a: cam.read_word(a, halted=True),
                   read_block=rblock, halt=cam.halt, resume=cam.resume, **kw)

    # ----- snapshot (the only I/O) ----------------------------------------
    def snapshot(self) -> _Snapshot:
        """Halt once, gather regs + candidate code windows, resume. Reused across
        any number of candidate relocs by evaluate()."""
        if self._halt:
            self._halt()
        try:
            regs = self._read_regs() or {}
            cand_addrs: list[tuple[str, int]] = []
            for rn in ("pc", "lr", "ctr"):
                v = regs.get(rn, 0) & 0xFFFFFFFF
                if self.code_lo <= v < self.code_hi:
                    cand_addrs.append((rn, v & ~3))
            sp = regs.get("r1", 0) & 0xFFFFFFFF
            stack = self._read_stack(sp, self.stack_words) if sp else []
            for i, v in enumerate(stack):
                if self.code_lo <= v < self.code_hi and v % 4 == 0:
                    cand_addrs.append((f"stack+0x{i*4:x}", v & ~3))
            # de-dup by address, cap count
            seen, uniq = set(), []
            for label, a in cand_addrs:
                if a in seen:
                    continue
                seen.add(a)
                uniq.append((label, a))
                if len(uniq) >= self.max_candidates:
                    break
            cands = [(label, a, self._read_window(a)) for label, a in uniq]
            return _Snapshot(regs=regs, candidates=cands)
        finally:
            if self._resume:
                self._resume()

    def _read_stack(self, sp: int, nwords: int) -> list[int]:
        if self._read_block:
            blk = self._read_block(sp, nwords * 4)
            if blk:
                return [int.from_bytes(blk[i:i + 4], "big")
                        for i in range(0, len(blk) - len(blk) % 4, 4)]
            return []
        out = []
        for i in range(nwords):
            w = self._read_word(sp + i * 4)
            if w is None:
                break
            out.append(w & 0xFFFFFFFF)
        return out

    def _read_window(self, addr: int) -> bytes | None:
        """Read window_words at addr; None if not D-mappable or all-same filler."""
        n = self.window_words * 4
        blk = self._read_block(addr, n) if self._read_block else None
        if blk is None:
            words = []
            for i in range(self.window_words):
                w = self._read_word(addr + i * 4)
                if w is None:
                    return None
                words.append(w & 0xFFFFFFFF)
            blk = b"".join(w.to_bytes(4, "big") for w in words)
        if len(blk) < 4:
            return None
        first = blk[:4]
        if all(blk[i:i + 4] == first for i in range(0, len(blk) - 3, 4)):
            return None                      # repeated word == bus residue / 0
        return blk

    # ----- evaluation (pure; no I/O) --------------------------------------
    def evaluate(self, snap: _Snapshot, reloc: int, *,
                 min_hits=2, require_pc=False) -> RelocResult:
        img = getattr(self.ft, "img", None)
        hits, call_hits, ret_cands, evidence = 0, 0, 0, []
        byte_confirmed = False
        for label, addr, win in snap.candidates:
            off = (addr - reloc) & 0xFFFFFFFF
            fn = self.ft.resolve(off)
            resolved = fn is not None and not fn.get("in_gap")
            in_img = img is not None and 0 <= off <= len(img)
            # strong signal #1: live bytes equal the image at this offset
            if win is not None and in_img and off <= len(img) - len(win):
                if img[off:off + len(win)] == win:
                    byte_confirmed = True
                    evidence.append(f"BYTE {label} live 0x{addr:08x} == "
                                    f"img 0x{off:08x} ({len(win)}B)")
                    hits += 1
                    continue
            # strong signal #2: a RETURN address must sit right after a CALL in
            # the static image. Only lr/stack candidates are return addresses
            # (pc is the live PC, ctr is a call target — neither is a return).
            is_ret = label == "lr" or label.startswith("stack")
            if is_ret:
                ret_cands += 1
                if in_img and 4 <= off <= len(img):
                    prev = int.from_bytes(img[off - 4:off], "big")
                    if _is_call(prev):
                        call_hits += 1
                        evidence.append(f"CALL {label} 0x{addr:08x} -> img "
                                        f"0x{off:08x} (after call @0x{off-4:08x})")
            if resolved:
                hits += 1
        pc = snap.regs.get("pc", 0) & 0xFFFFFFFF
        pc_off = (pc - reloc) & 0xFFFFFFFF
        pc_fn = self.ft.resolve(pc_off)
        pc_func = (f"{pc_fn['name']}+0x{pc_fn['off']:x}"
                   + ("(gap)" if pc_fn.get("in_gap") else "")) if pc_fn else None
        pc_ok = pc_fn is not None and not pc_fn.get("in_gap")

        # Confidence tiers:
        #   byte fingerprint  -> conclusive
        #   post-call returns -> strong (image-only; survives I-side-only .text).
        #     A wrong (constant-shifted) reloc lands returns mid-instruction, so a
        #     CALL at off-4 is rare; require a majority (>=2 and >=half) to pass.
        #   symbols only      -> weak fallback ONLY when there are no return
        #     candidates to test (a dense manifest resolves almost any reloc).
        call_ok = ret_cands > 0 and call_hits >= max(2, (ret_cands + 1) // 2)
        if byte_confirmed or call_ok:
            ok = True
        elif ret_cands > 0:
            ok = False                       # had returns to test, none agreed
        else:
            ok = hits >= min_hits and (pc_ok or not require_pc)

        note = ""
        if not snap.candidates:
            note = "no code candidates (idle/unmapped context — retry under load)"
        elif byte_confirmed:
            pass
        elif call_ok:
            note = "image-only (no D-mappable .text window — normal at idle)"
        elif ret_cands > 0:
            note = f"returns do NOT sit after calls ({call_hits}/{ret_cands}) — wrong reloc"
        else:
            note = "symbols only, no return addrs to test — low confidence"
        return RelocResult(reloc=reloc, ok=ok, byte_confirmed=byte_confirmed,
                           call_hits=call_hits, return_cands=ret_cands,
                           symbol_hits=hits, candidates=len(snap.candidates),
                           pc=pc, pc_func=pc_func, evidence=evidence, note=note)

    # ----- public API -----------------------------------------------------
    def verify(self, reloc: int, *, min_hits=2, require_pc=False) -> RelocResult:
        return self.evaluate(self.snapshot(), reloc,
                             min_hits=min_hits, require_pc=require_pc)

    def search(self, relocs=KNOWN_RELOCS, *, min_hits=2) -> RelocResult:
        """Take one snapshot, score each candidate reloc, return the best
        (byte-confirmed beats symbol hits beats higher count)."""
        snap = self.snapshot()
        results = [self.evaluate(snap, r, min_hits=min_hits) for r in relocs]
        return max(results, key=lambda r: (r.byte_confirmed, r.call_hits,
                                           r.ok, r.symbol_hits))

    def assert_reloc(self, reloc: int, *, min_hits=2, require_pc=False,
                     verbose=True) -> RelocResult:
        """Verify and raise RelocError if it doesn't hold up. Returns the result
        on success. Use as a one-liner preflight gate."""
        res = self.verify(reloc, min_hits=min_hits, require_pc=require_pc)
        if verbose:
            print(f"  [reloc] {res}")
            for e in res.evidence[:4]:
                print(f"          {e}")
        if not res.ok:
            hint = (" Try `reloc_verify.py` (searches known relocs) or "
                    "`camera_probe.py --phases reloc` to derive it.")
            raise RelocError(
                f"reloc 0x{reloc:08x} not verified on the live target "
                f"({res.call_hits}/{res.return_cands} return addrs post-call, "
                f"{res.symbol_hits}/{res.candidates} resolve, "
                f"byte_confirmed={res.byte_confirmed}).{hint}")
        return res


def _load_ft(manifest, image) -> FuncTable:
    if manifest is None:
        manifest = _HERE.parent / "reverse/build_32/src/manifest.csv"
    if image is None:
        image = _HERE.parent / "reverse/build_32/extracted/software.bin"
    return FuncTable(Path(manifest), Path(image) if image else None)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Verify (or search for) the live .text reloc over the XMD "
                    "GDB stub. Read-only.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345)
    ap.add_argument("--reloc", type=lambda s: int(s, 0), default=None,
                    help="verify this reloc; omit to search KNOWN_RELOCS")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--image", default=None)
    ap.add_argument("--min-hits", type=int, default=2)
    args = ap.parse_args()

    from rsp import RSP
    try:
        rsp = RSP(args.host, args.port, allow_write=False, timeout=15.0,
                  label="xmd-hw").connect()
    except OSError as e:
        sys.exit(f"[FAIL] cannot reach {args.host}:{args.port} ({e})")
    rv = RelocVerifier.from_rsp(rsp, manifest=args.manifest, image=args.image)
    try:
        if args.reloc is not None:
            res = rv.verify(args.reloc, min_hits=args.min_hits)
            print(res)
            for e in res.evidence:
                print("   ", e)
            rc = 0 if res.ok else 1
        else:
            print("[*] searching known relocs:",
                  ", ".join(hex(r) for r in KNOWN_RELOCS))
            res = rv.search(min_hits=args.min_hits)
            print("[best]", res)
            for e in res.evidence:
                print("   ", e)
            rc = 0 if res.ok else 1
    finally:
        try:
            rsp.detach()
        except Exception:
            pass
        rsp.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
