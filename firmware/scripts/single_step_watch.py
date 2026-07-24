#!/usr/bin/env python3
"""
single_step_watch.py — Set a write watchpoint at --addr, then single-step
through execution from the current PC. After every step, check whether the
watched memory has changed. When it has, report the PC of the instruction
that just executed (i.e. the one that caused the change).

This avoids GDB watchpoint imprecision: we don't rely on QEMU's watchpoint
trap reporting the correct PC — we just step one instruction at a time and
diff the memory.

Usage:
    # Terminal A: QEMU halted at PC=0
    ./firmware/scripts/qemu_boot.sh --debug

    # Terminal B
    python3 firmware/scripts/single_step_watch.py --addr 0x0 --steps 200
"""

import argparse
import socket
import sys


def cksum(b):
    return f"{sum(b) & 0xff:02x}".encode()


def send(sock, p):
    pkt = b"$" + p.encode() + b"#" + cksum(p.encode())
    sock.sendall(pkt)
    if sock.recv(1) != b"+":
        raise RuntimeError("bad ack")


def recv(sock, timeout=10):
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
    sock.sendall(b"+")
    return buf.decode("latin-1")


def query(sock, p):
    send(sock, p)
    return recv(sock)


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


def step(sock, timeout=10):
    """Single-step: 's' packet."""
    send(sock, "s")
    return recv(sock, timeout)


def read_mem_word(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try:
        return int(r, 16)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", default="0x0",
                    help="watched address (default 0x0)")
    ap.add_argument("--steps", type=int, default=200,
                    help="max single-steps to perform")
    ap.add_argument("--width", type=int, default=8,
                    help="how many 4-byte words to watch from --addr "
                         "(default 8 = 32 bytes)")
    args = ap.parse_args()

    addr = int(args.addr, 16) if args.addr.startswith("0x") else int(args.addr)
    sock = socket.create_connection((args.host, args.port), timeout=10)

    try:
        send(sock, "?")
        s = recv(sock)
        print(f"[*] Initial state: {s!r}")

        # Read initial PC and the watched memory snapshot
        g = query(sock, "g")
        regs = parse_g(g)
        pc = regs.get("pc", 0)
        print(f"[*] PC = 0x{pc:08x}")

        before = []
        for i in range(args.width):
            before.append(read_mem_word(sock, addr + i*4))
        print(f"[*] Initial memory @ 0x{addr:08x}:")
        for i, v in enumerate(before):
            print(f"      +{i*4:02x}: 0x{v:08x}")

        for n in range(args.steps):
            pre_pc = pc
            stop = step(sock)

            # Read PC after step
            g = query(sock, "g")
            regs = parse_g(g)
            new_pc = regs.get("pc", 0)

            # Check if memory changed
            after = []
            changed = []
            for i in range(args.width):
                v = read_mem_word(sock, addr + i*4)
                after.append(v)
                if v != before[i]:
                    changed.append((i, before[i], v))

            if changed:
                print(f"\n=== Step {n+1}: memory changed at 0x{addr:08x} ===")
                print(f"  PC before step: 0x{pre_pc:08x}")
                print(f"  PC after step : 0x{new_pc:08x}")
                # Read the instruction that just executed (at pre_pc)
                insn = read_mem_word(sock, pre_pc)
                print(f"  Executed instruction @ 0x{pre_pc:08x}: 0x{insn:08x}")
                for off, was, now in changed:
                    print(f"  *(0x{addr + off*4:08x}): 0x{was:08x} -> 0x{now:08x}")
                # Dump regs at this halt
                print(f"  Regs: PC=0x{regs['pc']:08x} LR=0x{regs.get('lr',0):08x} "
                      f"CTR=0x{regs.get('ctr',0):08x}")
                for i in range(0, 13):
                    print(f"  r{i:<2d}=0x{regs.get(f'r{i}',0):08x}",
                          end="  " if i % 4 != 3 else "\n")
                print()
                before = after  # update baseline so we keep noticing further changes
                # Don't break — keep going to capture more writes

            pc = new_pc

            # Periodic progress dot
            if (n + 1) % 20 == 0:
                print(f"[*] {n+1} steps done, PC=0x{pc:08x}")

        print(f"\n[*] {args.steps} steps complete; final PC=0x{pc:08x}")

    finally:
        try:
            send(sock, "D")
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
