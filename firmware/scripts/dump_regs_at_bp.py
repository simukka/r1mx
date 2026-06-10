#!/usr/bin/env python3
"""
dump_regs_at_bp.py — Set a HW BP at --addr, wait for it to fire, dump
key registers (PC, LR, CTR, r1, r3, r30, r31), then detach.

Works against QEMU (:1234) or live silicon via the XMD GDB stub (:2345 — see
host_xmd_bridge.md). Uses hardware breakpoints (Z1/IAC), so it never patches
target memory and is safe on the camera.
"""
import argparse
import sys

from rsp import RSP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", required=True, help="BP address (hex)")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    addr = int(args.addr, 16)
    t = RSP(args.host, args.port, timeout=args.timeout).connect()

    try:
        t.stop_reply()
        print(f"[*] HW BP set at 0x{addr:08x}, waiting up to {args.timeout}s...")
        regs = t.run_to(addr, hw=True, timeout=args.timeout)

        print(f"\n=== Registers at BP 0x{addr:08x} ===")
        for name in ["pc", "lr", "ctr", "r1", "r3", "r4",
                     "r28", "r29", "r30", "r31"]:
            print(f"  {name:<6} = 0x{regs.get(name, 0):08x}")
        print()
        print("  [SP+0x24 = where LR is saved in fn_371cd0 frame]")

        sp = regs.get("r1", 0)
        for offset in [0x00, 0x04, 0x20, 0x24]:
            val = t.read_word(sp + offset)
            print(f"  mem[SP+0x{offset:02x}] = mem[0x{sp+offset:08x}] = "
                  f"0x{val:08x}")
    finally:
        try:
            t.detach()
        except Exception:
            pass
        t.close()


if __name__ == "__main__":
    sys.exit(main())
