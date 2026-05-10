# SSD Drive Datasheets — Findings Summary

*Phase 1 of the REDMAG 256GB SSD reverse engineering effort.*  
*See `ssd_drive/README.md` for the top-level summary.*

---

## Files in This Folder

| File | Source | Content | Format |
|------|--------|---------|--------|
| `cSSD-HG3.pdf` | Toshiba | HG3 Series brief spec (capacities, model numbers, headline specs) | Selectable PDF |
| `document.pdf` | Toshiba | HG3 Series Brochure Rev.1.1 — full specification document | Selectable PDF |
| `Microsoft Word - Document.doc - PS-78320-002.pdf` | 3M (Molex) | Product Specification for 1.8-inch SATA receptacle connector (SMT, right-angle, 3.80mm height) | Scanned images — OCR applied |
| `r1-ssd.pdf` | Unknown (Qt-generated, June 2021) | Single-page image — content not recoverable via OCR (blank page) | Image PDF |

---

## Drive Identification

The REDMAG 256GB SSD is a **Toshiba HG3 Series** drive, model number:

```
THNSNC256GBSJ
```

Decoded using the Toshiba ordering information schema:

| Field | Code | Meaning |
|-------|------|---------|
| Brand | `THN` | Toshiba NAND drive |
| Model type | `SN` | Normal SSD (non-FDE) |
| Controller | `C` | Type C (Toshiba proprietary) |
| Capacity | `256G` | 256 GB (1 GB = 1,000,000,000 bytes) |
| Form factor | `B` | 2.5-type case, 9.5mm height |
| Host I/F | `S` | Standard SATA connector |
| NAND process | `J` | 32nm MLC |

An FDE (Full Disk Encryption) variant also exists: `THNSFC256GBSJ`.

---

## Full Specification (2.5-inch, 256 GB model)

### Electrical

| Parameter | Value |
|-----------|-------|
| Interface standard | ACS-2, SATA revision 2.6 |
| Host transfer rate | 300 MB/s (3.0 Gbit/s max) |
| Supply voltage | 5.0V ±5% |
| Allowable noise/ripple | 100 mV p-p or less |
| Supply rise time | 2–100 ms |
| Over-current protection | Rated current 3.15A |
| Read power (256 GB) | 1.7W Typ. |
| Write power (256 GB) | 3.3W Typ. |
| Idle power (256 GB) | 52mW Typ. |
| Standby/Sleep power | 52mW Typ. (SATA power management, Slumber mode) |

### Performance

| Parameter | Value |
|-----------|-------|
| Sequential read | 220 MB/s average (128KB sequential) |
| Sequential write | 180 MB/s average (128KB sequential) |
| User addressable sectors (256 GB) | 500,118,192 LBA sectors |
| Bytes per sector | 512 |

### Memory

| Parameter | Value |
|-----------|-------|
| NAND type | Toshiba 32nm MLC NAND Flash |
| Controller | Toshiba Type C (proprietary, embedded) |
| Translation modes | Any drive configuration supported |
| LBA modes | 28-bit and 48-bit LBA |

### Mechanical

| Parameter | Value |
|-----------|-------|
| Length | 100.0 mm |
| Width | 69.85 mm |
| Height | 9.5 mm |
| Weight (256 GB / 512 GB) | 58g Typ. |
| Weight (64 GB / 128 GB) | 51g Typ. |

### Environmental

| Parameter | Value |
|-----------|-------|
| Operating temperature | 0°C to 70°C (Tc / case temperature) |
| Non-operating temperature | -40°C to 85°C |
| Temperature gradient | 30°C/h maximum |
| Operating humidity | 8%–90% RH (no condensation) |
| Non-operating humidity | 8%–95% RH (no condensation) |
| Operating shock | 1500G, 0.5ms half-sine wave |
| Non-operating shock | 1500G, 0.5ms half-sine wave |
| Operating vibration | 20G peak, 10–2,000Hz (20 min/axis × 3 axes) |
| Non-operating vibration | 20G peak, 10–2,000Hz (12 cycles/axis × 3 axes × 20 min) |

### Reliability

| Parameter | Value |
|-----------|-------|
| MTTF | 1,000,000 hours |
| Product life | ~5 years or 20,000 power-on hours (whichever is earlier) |

### Compliance

