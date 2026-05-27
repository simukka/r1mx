#!/usr/bin/env python3
"""Check TCB fields that determine task initial PC and LR at fn_371cd0 epilogue."""
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

def rw(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try: return int(r, 16)
    except: return 0

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        # BP at epilogue (after all context writes)
        r = query(sock, "Z0,371db8,4")
        if r != "OK": print(f"[!] {r!r}"); return
        send(sock, "c")
        recv(sock, 60)
        query(sock, "z0,371db8,4")
        regs = parse_g(query(sock, "g"))

        tcb = regs["r31"]
        print(f"TCB (r31) = 0x{tcb:08x}")
        print()

        # ctx+0x8c = TCB+0x24c (task initial PC) — set at 0x371d9c from TCB+0xc0
        ctx_pc = rw(sock, tcb + 0x24c)
        tcb_0xc0 = rw(sock, tcb + 0xc0)
        print(f"TCB+0x0c0 = 0x{tcb_0xc0:08x}  (source for ctx+0x8c)")
        print(f"ctx+0x8c  = TCB+0x24c = 0x{ctx_pc:08x}  (task initial PC / SRR0)")

        # ctx+0x84 = TCB+0x244 (task initial LR) — set at 0x371dac from TCB[0x94][0xd4]
        tcb_0x94 = rw(sock, tcb + 0x94)
        lr_src = rw(sock, tcb_0x94 + 0xd4) if tcb_0x94 else 0
        ctx_lr = rw(sock, tcb + 0x244)
        print(f"TCB+0x094 = 0x{tcb_0x94:08x}")
        print(f"TCB[0x94]+0xd4 = 0x{lr_src:08x}  (source for ctx+0x84)")
        print(f"ctx+0x84  = TCB+0x244 = 0x{ctx_lr:08x}  (task initial LR)")
        print()

        if ctx_pc == 0:
            print("*** ctx+0x8c is 0 — task will start at address 0x0!")
        elif ctx_pc == 0x381a8c:
            print("ctx+0x8c = 0x381a8c — correct task entry")
        else:
            print(f"ctx+0x8c = 0x{ctx_pc:08x}")

        if ctx_lr == 0:
            print("*** ctx+0x84 is 0 — LR will be 0 when task runs fn_381a8c!")
        elif ctx_lr == 0x381a8c:
            print("ctx+0x84 = 0x381a8c — correct LR")
        else:
            print(f"ctx+0x84 = 0x{ctx_lr:08x}")

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
