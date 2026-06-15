#!/usr/bin/env python3
"""lift.py -- assemble a reconstruction packet for one firmware function.

This is the front of the Claude-in-the-loop reconstruction pipeline (plan Phase 1).
Given a function address (or FUN_ name), it gathers everything needed to rewrite that
function as readable, byte-exact C and prints it as one markdown "packet":

  * the manifest record (provenance, module, size, fidelity badge)
  * the Ghidra pseudocode (src/all_functions/0x..._*.c)
  * the original PPC405 disassembly of the function's bytes from software.bin
  * callees (bl targets) and callers (who bl's here), named via the manifest
  * referenced data: string literals + data symbols the function materializes
    (lis/addi|ori pairs), with the D_<addr> names data_symbols.ld wants
  * candidate Xilinx headers from xsrc/ when the module looks driver-shaped

With --scaffold it also writes a starter unit at src/units/<name>.c following the
doc-header standard, wired with extern decls for every callee, ready to iterate
against funcmatch.

Usage:
  firmware/scripts/lift.py 0x000af634           # print the packet
  firmware/scripts/lift.py FUN_000af634
  firmware/scripts/lift.py 0xaf634 --scaffold    # also write src/units/FUN_000af634.c
  firmware/scripts/lift.py 0xaf634 --scaffold --unit upgrade_verify.c   # append-mode name

Disassembly uses objdumpppc when present (the toolchain container), else falls back
to the host's powerpc-linux-gnu-objdump (-m powerpc:403). Pure host script: it does
NOT need the container, so it can run anywhere the repo is checked out.
"""
from __future__ import annotations
import json, struct, re, bisect, subprocess, shutil, argparse, sys
from pathlib import Path
from collections import defaultdict

REPO  = Path(__file__).resolve().parents[2]
SRC   = REPO / "firmware/reverse/build_32/src"
BASE  = REPO / "firmware/reverse/build_32/extracted/software.bin"
MAN   = SRC / "manifest.json"
FUNCS = SRC / "all_functions"
UNITS = SRC / "units"
DATA_LD = UNITS / "data_symbols.ld"
XSRC  = REPO / "firmware/reverse/build_32/xsrc"

# Executable regions of the flat image (mirrors build_provenance_map.py CODE).
CODE = [(0x000000, 0x700000), (0xE00000, 0xE8BF20)]

data = BASE.read_bytes()
N = len(data)
def u32(o): return struct.unpack_from(">I", data, o)[0]


# --- manifest + address lookups ---------------------------------------------
def load_manifest():
    recs = json.loads(MAN.read_text())
    by_addr = {r["addr"]: r for r in recs}
    by_name = {r["name"]: r for r in recs}
    by_name |= {f"FUN_{r['addr']:08x}": r for r in recs}
    starts = sorted(by_addr)
    return recs, by_addr, by_name, starts


def fn_containing(addr, by_addr, starts):
    """Manifest record whose [addr, addr+size) contains addr, or None."""
    i = bisect.bisect_right(starts, addr) - 1
    if i < 0:
        return None
    s = starts[i]
    r = by_addr[s]
    return r if s <= addr < s + max(r["size"], 4) else None


def name_at(addr, by_addr, starts):
    r = fn_containing(addr, by_addr, starts)
    if not r:
        return f"0x{addr:08x}"
    canon = f"FUN_{r['addr']:08x}"
    off = addr - r["addr"]
    suffix = f"+0x{off:x}" if off else ""
    if r["name"] and r["name"] != canon:
        return f"{r['name']}{suffix}"
    return f"{canon}{suffix}"


# --- disassembly -------------------------------------------------------------
def find_objdump():
    for tool, mach in (("objdumpppc", "powerpc:403"),
                       ("powerpc-wrs-vxworks-objdump", "powerpc:403"),
                       ("powerpc-linux-gnu-objdump", "powerpc:403"),
                       ("objdump", "powerpc:403")):
        if shutil.which(tool):
            return tool, mach
    return None, None


