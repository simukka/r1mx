#!/usr/bin/env python3
"""
wdb_probe.py — minimal Wind River WDB agent client (ONC-RPC over UDP)

The RED ONE MX VxWorks 6.4 image runs the WDB target agent unconditionally
(see firmware/reverse/build_32/debug_interfaces.md).  It listens on UDP 17185
at the camera's boot IP 192.168.0.2 and is *unauthenticated* — anyone on the
subnet gets full target memory read/write.

This is a self-contained client (stdlib socket/struct only — no pyusb, no
Metasploit) implementing just enough WDB to:

  * TARGET_CONNECT  — prove the agent is live, read agent/runtime/CPU info,
                      the live bootline, and the RAM layout.
  * MEM_READ        — read arbitrary target memory (cross-checks the static
                      RE map against live RAM).
  * MEM_WRITE       — gated behind --write + --yes-i-really-mean-it; the write
                      request struct is UNVERIFIED, so it is off by default.

Wire format reproduced from the canonical open-source reference
(Metasploit's Msf::Exploit::Remote::WDBRPC mixin):
  - RPC program 0x55555555, version 1, UDP 17185
  - 40-byte RPC call header + 12-byte WDB wrapper (checksum, size, seqno)
  - checksum = ~(sum of 16-bit BE words), computed with flag+xid still zero
  - connect reply: skip 36 header bytes; mem-read reply: data = reply[48:]

Network setup (host side, needs sudo — run yourself, e.g. with `! `):
  sudo ip addr add 192.168.0.1/24 dev <iface>   # camera is 192.168.0.2
Keep this on the iface physically wired to the camera so your normal LAN
(e.g. 10.0.1.0/24 on enp5s0) is untouched.  VxWorks may ignore ICMP, so don't
rely on ping — check `ip neigh` for an ARP entry, or just run this tool.

Usage:
  python3 wdb_probe.py                       # connect + info + self-test reads
  python3 wdb_probe.py --read 0xE9C4BC --len 16
  python3 wdb_probe.py --host 192.168.0.2 --selftest
  python3 wdb_probe.py --write 0xADDR --bytes 01000000 --yes-i-really-mean-it
"""

import argparse
import datetime
import os
import random
import socket
import struct
import sys

WDB_PROG = 0x55555555
WDB_VERS = 1
WDB_PORT = 17185
WDB_HOST = "192.168.0.2"

# WDB procedure numbers
P_CONNECT = 1
P_DISCONNECT = 2
P_MEM_READ = 10
P_MEM_WRITE = 11

# RE-map addresses to validate live RAM against static analysis.
# (addr, length, label, expected_first_u32_or_None)
SELFTEST_READS = [
    (0xE9C4BC, 16, "BSS: WDB UDP port (expect 0x00004321)", 0x00004321),
    (0xD5C608, 96, "String: VxWorks boot config (h=192.168.0.1 ...)", None),
    (0xD35928, 32, "String: DEBUG.USB.CONNECTION", None),
]

_seqno = 0


# --------------------------------------------------------------------------- #
# Capture log (tee to stdout + file), mirrors probe_serial.py.
# --------------------------------------------------------------------------- #
_THIS = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_DIR = os.path.normpath(
    os.path.join(_THIS, "..", "reverse", "build_32", "captures")
)


class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._fh = open(path, "w", encoding="utf-8")
        self.log(f"# wdb_probe.py capture — {_utc()}")

    def log(self, msg=""):
        print(msg)
        self._fh.write(msg + "\n")
        self._fh.flush()

    def close(self):
        self._fh.close()


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def hexdump(data, base=0, indent="    "):
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{indent}{base + i:08X}  {hex_part:<48}  {asc_part}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# WDB wire format
# --------------------------------------------------------------------------- #
def _checksum(data):
    """~(sum of 16-bit big-endian words), one fold, low 16 bits."""
    s = 0
    for i in range(0, len(data) - (len(data) & 1), 2):
        s += (data[i] << 8) | data[i + 1]
    s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def build_request(proc, data=b""):
    global _seqno
    _seqno += 1
    pkt = bytearray(
        struct.pack(">10I", 0, 0, 2, WDB_PROG, WDB_VERS, proc, 0, 0, 0, 0)
        + struct.pack(">3I", 0, 0, _seqno)   # checksum, size, seqno
        + data
    )
    struct.pack_into(">I", pkt, 44, len(pkt) - 4)        # size excludes xid
    struct.pack_into(">H", pkt, 42, _checksum(bytes(pkt)))  # flag+xid still 0
    struct.pack_into(">H", pkt, 40, 0xFFFF)              # checksum-present flag
    struct.pack_into(">I", pkt, 0, random.randint(0, 0xFFFFFFFF))  # xid
    return bytes(pkt)


