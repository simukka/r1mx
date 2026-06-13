#!/usr/bin/env python3
"""
usb_shell_enable.py — bring up the VxWorks shell on the USB CDC-ACM port
(the camera's USB Type-B), driven over JTAG/XMD via the shared RSP client.

WHY THIS EXISTS
---------------
The firmware already knows how to put a shell on the USB serial port — when the
`DEBUG.USB.CONNECTION` param goes non-zero, `UiUsbSerial::ProcessUsbDebugChange`
calls `runTargetShell()`, which opens the CDC tty and spawns a shell on it.
But (see debug_interfaces.md "Static Trace", 2026-06-10) that path can't be
triggered by poking a static address: the param value is a heap-resident object,
and `runTargetShell`/`ProcessUsbDebugChange` aren't statically resolvable (the
decompiled corpus is incomplete and the references are data-table-driven).

So instead of triggering the firmware's path, we reproduce it directly on the
live target: open "/tyCo/cdc0" and call the shell-session creator on that fd.

WHAT IS PINNED (static analysis)
--------------------------------
  CDC-ACM tty device name : "/tyCo/cdc0"  @ 0xD2A9D8   (matches live /dev/ttyACM0)
  shell-session creator   : 0x001BBB14  (shellGenericInit-family; both shell-lib
                            call sites bl here: 0x1B3D98, 0x1B4684)
    -> core               : 0x001BB014  -> shellBackgroundInit @ 0x1B9E5C
  login gate              : shellLoginInstall @ 0xE1E13C
  live shell-config block : globals at 0xE1350C..0xE13544 (the exact values the
                            running console shell was created with — read these,
                            don't fabricate them), shell-name buffer @ 0x10CF434

WHAT IS *NOT* statically resolvable (capture phase resolves these on the target)
--------------------------------------------------------------------------------
  - open() / iosOpen()    : NOT in the (partial) static symbol table.
  - exact arg-slot mapping of 0x1BBB14 (which of the config words are fdIn/Out/Err
    vs stack size / name / flags). The capture phase dumps the live block so the
    operator can confirm the mapping against a known-good (console) shell.

SAFETY
------
Reads are always allowed. Anything that writes target memory/regs (the ARM phase)
requires --allow-write AND an idle camera AND operator confirmation. Halting a
camera mid-record aborts the recording (see memory: recording-halt-disrupts-realtime)
— arm only while idle. The harness always restores the pre-call register state and
resumes the CPU on exit.

Typical use:
  # 1) read-only: dump live config + resolve open(), print the call plan
  python3 usb_shell_enable.py capture
  # 2) arm (idle camera; fill --open-addr from capture output):
  python3 usb_shell_enable.py arm --allow-write --open-addr 0x00XXXXXX
"""
import argparse
import sys
import time

from rsp import RSP, RSPError, WriteDisabled

# ---- pinned constants (build_32, flat image: VA == file offset) -------------
CDC_DEV_STR      = 0x00D2A9D8       # "/tyCo/cdc0"
SHELL_GEN_INIT   = 0x001BBB14       # shellGenericInit-family entry
SHELL_CFG_BASE   = 0x00E13000       # the call sites lwz config from 0xE135xx
SHELL_CFG_OFFS   = [0x350C, 0x351C, 0x3520, 0x3524, 0x3528,
                    0x352C, 0x3530, 0x3534, 0x3538, 0x3544]
SHELL_NAME_BUF   = 0x010CF434       # 0x10D0000 - 0xBCC, from `addi r4,_,-0xBCC`
WDB_PORT_CANARY  = 0x00E9C4BC       # reads 0x00004321 on a live, booted target

O_RDWR = 2

# A mapped, aligned text address used only as a return-catcher: we set LR here and
# place a HW breakpoint on it, so the CPU halts the instant the called function
# returns (the instruction is never executed). Override with --trap if needed.
DEFAULT_TRAP = 0x001B9E5C           # shellBackgroundInit entry (never executed)


# ---- console helpers (mirrors upgrade_bypass_test.py conventions) -----------
def banner(msg):
    print("\n" + "=" * 72 + f"\n{msg}\n" + "=" * 72)


def confirm(prompt):
    print("\n>>> " + prompt)
    if input("    [Enter] to proceed, or 'q' to abort: ").strip().lower() == "q":
        sys.exit("aborted by operator")


def sanity_alive(t):
    """Read the WDB-port canary; proves DRAM is up and we're talking to a booted
    target (read-only)."""
    v = t.read_word(WDB_PORT_CANARY)
    ok = (v & 0xFFFF) == 0x4321
    print(f"  canary 0x{WDB_PORT_CANARY:08x} = 0x{v:08x} "
          f"({'OK — target booted' if ok else 'UNEXPECTED'})")
    return ok


