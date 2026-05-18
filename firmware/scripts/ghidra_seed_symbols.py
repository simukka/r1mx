"""
ghidra_seed_symbols.py -- Seeds the r1mx Ghidra project with known symbols.

Seeds with:
  - Known function labels (build32_static_analysis.md)
  - Exception vector table labels
  - MMIO peripheral base labels (BSS, canary, blob markers)

Usage (standalone via pyghidra):
    cd /path/to/r1mx
    GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
    python3 firmware/scripts/ghidra_seed_symbols.py

Or from the Ghidra Script Manager: open r1mx.gpr, run this file.
In Script Manager mode 'currentProgram' is already in scope; the script
detects this and skips the project-open bootstrap.
"""

import os, sys

# ---------------------------------------------------------------------------
# Bootstrap: open existing Ghidra project when run as a standalone script
# ---------------------------------------------------------------------------
_STANDALONE = "currentProgram" not in dir()

if _STANDALONE:
    import pyghidra

    _GHIDRA_HOME = os.environ.get(
        "GHIDRA_INSTALL_DIR",
        os.path.expanduser("~/Downloads/ghidra_12.0.4_PUBLIC"),
    )
    _REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    _PROJ_PATH = os.path.join(_REPO, "reverse")
    _CONSUMER = "pyghidra_seed"

    pyghidra.start(install_dir=_GHIDRA_HOME)

    from pyghidra import open_project

    _project_ctx = open_project(_PROJ_PATH, "r1mx")
    _project = _project_ctx.__enter__()
    _dom_file = _project.getProjectData().getRootFolder().getFile("software.bin")
    if _dom_file is None:
        print("ERROR: software.bin not found in r1mx project at", _PROJ_PATH)
        _project_ctx.__exit__(None, None, None)
        sys.exit(1)
    currentProgram = _dom_file.getDomainObject(_CONSUMER, True, False, None)
    print("Opened:", currentProgram.getName(), "arch:", currentProgram.getLanguageID())

# ---------------------------------------------------------------------------
# Ghidra API imports (available after pyghidra.start() or inside Ghidra)
# ---------------------------------------------------------------------------
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit
from ghidra.program.flatapi import FlatProgramAPI

flat       = FlatProgramAPI(currentProgram)
sym_table  = currentProgram.getSymbolTable()
listing    = currentProgram.getListing()
addr_space = currentProgram.getAddressFactory().getDefaultAddressSpace()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def addr(offset):
    return addr_space.getAddress(offset)

def label(offset, name, comment=None):
    a = addr(offset)
    for s in sym_table.getSymbols(a):
        if s.getSource() == SourceType.DEFAULT:
            s.delete()
    sym_table.createLabel(a, name, SourceType.USER_DEFINED)
    if comment:
        listing.setComment(a, CodeUnit.PLATE_COMMENT, comment)
    print("  [+] {:<30s}  @ 0x{:08X}".format(name, offset))

def func(offset, name, comment=None):
    a = addr(offset)
    if listing.getInstructionAt(a) is None:
        flat.disassemble(a)
    fn = listing.getFunctionAt(a)
    if fn is None:
        flat.createFunction(a, name)
    else:
        fn.setName(name, SourceType.USER_DEFINED)
    label(offset, name, comment)

def mem_label(offset, name, comment=None):
    """Label an MMIO / external address that may not be in the binary image."""
    a = addr(offset)
    try:
        sym_table.createLabel(a, name, SourceType.USER_DEFINED)
        if comment:
            listing.setComment(a, CodeUnit.EOL_COMMENT, comment)
        print("  [m] {:<30s}  @ 0x{:08X}".format(name, offset))
    except Exception as e:
        print("  [!] 0x{:08X} {} -- {}".format(offset, name, e))

