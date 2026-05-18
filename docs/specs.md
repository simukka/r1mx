---
layout: page
title: Technical Specifications
subtitle: RED ONE (Mysterium™) and RED ONE MX (Mysterium-X™)
permalink: /specs/
---

This page documents the technical specifications for the RED ONE and RED ONE MX cameras
as published by RED Digital Cinema. The **RED ONE MX** refers to any RED ONE body
equipped with the Mysterium-X™ sensor, either factory-configured or field-upgraded.

<div class="gallery">
  <figure class="figure">
    <img src="{{ '/assets/images/redone-specs-front.png' | relative_url }}" alt="RED ONE MX front view" />
    <figcaption>Front</figcaption>
  </figure>
  <figure class="figure">
    <img src="{{ '/assets/images/redone-specs-back.png' | relative_url }}" alt="RED ONE MX rear view" />
    <figcaption>Rear</figcaption>
  </figure>
  <figure class="figure">
    <img src="{{ '/assets/images/redone-side.png' | relative_url }}" alt="RED ONE MX side view" />
    <figcaption>Side</figcaption>
  </figure>
  <figure class="figure">
    <img src="{{ '/assets/images/redone-detail.png' | relative_url }}" alt="RED ONE MX detail" />
    <figcaption>Detail</figcaption>
  </figure>
</div>

<div class="callout callout--info">
  Sources: Archived red.com tech specs pages (May 2010 and January 2011 snapshots via
  the Wayback Machine). Original pages:
  <code>web.archive.org/web/20100516/http://www.red.com/cameras/tech_specs</code> and
  <code>web.archive.org/web/20110102/http://www.red.com/products/red-one</code>
</div>

## Sensor Comparison

| Specification | RED ONE (Mysterium™) | RED ONE MX (Mysterium-X™) |
|---|---|---|
| Sensor name | Mysterium™ | Mysterium-X™ |
| Megapixels | 12 MP | **14 MP** |
| Full pixel array | 4900 (h) × 2580 (v) | **5120 (h) × 2700 (v)** |
| Active pixel array | 4520 (h) x 2540 (v) | N/A |
| Max image area | N/A | 4480 (h) x 2304 (v) |
| Physical sensor size | 24.4mm × 13.7mm | 24.2mm (h) × 12.5mm (v) × 27.3mm (d) diagonal |
| Lens coverage | Super 35mm | Super 35mm |
| Dynamic range | > 66 dB | **13+ stops** |
| S/N ratio | 66 dB | 66 dB |
| ISO range | 320–1600 | **320–6400** (with MX sensor) |
| Firmware required | Any release build | **Build 30 minimum** |

### Depth of Field Equivalence

| Mode | DoF equivalent |
|---|---|
| 4K / 4.5K (full sensor) | 35mm Cine lens (Super 35mm) |
| 2K windowed | S16mm equivalent |

---

## Resolution Modes

All resolutions available on both Mysterium and Mysterium-X sensors (where firmware supports them).
4.5K requires Build 20 or later.

| Resolution | Dimensions | Aspect |
|---|---|---|
| **4.5K** | 4480 × 1920 | 2.4:1 (introduced Build 20) |
| 4K 16:9 | 4096 × 2304 | 16:9 |
| 4K 2:1 | 4096 × 2048 | 2:1 |
| 4K HD | 3840 × 2160 | 16:9 |
| 4K Anamorphic 2:1 | 2764 × 2304 | Anam. 2:1 |
| 3K 16:9 | 3072 × 1728 | 16:9 |
| 3K 2:1 | 3072 × 1536 | 2:1 |
| 3K Anamorphic 2:1 | 2074 × 1728 | Anam. 2:1 |
| 2K 16:9 | 2048 × 1152 | 16:9 |
| 2K 2:1 | 2048 × 1024 | 2:1 |
| 2K Anamorphic | 1382 × 1152 | Anam. |

---

## Frame Rates

| Resolution | Frame rates |
|---|---|
| 4.5K | 23.98, 24, 25, 29.97 fps |
| 4K (all modes) | 23.98, 24, 25, 29.97 fps |
| 3K (all modes) | + 50, 59.94 fps |
| 2K (all modes) | + 75, 120 fps (Mysterium); 50, 59.94 fps (Mysterium-X) |