# ---- the reusable artifact: call a target function over RSP -----------------
def call_remote(t, pc, gpr_args=(), *, stack_args=(), trap=DEFAULT_TRAP,
                timeout=20.0, restore=True):
    """Invoke target function at `pc` with PPC SysV args and return r3.

    gpr_args   : up to 8 ints -> r3..r10
    stack_args : ints placed at the parameter-save area (sp+8, +12, ...) for the
                 9th+ argument, if ever needed.
    Mechanism : save regs -> set args/PC/LR=trap -> HW bp @trap -> cont -> read r3
                -> restore regs. Requires allow_write. The HW bp never patches
                memory (Z1), keeping the camera's RAM untouched apart from the
                args we set and any scratch the caller wrote.
    """
    if not t.allow_write:
        raise WriteDisabled("call_remote needs RSP(allow_write=True)")
    if len(gpr_args) > 8:
        raise ValueError("more than 8 GPR args; use stack_args for the rest")

    saved = t.regs()
    sp = saved["r1"]
    try:
        for i, a in enumerate(gpr_args):
            t.write_reg(f"r{3 + i}", a & 0xFFFFFFFF)
        # PPC SysV: stack args start at sp+8 (after backchain + LR save word).
        for i, a in enumerate(stack_args):
            t.write_mem(sp + 8 + 4 * i, (a & 0xFFFFFFFF).to_bytes(4, "big"))
        t.write_reg("lr", trap)
        t.write_reg("pc", pc)

        if not t.set_bp(trap, hw=True):
            raise RSPError(f"could not set HW bp @0x{trap:08x}")
        stop = t.cont(timeout)
        t.clear_bp(trap, hw=True)
        if not (stop.startswith("T") or stop.startswith("S")):
            raise RSPError(f"call did not return cleanly: stop={stop!r}")

        end = t.regs()
        if end.get("pc", 0) != trap:
            print(f"  [warn] returned at pc=0x{end.get('pc',0):08x}, "
                  f"expected trap 0x{trap:08x}")
        return end["r3"] & 0xFFFFFFFF
    finally:
        if restore:
            for name in ("r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10",
                         "lr", "pc", "r1"):
                if name in saved:
                    try:
                        t.write_reg(name, saved[name])
                    except Exception:
                        pass


# ---- a runtime symbol-table search (resolves what the static symtab omits) --
def find_symbol(t, name, windows):
    """Linear-scan the in-RAM VxWorks symbol table for `name`.
    Entry layout (build_32): {flags, 0, char* nameptr, void* value, 0}, stride
    0x14, nameptr is absolute (VA == file offset). Returns value or None.
    `windows` is a list of (lo, hi) byte ranges to scan."""
    want = name.encode() + b"\x00"
    for lo, hi in windows:
        addr = lo
        CHUNK = 0x8000
        while addr < hi:
            blk = t.read_mem(addr, min(CHUNK, hi - addr))
            for off in range(0, len(blk) - 0x14, 4):
                namep = int.from_bytes(blk[off + 8:off + 12], "big")
                if not (0xC00000 <= namep < 0xF00000):
                    continue
                # cheap name check: read just enough bytes for the candidate
                try:
                    s = t.read_mem(namep, len(want))
                except RSPError:
                    continue
                if s == want:
                    val = int.from_bytes(blk[off + 12:off + 16], "big")
                    return val
            addr += CHUNK - 0x14
    return None


SYMTAB_WINDOWS = [(0x00E2B000, 0x00E78000), (0x00E31000, 0x00E36000)]


