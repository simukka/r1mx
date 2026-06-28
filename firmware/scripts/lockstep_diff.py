#!/usr/bin/env python3
"""
lockstep_diff.py — run the live PPC405 (via XMD's GDB stub) and QEMU
side-by-side and diff them instruction-by-instruction to find exactly where the
emulation diverges from real silicon. This is the tool for finishing the
r1mx-virtex4 peripheral models (plans/qemu_xilinx_drivers.md).

Targets (both speak RSP — see rsp.py):
    HW   : XMD GDB stub, reached via VirtualBox NAT pf  (default 127.0.0.1:2345)
    QEMU : qemu_boot.sh --patched --debug               (default 127.0.0.1:1234)

Typical use
-----------
  # terminal 1
  firmware/scripts/qemu_boot.sh --patched --debug
  # VM: standalone xmd ; connect ppc hw   (starts stub on guest :1234)
  # host: VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"

  # terminal 2 — step both to usrInit, then diff 500 instructions
  python3 firmware/scripts/lockstep_diff.py --bp 0x36c350 --steps 500 \
          --watch 0xe0600000:16 --watch 0x00e26d28:4

Modes
-----
  (default)        lock-step single-step both, report FIRST register/memory
                   divergence with the diverging instruction.
  --mmio-capture A read each --watch range on HW only and print the live values
                   (ground truth for modelling a QEMU device). No QEMU needed.

Safety: read-only. Hardware breakpoints (Z1/IAC) only — never patches camera
memory. Never resets. See host_xmd_bridge.md.
"""

import argparse
import sys
from pathlib import Path

from rsp import RSP, PPC_REG_NAMES, RSPError, layout_for

# Flat firmware image (VA == file offset). Used to source INSTRUCTION bytes when
# the HW stub returns 0: XMD's 'm' reads go through the data MMU/TLB, so code
# addresses not currently D-mapped read back as 0 (see host_xmd_bridge.md).
DEFAULT_IMAGE = (Path(__file__).resolve().parent.parent
                 / "reverse/build_32/extracted/software.bin")


def parse_watch(items):
    out = []
    for it in items or []:
        addr_s, _, len_s = it.partition(":")
        addr = int(addr_s, 0)
        length = int(len_s, 0) if len_s else 4
        out.append((addr, length))
    return out


def insn_word(target, addr, image):
    """Instruction word at `addr`, preferring a real value. HW data-side reads
    return 0 for code not mapped in the D-TLB, so fall back to the flat image
    (and report which source was used)."""
    try:
        w = target.read_word(addr)
    except RSPError:
        w = 0
    if w == 0 and image is not None and 0 <= addr and addr + 4 <= len(image):
        iw = int.from_bytes(image[addr:addr + 4], "big")
        if iw != 0:
            return iw, "image"
    return w, "stub"


def snapshot_mem(t, watch):
    snap = {}
    for addr, length in watch:
        try:
            snap[addr] = t.read_mem(addr, length)
        except RSPError:
            snap[addr] = None
    return snap


def diff_regs(a, b):
    out = []
    for name in PPC_REG_NAMES:
        if a.get(name) != b.get(name):
            out.append((name, a.get(name), b.get(name)))
    return out


def fmt_regs(label, regs):
    pc = regs.get("pc", 0)
    return (f"{label}: PC=0x{pc:08x} LR=0x{regs.get('lr',0):08x} "
            f"CTR=0x{regs.get('ctr',0):08x} MSR=0x{regs.get('msr',0):08x} "
            f"r1=0x{regs.get('r1',0):08x} r3=0x{regs.get('r3',0):08x}")


def addr_pair(spec, default_port):
    host, _, port = spec.partition(":")
    return host or "127.0.0.1", int(port) if port else default_port


