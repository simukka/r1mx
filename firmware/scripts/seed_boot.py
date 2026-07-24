#!/usr/bin/env python3
"""
seed_boot.py — advance the REAL boot path (forced usrRoot) by SEEDING the
heap/BSS-resident kernel data structures that a completed cold boot would build.

Background (re_reference.md §0.3): software.bin is the firmware program image RED
ships (decrypted from the official redone.su Build 32 installer), NOT a memory dump
of a booted camera. BSS (0xE9BF20..0x1153480) is *above* the 0xE8BF20 file end, so it
reads zero in QEMU, and the heap is unallocated — both normal for a program image,
runtime-populated by a cold boot. Forcing PC = usrRoot (0x37C440) runs the genuine
boot code but skips the C++ ctor / module-init phase that would build those kernel
lists, so it walks list heads (in BSS) still in their uninitialized state — and the
walks spin or fault.

This harness boots normally to the artifact dispatch point, applies a growing table
of SEEDS (cold-boot-correct values for those structures — typically self-referential
empty circular lists), then forces usrRoot and traces to the NEXT divergence so we
can identify and seed the next structure. Each confirmed seed is a candidate for
r1mx_apply_boot_env_fixups in the QEMU machine.

Requires: qemu_boot.sh --debug --background  (stub on :1234).
"""
import sys, time
from pathlib import Path
from rsp import RSP, RSPError

ROOT_ARTIFACT = 0x00381A8C
USRROOT       = 0x0037C440
DISPATCH_FN   = 0x00371CD0   # FUN_00371cd0 — task-context setup / dispatch branch

# ---- DISPATCH CRACK (harvested from cam-working-01, 2026-06-14) --------------
# FUN_00371cd0: `if (*0xE3A790 == TCB+0x94)` -> if-path = OpenSSL artifact (what
# patches #53/55 chase); else-path -> saved PC = TCB+0xC0 = usrRoot (0x37C440).
# TIMING MATTERS: TCB+0x94 is COPIED from *0xE3A790 at task setup. So these seeds
# only force the else-path when applied AT THE DISPATCH (run_to DISPATCH_FN, then
# write — after taskInit captured TCB+0x94=0, before the branch reads *0xE3A790).
# At boot they'd propagate into TCB+0x94 and re-match -> if-path. The standalone
# QEMU fix instead FORCES the else-path by patching the branch at 0x371D5C
# (bne -> b) in r1mx_apply_boot_env_fixups; see boot_reconstruction_status.md.
DISPATCH_SEEDS = [
    (0x00E3A790, 0x00FC9580, "selector: non-zero so root TCB+0x94(=0) != sel -> else-path (apply AT dispatch)"),
    (0x00E293F4, 0x00000000, "else-path fn-ptr: NULL so FUN_00371c74 skips it (cold 0x542974 is stale)"),
]

# ---- the growing seed table -------------------------------------------------
# Each entry: (addr, value, note). 32-bit big-endian writes applied before usrRoot.
# An empty VxWorks circular list anchored at H means H->next == H (and tail == H).
SEEDS = [
    # #1 deferred-write list walked by FUN_0037d87c (eventpoint/bp-restore style):
    #    head @ 0xE9C5C0; cold-boot empty == self-referential. Un-built here, the
    #    head points into not-yet-allocated heap (0x0DCF5120) -> infinite walk.
    (0x00E9C5C0, 0x00E9C5C0, "FUN_0037d87c list head->next = self (empty)"),
    (0x00E9C5C4, 0x00E9C5C0, "FUN_0037d87c list tail/prev = self (empty)"),
    # #2 allocator/free fn-ptrs normally set by module-init FUN_005555ec (a C++
    #    ctor we skip). zalloc (FUN_00555488) calls *0xE9C34C; NULL -> bctrl 0 -> 0x700.
    (0x00E9C34C, 0x005652D0, "allocator fn-ptr (FUN_005555ec: *0xE9C34C=0x5652D0)"),
    (0x00E9C648, 0x00565518, "free/companion fn-ptr (FUN_005555ec: *0xE9C648=0x565518)"),
]

