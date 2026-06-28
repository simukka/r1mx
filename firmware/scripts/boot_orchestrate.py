#!/usr/bin/env python3
"""boot_orchestrate.py — Option-B "machine-side orchestration" experiment.

GOAL: carry the NATURAL Build-32 boot past the device-init wall (FUN_00555488)
by driving the proven harness pieces (build the general allocator, run the PCI
enumerator) in order at the wall, then driving the firmware's OWN device-table
builder FUN_00563B58 so the device-ctx alloc finds a populated table — and then
resuming the natural boot.

RESULT (2026-06-19): the first two stages WORK end-to-end from the wall context:
  - build_allocator: general malloc returns real in-pool memory (proven).
  - FUN_00367f54 (PCI enum, bounded at the EHCI loop-2 divert 0x3681D4): matches
    both modelled USB controllers (OHCI 0x0C03A0 + EHCI 0x0C0320) and allocates a
    0x24 descriptor for each (0x10cf458[0]=0x08000150, [1]=0x08000188); count=1.

  But stage 3 — the firmware's device-table builder FUN_00563B58 (which writes the
  table base *0xE3A624 / count *0xE3A630 the keystone alloc 0x5651E8 indexes) —
  DIVERGES into the keystone fault loop (PC bounces 0x700 / 0x36fd38, the low
  EVPR-relocated PCI-config code reached by a bctrl-to-0) regardless of whether the
  alloc fn-ptr *0xE9C34C points at the mid-function handler 0x5652D0 or the true
  entry 0x5651E8.  Root cause: FUN_00563B58 calls the device-ctx alloc
  (FUN_005552A4 -> *0xE9C34C) and the per-device 84 KB context builder
  (FUN_00560544) plus device-specific init (0x5ab360 / 0x5ac50c), which need the
  running VxWorks scheduler + object/class system (same dependency that hangs the
  real allocator init FUN_0045acac in FUN_00442e48 object-registration).  The
  device-ctx alloc 0x5651E8 indexes an as-yet-empty table (count=0 -> -7 / faults)
  — the table-build and the alloc are mutually dependent and only resolvable by a
  live scheduler.  So driving the firmware's real device-init from a synthetic
  forced-call frame is BLOCKED at the device-table layer (the documented
  irreducible circular bootstrap, now pinned to FUN_00563B58).

  Remaining Option-B avenue: fully HAND-FABRICATE the device table + 84 KB
  per-device contexts in RAM (reverse-engineer every field the boot reads from
  iRam00E3A624[]/the context) and seed them as machine fixups — large, fragile,
  low-confidence.  See boot_reconstruction_status.md 2026-06-19.

Use:  ./qemu_boot.sh --patched --debug --background   (stub :1234), then run this.
"""
import struct
from rsp import RSP
import build_allocator as BA

CATCH = 0x0000000C
WALL = 0x00555488
DISPATCH = 0x00371CD0
ENUM = 0x00367F54
ENUM_BOUND = 0x003681D4          # EHCI loop-2 method divert (bound the enum here)
TABLE_BUILDER = 0x00563B58       # FUN_00563B58: builds device table E3A624/E3A630
INIT_BASE = 0x00EA0000           # r30 base the low config/init path expects

ALLOC_FNPTR = 0x00E9C34C         # device-ctx alloc fn-ptr (set by FUN_005555EC)
FREE_FNPTR = 0x00E9C648
ALLOC_REAL_ENTRY = 0x005651E8    # FUN_005651E8 true entry (builds r27/r28 from table)
ALLOC_MID_HANDLER = 0x005652D0   # harvested/live fn-ptr value (mid-function handler)
ONCE_GUARD = 0x00E3A5E4          # FUN_00552BF4/E88 shared once-counter
ENUM_COUNT = 0x00E26978
TABLE_BASE = 0x00E3A624
TABLE_COUNT = 0x00E3A630


def u32(t, a): return struct.unpack(">I", t.read_mem(a, 4))[0]
def w32(t, a, v): t.write_mem(a, struct.pack(">I", v & 0xFFFFFFFF))


def call_ctx(t, sp, pc, *args, r30=None, bound=None, timeout=30):
    """Forced firmware call: set sp/args(+optional r30)/lr=CATCH/pc, continue."""
    bps = [CATCH] + ([bound] if bound else [])
    for b in bps:
        t.set_bp(b, hw=True)
    t.write_reg("r1", sp)
    for i, x in enumerate(args):
        t.write_reg(f"r{3+i}", x & 0xFFFFFFFF)
    if r30 is not None:
        t.write_reg("r30", r30)
    t.write_reg("lr", CATCH)
    t.write_reg("pc", pc)
    try:
        t.cont(timeout=timeout)
    except Exception:
        pass
    pc_out = t.regs().get("pc", 0)
    for b in bps:
        try:
            t.clear_bp(b, hw=True)
        except Exception:
            pass
    return pc_out


def reach_wall(t):
    t.run_to(DISPATCH, hw=True, timeout=90)
    t.set_bp(WALL, hw=True)
    t.cont(timeout=45)
    t.clear_bp(WALL, hw=True)
    return t.regs()["r1"]


def main(fnptr=ALLOC_MID_HANDLER):
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=70, label="qemu").connect()
    try:
        sp = reach_wall(t)
        print(f"[*] device-init wall, sp=0x{sp:08x}")

        # Stage 1 — general allocator (proven).
        if not BA.build(t, sp):
            print("[!] allocator build failed"); return
        print("[*] stage 1 OK: general allocator built")

        # Stage 2 — PCI enum (proven). Seed fn-ptrs + make E88's guard non-zero;
        # clear the cold-garbage table/count so the builder gate opens.
        w32(t, ALLOC_FNPTR, fnptr); w32(t, FREE_FNPTR, 0x00565518)
        w32(t, ONCE_GUARD, 1)
        w32(t, ENUM_COUNT, 0); w32(t, TABLE_BASE, 0); w32(t, TABLE_COUNT, 0)
        call_ctx(t, sp, ENUM, r30=INIT_BASE, bound=ENUM_BOUND, timeout=70)
        print(f"[*] stage 2 OK: enum count={u32(t, ENUM_COUNT)} "
              f"desc0=0x{u32(t, 0x010CF458):08x} desc1=0x{u32(t, 0x010CF45C):08x}")

        # Stage 3 — firmware device-table builder (DIVERGES — see module docstring).
        print(f"[*] stage 3: driving FUN_00563B58 (fn-ptr=0x{fnptr:08x}) ...")
        pc = call_ctx(t, sp, TABLE_BUILDER, r30=INIT_BASE, timeout=60)
        built = u32(t, TABLE_BASE)
        if pc == CATCH and built:
            print(f"[*] stage 3 OK?! table base=0x{built:08x} count={u32(t, TABLE_COUNT)}")
        else:
            print(f"[!] stage 3 DIVERGED at 0x{pc:08x} (keystone fault loop); "
                  f"table base=0x{built:08x} — device-table build needs the live scheduler")
    finally:
        t.close()


if __name__ == "__main__":
    main()
