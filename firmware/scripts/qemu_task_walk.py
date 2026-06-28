#!/usr/bin/env python3
"""
qemu_task_walk.py — enumerate the live VxWorks task list inside QEMU.

Counterpart to task_walker.py (which targets live silicon over XMD). This one
drives the QEMU gdb stub (rsp.py on :1234) and uses D_text = 0x10000 (QEMU loads
software.bin at base 0x10000, so runtime PC = file offset + 0x10000).

Walks the WIND active-task list and resolves each task's static ENTRY point
(TCB+0xc0) to a function name via manifest.csv. Read-only (interrupt + memory
reads only); leaves the target running on exit.

WIND_TCB anchors (build 32, confirmed empirically against this image):
  taskIdCurrent : 0x00e9c3e0
  readyQ head   : 0x010d0584
  TCB signature : *(tcb+0x08) == 0x00810600
  active node   : tcb+0x1c  (DL_NODE next@+0x1c, prev@+0x20); TCB = node-0x1c
  priority      : *(tcb+0x48)
  ENTRY (static): *(tcb+0xc0)   (NOT the live PC)

Usage:  python3 firmware/scripts/qemu_task_walk.py [--host 127.0.0.1] [--port 1234]
(QEMU must be running with -gdb tcp::1234, e.g. qemu_boot.sh --debug minus -S, or
 launched with -gdb tcp::1234 free-running.)
"""
from __future__ import annotations
import argparse, csv, re, sys
from bisect import bisect_right
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from rsp import RSP  # noqa: E402

TASK_ID_CURRENT = 0x00e9c3e0
READYQ_HEAD     = 0x010d0584
SIG             = 0x00810600
NODE_OFF        = 0x1c          # DL_NODE(next@+0,prev@+4); TCB = node - NODE_OFF
PRIO_OFF        = 0x48
ENTRY_OFF       = 0xc0
DTEXT           = 0x10000       # QEMU runtime = file offset + 0x10000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--manifest", default=str(
        _HERE.parent / "reverse/build_32/src/manifest.csv"))
    args = ap.parse_args()

    man = []
    with open(args.manifest) as f:
        for row in csv.reader(f):
            if row and row[0].startswith("0x"):
                try: man.append((int(row[0], 16), row[1]))
                except ValueError: pass
    man.sort(); addrs = [a for a, _ in man]

    def resolve(rt):
        if not rt:
            return "-"
        off = rt - DTEXT
        i = bisect_right(addrs, off) - 1
        if i < 0:
            return f"0x{rt:08x}"
        a, nm = man[i]
        return nm if off == a else f"{nm}+0x{off - a:x}"

    t = RSP(args.host, args.port); t.connect(); t.interrupt()

    def words(a, n):
        try:
            b = t.read_mem(a, 4 * n)
            return [int.from_bytes(b[i*4:i*4+4], "big") for i in range(n)]
        except Exception:
            return None

    def w(a):
        v = words(a, 1); return v[0] if v else None

    def looks(b):
        s = b.split(b"\x00", 1)[0]
        if 2 <= len(s) <= 31 and all(32 <= c < 127 for c in s) \
           and re.match(rb"[A-Za-z_][\w .:/+-]*$", s):
            return s.decode("ascii", "replace")
        return None

    def find_name(tcb):
        for x in (words(tcb, 0x40) or []):
            if 0x00100000 <= x <= 0x0a000000:
                ws = words(x, 8)
                if ws:
                    nm = looks(b"".join(v.to_bytes(4, "big") for v in ws))
                    if nm:
                        return nm
        return "?"

    cur = w(TASK_ID_CURRENT)
    order, seen = [], set()

    def consider(tcb):
        if tcb in seen:
            return False
        if w(tcb + 8) == SIG:
            seen.add(tcb); order.append(tcb); return True
        return False

    consider(cur)
    frontier = [cur]
    for _ in range(256):
        newf = []
        for tcb in frontier:
            node = tcb + NODE_OFF
            for link in (0, 4):
                nb = w(node + link)
                if nb and 0x01000000 <= nb <= 0x10000000:
                    ntcb = nb - NODE_OFF
                    if consider(ntcb):
                        newf.append(ntcb)
        if not newf:
            break
        frontier = newf

    rq = w(READYQ_HEAD)
    print(f"taskIdCurrent=0x{cur:08x}  readyQ=0x{rq:08x}   {len(order)} tasks\n")
    print(f"{'TCB':>10} {'prio':>4}  {'name':<16} entry")
    for tcb in sorted(order, key=lambda x: (w(x + PRIO_OFF)
                                            if w(x + PRIO_OFF) is not None else 999)):
        pr = w(tcb + PRIO_OFF); ent = w(tcb + ENTRY_OFF); nm = find_name(tcb)
        star = " <==CUR" if tcb == cur else ""
        print(f"0x{tcb:08x} {pr:>4}  {nm:<16} {resolve(ent)}{star}")

    t.send("c")  # resume


if __name__ == "__main__":
    main()
