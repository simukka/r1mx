#!/usr/bin/env python3
"""funcmatch.py — does reconstructed C compile to the ORIGINAL firmware bytes?

This is the byte-for-bit gate for the carve-out reconstruction. It compiles a unit
with the *original* compiler — Wind River GNU GCC 3.4.4, target powerpc-wrs-vxworks,
the one that built Build 32 (see ../reverse/build_32/toolchain/README.md) — links each
function at its original absolute address (reusing the manifest + symbols.ld exactly
like relink.py), extracts its bytes, and compares them against software.bin. On a
mismatch it prints a side-by-side disassembly and the first diverging instruction, so
the C can be massaged until it matches (decomp.me / asm-differ style).

Runs INSIDE the toolchain container, where ccppc/ldppc/objcopyppc/objdumpppc/readelfppc
are on PATH:

    toolchain/in-container.sh python3 firmware/scripts/funcmatch.py UNIT.c [UNIT2.c ...]
    toolchain/in-container.sh python3 firmware/scripts/funcmatch.py --only FUN_000000ac UNIT.c
    toolchain/in-container.sh python3 firmware/scripts/funcmatch.py --cflags "-mcpu=405 -O1" UNIT.c
    toolchain/in-container.sh python3 firmware/scripts/funcmatch.py --sweep UNIT.c   # find best flags

Exit code is the number of functions that did NOT match (0 == all matched), so it
doubles as a CI check.
"""
from __future__ import annotations
import json, subprocess, argparse, sys, os, tempfile, shutil
from pathlib import Path

REPO  = Path(__file__).resolve().parents[2]
SRC   = REPO / "firmware/reverse/build_32/src"
BASE  = REPO / "firmware/reverse/build_32/extracted/software.bin"
MAN   = SRC / "manifest.json"
BUILD = SRC / "build"
SYMS  = BUILD / "symbols.ld"
# Optional hand-maintained absolute addresses of DATA symbols (strings, tables, BSS
# objects) referenced by units, so @ha/@l (lis/addi) relocations match the original.
DATA_LD = SRC / "data_symbols.ld"

# Reconstructed units live under these roots, mirroring the firmware __FILE__ module
# tree (src/red/<module>/…, src/hw/…). discover_units() finds them for relink/recon.
UNIT_ROOTS = [SRC / "red", SRC / "hw"]
_UNIT_EXCLUDE = {"include", "ghidra", "build"}


def discover_units():
    """Every reconstructed byte-match unit: *.c/*.S under src/red + src/hw.
    C++ TUs (*.cpp, e.g. flashvx.cpp) live in the tree for clangd navigation but are
    NOT byte-gated yet — add "*.cpp" here once a C++ unit reaches byte_exact/functional
    (until then including it would trip relink --verify's skip==0 invariant)."""
    found = []
    for root in UNIT_ROOTS:
        if not root.exists():
            continue
        for pat in ("*.c", "*.S"):
            for p in root.rglob(pat):
                if not any(part in _UNIT_EXCLUDE for part in p.relative_to(SRC).parts):
                    found.append(p)
    return sorted(set(found))

# The flag set that reproduces the mmio_leaves accessors byte-for-bit; the sweep can
# refine it for harder functions. Kept in sync with toolchain/toolchain.mk.
DEFAULT_CFLAGS = "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic"

# Candidate flag sets tried by --sweep (first column is a short label).
SWEEP_GRID = [
    ("O2",            "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic"),
    ("O2-strict",     "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic -mstrict-align"),
    ("O2-noschedp",   "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic -mno-sched-prolog"),
    ("Os",            "-mcpu=405 -Os -ffreestanding -ffunction-sections -fno-pic"),
    ("O1",            "-mcpu=405 -O1 -ffreestanding -ffunction-sections -fno-pic"),
    ("O2-eabi",       "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic -meabi -msdata=none"),
    ("O2-fnocommon",  "-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic -fno-common"),
]

GREEN, RED, DIM, BOLD, RST = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"


def run(cmd, ok=(0,)):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode not in ok:
        raise RuntimeError(f"$ {' '.join(map(str,cmd))}\n{p.stdout}{p.stderr}")
    return p


