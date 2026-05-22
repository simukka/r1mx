#!/usr/bin/env python3
"""
trace_descriptor_writer.py — Find what writes the root-task descriptor at 0x020390d0.

Connects to QEMU's GDB stub on :1234, sets a write watchpoint at 0x020390d0,
resumes execution, and logs every PC that fires the watchpoint along with
the surrounding register state. Continues until --max-hits is reached or
--timeout elapses (whichever comes first).

Usage:
    # Terminal A: start QEMU halted at PC=0x0 with GDB stub
    ./firmware/scripts/qemu_boot.sh --patched --debug

    # Terminal B:
    python3 firmware/scripts/trace_descriptor_writer.py

Constraints from re_reference.md:
  - QEMU PPC405 HW BPs broken; use SW BPs (Z0) or watchpoints (Z2/Z4)
  - Send '$c#63'; do NOT recv until wait_bp() drains it
  - Clear stale BPs at session start
"""

import argparse
import socket
import struct
import sys
import time


# ---------- GDB RSP protocol primitives ----------

def checksum(payload: bytes) -> bytes:
    return f"{sum(payload) & 0xff:02x}".encode()


def send_packet(sock: socket.socket, payload: str, no_ack: bool) -> None:
    pkt = b"$" + payload.encode() + b"#" + checksum(payload.encode())
    sock.sendall(pkt)
    if not no_ack:
        # Read the '+' or '-' acknowledgement.
        ack = sock.recv(1)
        if ack != b"+":
            raise RuntimeError(f"bad ack {ack!r} for packet {payload!r}")


def recv_packet(sock: socket.socket, no_ack: bool, timeout: float = 30.0) -> str:
    sock.settimeout(timeout)
    buf = bytearray()
    # Skip until '$'
    while True:
        b = sock.recv(1)
        if not b:
            raise RuntimeError("connection closed")
        if b == b"$":
            break
    # Read until '#' then 2 checksum chars
    while True:
        b = sock.recv(1)
        if not b:
            raise RuntimeError("connection closed mid-packet")
        if b == b"#":
            sock.recv(2)  # discard checksum
            break
        buf.extend(b)
    if not no_ack:
        sock.sendall(b"+")
    return buf.decode("latin-1")


def rsp_query(sock: socket.socket, payload: str, no_ack: bool) -> str:
    send_packet(sock, payload, no_ack)
    return recv_packet(sock, no_ack)


# ---------- Register decoding (PowerPC 32-bit, GDB's stock layout) ----------

# Stock GDB PowerPC reg ordering (`g` packet): r0..r31, pc, msr, cr, lr, ctr, xer
# Each register is 4 bytes (8 hex chars), big-endian.
PPC_REG_NAMES = (
    [f"r{i}" for i in range(32)] +
    ["pc", "msr", "cr", "lr", "ctr", "xer"]
)


def parse_g_packet(hexstr: str) -> dict:
    """Parse a 'g' reply. QEMU may include FPRs and extras — we only care about GPRs+pc+lr+ctr."""
    regs = {}
    # Each register is 8 hex chars (big-endian 4-byte word). Stop at the first non-hex slop.
    pos = 0
    for name in PPC_REG_NAMES:
        chunk = hexstr[pos:pos + 8]
        if len(chunk) < 8:
            break
        try:
            regs[name] = int(chunk, 16)
        except ValueError:
            break
        pos += 8
    return regs


# ---------- High-level operations ----------

