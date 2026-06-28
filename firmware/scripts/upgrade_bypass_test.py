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

# Upgrade-verify error flag (upgrade_install_analysis.md §"How verification works"):
# the per-file verify sets *(0x00E9E85C)=1 on a failed EVP_VerifyFinal. It lives in
# BSS (absolute live address, > image size) so it's only readable on the live core.
ERROR_FLAG_ADDR = 0x00E9E85C

# Upgrade pipeline waypoints — IMAGE offsets (flat image; live = img + --reloc).
# Ordered early -> late; all four have low caller counts so each is a clean trap,
# and there are exactly four, matching the PPC405's four IAC (PC) breakpoints that
# XMD exposes. Tracing which fire (and in what order) shows how far an upgrade got.
#   extract  FUN_000a8bdc  lib/libflashutils/extract.c — extract/decrypt/verify entry
#   verify   FUN_00210800  per-file signature verify (calls the wrapper at its entry)
#   wrapper  FUN_000af634  verify wrapper — the result gate / OVERRIDE POINT
#   flash    FUN_000adc28  flash erase/program (only reached if verification passes)
WAYPOINT_DEFAULTS = {
    "extract": 0x000A8BDC,
    "verify":  0x00210800,
    "wrapper": 0x000AF634,
    "flash":   0x000ADC28,
}
WAYPOINT_DESC = {
    "extract": "extract/decrypt/verify entry (extract.c FUN_000a8bdc)",
    "verify":  "per-file signature verify (FUN_00210800)",
    "wrapper": "verify wrapper — OVERRIDE POINT (FUN_000af634)",
    "flash":   "flash erase/program (FUN_000adc28)",
}
# Early -> late ordering used for the trace summary / interpretation.
WAYPOINT_ORDER = ["extract", "verify", "wrapper", "flash"]


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


