#!/usr/bin/env python3
"""bp_verify.py -- Minimal breakpoint verification test for qemu-r1mx.

Launches QEMU, sets one SW BP at the bl-kernelInit call site (0x36c424),
resumes, and logs every raw byte received from the GDB stub for 10 seconds.

This script exists to verify our understanding of the QEMU GDB stub protocol
and to diagnose why smoke_test.py's wait_stop() may not be receiving T05.

Run from the repo root:
    .venv/bin/python firmware/scripts/bp_verify.py
"""

from __future__ import annotations

import socket
import struct
import subprocess
import sys
import time
from pathlib import Path

QEMU     = Path.home() / "src/qemu-r1mx/build/qemu-system-ppc"
FIRMWARE = Path(__file__).resolve().parents[2] / \
           "firmware/reverse/build_32/extracted/software.patched.r1mx.bin"
PORT     = 2345   # different from smoke_test to avoid conflicts
BP_ADDR  = 0x36C424   # bl 0x5a7f30 (kernelInit call site in usrInit)
TIMEOUT  = 15.0

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def cksum(payload: bytes) -> bytes:
    return f"{sum(payload) & 0xff:02x}".encode()

def send_pkt(s: socket.socket, cmd: str) -> None:
    b = cmd.encode()
    pkt = b"$" + b + b"#" + cksum(b)
    s.sendall(pkt)

def recv_ack(s: socket.socket) -> bytes:
    """Read one byte (the '+'/'-' ack). Return it."""
    s.settimeout(3.0)
    try:
        return s.recv(1)
    except socket.timeout:
        return b""

def recv_pkt(s: socket.socket, timeout: float = 5.0) -> str:
    """Read one '$..#xx' packet, send '+', return payload string."""
    s.settimeout(timeout)
    buf = bytearray()
    try:
        while True:
            b = s.recv(1)
            if not b:
                return ""
            if b == b"$":
                break
        while True:
            b = s.recv(1)
            if not b:
                return ""
            if b == b"#":
                s.recv(2)  # checksum
                break
            buf.extend(b)
        s.sendall(b"+")
        return buf.decode("latin-1")
    except socket.timeout:
        return ""

def cmd(s: socket.socket, payload: str, recv_timeout: float = 3.0) -> str:
    send_pkt(s, payload)
    ack = recv_ack(s)
    if ack not in (b"+", b"-"):
        print(f"  WARN: unexpected ack {ack!r} for {payload!r}")
    return recv_pkt(s, timeout=recv_timeout)

def get_nip(s: socket.socket) -> int:
    """Read NIP (register index 32) from 'g' packet."""
    h = cmd(s, "g", recv_timeout=5.0)
    if len(h) >= 33 * 8:
        return int(h[32*8:33*8], 16)
    return 0

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    if not QEMU.exists():
        print(f"ERROR: QEMU not found: {QEMU}"); return 1
    if not FIRMWARE.is_file():
        print(f"ERROR: firmware not found: {FIRMWARE}"); return 1

    print(f"[*] Starting QEMU (port {PORT})...")
    proc = subprocess.Popen(
        [str(QEMU),
         "-machine", "r1mx-virtex4",
         "-m", "2048",
         "-nographic",
         "-device", f"loader,file={FIRMWARE},addr=0x0,force-raw=on",
         "-S",
         "-gdb", f"tcp::{PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for GDB stub
        s = None
        for _ in range(30):
            try:
                s = socket.create_connection(("127.0.0.1", PORT), timeout=1.0)
                s.settimeout(None)
                break
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(0.3)
        if s is None:
            print("ERROR: GDB stub never became available"); return 1
        print("[*] Connected to GDB stub")

        # 1. Query initial stop
        reply = cmd(s, "?")
        print(f"[*] Initial stop reply: {reply[:40]!r}")

        # 2. Clear any stale BP at our target address
        r = cmd(s, f"z0,{BP_ADDR:x},4")
        print(f"[*] Clear stale BP at 0x{BP_ADDR:x}: {r!r}")

        # 3. Set SW BP
        r = cmd(s, f"Z0,{BP_ADDR:x},4")
        print(f"[*] Set Z0 BP at 0x{BP_ADDR:08x}: {r!r}")
        if r != "OK":
            print("    WARN: BP not accepted")

        # 4. Resume (do NOT read the '+' ack -- let raw_drain see it)
        print(f"[*] Resuming -- logging all bytes received for {TIMEOUT}s...")
        s.sendall(b"$c#63")

        # 5. Log every byte / packet received for TIMEOUT seconds
        s.settimeout(0.1)
        deadline = time.monotonic() + TIMEOUT
        raw_log: list[bytes] = []
        stop_reply: str = ""
        while time.monotonic() < deadline:
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                print("[*] Socket closed by QEMU")
                break
            raw_log.append(chunk)
            combined = b"".join(raw_log)
            # ack any packets we received so QEMU is not blocked
            pkt_count = combined.count(b"#")
            # send one '+' per '#' we haven't acked yet
            # (rough heuristic: send '+' for every chunk that has data)
            s.sendall(b"+" * chunk.count(b"#"))
            # check for stop reply
            if b"T05" in combined or b"T03" in combined or b"T02" in combined:
                # find the stop-reply packet
                for marker in (b"T05", b"T03", b"T02"):
                    idx = combined.find(b"$" + marker)
                    if idx >= 0:
                        end = combined.find(b"#", idx + 1)
                        if end >= 0:
                            stop_reply = combined[idx+1:end].decode("latin-1")
                            print(f"\n[*] STOP REPLY received after "
                                  f"{time.monotonic() - (deadline - TIMEOUT):.3f}s: "
                                  f"{stop_reply[:60]!r}")
                break

        # 6. Print raw byte log
        all_bytes = b"".join(raw_log)
        print(f"\n[*] Total bytes received in {TIMEOUT}s: {len(all_bytes)}")
        # show first 512 bytes as hex + printable
        preview = all_bytes[:512]
        print(f"[*] First {len(preview)} bytes (hex):")
        for i in range(0, len(preview), 32):
            row = preview[i:i+32]
            hex_part = " ".join(f"{b:02x}" for b in row)
            asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
            print(f"    {i:04x}  {hex_part:<96}  {asc_part}")

        # 7. Halt and read PC regardless
        s.settimeout(None)
        s.sendall(b"\x03")  # Ctrl-C
        time.sleep(0.3)
        try:
            s.settimeout(2.0)
            halt_data = s.recv(4096)
            s.sendall(b"+")
            print(f"\n[*] Halt reply: {halt_data[:80]!r}")
        except socket.timeout:
            print("\n[*] No halt reply (already stopped?)")

        nip = get_nip(s)
        print(f"[*] PC after halt: 0x{nip:08x}")

        # 8. Verdict
        print()
        if stop_reply.startswith("T05"):
            print("[PASS] BP fired -- T05 received")
            print(f"       stop reply: {stop_reply!r}")
        elif stop_reply:
            print(f"[INFO] Stop reply received (not T05): {stop_reply!r}")
        else:
            print(f"[FAIL] No T05 received in {TIMEOUT}s")
            print(f"       PC at halt = 0x{nip:08x}")
            if nip > BP_ADDR:
                print(f"       PC is past the BP address (0x{BP_ADDR:x}) -- BP silently bypassed")
            elif nip < BP_ADDR:
                print(f"       PC has not yet reached the BP address -- firmware still booting?")

        s.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    return 0

if __name__ == "__main__":
    sys.exit(main())
