#!/usr/bin/env python3
"""trace_dispatch_path.py -- trace the kernelInit -> taskActivate -> windExit ->
context-switch dispatch path to find exactly where the first context switch is
(or is not) taken.

Background (re_reference.md §0.3): kernelInit (0x5a7f30) ENTERS and RETURNS in
the current QEMU build, instead of context-switching into the root task and
never returning.  The last call in kernelInit is `bl 0x5b11ac` (taskActivate,
thunk -> 0x5b0ff4) at 0x5a8190.  taskActivate adds the root task to the ready
queue (bl 0x5b57b0) then calls windExit (bl 0x372534).  windExit may call
reschedule (0x3723c0).  The actual context switch into a task is the routine
at 0x372638..0x372838 which saves the current context, branches to the
scheduler core (0x5aaf5c) to pick the next task, restores the new TCB, and
`rfi`s into it at 0x372838 (loading the task's MSR with EE=1 and its PC).

This tracer sets breakpoints at each waypoint and logs the order/regs they fire
so we can see how far the first dispatch gets.  Uses the proven smoke_test
GDB-RSP discipline: standard ACK mode, and on each hit clear-the-BP / single-step
/ re-insert so `continue` actually advances (QEMU re-triggers a BP_GDB if you
continue while parked on it).

Usage:
    python3 firmware/scripts/trace_dispatch_path.py [--max-hits 80] [--timeout 40]
"""
from __future__ import annotations
import argparse, os, re, signal, socket, subprocess, sys, time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
QEMU = Path.home() / "src/qemu-r1mx/build/qemu-system-ppc"
FW = _REPO / "firmware/reverse/build_32/extracted/software.bin"
PORT = 1234

WAYPOINTS = {
    0x5a8190: "kernelInit: bl taskActivate (last call)",
    0x5a8194: "kernelInit: RETURN point (post-taskActivate) -- abnormal if hit",
    0x5b0ff4: "taskActivate entry",
    0x5b57b0: "windAdd-to-readyQ (bl from taskActivate)",
    0x372534: "windExit entry",
    0x3723c0: "reschedule entry",
    0x372638: "ctxswitch SAVE side (windExit low-level)",
    0x5aaf5c: "scheduler core (pick next task)",
    0x372838: "*** rfi INTO TASK (context switch happens) ***",
    0x36c428: "usrInit: post-kernelInit return -- kernelInit RETURNED",
    0x000124:  "halt loop (terminal)",
}

PPC = [f"r{i}" for i in range(32)] + ["pc", "msr", "cr", "lr", "ctr", "xer"]


def cksum(b: bytes) -> bytes:
    return f"{sum(b) & 0xff:02x}".encode()


class Gdb:
    def __init__(self, host, port, timeout=15.0):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(None)

    def _send(self, p):
        self.s.sendall(b"$" + p.encode() + b"#" + cksum(p.encode()))
        a = self.s.recv(1)
        if a not in (b"+", b"-"):
            raise RuntimeError(f"bad ack {a!r}")

    def _recv(self, timeout):
        self.s.settimeout(timeout)
        try:
            while True:
                b = self.s.recv(1)
                if not b:
                    raise RuntimeError("closed")
                if b == b"$":
                    break
            buf = bytearray()
            while True:
                b = self.s.recv(1)
                if b == b"#":
                    self.s.recv(2)
                    break
                buf.extend(b)
            self.s.sendall(b"+")
            return buf.decode("latin-1")
        finally:
            self.s.settimeout(None)

    def q(self, p, timeout=5.0):
        self._send(p)
        return self._recv(timeout)

    def regs(self):
        h = self.q("g")
        r = {}
        for i, n in enumerate(PPC):
            c = h[i * 8:i * 8 + 8]
            if len(c) < 8:
                break
            try:
                r[n] = int(c, 16)
            except ValueError:
                break
        return r

    def setbp(self, a):
        return self.q(f"Z0,{a:x},4") == "OK"

    def clrbp(self, a):
        try:
            self.q(f"z0,{a:x},4")
        except Exception:
            pass

    def step(self):
        self.s.sendall(b"$s#73")
        return self._wait(5.0)

    def cont(self):
        self.s.sendall(b"$c#63")

    def _wait(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            rem = deadline - time.monotonic()
            if rem <= 0:
                return None
            try:
                r = self._recv(rem)
            except socket.timeout:
                return None
            if r and r[0] in ("T", "S", "W", "X"):
                return r

    def wait(self, timeout):
        return self._wait(timeout)

    def interrupt(self):
        self.s.sendall(b"\x03")
        try:
            return self._recv(5.0)
        except socket.timeout:
            return None

    def close(self):
        try:
            self._send("D")
        except Exception:
            pass
        self.s.close()


def kill_port(port):
    try:
        out = subprocess.check_output(["ss", "-tlnpH", f"sport = :{port}"],
                                      stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            m = re.search(r"pid=(\d+)", line)
            if m:
                try:
                    os.kill(int(m.group(1)), signal.SIGKILL)
                except ProcessLookupError:
                    pass
    except Exception:
        pass


def main():
    global FW
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-hits", type=int, default=80)
    ap.add_argument("--timeout", type=float, default=40.0)
    ap.add_argument("--firmware", type=Path, default=FW)
    args = ap.parse_args()
    FW = args.firmware

    kill_port(PORT)
    time.sleep(0.2)
    proc = subprocess.Popen(
        [str(QEMU), "-machine", "r1mx-virtex4", "-m", "2048", "-nographic",
         "-device", f"loader,file={FW},addr=0x10000,force-raw=on",
         "-S", "-gdb", f"tcp::{PORT}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        # wait for port
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
                break
            except OSError:
                time.sleep(0.2)
        g = Gdb("127.0.0.1", PORT)
        g.q("?")
        r0 = g.regs()
        if r0.get("pc", -1) != 0:
            print(f"WARN: not fresh boot, pc=0x{r0.get('pc',0):08x}")
        for a in WAYPOINTS:
            g.setbp(a)
        print(f"Set {len(WAYPOINTS)} breakpoints. Tracing (max {args.max_hits} hits, "
              f"{args.timeout}s)...\n")
        t0 = time.monotonic()
        hits = 0
        counts = {}
        g.cont()
        while hits < args.max_hits and (time.monotonic() - t0) < args.timeout:
            rep = g.wait(args.timeout - (time.monotonic() - t0))
            if rep is None:
                print("  [timeout waiting for next stop]")
                g.interrupt()
                rr = g.regs()
                print(f"  halted at pc=0x{rr.get('pc',0):08x} msr=0x{rr.get('msr',0):08x}")
                break
            r = g.regs()
            pc = r.get("pc", 0)
            hits += 1
            counts[pc] = counts.get(pc, 0) + 1
            label = WAYPOINTS.get(pc, f"<unknown 0x{pc:08x}>")
            t = time.monotonic() - t0
            tag = f"#{hits:02d} +{t:5.2f}s"
            print(f"{tag}  pc=0x{pc:08x}  msr=0x{r.get('msr',0):08x}  "
                  f"lr=0x{r.get('lr',0):08x}  r3=0x{r.get('r3',0):08x}  {label}")
            if pc == 0x124:
                print("  --> reached terminal halt loop; stopping trace.")
                break
            # step off this BP then continue
            if pc in WAYPOINTS:
                g.clrbp(pc)
                g.step()
                g.setbp(pc)
            g.cont()
        print("\n--- hit histogram ---")
        for pc, c in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {c:3d}x  0x{pc:08x}  {WAYPOINTS.get(pc,'?')}")
        g.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
