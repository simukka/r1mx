#!/usr/bin/env python3
"""
patch_firmware.py — Binary patcher for RED ONE MX firmware binaries

Applies NOP patches to stub out hardware init sequences that crash QEMU.
Defaults to Build 32 (software.bin).  Pass --build13 for Build 13.

Usage:
    python3 scripts/patch_firmware.py [--input PATH] [--output PATH]
                                      [--list] [--probe ADDR] [--phase N]
                                      [--build13]

Strategy:
  PPC big-endian NOP = 0x60000000 (ori r0, r0, 0)
  PPC return (blr)   = 0x4E800020

  We NOP individual instructions that access hardware not present in QEMU,
  or replace function preambles with blr to skip entire init routines.

Build 32 patch summary:
  Phase 1 (always apply):
    0x000084   SP relocation: lis r1,1 → lis r1,0x800
    0x36C388   NOP canary wait bne #1
    0x36C394   NOP canary wait bne #2
  Phase 2 (apply as crash sites are discovered):
    0x36FA1C   Always-branch past bogus SSL verify-callback dispatch

Build 13 patches are preserved for reference (--build13 flag).
"""

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PPC_NOP = b"\x60\x00\x00\x00"   # ori r0, r0, 0
PPC_BLR = b"\x4e\x80\x00\x20"   # blr (return)
PPC_LI_R3_0_BLR = b"\x38\x60\x00\x00\x4e\x80\x00\x20"  # li r3,0; blr (return 0)


@dataclass
class Patch:
    offset: int
    original: bytes     # expected original bytes (safety check)
    replacement: bytes
    description: str
    phase: int = 1      # which boot phase this patch is for


# ---------------------------------------------------------------------------
# Known patches — organised by boot phase
# ---------------------------------------------------------------------------
# Phase 1: DCR-level hardware init (SDRAM0, EBC0, CPC0, UIC0).
#   QEMU bamboo silently ignores unknown DCR writes via `mtdcr`, so these
#   may not actually crash. Include as safeguards.
#
# Phase 2: MMIO peripheral init (timer, interrupt controller, FPGA registers).
#   These WILL crash — QEMU will generate machine checks on unmapped MMIO.
#   Add patches here as crash addresses are discovered via r2 debug session.
#
# Patch format:
#   offset      — file offset (= runtime address since binary loads at 0x0)
#   original    — first 4 bytes at that offset (verify before patching)
#   replacement — NOP or BLR
#   description — what is being stubbed

