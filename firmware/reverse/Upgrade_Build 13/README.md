# Build 13 v1.8.8 "Sundance"

The earliest known public firmware for the RED ONE MX, retrieved via Wayback Machine.
This build predates the AES encryption introduced from Build 17 onward — the upgrade
package is a plain tar archive with no obfuscation.

Created around January 2008.

## Package contents

```
Upgrade_Build 13/
├── build_13_ops_guide_v1.8.8.pdf        (6.4 MB — operator manual)
├── build_13_red_one_v1.8.8_readme .txt  (3.4 KB — install instructions)
└── Upgrade/
    └── su.tar                           (7.7 MB — firmware upgrade archive)
```

`su.tar` is a plain GNU tar that contains two gzip-compressed images:

| File in su.tar | Extracted to | Role |
|---|---|---|
| `SundanceBootable.bin.gz` | `SundanceBootable.bin` (13 MB) | Main OS + application firmware |
| `iofpga_top.bin.gz` | `iofpga_top.bin` (4 MB) | I/O FPGA bitstream |

## Tools used

- Wayback Machine (recovery)
- binwalk (signature scanning and extraction)
- Python / zlib (decompression of embedded assets)
- strings / xxd (inspection)

## Architecture

### CPU and OS — PowerPC 405 / VxWorks

The camera's main processor board is codenamed **"Sundance"**. It runs on a
**PowerPC 405** RISC core executing **Wind River VxWorks**.

Key identifiers found in `SundanceBootable.bin`:

```
VxWorks WIND kernel version "2.10"
Copyright Wind River Systems, Inc., 1984-2006
```

The `2.10` version string refers to the **Wind River Platform release**, not a Linux
kernel version. Cross-referencing the archived Wind River product pages (circa 2008):

| Product | Platform Release | Kernel | Release Date |
|---|---|---|---|
| Wind River Linux | 2.0 | 2.6.21 | 15 Dec 2007 |
| Wind River Linux | 3.0.1 | 2.6.27 | Sep 2009 |

The embedded Dinkumware C library copyright (`© 1992–2002 P.J. Plauger`) and the
BSP source path confirm the VxWorks lineage, not Linux:

```
/home/sundance/release/SW/Src/bsp_ppc405_0_revB/ppc405_0_drv_csp/xsrc/xversion.c
```

**Version string embedded in firmware:**

```
SUNDANCEMAGIC_^*%#_SW_RELEASENAME=v1.8.8#13
```

### FPGA — Xilinx Virtex/Spartan

`iofpga_top.bin` opens with the standard Xilinx dummy + sync word:

```
0x0000  Xilinx Virtex/Spartan FPGA bitstream dummy + sync word
```

This bitstream handles sensor I/O, signal routing and peripherals independently of
the CPU. It is loaded/programmed at boot time alongside the VxWorks image.

## What's inside SundanceBootable.bin

### On-screen display — Adobe Flash SWF

The camera's entire menu system is rendered using **Adobe Flash Player 7** embedded
in VxWorks. Multiple SWF files are packed inside the image:

```
0x660270  Uncompressed Adobe Flash SWF file, Version 7, size 2846522 bytes
0xBAA1D0  (zlib-compressed) → FWS SWF (uncompressed after inflate)
0xBB1E34  (zlib-compressed) → FWS SWF fragment (ActionScript strings visible)
```

ActionScript strings visible in the decompressed SWFs include standard Flash
intrinsics (`ASSetPropFlags`, `ASnative`, `System.capabilities`) confirming a full
embedded Flash runtime.

### GUI panel definitions — XML

Two XML documents are embedded:

**1. Panel/button layout** (offset `0x4E9BE4`) — defines the physical navigation
panels shown on the camera's LCD/EVF:

```xml
<Panels>
  <Panel id="Panel_Sensor"       label="SENSOR">
  <Panel id="Panel_Sensitivity"  label="EXPOSURE">
  <Panel id="Panel_WhiteBalance" label="COLOR TEMP">
  <Panel id="Panel_Shutter"      label="SHUTTER">
  <Panel id="Panel_VariSpeed"    label="VARISPEED">
  ...
</Panels>
```

