"""
ghidra_seed_symbols.py — Ghidra post-import script (runs inside Ghidra / analyzeHeadless)

Seeds the r1mx project with:
  - Known function labels from build32_static_analysis.md
  - Exception vector table labels
  - MMIO memory region labels
  - BSS region bookmarks

Run via analyzeHeadless -postScript, or from the Ghidra Script Manager.
"""

# --- Imports (Ghidra Jython / PyGhidra API) ---
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.data import (
    DataTypeManager, ByteDataType, DWordDataType, ArrayDataType
)
from ghidra.program.model.listing import CodeUnit
from ghidra.program.flatapi import FlatProgramAPI

flat = FlatProgramAPI(currentProgram)
sym_table = currentProgram.getSymbolTable()
listing = currentProgram.getListing()
addr_factory = currentProgram.getAddressFactory()
addr_space = addr_factory.getDefaultAddressSpace()
mem = currentProgram.getMemory()


def addr(offset):
    return addr_space.getAddress(offset)


def label(offset, name, comment=None):
    """Create a label at the given offset. Overwrites DEFAULT labels."""
    a = addr(offset)
    # Remove any existing default symbol
    for s in sym_table.getSymbols(a):
        if s.getSource() == SourceType.DEFAULT:
            s.delete()
    sym_table.createLabel(a, name, SourceType.USER_DEFINED)
    if comment:
        listing.setComment(a, CodeUnit.PLATE_COMMENT, comment)
    print("  [+] {:10s}  @ 0x{:08X}".format(name, offset))


def func(offset, name, comment=None):
    """Disassemble + create function + label."""
    a = addr(offset)
    if listing.getInstructionAt(a) is None:
        flat.disassemble(a)
    if listing.getFunctionAt(a) is None:
        flat.createFunction(a, name)
    else:
        listing.getFunctionAt(a).setName(name, SourceType.USER_DEFINED)
    label(offset, name, comment)


def mem_label(offset, name, comment=None):
    """Label a data/MMIO address that may not be in the binary image."""
    a = addr(offset)
    try:
        sym_table.createLabel(a, name, SourceType.USER_DEFINED)
        if comment:
            listing.setComment(a, CodeUnit.EOL_COMMENT, comment)
        print("  [m] {:30s}  @ 0x{:08X}".format(name, offset))
    except Exception as e:
        print("  [!] Could not label 0x{:08X} ({}): {}".format(offset, name, e))


# ─────────────────────────────────────────────
# 1. Exception vector table
# ─────────────────────────────────────────────
print("\n=== Exception Vectors ===")
label(0x00000000, "reset_vector",         "PPC405 reset / romInit entry")
label(0x00000200, "machine_check_vec",    "Machine check exception")
label(0x00000300, "dsi_vec",              "Data storage interrupt (DSI)")
label(0x00000400, "isi_vec",              "Instruction storage interrupt (ISI)")
label(0x00000500, "ext_interrupt_vec",    "External interrupt")
label(0x00000600, "alignment_vec",        "Alignment exception")
label(0x00000700, "program_check_vec",    "Program check exception")
label(0x00000800, "fp_unavail_vec",       "FP unavailable")
label(0x00000900, "decrementer_vec",      "Decrementer interrupt")
label(0x00000C00, "sys_call_vec",         "System call (sc)")
label(0x00000D00, "trace_vec",            "Trace exception")

# ─────────────────────────────────────────────
# 2. Known functions
# ─────────────────────────────────────────────
print("\n=== Functions ===")
func(0x00000000, "romInit",
     "Reset vector entry. Clears MSR, invalidates caches, sets up temp SP at 0xFFF0, "
     "then branches to main_boot_init.")

func(0x00000124, "halt_loop",
     "Infinite branch-to-self: b 0x124. Reached only if romInit returns (fatal).")

func(0x0000D8A0, "timer_clock_helper",
     "Timer/clock helper. Called twice from main_boot_init (0x36C3F0 and 0x36C3F8). "
     "Loads/stores the tick counter.")

func(0x0000DCB0, "hw_seq_init",
     "Early hardware sequencer init. Calls sysClkInit and performs SDRAM/FPGA setup.")

func(0x00012D90, "mmio_dispatch_table",
     "Large switch statement dispatching on MMIO peripheral base address.")

func(0x001C18DC, "uart_init",
     "Xilinx UART Lite driver init. First MMIO access at 0x40600000 visible at 0x1C1A0C.")

func(0x0036C350, "main_boot_init",
     "Equivalent of VxWorks usrInit/usrConfig. "
     "Waits for stack canary at 0xE269A4/A0, zeroes BSS (0xE9BF20–0x01153480), "
     "then starts the VxWorks kernel.")

