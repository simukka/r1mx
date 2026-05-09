# Build 32 v32.0.3 — Subsystem Map & Decompilation Notes

## Overview

This document covers static decompilation of key subsystems in `reverse/build_32/extracted/software.bin`:
1. Upgrade state machine (`SmartUpgrade` / `GoSplash`)
2. Color science pipeline (REDColor, REDColor2, REDColor3, REDlog Film)
3. FLUT parameter handling
4. RECORD / HANC metadata flag
5. String cross-reference table
6. Ghidra / r2ghidra import settings

---

## 1. Upgrade State Machine

### Architecture

The upgrade system is object-oriented (ActionScript 3 / Scaleform GFx on the GUI side, C++ on the firmware side). The upgrade C++ controller is **`UpgradeMC`**, the UI handler is **`OSD`**.

### Key Message/State Strings (from XML parameter definitions)

| Parameter name                        | Type    | Location        |
|---------------------------------------|---------|-----------------|
| `UPGRADE.AVAILABLE`                   | boolean | `0x9D41xx` XML  |
| `UPGRADE.STATUS`                      | text    | `0x9D41xx` XML  |
| `UPGRADE.APPLYUPGRADE`                | —       | Dispatch msg    |
| `UPGRADE.VERSION.SOFTWARE`            | —       | version read    |
| `UPGRADE.VERSION.IOFPGA`              | —       | version read    |
| `UPGRADE.VERSION.VPFPGA`              | —       | version read    |
| `SYSTEM.DEV.EVF.UPGRADE.STATUS`       | text    | EVF status      |
| `SYSTEM.DEV.EVF.UPGRADE.AVAILABLE`    | boolean | EVF available   |
| `SYSTEM.DEV.EVF.UPGRADE.APPLYUPGRADE` | —       | EVF dispatch    |

### State Machine Transitions (reconstructed from strings)

```
[IDLE]
  ↓  GoSplash() checks UPGRADE.AVAILABLE
[OSD::GoSplash()]         @ string ref 0xAC4D08 / 0xC0E064
  "OSD::GoSplash() UPGRADE.AVAILABLE! Proceeding with SmartUpgrade()..."
  ↓  dispatch UPGRADE_SOFTWARE
[UpgradeMC::SmartUpgrade()]   @ string ref 0xAED7A1 / 0xC36273
  "UpgradeMC::SmartUpgrade() envoked..."
  ↓  search upgrade media
    found su.tar   → 0xAED85C: "...Upgrade file 'su.tar' detected"   → FRAME_AVAILABLE
    no su.tar      → 0xAED92F: "...NO UPGRADE file 'su.tar' detected"  → FRAME_NO_UPGRADE
  ↓  result dispatched to UI
[FRAME_UPGRADE_OK / FRAME_UPGRADE_FAILED / FRAME_NO_UPGRADE]
```

### Firmware Search Order for `redone.su`

The firmware searches for the upgrade package at these paths (in order):

```
/tffs0/upgrade/redone.su          (0xD3632F) — internal flash
/ata00:1/upgrade/redone.su        (0xD3634D) — CF card slot 0
/ata10:1/upgrade/redone.su        (0xD36369) — CF card slot 1 (if applicable)
/sdmc/upgrade/redone.su           (0xD36382) — SD card
/usbd0/upgrade/redone.su          (0xD3639B) — USB device
```

*(Note: the readme says the camera only reads an `upgrade/` folder — the search order above shows all mount points attempted.)*

### Dispatch Table Entry

From XML at `0x9DACBF`:
```xml
<Button id="..." label="SOFTWARE UPDATE">
    <Dispatch>UPGRADE_SOFTWARE</Dispatch>
</Button>
```

The button dispatch routes through the main event dispatcher. `UPGRADE_SOFTWARE` is also in the action list at `0xADA8D7`:
```
G_RESET · UPGRADE_SOFTWARE · VIEW_STATUS · SENSOR_ADVANCED · UNMOUNT_DIGMAG · ...
```