# ---- PCI config mechanism (device-layer prerequisite) -----------------------
# What the firmware's PCI subsystem init WOULD set so config cycles work against
# the QEMU XPci_v3 bridge (which now hosts the ISP1562 USB stubs — see
# hw/pci-host/xilinx_opb_pci.c).  Verified (2026-06-13): with these set, the
# firmware's own scanner FUN_00000b3c(0x0c03a0/0x0c0320) FINDS the modelled
# devices (bus0/dev1 + bus0/dev2).  CAR/CDR are the bridge cfg-cycle ports.
#
# NB: these are NOT YET load-bearing in this harness.  The cold-boot device
# enumeration (FUN_00367f54) that consumes them needs a working heap allocator
# (FUN_0045b974 -> object *0xE295C4), and that allocator OBJECT is still
# uninitialised in the forced-usrRoot context (its method slot reads rodata
# garbage -> 0x700).  So enumeration faults (0x600/0x700) regardless of these.
# Kept here as the ready prerequisite for once the allocator/C++-ctor phase is
# solved (the current frontier; see boot_reconstruction_status.md 2026-06-13).
PCI_SEEDS = [
    (0x00E0BDFC, 0x00000000, "PCI config gate open (FUN_000005a4 guard)"),
    (0x00E0BDF8, 0x00000001, "PCI config mechanism #1"),
    (0x00E0BDF4, 0x00000000, "PCI max bus number = 0"),
    (0x00E9C708, 0xE120010C, "PCI CONFIG_ADDRESS (XPci_v3 CAR, base+0x10C)"),
    (0x00E9C70C, 0xE1200110, "PCI CONFIG_DATA    (XPci_v3 CDR, base+0x110)"),
    (0x00E26978, 0x00000000, "device count := 0 (FUN_00367f54 increments; .data garbage)"),
    (0x00E3A624, 0x00000000, "device table base := 0 (FUN_00563b58 allocates; .data garbage)"),
    (0x00E3A630, 0x00000000, "device-context count := 0"),
]

# Toggle to also apply PCI_SEEDS (off by default — gated on allocator, see above).
APPLY_PCI_SEEDS = False

# landmark + exception-vector net (same as probe_usrroot.py)
SYSCLKENABLE = 0x0000942C
VECTORS = {
    0x00000100: "SystemReset", 0x00000200: "MachineCheck", 0x00000300: "DSI(data)",
    0x00000400: "ISI(instr)",  0x00000600: "Alignment",    0x00000700: "Program",
    0x00000800: "FPUnavail",   0x00000C00: "SystemCall",    0x00001000: "PIT",
    0x00001010: "FIT",         0x00001020: "Watchdog",      0x00000500: "ExtIntr",
}
LANDMARKS = {SYSCLKENABLE: "sysClkEnable"}
RET_CATCH = 0x00000004


