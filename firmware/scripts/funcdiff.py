#!/usr/bin/env python3
"""funcdiff.py -- behavioural differential test: original vs reconstructed function.

The functional-equivalence validator that pairs with funcmatch. When a reconstruction
isn't byte-identical (a `draft`/`functional` unit), this proves it *behaves* the same
as the original by running BOTH in the r1mx QEMU over the GDB stub and comparing
outputs -- promoting the function from `draft` to `functional` fidelity.

Method, per test vector: halt the target, write the input registers + input memory,
point PC at the function with LR set to a sentinel return (a hardware breakpoint),
run to that breakpoint, and capture the requested output register(s) and memory
region(s). Do it once with the ORIGINAL image bytes in place, once with the
reconstructed bytes overlaid at the function's address, then diff.

  - PURE / leaf functions (e.g. memcmp at 0x39ac2c): fully handled here.
  - STATEFUL functions (call into the image, touch globals): the call setup is the
    same, but compare the whole execution with lockstep_diff.py instead.

REQUIRES A RUNNING TARGET (the end-to-end step). Boot QEMU with the gdbstub:
    firmware/scripts/qemu_boot.sh --debug          # original image, stub on :1234
Writes (scratch memory, registers, the overlay) need allow_write, so this is
QEMU-ONLY by default -- it never patches the live camera (see rsp.py read-only rules).
For byte_exact functions funcdiff is unnecessary (identical bytes => identical behaviour).

Usage:
  funcdiff.py --func 0x0039ac2c --unit units/libc_leaves.c --ret 0x4 \
      --set r3=0x200000 r4=0x200010 r5=8 \
      --mem 0x200000=0011223344556677 --mem 0x200010=0011223344556688 \
      --out r3
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funcmatch as fm
from rsp import RSP


def recon_bytes(unit: Path, func_addr: int) -> bytes:
    """Compile+link the unit with the original compiler and return the reconstructed
    bytes for the function at func_addr (reuses funcmatch's build path)."""
    fm.ensure_wind_base()
    fm.BUILD.mkdir(exist_ok=True)
    fm.gen_symbols()
    if fm.DATA_LD.exists():
        shutil.copy(fm.DATA_LD, fm.BUILD / fm.DATA_LD.name)
    man = fm.load_manifest()
    work = fm.BUILD / "funcdiff"; work.mkdir(exist_ok=True)
    for sym, addr, ln, ident, orig, got in fm.match_unit(
            unit, fm.DEFAULT_CFLAGS, man, fm.detect_machine(), set(), work):
        if addr == func_addr:
            return got
    raise SystemExit(f"no function at 0x{func_addr:08x} defined in {unit}")


def run_once(t: RSP, func: int, ret: int, ins: dict, mems: dict,
             outs: list, outmems: list, install: bytes = None, restore: bytes = None):
    """Set up state, run the function once, capture outputs. If `install` is given,
    overlay it at `func` first and `restore` the original bytes afterwards."""
    t.interrupt()
    if install is not None:
        t.write_mem(func, install)
    for a, h in mems.items():
        t.write_mem(a, bytes.fromhex(h))
    for r, v in ins.items():
        t.write_reg(r, v)
    t.write_reg("lr", ret)
    t.write_reg("pc", func)
    regs = t.run_to(ret)
    out_reg = {r: regs.get(r) for r in outs}
    out_mem = {f"0x{a:08x}:{n}": t.read_mem(a, n).hex() for a, n in outmems}
    if install is not None and restore is not None:
        t.write_mem(func, restore)
    return out_reg, out_mem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="127.0.0.1:1234", help="host:port of the gdbstub")
    ap.add_argument("--func", required=True, help="function address (hex)")
    ap.add_argument("--unit", required=True, help="src/units/*.c defining it")
    ap.add_argument("--ret", default="0x4", help="sentinel return address (hw bp)")
    ap.add_argument("--set", dest="ins", nargs="*", default=[], help="rN=val inputs")
    ap.add_argument("--mem", action="append", default=[], help="addr=hexbytes input memory")
    ap.add_argument("--out", nargs="*", default=["r3"], help="output registers to compare")
    ap.add_argument("--out-mem", dest="outmem", action="append", default=[],
                    help="addr:len output memory regions to compare")
    a = ap.parse_args()

    func, ret = int(a.func, 0), int(a.ret, 0)
    ins = {k: int(v, 0) for k, v in (s.split("=") for s in a.ins)}
    mems = {int(k, 0): v for k, v in (s.split("=") for s in a.mem)}
    outmems = [(int(x, 0), int(n, 0)) for x, n in (s.split(":") for s in a.outmem)]
    host, port = a.target.split(":")

    got = recon_bytes(Path(a.unit), func)

    t = RSP(host, int(port), allow_write=True, label="qemu").connect()
    t.interrupt()
    orig = t.read_mem(func, len(got))
    print(f"func 0x{func:08x}  ({len(got)} bytes)")
    print(f"  original : {orig.hex()}")
    print(f"  recon    : {got.hex()}"
          + ("   (byte-identical -- funcdiff trivial)" if got == orig else ""))

    o_reg, o_mem = run_once(t, func, ret, ins, mems, a.out, outmems)
    r_reg, r_mem = run_once(t, func, ret, ins, mems, a.out, outmems, install=got, restore=orig)
    t.detach(); t.close()

    same = (o_reg == r_reg and o_mem == r_mem)
    print(f"\n  {'output':<14} {'original':<18} reconstructed")
    for r in a.out:
        d = "" if o_reg[r] == r_reg[r] else "  <-- DIFF"
        print(f"  {r:<14} {o_reg[r]!s:<18} {r_reg[r]!s}{d}")
    for k in o_mem:
        d = "" if o_mem[k] == r_mem[k] else "  <-- DIFF"
        print(f"  {k:<14} {o_mem[k]:<18} {r_mem[k]}{d}")
    print("\nfuncdiff:", "EQUIVALENT" if same else "DIFFERENT")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
