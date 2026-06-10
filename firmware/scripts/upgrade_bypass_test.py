#!/usr/bin/env python3
"""
upgrade_bypass_test.py — operator-in-the-loop driver for the right-to-repair
"can we get the stock firmware to accept a modified upgrade?" test.

Plan: plans/can-we-use-xmd-peaceful-crown.md
Background: firmware/reverse/build_32/upgrade_install_analysis.md (verifier
addresses, flow), firmware/reverse/build_32/host_xmd_bridge.md (the JTAG bridge).

WHAT THIS DOES
  Stage B is the real test. A USB stick carries a *modified* upgrade package
  (one version byte bumped, e.g. 32.0.3 -> 32.0.4) whose RSA signature
  (redone.2) therefore no longer matches. The stock firmware's signature
  verifier would reject it; we catch the verifier at a hardware breakpoint over
  JTAG (XMD GDB stub) and force it to report success for this one install, then
  confirm the camera flashes our image and reboots showing the bumped version.

  The bypass is done WITHOUT patching flash: either (default) a register
  override at the breakpoint (set r3=0 = the wrapper's success value, and
  PC=LR to return immediately — no I-cache concern), or (--method patch) an
  in-RAM `li r3,0; blr` byte-patch of the verifier (subject to PPC405 I-cache
  coherency — see warning).

  Stage A is a dry run: package the *unmodified* image, prove the USB media +
  boot-time auto-detect + UI-confirm path works end to end, no JTAG involved.

SAFETY
  * Target the WORKING camera while idle (not recording). The upgrade verify is
    a setup-phase operation, so the brief halt is safe.
  * This erases+writes NOR. Keep the original redone.su and a JTAG/NOR-programmer
    recovery path ready. Run Stage A before Stage B.
  * Stage B refuses to start unless the VM is running and the XMD GDB stub
    answers with a live register set.

USAGE
  # dry run (packaging + trigger only; no JTAG)
  upgrade_bypass_test.py --stage a --expect-version 32.0.3

  # the real test (register-override bypass)
  upgrade_bypass_test.py --stage b --wrapper-addr 0xAF634 --reloc 0x10180 \
                         --expect-version 32.0.4

  # negative control: arm the bp but do NOT override -> firmware must reject it
  upgrade_bypass_test.py --stage b --negative-control --expect-version 32.0.3
"""

import argparse
import socket
import subprocess
import sys

from rsp import RSP, RSPError

# li r3,0 ; blr  — the verifier-wrapper success patch (big-endian PPC).
PATCH_BYTES = bytes.fromhex("38600000" "4e800020")

# DRAM-ready canary (re_reference.md §9) — a cheap "is this the live camera and
# is DRAM up?" sanity read during preflight.
CANARY_ADDR = 0x00E269A4
CANARY_VAL = 0x12348765


# ----------------------------------------------------------------------------
# operator interaction
# ----------------------------------------------------------------------------
def banner(msg):
    print("\n" + "=" * 72 + f"\n{msg}\n" + "=" * 72)


def confirm(prompt):
    """Block until the operator confirms a manual step. 'q' aborts the test."""
    print("\n>>> " + prompt)
    ans = input("    [Enter] when done, or 'q' to abort: ").strip().lower()
    if ans == "q":
        print("[abort] operator aborted.")
        sys.exit(2)


def confirm_and_verify(prompt, verify_fn, *, retries=2):
    """Operator does a step, confirms, then we VERIFY before proceeding. On a
    failed verification, re-prompt (up to `retries`) rather than press on."""
    for attempt in range(retries + 1):
        confirm(prompt)
        try:
            if verify_fn():
                return True
            print("[verify] check did not pass.")
        except Exception as e:
            print(f"[verify] error: {e}")
        if attempt < retries:
            print("[verify] let's retry that step.")
    print("[abort] step could not be verified.")
    sys.exit(3)


def ask_version(label):
    return input(f"    Enter the {label} exactly as shown on the splash: ").strip()


# ----------------------------------------------------------------------------
# preflight
# ----------------------------------------------------------------------------
def check_vm_running(vm_name):
    try:
        out = subprocess.run(["VBoxManage", "list", "runningvms"],
                             capture_output=True, text=True, timeout=15)
    except FileNotFoundError:
        print("  [warn] VBoxManage not on PATH — cannot confirm the VM. "
              "Re-run with --no-vm-check if it is running.")
        return False
    except subprocess.TimeoutExpired:
        print("  [warn] VBoxManage timed out.")
        return False
    return f'"{vm_name}"' in out.stdout


def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except OSError:
        return False