# ---------------------------------------------------------------------------
# Build 32 patches  (default — software.bin, 15,253,280 bytes)
# SHA-256: 416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd
# ---------------------------------------------------------------------------
BUILD32_PATCHES: list[Patch] = [
    # -----------------------------------------------------------------------
    # Phase 1 — SP relocation
    #
    # romInit at 0x84 sets SP = 0x10000 (64 KB).  With a 15 MB image and deep
    # VxWorks init call chains, the stack collides with code.  Relocate to the
    # 128 MB mark (well above the firmware image).
    #   lis r1, 0x0001  →  lis r1, 0x0800
    Patch(
        offset=0x000084,
        original=b'\x3c\x20\x00\x01',
        replacement=b'\x3c\x20\x08\x00',
        description="Relocate romInit SP: lis r1,1 → lis r1,0x800 (SP=0x07FFFFF0)",
        phase=1,
    ),
    # -----------------------------------------------------------------------
    # Phase 1 — Stack canary wait loop (0x36C380–0x36C394)
    #
    # usrInit at 0x36C350 spins waiting for:
    #   *(0x00E269A4) == 0x12348765
    #   *(0x00E269A0) == 0x5A5AC3C3
    # Set by secondary hardware init on real camera; never written in QEMU.
    # NOP both bne branches to fall through immediately.
    Patch(
        offset=0x36C388,
        original=b'\x40\x9e\xff\xf8',
        replacement=PPC_NOP,
        description="NOP canary bne #1 (0x36C380 loop, tests 0x00E269A4)",
        phase=1,
    ),
    Patch(
        offset=0x36C394,
        original=b'\x40\x9e\xff\xec',
        replacement=PPC_NOP,
        description="NOP canary bne #2 (0x36C380 loop, tests 0x00E269A0)",
        phase=1,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 — Crash patches discovered via QEMU CPU trace analysis
    # -----------------------------------------------------------------------
    #
    # Crash #1: bogus SSL/TLS verify-callback dispatch (0x36FA1C)
    #
    # Diagnosed via -d cpu,int QEMU trace. Execution path:
    #   usrInit (0x36C3C8) → bl 0x36F9F8 → bctrl at 0x36FA24 → 0xD7E680
    #
    # fn_36F9F8 loads a "function pointer" from 0xE26D28 (HA=0xE2, off=+0x6D28).
    # That address holds 0x00D7E680 — a pointer to the SSL string literal
    # "cert depth=%d %s\n".  This is clearly an X.509/SSL callback table
    # entry, NOT a function pointer.  The code does:
    #   if (ptr == 0) skip; else call(ptr);
    # but the entry is non-zero (it is the string address), so it tries to
    # call into the data segment.  Instruction at +16 (0xD7E690) = 0x0A000000
    # (opcode 2 = tdi, invalid on PPC32) → QEMU raises HV_EMU (96) → infinite
    # exception restart loop.
    #
    # Fix: change the `beq 0x36FA28` to unconditional `b 0x36FA28`, so the
    # bctrl is always bypassed regardless of the callback pointer value.
    Patch(
        offset=0x36FA1C,
        original=b'\x41\x82\x00\x0c',   # beq 0x36FA28 (skip if ptr==0)
        replacement=b'\x48\x00\x00\x0c', # b 0x36FA28 (always skip)
        description="Skip bogus SSL verify-callback dispatch: fn_36F9F8 reads a string ptr (0xD7E680) as a function ptr; always branch past bctrl",
        phase=2,
    ),
    #
    # Known candidate crash sites (from static analysis — verify addresses):
    #   0x000012DB4  lis r0, 0x4010  → MMIO 0x4010E507 (unknown peripheral)
    #   0x000012DD4  lis r0, 0x4004  → MMIO 0x4004E505 (unknown peripheral)
    #   0x0000DCB0   sysHwInit_seq   → calls device enable sub-functions w/ MMIO
    #   0x001C18DC   sysSerialInit   → XUartLite at 0x40600000 (may work in QEMU)
]

# ---------------------------------------------------------------------------
# Build 13 patches  (legacy — SundanceBootable.bin, ~13 MB)
# Use: python3 scripts/patch_firmware.py --build13
# ---------------------------------------------------------------------------
BUILD13_PATCHES: list[Patch] = [
    Patch(
        offset=0x7C,
        original=b'\x3c\x20\x00\x01',
        replacement=b'\x3c\x20\x08\x00',
        description="Relocate romInit stack: lis r1,1 → lis r1,0x800 (SP=0x07FFFFF0)",
        phase=1,
    ),
    Patch(
        offset=0x2ED058,
        original=b'\x40\x9e\xff\xf8',
        replacement=PPC_NOP,
        description="NOP canary wait loop: bne cr7, 0x2ED050 (first branch)",
        phase=1,
    ),
    Patch(
        offset=0x2ED064,
        original=b'\x40\x9e\xff\xec',
        replacement=PPC_NOP,
        description="NOP canary wait loop: bne cr7, 0x2ED050 (second branch)",
        phase=1,
    ),
    Patch(
        offset=0x2F06D8,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x2F06B0 (skip exception-handler bctrl)",
        phase=1,
    ),
    Patch(
        offset=0x2F06DC,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x2F06B0 (skip call to 0x500 exception handler body)",
        phase=1,
    ),
    Patch(
        offset=0xDA80,
        original=b'\x4b\xff\xc1\x41',
        replacement=PPC_NOP,
        description="NOP: bl 0x9BC0 (IO/VP FPGA bitstream loader — no FPGA in QEMU)",
        phase=2,
    ),
    Patch(
        offset=0x3AB000,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x3AAFD8 path-1 (skip fptr call via *(0xBC5484))",
        phase=2,
    ),
    Patch(
        offset=0x3AB004,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x3AAFD8 path-1 (*(0xBC5484) default = 0x500 AE vector)",
        phase=2,
    ),
    Patch(
        offset=0x3AB04C,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x3AAFD8 path-2 (skip fptr call via *(0xBC5488))",
        phase=2,
    ),
    Patch(
        offset=0x3AB050,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x3AAFD8 path-2 (*(0xBC5488) = 0x500 Alignment vector)",
        phase=2,
    ),
    Patch(
        offset=0x2ED0A0,
        original=b'\x48\x00\x1d\x81',
        replacement=PPC_NOP,
        description="NOP: bl 0x2EEE20 in usrInit — EVPR-relocating hardware init crashes QEMU",
        phase=2,
    ),
]

# Active patch set — selected by --build13 flag
KNOWN_PATCHES: list[Patch] = BUILD32_PATCHES


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_patches(data: bytearray, patches: list[Patch],
                  phase: Optional[int] = None) -> tuple[int, list[str]]:
    """
    Apply patches to a mutable bytearray.
    Returns (count_applied, list_of_warnings).
    """
    applied = 0
    warnings = []
    for p in patches:
        if phase is not None and p.phase != phase:
            continue
        end = p.offset + len(p.original)
        if end > len(data):
            warnings.append(f"SKIP offset {hex(p.offset)}: beyond file end")
            continue
        actual = bytes(data[p.offset:end])
        if actual != p.original:
            warnings.append(
                f"MISMATCH at {hex(p.offset)} '{p.description}': "
                f"expected {p.original.hex()} got {actual.hex()} — skipped"
            )
            continue
        data[p.offset:p.offset + len(p.replacement)] = p.replacement
        applied += 1
        print(f"  [+] {hex(p.offset)}: {p.description}")
    return applied, warnings


def add_patch(offset: int, fw_path: Path) -> None:
    """
    Helper: print the original bytes at an offset so a new Patch entry can
    be added to KNOWN_PATCHES.  Use during the r2 debug session:
        python3 scripts/patch_firmware.py --probe 0xADDRESS
    """
    with open(fw_path, "rb") as f:
        f.seek(offset)
        orig = f.read(4)
    print(f"Probe at {hex(offset)}: original bytes = {orig.hex()}")
    print(f"Add to KNOWN_PATCHES:")
    print(f"    Patch(")
    print(f"        offset=0x{offset:08x},")
    print(f"        original=b'{orig.hex()}',")
    print(f"        replacement=PPC_NOP,")
    print(f"        description='NOP: <describe what this does>',")
    print(f"        phase=2,")
    print(f"    ),")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch RED ONE MX firmware binary for QEMU hardware stubs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i", type=Path,
        default=None,
        help="Input firmware binary (default: Build 32 software.bin)",
    )
    parser.add_argument(
        "--output", "-o", type=Path,
        default=None,
        help="Output path (default: <input_dir>/software.patched.bin)",
    )
    parser.add_argument(
        "--build13", action="store_true",
        help="Use Build 13 patches (SundanceBootable.bin) instead of Build 32",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="List all known patches and exit",
    )
    parser.add_argument(
        "--probe", type=lambda x: int(x, 0),
        metavar="OFFSET",
        help="Print original bytes at OFFSET to help create a new Patch entry",
    )
    parser.add_argument(
        "--phase", type=int, default=None,
        help="Only apply patches for this phase number",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    # Select patch set and default paths
    if args.build13:
        patches = BUILD13_PATCHES
        default_input = repo_root / "reverse/Upgrade_Build 13/Upgrade/SundanceBootable.bin"
        default_output_name = "SundanceBootable.patched.bin"
        build_label = "Build 13"
    else:
        patches = BUILD32_PATCHES
        default_input = repo_root / "reverse/build_32/extracted/software.bin"
        default_output_name = "software.patched.bin"
        build_label = "Build 32"

    # Resolve input path
    if args.input is None:
        args.input = default_input
    elif not args.input.is_absolute():
        args.input = repo_root / args.input

    # Resolve output path
    if args.output is None:
        args.output = args.input.parent / default_output_name
    elif not args.output.is_absolute():
        args.output = repo_root / args.output

    if args.list:
        print(f"Patches for {build_label} ({len(patches)} total):")
        for p in patches:
            print(f"  Phase {p.phase}  {hex(p.offset):<12}  {p.description}")
        return

    if args.probe is not None:
        add_patch(args.probe, args.input)
        return

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = bytearray(args.input.read_bytes())
    original_sha = sha256_of(bytes(data))
    print(f"[*] {build_label} input : {args.input} ({len(data):,} bytes)")
    print(f"    sha256: {original_sha}")

    phase1 = [p for p in patches if p.phase == 1]
    phase2 = [p for p in patches if p.phase == 2]
    active = [p for p in patches if args.phase is None or p.phase == args.phase]

    if not active:
        print(f"\n[!] No patches to apply (phase filter: {args.phase}).", file=sys.stderr)
        return

    phase2_pending = [p for p in phase2 if args.phase is None or args.phase == 2]
    if not phase2_pending and args.phase is None:
        print(f"\n[i] {len(phase1)} Phase 1 patch(es) defined.")
        print( "    Phase 2 MMIO patches: none yet — add from debug session.")
        print( "    Workflow:")
        print( "      Terminal 1: ./scripts/qemu_boot.sh --patched --debug")
        print( "      Terminal 2: r2 -a ppc -b 32 -e cfg.bigendian=true \\")
        print( "                     -D gdb gdb://localhost:1234 \\")
        print( "                     -i scripts/r2_debug.r2")
        print( "    On crash: python3 scripts/patch_firmware.py --probe 0x<PC>")
        print()

    print(f"[*] Applying {len(active)} patch(es) (phase={args.phase or 'all'})…")
    count, warnings = apply_patches(data, active, phase=args.phase)

    for w in warnings:
        print(f"  [!] {w}", file=sys.stderr)

    patched_sha = sha256_of(bytes(data))
    args.output.write_bytes(data)

    print(f"[*] Applied {count}/{len(active)} patches")
    print(f"[*] Output : {args.output}")
    print(f"    sha256: {patched_sha}")


if __name__ == "__main__":
    main()