# ---- phases -----------------------------------------------------------------
def phase_capture(t, args):
    banner("CAPTURE (read-only): live shell-config + symbol resolution")
    if not sanity_alive(t) and not args.force:
        sys.exit("canary mismatch — target may not be booted (use --force to override)")

    dev = t.read_mem(CDC_DEV_STR, 16).split(b"\x00", 1)[0].decode("latin1", "replace")
    print(f"\n  CDC device string @0x{CDC_DEV_STR:08x} = {dev!r} "
          f"({'OK' if dev == '/tyCo/cdc0' else 'UNEXPECTED'})")

    print("\n  live shell-config block (values the console shell was created with):")
    for o in SHELL_CFG_OFFS:
        a = SHELL_CFG_BASE + o
        v = t.read_word(a)
        print(f"    0x{a:08x} = 0x{v:08x}")
    nm = t.read_mem(SHELL_NAME_BUF, 32).split(b"\x00", 1)[0].decode("latin1", "replace")
    print(f"    shell-name buf @0x{SHELL_NAME_BUF:08x} = {nm!r}")

    print("\n  resolving runtime-only symbols from the in-RAM symbol table ...")
    for sym in ("open", "iosOpen", "close"):
        v = find_symbol(t, sym, SYMTAB_WINDOWS)
        print(f"    {sym:10s} -> " + (f"0x{v:08x}" if v else "NOT FOUND "
              "(widen SYMTAB_WINDOWS or pass --open-addr manually)"))

    print("\n  PLAN for `arm`:")
    print("    fd = open(0x%08x \"/tyCo/cdc0\", O_RDWR=2, 0)" % CDC_DEV_STR)
    print("    shellGenericInit(0x%08x) with the config block above, fdIn=fdOut=fdErr=fd" % SHELL_GEN_INIT)
    print("    -> confirm which config words are the fd slots against a known-good")
    print("       console shell before arming.")


def phase_arm(t, args):
    banner("ARM (writes target memory/regs): spawn shell on /tyCo/cdc0")
    if not args.open_addr:
        sys.exit("need --open-addr (run `capture` first to resolve open())")
    if not sanity_alive(t) and not args.force:
        sys.exit("canary mismatch — refusing to arm")

    confirm("Confirm the camera is IDLE (not recording). Arming writes registers "
            "and a scratch string to RAM, then calls open()+shellGenericInit().")

    # scratch buffer for the device-path arg: low on the current stack, well clear
    # of the active frame. We could also just reuse CDC_DEV_STR directly (it's a
    # valid "/tyCo/cdc0\0" in rodata) — prefer that, no write needed:
    dev_ptr = CDC_DEV_STR

    print("\n  [1/2] fd = open(\"/tyCo/cdc0\", O_RDWR, 0)")
    fd = call_remote(t, args.open_addr, (dev_ptr, O_RDWR, 0),
                     trap=args.trap, timeout=args.timeout)
    fd_s = fd if fd < 0x80000000 else fd - 0x100000000
    print(f"      open() returned fd = {fd_s} (0x{fd:08x})")
    if fd_s < 0:
        sys.exit("open() failed (negative fd) — device busy or wrong name")

    # Assemble shellGenericInit args from the captured config + our fd. The exact
    # vector is confirmed in the capture phase; --dry-run prints it without calling.
    cfg = [t.read_word(SHELL_CFG_BASE + o) for o in SHELL_CFG_OFFS]
    # Provisional mapping: pass the live config words through, override the trailing
    # three (fdIn/fdOut/fdErr) with our fd. Operator confirms slot order in capture.
    gpr = (SHELL_NAME_BUF, cfg[0], cfg[1], cfg[2], cfg[3], fd, fd, fd)
    print("\n  [2/2] shellGenericInit(...) gpr_args = " +
          ", ".join(f"0x{x:08x}" for x in gpr))
    if args.dry_run:
        print("      --dry-run: not calling. Confirm the arg vector, then re-run "
              "without --dry-run.")
        return
    rc = call_remote(t, SHELL_GEN_INIT, gpr, trap=args.trap, timeout=args.timeout)
    print(f"      shellGenericInit returned 0x{rc:08x}")
    print("\n  If it succeeded, open /dev/ttyACM0 on the host and press Enter for a prompt.")


# ---- main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phase", choices=["capture", "arm"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345,
                    help="XMD GDB stub via VBox natpf (host side); QEMU is 1234")
    ap.add_argument("--allow-write", action="store_true",
                    help="required for `arm`; enables register/memory writes")
    ap.add_argument("--open-addr", type=lambda s: int(s, 0), default=None,
                    help="address of open()/iosOpen() resolved in capture phase")
    ap.add_argument("--trap", type=lambda s: int(s, 0), default=DEFAULT_TRAP,
                    help="return-catcher address (HW bp; never executed)")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--dry-run", action="store_true",
                    help="arm: print the shellGenericInit arg vector but don't call")
    ap.add_argument("--force", action="store_true",
                    help="proceed despite a canary mismatch")
    args = ap.parse_args()

    if args.phase == "arm" and not args.allow_write:
        sys.exit("`arm` writes the target — pass --allow-write to confirm intent")

    with RSP(args.host, args.port, allow_write=args.allow_write,
             timeout=args.timeout, label=f"xmd:{args.port}") as t:
        if args.phase == "capture":
            phase_capture(t, args)
        else:
            phase_arm(t, args)


if __name__ == "__main__":
    main()
