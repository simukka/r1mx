#!/usr/bin/env python3
"""Confirm/refute QEMU SW BP step-over bug.

Steps:
  1. Arm Z0 at 0x5A7F30.
  2. `c` → expect halt at 0x5A7F30. Record PC.
  3. `c` again → if PC == 0x5A7F30, step-over via `c` is BROKEN.
  4. `s` (single-step) → record PC. Should be 0x5A7F34 if `s` works.
  5. If `s` fails too: remove BP (z0), `s`, check PC, re-arm.
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
def get_pc(sock):
    h = query(sock, "g")
    r = h[32*8:32*8+8]
    return int(r, 16) if len(r)==8 else 0

ADDR = 0x5A7F30

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?"); recv(sock)
        print(f"[+] start PC = 0x{get_pc(sock):08x}")
        r = query(sock, f"Z0,{ADDR:x},4"); print(f"[+] Z0 0x{ADDR:x}: {r}")

        send(sock, "c"); recv(sock, 30)
        pc1 = get_pc(sock); print(f"[1] after first 'c': PC = 0x{pc1:08x}")

        send(sock, "c"); recv(sock, 10)
        pc2 = get_pc(sock); print(f"[2] after second 'c': PC = 0x{pc2:08x}")
        if pc2 == pc1:
            print("    >>> `c` step-over from SW BP is BROKEN (PC didn't advance)")
        else:
            print("    >>> `c` step-over works fine")

        # Try `s` (single-step) while BP still armed
        send(sock, "s"); recv(sock, 10)
        pc3 = get_pc(sock); print(f"[3] after 's' (BP still armed): PC = 0x{pc3:08x}")

        # Remove BP, try `s` from same PC
        if pc3 == pc2:
            print("    >>> `s` also stuck while BP armed")
            query(sock, f"z0,{ADDR:x},4")
            print("[*] removed BP, retrying `s`")
            send(sock, "s"); recv(sock, 10)
            pc4 = get_pc(sock); print(f"[4] after 's' (BP removed): PC = 0x{pc4:08x}")
            if pc4 != pc2:
                print("    >>> workaround: remove-BP + `s` advances PC")
            else:
                print("    >>> EVEN remove+`s` failed — deeper issue")
        else:
            print("    >>> `s` advanced — workaround is to `s` past BPs instead of `c`")
        return 0
    finally:
        try: query(sock, f"z0,{ADDR:x},4")
        except: pass
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
