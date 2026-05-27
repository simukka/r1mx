#!/usr/bin/env python3
"""Sweep kernelInit body (post-fn_371cd0 call) to trace the dispatch path.

BPs at 0x40 stride across 0x5b2520..0x5b3000, plus rfi sites, plus idle.
Uses `s`-then-`c` step-over workaround.
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
def query(sock, p): send(sock, p); return recv(sock)

PPC = [f"r{i}" for i in range(32)] + ["pc","msr","cr","lr","ctr","xer"]
def parse_g(h):
    r = {}; p = 0
    for n in PPC:
        c = h[p:p+8]
        if len(c) < 8: break
        try: r[n] = int(c, 16)
        except: break
        p += 8
    return r

def main():
    addrs = list(range(0x5b2520, 0x5b3000, 0x40))
    addrs += [0x70c, 0x371718, 0x371838, 0x372838, 0xe2b2c0]
    addrs += [0x36c428, 0x124, 0x381a8c]
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        for a in addrs: query(sock, f"Z0,{a:x},4")
        print(f"[+] Armed {len(addrs)} BPs ({sum(1 for a in addrs if 0x5b2520<=a<0x5b3000)} body)")
        for i in range(60):
            send(sock, "c")
            try: recv(sock, 30)
            except socket.timeout:
                print(f"[-] timeout after {i} hits"); break
            regs = parse_g(query(sock, "g"))
            pc = regs.get("pc",0)
            tag = f"body+0x{pc-0x5b24b8:04x}" if 0x5b2520<=pc<0x5b3000 else f"0x{pc:08x}"
            print(f"#{i+1:2d} {tag:18s} lr=0x{regs.get('lr',0):08x} r1=0x{regs.get('r1',0):08x} r3=0x{regs.get('r3',0):08x} r31=0x{regs.get('r31',0):08x} cr=0x{regs.get('cr',0):08x} msr=0x{regs.get('msr',0):08x}")
            if pc == 0x124:
                print("[!] reached idle — kInit returned, dispatch path was NOT taken"); break
            if pc in (0x70c, 0x371718, 0x371838, 0x372838, 0xe2b2c0):
                print("[*] RFI SITE HIT — dispatch path found!"); break
            if pc == 0x381a8c:
                print("[*] fn_381a8c HIT — usrRoot is running!"); break
            # step past BP
            send(sock, "s")
            try: recv(sock, 5)
            except socket.timeout:
                print(f"     [!] `s` timeout at 0x{pc:x}"); break
        return 0
    finally:
        for a in addrs:
            try: query(sock, f"z0,{a:x},4")
            except: pass
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