### GoSplash Function (ActionScript/SWF side)

Located in SWF at `0x9E03BC` (SWF v7, 1.33 MB). String anchors:
- `0xAC4ADA`: `__GoSplashFnc · GoSplash · mx.utils.Delegate.create`
- `0xAC4DC3`: `SmartUpgrade · __slate · Slate · __imageParamName`

The `GoSplash` function is a Scaleform (ActionScript 2/3) movie clip method that:
1. Checks `UPGRADE.AVAILABLE` parameter
2. If true, calls `SmartUpgrade()` via `mx.utils.Delegate.create`
3. Displays the upgrade progress bar via `UPGRADE.STATUS` parameter

---

## 2. Color Science Pipeline

### Color Modes (Build 32 additions: REDColor2, REDColor3, REDlogFilm)

From XML parameter definition at `0xC99409` (`VIDEO.MONITOR.VIEW_MODE`):

```xml
<Param name = "VIDEO.MONITOR.VIEW_MODE" type = "text" value = "REDcolor3">
    <LegalValues>
        <Choice UiTxt = "RAW">Raw</Choice>
        <Choice UiTxt = "REDcolor">REDcolor</Choice>
        <Choice UiTxt = "REDcolor 2">REDcolor2</Choice>
        <Choice UiTxt = "REDcolor 3">REDcolor3</Choice>
        <Choice UiTxt = "REDlog Film">REDlogFilm</Choice>
        <Choice UiTxt = "REDspace">REDspace</Choice>
    </LegalValues>
```

Internal enum name mapping (from string at `0xC66C8F`):
```
REDcolor · REDcolor2 · REDlogFilm · REDspace · REDcolor3
```
Short codes (from `0xC66CB6`): `RC1 · RC2 · RLF · RSP · RC3`

Default value: `REDcolor3` (set as default for `VIDEO.MONITOR.VIEW_MODE`)

### Debug/Internal Color Science Parameter

From XML at `0xC7249E` (`DEBUG.IMGPROC.PREEMPH`):
```xml
<Param name = "DEBUG.IMGPROC.PREEMPH" type = "text" value = "SQRT">
    <LegalValues>
        <Choice UiTxt = "SQRT">SQRT</Choice>
        <Choice UiTxt = "LINEAR">LINEAR</Choice>
        <Choice UiTxt = "EQUISTOP">EQUISTOP</Choice>
        <Choice UiTxt = "REDcolor">REDcolor</Choice>
        <Choice UiTxt = "REDcolor 2">REDcolor2</Choice>
        <Choice UiTxt = "REDcolor 3">REDcolor3</Choice>
        <Choice UiTxt = "REDLOG">REDLOG</Choice>
    </LegalValues>
```

This debug parameter controls the pre-emphasis curve applied before color matrix — likely maps to the internal `GNCamera_gammaFLUT` / `GNCamera_contrastFLUT` pipeline.

### FLUT (Film Look-Up Table) Functions

From the symbol/string table at `0xDD87F4`, the FLUT subsystem exports these functions:

| Symbol                               | Description                               |
|--------------------------------------|-------------------------------------------|
| `FLUTExceptionList`                  | Exception/error list handler              |
| `FLUTGain`                           | Apply gain (exposure) to LUT              |
| `FLUTGetLut`                         | Retrieve the computed LUT data            |
| `FlUtilsEraseGroup`                  | Erase a LUT group from flash              |
| `FlUtilsProgramGroupFromFile`        | Program LUT group from file               |
| `FlUtilsProgramGroupFromZippedFile`  | Program LUT group from zip file           |
| `FlUtilsVerifyGroupWithFile`         | Verify LUT group against file             |
| `FlUtilsVerifyGroupWithZippedFile`   | Verify LUT group against zip file         |
| `FLUTInitialize`                     | Initialize the FLUT subsystem             |
| `FLUTInitializeFast`                 | Fast (partial) initialization             |
| `FLUTIteratorConversion`             | Iterate conversion over LUT entries       |
| `FLUTIteratorConversionFast`         | Fast iterator (bulk conversion)           |
| `FLUTSetupGN`                        | Set up FLUT for GainNoise curve           |
| `FLUTSize`                           | Return size of current LUT                |
| `FLUTUnified`                        | Unified LUT combination                  |
| `FLUTWhiteBalanceFromRAWRGB`         | White balance entry point from raw RGB    |