def mmio_capture(hw, watch):
    print("[*] MMIO capture from LIVE hardware (ground truth for QEMU models):")
    regs = hw.regs()
    print("    " + fmt_regs("HW", regs))
    for addr, length in watch:
        try:
            data = hw.read_mem(addr, length)
            words = " ".join(f"{int.from_bytes(data[i:i+4],'big'):08x}"
                             for i in range(0, len(data) - len(data) % 4, 4))
            print(f"    [0x{addr:08x}] +{length}B = {words or data.hex()}")
        except RSPError as e:
            print(f"    [0x{addr:08x}] read failed: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hw", default="127.0.0.1:2345",
                    help="XMD GDB stub host:port (default 127.0.0.1:2345)")
    ap.add_argument("--qemu", default="127.0.0.1:1234",
                    help="QEMU gdbstub host:port (default 127.0.0.1:1234)")
    ap.add_argument("--bp", default=None,
                    help="fast-forward BOTH targets to this addr before stepping")
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--watch", action="append", default=[],
                    help="memory/MMIO range ADDR[:LEN] to compare each step "
                         "(repeatable). LEN defaults to 4.")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--image", default=str(DEFAULT_IMAGE),
                    help="flat firmware image (VA==offset) to source instruction "
                         "bytes when the HW stub returns 0 for un-D-mapped code")
    ap.add_argument("--mmio-capture", action="store_true",
                    help="HW-only: dump --watch ranges from live silicon, no diff")
    args = ap.parse_args()

    watch = parse_watch(args.watch)
    try:
        image = Path(args.image).read_bytes()
        print(f"[*] instruction image: {args.image} ({len(image)} bytes)")
    except OSError:
        image = None
        print(f"[!] image not loaded ({args.image}); HW insn reads may show 0")
    hwh, hwp = addr_pair(args.hw, 2345)
    hw = RSP(hwh, hwp, timeout=args.timeout, label="HW").connect()

    if args.mmio_capture:
        try:
            hw.stop_reply(args.timeout)
            mmio_capture(hw, watch)
        finally:
            hw.detach(); hw.close()
        return 0

    qh, qp = addr_pair(args.qemu, 1234)
    qemu = RSP(qh, qp, timeout=args.timeout, label="QEMU").connect()

    try:
        for t in (hw, qemu):
            t.stop_reply(args.timeout)

        # Report register-block sizes. Different sizes are EXPECTED (XMD 146-word
        # vs QEMU 38-word) and handled by per-target layouts; only an unrecognised
        # size is a problem.
        for t in (hw, qemu):
            t.regs()
            nwords = t._reglen // 8
            known = "known layout" if layout_for(nwords) else "UNKNOWN layout"
            print(f"[*] {t.label} 'g' block = {nwords} x 32-bit regs ({known})")
            if not layout_for(nwords):
                print(f"[!] {t.label}: unrecognised register block size — add a "
                      "layout in rsp.py (run rsp_discover.py to map it).")

        if args.bp:
            bp = int(args.bp, 0)
            print(f"[*] Fast-forwarding both targets to 0x{bp:08x} ...")
            for t in (hw, qemu):
                t.run_to(bp, hw=True, timeout=args.timeout)
            print("[*] Both at breakpoint.")

        rh, rq = hw.regs(), qemu.regs()
        mh, mq = snapshot_mem(hw, watch), snapshot_mem(qemu, watch)

        rd = diff_regs(rh, rq)
        if rd:
            print("[!] Targets already differ BEFORE stepping:")
            for name, a, b in rd:
                print(f"      {name}: HW=0x{(a or 0):08x} QEMU=0x{(b or 0):08x}")

        for n in range(1, args.steps + 1):
            pre_pc_hw = rh.get("pc", 0)
            hw.step(args.timeout)
            qemu.step(args.timeout)
            rh, rq = hw.regs(), qemu.regs()
            mh, mq = snapshot_mem(hw, watch), snapshot_mem(qemu, watch)

            rdiff = diff_regs(rh, rq)
            mdiff = [(a, mh.get(a), mq.get(a)) for a, _ in watch
                     if mh.get(a) != mq.get(a)]

            if rdiff or mdiff:
                iw, src = insn_word(hw, pre_pc_hw, image)
                print(f"\n=== DIVERGENCE at step {n} ===")
                print(f"  instr just executed @ HW PC 0x{pre_pc_hw:08x}: "
                      f"0x{iw:08x} (from {src})")
                print("  " + fmt_regs("HW  ", rh))
                print("  " + fmt_regs("QEMU", rq))
                for name, a, b in rdiff:
                    print(f"    REG {name}: HW=0x{(a or 0):08x} "
                          f"!= QEMU=0x{(b or 0):08x}")
                for addr, a, b in mdiff:
                    print(f"    MEM 0x{addr:08x}: HW={a.hex() if a else None} "
                          f"!= QEMU={b.hex() if b else None}")
                print("\n[=>] First divergence usually marks an unmodeled/incorrect "
                      "peripheral read in QEMU. Capture the live value with "
                      "--mmio-capture and fix the device model.")
                return 2

            if n % 50 == 0:
                print(f"[*] {n} steps in lock-step; "
                      f"PC=0x{rh.get('pc',0):08x} (matched)")

        print(f"\n[*] {args.steps} steps with NO divergence "
              f"(final PC=0x{rh.get('pc',0):08x}). Emulation matches here.")
        return 0
    finally:
        for t in (hw, qemu):
            try:
                t.detach()
            except Exception:
                pass
            t.close()


if __name__ == "__main__":
    sys.exit(main())
