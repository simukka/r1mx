# RED ONE MX — Build 32 Firmware Reverse Engineering Reference

**Purpose:** Single-document reference for firmware reverse engineering of Build 32 v32.0.3.
Load this document at the start of any RE session. No need to hunt through PDFs or separate analysis files.

**Firmware binary:** `firmware/reverse/build_32/extracted/software.bin`
**CPU:** PowerPC 405GP, 32-bit, big-endian
**OS:** VxWorks WIND kernel 2.10 (Wind River Platform ~6.x)
**Build date:** September 7, 2013
**SHA-256:** `416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd`

---

## Table of Contents

1. [PPC405GP Architecture Reference](#1-ppc405gp-architecture-reference)
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

---

## 1. PPC405GP Architecture Reference

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
| PVR | 287 | Processor Version Register (read-only); 405GP = `0x40110000` |
| MSR | — | Machine State Register (via `mfmsr`/`mtmsr`) |
| DBCR0 | 1010 | Debug Control Register 0 |
| DBCR1 | 1011 | Debug Control Register 1 |
| DBSR | 1008 | Debug Status Register |
| EVPR | 982 | Exception Vector Prefix Register |
| CCR0 | 947 | Core Configuration Register 0 |
| ICCR | 1011 | Instruction Cache Cacheable Regions |
| DCCR | 1018 | Data Cache Cacheable Regions |

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
| `0x0800` | FP unavailable | stub (no FPU on 405GP) |
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

**Address `0x40600000` (UART Lite MMIO):**
```
LO  = 0x0000
HA  = 0x4060
```
Assembly: `lis r3, 0x4060` then no `addi` needed (or `addi r3, r3, 0`)

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
| `0xE9xxxx` (≥ 0x8000) | `0xEA` | BSS-adjacent variables |

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

[MMIO — above 0x40000000]
0x40000000 – 0x5FFFFFFF   FPGA peripheral registers (via OPB/PLB bus)
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

All peripherals are in the FPGA fabric at `0x4000_0000+`. The PPC405GP internal peripherals (SDRAM, EBC, clocks) use the DCR bus (see Section 7).

### Confirmed Peripherals

| MMIO Base | Peripheral | Reference count | Notes |
|-----------|------------|----------------|-------|
| `0x40000000` | FPGA primary register block | 223 | Master FPGA control interface |
| `0x40600000` | Xilinx UART Lite | 107 | First MMIO accessed in boot; `sysSerialInit` at `0x1C18DC` |
| `0x408F0000` | Unknown | 67 | High ref-count — likely interrupt or timer |
| `0x40590000` | Unknown | 35 | |
| `0x40340000` | Unknown | 47 | |
| `0x40240000` | Unknown | 36 | |
| `0x40100000` | Unknown | 35 | |
| `0x40040000` | Unknown | 31 | |
| `0x40400000` | Unknown | 16 | |
| `0x40080000` | Unknown | 15 | |
| `0x40C00000` | XEmacLite (Ethernet MAC) | — | From boot config string; WDB transport |

### XEmacLite Register Layout (at 0x40C00000)

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x000` | TX buffer (2KB) | Transmit data |
| `+0x07C` | TX length | Bytes to transmit |
| `+0x07E` | TX status/ctrl | Bit 0: TxDone; write 1 to send |
| `+0x800` | RX buffer (2KB) | Received data |
| `+0x87C` | RX length | Bytes received |
| `+0x87E` | RX status/ctrl | Bit 0: RxEmpty (0 = data ready) |
| `+0xFFC` | MAC address | First 4 bytes of MAC |

### Xilinx UART Lite Register Layout (at 0x40600000)

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x00` | RX FIFO | Read received byte |
| `+0x04` | TX FIFO | Write byte to transmit |
| `+0x08` | Status | Bit 0: RX valid; Bit 2: TX full; Bit 3: TX empty |
| `+0x0C` | Control | Bit 0: Reset TX FIFO; Bit 1: Reset RX FIFO; Bit 4: Enable interrupts |

**Baud rate:** Fixed at FPGA compile time (not software-configurable). Likely 115200 based on standard Xilinx EDK reference design defaults. Confirm from FPGA bitstream analysis or physical testing.

### First MMIO Accesses in Boot (crash candidates in QEMU)

```
0x000012DB4  lis r0, 0x4010  → MMIO addr 0x4010E507  (unknown)
0x000012DD4  lis r0, 0x4004  → MMIO addr 0x4004E505  (unknown)
0x0000DCB0   sysHwInit_seq   → calls sub at 0x1C8BC repeatedly (device enable codes)
0x001C18DC   sysSerialInit   → accesses UART Lite at 0x40600000
```

---

## 7. DCR (On-Chip Peripheral) Map

The PPC405GP has on-chip peripherals accessible via the Device Control Register (DCR) bus. QEMU's `bamboo` machine silently ignores unknown `mtdcr`/`mfdcr` accesses — these should not cause crashes.

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

1. **Stack canary wait** (`0x36C380–0x36C394`):  
   Waits for RAM at `0xE269A0/A4` to equal magic values `0x5A5AC3C3` / `0x12348765`.  
   Set by a secondary init path on real hardware. **Must be patched for QEMU** (NOP the `bne` branches).

2. **BSS zero-init** (`0x36C398–0x36C3AC`):  
   `memset(0xE9BF20, 0, 0x2B7560)` — zeroes 2.8MB BSS segment.

3. **Hardware sequencer** (`0xDCB0`):  
   `sysHwInit_seq` — enables subsystems. Calls `0x1C8BC` repeatedly with device IDs.  
   First MMIO accesses — likely crash point for QEMU.

4. **UART init** (`0x1C18DC`):  
   `sysSerialInit` — configures XUartLite at `0x40600000`.  
   After this, VxWorks console output starts (boot messages).

5. **VxWorks kernel start**:  
   Jumps to `kernelInit()` → spawns root task → calls `usrRoot()`.

6. **`usrRoot()` / `usrAppInit()`**:  
   Spawns all application tasks:
   - File system init (TFFS, ATA CF, USB mass storage)
   - Network init (XEmacLite driver, DHCP/static IP)
   - WDB agent (`usrWdbInit` at `0x36B3DC`) — **always spawned**
   - Camera subsystem tasks (sensor, FPGA, video pipeline, UI/OSD)

7. **Upgrade check** (`SmartUpgrade`):  
   Searches these paths in order:
   ```
   /tffs0/upgrade/redone.su
   /ata00:1/upgrade/redone.su
   /ata10:1/upgrade/redone.su
   /sdmc/upgrade/redone.su
   /usbd0/upgrade/redone.su
   ```

---

## 9. Stack Canary — QEMU Patch

### The Problem

At boot offset `0x36C380`, the firmware spins in an infinite loop waiting for two magic values to appear in RAM. On real hardware, these are written by a secondary initialization path (likely the FPGA or a secondary CPU core). In QEMU, RAM is zero-initialized and nothing writes these values → **boot hangs forever**.

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

First MMIO crash expected at `0x12DB4` (accesses `0x4010E507`). Use `--debug` mode to find subsequent crash points. Document each in `patch_firmware.py`.

---

## 9a. Phase 2/3 QEMU Patches — Discovered at Runtime

Applied in addition to the Phase 1 patches above. All offsets are also runtime addresses (firmware loads at 0x0).

Run `cd firmware && python3 scripts/patch_firmware.py` to apply all patches and produce `software.patched.bin`.

### Complete Patch Table (36 patches — current as of session 4)

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
| 21–33 | 2 | BSS data | Null 13 sentinel `0xFFFFFFFF` values used as fn-ptrs (since BSS memset was skipped by Patch #5, they remain uninitialized) |
| 34–35 | 3 | `0x5D58B8`, `0x5D58E8` | SSD whitelist bypass: patch IsCompatible check to always return 1 |
| 36 | 2 | `0x62CC` | NOP null bctrl in fn_6288 — fn_2748 clears *(r30+64) leaving CTR=0; bctrl→0x0 resets CPU |

### Current Boot State (after 36 patches — session 4)

After all 36 patches, the boot successfully reaches `fn_DCB0` (`sysHwInit_seq`) and begins
executing the hardware sequencer. This is confirmed by:

- **NIP sampling**: 0xE8A4 (UART TX write helper) dominates — firmware is writing characters
- **r0 = 0xDD84** at sample time — saved LR inside fn_DCB0's call chain
- **SP = 0x07FFFF90** — consistent with fn_DCB0 stack frame (16-byte frame below 0x07FFFFA0)
- **Single-step trace**: previously confirmed NIP=0xDCC4 (fn_DCB0 + 0x14), LR=0xDCCC

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
| `0x0000DCB0` | `sysHwInit_seq` | Hardware sequencer — first MMIO |
| `0x0000D8A0` | timer/clock helper | Called from `0x36C3F0/F8` |
| `0x00012D90` | MMIO dispatch table | Large switch on peripheral base |
| `0x001C18DC` | `sysSerialInit` | XUartLite init at 0x40600000 |
| `0x001C1A0C` | first UART Lite access | `lis rX, 0x4060` in serial init |
| `0x0036B3DC` | `usrWdbInit` | WDB agent init — always called |
| `0x0036B7EC` | BSP init caller | Calls `usrWdbInit`, spawns WDB task |
| `0x0036C350` | main boot init | Equivalent of `usrInit`/`usrConfig` |
| `0x00496698` | `memset` | BSS zero-init target |

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

**XUartLite** (FPGA, at `0x40600000`):
- Fixed baud rate (baked into FPGA bitstream — likely 115200)
- Likely connected to an internal path (lens control?)

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

### Prerequisites

```bash
# Install QEMU (if not present):
apt install qemu-system-ppc

# Install radare2:
apt install radare2

# Verify:
qemu-system-ppc --version
r2 --version
```

### Launch (Build 32 — normal mode)

```bash
cd firmware/
qemu-system-ppc \
    -machine bamboo \
    -m 256M \
    -nographic \
    -device "loader,file=reverse/build_32/extracted/software.patched.bin,addr=0x0,force-raw=on" \
    -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on"
```

### Launch (Debug mode — r2 GDB stub)

```bash
# Terminal 1: start QEMU paused
qemu-system-ppc \
    -machine bamboo \
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
    -machine bamboo \
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
- **Always use `Z0`, never `Z1`**

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
3. **Language:** `PowerPC:BE:32:default`
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