def wait_for_stop(sock: socket.socket, no_ack: bool, timeout: float) -> str:
    """Block until a Txx stop reply is received. Returns the raw reply payload."""
    sock.settimeout(timeout)
    reply = recv_packet(sock, no_ack, timeout)
    return reply


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--addr", default="0x020390d0",
                    help="watchpoint address (default 0x020390d0)")
    ap.add_argument("--length", type=int, default=4,
                    help="watchpoint length in bytes (default 4)")
    ap.add_argument("--max-hits", type=int, default=20,
                    help="stop after this many watchpoint hits")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="overall wall-clock timeout in seconds")
    ap.add_argument("--per-hit-timeout", type=float, default=60.0,
                    help="max wait between hits (seconds)")
    args = ap.parse_args()

    addr = int(args.addr, 16) if isinstance(args.addr, str) else int(args.addr)
    print(f"[*] Connecting to GDB stub at {args.host}:{args.port}")
    sock = socket.create_connection((args.host, args.port), timeout=10)

    # Initial handshake — read first response from QEMU (if any).
    # QEMU's stub doesn't proactively send a stop reply at connect; instead the
    # very first '?' query returns the current stop signal.
    no_ack = False
    try:
        # Probe for connection by sending '?' which should give us a Txx reply
        # for the initial halt at PC=0.
        send_packet(sock, "?", no_ack)
        reply = recv_packet(sock, no_ack)
        print(f"[*] Initial stop reply: {reply!r}")

        # Switch to NoAck mode to avoid the '+' chatter — many stubs support this.
        ack_reply = rsp_query(sock, "QStartNoAckMode", no_ack)
        if ack_reply == "OK":
            no_ack = True
            print("[*] NoAck mode enabled")
        else:
            print(f"[*] NoAck mode rejected ({ack_reply!r}); staying in ACK mode")

        # Set the write watchpoint. RSP: Z2,addr,length  (write watchpoint)
        wp_cmd = f"Z2,{addr:x},{args.length}"
        wp_reply = rsp_query(sock, wp_cmd, no_ack)
        print(f"[*] Z2,{addr:x},{args.length} -> {wp_reply!r}")
        if wp_reply != "OK":
            print(f"[!] Watchpoint not accepted; aborting")
            return 1

        # Dump initial registers before resume.
        g_reply = rsp_query(sock, "g", no_ack)
        regs = parse_g_packet(g_reply)
        print(f"[*] Initial PC=0x{regs.get('pc', 0):08x}")

        # Resume and loop, capturing each watchpoint hit.
        wall_start = time.time()
        hits = 0
        seen_pcs = []
        while hits < args.max_hits:
            elapsed = time.time() - wall_start
            remaining = args.timeout - elapsed
            if remaining <= 0:
                print(f"[!] Wall-clock timeout ({args.timeout}s) reached")
                break

            # Send continue WITHOUT receiving anything — the stop reply will
            # arrive when the watchpoint fires.
            send_packet(sock, "c", no_ack)

            try:
                stop = wait_for_stop(sock, no_ack,
                                     min(args.per_hit_timeout, remaining))
            except socket.timeout:
                print(f"[!] No watchpoint hit within {args.per_hit_timeout}s "
                      f"(wall {elapsed:.1f}s)")
                # Interrupt the target so we can query state and exit cleanly.
                sock.sendall(b"\x03")
                try:
                    stop = wait_for_stop(sock, no_ack, 5.0)
                    print(f"[*] Interrupted: {stop!r}")
                except Exception:
                    pass
                break

            hits += 1
            t = time.time() - wall_start
            print(f"\n=== Hit #{hits} at wall t={t:.2f}s ===")
            print(f"  stop reply: {stop!r}")

            # Parse 'watch:' field if present.
            watch_addr = None
            for part in stop.split(";"):
                if part.startswith("watch:") or part.startswith("rwatch:") \
                        or part.startswith("awatch:"):
                    watch_addr = int(part.split(":", 1)[1], 16)
                    break

            # Dump GPRs/PC/LR/CTR.
            g_reply = rsp_query(sock, "g", no_ack)
            regs = parse_g_packet(g_reply)
            pc = regs.get("pc", 0)
            lr = regs.get("lr", 0)
            ctr = regs.get("ctr", 0)
            print(f"  PC = 0x{pc:08x}   LR = 0x{lr:08x}   CTR = 0x{ctr:08x}")
            if watch_addr is not None:
                print(f"  watch_addr = 0x{watch_addr:08x}")
            # Print r0..r12 — the volatile/argument set most likely involved in the store.
            for i in range(0, 13):
                v = regs.get(f"r{i}", 0)
                print(f"  r{i:<2d} = 0x{v:08x}", end="    " if (i % 4) != 3 else "\n")
            print()
            # And r28..r31 — non-volatile frame regs.
            for i in range(28, 32):
                v = regs.get(f"r{i}", 0)
                print(f"  r{i:<2d} = 0x{v:08x}", end="    ")
            print()

            # Read the 4 bytes at the watch target — the post-store value.
            mem_reply = rsp_query(sock, f"m{addr:x},4", no_ack)
            try:
                stored = int(mem_reply, 16)
                print(f"  *({addr:#x}) = 0x{stored:08x}")
            except ValueError:
                print(f"  *({addr:#x}) read returned: {mem_reply!r}")

            # Read the 4 instruction bytes at PC-4 (the instruction that just executed
            # — PPC405 reports the trap *after* the instruction that triggered it,
            # so the offending store is at PC-4 in most cases; but QEMU sometimes
            # reports PC at the store. We'll dump both candidates).
            for delta in (-4, 0):
                ip = (pc + delta) & 0xffffffff
                ireply = rsp_query(sock, f"m{ip:x},4", no_ack)
                try:
                    insn = int(ireply, 16)
                    print(f"  insn @ PC{delta:+d} (0x{ip:08x}) = 0x{insn:08x}")
                except ValueError:
                    print(f"  insn @ PC{delta:+d} (0x{ip:08x}) read: {ireply!r}")

            seen_pcs.append(pc)

        print(f"\n[*] Done. {hits} hit(s) recorded.")
        if seen_pcs:
            print(f"[*] PCs at watchpoint fires:")
            for i, pc in enumerate(seen_pcs):
                print(f"      #{i+1}: 0x{pc:08x}")

    finally:
        # Best-effort detach so QEMU keeps running for follow-up if user wants.
        try:
            send_packet(sock, "D", no_ack)
        except Exception:
            pass
        sock.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
