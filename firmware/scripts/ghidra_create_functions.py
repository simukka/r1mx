#!/usr/bin/env python3
"""
ghidra_create_functions.py — seed Ghidra with the function entries it missed.

Ghidra's auto-analysis only created ~10.5k functions for software.bin; ~5k more
exist but are reached only via indirect calls / function pointers / data-driven
dispatch (usrRoot, the allocator, init dispatchers, module inits …), so Ghidra
never made them functions and `ghidra_decompile_all.py` couldn't export them.

This script reads the complete entry list produced by
    python3 callgraph.py --dump-entries /tmp/r1mx_entries.txt
(every `bl` target in .text ∪ symbol-table function values) and, for each address
that isn't already inside a function, disassembles + creates a function there.
Run it BEFORE ghidra_decompile_all.py so the export is complete.

Usage (headless):
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \\
    analyzeHeadless <repo>/firmware/reverse r1mx \\
        -process software.bin \\
        -preScript ghidra_create_functions.py /tmp/r1mx_entries.txt \\
        -scriptPath <repo>/firmware/scripts \\
        -noanalysis
  (then re-run ghidra_decompile_all.py as the postScript / separately)

Or standalone via pyghidra (mirrors ghidra_decompile_all.py's bootstrap).
"""
import os
import sys

_STANDALONE = "currentProgram" not in dir()
if _STANDALONE:
    import pyghidra
    _GHIDRA_HOME = os.environ.get(
        "GHIDRA_INSTALL_DIR", os.path.expanduser("~/Downloads/ghidra_12.0.4_PUBLIC"))
    _REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    pyghidra.start(install_dir=_GHIDRA_HOME)
    from pyghidra import open_project
    _ctx = open_project(os.path.join(_REPO, "reverse"), "r1mx")
    _project = _ctx.__enter__()
    _f = _project.getProjectData().getRootFolder().getFile("software.bin")
    currentProgram = _f.getDomainObject("pyghidra_create_functions", True, False, None)

from ghidra.program.flatapi import FlatProgramAPI
from ghidra.program.model.address import AddressSet

flat = FlatProgramAPI(currentProgram)
fm = currentProgram.getFunctionManager()
af = flat.getMonitor() if hasattr(flat, "getMonitor") else None


def _entries_path():
    # script args: getScriptArgs() under analyzeHeadless; argv otherwise
    try:
        args = getScriptArgs()  # noqa: F821  (injected by Ghidra)
        if args:
            return args[0]
    except Exception:
        pass
    for a in sys.argv[1:]:
        if a.endswith(".txt"):
            return a
    return "/tmp/r1mx_entries.txt"


def run():
    path = _entries_path()
    addrs = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                addrs.append(int(line, 16))
    print("seeding %d candidate entries from %s" % (len(addrs), path))
    af_space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    created = skipped = failed = 0
    for i, a in enumerate(addrs):
        ga = af_space.getAddress(a)
        if fm.getFunctionContaining(ga) is not None:
            skipped += 1
            continue
        try:
            if flat.getInstructionAt(ga) is None:
                flat.disassemble(ga)
            fn = flat.createFunction(ga, None)  # default name FUN_xxxxxxxx
            if fn is not None:
                created += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        if (i + 1) % 500 == 0:
            print("  ... %d/%d (created=%d skipped=%d failed=%d)"
                  % (i + 1, len(addrs), created, skipped, failed))
    print("DONE: created=%d skipped(existing)=%d failed=%d" % (created, skipped, failed))
    if _STANDALONE:
        # save so the new functions persist for the decompile export
        _f.save("seed functions from callgraph bl-targets", None)


run()
