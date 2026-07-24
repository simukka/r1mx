#!/usr/bin/env python3
"""probe_malloc.py — characterize WHY repeated mallocs fail after the hand-built
allocator, and test whether the FAITHFUL real init (FUN_0045acac) fixes it.

The hand-built allocator (build_allocator.py) services only the FIRST malloc;
the 2nd+ return garbage.  The core carve FUN_0045a428 reinserts the split
remainder into the free tree (+0x40) via FUN_0045a2c0, which pops/pushes tree
nodes from a free-node pool head at +0x48 (count +0x4c).  This probe does N
sequential mallocs and dumps the partition's tree state between each, for two
build modes:

  --mode hand : build_allocator (FUN_004593a8 + FUN_0045aa38, skips FUN_0043c570)
  --mode real : force guard *0xE295F8=0 and call the REAL init FUN_0045acac
                (= FUN_0043c570 object-create + FUN_0045aa38) — the faithful path

Requires: qemu_boot.sh --debug --background (stub :1234).
"""
import argparse
import struct
from rsp import RSP
from build_allocator import build as hand_build, _call, POOL_BASE, POOL_SIZE, PART_ADDR, CATCH

# faithful init
GUARD     = 0x00E295F8   # iRam00e295f8 init guard (FUN_0045acac runs only if 0)
FUN_INIT  = 0x0045ACAC   # real allocator init: FUN_0043c570 + FUN_0045aa38
FUN_MOD   = 0x004593A8   # module init (flags + fn-ptrs)
FUN_MALLOC= 0x0045B974

USRROOT_TRUE_ENTRY = 0x0037BF78
USRROOT_RESUME     = 0x0037C440
CFG_INSN_ADDR      = 0x00000274
CFG_INSN_GOOD      = 0x7C632B78


def u32(t, a): return struct.unpack(">I", t.read_mem(a, 4))[0]
def w32(t, a, v): t.write_mem(a, struct.pack(">I", v & 0xFFFFFFFF))


def reach_wall(t):
    """Faithful true-entry path to the device-init allocator wall (0x274 intact)."""
    t.run_to(0x00371CD0, hw=True, timeout=60.0)
    w32(t, 0xE9C5C0, 0xE9C5C0); w32(t, 0xE9C5C4, 0xE9C5C0)
    t.run_to(USRROOT_RESUME, hw=True, timeout=30.0)
    ctx = {r: t.regs().get(r, 0) for r in ('r1','r3','r4','r5','r6','r7','r8','r9','r10')}
    for phase in (1, 2):
        for r, v in ctx.items(): t.write_reg(r, v)
        t.write_reg("lr", CATCH); t.write_reg("pc", USRROOT_TRUE_ENTRY)
        if phase == 1:
            t.run_to(CATCH, hw=True, timeout=40.0)
        else:
            t.set_bp(0x00555488, hw=True); t.cont(timeout=40); t.clear_bp(0x00555488, hw=True)
    return t.regs()["r1"]


def real_build(t, sp, pool=POOL_BASE, size=POOL_SIZE):
    """Faithful: module init, force guard=0, call real FUN_0045acac(pool,size)."""
    _call(t, sp, FUN_MOD, 0, 0, 0xBB0)        # module flags + alloc/free method fn-ptrs
    w32(t, 0xE295D4, u32(t, 0xE26D3C))         # min-align = granule (FUN_0045acac also sets this)
    w32(t, GUARD, 0)                           # ungate the real init
    pc, lr, r3 = _call(t, sp, FUN_INIT, pool, size, timeout=40)
    print(f"[real] FUN_0045acac(pool,size) ret={r3:#x} stop=0x{pc:08x} guard={u32(t,GUARD):#x}")
    if pc != CATCH:
        print(f"[real] init FAULTED at 0x{pc:08x}"); return False
    w32(t, 0xE295C4, PART_ADDR)
    return True


def dump_part(t, tag):
    p = PART_ADDR
    print(f"  [{tag}] tree+0x40=0x{u32(t,p+0x40):08x} nodepool+0x48=0x{u32(t,p+0x48):08x} "
          f"nodecnt+0x4c=0x{u32(t,p+0x4c):08x} +0xc0(flags)=0x{u32(t,p+0xc0):08x} "
          f"blkcnt+0xe0=0x{u32(t,p+0xe0):08x} +0xcc(method)=0x{u32(t,p+0xcc):08x} "
          f"+0x30(vtab)=0x{u32(t,p+0x30):08x}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("hand", "real"), default="real")
    ap.add_argument("-n", type=int, default=6)
    args = ap.parse_args()

    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=30.0, label="qemu").connect()
    try:
        sp = reach_wall(t)
        intact = u32(t, CFG_INSN_ADDR) == CFG_INSN_GOOD
        print(f"[*] wall sp=0x{sp:08x}  0x274 intact={intact}")

        if args.mode == "hand":
            if not hand_build(t, sp): print("[!] hand build failed"); return
        else:
            if not real_build(t, sp): print("[!] real build failed"); return
        dump_part(t, "post-build")

        print(f"[*] {args.n} sequential mallocs (mode={args.mode}):")
        for i in range(args.n):
            sz = 0x24 if i % 2 else 0x54
            pc, lr, r3 = _call(t, sp, FUN_MALLOC, sz, timeout=20)
            inpool = POOL_BASE <= r3 < POOL_BASE + POOL_SIZE
            ok = "OK " if (pc == CATCH and inpool) else "BAD"
            print(f"  malloc#{i+1}(0x{sz:02x}) -> 0x{r3:08x} [{ok}] stop=0x{pc:08x}")
            dump_part(t, f"after#{i+1}")
    finally:
        t.close()


if __name__ == "__main__":
    main()
