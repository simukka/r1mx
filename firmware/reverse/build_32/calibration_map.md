# Build 32 v32.0.3 — Calibration Map

What can be **calibrated** in the RED ONE MX Build 32 firmware, where the data lives,
and which code paths produce/consume it. Sourced from string/XML extraction of
`extracted/software.bin`, the `app_modules/vpimgproc/` symbol table, `panels.xml`, and
the `GUI.OSD_Components.CalibrateMC` ActionScript class.

> **Scope note.** "Calibration" here spans three distinct layers that the firmware keeps
> separate: (1) **sensor electrical** setup (DAC/voltage references), (2) the **on-FPGA
> per-pixel correction engine** (`VpImgProc`), and (3) **user/factory image calibration**
> (black-shading + factory cal file). The color-science pipeline (matrix/WB/FLUT/gamma) is
> a fourth, look-oriented layer documented in `build32_subsystem_map.md §2` and summarized
> here for completeness.

---

## 0. The three calibration layers at a glance

| Layer | What it corrects | Where stored | Who triggers it |
|-------|------------------|--------------|-----------------|
| **L1 — Sensor electrical** | ADC reference voltages, ramp/offset DACs, sun-spot clamp | `FactoryDefaults.xml` (`RomDrive:\Config\`) as `DEBUG.SENSOR.*` integers | Boot-time sensor init (`VpSensorChip.cpp`) |
| **L2 — On-FPGA correction** | Per-pixel offset/gain, black level, column offset, defect pixels | FPGA "Cal RAM" (live), loaded from cal file | `VpImgProc` engine (`VpCalRam*`, `VpBlackLevel*`, `VpDefect*`) |
| **L3 — Image calibration files** | Black-shading map (FPN), factory dark/light cal | `…/calibrate/sensor.cal` (+ compressed user cal) | User menu (`CALIBRATE.*` params, `CalibrateMC`) |
| **L4 — Color science / look** | White balance, tint, color matrix, gamma, FLUT, per-ISO NR | Profiled "look" params, runtime `COLOR_MATRIX` resource | Paint menus + `GNCamera_*` pipeline |

---

## 1. Calibration data storage (file paths)

The on-disk calibration artifact is **`sensor.cal`**, searched across all removable media:

```
/ata00:1/calibrate/sensor.cal     (CF slot 0)
/ata10:1/calibrate/sensor.cal     (CF slot 1)
/usbd0/calibrate/sensor.cal       (USB)
%s/sensor.cal                     (generic, base path substituted at runtime)
```

Factory defaults (incl. all L1 sensor voltages) ship in firmware ROM:

```
RomDrive:\Config\FactoryDefaults.xml
```

Related runtime files seen near the cal paths: `UserMap.raw`, `MatrixDump.txt`,
`4480x1876.raw` (full-frame raw dumps used during cal capture).

Relevant log strings (cal file I/O):
- `Reading header from factory calibration data`
- `Failed to read calibration header from flash`
- `Writing user calibration file` / `Installing user calibration file`
- `Failed to create/write [compressed] user calibration data file '%s' (errno=…)`
- `Cal RAM load %s (%s calibration used)`
- `New calibration file generated successfully`

So there are **two cal sources** the firmware merges: a **factory** cal (header read from
flash) and a **user** cal (created/written to media, optionally gzip-compressed). The UI
flag `MERGINGFACTORYCAL` confirms a merge step.

---

## 2. Layer 1 — Sensor electrical calibration (`DEBUG.SENSOR.*`)

These are per-model integer DAC settings (nanovolts) defining the sensor's analog front
end. Two model variants ship in the same firmware — `REDONE.*` (Mysterium / ONE MX) and
`EPIC.*` (Mysterium-X) — selected at runtime.

| Parameter | REDONE value | EPIC value | Meaning |
|-----------|-------------:|-----------:|---------|
| `DEBUG.SENSOR.VBSTLINE` | 3,600,000 | — | Boost line voltage |
| `DEBUG.SENSOR.VREFCAL` | 700,000 | — | Reference calibration voltage |
| `…SENSOR.VOFFSETPTOP` | 650,000 | 996,000 | Pixel offset, top |
| `…SENSOR.VOFFSETPBOT` | 1,150,000 | 1,377,000 | Pixel offset, bottom |
| `…SENSOR.VREFADCDIV8` | 225,000 | 323,000 | ADC reference ÷8 tap |
| `…SENSOR.VREFADCDIV32` | 56,250 | 80,000 | ADC reference ÷32 tap |
| `…SUNSPot.VREFCLAMP` | — | 1,740,000 | Black-sun clamp voltage |
| `…SUNSPOT.VTXMIDDAC` | 1,600,000 | — | Sun-spot transfer-gate mid DAC |
| `…SUNSPOT.ENABLE` | true | true | Black-sun suppression on |

Code: `app_modules/vpimgproc/VpSensorChip.cpp`; programmed via the `Vp*Set` analog
register accessors (`VpAnalogVltEnSet`, `VpAdcTstModeSet`, `VpAosTopLineAddrSet`,
`VpAosBotLineAddrSet`, …).

> **"Black sun" / SSD:** the Mysterium sensor blooms to *white* on extreme overexposure;
> the SSD (Sun-Spot Detect) logic clamps it back to black. GUI toggle: `Eng_BlackSun`
> labeled **"SSD ENABLE"**. This is a calibration-adjacent correction, not a stored map.

---

## 3. Layer 2 — On-FPGA per-pixel correction engine (`VpImgProc`)

The VP (Video Processor) FPGA holds a **Cal RAM** that applies per-pixel and per-column
corrections in hardware on the live image stream. The firmware-side driver classes live
in `app_modules/vpimgproc/`:

```
VpImgProc.cpp        VpImgProcType.cpp     VpSensorChip.cpp
VpBlackBalance.cpp   VpGain.cpp            VpColorMatrix.cpp
VpGamma.cpp          VpFilters.cpp         VpMagnification.cpp   VpZebra.cpp
```

### 3a. Cal RAM (per-pixel correction store)

| Symbol | Role |
|--------|------|
| `VpCalRamActivate` / `VpCalRamDeactivate` | Enable/disable the per-pixel correction RAM |
| `VpCalRamFill` / `VpCalRamWrite` / `VpCalRamRead` | Load/read correction coefficients |
| `VpCalRamTest` / `VpCalRamLastStatus` / `VpCalRamGetReport` | Self-test + status |
| `VpCalRamStateStr` | Human-readable state |
| `VpCalPerPixelDisableSet` | Master per-pixel-correction bypass |
| `VpCalFrameAddr/Len/LineCount/LineStride [Get/Set]` | DMA geometry for cal-frame capture |
| `VpCalFsmStateGet` | Calibration finite-state-machine state |

### 3b. Black-level / BCS (Black Calibration Subtraction)

| Symbol | Role |
|--------|------|
| `VpBlackLevelModeSet` / `VpBlackLevelDisableSet` | Black-level loop mode / bypass |
| `VpBlackLevelSumGet` / `VpBlackLevelOutputCalc` | Read accumulated black sum, compute output |
| `VpBlackLineOffsetSet` / `VpBlackSampleOffsetSet` | Optical-black window position |
| `VpCalBlackLevelSet` / `VpCalBlackLevelCoeffSet` / `…ModeSet` / `…DisableSet` | Per-cal black-level coefficients |
| `VpCalBcs*` (`Bypass/Disable/HoldUpdate/IndCompMode/LoopCoef/MixModeDisplay/SendToFile/SingleFrame/SwapColForLuma/TotLineCount`) | Black-Calibration-Subtraction servo loop config |
| `VpBlackBalance` (class, `VpBlackBalance.cpp`) | Per-channel black balance; `ConfigureHw`/`DisableHw` |

### 3c. Gain

| Symbol | Role |
|--------|------|
| `VpGain` (class, `VpGain.cpp`) | Digital gain stage; `ConfigureHw`/`DisableHw` |
| `VpGainSet` | Set gain register |
| `EPIC/.PAINT.GAIN.ANALOG_{RED,GREEN,BLUE}` | Per-channel analog gain (EPIC) |
| `GUI.PAINT.GAIN.{MASTER,RED,GREEN,BLUE}_VALUE` | User digital gain (master default 1.0) |
| `DEBUG.GAIN.BOOST` | Debug gain boost |

### 3d. Column offset (vertical FPN)

`VpColumnOffsetSet` / `VpColumnOffsetGet` — per-column offset correction (fixes vertical
banding / column FPN characteristic of CMOS sensors).

### 3e. Defect (bad-pixel) correction

| Symbol | Role |
|--------|------|
| `VpDefectGrnCodeSet` / `VpDefectGrnFIRSet` | Green-channel defect map + interpolation FIR |
| `VpDefectRbCodeSet` / `VpDefectRbFIRSet` | Red/Blue-channel defect map + FIR |
| `VpDefectMidLevelSet` | Mid-level defect threshold |
| `gDefectCodeGrn` / `gDefectCodeRedBlue` | Defect code tables (globals) |
| `gDefectCoeffsGrn` / `gDefectCoeffsRedBlue` | Defect correction coefficient tables |

Detected during a light/dark cal capture — log strings:
`Calculating offsets and identifying bad pixels`,
`Determining bad pixel correction algorithms`,
`%d (R/G1/G2/B) new bad pixels detected`, `%d total new bad pixels detected`.

---

## 4. Layer 3 — User-facing calibration (`CALIBRATE.*`) + black shading

### 4a. CALIBRATE parameter reference

| Parameter | Type | Purpose |
|-----------|------|---------|
| `CALIBRATE.FACTORY.FILE_AVAILABLE` | bool | Factory cal present on media? (UI "CAL PRESENT") |
| `CALIBRATE.FACTORY.APPLY_CAL_FILE` | — | Apply the factory cal file |
| `CALIBRATE.FACTORY.STATE` | text | Factory cal FSM state (→ IDLE on exit) |
| `CALIBRATE.USER.CREATE_CAL_FILE` | — | Generate user cal from captured frames |
| `CALIBRATE.USER.DELETE_CAL_FILE` | — | Delete user cal |
| `CALIBRATE.USER.STATE` | text | User cal FSM state (→ IDLE on exit) |
| `CALIBRATE.CAPTURE_CLIPNAME` | text | Source clip used as cal input (`calibrationclip`) |
| `CALIBRATE.CAPTURE_FRAMECOUNT` | int | Frames to average for cal |
| `CALIBRATE.CAPTURE_CURRENTFRAME` | int | Capture progress counter |
| `CALIBRATE.APPLYGAIN` | — | Apply gain portion of cal |
| `CALIBRATE.OUTPUTFORMAT` | — | Cal output format |
| `GUI.CALIBRATE.CAPTURE_FRAMECOUNT` | int | UI mirror of frame count |
| `EPIC/REDONE.DEBUG.CALIBRATE.OHI` | int | Cal offset clamp, high (EPIC 10 / REDONE 16) |
| `EPIC/REDONE.DEBUG.CALIBRATE.OLO` | int | Cal offset clamp, low (EPIC −10 / REDONE −16) |
| `SYSTEM.MANUFACTURING.CALIBRATION_DATE` | text | Factory cal timestamp |
| `SYSTEM.MANUFACTURING.CALIBRATION_PROCESS_VER` | text | Cal procedure version |

### 4b. Capture dispatches (GUI → firmware)

```
CALIBRATE_CAPTURE_DARK        — grab dark frame (no light)
CALIBRATE_CAPTURE_LIGHT       — grab flat-field light frame
CALIBRATE_CAPTURE_LIGHT_F24   — grab light frame with F24 reference source
CALIBRATE_APPLY               — apply captured cal
USERCAL_START / USERCAL_RESTORE  — black-shading start / restore (Maintenance menu)
```

Operator prompts confirm the workflow:
`expose the sensor to the F24 calibration light source`,
`make sure the sensor is exposed to the calibration light source`,
`OFFSET CORRECTION AND PIXEL CORRECTION ON FOR CAL CAPTURES!`

### 4c. Black-Shading state machine (FPN map)

User-initiated black-shading (dark-frame FPN map) runs an explicit, banner-driven FSM —
the LCD shows each stage:

```
BLACK SHADE CALIBRATE
  → BLACK SHADING: SAMPLING SENSOR...
  → BLACK SHADING: ANALYZING DATA...
  → BLACK SHADING: CALCULATING BLACK LEVEL...
  → BLACK SHADING: CALCULATING OFFSETS...
  → BLACK SHADING: CALCULATING CORRECTIONS...
  → BLACK SHADING: MERGING...          (merges with factory cal)
  → BLACK SHADING: INSTALLING...
  → BLACK SHADING: WRITING...          (writes sensor.cal)
  → BLACK SHADING: ANALYSIS COMPLETE.
```

Capture-stage logs: `buffers are primed, starting calibration capture`,
`captured/wrote calibration frame %d`, `Calibration summer initialized for %s cal`
(the "summer" = frame accumulator/averager).

---

## 5. Layer 4 — Color science / look calibration

Full pipeline in `build32_subsystem_map.md §2`. Calibratable elements:

| Element | Param / symbol | Range / default |
|---------|----------------|-----------------|
| White balance (color temp) | `PAINT.WHITE_BALANCE.CURRENT` (int K) | 1700 – 100000, default **5600** |
| Tint | `PAINT.TINT.CURRENT` (int) | −100 – +100, default 0 |
| Auto WB | `GUI.PAINT.WHITE_BALANCE.AUTO` / `KEYFNC_DO_AUTO_WHITE_BALANCE` | — |
| ISO / sensitivity | `GUI.PAINT.EXPOSURE.ISO` | 100…2000 (100,125,160,200,250,320,400,500,640,800,1000,1280,1600,2000), default **320** |
| ISO tweak | `DEBUG.ISO.TWEAK` (float) | default −0.3 |
| Color matrix (3×3) | `GUI.PAINT.COLOR_MATRIX` resource (`@0xCBA89F`) / `GNCamera_SensorColorMatrix` / `VpColorMatrix.cpp` | calibrated values loaded at runtime |
| Gamma curve | `GNCamera_gammaType` / `MakeGammaFLUT` / `VpGamma.cpp` | SQRT/LINEAR/EQUISTOP/REDcolor[1-3]/REDlogFilm |
| FLUT (exposure offset) | `GUI.PAINT.EXPOSURE.FLUT` (`@0xCA65B8`) | −4.0 … +4.0 EV, 0.1 step |
| Contrast / saturation | `GNCamera_contrastFLUT` / `GNCamera_saturation` | — |
| Pre-emphasis (debug) | `DEBUG.IMGPROC.PREEMPH` (`@0xC7249E`) | SQRT default |

### Per-ISO noise-reduction calibration tables

`PAINT.NR_FILT.ISO_<n>.{RED,GREEN,BLUE}.{SLOPE,STRENGTH}` — a full table for **every ISO
rating**. Defaults are uniform across ISOs in this build (SLOPE: R/B=64, G=450;
STRENGTH=1.0), i.e. shipped flat and tuned per-unit/firmware-rev rather than per-capture.

---

## 6. Thermal calibration coefficients

Temperature sensors carry per-sensor linear-fit calibration coefficients
(`*_A` = slope, `*_B` = offset):

```
SYSTEM.THERMAL.SENSOR.VP_A / VP_B          (VP FPGA / imager die)
SYSTEM.THERMAL.SENSOR.CPU_A / CPU_B
SYSTEM.THERMAL.SENSOR.PWR_SUPPLY_A / _B
SYSTEM.THERMAL.SENSOR.SENSOR               (sensor temp readout)
```

Plus thresholds (alarm/shutdown/overtemp/undertemp) and fan-control servo settings under
`SYSTEM.THERMAL.{ALARM,SHUTDOWN,FAN}.*`. Sensor temperature feeds dark-current behavior,
so thermal cal indirectly affects black-level accuracy.

---

## 7. Manufacturing / identity metadata (read-mostly)

Written at factory cal time, surfaced for traceability:

```
SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER
SYSTEM.MANUFACTURING.IMAGER_SERIAL_NUMBER
SYSTEM.MANUFACTURING.CALIBRATION_DATE
SYSTEM.MANUFACTURING.CALIBRATION_PROCESS_VER
SYSTEM.MANUFACTURING.RUNTIME
SYSTEM.MANUFACTURING.ALIAS
SYSTEM.MANUFACTURING.PASSWORD.{ADMIN,USER}   (gate eng/cal menus)
```

The cal file's header (the "factory calibration data" header read from flash) is expected
to be keyed to `IMAGER_SERIAL_NUMBER` — a cal file is sensor-specific.

---

## 8. GUI access map

| Menu path | Panel / class | Actions |
|-----------|---------------|---------|
| Engineering → **CALIBRATE** | `Panel_Calibrate` / `CalibrateMC` | GRAB DARK, GRAB LIGHT, GRAB LIGHT F24, APPLY CAL, CAL PRESENT |
| **MAINTENANCE** → BLK SHADING | `Panel_BlkShading` | START (`USERCAL_START`), RESTORE (`USERCAL_RESTORE`) |
| MAINTENANCE → RESTORE | — | LOOK / USER / SYSTEM → Factory Defaults |
| SENSOR → COLOR TEMP | `Panel_WhiteBalance` | WB / tint |
| SENSOR → SENSITIVITY | `Panel_Sensitivity` | ISO |

`GUI.OSD_Components.CalibrateMC` drives capture: prompts "DARK CAL?", flags
`__autoApplyCal`, `__captureComplete`, `__factoryCal`; on completion sets
`CALIBRATE.{USER,FACTORY}.STATE = IDLE` and returns to `Panel_Calibrate`. The cal menus
are gated behind `SYSTEM.MANUFACTURING.PASSWORD.*` capability checks (`VxCap`).

---

## 9. Summary — what is calibratable

1. **Sensor electrical** (L1): ADC reference voltages, pixel offsets, ramp/sun-spot DACs —
   `DEBUG.SENSOR.*` / `SUNSPOT.*`, per REDONE/EPIC model, from `FactoryDefaults.xml`.
2. **Per-pixel/per-column correction** (L2): black level, black balance, column offset,
   bad-pixel map+FIR, digital gain — `VpCalRam*` / `VpBlackLevel*` / `VpColumnOffset*` /
   `VpDefect*` / `VpGain`, applied live in the VP FPGA.
3. **Black-shading / dark-frame FPN map** (L3): user-run FSM that samples the sensor,
   computes offsets/corrections, merges with factory cal, writes `…/calibrate/sensor.cal`.
4. **Factory cal file** (L3): dark + flat-field (F24 light) capture, header keyed to imager
   serial, applied via `CALIBRATE.FACTORY.APPLY_CAL_FILE`.
5. **Color/look** (L4): white balance (1700–100000 K), tint (±100), ISO (100–2000),
   3×3 color matrix, gamma curve, FLUT (±4 EV), contrast/saturation, per-ISO NR tables.
6. **Thermal** sensor linear-fit coefficients (`*_A`/`*_B`) and thresholds.

## 10. Open questions / next steps

- **`sensor.cal` binary format** — header layout, coefficient packing, gzip framing.
  Capture one from a working camera (`/ata00:1/calibrate/sensor.cal`) and diff against a
  fresh black-shading run.
- **Cal RAM geometry** — confirm `VpCalFrameLen`/`LineStride`/`LineCount` against the
  4480×1876 raw dimension and the FPGA per-pixel coefficient width.
- **Factory vs user merge** — exact precedence in the `MERGINGFACTORYCAL` step
  (additive offsets vs override).
- **FPGA-resident BRAM cal tables** — extractable from the bitstream via FAR block-type
  `010` frames (see `re_reference.md` Frame Structure) to recover any hard-coded LUTs.
- Locate the C++ cal FSM entry (consumer of `CALIBRATE.USER.CREATE_CAL_FILE`) to map the
  `BLACK SHADING:` banner sequence to addresses.
```
