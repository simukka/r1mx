#!/usr/bin/env python3
"""Sweep kernelInit body to localize the fault point.

Arms a BP at every 0x40 bytes from 0x5A7F30 through 0x5A8530 (~0x600 bytes,
generous bound) plus 0x36c424 (wrap-back). Tracks the highest body PC reached
before each wrap. That highest PC is the last instruction executed before the
fault that routes back to 0x36c424.
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

WRAP = 0x36c424
START = 0x5A7F30
END   = 0x5A8530
STRIDE = 0x40

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    addrs = list(range(START, END, STRIDE))  # body only; wrap BP interferes with bl step-over
    try:
        send(sock, "?"); recv(sock)
        for a in addrs:
            query(sock, f"Z0,{a:x},4")
        print(f"[+] Armed {len(addrs)} BPs ({len(addrs)-1} body + wrap)")
        max_pc_this_cycle = 0
        wraps = 0
        for i in range(60):
            send(sock, "c")
            try: recv(sock, 10)
            except socket.timeout:
                print(f"[-] timeout after {i} hits"); break
            r = parse_g(query(sock, "g"))
            pc = r.get("pc",0)
            tag = "WRAP" if pc == WRAP else f"body+0x{pc-START:03x}"
            if pc == WRAP:
                wraps += 1
                print(f"#{i+1:2d} {tag:14s}  (cycle {wraps} max body PC = 0x{max_pc_this_cycle:08x})")
                max_pc_this_cycle = 0
            else:
                if pc > max_pc_this_cycle: max_pc_this_cycle = pc
                print(f"#{i+1:2d} {tag:14s}  pc=0x{pc:08x} lr=0x{r.get('lr',0):08x} r3=0x{r.get('r3',0):08x} r1=0x{r.get('r1',0):08x} msr=0x{r.get('msr',0):08x}")
            if wraps >= 4: break
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