UL 60950-1 (USA), CSA-C22.2 No.60950-1 (Canada), EN 60950-1 (Germany/TÜV),  
KCC KN22/KN24 (Korea), FCC Part 15 Subpart B Class B (USA),  
BSMI CNS13438 (Taiwan), CE EN 55022/55024 (Europe), C-Tick AS/NZS CISPR 22 Class B (AU/NZ)

---

## 2.5-inch Standard SATA Connector — Pin Assignment

*Source: Toshiba HG3 Brochure Rev.1.1, Table 8-1*

The 2.5-inch model uses a **standard 22-pin SATA combo connector** (7-pin signal + 15-pin power).

### Signal Segment (S1–S7)

| Pin | Signal | Function |
|-----|--------|----------|
| S1 | GND | Ground — 2nd mate |
| S2 | A+ | Differential Signal Pair A — Device Rx (host → drive) |
| S3 | A– | Differential Signal Pair A — Device Rx (host → drive) |
| S4 | GND | Ground |
| S5 | B– | Differential Signal Pair B — Device Tx (drive → host) |
| S6 | B+ | Differential Signal Pair B — Device Tx (drive → host) |
| S7 | GND | Ground — 2nd mate |

### Power Segment (P1–P15)

| Pin | Signal | Function |
|-----|--------|----------|
| P1 | V33 | 3.3V power — **Unused** |
| P2 | V33 | 3.3V power — **Unused** |
| P3 | V33 | 3.3V power pre-charge, 2nd mate — **Unused** |
| P4 | GND | Ground |
| P5 | GND | Ground |
| P6 | GND | Ground |
| P7 | V5 | 5V power pre-charge, 2nd mate |
| P8 | V5 | **5V power** (primary supply) |
| P9 | V5 | **5V power** (primary supply) |
| P10 | GND | Ground |
| P11 | DAS/DSS | Reserved at ATA-8 — **Not used** |
| P12 | GND | Ground — 1st mate |
| P13 | V12 | 12V power pre-charge, 2nd mate — **Unused** |
| P14 | V12 | 12V power — **Unused** |
| P15 | V12 | 12V power — **Unused** |

> **Key finding:** The drive operates on **5V only**. 3.3V and 12V rails are unused. P7 is pre-charge (2nd mate); P8 and P9 carry the main 5V supply.

Additionally, three test pads are exposed on the PCB edge (not part of the SATA connector):

| Label | Function |
|-------|----------|
| N.C. | Not connected |
| TX | Test use — not connected |
| UX | Test use — not connected |

---

## Micro SATA Connector — Pin Assignment (for reference)

*Source: Toshiba HG3 Brochure Rev.1.1, Table 8-2 — applies to 1.8-inch and module variants*

### Signal Segment (S1–S7)

| Pin | Signal | Function |
|-----|--------|----------|
| S1 | GND | Ground — 2nd mate |
| S2 | A+ | Device Rx+ |
| S3 | A– | Device Rx– |
| S4 | GND | Ground |
| S5 | B– | Device Tx– |
| S6 | B+ | Device Tx+ |
| S7 | GND | Ground — 2nd mate |

### Power Segment (P1–P9)

| Pin | Signal | Function |
|-----|--------|----------|
| P1 | V33 | **3.3V power** (primary supply for 1.8-inch/module) |
| P2 | V33 | 3.3V power pre-charge, 2nd mate |
| P3 | GND | Ground |
| P4 | GND | Ground |
| P5 | V5 | 5V power pre-charge, 2nd mate — **Unused** |
| P6 | V5 | 5V power — **Unused** |
| P7 | R | Reserved |
| P8 | V | Vendor specific |
| P9 | V | Vendor specific |

---

## Supported ATA Command Set

*Source: Toshiba HG3 Brochure Rev.1.1, Table 9-1*

