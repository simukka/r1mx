#!/usr/bin/env python3
"""
bisect_corruption.py — Bisect the boot path to find WHEN memory at --addr
becomes corrupted. Set a series of breakpoints at known boot milestones,
let the system run to each one, check whether the watched memory has changed.

Outputs a table of milestone -> memory snapshot. The first milestone with a
changed snapshot is the function (or earlier) that introduces the corruption.
"""

import argparse
import socket
import sys
import time


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


def read_mem(sock, addr, length):
    r = query(sock, f"m{addr:x},{length:x}")
    out = []
    for i in range(0, len(r), 8):
        out.append(int(r[i:i+8], 16) if len(r[i:i+8]) == 8 else 0)
    return out


# Milestones from re_reference.md / annotations.r2
# Default list runs deep into kernelInit and the root-task path.
MILESTONES = [
    (0x0036C424, "usrInit: about to call kernelInit"),
    (0x005A7F30, "kernelInit entry"),
    (0x005A8170, "kernelInit: WDB task spawn area"),
    (0x005A8190, "kernelInit: deferred ctor NOP (Patch #56) site"),
    (0x005A8194, "kernelInit: WDB network init NOP (Patch #57) site"),
    (0x005A838C, "kernelInit: RTTI assertion loop NOP (Patch #55) site"),
    (0x005A2A28, "WDB task spawn (per re_reference)"),
    (0x0037C440, "rootTask entry"),
    (0x00381A8C, "fn_381a8c root task wrapper (Patch #53a target)"),
    (0x00382E80, "fn_382e80 main dispatcher"),
    (0x0036B3DC, "usrWdbInit entry"),
    (0x0036B7EC, "bsp_init_caller (calls usrWdbInit)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", default="0x0", help="watched address")
    ap.add_argument("--length", type=int, default=32,
                    help="bytes to watch (default 32)")
    ap.add_argument("--bp-timeout", type=float, default=15.0)
    args = ap.parse_args()

    addr = int(args.addr, 16)
    sock = socket.create_connection((args.host, args.port), timeout=10)

    try:
        # Halt if running
        send(sock, "?")
        s = recv(sock)
        if "T05" not in s and "T02" not in s:
            sock.sendall(b"\x03")
            recv(sock, 5)

        # Take initial snapshot
        initial = read_mem(sock, addr, args.length)
        print(f"[*] Initial memory @ 0x{addr:08x}:")
        for i, v in enumerate(initial):
            print(f"      +{i*4:02x}: 0x{v:08x}")
        print()

        last_snapshot = initial[:]

        for ms_addr, ms_label in MILESTONES:
            # Set BP at milestone
            r = query(sock, f"Z0,{ms_addr:x},4")
            if r != "OK":
                print(f"[!] Failed to set BP at 0x{ms_addr:08x}: {r!r}")
                continue

            # Continue
            send(sock, "c")
            try:
                stop = recv(sock, args.bp_timeout)
            except socket.timeout:
                print(f"[!] BP at 0x{ms_addr:08x} ({ms_label}) did NOT fire within {args.bp_timeout}s — STOPPING")
                # Interrupt
                sock.sendall(b"\x03")
                try:
                    recv(sock, 5)
                except Exception:
                    pass
                # Read memory at current point
                snap = read_mem(sock, addr, args.length)
                changed_offsets = [i for i in range(len(snap)) if snap[i] != initial[i]]
                if changed_offsets:
                    print(f"    Memory had been corrupted at offsets: {[hex(o*4) for o in changed_offsets]}")
                # Clear BP
                query(sock, f"z0,{ms_addr:x},4")
                break

            # Clear BP immediately
            query(sock, f"z0,{ms_addr:x},4")

            # Read memory snapshot
            snap = read_mem(sock, addr, args.length)
            changes_since_init = [(i*4, initial[i], snap[i])
                                  for i in range(len(snap))
                                  if snap[i] != initial[i]]
            changes_since_last = [(i*4, last_snapshot[i], snap[i])
                                  for i in range(len(snap))
                                  if snap[i] != last_snapshot[i]]

            print(f"  [REACHED] 0x{ms_addr:08x} {ms_label}")
            if changes_since_init:
                print(f"    Total changes from init: {len(changes_since_init)}")
                for off, old, new in changes_since_init[:8]:
                    print(f"      +{off:02x}: 0x{old:08x} -> 0x{new:08x}")
            else:
                print(f"    [no changes]")
            if changes_since_last and last_snapshot != initial:
                print(f"    New changes since last milestone: {len(changes_since_last)}")

            last_snapshot = snap[:]

    finally:
        try:
            send(sock, "D")
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
