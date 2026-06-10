#!/usr/bin/env python3
"""
gdb_halt_inspect.py — Connect to a GDB stub, halt the target, dump PC + key
registers + a small instruction-context hint, then detach.

Used to diagnose where execution currently is. Works against QEMU (:1234) or
live silicon via the XMD GDB stub (:2345 — see host_xmd_bridge.md).
"""

import argparse
import socket
import sys
import time

from rsp import RSP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--samples", type=int, default=5,
                    help="number of halt/sample/continue cycles")
    ap.add_argument("--sleep-between", type=float, default=0.5)
    args = ap.parse_args()

    t = RSP(args.host, args.port, timeout=10.0).connect()
    try:
        s0 = t.stop_reply()
        print(f"[*] Initial stop reply: {s0!r}")
        if "T05" in s0 or "T02" in s0:
            print("[*] Target is already halted")
        else:
            print(f"[*] Unexpected state: {s0!r}")

        for i in range(args.samples):
            if i > 0:
                t.send("c")
                time.sleep(args.sleep_between)
                try:
                    stop = t.interrupt(5.0)
                    print(f"\n[*] Sample {i+1} stop reply: {stop!r}")
                except socket.timeout:
                    print(f"[!] Could not halt for sample {i+1}")
                    continue

            regs = t.regs()
            pc = regs.get("pc", 0)
            lr = regs.get("lr", 0)
            print(f"  Sample {i+1}: PC=0x{pc:08x}  LR=0x{lr:08x}  "
                  f"CTR=0x{regs.get('ctr',0):08x}  MSR=0x{regs.get('msr',0):08x}  "
                  f"SP=0x{regs.get('r1',0):08x}")
            try:
                print(f"    insn @ PC..PC+16: {t.read_mem(pc, 16).hex()}")
            except Exception as e:
                print(f"    insn read failed: {e}")
            try:
                print(f"    insn @ LR (0x{lr:08x}): {t.read_mem(lr, 4).hex()}")
            except Exception as e:
                print(f"    LR read failed: {e}")
    finally:
        try:
            t.detach()
        except Exception:
            pass
        t.close()


if __name__ == "__main__":
    sys.exit(main())
