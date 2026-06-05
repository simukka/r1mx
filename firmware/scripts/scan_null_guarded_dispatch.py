#!/usr/bin/env python3
"""scan_null_guarded_dispatch.py -- find NULL-guarded indirect calls through .data slots.

Background (see re_reference / cold-boot-first-divergence memory):
The unmodified Build 32 firmware crashes early in usrInit because NULL-guarded
function-pointer / vtable slots in .data (`if (ptr) call ptr`) hold non-zero STALE
values instead of 0. At a clean cold boot these slots are 0, the firmware's own guard
skips the call, and the real values are installed later by lazy init in usrRoot. Our
image's .data is non-cold, so the guards fire and dispatch through a bad pointer -> halt.

This scanner enumerates, across the code region, every indirect call (`bctrl`/`bctr`)
whose CTR source traces back to a fixed .data address (via `lis(+ori/addi); lwz`, and the
two-level `lwz base,glob; lwz method,off(base)` vtable form). For each it reports:
  - the call site,
  - the .data slot address the pointer came from,
  - the slot's current value in the file,
  - whether the call is NULL-guarded (a `beq`/`bne` on the pointer precedes the bctrl),
  - whether the resolved target looks like code, a string, or out-of-range.

SUSPECTS = guarded AND slot value != 0 AND target does NOT look like a normal function.
Those are the cold-boot slots that should read 0 but don't -- the generalization of
firmware patches #4/#6/#7/#8/#9 (+#13-#20 cascade).

Usage:
    .venv/bin/python firmware/scripts/scan_null_guarded_dispatch.py \
        [--bin reverse/build_32/extracted/software.bin] \
        [--code-end 0x600000] [--all]
"""
import argparse, struct, sys
from pathlib import Path

def signext16(x): return x - 0x10000 if x & 0x8000 else x

