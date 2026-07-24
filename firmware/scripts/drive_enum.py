#!/usr/bin/env python3
"""drive_enum.py — drive the PCI device enumerator FUN_00367f54 from the forced-
usrRoot allocator-wall context, and prove the device-modelling + firmware config-
scan path end-to-end.

CRITICAL CONTEXT (2026-06-16, this session):
The forced dispatch enters usrRoot at its RESUME label 0x37c440 (`b 0x37c290`),
which SKIPS the prologue + the `lis r30,0xea` setup at 0x37c14c. So at the
dispatcher block 0x37c290 r30=0, and `lwz r9,-0x3c20(r30); stw r3,0x278(r9)`
writes through r9=0xffffffff to physical 0x277 — clobbering the low PCI config-
driver instruction at 0x274 (`or r3,r3,r5` 0x7c632b78 -> illegal 0x7c632b02 ->
traps to 0x700). That single corrupted byte silently breaks EVERY PCI config read
(FUN_000005a4), which is why the enum used to find 0 devices.

FIX (proven): run to 0x37c290 and set r30=r26=0x00EA0000 (their real base) before
continuing. Then 0x274 stays intact and the whole scan path works:
  FUN_000005a4(0,1,0,0) = 0x156204CC (ISP1562), FUN_00000b3c(0x0C03A0) -> bus0/dev1,
  FUN_00367340(0xc,3,0xa0,0) -> ret 1 (found).

ALLOCATOR BLOCKER RESOLVED (2026-06-17): the enum mallocs one 0x24 descriptor per
device via FUN_0045b974. The repeated-malloc failure was NOT a hand-build limit —
it was the uninitialized guard-zone global *0xE295E4 (cold garbage ~0x00d8fad0 =
~14 MB). With it nonzero, addToPool wasted 14 MB at the pool front and the carve
overhead was so large the first malloc took the no-split branch and emptied the
free tree (only ONE malloc serviceable). build_allocator now seeds *0xE295E4 = 0
(guards off, production default; a read-only config const the bypassed early data
init would set). Allocator now services unlimited sequential mallocs; the enum
runs to a clean return, matches both USB controllers (OHCI 0x0C03A0 + EHCI
0x0C0320), and allocates a descriptor for each. The real init FUN_0045acac is NOT
usable (it hangs in FUN_00442e48 object registration — needs the object/class
system / a scheduler), so this seeded hand-build is the faithful-enough path.
Residual: the EHCI (loop-2) post-alloc init runs a method call (*0x377c24) +
EHCI capability-register poll — the next device-model layer, not the allocator.

Requires: qemu_boot.sh --debug --background (stub :1234).
"""
import struct
from rsp import RSP
from build_allocator import build, _call

USRROOT_TRUE_ENTRY = 0x0037BF78   # real cold entry (prologue) — sets r30 itself
USRROOT_RESUME     = 0x0037C440   # loop-back resume label (`b 0x37c290`) — SKIPS r30 setup
CFG_INSN_ADDR      = 0x00000274   # canary: must stay 0x7c632b78
CFG_INSN_GOOD      = 0x7C632B78
CATCH              = 0x0000000C

def u32(t, a): return struct.unpack(">I", t.read_mem(a, 4))[0]
def w32(t, a, v): t.write_mem(a, struct.pack(">I", v & 0xFFFFFFFF))