### GNCamera Color Pipeline Globals

From string table at `0xDDA459` (`GNCamera_*` variables):

```
GNCamera_contrastFLUT       — contrast curve LUT
GNCamera_contrastValue      — scalar contrast value
GNCamera_curveFLUT          — tone curve LUT
GNCamera_exposureCompensation — EV compensation
GNCamera_FLUTControl        — FLUT enable/mode control
GNCamera_ForceLutUpdate     — force LUT refresh flag
GNCamera_gammaFLUT          — gamma curve LUT
GNCamera_gammaType          — enum: SQRT/LINEAR/EQUISTOP/REDcolor[N]/REDlogFilm
GNCamera_saturation         — saturation scalar
GNCamera_SensorColorMatrix  — 3×3 sensor-to-XYZ matrix
GNCamera_SeparateSetupMatrix— separate setup matrix flag
GNCamera_setupFLUT          — setup/CDL LUT
GNCamera_SignalOffFLUT      — signal offset (black point) LUT
```

### Color Pipeline (Make* functions)

From string table at `0xDE0C50`:
```
MakeFLUT           — combine all LUTs into final pipeline LUT
MakeFLUTCombine    — combine two LUTs
MakeGammaFLUT      — generate gamma curve LUT (for current gammaType)
MakeUserCurve      — generate user-defined tone curve
MakeViewLUT        — generate monitor/viewfinder LUT
```

### Pipeline Order (inferred)

```
RAW sensor data
    ↓
White balance matrix (FLUTWhiteBalanceFromRAWRGB)
    ↓
3×3 color matrix (GNCamera_SensorColorMatrix)
    ↓
Tone/gamma LUT (GNCamera_gammaFLUT via MakeGammaFLUT)
    → gammaType selects: SQRT | LINEAR | EQUISTOP | REDcolor | REDcolor2 | REDcolor3 | REDlogFilm
    ↓
FLUT adjustment (GNCamera_FLUTControl, GUI.PAINT.EXPOSURE.FLUT ± 4.0 EV)
    ↓
Contrast / saturation (GNCamera_contrastFLUT, GNCamera_saturation)
    ↓
Output LUT for monitor/viewfinder (MakeViewLUT)
```

### COLOR_MATRIX Resource

From XML at `0xCBA89F`:
```xml
<Resource type = "GUI.PAINT.COLOR_MATRIX">
    <matrix>
        <dimensions><rows>3</rows><columns>3</columns></dimensions>
        <data>
            <row>1.0  2.0  3.0</row>
            <row>4.0  5.0  6.0</row>
            <row>7.0  8.0  9.0</row>
        </data>
    </matrix>
</Resource>
```
*(Default identity-ish matrix — actual calibrated values loaded at runtime from `/tffs0/user.cal.gz`)*

---

## 3. FLUT Parameter

### XML Definition (from `0xCA65B8`)

```xml
<Param name = "GUI.PAINT.EXPOSURE.FLUT"
       type  = "float"
       value = "0">
    <Flags>
        <UI/>
        <Profiled type = "look" />
    </Flags>
    <Constraints>
        <Limits>
            <Min>-4.0</Min>
            <Max>4.0</Max>
        </Limits>
        <Choices>
            <Series first="-4.0" last="4.0" increment="0.1" />
        </Choices>
    </Constraints>
</Param>
```

