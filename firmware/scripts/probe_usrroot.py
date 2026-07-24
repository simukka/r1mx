#!/usr/bin/env python3
"""
probe_usrroot.py — push the REAL boot path in QEMU.

The normal boot dispatches the root task into 0x381a8c (an OpenSSL X.509 artifact
forced by patches #53a/c; see re_reference.md §0.3). This probe instead hijacks the
running root-task context and forces PC = usrRoot (0x37C440, the natural rootRtn),
keeping the live task stack, then free-runs against a net of landmark + exception-
vector breakpoints to find the FIRST real divergence (missing device / fault / a
boot milestone like sysClkEnable). Reports where it lands.

Requires a QEMU r1mx-virtex4 stub on :1234 (qemu_boot.sh --debug).
"""
import sys, time
from rsp import RSP, RSPError

ROOT_ARTIFACT = 0x00381A8C   # where the patched boot currently dispatches
USRROOT       = 0x0037C440   # natural rootRtn (usrRoot), present in .text
SYSCLKENABLE  = 0x0000942C   # boot milestone we hope to reach

# PPC405 exception vectors (prefix 0x0000xxxx) — a hit here = a fault/divergence.
VECTORS = {
    0x00000100: "SystemReset", 0x00000200: "MachineCheck", 0x00000300: "DSI(data)",
    0x00000400: "ISI(instr)",  0x00000600: "Alignment",    0x00000700: "Program",
    0x00000800: "FPUnavail",   0x00000C00: "SystemCall",    0x00001000: "PIT",
    0x00001010: "FIT",         0x00001020: "Watchdog",      0x00000500: "ExtIntr",
}

# A few high-value boot landmarks usrRoot is expected to traverse.
LANDMARKS = {SYSCLKENABLE: "sysClkEnable"}


def main():
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=20.0, label="qemu").connect()
    try:
        print("[*] booting to the artifact root-task entry 0x%08x ..." % ROOT_ARTIFACT)
        regs = t.run_to(ROOT_ARTIFACT, hw=True, timeout=60.0)
        sp, lr = regs["r1"], regs.get("lr", 0)
        print(f"    in root-task context: r1(sp)=0x{sp:08x}  lr=0x{lr:08x}  "
              f"r3=0x{regs.get('r3',0):08x}")

        print("[*] forcing PC = usrRoot 0x%08x (keeping live stack) ..." % USRROOT)
        t.write_reg("pc", USRROOT)
        # give usrRoot a return-catcher so we notice if it ever returns
        RET_CATCH = 0x00000004
        t.write_reg("lr", RET_CATCH)

        bps = list(VECTORS) + list(LANDMARKS) + [RET_CATCH]
        for a in bps:
            t.set_bp(a, hw=True)

        print("[*] free-running usrRoot against %d landmark/vector breakpoints ..." % len(bps))
        deadline = time.time() + 30.0
        hit = None
        spun = False
        while time.time() < deadline:
            try:
                stop = t.cont(timeout=12.0)
            except TimeoutError:
                spun = True
                break
            if not (stop.startswith("T") or stop.startswith("S")):
                print(f"    unexpected stop reply: {stop!r}"); break
            pc = t.regs().get("pc", 0)
            if pc in VECTORS:
                hit = ("VECTOR", pc, VECTORS[pc]); break
            if pc in LANDMARKS:
                hit = ("LANDMARK", pc, LANDMARKS[pc]); break
            if pc == RET_CATCH:
                hit = ("RETURN", pc, "usrRoot returned"); break
            print(f"    stopped at unexpected pc=0x{pc:08x}; continuing")

        if spun and hit is None:
            # interrupt, then single-step to capture the loop body and confirm spin
            t.interrupt(timeout=5.0)
            r1 = t.regs(); pc1 = r1.get("pc", 0)
            seen = [pc1]
            for _ in range(14):
                t.step(timeout=5.0)
                seen.append(t.regs().get("pc", 0))
            pc2 = seen[-1]
            lo = min(seen) & ~0xf
            code = t.read_mem(lo - 0x10, 0x60)
            print(f"\n  SPIN detected — pc range 0x{min(seen):08x}..0x{max(seen):08x} "
                  f"(start 0x{pc1:08x})")
            print(f"    lr=0x{r1.get('lr',0):08x} r3=0x{r1.get('r3',0):08x} "
                  f"r4=0x{r1.get('r4',0):08x} r5=0x{r1.get('r5',0):08x} r1=0x{r1.get('r1',0):08x}")
            try:
                from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN
                md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
                print("    loop disassembly:")
                for ins in md.disasm(code, lo - 0x10):
                    mark = " <= pc" if ins.address in set(seen) else ""
                    print(f"      0x{ins.address:08x}: {ins.mnemonic:7s} {ins.op_str}{mark}")
            except Exception as e:
                print(f"    (capstone unavailable: {e}) raw={code.hex()}")
            # record the spin as the divergence (target is already halted here)
            hit = ("SPIN", min(seen), "usrRoot spins (likely a list/poll over zero heap)")
        for a in bps:
            try: t.clear_bp(a, hw=True)
            except Exception: pass

        print("\n=== RESULT ===")
        if hit:
            kind, pc, name = hit
            r = t.regs()
            print(f"  FIRST DIVERGENCE: {kind} @0x{pc:08x}  ({name})")
            print(f"    lr=0x{r.get('lr',0):08x}  r3=0x{r.get('r3',0):08x}  "
                  f"r4=0x{r.get('r4',0):08x}  r1=0x{r.get('r1',0):08x}")
            if kind == "VECTOR":
                # for DSI/ISI, the faulting address is in DEAR (SPR 981) / SRR0
                print("    -> usrRoot took a CPU exception; inspect SRR0/DEAR and the"
                      " instruction before the fault to find the missing dependency.")
            elif kind == "LANDMARK":
                print("    -> reached a real boot milestone on the natural path!")
            elif kind == "SPIN":
                print("    -> usrRoot advanced on the REAL boot path but spins here;"
                      " check whether the data it walks lives above the 0xE8BF20 file"
                      " end (runtime heap a completed cold boot would build) or is an"
                      " unmodeled device poll.")
        else:
            print("  usrRoot returned or hit no net point cleanly (see above).")
    finally:
        t.close()


if __name__ == "__main__":
    main()