def ensure_wind_base():
    """The Wind River driver aborts if WIND_BASE is unset (header spec calls
    getenv(WIND_BASE /target/h)). A stub satisfies it for freestanding compiles."""
    if not os.environ.get("WIND_BASE"):
        stub = Path(tempfile.gettempdir()) / "wb_stub"
        (stub / "target" / "h").mkdir(parents=True, exist_ok=True)
        os.environ["WIND_BASE"] = str(stub)


def load_manifest():
    recs = json.loads(MAN.read_text())
    return {r["name"]: r for r in recs} | {f"FUN_{r['addr']:08x}": r for r in recs}


def gen_symbols():
    run([sys.executable, str(REPO / "firmware/scripts/gen_symbols_ld.py"),
         str(MAN), str(SYMS)])


def detect_machine():
    """objdump bfd machine name that this (2003 Wind River) binutils accepts for PPC405."""
    sample = BASE.read_bytes()[0xac:0xb8]
    f = BUILD / "_mach_probe.bin"; f.write_bytes(sample)
    for m in ("powerpc:403", "powerpc:common", "powerpc"):
        p = subprocess.run(["objdumpppc", "-D", "-b", "binary", "-m", m, "-EB", str(f)],
                           capture_output=True, text=True)
        if p.returncode == 0 and "eieio" in p.stdout:
            return m
    return "powerpc:403"


def compile_unit(src: Path, cflags: str, work: Path) -> Path:
    obj = work / (src.stem + ".o")
    lang = "assembler-with-cpp" if src.suffix == ".S" else "c"
    run(["ccppc", *cflags.split(), "-c", "-x", lang, str(src), "-o", str(obj)])
    return obj


def defined_funcs(obj: Path, man: dict) -> list[str]:
    out = run(["readelfppc", "-sW", str(obj)]).stdout
    syms = []
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 8 and p[3] == "FUNC" and p[6] != "UND":
            name = p[7].split("@")[0]
            if name in man:
                syms.append(name)
    return sorted(set(syms))


def link_placed(obj: Path, placed: list, work: Path) -> Path:
    """Link the object ONCE with every reconstructed function placed at its absolute
    address, so a function that calls a sibling in the same file resolves correctly
    (and isn't shadowed by a discarded local definition). External refs come from
    symbols.ld / data_symbols.ld. Returns the linked ELF."""
    secs = "\n".join(f"  .text.{s} 0x{a:08x} : {{ KEEP(*(.text.{s})) }}" for s, a in placed)
    includes = f"INCLUDE {SYMS.name}\n"
    if (BUILD / DATA_LD.name).exists():
        includes += f"INCLUDE {DATA_LD.name}\n"
    ld = work / f"{obj.stem}.ld"
    ld.write_text(
        includes +
        f"SECTIONS {{\n{secs}\n"
        f"  /DISCARD/ : {{ *(.text) *(.text.*) *(.comment) *(.note.*) *(.eh_frame)"
        f" *(.glink) *(.got*) *(.data*) *(.bss*) *(.rela*) *(.sdata*) *(.PPC.*) }}\n}}\n")
    elf = work / f"{obj.stem}.elf"
    run(["ldppc", "-EB", "-o", str(elf), "-L", str(BUILD), "-T", str(ld), str(obj)])
    return elf


def extract_section(elf: Path, sym: str, work: Path) -> bytes:
    frag = work / f"x_{sym}.bin"
    run(["objcopyppc", "-O", "binary", f"--only-section=.text.{sym}", str(elf), str(frag)])
    return frag.read_bytes()


def disasm(data: bytes, addr: int, mach: str, work: Path, tag: str) -> list[str]:
    f = work / f"_dis_{tag}.bin"; f.write_bytes(data)
    p = subprocess.run(["objdumpppc", "-D", "-b", "binary", "-m", mach, "-EB",
                        f"--adjust-vma=0x{addr:08x}", str(f)], capture_output=True, text=True)
    rows = []
    for line in p.stdout.splitlines():
        s = line.strip()
        if ":" in s and "\t" in s:           # "  ac:\t7c 00 06 ac \teieio"
            rows.append(s)
    return rows


