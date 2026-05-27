#!/usr/bin/env python3
"""
trace_371cd0_entries.py — Fire BP at fn_371cd0 entry up to N times,
printing LR (= caller return addr) and r1 each time.
Reveals whether the second call has LR=0 at entry.
"""
import socket, sys

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
        if b == b"$": break
        if not b: raise RuntimeError("closed")
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

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    addr = 0x371cd0
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        for i in range(N):
            r = query(sock, f"Z0,{addr:x},4")
            if r != "OK":
                print(f"[!] BP set failed: {r!r}")
                break
            send(sock, "c")
            try:
                stop = recv(sock, 90)
            except socket.timeout:
                print(f"[!] Hit #{i+1} timed out")
                break
            query(sock, f"z0,{addr:x},4")
            g = query(sock, "g")
            regs = parse_g(g)
            print(f"Hit #{i+1} at 0x{addr:08x}:")
            print(f"  r1   = 0x{regs.get('r1',0):08x}  (caller SP = 0x{regs.get('r1',0)+0x20:08x})")
            print(f"  lr   = 0x{regs.get('lr',0):08x}  (return addr)")
            print(f"  r3   = 0x{regs.get('r3',0):08x}  (arg0: TCB ptr)")
            print(f"  r4   = 0x{regs.get('r4',0):08x}  (arg1)")
            if regs.get('lr', 0) == 0:
                print(f"  *** LR IS ZERO AT ENTRY — this call will crash on return ***")
            print()

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