def preflight_bridge(args):
    """Gate Stage B on a live JTAG bridge. Returns a connected, write-enabled
    RSP client, or exits with guidance."""
    banner("PREFLIGHT — JTAG bridge must be live")

    if args.no_vm_check:
        print("  [skip] VM check disabled (--no-vm-check)")
    elif check_vm_running(args.vm_name):
        print(f"  [ok]   VM '{args.vm_name}' is running")
    else:
        sys.exit(f"  [FAIL] VM '{args.vm_name}' is not running.\n"
                 f"         Start it in VirtualBox, then `xmd; connect ppc hw`.")

    if check_port(args.host, args.port):
        print(f"  [ok]   {args.host}:{args.port} is reachable")
    else:
        sys.exit(f"  [FAIL] cannot reach {args.host}:{args.port}.\n"
                 f"         Forward the stub to the host (host_xmd_bridge.md):\n"
                 f"         VBoxManage controlvm {args.vm_name} natpf1 "
                 f'"xmdgdb,tcp,127.0.0.1,{args.port},,1234"\n'
                 f"         and ensure `connect ppc hw` is running in the VM.")

    t = RSP(args.host, args.port, allow_write=True, timeout=15.0,
            label="xmd-hw").connect()
    try:
        # Prove we have real control: halt briefly, read a live register set,
        # then resume. A plausible PC back == the XMD stub is serving the core.
        t.interrupt(10.0)
        regs = t.regs()
        pc = regs.get("pc")
        if pc is None:
            sys.exit("  [FAIL] XMD stub returned no PC — not connected to the core.")
        print(f"  [ok]   XMD stub live — halted PC=0x{pc:08x} "
              f"LR=0x{regs.get('lr',0):08x}")
        try:
            cv = t.read_word(CANARY_ADDR)
            tag = "ok" if cv == CANARY_VAL else "warn"
            print(f"  [{tag}] DRAM canary @0x{CANARY_ADDR:08x} = 0x{cv:08x} "
                  f"(expect 0x{CANARY_VAL:08x})")
        except RSPError as e:
            print(f"  [warn] canary read failed: {e}")
        t.send("c")  # resume; we re-arm at the breakpoint below
    except Exception:
        t.close()
        raise
    return t


# ----------------------------------------------------------------------------
# stages
# ----------------------------------------------------------------------------
def run_stage_a(args):
    banner("STAGE A — packaging + trigger dry run (no JTAG, signature stays valid)")
    print(
        "Goal: prove the USB media, the boot-time auto-detect, and the UI-confirm\n"
        "path all work, using the UNMODIFIED package (verify passes on its own).\n"
        "  1. Extract redone.1-4 from the stock redone.su and re-tar UNCHANGED.\n"
        "  2. FAT32 USB stick, file at  upgrade/redone.su  (root-level folder).\n"
        "  3. Insert into the camera USB type-A port and POWER-CYCLE.\n"
        "  4. Confirm the upgrade at the splash prompt; let it flash and reboot.")

    def verify():
        v = ask_version("version after reboot")
        if v == args.expect_version:
            print(f"  [PASS] rebooted to {v} — media + trigger path verified.")
            return True
        print(f"  [no]   saw {v!r}, expected {args.expect_version!r}.")
        return False

    confirm_and_verify(
        "Insert the unmodified-package USB, power-cycle, confirm the upgrade, "
        "and wait for the camera to reboot to the splash.",
        verify)
    print("\nStage A complete. Proceed to Stage B with the MODIFIED package.")


