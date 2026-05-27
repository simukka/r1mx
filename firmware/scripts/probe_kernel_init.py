#!/usr/bin/env python3
"""Probe kernelInit + all rfi sites.

Determines whether kernelInit (0x5A7F30) is reached and whether ANY rfi ever
fires (0x70c, 0x371718, 0x371838, 0x372838, 0xe2b2c0). Reports first BP hit
with PC and key registers, then continues to see if more fire.
"""
import socket, sys

def cksum(b): return f"{sum(b) & 0xff:02x}".encode()

def send(sock, p):
    sock.sendall(b"$" + p.encode() + b"#" + cksum(p.encode()))
    if sock.recv(1) != b"+": raise RuntimeError("bad ack")

def recv(sock, timeout=10):
    sock.settimeout(timeout)
    while True:
        b = sock.recv(1)
        if b == b"$": break
        if not b: raise RuntimeError("closed")
    buf = bytearray()
    while True:
        b = sock.recv(1)
        if b == b"#":
            sock.recv(2); break
        buf.extend(b)
    sock.sendall(b"+")
    return buf.decode("latin-1")

def query(sock, p):
    send(sock, p); return recv(sock)

PPC_REG_NAMES = [f"r{i}" for i in range(32)] + ["pc","msr","cr","lr","ctr","xer"]

def parse_g(hexstr):
    regs = {}; pos = 0
    for name in PPC_REG_NAMES:
        chunk = hexstr[pos:pos+8]
        if len(chunk) < 8: break
        try: regs[name] = int(chunk, 16)
        except ValueError: break
        pos += 8
    return regs

BPS = [
    ("kernelInit",   0x5A7F30),
    ("rfi@0x70c",    0x0000070c),
    ("rfi@0x371718", 0x00371718),
    ("rfi@0x371838", 0x00371838),
    ("rfi@0x372838", 0x00372838),
    ("rfi@0xe2b2c0", 0x00e2b2c0),
]

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        for name, addr in BPS:
            r = query(sock, f"Z0,{addr:x},4")
            print(f"[+] Z0 {name} 0x{addr:x}: {r}")

        hits = []
        for i in range(8):
            send(sock, "c")
            try:
                recv(sock, 20)
            except socket.timeout:
                print(f"\n[-] No further BP in 20s (after {len(hits)} hits)")
                try:
                    sock.sendall(b"\x03")
                    recv(sock, 2)
                except Exception: pass
                break
            regs = parse_g(query(sock, "g"))
            pc = regs.get("pc", 0)
            name = next((n for n,a in BPS if a == pc), "?")
            hits.append((name, pc, regs))
            print(f"\n=== HIT #{i+1}: {name} PC=0x{pc:08x} ===")
            for k in ("r1","r3","r4","r11","r31","lr","ctr","msr"):
                print(f"  {k:>4} = 0x{regs.get(k,0):08x}")

        if not hits:
            print("\n[!] kernelInit NEVER reached — boot fails before task subsystem init")
        else:
            seen = {h[0] for h in hits}
            print(f"\n[*] Distinct sites hit: {seen}")
        return 0
    finally:
        for _, addr in BPS:
            try: query(sock, f"z0,{addr:x},4")
            except Exception: pass
        try: send(sock, "D")
        except Exception: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
