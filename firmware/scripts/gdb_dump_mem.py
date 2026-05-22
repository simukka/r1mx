#!/usr/bin/env python3
"""gdb_dump_mem.py — Halt QEMU, dump arbitrary memory ranges, detach."""

import argparse
import socket
import sys


def cksum(b): return f"{sum(b) & 0xff:02x}".encode()


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--ranges", nargs="+", required=True,
                    help="addr:len pairs in hex, e.g. 0x0:32 0x700:32")
    args = ap.parse_args()

    sock = socket.create_connection((args.host, args.port), timeout=10)
    try:
        # Halt if running
        send(sock, "?")
        s = recv(sock)
        if "T05" not in s and "T02" not in s:
            sock.sendall(b"\x03")
            s = recv(sock, 5)
        print(f"[*] State: {s!r}")

        for r in args.ranges:
            addr_s, ln_s = r.split(":")
            addr = int(addr_s, 16) if addr_s.startswith("0x") else int(addr_s, 16)
            ln = int(ln_s, 16) if ln_s.startswith("0x") else int(ln_s)
            reply = query(sock, f"m{addr:x},{ln:x}")
            # Pretty print 4-byte words
            print(f"\n  Memory @ 0x{addr:08x} ({ln} bytes):")
            for i in range(0, ln, 16):
                chunk = reply[i*2:(i+16)*2]
                # words
                words = []
                for j in range(0, min(16, ln-i), 4):
                    h = chunk[j*2:(j+4)*2]
                    if len(h) == 8:
                        words.append(h)
                print(f"    0x{addr+i:08x}: " + " ".join(words))

    finally:
        try:
            send(sock, "D")
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
