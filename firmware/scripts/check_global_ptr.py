#!/usr/bin/env python3
"""Read runtime value of mem[0xe293f4] (fn_371c74 indirect call target)."""
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

def read_word(sock, addr):
    r = query(sock, f"m{addr:x},4")
    try: return int(r, 16)
    except: return None

def main():
    sock = socket.create_connection(("127.0.0.1", 1234), timeout=10)
    try:
        send(sock, "?")
        recv(sock)

        # Set BP at fn_371c74 entry (0x371c74) to catch the call
        r = query(sock, "Z0,371c74,4")
        if r != "OK":
            print(f"[!] BP failed: {r!r}")
            return
        send(sock, "c")
        try:
            recv(sock, 60)
        except socket.timeout:
            print("[!] Timed out waiting for BP")
            return
        query(sock, "z0,371c74,4")

        # Read the global pointer
        ptr_val = read_word(sock, 0xe293f4)
        print(f"Runtime mem[0xe293f4] = 0x{ptr_val or 0:08x}")
        if ptr_val == 0x542974:
            print("  => Points to fn_542910's epilogue mid-point — WILL corrupt r1!")
            print("  => This is the root cause of the boot crash.")
        elif ptr_val == 0:
            print("  => NULL — fn_371c74 takes the r31=-1 path (safe)")
        else:
            print(f"  => Unexpected value")

        # Also check the surrounding words
        print(f"\nContext around 0xe293f4:")
        for off in [-8, -4, 0, 4, 8]:
            v = read_word(sock, 0xe293f4 + off)
            m = " <-- fn ptr" if off == 0 else ""
            print(f"  mem[0x{0xe293f4+off:08x}] = 0x{v or 0:08x}{m}")

    finally:
        try: send(sock, "D")
        except: pass
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
