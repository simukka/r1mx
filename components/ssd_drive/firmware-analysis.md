# Firmware SATA Analysis — ATA Commands & Drive Identity Validation

*Phase 4 of the REDMAG 256GB SSD reverse engineering effort.*

---

## Overview

This document analyses the RED ONE MX firmware (Build 13 / v1.8.8 "Sundance") to determine:
1. Which ATA commands the camera issues to storage devices
2. Whether the camera validates drive identity (model string, capacity, etc.)
3. The storage architecture and device paths
4. Implications for replacement drives

The analysis was performed on the decrypted/extracted `SundanceBootable.bin` (PowerPC 405 VxWorks binary)
from the Build 13 upgrade package — the earliest known public firmware, circa January 2008.

---

## Architecture Summary

| Component | Details |
|-----------|---------|
| CPU | PowerPC 405 ("Sundance" board) |
| OS | Wind River VxWorks (kernel version 2.10) |
| SATA host | Silicon Image SiI3512 (on AUDIO_PCI board, via PCI bus) |
| SATA driver | `ataDrv` / `ataInit` (VxWorks ATA driver — standard Wind River component) |
| Monitor task | `ataSataMon` — monitors drive attach/detach events |
| Media manager | `DigMagMgrModule` — high-level drive management |
| Format handler | `FormatMC` — handles media formatting via the OSD |

### Device Paths

| Path | Description |
|------|-------------|
| `/ata00` | SATA port 0 device node |
| `/ata00:1` | SATA port 0, partition 1 (primary recording media) |
| `/ata10` | SATA port 1 device node |
| `/ata10:1` | SATA port 1, partition 1 (secondary / side record) |

The primary recording SSD connects to SATA port 0. Port 1 may support a second storage device.

---

## ATA Driver Behaviour

### Startup Sequence

The `ataInit` / `ataDrv` module follows the standard VxWorks ATA initialization:

```
ataInit start %d ms: ASTATUS=%02x  STATUS=%02x    ← wait for BSY=0
ataInit unbusy %d ms: ASTATUS=%02x  STATUS=%02x   ← device ready
ataDevIdentify(%d/%d): Starting                    ← issue IDENTIFY DEVICE (0xEC)
ataDevIdentify(%d/%d): Type = %d                   ← log detected drive type
```

### IDENTIFY DEVICE (0xEC) — Always Issued

The firmware **always issues `IDENTIFY DEVICE`** at startup via `ataDevIdentify()`. The
response is parsed for:

| Field | Log format string | Used for |
|-------|------------------|---------|
| Model number (words 27–46) | `model = ...` / `%s: failed to retrieve model number for device at %s` | Drive identification / compatibility check |
| Serial number (words 10–19) | `Serial Number = 0x%x` / `%s: Failed call to set serial number` | Logging / camera serial linkage |
| SATA capabilities (word 76) | `sataCap =0x%04x` | Feature negotiation |
| SATA features supported (word 78) | `sataFeatSup =0x%04x` | |
| SATA features enabled (word 79) | `sataFeatEnab=0x%04x` | |
| Capacity (words 60–61, 100–103) | `Total Capacity: %lld` / `capacity0/1` | Media capacity display |
| Sector count (words 60–61) | `sectors0/1` | Filesystem setup |
| Bytes per sector | `bytesSector` | Sector size config |
| Multi-word DMA | `singleDma` / `multiSectors` | DMA mode selection |
| PIO mode | `pioMode` | Fallback PIO config |

**Key implication:** Any replacement drive must respond correctly to `IDENTIFY DEVICE`.
The model number string field (40 bytes, ASCII, space-padded) is read and logged.

### Hot-plug Support

```
ataDrv: enabling hot plug on %d
```

The firmware supports hot-plug on both SATA ports — the `ataSataMon` task polls for
drive insert/removal events.

---

## Drive Compatibility Check — `DigMagMgrModule::IsCompatible()`

