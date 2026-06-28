#!/usr/bin/env python3
"""smoke_test.py -- Automated boot smoke test for RED ONE MX Build 32 firmware.

Launches QEMU in debug mode, connects the GDB RSP stub, sets breakpoints at
key boot milestones, and verifies the firmware reaches each one in order.

Checks performed (in order):
  [1] reset_loop     -- UART ^^^ count stays < threshold before usrInit
  [2] usrInit        -- BP at 0x36c424 fires (kernelInit call site; usrInit done)
  [3] kernelInit     -- BP at 0x5a7f30 fires (VxWorks multitasking starting)
  [4] dispatch       -- BP at 0x372838 fires (rfi context-switch INTO the root task);
                        lr == 0x381a8c, r3 == 0x020390d0 (root-task entry + descriptor)
  [5] root_task_running -- after dispatch, the CPU is executing the root-task body
                        (PC in 0x380000..0x384000), NOT the old 0x124 halt loop
  [6] msr_ee         -- MSR.EE == 0 while the root task runs (sysClkEnable is not
                        reached on this QEMU boot; the cold-boot init that leads there
                        has not run -- see re_reference §0.3)
  [7] cmd_interp_loop -- liveness: the dispatched task (PC 0x381a8c, forced by patches
                        into OpenSSL X.509v3 code -- see re_reference §0.3) makes forward
                        progress: r3 advances by 6 between two hits of fn_382bec (0x382bec),
                        proving the dispatched code runs over the (zero) buffer, not a hang.
                        NB: a patch-artifact steady state, not the camera's real boot path

When a milestone BP times out the test halts QEMU with Ctrl-C and runs a set of
assumption checks against the live CPU/memory state to explain the stall.

Exit code 0 if every enabled check passes, 1 otherwise.

Usage:
    # From repo root:
    .venv/bin/python firmware/scripts/smoke_test.py

    # Override paths / tune timeouts:
    .venv/bin/python firmware/scripts/smoke_test.py \\
        --qemu ~/src/qemu-r1mx/build/qemu-system-ppc \\
        --firmware reverse/build_32/extracted/software.patched.r1mx.bin \\
        --timeout-scale 2.0

    # Run only the reset-loop and kernelInit checks:
    .venv/bin/python firmware/scripts/smoke_test.py --checks reset_loop,kernelInit

GDB RSP protocol notes (see re_reference.md §15 for full details):
    - Use standard ACK mode -- do NOT negotiate QStartNoAckMode (causes T05 loss)
    - Send '$c#63' without reading the '+' ack; wait_stop drains it
    - Filter 'O' (console output) packets in wait_stop; look for T02/T03/T05
    - Both Z0 (SW) and Z1 (HW) BPs use the same TCG cpu_breakpoint_insert path;
      they bypass firmware exception handlers entirely (no 0x700 involvement)
    - After a BP fires you MUST clear it (or single-step) before the next 'c'.
      QEMU re-triggers a BP_GDB breakpoint if you continue while the CPU is
      still parked on it: continue re-reports the SAME PC instead of advancing.
      (Verified with bp_probe: continue from 0x36c424 re-hit 0x36c424; clearing
      the BP first let it advance to kernelInit @ 0x5a7f30.)  The milestone loop
      below clears each BP as it fires so the next continue steps off it.
    - SPR encoding: spr = ((w >> 11) & 0x1f) << 5 | ((w >> 16) & 0x1f)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent          # firmware/scripts/
_FIRMWARE_DIR = _HERE.parent                     # firmware/
_REPO_ROOT = _FIRMWARE_DIR.parent               # repo root

DEFAULT_QEMU = Path.home() / "src/qemu-r1mx/build/qemu-system-ppc"
DEFAULT_FIRMWARE = (
    _REPO_ROOT
    / "firmware/reverse/build_32/extracted/software.patched.r1mx.bin"
)
DEFAULT_GDB_PORT = 1234
DEFAULT_TIMEOUT_SCALE = 1.0

# ---------------------------------------------------------------------------
# Boot milestones
# ---------------------------------------------------------------------------

@dataclass
class Milestone:
    key: str
    addr: int
    label: str
    timeout_s: float          # before scaling
    # optional memory reads to report at BP hit: list of (label, addr, size)
    mem_reads: list[tuple[str, int, int]] = field(default_factory=list)
    # optional register expectations at BP hit: {reg_name: expected_value}
    expect_regs: dict[str, int] = field(default_factory=dict)


MILESTONES: list[Milestone] = [
    Milestone(
        key="usrInit",
        addr=0x36C424,
        label="usrInit complete  (bl kernelInit call site)",
        timeout_s=30.0,
        mem_reads=[
            ("intCnt @ 0xe2942c",      0xe2942c,   4),
            ("kernelState @ 0x10d0580", 0x010d0580, 4),
        ],
    ),
    Milestone(
        key="kernelInit",
        addr=0x5A7F30,
        label="kernelInit entry  (VxWorks multitasking starts)",
        timeout_s=30.0,
        mem_reads=[
            ("intCnt @ 0xe2942c",      0xe2942c,   4),
        ],
    ),
    Milestone(
        key="dispatch",
        addr=0x372838,
        label="rfi context-switch INTO root task  (0x372838; lr=0x381a8c, r3=0x020390d0)",
        timeout_s=30.0,
        expect_regs={"lr": 0x00381A8C, "r3": 0x020390D0},
    ),
]

# The first context switch (rfi at 0x372838) dispatches the root task.
# These are the expected register values at that instant (re_reference §0).
ROOT_TASK_ENTRY  = 0x00381A8C   # root-task PC (kernelInit arg1; lr at the rfi)
ROOT_TASK_DESC   = 0x020390D0   # root-task descriptor pointer (r3 at the rfi)
# The root task then executes its body; sample it here to prove it is running.
ROOT_BODY_LO     = 0x00380000
ROOT_BODY_HI     = 0x00384000

# ^^^ lines seen before usrInit BP fires; >this means reset loop
RESET_LOOP_THRESHOLD = 5

# ---------------------------------------------------------------------------
# Known stall signatures: PC range -> human description
# Used to infer boot stage when a milestone BP times out.
# ---------------------------------------------------------------------------

_STALL_RANGES: list[tuple[int, int, str]] = [
    (0x000124, 0x000124, "at post-usrInit dead loop (b 0x124) — usrInit+kernelInit RETURNED; boot stub spins"),
    (0x36C350, 0x36C43F, "in usrInit body (pre-kernelInit)"),
    (0x5A7F30, 0x5A9000, "in kernelInit setup"),
    (0x5AB0DC, 0x5AB0DC, "at workQ spin — windWorker waiting for timer ISR"),
    (0x440000, 0x44FFFF, "in VxWorks scheduler (0x44xxxx)"),
    (0x490000, 0x49FFFF, "in VxWorks scheduler (0x49xxxx)"),
    (0x5B0000, 0x5BBFFF, "in VxWorks kernel internals (0x5bxxxx)"),
    (0x36C440, 0x36C4FF, "in usrRoot! (root task running)"),
    (0x381A8C, 0x382FFF, "in root task body (fn_381a8c)"),
    (0x37C440, 0x37CFFF, "in WDB task"),
]

# Assumption checks run at the workQ spin (PC == 0x5ab0dc).
# Each is (label, check_fn) where check_fn(regs, mem) -> (passed, detail).
# mem keys are the addresses as ints; regs keys are PPC_REG_NAMES entries.
_WORQQ_SPIN_ADDR = 0x5AB0DC
_WORQQ_FLAG_ADDR = 0x010D0584
_INT_CNT_ADDR    = 0xe2942c
_KERNEL_STATE    = 0x010D0580

# Regression sentinel: the OLD terminal state when the wrong patch #57 made
# kernelInit return.  If the CPU is ever found here post-dispatch, multitasking
# regressed (see _post_dispatch_check).
HALT_LOOP_ADDR = 0x00000124   # boot-stub `b 0x124` dead loop (pre-fix terminal state)


def _infer_stall_stage(pc: int) -> str:
    for lo, hi, label in _STALL_RANGES:
        if lo <= pc <= hi:
            return label
    return f"unknown range 0x{pc:08x}"


def _workq_assumption_checks(
    regs: dict[str, int],
    mem: dict[int, int],
) -> list[tuple[str, bool, str]]:
    """Return list of (label, passed, detail) assumption checks for the workQ stall."""
    results = []

    # 1. Confirm we are actually at the workQ spin
    pc = regs.get("pc", 0)
    results.append((
        "PC == workQ spin (0x5ab0dc)",
        pc == _WORQQ_SPIN_ADDR,
        f"pc = 0x{pc:08x}",
    ))

    # 2. r24 should point to the workQ flag (confirmed spin variable)
    r24 = regs.get("r24", 0)
    results.append((
        "r24 == workQ flag address (0x010d0584)",
        r24 == _WORQQ_FLAG_ADDR,
        f"r24 = 0x{r24:08x}",
    ))

    # 3. workQ flag must be 0 (timer ISR has never fired to set it)
    wq = mem.get(_WORQQ_FLAG_ADDR)
    if wq is not None:
        results.append((
            "*(workQ flag) == 0  (timer ISR never fired)",
            wq == 0,
            f"*(0x010d0584) = 0x{wq:08x}",
        ))
    else:
        results.append(("*(workQ flag) readable", False, "memory read failed"))

    # 4. MSR.EE must be 0 (external interrupts disabled — PIT can never fire)
    msr = regs.get("msr", 0)
    ee_set = bool(msr & 0x8000)
    results.append((
        "MSR.EE == 0  (interrupts disabled; PIT tick cannot fire)",
        not ee_set,
        f"msr = 0x{msr:08x}  (EE={'1 -- UNEXPECTED' if ee_set else '0'})",
    ))

    # 5. intCnt must be 0 (not inside an ISR)
    ic = mem.get(_INT_CNT_ADDR)
    if ic is not None:
        results.append((
            "intCnt == 0  (not executing inside an ISR)",
            ic == 0,
            f"*(0xe2942c) = 0x{ic:08x}",
        ))
    else:
        results.append(("intCnt readable", False, "memory read failed"))

    # 6. Report kernelState (informational)
    ks = mem.get(_KERNEL_STATE)
    if ks is not None:
        results.append((
            "kernelState (informational)",
            True,
            f"*(0x010d0580) = 0x{ks:08x}",
        ))

    return results

# ---------------------------------------------------------------------------
# GDB RSP client
# ---------------------------------------------------------------------------

PPC_REG_NAMES = (
    [f"r{i}" for i in range(32)]
    + ["pc", "msr", "cr", "lr", "ctr", "xer"]
)


def _cksum(payload: bytes) -> bytes:
    return f"{sum(payload) & 0xff:02x}".encode()


class GdbRsp:
    """Minimal GDB RSP client, tuned for QEMU PPC405.

    Uses standard ACK mode throughout.  Do NOT negotiate QStartNoAckMode:
    it suppresses the '+' ack that precedes the T05 stop reply and causes
    wait_stop() to miss the breakpoint notification.
    """

    def __init__(self, host: str, port: int, connect_timeout: float = 15.0):
        self._sock = socket.create_connection((host, port), timeout=connect_timeout)
        self._sock.settimeout(None)

    def close(self) -> None:
        try:
            self._send("D")
        except Exception:
            pass
        try:
            self._sock.close()
        except Exception:
            pass

    # -- low-level protocol --------------------------------------------------

    def _send(self, payload: str) -> None:
        encoded = payload.encode()
        pkt = b"$" + encoded + b"#" + _cksum(encoded)
        self._sock.sendall(pkt)
        ack = self._sock.recv(1)
        if ack not in (b"+", b"-"):
            raise RuntimeError(f"unexpected ack {ack!r} for {payload!r}")

    def _recv(self, timeout: float) -> str:
        """Read one GDB RSP packet, send '+' ack, return payload string."""
        self._sock.settimeout(timeout)
        try:
            buf = bytearray()
            # skip to '$'
            while True:
                b = self._sock.recv(1)
                if not b:
                    raise RuntimeError("connection closed")
                if b == b"$":
                    break
            # read until '#' then consume 2-byte checksum
            while True:
                b = self._sock.recv(1)
                if not b:
                    raise RuntimeError("connection closed mid-packet")
                if b == b"#":
                    self._sock.recv(2)
                    break
                buf.extend(b)
            self._sock.sendall(b"+")
            return buf.decode("latin-1")
        finally:
            self._sock.settimeout(None)

    def _query(self, payload: str, timeout: float = 5.0) -> str:
        self._send(payload)
        return self._recv(timeout)

    # -- public API ----------------------------------------------------------

    def initial_stop(self) -> str:
        """Read the initial stop reply from a halted (-S) QEMU."""
        self._send("?")
        return self._recv(timeout=5.0)

    def get_regs(self) -> dict[str, int]:
        h = self._query("g")
        regs: dict[str, int] = {}
        for i, name in enumerate(PPC_REG_NAMES):
            chunk = h[i * 8 : i * 8 + 8]
            if len(chunk) < 8:
                break
            try:
                regs[name] = int(chunk, 16)
            except ValueError:
                break
        return regs

    def read_mem(self, addr: int, nbytes: int) -> Optional[bytes]:
        """Read memory; returns None if QEMU returns 'E'."""
        reply = self._query(f"m{addr:x},{nbytes:x}")
        if reply.startswith("E"):
            return None
        try:
            return bytes.fromhex(reply)
        except ValueError:
            return None

    def set_bp(self, addr: int) -> bool:
        r = self._query(f"Z0,{addr:x},4")
        return r == "OK"

    def clear_bp(self, addr: int) -> None:
        try:
            self._query(f"z0,{addr:x},4")
        except Exception:
            pass

    def resume(self) -> None:
        """Send 'c' without reading the '+' ack.

        In standard ACK mode QEMU sends '+' immediately, then runs the CPU.
        wait_stop() will drain both the '+' and the eventual T05 by scanning
        the raw byte stream for stop-reply packets.
        """
        self._sock.sendall(b"$c#63")

    def wait_stop(self, timeout: float) -> Optional[str]:
        """Wait for a T/S/W stop reply, ignoring O (console output) packets.

        Returns the stop-reply payload string (e.g. 'T05...') or None on
        timeout.  Must drain the '+' ack that precedes the stop reply in
        standard ACK mode, which _recv() handles by scanning for '$'.
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            try:
                reply = self._recv(timeout=remaining)
            except socket.timeout:
                return None
            # T/S/W = stop reply;  O = console output (discard and keep waiting)
            if reply and reply[0] in ("T", "S", "W", "X"):
                return reply

    def interrupt(self) -> Optional[str]:
        """Send Ctrl-C to halt a running target; return stop reply or None."""
        self._sock.sendall(b"\x03")
        try:
            return self._recv(timeout=5.0)
        except socket.timeout:
            return None

    def step(self, timeout: float = 5.0) -> Optional[str]:
        """Single-step one instruction; return the stop reply or None.

        Used to step off a breakpoint before resuming (QEMU re-triggers a
        BP_GDB if you continue while still parked on it -- see §0.5 harness note).
        """
        self._sock.sendall(b"$s#73")
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            try:
                reply = self._recv(timeout=remaining)
            except socket.timeout:
                return None
            if reply and reply[0] in ("T", "S", "W", "X"):
                return reply


