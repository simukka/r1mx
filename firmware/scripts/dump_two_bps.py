#!/usr/bin/env python3
"""
dump_two_bps.py — Fire BP at addr1, read SP and compute LR-save-slot addr,
then fire BP at addr2 and read that saved slot to see if/when LR is corrupted.
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

PPC_REG_NAMES = ([f"r{i}" for i in range(32)] + ["pc","msr","cr","lr","ctr","xer"])

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

def read_word(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try: return int(r, 16)
    except: return 0

def wait_bp(sock, addr, label, timeout):
    r = query(sock, f"Z0,{addr:x},4")
    if r != "OK":
        print(f"[!] Failed to set BP at {label}: {r}")
        return None
    send(sock, "c")
    try:
        stop = recv(sock, timeout)
    except socket.timeout:
        print(f"[!] BP {label} timed out")
        return None
    query(sock, f"z0,{addr:x},4")
    g = query(sock, "g")
    return parse_g(g)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    sock = socket.create_connection((args.host, args.port), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        # BP1: 0x371d44 — get SP and compute LR-save-slot
        regs1 = wait_bp(sock, 0x371d44, "0x371d44 (stw r30 in fn_371cd0)", args.timeout)
        if not regs1: return 1
        sp1 = regs1["r1"]
        # fn_371cd0 frame base = sp1, LR saved at sp1 + 0x24
        lr_slot = sp1 + 0x24
        lr_val1 = read_word(sock, lr_slot)
        print(f"\n=== BP1 at 0x371d44 ===")
        print(f"  r1  (SP)     = 0x{sp1:08x}")
        print(f"  r30 (stk_top)= 0x{regs1['r30']:08x}")
        print(f"  r31 (TCB)    = 0x{regs1['r31']:08x}")
        print(f"  LR save slot = 0x{lr_slot:08x} → 0x{lr_val1:08x}")
        print()

        # BP2: 0x371dc8 — blr, read same LR slot
        regs2 = wait_bp(sock, 0x371dc8, "0x371dc8 (blr)", args.timeout)
        if not regs2: return 1
        sp2 = regs2["r1"]
        lr_val2 = read_word(sock, lr_slot)
        lr_reg = regs2["lr"]
        print(f"=== BP2 at 0x371dc8 (blr) ===")
        print(f"  r1  (SP)     = 0x{sp2:08x}")
        print(f"  LR reg       = 0x{lr_reg:08x}  (what blr will jump to)")
        print(f"  LR save slot = 0x{lr_slot:08x} → 0x{lr_val2:08x}")
        print()

        if lr_val2 != lr_val1:
            print(f"  *** LR SLOT CORRUPTED: 0x{lr_val1:08x} → 0x{lr_val2:08x} ***")
        else:
            print(f"  LR slot unchanged; LR reg = 0x{lr_reg:08x}")

        # Also read a few words around the LR slot
        print("\n  Stack area around LR slot:")
        for off in [-8, -4, 0, 4, 8, 0xc, 0x10]:
            v = read_word(sock, lr_slot + off)
            marker = " <-- LR slot" if off == 0 else ""
            print(f"    mem[0x{lr_slot+off:08x}] = 0x{v:08x}{marker}")

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
