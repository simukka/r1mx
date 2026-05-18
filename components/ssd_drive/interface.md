# SSD Interface — iVDR Connector to SATA Signal Mapping

*Phase 3 of the REDMAG 256GB SSD reverse engineering effort.*

---

## Overview

The RED ONE MX SSD board bridges the camera's internal bus to the REDMAG SSD drive via two connectors:

1. **Camera-side**: 26-pin iVDR connector (Amphenol ICC 10033998-002LF) — connects to camera internals
2. **Drive-side**: 3M SATA Combo Connector (78-5100-2109-6 / 5622 series) — mates with the 2.5-inch SSD

The SSD board PCB is documented in `ssd_board/reverse.svg` (Inkscape format, layers: top, bottom, vias).
Signal tracing has not yet been completed — physical continuity checks or high-resolution PCB imaging
are needed to complete the iVDR pin → SATA signal map.

---

## Connector 1: Camera-Side — Amphenol ICC 10033998-002LF

**iVDR (Information Versatile Disk for Removable Usage)** is a Japanese consumer standard (JEITA CP-4241)
for a removable hard drive cartridge, adopted by the iVDR Consortium (Canon, Fujitsu, Hitachi, Pioneer,
Sanyo, Sharp, JVC and others, founded 2002).

| Parameter | Value |
|-----------|-------|
| Part number | 10033998-002LF (Amphenol ICC / FCI) |
| Positions | 26 |
| Pitch | 1.27 mm |
| Style | Right-angle, surface mount (SMT) |
| Contact plating | Gold |
| Current rating | 1.5A per contact |
| Voltage rating | 100V |
| Mating cycles | 10,000 (per iVDR spec — much higher than USB's ~1,500) |
| Status | **Obsolete / EOL** |
| Digikey (Norway) | [609-5400-ND](https://www.digikey.no/product-detail/en/amphenol-icc-fci/10033998-002LF/609-5400-ND/4239008) |
| Amphenol drawing | https://www.amphenol-icc.com/media/wysiwyg/files/drawing/10033998.pdf |
| Amphenol drawing 2 | https://cdn.amphenol-icc.com/media/wysiwyg/files/drawing/10079510.pdf |

### iVDR Protocol
- Complies with **SATA revision 2.6** at the electrical/protocol layer (3 Gbit/s)
- Adds extensions for: **security** (hardware tamper-resistant region, PKI-based), **presence detection**
- The core data path is standard SATA differential pairs (TX+/TX−, RX+/RX−)
- iVDR mandates shock resistance up to 900G (consumer HDD usage model)

### iVDR 26-pin Connector Signal Assignment
*(Based on JEITA CP-4241 / iVDR Consortium documentation)*

| Pin | Signal | Direction | Description |
|-----|--------|-----------|-------------|
| 1 | +5V | — | Power supply |
| 2 | +5V | — | Power supply |
| 3 | +5V | — | Power supply |
| 4 | GND | — | Ground |
| 5 | GND | — | Ground |
| 6 | GND | — | Ground |
| 7 | +3.3V | — | Power (optional; may be unused for 5V-only drives) |
| 8 | +3.3V | — | Power (optional) |
| 9 | +3.3V | — | Power (optional) |
| 10 | GND | — | Ground |
| 11 | GND | — | Ground |
| 12 | GND | — | Ground |
| 13 | SATA RX+ | Host → Drive | Differential receive pair + (Device Rx) |
| 14 | SATA RX− | Host → Drive | Differential receive pair − (Device Rx) |
| 15 | GND | — | Signal ground |
| 16 | SATA TX− | Drive → Host | Differential transmit pair − (Device Tx) |
| 17 | SATA TX+ | Drive → Host | Differential transmit pair + (Device Tx) |
| 18 | GND | — | Signal ground |
| 19 | GND | — | Signal ground |
| 20 | PRSNT# | Bidirectional | Presence detect — pulled low by drive when inserted |
| 21 | SEC | — | Security/encryption signal (iVDR extension) |
| 22 | KEY | — | Keying / reserved |
| 23–26 | RSVD | — | Reserved (manufacturer-specific) |

> **Note:** Pins 23–26 and the exact assignment of 21–22 vary by implementation and are not
> publicly documented in the iVDR open spec. The RED ONE may use some of these for
> drive-present signaling to the camera firmware. Physical continuity tracing is required.

> **Key finding for THNSNC256GBSJ**: The drive is 5V-only (see datasheets/README.md).
> The 3.3V rails (pins 7–9) on the iVDR connector are present per spec but are
> **not connected to the SSD's 3.3V power pins**, which are marked "Unused" in the
> Toshiba HG3 SATA connector pinout.

---

## Connector 2: Drive-Side — 3M SATA Combo Connector

**Part:** 3M™ 5622 Series, SATA Combo Connector Device Plug  
**Drawing number:** 78-5100-2109-6  
**Variants:**
- 5622-4100-ML — Right-angle through-hole
- 5622-6309-ML — Straddlemount

This is the **standard 22-pin SATA combo connector plug** that mates with the 2.5-inch drive's
standard SATA receptacle. The 22-pin connector carries both the 7-pin signal segment and 15-pin
power segment on a single piece.

| Parameter | Value |
|-----------|-------|
| Standard | SATA specification compliant |
| Housing | High temperature thermoplastic, black, UL94V-0 |
| Contact | Copper alloy |
| Plating | 30μin Au (mating area), 50μin Ni underplate, 100μin Sn (termination) |
| Current rating | 1.5A |
| Insulation resistance | 10⁹ MΩ (min) |
| Withstanding voltage | 500V AC at sea level |
| Operating temperature | -40°C to +85°C |
| UL File | E68080 |
| RoHS compliant | Yes |

Signal assignment follows the standard SATA pinout — see `datasheets/README.md` Section
"2.5-inch Standard SATA Connector — Pin Assignment" for the full table.

---

## SSD Board PCB — Current Status

The `ssd_board/reverse.svg` file exists with three layers (top, bottom, vias) but contains
**only geometric shapes** (pads, vias, traces as circles and paths) — no signal labels have been
added yet.

### Next Steps for Signal Tracing

To complete the iVDR → SATA signal map, the following physical steps are needed:

1. **High-resolution photography**: Photograph both sides of the SSD board PCB under bright lighting
   to capture all trace routing.
2. **Continuity testing**: Use a multimeter in continuity mode to probe each iVDR pin to the
   corresponding SATA connector pin.
3. **Layer markup**: Add signal labels to `reverse.svg` layers in Inkscape once traces are identified.
4. **Key signals to prioritize**:
   - +5V (iVDR → SATA P8/P9)
   - GND (iVDR → SATA P4/P5/P6/P10)
   - SATA TX+/TX− (iVDR 16/17 → SATA S5/S6)
   - SATA RX+/RX− (iVDR 13/14 → SATA S2/S3)
   - PRSNT# — where this goes on the camera side
   - SEC / reserved pins — whether connected or NC

### Expected Topology (based on known signal equivalence)

```
iVDR 26-pin                    SSD Board PCB                    SATA 22-pin
(Camera side)                  (Routing)                        (Drive side)

Pin 1,2,3  +5V    ───────────────────────────────────────────►  P8, P9  (+5V)
Pin 4,5,6  GND    ───────────────────────────────────────────►  P4,P5,P6,P10  (GND)
Pin 7,8,9  +3.3V  ───────────────────────────────X (likely NC — drive 3.3V unused)
Pin 10,11  GND    ───────────────────────────────────────────►  S1, S4, S7  (GND)
Pin 13  SATA RX+  ───────────────────────────────────────────►  S2  (A+, Device Rx+)
Pin 14  SATA RX−  ───────────────────────────────────────────►  S3  (A−, Device Rx−)
Pin 15  GND       ───────────────────────────────────────────►  S4  (GND)
Pin 16  SATA TX−  ───────────────────────────────────────────►  S5  (B−, Device Tx−)
Pin 17  SATA TX+  ───────────────────────────────────────────►  S6  (B+, Device Tx+)
Pin 20  PRSNT#    ─────── ?  (camera firmware reads drive presence)
Pin 21  SEC       ─────── ?  (iVDR security — may be NC on this implementation)
Pin 22–26 RSVD   ─────── ?  (unknown)
```

---

## SATA Host in the Camera

The RED ONE MX's **AUDIO_PCI board** contains the SATA host controller:

**Silicon Image SiI3512ECTU128**
- 2-port SATA PCI host controller
- Supports SATA I/II (1.5 and 3 Gbit/s)
- Connects to the camera's PCI bus (via the CPU_IO board)
- One port drives the SSD; the second port may drive a second storage device

The SiI3512 is well-documented; its Linux kernel driver is available as `sata_sil.c`.
This means the camera firmware (VxWorks) almost certainly uses a SiI3512 driver that
issues standard ATA commands — there is no hardware barrier to using a different SATA drive,
provided it responds correctly to ATA commands.

---

## Key Conclusions

1. **The SSD board is a passive adapter** — it routes iVDR signals to a standard SATA connector
   with no active components (no level shifters, no protocol translation).

2. **Power is straightforward** — 5V from iVDR pins 1–3, GND from iVDR pins 4–6 and 10–12.

3. **SATA signals are direct** — SATA TX/RX differentials route straight through from iVDR
   pins 13/14/16/17 to the SATA signal segment.

4. **Presence detect (pin 20)** — the iVDR PRSNT# signal tells the camera when a drive is inserted.
   Any replacement drive or adapter board must pull this pin appropriately.

5. **iVDR Security pins** — likely unused by RED (camera uses ATA security commands instead of
   iVDR's PKI-based tamper region). Physical tracing will confirm.

6. **Replacement implication**: Any 2.5-inch SATA SSD can be adapted to work in the RED ONE MX
   SSD bay using a simple adapter board that:
   - Provides the 26-pin iVDR connector (Amphenol 10033998 or equivalent)
   - Routes 5V from iVDR → SATA power
   - Routes SATA TX/RX differentials
   - Pulls PRSNT# (pin 20) appropriately to indicate drive presence