# ---------------------------------------------------------------------------
# UART monitor (runs in a background thread)
# ---------------------------------------------------------------------------

class UartMonitor:
    """Reads QEMU stdout in a daemon thread, counting ^^^ lines."""

    def __init__(self, stream):
        self._stream = stream
        self.lines: list[str] = []
        self.hat_count = 0           # number of ^^^123456789 lines seen
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        try:
            for raw in self._stream:
                if self._stop.is_set():
                    break
                try:
                    line = raw.decode("latin-1", errors="replace").rstrip()
                except Exception:
                    continue
                self.lines.append(line)
                if "^^^" in line:
                    self.hat_count += 1
        except Exception:
            pass


# ---------------------------------------------------------------------------
# QEMU process manager
# ---------------------------------------------------------------------------

class QemuProcess:
    """Launches and terminates the QEMU process."""

    def __init__(
        self,
        qemu_bin: Path,
        firmware: Path,
        memory_mb: int = 2048,
        gdb_port: int = DEFAULT_GDB_PORT,
    ):
        self._qemu_bin = qemu_bin
        self._firmware = firmware
        self._memory_mb = memory_mb
        self._gdb_port = gdb_port
        self._proc: Optional[subprocess.Popen] = None
        self.uart: Optional[UartMonitor] = None

    @staticmethod
    def _kill_port(port: int) -> None:
        """Kill any process listening on *port* to avoid connecting to a stale QEMU."""
        import signal as _signal
        try:
            import subprocess as _sp
            out = _sp.check_output(
                ["ss", "-tlnpH", f"sport = :{port}"],
                stderr=_sp.DEVNULL,
                text=True,
            )
            for line in out.splitlines():
                # line format: LISTEN 0 1 0.0.0.0:1234 ... pid=12345,...
                m = re.search(r'pid=(\d+)', line)
                if m:
                    pid = int(m.group(1))
                    try:
                        os.kill(pid, _signal.SIGTERM)
                        time.sleep(0.3)
                        # escalate if still alive
                        os.kill(pid, _signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        except Exception:
            pass

    def start(self) -> None:
        # Evict any stale QEMU that is still listening on the GDB port from a
        # previous session.  Without this, _wait_for_port() returns immediately
        # (the stale process answers), we attach to old state rather than a
        # fresh boot, and all breakpoints miss.
        self._kill_port(self._gdb_port)
        time.sleep(0.2)

        qemu_cmd = [
            str(self._qemu_bin),
            "-machine", "r1mx-virtex4",
            "-m", str(self._memory_mb),
            "-nographic",
            "-device", f"loader,file={self._firmware},addr=0x0,force-raw=on",
            "-S",                           # halt at PC=0x0
            "-gdb", f"tcp::{self._gdb_port}",
        ]
        # stdbuf -oL forces line-buffered stdout so the UartMonitor thread
        # sees ^^^ lines promptly rather than in 4 KB pipe chunks.
        stdbuf = shutil.which("stdbuf")
        if stdbuf:
            cmd = [stdbuf, "-oL"] + qemu_cmd
        else:
            cmd = qemu_cmd
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self.uart = UartMonitor(self._proc.stdout)
        self.uart.start()

    def stop(self) -> None:
        if self._proc is None:
            return
        if self.uart:
            self.uart.stop()
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait()
        except Exception:
            pass
        self._proc = None

    def pid(self) -> Optional[int]:
        return self._proc.pid if self._proc else None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

_COL = {PASS: "\033[32m", FAIL: "\033[31m", SKIP: "\033[33m", "RST": "\033[0m"}


def _col(status: str, text: str) -> str:
    if sys.stdout.isatty():
        return f"{_COL.get(status, '')}{text}{_COL['RST']}"
    return text


@dataclass
class CheckResult:
    key: str
    label: str
    status: str         # PASS | FAIL | SKIP
    detail: str = ""
    regs: dict[str, int] = field(default_factory=dict)
    mem: dict[str, int] = field(default_factory=dict)


def _print_result(r: CheckResult) -> None:
    tag = f"[{r.status}]"
    print(f"  {_col(r.status, tag):20s} {r.label}")
    if r.detail:
        print(f"           {r.detail}")
    if r.regs:
        for k in ("pc", "msr", "lr", "r1", "r3"):
            if k in r.regs:
                print(f"             {k:>4} = 0x{r.regs[k]:08x}")
    if r.mem:
        for label, val in r.mem.items():
            print(f"             {label} = 0x{val:08x}")


# ---------------------------------------------------------------------------
# Terminal-state race (post-kernelInit)
# ---------------------------------------------------------------------------

_TERMINAL_LABELS = {
    "root_task_running": "Root task is executing its body (0x380000..0x384000), not 0x124 halt",
    "msr_ee": "MSR.EE == 0 while root task spins (sysClkEnable not yet reached)",
    "cmd_interp_loop": "Dispatched task advances (liveness): r3 += 6 at fn_382bec, not hung",
}

# Dispatched-task liveness (re_reference.md §0.3): patches #53a/b/c/55 force the
# root-task PC to 0x381a8c, which is OpenSSL 0.9.8a X.509v3 parsing code (Wind
# River Security Libraries) -- NOT a camera command interpreter (an earlier
# reading was wrong).  Fed the zero-filled buffer at 0x020390d0, it parses an
# empty value in a deterministic loop, the pointer in r3 advancing ~6 bytes per
# pass through fn_382bec.  We hit fn_382bec twice and assert the +6 advance as a
# LIVENESS check (the dispatched code runs and makes forward progress, not a
# crash/halt).  The advance is real but it is patch-artifact behaviour, not the
# camera's real boot path.
CMD_ADVANCER_ADDR = 0x00382BEC   # fn_382bec (OpenSSL v3 parser inner step / loop tail)
RECORD_STRIDE     = 6


def _post_dispatch_check(
    gdb: GdbRsp,
    enabled_checks: set[str],
    timeout_scale: float,
) -> list[CheckResult]:
    """After the first context switch, confirm the root task is actually running.

    Encodes re_reference.md §0 (post-fix): kernelInit dispatches the root task
    via the rfi at 0x372838 and does NOT return.  Let the root task run briefly,
    halt it, and assert the PC is inside the root-task body (0x380000..0x384000)
    rather than the old 0x124 halt loop.

    REGRESSION TRIPWIRE: if the CPU is found at 0x124 (or at usrInit's post-
    kernelInit return 0x36c428), the wrong patch #57 (NOP at 0x5a8190) has come
    back -- FAIL loudly.
    """
    results: list[CheckResult] = []
    print("\n  [*] Letting the root task run, then sampling its PC...")
    gdb.resume()
    time.sleep(1.5 * timeout_scale)
    gdb.interrupt()
    regs = gdb.get_regs()
    pc = regs.get("pc", 0)

    if "root_task_running" in enabled_checks:
        if pc in (HALT_LOOP_ADDR, 0x36C428):
            r = CheckResult(
                key="root_task_running", label=_TERMINAL_LABELS["root_task_running"],
                status=FAIL,
                detail=(f"REGRESSION: CPU at 0x{pc:08x} -- kernelInit returned again. "
                        "The wrong patch #57 (NOP at 0x5a8190) may be re-enabled; "
                        "the root task is not being dispatched."),
                regs=regs,
            )
        elif ROOT_BODY_LO <= pc < ROOT_BODY_HI:
            r = CheckResult(
                key="root_task_running", label=_TERMINAL_LABELS["root_task_running"],
                status=PASS,
                detail=(f"PC=0x{pc:08x} is inside the root-task body "
                        f"(0x{ROOT_BODY_LO:06x}..0x{ROOT_BODY_HI:06x}) -- multitasking "
                        "is live (root task dispatched and running)."),
                regs=regs,
            )
        else:
            r = CheckResult(
                key="root_task_running", label=_TERMINAL_LABELS["root_task_running"],
                status=FAIL,
                detail=(f"PC=0x{pc:08x} ({_infer_stall_stage(pc)}); expected root-task "
                        f"body 0x{ROOT_BODY_LO:06x}..0x{ROOT_BODY_HI:06x}"),
                regs=regs,
            )
        results.append(r)

    if "msr_ee" in enabled_checks:
        msr = regs.get("msr", 0)
        ee = bool(msr & 0x8000)
        results.append(CheckResult(
            key="msr_ee", label=_TERMINAL_LABELS["msr_ee"],
            status=PASS if not ee else FAIL,
            detail=f"msr=0x{msr:08x}  (EE={'1 -- UNEXPECTED' if ee else '0'})",
            regs=regs,
        ))

    if "cmd_interp_loop" in enabled_checks:
        results.append(_check_cmd_interp_loop(gdb, timeout_scale))

    return results


def _check_cmd_interp_loop(gdb: GdbRsp, timeout_scale: float) -> CheckResult:
    """Liveness check on the dispatched task (§0.3).

    Hit fn_382bec (OpenSSL v3 parser inner step / loop tail) twice and assert the
    pointer r3 advanced by exactly RECORD_STRIDE.  This proves the dispatched code
    (OpenSSL X.509v3 parsing, forced to 0x381a8c by patches) runs and makes
    deterministic forward progress over the zero-filled buffer at 0x020390d0,
    rather than being hung/crashed.  (Patch-artifact behaviour, not the real boot.)
    """
    key = "cmd_interp_loop"
    label = _TERMINAL_LABELS[key]
    samples: list[int] = []
    gdb.set_bp(CMD_ADVANCER_ADDR)
    try:
        for _ in range(2):
            gdb.resume()
            if gdb.wait_stop(5.0 * timeout_scale) is None:
                return CheckResult(
                    key=key, label=label, status=FAIL,
                    detail=(f"fn_382bec (0x{CMD_ADVANCER_ADDR:06x}) not reached -- "
                            "root task is not in the command-interpreter loop"),
                )
            r = gdb.get_regs()
            if r.get("pc", 0) != CMD_ADVANCER_ADDR:
                return CheckResult(
                    key=key, label=label, status=FAIL,
                    detail=f"stopped at 0x{r.get('pc',0):08x}, expected 0x{CMD_ADVANCER_ADDR:06x}",
                    regs=r,
                )
            samples.append(r.get("r3", 0))
            # step off the BP so the next resume advances (QEMU re-triggers a
            # parked BP otherwise)
            gdb.clear_bp(CMD_ADVANCER_ADDR)
            gdb.step(5.0 * timeout_scale)
            gdb.set_bp(CMD_ADVANCER_ADDR)
    finally:
        gdb.clear_bp(CMD_ADVANCER_ADDR)

    delta = (samples[1] - samples[0]) & 0xFFFFFFFF
    ok = delta == RECORD_STRIDE
    return CheckResult(
        key=key, label=label, status=PASS if ok else FAIL,
        detail=(f"record ptr r3: 0x{samples[0]:08x} -> 0x{samples[1]:08x} "
                f"(+{delta}); expected stride +{RECORD_STRIDE}"),
    )


# ---------------------------------------------------------------------------
# Smoke test runner
# ---------------------------------------------------------------------------

def _wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.2)
    return False


