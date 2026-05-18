---
layout: guide
title: "NVRAM Battery Replacement"
subtitle: "Fix the battery that causes time resets and lost settings on every boot."
difficulty: Medium
time: "45-90 minutes"
tools:
  - Torx T6 screwdriver
  - Torx T8 screwdriver
  - Phillips PH0 screwdriver
  - Soldering iron (fine tip, 300-350 C)
  - Solder wick / desoldering braid
  - Rosin flux (no-clean)
  - Multimeter
  - Tweezers
parts:
  - "Panasonic ML2020 rechargeable coin cell (3V, Li-Mn) - NOT CR2020"
category: repair
status: available
permalink: /guides/nvram-battery-replacement/
---

## Overview

The RED ONE MX uses a small rechargeable lithium-manganese coin cell to maintain NVRAM
(non-volatile memory) when the main battery is removed. This cell keeps the real-time clock
and persistent settings alive between shoots.

When this cell dies, the camera loses all memory of settings and resets its clock to a
default time (typically 1:00 AM) on every boot.

The cell is soldered directly to the power board - it is **not** in a socket. Replacement
requires partial disassembly and basic soldering skills.

<div class="callout callout--warn">
  The correct part is the <strong>Panasonic ML2020</strong> - a rechargeable (secondary) cell.
  Do not substitute a CR2020 primary cell. The charging circuit on the power board is designed
  for a rechargeable cell; installing a primary cell may overheat or rupture it.
</div>

<div class="guide-attribution">
  <strong>Source:</strong> Battery identified by <strong>Kyle Simukka</strong> at
  <a href="https://reduser.net/threads/dead-nvram-battery-in-red-one-mx-ml2020.188312/" target="_blank" rel="noopener">Dead NVRAM battery in RED ONE MX - ML2020</a>
  (REDuser.net, 2020).
</div>

---

## Symptoms

This guide applies if you observe **all three** of these symptoms:

| Symptom | Notes |
|---|---|
| Clock resets to a fixed time on every boot | Typically resets to 1:00 AM or a date in 2001/2009 |
| All custom menu settings lost after power cycle | White balance, ISO, project settings, etc. |
| Camera otherwise functions normally | Boots, records, outputs video correctly |

If the camera also fails to boot, see the
[No-Boot Diagnosis]({{ '/guides' | relative_url }}) guide first (planned).

---

## Part Sourcing

The Panasonic ML2020 is widely available from electronics distributors:

| Supplier | Notes |
|---|---|
| Mouser Electronics | Search "ML2020" - stocked as Panasonic ML2020/F2N or similar |
| Digi-Key | Same part family, multiple package variants |
| eBay | Available in bulk packs from Japan - verify "ML" not "CR" before ordering |

The cell costs $2-5 USD. Order 2-3 in case of installation issues.

---

## Steps

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Confirm the diagnosis before disassembling.</strong>
    <p>Boot the camera with a charged main battery. Note the current time shown in the menu.
    Remove the main battery for 30 seconds. Reinstall and boot again. If the clock has reset,
    the NVRAM battery is dead or nearly dead. Proceed with replacement.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Camera menu showing the time/date settings page
</div>

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Fully discharge the main battery and remove all power from the camera.</strong>
    <p>Remove the main battery pack. Remove any external power supply (DC input). Allow the
    camera to sit unpowered for at least 5 minutes before opening.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Remove the rear panel to access the internal boards.</strong>
    <p>The RED ONE MX rear panel is held by Torx T8 screws around the perimeter. Remove all
    screws and carefully separate the panel. The various cable harnesses are short; do not
    force the panel away from the body. Set it aside in a safe location.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Rear panel with Torx screw locations marked
</div>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>Locate the power board and the ML2020 cell.</strong>
    <p>The power board is identifiable by the large power input connector and the cluster of
    power management ICs. The ML2020 coin cell is a small round silver cell (20mm diameter,
    2mm thick) soldered with its positive terminal marked "+" on the board silkscreen.</p>
    <p>The cell is typically located near the edge of the power board, away from the high-density
    component areas. It is soldered through two small through-hole solder points or with
    surface-mount clips depending on board revision.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Close-up of power board showing ML2020 location. Contribution welcome - see <a href="{{ '/guides/contributing' | relative_url }}">Contributing Guide</a>.
</div>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Measure the old cell voltage before removing it.</strong>
    <p>Use a multimeter to measure the voltage across the cell in-circuit (positive probe to +,
    negative probe to -). A healthy ML2020 reads 2.8-3.0V. If you read below 2.5V, the cell
    is confirmed dead. If you read 0V, it may be shorted or completely exhausted.</p>
    <p>Record the voltage for your notes. This is useful for debugging if symptoms persist
    after replacement.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">6</div>
  <div class="guide-step-body">
    <strong>Remove the old cell using desoldering braid.</strong>
    <p>Apply flux to the solder joints. Use desoldering braid and the soldering iron to remove
    the solder from each joint. Once the solder is cleared, the cell should lift out freely.
    Do not apply excessive heat. The cell is small and will heat up quickly; work in short
    bursts to avoid damage to the surrounding pads.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">7</div>
  <div class="guide-step-body">
    <strong>Install the new ML2020 cell, observing polarity.</strong>
    <p>Verify the "+" marking on the board before placing the new cell. Place the ML2020 with
    the positive side (marked "+" on the cell itself) matching the board silkscreen. Apply a
    small amount of fresh solder to each joint. The joints should be smooth and shiny.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">8</div>
  <div class="guide-step-body">
    <strong>Verify installation with a multimeter.</strong>
    <p>Measure voltage across the new cell before reassembling. A new ML2020 should read
    3.0V or very close to it. If you read near 0V, the polarity may be reversed - check and
    correct before proceeding.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">9</div>
  <div class="guide-step-body">
    <strong>Reassemble and test.</strong>
    <p>Reinstall the rear panel. Install the main battery and boot the camera. Set the correct
    time and date in the camera menu. Remove the battery for 30 seconds. Reinstall and boot.
    If the clock has retained the correct time, the replacement was successful.</p>
    <p>Allow the camera to run for a full charge cycle so the charging circuit can top off the
    new cell. The ML2020 will charge from the main battery while the camera is powered on.</p>
  </div>
</div>

---

## Troubleshooting

| Problem | Possible cause | Action |
|---|---|---|
| Clock still resets after replacement | Cell installed with reversed polarity | Remove and reinstall, checking + marking |
| Clock still resets after replacement | Cold solder joint | Reheat both joints with fresh flux |
| Camera does not boot after reassembly | Loose connector or cable disturbed during reassembly | Open rear panel and check all cable harnesses |
| Measured voltage on new cell is 0V | Reversed polarity shorted cell | Replace cell - a shorted Li-Mn cell should be safely discarded |

---

## See Also

- [Black Shading Calibration]({{ '/guides/black-shading-calibration' | relative_url }}) - recommended after any settings loss
- [Hardware Reference]({{ '/hardware' | relative_url }}) - power board documentation
