/*
 * r1mx_firmware.ld — GNU ld linker script for RED ONE MX firmware (build 32 v32.0.3)
 *
 * Target:     PowerPC 405GP, big-endian, 32-bit, flat binary
 * Load base:  0x00000000 (physical RAM zero — no MMU mapping at boot)
 * Entry:      0x00000000 (romInit, reset vector)
 *
 * Memory layout reverse-engineered from software.bin (SHA-256:
 *   416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd)
 *
 * To build and produce a flat binary matching the original:
 *
 *   powerpc-linux-gnu-gcc -mcpu=405 -mbig-endian -O2 -ffreestanding -nostdlib \
 *     -T r1mx_firmware.ld -o firmware.elf <objects>
 *   powerpc-linux-gnu-objcopy -O binary firmware.elf software_rebuilt.bin
 *
 * Validate:
 *   cmp software_rebuilt.bin software.bin   # byte-identical only if compiler/flags match exactly
 *   powerpc-linux-gnu-objdump -d firmware.elf | diff - <(r2 -a ppc -b 32 -e cfg.bigendian=true \
 *     -c "pd @ 0" -q firmware/reverse/build_32/extracted/software.bin)
 */

ENTRY(romInit)

/*
 * Physical memory map (PPC405GP on Xilinx ML310-style board).
 * - SDRAM:   0x00000000 – 0x0FFFFFFF (256 MB, though camera likely has 64–128 MB)
 * - Flash:   not mapped at 0 at runtime (remapped after boot)
 * - MMIO:    0x40000000 – 0x4FFFFFFF (FPGA + peripherals)
 */