Parameters are referenced by dotted names such as:
- `GUI.PAINT.EXPOSURE.ASA`
- `PAINT.WHITE_BALANCE.CURRENT`
- `RECORD.SHUTTER_SPEED.FRACTIONAL_SECONDS`
- `SYSTEM.DEV.GENLOCK.REQUESTED`

**2. Parameter/config registry** (offset `0xA84008`) — full camera parameter
schema with types, default values, profile flags and flash config file paths:

```xml
<RedParameters>
  <FactoryDefaults>
    <File>RomDrive:\Config\FactoryDefaults.xml</File>
  </FactoryDefaults>
  <FlashConfig>
    <File>FlashDrive:\Config\GuiParams.xml</File>
    <File>FlashDrive:\Config\FpgaParams.xml</File>
    <File>FlashDrive:\Config\ImagingParams.xml</File>
  </FlashConfig>
  ...
</RedParameters>
```

User-facing config persists on the camera's flash storage at `FlashDrive:\Config\`
and is separate from the firmware image — it survives firmware upgrades.

### Splash / boot screen

A raw framebuffer image is stored at offset `0xAAD180` (gzip, original filename
`splash.raw`, timestamp 2007-08-03). Decompressed size: **3,256,320 bytes**.
At 24 bpp that resolves to **1024 × 1060 pixels** — matching the RED ONE's
viewfinder/LCD composite display resolution.

### Zlib-compressed assets

~50 zlib blobs are packed sequentially starting around offset `0x6B52F7`. These
decompress to font tables, UI bitmaps and JPEG thumbnails used by the Flash OSD.
The largest (`0x6B7D2F`, 3.6 MB decompressed) appears to be a full-screen UI
framebuffer: `0xFF 0xBF 0xBF 0xBF …` repeating — a grey fill or background canvas.

### Encrypted section

One section at offset `0x8EFA32` is identified by binwalk as:

```
mcrypt 2.2 encrypted data, algorithm: blowfish-448, mode: CBC, keymode: 8bit
```

Purpose unknown — likely calibration data, licensing metadata or a protected
factory configuration block.

### Upgrade logic (strings)

The VxWorks image contains the full upgrade state machine. On boot it checks for
`su.tar` on removable media:

```
UpgradeMC::SmartUpgrade() NO UPGRADE file 'su.tar' detected
OSD::GoSplash() checking for upgrade...
OSD::GoSplash() UPGRADE.AVAILABLE! Proceeding with SmartUpgrade()...
```

Dispatches: `UPGRADE_SOFTWARE`, `START_UPGRADE`, `COMPLETE_UPGRADE`,
`FRAME_UPGRADE_OK`, `FRAME_UPGRADE_FAILED`.

### Debug / maintenance interface

VxWorks is compiled with its full shell and spy profiler. Network boot string:

```
xemaclite(0,0)host:vxWorks h=192.168.0.1 e=192.168.0.2 u=xemhost
```

USB target interface (`usbTargInitialize`) and TFFS flash filesystem (`/tffs`) are
also present, suggesting a serial or Ethernet debug console is accessible on
service/engineering units.

## binwalk SundanceBootable.bin (key entries)