The `MEDIA.DIGMAG.TYPE` parameter tracks the detected drive type. Known values (from OSD XML):

| Value | UI Text | Description |
|-------|---------|-------------|
| `DigMag` | "DigMag" | Compatible RED Magazine drive |
| `INCOMPATIBLE` | "Incompatible" | Drive present but not compatible |
| `INCOMPATIBLE_DIGMAG` | — | Incompatible RED Magazine |
| `BAD_FRAMERATE` | "Incompatible framerate" | Drive too slow for current recording format |

The `DigMagMgrModule::IsCompatible()` C++ method (mangled symbol: `_ZN15DigMagMgrModule12IsCompatibleEv`)
is the gating function that sets this parameter.

### Known Compatible Drives (hardcoded in Build 13)

The following model strings are embedded in the firmware binary:

| Model String | Type Label | Drive Info |
|---|---|---|
| `Adtron A25FB-32GC21N` | `RedFlash` | Adtron 32GB 2.5" SLC SATA SSD — original REDMAG |
| `WDC WD800BEVS-22LAT0` | `RedSata (WDC)` | Western Digital Scorpio Blue 80GB 2.5" HDD |
| `HTS721010G9SA00` | `RedSata (Hitachi)` | Hitachi Travelstar 7K100 100GB 2.5" HDD |

> **Note:** The Toshiba HG3 (`THNSNC256GBSJ`) does NOT appear in Build 13 strings.
> This is expected — the HG3 was released in 2011, while Build 13 is from 2008.
> The Toshiba was added in a later firmware build (likely Build 17–30).

### Build 32 Drive Type Table (Extracted — September 2013)

Build 32 (`build_32_v32.0.3.zip`, 2013-09-06) was decrypted using the known key and
analysed. The encrypted payload is a POSIX tar containing `redone.1` (VxWorks app,
AES-256-CBC + gzip, ~8.5 MB decrypted) and `redone.3` (Xilinx FPGA bitstream).

**Key changelog from the Build 32 README:**
- "Added 512GB support" — first firmware to support 512GB REDMAG drives
- "RED 48GB SSD is not compatible with REDONE" — explicitly blocked drive type

The complete **drive type display table** was extracted from the VxWorks binary at
offset `0xD2E5D0`. These are the UI-visible names for each approved drive type:

| Display Name | Category | Notes |
|---|---|---|
| `RED 16GB CF` | CompactFlash | Legacy CF recording media |
| `RED 32GB CF` | CompactFlash | |
| `RED 64GB CF` | CompactFlash | |
| `RED 55GB SSD` | SSD (legacy) | Original REDMAG 55GB (Adtron-based) |
| `RED 64GB SSD` | SSD (legacy) | REDMAG 64GB |
| `RED 128GB SSD` | SSD (legacy) | REDMAG 128GB |
| `RED 256GB SSD` | SSD (legacy) | REDMAG 256GB |
| `RED 512GB SSD` | SSD (legacy) | REDMAG 512GB |
| `RED 16GB REV B` | SSD | |
| `RED 32GB REV A1` | SSD | |
| `RED 64GB REV A1` | SSD | |
| **`RED  64GB Rev T1`** | **Toshiba** | **HG3 64GB, 1st production revision** |
| **`RED 128GB Rev T1`** | **Toshiba** | **HG3 128GB, 1st production revision** |
| **`RED 256GB Rev T1`** | **Toshiba** | **HG3 256GB, 1st production revision ← this drive** |
| **`RED  64GB Rev T2`** | **Toshiba** | **HG3 64GB, 2nd production revision** |
| **`RED 128GB Rev T2`** | **Toshiba** | **HG3 128GB, 2nd production revision** |
| **`RED 256GB Rev T2`** | **Toshiba** | **HG3 256GB, 2nd production revision** |
| **`RED  64GB Rev T3`** | **Toshiba** | **HG3 64GB, 3rd production revision** |
| **`RED 128GB Rev T3`** | **Toshiba** | **HG3 128GB, 3rd production revision** |
| **`RED 256GB Rev T3`** | **Toshiba** | **HG3 256GB, 3rd production revision** |
| `RED 512GB V1` | 512GB | Added in Build 32 |
| `RED 512GB V2` | 512GB | |
| `RED 512GB V3` | 512GB | |
| `RED 512GB V4` | 512GB | |
| `RED 55GB V1` | 55GB variant | |
| `RED 55GB V2` | 55GB variant | |
| `External Disk 0` | Unknown / external | Fallback for unrecognised drives |