# ---------------------------------------------------------------------------
# All modifications in one transaction
# ---------------------------------------------------------------------------
tx = currentProgram.startTransaction("seed_symbols")
ok = False
try:
    # 1. Exception vectors
    print("\n=== Exception Vectors ===")
    label(0x00000000, "reset_vector",      "PPC405 reset / romInit entry")
    label(0x00000200, "machine_check_vec", "Machine check exception")
    label(0x00000300, "dsi_vec",           "Data storage interrupt (DSI)")
    label(0x00000400, "isi_vec",           "Instruction storage interrupt (ISI)")
    label(0x00000500, "ext_interrupt_vec", "External interrupt")
    label(0x00000600, "alignment_vec",     "Alignment exception")
    label(0x00000700, "program_check_vec", "Program check exception")
    label(0x00000800, "fp_unavail_vec",    "FP unavailable")
    label(0x00000900, "decrementer_vec",   "Decrementer interrupt")
    label(0x00000C00, "sys_call_vec",      "System call (sc)")
    label(0x00000D00, "trace_vec",         "Trace exception")

    # 2. Known functions
    print("\n=== Functions ===")
    func(0x00000000, "romInit",
         "Reset entry. Clears MSR, invalidates caches, temp SP at 0xFFF0, "
         "then calls main_boot_init.")
    func(0x00000124, "halt_loop",
         "Infinite branch-to-self. Reached only if romInit returns (fatal).")
    func(0x0000D8A0, "timer_clock_helper",
         "Timer/clock helper called twice from main_boot_init.")
    func(0x0000DCB0, "hw_seq_init",
         "Early hardware sequencer: sysClkInit, SDRAM/FPGA setup.")
    func(0x00012D90, "mmio_dispatch_table",
         "Large switch dispatching on MMIO peripheral base address.")
    func(0x001C18DC, "uart_init",
         "Xilinx UART Lite driver init. MMIO base 0x40600000 at 0x1C1A0C.")
    func(0x0036C350, "main_boot_init",
         "Equivalent of VxWorks usrInit. Waits for stack canaries at "
         "0xE269A4/A0, zeroes BSS (0xE9BF20-0x1153480), starts kernel.")
    func(0x00496698, "memset",
         "Zeroes BSS segment (~2.8 MB) called from main_boot_init.")

    # 3. Patch / canary sites
    print("\n=== Patch / Canary Sites ===")
    label(0x00000084, "romInit_sp_patch",
          "QEMU PATCH: 3C200001->3C200800 (lis r1,0x800 moves temp SP to 8 MB)")
    label(0x0036C380, "canary_wait_loop",
          "Spin: waits for 0xE269A4==0x12348765 and 0xE269A0==0x5A5AC3C3")
    label(0x0036C388, "canary_patch_1",
          "QEMU PATCH: 409EFFF8->60000000 (NOP bne toward canary_wait_loop)")
    label(0x0036C394, "canary_patch_2",
          "QEMU PATCH: 409EFFEC->60000000 (NOP bne toward canary_wait_loop)")

    # 4. BSS region
    print("\n=== BSS Region ===")
    label(0x00E9BF20, "bss_start",
          "BSS segment start -- zeroed by main_boot_init via memset")
    label(0x01153480, "bss_end",
          "BSS segment end  (size 0x2B7560 = ~2.8 MB)")

    # 5. Embedded blobs
    print("\n=== Embedded Blobs ===")
    label(0x00495BE8, "windriver_copyright",  "Wind River Systems 1984-2006")
    label(0x005A83D8, "vxworks_version_str",  "VxWorks WIND kernel version 2.10")
    label(0x00672824, "gzip_blob_1",          "gzip compressed blob (null date)")
    label(0x007D7BFC, "gzip_blob_2",          "gzip compressed blob")
    label(0x00942B88, "splash_mx_raw_gz",     "splash_mx.raw (Mysterium-X splash 2009-12-16)")
    label(0x009C0EDC, "splash_raw_gz",        "splash.raw (alternate splash 2008-07-14)")
    label(0x009D2AE0, "xml_osd_panels",       "XML v1.0: OSD/UI panel definitions (~40 KB)")
    label(0x009E03BC, "swf_gui_1",            "Adobe Flash SWF v7: main GUI (1,329,944 bytes)")
    label(0x00B24EF8, "swf_gui_2",            "Adobe Flash SWF v7: alternate GUI (1,346,327 bytes)")
    label(0x00C6E1A4, "xml_param_defs",       "XML v1.0: camera parameter definitions (~200 KB)")
    label(0x00DEF5D0, "stuffit_data_tables",  "StuffIt data structures")
    label(0x00E05700, "dinkumware_copyright", "P.J. Plauger / Dinkumware 1992-2002 (C++ runtime)")

    # 6. MMIO peripheral bases (external -- may not be in binary image)
    print("\n=== MMIO Peripheral Bases ===")
    mem_label(0x40000000, "FPGA_REG_BASE",  "Primary FPGA register bus (223 refs in code)")
    mem_label(0x40600000, "UART_LITE_BASE", "Xilinx UART Lite MMIO base (107 refs)")
    mem_label(0x408F0000, "MMIO_408F0000",  "Unknown peripheral (67 refs)")
    mem_label(0x40340000, "MMIO_40340000",  "Unknown peripheral (47 refs)")
    mem_label(0x40590000, "MMIO_40590000",  "Unknown peripheral (35 refs)")
    mem_label(0x40240000, "MMIO_40240000",  "Unknown peripheral (36 refs)")
    mem_label(0x40100000, "MMIO_40100000",  "Unknown peripheral (35 refs)")
    mem_label(0x40040000, "MMIO_40040000",  "Unknown peripheral (31 refs)")
    mem_label(0x40400000, "MMIO_40400000",  "Unknown peripheral (16 refs)")
    mem_label(0x40080000, "MMIO_40080000",  "Unknown peripheral (15 refs)")
    mem_label(0x00E269A4, "canary_val_1",   "Stack canary slot: expected 0x12348765")
    mem_label(0x00E269A0, "canary_val_2",   "Stack canary slot: expected 0x5A5AC3C3")

    ok = True
    print("\n=== Symbol seeding complete. ===")
finally:
    currentProgram.endTransaction(tx, ok)

# ---------------------------------------------------------------------------
# Standalone: save + close project
# ---------------------------------------------------------------------------
if _STANDALONE and ok:
    currentProgram.save("seed_symbols", None)
    print("Project saved.")
    currentProgram.release(_CONSUMER)
    _project_ctx.__exit__(None, None, None)
