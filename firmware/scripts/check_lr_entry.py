#!/usr/bin/env python3
"""
check_lr_entry.py — Check fn_371cd0's LR save slot at three points:
  1. Right after entry prologue (0x371ce4, after stw r0,0x24(r1))
  2. After memset call returns (0x371cf8)
  3. At blr (0x371dc8)
Resolves the "where did LR=0 come from" question.
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

def read_word(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try: return int(r, 16)
    except: return None

def wait_bp(sock, addr, label, timeout=60):
    r = query(sock, f"Z0,{addr:x},4")
    if r != "OK":
        print(f"[!] Failed to set BP at {label}: {r!r}")
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
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        # BP1: right after stw r0,0x24(r1) at 0x371ce0 — next insn is addi r31,r3,0 at 0x371ce4
        regs1 = wait_bp(sock, 0x371ce4, "0x371ce4 (after LR save)")
        if not regs1: return 1
        sp1 = regs1["r1"]
        lr_slot = sp1 + 0x24
        lr_at_entry = read_word(sock, lr_slot)
        print(f"=== BP1: after prologue LR save (0x371ce4) ===")
        print(f"  r1        = 0x{sp1:08x}")
        print(f"  lr reg    = 0x{regs1['lr']:08x}")
        print(f"  LR slot   = r1+0x24 = 0x{lr_slot:08x} → 0x{lr_at_entry or 0:08x}")
        # dump a few words around the slot
        for off in [-4, 0, 4, 8]:
            v = read_word(sock, lr_slot + off)
            m = " <-- LR" if off == 0 else ""
            print(f"    mem[0x{lr_slot+off:08x}] = 0x{v or 0:08x}{m}")
        print()

        # BP2: after memset returns (0x371cf8), see if LR slot changed
        regs2 = wait_bp(sock, 0x371cf8, "0x371cf8 (after memset)")
        if not regs2: return 1
        sp2 = regs2["r1"]
        lr_after_memset = read_word(sock, lr_slot)
        print(f"=== BP2: after memset (0x371cf8) ===")
        print(f"  r1        = 0x{sp2:08x}  (delta from BP1: {sp2-sp1:+d})")
        print(f"  LR slot 0x{lr_slot:08x} → 0x{lr_after_memset or 0:08x}")
        if lr_after_memset != lr_at_entry:
            print(f"  *** LR SLOT CHANGED: 0x{lr_at_entry or 0:08x} → 0x{lr_after_memset or 0:08x} ***")
        else:
            print(f"  LR slot unchanged")
        print()

        # BP3: at blr
        regs3 = wait_bp(sock, 0x371dc8, "0x371dc8 (blr)")
        if not regs3: return 1
        sp3 = regs3["r1"]
        # at blr, r1 is already caller_sp (post addi r1,r1,0x20)
        # so frame_base = sp3 - 0x20
        frame_base = sp3 - 0x20
        actual_lr_slot = frame_base + 0x24
        lr_at_blr_slot = read_word(sock, actual_lr_slot)
        print(f"=== BP3: at blr (0x371dc8) ===")
        print(f"  r1        = 0x{sp3:08x}  (post addi; frame_base = 0x{frame_base:08x})")
        print(f"  lr reg    = 0x{regs3['lr']:08x}  (what blr will jump to)")
        print(f"  real LR slot = frame_base+0x24 = 0x{actual_lr_slot:08x} → 0x{lr_at_blr_slot or 0:08x}")
        print(f"  BP1 LR slot  = 0x{lr_slot:08x} → 0x{read_word(sock, lr_slot) or 0:08x}")
        print()
        if actual_lr_slot != lr_slot:
            print(f"  *** SLOT MISMATCH: entry r1=0x{sp1:08x} → slot=0x{lr_slot:08x}")
            print(f"                     epilogue r1=0x{frame_base:08x} → slot=0x{actual_lr_slot:08x}")

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