**FLUT** = Film Look-Up Table exposure offset.
- Range: −4.0 to +4.0 (in EV stops, 0.1 increments)
- Profiled type: `look` (saved per-look profile, not system)
- Controls: `GNCamera_FLUTControl` float variable
- UI label: `FLUT` (shown in `Panel_FLUT` OSD panel)

### Slave Camera FLUT (Master/Slave mode)

From operational notes: *"FLUT parameter remains independent on Slave camera when in Master/Slave mode."*

FLUT sync parameters:
- `CAMERA.SLAVE_MODE_IMPORT_FLUT` — trigger slave FLUT import from master
- `GUI.PAINT.CW.SLAVE.SHADOWFLUT` — cold-white slave shadow FLUT
- `GUI.PAINT.CCW.SLAVE.SHADOWFLUT` — cold-white CCW slave shadow FLUT

---

## 4. RECORD / HANC Metadata Flag

### Known Issue Fixed in Build 32

From release notes:
> *"Fix HANC metadata RECORD flag"*

HANC (Horizontal Ancillary data) is embedded in the HD-SDI blanking interval. The RECORD flag indicates the camera is actively recording.

### HD-SDI Driver

- Driver init string: `"Initializing HD-SDI driver..."` at `0xD30A9D`
- RECORD tally parameter: `GUI.PROGRAM.TALLY` (XML at `0xC864B2`)
  - Legal values: `TALENT · RED · BLINK_RED · BLINK_1 · BLINK_AMBER · BLINK_GREEN`

The RECORD_IN HANC flag is separate from the visual tally. It is asserted in the HD-SDI HANC packet during the recording window.

### Known Timing Behavior (from operational notes)

> *"RECORD tally in HD-SDI HANC indicates 'in record' earlier than the first frame of the recorded .R3D file, and stays enabled a few frames after the last frame."*

This is expected behavior (not a bug). The Build 32 fix corrected a different problem: the RECORD flag was not being set correctly in the HANC data stream (separate from the timing offset).

### Investigation Points

The HD-SDI driver is in code region `0x1C18DC` and nearby. To find the HANC RECORD flag write:
1. Search for writes to the HD-SDI MMIO base `0x40600000` + HANC register offset
2. Cross-reference with the RECORD state machine (`VIDEO.RECORD.*` parameters)
3. Look for the `GPI trigger` path which also routes to the RECORD tally logic

---

## 5. String Cross-Reference Table

### Code → String Address Map

| String content                                     | Offset (data) | Access from code range |
|----------------------------------------------------|---------------|------------------------|
| `OSD::GoSplash() UPGRADE.AVAILABLE!...`            | `0xAC4D08`    | SWF at `0x9E03BC`      |
| `UpgradeMC::SmartUpgrade() envoked...`             | `0xAED7A1`    | ~`0x3xxxxx` (C++ code) |
| `SmartUpgrade() Upgrade file 'su.tar' detected`    | `0xAED85C`    | ~`0x3xxxxx`            |
| `SmartUpgrade() NO UPGRADE file 'su.tar' detected` | `0xAED92F`    | ~`0x3xxxxx`            |
| `/tffs0/upgrade/redone.su`                         | `0xD3632F`    | upgrade search code    |
| `/ata00:1/upgrade/redone.su`                       | `0xD3634D`    | upgrade search code    |
| `GNCamera_FLUTControl = %f`                        | `0xD451F5`    | FLUT apply code        |
| `GNCamera_curveActive`                             | `0xD451F5`    | FLUT apply code        |
| `Initializing HD-SDI driver...`                    | `0xD30A9D`    | device init sequence   |
| `Initializing IOFPGA communication lib`            | `0xD30AXX`    | device init sequence   |

### PPC Address-Load Pattern Reference

To find code that references a data string at address `0xABCDEF`:

