#!/usr/bin/env python3
"""Trace single-step from kInit return (0x36c428) to whatever lands at idle@0x124.

Identifies every instruction executed in the unwind chain. Annotates `bl`
(into a function we never return from), `blr` (frame pop), and `rfi`.
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

def read_word(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try: return int(r, 16)
    except: return None

def decode(insn):
    if insn is None: return "??"
    op = (insn >> 26) & 0x3f
    if insn == 0x4E800020: return "blr"
    if insn == 0x4C000064: return "rfi"
    if op == 18:
        lk = insn & 1
        return "bl ..." if lk else "b ..."
    if op == 16: return "bc ..."
    if op == 19 and ((insn >> 1) & 0x3ff) == 16:
        lk = insn & 1
        return "bclr/blrl" if lk else "bclr"
    return ""

BUDGET = 400
KINIT_RET = 0x36c428

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        # Arm only kInit_ret
        query(sock, f"Z0,{KINIT_RET:x},4")
        send(sock, "c")
        recv(sock, 60)
        regs = parse_g(query(sock, "g"))
        print(f"[+] reached 0x36c428: r1=0x{regs.get('r1',0):08x} lr=0x{regs.get('lr',0):08x} r3=0x{regs.get('r3',0):08x}")
        query(sock, f"z0,{KINIT_RET:x},4")  # remove BP so `s` advances

        last_pc = -1
        same_count = 0
        for i in range(BUDGET):
            send(sock, "s")
            try: recv(sock, 5)
            except socket.timeout:
                print(f"[-] timeout at step {i}"); break
            regs = parse_g(query(sock, "g"))
            pc = regs.get("pc", 0)
            insn = read_word(sock, pc)
            dec = decode(insn)
            mark = ""
            if "bl" in dec and "blr" not in dec: mark = "  <- BL"
            if dec == "blr": mark = "  <- BLR"
            if dec == "rfi": mark = "  <- RFI"
            if pc == 0x124: mark = "  <- IDLE"
            print(f"{i:3d} pc=0x{pc:08x} insn=0x{(insn or 0):08x} {dec:10s} lr=0x{regs.get('lr',0):08x} r1=0x{regs.get('r1',0):08x}{mark}")
            if pc == last_pc:
                same_count += 1
                if same_count > 3:
                    print("[*] PC stuck — done"); break
            else:
                same_count = 0
                last_pc = pc
            if pc == 0x124: break
        return 0
    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