```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
4096428       0x3E81AC        Copyright string: "Copyright Wind River Systems, Inc., 1984-2006"
4521448       0x44FDE8        VxWorks WIND kernel version "2.10"
5151716       0x4E9BE4        XML document, version: "1.0"  (GUI panel definitions)
5190636       0x4F33EC        gzip compressed data (null date)
6685296       0x660270        Uncompressed Adobe Flash SWF file, Version 7, 2846522 bytes
6802401       0x67CBE1        JPEG image data, JFIF standard 1.02
6831989       0x683F75        Copyright string: "Copyright (c) 1998 Hewlett-Packard Company"
7033591       0x6B52F7        Zlib compressed data, best compression  (font/UI assets begin)
9370162       0x8EFA32        mcrypt 2.2 encrypted data, blowfish-448, CBC
9531856       0x9171D0        gzip compressed data
11026440      0xA84008        XML document, version: "1.0"  (parameter registry)
11194752      0xAAD180        gzip compressed data, original filename: "splash.raw"
11254812      0xABBC1C        Zlib compressed data (Adobe Flash SWF after inflate)
11604188      0xB110DC        Unix path: /home/sundance/release/SW/Src/bsp_ppc405_0_revB/...
11914228      0xB5CBF4        StuffIt Deluxe data (TDList — font/glyph table structures)
12231120      0xBAA1D0        Zlib compressed data → FWS SWF
12262964      0xBB1E34        Zlib compressed data → FWS SWF fragment
```

---

## QEMU Emulation

> **Goal:** Boot `SundanceBootable.bin` to the VxWorks interactive `->` shell in QEMU,
> enabling live memory inspection, symbol calls and firmware reverse engineering without
> physical hardware.

### Environment

| Component | Version / Value |
|---|---|
| QEMU machine | `bamboo` (PPC405EP, the closest available) |
| QEMU version | 10.1.0 |
| RAM | 512 MB (`-m 512M`) — addresses above 256 MB are needed by init code |
| Binary load address | `0x00000000` (via QEMU `loader` device) |
| GDB stub | `tcp::1234` |
| radare2 | 5.9.8 (PPC capstone backend, GDB remote debug) |

**QEMU launch command:**
```bash
PATCHED="reverse/Upgrade_Build 13/Upgrade/SundanceBootable.patched.bin"
setsid qemu-system-ppc -machine bamboo -m 512M -nographic \
  -device "loader,file=$PATCHED,addr=0x0,force-raw=on" \
  -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on" \
  -S -gdb tcp::1234 </dev/null >/tmp/qemu.log 2>&1 &
```

> **Note:** Two separate `-device` arguments are required. `-cpu 405gp` must NOT be
> used with the bamboo machine (MMU model conflict).

### Memory map (confirmed at runtime)

| Range | Contents |
|---|---|
| `0x00000000–0x0000009C` | `romInit` — hardware setup, exception vectors |
| `0x00000100–0x00000600` | VxWorks exception vector table (BUT see critical note below) |
| `0x002ED020` | `usrInit` entry point (VxWorks BSS clear + subsystem init) |
| `0x00C118D0–0x00D441B0` | BSS segment (~1.2 MB, zeroed by usrInit) |
| `0x00BC0000–0x00C118CF` | Initialised data segment (static values from binary) |
| `0x40600000` | Xilinx UART Lite (MMIO — not yet reached in boot) |

### Critical: Exception vectors are overwritten by firmware code

The PPC405 exception vector area (`0x000–0xFFF`) is repurposed by the firmware:

| Address | Normal PPC405 use | Actual contents |
|---|---|---|
| `0x000` | Critical Input | `romInit` hardware init code (re-runs on any critical exception) |
| `0x100` | Machine Check | `blr` — returns via LR (wrong, but harmless for most paths) |
| `0x11C` | (in Machine Check handler) | `b 0x11C` — infinite panic loop |
| `0x200–0x500` | DSI/ISI/Ext/Align/Program | Real VxWorks handlers (save regs, dispatch) |
| `0x600` | **Program Exception** | **Function epilogue code** (see below) |

#### Why Z0 (software) breakpoints are permanently broken

Address `0x600` contains a VxWorks function **epilogue**, not a real exception handler:
```
lwz  r0, 0x34(r1)   ; restore LR from stack
<restore r25–r31>
mtspr LR, r0
addi r1, r1, 0x30
blr
```
When QEMU inserts a `trap` instruction for a Z0 breakpoint, the trap fires the Program
Exception at `0x600`, which executes this epilogue. If the stack contains uninitialised
data, `blr` jumps to `0x0` (romInit) → infinite crash loop.

