#!/usr/bin/env python3
"""
rsp.py — shared GDB Remote Serial Protocol (RSP) client for the RED ONE MX
PPC405 work. One client, two targets:

  * QEMU's gdbstub        (firmware/scripts/qemu_boot.sh --debug, TCP :1234)
  * XMD's GDB server      (live silicon over JTAG; `connect ppc hw` in the
                           WinXP VM, reached from the host via a VirtualBox
                           NAT port-forward — see host_xmd_bridge.md)

Both speak the same protocol and serve the same PPC core register block, so the
same code drives emulator and hardware — which is what makes the lock-step
differential harness (lockstep_diff.py) possible.

This module is the de-duplicated home of the `cksum/send/recv/query/parse_g`
logic that was copy-pasted across ~18 probe scripts. Those scripts can be
converted to:

    from rsp import RSP, PPC_REG_NAMES
    t = RSP("127.0.0.1", 1234); t.connect()
    regs = t.regs(); print(hex(regs["pc"]))

READ-ONLY BY DEFAULT — critical on real hardware:
  * Memory/register *writes* and CPU *reset* are disabled unless the client is
    constructed with allow_write=True. The default raises on any write attempt.
  * Breakpoints default to HARDWARE (Z1, PPC405 IAC registers) which do NOT
    modify target memory. Software breakpoints (Z0) patch a trap instruction
    into memory and are therefore unsafe on the camera; only request them
    explicitly (hw=False), and only against QEMU.
"""

import socket


PPC_REG_NAMES = (
    [f"r{i}" for i in range(32)]
    + ["pc", "msr", "cr", "lr", "ctr", "xer"]
)

# The 'g' register block is laid out differently per stub, so we map each
# logical register to its 32-bit WORD index within the block and select the map
# by the block's word count.
#
#  * QEMU serves the 38-word PPC core block: r0..r31, pc, msr, cr, lr, ctr, xer
#    (contiguous).
#  * XMD's PPC405 stub serves a 146-word block in the classic GDB PowerPC order:
#    32 GPRs, then 32 *64-bit* FPRs (= 64 words, unused on the FPU-less 405),
#    then pc/msr/cr/lr/ctr/xer/fpscr, then vendor SPRs. Verified empirically at a
#    known breakpoint (pc & lr == 0x5bb11c at word 96/99; pvr == 0x20011470 at
#    word 103) — see rsp_discover.py.
_QEMU_LAYOUT = {name: i for i, name in enumerate(PPC_REG_NAMES)}
_XMD_LAYOUT = {f"r{i}": i for i in range(32)}
_XMD_LAYOUT.update(pc=96, msr=97, cr=98, lr=99, ctr=100, xer=101,
                   fpscr=102, pvr=103)

REG_LAYOUTS = {38: _QEMU_LAYOUT, 146: _XMD_LAYOUT}


def layout_for(nwords: int):
    """Return {name: word_index} for a 'g' block of `nwords` 32-bit words, or
    None if the size is unrecognised (caller should fall back / warn)."""
    return REG_LAYOUTS.get(nwords)


def cksum(b: bytes) -> bytes:
    return f"{sum(b) & 0xff:02x}".encode()


class RSPError(RuntimeError):
    pass


class WriteDisabled(RSPError):
    """Raised when a mutating op is attempted on a read-only client."""


