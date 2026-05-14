---
layout: guide
title: "Fan Bearing Oiling"
subtitle: "A simple fix for a rattling or noisy cooling fan that does not require full fan replacement."
difficulty: Medium
time: "30-60 minutes"
tools:
  - Torx T6 screwdriver
  - Torx T8 screwdriver
  - Phillips PH0 screwdriver
  - Tweezers or small pick
  - Light machine oil (sewing machine oil, or 3-in-1 oil - very small amount)
  - Cotton swabs
parts: []
category: maintenance
status: available
permalink: /guides/fan-bearing-oiling/
---

## Overview

The RED ONE MX uses an active cooling fan to protect the sensor and electronics during
operation. Fan bearings wear over time and can become noisy, rattling, or intermittently
seized. In many cases the fan itself is still functional - the bearings simply need
lubrication.

This procedure oils the fan shaft bearings to restore quiet operation and extend fan life.
If the fan has physically failed (no rotation, or burning smell), replacement is required
instead.

<div class="guide-attribution">
  <strong>Source:</strong> Procedure documented by <strong>Aaron Rash</strong> at
  <a href="https://reduser.net/threads/noisy-fan-fix-red-one-mx-bearing-oil.172799/" target="_blank" rel="noopener">Noisy Fan Fix - RED ONE MX Bearing Oil</a>
  (REDuser.net, thread 172799).
</div>

---

## Symptoms

This guide applies if you observe:

| Symptom | Notes |
|---|---|
| Rattling or buzzing sound during operation | Increases with camera temperature |
| Fan runs but is louder than normal | May change tone at different fan speeds |
| Intermittent fan noise | Bearings may be partially seized |

If the fan does not spin at all, or if SYSTEM > MAINTENANCE > FAN reports an error,
see the fan replacement guide (planned).

---

## Understanding the Fan Diagnostic Menu

Before disassembling, use the camera's built-in fan test:

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Access the fan diagnostic in the camera menu.</strong>
    <p>Navigate to: <strong>SYSTEM &gt; MAINTENANCE &gt; FAN</strong><br />
    This menu allows you to run the fan at different speeds and monitor its operation.
    Run the fan at maximum speed and listen for the noise. If noise is present at high speed,
    bearing wear is confirmed.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Camera menu showing SYSTEM > MAINTENANCE > FAN screen
</div>

---

## Disassembly Steps

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Power down and remove all power from the camera.</strong>
    <p>Remove the main battery and any external power. Allow the camera to cool fully if it
    was recently in use. The cooling fan and heatsink may be hot.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Remove the rear panel to access the fan assembly.</strong>
    <p>The rear panel is secured by Torx T8 screws around its perimeter. Remove all screws
    and set them aside in order. Carefully separate the panel, noting the cable harnesses.
    The fan is mounted inside the body and becomes accessible once the panel is removed.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Rear panel removed, showing fan assembly location inside camera body
</div>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>Disconnect the fan power cable.</strong>
    <p>The fan has a small 2- or 3-pin connector. Carefully disconnect it by pulling straight
    back on the connector body - do not pull on the wires themselves.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Remove the fan from its mount.</strong>
    <p>The fan is typically secured with 4 small screws (Phillips PH0 or Torx T6). Remove
    these and carefully lift the fan out. Note the orientation so it can be reinstalled
    correctly - airflow direction matters.</p>
  </div>
</div>

---

## Oiling the Bearings

<div class="guide-step">
  <div class="guide-step-num">6</div>
  <div class="guide-step-body">
    <strong>Locate the bearing access point on the fan.</strong>
    <p>Most 40-60mm computer fans have a small rubber or plastic sticker on the back (hub side)
    of the fan that covers the shaft bearing. Carefully peel back this sticker - it is often
    reusable if handled gently. Underneath you will see the fan shaft.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Back of fan showing rubber sticker over bearing access point
</div>

<div class="guide-step">
  <div class="guide-step-num">7</div>
  <div class="guide-step-body">
    <strong>Apply one or two drops of light machine oil to the shaft.</strong>
    <p>Use a very small amount of light machine oil - such as sewing machine oil, 3-in-1 oil,
    or a similar light lubricant. One or two drops is sufficient. More oil can attract dust
    and make the problem worse over time.</p>
    <p>Apply the oil to the shaft where it enters the bearing. Spin the fan blades by hand a
    few times to work the oil into the bearing surfaces.</p>
    <div class="callout callout--warn">
      Do not use WD-40. It is a solvent and will remove existing lubrication without providing
      adequate long-term protection.
    </div>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">8</div>
  <div class="guide-step-body">
    <strong>Replace the rubber sticker and spin-test the fan by hand.</strong>
    <p>Press the rubber sticker back into place. Spin the fan blades by hand - it should
    rotate freely and smoothly without any catching or roughness.</p>
    <p>If the fan still feels rough or gritty when spun by hand, the bearings may be worn
    beyond lubrication. Fan replacement may be required.</p>
  </div>
</div>

---

## Reassembly and Testing

<div class="guide-step">
  <div class="guide-step-num">9</div>
  <div class="guide-step-body">
    <strong>Reinstall the fan in its original orientation.</strong>
    <p>Replace the fan screws and reconnect the power cable. Verify the orientation matches
    how it was removed - the fan arrow (if present) typically indicates airflow direction.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">10</div>
  <div class="guide-step-body">
    <strong>Reinstall the rear panel and test.</strong>
    <p>Replace the rear panel and all Torx T8 screws. Install the battery and power on.
    Navigate to SYSTEM &gt; MAINTENANCE &gt; FAN and run the fan at maximum speed.
    The noise should be significantly reduced or eliminated.</p>
  </div>
</div>

---

## Troubleshooting

| Problem | Possible cause | Action |
|---|---|---|
| Fan still noisy after oiling | Bearing worn beyond lubrication | Fan replacement required |
| Fan vibrates instead of rattles | Fan blade cracked or out of balance | Fan replacement required |
| No change in noise level | Oil not reaching bearings | Remove sticker again, apply more oil to shaft directly |
| Camera reports fan error | Fan cable not fully seated | Check connector and reseat |

---

## See Also

- [Diagnosing Overheating / Fan Failure]({{ '/guides' | relative_url }}) - planned guide
- [Hardware Reference]({{ '/hardware' | relative_url }}) - fan specifications
