#!/usr/bin/env python3
"""
task_walker.py — Phase 2 of plans/working_camera_jtag_analysis.md.

READ-ONLY walk of the live VxWorks active-task list on a working RED ONE MX
camera (over Channel B / xmd_rpc), producing the task -> driver/device map that
the QEMU device models need.

It does NOT depend on VxWorks symbols (none ship in the production image). The
WIND_TCB layout below was derived empirically from live memory on cam-working-01
and cross-checked against the decompile (FUN_005aaf5c reschedule loop):

  taskIdCurrent global : 0x00e9c3e0   ([..] -> current TCB)
  readyQ head global   : 0x010d0584
  TCB signature        : *(tcb+0x08) == 0x00810600   (task class ptr)
  active-list node     : tcb+0x50  (DL_NODE next,prev) ; TCB = node-0x50
  priority             : *(tcb+0x48)  (byte/word, 0..255)
  stack base/lim/end   : *(tcb+0x60 / +0x64 / +0x68)
  ENTRY point          : *(tcb+0xc0)   (static, set by taskInit; NOT the live PC.
                         Verified: current task's +0xc0 != live CPU pc. Tasks that
                         share a +0xc0 value are instances of the same task type.)
  stackEnd (static)    : *(tcb+0xc8)   (NOT the live saved SP — that REG_SET offset
                         is in context-switch asm and is still unknown.)
  NOTE: live PC/SP and pend-object are NOT readable from these fields. For live
  per-task state, use Phase 3 (breakpoint the driver), not this walker.

Live code addresses are translated to image offsets with D_text and resolved to
a containing function via firmware/reverse/build_32/src/manifest.csv. Default
D_text = 0x10180 (cam-working-01; see camera_reports/cam-working-01/PHASE0_reloc.md).
RE-DERIVE D_text per camera (Phase 0) and pass --d-text.

Usage (camera booted, agent_loop running in XMD):
  python3 firmware/scripts/task_walker.py --id cam-working-01 --d-text 0x10180
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from bisect import bisect_right
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import xmd_rpc  # noqa: E402

# --- confirmed kernel anchors (cam-working-01, build 32) -------------------
TASK_ID_CURRENT = 0x00e9c3e0
READYQ_HEAD     = 0x010d0584
TCB_SIG_OFF     = 0x08
TCB_SIG_VAL     = 0x00810600
ACTIVE_NODE_OFF = 0x50          # DL_NODE(next,prev); TCB = node - ACTIVE_NODE_OFF
OFF_PRIO        = 0x48
OFF_STACK_BASE  = 0x60
OFF_STACK_LIM   = 0x64
OFF_STACK_END   = 0x68
OFF_ENTRY       = 0xc0          # static entry point (NOT live PC)
OFF_STACK_END2  = 0xc8          # static stackEnd (NOT live SP)
OFF_SAVED_PC    = OFF_ENTRY     # back-compat aliases
OFF_SAVED_SP    = OFF_STACK_END2
TCB_WORDS       = 0x80          # 512 bytes is enough to cover all fields above

_DEAD = ("Debug Operation Not Supported", "Unable to Stop", "No target")


class Bridge:
    def __init__(self, bridge_dir, timeout):
        self.dir, self.timeout = bridge_dir, timeout
    def rpc(self, cmd):
        # read-only guard: nothing here mutates, but be explicit.
        for tok in re.split(r"[;\s]+", cmd.strip().lower()):
            if tok in ("rst", "mwr", "rwr", "dow", "program", "erase"):
                raise PermissionError(f"refused (read-only): {cmd!r}")
        return xmd_rpc.rpc(cmd, dir_=self.dir, timeout=self.timeout)
    def halt(self):  self.rpc("stop")
    def resume(self):
        try: self.rpc("con")
        except Exception: pass
    def alive(self):
        return not any(m in self.rpc("rrd") for m in _DEAD)
    def words(self, addr, n):
        out, res = [], self.rpc(f"set o [mrd 0x{addr:x} {n}]; set o")
        for line in res.splitlines():
            m = re.match(r'\s*([0-9A-Fa-f]+):\s+([0-9A-Fa-f]+)\s*$', line)
            if m: out.append(int(m.group(2), 16))
        return out
    def word(self, addr):
        w = self.words(addr, 1); return w[0] if w else None


class FuncTable:
    """Resolve an image address to its containing function via manifest.csv,
    with prologue back-scan for addresses that fall in manifest gaps."""
    MFLR_R0 = b"\x7c\x08\x02\xa6"
    def __init__(self, manifest: Path, image: Path | None = None):
        self.addrs, self.rows = [], []
        with manifest.open() as fh:
            for r in csv.DictReader(fh):
                try: a = int(r["addr"], 16)
                except (KeyError, ValueError): continue
                self.addrs.append(a)
                self.rows.append((a, int(r.get("size") or 0),
                                  r.get("name", ""), r.get("module", "")))
        order = sorted(range(len(self.addrs)), key=lambda i: self.addrs[i])
        self.addrs = [self.addrs[i] for i in order]
        self.rows  = [self.rows[i] for i in order]
        self.img = image.read_bytes() if image and image.exists() else None

    @staticmethod
    def _is_stwu_r1_neg(w: bytes) -> bool:
        # stwu r1,-N(r1) : 0x9421 hhll with signed16(hhll) < 0  (frame setup)
        return len(w) == 4 and w[0] == 0x94 and w[1] == 0x21 and (w[2] & 0x80)

    def _backscan_entry(self, img_addr: int, floor: int):
        """Nearest function prologue at/below img_addr: a `stwu r1,-N(r1)` with
        a `mflr r0` within the next few insns. Returns its addr or None."""
        if self.img is None: return None
        lo = max(0, floor, img_addr - 0x8000)
        a = img_addr & ~3
        while a >= lo:
            if self._is_stwu_r1_neg(self.img[a:a + 4]) and \
               self.MFLR_R0 in self.img[a:a + 20]:
                return a
            a -= 4
        return None

    def resolve(self, img_addr):
        i = bisect_right(self.addrs, img_addr) - 1
        if i < 0: return None
        a, size, name, module = self.rows[i]
        if not (size and img_addr >= a + size):
            return {"name": name, "addr": a, "off": img_addr - a,
                    "module": module, "in_gap": False}
        # gap: try to recover the true entry by prologue back-scan
        ent = self._backscan_entry(img_addr, floor=a + size)
        if ent is not None:
            return {"name": f"sub_{ent:06x}", "addr": ent, "off": img_addr - ent,
                    "module": "", "in_gap": False, "recovered": True}
        return {"name": name, "addr": a, "off": img_addr - a,
                "module": module, "in_gap": True}


def looks_like_name(b: bytes):
    s = b.split(b"\x00", 1)[0]
    if 2 <= len(s) <= 31 and all(32 <= c < 127 for c in s) \
       and re.match(rb"[A-Za-z_][\w .:/+-]*$", s):
        return s.decode("ascii", "replace")
    return None


def find_name(br: Bridge, tcb_words, base):
    """Scan TCB pointer fields for one that points at a short ASCII name."""
    seen = set()
    for w in tcb_words:
        if w in seen or not (0x00100000 <= w <= 0x0a000000): continue
        seen.add(w)
        if w in (TCB_SIG_VAL,): continue
        ws = br.words(w, 8)
        if not ws: continue
        blob = b"".join(x.to_bytes(4, "big") for x in ws)
        nm = looks_like_name(blob)
        if nm: return nm, f"0x{w:08x}"
    return None, None


def walk_active(br: Bridge, start_tcb, limit=128):
    """Enumerate the active-task list. Each TCB carries a DL_NODE at +0x50
    (next) / +0x54 (prev). The list threads through a head sentinel whose
    (node-0x50) lacks the task signature; we skip sentinels but keep walking,
    and traverse BOTH directions from the start TCB so we get the whole list
    whether it is circular or NULL-terminated. Returns (ordered_tcbs, head)."""
    order, seen, head = [], set(), None

    def consider(tcb):
        if tcb in seen: return
        if br.word(tcb + TCB_SIG_OFF) == TCB_SIG_VAL:
            seen.add(tcb); order.append(tcb)

    consider(start_tcb)
    for link in (0x0, 0x4):                       # +0x0 = .next, +0x4 = .prev
        node = start_tcb + ACTIVE_NODE_OFF
        node_seen = {node}
        for _ in range(limit):
            nxt = br.word(node + link)            # neighbouring node address
            if not nxt or nxt in node_seen: break
            node_seen.add(nxt)
            tcb = nxt - ACTIVE_NODE_OFF
            if br.word(tcb + TCB_SIG_OFF) == TCB_SIG_VAL:
                consider(tcb)
            else:
                head = nxt                        # list-head sentinel
            node = nxt
    return order, head


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True)
    ap.add_argument("--d-text", default="0x10180")
    ap.add_argument("--manifest", default=str(
        _HERE.parent / "reverse/build_32/src/manifest.csv"))
    ap.add_argument("--image", default=str(
        _HERE.parent / "reverse/build_32/extracted/software.bin"),
        help="firmware image for prologue back-scan of manifest gaps")
    ap.add_argument("--bridge-dir", default=xmd_rpc.DEFAULT_DIR)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--limit", type=int, default=128)
    ap.add_argument("--rounds", type=int, default=4,
                    help="halt/walk/resume rounds to union (TLB-residency robust)")
    ap.add_argument("--no-names", action="store_true",
                    help="skip name scan (faster; many extra reads otherwise)")
    ap.add_argument("--out", default=str(
        _HERE.parent / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    d_text = int(args.d_text, 16)
    ft = FuncTable(Path(args.manifest), Path(args.image))
    br = Bridge(args.bridge_dir, args.timeout)

    try:
        br.halt()
        if not br.alive():
            print("[!] no live debug link (XMD 'connect ppc hw' in the VM)."); return 2
    except Exception as e:
        print(f"[!] no agent response ({e}); is agent_loop running?"); return 1

    # Multi-round union: each halt has a different task context, so different
    # TCB heap pages are TLB-resident and readable. Merge across rounds so the
    # persistent task set converges (robust to TLB residency + transient tasks).
    merged = {}          # tcb_addr -> record (first complete reading wins)
    head = None
    for rnd in range(args.rounds):
        if rnd:
            br.resume()              # let the camera run + switch context
            br.rpc("rrd")            # round-trip latency = brief run time
            br.halt()
            if not br.alive(): break
        cur = br.word(TASK_ID_CURRENT)
        tcbs, h = walk_active(br, cur, args.limit)
        head = head or h
        for t in tcbs:
            if t in merged: continue
            w = br.words(t, TCB_WORDS)
            if len(w) < OFF_SAVED_SP // 4 + 1: continue
            gw = lambda off: w[off // 4]
            pc = gw(OFF_SAVED_PC)
            if not pc:               # unreadable this round; retry next round
                continue
            fn = ft.resolve(pc - d_text)
            name = None if args.no_names else find_name(br, w, t)[0]
            merged[t] = {
                "tcb": f"0x{t:08x}", "name": name,
                "priority": gw(OFF_PRIO) & 0xff,
                "entry": f"0x{pc:08x}",            # static entry (NOT live PC)
                "stack_base": f"0x{gw(OFF_STACK_BASE):08x}",
                "stack_end": f"0x{gw(OFF_STACK_END2):08x}",
                "entry_func": (f"{fn['name']}+0x{fn['off']:x}"
                               + ("(gap)" if fn['in_gap'] else "")) if fn else None,
                "entry_img": f"0x{pc - d_text:08x}", "round": rnd,
                "module": fn["module"] if fn and fn["module"] else None,
            }
        print(f"[*] round {rnd}: cur=0x{cur:08x}  +{len(tcbs)} walked  "
              f"= {len(merged)} unique so far")

    tasks = sorted(merged.values(), key=lambda r: int(r["tcb"], 16))
    print(f"[*] union: {len(tasks)} tasks"
          + (f"  head=0x{head:08x}" if head else ""))
    for rec in tasks:
        print(f"    {rec['tcb']}  pri={rec['priority']:>3}  "
              f"entry={rec['entry']}  {rec['entry_func'] or '?'}"
              f"  {('['+rec['name']+']') if rec['name'] else ''}")

    report = {
        "camera_id": args.id, "phase": "2-task-walk",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "d_text": f"0x{d_text:x}", "task_id_current": f"0x{cur:08x}",
        "active_list_head": f"0x{head:08x}" if head else None,
        "tcb_layout": {"sig_off": TCB_SIG_OFF, "sig_val": f"0x{TCB_SIG_VAL:x}",
                       "active_node_off": ACTIVE_NODE_OFF, "prio_off": OFF_PRIO,
                       "entry_off": OFF_ENTRY, "note": "entry is static, not live PC"},
        "tasks": tasks,
    }
    br.resume()
    outdir = Path(args.out) / args.id
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "").replace("-", "")
    (outdir / f"tasks_{stamp}.json").write_text(json.dumps(report, indent=2))
    print(f"\n[*] {len(tasks)} tasks -> {outdir / f'tasks_{stamp}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
