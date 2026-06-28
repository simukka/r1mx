#!/usr/bin/env python3
"""
callgraph.py — build a COMPLETE PPC call graph for software.bin straight from the
binary, independent of Ghidra's (incomplete) function set.

Why: Ghidra's auto-analysis only created ~10.5k functions — it misses everything
reached solely via indirect calls / function pointers / data-driven dispatch
(usrRoot, the allocator, the init dispatchers, the module inits …), so those were
never in `src/all_functions/`. But on PPC every `bl` targets a function entry, so
the set of all `bl` targets (∪ symbol-table function values) is a near-complete
function-entry list. Boundaries follow from sorting the entries; the reverse map
gives reliable callers() for climbing the call graph.

CLI:
    callgraph.py --func 0x35a9fc          # enclosing function entry
    callgraph.py --callers 0x552bf4       # direct callers of a function
    callgraph.py --climb 0x35a9fc [--depth 12]   # walk callers upward
    callgraph.py --stats
Can also be imported:  from callgraph import CallGraph
"""
import argparse, struct, bisect, os, sys

BIN = os.path.join(os.path.dirname(__file__),
                   "../reverse/build_32/extracted/software.bin")
TEXT_LO, TEXT_HI = 0x10000, 0xc00000


class CallGraph:
    def __init__(self, path=BIN):
        self.data = open(path, "rb").read()
        self.N = len(self.data)
        self._build()

    def _be(self, p):
        return struct.unpack(">I", self.data[p:p + 4])[0]

    def _symtab_funcs(self):
        """Function-entry addresses from the in-image VxWorks symbol table."""
        out = set()
        d, N = self.data, self.N
        p = 0
        while p + 0x14 <= N:
            if self._be(p + 4) == 0 and self._be(p + 0x10) == 0:
                namep = self._be(p + 8); val = self._be(p + 0xc)
                if (0xc00000 <= namep < N and d[namep - 1] == 0
                        and TEXT_LO <= val < TEXT_HI):
                    out.add(val)
            p += 4
        return out

    def _build(self):
        d = self.data
        self.callsites = []          # (site_addr, target, is_bl)
        targets_bl = set()
        for p in range(TEXT_LO, TEXT_HI, 4):
            w = struct.unpack(">I", d[p:p + 4])[0]
            if (w >> 26) == 18:                      # I-form branch (b/bl/ba/bla)
                li = w & 0x03fffffc
                if li & 0x02000000:
                    li -= 0x04000000
                tgt = (li if (w & 2) else (p + li)) & 0xffffffff
                if TEXT_LO <= tgt < TEXT_HI:
                    bl = bool(w & 1)
                    self.callsites.append((p, tgt, bl))
                    if bl:
                        targets_bl.add(tgt)
        # function entries = bl targets ∪ symtab function values
        self.entries = sorted(targets_bl | self._symtab_funcs())
        self._eidx = self.entries
        # reverse map: entry -> [caller sites] (bl only)
        self.callers_map = {}
        for site, tgt, bl in self.callsites:
            if bl:
                self.callers_map.setdefault(tgt, []).append(site)

    def func_of(self, addr):
        i = bisect.bisect_right(self._eidx, addr) - 1
        return self._eidx[i] if i >= 0 else None

    def callers(self, entry):
        """Direct-call sites whose target's enclosing function == entry."""
        # exact-entry callers plus any bl into the function body
        out = set(self.callers_map.get(entry, []))
        nxt_i = bisect.bisect_right(self._eidx, entry)
        nxt = self._eidx[nxt_i] if nxt_i < len(self._eidx) else TEXT_HI
        for tgt, sites in self.callers_map.items():
            if entry <= tgt < nxt and tgt != entry:
                out.update(sites)
        return sorted(out)

    def caller_funcs(self, entry):
        return sorted({self.func_of(s) for s in self.callers(entry)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--func", type=lambda s: int(s, 0))
    ap.add_argument("--callers", type=lambda s: int(s, 0))
    ap.add_argument("--climb", type=lambda s: int(s, 0))
    ap.add_argument("--depth", type=int, default=12)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--dump-entries", metavar="FILE",
                    help="write all function-entry addresses (one hex per line) for "
                         "seeding Ghidra (see ghidra_create_functions.py)")
    a = ap.parse_args()
    cg = CallGraph()
    if a.dump_entries:
        with open(a.dump_entries, "w") as f:
            for e in cg.entries:
                f.write(f"0x{e:08x}\n")
        print(f"wrote {len(cg.entries)} entries -> {a.dump_entries}")
    if a.stats:
        print(f"function entries (bl-targets ∪ symtab): {len(cg.entries)}  "
              f"(corpus had 10554)")
        print(f"call sites (b/bl into text): {len(cg.callsites)}")
    if a.func is not None:
        print(f"0x{a.func:08x} is in function 0x{cg.func_of(a.func):08x}")
    if a.callers is not None:
        fs = cg.func_of(a.callers)
        cf = cg.caller_funcs(fs)
        print(f"function 0x{fs:08x} <- {len(cf)} caller functions:")
        for f in cf[:40]:
            print(f"  0x{f:08x}")
    if a.climb is not None:
        cur = cg.func_of(a.climb)
        seen = set()
        for d in range(a.depth):
            cf = cg.caller_funcs(cur)
            print(f"L{d}: func 0x{cur:08x} <- {len(cf)} callers: "
                  + ", ".join(f"0x{f:08x}" for f in cf[:8]))
            if not cf or cur in seen:
                break
            seen.add(cur)
            cur = cf[0]


if __name__ == "__main__":
    main()