**Always use Z1 (hardware) breakpoints exclusively:**
```
Z1,<addr>,4    # set
z1,<addr>,4    # clear
```
QEMU intercepts Z1 hits at the TCG level before the CPU sees them — exception vectors
are never involved.

#### Why crashes wipe Z1 breakpoints (critical for GDB sessions)

`romInit` at offset `0x0C` executes `mtspr DBCR0, r4` (r4=0), clearing the hardware
debug control register. Although QEMU's TCG Z1 implementation does not use the CPU's
DBCR0, **a crash-to-0x0 followed by a QEMU restart of romInit will trigger QEMU's own
internal TB (translation block) flush**, and on some QEMU versions can silently lose
hardware BP registrations. Always restart QEMU from scratch after any crash before
setting new Z1 breakpoints.

### Boot sequence (annotated)

```
0x0000_009C  bl usrInit          ; romInit jumps here after hw setup
0x002E_D020  usrInit entry        ; VxWorks init
0x002E_D050  <canary wait loop>   ; PATCH 2+3: NOP'd — waits for 0xBC3174/3170
0x002E_D07C  bl bzero             ; clears BSS 0xC118D0–0xD441B0
0x002E_D098  bl 0x2F06B0          ; PATCH 4+5: NOP'd — bctrl to 0x500 AE vector
0x002E_D09C  bl 0x2EF094          ; ← returns OK
0x002E_D0A0  bl 0x2EEE20          ; PATCH 6: NOP'd — EVPR relocation (moves vectors)
0x002E_D0A4  bl 0xDA30            ; sysHwInit — MMIO init, FPGA load attempt
  0x0000_DA40–DA7C  bl 0x1C634 ×7 ; MMIO register writes (0xE060xxxx area)
  0x0000_DA60       bl 0x2F2D0C   ; mtspr EVPR, r0 — resets vectors to base 0x0
  0x0000_DA74       bl 0xD9A8     ; secondary hw init
  0x0000_DA80       bl 0x9BC0     ; PATCH 7: NOP'd — FPGA bitstream loader (see below)
  0x0000_DA94       bl 0x9E1C     ; status check — OK
  … (many more bl 0x1C634 calls)  ; MMIO peripheral init
0x002E_D0A8  ← returned from sysHwInit
0x002E_D0AC  li r3,0 / bl 0x3AAFD8   ; fptr callback — *(0xBC5484) [NEXT CRASH SITE]
0x002E_D0B4  li r3,1 / bl 0x3AAFD8   ; fptr callback — *(0xBC5488) = 0x500 (pending fix)
```

### Applied patches (patch_firmware.py)

All patches target `SundanceBootable.patched.bin`. Source: `scripts/patch_firmware.py`.

| # | Offset | Original | Replacement | Reason |
|---|---|---|---|---|
| 1 | `0x0000007C` | `lis r1, 0x1` | `lis r1, 0x800` | SP relocation: 64KB→128MB. Prevent stack growing into code. |
| 2 | `0x002ED058` | `bne cr7, 0x2ED050` | NOP | Bypass canary wait loop (needs 0xBC3174=0x12348765, never set in QEMU) |
| 3 | `0x002ED064` | `bne cr7, 0x2ED050` | NOP | Bypass canary wait loop (second branch) |
| 4 | `0x002F06D8` | `mtctr r31` | NOP | Skip callback to `*(0xBC34F8)=0x500` (Alignment vector body) |
| 5 | `0x002F06DC` | `bctrl` | NOP | Skip the `bctrl` itself |
| 6 | `0x002ED0A0` | `bl 0x2EEE20` | NOP | Skip EVPR-relocating init (moves exception vectors → debug traps crash) |
| 7 | `0x0000DA80` | `bl 0x9BC0` | NOP | Skip FPGA bitstream loader (infinite bcopy loop — see below) |

### FPGA loader analysis (0x9BC0)

`0x9BC0` implements the **IO/VP FPGA bitstream loader** — it programs `iofpga_top.bin`
into the camera's Xilinx FPGA at boot time. Evidence:

