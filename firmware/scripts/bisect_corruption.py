#!/usr/bin/env python3
"""
bisect_corruption.py — Bisect the boot path to find WHEN memory at --addr
becomes corrupted. Set a series of breakpoints at known boot milestones,
let the system run to each one, check whether the watched memory has changed.

Outputs a table of milestone -> memory snapshot. The first milestone with a
changed snapshot is the function (or earlier) that introduces the corruption.
"""

import argparse
import socket
import sys
import time


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


def read_mem(sock, addr, length):
    r = query(sock, f"m{addr:x},{length:x}")
    out = []
    for i in range(0, len(r), 8):
        out.append(int(r[i:i+8], 16) if len(r[i:i+8]) == 8 else 0)
    return out


# Milestones from re_reference.md / annotations.r2
# Default list runs deep into kernelInit and the root-task path.
MILESTONES = [
    (0x0036C424, "usrInit: about to call kernelInit"),
    (0x005A7F30, "kernelInit entry"),
    (0x005A8170, "kernelInit: bl 0x5b2880 (WDB spawn area)"),
    # inside fn_5b2880
    (0x005B2884, "fn_5b2880: lis r11,0xea (start of body)"),
    (0x005B2908, "fn_5b2880: stw r21,0x28(r1) (just before bl 0x5b231c)"),
    (0x005B290C, "fn_5b2880: bl 0x5b231c (inner call)"),
    # inside fn_5b231c
    (0x005B2320, "fn_5b231c: lis r12,0xe3 (entry body)"),
    (0x005B2384, "fn_5b231c: ble 0x5b23a0 (branch check)"),
    # ble taken -> 0x5b23a0 path
    (0x005B23A0, "fn_5b231c: 0x5b23a0 lis r12,0xe4"),
    (0x005B23A8, "fn_5b231c: cmpwi r12,0 (check global)"),
    (0x005B23AC, "fn_5b231c: beq 0x5b23c8 (if null) -- beq fires here"),
    # beq taken -> 0x5b23c8 path (confirmed: fall-through 0x5b23b0 times out)
    (0x005B23C8, "fn_5b231c: 0x5b23c8 (beq target)"),
    (0x005B23D0, "fn_5b231c: lwz r12,0x94(r31)"),
    (0x005B23E0, "fn_5b231c: stw r10,0x18(r1) (post bne)"),
    (0x005B2480, "fn_5b231c: lwz r4,-0x4bb4(r4)"),
    (0x005B2484, "fn_5b231c: bl 0x498cd8"),
    (0x005B2488, "fn_5b231c: after bl 498cd8"),
    (0x005B24BC, "fn_5b231c: bl 0x371cd0 (TCB setup)"),
    # inside fn_371cd0
    (0x00371CF4, "fn_371cd0: bl 0x496698 (memset TCB+1c0)"),
    (0x00371CF8, "fn_371cd0: after memset (check r9)"),
    (0x00371D00, "fn_371cd0: cmpwi r9,0 (alloc check)"),
    (0x00371D04, "fn_371cd0: bne 0x371d14"),
    (0x00371D08, "fn_371cd0: bl 0x371ec8 (r9==0 path)"),
    (0x00371D0C, "fn_371cd0: after bl 371ec8 (r9==0)"),
    # 0x371d10: b 0x371d24 (unconditional; skips 0x371d14)
    (0x00371D24, "fn_371cd0: lwz r12,0x98(r31) (post-alloc merge)"),
    (0x00371D44, "fn_371cd0: stw r30,0x1c4(r31) (stack ptr store)"),
    (0x00371D4C, "fn_371cd0: stw r11,0(r30)  <-- writes to aligned stack"),
    (0x00371D58, "fn_371cd0: cmplw r10,r28 (RTTI check)"),
    (0x00371D5C, "fn_371cd0: b 0x371d78 (Patch#55 skip)"),
    (0x00371D78, "fn_371cd0: at 0x371d78 (post RTTI)"),
    (0x00371D90, "fn_371cd0: bl 0x371c74 (arg copy helper)"),
    (0x00371D94, "fn_371cd0: after bl 371c74"),
    (0x00371DB8, "fn_371cd0: epilogue: lwz r0,0x24(r1)"),
    (0x00371DBC, "fn_371cd0: epilogue: lmw r28,0x10(r1)"),
    (0x00371DC0, "fn_371cd0: epilogue: mtlr r0"),
    (0x00371DC4, "fn_371cd0: epilogue: addi r1,r1,0x20"),
    (0x00371DC8, "fn_371cd0: blr (about to return to 5b24c0)"),
    (0x005B24C0, "fn_5b231c: after bl 371cd0 <-- LR target"),
    (0x005B286C, "fn_5b231c: epilogue (returning)"),
    (0x005B2910, "fn_5b2880: lwz r0,0x64(r1) (return from 5b231c)"),
    (0x005B2920, "fn_5b2880: blr (about to return to 0x5a8174)"),
    # back in kernelInit
    (0x005A8174, "kernelInit: lis r9,0xea  (after bl 5b2880 returns)"),
    (0x005A8180, "kernelInit: stw r22,0(r31)  <-- suspect"),
    (0x005A8190, "kernelInit: deferred ctor NOP (Patch #56) site"),
    (0x005A8194, "kernelInit: WDB network init NOP (Patch #57) site"),
    (0x005A838C, "kernelInit: RTTI assertion loop NOP (Patch #55) site"),
    (0x005A2A28, "WDB task spawn (per re_reference)"),
    (0x0037C440, "rootTask entry"),
    (0x00381A8C, "fn_381a8c root task wrapper (Patch #53a target)"),
    (0x00382E80, "fn_382e80 main dispatcher"),
    (0x0036B3DC, "usrWdbInit entry"),
    (0x0036B7EC, "bsp_init_caller (calls usrWdbInit)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", default="0x0", help="watched address")
    ap.add_argument("--length", type=int, default=32,
                    help="bytes to watch (default 32)")
    ap.add_argument("--bp-timeout", type=float, default=15.0)
    args = ap.parse_args()

    addr = int(args.addr, 16)
    sock = socket.create_connection((args.host, args.port), timeout=10)

    try:
        # Halt if running
        send(sock, "?")
        s = recv(sock)
        if "T05" not in s and "T02" not in s:
            sock.sendall(b"\x03")
            recv(sock, 5)

        # Take initial snapshot
        initial = read_mem(sock, addr, args.length)
        print(f"[*] Initial memory @ 0x{addr:08x}:")
        for i, v in enumerate(initial):
            print(f"      +{i*4:02x}: 0x{v:08x}")
        print()

        last_snapshot = initial[:]

        for ms_addr, ms_label in MILESTONES:
            # Set BP at milestone
            r = query(sock, f"Z0,{ms_addr:x},4")
            if r != "OK":
                print(f"[!] Failed to set BP at 0x{ms_addr:08x}: {r!r}")
                continue

            # Continue
            send(sock, "c")
            try:
                stop = recv(sock, args.bp_timeout)
            except socket.timeout:
                print(f"[!] BP at 0x{ms_addr:08x} ({ms_label}) did NOT fire within {args.bp_timeout}s — STOPPING")
                # Interrupt
                sock.sendall(b"\x03")
                try:
                    recv(sock, 5)
                except Exception:
                    pass
                # Read memory at current point
                snap = read_mem(sock, addr, args.length)
                changed_offsets = [i for i in range(len(snap)) if snap[i] != initial[i]]
                if changed_offsets:
                    print(f"    Memory had been corrupted at offsets: {[hex(o*4) for o in changed_offsets]}")
                # Clear BP
                query(sock, f"z0,{ms_addr:x},4")
                break

            # Clear BP immediately
            query(sock, f"z0,{ms_addr:x},4")

            # Read memory snapshot
            snap = read_mem(sock, addr, args.length)
            changes_since_init = [(i*4, initial[i], snap[i])
                                  for i in range(len(snap))
                                  if snap[i] != initial[i]]
            changes_since_last = [(i*4, last_snapshot[i], snap[i])
                                  for i in range(len(snap))
                                  if snap[i] != last_snapshot[i]]

            print(f"  [REACHED] 0x{ms_addr:08x} {ms_label}")
            if changes_since_init:
                print(f"    Total changes from init: {len(changes_since_init)}")
                for off, old, new in changes_since_init[:8]:
                    print(f"      +{off:02x}: 0x{old:08x} -> 0x{new:08x}")
            else:
                print(f"    [no changes]")
            if changes_since_last and last_snapshot != initial:
                print(f"    New changes since last milestone: {len(changes_since_last)}")

            last_snapshot = snap[:]

    finally:
        try:
            send(sock, "D")
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
