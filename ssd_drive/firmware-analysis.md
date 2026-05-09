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
| `Adtron A25FB-32GC21N` | `RedFlash` | Adtron 32GB 2.5" SLC SATA SSD — likely the original REDMAG |
| `WDC WD800BEVS-22LAT0` | `RedSata (WDC)` | Western Digital Scorpio Blue 80GB 2.5" HDD |
| `HTS721010G9SA00` | `RedSata (Hitachi)` | Hitachi Travelstar 7K100 100GB 2.5" HDD |

> **Note:** The Toshiba HG3 (`THNSNC256GBSJ`) does NOT appear in Build 13 strings.
> This is expected — the HG3 was released in 2011, while Build 13 is from 2008.
> The Toshiba was added in a later firmware build (likely Build 17–30).

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
configured via vendor-specific commands or EEPROM programming. If the model string can be
set to match one of the approved drive entries, the camera firmware will accept the drive.

**Recommended target model strings (from later firmware builds, where Toshiba appears):**
- Later builds (Build 17–32) likely add `THNSNC256GBSJ` and possibly other approved SSDs
- Extracting and analyzing a later firmware build would reveal the complete current list

### Option B — Firmware Patch

Patch the `IsCompatible()` function in the VxWorks image to always return `true` (DigMag).
This requires:
1. Locating `_ZN15DigMagMgrModule12IsCompatibleEv` in the binary
2. Replacing the model-string comparison logic with a direct `return true`
3. Packaging the patched firmware as an upgrade

This approach works on any modern SATA SSD but requires modifying the firmware image.
The encryption key for Build 17+ is known (`M1H5gwOXh757rIRVY6Gj2tN080AYSX03`), so
patching encrypted builds is feasible.

### Option C — Use a Firmware Version that Supports the Target SSD

Build 32 (v32.0.3) is the latest firmware. It was released after the Toshiba HG3 and
likely contains the complete approved-drive list including the THNSNC256GBSJ. A camera
running Build 32 may accept generic modern SSDs that weren't in earlier builds.

**Action needed:** Extract and analyse Build 17–32 firmware to find the complete
`IsCompatible()` drive table.

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

1. **Analyse later firmware (Build 17–32)** to extract the complete `IsCompatible()` drive table:
   ```bash
   # Decrypt Build 32
   openssl enc -d -aes-256-cbc -md md5 \
     -pass pass:M1H5gwOXh757rIRVY6Gj2tN080AYSX03 \
     -in firmware/builds/build_32_v32.0.3.zip -out /tmp/build32.tar.gz
   ```

2. **Locate `_ZN15DigMagMgrModule12IsCompatibleEv`** in the binary via cross-reference
   from the mangled symbol name (if present in debug strings) or by tracing calls to
   the MEDIA.DIGMAG.TYPE parameter setter.

3. **Test a SATA SSD via eSATA** (if accessible) to observe the firmware's compatibility
   response before committing to internal replacement.

4. **Identify the complete model string table** by searching for the known model strings
   (`Adtron`, `WDC`, `Hitachi`, `THNSNC`) in later firmware builds and listing all adjacent entries.