- Strings in binary: `DrvInitVpfpga`, `DrvInitIofpga`, `iofpga_top.bin.gz`
- Magic value `0x22222222` expected at a runtime address (set by boot ROM on real
  hardware) to signal FPGA ready — never initialised in QEMU
- Calls `0x16728` (FPGA ready check), `0x168b4` (get bitstream size/pointer)
- Downstream `bcopy` at `0x2ED5CC` reads a zero-initialised BSS size value, which
  wraps to ~194 million iterations (~776 MB) — effectively infinite in QEMU

**Real hardware flow:** boot ROM → sets 0x22222222 magic → `0x9BC0` copies 4 MB
`iofpga_top.bin` to FPGA config port → FPGA comes up.

**QEMU workaround:** NOP the `bl 0x9BC0` call at `0xDA80`. The VxWorks image continues
booting without FPGA hardware (most camera peripherals will be absent but VxWorks
itself should reach the shell).

### Current boot progress

| Stage | Status |
|---|---|
| romInit → usrInit | ✅ Reaches 0x2ED020 |
| BSS clear | ✅ Completes (0xC118D0–0xD441B0) |
| usrInit canary bypass | ✅ Patch 2+3 |
| `0x2F06B0` fptr callback stub | ✅ Patch 4+5 |
| `0x2EEE20` EVPR init stub | ✅ Patch 6 |
| `sysHwInit` (0xDA30) | ✅ Completes (returns to 0x2ED0A8) |
| FPGA loader (0x9BC0) | ✅ NOP'd — Patch 7 |
| `0x3AAFD8` fptr callback at 0x2ED0AC | ⏳ **Next: NOP bctrl in 0x3AB000/0x3AB04C** |
| `0x3AAFD8` second call at 0x2ED0B4 | ⏳ Pending (*(0xBC5488)=0x500 will crash) |
| Remaining usrInit calls | ⏳ Pending |
| VxWorks `->` shell | 🎯 Goal |

### Next patches needed

#### Patches 8–9: NOP `bctrl` at 0x3AB000 and 0x3AB04C

`usrInit` calls `0x3AAFD8` twice (with r3=0 and r3=1). The function loads a function
pointer from `*(0xBC5484)` or `*(0xBC5488)` respectively and calls it via `bctrl`.
Static binary has `*(0xBC5484) = 0` but `*(0xBC5488) = 0x500` (Alignment exception
vector body — will crash).

The `mtspr CTR + bctrl` sequence appears at two locations in the function:

```python
Patch(offset=0x3AB000, original=b'\x7f\xe9\x03\xa6', replacement=PPC_NOP,
      description="NOP: mtctr r31 in 0x3AAFD8 (fptr path 1)")
Patch(offset=0x3AB004, original=b'\x4e\x80\x04\x21', replacement=PPC_NOP,
      description="NOP: bctrl in 0x3AAFD8 (fptr path 1 — *(0xBC5484))")
Patch(offset=0x3AB04C, original=b'\x7f\xe9\x03\xa6', replacement=PPC_NOP,
      description="NOP: mtctr r31 in 0x3AB024 (fptr path 2)")
Patch(offset=0x3AB050, original=b'\x4e\x80\x04\x21', replacement=PPC_NOP,
      description="NOP: bctrl in 0x3AB024 (fptr path 2 — *(0xBC5488)=0x500)")
```

### Recurring crash pattern: bctrl to exception vector bodies

The most common crash cause: the firmware stores addresses of **exception vector bodies**
(0x500 = Alignment, 0x600 = Program, etc.) into function pointer slots in the data
segment. These are intended as **default handlers** to be replaced at runtime by driver
registration. In QEMU the runtime registration never completes (no hardware), so the
default `0x500` pointer remains. When called as a normal function via `bctrl`, the
exception body reads LR from a wrong stack offset → `blr` → PC=0 → romInit → crash.