class RSP:
    def __init__(self, host="127.0.0.1", port=1234, *, allow_write=False,
                 timeout=10.0, label=None):
        self.host = host
        self.port = port
        self.allow_write = allow_write
        self.timeout = timeout
        self.label = label or f"{host}:{port}"
        self.sock = None
        self._reglen = None  # observed length of the 'g' reply (hex chars)

    # ----- connection -----------------------------------------------------
    def connect(self):
        self.sock = socket.create_connection((self.host, self.port),
                                             timeout=self.timeout)
        return self

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *exc):
        # Resume the target on the way out so we never leave it halted.
        try:
            self.detach()
        except Exception:
            pass
        self.close()

    # ----- raw packet I/O -------------------------------------------------
    def send(self, payload: str):
        pkt = b"$" + payload.encode() + b"#" + cksum(payload.encode())
        self.sock.sendall(pkt)
        if self.sock.recv(1) != b"+":
            raise RSPError(f"[{self.label}] bad ack for {payload!r}")

    def recv(self, timeout=None) -> str:
        self.sock.settimeout(timeout if timeout is not None else self.timeout)
        while True:
            b = self.sock.recv(1)
            if b == b"$":
                break
            if not b:
                raise RSPError(f"[{self.label}] connection closed")
        buf = bytearray()
        while True:
            b = self.sock.recv(1)
            if b == b"#":
                self.sock.recv(2)  # discard checksum
                break
            buf.extend(b)
        self.sock.sendall(b"+")
        return buf.decode("latin-1")

    def query(self, payload: str, timeout=None) -> str:
        self.send(payload)
        return self.recv(timeout)

    # ----- state ----------------------------------------------------------
    def stop_reply(self, timeout=None) -> str:
        """Send '?' — current stop reason (e.g. T05...)."""
        return self.query("?", timeout)

    def regs(self) -> dict:
        g = self.query("g")
        self._reglen = len(g)
        return self.parse_g(g)

    @staticmethod
    def parse_g(hexstr: str) -> dict:
        """Decode a 'g' reply into {reg_name: value}, picking the layout by the
        block's word count. Unknown sizes fall back to the contiguous QEMU/gdb
        order so a new stub still yields sensible GPRs+pc."""
        words = [int(hexstr[i:i + 8], 16)
                 for i in range(0, len(hexstr) - len(hexstr) % 8, 8)]
        layout = layout_for(len(words)) or _QEMU_LAYOUT
        return {name: words[idx] for name, idx in layout.items()
                if idx < len(words)}

    def read_mem(self, addr: int, length: int) -> bytes:
        """Read `length` bytes at `addr`; returns raw bytes (big-endian wire)."""
        r = self.query(f"m{addr & 0xffffffff:x},{length:x}")
        if r.startswith("E") and len(r) <= 3:
            raise RSPError(f"[{self.label}] mem read @0x{addr:08x} failed: {r}")
        return bytes.fromhex(r)

    def read_word(self, addr: int) -> int:
        return int.from_bytes(self.read_mem(addr, 4), "big")

    # ----- execution ------------------------------------------------------
    def step(self, timeout=None) -> str:
        return self.query("s", timeout)

    def cont(self, timeout=None) -> str:
        self.send("c")
        return self.recv(timeout)

    def interrupt(self, timeout=None) -> str:
        self.sock.sendall(b"\x03")
        return self.recv(timeout)

    def detach(self):
        # 'D' resumes and detaches; safe (read-only).
        self.send("D")

    # ----- breakpoints ----------------------------------------------------
    def set_bp(self, addr: int, *, hw=True, kind=4) -> bool:
        """Insert a breakpoint. hw=True → Z1 (hardware/IAC, no memory write);
        hw=False → Z0 (software trap; UNSAFE on real HW, QEMU only)."""
        z = "Z1" if hw else "Z0"
        if not hw and not self.allow_write:
            raise WriteDisabled(
                f"[{self.label}] software breakpoint patches memory; "
                "use hw=True or construct RSP(allow_write=True)")
        return self.query(f"{z},{addr & 0xffffffff:x},{kind}") == "OK"

    def clear_bp(self, addr: int, *, hw=True, kind=4) -> bool:
        z = "z1" if hw else "z0"
        return self.query(f"{z},{addr & 0xffffffff:x},{kind}") == "OK"

    def run_to(self, addr: int, *, hw=True, timeout=None) -> dict:
        """Set bp, continue, wait for hit, clear bp, return registers."""
        if not self.set_bp(addr, hw=hw):
            raise RSPError(f"[{self.label}] could not set bp @0x{addr:08x}")
        stop = self.cont(timeout)
        self.clear_bp(addr, hw=hw)
        if not (stop.startswith("T") or stop.startswith("S")):
            raise RSPError(f"[{self.label}] unexpected stop @bp: {stop!r}")
        return self.regs()

    # ----- guarded mutations (off unless allow_write) ---------------------
    def write_mem(self, addr: int, data: bytes):
        if not self.allow_write:
            raise WriteDisabled(f"[{self.label}] write_mem disabled (read-only)")
        return self.query(f"M{addr & 0xffffffff:x},{len(data):x}:{data.hex()}")

    def _reg_index(self, name: str) -> int:
        """Resolve a logical register name to its index in the active 'g'
        block. The layout depends on the stub, so we need the observed block
        size — read the registers once if we haven't yet."""
        if self._reglen is None:
            self.regs()
        words = self._reglen // 8
        layout = layout_for(words) or _QEMU_LAYOUT
        if name not in layout:
            raise RSPError(f"[{self.label}] register {name!r} not in the "
                           f"{words}-word layout")
        return layout[name]

    def write_reg(self, name: str, value: int, *, nbytes=4):
        """Write a single register via the RSP 'P' packet (Pn=value). `name` is
        a logical register (e.g. 'r3', 'pc'); the wire value is big-endian to
        match the 'g' block. Guarded like write_mem."""
        if not self.allow_write:
            raise WriteDisabled(f"[{self.label}] write_reg disabled (read-only)")
        idx = self._reg_index(name)
        mask = (1 << (8 * nbytes)) - 1
        val_hex = (value & mask).to_bytes(nbytes, "big").hex()
        r = self.query(f"P{idx:x}={val_hex}")
        if r != "OK":
            raise RSPError(f"[{self.label}] write_reg {name} (P{idx:x}) failed: "
                           f"{r!r} — stub may not support 'P' (try --method patch)")
        return True