def disasm(addr, size):
    tool, mach = find_objdump()
    if not tool:
        return ["(no PPC objdump on PATH -- run inside the toolchain container)"]
    frag = Path("/tmp/_lift_dis.bin")
    frag.write_bytes(data[addr:addr + size])
    p = subprocess.run([tool, "-D", "-b", "binary", "-m", mach, "-EB",
                        f"--adjust-vma=0x{addr:08x}", str(frag)],
                       capture_output=True, text=True)
    rows = []
    for line in p.stdout.splitlines():
        s = line.rstrip()
        if re.match(r"\s*[0-9a-f]+:\t", s):
            rows.append(s.strip())
    return rows or ["(disassembly produced no rows)"]


# --- referenced strings / data symbols + bl call edges -----------------------
def ascii_at(addr):
    """Decode a NUL-terminated printable string at a file offset, or None."""
    if not (0 <= addr < N):
        return None
    end = addr
    while end < N and 0x20 <= data[end] < 0x7f:
        end += 1
    if end - addr >= 4 and (end >= N or data[end] == 0):
        return data[addr:end].decode("ascii")
    return None


def scan_refs(addr, size):
    """Walk a function's instructions; collect bl targets and lis+addi|ori data refs.

    Returns (callees:set[int], datarefs:list[(addr, str|None)]). Mirrors the
    materialization heuristic in build_provenance_map.py (addis rA=0 then a matching
    lo half within a short window)."""
    callees, datarefs, seen = set(), [], set()
    end = min(addr + size, N - 4)
    i = addr
    while i < end:
        w = u32(i); op = w >> 26
        if op == 18 and (w & 1):                     # bl
            li = w & 0x03FFFFFC
            if li & 0x02000000:
                li -= 0x04000000
            callees.add((i + li) & 0xFFFFFFFF)
            i += 4; continue
        if op == 15 and ((w >> 16) & 0x1F) == 0:     # lis rD,hi (addis rD,0,hi)
            rD = (w >> 21) & 0x1F; hi = w & 0xFFFF
            for j in range(i + 4, min(i + 36, end), 4):
                w2 = u32(j); op2 = w2 >> 26
                if op2 < 14:
                    continue
                if ((w2 >> 16) & 0x1F) != rD:
                    if op2 == 15 and ((w2 >> 21) & 0x1F) == rD:
                        break
                    continue
                lo = w2 & 0xFFFF
                d = ((hi << 16) | lo) if op2 == 24 else \
                    ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo))
                d &= 0xFFFFFFFF
                if d not in seen:
                    seen.add(d)
                    datarefs.append((d, ascii_at(d)))
                break
        i += 4
    return callees, datarefs


def find_callers(addr):
    """Full-image scan for bl instructions whose target is addr."""
    callers = []
    for a, b in CODE:
        for i in range(a, min(b, N) - 4, 4):
            w = u32(i)
            if (w >> 26) != 18 or not (w & 1):
                continue
            li = w & 0x03FFFFFC
            if li & 0x02000000:
                li -= 0x04000000
            if ((i + li) & 0xFFFFFFFF) == addr:
                callers.append(i)
    return callers


def ghidra_file(rec):
    canon = f"FUN_{rec['addr']:08x}"
    name = rec["name"] or canon
    for cand in (FUNCS / f"0x{rec['addr']:08x}_{name}.c",
                 FUNCS / f"0x{rec['addr']:08x}_{canon}.c"):
        if cand.exists():
            return cand
    hits = list(FUNCS.glob(f"0x{rec['addr']:08x}_*.c"))
    return hits[0] if hits else None


def xsrc_hints(module):
    """Cheap header suggestions: xsrc files whose stem appears in the module path."""
    if not module:
        return []
    tail = module.rsplit("/", 1)[-1].replace("lib", "").replace(".c", "")
    hits = []
    for p in sorted(XSRC.glob("*.h")) + sorted(XSRC.glob("*")):
        if not p.is_file():
            continue
        stem = p.stem.lstrip("x").lower()
        if stem and (stem in tail.lower() or tail.lower() in stem):
            hits.append(p.name)
    return hits[:6]


