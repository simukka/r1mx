"""
ghidra_batch_decompile_region.py -- Batch decompile all functions in a code region.

Decompiles every function Ghidra knows about in the specified range,
writing each to a separate .c file. Useful for understanding a module
before we have full symbol names.

Usage:
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
    DECOMPILE_START=0x1e000 DECOMPILE_END=0x40000 \
    python3 firmware/scripts/ghidra_batch_decompile_region.py
"""

import os, sys

_STANDALONE = "currentProgram" not in dir()

if _STANDALONE:
    import pyghidra

    _GHIDRA_HOME = os.environ.get(
        "GHIDRA_INSTALL_DIR",
        os.path.expanduser("~/Downloads/ghidra_12.0.4_PUBLIC"),
    )
    _REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    _PROJ_PATH = os.path.join(_REPO, "reverse")
    _CONSUMER = "pyghidra_batch_decompile"

    pyghidra.start(install_dir=_GHIDRA_HOME)

    from pyghidra import open_project

    _project_ctx = open_project(_PROJ_PATH, "r1mx")
    _project = _project_ctx.__enter__()
    _dom_file = _project.getProjectData().getRootFolder().getFile("software.bin")
    if _dom_file is None:
        print("ERROR: software.bin not found in r1mx project")
        _project_ctx.__exit__(None, None, None)
        sys.exit(1)
    currentProgram = _dom_file.getDomainObject(_CONSUMER, True, False, None)
    print("Opened:", currentProgram.getName(), "arch:", currentProgram.getLanguageID())

from ghidra.app.decompiler import DecompInterface
from ghidra.program.model.symbol import SourceType
from ghidra.program.flatapi import FlatProgramAPI
from ghidra.util.task import ConsoleTaskMonitor

flat     = FlatProgramAPI(currentProgram)
listing  = currentProgram.getListing()
addr_fac = currentProgram.getAddressFactory().getDefaultAddressSpace()
monitor  = ConsoleTaskMonitor()

RANGE_START = int(os.environ.get("DECOMPILE_START", "0x1e000"), 16)
RANGE_END   = int(os.environ.get("DECOMPILE_END",   "0x40000"), 16)
SUFFIX      = os.environ.get("DECOMPILE_SUFFIX", f"{RANGE_START:08x}")

OUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "reverse", "build_32", "src", "xmlsocket",
    f"region_{SUFFIX}"
)
os.makedirs(OUT_DIR, exist_ok=True)


def addr(offset):
    return addr_fac.getAddress(offset)


# Force-disassemble the region to ensure all instructions are decoded
tx = currentProgram.startTransaction("batch_disassemble")
try:
    from ghidra.program.model.address import AddressSet
    region = AddressSet(addr(RANGE_START), addr(RANGE_END - 1))
    flat.disassemble(addr(RANGE_START))
    print(f"Disassembly requested for 0x{RANGE_START:08x}–0x{RANGE_END:08x}")
finally:
    currentProgram.endTransaction(tx, True)

# Collect all known functions in range
ifc = DecompInterface()
ifc.openProgram(currentProgram)

fns = []
fn_iter = listing.getFunctions(addr(RANGE_START), True)
while fn_iter.hasNext():
    fn = fn_iter.next()
    ep = fn.getEntryPoint().getOffset()
    if ep >= RANGE_END:
        break
    fns.append(fn)

print(f"Found {len(fns)} functions in 0x{RANGE_START:08x}–0x{RANGE_END:08x}")

ok_count = 0
fail_count = 0

for fn in fns:
    ep = fn.getEntryPoint().getOffset()
    name = fn.getName()
    result = ifc.decompileFunction(fn, 120, monitor)
    if result.decompileCompleted():
        c = result.getDecompiledFunction().getC()
        out_path = os.path.join(OUT_DIR, f"0x{ep:08x}_{name}.c")
        with open(out_path, "w") as f:
            f.write(
                f"/* 0x{ep:08x}  {name}  size={fn.getBody().getNumAddresses()} bytes */\n\n{c}"
            )
        print(f"  OK  0x{ep:08x}  {name}")
        ok_count += 1
    else:
        print(f"  !! FAIL  0x{ep:08x}  {name}: {result.getErrorMessage()[:60]}")
        fail_count += 1

ifc.dispose()
print(f"\nDecompiled {ok_count}/{ok_count+fail_count} functions → {os.path.abspath(OUT_DIR)}/")

if _STANDALONE:
    currentProgram.release(_CONSUMER)
    _project_ctx.__exit__(None, None, None)
    print("Done.")