func(0x00496698, "memset",
     "Called from main_boot_init to zero the BSS segment (~2.8 MB).")

# ─────────────────────────────────────────────
# 3. Stack canary check addresses
# ─────────────────────────────────────────────
print("\n=== Stack Canary Addresses ===")
label(0x0036C380, "canary_wait_loop_start",
      "Spin loop: waits for 0xE269A4 == 0x12348765 and 0xE269A0 == 0x5A5AC3C3. "
      "QEMU patch: NOP the bne at 0x36C388 and 0x36C394.")
label(0x0036C388, "canary_patch_1",
      "QEMU PATCH: 409EFFF8 → 60000000 (NOP bne cr7 → canary_wait_loop_start)")
label(0x0036C394, "canary_patch_2",
      "QEMU PATCH: 409EFFEC → 60000000 (NOP bne cr7 → canary_wait_loop_start)")

# ─────────────────────────────────────────────
# 4. romInit SP patch site
# ─────────────────────────────────────────────
label(0x00000084, "romInit_sp_init",
      "QEMU PATCH: 3C200001 → 3C200800: lis r1,1 → lis r1,0x800 relocates temp SP to 0x07FFFFF0")

# ─────────────────────────────────────────────
# 5. BSS region bookmarks
# ─────────────────────────────────────────────
print("\n=== BSS Region ===")
label(0x00E9BF20, "bss_start", "BSS segment start (zeroed by main_boot_init via memset)")
label(0x01153480, "bss_end",   "BSS segment end  (size: 0x2B7560 = ~2.8 MB)")

# ─────────────────────────────────────────────
# 6. Embedded data blobs
# ─────────────────────────────────────────────
print("\n=== Embedded Blobs ===")
label(0x00495BE8, "windriver_copyright",  "Copyright string: Wind River Systems 1984-2006")
label(0x005A83D8, "vxworks_version_str",  "VxWorks WIND kernel version 2.10 string")
label(0x00672824, "gzip_blob_1",          "gzip compressed data (null date, internal blob)")
label(0x007D7BFC, "gzip_blob_2",          "gzip compressed data")
label(0x00942B88, "splash_mx_raw_gz",     "gzip: splash_mx.raw — Mysterium-X splash screen (2009-12-16)")
label(0x009C0EDC, "splash_raw_gz",        "gzip: splash.raw — alternate splash screen (2008-07-14)")
label(0x009D2AE0, "xml_osd_panels",       "XML v1.0: OSD/UI panel definitions (~40 KB)")
label(0x009E03BC, "swf_gui_1",            "Adobe Flash SWF v7: main GUI (1,329,944 bytes)")
label(0x00B24EF8, "swf_gui_2",            "Adobe Flash SWF v7: alternate GUI (1,346,327 bytes)")
label(0x00C6E1A4, "xml_param_defs",       "XML v1.0: camera parameter definitions (~200 KB)")
label(0x00DEF5D0, "stuffit_data_tables",  "StuffIt data structures: internal data tables")
label(0x00E05700, "dinkumware_copyright", "Copyright: P.J. Plauger / Dinkumware 1992-2002 (C++ runtime)")

# ─────────────────────────────────────────────
# 7. MMIO peripheral map (external memory — may not be in binary image)
# ─────────────────────────────────────────────
print("\n=== MMIO Peripheral Bases ===")
mem_label(0x40000000, "FPGA_REG_BASE",   "Primary FPGA registers / bus (223 refs in code)")
mem_label(0x40600000, "UART_LITE_BASE",  "Xilinx UART Lite MMIO base (107 refs)")
mem_label(0x408F0000, "MMIO_408F0000",   "Unknown peripheral (67 refs)")
mem_label(0x40340000, "MMIO_40340000",   "Unknown peripheral (47 refs)")
mem_label(0x40590000, "MMIO_40590000",   "Unknown peripheral (35 refs)")
mem_label(0x40240000, "MMIO_40240000",   "Unknown peripheral (36 refs)")
mem_label(0x40100000, "MMIO_40100000",   "Unknown peripheral (35 refs)")
mem_label(0x40040000, "MMIO_40040000",   "Unknown peripheral (31 refs)")
mem_label(0x40400000, "MMIO_40400000",   "Unknown peripheral (16 refs)")
mem_label(0x40080000, "MMIO_40080000",   "Unknown peripheral (15 refs)")

# Canary check MMIO-mapped RAM addresses
mem_label(0x00E269A4, "canary_val_1",   "Stack canary: expected 0x12348765")
mem_label(0x00E269A0, "canary_val_2",   "Stack canary: expected 0x5A5AC3C3")

print("\n=== Symbol seeding complete. ===")
