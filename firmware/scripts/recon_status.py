#!/usr/bin/env python3
"""recon_status.py -- reconstruction coverage dashboard.

Rebuilds every function in src/units/ with the ORIGINAL compiler (via funcmatch) and
reports how much of the firmware is reconstructed and at what fidelity:

  byte_exact  rebuilds to the original firmware bytes (funcmatch 100%) -- verified
  draft       reconstructed C that compiles + links but isn't byte-identical yet
              (match% shown); behavioural validation (funcdiff) promotes it to
              `functional`
  raw         still only Ghidra pseudocode (the rest of the image)

Writes src/recon_status.json, which build_provenance_map.py merges into each manifest
record's `fidelity` field. Run inside the toolchain container:

  toolchain/in-container.sh python3 firmware/scripts/recon_status.py
"""
from __future__ import annotations
import json, shutil, datetime, sys
from pathlib import Path
import funcmatch as fm

G, R, Y, B, Z = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m"


def main():
    fm.ensure_wind_base()
    fm.BUILD.mkdir(exist_ok=True)
    fm.gen_symbols()
    if fm.DATA_LD.exists():
        shutil.copy(fm.DATA_LD, fm.BUILD / fm.DATA_LD.name)

    recs = json.loads(fm.MAN.read_text())
    by_name = {r["name"]: r for r in recs}
    man = fm.load_manifest()
    mach = fm.detect_machine()
    work = fm.BUILD / "recon"; work.mkdir(exist_ok=True)

    units = sorted(list(fm.UNITS.glob("*.c")) + list(fm.UNITS.glob("*.S")))
    funcs = []
    for src in units:
        try:
            res = fm.match_unit(src, fm.DEFAULT_CFLAGS, man, mach, set(), work)
        except Exception as e:
            print(f"  {R}skip{Z} {src.name}: {str(e).splitlines()[-1][:70]}")
            continue
        for sym, addr, ln, ident, orig, got in res:
            neq = sum(a == b for a, b in zip(orig, got))
            pct = 100 * neq // max(ln, 1)
            r = by_name.get(sym, {})
            funcs.append(dict(name=sym, addr=f"0x{addr:08x}", size=ln,
                              provenance=r.get("provenance") or "?",
                              module=r.get("module") or "", match=pct,
                              fidelity=("byte_exact" if ident else "draft"),
                              unit=src.name))
    funcs.sort(key=lambda f: (f["unit"], int(f["addr"], 16)))

    nbe = sum(1 for f in funcs if f["fidelity"] == "byte_exact")
    ndr = len(funcs) - nbe
    red_total = sum(1 for r in recs if r["provenance"] == "red")
    red_done = sum(1 for f in funcs if f["provenance"] == "red")

    print(f"\n{B}=== reconstruction status ==={Z}  "
          f"({len(funcs)} functions across {len(units)} unit files)\n")
    print(f"  {'addr':>10}  {'fidelity':<10} {'match':>5}  {'prov':<8} "
          f"{'module':<20} {'unit':<18} name")
    for f in funcs:
        col = G if f["fidelity"] == "byte_exact" else Y
        m = "100%" if f["fidelity"] == "byte_exact" else f"{f['match']}%"
        print(f"  {f['addr']}  {col}{f['fidelity']:<10}{Z} {m:>5}  "
              f"{f['provenance']:<8} {(f['module'] or '-'):<20} {f['unit']:<18} {f['name']}")

    print(f"\n  {B}byte_exact{Z} {G}{nbe}{Z}   {B}draft{Z} {Y}{ndr}{Z}   "
          f"reconstructed total {len(funcs)} / {len(recs)} image fns")
    print(f"  RED-provenance reconstructed: {red_done}/{red_total} "
          f"({100*red_done//max(red_total,1)}%)"
          f"   (other-provenance reconstructed: {len(funcs)-red_done})")

    out = fm.SRC / "recon_status.json"
    out.write_text(json.dumps(dict(
        generated=datetime.datetime.now().isoformat(timespec="seconds"),
        summary=dict(reconstructed=len(funcs), byte_exact=nbe, draft=ndr,
                     red_total=red_total, red_reconstructed=red_done),
        functions=funcs), indent=1))
    print(f"\n  wrote {out.relative_to(fm.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
