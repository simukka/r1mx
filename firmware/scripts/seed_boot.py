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

Requires: qemu_boot.sh --patched --debug --background  (stub on :1234).
"""
import sys, time
from rsp import RSP, RSPError

ROOT_ARTIFACT = 0x00381A8C
USRROOT       = 0x0037C440

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


def main():
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=20.0, label="qemu").connect()
    try:
        print("[*] boot -> artifact entry 0x%08x" % ROOT_ARTIFACT)
        regs = t.run_to(ROOT_ARTIFACT, hw=True, timeout=60.0)
        print(f"    sp=0x{regs['r1']:08x}")

        print(f"[*] applying {len(SEEDS)} seed(s):")
        for addr, val, note in SEEDS:
            t.write_mem(addr, (val & 0xFFFFFFFF).to_bytes(4, "big"))
            rb = int.from_bytes(t.read_mem(addr, 4), "big")
            ok = "OK" if rb == (val & 0xFFFFFFFF) else f"MISMATCH(read 0x{rb:08x})"
            print(f"    0x{addr:08x} <- 0x{val:08x}  [{ok}]  {note}")

        print("[*] forcing PC = usrRoot 0x%08x" % USRROOT)
        t.write_reg("pc", USRROOT)
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
