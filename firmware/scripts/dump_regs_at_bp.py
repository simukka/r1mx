#!/usr/bin/env python3
"""
dump_regs_at_bp.py — Set a SW BP at --addr, wait for it to fire, dump
key registers (PC, LR, CTR, r1, r3, r30, r31), then detach.
"""
import argparse, socket, sys

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", required=True, help="BP address (hex)")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    addr = int(args.addr, 16) if args.addr.startswith("0x") else int(args.addr, 16)
    sock = socket.create_connection((args.host, args.port), timeout=10)

    try:
        send(sock, "?")
        recv(sock)

        r = query(sock, f"Z0,{addr:x},4")
        if r != "OK":
            print(f"[!] Failed to set BP at 0x{addr:08x}: {r!r}")
            return 1

        print(f"[*] BP set at 0x{addr:08x}, waiting up to {args.timeout}s...")
        send(sock, "c")
        stop = recv(sock, args.timeout)
        print(f"[*] Stopped: {stop!r}")

        query(sock, f"z0,{addr:x},4")

        g = query(sock, "g")
        regs = parse_g(g)

        print(f"\n=== Registers at BP 0x{addr:08x} ===")
        for name in ["pc", "lr", "ctr", "r1", "r3", "r4", "r28", "r29", "r30", "r31"]:
            print(f"  {name:<6} = 0x{regs.get(name, 0):08x}")
        print()
        print(f"  [SP+0x24 = where LR is saved in fn_371cd0 frame]")

        # Read memory at sp + 0x24 to see actual saved LR
        sp = regs.get("r1", 0)
        for offset in [0x00, 0x04, 0x20, 0x24]:
            r = query(sock, f"m{sp+offset:x},4")
            try:
                val = int(r, 16)
            except ValueError:
                val = 0
            print(f"  mem[SP+0x{offset:02x}] = mem[0x{sp+offset:08x}] = 0x{val:08x}")

    finally:
        try:
            send(sock, "D")
        except Exception:
            pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