```python
ha = ((0xABCDEF + 0x8000) >> 16) & 0xFFFF   # high-adjusted
lo = 0xABCDEF & 0xFFFF                        # low 16 bits (signed)
# Search for: lis rX, ha  (0x3C?0HHHH)
# Then:       addi rX, rX, lo  OR  lbz/lwz rX, lo(rY)
```

Example for `0xAED7A1`:
- `ha = (0xAED7A1 + 0x8000) >> 16 = 0x00AF`
- `lo = 0xD7A1` (signed = -0x285F)
- Search code for `lis rX, 0x00AF` followed within 4 instructions by `0xD7A1` low-word

---

## 6. Ghidra / r2ghidra Import Settings

### Ghidra

1. **New Project** → Import `reverse/build_32/extracted/software.bin`
2. Format: **Raw Binary**
3. Language: **PowerPC:BE:32:default**
4. Base address: `0x00000000`
5. After import, set entry point: `0x00000000`
6. Run **Auto Analyze** with: `Aggressive Instruction Finder`, `Decompiler Parameter ID`
7. Add bookmarks / labels from this table:

```
0x00000000  romInit_reset
0x0036C350  usrInit_main
0x001C18DC  sysSerialInit
0x0000DCB0  sysHwInit_seq
0x0000D8A0  sysClkHelper
0x00012D90  mmio_dispatch
0x00E9BF20  bss_start
0x01153480  bss_end
```

8. Mark `0x700000 – 0xDFFFFF` as **DATA** to prevent code analysis in the resource/SWF regions.
9. The XML documents at `0x9D2AE0` and `0xC6E1A4` can be carved and saved for reference:
   - Run `binwalk -e software.bin` (already done; output in `_software.bin.extracted/`)

### r2ghidra (Ghidra decompiler plugin for r2)

```r2
# Install: r2pm -ci r2ghidra
# Open binary
r2 -a ppc -b 32 -e cfg.bigendian=true software.bin

# Full analysis (may take 10+ minutes on 15MB binary)
aaa

# Label key symbols
f sym.usrInit      @ 0x36c350
f sym.sysSerial    @ 0x1c18dc
f sym.bss_start    @ 0xe9bf20
f sym.bss_end      @ 0x01153480

# Decompile a function
pdg @ sym.usrInit    # Ghidra decompile
pdf @ sym.usrInit    # r2 disassemble

# Find all calls to FLUTGain (address unknown — find with axt after labeling)
# axt @ <FLUTGain_addr>
```

### r2 Static Analysis (no install needed)

```bash
# Quick static analysis of boot sequence
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -q -c 'aef; pdf @ 0x36c350; pdf @ 0x1c18dc' \
   reverse/build_32/extracted/software.bin

# Find strings and cross-refs
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -q -c 'iz; aaa; axF' \
   reverse/build_32/extracted/software.bin
```

---

## 7. File Locations

| File                                             | Description                              |
|--------------------------------------------------|------------------------------------------|
| `reverse/build_32/extracted/software.bin`        | Main firmware binary (PPC32 BE, 15 MB)  |
| `reverse/build_32/extracted/fpga.bin`            | I/O FPGA Xilinx bitstream (4 MB)        |
| `reverse/build_32/extracted/_software.bin.extracted/` | binwalk carve output (SWFs, XML, gzip) |
| `reverse/build_32/build32_static_analysis.md`    | Phase 1 & r2 static analysis reference  |
| `reverse/build_32/build32_subsystem_map.md`      | This file                               |
| `scripts/analyze_build.py`                       | Decrypt + extract + static analysis tool |
| `scripts/patch_firmware.py`                      | QEMU hardware stub patcher (update for Build 32) |
| `scripts/qemu_boot.sh`                           | QEMU launch script (update for Build 32) |
| `scripts/r2_debug.r2`                            | r2 debug session script (update for Build 32) |
