"""
ghidra_export_xml_decompile.py -- Export Ghidra decompiled C for XML socket handler functions.

Decompiles every function in the XML socket handler region and writes C pseudocode to
firmware/reverse/build_32/src/xmlsocket/.

Run ghidra_find_xml_functions.py first to label the functions.

Usage (standalone via pyghidra):
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
    python3 firmware/scripts/ghidra_export_xml_decompile.py

Or as a postScript via analyzeHeadless.
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
    _CONSUMER = "pyghidra_export_xml"

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

OUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "reverse", "build_32", "src", "xmlsocket"
)
os.makedirs(OUT_DIR, exist_ok=True)


def addr(offset):
    return addr_fac.getAddress(offset)


# Named functions to decompile (set by ghidra_find_xml_functions.py or manual labeling).
# Also include any unnamed functions in these address ranges that look like XML handler code.
NAMED_TARGETS = [
    "UiIpModule_socket_setup",
    "UiIpModule_accept_loop",
    "Connection_Authenticate",
    "Connection_ProcessGuiCommand",
    "xmlUtil_ParseCommand",
    "xmlUtil_ParseMessage",
    "GPDB_GetFile",
    "GPDB_GetParam",
    "GPDB_AuthInit",
    "GPDB_AuthPass",
]

# Address ranges likely containing XML handler code (from string clustering).
# All functions whose entry points fall in these ranges will also be decompiled.
SCAN_RANGES = [
    (0xd94000, 0xd9afff),   # Connection + UiIpModule classes
    (0xdb7800, 0xdb8fff),   # xmlUtil
    (0xab9000, 0xabafff),   # GPDB parameter accessors
]

# Map from output file stem to address ranges / function names
OUTPUT_GROUPS = {
    "connection":    ([(0xd94000, 0xd97fff)], ["Connection_Authenticate", "Connection_ProcessGuiCommand"]),
    "ui_ip_module":  ([(0xd98000, 0xd9afff)], ["UiIpModule_socket_setup", "UiIpModule_accept_loop"]),
    "xmlutil":       ([(0xdb7800, 0xdb8fff)], ["xmlUtil_ParseCommand", "xmlUtil_ParseMessage"]),
    "gpdb":          ([(0xab9000, 0xabafff)], ["GPDB_GetFile", "GPDB_GetParam", "GPDB_AuthInit", "GPDB_AuthPass"]),
}


def decompile_function(ifc, fn):
    """Return decompiled C string for fn, or None on failure."""
    result = ifc.decompileFunction(fn, 120, monitor)
    if result.decompileCompleted():
        return result.getDecompiledFunction().getC()
    return None


def collect_functions_in_range(start_offset, end_offset):
    """Yield all Function objects whose entry point is in [start, end]."""
    it = listing.getFunctions(addr(start_offset), True)
    while it.hasNext():
        fn = it.next()
        ep = fn.getEntryPoint().getOffset()
        if ep > end_offset:
            break
        yield fn


ifc = DecompInterface()
ifc.openProgram(currentProgram)

print(f"\n=== Exporting decompiled C to {os.path.abspath(OUT_DIR)} ===\n")

for stem, (ranges, named) in OUTPUT_GROUPS.items():
    seen = set()
    chunks = []

    # Collect named targets first
    for name in named:
        syms = list(currentProgram.getSymbolTable().getSymbols(name))
        for sym in syms:
            fn = flat.getFunctionAt(sym.getAddress())
            if fn and fn.getEntryPoint().getOffset() not in seen:
                seen.add(fn.getEntryPoint().getOffset())
                c = decompile_function(ifc, fn)
                if c:
                    chunks.append(f"/* ---- {fn.getName()} @ {fn.getEntryPoint()} ---- */\n{c}")
                    print(f"  [OK] {fn.getName():<45s} @ {fn.getEntryPoint()}")
                else:
                    print(f"  [!!] {fn.getName():<45s} @ {fn.getEntryPoint()}  decompile FAILED")

    # Scan address ranges for any additional functions
    for (rstart, rend) in ranges:
        for fn in collect_functions_in_range(rstart, rend):
            ep = fn.getEntryPoint().getOffset()
            if ep in seen:
                continue
            seen.add(ep)
            c = decompile_function(ifc, fn)
            if c:
                chunks.append(f"/* ---- {fn.getName()} @ {fn.getEntryPoint()} ---- */\n{c}")
                print(f"  [rng] {fn.getName():<45s} @ {fn.getEntryPoint()}")
            else:
                print(f"  [~rng] {fn.getName():<45s} @ {fn.getEntryPoint()}  decompile FAILED")

    if not chunks:
        print(f"  [--] {stem}: no functions found")
        continue

    out_path = os.path.join(OUT_DIR, f"{stem}.c")
    header = (
        f"/* AUTO-GENERATED by ghidra_export_xml_decompile.py\n"
        f" * Firmware: RED ONE MX build_32/software.bin (PowerPC 405F6, VxWorks 2.10)\n"
        f" * This is Ghidra decompiler pseudocode — not original source.\n"
        f" */\n\n"
    )
    with open(out_path, "w") as f:
        f.write(header + "\n\n".join(chunks) + "\n")
    print(f"  => wrote {len(chunks)} function(s) to {out_path}\n")

ifc.dispose()

if _STANDALONE:
    currentProgram.release(_CONSUMER)
    _project_ctx.__exit__(None, None, None)
    print("Done.")
