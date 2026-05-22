#!/usr/bin/env python3
"""
probe_root_task_args.py — Set a SW BP at fn_381a8c (root-task entry, 0x381a8c)
and dump the arg registers when it fires. The first arg (r3) is the descriptor
pointer — its value may differ from 0x020390d0 documented earlier if the heap
allocator path changed (e.g. due to new patches).

Then immediately set a write watchpoint on that descriptor address and continue,
capturing every PC that writes to it.
"""

import argparse
import socket
import sys
import time


def cksum(b: bytes) -> bytes:
    return f"{sum(b) & 0xff:02x}".encode()


def send(sock, payload, no_ack):
    pkt = b"$" + payload.encode() + b"#" + cksum(payload.encode())
    sock.sendall(pkt)
    if not no_ack:
        if sock.recv(1) != b"+":
            raise RuntimeError("bad ack")


def recv(sock, no_ack, timeout=30.0):
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


def query(sock, payload, no_ack):
    send(sock, payload, no_ack)
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
    ap.add_argument("--bp", default="0x381a8c",
                    help="address of root task entry (default fn_381a8c)")
    ap.add_argument("--bp-timeout", type=float, default=120.0)
    ap.add_argument("--also-watch", action="store_true",
                    help="after BP fires, replace it with a write watchpoint "
                         "on whatever r3 turned out to be, and trace writers")
    ap.add_argument("--watch-hits", type=int, default=10)
    ap.add_argument("--watch-timeout", type=float, default=120.0)
    args = ap.parse_args()

    bp_addr = int(args.bp, 16)
    print(f"[*] Connecting to {args.host}:{args.port}")
    sock = socket.create_connection((args.host, args.port), timeout=10)
    no_ack = False

    try:
        send(sock, "?", no_ack)
        initial = recv(sock, no_ack)
        print(f"[*] Initial stop: {initial!r}")

        # SW BP at fn_381a8c (Z0,addr,4)
        r = query(sock, f"Z0,{bp_addr:x},4", no_ack)
        print(f"[*] Z0,{bp_addr:x},4 -> {r!r}")
        if r != "OK":
            print("[!] BP not accepted; aborting")
            return 1

        # Continue and wait for BP fire
        t0 = time.time()
        send(sock, "c", no_ack)
        try:
            stop = recv(sock, no_ack, args.bp_timeout)
        except socket.timeout:
            print(f"[!] BP at 0x{bp_addr:x} did not fire within {args.bp_timeout}s")
            sock.sendall(b"\x03")
            try:
                recv(sock, no_ack, 5.0)
            except Exception:
                pass
            return 2

        elapsed = time.time() - t0
        print(f"\n=== BP hit at 0x{bp_addr:x} (wall {elapsed:.1f}s) ===")
        print(f"  stop reply: {stop!r}")

        # Dump regs
        g = query(sock, "g", no_ack)
        regs = parse_g(g)
        pc = regs.get("pc", 0)
        lr = regs.get("lr", 0)
        ctr = regs.get("ctr", 0)
        print(f"  PC=0x{pc:08x}  LR=0x{lr:08x}  CTR=0x{ctr:08x}")
        for i in range(0, 13):
            print(f"  r{i:<2d}=0x{regs.get(f'r{i}',0):08x}",
                  end="    " if i % 4 != 3 else "\n")
        print()
        for i in range(28, 32):
            print(f"  r{i:<2d}=0x{regs.get(f'r{i}',0):08x}", end="    ")
        print()

        descriptor = regs.get("r3", 0)
        print(f"\n[*] Descriptor pointer (r3) = 0x{descriptor:08x}")

        # Read the first 32 bytes of the descriptor
        m = query(sock, f"m{descriptor:x},32", no_ack)
        print(f"[*] First 32 bytes of *(r3): {m}")

        # Remove the BP
        query(sock, f"z0,{bp_addr:x},4", no_ack)

        if args.also_watch and descriptor:
            print(f"\n[*] Now setting write watchpoint on 0x{descriptor:08x}")
            # We need to "rewind" — but we just executed. The watchpoint will
            # catch FUTURE writes only. Since we already passed the writer (the
            # descriptor was populated before kernelInit dispatched the task),
            # the watchpoint may not fire. Try anyway for a short window.
            r = query(sock, f"Z2,{descriptor:x},4", no_ack)
            print(f"[*] Z2,{descriptor:x},4 -> {r!r}")
            if r == "OK":
                hits = 0
                t_w0 = time.time()
                while hits < args.watch_hits:
                    elapsed = time.time() - t_w0
                    rem = args.watch_timeout - elapsed
                    if rem <= 0:
                        print(f"[!] watch timeout reached")
                        break
                    send(sock, "c", no_ack)
                    try:
                        s = recv(sock, no_ack, min(args.watch_hits and 30, rem))
                    except socket.timeout:
                        print(f"[!] no watch hit in window")
                        sock.sendall(b"\x03")
                        try:
                            recv(sock, no_ack, 5.0)
                        except Exception:
                            pass
                        break
                    hits += 1
                    g = query(sock, "g", no_ack)
                    regs = parse_g(g)
                    print(f"  hit#{hits}: PC=0x{regs.get('pc',0):08x}  "
                          f"stop={s!r}")

    finally:
        try:
            send(sock, "D", no_ack)
        except Exception:
            pass
        sock.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
