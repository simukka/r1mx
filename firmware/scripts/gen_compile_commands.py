#!/usr/bin/env python3
"""gen_compile_commands.py -- emit compile_commands.json for clangd.

Walks the reconstructed source under src/red + src/hw and writes
src/compile_commands.json using the ORIGINAL toolchain flags (parsed from
toolchain/toolchain.mk: WR_CFLAGS for C, WR_CXXFLAGS for C++) plus -I src/include.

This is a pure HOST script (no container): it only produces an editor index so clangd
can navigate and type-check the units. The byte-for-bit build still uses the original
ccppc. The generated file has machine-specific absolute paths and is gitignored;
src/.clangd adapts clang's PPC frontend to the GCC-3.4.4 flags. Run via
`make -C firmware/reverse/build_32/src compile-commands`.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO    = Path(__file__).resolve().parents[2]
SRC     = REPO / "firmware/reverse/build_32/src"
INCLUDE = SRC / "include"
TC_MK   = REPO / "firmware/reverse/build_32/toolchain/toolchain.mk"
ROOTS   = [SRC / "red", SRC / "hw"]
OUT     = SRC / "compile_commands.json"


def read_toolchain_flags() -> tuple[list[str], list[str]]:
    """Parse WR_CFLAGS / WR_CXXFLAGS from toolchain.mk (the single source of truth), so
    the editor index and the container build never drift apart."""
    text = TC_MK.read_text()
    vals: dict[str, str] = {}
    for name in ("WR_CFLAGS", "WR_CXXFLAGS"):
        m = re.search(rf"^\s*{name}\s*:?=\s*(.*)$", text, re.M)
        vals[name] = m.group(1).strip() if m else ""
    # expand a $(WR_CFLAGS) reference inside WR_CXXFLAGS
    vals["WR_CXXFLAGS"] = vals["WR_CXXFLAGS"].replace("$(WR_CFLAGS)", vals["WR_CFLAGS"]).strip()
    return vals["WR_CFLAGS"].split(), vals["WR_CXXFLAGS"].split()


def main() -> int:
    cflags, cxxflags = read_toolchain_flags()
    inc = ["-I", str(INCLUDE)]
    entries = []
    for root in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.suffix == ".c":
                driver, flags = "clang", cflags
            elif p.suffix in (".cpp", ".cc", ".cxx"):
                driver, flags = "clang++", cxxflags
            else:
                continue
            entries.append({
                "directory": str(SRC),
                "file": str(p),
                "arguments": [driver, *flags, *inc, "-c", str(p)],
            })
    OUT.write_text(json.dumps(entries, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}  ({len(entries)} translation units)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