def selftest_breakpoint(t, pc, timeout=5.0):
    """Confirm a hardware (Z1/IAC) breakpoint actually arms and fires on this
    stub. The core is halted (usually in the idle loop) when we're called: set a
    bp at the current PC, continue, and check it re-traps. Non-fatal — it only
    annotates whether later 'no waypoint hit' results can be trusted."""
    if not t.set_bp(pc, hw=True):
        print(f"  [warn] hw breakpoint NOT accepted @0x{pc:08x} — XMD may not "
              f"honor Z1; the waypoint trace will be unreliable.")
        return False
    t.send("c")
    try:
        stop = t.recv(timeout)
    except (TimeoutError, socket.timeout):
        # It never came back — re-halt and clean up so preflight can continue.
        t.interrupt(10.0)
        t.clear_bp(pc, hw=True)
        print(f"  [warn] hw breakpoint did NOT fire @0x{pc:08x} within {timeout}s "
              f"(target may not have re-reached it, or Z1 is a no-op on this "
              f"stub). A later 'no waypoint hit' would be inconclusive.")
        return False
    rp = t.regs().get("pc", 0) & 0xFFFFFFFF
    t.clear_bp(pc, hw=True)
    ok = stop.startswith(("T", "S")) and rp == pc
    print(f"  [{'ok' if ok else 'warn'}] hw breakpoint "
          f"{'fired' if ok else 'returned'} @0x{rp:08x} "
          f"{'— Z1 works on this stub.' if ok else f'(expected 0x{pc:08x}).'}")
    return ok


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
        # Prove the instrument before we rely on it: a hardware breakpoint must
        # actually arm AND fire on this XMD stub, else a "no waypoint hit" later
        # is meaningless (we couldn't tell "path not taken" from "bp never armed").
        if pc is not None and not args.no_bp_selftest:
            selftest_breakpoint(t, pc)
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
    # Resolve the pipeline waypoints to live addresses (img offset + reloc) and
    # build the reverse map so we can name a breakpoint by the PC it traps at.
    wp_img = dict(WAYPOINT_DEFAULTS)
    wp_img["extract"] = args.extract_addr
    wp_img["verify"] = args.verify_addr
    wp_img["wrapper"] = args.wrapper_addr   # the override point
    wp_img["flash"] = args.flash_addr
    live = {n: (a + args.reloc) & 0xFFFFFFFF for n, a in wp_img.items()}
    by_pc = {a: n for n, a in live.items()}

    banner("STAGE B — modified package + JTAG signature-bypass trace")
    print(f"  .text reloc      : 0x{args.reloc:08x}")
    print(f"  method           : {args.method}"
          f"{'  (NEGATIVE CONTROL — no override)' if args.negative_control else ''}")
    print("  pipeline breakpoints (img + reloc = live):")
    for n in WAYPOINT_ORDER:
        mark = "  <- override" if n == "wrapper" else ""
        print(f"    {n:8} 0x{wp_img[n]:08x} -> 0x{live[n]:08x}  "
              f"{WAYPOINT_DESC[n]}{mark}")

    t = preflight_bridge(args)
    reached = []          # ordered list of waypoint names that trapped
    flashed = False
    try:
        # 1) Operator navigates to (but does not select) UPDATE SW; THEN we arm
        #    all four pipeline breakpoints so we can trace how far the upgrade
        #    gets. XMD exposes four IAC slots — exactly enough for the set.
        def arm():
            t.interrupt(10.0)
            regs = t.regs()
            print(f"  [halt] PC=0x{regs.get('pc',0):08x} — camera reachable.")
            armed = []
            for n in WAYPOINT_ORDER:
                if t.set_bp(live[n], hw=True):
                    armed.append(n)
                    print(f"  [arm]  {n:8} @0x{live[n]:08x}")
                else:
                    print(f"  [warn] could not set bp for {n} @0x{live[n]:08x} "
                          f"(out of IAC slots, or Z1 refused).")
            if not armed:
                print("  [verify] no breakpoints armed — cannot trace.")
                t.send("c")
                return False
            t.send("c")  # free-run; the upgrade pipeline will trap as it runs
            return True

        confirm_and_verify(
            "Insert the MODIFIED-package USB, then on the camera press SYSTEM ->\n"
            "    SETUP -> MAINTENANCE and HIGHLIGHT 'UPDATE SW' (do NOT select it\n"
            "    yet).",
            arm)

        # 2) Operator triggers the upgrade; we trace every waypoint it hits.
        confirm("Now select 'UPDATE SW' in the camera UI to start the upgrade.")
        print(f"  [wait] tracing the upgrade pipeline "
              f"(up to {args.bp_timeout:.0f}s per step) ...")
        try:
            while True:
                stop = t.recv(args.bp_timeout)
                if not (stop.startswith("T") or stop.startswith("S")):
                    print(f"  [warn] unexpected stop reply: {stop!r}")
                    break
                regs = t.regs()
                pc = regs.get("pc", 0) & 0xFFFFFFFF
                name = by_pc.get(pc, f"?@0x{pc:08x}")
                reached.append(name)
                try:
                    flag = f"errflag=0x{t.read_word(ERROR_FLAG_ADDR):08x}"
                except Exception:
                    flag = "errflag=?"
                print(f"  [HIT]  {name:8} PC=0x{pc:08x} r3=0x{regs.get('r3',0):08x} "
                      f"LR=0x{regs.get('lr',0):08x} {flag}")

                if name == "flash":
                    print("  [done] reached flash erase/program — verification "
                          "passed or was overridden. Resuming to let it flash.")
                    flashed = True
                    for a in live.values():
                        t.clear_bp(a, hw=True)
                    t.send("c")
                    break

                if name == "wrapper" and not args.negative_control:
                    if args.method == "regs":
                        t.write_reg("r3", 0)                 # wrapper success value
                        t.write_reg("pc", regs.get("lr", 0))  # return to caller now
                        print("  [ovr]  r3<-0, PC<-LR : verifier forced to return "
                              "success (wrapper runs once per signed file).")
                    else:  # patch
                        t.write_mem(pc, PATCH_BYTES)
                        print(f"  [ovr]  patched 0x{pc:08x} <- li r3,0; blr "
                              f"({PATCH_BYTES.hex()})")
                        print("  [warn] PPC405 ignores I-cache on JTAG writes; "
                              "prefer --method regs if this has no effect.")
                elif name == "wrapper":
                    print("  [ctrl] NEGATIVE CONTROL: wrapper left untouched — "
                          "the firmware should REJECT this package.")

                t.send("c")  # continue tracing the next waypoint
        except (TimeoutError, socket.timeout):
            print(f"  [wait] no further breakpoint within {args.bp_timeout:.0f}s "
                  "— pipeline appears to have stopped advancing.")
    finally:
        try:
            t.detach()
        except Exception:
            pass
        t.close()

    # 3) Trace summary + interpretation — this is what tells you what the camera
    #    actually did, independent of the splash version.
    banner("STAGE B — pipeline trace")
    seen = set(reached)
    for n in WAYPOINT_ORDER:
        mark = "HIT " if n in seen else " -- "
        print(f"  [{mark}] {n:8} 0x{live[n]:08x}  {WAYPOINT_DESC[n]}")
    if reached:
        print("  order: " + " -> ".join(reached))
    if flashed:
        print("\n  => upgrade reached flashing.")
    elif "wrapper" in seen or "verify" in seen:
        print("\n  => reached signature verification but did NOT flash — the "
              "override is missing/ineffective, or a stage after verify rejected "
              "it. Check the errflag values and try --method patch vs regs.")
    elif "extract" in seen:
        print("\n  => extraction started but never reached signature verify — the "
              "modified package fails during decrypt/gunzip/parse (a packaging "
              "problem, NOT the signature). Re-check the Stage-B repackage.")
    else:
        print("\n  => NONE of the upgrade waypoints fired. If the preflight bp "
              "self-test PASSED, the menu 'UPDATE SW' path does not run this "
              "SmartUpgrade/extract.c pipeline (wrong trigger or wrong --reloc); "
              "if the self-test FAILED, the JTAG breakpoint never armed.")

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
    ap.add_argument("--wrapper-addr", type=auto_int,
                    default=WAYPOINT_DEFAULTS["wrapper"],
                    help="verifier wrapper file offset (FUN_000af634) — the "
                         "override point")
    ap.add_argument("--extract-addr", type=auto_int,
                    default=WAYPOINT_DEFAULTS["extract"],
                    help="extract/decrypt/verify entry file offset (FUN_000a8bdc)")
    ap.add_argument("--verify-addr", type=auto_int,
                    default=WAYPOINT_DEFAULTS["verify"],
                    help="per-file signature verify file offset (FUN_00210800)")
    ap.add_argument("--flash-addr", type=auto_int,
                    default=WAYPOINT_DEFAULTS["flash"],
                    help="flash erase/program file offset (FUN_000adc28)")
    ap.add_argument("--reloc", type=auto_int, default=0x0,
                    help="per-unit .text relocation added to every waypoint "
                         "offset (see working-camera-reloc; cam-working-01=0x10180)")
    ap.add_argument("--method", choices=["regs", "patch"], default="regs",
                    help="regs = override r3/PC at the bp (recommended); "
                         "patch = in-RAM li r3,0;blr (I-cache caveat)")
    ap.add_argument("--negative-control", action="store_true",
                    help="arm the bps but do NOT override — prove rejection")
    ap.add_argument("--no-bp-selftest", action="store_true",
                    help="skip the preflight hardware-breakpoint self-test")
    ap.add_argument("--expect-version", default="32.0.4",
                    help="version expected on the splash after the test")
    ap.add_argument("--bp-timeout", type=float, default=600.0,
                    help="seconds to wait at each step for the next waypoint")
    args = ap.parse_args()

    if args.stage == "a":
        run_stage_a(args)
    else:
        run_stage_b(args)


if __name__ == "__main__":
    sys.exit(main())
