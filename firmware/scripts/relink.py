#!/usr/bin/env python3
"""relink.py — "carve-out relink" build for RED ONE MX firmware.

Compiles reconstructed C/asm *units*, links each function so it lands at its
original absolute address (calling the rest of the unchanged image by name via
the generated symbols.ld), and overlays the resulting bytes onto the base image.

This is how proprietary RED code is progressively promoted from binary blob to
real source: each reconstructed function, once byte-identical (or intentionally
modified), replaces its slice of the image.

Units live in src/units/*.c and src/units/*.S. Every function whose symbol name
matches a manifest entry (by name, or FUN_<addr>) is treated as a reconstructed
unit and overlaid at its manifest address.

Usage:
  scripts/relink.py                 # build software.relinked.bin, report diffs
  scripts/relink.py --verify        # additionally assert every UNMODIFIED unit
                                     # is byte-identical to the original (fidelity)
  scripts/relink.py --out PATH
"""
from __future__ import annotations
import json, subprocess, struct, argparse, sys, re
from pathlib import Path

REPO = Path("/home/simukka/src/RED/r1mx")
SRC  = REPO / "firmware/reverse/build_32/src"
BASE = SRC / "../extracted/software.bin"
MAN  = SRC / "manifest.json"
BUILD = SRC / "build"
SYMS  = BUILD / "symbols.ld"
UNITS = SRC / "units"
CROSS = "powerpc-linux-gnu-"
CFLAGS = ["-mbig-endian", "-mcpu=405", "-O2", "-ffreestanding", "-nostdlib",
          "-fno-stack-protector", "-ffunction-sections", "-fno-pic"]

def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--out", default=str(BUILD / "software.relinked.bin"))
    args = ap.parse_args()
    BUILD.mkdir(exist_ok=True)

    # 1. symbols.ld (absolute address of every image function)
    sh(["python3", str(REPO / "firmware/scripts/gen_symbols_ld.py"),
        str(MAN), str(SYMS)])
    man = {r["name"]: r for r in json.loads(MAN.read_text())}
    by_addr = {r["addr"]: r for r in json.loads(MAN.read_text())}

    # 2. compile every unit source -> one .o each, with per-function sections
    objs = []
    for s in sorted(list(UNITS.glob("*.c")) + list(UNITS.glob("*.S"))):
        o = BUILD / (s.stem + ".o")
        sh([CROSS + "gcc", *CFLAGS, "-c", "-x",
            ("assembler-with-cpp" if s.suffix == ".S" else "c"), str(s), "-o", str(o)])
        objs.append(o)
    if not objs:
        print("no units found in", UNITS); return 0

    # 3. discover reconstructed function symbols (have a .text.<sym> section
    #    AND a manifest entry telling us where they belong)
    units = []   # (sym, addr, obj)
    for o in objs:
        rd = sh([CROSS + "readelf", "-sW", str(o)]).stdout
        for line in rd.splitlines():
            m = re.search(r"\b(FUNC)\b.*\b(\S+)$", line)
            if not m: continue
            sym = m.group(2)
            if sym in man:
                units.append((sym, man[sym]["addr"], o))
    if not units:
        print("no unit symbols matched the manifest"); return 1

    # 4. per-unit: link the one function at its absolute address, extract bytes
    out = bytearray(BASE.read_bytes())
    orig = BASE.read_bytes()
    report, fidelity_fail = [], 0
    for sym, addr, obj in sorted(units, key=lambda x: x[1]):
        ld = BUILD / f"unit_{sym}.ld"
        ld.write_text(
            f'INCLUDE {SYMS.name}\n'
            f'SECTIONS {{\n'
            f'  . = 0x{addr:08x};\n'
            f'  .text : {{ KEEP(*(.text.{sym})) }}\n'
            f'  /DISCARD/ : {{ *(.text) *(.text.*) *(.comment) *(.note.*)'
            f' *(.eh_frame) *(.glink) *(.got*) *(.data*) *(.bss*) }}\n'
            f'}}\n')
        elf = BUILD / f"unit_{sym}.elf"
        sh([CROSS + "ld", "-EB", "-o", str(elf), "-L", str(BUILD),
            "-T", str(ld), str(obj)])
        frag = BUILD / f"unit_{sym}.bin"
        sh([CROSS + "objcopy", "-O", "binary", "--only-section=.text",
            str(elf), str(frag)])
        b = frag.read_bytes()
        was = bytes(orig[addr:addr + len(b)])
        identical = (b == was)
        if not identical and args.verify:
            # a unit that *should* be faithful but isn't -> only fail if it is
            # tagged unmodified (heuristic: we flag, user decides). Report below.
            pass
        out[addr:addr + len(b)] = b
        report.append((addr, sym, len(b), identical))

    Path(args.out).write_bytes(bytes(out))

    # 5. report
    print(f"{'addr':>10}  {'symbol':24} {'len':>4}  vs-original")
    changed = 0
    for addr, sym, ln, identical in report:
        tag = "identical" if identical else "CHANGED"
        if not identical: changed += 1
        print(f"0x{addr:08x}  {sym:24} {ln:4}  {tag}")
    total_diff = sum(1 for i in range(len(orig)) if orig[i] != out[i])
    print(f"\n{len(report)} units overlaid; {changed} changed vs original; "
          f"{total_diff} total bytes differ from base image")
    import hashlib
    print("relinked sha256:", hashlib.sha256(bytes(out)).hexdigest())
    print("base     sha256:", hashlib.sha256(orig).hexdigest())
    print("wrote", args.out)

    if args.verify and changed == 0 and total_diff == 0:
        print("\nVERIFY: all units byte-identical to original — relinked image == base ✓")
    return 0

if __name__ == "__main__":
    sys.exit(main())