def load_harvest(path):
    """Load a harvest_slots.py report and return its seedable rows as
    (addr, value, note) tuples (class in code/data/bss/null)."""
    import json
    rep = json.loads(Path(path).read_text())
    out = []
    for a, s, n in rep.get("seed_table", []):
        out.append((a, s, n))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harvest", action="append", default=[],
                    help="harvest_slots.py JSON report(s); merge its seed_table into SEEDS")
    ap.add_argument("--root-entry", default=None,
                    help="force PC here (QEMU addr) instead of usrRoot 0x37C440 — e.g. the "
                         "harvested root TCB+0xC0 value if it differs")
    ap.add_argument("--pci", action="store_true", help="also apply PCI_SEEDS")
    ap.add_argument("--port", type=int, default=1234)
    args = ap.parse_args()

    entry = int(args.root_entry, 0) if args.root_entry else USRROOT
    harvested = []
    for h in args.harvest:
        rows = load_harvest(h)
        harvested += rows
        print(f"[*] loaded {len(rows)} seed(s) from {h}")

    t = RSP("127.0.0.1", args.port, allow_write=True, timeout=20.0, label="qemu").connect()
    try:
        print("[*] boot -> artifact entry 0x%08x" % ROOT_ARTIFACT)
        regs = t.run_to(ROOT_ARTIFACT, hw=True, timeout=60.0)
        print(f"    sp=0x{regs['r1']:08x}")

        seeds = SEEDS + harvested + (PCI_SEEDS if (APPLY_PCI_SEEDS or args.pci) else [])
        print(f"[*] applying {len(seeds)} seed(s):")
        for addr, val, note in seeds:
            t.write_mem(addr, (val & 0xFFFFFFFF).to_bytes(4, "big"))
            rb = int.from_bytes(t.read_mem(addr, 4), "big")
            ok = "OK" if rb == (val & 0xFFFFFFFF) else f"MISMATCH(read 0x{rb:08x})"
            print(f"    0x{addr:08x} <- 0x{val:08x}  [{ok}]  {note}")

        label = "usrRoot" if entry == USRROOT else "root-entry"
        print(f"[*] forcing PC = {label} 0x{entry:08x}")
        t.write_reg("pc", entry)
        t.write_reg("lr", RET_CATCH)

        bps = list(VECTORS) + list(LANDMARKS) + [RET_CATCH]
        for a in bps:
            t.set_bp(a, hw=True)

        print("[*] free-running usrRoot ...")
        hit = None; spun = False
        deadline = time.time() + 30.0
        while time.time() < deadline:
            try:
                stop = t.cont(timeout=12.0)
            except TimeoutError:
                spun = True; break
            pc = t.regs().get("pc", 0)
            if pc in VECTORS: hit = ("VECTOR", pc, VECTORS[pc]); break
            if pc in LANDMARKS: hit = ("LANDMARK", pc, LANDMARKS[pc]); break
            if pc == RET_CATCH: hit = ("RETURN", pc, "usrRoot returned"); break
            print(f"    unexpected stop pc=0x{pc:08x}; continuing")

        if spun and hit is None:
            t.interrupt(timeout=5.0)
            r1 = t.regs(); pc1 = r1.get("pc", 0)
            seen = [pc1]
            for _ in range(16):
                t.step(timeout=5.0); seen.append(t.regs().get("pc", 0))
            lo = min(seen) & ~0xf
            code = t.read_mem(lo - 0x10, 0x70)
            print(f"\n  SPIN @ pc range 0x{min(seen):08x}..0x{max(seen):08x}")
            print(f"    lr=0x{r1.get('lr',0):08x} r3=0x{r1.get('r3',0):08x} "
                  f"r4=0x{r1.get('r4',0):08x} r5=0x{r1.get('r5',0):08x} r1=0x{r1.get('r1',0):08x}")
            try:
                from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN
                md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
                for ins in md.disasm(code, lo - 0x10):
                    m = " <= pc" if ins.address in set(seen) else ""
                    print(f"      0x{ins.address:08x}: {ins.mnemonic:7s} {ins.op_str}{m}")
            except Exception as e:
                print(f"    (no capstone: {e}) raw={code.hex()}")
            hit = ("SPIN", min(seen), "next structure to seed")

        for a in bps:
            try: t.clear_bp(a, hw=True)
            except Exception: pass

        print("\n=== RESULT ===")
        if hit:
            kind, pc, name = hit
            print(f"  {kind} @0x{pc:08x}  ({name})")
            if kind == "LANDMARK":
                print("  *** reached a real boot milestone on the natural path ***")
            elif kind in ("SPIN", "VECTOR"):
                print("  -> identify the function here, decompile, and add the next seed.")
        else:
            print("  no net hit / usrRoot returned cleanly.")
    finally:
        t.close()


if __name__ == "__main__":
    main()
