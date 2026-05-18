---
layout: page
title: Repair Guides
subtitle: Step-by-step guides for maintaining, diagnosing, and repairing the RED ONE MX
permalink: /guides/
---

Community repair guides for the RED ONE MX, inspired by iFixit. Guides range from "tighten
a loose screw" to "repair a broken trace under a microscope." Every guide has a difficulty
rating, time estimate, and tools list.

Guides marked **Available** are complete. **Planned** guides are on the roadmap - write one
by following the [Contributing Guide]({{ '/guides/contributing' | relative_url }}).
Anyone can write a guide (including AI agents), but a human will need to take the photos.

<div class="callout callout--warn">
  <strong>Safety:</strong> The RED ONE MX contains capacitors that can hold charge after
  power-off. Always power down fully and wait at least 60 seconds before opening the body.
  Use ESD precautions when handling any PCB.
</div>

---

<div class="guide-community-q">
  <h3>Common questions from REDuser.net - each maps to a guide below</h3>
  <ul>
    <li>"Camera powers on but the menu monitor stays white" - lens data cable pinched</li>
    <li>"No HD-SDI, HDMI, audio, and CF/SSD all failed at the same time" - mezzanine connector</li>
    <li>"SSD shows as INCOMPATIBLE" - firmware drive allowlist</li>
    <li>"Fan is rattling or very loud" - fan bearing failure or debris</li>
    <li>"Camera won't boot after a battery swap" - power board connector / voltage sag</li>
    <li>"Colors look wrong after a firmware update" - black shading calibration not run</li>
    <li>"Camera freezes when plugging in an accessory while powered" - known boot sensitivity; power down first</li>
    <li>"Finding a tech who still services RED ONE" - see Resources page</li>
  </ul>
</div>

---

## Maintenance

Simple tasks that require no disassembly. Do these on a regular schedule to prevent failures.

<ul class="guide-list">
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Tightening body screws and Torx hardware</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Cleaning the PL mount interface</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Inspecting and cleaning V-mount battery contacts</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Inspecting and cleaning the iVDR / REDMAG connector</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Cleaning the CF card reader contacts</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Cleaning the cooling fan (external access)</span>
    <span class="guide-list-time">15 min - Planned</span>
  </li>
  <li class="guide-list-item">
    <a class="guide-list-item" href="{{ '/guides/fan-bearing-oiling' | relative_url }}" style="display:contents; text-decoration:none;">
      <span class="guide-pill medium">Medium</span>
      <span class="guide-list-title" style="color:var(--text);">Fan bearing oiling (fix rattling fan without full replacement)</span>
      <span class="guide-list-time">30-60 min - <strong style="color:#5dba5d;">Available</strong></span>
    </a>
  </li>
</ul>

---

## Media and Storage

<ul class="guide-list">
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Formatting a CF card in-camera</span>
    <span class="guide-list-time">5 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Creating a firmware upgrade CF card</span>
    <span class="guide-list-time">10 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Installing and swapping a REDMAG SSD module</span>
    <span class="guide-list-time">5 min - Planned</span>
  </li>
  <li class="guide-list-item">
    <a class="guide-list-item" href="{{ '/guides/redmag-ssd-module' | relative_url }}" style="display:contents; text-decoration:none;">
      <span class="guide-pill hard">Hard</span>
      <span class="guide-list-title" style="color:var(--text);">Building a community REDMAG SSD replacement module</span>
      <span class="guide-list-time">2-4 hrs - <strong style="color:#5dba5d;">Available</strong></span>
    </a>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">Diagnosing "media not recognized" and INCOMPATIBLE errors</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
</ul>

---

## Firmware and Calibration

<ul class="guide-list">
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Upgrading firmware: full step-by-step procedure</span>
    <span class="guide-list-time">30 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Downgrading firmware safely</span>
    <span class="guide-list-time">30 min - Planned</span>
  </li>
  <li class="guide-list-item">
    <a class="guide-list-item" href="{{ '/guides/black-shading-calibration' | relative_url }}" style="display:contents; text-decoration:none;">
      <span class="guide-pill easy">Easy</span>
      <span class="guide-list-title" style="color:var(--text);">Black shading calibration (required after every firmware change)</span>
      <span class="guide-list-time">15 min - <strong style="color:#5dba5d;">Available</strong></span>
    </a>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Reading and recording build number and sensor info</span>
    <span class="guide-list-time">5 min - Planned</span>
  </li>
</ul>

---

## Diagnosis

Use these guides to identify the root cause before attempting a repair.

<ul class="guide-list">
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">No-boot diagnosis flowchart</span>
    <span class="guide-list-time">30 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">White menu screen on boot: lens data cable inspection</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
  <li class="guide-list-item">
    <a class="guide-list-item" href="{{ '/guides/diagnosing-mezzanine-failure' | relative_url }}" style="display:contents; text-decoration:none;">
      <span class="guide-pill medium">Medium</span>
      <span class="guide-list-title" style="color:var(--text);">Diagnosing simultaneous multi-output failure (mezzanine connector)</span>
      <span class="guide-list-time">20-30 min - <strong style="color:#5dba5d;">Available</strong></span>
    </a>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">SSD not recognized: diagnosis and fix options</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">Diagnosing overheating and fan failure</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">Camera freezes or hangs during operation</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">No power after REDMAG swap: connector and power delivery check</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
</ul>

---

## Repairs

These guides require partial or full disassembly. Read the relevant diagnosis guide first.

<ul class="guide-list">
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">Replacing the cooling fan</span>
    <span class="guide-list-time">45 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill medium">Medium</span>
    <span class="guide-list-title">Swapping the PL lens mount</span>
    <span class="guide-list-time">30 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill easy">Easy</span>
    <span class="guide-list-title">Replacing the V-mount battery plate</span>
    <span class="guide-list-time">20 min - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill hard">Hard</span>
    <span class="guide-list-title">Repairing broken traces near the mezzanine connector</span>
    <span class="guide-list-time">2-4 hrs - Planned</span>
  </li>
  <li class="guide-list-item planned">
    <span class="guide-pill hard">Hard</span>
    <span class="guide-list-title">Cleaning or replacing the iVDR connector</span>
    <span class="guide-list-time">1-2 hrs - Planned</span>
  </li>
  <li class="guide-list-item">
    <a class="guide-list-item" href="{{ '/guides/nvram-battery-replacement' | relative_url }}" style="display:contents; text-decoration:none;">
      <span class="guide-pill medium">Medium</span>
      <span class="guide-list-title" style="color:var(--text);">Replacing the NVRAM backup battery (ML2020)</span>
      <span class="guide-list-time">45-90 min - <strong style="color:#5dba5d;">Available</strong></span>
    </a>
  </li>
</ul>

---

## Contribute a Guide

The fastest way to help this project is to write a guide for a procedure you have already done.

- Copy the [guide template]({{ '/guides/contributing' | relative_url }})
- Add your steps (photos can be added later - placeholder blocks are built in)
- Open a pull request at [github.com/simook/r1mx](https://github.com/simook/r1mx)

No coding knowledge required. If you can write a numbered list, you can write a guide.
