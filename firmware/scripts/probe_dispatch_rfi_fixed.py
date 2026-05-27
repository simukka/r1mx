#!/usr/bin/env python3
"""Probe rfi dispatch sites — with step-over workaround for QEMU bug.

The PPC GDB stub on this QEMU build mis-handles SW BP step-over via `c`. After
each BP hit we issue `s` once to advance past the trap, then `c` to continue.
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
    ("rfi@0x70c",     0x0000070c),
    ("rfi@0x371718",  0x00371718),
    ("rfi@0x371838",  0x00371838),
    ("rfi@0x372838",  0x00372838),
    ("rfi@0xe2b2c0",  0x00e2b2c0),
    ("kInit@0x5A7F30",0x005A7F30),
    ("kInit_ret@0x36c428", 0x0036c428),
    ("fn_381a8c",     0x00381a8c),
    ("fn_371cd0",     0x00371cd0),
    ("fn_371cd0_ret@0x371db8", 0x00371db8),
    ("idle@0x124",    0x00000124),
]

def go(sock, action, timeout):
    """Send 's' or 'c' and wait for stop. Return parsed regs."""
    send(sock, action)
    recv(sock, timeout)
    return parse_g(query(sock, "g"))

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        for n, a in BPS:
            query(sock, f"Z0,{a:x},4")
        print(f"[+] Armed {len(BPS)} BPs")
        for i in range(40):
            try:
                regs = go(sock, "c", 60)
            except socket.timeout:
                print(f"[-] timeout after {i} hits"); break
            pc = regs.get("pc", 0)
            name = next((n for n,a in BPS if a == pc), f"?@0x{pc:x}")
            print(f"#{i+1:2d} {name:18s} pc=0x{pc:08x} lr=0x{regs.get('lr',0):08x} "
                  f"r1=0x{regs.get('r1',0):08x} r3=0x{regs.get('r3',0):08x} msr=0x{regs.get('msr',0):08x}")
            # step past the BP so `c` won't re-hit
            try:
                sregs = go(sock, "s", 5)
                if sregs.get("pc",0) == pc:
                    print(f"     [!] `s` didn't advance from 0x{pc:x}")
            except socket.timeout:
                print(f"     [!] `s` timeout at 0x{pc:x}"); break
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
