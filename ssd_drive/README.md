# REDMAG 256GB SSD — Reverse Engineering Summary

*Part of the RED ONE MX reverse engineering project. See root [README.md](../README.md).*

---

## Overview

The **REDMAG 256GB SSD** is the internal solid-state recording media used in the RED ONE MX
digital cinema camera. It is a proprietary module that uses a standard 2.5-inch SATA SSD
inside a custom housing, connected to the camera via a 26-pin iVDR connector.

The drive is end-of-sale and increasingly difficult to source. This document summarises all
research to date on the drive's hardware, interface, firmware interaction, and replacement options.

---

## Quick Reference

| Property | Value |
|----------|-------|
| Drive make/model | Toshiba HG3 Series — **THNSNC256GBSJ** |
| Form factor | 2.5-inch, 9.5mm height |
| Interface | SATA II (ACS-2, SATA revision 2.6), 3 Gbit/s |
| Controller | Toshiba TC58 "Type C" (proprietary) |
| NAND | Toshiba 32nm MLC (TH58TEG series, Toggle Mode) |
| Capacity | 256 GB (500,118,192 LBA sectors × 512 B) |
| Power | 5V ±5% only — 3.3V and 12V rails unused |
| Sequential read | 220 MB/s average (128 KB blocks) |
| Sequential write | 180 MB/s average (128 KB blocks) |
| Camera connector | Amphenol ICC 10033998-002LF (iVDR 26-pin, EOL) |
| Drive connector | 3M 5622 series SATA combo (22-pin standard) |
| Camera SATA host | Silicon Image SiI3512 (on AUDIO_PCI board) |
| Firmware validates model? | **Yes** — drive model string checked at boot |
| Known approved drives (Build 13) | Adtron A25FB-32GC21N, WDC WD800BEVS-22LAT0, HTS721010G9SA00 |

---

## Document Index

| Document | Contents |
|----------|---------|
| [`datasheets/README.md`](datasheets/README.md) | Full datasheet analysis: specs, SATA pinout, ATA command table, PS-78320-002 OCR |
| [`components.md`](components.md) | Internal component identification: TC58 controller, TH58TEG NAND |
| [`interface.md`](interface.md) | iVDR 26-pin ↔ SATA signal mapping, connector specs, PCB topology |
| [`firmware-analysis.md`](firmware-analysis.md) | Camera firmware SATA analysis: ATA commands, drive model validation, device paths |
| [`replacement-options.md`](replacement-options.md) | Replacement strategies: drop-in, model string spoofing, PCB adapter, firmware patch |

---

## Hardware

### Drive: Toshiba THNSNC256GBSJ

The REDMAG 256GB SSD is a rebadged Toshiba HG3 Series drive in a custom RED housing.
The housing adds the iVDR connector interface while the internal drive is a standard 2.5-inch SATA SSD.

The HG3 line was Toshiba's consumer/client SSD family from 2011, using their first-generation
32nm MLC NAND flash and a proprietary TC58-family embedded controller. The product line
reached end-of-sale and is no longer manufactured.

### Interface Board (ssd_board/)

The SSD board is a **passive adapter PCB** that routes signals between:
- **Camera side:** 26-pin iVDR connector (Amphenol 10033998-002LF)
- **Drive side:** Standard 22-pin SATA combo connector (3M 5622 series)

No active components are needed. The iVDR connector carries standard SATA TX/RX differential
pairs and 5V power directly through to the drive. The PRSNT# (presence detect) pin on the
iVDR connector is pulled low by the drive when inserted.

**Key schematic (expected topology):**

```
iVDR Pin 1,2,3   (+5V) ────► SATA P8, P9    (5V power)
iVDR Pin 4,5,6   (GND) ────► SATA P4–P6,P10 (ground)
iVDR Pin 13      (RX+) ────► SATA S2         (A+, Device Rx+)
iVDR Pin 14      (RX−) ────► SATA S3         (A−, Device Rx−)
iVDR Pin 16      (TX−) ────► SATA S5         (B−, Device Tx−)
iVDR Pin 17      (TX+) ────► SATA S6         (B+, Device Tx+)
iVDR Pin 20  (PRSNT#)  ────► Camera firmware (presence detect)
```

Physical continuity testing is needed to confirm and complete this map.

---

## Camera Firmware Interaction

### What happens at boot

