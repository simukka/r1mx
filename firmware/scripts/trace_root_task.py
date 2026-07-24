#!/usr/bin/env python3
"""trace_root_task.py -- single-step the root task after the first context
switch (rfi @ 0x372838) to learn what it actually does.

re_reference.md §0.3 frontier: after the dispatch fix, the root task (entry
0x381a8c, descriptor r3=0x020390d0) runs but appears to "spin" in 0x380000..
0x383400.  Those addresses (0x3801cc, 0x380ea4, 0x382c78, 0x383000) are
string/buffer parsing helpers, so the "spin" may actually be a parser walking
a command/descriptor string -- i.e. forward progress, not a hang.

This tracer:
  1. boots QEMU -S, sets a temp BP at the rfi target so we land in the task,
  2. single-steps N instructions from there,
  3. records the full PC trace, the `bl` call targets (with the LR-return), and
     detects repeating cycles so we can tell "stuck loop" from "long parse".

Reuses the smoke_test / trace_dispatch_path GDB-RSP discipline.

Usage:
    python3 firmware/scripts/trace_root_task.py [--steps 4000] [--from 0x372838]
"""
from __future__ import annotations
import argparse, os, re, signal, socket, subprocess, sys, time
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
QEMU = Path.home() / "src/qemu-r1mx/build/qemu-system-ppc"
FW = _REPO / "firmware/reverse/build_32/extracted/software.bin"
PORT = 1234

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

    def read_mem(self, addr, n):
        h = self.q(f"m{addr:x},{n:x}")
        if not h or h[0] in "E":
            return None
        return bytes.fromhex(h)

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
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--from", dest="from_addr", type=lambda x: int(x, 0), default=0x372838,
                    help="temp BP to reach before stepping (default rfi 0x372838)")
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
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
                break
            except OSError:
                time.sleep(0.2)
        g = Gdb("127.0.0.1", PORT)
        g.q("?")

        # Reach the rfi, then step once to land in the task body.
        g.setbp(args.from_addr)
        g.cont()
        rep = g.wait(40.0)
        if rep is None:
            print("FAIL: never reached rfi target")
            return
        g.clrbp(args.from_addr)
        # step the rfi itself to enter the task
        g.step()
        r = g.regs()
        print(f"entered task: pc=0x{r['pc']:08x} msr=0x{r['msr']:08x} "
              f"lr=0x{r['lr']:08x} r3=0x{r['r3']:08x} sp=0x{r['r1']:08x}\n")

        trace = []
        calls = []         # (caller_pc, target, lr)
        prev_pc = None
        msr_seen = set()
        for i in range(args.steps):
            r = g.regs()
            pc = r["pc"]
            trace.append(pc)
            msr_seen.add(r["msr"] & 0x8000)  # EE bit
            # detect a call: pc jumps far while a fresh LR points just after prev
            if prev_pc is not None and abs(pc - prev_pc) > 0x40:
                lr = r["lr"]
                if lr == prev_pc + 4:
                    calls.append((prev_pc, pc, lr))
            prev_pc = pc
            rep = g.step()
            if rep is None:
                print(f"  [step stalled at #{i}, pc=0x{pc:08x}]")
                break
            # bail early if we left the task region into kernel/clk
            if pc == 0x942c:
                print("  *** reached sysClkEnable (0x942c)! ***")
                break
            if pc == 0x124:
                print("  *** reached halt loop 0x124 (regression) ***")
                break

        print(f"stepped {len(trace)} instrs")
        lo, hi = min(trace), max(trace)
        print(f"PC range: 0x{lo:08x}..0x{hi:08x}")
        print(f"MSR.EE bit values seen: {sorted(hex(x) for x in msr_seen)}")
        uniq = sorted(set(trace))
        print(f"unique PCs: {len(uniq)}")

        print("\n--- top 20 hottest PCs ---")
        for pc, c in Counter(trace).most_common(20):
            print(f"  {c:5d}x  0x{pc:08x}")

        print("\n--- distinct call targets (bl) ---")
        ctgt = Counter(t for _, t, _ in calls)
        for tgt, c in ctgt.most_common(40):
            print(f"  {c:4d}x  -> 0x{tgt:08x}")

        # cycle detection: smallest period such that trace repeats at the tail
        tail = trace[-min(len(trace), 800):]
        period = None
        for p in range(1, len(tail) // 3):
            if tail[-p:] == tail[-2 * p:-p] == tail[-3 * p:-2 * p]:
                period = p
                break
        if period:
            cyc = tail[-period:]
            print(f"\n*** TAIL CYCLE detected, period {period} instrs ***")
            print(f"    cycle PCs: {[hex(x) for x in sorted(set(cyc))]}")
        else:
            print("\nno tight tail cycle (<= ~260) -- task is making forward progress")
        g.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
