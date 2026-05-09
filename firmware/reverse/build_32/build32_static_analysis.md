# Build 32 v32.0.3 — Static Analysis Reference

## Overview

| Field            | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| Camera           | RED ONE MX                                                            |
| Build            | 32, version 32.0.3                                                    |
| Release date     | September 7, 2013                                                     |
| Firmware format  | Encrypted (`redone.su`), AES-256-CBC, MD5 KDF                        |
| Decryption pass  | `M1H5gwOXh757rIRVY6Gj2tN080AYSX03`                                   |
| CPU              | PowerPC 405GP, 32-bit, big-endian                                     |
| RTOS             | VxWorks WIND kernel version 2.10                                      |
| Load base        | `0x00000000` (flat binary, loads at physical zero)                   |
| QEMU machine     | `bamboo` (`-machine bamboo -m 256M`)                                  |
| QEMU CPU override| `405gp`                                                               |

---

## Firmware Components (extracted)

| File          | Size (bytes) | SHA-256                                                           | Role                    |
|---------------|--------------|-------------------------------------------------------------------|-------------------------|
| `software.bin`| 15,253,280   | `416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd` | Main OS + app firmware |
| `fpga.bin`    | 4,133,176    | `497d8f37613b235469666557edc0eadf0d96f8a6f784817284ec0dfdd2827f10` | I/O FPGA bitstream      |

The outer `redone.su` is a POSIX tar with four files:
- `redone.1` — AES-encrypted gzip of `software.bin`
- `redone.2` — unknown (likely splash screen or VP-FPGA bitstream)
- `redone.3` — AES-encrypted gzip of `fpga.bin`
- `redone.4` — unknown (likely config / version manifest)

---

## Version Strings

| Key               | Value                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------|
| SUNDANCEMAGIC     | `2009_07_01_0`                                                                            |
| VxWorks kernel    | `2.10`                                                                                    |
| BSP path          | `C:/sundance/SW/32_0_3/Sundance/bsp_ppc405_0_revB/ppc405_0_drv_csp/xsrc/xversion.c`    |
| CPU arch          | PowerPC 405                                                                               |
| FPGA type         | Xilinx Virtex/Spartan bitstream                                                           |

---

## Binary Structure

| Range                    | Content                          |
|--------------------------|----------------------------------|
| `0x000000 – 0x6FFFFF`   | Executable code (~7 MB)         |
| `0x700000 – 0x8FFFFF`   | Mixed code/data (large structs) |
| `0x900000 – 0xCFFFFF`   | Embedded data (XML, SWF, fonts) |
| `0xD00000 – 0xDFFFFF`   | Symbol/string tables, debug info|
| `0xE00000 – 0xE8BF1F`   | Code tail (BSS-init path)        |

Total size: 14.55 MB (0xE8BF20 bytes)

---

## Boot Sequence

### Reset Vector (0x0000)
```
0x0000:  b 0x8                     ; skip to init
0x0008:  li r4, 0 / mtmsr r4       ; MSR = 0 (disable interrupts)
         mttbl/mttbu r4            ; clear timebase
         mticcr/mtdccr r4          ; disable I/D-cache
         iccci / dccci             ; invalidate caches
0x0084:  lis r1, 0x0001            ; SP = 0x00010000  ← SP INIT OFFSET
0x0088:  addi r1, r1, 0
0x008c:  addi r1, r1, -0x10        ; SP = 0x0000FFF0
0x00a4:  bl 0x36c350               ; → main boot init function
0x00a8:  bl 0x124                  ; → infinite halt loop (never reached)
```

**romInit SP instruction for QEMU patch:**
- **Offset `0x84`**: `3C200001` (`lis r1, 0x0001`)
- To relocate SP to 128 MB: change to `3C200800` (`lis r1, 0x0800`) → SP = `0x07FFFFF0`

### Exception Vector Table

| Address | Handler                    |
|---------|----------------------------|
| `0x0000`| Reset vector               |
| `0x0200`| Machine check              |
| `0x0300`| DSI (data storage)         |
| `0x0400`| ISI (instruction storage)  |
| `0x0500`| External interrupt         |
| `0x0600`| Alignment                  |
| `0x0700`| Program check              |
| `0x0800`| FP unavailable             |
| `0x0900`| Decrementer                |
| `0x0C00`| System call                |
| `0x0D00`| Trace                      |

*(Addresses inherited from Build 13 template; confirm addresses match via r2 `pd 1 @ 0x200` etc.)*

---

## Key Function Addresses