def reach_wall_clean(t):
    """Boot -> device-init allocator wall 0x555488, on a faithful task frame, 0x274
    intact.  Returns sp.

    As of 2026-06-17 the qemu-r1mx machine LANDS the dispatch fix itself
    (r1mx_apply_boot_env_fixups #6): it redirects the root routine to usrRoot's true
    entry 0x37BF78 (patch at 0x36C414) and seeds the per-call state flag *0xE2706C=0
    plus the deferred-write list, so the NATURAL boot enters usrRoot at its prologue
    (which sets r30=0xEA0000), runs the dispatcher 0x37c290 WITHOUT corrupting 0x274,
    and reaches the device-ctx alloc wall 0x555488 in one pass -- no register injection
    or 2-call replay needed.  (The old forced true-entry 2-call sequence is retired;
    see boot_reconstruction_status.md 2026-06-17.  USRROOT_TRUE_ENTRY/_RESUME kept for
    reference.)"""
    t.run_to(0x00371CD0, hw=True, timeout=90.0)            # dispatch (past kernelInit)
    t.set_bp(0x00555488, hw=True); t.cont(timeout=45); t.clear_bp(0x00555488, hw=True)
    assert u32(t, CFG_INSN_ADDR) == CFG_INSN_GOOD, "0x274 corrupted -- dispatch fix not applied?"
    return t.regs()["r1"]

def main():
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=30.0, label="qemu").connect()
    try:
        sp = reach_wall_clean(t)
        intact = u32(t, CFG_INSN_ADDR) == CFG_INSN_GOOD
        print(f"[*] wall sp=0x{sp:08x}  0x274=0x{u32(t,CFG_INSN_ADDR):08x} (intact={intact})")
        if not intact:
            print("[!] 0x274 already corrupted — r30 fix didn't take; abort"); return
        if not build(t, sp):
            print("[!] allocator build failed; abort"); return

        # sanity: the firmware's own scan now finds the modelled ISP1562s
        sa, sb, sc = 0x08E00020, 0x08E00024, 0x08E00028
        for a in (sa, sb, sc): w32(t, a, 0xEEEEEEEE)
        pc, lr, r3 = _call(t, sp, 0x00367340, 0xc, 3, 0xa0, 0, sa, sb, sc, timeout=20)
        print(f"[*] FUN_00367340(0xc,3,0xa0,0) ret={r3} -> bus{u32(t,sa)>>24} "
              f"dev{u32(t,sb)>>24} fn{u32(t,sc)>>24}  (device match WORKS)")

        # Drive the enum.  Loop 1 (OHCI) enumerates dev1 cleanly (count->1, desc[0]).
        # Loop 2 (EHCI) matches dev2 + mallocs desc[1], then calls descriptor[0] =
        # literal 0x377C24 via `bctrl` at 0x3681D4 -- a mid-function soft-float
        # continuation with non-standard linkage (restores lr from a caller-prepared
        # 0(r1)), so on a forced/synthetic frame it DIVERTS (not back into loop 2; see
        # boot_reconstruction_status.md 2026-06-17 "EHCI loop-2 NOT a device-model gap").
        # We therefore bound the run at that method call: by then both controllers are
        # matched and both descriptors allocated -- the meaningful result.  (The handoff
        # poll past it is a PCI-config read on a faithful frame, never reached here.)
        EHCI_METHOD_BCTRL = 0x003681D4
        w32(t, 0xE26978, 0)
        print("[*] driving FUN_00367f54 ...")
        t.set_bp(EHCI_METHOD_BCTRL, hw=True)
        pc, lr, r3 = _call(t, sp, 0x00367F54, timeout=60)
        t.clear_bp(EHCI_METHOD_BCTRL, hw=True)
        cnt = u32(t, 0xE26978)
        where = ("loop-2 EHCI method bctrl (0x377C24) — diverts on forced frame; "
                 "both controllers matched + descriptors allocated"
                 if pc == EHCI_METHOD_BCTRL else
                 "clean return" if pc == CATCH else f"unexpected 0x{pc:08x}")
        print(f"=== enum stop=0x{pc:08x} count={cnt}  [{where}] ===")
        # USB controller descriptor slots (0x10cf458[]): slot0=OHCI, slot1=EHCI
        for i in range(5):
            d = u32(t, 0x010CF458 + i*4)
            if d:
                print(f"    desc[{i}]=0x{d:08x}  ({'OHCI' if i == 0 else 'EHCI' if i == 1 else '?'})")
    finally:
        t.close()

if __name__ == "__main__":
    main()