# --- packet ------------------------------------------------------------------
def build_packet(rec, by_addr, by_name, starts):
    addr, size = rec["addr"], rec["size"]
    canon = f"FUN_{addr:08x}"
    callees, datarefs = scan_refs(addr, size)
    callers = find_callers(addr)

    L = []
    w = L.append
    w(f"# Reconstruction packet -- {canon}"
      + (f"  ({rec['name']})" if rec["name"] and rec["name"] != canon else ""))
    w("")
    w(f"- **address**  0x{addr:08x}  (size {size} bytes, {size//4} insns)")
    w(f"- **provenance**  {rec.get('provenance') or 'unknown'}"
      f"  module=`{rec.get('module') or '-'}`  method={rec.get('method')}"
      f"  conf={rec.get('confidence')}")
    w(f"- **fidelity**  {rec.get('fidelity', 'raw')}"
      f"   xrefs={rec.get('xrefs')}   reconstruct={rec.get('reconstruct')}")
    w("")

    # callers / callees
    w("## Call graph")
    if callers:
        w(f"**Callers ({len(callers)}):**")
        for c in callers[:20]:
            w(f"  - 0x{c:08x}  in {name_at(c, by_addr, starts)}")
        if len(callers) > 20:
            w(f"  - ... and {len(callers)-20} more")
    else:
        w("**Callers:** none found by bl-scan (may be vtable/table-dispatched).")
    w("")
    cset = sorted(callees)
    if cset:
        w(f"**Callees ({len(cset)}):**")
        for t in cset:
            r = fn_containing(t, by_addr, starts)
            extra = ""
            if r:
                extra = f"  prov={r.get('provenance') or '?'} mod={r.get('module') or '-'}"
            w(f"  - {name_at(t, by_addr, starts):<28} 0x{t:08x}{extra}")
    else:
        w("**Callees:** none (leaf function).")
    w("")

    # referenced data / strings
    w("## Referenced data (lis/addi|ori materializations)")
    if datarefs:
        for d, s in datarefs:
            if s is not None:
                w(f"  - D_{d:08x}  =  {json.dumps(s)}")
            else:
                tgt = fn_containing(d, by_addr, starts)
                tag = f"  -> {name_at(d, by_addr, starts)}" if tgt else "  (data/BSS)"
                w(f"  - 0x{d:08x}{tag}")
        w("")
        w("> String/data addresses must be passed as linker symbols (data_symbols.ld,")
        w("> `D_<addr>`/`B_<addr>`) so ccppc emits the @ha/@l (lis/addi) pair and the")
        w("> bytes match. Already-present entries in data_symbols.ld are reused.")
    else:
        w("  (none detected)")
    w("")

    # disassembly
    w("## Original disassembly (software.bin)")
    w("```")
    for r in disasm(addr, size):
        w(r)
    w("```")
    w("")

    # ghidra pseudocode
    gf = ghidra_file(rec)
    w("## Ghidra pseudocode")
    if gf:
        w(f"`{gf.relative_to(REPO)}`")
        w("```c")
        w(gf.read_text(errors="replace").rstrip())
        w("```")
    else:
        w("(no all_functions/ file found for this address)")
    w("")

    # xsrc hints
    hints = xsrc_hints(rec.get("module"))
    if hints:
        w("## Candidate Xilinx headers (xsrc/)")
        for h in hints:
            w(f"  - xsrc/{h}")
        w("")

    return "\n".join(L), sorted(callees), datarefs


# --- scaffold ----------------------------------------------------------------
def known_data_syms():
    if not DATA_LD.exists():
        return set()
    return set(re.findall(r"\b([DB]_[0-9a-fA-F]{8})\b", DATA_LD.read_text()))


