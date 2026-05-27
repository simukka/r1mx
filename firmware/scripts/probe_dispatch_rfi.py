#!/usr/bin/env python3
"""Probe which rfi site dispatches the root task.

Arms SW BPs at the two candidate rfi sites (0x371718 and 0x371838) and waits
up to 30s for either to fire. On hit, reports which site fired plus r3 (the
likely ctx pointer arg) and r4 (often SRR0/stack scratch).
"""
import socket, sys, time

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
    regs = {}
    pos = 0
    for name in PPC_REG_NAMES:
        chunk = hexstr[pos:pos+8]
        if len(chunk) < 8: break
        try: regs[name] = int(chunk, 16)
        except ValueError: break
        pos += 8
    return regs

CANDIDATES = [0x371718, 0x371838]

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        for addr in CANDIDATES:
            r = query(sock, f"Z0,{addr:x},4")
            print(f"[+] Z0 0x{addr:x}: {r}")
        send(sock, "c")
        try:
            recv(sock, 30)
        except socket.timeout:
            print("[-] No BP fired within 30s — neither rfi dispatched")
            send(sock, "\x03")
            try: recv(sock, 2)
            except: pass
            return 1
        regs = parse_g(query(sock, "g"))
        pc = regs.get("pc", 0)
        print(f"\n=== BP HIT at PC=0x{pc:08x} ===")
        for addr in CANDIDATES:
            query(sock, f"z0,{addr:x},4")
        for k in ("r1","r3","r4","r11","r31","lr","ctr","msr"):
            v = regs.get(k, 0)
            print(f"  {k:>4} = 0x{v:08x}")
        if pc in CANDIDATES:
            print(f"\n[*] Match: this is the dispatch rfi at 0x{pc:x}")
        return 0
    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