def run_smoke_test(
    qemu_bin: Path,
    firmware: Path,
    gdb_port: int,
    timeout_scale: float,
    enabled_checks: set[str],
) -> list[CheckResult]:
    results: list[CheckResult] = []

    with QemuProcess(qemu_bin, firmware, gdb_port=gdb_port) as qemu:
        print(f"  [*] QEMU pid {qemu.pid()}, waiting for GDB stub on port {gdb_port}...")
        if not _wait_for_port("127.0.0.1", gdb_port, timeout=10.0):
            results.append(CheckResult(
                key="qemu_start", label="QEMU GDB stub ready",
                status=FAIL, detail="timed out waiting for port 1234",
            ))
            return results

        gdb = GdbRsp("127.0.0.1", gdb_port)
        try:
            gdb.initial_stop()
            # Standard ACK mode throughout -- no QStartNoAckMode negotiation.

            # Verify this is a fresh QEMU halted at PC=0x0 (not a stale instance
            # from a previous session that _kill_port failed to evict).
            initial_regs = gdb.get_regs()
            initial_pc = initial_regs.get("pc", 0xFFFFFFFF)
            if initial_pc != 0x0:
                results.append(CheckResult(
                    key="qemu_start", label="QEMU GDB stub ready",
                    status=FAIL,
                    detail=f"expected fresh boot at PC=0x0, got PC=0x{initial_pc:08x} -- stale QEMU?",
                ))
                return results

            # -- Check: reset_loop ----------------------------------------
            # We verify this opportunistically while waiting for the usrInit BP.
            # The check runs inline (not a separate GDB session) by monitoring
            # the UART hat_count during the usrInit wait phase.

            # -- Set all milestone BPs up front ----------------------------
            active_milestones = [m for m in MILESTONES if m.key in enabled_checks]
            for m in active_milestones:
                ok = gdb.set_bp(m.addr)
                status_str = "ok" if ok else "FAILED"
                print(f"  [*] BP 0x{m.addr:08x} ({m.key}): {status_str}")

            # -- Run through milestones in order ---------------------------
            prev_failed = False
            for m in active_milestones:
                if prev_failed:
                    results.append(CheckResult(
                        key=m.key, label=m.label, status=SKIP,
                        detail="skipped: preceding milestone failed",
                    ))
                    continue

                print(f"\n  [*] Waiting for {m.key} (timeout {m.timeout_s * timeout_scale:.0f}s)...")
                gdb.resume()

                t0 = time.monotonic()
                timeout = m.timeout_s * timeout_scale
                reply = gdb.wait_stop(timeout=timeout)
                elapsed = time.monotonic() - t0

                # -- reset_loop check (piggy-back on first milestone wait) --
                if m.key == "usrInit" and "reset_loop" in enabled_checks:
                    hat = qemu.uart.hat_count if qemu.uart else 0
                    if hat > RESET_LOOP_THRESHOLD:
                        rl = CheckResult(
                            key="reset_loop",
                            label=f"No reset loop (^^^ count < {RESET_LOOP_THRESHOLD})",
                            status=FAIL,
                            detail=f"^^^ appeared {hat} times in {elapsed:.1f}s -- firmware stuck in sysHwInit_seq reset loop",
                        )
                    else:
                        rl = CheckResult(
                            key="reset_loop",
                            label=f"No reset loop (^^^ count < {RESET_LOOP_THRESHOLD})",
                            status=PASS,
                            detail=f"^^^ seen {hat} time(s) -- no reset loop detected",
                        )
                    results.append(rl)
                    _print_result(rl)

                if reply is None:
                    # Halt and sample to show where it's stuck.
                    gdb.interrupt()
                    regs = gdb.get_regs()
                    pc = regs.get("pc", 0)
                    hat = qemu.uart.hat_count if qemu.uart else 0
                    stage = _infer_stall_stage(pc)
                    r = CheckResult(
                        key=m.key, label=m.label, status=FAIL,
                        detail=(
                            f"timed out after {elapsed:.1f}s "
                            f"(^^^ count={hat}, PC=0x{pc:08x} -- {stage})"
                        ),
                        regs=regs,
                    )
                    results.append(r)
                    _print_result(r)

                    # Run assumption checks when stalled at the known workQ spin.
                    if pc == _WORQQ_SPIN_ADDR:
                        mem: dict[int, int] = {}
                        for addr in (_WORQQ_FLAG_ADDR, _INT_CNT_ADDR, _KERNEL_STATE):
                            raw = gdb.read_mem(addr, 4)
                            if raw and len(raw) >= 4:
                                mem[addr] = int.from_bytes(raw[:4], "big")
                        print()
                        print("  --- workQ stall assumption checks ---")
                        for label, passed, detail in _workq_assumption_checks(regs, mem):
                            status = PASS if passed else FAIL
                            tag = f"[{status}]"
                            print(f"  {_col(status, tag):20s} {label}")
                            print(f"           {detail}")
                        print()

                    prev_failed = True
                    continue

                # BP fired -- read registers to verify *which* BP we hit.
                regs = gdb.get_regs()
                pc = regs.get("pc", 0)

                # Step off this BP so the *next* resume() actually advances.
                # QEMU re-triggers a BP_GDB breakpoint if you continue while the
                # CPU is still parked on it (see GDB RSP notes in the docstring),
                # which otherwise makes every later milestone false-PASS by
                # re-reporting this same address.  Clearing it here is the
                # step-over.
                gdb.clear_bp(m.addr)

                # PC assertion: the BP that fired must be *this* milestone's
                # address.  Without this the loop reports PASS for whatever
                # address came back, so a stale/re-triggered earlier BP leaking
                # through would be mistaken for reaching this milestone.
                if pc != m.addr:
                    r = CheckResult(
                        key=m.key, label=m.label, status=FAIL,
                        detail=(
                            f"stopped at 0x{pc:08x} but expected 0x{m.addr:08x} "
                            f"after {elapsed:.1f}s -- wrong BP fired "
                            f"({_infer_stall_stage(pc)}); milestone NOT validated"
                        ),
                        regs=regs,
                    )
                    results.append(r)
                    _print_result(r)
                    prev_failed = True
                    continue

                # Register assertions (e.g. the dispatch BP must show the
                # root-task entry in lr and the descriptor in r3).
                reg_mismatch = [
                    f"{rn}=0x{regs.get(rn, 0):08x} (want 0x{rv:08x})"
                    for rn, rv in m.expect_regs.items()
                    if regs.get(rn) != rv
                ]
                if reg_mismatch:
                    r = CheckResult(
                        key=m.key, label=m.label, status=FAIL,
                        detail=(f"BP fired at 0x{pc:08x} but register check failed: "
                                + ", ".join(reg_mismatch)),
                        regs=regs,
                    )
                    results.append(r)
                    _print_result(r)
                    prev_failed = True
                    continue

                # Expected BP -- read milestone memory probes.
                mem_vals: dict[str, int] = {}
                for label, addr, size in m.mem_reads:
                    raw = gdb.read_mem(addr, size)
                    if raw and len(raw) >= size:
                        mem_vals[label] = int.from_bytes(raw[:size], "big")

                r = CheckResult(
                    key=m.key, label=m.label, status=PASS,
                    detail=f"BP fired at 0x{pc:08x} after {elapsed:.1f}s",
                    regs=regs,
                    mem=mem_vals,
                )
                results.append(r)
                _print_result(r)

            # -- Root-task-running + MSR.EE + cmd-interp loop (post-dispatch) --
            want_terminal = enabled_checks & {"root_task_running", "msr_ee", "cmd_interp_loop"}
            if want_terminal and not prev_failed:
                for r in _post_dispatch_check(gdb, enabled_checks, timeout_scale):
                    results.append(r)
                    _print_result(r)
            elif want_terminal:
                for key in ("root_task_running", "msr_ee", "cmd_interp_loop"):
                    if key in enabled_checks:
                        results.append(CheckResult(
                            key=key, label=_TERMINAL_LABELS[key], status=SKIP,
                            detail="skipped: a preceding milestone failed",
                        ))

        finally:
            for m in active_milestones:
                gdb.clear_bp(m.addr)
            gdb.clear_bp(HALT_LOOP_ADDR)
            gdb.close()

    # Add skipped reset_loop if it wasn't evaluated (e.g. usrInit not in checks)
    if "reset_loop" in enabled_checks and not any(r.key == "reset_loop" for r in results):
        results.append(CheckResult(
            key="reset_loop",
            label=f"No reset loop (^^^ count < {RESET_LOOP_THRESHOLD})",
            status=SKIP,
            detail="usrInit check was not enabled; reset_loop evaluated during it",
        ))

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

