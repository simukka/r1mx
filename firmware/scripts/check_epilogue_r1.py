#!/usr/bin/env python3
"""
check_epilogue_r1.py — Capture r1 at fn_371cd0 epilogue entry (0x371db8)
before any restore, plus read the LR slot and a few words around it.
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

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        # BP at entry to get baseline r1
        r = query(sock, "Z0,371cd0,4")
        if r != "OK": print(f"[!] entry BP: {r!r}")
        send(sock, "c")
        recv(sock, 60)
        query(sock, "z0,371cd0,4")
        g = parse_g(query(sock, "g"))
        entry_r1 = g["r1"]
        frame_base = entry_r1 - 0x20  # after stwu will be entry_r1-0x20
        print(f"Entry: r1={entry_r1:08x}, frame_base will be {frame_base:08x}")
        print(f"  Expected LR slot (frame_base+0x24) = 0x{frame_base+0x24:08x}")
        print(f"  lr reg at entry = 0x{g['lr']:08x}")
        print()

        # BP at epilogue start: 0x371db8  (lwz r0, 0x24(r1))
        r = query(sock, "Z0,371db8,4")
        if r != "OK": print(f"[!] epilogue BP: {r!r}")
        send(sock, "c")
        recv(sock, 60)
        query(sock, "z0,371db8,4")
        g2 = parse_g(query(sock, "g"))
        ep_r1 = g2["r1"]
        lr_slot = ep_r1 + 0x24
        lr_slot_val = read_word(sock, lr_slot)
        print(f"Epilogue (0x371db8): r1={ep_r1:08x}, lr_slot=r1+0x24=0x{lr_slot:08x} → 0x{lr_slot_val or 0:08x}")
        print(f"  delta r1 from entry: {ep_r1 - (entry_r1 - 0x20):+d}")
        print()

        # Dump stack words around the lr slot
        print("Stack around r1+0x24:")
        for off in [-0x10, -0xc, -8, -4, 0, 4, 8, 0xc, 0x10, 0x14, 0x20, 0x24]:
            v = read_word(sock, ep_r1 + off)
            m = " <-- lr_slot (r1+0x24)" if off == 0x24 else (
                " <-- caller SP" if off == 0x20 else (
                " <-- r1" if off == 0 else ""))
            print(f"  mem[r1+{off:+4x}] = mem[0x{ep_r1+off:08x}] = 0x{v or 0:08x}{m}")

        if ep_r1 != frame_base:
            print(f"\n*** r1 CHANGED inside fn_371cd0!")
            print(f"    Expected {frame_base:08x}, got {ep_r1:08x} (delta {ep_r1-frame_base:+d})")

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
