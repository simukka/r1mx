#!/usr/bin/env python3
"""
upgrade_observe.py — operator-in-the-loop, READ-ONLY observation of what the live
RED ONE MX actually executes while the operator walks the firmware-upgrade menu
(insert USB -> SYSTEM -> SETUP -> MAINTENANCE -> UPDATE SW -> confirm).

WHY THIS EXISTS
---------------
upgrade_bypass_test.py arms four HARDWARE breakpoints at addresses we *guessed*
(from static analysis of software.bin) were the upgrade pipeline
(extract/verify/wrapper/flash). On a known-good repackage that the camera DOES
install, NONE of them fire. A passing single-slot self-test proves Z1 works, so
the conclusion is that those addresses are simply NOT on the code path the menu
runs — predicting the path failed. So instead of predicting, OBSERVE it.

HOW (PC sampling / poor-man's profiler over JTAG)
-------------------------------------------------
At each operator step we take a BURST of samples: halt the core, read PC + LR +
the current task + a short stack backtrace, resume; repeat. Translation:

    image_offset = live_PC - reloc            (cam-working-01 reloc = 0x10180)

and resolve image_offset -> containing function via manifest.csv (same FuncTable
task_walker uses, with prologue back-scan for gaps).

  * UI navigation is idle-loop bound — samples land in the scheduler idle loop,
    confirming "nothing upgrade-ish yet".
  * AES-256 decrypt, gunzip, RSA verify and NOR flash are CPU-BOUND — during the
    real upgrade the busy task dominates, so a handful of samples catch the true
    code addresses and call stacks. THOSE are the real breakpoint waypoints.

The output is a per-step PC histogram + the union of functions/stacks seen during
the upgrade window — i.e. the actual extract->verify->flash path, with image
offsets you can feed straight back into upgrade_bypass_test.py --extract-addr/etc.

SAFETY
------
READ-ONLY by construction: RSP(allow_write=False) — no memory/register writes, no
reset, HARDWARE breakpoints are never even used here (pure halt/sample/resume).
Brief halts during the setup/upgrade phase are safe (same discipline as the
bypass test). Target the WORKING camera; do NOT sample during active recording.

USAGE
-----
  # forward the XMD stub to the host first (host_xmd_bridge.md):
  #   VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"
  python3 firmware/scripts/upgrade_observe.py --reloc 0x10180

  # tune burst size / the during-upgrade capture length:
  python3 firmware/scripts/upgrade_observe.py --reloc 0x10180 \
      --samples 80 --watch-secs 90 --depth 8
"""
from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from rsp import RSP, RSPError                      # noqa: E402  read-only client
from task_walker import FuncTable, TASK_ID_CURRENT  # noqa: E402  PC->func + cur task
from reloc_verify import RelocVerifier, RelocError  # noqa: E402  preflight reloc gate

# DRAM-ready canary (re_reference.md §9): cheap "live camera + DRAM up?" read.
CANARY_ADDR = 0x00E269A4
CANARY_VAL = 0x12348765

# The ordered manual steps. Each is a SHORT burst (camera should be idle for all
# but the last). The last entry switches to continuous capture of the upgrade.
STEPS = [
    ("baseline", "Camera booted & IDLE, USB NOT inserted yet. Just confirm."),
    ("usb_in",   "Insert the upgrade USB stick (do not touch the menu yet)."),
    ("system",   "Press SYSTEM on the camera."),
    ("setup",    "Navigate to SETUP."),
    ("maint",    "Navigate to MAINTENANCE."),
    ("update_hl","HIGHLIGHT 'UPDATE SW' (do NOT select it yet)."),
]


# ----------------------------------------------------------------------------
def banner(msg):
    print("\n" + "=" * 72 + f"\n{msg}\n" + "=" * 72)


def confirm(prompt):
    print("\n>>> " + prompt)
    try:
        if input("    [Enter] when done, or 'q' to abort: ").strip().lower() == "q":
            print("[abort] operator aborted.")
            sys.exit(2)
    except (EOFError, KeyboardInterrupt):
        print("\n[abort] operator aborted.")
        sys.exit(2)


def check_vm_running(vm_name):
    try:
        out = subprocess.run(["VBoxManage", "list", "runningvms"],
                             capture_output=True, text=True, timeout=15)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return f'"{vm_name}"' in out.stdout