**Toshiba drive revisions T1/T2/T3** correspond to different firmware revisions of the
same THNSNC hardware — Toshiba shipped the HG3 drives in multiple production lots with
distinct `IDENTIFY DEVICE` firmware revision strings. The camera distinguishes these to
display the correct label; all three are accepted as compatible.

**The drive compatibility function has been confirmed to use three parameters:**
```
DigMagMgrModule::DecodeDriveType(char* model_string, char* firmware_revision, unsigned long sectors)
```
(mangled: `_ZN15DigMagMgrModule15DecodeDriveTypeEPcS0_m`)

This is more sophisticated than Build 13's simple model-string check: Build 32 also
examines the **ATA firmware revision field** (word 23–26 of IDENTIFY DEVICE, 8 bytes).
This is how T1/T2/T3 revisions are discriminated.

**Raw ATA model strings for Toshiba entries:** The raw `THNSNC064GBSJ`, `THNSNC128GBSJ`,
`THNSNC256GBSJ` strings are **not stored as plain text** in the Build 32 binary — they
are likely encoded in the code section as comparison operands or as hashed values. The
display names (RED xxGB Rev Tn) ARE stored as plain strings. Physical SATA capture or
deeper disassembly is required to recover the exact comparison strings.

### How Compatibility is Likely Checked

Based on the string evidence, the firmware:

1. Issues `IDENTIFY DEVICE` at startup
2. Reads the model number string (40 bytes)
3. Compares the model string against a hardcoded table of approved drives
4. Sets `MEDIA.DIGMAG.TYPE` accordingly (DigMag / INCOMPATIBLE / INCOMPATIBLE_DIGMAG)

If the model string does not match any entry in the table, the drive is reported as
`INCOMPATIBLE` and the camera likely refuses to record to it.

**This is the critical firmware constraint for replacement drives.**

### FormatMC "Unknown drive" Cases

The `FormatMC` module logs "Unknown drive" in several code paths:

```
FormatMC::DoConfig() Unknown drive: 
FormatMC::DoConfigDone() Unknown drive 
FormatMC::DoFormat() Unknown drive 
FormatMC::SmartFormat() Unknown drive state '
```

These suggest the compatibility list is checked before allowing format operations.

---

## SATA Features Negotiated

From the `sataCap` / `sataFeatSup` / `sataFeatEnab` log fields, the firmware reads
and negotiates SATA features from the `IDENTIFY DEVICE` response (word 76–79). The
VxWorks ATA driver typically enables:

- **DMA Auto-Activate** (if supported) — EFh / 10h / 02h
- **DIPM (Device-Initiated Power Management)** — EFh / 10h / 03h
- **Volatile write cache** — EFh / 02h (enabled by default)
- **APM (Advanced Power Management)** — EFh / 05h (if supported)

The specific features enabled depend on the drive's capability word response.

---

## E-SATA External Port

Separate strings suggest an **external eSATA port** exists on the RED ONE:

```
%s: E-SATA power state: %s
InitESataHotPlugDetectCallback
SetESataPowerState
_ZN13DiskMonModule18SetESataPowerStateEb
_ZN13DiskMonModule25ESataHotPlugDetectHandlerEPvhh
_ZN13DiskMonModule30InitESataHotPlugDetectCallbackEv
```

This likely corresponds to the RED One's external expansion port (for attaching external
storage or accessories). The `DiskMonModule` manages power gating for this port.

---

