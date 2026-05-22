#!/usr/bin/env python3
"""
gdb_halt_inspect.py — Connect to the GDB stub, halt the target with Ctrl-C,
dump PC + key registers + a small backtrace hint, then detach.

Used to diagnose where the firmware is currently executing.
"""

import argparse
import socket
import sys
import time


def cksum(b):
    return f"{sum(b) & 0xff:02x}".encode()


def send(sock, payload, no_ack=False):
    pkt = b"$" + payload.encode() + b"#" + cksum(payload.encode())
    sock.sendall(pkt)
    if not no_ack:
        if sock.recv(1) != b"+":
            raise RuntimeError("bad ack")


def recv(sock, no_ack=False, timeout=10.0):
    sock.settimeout(timeout)
    while True:
        b = sock.recv(1)
        if b == b"$":
            break
        if not b:
            raise RuntimeError("closed")
    buf = bytearray()
    while True:
        b = sock.recv(1)
        if b == b"#":
            sock.recv(2)
            break
        buf.extend(b)
    if not no_ack:
        sock.sendall(b"+")
    return buf.decode("latin-1")


def query(sock, p, no_ack=False):
    send(sock, p, no_ack)
    return recv(sock, no_ack)


PPC_REG_NAMES = (
    [f"r{i}" for i in range(32)]
    + ["pc", "msr", "cr", "lr", "ctr", "xer"]
)


def parse_g(hexstr):
    regs = {}
    pos = 0
    for name in PPC_REG_NAMES:
        chunk = hexstr[pos:pos + 8]
        if len(chunk) < 8:
            break
        try:
            regs[name] = int(chunk, 16)
        except ValueError:
            break
        pos += 8
    return regs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--samples", type=int, default=5,
                    help="number of halt/sample/continue cycles")
    ap.add_argument("--sleep-between", type=float, default=0.5)
    args = ap.parse_args()

    sock = socket.create_connection((args.host, args.port), timeout=10)
    try:
        # Probe current state
        send(sock, "?", False)
        s0 = recv(sock, False)
        print(f"[*] Initial stop reply: {s0!r}")

        if "T05" in s0 or "T02" in s0:
            print("[*] Target is already halted")
        else:
            print(f"[*] Unexpected state: {s0!r}")

        for i in range(args.samples):
            # If not first sample, resume briefly so we sample over time
            if i > 0:
                send(sock, "c", False)
                time.sleep(args.sleep_between)
                sock.sendall(b"\x03")
                try:
                    stop = recv(sock, False, 5.0)
                    print(f"\n[*] Sample {i+1} stop reply: {stop!r}")
                except socket.timeout:
                    print(f"[!] Could not halt for sample {i+1}")
                    continue

            g = query(sock, "g", False)
            regs = parse_g(g)
            pc = regs.get("pc", 0)
            lr = regs.get("lr", 0)
            ctr = regs.get("ctr", 0)
            msr = regs.get("msr", 0)
            r1 = regs.get("r1", 0)
            print(f"  Sample {i+1}: PC=0x{pc:08x}  LR=0x{lr:08x}  "
                  f"CTR=0x{ctr:08x}  MSR=0x{msr:08x}  SP=0x{r1:08x}")

            # Read 16 bytes (4 instructions) around PC
            try:
                m = query(sock, f"m{(pc - 0) & 0xffffffff:x},16", False)
                print(f"    insn @ PC..PC+16: {m}")
            except Exception as e:
                print(f"    insn read failed: {e}")

            # Read 4 bytes at LR (likely return point)
            try:
                m = query(sock, f"m{lr:x},4", False)
                print(f"    insn @ LR (0x{lr:08x}): {m}")
            except Exception as e:
                print(f"    LR read failed: {e}")

    finally:
        # Detach (resume)
        try:
            send(sock, "D", False)
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