1. The camera's VxWorks firmware initialises the SiI3512 SATA host controller
2. `ataDevIdentify()` issues **IDENTIFY DEVICE** (ATA command ECh) to the drive
3. The firmware reads the **model number string** (words 27–46, 40 ASCII bytes)
4. `DigMagMgrModule::IsCompatible()` compares the model string against a hardcoded table
5. If the drive is recognised: `MEDIA.DIGMAG.TYPE = "DigMag"` → recording enabled
6. If unrecognised: `MEDIA.DIGMAG.TYPE = "INCOMPATIBLE"` → camera refuses to record

### Known approved drives (Build 13 firmware, 2008)

| Model string | Type label | Drive |
|---|---|---|
| `Adtron A25FB-32GC21N` | RedFlash | Adtron 32GB SLC SATA SSD |
| `WDC WD800BEVS-22LAT0` | RedSata (WDC) | Western Digital 80GB HDD |
| `HTS721010G9SA00` | RedSata (Hitachi) | Hitachi 100GB HDD |

> The Toshiba THNSNC256GBSJ is not in Build 13 (released 2008; Toshiba HG3 was 2011).
> It was added in a later firmware build. **Full approved list requires Build 32 analysis.**

---

## Replacement Strategy

### Recommended path

```
Step 1 (Days):   Extract Build 32 firmware → get complete approved drive list
Step 2 (Weeks):  Reprogram model string on modern Phison/SMI SATA SSD (Option B)
                 + Design passive iVDR adapter PCB (Option C)
Step 3 (Months): Patch IsCompatible() in firmware for universal drive support (Option D)
```

### Summary table

| Option | Description | Cost | Complexity |
|--------|-------------|------|-----------|
| **A1** | Source original Toshiba HG3 (used/refurbished) | $20–$60 | None |
| **A2** | Use other drive from Build 32 approved list | $15–$50 | Low |
| **B** | Reprogram model string on modern SSD (Phison/SMI) | $15–$50 | Medium |
| **C** | Passive iVDR→SATA adapter PCB (any drive mechanically) | $15–$40 PCB | Medium |
| **D** | Patch `IsCompatible()` in firmware | Minimal | High |
| **E** | FPGA-based SATA drive emulator | $100+ | Very high |

See [`replacement-options.md`](replacement-options.md) for full details.

---

## Files in This Directory

```
ssd_drive/
├── README.md                    ← This file — master summary
├── components.md                ← Internal component identification
├── interface.md                 ← iVDR ↔ SATA signal mapping
├── firmware-analysis.md         ← Camera firmware SATA/ATA analysis
├── replacement-options.md       ← Replacement drive strategies
├── datasheets/
│   ├── README.md                ← Datasheet analysis and extracted data
│   ├── cSSD-HG3.pdf             ← Toshiba HG3 brief spec
│   ├── document.pdf             ← Toshiba HG3 Brochure Rev.1.1 (full)
│   └── Microsoft Word - Document.doc - PS-78320-002.pdf
│                                ← 3M 1.8-inch SATA receptacle spec (scanned)
├── r1-ssd.pdf                   ← Project drawing (image-only, minimal content)
├── ssd.png                      ← Photo of the REDMAG SSD drive
├── drive.FCStd / drive.FCStd1   ← FreeCAD models of the drive housing
├── drive_mezz_board.FCStd       ← FreeCAD model — mezzanine board
├── drive_sleeve.FCStd           ← FreeCAD model — drive sleeve
├── side_ssd.FCStd               ← FreeCAD model — side SSD
├── side_ssd_cover.FCStd         ← FreeCAD model — side cover
├── models/
│   ├── bottom_shell.stl         ← 3D printable bottom shell
│   └── top_shell.stl            ← 3D printable top shell
└── prints/
    └── drive-bottom_shell001_test1.stl  ← Test print
```

---

## Outstanding Work

| Priority | Task | Phase |
|----------|------|-------|
| 🔴 High | Extract and analyse Build 32 firmware — get complete drive approved list | 4 extension |
| 🔴 High | Locate `_ZN15DigMagMgrModule12IsCompatibleEv` in binary, disassemble | 4 extension |
| 🟡 Medium | Physical SSD teardown — photograph die markings to confirm TC58 part# | 2 |
| 🟡 Medium | Complete `ssd_board/reverse.svg` signal labelling via continuity testing | 3 |
| 🟡 Medium | Test approved drives (WDC WD800, Hitachi HTS721) to verify firmware accepts them | 5 |
| 🟡 Medium | Prototype iVDR→SATA adapter PCB (Option C in replacement-options.md) | 5 |
| 🟢 Low | FPGA SATA drive emulator research (LiteSATA evaluation) | 5 |
| 🟢 Low | Attempt QEMU boot of VxWorks to interactive shell for live firmware analysis | 4 extension |