| Op-Code | Sub-code | Command |
|---------|----------|---------|
| 00h | — | NOP |
| 06h | — | DATA SET MANAGEMENT (TRIM) |
| 10h | — | RECALIBRATE |
| 20h | — | READ SECTOR(S) |
| 21h | — | READ SECTOR(S) without retry |
| 24h | — | READ SECTOR(S) EXT |
| 25h | — | READ DMA EXT |
| 27h | — | READ NATIVE MAX ADDRESS EXT |
| 29h | — | READ MULTIPLE EXT |
| 2Fh | — | READ LOG EXT |
| 30h | — | WRITE SECTOR(S) |
| 31h | — | WRITE SECTOR(S) without retry |
| 34h | — | WRITE SECTOR(S) EXT |
| 35h | — | WRITE DMA EXT |
| 37h | — | SET MAX ADDRESS EXT |
| 39h | — | WRITE MULTIPLE EXT |
| 3Dh | — | WRITE DMA FUA EXT |
| 3Fh | — | WRITE LOG EXT |
| 40h | — | READ VERIFY SECTOR(S) |
| 41h | — | READ VERIFY SECTOR(S) without retry |
| 42h | — | READ VERIFY SECTOR(S) EXT |
| 45h | — | WRITE UNCORRECTABLE EXT |
| 47h | — | READ LOG DMA EXT |
| 57h | — | WRITE LOG DMA EXT |
| 70h | — | SEEK |
| 90h | — | EXECUTE DEVICE DIAGNOSTIC |
| 91h | — | INITIALIZE DEVICE PARAMETERS |
| 92h | — | DOWNLOAD MICROCODE |
| B0h | D0h | SMART READ DATA |
| B0h | D1h | SMART READ ATTRIBUTE THRESHOLDS |
| B0h | D2h | SMART ENABLE/DISABLE ATTRIBUTE AUTOSAVE |
| B0h | D3h | SMART SAVE ATTRIBUTE VALUES |
| B0h | D4h | SMART EXECUTE OFF-LINE IMMEDIATE |
| B0h | D5h | SMART READ LOG |
| B0h | D6h | SMART WRITE LOG |
| B0h | D8h | SMART ENABLE OPERATIONS |
| B0h | D9h | SMART DISABLE OPERATIONS |
| B0h | DAh | SMART RETURN STATUS |
| B0h | DBh | SMART ENABLE/DISABLE AUTOMATIC OFF-LINE |
| B1h | C0h | DEVICE CONFIGURATION RESTORE |
| B1h | C1h | DEVICE CONFIGURATION FREEZE LOCK |
| B1h | C2h | DEVICE CONFIGURATION IDENTIFY |
| B1h | C3h | DEVICE CONFIGURATION SET |
| C4h | — | READ MULTIPLE |
| C5h | — | WRITE MULTIPLE |
| C6h | — | SET MULTIPLE MODE |
| C8h | — | READ DMA |
| C9h | — | READ DMA without retry |
| CAh | — | WRITE DMA |
| CBh | — | WRITE DMA without retry |
| CEh | — | WRITE MULTIPLE FUA EXT |
| E0h | — | STANDBY IMMEDIATE |
| E1h | — | IDLE IMMEDIATE |
| E2h | — | STANDBY |
| E3h | — | IDLE |
| E4h | — | READ BUFFER |
| E5h | — | CHECK POWER MODE |
| E6h | — | SLEEP |
| E7h | — | FLUSH CACHE |
| E8h | — | WRITE BUFFER |
| EAh | — | FLUSH CACHE EXT |
| ECh | — | IDENTIFY DEVICE |
| EFh | 02h | SET FEATURES — Enable volatile write cache |
| EFh | 03h | SET FEATURES — Set transfer mode |
| EFh | 05h | SET FEATURES — Enable APM feature set |
| EFh | 10h | SET FEATURES — Enable Serial ATA feature set |
| EFh | 10h/02h | SET FEATURES — Enable DMA Auto-Activate |
| EFh | 10h/03h | SET FEATURES — Enable DIPM transitions |
| EFh | 10h/06h | SET FEATURES — Enable SSP |
| EFh | 55h | SET FEATURES — Disable read look-ahead |
| EFh | 66h | SET FEATURES — Disable reverting to power-on default |
| EFh | 82h | SET FEATURES — Disable volatile write cache |
| EFh | 85h | SET FEATURES — Disable APM feature set |
| EFh | 90h | SET FEATURES — Disable Serial ATA feature set |
| EFh | 90h/02h | SET FEATURES — Disable DMA Auto-Activate |
| EFh | 90h/03h | SET FEATURES — Disable DIPM |
| EFh | 90h/06h | SET FEATURES — Disable SSP |
| EFh | AAh | SET FEATURES — Enable read look-ahead |
| EFh | CCh | SET FEATURES — Enable reverting to power-on default |
| F1h | — | SECURITY SET PASSWORD |
| F2h | — | SECURITY UNLOCK |
| F3h | — | SECURITY ERASE PREPARE |
| F4h | — | SECURITY ERASE UNIT |
| F5h | — | SECURITY FREEZE LOCK |
| F6h | — | SECURITY DISABLE PASSWORD |
| F8h | — | READ NATIVE MAX ADDRESS |
| F9h | — | SET MAX ADDRESS |
| F9h | 01h | SET MAX SET PASSWORD |
| F9h | 02h | SET MAX LOCK |
| F9h | 03h | SET MAX UNLOCK |
| F9h | 04h | SET MAX FREEZE LOCK |