| Symbol                  | Address      | Notes                                               |
|-------------------------|--------------|-----------------------------------------------------|
| `romInit` / reset entry | `0x00000000` | Reset vector; hardware init inline                  |
| Main boot init          | `0x0036C350` | Equivalent of `usrInit`/`usrConfig`; waits canary, zeros BSS, starts VxWorks |
| Halt loop               | `0x00000124` | `b 0x124` — infinite loop; called if init returns  |
| UART driver init        | `0x001C18DC` | First use of `0x40600000` (Xilinx UART Lite) at `0x1C1A0C` |
| MMIO dispatch table     | `0x00012D90` | Large switch on peripheral base address            |
| Hardware seq init       | `0x0000DCB0` | Early boot — calls `sysClkInit`, SDRAM/FPGA setup  |
| Timer/clock helper      | `0x0000D8A0` | Called twice from `0x36C3F0/F8`; loads/stores tick counter |

---

## Stack Canary Wait Loop

Located inside `0x36C350` (main boot init):

```
0x36C358:  lis r9, 0x1234          ; r9 = 0x1234xxxx
0x36C35C:  lis r10, 0x5A5A         ; r10 = 0x5A5Axxxx
0x36C370:  ori r9, r9, 0x8765      ; r9 = 0x12348765
0x36C374:  ori r10, r10, 0xC3C3    ; r10 = 0x5A5AC3C3

0x36C378:  lis r11, 0xE2           ; r11 = 0x00E20000
0x36C37C:  lis r8, 0xE2            ; r8  = 0x00E20000

; --- CANARY WAIT LOOP ---
0x36C380:  lwz r0, 0x69A4(r11)     ; load *0x00E269A4
0x36C384:  cmpw cr7, r0, r9        ; compare to 0x12348765
0x36C388:  bne cr7, 0x36C380       ; ← PATCH 1: NOP this (409EFFF8 → 60000000)

0x36C38C:  lwz r0, 0x69A0(r8)      ; load *0x00E269A0
0x36C390:  cmpw cr7, r0, r10       ; compare to 0x5A5AC3C3
0x36C394:  bne cr7, 0x36C380       ; ← PATCH 2: NOP this (409EFFEC → 60000000)
```

**Canary RAM addresses (set by a separate init path on real hardware):**
- `0x00E269A4` → expected value `0x12348765`
- `0x00E269A0` → expected value `0x5A5AC3C3`

---

## BSS Region

Zeroed by `bzero/memset` call at `0x36C3AC` (target `0x496698`):

```
0x36C398:  lis r28, 0x0115          ; r28 = 0x01150000
0x36C39C:  lis r3, 0x00EA           ; r3  = 0x00EA0000
0x36C3A0:  addi r28, r28, 0x3480   ; r28 = 0x01153480  (BSS end)
0x36C3A4:  addi r3, r3, -0x40E0    ; r3  = 0x00E9BF20  (BSS start)
0x36C3A8:  subf r4, r3, r28         ; r4  = BSS size = 0x002B7560 (~2.8 MB)
0x36C3AC:  bl 0x496698              ; memset(bss_start, 0, bss_size)
```

| Symbol      | Address      |
|-------------|--------------|
| `bss_start` | `0x00E9BF20` |
| `bss_end`   | `0x01153480` |
| BSS size    | `0x002B7560` (2,848,096 bytes) |

---

## MMIO Peripheral Map

Most-referenced MMIO bases in code (from `lis rX, hi` scan, code range `0x0–0x6FFFFF`):

| MMIO Base       | Ref count | Likely peripheral            |
|-----------------|-----------|------------------------------|
| `0x40000000`    | 223       | Primary FPGA registers / bus |
| `0x40600000`    | 107       | Xilinx UART Lite             |
| `0x408F0000`    | 67        | Unknown peripheral           |
| `0x40590000`    | 35        | Unknown peripheral           |
| `0x40340000`    | 47        | Unknown peripheral           |
| `0x40240000`    | 36        | Unknown peripheral           |
| `0x40100000`    | 35        | Unknown peripheral           |
| `0x40040000`    | 31        | Unknown peripheral           |
| `0x40400000`    | 16        | Unknown peripheral           |
| `0x40080000`    | 15        | Unknown peripheral           |

First MMIO accesses in code (likely crash candidates for QEMU Phase 2 patches):
- `0x12DB4`: `lis r0, 0x4010`  →  MMIO addr `0x4010E507`
- `0x12DD4`: `lis r0, 0x4004`  →  MMIO addr `0x4004E505`

---

## Key Embedded Components (binwalk highlights)

