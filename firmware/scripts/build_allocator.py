#!/usr/bin/env python3
"""build_allocator.py — construct RED's tree memory-partition allocator in QEMU
by driving the firmware's own init functions, then verify malloc works.

The cold boot stalls because the heap allocator (`*0xE295C4`, RED's custom
tree-based memory partition at the fixed address 0xFC2530) is never built — its
init (`FUN_0045acac`) is gated by a garbage `.data` guard (`iRam00e295f8 != 0`)
and needs the object/class system. This bypasses that: it sets the module
globals, seeds two garbage prerequisites, and calls the partition init
`FUN_0045aa38(0xFC2530, pool, size)` directly (which does memset + flags +
semMInit lock + addToPool), then points `*0xE295C4` at it. VERIFIED 2026-06-15:
`FUN_0045B974(0x54)` then returns real, writable pool memory.

Call `build(rsp, sp)` from a harness while halted in a valid root-task context
(e.g. at the FUN_00555488 allocator wall). `rsp` must be allow_write=True.

Addresses (img base 0; see boot_reconstruction_status.md / heap_structures_README.md):
  FUN_004593a8  module init (sets flags default 0xBB0 + fn-ptrs)
  FUN_0045aa38  partition init + addToPool (the create)
  FUN_0045b974  malloc entry (verify)
  0xFC2530      fixed partition object address (hardcoded in firmware)
  *0xE295C4     global pointer to the partition
  *0xE295D4     min-align (= granule *0xE26D3C)
  *0xE295F4     method-setup fn-ptr (garbage cold -> seed 0 to skip)
  *0xE295F8     init guard (garbage cold; FUN_0045acac runs only if 0)
"""
import struct

POOL_BASE = 0x08000000
POOL_SIZE = 0x04000000   # 64 MB in the heap band (sysMemTop=0x10000000)
PART_ADDR = 0x00FC2530
CATCH     = 0x0000000C
# NB: do NOT trap on {0x100..0x700} as "exception vectors". The PPC405 relocates
# its vectors via EVPR; the firmware's low XPci config driver actually lives at
# 0x100-0x9000 (physical 0x600 is a `beq` inside FUN_000005a4). Bps there fire on
# NORMAL code and were misread as a "0x600 alignment fault" (debunked 2026-06-15).
# Rely on a high CATCH + the QEMU `-d int` log for real exceptions instead.
_VEC = set()


def _u32(t, a):
    return struct.unpack(">I", t.read_mem(a, 4))[0]


def _w32(t, a, v):
    t.write_mem(a, struct.pack(">I", v & 0xFFFFFFFF))


def _call(t, sp, pc, *args, timeout=25):
    """Call a firmware function via the stub; return (stop_pc, lr, r3)."""
    for v in _VEC:
        t.set_bp(v, hw=True)
    t.set_bp(CATCH, hw=True)
    t.write_reg("r1", sp)
    for i, x in enumerate(args):
        t.write_reg(f"r{3+i}", x & 0xFFFFFFFF)
    t.write_reg("lr", CATCH)
    t.write_reg("pc", pc)
    t.cont(timeout=timeout)
    r = t.regs()
    for v in list(_VEC) + [CATCH]:
        try:
            t.clear_bp(v, hw=True)
        except Exception:
            pass
    return r.get("pc", 0), r.get("lr", 0), r.get("r3", 0)


def build(t, sp, pool=POOL_BASE, size=POOL_SIZE, verify=True):
    """Construct the allocator. Returns True on success (malloc returns pool mem)."""
    # 1) module globals (flags default 0xBB0, alloc/free method fn-ptrs)
    _call(t, sp, 0x004593a8, 0, 0, 0xBB0)
    # 2) seed the garbage prerequisites FUN_0045aa38 / the carve FUN_0045a428 need
    _w32(t, 0xE295D4, _u32(t, 0xE26D3C))   # min-align = granule
    _w32(t, 0xE295F4, 0)                    # method-setup fn-ptr -> skip (cold garbage)
    # iRam00e295e4 = per-allocation guard/red-zone size (memPartLib). Cold-garbage
    # ~0x00d8fad0 (~14 MB) makes addToPool waste 14 MB at the pool front and makes
    # the carve overhead so large the FIRST malloc takes the no-split branch and
    # empties the free tree -> only ONE malloc is serviceable. Nothing in the
    # allocator init writes it (it's a read-only config const set by the bypassed
    # early data init); 0 = guards off, the production default. (Root cause found
    # 2026-06-17 via probe_geom.py.)
    _w32(t, 0xE295E4, 0)
    # 3) init the partition at the fixed 0xFC2530 with the pool
    pc, lr, r3 = _call(t, sp, 0x0045AA38, PART_ADDR, pool, size)
    if pc != CATCH:
        print(f"[build_allocator] FUN_0045aa38 faulted at 0x{pc:08x}")
        return False
    # 4) point the global at our partition
    _w32(t, 0xE295C4, PART_ADDR)
    flags = _u32(t, PART_ADDR + 0xC0)
    tree = _u32(t, PART_ADDR + 0x40)
    print(f"[build_allocator] partition built: +0xC0=0x{flags:08x} +0x40 tree=0x{tree:08x} "
          f"count=0x{_u32(t, PART_ADDR+0x4c):08x}")
    if not verify:
        return True
    # 5) verify malloc
    pc, lr, r3 = _call(t, sp, 0x0045B974, 0x54)
    ok = (pc == CATCH and pool <= r3 < pool + size)
    if ok:
        _w32(t, r3, 0xA5A5A5A5)
        rb = _u32(t, r3)
        ok = (rb == 0xA5A5A5A5)
        print(f"[build_allocator] FUN_0045b974(0x54) = 0x{r3:08x} (in pool), writable={ok}")
    else:
        print(f"[build_allocator] malloc verify FAILED pc=0x{pc:08x} r3=0x{r3:08x}")
    return ok


if __name__ == "__main__":
    # Standalone: boot QEMU (dispatch fix in machine), reach the allocator wall, build, verify.
    from rsp import RSP
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=30.0, label="qemu").connect()
    try:
        t.run_to(0x00371CD0, hw=True, timeout=60.0)             # dispatch
        _w32(t, 0xE9C5C0, 0xE9C5C0); _w32(t, 0xE9C5C4, 0xE9C5C0)  # deferred-write list
        t.set_bp(0x00555488, hw=True); t.cont(timeout=20); t.clear_bp(0x00555488, hw=True)
        sp = t.regs()["r1"]
        print(f"[*] at allocator wall, sp=0x{sp:08x}")
        ok = build(t, sp)
        print("[*] RESULT:", "allocator WORKS" if ok else "FAILED")
    finally:
        t.close()
