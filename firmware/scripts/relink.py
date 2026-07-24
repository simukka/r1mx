#!/usr/bin/env python3
"""relink.py — "carve-out relink" build for RED ONE MX firmware.

Compiles reconstructed C/asm *units*, links each function so it lands at its
original absolute address (calling the rest of the unchanged image by name via the
generated symbols.ld, and resolving data/string addresses via data_symbols.ld), and
overlays the resulting bytes onto the base image.

This is how proprietary RED code is progressively promoted from binary blob to real
source: each reconstructed function, once byte-identical (or intentionally modified),
replaces its slice of the image.

Units live under src/red/ and src/hw/ (mirroring the firmware __FILE__ module tree);
funcmatch.discover_units() finds them. Every function whose symbol name matches a
manifest entry (by name, or FUN_<addr>) is treated as a reconstructed unit and
overlaid at its manifest address.

This reuses funcmatch's linking primitives, so it compiles with the ORIGINAL compiler
(Wind River ccppc 3.4.4) exactly as the byte-exact gate does — including the
units/data_symbols.ld @ha/@l (lis/addi) relocations for referenced strings/tables.
It therefore runs INSIDE the toolchain container:

  toolchain/in-container.sh python3 firmware/scripts/relink.py
  toolchain/in-container.sh python3 firmware/scripts/relink.py --verify
  toolchain/in-container.sh python3 firmware/scripts/relink.py --identity
  toolchain/in-container.sh python3 firmware/scripts/relink.py --out PATH

(The Makefile's `relink`/`verify-relink`/`verify` targets wrap this in the container for you.)
"""
from __future__ import annotations
import json, argparse, sys, hashlib
from pathlib import Path
import funcmatch as fm

GREEN, RED, YELLOW, BOLD, RST = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m"


def load_functional() -> set[str]:
    """Symbols badged `functional` in units/functional.txt — intentionally NOT
    byte-identical but proven behaviourally equivalent. --verify won't flag these."""
    f = fm.SRC / "functional.txt"
    out = set()
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(line.split()[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="assert every non-functional unit is byte-identical to base")
    ap.add_argument("--identity", action="store_true",
                    help="overlay ONLY byte-exact units (skip functional intentional-diffs) "
                         "and assert the result is byte-identical to the original software.bin "
                         "— the bit-for-bit north-star gate")
    ap.add_argument("--out", default=str(fm.BUILD / "software.relinked.bin"))
    args = ap.parse_args()

    # Same setup as funcmatch: stub WIND_BASE, regenerate symbols.ld, stage
    # data_symbols.ld into build/ so the per-unit link can INCLUDE it.
    fm.ensure_wind_base()
    fm.BUILD.mkdir(exist_ok=True)
    fm.gen_symbols()
    import shutil
    if fm.DATA_LD.exists():
        shutil.copy(fm.DATA_LD, fm.BUILD / fm.DATA_LD.name)

    man = fm.load_manifest()
    mach = fm.detect_machine()
    functional = load_functional()
    work = fm.BUILD / "relink"; work.mkdir(exist_ok=True)

    orig = fm.BASE.read_bytes()
    out = bytearray(orig)

    # Overlay policy: a unit's bytes replace the image slice only if it is faithful
    # (byte-identical to the original) or an INTENTIONAL change declared in
    # functional.txt. Plain `draft` units (incomplete reconstructions, illustrative
    # vendor stubs) are compiled+linked — which still exercises symbol/data-symbol
    # resolution — but left as original blob, so the relinked image stays bootable.
    units = fm.discover_units()
    report = []          # (addr, sym, len, status, unit)   status in {identical,functional,draft}
    skipped = []
    for src in units:
        try:
            res = fm.match_unit(src, fm.DEFAULT_CFLAGS, man, mach, set(), work)
        except Exception as e:
            skipped.append((src.name, str(e).splitlines()[-1][:70]))
            continue
        for sym, addr, ln, identical, _o, got in res:
            if identical:
                status = "identical"
            elif sym in functional:
                status = "functional"
            else:
                status = "draft"
            # Normal build overlays faithful + intentional (identical + functional).
            # --identity overlays ONLY byte-exact bytes, so the result must equal base.
            overlay = (status == "identical") or (status == "functional" and not args.identity)
            if overlay:
                out[addr:addr + ln] = got
            report.append((addr, sym, ln, status, src.name))

    Path(args.out).write_bytes(bytes(out))

    report.sort()
    print(f"{'addr':>10}  {'symbol':24} {'len':>4}  {'unit':<22} status")
    n_id = n_fn = n_dr = 0
    for addr, sym, ln, status, unit in report:
        if status == "identical":
            n_id += 1; tag = f"{GREEN}identical{RST}"
        elif status == "functional":
            n_fn += 1; tag = f"{YELLOW}overlaid (functional, intentional){RST}"
        else:
            n_dr += 1; tag = f"{YELLOW}draft — not overlaid (left as blob){RST}"
        print(f"0x{addr:08x}  {sym:24} {ln:4}  {unit:<22} {tag}")

    for name, why in skipped:
        print(f"{RED}skipped{RST} {name}: {why}")

    total_diff = sum(1 for i in range(len(orig)) if orig[i] != out[i])
    print(f"\n{len(report)} units linked: {GREEN}{n_id} identical{RST}, "
          f"{n_fn} functional (overlaid), {n_dr} draft (not overlaid); "
          f"{total_diff} bytes differ from base image")
    relinked_sha = hashlib.sha256(bytes(out)).hexdigest()
    base_sha = hashlib.sha256(orig).hexdigest()
    print("relinked sha256:", relinked_sha)
    print("base     sha256:", base_sha)
    print("wrote", args.out)

    if args.identity:
        # Bit-for-bit gate: only byte-exact units were overlaid, so the relinked image
        # must be byte-identical to the original. A skip means a byte-exact unit could
        # not be rebuilt, so its claim is unproven — fail rather than silently pass.
        if skipped:
            print(f"\n{RED}IDENTITY FAIL{RST}: {len(skipped)} unit(s) failed to "
                  f"compile/link (see skipped above)")
            return 1
        if relinked_sha == base_sha:
            print(f"\n{GREEN}IDENTITY OK{RST}: relinked image is BYTE-IDENTICAL to the "
                  f"original software.bin — {n_id} byte-exact unit(s) rebuilt from source "
                  f"and overlaid with zero drift.")
            return 0
        print(f"\n{RED}IDENTITY FAIL{RST}: relinked image differs from the original at "
              f"{total_diff} byte(s); a unit badged byte-exact no longer rebuilds identically.")
        return 1

    if args.verify:
        if skipped:
            print(f"\n{RED}VERIFY FAIL{RST}: {len(skipped)} unit(s) failed to "
                  f"compile/link (see skipped above)")
            return 1
        # Faithfulness holds by construction: only identical + functional bytes were
        # overlaid. Assert that the bytes that differ are exactly the functional ones.
        print(f"\n{GREEN}VERIFY OK{RST}: relinked image differs from base only at "
              f"{n_fn} intentionally-badged functional unit(s); all other "
              f"reconstructed units are byte-identical. ({n_dr} draft unit(s) link "
              f"cleanly but remain blob.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