class _Cursor:
    """Sequential XDR-ish decoder over a reply buffer."""

    def __init__(self, data, off=0):
        self.d = data
        self.i = off

    def remaining(self):
        return len(self.d) - self.i

    def u32(self):
        v = struct.unpack_from(">I", self.d, self.i)[0]
        self.i += 4
        return v

    def boolean(self):
        return self.u32() != 0

    def string(self):
        slen = self.u32()
        if slen == 0:
            return ""
        pad = (slen + 3) & ~3
        raw = self.d[self.i:self.i + pad]
        self.i += pad
        return raw.split(b"\x00")[0].decode("latin-1", "replace")

    def arr_u32(self):
        n = self.u32()
        return [self.u32() for _ in range(n)]


# --------------------------------------------------------------------------- #
# Transport
# --------------------------------------------------------------------------- #
def _send_recv(sock, host, port, pkt, timeout, retries):
    last_err = None
    for _ in range(retries + 1):
        try:
            sock.sendto(pkt, (host, port))
            sock.settimeout(timeout)
            res, _src = sock.recvfrom(65535)
            return res
        except socket.timeout as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return None


def parse_connect_reply(res):
    """Connect reply: 36-byte header, then the runtime info fields."""
    if len(res) < 40:
        raise ValueError(f"connect reply too short ({len(res)} bytes)")
    c = _Cursor(res, 36)
    info = {}
    info["agent_ver"] = c.string()
    info["agent_mtu"] = c.u32()
    info["agent_mod"] = c.u32()
    info["rt_type"] = c.u32()
    info["rt_vers"] = c.string()
    info["rt_cpu_type"] = c.u32()
    info["rt_has_fpp"] = c.boolean()
    info["rt_has_wp"] = c.boolean()
    info["rt_page_size"] = c.u32()
    info["rt_endian"] = c.u32()
    info["rt_bsp_name"] = c.string()
    info["rt_bootline"] = c.string()
    info["rt_membase"] = c.u32()
    info["rt_memsize"] = c.u32()
    info["rt_region_count"] = c.u32()
    info["rt_regions"] = c.arr_u32()
    return info


def wdb_connect(sock, host, port, log):
    # courtesy disconnect first (agent allows one client at a time)
    try:
        _send_recv(sock, host, port, build_request(P_DISCONNECT), 1.0, 1)
    except socket.timeout:
        pass
    data = struct.pack(">3I", 2, 0, 0)   # connect request body
    res = _send_recv(sock, host, port, build_request(P_CONNECT, data), 5.0, 2)
    if res is None:
        raise RuntimeError("no reply to TARGET_CONNECT")
    log.log(f"  connect reply: {len(res)} bytes")
    return parse_connect_reply(res)


def wdb_memread(sock, host, port, addr, length):
    """Returns the raw bytes at addr (reply[48:])."""
    data = struct.pack(">3I", addr & 0xFFFFFFFF, length, 0)
    res = _send_recv(sock, host, port, build_request(P_MEM_READ, data),
                     0.5, 120)
    if res is None or len(res) <= 48:
        raise RuntimeError(f"short/no mem-read reply at 0x{addr:08X}")
    return res[48:48 + length]


def wdb_memwrite(sock, host, port, addr, payload):
    """UNVERIFIED write-request struct — only reached via explicit opt-in."""
    data = struct.pack(">3I", addr & 0xFFFFFFFF, len(payload), 0) + payload
    res = _send_recv(sock, host, port, build_request(P_MEM_WRITE, data),
                     1.0, 5)
    return res


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
CPU_TYPES = {  # partial VxWorks cpuType map for readability
    0x0B: "PPC405", 0x0C: "PPC440", 0x09: "PPC603", 0x0A: "PPC604",
}


def report_info(info, log):
    log.log("\n=== WDB TARGET INFO ===")
    log.log(f"  agent version : {info['agent_ver']}")
    log.log(f"  agent MTU     : {info['agent_mtu']}")
    log.log(f"  runtime type  : {info['rt_type']}")
    log.log(f"  runtime vers  : {info['rt_vers']}")
    cpu = info["rt_cpu_type"]
    log.log(f"  CPU type      : {cpu} ({CPU_TYPES.get(cpu, 'unknown')})")
    log.log(f"  has FPP / WP  : {info['rt_has_fpp']} / {info['rt_has_wp']}")
    log.log(f"  page size     : {info['rt_page_size']}")
    log.log(f"  endianness    : {'big' if info['rt_endian'] else 'little'}")
    log.log(f"  BSP name      : {info['rt_bsp_name']}")
    log.log(f"  bootline      : {info['rt_bootline']}")
    log.log(f"  mem base/size : 0x{info['rt_membase']:08X} / "
            f"0x{info['rt_memsize']:08X}")
    log.log(f"  regions       : {info['rt_region_count']} "
            f"{[hex(r) for r in info['rt_regions']]}")


