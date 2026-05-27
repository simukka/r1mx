#!/usr/bin/env python3
"""Diagnose kernelInit loop: does it return, and where does control go?

BPs:
  - 0x36c424  = `bl kernelInit` call site (caller pre-call)
  - 0x36c428  = caller return address (post-call)
  - 0x5A7F30  = kernelInit entry
  - 0x700     = Patch #58 exception handler (Program Exception)
  - 0x300     = Data Storage Exception
  - 0x400     = Instruction Storage Exception
  - 0x600     = Alignment
  - 0xc00     = Syscall
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

BPS = [
    ("precall@0x36c424", 0x36c424),
    ("postcall@0x36c428", 0x36c428),
    ("kernelInit@0x5A7F30", 0x5A7F30),
    ("exc_DSI@0x300",  0x300),
    ("exc_ISI@0x400",  0x400),
    ("exc_Align@0x600",0x600),
    ("exc_Prog@0x700", 0x700),
    ("exc_Sys@0xc00",  0xc00),
]

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        for n, a in BPS:
            query(sock, f"Z0,{a:x},4")
        print(f"[+] Armed {len(BPS)} BPs")
        for i in range(12):
            send(sock, "c")
            try: recv(sock, 15)
            except socket.timeout:
                print(f"[-] timeout after {i} hits")
                try:
                    sock.sendall(b"\x03"); recv(sock, 2)
                except: pass
                break
            r = parse_g(query(sock, "g"))
            pc = r.get("pc",0)
            name = next((n for n,a in BPS if a == pc), f"?@0x{pc:x}")
            print(f"#{i+1:2d} {name:24s} lr=0x{r.get('lr',0):08x} r1=0x{r.get('r1',0):08x} r3=0x{r.get('r3',0):08x} msr=0x{r.get('msr',0):08x}")
        return 0
    finally:
        for _, a in BPS:
            try: query(sock, f"z0,{a:x},4")
            except: pass
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