> **Note (Mysterium-X):** With the MX sensor, maximum frame rates at 2K are limited
> compared to the original Mysterium sensor. The MX sensor prioritises dynamic range
> and low-light performance over extreme high-speed capability.

---

## REDCODE™ Compression

REDCODE is RED's proprietary 12-bit RAW wavelet compression codec. The camera records
`.R3D` files directly to the storage media.

| Quality Level | Data rate | Available resolutions |
|---|---|---|
| **REDCODE 28** | ~28 MB/s | All resolutions |
| **REDCODE 36** | ~36 MB/s | All resolutions |
| **REDCODE 42** | ~42 MB/s | 4.5K, 4K, 3K, 2K (Build 30+) |

- All levels: **12-bit RAW** with full sensor data retained
- Color science: REDcolor (Build 20+), REDcolor2 with FLUT (Build 30+)
- No lossy downsampling; full debayer in post

---

## Recording Formats & I/O

### Digital Media (in-camera)

| Interface | Media type | Notes |
|---|---|---|
| CF Module (in-body) | CompactFlash card | Included with camera body; also used for firmware upgrades |
| RED SSD™ Module | REDMAG SSD (128GB or 256GB) | Via iVDR 26-pin connector |
| RED DRIVE™ | External RAID-0 (320GB) | Via Drive Connector LEMO; mounts on RED-RAIL |
| RED-RAM™ | External RAID-0 SSD (128GB) | Same form factor as RED DRIVE |

### Monitor Outputs

| Output | Signal | Notes |
|---|---|---|
| HD-SDI | 1280×720p 4:2:2, 48kHz 24-bit audio | Frame guides, Look Around, HANC metadata |
| HDMI | 1280×720p 4:2:2 | Same signal as HD-SDI |
| 3G SDI | 1080p via GS2978 driver IC | Requires appropriate cable |

### Control & Connectivity

| Port | Type | Use |
|---|---|---|
| USB-2 | USB-A | Remote control; file transfer to computer |
| FireWire 400/800 | IEEE 1394 | Media offload (RED DRIVE) |
| eSATA | External SATA | Media offload (RED DRIVE) |
| GPI/O | GPIO trigger | Remote start/stop; trigger COLOR via Build 30 |
| LEMO 5-pin | LTC timecode | Time-of-day timecode output |
| XLR (×2) | Analog audio in | Via XLR module (4-ch, 24-bit, 48kHz) |
| mini-XLR | Audio in/out | Included cable: mini-XLR to XLR adaptor |

---

## Audio

| Specification | Value |
|---|---|
| Channels | 4 channel (standard) |
| Bit depth | 24-bit |
| Sample rate | 48kHz |
| Encoding | Uncompressed PCM embedded in R3D |
| Preamp | PGA2500I digitally-controlled microphone preamp |
| DAC | DAC23 stereo 8–96kHz with headphone amp |
| Input | XLR (balanced) via XLR module |

---

## Physical

| Specification | Value |
|---|---|
| Body weight | ~10 lbs (4.5 kg) without lens, battery, or viewfinder |
| Construction | Precision-machined aluminum alloy |
| Dimensions | Approx. 18 cm × 19 cm × 19 cm (body only) |
| Operating temperature | 0°C to +40°C (32°F to 104°F) |
| Storage temperature | −20°C to +50°C (−4°F to 122°F) |
| Lens mount (standard) | PL Mount (ARRI-compatible) |
| Lens mount (optional) | Nikon F, Canon EF, B4 to PL adaptor |

---

## Delivery Formats (Post Production)

Output via **REDCINE-X** or **ROCKETCINE-X** software:

| Format | Notes |
|---|---|
| DPX | Log, Linear, or REC709 colorspace; 4K or 2K |
| OpenEXR | 4K or 2K |
| TIFF | 4K or 2K |
| ProRes HQ 1080p | Via Apple FCP pipeline |
| DNxHD QuickTime | Via Avid pipeline |
| H.264/MP4 | Via REDCINE-X |
| Avid AAF/MXF | EDL-based conforming |

### Post Production Software Compatibility (as of 2011)

Final Cut Pro · Avid Media Composer · Avid DS · Adobe Premiere Pro ·
Adobe After Effects · Sony Vegas · Assimilate Scratch · Filmlight Baselight ·
Quantel Pablo · DaVinci Resolve · The Foundry Nuke · DVS Clipster ·
REDCINE-X · ROCKETCINE-X