---

## PS-78320-002 Connector Specification (3M / Molex)

*OCR recovered from scanned 7-page document.*

**Product:** 1.8-inch HDD/SSD Serial ATA Receptacle, Right-Angle SMT, 3.80mm height  
**Part numbers:** 78320-0001, 78320-1001 (standard) / 78320-0002, 78320-1002 (variant)  
**Document number:** PS-78320-002  
**Revision:** EC No. S2010-0402, dated 2009/11/04  
**Safety approvals:** UL File E29179, CSA 1699307 (LR19980)

This is the **1.8-inch SATA receptacle connector** specification — used on the *SSD board* interface PCB
(as the drive-side SATA combo connector). The spec defines electrical, mechanical, and environmental
performance requirements for the SMT connector that mates with the 1.8-inch SATA plug on an HDD/SSD.

### Electrical Ratings

| Parameter | Value |
|-----------|-------|
| Voltage | 30V max |
| Current | 1.5A DC or AC (RMS) max @ 60Hz |
| Low Level Contact Resistance (initial) | 30mΩ max |
| Low Level Contact Resistance (delta) | 15mΩ max |
| Contact current rating (power segment) | 1.5A per pin min |
| Insulation resistance | 1000MΩ min |
| Dielectric withstanding voltage | 500 VAC, 1 min — no breakdown |

### Operating Conditions

| Parameter | Value |
|-----------|-------|
| Operating temperature | -40°C to +105°C |
| Non-operating temperature | -40°C to +105°C |
| Humidity | 20%–80% |
| Pressure | 650–800 mm Hg |

### Mechanical Ratings

| Parameter | Value |
|-----------|-------|
| Insertion force | 20N max |
| Removal force | 2.5N min (initial & after 500 cycles) |
| Durability | 500 mating cycles |
| Terminal retention force | 4.45N min |
| Physical shock | 30g half-sine, 11ms, 18 shocks (EIA 364-27 Condition H) |
| Random vibration | 5.35g RMS, 30 min per plane (EIA 364-28 Condition V Test A) |

### Reflow Soldering Profile

| Parameter | Value |
|-----------|-------|
| Average ramp rate | 3°C/sec max |
| Preheat temperature | 150°C min – 200°C max |
| Preheat time | 60–180 sec |
| Ramp to peak | 3°C/sec max |
| Time above liquidus (217°C) | 60–150 sec |
| Peak temperature | 260 +0/−5°C |
| Time within 5°C of peak | 20–40 sec |
| Cool-down ramp | 6°C/sec max |
| Total time 25°C to peak | 8 min max |

---

## Key Notes for Replacement / Custom Drive Design

1. **Power supply:** The 2.5-inch THNSNC256GBSJ runs on **5V only** from P8/P9. 3.3V and 12V
   rails are completely unused. Any replacement must supply clean 5.0V ±5% with ≤100mV ripple.

2. **SATA generation:** The drive is SATA II (3 Gbit/s). SATA III (6 Gbit/s) replacements are
   backward compatible and will negotiate to 3 Gbit/s automatically.

3. **Capacity:** The drive exposes exactly **500,118,192 LBA sectors** (500GB-style sector count).
   If the RED ONE firmware validates capacity, a replacement must match this or be larger
   (native max address can be set via `SET MAX ADDRESS`).

4. **IDENTIFY DEVICE (ECh):** The camera firmware likely calls this on startup. The response
   contains the model number string, serial number, firmware revision, and capabilities word.
   Whether the camera validates the model string is unknown — see Phase 4 (firmware analysis).

5. **TRIM support:** The drive supports `DATA SET MANAGEMENT` (06h / TRIM). This is a nice-to-have
   for replacements but not required for camera operation.

6. **Security commands:** The full ATA Security feature set is implemented. The camera may use
   `SECURITY FREEZE LOCK` (F5h) as a standard protective measure at startup.