# ----------------------------------------------------------------------------
class Observer:
    """Halt/sample/resume the live PPC405 over the XMD GDB stub, READ-ONLY."""

    def __init__(self, t: RSP, ft: FuncTable, reloc: int, depth: int):
        self.t = t
        self.ft = ft
        self.reloc = reloc
        self.depth = depth
        self._names: dict[int, str | None] = {}   # tcb -> task name cache

    # PC/LR are code addresses (numbers): resolve them even though .text is
    # I-side-only and unreadable as data on an idle camera.
    def fname(self, live_addr: int) -> str:
        if not live_addr:
            return "0"
        fn = self.ft.resolve((live_addr - self.reloc) & 0xFFFFFFFF)
        if fn is None:
            return f"?@0x{live_addr:08x}"
        tag = "(gap)" if fn.get("in_gap") else ""
        return f"{fn['name']}+0x{fn['off']:x}{tag}"

    def _read_word(self, addr: int):
        try:
            return self.t.read_word(addr)
        except (RSPError, ValueError):
            return None

    def backtrace(self, pc: int, sp: int) -> list[int]:
        """Best-effort PPC back-chain unwind. Each frame: *(sp)=caller frame,
        *(caller+4)=return addr the callee stored. Stack (DDR) reads fine even
        when .text is unreadable. Numbers only — resolved later."""
        chain = [pc]
        frame = sp
        for _ in range(self.depth):
            if not frame or frame & 3 or not (0x00400000 <= frame <= 0x0fffffff):
                break
            caller = self._read_word(frame)
            if not caller or caller <= frame:        # back chain grows upward
                break
            lr = self._read_word(caller + 4)
            if not lr:
                break
            chain.append(lr & 0xFFFFFFFF)
            frame = caller
        return chain

    def task_name(self, tcb: int) -> str | None:
        """Scan a TCB's pointer fields for one that points at a short ASCII name
        (same heuristic as task_walker.find_name, via RSP reads). Cached."""
        if tcb in self._names:
            return self._names[tcb]
        name = None
        try:
            blk = self.t.read_mem(tcb, 0x80)
        except RSPError:
            self._names[tcb] = None
            return None
        words = [int.from_bytes(blk[i:i + 4], "big") for i in range(0, len(blk), 4)]
        for w in words:
            if not (0x00100000 <= w <= 0x0a000000):
                continue
            try:
                s = self.t.read_mem(w, 32)
            except RSPError:
                continue
            s = s.split(b"\x00", 1)[0]
            if 2 <= len(s) <= 31 and all(32 <= c < 127 for c in s) \
               and (s[0:1].isalpha() or s[0:1] == b"_"):
                name = s.decode("ascii", "replace")
                break
        self._names[tcb] = name
        return name

    def sample(self) -> dict | None:
        """One halt/read/resume cycle. Returns {pc,lr,sp,tcb,stack} or None."""
        try:
            self.t.interrupt(10.0)
        except (RSPError, socket.timeout, TimeoutError):
            return None
        regs = self.t.regs()
        pc = regs.get("pc", 0) & 0xFFFFFFFF
        lr = regs.get("lr", 0) & 0xFFFFFFFF
        sp = regs.get("r1", 0) & 0xFFFFFFFF
        tcb = self._read_word(TASK_ID_CURRENT)
        stack = self.backtrace(pc, sp)
        self.t.send("c")                              # resume; keep the camera live
        return {"pc": pc, "lr": lr, "sp": sp, "tcb": tcb, "stack": stack}

    def burst(self, n: int, interval: float) -> dict:
        """Take n samples; aggregate a function histogram + top call stacks."""
        pc_hist: Counter = Counter()
        stack_hist: Counter = Counter()
        tcbs: Counter = Counter()
        raw = []
        got = 0
        for _ in range(n):
            s = self.sample()
            if s is None:
                continue
            got += 1
            pc_hist[self.fname(s["pc"])] += 1
            stack_hist[" <- ".join(self.fname(a) for a in s["stack"])] += 1
            if s["tcb"]:
                tcbs[s["tcb"]] += 1
            raw.append(s)
            if interval:
                time.sleep(interval)
        return {"n": got, "pc_hist": pc_hist, "stack_hist": stack_hist,
                "tcbs": tcbs, "raw": raw}

    def watch(self, secs: float, interval: float, report_every: float) -> dict:
        """Continuous sampling for `secs` (the actual upgrade). Prints a rolling
        top-function view so the operator sees the pipeline advance live."""
        pc_hist: Counter = Counter()
        stack_hist: Counter = Counter()
        tcbs: Counter = Counter()
        raw = []
        t0 = time.time()
        last = t0
        got = 0
        while time.time() - t0 < secs:
            s = self.sample()
            if s is None:
                continue
            got += 1
            fn = self.fname(s["pc"])
            pc_hist[fn] += 1
            stack_hist[" <- ".join(self.fname(a) for a in s["stack"])] += 1
            if s["tcb"]:
                tcbs[s["tcb"]] += 1
            raw.append(s)
            now = time.time()
            if now - last >= report_every:
                top = pc_hist.most_common(4)
                print(f"  [{now - t0:5.1f}s] {got:4d} samples | "
                      + " | ".join(f"{f} x{c}" for f, c in top))
                last = now
            if interval:
                time.sleep(interval)
        return {"n": got, "pc_hist": pc_hist, "stack_hist": stack_hist,
                "tcbs": tcbs, "raw": raw}