**Detection pattern in disassembly:**
```ppc
lwz  rX, 0xNNNN(rY)   ; load function pointer from data seg
cmpwi rX, 0
bne  <call_site>
...
<call_site>:
mtspr CTR, rX         ; ← NOP THIS
bctrl                 ; ← NOP THIS
```

**Fix:** NOP both `mtspr CTR` and `bctrl`. The calling code checks the return value but
continues fine when r3 = 0 (the value left after the NOP sequence).

### GDB / radare2 cheat sheet

```bash
# Connect radare2 to running QEMU
r2 -a ppc -b 32 -e cfg.bigendian=true -D gdb gdb://localhost:1234

# In r2: set Z1 hardware breakpoint and run
db 0x2ED020     # actually use Z1 via: !!echo "Z1,2ED020,4" | nc localhost 1234
dc              # continue

# GDB RSP manual (via netcat or Python socket):
# Z1,<hex_addr>,4    set hardware BP
# z1,<hex_addr>,4    clear hardware BP
# g                  read all registers (256 chars = GPR0-31, then PC at [256:264])
# s                  single step
# c                  continue
# 0x03 byte          interrupt (halt running QEMU)
```

**Register layout in `g` response** (hex chars, 8 per register):
```
[0:256]   GPR0–GPR31 (8 hex chars each = 32 registers × 32 bits)
[256:264] PC
[264:272] MSR
[272:280] CR
[280:288] LR
[288:296] CTR
```

### Key addresses

| Address | Symbol / Role |
|---|---|
| `0x00000000` | `romInit` / Critical Input exception vector |
| `0x00000600` | **Function epilogue** (NOT a real exception handler) |
| `0x002ED020` | `usrInit` entry |
| `0x002ED050` | Canary wait loop (NOP'd) |
| `0x002ED07C` | BSS clear (`bzero` call) |
| `0x002EF094` | Sub-init function (returns OK) |
| `0x002EEE20` | EVPR init (NOP'd) |
| `0x002F06B0` | Function pointer dispatcher (patched) |
| `0x002F2D0C` | `mtspr EVPR, r3` (SPR 982 = EVPR on PPC405) |
| `0x0000DA30` | `sysHwInit` entry |
| `0x00001C634` | MMIO write helper (accesses 0xE060xxxx area) |
| `0x00009BC0` | FPGA bitstream loader (NOP'd) |
| `0x003AAFD8` | Function pointer dispatcher #2 (pending patch) |
| `0x00BC3174` | Canary slot 1 (needs `0x12348765` on real HW) |
| `0x00BC3170` | Canary slot 2 (needs `0x5A5AC3C3` on real HW) |
| `0x00BC34F8` | Function pointer (= `0x500` in static binary) |
| `0x00BC5488` | Function pointer (= `0x500` in static binary) |

---

## Firmware build encryption (Build 17+)

From Build 17, `su.tar` is replaced by `redone.su`, encrypted with AES-256-CBC:

```
Key: M1H5gwOXh757rIRVY6Gj2tN080AYSX03
```

The `scripts/analyze_build.py` tool handles both encrypted and unencrypted packages
automatically.

---

## Resources

- [Wind River VxWorks (archived 2008)](https://web.archive.org/web/20080512034830/http://www.windriver.com/products/vxworks/)
- [VxWorks BSP developers guide](https://docs.windriver.com/bundle/Wind_River_Linux_Kernel_and_BSP_Developers_Guide_8.0_1/page/fuy1554300103283.html)
- [Wind River downloads (PPC405 BSP)](https://support2.windriver.com/index.php?page=other-downloads&dw_search_product=66&dw_search_product_version=344&order_by=content_modified_date&order_way=asc#list)
- [FYS4220 VxWorks lab notes — UiO](https://www.uio.no/studier/emner/matnat/fys/FYS4220/h11/undervisningsmateriale/laboppgaver-rt/)
- IBM PowerPC 405GP/EP User Manuals (for DCR, SPR, exception vector layout)
- QEMU bamboo machine source: `hw/ppc/ppc405_boards.c`