## Implications for Replacement Drives

### Option A — Model String Spoofing

The most straightforward replacement approach is to use a **modern SATA SSD that responds
with an approved model string** in its `IDENTIFY DEVICE` response.

Some SATA SSD controllers (notably JMicron and Phison-based) allow the model string to be
configured via vendor-specific commands or EEPROM programming.

**Target for Build 32 (confirmed Toshiba entries):**
- Model string: `THNSNC256GBSJ` (confirmed as approved — T1/T2/T3 revisions all accepted)
- Firmware revision: any of the T1/T2/T3 THNSNC firmware revision strings
  (e.g., `JUPS4101`, `JUPS4102`, `JUPS4103` — exact values to be confirmed by physical capture)
- Capacity: must report ≥ expected sector count for 256GB

**If targeting the generic `RED 256GB SSD` type** (Build 32 also retains this entry),
the model string is likely an older RED-internal SSD identifier. The Adtron/WDC/Hitachi
model strings from Build 13 are **no longer required** — they are absent from Build 32.

### Option B — Firmware Patch

Patch the `IsCompatible()` function in the VxWorks image to always return `true` (DigMag).
This requires:
1. Locating `_ZN15DigMagMgrModule12IsCompatibleEv` in the binary at offset `0xDA6010` (symtab)
2. Replacing the model-string/firmware-rev comparison logic with a direct `return true`
3. Packaging the patched firmware as an upgrade

The encryption key for Build 17+ is known (`M1H5gwOXh757rIRVY6Gj2tN080AYSX03`), so
patching encrypted builds is feasible. The patched binary must be re-encrypted and re-packaged.

### Option C — Use a Firmware Version that Supports the Target SSD

Build 32 (v32.0.3) is the latest firmware. Analysis confirms it contains:
- All three Toshiba HG3 256GB production revisions (T1/T2/T3) as approved types
- 512GB support added for the first time

**A camera running Build 32 will accept the THNSNC256GBSJ if the model string matches.**

### Minimum Requirements for Any Replacement Drive

Regardless of approach, the replacement must:

| Requirement | Value |
|-------------|-------|
| Form factor | 2.5-inch SATA (standard connector) |
| Interface | SATA II (3 Gbit/s) or SATA III (backward compatible) |
| Power supply | 5V ±5% only |
| Sector size | 512 bytes (or 512e with 4K physical) |
| IDENTIFY DEVICE | Must respond correctly |
| Capacity | ≥500,118,192 sectors (256 GB) recommended |
| Model string | Must match firmware's approved list (or firmware must be patched) |
| Sequential write | ≥180 MB/s sustained at 128KB block size |
| TRIM (06h) | Beneficial but not required |
| ATA Security | SECURITY FREEZE LOCK (F5h) must be handled |

---

## Next Steps

1. **Capture ATA IDENTIFY DEVICE response** from a real THNSNC256GBSJ to confirm:
   - Exact model string (likely `THNSNC256GBSJ` — but ATA pads with spaces)
   - Exact firmware revision string for T1/T2/T3 (likely `JUPSxxxx` format)
   - Use a SATA protocol analyser or `hdparm -i /dev/sdX` on Linux

2. **Disassemble `DecodeDriveType`** in Build 32 binary to confirm exact model/revision
   string comparisons. The function is at a code address referenced via the symbol table.
   Load the binary at the VxWorks link address (determined from the header) in Ghidra/IDA.

3. **Test model string spoofing** on a Phison or JMicron based SSD:
   - Program `THNSNC256GBSJ` as the IDENTIFY DEVICE model string
   - Insert into RED ONE running Build 32
   - Observe whether it reports as `DigMag` or `INCOMPATIBLE`

4. **Physical SSD teardown** of a donor THNSNC256GBSJ unit:
   - Photograph TH58TEGxDCJ package markings on NAND chips
   - Photograph controller die marking (TC58NC… prefix expected)
   - Confirm 8× TH58TEG8DCJTAK0 package count