# ----------------------------------------------------------------------------
def print_burst(label, b: dict, idle_fn: str | None):
    n = b["n"]
    if not n:
        print(f"  [{label}] no samples (could not halt the core).")
        return
    idle_hits = b["pc_hist"].get(idle_fn, 0) if idle_fn else 0
    busy = n - idle_hits
    print(f"  [{label}] {n} samples"
          + (f" — {100*idle_hits//n}% in idle ({idle_fn})" if idle_fn else "")
          + (f", {busy} NON-IDLE" if idle_fn else ""))
    for fn, c in b["pc_hist"].most_common(6):
        flag = "  <- idle" if fn == idle_fn else ""
        print(f"        {c:4d}  {fn}{flag}")


def summarize_funcs(b: dict, reloc: int, ft: FuncTable, idle_fn: str | None):
    """Turn the during-upgrade histogram into candidate breakpoint waypoints:
    function entry image offsets you can pass to upgrade_bypass_test.py."""
    out = []
    for fn, c in b["pc_hist"].most_common():
        if fn == idle_fn or fn.startswith("?@") or fn == "0":
            continue
        # fn looks like 'NAME+0xoff'; recover the entry image offset.
        name = fn.split("+", 1)[0]
        out.append((name, c))
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345,
                    help="XMD GDB stub, host side (host_xmd_bridge.md)")
    ap.add_argument("--vm-name", default="r1mx_32")
    ap.add_argument("--no-vm-check", action="store_true")
    ap.add_argument("--reloc", type=lambda s: int(s, 0), default=0x10180,
                    help="live_PC - reloc = image offset (cam-working-01=0x10180)")
    ap.add_argument("--force-reloc", action="store_true",
                    help="continue even if the reloc preflight check fails")
    ap.add_argument("--manifest", default=str(
        _HERE.parent / "reverse/build_32/src/manifest.csv"))
    ap.add_argument("--image", default=str(
        _HERE.parent / "reverse/build_32/extracted/software.bin"))
    ap.add_argument("--samples", type=int, default=60,
                    help="samples per per-step burst")
    ap.add_argument("--depth", type=int, default=6, help="backtrace depth")
    ap.add_argument("--interval", type=float, default=0.0,
                    help="extra sleep between samples (s); 0 = as fast as JTAG allows")
    ap.add_argument("--watch-secs", type=float, default=90.0,
                    help="seconds to sample continuously during the upgrade")
    ap.add_argument("--report-every", type=float, default=3.0,
                    help="rolling-print cadence during the watch (s)")
    ap.add_argument("--id", default="cam-working-01")
    ap.add_argument("--out", default=str(
        _HERE.parent / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    banner("upgrade_observe — READ-ONLY live PC sampling of the upgrade menu path")
    if not args.no_vm_check:
        vm = check_vm_running(args.vm_name)
        if vm is None:
            print("  [warn] could not run VBoxManage — skipping VM check.")
        elif vm:
            print(f"  [ok]   VM '{args.vm_name}' is running")
        else:
            sys.exit(f"  [FAIL] VM '{args.vm_name}' not running. Start it, then "
                     f"`xmd; connect ppc hw`.")

    ft = FuncTable(Path(args.manifest), Path(args.image))
    try:
        t = RSP(args.host, args.port, allow_write=False, timeout=15.0,
                label="xmd-hw").connect()
    except OSError as e:
        sys.exit(f"  [FAIL] cannot reach {args.host}:{args.port} ({e}).\n"
                 f"         VBoxManage controlvm {args.vm_name} natpf1 "
                 f'"xmdgdb,tcp,127.0.0.1,{args.port},,1234"  and `connect ppc hw`.')

    obs = Observer(t, ft, args.reloc, args.depth)
    report = {
        "camera_id": args.id, "tool": "upgrade_observe",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "reloc": f"0x{args.reloc:08x}", "transport": "RSP/XMD-gdbstub (read-only)",
        "samples_per_burst": args.samples, "watch_secs": args.watch_secs,
        "steps": [],
    }
    idle_fn = None
    try:
        # preflight: refuse to run with a wrong --reloc (else every PC mis-resolves)
        rv = RelocVerifier.from_rsp(t, ft)
        try:
            rv.assert_reloc(args.reloc)
        except RelocError as e:
            if args.force_reloc:
                print(f"  [warn] {e}\n  [warn] --force-reloc set; continuing anyway.")
            else:
                sys.exit(f"  [FAIL] {e}\n         re-run with --reloc <correct> "
                         f"(camera_probe.py --phases reloc), or --force-reloc.")

        # liveness + DRAM sanity
        try:
            cv = t.read_word(CANARY_ADDR)
            print(f"  [{'ok' if cv == CANARY_VAL else 'warn'}] DRAM canary "
                  f"@0x{CANARY_ADDR:08x}=0x{cv:08x} (expect 0x{CANARY_VAL:08x})")
        except RSPError as e:
            print(f"  [warn] canary read failed: {e}")

        # ---- per-step bursts (camera idle for all of these) ----
        for key, prompt in STEPS:
            confirm(prompt)
            b = obs.burst(args.samples, args.interval)
            if key == "baseline" and b["pc_hist"]:
                idle_fn = b["pc_hist"].most_common(1)[0][0]
                print(f"  [idle] dominant idle-loop function: {idle_fn}")
            print_burst(key, b, idle_fn)
            report["steps"].append({
                "step": key, "n": b["n"],
                "pc_hist": dict(b["pc_hist"].most_common()),
                "stack_hist": dict(b["stack_hist"].most_common(8)),
                "tcbs": {f"0x{k:08x}": (obs.task_name(k), v)
                         for k, v in b["tcbs"].most_common()},
            })

        # ---- the real thing: select UPDATE SW, then sample continuously ----
        banner("SELECT 'UPDATE SW' NOW — sampling the upgrade pipeline")
        confirm("Select 'UPDATE SW' (and confirm any prompt) to START the upgrade.")
        print(f"  [watch] sampling for {args.watch_secs:.0f}s "
              f"(idle = {idle_fn}) ...")
        w = obs.watch(args.watch_secs, args.interval, args.report_every)

        banner("UPGRADE WINDOW — what actually executed")
        print_burst("upgrade", w, idle_fn)
        print("\n  Top call stacks during the upgrade (outermost last):")
        for stk, c in w["stack_hist"].most_common(8):
            print(f"    x{c:<4d} {stk}")
        print("\n  Candidate breakpoint waypoints (non-idle functions seen):")
        cands = summarize_funcs(w, args.reloc, ft, idle_fn)
        for name, c in cands[:12]:
            # recover entry image offset from the manifest for a ready-to-use addr
            row = next((r for r in zip(ft.addrs, ft.rows) if r[1][2] == name), None)
            img = row[0] if row else None
            extra = f"  img=0x{img:08x}  live=0x{(img+args.reloc)&0xffffffff:08x}" \
                    if img is not None else ""
            print(f"    x{c:<4d} {name}{extra}")
        report["steps"].append({
            "step": "upgrade", "n": w["n"],
            "pc_hist": dict(w["pc_hist"].most_common()),
            "stack_hist": dict(w["stack_hist"].most_common(16)),
            "tcbs": {f"0x{k:08x}": (obs.task_name(k), v)
                     for k, v in w["tcbs"].most_common()},
            "candidates": [{"name": n, "hits": c} for n, c in cands],
        })
    finally:
        try:
            t.detach()        # resume + detach so we never leave it halted
        except Exception:
            pass
        t.close()

    outdir = Path(args.out) / args.id
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "").replace("-", "")
    jpath = outdir / f"upgrade_observe_{stamp}.json"
    jpath.write_text(json.dumps(report, indent=2))
    print(f"\n[*] report written: {jpath}")
    print("    -> feed the candidate img offsets into upgrade_bypass_test.py "
          "(--extract-addr/--verify-addr/--wrapper-addr/--flash-addr).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
