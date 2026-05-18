---
layout: page
title: Hardware Reference
subtitle: PCB boards, key ICs, and interconnects from the r1mx reverse engineering project
permalink: /hardware/
---

The RED ONE MX houses four primary PCB boards, one sensor board, and several supporting boards,
all precision-machined into an aluminum alloy body. This page summarizes the known hardware
architecture based on the ongoing [r1mx reverse engineering project](https://github.com/simukka/r1mx).

<figure class="figure">
  <img src="{{ '/assets/images/red-one-overview.png' | relative_url }}"
       alt="RED ONE MX camera overview"
       width="334" height="515" />
  <figcaption>RED ONE MX body overview</figcaption>
</figure>

<div class="callout callout--warn">
  <strong>Work in progress:</strong> The r1mx project is actively reverse engineering each board.
  Information here reflects current findings and will be updated as research progresses.
  See the <a href="https://github.com/simukka/r1mx">GitHub repository</a> for the latest schematics,
  component lists, and board images.
</div>

---

## Board Overview

<div class="board-grid">
  <div class="board-card">
    <div class="board-card-title">AUDIO_PCI Board</div>
    <ul>
      <li><strong>ISP1562</strong> - USB PCI host controller</li>
      <li><strong>NET2280REV1A-LF</strong> - USB-to-SPI/PCI bridge (USB 2.0)</li>
      <li><strong>SiI3512ECTU128</strong> - 2-port SATA PCI host controller</li>
      <li><strong>PCA9698DGG</strong> - 40-bit I2C I/O expander</li>
      <li><strong>TMDS141</strong> - HDMI re-driver</li>
      <li><strong>DAC23</strong> - Stereo audio DAC, 8-96kHz + headphone amp</li>
      <li><strong>PGA2500I</strong> - Digitally controlled mic preamp</li>
      <li><strong>GS2978</strong> - 3G SDI cable driver</li>
    </ul>
  </div>

  <div class="board-card">
    <div class="board-card-title">CPU_IO Board</div>
    <ul>
      <li>Central processing and I/O routing board</li>
      <li>Connects to AUDIO_PCI via 180-position high-speed mezzanine connector</li>
      <li>Connects to SENSOR board via 240-position high-speed mezzanine connector</li>
      <li>3x flat flex connectors to Monitor, EVF, and display outputs</li>
      <li>Houses the main SoC/CPU running VxWorks 6.x</li>
    </ul>
  </div>

  <div class="board-card">
    <div class="board-card-title">SENSOR Board</div>
    <ul>
      <li>Houses the Mysterium-X 14MP sensor</li>
      <li>Connects to Xilinx Virtex-4 FPGA for sensor data pipeline</li>
      <li><strong>XC4VLX</strong> family FPGA - handles encoding and data routing</li>
      <li>Connects to CPU_IO via 240-position mezzanine</li>
    </ul>
  </div>

  <div class="board-card">
    <div class="board-card-title">UI Board</div>
    <ul>
      <li><strong>LTBPY</strong> - Hot-swappable 2-wire bus buffer</li>
      <li><strong>PCA9698DGG</strong> - 40-bit I2C I/O expander</li>
      <li><strong>AD5241</strong> - 256-position digital potentiometer</li>
      <li><strong>CoolRunner-II XC2C256</strong> - CPLD for UI logic</li>
      <li>Provides physical joystick and button interface for camera operators</li>
    </ul>
  </div>

  <div class="board-card">
    <div class="board-card-title">POWER Board</div>
    <ul>
      <li>Manages power distribution to all camera systems</li>
      <li>Interfaces with RED BRICK V-Mount battery</li>
      <li>Supports AC power adaptor input</li>
      <li>Research ongoing - see repository for current findings</li>
    </ul>
  </div>

  <div class="board-card">
    <div class="board-card-title">SSD Board</div>
    <ul>
      <li>Houses the iVDR 26-pin connector (Amphenol 10033998-002LF)</li>
      <li>Interfaces REDMAG SSD modules to the SiI3512 SATA controller</li>
      <li>Standard 2.5" SATA SSD internally</li>
      <li>See <a href="#ssd-drive">SSD Drive section</a> below</li>
    </ul>
  </div>
</div>

---

## Board Interconnects

### CPU_IO to AUDIO_PCI (180-position mezzanine)

The CPU_IO and AUDIO_PCI boards are connected by a 180-position high-speed mezzanine connector.
This single connector carries:

- HD-SDI and HDMI video signals
- XLR audio input/output
- USB host bus
- SATA storage bus (CF, SSD, RED DRIVE)

<div class="callout callout--danger">
  <strong>Known failure point:</strong> Broken traces on the CPU_IO board at or near the
  180-position mezzanine connector cause <em>simultaneous</em> loss of multiple subsystems.
  If your camera exhibits all of the following at once, suspect this interconnect:
  <ul style="margin-top:0.5rem">
    <li>No HD-SDI or HDMI video output</li>
    <li>No XLR audio input</li>
    <li>Unable to detect CF card, SSD, or RED DRIVE</li>
  </ul>
  See the <a href="{{ '/guides' | relative_url }}">Repair Guides</a> page for
  diagnostic steps.
</div>

### CPU_IO to SENSOR (240-position mezzanine)

A 240-position high-speed mezzanine connector carries the full-bandwidth sensor data
from the SENSOR board to the CPU_IO board for FPGA processing.

---

## Key ICs Reference

| Part Number | Function | Board | Notes |
|---|---|---|---|
| Xilinx XC4VLX (Virtex-4) | FPGA - sensor data pipeline + REDCODE encoding | SENSOR | Handles all RAW data processing |
| SiI3512ECTU128 | 2-port SATA PCI host controller | AUDIO_PCI | Controls CF and SSD storage |
| ISP1562 | USB PCI host controller | AUDIO_PCI | USB 2.0 host bus |
| NET2280REV1A-LF | USB-to-PCI bridge | AUDIO_PCI | USB 2.0 interface bridge |
| GS2978 | 3G SDI cable driver | AUDIO_PCI | HD-SDI output |
| TMDS141 | HDMI re-driver | AUDIO_PCI | HDMI output signal conditioning |
| DAC23 | Stereo audio DAC | AUDIO_PCI | 8-96kHz, integrated headphone amp |
| PGA2500I | Mic preamp | AUDIO_PCI | Digitally controlled, XLR input |
| PCA9698DGG | 40-bit I2C I/O expander | AUDIO_PCI, UI | Used on multiple boards |
| CoolRunner-II XC2C256 | CPLD | UI | UI button and joystick logic |
| AD5241 | Digital potentiometer | UI | 256-position, I2C controlled |
| LTBPY | 2-wire bus buffer | UI | Hot-swappable I2C buffer |

---

## Firmware Architecture

The RED ONE MX runs **VxWorks 6.x** (Wind River Systems) as its real-time operating system.
The firmware image is encrypted and stored in flash memory.

| Component | Details |
|---|---|
| OS | VxWorks 6.x (RTOS) |
| FPGA bitstream | Xilinx Virtex-4 (XC4VLX family) |
| Encryption | AES-256-CBC with MD5 KDF |
| Decryption key | Public - see firmware/README.md in the repository |
| Build system | Xilinx EDK (Embedded Development Kit) |

The firmware is distributed as encrypted `.zip` archives. The r1mx project has
documented the decryption method and extracted artifacts for all known production builds.
See the [Firmware page]({{ '/firmware' | relative_url }}) for the full build history.

---

## SSD Drive (REDMAG)

The RED ONE MX records to REDMAG SSD modules via the iVDR 26-pin connector.
The r1mx project has fully documented the SSD interface.

### Identified Drive: Toshiba HG3 Series (THNSNC256GBSJ)

| Specification | Value |
|---|---|
| Interface | SATA II (3 Gbit/s), 5V only |
| NAND | Toshiba 32nm MLC (TH58TEG series, Toggle Mode) |
| Controller | Toshiba TC58 "Type C" (proprietary) |
| Sequential read | 220 MB/s |
| Sequential write | 180 MB/s |
| Camera connection | Silicon Image SiI3512 -> iVDR 26-pin (Amphenol 10033998-002LF) |

### Drive Validation

<div class="callout callout--warn">
  <strong>Firmware drive validation:</strong> At boot, the camera reads the drive's ATA model
  string and checks it against a hardcoded approved-drive list. Replacement drives must either
  match an approved model string or the firmware must be patched. Drives that fail validation
  will not be mounted.
</div>

Full research including datasheets, interface mapping, firmware analysis, and replacement
options is documented in
[ssd_drive/README.md](https://github.com/simukka/r1mx/blob/main/ssd_drive/README.md).

---

## Board Manufacturing

The PCB boards were manufactured by the
[Sanmina Corporation](https://web.archive.org/web/20081024222256/https://www.sanmina.com/).
Sanmina is a contract electronics manufacturer that produced boards for many professional
broadcast and cinema equipment makers during this era.

---

## Contributing

The r1mx project is actively building out schematics, component lists, and repair guides.
If you have a RED ONE MX and want to contribute measurements, photos, or findings:

- Open an issue or pull request on [GitHub](https://github.com/simukka/r1mx)
- All board images, component measurements, and reverse engineering artifacts are welcome
