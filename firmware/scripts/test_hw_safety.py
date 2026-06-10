#!/usr/bin/env python3
"""test_hw_safety.py -- prove the live-hardware tooling is READ-ONLY.

Safety invariant under test
---------------------------
Anything that survives a power-cycle of the camera requires a *mutation* of
persistent or volatile target state: a memory write (NOR flash @0xf0000000,
DDR), a register write, a CPU reset/restart, or a *software* breakpoint (which
patches a trap instruction into memory). Therefore:

    "no operation ever emits a mutating packet/command"
        ==> "we can always power-cycle and return to a healthy running state".

This suite enforces that invariant the only way that can't drift: by standing up
a mock GDB stub that records EVERY RSP packet the client sends and flags any
mutating one, then driving rsp.py, the converted probe scripts, and
lockstep_diff.py against it. It also checks the Channel-B XMD agent's read-only
denylist (xmd_agent.tcl) via tclsh, and xmd_rpc.py's error handling.

Mutating (UNSAFE, must NEVER appear by default):
    M / X   write memory          G / P   write registers
    R       restart/run           k       kill
    Z0 / z0 software breakpoint (patches memory)

Safe (read-only): ? g m p s c C S D H q T, hardware breakpoints/watchpoints
Z1..Z4 / z1..z4 (debug registers; do not touch memory), and the raw \\x03
interrupt (halt only).

Usage:
    python3 firmware/scripts/test_hw_safety.py [-v]
Exit code 0 iff every safety assertion holds.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from rsp import RSP, WriteDisabled, cksum  # noqa: E402


# --------------------------------------------------------------------------- #
# Safety oracle: classify an RSP packet payload.
# --------------------------------------------------------------------------- #
def is_mutating(payload: str) -> bool:
    """True if the packet would change target state (and thus break the
    power-cycle-restores invariant)."""
    if not payload:
        return False
    c = payload[0]
    if c in "MXGPR":          # write mem (M/X), write regs (G/P), restart (R)
        return True
    if c == "k":              # kill
        return True
    if c in "Zz" and len(payload) > 1 and payload[1] == "0":  # software bp
        return True
    return False


def command_allowed(payload: str) -> bool:
    """Positive allowlist: the only packets our read-only tooling should send."""
    if payload == "?":
        return True
    if not payload:
        return False
    c = payload[0]
    if c in "gmscCSDHpqT":
        return True
    if c in "Zz" and len(payload) > 1 and payload[1] in "1234":  # hw bp/watch
        return True
    return False


# --------------------------------------------------------------------------- #
# Mock GDB stub that records traffic and never lets the client hang.
# --------------------------------------------------------------------------- #
class SafetyMockGdbServer:
    """Minimal RSP target. Answers reads/steps so the client makes progress,
    records every command payload, and tags mutating ones as violations."""

    def __init__(self, reg_hex: str | None = None):
        self.reg_hex = reg_hex or ("00000000" * 38)  # 38 PPC core regs
        self.commands: list[str] = []
        self.violations: list[str] = []
        self._lock = threading.Lock()
        self._stop = False
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(8)
        self._t = threading.Thread(target=self._accept, daemon=True)
        self._t.start()

    # -- lifecycle --
    def _accept(self):
        while not self._stop:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(conn,),
                             daemon=True).start()

    def stop(self):
        self._stop = True
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()

    # -- per-connection RSP loop --
    def _serve(self, conn):
        buf = bytearray()
        while not self._stop:
            try:
                data = conn.recv(4096)
            except OSError:
                break
            if not data:
                break
            buf.extend(data)
            while buf:
                b0 = buf[0:1]
                if b0 in (b"+", b"-"):
                    del buf[0]
                elif b0 == b"\x03":             # interrupt -> halt
                    del buf[0]
                    self._send(conn, "T05thread:01;")
                elif b0 == b"$":
                    hp = buf.find(b"#")
                    if hp < 0 or len(buf) < hp + 3:
                        break                    # incomplete; wait for more
                    payload = buf[1:hp].decode("latin-1")
                    del buf[:hp + 3]
                    conn.sendall(b"+")           # ack the command
                    self._record(payload)
                    self._send(conn, self._reply_for(payload))
                else:
                    del buf[0]
        try:
            conn.close()
        except OSError:
            pass

    def _record(self, payload):
        with self._lock:
            self.commands.append(payload)
            if is_mutating(payload):
                self.violations.append(payload)

    def _reply_for(self, p: str) -> str:
        if p == "?":
            return "T05thread:01;"
        if not p:
            return ""
        c = p[0]
        if c == "g":
            return self.reg_hex
        if c == "m":
            try:
                n = int(p.split(",")[1], 16)
            except (IndexError, ValueError):
                n = 4
            return "00" * n
        if c in "Zz":
            return "OK"
        if c in "scCS":
            return "T05thread:01;"
        if c in "DH":
            return "OK"
        if c in "MXGPR":   # answer mutating ops too, so a buggy client proceeds
            return "OK"
        return ""          # unsupported (q, p, T, ...) -> empty, per RSP

    def _send(self, conn, body: str):
        conn.sendall(b"$" + body.encode("latin-1") + b"#" + cksum(body.encode()))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
class TestSafetyOracle(unittest.TestCase):
    """The oracle itself must be correct, or every other test is hollow."""

    def test_mutating_detected(self):
        for p in ["M0,1:00", "X0,1:\x00", "G0011", "P0=00000001",
                  "R00", "k", "Z0,1000,4", "z0,1000,4"]:
            self.assertTrue(is_mutating(p), f"{p!r} should be mutating")

    def test_readonly_not_flagged(self):
        for p in ["?", "g", "m0,4", "m f0000000,10", "Z1,1000,4",
                  "z1,1000,4", "Z2,1000,4", "s", "c", "D", "Hg0", "p40"]:
            self.assertFalse(is_mutating(p), f"{p!r} should be safe")
            self.assertTrue(command_allowed(p) or p.startswith("p"),
                            f"{p!r} should be allowlisted")


class TestRegisterLayouts(unittest.TestCase):
    """Correct register decoding per stub. XMD's 146-word PPC405 block places
    pc/lr/etc after 32 GPRs + 32 64-bit FPRs; QEMU's 38-word block is
    contiguous. A regression here means hardware pc/lr read as garbage (the
    exact bug found 2026-06-07: pc decoded as 0 from a zeroed FP slot)."""

    def test_xmd_146word_layout(self):
        from rsp import RSP, layout_for
        self.assertIsNotNone(layout_for(146), "XMD layout must be registered")
        w = [0] * 146
        w[1], w[3], w[31] = 0x022827a0, 0xffffffff, 0x00e9c25c
        w[96], w[99], w[100], w[101] = 0x5bb11c, 0x5bb11c, 0x381fa8, 0x20000000
        w[103] = 0x20011470  # PVR fingerprint
        r = RSP.parse_g("".join(f"{x:08x}" for x in w))
        self.assertEqual(r["pc"], 0x5bb11c)
        self.assertEqual(r["lr"], 0x5bb11c)
        self.assertEqual(r["ctr"], 0x381fa8)
        self.assertEqual(r["r3"], 0xffffffff)
        self.assertEqual(r["r31"], 0x00e9c25c)
        self.assertEqual(r.get("pvr"), 0x20011470)

    def test_qemu_38word_layout(self):
        from rsp import RSP, layout_for
        self.assertIsNotNone(layout_for(38))
        r = RSP.parse_g("".join(f"{i:08x}" for i in range(38)))
        self.assertEqual(r["r0"], 0)
        self.assertEqual(r["r31"], 31)
        self.assertEqual(r["pc"], 32)
        self.assertEqual(r["xer"], 37)


class TestRspClientReadOnly(unittest.TestCase):
    def setUp(self):
        self.srv = SafetyMockGdbServer()
        self.addCleanup(self.srv.stop)

    def client(self, **kw):
        t = RSP("127.0.0.1", self.srv.port, timeout=5.0, **kw).connect()
        self.addCleanup(t.close)
        return t

    def test_all_read_paths_emit_no_mutation(self):
        t = self.client()
        t.stop_reply()
        t.regs()
        t.read_mem(0x0, 16)
        t.read_word(0xf0000000)          # NOR flash region read
        t.run_to(0x100, hw=True)         # uses hardware breakpoint
        t.step()
        t.cont()
        t.interrupt()
        t.detach()
        self.assertEqual(self.srv.violations, [],
                         f"mutating packets leaked: {self.srv.violations}")
        # everything we sent is on the positive allowlist
        for cmd in self.srv.commands:
            self.assertTrue(command_allowed(cmd),
                            f"unexpected packet on the wire: {cmd!r}")

    def test_breakpoints_are_hardware_not_software(self):
        t = self.client()
        t.run_to(0x200, hw=True)
        self.assertTrue(any(c.startswith("Z1") for c in self.srv.commands),
                        "expected a hardware breakpoint (Z1)")
        self.assertFalse(any(c.startswith("Z0") for c in self.srv.commands),
                         "software breakpoint (Z0) patches memory -- forbidden")

    def test_default_set_bp_is_hardware(self):
        t = self.client()
        t.set_bp(0x300)                  # no hw= kwarg -> must default hardware
        self.assertIn("Z1,300,4", self.srv.commands)
        self.assertEqual(self.srv.violations, [])

    def test_write_mem_disabled_by_default(self):
        t = self.client()
        with self.assertRaises(WriteDisabled):
            t.write_mem(0x0, b"\xde\xad")
        self.assertFalse(any(c[0] in "MX" for c in self.srv.commands),
                         "no memory-write packet may reach the wire")
        self.assertEqual(self.srv.violations, [])

    def test_software_bp_disabled_by_default(self):
        t = self.client()
        with self.assertRaises(WriteDisabled):
            t.set_bp(0x400, hw=False)
        self.assertFalse(any(c.startswith("Z0") for c in self.srv.commands))
        self.assertEqual(self.srv.violations, [])

    def test_opt_in_required_for_writes(self):
        # Even with allow_write=True, a write only happens when explicitly called;
        # read paths stay clean. This documents that mutation is opt-in only.
        t = self.client(allow_write=True)
        t.regs()
        t.read_mem(0, 4)
        self.assertEqual(self.srv.violations, [],
                         "read paths must not mutate even with allow_write=True")


class TestScriptsReadOnly(unittest.TestCase):
    """Drive the actual CLI scripts as subprocesses; assert the wire is clean."""

    def _run(self, name, *args, timeout=30):
        srv = SafetyMockGdbServer()
        try:
            cmd = [sys.executable, str(_HERE / name),
                   "--port", str(srv.port), *args]
            subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        finally:
            srv.stop()
        return srv

    def _assert_clean(self, srv):
        self.assertEqual(srv.violations, [],
                         f"script emitted mutating packets: {srv.violations}")
        for cmd in srv.commands:
            self.assertTrue(command_allowed(cmd),
                            f"unexpected packet from script: {cmd!r}")

    def test_gdb_halt_inspect(self):
        self._assert_clean(self._run("gdb_halt_inspect.py", "--samples", "1"))

    def test_dump_regs_at_bp(self):
        srv = self._run("dump_regs_at_bp.py", "--addr", "0x100", "--timeout", "5")
        self._assert_clean(srv)
        self.assertFalse(any(c.startswith("Z0") for c in srv.commands))
        self.assertTrue(any(c.startswith("Z1") for c in srv.commands))

    def test_lockstep_mmio_capture_hw_only(self):
        srv = SafetyMockGdbServer()
        try:
            cmd = [sys.executable, str(_HERE / "lockstep_diff.py"),
                   "--mmio-capture", "--hw", f"127.0.0.1:{srv.port}",
                   "--watch", "0xe0600000:16", "--watch", "0xf0000000:8"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        finally:
            srv.stop()
        self._assert_clean(srv)

    def test_lockstep_full_diff_both_targets(self):
        hw = SafetyMockGdbServer()
        qemu = SafetyMockGdbServer()
        try:
            cmd = [sys.executable, str(_HERE / "lockstep_diff.py"),
                   "--hw", f"127.0.0.1:{hw.port}",
                   "--qemu", f"127.0.0.1:{qemu.port}",
                   "--bp", "0x100", "--steps", "3"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        finally:
            hw.stop()
            qemu.stop()
        for srv in (hw, qemu):
            self._assert_clean(srv)
            self.assertFalse(any(c.startswith("Z0") for c in srv.commands))


class TestXmdAgentDenylist(unittest.TestCase):
    """Channel B: xmd_agent.tcl must refuse mutating commands WITHOUT running
    them. Verified through tclsh (the same interpreter family as XMD's)."""

    @unittest.skipUnless(shutil.which("tclsh"), "tclsh not available")
    def test_denylist_refuses_before_execution(self):
        agent = _HERE / "xmd_agent.tcl"
        with tempfile.TemporaryDirectory() as d:
            tcl = f'''
                source {{{agent.as_posix()}}}
                set ::AGENT_DIR {{{Path(d).as_posix()}}}
                set ::AGENT_CMD "$::AGENT_DIR/xmd_cmd.txt"
                set ::AGENT_OUT "$::AGENT_DIR/xmd_out.txt"
                proc runcmd {{c}} {{
                    set f [open $::AGENT_CMD w]; puts -nonewline $f $c; close $f
                    agent_once
                    set f [open $::AGENT_OUT r]; set out [read $f]; close $f
                    return $out
                }}
                puts "RST=[runcmd {{rst}}]"
                puts "MWR=[runcmd {{mwr 0x0 0x1}}]"
                puts "DOW=[runcmd {{dow image.elf}}]"
                puts "ERASE=[runcmd {{erase}}]"
                puts "ALLOWED=[runcmd {{expr 40 + 2}}]"
                puts "DENYFN=[agent_denied {{mrd 0x0 4}}]/[agent_denied {{rrd}}]/[agent_denied {{bps 0x0 hw}}]/[agent_denied {{stp}}]"
            '''
            r = subprocess.run(["tclsh"], input=tcl, capture_output=True,
                               text=True, timeout=30)
            out = r.stdout
            self.assertEqual(r.returncode, 0, f"tclsh failed: {r.stderr}")

            # Every mutating command must be refused...
            for key in ("RST", "MWR", "DOW", "ERASE"):
                line = next(l for l in out.splitlines() if l.startswith(key + "="))
                self.assertIn("command refused", line, f"{key} not refused: {line}")
                # ...and refused BEFORE execution: an executed-but-failed command
                # would instead report 'invalid command name'.
                self.assertNotIn("invalid command", line,
                                 f"{key} was executed, not short-circuited: {line}")

            # A benign, non-denied command still runs (round-trip works).
            allowed = next(l for l in out.splitlines() if l.startswith("ALLOWED="))
            self.assertIn("42", allowed, f"allowed command did not run: {allowed}")

            # Real read-only XMD commands are NOT on the denylist.
            denyfn = next(l for l in out.splitlines() if l.startswith("DENYFN="))
            self.assertIn("=0/0/0/0", denyfn,
                          f"a read-only command was wrongly denied: {denyfn}")


class TestXmdRpcHostSide(unittest.TestCase):
    """xmd_rpc.py only shuttles strings; verify it surfaces agent errors and
    parses mrd output correctly (its read-only contract)."""

    def setUp(self):
        sys.path.insert(0, str(_HERE))
        import xmd_rpc  # noqa
        self.xmd_rpc = xmd_rpc

    def test_error_response_is_nonzero_exit(self):
        argv = ["xmd_rpc.py", "rst"]
        saved = sys.argv
        self.xmd_rpc.rpc = lambda *a, **k: "ERROR: command refused (read-only guard): rst"
        try:
            sys.argv = argv
            with contextlib.redirect_stdout(io.StringIO()):
                rc = self.xmd_rpc.main()
        finally:
            sys.argv = saved
        self.assertEqual(rc, 1, "an agent ERROR must yield a nonzero exit code")

    def test_mrd_parse_is_lossless(self):
        b = self.xmd_rpc.parse_mrd(
            "00000000:  DEADBEEF 00000001\n00000008:  CAFEBABE")
        self.assertEqual(b, bytes.fromhex("deadbeef00000001cafebabe"))


if __name__ == "__main__":
    unittest.main()