| Offset       | Description                                                 |
|--------------|-------------------------------------------------------------|
| `0x495BE8`   | Copyright: Wind River Systems, 1984–2006                   |
| `0x5A83D8`   | VxWorks WIND kernel version `2.10`                         |
| `0x672824`   | gzip compressed data (null date — likely internal blob)    |
| `0x7D7BFC`   | gzip compressed data                                        |
| `0x942B88`   | gzip: `splash_mx.raw` (splash screen, 2009-12-16)          |
| `0x9C0EDC`   | gzip: `splash.raw` (alt splash, 2008-07-14)                |
| `0x9D2AE0`   | XML document v1.0 (OSD/UI panel definitions — ~40 KB)       |
| `0x9E03BC`   | Adobe Flash SWF v7, 1,329,944 bytes (GUI)                  |
| `0xB24EF8`   | Adobe Flash SWF v7, 1,346,327 bytes (GUI alt)              |
| `0xC6E1A4`   | XML document v1.0 (parameter definitions — ~200 KB)        |
| `0xDEF5D0`   | StuffIt data structures (internal data tables)             |
| `0xE05700`   | Copyright: P.J. Plauger / Dinkumware 1992–2002             |

SWF count: 9 total  
XML documents: 2 (`0x9D2AE0`, `0xC6E1A4`)

---

## Phase 2/3 QEMU Patch Targets (for future work)

### Required Phase 1 Patches (confirmed from static analysis)

| Offset     | Original bytes  | Replacement     | Description                                    |
|------------|-----------------|-----------------|------------------------------------------------|
| `0x000084` | `3C200001`      | `3C200800`      | Relocate romInit SP: `lis r1,1` → `lis r1,0x800` (SP = `0x07FFFFF0`) |
| `0x36C388` | `409EFFF8`      | `60000000`      | NOP canary wait loop — first `bne cr7, 0x36C380` |
| `0x36C394` | `409EFFEC`      | `60000000`      | NOP canary wait loop — second `bne cr7, 0x36C380` |

### Phase 2 Investigation Points

These addresses access MMIO peripherals that do not exist in QEMU and will likely cause machine-check exceptions:

1. **`0x12DB4`** — first MMIO access (`lis r0, 0x4010`; `ori r0, r0, 0xE507`). Identify the peripheral and either NOP or stub.
2. **`0x12DD4`** — second MMIO access (`lis r0, 0x4004`; `ori r0, r0, 0xE505`).
3. **`0x0DCB0`** — early hardware sequencer; calls `0x1C8BC` repeatedly with small integer args (device enable codes). Each sub-call may trigger MMIO.
4. **UART init at `0x1C18DC`** — MMIO at `0x40600000`. QEMU bamboo includes a minimal UART, but the driver may expect specific register behavior.

### Workflow for Phase 2/3

```
# Terminal 1
./scripts/qemu_boot.sh --debug   # starts QEMU paused, GDB on :1234

# Terminal 2
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -D gdb gdb://localhost:1234 \
   -i scripts/r2_debug.r2        # sets breakpoints, continues

# On crash: read PC register
# dr pc
# pd 4                            # disassemble crash site
# python3 scripts/patch_firmware.py --probe <PC> --input reverse/build_32/extracted/software.bin
# Add Patch entry to KNOWN_PATCHES, re-run with --patched
```

---

## r2_debug.r2 Update Checklist

When updating `scripts/r2_debug.r2` for Build 32, replace all Build 13 addresses with:

```r2
f sym.reset_vector       @ 0x00000000
f sym.machine_check_vec  @ 0x00000200
f sym.dsi_vec            @ 0x00000300
f sym.isi_vec            @ 0x00000400
f sym.ext_interrupt_vec  @ 0x00000500
f sym.alignment_vec      @ 0x00000600
f sym.program_check_vec  @ 0x00000700
f sym.fp_unavail_vec     @ 0x00000800
f sym.decrementer_vec    @ 0x00000900
f sym.sys_call_vec       @ 0x00000C00
f sym.trace_vec          @ 0x00000D00

f sym.romInit_temp_stack @ 0x0000FFF0
f sym.usrInit            @ 0x0036C350
f sym.bss_start          @ 0x00E9BF20
f sym.bss_end            @ 0x01153480
f sym.sysSerialInit      @ 0x001C18DC

db 0x0036C350   ; break at main boot init
db 0x001C18DC   ; break at UART init
```

---

## qemu_boot.sh / patch_firmware.py Update Checklist

**`qemu_boot.sh`:**
- Change `FW_DIR` from `"reverse/Upgrade_Build 13/Upgrade"` to `"reverse/build_32/extracted"`
- Change `FIRMWARE` variable to use `software.bin` / `software.patched.bin`

**`patch_firmware.py`:**
- Change `--input` default from `reverse/Upgrade_Build 13/Upgrade/SundanceBootable.bin`
  to `reverse/build_32/extracted/software.bin`
- Change `--output` default to `reverse/build_32/extracted/software.patched.bin`
- Replace Phase 1 patches with Build 32 offsets (table above)
