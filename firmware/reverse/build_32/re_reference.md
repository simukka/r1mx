# RED ONE MX — Build 32 Firmware Reverse Engineering Reference

**Purpose:** Single-document reference for firmware reverse engineering of Build 32 v32.0.3.
Load this document at the start of any RE session. No need to hunt through PDFs or separate analysis files.

**Firmware binary:** `firmware/reverse/build_32/extracted/software.bin`
**CPU:** PowerPC 405F6 (Xilinx Virtex-4 FX hard-macro core), 32-bit, big-endian
**OS:** VxWorks WIND kernel 2.10 (Wind River Platform ~6.x)
**Build date:** September 7, 2013
**SHA-256:** `416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd`

---

## Table of Contents

1. [PPC405F6 Architecture Reference](#1-ppc405f6-architecture-reference)
2. [Ha/Lo Addressing — The Pointer Offset Problem](#2-halo-addressing--the-pointer-offset-problem)
3. [PPC405 Calling Convention](#3-ppc405-calling-convention)
4. [Binary Memory Layout](#4-binary-memory-layout)
5. [VxWorks Memory Model](#5-vxworks-memory-model)
6. [MMIO Peripheral Map](#6-mmio-peripheral-map)
7. [DCR (On-Chip Peripheral) Map](#7-dcr-on-chip-peripheral-map)
8. [Boot Sequence — Step by Step](#8-boot-sequence--step-by-step)
9. [Stack Canary — QEMU Patch](#9-stack-canary--qemu-patch)
10. [Key Function Addresses](#10-key-function-addresses)
11. [Key Data & BSS Addresses](#11-key-data--bss-addresses)
12. [Debug Interfaces — Quick Reference](#12-debug-interfaces--quick-reference)
13. [VxWorks Internals Cheat Sheet](#13-vxworks-internals-cheat-sheet)
14. [Firmware Package Format](#14-firmware-package-format)
15. [QEMU Setup & Usage](#15-qemu-setup--usage)
16. [radare2 Workflow](#16-radare2-workflow)
17. [Ghidra Setup](#17-ghidra-setup)
18. [Firmware Modification Workflow](#18-firmware-modification-workflow)
19. [Physical Camera Debug Interfaces](#19-physical-camera-debug-interfaces)
20. [Embedded Resources Map](#20-embedded-resources-map)
21. [FPGA Bitstream Analysis](#21-fpga-bitstream-analysis-fpgabin)
22. [Recommended Toolchain](#22-recommended-toolchain)

---

## 1. PPC405F6 Architecture Reference

### General Purpose Registers

| Register | ABI Role | Notes |
|----------|----------|-------|
| r0 | Scratch | Not a "zero register" in PPC (unlike MIPS). Used freely as temp. |
| r1 | Stack Pointer (SP) | Always points to bottom of current frame; must be 8-byte aligned |
| r2 | Small Data Area 2 (SDA2) | Read-only base for `.sdata2` / `.sbss2`; loaded once at startup |
| r3 | First arg / return value | Function parameter 1 and return value |
| r4–r10 | Args 2–8 | Function parameters |
| r11 | Scratch / env pointer | Used in dynamically-linked code; scratch in static builds |
| r12 | Scratch | Used for computed calls (e.g., vtable dispatch) |
| r13 | Small Data Area (SDA) | Read-write base for `.sdata` / `.sbss`; loaded once at startup |
| r14–r31 | Callee-saved | Must be preserved across calls |
| r14–r31 | Non-volatile | Caller can rely on these surviving a function call |

### Special Purpose Registers (SPRs) — most relevant

| SPR name | SPR# | Description |
|----------|------|-------------|
| LR | 8 | Link Register — holds return address after `bl` |
| CTR | 9 | Count Register — used for loops (`bdnz`) and indirect calls (`bctrl`) |
| XER | 1 | Integer exception register (carry, overflow, byte count) |
| SRR0 | 26 | Save/Restore Register 0 — PC at exception |
| SRR1 | 27 | Save/Restore Register 1 — MSR at exception |
| SPRG0–3 | 272–275 | Software-use SPRs (VxWorks uses for per-CPU data) |
| PVR | 287 | Processor Version Register (read-only); **PPC405F6 = `0x20011000`** (⚠ not 0x40110000 which is 405GP) |
| MSR | — | Machine State Register (via `mfmsr`/`mtmsr`) |
| DBCR0 | 1010 (0x3F2) | Debug Control Register 0 |
| DBCR1 | 957 (0x3BD) | Debug Control Register 1 |
| DBSR | 1008 (0x3F0) | Debug Status Register |
| EVPR | 982 (0x3D6) | Exception Vector Prefix Register |
| ESR | 980 (0x3D4) | Exception Syndrome Register |
| DEAR | 981 (0x3D5) | Data Exception Address Register |
| SRR2 | 990 (0x3DE) | Critical Save/Restore Register 0 (40x only) |
| SRR3 | 991 (0x3DF) | Critical Save/Restore Register 1 (40x only) |
| TSR | 984 (0x3D8) | Timer Status Register |
| TCR | 986 (0x3DA) | Timer Control Register |
| CCR0 | 947 (0x3B3) | Core Configuration Register 0 |
| ZPR | 944 (0x3B0) | Zone Protection Register |
| MMUCR | 946 (0x3B2) | MMU Control Register |
| DAC1 | 1014 (0x3F6) | Data Address Compare 1 |
| DAC2 | 1015 (0x3F7) | Data Address Compare 2 |
| ICCR | 1019 (0x3FB) | Instruction Cache Cacheable Regions |
| DCCR | 1018 (0x3FA) | Data Cache Cacheable Regions |

**⚠ 40x vs Book E (PPC440) SPR differences:** The PPC405F6 uses **40x family** SPR numbers, which differ significantly from Book E (PPC440). If you see tooling, scripts, or notes referencing `IVPR` (Book E), `CSRR0/CSRR1` (Book E critical save), or DBSR=0x130 — those are **PPC440 values, not valid here**. Key 40x-specific differences:

| 40x (PPC405F6) ✅ | Book E (PPC440) ❌ | Notes |
|---|---|---|
| `EVPR` SPR 982 | `IVPR` SPR 63 | Exception vector base |
| `DBSR` SPR 1008 | `DBSR` SPR 0x130 | Debug status |
| `DBCR0` SPR 1010 | `DBCR0` SPR 0x134 | Debug control |
| `SRR2`/`SRR3` SPR 990/991 | `CSRR0`/`CSRR1` SPR 58/59 | Critical interrupt save |

### Machine State Register (MSR) — key bits

| Bit | Name | Meaning when set |
|-----|------|-----------------|
| 17 | EE | External Interrupts Enabled |
| 18 | PR | User mode (0 = supervisor) |
| 19 | FP | Floating-point unavailable exception (405 has no FPU — keep 0) |
| 20 | ME | Machine Check Exceptions Enabled |
| 21 | FE0 | FP exception mode 0 |
| 25 | CE | Critical Interrupt Enable |
| 26 | ILE | Instruction Little-Endian |
| 28 | DE | Debug Exceptions Enable |
| 30 | IR | Instruction Relocate (MMU on) |
| 31 | DR | Data Relocate (MMU on) |

**After reset:** MSR = 0 (interrupts disabled, supervisor mode, no MMU, big-endian)

### Exception Vector Table (physical addresses)

| Address | Exception | Handler installed by VxWorks |
|---------|-----------|------------------------------|
| `0x0000` | Reset / Machine check | `romInit` / hardware init |
| `0x0200` | Machine check | VxWorks MC handler |
| `0x0300` | DSI (data storage interrupt) | VxWorks data fault handler |
| `0x0400` | ISI (instruction storage interrupt) | VxWorks instruction fault |
| `0x0500` | External interrupt | VxWorks IRQ dispatcher |
| `0x0600` | Alignment | VxWorks alignment handler |
| `0x0700` | Program (illegal instr, priv viol, trap) | VxWorks program exception |
| `0x0800` | FP unavailable | stub (no FPU on PPC405F6) |
| `0x0900` | Decrementer | VxWorks tick handler |
| `0x0C00` | System call | VxWorks syscall |
| `0x0D00` | Trace | Debug trace handler |
| `0x0F20` | APU unavailable | — |
| `0x1000` | PIT (Programmable Interval Timer) | Timer handler |
| `0x1010` | FIT (Fixed Interval Timer) | — |
| `0x1020` | Watchdog | Watchdog handler |
| `0x1100` | DTLB miss | TLB miss handler |
| `0x1200` | ITLB miss | TLB miss handler |
| `0x2000` | Debug | DBSR debug handler |

**Note:** EVPR (SPR 982) shifts the base of the exception table. At boot EVPR=0, so vectors are at physical 0x0. VxWorks later sets EVPR to keep vectors accessible after possible memory remapping.

**CRITICAL for QEMU debugging:** Before kernelInit (0x5a7f30), the exception vector table
(0x100–0xd00) contains the binary's raw code (not VxWorks handlers). QEMU's SW BP trap
instruction, when it fires before fn_36e168 completes (0x36c3d0), triggers a jump into this
garbage code → crash. **Never place SW BPs inside functions that run between fn_36e168 entry
and kernelInit.** Place BPs only at call/return boundaries in usrInit.

### PPC405 SPR Field Encoding (corrected)

The `mfspr`/`mtspr` instruction encodes the SPR number across two 5-bit fields that are **swapped**:

```
mtspr SPRN, rS  ==>  [6:10]=rS [11:15]=spr[4:0] [16:20]=spr[9:5] [21:30]=467 [31]=0
```

Decoding formula:
```python
spr = ((w >> 11) & 0x1f) << 5 | ((w >> 16) & 0x1f)
```

Examples:
- `0x7C0802A6` → `mflr r0`       (SPR 8 = LR)
- `0x7C0902A6` → `mfctr r0`      (SPR 9 = CTR)
- `0x7C76F3A6` → `mtspr EVPR(982), r3`

**IMPORTANT**: earlier docs had this formula wrong (high/low bits swapped). Always use the
formula above when decoding SPR numbers from raw instruction words.

---

## 2. Ha/Lo Addressing — The Pointer Offset Problem

This is the most common source of confusion when reading PPC disassembly.

### The Problem

PPC has no "load immediate 32-bit" instruction. To load a 32-bit address, the assembler uses two instructions:

```asm
lis  rX, HA(addr)      ; load upper 16 bits (high-adjusted)
addi rX, rX, LO(addr)  ; add signed lower 16 bits
```

or for memory accesses:
```asm
lis  rY, HA(addr)
lwz  rX, LO(addr)(rY)  ; load word from addr
```

### The Ha/Lo Formula

`addi` sign-extends its 16-bit immediate. So if `LO(addr) >= 0x8000`, `addi` will subtract 0x10000 from the result. The assembler compensates by adding 1 to the high word:

```
HA(addr) = (addr + 0x8000) >> 16    ; "high adjusted"
LO(addr) = addr & 0xFFFF             ; raw low 16 bits (interpreted as signed)
```

Result: `lis rX, HA` loads `HA << 16`, then `addi rX, rX, LO` adds the sign-extended `LO`, giving the original `addr`.

### Examples

**Address `0xD2E3E8`:**
```
LO  = 0xE3E8  (≥ 0x8000, so HA is adjusted)
HA  = (0xD2E3E8 + 0x8000) >> 16 = 0xD3E3 >> 4... wait:
    = (0x00D2E3E8 + 0x00008000) >> 16
    = 0x00D36000 >> 16 ... let me redo:
    = (0x00D2E3E8 + 0x00008000) = 0x00D363E8
    >> 16 = 0x00D3
HA  = 0x00D3
LO  = 0xE3E8  (as signed 16-bit = -0x1C18)
```
Assembly: `lis r3, 0xD3` then `addi r3, r3, -0x1C18` → `r3 = 0x00D30000 - 0x1C18 = 0x00D2E3E8` ✓

**Address `0xD30044`:**
```
LO  = 0x0044  (< 0x8000, no adjustment)
HA  = 0x00D3
```
Assembly: `lis r3, 0xD3` then `addi r3, r3, 0x44` → `r3 = 0x00D30044` ✓

**Address `0xe0600000` (UART Lite MMIO — XUartLite base, confirmed):**
```
LO  = 0x0000
HA  = 0xe060
```
Assembly: `lis r3, 0xe060` then no `addi` needed (or `addi r3, r3, 0`)

> ⚠️ WARNING: `lis rX, 0x40xx` is **NOT** an MMIO access — it loads the high word of an
> IEEE 754 floating-point constant. E.g. `0x40600000` = float32 **3.5**; `0x40240000` =
> float64 **10.0**; `0x40590000` = float64 **100.0**. All MMIO is at `0xE0000000+`.

### Quick Reference Table for Common High Bytes

| Address range | lis rX, ? | Notes |
|---------------|-----------|-------|
| `0xC6xxxx` (≥ 0x8000) | `0xC7` | e.g. `0xC6E1A4`: HA=0xC7, LO=0xE1A4 |
| `0xD0xxxx` (≥ 0x8000) | `0xD1` | high byte string table area |
| `0xD2xxxx` (≥ 0x8000) | `0xD3` | SSD whitelist, debug params |
| `0xD3xxxx` (< 0x8000) | `0xD3` | upgrade paths, param names |
| `0xD4xxxx` (≥ 0x8000) | `0xD5` | FLUT data |
| `0xDCxxxx` (≥ 0x8000) | `0xDD` | C++ vtable symbol strings |
| `0xDFxxxx` (< 0x8000) | `0xDF` | driver config table names |
| `0xE0xxxx` (< 0x8000) | `0xE0` | MMIO peripherals (UartLite 0xe0600000, etc.) |
| `0xE0xxxx` (≥ 0x8000) | `0xE1` | MMIO peripherals (XIntc 0xe0800000 → HA=0xE081) |
| `0xE9xxxx` (≥ 0x8000) | `0xEA` | BSS-adjacent variables |
| `0x40xxxx` **⚠️ FLOAT** | — | **IEEE 754 constant, NEVER MMIO** — 0x40240000=10.0, 0x40590000=100.0 |

### Python Helper

```python
def ha_lo(addr):
    ha = (addr + 0x8000) >> 16
    lo = addr & 0xFFFF
    lo_signed = lo if lo < 0x8000 else lo - 0x10000
    return ha, lo_signed

# Find references to address 0xD2E3E8 in binary:
# Look for bytes: 3C XX 00 D3  (lis rX, 0xD3)  followed within ~20 bytes by
#                 38 XX E3 E8  or  80 XX E3 E8  etc. (addi/lwz with -0x1C18)
```

### Searching with r2

```r2
# Find all lis rX, 0xD3  (looking for refs to 0xD2xxxx or 0xD3xxxx range)
/x 3c??00d3

# Find addi with specific lo offset -0x1C18 (0xE3E8):
/x 3800e3e8

# Combine: search for the pair
/x 3c??00d3????????????????????38??e3e8
```

---

## 3. PPC405 Calling Convention

### ABI Summary (EABI / VxWorks)

```
Arguments:    r3–r10 (first 8 integer args, each up to 4 bytes)
              Double-word args: aligned reg pair (r3+r4, r5+r6, etc.)
              Additional args: pushed on stack

Return:       r3 (32-bit) or r3+r4 (64-bit)
              Floating point: f1 (but 405GP has no FPU)

Volatile:     r0, r3–r12, cr0–cr1, cr5–cr7
Saved:        r14–r31 (callee must save/restore), r2, r13
              cr2, cr3, cr4 (callee-saved condition register fields)
              LR (callee must save before any bl instruction)

Stack:        Grows downward; r1 always 8-byte aligned
              r1 points to current frame's bottom
              Word at r1: saved r1 of caller (back-chain pointer)
              Word at r1+4: saved LR (return address)
```

### Stack Frame Layout (after function prologue)

```
High address (caller's r1):
  r1 + 0:  back-chain pointer (caller's r1)
  r1 + 4:  saved LR
  r1 + 8:  saved CR (if needed)
  r1 + 12: saved r14 (if callee-saved regs used)
  ...
  r1 + N:  local variables
  r1 + N+pad: 8-byte aligned bottom (= current r1)
Low address (current r1)
```

### Standard Prologue Pattern

```asm
stwu  r1, -N(r1)    ; allocate N bytes on stack and save old r1
mflr  r0            ; move LR to r0
stw   r0, N+4(r1)   ; save LR to frame
stw   r31, N-4(r1)  ; save callee-saved regs
```

### Standard Epilogue Pattern

```asm
lwz  r0, N+4(r1)    ; restore saved LR
lwz  r31, N-4(r1)   ; restore callee-saved regs
mtlr r0             ; move back to LR
addi r1, r1, N      ; deallocate stack frame
blr                 ; return
```

### Indirect Calls (common with C++ vtables)

```asm
lis  r12, HA(vtable_addr)
lwz  r12, LO(vtable_addr)(r12)   ; r12 = vtable pointer
lwz  r0, OFFSET(r12)              ; r0 = function pointer from vtable
mtctr r0                          ; move to Count Register
bctrl                             ; call via CTR
```

---

## 4. Binary Memory Layout

```
File offset  Runtime addr   Size     Content
-----------  ------------   ------   -------
0x000000     0x00000000     7 MB     Executable code (PPC instructions)
0x700000     0x00700000     2 MB     Mixed code and large data structs
0x900000     0x00900000     4 MB     Embedded resources:
                                       0x942B88  gzip: splash_mx.raw (2009)
                                       0x9C0EDC  gzip: splash.raw (2008)
                                       0x9D2AE0  XML: OSD/UI panel defs (~40KB)
                                       0x9E03BC  SWF v7: GUI (~1.33 MB)
                                       0xB24EF8  SWF v7: alt GUI (~1.35 MB)
                                       (9 SWF files total)
0xC6E1A4     0x00C6E1A4     200KB    XML: parameter definitions
0xD00000     0x00D00000     1 MB     Symbol strings, debug info, vtable names
0xE00000     0x00E00000     580KB    Code tail (BSP init, driver stubs)
0xE8BF20     0x00E8BF20     —        End of file

[NOT IN FILE — runtime only]
0xE9BF20     0x00E9BF20     2.8MB    BSS (zero-initialized at boot)
0x01153480   (BSS end)      —
```

**Total file size:** 15,253,280 bytes (0xE8BF20)

---

## 5. VxWorks Memory Model

### Address Space (no MMU in use — flat physical)

VxWorks on this BSP runs with the MMU disabled (MSR.IR=0, MSR.DR=0). All addresses are physical.

```
0x00000000 – 0x00E8BF1F   Firmware image (text + data + resources)
0x00E9BF20 – 0x01153480   BSS segment (runtime zero-init)
0x01153480 – 0x0FFFFFFF   Heap / task stacks / dynamic allocations

[MMIO — above 0xE0000000]
0xE0000000 – 0xE1FFFFFF   FPGA peripheral registers (via PLB bus, 64KB per slot)
0xE2000000 – 0xE203FFFF   PCI config aperture (256KB window)
0xA0000000 – 0xBFFFFFFF   PCI memory space (512MB window includes 64MB usable)
0xF0000000 – 0xF7FFFFFF   NOR Flash (128MB)
0xFFFF0000 – 0xFFFFFFFF   Boot ROM / VxWorks reset vector (64KB)
```

### Key VxWorks Data Structures

**Symbol Table:** VxWorks maintains a hash table of symbol names → addresses. In Build 32 this is populated at boot from the binary image. C++ symbols are mangled (e.g. `_ZN11UiUsbSerial14runTargetShellEv`). Use `symFind()` API via WDB to look up addresses by name.

**Task Control Block (TCB):** Each VxWorks task has a TCB containing: task ID, priority (0=highest), stack base/size, entry point, errno, registers. Access via `taskTcb(taskId)`.

**WDB Buffer:** The WDB agent allocates a packet buffer in the BSS/heap region. Located near `0xE9C000–0xE9CFFF` area.

### VxWorks Task Priorities (smaller = higher)

| Priority | Purpose |
|----------|---------|
| 0 | Interrupt service routines (not tasks) |
| 1–5 | Kernel/system critical |
| 3 | WDB agent task (confirmed from build 32) |
| 10–50 | Application tasks (camera subsystems) |
| 100–255 | Low priority background |

### Memory Allocation

- `malloc()` / `free()` → VxWorks memLib heap
- `taskSpawn()` → allocates stack from heap; default 8KB (WDB), 20–64KB (app tasks)
- `memPartCreate()` → create sub-pools

---

## 6. MMIO Peripheral Map

> ⚠️ **CRITICAL: 0x40xxxxxx values are IEEE 754 floats, NOT MMIO addresses.**
> The firmware's RED camera math library stores float64/float32 constants in the 0x40xxxxxx
> range: `0x40240000` = float64 **10.0**, `0x40340000` = **20.0**, `0x40590000` = **100.0**,
> `0x40600000` = float32 **3.5**, `0x40C00000` = float32 **6.0**. Any pattern matching
> `lis rX, 0x40??` in the code is loading a float constant, never an MMIO base address.
> The actual MMIO range is **0xE0000000+**.
>
> Evidence: PLB memory-map table at file offset 0xdfbbc8 lists all peripheral base
> addresses using the 0xC7 entry marker. Every entry uses 0xE0xxxxxx (or 0xE1/0xE2/0xA0/0xF0
> for PCI/flash). No 0x40xxxxxx entry exists in that table.

All FPGA peripherals are mapped at `0xE000_0000+` on the PLB bus. PPC405F6 internal
peripherals (SDRAM, EBC, clocks, UIC interrupt controller) use the DCR bus (see Section 7).

### Confirmed IP Core Inventory (from BSP source filenames in firmware symtab)

The firmware symbol table (`0xD00000–0xDFFFFF`) contains the full BSP source paths
`C:/sundance/SW/32_0_3/Sundance/bsp_ppc405_0_revB/ppc405_0_drv_csp/xsrc/<file>`.
These files identify **exactly** which Xilinx EDK IP cores are instantiated in the FPGA:

| Driver source file | Xilinx IP Core | Category |
|--------------------|----------------|----------|
| `xuartlite.c` + `_intr/sinit/stats/selftest/sio_adapter` | xps_uartlite | UART |
| `xuartns550.c` + `_adapter/format/intr/options/selftest/sinit/stats` | xps_uartns550 | UART (16550) |
| `xemaclite.c` + `_end_adapter/intr/selftest` | xps_emaclite | Ethernet MAC |
| `xintc.c` + `_intr/options/selftest` | xps_intc | Interrupt controller |
| `xiic.c` + `_intr/options/selftest/sinit/stats` | xps_iic | I²C controller |
| `xpci.c` + `xpci_config/intr/selftest/v3` | xps_pci_v3 | PCI bridge |
| `xdma_channel.c` + `_sg` | xps_central_dma | DMA engine |
| `xdma_multi.c` + `_sg` | xps_central_dma (multi) | DMA engine |
| `xopbarb.c` + `_selftest` | xps_opbarb | OPB arbiter |
| `xplbarb.c` + `_selftest` | xps_plbarb | PLB arbiter |
| `xipif_v1_23_b.c` | IPIF v1.23b | Common IP interface layer |
| `xio_dcr.c` | — | DCR bus access driver |
| `xversion.c` | — | BSP version strings |

**Absent:** `xtmrctr.c` — timer uses PPC405 internal PIT/FIT/WDT (SPRs), not xps_tmrctr.
**Absent:** `xgpio.c` — GPIO expansion uses PCA9698 I²C expanders accessed via XIic driver.

### PLB Memory Map Table (file offset 0xdfbbc8)

The BSP initialises the PLB address decoder from a table at file offset **0xdfbbc8**.
Entry format (32 bytes each): `[0xc7][0x00][base][0x00][0x00][base][0x10000][0x0fff]`
— 0xc7 marker, base address repeated, size 0x10000 (64KB) for most peripherals.

Found entries (in order, from PLB table at 0xdfbbc8 — 20 entries total):
```
0x0ff9c000  Heap/RAM end marker (size 0x64000 = 400KB, heap boundary sentinel)
0x80000000  PCI memory window (size 0x20000000 = 512MB, secondary PCI aperture)
0xe0600000  XUartLite (UART Lite, 115200 baud)       ← confirmed: config at 0xe005dc
0xe0640000  XUartNs550 #1 (NS16550 UART, 100MHz)     ← confirmed: config at 0xe00600
0xe0650000  XUartNs550 #2 (NS16550 UART, 100MHz)     ← confirmed: config at 0xe00614
0xe0800000  XIntc (Interrupt Controller)              ← confirmed: config table at 0xe003f4
0xe1200000  XPci_v3 register space (64KB, large register window)
0xe1020000  XEmacLite (Ethernet MAC)                 ← confirmed: config at 0xe00390
0xb2600000  XIic (I²C controller)                   ← confirmed: code at 0xdd24-0xdd30 accesses
                                                        RX_FIFO (+0x10C) and ADR (+0x110)
0x64010000  XDmaChannel (DMA engine) — candidate; no code refs found yet
0xe00a0000  Custom RED histogram IP
0xe0200000  Custom RED histogram IP
0xe0100000  Custom RED histogram IP
0xe0120000  Custom RED histogram IP
0xe2000000  PCI config aperture (size 0x40000 = 256KB, exception to 64KB norm)
0xe0080000  Custom RED histogram IP
0xa0000000  PCI memory space (64MB, primary aperture for SiI3512 + ISP1562 BARs)
0xf0000000  NOR Flash (128MB)
0xffff0000  Boot ROM / reset vector (64KB)
[end sentinel: 0x00000000]
```

Device names from interrupt registration table (0xdfbe00) and string area (0xd31fc4+):
- "Luma Histogram", "RGB Histogram", "RGB Comp Histo", "Mono Histogram",
  "Raw Histogram", "RGBRaw Histo", "Luma Waveform" — all custom RED FPGA IP blocks.

### MMIO Base → IP Core Map

Entries marked ✅ confirmed from data-section config tables or QEMU runtime crashes.
Entries marked 🔵 are from PLB map but specific IP core assignment not yet confirmed.
Entries marked ❓ are estimated pending XFoo_Initialize call site analysis.

| MMIO Base | IP Core | Confidence | Evidence |
|-----------|---------|------------|----------|
| `0xe0600000` | **xps_uartlite** | ✅ Confirmed | Config struct at 0xe005dc: baud=115200; QEMU crash at 0xe0600004 (TX FIFO) |
| `0xe0640000` | **xps_uartns550 #1** | ✅ Confirmed | Config struct at 0xe00600: base + 100MHz clock |
| `0xe0650000` | **xps_uartns550 #2** | ✅ Confirmed | Config struct at 0xe00614: base + 100MHz clock |
| `0xe0800000` | **xps_intc** | ✅ Confirmed | Config table at 0xe003f4: DeviceId=0, Base=0xe0800000, 32×default_handler entries |
| `0xe1020000` | **xps_emaclite** | ✅ Confirmed | Config at 0xe00390: [0x00][0xe1020000][TxPP=1][RxPP=1] + 7 VxWorks END adapter fn ptrs |
| `0xb2600000` | **xps_iic** | ✅ Confirmed | Code at 0xdd24-0xdd30: `lis r4, 0xb260; ori r4,r4,0x010c` (RX_FIFO) and `ori r5,r5,0x0110` (ADR) |
| `0xe00a0000` | Custom RED histogram IP | 🔵 PLB table | Device name strings at 0xd31fc4 |
| `0xe0080000` | Custom RED histogram IP | 🔵 PLB table | Device name strings |
| `0xe0100000` | Custom RED histogram IP | 🔵 PLB table | Device name strings |
| `0xe0120000` | Custom RED histogram IP | 🔵 PLB table | Device name strings |
| `0xe0200000` | Custom RED histogram / waveform IP | 🔵 PLB table | "Luma Waveform" string |
| `0xe1200000` | **xps_pci_v3** (register space) | 🔵 PLB table | Large window; PCI bridge for SiI3512 + ISP1562 |
| `0x64010000` | **xps_central_dma** | ❓ Candidate | PLB table; no code references found; XDmaChannel symbols present in binary |
| `0xe2000000` | PCI config aperture | 🔵 PLB table | 256KB window; standard XPci_v3 config access |
| `0xa0000000` | PCI memory window (primary) | 🔵 PLB table | 64MB; PCI device BARs (SiI3512 SATA, ISP1562 USB) |
| `0x80000000` | PCI memory window (secondary) | 🔵 PLB table | 512MB; additional PCI aperture |
| `0xf0000000` | NOR Flash | 🔵 PLB table | 128MB EBC/flash window |
| `0xffff0000` | Boot ROM | 🔵 PLB table | VxWorks reset vector (64KB) |

### xps_intc Register Layout (at 0xe0800000 — confirmed)

Standard Xilinx `XIntc` register map (IPIF v1.23b, EDK 10.1):

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x00` | ISR | Interrupt Status Register (pending and unmasked) |
| `+0x04` | IPR | Interrupt Pending Register |
| `+0x08` | IER | Interrupt Enable Register |
| `+0x0C` | IAR | Interrupt Acknowledge Register (write 1 to clear) |
| `+0x10` | SIE | Set Interrupt Enable |
| `+0x14` | CIE | Clear Interrupt Enable |
| `+0x18` | IVR | Interrupt Vector Register (index of highest-priority active IRQ) |
| `+0x1C` | MER | Master Enable Register (bit0=ME, bit1=HIE hardware enable) |

### xps_iic Register Layout (at 0xb2600000 — confirmed)

Standard Xilinx `XIic` register map:

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x1C` | GIE | Global Interrupt Enable (bit 31 = global enable) |
| `+0x20` | ISR | Interrupt Status Register |
| `+0x28` | IER | Interrupt Enable Register |
| `+0x40` | SOFTR | Software Reset (write 0xA to reset) |
| `+0x100` | CR | Control Register (bit5=TX, bit4=RSTA, bit3=TXAK, bit2=TXRX, bit1=MSMS, bit0=EN) |
| `+0x104` | SR | Status Register (bit6=BB bus-busy, bit5=AAS, bit2=TXFIFO_Empty) |
| `+0x108` | TX_FIFO | Write byte to transmit |
| `+0x10C` | RX_FIFO | Read received byte |
| `+0x110` | ADR | Slave address (7-bit in bits 7:1) |
| `+0x124` | GPO | General Purpose Output (for AuxGpio signals) |

### XEmacLite Register Layout (at 0xe1020000 — confirmed)

Config struct at firmware offset 0xe00390: DeviceId=0, Base=0xe1020000, TxPingPong=1,
RxPingPong=1, IncludeMdio=0. Followed by 7 VxWorks MUX END adapter function pointers
(init, ioctl, send, recv, pollSend, pollRecv, mcastAddrAdd).

**This is the WDB/gdbserver network transport.** To connect WDB agent: set target IP and
connect via wdbserial or wdbnetwork on the XEmacLite MAC.

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x000` | TX buffer (2KB) | Transmit data |
| `+0x07C` | TX length | Bytes to transmit |
| `+0x07E` | TX status/ctrl | Bit 0: TxDone; write 1 to send |
| `+0x800` | RX buffer (2KB) | Received data |
| `+0x87C` | RX length | Bytes received |
| `+0x87E` | RX status/ctrl | Bit 0: RxEmpty (0 = data ready) |
| `+0xFFC` | MAC address | First 4 bytes of MAC |

### Xilinx UART Lite Register Layout (at 0xe0600000 — confirmed)

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x00` | RX FIFO | Read received byte |
| `+0x04` | TX FIFO | Write byte to transmit |
| `+0x08` | Status | Bit 0: RX valid; Bit 2: TX full; Bit 3: TX empty |
| `+0x0C` | Control | Bit 0: Reset TX FIFO; Bit 1: Reset RX FIFO; Bit 4: Enable interrupts |

**Baud rate:** Fixed at 115200 (confirmed from XUartLite SIO config struct at 0xe005dc,
field `baud_rate = 0x0001C200`). FIFO depth: 2048 bytes (0x800).

### First MMIO Accesses in Boot (crash candidates in QEMU)

> Note: `lis r0, 0x4010` and similar 0x40xx patterns are **float constant loads**,
> not MMIO accesses. Do NOT stub addresses in the 0x40000000–0x5FFFFFFF range.

```
0x0000DCB0   sysHwInit_seq   → calls sub at 0x1C8BC repeatedly (device enable codes)
0x001C18DC   sysSerialInit   → accesses UART Lite at 0xe0600000
0xe0600004   TX FIFO         → QEMU MCE patch #37 (NOP TX write)
0xe0600008   Status reg      → QEMU MCE patch #38 (NOP status read)
0xe0be00xx   Unknown custom  → QEMU MCE patches #39–41 (fn_9B78 MMIO write)
```

---

## 7. DCR (On-Chip Peripheral) Map

The PPC405F6 (Xilinx Virtex-4 hard-macro) has on-chip peripherals accessible via the Device Control Register (DCR) bus. ⚠ **`bamboo` machine uses PPC440 with wrong PVR family — see Section 15 for correct QEMU setup.** DCR `mtdcr`/`mfdcr` for unknown registers silently returns 0 on most QEMU PPC405 targets — these should not cause crashes.

| DCR Range | Peripheral | Key registers |
|-----------|------------|---------------|
| `0x010–0x01F` | SDRAM0 | `0x010`: Config; `0x011`: Status; `0x018`: Timing |
| `0x020–0x02F` | EBC0 (External Bus) | `0x023`: Address Decode 0; per-bank config |
| `0x0A0–0x0AF` | PLB arbiter | Bus arbitration |
| `0x0C0–0x0CF` | CPC0 (Clock/Power) | `0x0C3`: PLLMR0 (PLL config); `0x0C4`: PLLMR1 |
| `0x0D0–0x0DF` | UIC0 (Interrupt Ctrl) | `0x0D0`: Status; `0x0D2`: Enable; `0x0D3`: Critical enable |
| `0x0E0–0x0EF` | UIC1 (cascade) | Second interrupt controller |
| `0x100–0x107` | DMA channel 0 | DMA transfers |
| `0x108–0x10F` | DMA channel 1 | |
| `0x200–0x20F` | MAL (Memory Access Layer) | Ethernet DMA engine |
| `0x400–0x4FF` | OPB arbiter | On-chip peripheral bus |

### PPC405F6 (Virtex-4) On-Chip Memory (OCM) DCR Block (ug018)

The Virtex-4 PPC405F6 has an OCM (On-Chip Memory) controller accessed via DCR bus.
The DCR base is set by FPGA input port `TIEDCRADDR[0:5]`. **Offsets from that base:**

| DCR offset | Register | Function |
|------------|----------|----------|
| +0 | ISINIT | ISOCM init data (write-only) |
| +1 | ISFILL | ISOCM fill (write-only) |
| +2 | ISARC | ISOCM address — upper 8 CPU address bits compared against BRAM |
| +3 | ISCNTL | ISOCM control: bit0=enable, bit2=DCR readback, bit3=auto-ratio, bits4:7=MCM ratio |
| +4 | UDICFG | APU UDI config |
| +5 | APUCFG | APU config |
| +6 | DSARC | DSOCM address — upper 8 CPU address bits |
| +7 | DSCNTL | DSOCM control: bit0=enable, bit3=auto-ratio, bits4:7=MCM ratio |

**QEMU note:** OCM is likely disabled in the RED BSP (no `xtmrctr.c`, no OCM driver in
source list). On `ref405ep` or custom PPC405 QEMU target, unknown `mtdcr`/`mfdcr` returns 0 (disabled), which is the correct state.

### Important: EVPR Register

EVPR (SPR 982) sets the upper 16 bits of the exception vector base address. Default at reset = 0 (vectors at 0x0). The firmware sets EVPR to 0 during BSP init and should keep it there for QEMU compatibility.

**Critical bug in Build 13 (patched):** Function at `0x2EEE20` calls `0x2F2D0C` which writes to EVPR SPR, moving exception vectors. Once moved, any QEMU debug trap goes to an unmapped address → instant crash. The equivalent function in Build 32 must be identified and patched similarly.

---

## 8. Boot Sequence — Step by Step

### Phase 0: Reset (0x0000)

```asm
0x0000:  b 0x8                   ; skip 8 bytes
0x0008:  li r4, 0
         mtmsr r4                ; MSR = 0 (disable interrupts, big-endian, no MMU)
         mttbl r4 / mttbu r4     ; clear timebase
         mticcr r4               ; disable instruction cache
         mtdccr r4               ; disable data cache
         iccci / dccci            ; invalidate caches
0x0084:  lis r1, 0x0001          ; SP = 0x00010000 ← PATCH FOR QEMU (see §9)
0x0088:  addi r1, r1, 0          ; (nop effectively)
0x008c:  addi r1, r1, -0x10      ; SP = 0x0000FFF0
0x00A4:  bl 0x36C350             ; → main boot init (usrInit equivalent)
0x00A8:  bl 0x124                ; → infinite halt loop (never reached)
```

### Phase 1: Hardware Init Sequence (`0x36C350`)

1. **DRAM ready spin-poll** (`0x36C380–0x36C394`):  
   Waits for RAM at `0xE269A0/A4` to equal DRAM test markers `0x5A5AC3C3` / `0x12348765`.  
   Written by secondary DRAM init path on real hardware. **Must be patched for QEMU** (NOP the `bne` branches).

2. **BSS zero-init** (`0x36C398–0x36C3AC`):  
   `memset(0xE9BF20, 0, 0x2B7560)` — zeroes 2.8MB BSS segment.

3. **Hardware sequencer** (`0xDCB0`):  
   `sysHwInit_seq` — enables subsystems. Calls `0x1C8BC` repeatedly with device IDs.  
   First MMIO accesses — likely crash point for QEMU.

4. **UART init** (`0x1C18DC`):  
   `sysSerialInit` — configures XUartLite at `0xe0600000`.  
   After this, VxWorks console output starts (boot messages).

5. **fn_36860c** (`0x36860c`): Task creation preflight — spawns conditional tasks  
   (only if certain globals are non-zero; skipped at cold boot → passes quickly in QEMU).

6. **Memory boundary setup** (`0xD8A0`): Computes `heap_end = 0x0FF9C000`  
   (`256MB - 0x64000`), stores to `[0xE0C380]`.

7. **`kernelInit()`** (`0x5A7F30`) called from `0x36C424` with:
   ```
   r3 = 0x37C440       ; rootTask function pointer
   r4 = 0x5DC0         ; root task stack = 23,936 bytes
   r5 = pMemPoolStart  ; computed from BSS end (0x01153480 area)
   r6 = 0x0FF9C000     ; pMemPoolEnd = heap_end
   r7 = 0x1388         ; interrupt stack = 5,000 bytes
   r8 = 0              ; lockOutLevel
   ```

8. **rootTask** at `0x37C440`: spawned by kernelInit as the first task.  
   Calls `usrRoot()` → spawns all application tasks.

9. **`usrRoot()` / `usrAppInit()`**:  
   Spawns all application tasks:
   - File system init (TFFS, ATA CF, USB mass storage)
   - Network init (XEmacLite driver, DHCP/static IP)
   - WDB agent (`usrWdbInit` at `0x36B3DC`) — **always spawned**
   - Camera subsystem tasks (sensor, FPGA, video pipeline, UI/OSD)

10. **Upgrade check** (`SmartUpgrade`):  
    Searches these paths in order:
    ```
    /tffs0/upgrade/redone.su
    /ata00:1/upgrade/redone.su
    /ata10:1/upgrade/redone.su
    /sdmc/upgrade/redone.su
    /usbd0/upgrade/redone.su
    ```

---

## 9. DRAM Ready Spin-Poll — QEMU Patch

### The Problem

At boot offset `0x36C380`, the firmware spins waiting for two DRAM test marker values to appear in RAM. On real hardware, these are written by the DRAM controller initialization sequence after memory is validated. In QEMU, RAM is zero-initialized and nothing writes these values → **boot hangs forever**.

### Canary Details

```
Expected value 1:  *(0x00E269A4) == 0x12348765
Expected value 2:  *(0x00E269A0) == 0x5A5AC3C3

Disassembly:
0x36C358:  lis r9, 0x1234      ; r9  = 0x12340000
0x36C35C:  lis r10, 0x5A5A     ; r10 = 0x5A5A0000
0x36C370:  ori r9, r9, 0x8765  ; r9  = 0x12348765
0x36C374:  ori r10, r10, 0xC3C3 ; r10 = 0x5A5AC3C3
0x36C378:  lis r11, 0xE2       ; r11 = 0x00E20000
0x36C37C:  lis r8, 0xE2        ; r8  = 0x00E20000

; ← SPIN LOOP STARTS HERE:
0x36C380:  lwz r0, 0x69A4(r11) ; r0 = *(0x00E269A4)
0x36C384:  cmpw cr7, r0, r9    ; compare to 0x12348765
0x36C388:  bne cr7, 0x36C380   ; ← PATCH 1: 0x409EFFF8 → 0x60000000 (NOP)

0x36C38C:  lwz r0, 0x69A0(r8)  ; r0 = *(0x00E269A0)
0x36C390:  cmpw cr7, r0, r10   ; compare to 0x5A5AC3C3
0x36C394:  bne cr7, 0x36C380   ; ← PATCH 2: 0x409EFFEC → 0x60000000 (NOP)
```

### Patches Required

| File offset | Original bytes | Replacement | Description |
|-------------|---------------|-------------|-------------|
| `0x36C388` | `40 9E FF F8` | `60 00 00 00` | NOP first canary `bne` |
| `0x36C394` | `40 9E FF EC` | `60 00 00 00` | NOP second canary `bne` |
| `0x000084` | `3C 20 00 01` | `3C 20 08 00` | Relocate SP from 64KB to 128MB mark |

### Additional Patches (MMIO stubs — find at runtime)

> First MMIO crashes will be in the 0xe0xxxxxx range (confirmed: 0xe0600004 TX FIFO = patch #37).
> `lis r0, 0x4010` patterns are float constant loads — ignore them.
> Use QEMU `--debug` mode to find crash points at unmapped 0xe0xxxxxx addresses. Document each in `patch_firmware.py`.

---

## 9a. Phase 2/3 QEMU Patches — Discovered at Runtime

Applied in addition to the Phase 1 patches above. All offsets are also runtime addresses (firmware loads at 0x0).

Run `cd firmware && python3 scripts/patch_firmware.py` to apply all patches and produce `software.patched.bin`.

### Complete Patch Table (44 patches — current as of session 8)

| # | Phase | Offset | Description |
|---|-------|--------|-------------|
| 1 | 1 | `0x000084` | SP reloc: `lis r1,1` → `lis r1,0x800` (SP=0x07FFFFD0) |
| 2 | 1 | `0x36C388` | NOP canary `bne` #1 (spins until `*(0xE269A4)==0x12348765`) |
| 3 | 1 | `0x36C394` | NOP canary `bne` #2 (spins until `*(0xE269A0)==0x5A5AC3C3`) |
| 4 | 2 | `0x36FA1C` | `beq` → `b`: skip SSL string-as-fn-ptr bctrl in fn_36F9F8 |
| 5 | 2 | `0x36C3AC` | NOP BSS memset — QEMU RAM already zero, saves ~15 s |
| 6 | 2 | `0xE26D2C` | Data: zero restart callback (was `0x00000008` — ROM reset entry) |
| 7 | 2 | `0xE293B4` | Data: null C++ RTTI ptr (was `0xE38B4C` — illegal instruction) |
| 8–9 | 2 | `0xE293BC`, `0xE293B0` | Null additional C++ dispatch fn ptrs in same struct |
| 10–11 | 2 | `0x387DD8` region | Guard bcopy call — null r10 was passing 2 GB count |
| 12 | 2 | `0x387834` | Unconditional branch past crash paths in fn_387834 |
| 13 | 2 | `0x36E038` | Bypass 1st corrupted bctrl dispatch (LR=0x36E03C confirmed) |
| 14 | 2 | `0x36E12C` | Bypass 2nd corrupted bctrl dispatch (infinite loop guard) |
| 15–20 | 2 | `0x36DC2C`, `0x36DCEC`, `0x370EDC`, `0x370EE4`, `0x370FD0`, `0x370FD8` | NOP/bypass 3rd–8th corrupted bctrl dispatch sites |
| 21–33 | 2 | BSS data | Null 13 sentinel `0xFFFFFFFF` values used as fn-ptrs (BSS memset skipped by Patch #5) |
| 34–35 | 3 | `0x5D58B8`, `0x5D58E8` | SSD whitelist bypass: IsCompatible always returns 1 |
| 36 | 2 | `0x62CC` | NOP null bctrl in fn_6288 — CTR=0 after fn_2748 clears ptr; bctrl→0x0 resets |
| 37 | 2 | `0x1B9EC` | NOP XUartLite TX-FIFO write (0xe0600004 unmapped → MCE per char) |
| 38 | 2 | `0x1B9D8` | NOP XUartLite status read (0xe0600008 unmapped; result unused after #37) |
| 39 | 2 | `0x9B78` region | NOP fn_9B78 early path: MMIO write to 0xe0be00 → MCE |
| 40 | 2 | `0x9B9C` | NOP fn_9B78 normal path: same unmapped MMIO (0xe0be00) |
| 41 | 2 | `0x9BC0` | NOP fn_9B78 second MMIO write in normal path |
| 42 | 2 | `0x548d80` | NOP `bl fn_4a6438` in fn_548d78 (dead code — fn_548d78 never called at runtime) |
| 43 | 2 | `0x548d88` | blr at fn_548d78+0x10 (dead code safety — fn_548d78 never called at runtime) |
| **44** | **2** | **`0x458a40`** | **KEY FIX: bctrl → `li r3,0` in fn_458a14 — bypasses dispatch to fn_37cd4c (stack frame mismatch crash)** |

**sha256 of current patched binary:** `b2a63a78d7606a0cb75486cbc03038e08f0f0470b43e8a270c4c325611bc8d8c`

### fn_458a14 dispatch table — static vs runtime

**CRITICAL:** The dispatch table pointer at `0xe29310` has TWO values:
- **Static binary value:** `0x00548d78` — stale, written at link time, NOT the runtime value
- **Runtime value:** `0x0037cd4c` — written at boot by init code at `0x36cc64-0x36cc68`

The init code runs (via fn_36e3dc → fn_36cb6c) BEFORE fn_458a14 is called. fn_548d78 is
never reached via the dispatch table at runtime. Patches #42 and #43 are dead-code safety
patches; Patch #44 is the actual fix.

`fn_37cd4c` is the **epilogue** of `fn_37cc94` (40-byte frame). Calling it from fn_458a14's
16-byte frame causes a stack frame size mismatch: epilogue reads garbage registers and blrs to
a bad LR → crash. Patch #44 replaces `bctrl` with `li r3, 0`, bypassing the call entirely.
usrInit ignores the return value of both fn_458a14 calls.

### Current Boot State (session 8 — 44 patches)

With all 44 patches applied, confirmed via single-step tracing:
- **fn_36e168** completes — VxWorks exception handlers installed at 0x200, 0x300, etc.
- **fn_DCB0** completes — hardware sequencer runs to completion
- **fn_458a14(r3=0)** → Patch #44: returns 0 cleanly ✓ (confirmed: NIP=0x36c3e0, r3=0)
- **fn_458a14(r3=1)** → Patch #44: returns 0 cleanly ✓ (confirmed: NIP=0x36c3e8, r3=0)
- **fn_36860c** entered at 0x36860c — not yet confirmed to complete

**fn_36860c analysis (static):** No direct MMIO access. All 7 sub-calls are VxWorks
task-spawn/messaging functions with guard checks (`[0xFCA3C0] != 0` etc.) that skip
the spawns at cold boot. fn_36860c should pass quickly in QEMU.

**After fn_36860c → fn_D8A0 (x2) → kernelInit at 0x36C424:**
- fn_D8A0 computes `heap_end = 0x0FF9C000` (256MB − 0x64000); no MMIO.
- No MMIO blockers found between fn_36860c return and kernelInit.

**Next milestone:** BP at `0x36C424` (kernelInit). If it fires, next BP at `0x37C440` (rootTask).
If fn_36860c stalls, single-step its 7 sub-calls: 0x445434, 0x5ACC58, 0x43C4FC, 0x448520, 0x5B0A84, 0x498CD8, 0x5B75E8.

### Session 8 — Critical GDB RSP Operational Notes

**SW BP trap crashes (DISCOVERED THIS SESSION):**
- QEMU SW BPs use a PPC trap instruction. When the trap fires, the CPU takes a Program Check
  exception (vector 0x700). Before fn_36e168 installs proper handlers, 0x700 contains raw
  binary code — not a handler. This causes an immediate crash, creating a phantom restart loop.
- **Symptom:** BP at call-site X fires repeatedly; BP at target function entry never fires.
- **Fix:** ONLY place BPs at call/return boundaries in usrInit. Never inside any function
  that executes between 0x36c3d0 (fn_36e168 entry) and 0x36c424 (kernelInit).
- **Note:** After fn_36e168 completes, VxWorks handlers ARE installed, but the Program Check
  handler at 0x700 may still mishandle QEMU's trap instruction. Continue using boundary-only BPs.

**Write watchpoints DO work on QEMU PPC405:**
- `Z2,addr,4` (write watchpoint) and `Z4,addr,4` (access watchpoint) accepted with `$OK#9a`
- Used successfully to catch runtime writes to `0xe29310` (dispatch table populate)
- Useful for "who writes this memory?" questions

**Stale BPs persist between sessions — ALWAYS clear at start:**
```python
for bp in [all addresses ever used in prior sessions]:
    gdb_cmd(s, f'z0,{bp:x},4')  # E22 response = wasn't set; OK = cleared
```

**GDB restart (`R00`) resets the CPU but preserves SW BPs in QEMU memory.**

### fn_DCB0 — `sysHwInit_seq` Full Disassembly

fn_DCB0 is the hardware sequencer. It initialises subsystems one by one, printing a progress
digit ('1'–'9') to UART before each call:

```
0xDCB0: mflr r0                         ; prologue
0xDCB4: stwu r1, -16(r1)
0xDCBC: stw r0, 20(r1)                  ; save LR
0xDCB8: li r3, 0x5E ('^')
0xDCC0: bl fn_1C8BC                     ; print '^'
0xDCC4: li r3, 0x5E
0xDCC8: bl fn_1C8BC                     ; print '^'
0xDCCC: li r3, 0x5E
0xDCD0: bl fn_1C8BC                     ; print '^'
0xDCD4: li r3, 0x31 ('1')
0xDCD8: bl fn_1C8BC                     ; print '1'
0xDCDC: li r3, 0
0xDCE0: bl fn_372054                    ; mtspr EVPR, r3 (set exception vectors to base 0)
0xDCE4: li r3, 0x32 ('2')
0xDCE8: bl fn_1C8BC                     ; print '2'
0xDCEC: li r4, 0
0xDCF0: li r3, 0
0xDCF4: bl fn_DC28                      ; init fn (skips fn_443F20 since r3=0)
0xDCF8: li r3, 0x33 ('3')
0xDCFC: bl fn_1C8BC                     ; print '3'
0xDD00: bl fn_9BC8                      ; *** LIKELY CRASH POINT ***
0xDD04: (after fn_9BC8 — checkpoint 1)
0xDD08-0xDD13: store result to 0xEA_C390
0xDD14: bl fn_9E24
0xDD18: li r3, 0x34 ('4')
0xDD1C: bl fn_1C8BC                     ; print '4'
0xDD20: bl fn_1968
0xDD24: (after fn_1968 — checkpoint 2)
0xDD3C: bl fn_19C
0xDD40: (after fn_19C — checkpoint 3)
0xDD44: li r3, 0x35 ('5')
0xDD48: bl fn_935C
0xDD4C: li r3, 0x36 ('6')
0xDD50: bl fn_1C8BC                     ; print '6'
0xDD54: bl fn_92C4
0xDD58: (after fn_92C4 — setup MMIO addresses)
0xDD80: bl fn_1C8BC                     ; print '7'
0xDD84: bl fn_A2D0
0xDD88: li r3, 0x38 ('8')
0xDD8C: bl fn_1C8BC                     ; print '8'
0xDD94: bl fn_1C8BC                     ; print '9'
0xDD9C: bl fn_1C8BC                     ; print CR (0x0D)
0xDDA4: bl fn_1C8BC                     ; print LF (0x0A)
0xDDB4: blr                             ; return to usrInit + 0x24
```

**Confirmed trivial functions** (not the crash point):
- `fn_372054` at `0xDCE0`: just `mtspr EVPR, r3; blr` — sets exception vector base to 0
- `fn_DC28` at `0xDCF4`: called with r3=0; since r3==0 the conditional `bl fn_443F20` is skipped; returns immediately

**Next target**: `fn_9BC8` (called at `0xDD00`). This is the first call after confirming
UART prints '^^^123' work. fn_9BC8 has not been analysed yet and is the prime suspect for
the blocking call.

### Next Steps — Isolate fn_DCB0 Blocking Call

**Known script bug (fixed in next session):** The `resume()` helper must NOT call `recv()` after
sending `$c#63`. If T05 arrives while `recv()` is draining, it gets lost and `wait_bp()` never
sees the breakpoint. Correct pattern:

```python
def resume(s):
    s.send(b'$c#63')
    # DO NOT recv here — wait_bp() will see the T05

def wait_bp(s, timeout=90):
    t0 = time.time()
    while time.time()-t0 < timeout:
        try:
            d = s.recv(4096)
            if b'T05' in d or b'T03' in d: return True
        except socket.timeout: pass
    return False
```

**GDB RSP sequence for next session:**

```python
# 1. Halt QEMU (send interrupt byte)
s.send(b'\x03'); time.sleep(0.5); s.recv(4096)  # drain T02

# 2. Set SW-BPs at early fn_DCB0 checkpoints (before fn_9BC8)
send_cmd(s, 'Z0,DCB0,4')   # fn_DCB0 entry
send_cmd(s, 'Z0,DCE4,4')   # after fn_372054 (between '1' and '2')
send_cmd(s, 'Z0,DCF8,4')   # after fn_DC28 (between '2' and '3')
send_cmd(s, 'Z0,DD04,4')   # after fn_9BC8 ← the key one
send_cmd(s, 'Z0,DD18,4')   # after fn_9E24
send_cmd(s, 'Z0,DD24,4')   # after fn_1968
send_cmd(s, 'Z0,DD40,4')   # after fn_19C
send_cmd(s, 'Z0,DD4C,4')   # after fn_935C
send_cmd(s, 'Z0,DD58,4')   # after fn_92C4
send_cmd(s, 'Z0,DD88,4')   # after fn_A2D0
send_cmd(s, 'Z0,DDB4,4')   # fn_DCB0 blr (fn completes!)

# 3. Resume — DO NOT recv after this
s.send(b'$c#63')

# 4. wait_bp() loop: for each hit, step past BP, re-arm, resume
```

The **first checkpoint that never fires** is in the function that blocks or crashes.
Once identified, disassemble that function to find the hardware poll loop and add a patch.

---

## 10. Key Function Addresses

### Boot & Init

| Address | Function | Description |
|---------|----------|-------------|
| `0x00000000` | `romInit` / reset vector | Hardware init, exception table |
| `0x00000124` | halt loop | `b 0x124` — infinite loop |
| `0x00371F30` | `sysPvrGet` (candidate) | `mfspr r3, PVR(287)` → returns `0x20011000`; raw instr `0x7C7F42A6` |
| `0x0000DCB0` | `sysHwInit_seq` / `fn_DCB0` | Hardware sequencer — completes with patches 1–41 |
| `0x0000D8A0` | timer/clock helper | Called from `0x36C3F0/F8` |
| `0x00012D90` | MMIO dispatch table | Large switch on peripheral base |
| `0x001C18DC` | `sysSerialInit` | XUartLite init at 0xe0600000 |
| `0x001C1A0C` | first UART Lite access | `lis rX, 0xe060` in serial init |
| `0x0036B3DC` | `usrWdbInit` | WDB agent init — always called |
| `0x0036B7EC` | BSP init caller | Calls `usrWdbInit`, spawns WDB task |
| `0x0036C350` | `usrInit` | Main boot init |
| `0x0036E168` | `fn_36e168` | VxWorks exc handler installer; writes MC handler to 0x200 |
| `0x00458A14` | `fn_458a14` | Driver dispatch — **PATCHED** (Patch #44: bctrl→li r3,0; returns 0 for both calls) |
| `0x00496698` | `memset` | BSS zero-init target |
| `0x004A5F00` | `fn_4a5f00` | Historical crash site (fn_4a5f44: bctrl to 0x203c6000) — no longer reached at runtime |
| `0x004A6438` | `fn_4a6438` | Core library fn (600+ callers); called by fn_36e168 chain |
| `0x00548D78` | `fn_548d78` | Driver init stub; bytes copied by fn_36e168 as exc handler stubs. **Never reached via dispatch table at runtime** |
| `0x0037CC94` | `fn_37cc94` | 40-byte frame function; fn_37cd4c is its epilogue |
| `0x0037CD4C` | `fn_37cd4c` | Epilogue of fn_37cc94 — RUNTIME dispatch table entry 0 (would crash fn_458a14; bypassed by Patch #44) |
| `0x0037CE78` | `fn_37ce78` | RUNTIME dispatch table entry 1 (mid-function of fn_37cc94) |
| `0x0036860C` | `fn_36860c` | Called after both fn_458a14 calls (usrInit:0x36c3ec) — 7 sub-calls, conditional task spawning (guards prevent execution at cold boot) |
| `0x005A7F30` | `kernelInit` | VxWorks kernel init — MILESTONE (usrInit:0x36c424) |
| `0x0037C440` | `rootTask` | First VxWorks task spawned by kernelInit; calls usrRoot() |

**usrInit layout (0x36c350):**
```
0x36c3cc: bl fn_36e3dc        <- pre-init (sets dispatch table via 0x36cc64)
0x36c3d0: bl fn_36e168        <- VxWorks exc handler install
0x36c3d4: bl fn_DCB0          <- hardware sequencer
0x36c3d8: li r3, 0
0x36c3dc: bl fn_458a14 r3=0   <- PATCHED: Patch #44 → returns 0 ✓
0x36c3e0: li r3, 1
0x36c3e4: bl fn_458a14 r3=1   <- PATCHED: Patch #44 → returns 0 ✓
0x36c3e8: addis r29,r0,0xea   <- overwrites r3; return value ignored
0x36c3ec: bl fn_36860c        <- conditional task spawns (guard-checked; passes in QEMU)
0x36c3f0: bl fn_0000d8a0      <- heap_end = 0x0FF9C000
0x36c3f4: stw r3, [0xE9C630]  <- store heap_end
0x36c3f8: bl fn_0000d8a0      <- early return (already set)
... arithmetic: compute pMemPoolStart from heap_end and BSS end ...
0x36c40c: lis r3, 0x38        <- r3 = rootTask fn ptr (becomes 0x37C440)
0x36c414: addi r3, r3, -0x3bc0
0x36c418: addi r4, r0, 0x5dc0  <- rootTask stack = 0x5DC0 bytes
0x36c41c: addi r7, r0, 0x1388  <- int stack = 5000 bytes
0x36c420: addi r8, r0, 0x0
0x36c424: bl 0x5a7f30         <- kernelInit(rootTask, stackSz, poolStart, poolEnd, intSz, 0)
0x36c43c: blr                 <- usrInit end
```

### WDB Agent

| Address | Function | Description |
|---------|----------|-------------|
| `0x0036B3DC` | `usrWdbInit` | WDB init; sets port 17185 at `0xE9C4BC` |
| `0x005A153C` | `wdbEndPktDevInit` | Init WDB over Ethernet END driver |
| `0x005A2A28` | WDB task spawn | Spawns WDB task (priority 3, stack 8KB) |
| `0x0036B5C4` | WDB initialized/BP install | Final WDB setup step |

### Camera Subsystems

| Address | Function / Class | Description |
|---------|----------|-------------|
| `0x0036B3DC` | WDB init | Always-on remote debug |
| TBD | `UiUsbSerial::runTargetShell` | Spawns VxWorks shell over USB |
| TBD | `UiUsbSerial::ProcessUsbDebugChange` | Callback on param change |
| TBD | `UpgradeMC::SmartUpgrade` | Firmware upgrade state machine |

### Exception Vectors (confirmed)

| Address | Handler |
|---------|---------|
| `0x0200` | Machine check |
| `0x0300` | DSI (data fault) |
| `0x0400` | ISI (instruction fault) |
| `0x0500` | External interrupt |
| `0x0600` | Alignment exception |
| `0x0700` | Program exception |
| `0x0900` | Decrementer (tick timer) |

---

## 11. Key Data & BSS Addresses

### BSS Layout

| Symbol | Address | Value / Notes |
|--------|---------|---------------|
| `bss_start` | `0x00E9BF20` | Zero-init start; `memset` called at boot |
| `bss_end` | `0x01153480` | Zero-init end |
| BSS size | — | `0x002B7560` = 2,848,096 bytes |
| WDB port var | `0x00E9C4BC` | Stores value `17185` (0x4321) |
| Canary addr 1 | `0x00E269A4` | Expected: `0x12348765` (in BSS region) |
| Canary addr 2 | `0x00E269A0` | Expected: `0x5A5AC3C3` |

### PVR Value Locations in Binary

| Address | Value | Context |
|---------|-------|---------|
| `0xD177A4` | `0x20011000` | PVR lookup table — entry for Virtex-4 FX PPC405F6 |
| `0xD17961` | `0x20011000` | Comparison table — alongside Virtex-2 Pro entry (`0x20010000`) |

These confirm the firmware targets PPC405F6 (`0x20011000`), **not** PPC405GP (`0x40110000`).
The constant `0x40110000` does not appear anywhere in the binary.

### Key Static Data Addresses (dispatch table / fn_458a14)

| Address | Static Binary Value | Runtime Value | Purpose |
|---------|---------------------|---------------|---------|
| `0xe29310` | `0x00548D78` (stale) | `0x0037cd4c` | fn_458a14 dispatch table entry 0 |
| `0xe29314` | `0x005489F8` (stale) | `0x0037ce78` | fn_458a14 dispatch table entry 1 |
| `0xe2b528` | `0x00000117` | — | Integer ID (not a pointer); caused fn_4a5f00 crash (historical) |
| `0xe26d2c` | `0x00000000` | — | Zeroed by Patch #6 (was 0x8 = ROM reset entry) |
| `0xe26a5c` | `0x0000000F` | — | Read by fn_36e168 prologue (`cmpwi r12,1`) |

**Dispatch table init code:** At `0x36cc64-0x36cc68` (inside fn_36cb6c, called from fn_36e3dc):
```asm
lis  r5,  0xe3;  addi r5,  r5,  -27888   ; r5  = 0x00e29310 (table base)
lis  r11, 0x38;  addi r11, r11, -12980   ; r11 = 0x0037cd4c (entry 0)
lis  r10, 0x38;  addi r10, r10, -12680   ; r10 = 0x0037ce78 (entry 1)
stw  r11, 0(r5)                           ; *(0xe29310) = 0x37cd4c
stw  r10, 4(r5)                           ; *(0xe29314) = 0x37ce78
```
This runs before fn_458a14 is called; the static binary value is never used at runtime.

### Parameter Strings & Data (in `.rodata`/data segment)

| Address | String / Data | Notes |
|---------|---------------|-------|
| `0xD2E3E8` | `RedRAM\0` | SSD whitelist entry 1 |
| `0xD2E3F0` | `RedRAID\0` | SSD whitelist entry 2 |
| `0xD2E3F8` | `LEXAR ATA FLASH CARD\0` | CF card |
| `0xD2E410` | `RED 16GB CF\0` | |
| `0xD2E41C` | `RED 32GB CF\0` | |
| `0xD2E428` | `RED 64GB CF\0` | |
| `0xD2E434` | `RED 55GB SSD \0` | |
| `0xD2E444` | `RED 64GB SSD \0` | |
| `0xD2E454` | `RED 128GB SSD \0` | |
| `0xD2E464` | `RED 256GB SSD \0` | Target model |
| `0xD2E474` | `RED 512GB SSD \0` | |
| `0xD2E484` | `/ata00:1\0` | Drive mount path |
| `0xD2E4F8` | `DRIVE0`, `NOTPRESENT`... | Drive state enum strings |
| `0xD30044` | `/tffs0/altshell` | Alternate shell path |
| `0xD3632F` | `/tffs0/upgrade/redone.su` | Upgrade search path 1 |
| `0xD3634D` | `/ata00:1/upgrade/redone.su` | Upgrade search path 2 |
| `0xD35928` | `DEBUG.USB.CONNECTION` | USB debug enable param name |
| `0xD4C50C` | `/roFs/tty0app.hex` | TTY app firmware path |
| `0xD5C608` | `xemaclite(0,0)host:vxWorks h=192.168.0.1 e=192.168.0.2 u=xemhost` | Boot config string |
| `0xDCB3BC` | `_ZTV11UiUsbSerial` | C++ vtable: UiUsbSerial class |
| `0xDF7930` | `XUartLite_ConfigTable` | UART Lite config table symbol |
| `0xDF7B3C` | `XUartNs550_ConfigTable` | 16550 UART config table symbol |

---

## 12. Debug Interfaces — Quick Reference

### Option A: WDB (Wind River Debug) — BEST FIRST CHOICE

**Status:** Always-on. No authentication. No camera modification needed.

```
Camera IP:  192.168.0.2
Host IP:    192.168.0.1/24
Protocol:   UDP port 17185 (0x4321)
Transport:  XEmacLite Ethernet
```

**Setup:**
```bash
# Linux: set host IP
ip addr add 192.168.0.1/24 dev eth0

# Connect with open-source wdbrpc client:
wdbrpc 192.168.0.2 17185

# OR use Wind River Workbench IDE (free download with registration)
# Target: UDP 192.168.0.2:17185
```

**WDB capabilities:** Memory read/write, task list, register read/write, breakpoints, symbol table lookup, function call injection.

**Enable USB shell via WDB:**
1. Find BSS address of `DEBUG.USB.CONNECTION` variable (TBD — scan BSS for param struct)
2. `wdbMemWrite(<addr>, 1, 4)` — write 1 to enable
3. USB shell spawned on camera USB port

### Option B: USB Shell

**Hardware:** NET2280 USB-to-PCI bridge (on AUDIO_PCI board) → USB device port on camera.

**Trigger:** Set `DEBUG.USB.CONNECTION` parameter to non-zero (via WDB or Ethernet param API).

**On Linux host:** Device appears as `/dev/ttyUSB0` (CDC-ACM virtual serial).  
**Gives:** VxWorks interactive shell.

### Option C: UART Serial

**XUartLite** (FPGA, at `0xe0600000` — confirmed):
- Fixed baud rate 115200 (confirmed from config struct at 0xe005dc)
- FIFO depth 2048 bytes; likely connected to debug/serial console

**XUartNs550** (16550-compatible):
- Programmable baud rate
- Likely the external RS-232 port on the CONTROL connector
- Look up `XUartNs550_ConfigTable` at `0xDF7B3C` for base address and baud rate

**Physical access:** RED ONE CONTROL connector (26-pin) includes RS-232 TX/RX signals. Use a USB-RS232 adapter or 3.3V LVTTL adapter (check voltage levels first with a multimeter).

**Try:** 115200 8N1 first. Also try 9600 8N1.

### Option D: Telnetd

Compiled in but requires a shell to be installed first. Once USB shell or altshell is active, telnetd listens on port 23 over the camera's Ethernet interface.

### Option E: altshell (`/tffs0/altshell`)

If a binary named `altshell` exists at `/tffs0/altshell` on the camera's NOR flash, it's loaded at boot instead of the normal shell. Write via WDB: create file via TFFS API calls.

### Option F: Hardware JTAG (PPC405 + FPGA TAP chain)

Both the PPC405 processor TAP and the Virtex-4 FPGA TAP are in the **same JTAG chain** on
the camera PCB (accessed via the JTAG header pins). Wind River Probe/ICE or a
Xilinx Platform Cable can be used. A `.brd` board file specifying the chain order is required.

**Virtex-4 FPGA JTAG instruction codes** (10-bit IR, ug071):

| IR (10-bit) | Instruction | Purpose |
|-------------|-------------|---------|
| `1111000100` | CFG_OUT | Readback FPGA config via JTAG |
| `1111000101` | CFG_IN | Configure FPGA via JTAG |
| `1111001001` | IDCODE | Read device IDCODE (returns `0x01EE4093` for XC4VFX100) |
| `1111001011` | JPROGRAM | Reset/clear config memory (same as PROG_B pulse) |
| `1111001100` | JSTART | Clock startup sequence after config |
| `1111001101` | JSHUTDOWN | Clock shutdown sequence before reconfig |
| `1111001000` | USERCODE | Read user-defined code |
| `1111001010` | HIGHZ | Tri-state all I/Os |

**PPC405F6 JTAG instruction codes** (4-bit IR, ug018):

| IR (4-bit) | Instruction |
|------------|-------------|
| `1111` | PPC_BYPASS |
| `0101` | PPC_DEBUG_1 |
| `0111` | DEBUG_2 |
| `1001` | DEBUG_3 |
| `1010` | DEBUG_4 |
| `1011` | DEBUG_5 |
| `1100` | DEBUG_6 |
| `1101` | DEBUG_7 |
| `1110` | DEBUG_8 |

**Notes (ug018):**
- `TRST` is **not implemented** in the Virtex-4 FPGA device — leave floating or tie high
- `TCK` max rate = **½ CPU clock** (if CPU = 400 MHz → max TCK = 200 MHz; use ≤33 MHz in practice)
- Hardware debug signals: `DBGC405DEBUGHALT`, `DBGC405UNCONDDEBUGEVENT`, `C405DBGWBFULL`, `C405DBGWBIAR[0:29]`

---

## 13. VxWorks Internals Cheat Sheet

### Key API Addresses (Build 32 — find with WDB `symFind`)

| Function | Purpose |
|----------|---------|
| `taskSpawn(name, pri, opts, stacksz, entry, arg0..9)` | Spawn new task |
| `taskDelay(ticks)` | Sleep N system ticks |
| `taskSuspend(tid)` / `taskResume(tid)` | Pause/resume task |
| `taskDelete(tid)` | Kill task |
| `memPartAlloc(partId, nBytes)` | Allocate from memory partition |
| `shellSpawn(name, loginEnabled)` | Start interactive shell |
| `shellInit(stackSz, options)` | Initialize shell subsystem |
| `symFindByName(sysSymTbl, name, pValue, pType)` | Look up symbol by name |
| `wdbMemRead(src, len, dst)` | WDB: read memory |
| `wdbMemWrite(dst, len, src)` | WDB: write memory |
| `tffsRawio(drive, cmd, args)` | Low-level TFFS flash I/O |

### Shell Commands (once VxWorks shell active)

```
i                   # list tasks
d <addr>            # dump memory as hex/ASCII
m <addr> = <val>    # write memory
l <addr>            # disassemble at address
ld 1,0,"<path>"     # load object module from file
ts <taskId>         # task suspend
tr <taskId>         # task resume
sp <funcAddr>       # spawn a task (call function)
period <n>,<func>   # call function every n ticks
```

### WDB Protocol Notes

- WDB uses a simple RPC-over-UDP protocol (port 17185)
- No authentication or encryption
- Can call any function by address: `wdbFuncCall(addr, arg0..4)`
- Can read/write any memory: `wdbMemRead`, `wdbMemWrite`
- Debug-level access: full register read/write, task listing, breakpoints
- Open-source clients: `wdbrpc` (Python), `tornado2` (Wind River SDK, free download)

---

## 14. Firmware Package Format

### File Structure of `redone.su`

```
redone.su                  ← POSIX tar archive
├── redone.1               ← AES-256-CBC encrypted gzip of software.bin
├── redone.2               ← AES-256-CBC encrypted (splash screen or VP-FPGA)
├── redone.3               ← AES-256-CBC encrypted gzip of fpga.bin (I/O FPGA)
└── redone.4               ← AES-256-CBC encrypted (config / version manifest)
```

### Decryption

```bash
# Key (public — see firmware/README.md):
PASS='M1H5gwOXh757rIRVY6Gj2tN080AYSX03'

# Decrypt redone.1 → software.bin:
openssl enc -d -aes-256-cbc -md md5 \
    -pass "pass:$PASS" \
    -in redone.1 | gunzip > software.bin

# Decrypt redone.3 → fpga.bin:
openssl enc -d -aes-256-cbc -md md5 \
    -pass "pass:$PASS" \
    -in redone.3 | gunzip > fpga.bin
```

### Re-encryption (for modified firmware)

```bash
PASS='M1H5gwOXh757rIRVY6Gj2tN080AYSX03'

# Re-encrypt software.bin → redone.1:
gzip -c software.patched.bin | \
    openssl enc -e -aes-256-cbc -md md5 \
    -pass "pass:$PASS" \
    -out redone.1.new

# Package into redone.su:
cp redone.2 redone.2.new   # keep originals for non-modified components
cp redone.3 redone.3.new
cp redone.4 redone.4.new
tar cf redone.su.new redone.1.new redone.2.new redone.3.new redone.4.new

# Install: copy redone.su.new to CF card at upgrade/redone.su
# Boot camera with CF inserted → SmartUpgrade() auto-detects
```

### Camera Upgrade Search Order

The firmware searches these paths at boot (in order):
1. `/tffs0/upgrade/redone.su` — internal NOR flash
2. `/ata00:1/upgrade/redone.su` — CF card slot 0
3. `/ata10:1/upgrade/redone.su` — CF card slot 1
4. `/sdmc/upgrade/redone.su` — SD card
5. `/usbd0/upgrade/redone.su` — USB device

---

## 15. QEMU Setup & Usage

### ⚠ Critical: QEMU Machine Selection

**`-machine bamboo` is WRONG for this firmware.** Bamboo is a PowerPC 440 evaluation board
(`ppc440ep` CPU, PVR = `0x422218XX`). The RED firmware runs on a **PowerPC 405F6**
(PVR = `0x20011000`). Using bamboo causes a PVR family mismatch and the VxWorks BSP will
fail its CPU version check at boot.

| Machine | CPU | PVR | Status |
|---------|-----|-----|--------|
| `bamboo` | ppc440ep | `0x422218xx` | ❌ Wrong CPU family |
| `ref405ep` | ppc405ep | `0x40120483` | ⚠ Best available in QEMU ≤ 8.2.0 (removed in 8.3+) |
| `virtex4-ml410` | ppc405f6 | `0x20011000` | ✅ Correct — **does not exist yet, must be written** |

> ⚠️ **QEMU 10.x (current environment)**: `ref405ep` is REMOVED. Available machines are
> `bamboo` (PPC440) and `virtex-ml507` (Virtex-5/PPC440) — both use wrong CPU family.
> To use QEMU for this firmware, either: (a) build QEMU 8.2.0 from source, or
> (b) write `hw/ppc/virtex4_ml410.c` custom machine for any QEMU version.

**Short-term (pin to QEMU 8.2.0 — build from source):**
```bash
# Build QEMU 8.2.0 from source (ref405ep present):
git clone https://gitlab.com/qemu-project/qemu.git qemu-8.2
cd qemu-8.2 && git checkout v8.2.0
./configure --target-list=ppc-softmmu --prefix=/opt/qemu-8.2
make -j$(nproc) && make install
# Use ref405ep — PVR 0x20010820 (Xilinx family prefix matches, close enough)
/opt/qemu-8.2/bin/qemu-system-ppc -machine ref405ep -cpu x2vp4 ...
```

**Long-term:** Write `hw/ppc/virtex4_ml410.c` (~300 lines) based on the existing
`virtex_ml507.c` (which is PPC440, Virtex-5) but substituting ppc405f6 CPU + correct DCR map.
Key fields to set: `PVR = 0x20011000`, memory at 0x0, MMIO at 0xe0000000+, no PCIe.

### Prerequisites

```bash
# Install QEMU 8.2.0 (last version with ref405ep):
# Build from source or use distro package; verify:
qemu-system-ppc --version    # must be <= 8.2.0 for ref405ep

# Install radare2:
apt install radare2

qemu-system-ppc --machine ref405ep,help   # confirm machine is available
```

### Launch (Build 32 — normal mode)

```bash
cd firmware/
qemu-system-ppc \
    -machine ref405ep \
    -m 256M \
    -nographic \
    -device "loader,file=reverse/build_32/extracted/software.patched.bin,addr=0x0,force-raw=on" \
    -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on"
```

### Launch (Debug mode — r2 GDB stub)

```bash
# Terminal 1: start QEMU paused
qemu-system-ppc \
    -machine ref405ep \
    -m 256M \
    -nographic \
    -S -gdb tcp::1234 \
    -device "loader,file=reverse/build_32/extracted/software.patched.bin,addr=0x0,force-raw=on" \
    -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on"

# Terminal 2: attach radare2
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -D gdb gdb://localhost:1234 \
   -i scripts/r2_debug.r2
```

### Launch (with Ethernet for WDB)

```bash
# Create TAP interface first (once, as root):
ip tuntap add dev tap0 mode tap
ip addr add 192.168.0.1/24 dev tap0
ip link set tap0 up

# Launch QEMU with networking:
qemu-system-ppc \
    -machine ref405ep \
    -m 256M \
    -nographic \
    -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
    -device xemaclite,netdev=net0,mac=00:0a:35:00:00:01 \
    -device "loader,file=reverse/build_32/extracted/software.patched.bin,addr=0x0,force-raw=on" \
    -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on"
```

### Crash Diagnosis Workflow

```bash
# Enable crash logging:
qemu-system-ppc ... -d int,cpu_reset 2>crash.log

# Find crash address in log:
grep "PC=" crash.log | head -5

# Disassemble crash site with r2:
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -q -c "pd 8 @ 0x<CRASH_ADDR>" \
   reverse/build_32/extracted/software.bin

# Add patch:
python3 scripts/patch_firmware.py --probe 0x<CRASH_ADDR>
# Copy the Patch entry output → add to KNOWN_PATCHES in patch_firmware.py
```

### GDB RSP Debugging — Correct Protocol (CRITICAL)

#### Known QEMU PPC405 Bug: Hardware Breakpoints (Z1) Don't Work

- **SW-BPs (Z0)** — WORK: replace instruction with PPC `trap`, QEMU traps it before firmware
- **HW-BPs (Z1)** — BROKEN on this target: `Z1,addr,4` never fires on QEMU PPC405
- **Write watchpoints (Z2/Z4)** — WORK: successfully used to catch runtime writes to data
- **Always use `Z0`, never `Z1`**

#### CRITICAL: Where SW BPs Are Safe

QEMU's SW BP trap instruction fires the CPU's Program Check exception (vector 0x700).
**Before fn_36e168 completes (0x36c3d0), the vector table contains raw binary code**, not
handlers → crash. **After fn_36e168** VxWorks handlers are installed, but placing BPs INSIDE
functions that fn_458a14 or fn_36860c call is still risky.

**Safe rule:** Place BPs ONLY at call/return boundaries in usrInit:
- ✅ `bl fn_X` in usrInit (the bl instruction itself)
- ✅ Return address after a bl (first instruction of next call)  
- ❌ Inside fn_X body (function entry, middle, or epilogue)

#### Stale BPs — Must Clear at Session Start

QEMU preserves SW BPs as long as it's running. Old BPs from prior sessions cause phantom
crashes. **ALWAYS clear all previously-used addresses at session start:**

```python
stale_bps = [0x36c3dc, 0x36c3e0, 0x36c3e4, 0x36c3e8, 0x36c3ec, 0x36c3f0, 0x36c424,
             0x458a14, 0x458a3c, 0x458a40, 0x458a44, 0x36860c, 0x36c43c]
for bp in stale_bps:
    gdb_cmd(s, f'z0,{bp:x},4')  # E22 = wasn't set (OK); OK = cleared
```

#### Connection + BP Protocol

Always halt QEMU before setting/clearing BPs:

```python
import socket, time

def gdb_connect(port=1237):
    s = socket.socket(); s.settimeout(5); s.connect(('localhost', port))
    return s

def halt(s):
    """Send interrupt and drain the T02 stop signal."""
    s.send(b'\x03')
    time.sleep(0.5)
    try: s.recv(4096)
    except: pass

def send_cmd(s, cmd, timeout=5):
    cs = sum(ord(c) for c in cmd) & 0xFF
    s.send(f'${cmd}#{cs:02x}'.encode())
    buf = b''; t0 = time.time()
    while time.time()-t0 < timeout:
        try:
            chunk = s.recv(8192)
            if chunk:
                s.send(b'+')
                buf += chunk
                # complete packet = $..#xx
                st = buf.find(b'$')
                if st >= 0 and b'#' in buf[st+1:] and len(buf) > buf.find(b'#', st+1)+2:
                    break
        except socket.timeout: break
    return buf

def get_regs(s):
    r = send_cmd(s, 'g', 10)
    # Find the long register packet (not T02/T05 stop packets)
    i = 0
    while i < len(r):
        if r[i:i+1] == b'$':
            end = r.find(b'#', i+1)
            if end >= 0:
                d = r[i+1:end]
                if len(d) >= 36*8:
                    def reg(n): return int(d[n*8:(n+1)*8], 16)
                    return reg(32), reg(35), reg(1)  # NIP, LR, SP
            i = end+3 if end >= 0 else i+1
        else:
            i += 1
    return 0, 0, 0

def set_bp(s, addr):  send_cmd(s, f'Z0,{addr:X},4')
def clr_bp(s, addr):  send_cmd(s, f'z0,{addr:X},4')
def step(s):          send_cmd(s, 's', 5)

def resume(s):
    """IMPORTANT: Do NOT recv after $c — let wait_bp() catch T05."""
    s.send(b'$c#63')

def wait_bp(s, timeout=60):
    """Returns (hit:bool, nip, lr, sp). Halts QEMU on return."""
    t0 = time.time()
    buf = b''
    while time.time()-t0 < timeout:
        try:
            d = s.recv(4096)
            buf += d
            if b'T05' in buf or b'T03' in buf:
                nip, lr, sp = get_regs(s)
                return True, nip, lr, sp
        except socket.timeout: pass
    return False, 0, 0, 0
```

#### Typical BP-Step-Resume loop

```python
s = gdb_connect(1237)
halt(s)                    # ← ALWAYS halt before setting BPs

set_bp(s, 0xDCB0)          # fn_DCB0 entry
resume(s)                  # DO NOT recv after this

hit, nip, lr, sp = wait_bp(s, 60)
if hit:
    print(f"Stopped at 0x{nip:08X}")
    clr_bp(s, nip)         # clear before stepping
    step(s)                # single-step past the trap
    nip2, _, _ = get_regs(s)
    print(f"After step: 0x{nip2:08X}")
    set_bp(s, nip)         # optionally re-arm
    resume(s)

# Close cleanly (QEMU resumes when socket closes)
s.close()
```

#### QEMU State Recovery

If QEMU stops responding (socket recv hangs), it may be stopped with a pending T05:

```python
s = gdb_connect(1237)
s.send(b'+')               # ACK any pending packet
time.sleep(0.2)
s.send(b'$?#3f')           # query stop reason
r = s.recv(4096)
print(repr(r))             # should show T02/T05
s.send(b'+')
# then send_cmd('g') to read regs
```

---

## 16. radare2 Workflow

### Initial Setup

```bash
# Open for static analysis (no execution):
r2 -a ppc -b 32 -e cfg.bigendian=true \
   reverse/build_32/extracted/software.bin

# Inside r2:
e asm.arch=ppc
e asm.bits=32
e cfg.bigendian=true

# Label key symbols:
f sym.romInit        @ 0x00000000
f sym.usrInit        @ 0x0036C350
f sym.sysSerial      @ 0x001C18DC
f sym.usrWdbInit     @ 0x0036B3DC
f sym.bss_start      @ 0x00E9BF20
f sym.bss_end        @ 0x01153480
f sym.halt_loop      @ 0x00000124
```

### Common r2 Commands for PPC RE

```r2
# Disassembly
pdf @ sym.usrInit          # disassemble function at usrInit
pd 20 @ 0x36C350           # disassemble 20 instructions at address
pI 0x40 @ 0x36C350         # disassemble 0x40 bytes

# Search
/x 3c??00d3                # find: lis rX, 0xD3 (load high for D2/D3 addresses)
/x 409efff8                # find specific bytes
/x 60000000                # find NOPs
/ DEBUG.USB.CONNECTION     # find string in binary

# Analysis
aa                         # auto-analyze (basic)
aaa                        # full analysis (slow, ~10 min for 15MB)
afl                        # list all functions found
axl @ sym.usrInit          # list cross-refs from usrInit
axt @ sym.usrWdbInit       # find callers of usrWdbInit

# Memory / Data
x/16wx @ 0xD2E3E8         # hex dump at SSD whitelist
ps @ 0xD5C608              # print string at boot config
pv @ 0xE9C4BC             # print value at WDB port BSS var

# Registers (GDB mode only)
dr                         # show all registers
dr pc                      # show PC
dr r1                      # show stack pointer

# Debugging (GDB mode)
dc                         # continue
ds                         # single step
db 0x36C350               # set breakpoint at usrInit
dbc 0x36C350              # clear breakpoint
```

### Ha/Lo Decode One-Liner

```bash
# Given a 32-bit address, compute lis/addi values:
python3 -c "
addr = 0xD2E3E8
ha = (addr + 0x8000) >> 16
lo = addr & 0xFFFF
lo_s = lo if lo < 0x8000 else lo - 0x10000
print(f'lis rX, {ha:#x}    ; loads {ha<<16:#010x}')
print(f'addi rX, rX, {lo_s}  ; +({lo_s:#06x})')
print(f'Result: {addr:#010x}')
"
```

---

## 17. Ghidra Setup

### Import Settings

1. **File** → Import `reverse/build_32/extracted/software.bin`
2. **Format:** Raw Binary
3. **Language:** `PowerPC:BE:32:4xx`  ← **CRITICAL: must use `4xx`, NOT `default`**
   - The `4xx` variant adds PPC405-specific opcodes: `dcread`, `icread`, `dlmzb`, `mfdcr`, `mtdcr`
   - Using `default` misses these instructions and produces incorrect decompilation
4. **Base address:** `0x00000000`
5. **Entry point:** `0x00000000`

### Post-Import Setup

1. Run **Auto Analyze** with:
   - `Aggressive Instruction Finder` ✓
   - `Decompiler Parameter ID` ✓
   - `Stack Analysis` ✓

2. Mark data regions (prevents bad code analysis):
   - `0x900000 – 0xCFFFFF` → Data (resources, XML, SWF)
   - `0xD00000 – 0xDFFFFF` → Data (string tables)

3. Add bookmarks / labels:
   ```
   0x00000000  romInit_reset
   0x0036C350  usrInit_main
   0x001C18DC  sysSerialInit
   0x0000DCB0  sysHwInit_seq
   0x0036B3DC  usrWdbInit
   0x00E9BF20  bss_start
   0x01153480  bss_end
   0x00D5C608  boot_config_string
   0x00D2E3E8  ssd_whitelist_start
   ```

4. **Data type for C++ vtables:** Search for `_ZTV` strings → these are vtable class names. The preceding 4-8 bytes contain RTTI pointers, followed by function pointers.

### Useful Ghidra Scripts for PPC

```python
# Find all function calls to a target address (Python script in Ghidra):
from ghidra.app.util.opinion import PeLoader
target = toAddr(0x36B3DC)  # usrWdbInit
refs = getReferencesTo(target)
for r in refs:
    print(r.getFromAddress(), r.getReferenceType())
```

---

## 18. Firmware Modification Workflow

### 1. Identify Patch Target

Use r2 or Ghidra to locate the exact instruction bytes to change.

### 2. Add to `patch_firmware.py`

```python
# In KNOWN_PATCHES list:
Patch(
    offset=0xXXXXXX,          # file offset = runtime address
    original=b'\xAA\xBB\xCC\xDD',  # verify original bytes
    replacement=PPC_NOP,       # or PPC_BLR or custom bytes
    description="What this does and why we patch it",
    phase=2,
),
```

### 3. Apply and Test

```bash
# Apply patches:
python3 firmware/scripts/patch_firmware.py \
    --input firmware/reverse/build_32/extracted/software.bin \
    --output firmware/reverse/build_32/extracted/software.patched.bin

# Test in QEMU:
./firmware/scripts/qemu_boot.sh --patched
```

### 4. Repackage for Camera

```bash
./firmware/scripts/repackage_firmware.sh \
    --input firmware/reverse/build_32/extracted/software.patched.bin \
    --build-dir firmware/reverse/build_32/extracted/ \
    --output /tmp/redone.su

# Copy to CF card:
mkdir -p /mnt/cf/upgrade
cp /tmp/redone.su /mnt/cf/upgrade/redone.su
```

### Priority Modification Targets

| Target | Location | Goal |
|--------|----------|------|
| SSD whitelist bypass | `0xD2E3E8` area | Accept any SATA drive |
| Shell always-on | `usrInit` / `shellInit` call | Skip `DEBUG.USB.CONNECTION` check |
| WDB always-on | Already always-on (no patch needed) | Confirm WDB task spawned |
| IP address change | BSS / boot config | Change from 192.168.0.2 |
| Version string spoof | `0x5A83D8` area | Report fake version |

---

## 19. Physical Camera Debug Interfaces

### UART (CONTROL Connector)

The RED ONE CONTROL connector is a 26-pin female connector on the camera body. It provides:
- RS-232 serial (for lens control / external control)
- Timecode I/O
- Genlock/sync
- Power (optional)

**Likely pin assignment (verify with oscilloscope):**
- Pins 1–2: RS-232 TX/RX (at ±12V RS-232 levels — need MAX232 adapter!)
- Pins 3–5: Timecode
- GND: Pins 13 or 26

**Safety:** RS-232 is ±12V. Do NOT connect directly to 3.3V UART — use a proper RS-232 level shifter (e.g., MAX3232) or a commercial USB-RS232 adapter.

**Baud rate:** Start with 115200 8N1. Also try 9600, 38400, 57600.

**Expected output:** VxWorks boot messages starting with:
```
VxWorks WIND kernel version 2.10
Copyright Wind River Systems, Inc., 1984-2006
```

### WDB Ethernet Connection

1. Connect straight Ethernet cable: camera ↔ host Ethernet port
2. Set host IP: `ip addr add 192.168.0.1/24 dev eth0`
3. Boot camera fully (allow ~60 seconds)
4. Connect: `wdbrpc 192.168.0.2 17185`

**Note:** The camera must be fully booted for WDB to respond. The WDB agent is spawned relatively late in the boot sequence.

### Information to Collect from Live Camera (via WDB)

```bash
# 1. Full memory dump (software region):
wdbrpc 192.168.0.2 17185 memread 0x00000000 0x00E9BF20 > live_software.bin
# Compare to build 32 — any differences = runtime modifications or different build

# 2. BSS dump (runtime state):
wdbrpc 192.168.0.2 17185 memread 0x00E9BF20 0x002B7560 > live_bss.bin

# 3. Task list:
wdbrpc 192.168.0.2 17185 tasklist

# 4. Symbol table lookup:
wdbrpc 192.168.0.2 17185 symfind DEBUG.USB.CONNECTION

# 5. Parameter values via WDB funcCall:
# Call camera's param get API to read current config
```

---

## 20. Embedded Resources Map

Resources embedded in the firmware binary (`software.bin`):

| Offset | Type | Description |
|--------|------|-------------|
| `0x672824` | gzip | Internal blob (purpose TBD) |
| `0x7D7BFC` | gzip | Internal blob (purpose TBD) |
| `0x942B88` | gzip | `splash_mx.raw` — Mysterium-X splash screen (2009-12-16) |
| `0x9C0EDC` | gzip | `splash.raw` — alternate splash (2008-07-14) |
| `0x9D2AE0` | XML v1.0 | OSD/UI panel definitions (~40KB) |
| `0x9E03BC` | SWF v7 | GUI Flash animation 1 (~1.33 MB) |
| `0xB24EF8` | SWF v7 | GUI Flash animation 2 (~1.35 MB) |
| `0xC6E1A4` | XML v1.0 | Parameter definitions (~200KB) — camera config schema |
| `0xDEF5D0` | StuffIt | Internal data tables |
| 9 total | SWF | GUI files total |

### Extracting Resources

```bash
# binwalk extraction (already done):
ls firmware/reverse/build_32/extracted/_software.bin.extracted/

# Manual extraction of XML at 0x9D2AE0:
python3 -c "
data = open('software.bin','rb').read()
# Find end of XML (look for '</Params>' or similar closing tag)
start = 0x9D2AE0
end = data.index(b'</root>', start) + 7  # adjust tag name
open('osd_params.xml','wb').write(data[start:end])
"

# Extract parameter XML at 0xC6E1A4:
# This file defines ALL camera parameters — their names, types, defaults
# Very useful for finding DEBUG.USB.CONNECTION and other param BSS offsets
```

### Parameter XML Schema

The XML at `0xC6E1A4` defines all camera parameters. Each entry has the form:
```xml
<Param name="DEBUG.USB.CONNECTION" type="integer" value="0" min="0" max="1"/>
```

These parameter definitions map directly to BSS variables. Parsing this XML gives us the complete list of writable camera parameters, which is the primary attack surface for firmware modification via WDB.

---

## 21. FPGA Bitstream Analysis (fpga.bin)

### Header Verification

`fpga.bin` (4,133,176 bytes, SHA-256: `497d8f37613b235469666557edc0eadf0d96f8a6f784817284ec0dfdd2827f10`):

```
$ file fpga.bin
fpga.bin: Xilinx RAW bitstream (.BIN)

Offset 0x00: FF FF FF FF          — sync pad
Offset 0x04: AA 99 55 66          — SYNC WORD ✓ (big-endian, SelectMAP/JTAG format)
Offset 0x08: 20 00 00 00          — NOP
Offset 0x0C: 30 00 80 01 (header) — Type1 WRITE CRC wc=1
Offset 0x10: 00 00 00 07          — CRC=7 (RCRC command follows)
...
Offset 0x24: 30 01 80 01 (header) — Type1 WRITE KEY wc=1
Offset 0x28: 01 EE 40 93          — KEY register = 0x01EE4093 (DES auth key or ignored)
```

> ⚠️ **Correction**: Offset 0x28 is the **KEY register value**, NOT the IDCODE.
> No WRITE_IDCODE packet was found in the bitstream — the bitstream skips device checking.

**Key:** The bitstream is **unencrypted** — AES-256 encryption was NOT used.
The sync word is readable in plaintext, confirming full readback and analysis is possible.

### Actual Packet Sequence

Parsed from fpga.bin (full output):
```
0x0000000c  Type1 WRITE CMD = RCRC      (reset CRC)
0x0000001c  Type1 WRITE COR = 0x000435E5 (Configuration Options Register)
0x00000024  Type1 WRITE KEY = 0x01EE4093 (DES key; bitstream is NOT encrypted)
0x0000002c  Type1 WRITE CMD = SWITCH
0x00000038  Type1 WRITE MASK = 0x00000600
0x00000040  Type1 WRITE CTL  = 0x00000600  ← PERSIST bit set (JTAG stays active)
  ...
0x00001240  Type1 WRITE MASK = 0x00000600
0x00001248  Type1 WRITE CTL  = 0x00000000
0x00001250  Type1 WRITE CMD  = NULL
0x0000125c  Type1 WRITE FAR  = 0x00000000  (start at frame 0)
0x00001264  Type1 WRITE CMD  = WCFG
0x00001270  Type1 WRITE FDRI wc=0          (Type 2 header follows)
0x00001274  Type2 WRITE wc=1031970         (4,127,880 bytes = 4,031 KB of frame data)
0x003f0f00  Type1 WRITE CRC  = 0xFEDCC5DD  (end CRC)
0x003f0f08  Type1 WRITE CMD  = GRESTORE
0x003f0f14  Type1 WRITE CMD  = LFRM
0x003f10ac  Type1 WRITE CMD  = GRESTORE
0x003f10b8  Type1 WRITE CMD  = NULL
0x003f10c4  Type1 WRITE FAR  = 0x00015300  (final FAR reference)
0x003f10cc  Type1 WRITE CMD  = START
0x003f10e8  Type1 WRITE CRC  = 0x0C011D96
0x003f10f0  Type1 WRITE CMD  = DESYNC
```

**CTL = 0x600**: Bit 9 (PERSIST) + Bit 10 (security) set → JTAG interface STAYS ACTIVE
after configuration. This means the JTAG TAP chain is accessible while the camera runs!

**No IDCODE check**: Bitstream will load on any Xilinx device without checking device ID.

### Frame Structure (ug071)

All Virtex-4 frames are fixed at **41 × 32-bit words = 1312 bits**.

**Frame Address Register (FAR) bit layout:**

| Bits | Field | Description |
|------|-------|-------------|
| 22 | Top/Bottom | 0 = top half of device, 1 = bottom half |
| 21:19 | Block type | `000`=CLB/IO/CLK  `001`=BRAM interconnect  `010`=BRAM data  `011`=CFG_CLB |
| 18:14 | Row address | |
| 13:9 | Column address | |
| 5:0 | Minor address | |

To extract BRAM content (calibration tables, sensor LUTs):
filter for FAR block type = `010` frames.

### Configuration Commands (CMD register codes, ug071)

| Hex | Name | Purpose |
|-----|------|---------|
| `0001` | WCFG | Write configuration data |
| `0011` | LFRM | Last frame (end of config data) |
| `0100` | RCFG | Read configuration (start readback) |
| `0101` | START | Begin startup sequence |
| `0110` | RCAP | Reset capture |
| `0111` | RCRC | Reset CRC |
| `1000` | AGHIGH | Assert GHIGH |
| `1001` | SWITCH | Switch to new configuration |
| `1010` | GRESTORE | Restore global state |
| `1011` | SHUTDOWN | Shutdown — required before reconfiguration |

### JTAG Readback Sequence (ug071)

```
1. JSHUTDOWN (IR=1111001101)     → clock shutdown via TCK
2. CFG_IN    (IR=1111000101)     → send RCFG + FDRO packets
3. CFG_OUT   (IR=1111000100)     → drain frame data
4. JSTART    (IR=1111001100)     → complete startup
```

Readback data: one pad frame (all zeros) precedes actual frame data. No CRC performed.
Mask file (`.msk`): bit `0` = compare, bit `1` = ignore (mask out routing/config registers
that change every run).

### ICAP — Runtime Reconfiguration Status

> **Result: NO ICAP driver present in firmware.**
>
> Searched for: XHwIcap strings, ICAP sync words (0xAA995566 / 0x665599AA), ICAP DCR
> access patterns, `hwicap`/`ICAP` symbol table entries — ALL returned zero results.
>
> Conclusion: The PPC405 firmware does NOT runtime-reconfigure the FPGA via ICAP.
> The FPGA is configured at power-on from dedicated NOR flash or via JTAG. FPGA
> "firmware updates" likely use a separate mechanism (SPI flash reprogramming via JTAG,
> not PPC405 runtime access).

**Two FPGAs in the RED ONE MX** (discovered from firmware strings):

| Internal name | Role | Update mechanism |
|---------------|------|-----------------|
| `iofpga` | I/O FPGA (Xilinx Virtex-4 FX) — PPC405 host, histograms, connectivity | `DrvInitIofpga`, `ColorMatrixToIofpga` — via JTAG/SPI flash |
| `vpfpga` | Video Processing FPGA — sensor pipeline, encoding | `DrvInitVpfpga`, `ColorMatrixToVpfpga` — via JTAG/SPI flash |

Key firmware symbols: `IoFPGAVersionGet`, `_sundance_targeted_iofpga`, `_sundance_targeted_vpfpga`,
`_ZN10ExecModule22EXEC_RAMDISK_FPGA_SIZEE` (FPGA bitstream stored in RAMDISK).

**CTL PERSIST bit = enabled** → JTAG access to both FPGAs is possible while camera runs.

---

## 22. Recommended Toolchain

### vxhunter — VxWorks Symbol Extraction

`vxhunter` (PAGalaxyLab/vxhunter, at `/tmp/vxhunter/`) can annotate Ghidra/radare2 scripts.
However, **our firmware uses a non-standard symbol table format** that vxhunter's auto-detection
fails to recognize. Use the custom extractor instead:

```bash
# Custom extractor (already run — 18,044 symbols at /tmp/r1mx_symbols.txt):
python3 - <<'EOF'
import struct
with open("firmware/reverse/build_32/extracted/software.bin","rb") as f:
    data = f.read()
SYM_START, SYM_END, SYM_ENTRY, STR_START = 0xE2BC5C, 0xE85C48, 20, 0xD85508
symbols = []
for i in range(SYM_START, SYM_END, SYM_ENTRY):
    nameoff = struct.unpack_from(">I", data, i+4)[0]
    val = struct.unpack_from(">I", data, i+8)[0]
    if STR_START <= nameoff < SYM_START:
        ne = data.find(b'\x00', nameoff)
        symbols.append((val, data[nameoff:ne].decode('ascii','replace')))
for val, name in sorted(symbols):
    print(f"0x{val:08x}\t{name}")
EOF
```

Symbol table: 18,044 entries at file offsets 0xE2BC5C–0xE85C48 (20 bytes each).
Format: [flags:2B][pad:2B][name_addr:4B][dest_addr:4B][group:4B][type:4B]

vxhunter Ghidra scripts (at `/tmp/vxhunter/firmware_tools/ghidra/`) can still be used to
apply the extracted symbol list as function names in Ghidra.

### Ghidra Language — MUST USE 4xx

When importing `software.bin` into Ghidra:
- **Language must be `PowerPC:BE:32:4xx`** (not `default`, not `VLE`)
- The `4xx` variant adds: `dcread`, `icread`, `dlmzb`, `mfdcr`/`mtdcr` for DCR bus instructions
- Without `4xx`, many boot-sequence instructions disassemble as `?? ILLEGAL`

### TORC — Virtex-4 Bitstream Parser

TORC (torc-isi/torc on GitHub) is the **only open-source tool that can parse Virtex-4
bitstreams**. Use it to extract BRAM content from `fpga.bin`, which may contain:
- Sensor calibration tables loaded at FPGA init
- LUT data for color science pipeline
- Boot code embedded in BRAM (uncommon but worth checking)

```bash
# Clone and build TORC (C++, requires Boost):
git clone https://github.com/torc-isi/torc
cd torc && cmake . && make

# Parse Virtex-4 bitstream:
./bin/torc_bitstream fpga.bin --device xc4vfx100 --extract-bram
```

### ISE 14.7 — Last Virtex-4 Toolchain

Xilinx ISE 14.7 (last version, 2013) is the final toolchain with Virtex-4 support.
Available as a free download from the Xilinx/AMD archive.

Key capabilities:
- **EDK** (Embedded Development Kit): contains `xparameters.h` templates — cross-reference
  against the 13 confirmed IP core drivers to derive the MMIO base addresses
- **iMPACT**: JTAG configuration and readback tool for the Virtex-4 FPGA
- **ChipScope**: on-chip logic analyzer; can read back state from a live camera

To derive the MMIO map from ISE/EDK:
1. Create a new Virtex-4 FX100 project in Platform Studio (EDK)
2. Add the 13 confirmed IP cores (xps_uartlite, xps_intc, xps_emaclite, xps_iic, xps_pci_v3, etc.)
3. Look at the generated `xparameters.h` — the addresses assigned by the tools will match
   what the firmware was compiled against (the linker script embeds them)

### QEMU virtex4_ml410.c — Custom Machine (Long-Term)

To properly emulate this firmware, write `hw/ppc/virtex4_ml410.c` based on the existing
`hw/ppc/virtex_ml507.c` (Virtex-5/PPC440 reference) with these key changes:

```c
// Key parameters for virtex4_ml410.c:
#define PPC_CPU_TYPE "ppc405f6"       // or "ppc405ep" as closest match
#define RAM_BASE     0x00000000UL
#define RAM_SIZE     (256 * MiB)
#define MMIO_BASE    0xE0000000UL     // FPGA fabric PLB peripherals
#define FLASH_BASE   0xFE000000UL     // NOR flash (romInit source)

// PVR to patch/spoof: 0x20011000 (PPC405F6)
// DCR map: UIC0 at 0x0C0, SDRAM at 0x010 (same as 405GP)
// UART Lite: MMIO at 0xe0600000 (confirmed; baud=115200)
// UART NS550 #1: MMIO at 0xe0640000 (confirmed; 100MHz clock)
// UART NS550 #2: MMIO at 0xe0650000 (confirmed; 100MHz clock)
// XIntc: MMIO at 0xe0800000 (confirmed from config table)
// XPci_v3: MMIO at 0xe1200000 (PLB table; PCI bridge for SiI3512+ISP1562)
// PCI config window: 0xe2000000 (256KB)
// PCI memory: 0xa0000000 (64MB)
// Flash: 0xf0000000 (128MB)
```

---

## Appendix: Quick Commands Reference

```bash
# Decrypt build 32:
cd firmware/builds/
unzip build_32_v32.0.3.zip
tar xf build_32_v32.0.3/redone.su
openssl enc -d -aes-256-cbc -md md5 -pass 'pass:M1H5gwOXh757rIRVY6Gj2tN080AYSX03' -in redone.1 | gunzip > software.bin

# Quick string search:
strings firmware/reverse/build_32/extracted/software.bin | grep -i "debug\|uart\|shell\|wdb"

# Find all C++ mangled names:
strings firmware/reverse/build_32/extracted/software.bin | grep '^_Z' | sort -u

# Disassemble boot sequence:
r2 -a ppc -b 32 -e cfg.bigendian=true -q \
   -c 'pd 30 @ 0x0; pd 20 @ 0x36c350' \
   firmware/reverse/build_32/extracted/software.bin

# Extract parameter XML:
python3 -c "
d=open('firmware/reverse/build_32/extracted/software.bin','rb').read()
s=0xC6E1A4
print(d[s:s+500].decode('ascii','replace'))
"

# Check build date/version:
strings firmware/reverse/build_32/extracted/software.bin | grep -E '(32_0_3|Build 32|SUNDANCE)'
```