def run_stage_b(args):
    addr = (args.wrapper_addr + args.reloc) & 0xFFFFFFFF
    banner("STAGE B — modified package + JTAG signature bypass")
    print(f"  verifier wrapper : 0x{args.wrapper_addr:08x}")
    print(f"  + .text reloc    : 0x{args.reloc:08x}")
    print(f"  breakpoint @     : 0x{addr:08x}")
    print(f"  method           : {args.method}"
          f"{'  (NEGATIVE CONTROL — no override)' if args.negative_control else ''}")

    t = preflight_bridge(args)
    try:
        # 1) Get the operator to the on-screen upgrade prompt, THEN arm the bp
        #    (so the armed window is small and we can't miss the verify).
        def arm():
            t.interrupt(10.0)
            regs = t.regs()
            print(f"  [halt] PC=0x{regs.get('pc',0):08x} — camera reachable.")
            if not t.set_bp(addr, hw=True):
                print(f"  [verify] could not set hw breakpoint @0x{addr:08x}")
                t.send("c")
                return False
            print(f"  [arm]  hardware breakpoint set @0x{addr:08x}")
            t.send("c")  # free-run until the verifier is reached
            return True

        confirm_and_verify(
            "Insert the MODIFIED-package USB, power-cycle, and wait until the\n"
            "    on-screen UPGRADE prompt appears. Do NOT confirm it yet.",
            arm)

        # 2) Operator confirms in the UI; we wait for the verifier to trap.
        confirm("Now CONFIRM the upgrade in the camera UI to start verification.")
        print(f"  [wait] watching for the verifier breakpoint @0x{addr:08x} ...")
        stop = t.recv(args.bp_timeout)
        if not (stop.startswith("T") or stop.startswith("S")):
            sys.exit(f"  [FAIL] unexpected stop reply: {stop!r}")
        regs = t.regs()
        pc = regs.get("pc", 0) & 0xFFFFFFFF
        if pc != addr:
            print(f"  [warn] halted at 0x{pc:08x}, expected 0x{addr:08x} "
                  f"(reloc wrong? other bp?).")
        print(f"  [HIT]  verifier reached: PC=0x{pc:08x} "
              f"r3=0x{regs.get('r3',0):08x} LR=0x{regs.get('lr',0):08x}")

        # 3) Apply (or deliberately withhold) the bypass.
        if args.negative_control:
            print("  [ctrl] NEGATIVE CONTROL: leaving the verifier untouched — "
                  "the firmware should REJECT this package.")
        elif args.method == "regs":
            t.write_reg("r3", 0)                    # wrapper success value
            t.write_reg("pc", regs.get("lr", 0))    # return to caller now
            print("  [ovr]  r3<-0, PC<-LR : verifier forced to return success.")
        else:  # patch
            t.write_mem(addr, PATCH_BYTES)
            print(f"  [ovr]  patched 0x{addr:08x} <- li r3,0; blr "
                  f"({PATCH_BYTES.hex()})")
            print("  [warn] PPC405 does not snoop I-cache on JTAG writes; if the "
                  "verifier was already cached this patch may not take effect. "
                  "Prefer --method regs.")

        t.clear_bp(addr, hw=True)
        t.send("c")  # let the flasher run
        print("  [run]  resumed — the upgrader should now erase+write flash.")
    finally:
        try:
            t.detach()
        except Exception:
            pass
        t.close()

    # 4) Confirm the outcome from the splash.
    banner("STAGE B — result")
    v = ask_version("version after the upgrade reboot")
    if args.negative_control:
        if v != args.expect_version:
            print(f"  [PASS] version unchanged ({v}) — package was REJECTED, as "
                  "expected without the override. The bypass (not luck) is what "
                  "makes Stage B pass.")
        else:
            print(f"  [FAIL] version changed to {v} without an override — "
                  "the package was accepted unexpectedly; investigate.")
    else:
        if v == args.expect_version:
            print(f"  [PASS] rebooted to {v} — the MODIFIED package installed. "
                  "Signature bypass validated end to end.")
        else:
            print(f"  [FAIL] saw {v!r}, expected {args.expect_version!r}. The "
                  "override or the flash did not take.")


# ----------------------------------------------------------------------------
def auto_int(s):
    return int(s, 0)


def main():
    ap = argparse.ArgumentParser(
        description="Operator-driven upgrade signature-bypass test (JTAG).")
    ap.add_argument("--stage", choices=["a", "b"], default="b",
                    help="a = packaging/trigger dry run; b = JTAG bypass test")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345,
                    help="XMD GDB stub, host side (host_xmd_bridge.md)")
    ap.add_argument("--vm-name", default="r1mx_32")
    ap.add_argument("--no-vm-check", action="store_true",
                    help="skip the VBoxManage running-VM check")
    ap.add_argument("--wrapper-addr", type=auto_int, default=0xAF634,
                    help="verifier wrapper file offset (FUN_000af634)")
    ap.add_argument("--reloc", type=auto_int, default=0x0,
                    help="per-unit .text relocation added to --wrapper-addr "
                         "(see working-camera-reloc)")
    ap.add_argument("--method", choices=["regs", "patch"], default="regs",
                    help="regs = override r3/PC at the bp (recommended); "
                         "patch = in-RAM li r3,0;blr (I-cache caveat)")
    ap.add_argument("--negative-control", action="store_true",
                    help="arm the bp but do NOT override — prove rejection")
    ap.add_argument("--expect-version", default="32.0.4",
                    help="version expected on the splash after the test")
    ap.add_argument("--bp-timeout", type=float, default=600.0,
                    help="seconds to wait for the verifier breakpoint to hit")
    args = ap.parse_args()

    if args.stage == "a":
        run_stage_a(args)
    else:
        run_stage_b(args)


if __name__ == "__main__":
    sys.exit(main())