def show_diff(orig: bytes, got: bytes, addr: int, mach: str, work: Path):
    o = disasm(orig, addr, mach, work, "orig")
    g = disasm(got,  addr, mach, work, "recon")
    first = next((i for i in range(min(len(orig), len(got))) if orig[i] != got[i]),
                 min(len(orig), len(got)))
    print(f"    first divergence at +0x{first:x} (0x{addr+first:08x})")
    print(f"    {'ORIGINAL':<40}  RECONSTRUCTED")
    for i in range(max(len(o), len(g))):
        ol = o[i] if i < len(o) else ""
        gl = g[i] if i < len(g) else ""
        mark = "  " if ol == gl else f"{RED}!!{RST}"
        print(f"  {mark}{ol:<40}  {gl}")


def match_unit(src: Path, cflags: str, man: dict, mach: str, only: set[str], work: Path):
    obj = compile_unit(src, cflags, work)
    # Place ALL of the file's reconstructed functions (so intra-file calls link), but
    # only report the ones requested.
    placed = [(s, man[s]["addr"]) for s in defined_funcs(obj, man)]
    if not placed:
        return []
    elf = link_placed(obj, placed, work)
    results = []
    for sym, addr in sorted(placed, key=lambda x: x[1]):
        if only and sym not in only:
            continue
        got = extract_section(elf, sym, work)
        orig = BASE.read_bytes()[addr:addr + len(got)]
        results.append((sym, addr, len(got), got == orig, orig, got))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("units", nargs="+", help="unit source(s) under src/red|src/hw to check")
    ap.add_argument("--only", action="append", default=[], help="restrict to these symbols")
    ap.add_argument("--cflags", default=DEFAULT_CFLAGS)
    ap.add_argument("--sweep", action="store_true", help="try the flag grid, report best")
    args = ap.parse_args()

    ensure_wind_base()
    BUILD.mkdir(exist_ok=True)
    gen_symbols()
    if DATA_LD.exists():
        shutil.copy(DATA_LD, BUILD / DATA_LD.name)
    man = load_manifest()
    mach = detect_machine()
    only = set(args.only)
    units = [Path(u) for u in args.units]
    work = BUILD / "funcmatch"; work.mkdir(exist_ok=True)

    if args.sweep:
        print(f"{BOLD}flag sweep over {len(units)} unit(s){RST}  (machine={mach})\n")
        print(f"  {'label':<14} {'flags':<62} matched")
        best = None
        for label, cflags in SWEEP_GRID:
            n_ok = n_tot = 0
            try:
                for src in units:
                    for _s, _a, _l, ident, _o, _g in match_unit(src, cflags, man, mach, only, work):
                        n_tot += 1; n_ok += int(ident)
            except RuntimeError as e:
                print(f"  {label:<14} {cflags:<62} ERROR ({str(e).splitlines()[-1][:30]})")
                continue
            tag = GREEN if n_ok == n_tot else ""
            print(f"  {tag}{label:<14} {cflags:<62} {n_ok}/{n_tot}{RST}")
            if best is None or n_ok > best[2]:
                best = (label, cflags, n_ok, n_tot)
        if best:
            print(f"\n  best: {BOLD}{best[0]}{RST} ({best[2]}/{best[3]}) -> {best[1]}")
        return 0

    print(f"{BOLD}funcmatch{RST}  compiler=ccppc-3.4.4  machine={mach}")
    print(f"flags: {args.cflags}\n")
    nfail = 0
    for src in units:
        res = match_unit(src, args.cflags, man, mach, only, work)
        if not res:
            print(f"{src.name}: no manifest-known functions defined"); continue
        for sym, addr, ln, ident, orig, got in res:
            if ident:
                print(f"  {GREEN}● byte-exact{RST}  0x{addr:08x}  {sym:24} ({ln} B)")
            else:
                nfail += 1
                neq = sum(a == b for a, b in zip(orig, got))
                print(f"  {RED}✗ MISMATCH{RST}   0x{addr:08x}  {sym:24} "
                      f"({neq}/{ln} bytes, {100*neq//max(ln,1)}%)")
                show_diff(orig, got, addr, mach, work)
    tot = sum(len(match_unit(Path(u), args.cflags, man, mach, only, work)) for u in args.units)
    print(f"\n{tot-nfail}/{tot} functions byte-exact"
          + (f"  {RED}({nfail} to fix){RST}" if nfail else f"  {GREEN}✓{RST}"))
    return nfail


if __name__ == "__main__":
    sys.exit(main())