def scaffold(rec, callees, datarefs, by_addr, by_name, starts, unit_name):
    addr = rec["addr"]
    canon = f"FUN_{addr:08x}"
    path = UNITS / (unit_name or f"{canon}.c")
    if path.exists():
        return path, False

    known = known_data_syms()
    # extern decls for callees (skip self), best-effort signatures
    decls = []
    for t in callees:
        r = fn_containing(t, by_addr, starts)
        nm = (r["name"] if r and r["name"] and r["name"] != f"FUN_{r['addr']:08x}"
              else f"FUN_{t:08x}") if r else f"FUN_{t:08x}"
        if r and r["addr"] == addr:
            continue
        decls.append(f"extern int  {nm}();")
    # data symbols this fn references (so the unit author wires @ha/@l correctly)
    data_notes = []
    for d, s in datarefs:
        sym = f"D_{d:08x}"
        present = "in data_symbols.ld" if sym in known else "ADD to data_symbols.ld"
        if s is not None:
            data_notes.append(f" *   extern char {sym}[];  {json.dumps(s)}  [{present}]")

    callers = find_callers(addr)
    callee_lines = "\n".join(
        f" *     -> {name_at(t, by_addr, starts)}" for t in callees) or " *     (leaf)"

    hdr = f"""/* {path.name} -- reconstructed RED firmware function {canon}.
 *
 * Address : 0x{addr:08x}   Size: {rec['size']} bytes
 * Module  : {rec.get('module') or '(unattributed)'}   Provenance: {rec.get('provenance') or 'unknown'}
 * Fidelity: {rec.get('fidelity', 'raw')}  (target: byte_exact)
 *
 * PURPOSE: <one line -- what this function does and who relies on it>
 *
 * Reconstructed with the original compiler (ccppc 3.4.4, powerpc-wrs-vxworks);
 * verify byte-for-bit with:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py units/{path.name}
 *
 * CALL GRAPH:
 *   callers: {len(callers)}    callees:
{callee_lines}
 *
 * Image functions resolve at their absolute addresses via build/symbols.ld; data
 * (strings/tables) via units/data_symbols.ld so the @ha/@l relocations match:
{chr(10).join(data_notes) if data_notes else ' *   (no data-symbol references detected)'}
 */
"""

    body_decls = "\n".join(dict.fromkeys(decls)) or "/* leaf: no callees */"
    # Ghidra pseudocode pasted as the starting point, commented out.
    gf = ghidra_file(rec)
    ghidra = gf.read_text(errors="replace") if gf else "(no pseudocode)"
    # Escape any '*/' so the embedded pseudocode can't terminate the C block comment.
    ghidra = ghidra.replace("*/", "* /")
    ghidra_block = "\n".join(" * " + ln for ln in ghidra.splitlines())

    stub = f"""{hdr}
{body_decls}

/* TODO(reconstruct): rewrite as readable, byte-exact C. Starting point is the
 * Ghidra pseudocode below. Iterate against funcmatch until the byte diff is 0.
 *
 * --- Ghidra pseudocode -----------------------------------------------------
{ghidra_block}
 * --------------------------------------------------------------------------- */

int {canon}(void)
{{
    /* STUB -- replace with the real reconstruction. */
    return 0;
}}
"""
    path.write_text(stub)
    return path, True


def main():
    ap = argparse.ArgumentParser(description="assemble a reconstruction packet")
    ap.add_argument("target", help="function address (0x..) or FUN_ / real name")
    ap.add_argument("--scaffold", action="store_true",
                    help="also write a starter unit at src/units/<name>.c")
    ap.add_argument("--unit", default=None,
                    help="filename for the scaffolded unit (default FUN_<addr>.c)")
    args = ap.parse_args()

    recs, by_addr, by_name, starts = load_manifest()

    t = args.target
    rec = None
    if t in by_name:
        rec = by_name[t]
    else:
        try:
            a = int(t, 16) if t.lower().startswith("0x") else int(t, 16)
        except ValueError:
            print(f"error: '{t}' is neither a known name nor a hex address",
                  file=sys.stderr)
            return 2
        rec = by_addr.get(a) or fn_containing(a, by_addr, starts)
    if not rec:
        print(f"error: no manifest function for {t}", file=sys.stderr)
        return 2

    packet, callees, datarefs = build_packet(rec, by_addr, by_name, starts)
    print(packet)

    if args.scaffold:
        path, created = scaffold(rec, callees, datarefs,
                                 by_addr, by_name, starts, args.unit)
        rel = path.relative_to(REPO)
        if created:
            print(f"\n[scaffold] wrote {rel}", file=sys.stderr)
        else:
            print(f"\n[scaffold] {rel} already exists -- left untouched",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
