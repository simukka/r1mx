---
layout: guide
title: "Black Shading Calibration"
subtitle: "Required after every firmware upgrade or downgrade. Takes 15 minutes and costs nothing."
difficulty: Easy
time: "15 minutes"
tools:
  - Lens cap (PL-mount body cap or any light-blocking cap)
  - Charged RED BRICK battery or AC adaptor
parts: []
category: firmware
status: available
permalink: /guides/black-shading-calibration/
---

## Overview

Black shading calibration corrects sensor offset errors by measuring the camera's output with
no light reaching the sensor. The camera records a baseline "dark frame" for every pixel and
uses it to cancel thermal noise and fixed-pattern noise during recording.

**When to run it:**
- After every firmware upgrade
- After every firmware downgrade
- After any repair that involved the sensor or IMAGE board
- Whenever you notice unexpected color casts, hot pixels, or unusual noise in shadows

Skipping this step after a firmware change is the single most common cause of degraded image
quality on the RED ONE MX.

<div class="callout callout--warn">
  The camera must be at a stable operating temperature before running black shading.
  Power it on and let it run for at least <strong>10 minutes</strong> before starting.
  Running calibration on a cold camera produces inaccurate results.
</div>

---

## Before You Start

Check that you have:

- A fully charged battery or AC power connected (calibration cannot be interrupted)
- A lens cap that completely blocks all light from reaching the sensor
- The camera powered on and warmed up for at least 10 minutes

---

## Steps

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Format a fresh CF card using the current firmware.</strong>
    <p>Insert a CF card and format it in-camera via <strong>SYSTEM &gt; FORMAT MEDIA</strong>.
    This ensures the card filesystem matches the current build and calibration data
    saves correctly.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Camera menu showing SYSTEM &gt; FORMAT MEDIA
</div>

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Fit the lens cap so no light can enter the camera.</strong>
    <p>Use a PL-mount body cap, a PL lens with its rear cap installed, or wrap the mount
    with a dark cloth. Even a small amount of ambient light will corrupt the calibration.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: PL body cap fitted to the camera mount
</div>

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Navigate to the Black Shade menu.</strong>
    <p>From the camera's home menu, go to:<br>
    <code>SYSTEM &gt; MAINTENANCE &gt; BLACK SHADE</code></p>
    <p>If this option is greyed out, the camera may be in a recording-ready state.
    Press <strong>STOP</strong> first.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: SYSTEM &gt; MAINTENANCE &gt; BLACK SHADE menu path
</div>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>Confirm the camera and environment are ready, then start calibration.</strong>
    <p>Select <strong>BLACK SHADE</strong> and confirm when prompted. The process takes
    approximately 60-90 seconds. Do not:</p>
    <ul>
      <li>Remove the battery or disconnect AC power</li>
      <li>Remove or insert any media</li>
      <li>Move the camera or remove the lens cap</li>
      <li>Press any buttons</li>
    </ul>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Wait for "Black Shade Complete" confirmation.</strong>
    <p>The camera will display a completion message on the rear status display and the
    RED-LCD / RED-EVF if attached. This confirms the calibration data was written
    to the CF card successfully.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: "Black Shade Complete" message on rear display
</div>

<div class="guide-step">
  <div class="guide-step-num">6</div>
  <div class="guide-step-body">
    <strong>Power cycle the camera.</strong>
    <p>Fully power down (hold power button until shutdown completes) and power back on.
    The calibration data is loaded from the CF card on boot.</p>
    <p>Do not remove the CF card between calibration and the next power cycle.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">7</div>
  <div class="guide-step-body">
    <strong>Verify by shooting a test clip.</strong>
    <p>Remove the lens cap, fit a lens, and record a short clip in a neutral scene
    (evenly lit grey card is ideal). Review in post and confirm:</p>
    <ul>
      <li>No unexpected color cast in shadows</li>
      <li>No fixed hot pixels or bright spots</li>
      <li>Shadow noise looks uniform (not patterned)</li>
    </ul>
  </div>
</div>

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| BLACK SHADE menu is greyed out | Camera in record-ready state | Press STOP, then try again |
| Calibration starts but camera reboots | Power interrupted or battery low | Use AC power and retry |
| "Calibration Failed" message | Light leak through mount, or CF card error | Check lens cap seal, reformat CF card, retry |
| Colors still wrong after calibration | Cold camera during calibration | Let camera warm up 10+ minutes, redo calibration |
| Hot pixels still visible | Calibration data not loaded | Power cycle with CF card installed |

---

## Notes

- Black shading data is stored on the CF card, not in camera flash memory. Keep the
  calibration CF card in the camera or clearly labelled.
- Calibration is temperature-sensitive. If the camera will be used in a significantly
  different environment (e.g., moving from an air-conditioned room to outdoor summer heat),
  re-run calibration in the actual shooting environment.
- Some users report running black shading at the start of each shooting day as standard
  practice. This is not strictly required but eliminates a variable.

---

## See Also

- [Firmware page]({{ '/firmware' | relative_url }}) - full build history and upgrade instructions
- [Upgrading firmware: full step-by-step procedure]({{ '/guides' | relative_url }}) - planned guide