def main():
    here = Path(__file__).resolve().parent
    repo = here.parent  # firmware/
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", default=str(repo / "reverse/build_32/extracted/software.bin"))
    ap.add_argument("--code-end", default="0x600000",
                    help="scan call sites only below this VA (code region); slots resolved anywhere")
    ap.add_argument("--window", type=int, default=12,
                    help="max instrs of provenance/guard lookback")
    ap.add_argument("--all", action="store_true", help="print every traced dispatch, not just suspects")
    ap.add_argument("--slots-only", action="store_true",
                    help="print only the space-separated hex suspect slots (for scripting)")
    args = ap.parse_args()

    data = Path(args.bin).read_bytes()
    n = len(data)
    code_end = int(args.code_end, 0)
    W = args.window

    def word(a):
        if a < 0 or a + 4 > n: return None
        return struct.unpack(">I", data[a:a+4])[0]

    def looks_like_code(a):
        """Heuristic: does VA `a` look like a function entry / valid code?"""
        w = word(a)
        if w is None: return False
        op = w >> 26
        # common prologues / valid first ops: stwu r1 (0x9421....), mflr (0x7c0802a6),
        # mr/li/addi/or/branch — basically a sane opcode, not 0x00000000 / not printable.
        if w == 0: return False
        # NB: do NOT reject on 4-byte printable ASCII -- many valid PPC instrs encode as
        # printable bytes (e.g. addi 0x38692B78 = "8i+x"). String detection is handled
        # separately in describe_target over a longer run.
        # 19 = bclr/bctr/blr (xl-form), 17 = sc, 18 = b; accept the common valid opcodes
        return op in (14,15,16,17,18,19,31,32,33,34,36,37,38,40,44,11,10,7,8,
                      12,13,24,25,26,27,28,29,21,23,20)

    def describe_target(val):
        if val is None or val == 0: return "NULL"
        if val >= n: return "OOB(>file)"
        # exception/reset vector region: decodes as instructions but calling it resets the CPU
        if val < 0x2000: return "VECTOR(reset/exc 0x%X)" % val
        # code region: a pointer here is plausibly a real (or stale-but-codeish) fn ptr
        if val < code_end:
            return "code" if looks_like_code(val) else "data?(0x%08X)" % word(val)
        # data/rodata region: a callable pointer here is wrong. printable => string.
        bs = data[val:val+16]
        run = 0
        for c in bs:
            if 32 <= c < 127: run += 1
            else: break
        if run >= 4:
            z = bs.find(b"\0"); return "STRING %r" % bs[:z if z >= 0 else 8]
        return "data(0x%08X)" % word(val)

    nwords = code_end // 4
    words = struct.unpack(">%dI" % nwords, data[:nwords*4])

    # register provenance: reg -> dict(kind, val, src(addr-of-slot or None), idx)
    reg = {}
    def inval(r): reg.pop(r, None)
    guard_idx = {}      # reg -> instr idx of a cmp-vs-0 / record-form result on it
    beq_idx = -10**9    # idx of most recent beq/bne (conditional eq/ne branch)

    results = []

    for i in range(nwords):
        w = words[i]
        op = w >> 26
        rD = (w >> 21) & 31; rA = (w >> 16) & 31; rB = (w >> 11) & 31
        disp = w & 0xffff

        # ---- conditional branch eq/ne (the NULL guard branch) ----
        if op == 16:
            bo = (w >> 21) & 31; bi = (w >> 16) & 31
            # branch-if-true/false on CR0[EQ] (bi==2): beq=12, bne=4
            if bi == 2 and bo in (12, 4):
                beq_idx = i

        # ---- address / value provenance ----
        if op == 15:  # addis (lis when rA==0)
            if rA == 0:
                reg[rD] = dict(kind="imm", val=(disp << 16), src=None, idx=i)
            elif rA in reg and reg[rA]["kind"] == "imm" and i - reg[rA]["idx"] <= W:
                reg[rD] = dict(kind="imm", val=reg[rA]["val"] + (disp << 16), src=None, idx=i)
            else:
                inval(rD)
            continue
        if op == 14:  # addi (rA==0 => li)
            if rA == 0:
                reg[rD] = dict(kind="imm", val=signext16(disp), src=None, idx=i)
            elif rA in reg and reg[rA]["kind"] == "imm" and i - reg[rA]["idx"] <= W:
                reg[rD] = dict(kind="imm", val=(reg[rA]["val"] + signext16(disp)) & 0xffffffff, src=None, idx=i)
            else:
                inval(rD)
            continue
        if op == 24:  # ori
            if rA in reg and reg[rA]["kind"] == "imm" and i - reg[rA]["idx"] <= W:
                reg[rD] = dict(kind="imm", val=reg[rA]["val"] | disp, src=None, idx=i)
            else:
                inval(rD)
            continue
        if op == 32:  # lwz rD, disp(rA)  -- load a pointer from memory
            # require a lis-based (>=0x10000) base so we only track real global slots,
            # not li-based small immediates (which produce bogus near-zero "slots").
            if (rA in reg and reg[rA]["kind"] == "imm" and i - reg[rA]["idx"] <= W
                    and reg[rA]["val"] >= 0x10000):
                slot = (reg[rA]["val"] + signext16(disp)) & 0xffffffff
                val = word(slot)
                reg[rD] = dict(kind="loaded", val=val, src=slot, idx=i)
            else:
                inval(rD)
            continue

        # record-form result (mr./or./and./addic.) => sets CR0 vs 0 (a guard candidate)
        if op == 31:
            xo = (w >> 1) & 0x3ff; rc = w & 1
            if rc:
                guard_idx[rD] = i
            # mr rD,rS = or rD,rS,rS (xo 444)
            if xo == 444 and rA == rB:
                src = reg.get(rA)
                if src and i - src["idx"] <= W:
                    reg[rD] = dict(src, idx=i)
                else:
                    inval(rD)
            elif xo == 467:  # mtspr (covers mtctr): handled below via raw match
                pass
            else:
                inval(rD)
            # fallthrough to mtctr/bctr detection below
        elif op in (11, 10):  # cmpi(11)/cmpli(10) crfD,rA,imm
            imm = signext16(disp) if op == 11 else disp
            if imm == 0:
                guard_idx[rA] = i
            continue
        elif op not in (15, 14, 24, 32, 16, 19):
            # any other op writing rD: be conservative, invalidate rD
            if op in (7, 8, 12, 13, 28, 29, 20, 21, 23, 25, 26, 27):
                inval(rD)

        # ---- mtctr (mtspr 9) ----
        if op == 31 and ((w >> 1) & 0x3ff) == 467:
            spr = ((w >> 16) & 0x1f) | (((w >> 11) & 0x1f) << 5)
            if spr == 9:  # CTR
                reg["CTR"] = reg.get((w >> 21) & 31) and dict(reg[(w >> 21) & 31]) or None
                if reg.get("CTR"):
                    reg["CTR"]["from_reg"] = (w >> 21) & 31
                    reg["CTR"]["idx"] = i

        # ---- bctrl (4e800421) / bctr (4e800420) ----
        if w in (0x4e800421, 0x4e800420):
            ctr = reg.get("CTR")
            if ctr and ctr.get("src") is not None and i - ctr["idx"] <= W + 3:
                slot = ctr["src"]; val = ctr["val"]
                fr = ctr.get("from_reg")
                guarded = False
                # guard if the ctr-source reg (or its base) was compared-vs-0 with a beq nearby
                if fr is not None and fr in guard_idx and guard_idx[fr] <= i and i - guard_idx[fr] <= W:
                    guarded = beq_idx >= guard_idx[fr]
                # also accept a generic beq in the window (author skips the whole block)
                if not guarded and 0 <= i - beq_idx <= W:
                    guarded = True
                results.append(dict(site=i*4, slot=slot, val=val,
                                    guarded=guarded, tgt=describe_target(val)))
            continue

    # ---- writer cross-reference: which slots are stw'd somewhere (lazy-init) ----
    # store ops: stw(36) stwu(37) stb(38) sth(44) -- effective addr via lis-based base
    writers = {}
    reg2 = {}
    for i in range(nwords):
        w = words[i]; op = w >> 26; rD = (w>>21)&31; rA = (w>>16)&31; disp = w & 0xffff
        if op == 15 and rA == 0:
            reg2[rD] = (disp<<16, i)
        elif op == 15 and rA in reg2 and i-reg2[rA][1] <= W:
            reg2[rD] = (reg2[rA][0]+(disp<<16), i)
        elif op == 24 and rA in reg2 and i-reg2[rA][1] <= W:
            reg2[rD] = (reg2[rA][0]|disp, i)
        elif op == 14 and rA == 0:
            reg2[rD] = (signext16(disp), i)
        elif op == 14 and rA in reg2 and i-reg2[rA][1] <= W:   # addi rD,rA,imm (lis+addi base)
            reg2[rD] = ((reg2[rA][0]+signext16(disp)) & 0xffffffff, i)
        elif op in (36,37,38,44) and rA in reg2 and i-reg2[rA][1] <= W and reg2[rA][0] >= 0x10000:
            ea = (reg2[rA][0]+signext16(disp)) & 0xffffffff
            writers.setdefault(ea, []).append(i*4)
            if op != 38 and op != 44: reg2.pop(rD, None)
        else:
            if op in (7,8,12,13,28,29,20,21,23,25,26,27,31,32,33,34,40):
                reg2.pop(rD, None)

    def rank(r):
        t = r["tgt"]
        if t.startswith("STRING"): return 0      # definitely-wrong: ptr into a string
        if t.startswith("OOB"):    return 1      # pointer outside the image
        if t.startswith("data"):   return 2      # points into data, or code-region non-code
        return 3
    # ---- report ----
    DATA_LO = 0xC00000  # ignore sub-code "slots" (provenance noise); real globals are >=0xC00000
    for r in results:
        r["nwrite"] = len(writers.get(r["slot"], []))
    def is_suspect(r):
        if not (r["guarded"] and r["val"] not in (None, 0) and r["slot"] >= DATA_LO):
            return False
        # wrong target (string/OOB/vector/data) => definitely should be 0 at cold boot.
        if not r["tgt"].startswith("code"):
            return True
        # target looks like code, BUT a runtime writer (lazy init) exists => the slot is
        # populated later; at cold boot it must be 0 (its current code ptr is stale).
        return r["nwrite"] > 0
    suspects = [r for r in results if is_suspect(r)]
    rows = [r for r in results if r["slot"] >= DATA_LO] if args.all else suspects

    if args.slots_only:
        print(" ".join("0x%08X" % s for s in sorted(set(r["slot"] for r in suspects))))
        return

    print("# NULL-guarded indirect-call dispatch through fixed .data slots")
    print("# binary: %s (0x%X bytes), code scan < 0x%X" % (args.bin, n, code_end))
    print("# total traced dispatches: %d   suspects (guarded, slot!=0, target!=code): %d"
          % (len(results), len(suspects)))
    print()
    hdr = "%-10s  %-10s  %-10s  %-6s  %s" % ("call_site", "data_slot", "slot_val", "writes", "target")
    print(hdr); print("-"*max(len(hdr),64))
    for r in sorted(rows, key=lambda r: (rank(r), r["slot"])):
        print("0x%08X  0x%08X  0x%08X  %-6d  %s"
              % (r["site"], r["slot"], r["val"] or 0, r["nwrite"], r["tgt"]))

    # unique slots among suspects (the cold-boot zero set)
    if suspects:
        slots = sorted(set(r["slot"] for r in suspects))
        print("\n# unique suspect .data slots (%d) -- candidate cold-boot zero set:" % len(slots))
        print(" ".join("0x%08X" % s for s in slots))
        nowriter = sorted(s for s in slots if not writers.get(s))
        haswriter = sorted(s for s in slots if writers.get(s))
        print("\n# of those, %d have a runtime writer (lazy-init slot):" % len(haswriter))
        print(" ".join("0x%08X" % s for s in haswriter))
        print("# and %d have NO writer (pure const-that-should-be-0 / stale .data):" % len(nowriter))
        print(" ".join("0x%08X" % s for s in nowriter))

if __name__ == "__main__":
    main()
