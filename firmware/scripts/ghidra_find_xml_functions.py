"""
ghidra_find_xml_functions.py -- Find firmware functions that handle the XML socket interface.

For each known string address (method name / error string embedded in the firmware),
find all code cross-references to it and label the enclosing function.

Usage (standalone via pyghidra):
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
    python3 firmware/scripts/ghidra_find_xml_functions.py

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
    _CONSUMER = "pyghidra_find_xml"

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

from ghidra.program.model.symbol import SourceType
from ghidra.program.flatapi import FlatProgramAPI

flat      = FlatProgramAPI(currentProgram)
ref_mgr   = currentProgram.getReferenceManager()
listing   = currentProgram.getListing()
sym_table = currentProgram.getSymbolTable()
addr_fac  = currentProgram.getAddressFactory().getDefaultAddressSpace()


def addr(offset):
    return addr_fac.getAddress(offset)


# String offsets → intended function label for the function that references the string.
# These are byte offsets into the raw binary (= virtual addresses, binary loads at 0x0).
TARGET_STRINGS = {
    # UiIpModule — TCP server
    0xd354e4: "UiIpModule_socket_setup",    # "socket() failed"
    0xd354f8: "UiIpModule_socket_setup",    # "bind() failed"   (same function)
    0xd35508: "UiIpModule_socket_setup",    # "listen() failed" (same function)
    0xd355c8: "UiIpModule_accept_loop",     # "accept() failed"

    # Connection — per-client session
    0xd94c48: "Connection_Authenticate",
    0xd94e0c: "Connection_ProcessGuiCommand",

    # xmlUtil — XML parse helpers
    0xdb78d8: "xmlUtil_ParseCommand",
    0xdb78f4: "xmlUtil_ParseMessage",

    # GPDB — parameter database
    0xab952e: "GPDB_GetFile",               # "GET_FILE" literal
    0xab95ca: "GPDB_GetParam",              # "GET_PARAM" literal
    0xac0745: "GPDB_AuthInit",              # "AUTH_INIT" literal
    0xac074f: "GPDB_AuthPass",              # "AUTH_PASS" literal
}

found = {}  # addr_str → set of labels

tx = currentProgram.startTransaction("find_xml_functions")
ok = False
try:
    print("\n=== Searching for XML socket functions ===")
    for offset, label_name in TARGET_STRINGS.items():
        str_addr = addr(offset)
        refs = list(ref_mgr.getReferencesTo(str_addr))
        if not refs:
            print(f"  [?] 0x{offset:08x}  no xrefs  ({label_name})")
            continue
        for ref in refs:
            fn = flat.getFunctionContaining(ref.getFromAddress())
            if fn is None:
                # Try to create a function at the nearest prior instruction
                print(f"  [~] 0x{offset:08x}  xref from 0x{ref.getFromAddress().getOffset():08x} — no function boundary (needs manual analysis)")
                continue
            fn_addr = fn.getEntryPoint().getOffset()
            key = f"0x{fn_addr:08x}"
            if key not in found:
                found[key] = set()
            found[key].add(label_name)

            # Apply label if the function has only a default Ghidra-generated name
            current_name = fn.getName()
            if current_name.startswith("FUN_") or current_name.startswith("DAT_"):
                try:
                    fn.setName(label_name, SourceType.USER_DEFINED)
                    print(f"  [+] {label_name:<40s}  @ 0x{fn_addr:08x}  (renamed from {current_name})")
                except Exception as e:
                    print(f"  [!] rename failed for {label_name} @ 0x{fn_addr:08x}: {e}")
            else:
                print(f"  [=] {label_name:<40s}  @ 0x{fn_addr:08x}  (existing name: {current_name})")

    ok = True
finally:
    currentProgram.endTransaction(tx, ok)

print("\n=== Summary: unique function entry points ===")
for fn_addr_str, labels in sorted(found.items()):
    print(f"  {fn_addr_str}  {', '.join(sorted(labels))}")

if _STANDALONE and ok:
    currentProgram.save("find_xml_functions", None)
    print("\nProject saved.")
    currentProgram.release(_CONSUMER)
    _project_ctx.__exit__(None, None, None)