def run_selftest(sock, host, port, log):
    log.log("\n=== MEM_READ self-test (live RAM vs static RE map) ===")
    ok = True
    for addr, length, label, expect in SELFTEST_READS:
        try:
            buf = wdb_memread(sock, host, port, addr, length)
        except Exception as e:
            log.log(f"  0x{addr:08X}  {label}\n    READ FAILED: {e}")
            ok = False
            continue
        log.log(f"  0x{addr:08X}  {label}")
        log.log(hexdump(buf, base=addr))
        if expect is not None and len(buf) >= 4:
            got = struct.unpack_from(">I", buf, 0)[0]
            verdict = "MATCH" if got == expect else "MISMATCH"
            if got != expect:
                ok = False
            log.log(f"    first u32 = 0x{got:08X}  expected 0x{expect:08X}"
                    f"  -> {verdict}")
    return ok


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="RED ONE MX WDB agent probe")
    ap.add_argument("--host", default=WDB_HOST, help="Camera IP")
    ap.add_argument("--port", type=int, default=WDB_PORT, help="WDB UDP port")
    ap.add_argument("--read", metavar="ADDR",
                    help="Read memory at ADDR (hex ok), then exit")
    ap.add_argument("--len", type=int, default=64, help="Bytes for --read")
    ap.add_argument("--selftest", action="store_true",
                    help="Read RE-map addresses and validate (default if no "
                         "--read/--write)")
    ap.add_argument("--write", metavar="ADDR",
                    help="Write memory at ADDR (hex ok) — UNVERIFIED/gated")
    ap.add_argument("--bytes", metavar="HEX",
                    help="Hex byte string for --write, e.g. 01000000")
    ap.add_argument("--yes-i-really-mean-it", action="store_true",
                    help="Required to actually perform a --write to live RAM")
    ap.add_argument("--log-dir", default=DEFAULT_LOG_DIR)
    args = ap.parse_args()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ")
    log = Logger(os.path.join(args.log_dir, f"wdb_{stamp}.log"))
    log.log(f"target={args.host}:{args.port}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rc = 0
    try:
        log.log("\n=== WDB TARGET CONNECT ===")
        try:
            info = wdb_connect(sock, args.host, args.port, log)
        except Exception as e:
            log.log(f"  CONNECT FAILED: {e}")
            log.log("  The WDB agent did not answer. Check: cable, host IP "
                    "192.168.0.1/24 on the right iface, `ip neigh` for an ARP "
                    "entry for 192.168.0.2, and that the camera is booted.")
            return 2
        report_info(info, log)

        if args.write:
            addr = int(args.write, 0)
            if not args.bytes or not args.__dict__["yes_i_really_mean_it"]:
                log.log("\nREFUSING to write: need --bytes HEX and "
                        "--yes-i-really-mean-it. (The MEM_WRITE request struct "
                        "is unverified; writing wrong data to live camera RAM "
                        "is risky.)")
                return 3
            payload = bytes.fromhex(args.bytes)
            log.log(f"\n=== MEM_WRITE 0x{addr:08X} <- {payload.hex()} "
                    f"(UNVERIFIED) ===")
            wdb_memwrite(sock, args.host, args.port, addr, payload)
            back = wdb_memread(sock, args.host, args.port, addr, len(payload))
            log.log("  read-back:")
            log.log(hexdump(back, base=addr))
            rc = 0 if back == payload else 4
        elif args.read:
            addr = int(args.read, 0)
            buf = wdb_memread(sock, args.host, args.port, addr, args.len)
            log.log(f"\n=== MEM_READ 0x{addr:08X} ({len(buf)} bytes) ===")
            log.log(hexdump(buf, base=addr))
        else:
            rc = 0 if run_selftest(sock, args.host, args.port, log) else 5
    finally:
        try:
            _send_recv(sock, args.host, args.port,
                       build_request(P_DISCONNECT), 1.0, 0)
        except Exception:
            pass
        sock.close()
        log.close()

    sys.exit(rc)


if __name__ == "__main__":
    main()
