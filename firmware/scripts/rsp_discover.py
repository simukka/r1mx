#!/usr/bin/env python3
"""
rsp_discover.py — learn a GDB stub's register-block layout empirically.

XMD's PPC405 GDB stub serves a much larger 'g' block than QEMU (146 vs 38
words) with a different ordering, so the fixed PPC_REG_NAMES in rsp.py mis-reads
pc/msr/lr/etc on hardware. Run this at a KNOWN breakpoint: it stops the CPU at
--addr (so we know pc == addr), dumps the whole 'g' block indexed, and points
out which word-index holds pc and the GPRs — enough to hardcode the XMD map.

Read-only: hardware breakpoint only, no writes, detaches (resumes) on exit.

Usage (at the device-poll bp, where r3 is known to be 0xffffffff):
    python3 firmware/scripts/rsp_discover.py --port 2345 --addr 0x5bb11c
"""

import argparse
import sys

from rsp import RSP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345)
    ap.add_argument("--addr", default="0x5bb11c",
                    help="address to break at; pc should read back == this")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    addr = int(args.addr, 0)
    t = RSP(args.host, args.port, timeout=args.timeout).connect()
    try:
        print(f"[*] stop reply: {t.stop_reply()!r}")
        print(f"[*] running to 0x{addr:08x} (HW bp) ...")
        if not t.set_bp(addr, hw=True):
            print("[!] could not set hw bp"); return 1
        stop = t.cont(args.timeout)
        t.clear_bp(addr, hw=True)
        print(f"[*] stopped: {stop!r}  (pc should now equal 0x{addr:08x})")

        g = t.query("g")
        words = [int(g[i:i+8], 16) for i in range(0, len(g) - len(g) % 8, 8)]
        print(f"[*] 'g' block: {len(g)} hex chars = {len(words)} x 32-bit words\n")

        for i, w in enumerate(words):
            tags = []
            if w == addr:
                tags.append("== addr  <-- candidate PC")
            if w == 0xffffffff:
                tags.append("0xffffffff (r3 at bp?)")
            tag = ("   " + ", ".join(tags)) if tags else ""
            print(f"  [{i:3d}] 0x{w:08x}{tag}")

        print("\n[*] candidate PC indices (word == 0x%08x): %s"
              % (addr, [i for i, w in enumerate(words) if w == addr]))

        # Does this stub support per-register reads ('p N')? (helps confirm map)
        pr = t.query(f"p{40:x}")
        print(f"[*] 'p40' reply: {pr!r}  "
              f"({'p-packets supported' if pr and not pr.startswith('E') and pr != '' else 'p-packets NOT supported'})")

        # Does it expose a target description we could parse automatically?
        xml = t.query("qXfer:features:read:target.xml:0,3ff")
        print(f"[*] qXfer target.xml: {xml[:60]!r}{'...' if len(xml) > 60 else ''}")
    finally:
        try:
            t.detach()
        except Exception:
            pass
        t.close()


if __name__ == "__main__":
    sys.exit(main())