ALL_CHECK_KEYS = ({"reset_loop", "root_task_running", "msr_ee", "cmd_interp_loop"}
                  | {m.key for m in MILESTONES})


def main() -> int:
    ap = argparse.ArgumentParser(
        description="RED ONE MX Build 32 firmware boot smoke test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--qemu",
        type=Path,
        default=DEFAULT_QEMU,
        help=f"QEMU binary (default: {DEFAULT_QEMU})",
    )
    ap.add_argument(
        "--firmware",
        type=Path,
        default=DEFAULT_FIRMWARE,
        help=f"Patched firmware binary (default: ...software.patched.r1mx.bin)",
    )
    ap.add_argument(
        "--port",
        type=int,
        default=DEFAULT_GDB_PORT,
        help=f"GDB stub port (default: {DEFAULT_GDB_PORT})",
    )
    ap.add_argument(
        "--timeout-scale",
        type=float,
        default=DEFAULT_TIMEOUT_SCALE,
        metavar="N",
        help="Multiply all timeouts by N (use >1 on slow machines)",
    )
    ap.add_argument(
        "--checks",
        metavar="KEY,...",
        help=(
            "Comma-separated subset of checks to run. "
            f"Available: {', '.join(sorted(ALL_CHECK_KEYS))}. "
            "Default: all."
        ),
    )
    ap.add_argument(
        "--list-checks",
        action="store_true",
        help="Print available checks and exit.",
    )
    args = ap.parse_args()

    if args.list_checks:
        print("Available checks (run in this order):")
        print("  reset_loop  -- UART ^^^ count stays below threshold before usrInit")
        for m in MILESTONES:
            print(f"  {m.key:<12} -- {m.label} (BP @ 0x{m.addr:08x})")
        print(f"  {'root_task_running':<12} -- {_TERMINAL_LABELS['root_task_running']}")
        print(f"  {'msr_ee':<12} -- {_TERMINAL_LABELS['msr_ee']}")
        print(f"  {'cmd_interp_loop':<12} -- {_TERMINAL_LABELS['cmd_interp_loop']}")
        return 0

    # Validate paths
    if not args.qemu.exists():
        print(f"ERROR: QEMU binary not found: {args.qemu}")
        print("  Build it:  cd ~/src/qemu-r1mx && make -j$(nproc)")
        return 1
    if not args.firmware.is_file():
        print(f"ERROR: firmware not found: {args.firmware}")
        print("  Build:  make -C firmware/reverse/build_32/src install")
        return 1

    # Parse enabled checks
    if args.checks:
        enabled = set(args.checks.split(","))
        unknown = enabled - ALL_CHECK_KEYS
        if unknown:
            print(f"ERROR: unknown check keys: {', '.join(sorted(unknown))}")
            print(f"  Available: {', '.join(sorted(ALL_CHECK_KEYS))}")
            return 1
    else:
        enabled = set(ALL_CHECK_KEYS)

    # Ensure usrInit is included whenever reset_loop is (it's evaluated there)
    if "reset_loop" in enabled:
        enabled.add("usrInit")

    print(f"\nRED ONE MX Build 32 -- Boot Smoke Test")
    print(f"  QEMU:     {args.qemu}")
    print(f"  Firmware: {args.firmware}")
    print(f"  Checks:   {', '.join(sorted(enabled))}")
    print(f"  Port:     {args.port}")
    print()

    results = run_smoke_test(
        qemu_bin=args.qemu,
        firmware=args.firmware,
        gdb_port=args.port,
        timeout_scale=args.timeout_scale,
        enabled_checks=enabled,
    )

    # Summary
    print()
    print("=" * 60)
    passed = sum(1 for r in results if r.status == PASS)
    failed = sum(1 for r in results if r.status == FAIL)
    skipped = sum(1 for r in results if r.status == SKIP)
    total = passed + failed  # skipped don't count toward total

    for r in results:
        tag = f"[{r.status}]"
        print(f"  {_col(r.status, tag):20s} {r.key}")

    print()
    summary_status = PASS if failed == 0 else FAIL
    print(
        f"  {_col(summary_status, f'Result: {passed}/{total} checks passed')} "
        f"({skipped} skipped)"
    )
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