MEMORY
{
    /* ── Executable image ── */
    RESET_VECS  (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00001000   /* Exception vector table (4 KB) */
    TEXT        (rx)  : ORIGIN = 0x00001000, LENGTH = 0x006FF000   /* Main code (~7 MB) */
    MIXED       (rwx) : ORIGIN = 0x00700000, LENGTH = 0x00200000   /* Mixed code+data structs (2 MB) */
    RODATA      (r)   : ORIGIN = 0x00900000, LENGTH = 0x00400000   /* Embedded blobs: XML, SWF, gzip (4 MB) */
    SYMTAB      (r)   : ORIGIN = 0x00D00000, LENGTH = 0x00100000   /* Symbol/string tables, debug (1 MB) */
    TEXT_TAIL   (rx)  : ORIGIN = 0x00E00000, LENGTH = 0x0008BF20   /* Code tail (BSS-init path) */

    /* ── Zero-initialised data (not in binary file, in RAM only) ── */
    BSS_RAM     (rw)  : ORIGIN = 0x00E9BF20, LENGTH = 0x002B7560   /* BSS ~2.8 MB */

    /* ── Stack (temporary boot stack; VxWorks replaces this) ── */
    BOOT_STACK  (rw)  : ORIGIN = 0x0000F000, LENGTH = 0x00001000   /* 4 KB, top = 0xFFF0 */

    /* ── MMIO peripheral space (not backed by RAM) ── */
    MMIO_FPGA   (!rx) : ORIGIN = 0x40000000, LENGTH = 0x01000000   /* FPGA register space */
}

/*
 * Output sections
 */
SECTIONS
{
    /* ─────────────────────────────────────────────────────────────────
     * Exception vector table — must live at exact PPC405 vector offsets.
     * Each handler is 0x100 bytes; the CPU jumps here on exception.
     * ──────────────────────────────────────────────────────────────── */
    .vectors 0x00000000 :
    {
        /* romInit / reset entry — offset 0x000 */
        KEEP(*(.vectors.reset))
        KEEP(*(.romInit))

        /* PPC405 standard exception vectors at fixed offsets */
        . = 0x200;  KEEP(*(.vectors.machine_check))
        . = 0x300;  KEEP(*(.vectors.dsi))
        . = 0x400;  KEEP(*(.vectors.isi))
        . = 0x500;  KEEP(*(.vectors.ext_interrupt))
        . = 0x600;  KEEP(*(.vectors.alignment))
        . = 0x700;  KEEP(*(.vectors.program))
        . = 0x800;  KEEP(*(.vectors.fp_unavail))
        . = 0x900;  KEEP(*(.vectors.decrementer))
        . = 0xC00;  KEEP(*(.vectors.syscall))
        . = 0xD00;  KEEP(*(.vectors.trace))

        . = 0x1000; /* end of vector table */
    } > RESET_VECS

    /* ─────────────────────────────────────────────────────────────────
     * Main code
     * ──────────────────────────────────────────────────────────────── */
    .text :
    {
        *(.text)
        *(.text.*)
        *(.gnu.linkonce.t.*)
    } > TEXT

    /* ─────────────────────────────────────────────────────────────────
     * Mixed code + large data structures (0x700000–0x8FFFFF)
     * ──────────────────────────────────────────────────────────────── */
    .text.mixed 0x00700000 :
    {
        *(.text.mixed)
        *(.data.mixed)
    } > MIXED

    /* ─────────────────────────────────────────────────────────────────
     * Read-only embedded blobs (XML, SWF, gzip splash screens)
     *
     * Key offsets (from binary, do not reorder):
     *   0x942B88  splash_mx.raw.gz
     *   0x9C0EDC  splash.raw.gz
     *   0x9D2AE0  XML OSD panels
     *   0x9E03BC  SWF GUI v7 (main)
     *   0xB24EF8  SWF GUI v7 (alt)
     *   0xC6E1A4  XML parameter definitions
     * ──────────────────────────────────────────────────────────────── */
    .rodata 0x00900000 :
    {
        *(.rodata)
        *(.rodata.*)
        *(.gnu.linkonce.r.*)

        /* Force-include named blob objects if compiled as separate .o files */
        KEEP(*(.blob.splash_mx))
        KEEP(*(.blob.splash))
        KEEP(*(.blob.xml_osd))
        KEEP(*(.blob.swf_gui_1))
        KEEP(*(.blob.swf_gui_2))
        KEEP(*(.blob.xml_params))
    } > RODATA

    /* ─────────────────────────────────────────────────────────────────
     * Symbol/debug tables (Dinkumware runtime + VxWorks strings)
     *   0xDEF5D0  StuffIt data tables
     *   0xE05700  Dinkumware copyright (C++ runtime)
     * ──────────────────────────────────────────────────────────────── */
    .symtab 0x00D00000 :
    {
        *(.symtab_data)
        *(.debug_strings)
    } > SYMTAB

    /* ─────────────────────────────────────────────────────────────────
     * Code tail — BSS-init path (main_boot_init and late init functions)
     *   Includes:  hw_seq_init (0xDCB0), timer_clock_helper (0xD8A0),
     *              main_boot_init (0x36C350), memset (0x496698)
     * ──────────────────────────────────────────────────────────────── */
    .text.tail 0x00E00000 :
    {
        *(.text.tail)
        *(.text.init)
    } > TEXT_TAIL

    /* ─────────────────────────────────────────────────────────────────
     * Initialised data (.data) — loaded from binary, copied to RAM.
     * Placed immediately after code tail in the image.
     * ──────────────────────────────────────────────────────────────── */
    .data :
    {
        *(.data)
        *(.data.*)
        *(.gnu.linkonce.d.*)
        _edata = .;
    } > BSS_RAM AT > TEXT_TAIL   /* LMA in TEXT_TAIL, VMA in BSS_RAM */

    /* ─────────────────────────────────────────────────────────────────
     * BSS — zero-initialised, not present in binary file.
     *   VMA: 0x00E9BF20 – 0x01153480  (size 0x002B7560, ~2.8 MB)
     *   Zeroed by main_boot_init calling memset @ 0x496698.
     *
     * Stack canary locations (checked before zeroing):
     *   0x00E269A4  expected 0x12348765
     *   0x00E269A0  expected 0x5A5AC3C3
     * ──────────────────────────────────────────────────────────────── */
    .bss (NOLOAD) :
    {
        _bss_start = .;
        *(.bss)
        *(.bss.*)
        *(COMMON)
        . = ALIGN(4);
        _bss_end = .;
    } > BSS_RAM

    /* Sanity-check the BSS bounds against the reverse-engineered values */
    ASSERT(_bss_start == 0x00E9BF20,
           "ERROR: bss_start mismatch — expected 0x00E9BF20. Check section ordering.")
    ASSERT(_bss_end <= 0x01153480,
           "ERROR: bss_end exceeds 0x01153480. BSS is too large.")

    /* ─────────────────────────────────────────────────────────────────
     * Temporary boot stack — used only during romInit before VxWorks
     * sets up its own stack. SP initialised to 0x0000FFF0 by romInit.
     * ──────────────────────────────────────────────────────────────── */
    .boot_stack (NOLOAD) :
    {
        _boot_stack_bottom = .;
        . += 0x1000;
        _boot_stack_top = . - 16;  /* aligned: 0x0000FFF0 */
    } > BOOT_STACK

    /* ─────────────────────────────────────────────────────────────────
     * Discard debug / unwanted sections
     * ──────────────────────────────────────────────────────────────── */
    /DISCARD/ :
    {
        *(.note.*)
        *(.comment)
        *(.eh_frame)
        *(.ARM.*)
    }
}

/*
 * Provide symbols that C code can reference for BSS init and stack setup.
 * These match what main_boot_init (0x36C350) computes at runtime.
 */
PROVIDE(__bss_start__ = _bss_start);
PROVIDE(__bss_end__   = _bss_end);
PROVIDE(__stack_top__ = _boot_stack_top);
