"""
ghidra_trace_xml_chain.py -- Trace the XML socket handler call chain.

Starting from the known socket setup function (found via 'listen() failed' string xref
at code address 0x1fb40), decompile it and walk up its call graph to find
Connection::ProcessGuiCommand and related XML handler functions.

Usage:
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
    python3 firmware/scripts/ghidra_trace_xml_chain.py
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
    _CONSUMER = "pyghidra_trace_xml"

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

flat      = FlatProgramAPI(currentProgram)
listing   = currentProgram.getListing()
ref_mgr   = currentProgram.getReferenceManager()
addr_fac  = currentProgram.getAddressFactory().getDefaultAddressSpace()
monitor   = ConsoleTaskMonitor()

OUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "reverse", "build_32", "src", "xmlsocket"
)
os.makedirs(OUT_DIR, exist_ok=True)

ifc = DecompInterface()
ifc.openProgram(currentProgram)


def addr(offset):
    return addr_fac.getAddress(offset)


def ensure_function(offset, name=None):
    """Disassemble and create function at offset if not already present."""
    a = addr(offset)
    fn = listing.getFunctionAt(a)
    if fn is None:
        if listing.getInstructionAt(a) is None:
            flat.disassemble(a)
        fn = flat.createFunction(a, name or f"FUN_{offset:08x}")
    if name and fn and fn.getName().startswith("FUN_"):
        fn.setName(name, SourceType.USER_DEFINED)
    return fn


def decompile(fn):
    if fn is None:
        return None
    result = ifc.decompileFunction(fn, 120, monitor)
    if result.decompileCompleted():
        return result.getDecompiledFunction().getC()
    print(f"  DECOMPILE FAIL: {fn.getName()} @ {fn.getEntryPoint()}: {result.getErrorMessage()}")
    return None


def get_callers(fn):
    """Return list of (caller_fn, call_site_addr) for all callers of fn."""
    callers = []
    for ref in ref_mgr.getReferencesTo(fn.getEntryPoint()):
        from_addr = ref.getFromAddress()
        caller = listing.getFunctionContaining(from_addr)
        if caller:
            callers.append((caller, from_addr))
    return callers


def get_callees(fn):
    """Return list of callee Function objects called by fn."""
    body = fn.getBody()
    callees = []
    addr_set = body.getAddressRanges()
    while addr_set.hasNext():
        r = addr_set.next()
        a = r.getMinAddress()
        while a.compareTo(r.getMaxAddress()) <= 0:
            refs = list(ref_mgr.getReferencesFrom(a))
            for ref in refs:
                from ghidra.program.model.symbol import RefType
                if ref.getReferenceType().isCall():
                    callee = listing.getFunctionAt(ref.getToAddress())
                    if callee:
                        callees.append(callee)
            a = a.next()
    return callees


tx = currentProgram.startTransaction("trace_xml_chain")
ok = False
try:
    # Step 1: Force-create the socket setup function found at 0x1f8f4
    # (contains 'listen() failed' reference at 0x1fb40)
    print("\n=== Step 1: Create socket setup function ===")
    socket_fn = ensure_function(0x0001f8f4, "UiIpModule_socket_setup")
    if socket_fn:
        print(f"  Function: {socket_fn.getName()} @ {socket_fn.getEntryPoint()}")
        print(f"  Body size: {socket_fn.getBody().getNumAddresses()} bytes")

    # Also try the earlier prologue
    fn2 = ensure_function(0x0001f89c)
    if fn2:
        print(f"  Adjacent: {fn2.getName()} @ {fn2.getEntryPoint()}")

    # Step 2: Find callers of socket setup
    print("\n=== Step 2: Find callers of socket setup ===")
    if socket_fn:
        callers = get_callers(socket_fn)
        print(f"  {len(callers)} caller(s):")
        for caller, site in callers:
            print(f"    {caller.getName()} @ {caller.getEntryPoint()}  (call site: {site})")

    # Step 3: Scan for functions in the 0x1e000-0x30000 range (near socket code)
    print("\n=== Step 3: Enumerate functions near socket code (0x1e000-0x30000) ===")
    fns_near = []
    fn_iter = listing.getFunctions(addr(0x1e000), True)
    while fn_iter.hasNext():
        fn = fn_iter.next()
        ep = fn.getEntryPoint().getOffset()
        if ep > 0x30000:
            break
        fns_near.append(fn)
        print(f"  {fn.getName()} @ 0x{ep:08x}  size={fn.getBody().getNumAddresses()}")

    ok = True
finally:
    currentProgram.endTransaction(tx, ok)

# Step 4: Decompile the socket function and callers
print("\n=== Step 4: Decompile ===")
fns_to_decompile = []
if socket_fn:
    fns_to_decompile.append(("UiIpModule_socket_setup", socket_fn))
    for caller, _ in get_callers(socket_fn):
        fns_to_decompile.append((caller.getName(), caller))

written = []
for name, fn in fns_to_decompile:
    c = decompile(fn)
    if c:
        out_path = os.path.join(OUT_DIR, f"{name}.c")
        with open(out_path, "w") as f:
            f.write(
                f"/* AUTO-GENERATED by ghidra_trace_xml_chain.py\n"
                f" * {fn.getName()} @ {fn.getEntryPoint()}\n"
                f" * Firmware: RED ONE MX build_32/software.bin (PowerPC 405F6, VxWorks 2.10)\n"
                f" */\n\n{c}"
            )
        print(f"  OK: {name} -> {out_path}")
        written.append(out_path)
    else:
        print(f"  FAIL: {name}")

print(f"\nWrote {len(written)} file(s) to {os.path.abspath(OUT_DIR)}/")

ifc.dispose()

if _STANDALONE and ok:
    currentProgram.save("trace_xml_chain", None)
    print("Project saved.")
    currentProgram.release(_CONSUMER)
    _project_ctx.__exit__(None, None, None)
