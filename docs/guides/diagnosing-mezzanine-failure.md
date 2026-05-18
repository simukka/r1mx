---
layout: guide
title: "Diagnosing Mezzanine Connector Failure"
subtitle: "Simultaneous loss of HD-SDI, HDMI, audio, and all storage is the signature of this single failure."
difficulty: Medium
time: "20-30 minutes"
tools:
  - None required for diagnosis
  - Torx T6 and T8 screwdrivers (if proceeding to repair)
  - Stereo microscope or strong magnifying glass (for visual trace inspection)
parts: []
category: diagnosis
status: available
permalink: /guides/diagnosing-mezzanine-failure/
---

## Overview

The most common RED ONE MX failure is lifted PCB traces on the CPU_IO board near the
180-pin Samtec QTH-090-06 mezzanine connector. This connector routes all digital I/O
(video outputs, audio, and storage interfaces) through a single high-density interface.
When thermal cycling stress cracks traces near this connector, all of those subsystems
fail simultaneously.

This guide covers diagnosis only. If the failure is confirmed, see the
[Repairing Broken Traces Near the Mezzanine Connector]({{ '/guides' | relative_url }}) guide
(planned) for the repair procedure.

<div class="callout callout--warn">
  Do not attempt diagnosis by removing and reinserting the mezzanine connector repeatedly.
  The connector is fragile. Reseat it once carefully if you suspect poor contact, then stop.
</div>

---

## The Diagnostic Signature

Mezzanine trace failure produces a very specific pattern. **All four of these must fail simultaneously:**

| Output | Normal state | Failure state |
|---|---|---|
| HD-SDI | Signal present on connected monitor/recorder | No signal |
| HDMI | Signal present | No signal |
| XLR audio input | Audio recorded normally | No audio in recording |
| Storage (CF + SSD + RED DRIVE) | Media detected and accessible | All show as absent or unrecognised |

**If only some of these fail**, the fault is likely elsewhere:
- Only storage fails: check the iVDR connector and SSD module
- Only audio fails: check XLR cable and module
- Only SDI fails: check cable and GS2978 SDI driver chip (AUDIO_PCI board)

The key diagnostic feature is **simultaneous total failure of all four subsystems.**
If you see that pattern, the mezzanine connector traces are the most likely cause.

<div class="guide-attribution">
  <strong>Source:</strong> Failure mode first documented by <strong>Kyle Simukka</strong> at
  <a href="https://reduser.net/threads/researching-red-one-camera-repair-tech.3807690/" target="_blank" rel="noopener">Researching: Red One Camera Repair Tech?</a>
  (REDuser.net, post #8, 2022) and
  <a href="https://reduser.net/threads/red-one-mx-isnt-powering-up-oh-no.188186/" target="_blank" rel="noopener">Red One MX isn't powering up... OH NO!!!</a>
  (REDuser.net, post #12, 2020).
</div>

---

## Steps

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Confirm all four subsystems are failing simultaneously.</strong>
    <p>Connect a known-good HDMI or HD-SDI monitor. Connect a known-good CF card.
    Connect a known-good REDMAG SSD. Connect a known-good XLR microphone or source.
    Power on the camera and check each output.</p>
    <p>If all four fail with known-good accessories, the fault is almost certainly in the
    camera body, not the accessories. Proceed to step 2.</p>
  </div>
</div>

<div class="photo-needed">
  <span class="photo-icon">📷</span>
  Photo needed: Camera with HDMI monitor attached showing "No Signal", and media menu showing no drives detected
</div>

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Locate the mezzanine connector on the CPU_IO board.</strong>
    <p>The CPU_IO board is the large red PCB accessible after removing the camera's rear panel.
    The 180-pin mezzanine connector (labelled J7 on the board) runs horizontally across the
    board and connects the CPU_IO board to the AUDIO_PCI board below it.</p>
  </div>
</div>

<figure class="figure">
  <img src="{{ '/assets/images/guides/damage/IMG_2967.jpg' | relative_url }}"
       alt="CPU_IO board showing dual DDR memory modules and the mezzanine connector running horizontally" />
  <figcaption>CPU_IO board (P/N 131-000000). The horizontal black connector running across the center is the 180-pin Samtec QTH-090-06 mezzanine connector (J7). Photo: Kyle Simukka / r1mx project.</figcaption>
</figure>

<figure class="figure">
  <img src="{{ '/assets/images/guides/damage/IMG_2972.jpg' | relative_url }}"
       alt="CPU_IO board wider angle showing full mezzanine connector and AUDIO_PCI board below" />
  <figcaption>Wider view showing both boards. The CPU_IO board is on top; the AUDIO_PCI board below it. The mezzanine connector bridges them at center. The large inductor labelled 3R9 is on the AUDIO_PCI board. Photo: Kyle Simukka / r1mx project.</figcaption>
</figure>

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Inspect the area around the mezzanine connector under magnification.</strong>
    <p>Look for any of the following around the connector body on the CPU_IO board:</p>
    <ul>
      <li>Hairline cracks running across copper traces (appears as a thin dark line through a trace)</li>
      <li>Lifted traces (trace visually separated from board surface)</li>
      <li>Cold solder joints at the connector pins (dull, grainy, or bulging solder)</li>
      <li>Physical deformation from impact or thermal stress</li>
    </ul>
    <p>The traces most commonly affected are on the CPU_IO board side, within 5mm of the
    connector body. The damage is often subtle and requires at minimum a strong loupe
    or magnifying glass; a stereo microscope is ideal.</p>
  </div>
</div>

<figure class="figure">
  <img src="{{ '/assets/images/guides/damage/IMG_2990.jpg' | relative_url }}"
       alt="AUDIO_PCI board showing LT1161CSW chip and edge connectors near the mezzanine" />
  <figcaption>AUDIO_PCI board section showing the edge connector area (bottom of board). The LT1161CSW power switch IC is also visible. This board sits directly below the CPU_IO board. Photo: Kyle Simukka / r1mx project.</figcaption>
</figure>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>If visual inspection finds no obvious damage, perform a continuity test.</strong>
    <p>With the boards separated (camera fully disassembled), use a multimeter on continuity
    mode to probe traces on the CPU_IO board near the mezzanine connector. A broken trace
    will show no continuity between two points that should be connected.</p>
    <p>Identifying which specific traces to test requires the board schematics - these are
    under active research in the r1mx project. See the
    <a href="{{ '/hardware' | relative_url }}">Hardware Reference</a> page for current status.</p>
  </div>
</div>

<figure class="figure">
  <img src="{{ '/assets/images/guides/damage/IMG_2968.jpg' | relative_url }}"
       alt="Close-up of CPU_IO board showing Gennum GS4911B chip and fine PCB traces near the mezzanine area" />
  <figcaption>CPU_IO board detail showing the Gennum GS4911B SDI chip (upper right) and dense trace routing near the mezzanine connector region. This is the area to inspect carefully. Photo: Kyle Simukka / r1mx project.</figcaption>
</figure>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Document your findings before reassembling.</strong>
    <p>Photograph the area under magnification. Note the exact location of any damaged traces.
    This documentation is valuable for:</p>
    <ul>
      <li>Planning the trace repair</li>
      <li>Contributing findings to the <a href="https://github.com/simukka/r1mx" target="_blank" rel="noopener">r1mx project</a></li>
      <li>Getting help from the community (post photos to <a href="https://reduser.net/forums/red-one.22/" target="_blank" rel="noopener">REDuser.net RED ONE forum</a>)</li>
    </ul>
  </div>
</div>

---

## What to Do Next

| Finding | Next action |
|---|---|
| Clearly lifted or cracked traces visible | Proceed to trace repair guide (Hard difficulty) |
| Connector physically damaged or pins bent | Connector replacement required - seek professional service |
| No visible damage found | Perform continuity test; or send to qualified repair technician |
| Fault not reproducible | May be intermittent connection - clean and reseat connector once |

---

## Board Reference Photos

These are Kyle Simukka's photos of a RED ONE MX CPU_IO board taken during the r1mx
reverse engineering project (July 2020). Click any image for full size.

<div class="gallery">
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_2967.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_2967.jpg' | relative_url }}" alt="CPU_IO board overview" />
    </a>
    <figcaption>CPU_IO board - DDR memory and mezzanine connector</figcaption>
  </figure>
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_2968.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_2968.jpg' | relative_url }}" alt="CPU_IO board Gennum chip area" />
    </a>
    <figcaption>Gennum GS4911B and trace routing</figcaption>
  </figure>
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_2972.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_2972.jpg' | relative_url }}" alt="Both boards stacked" />
    </a>
    <figcaption>CPU_IO over AUDIO_PCI - full mezzanine connector view</figcaption>
  </figure>
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_2969.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_2969.jpg' | relative_url }}" alt="Board corner showing damaged component" />
    </a>
    <figcaption>Board corner - note damaged component (burnt MOSFET)</figcaption>
  </figure>
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_3004.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_3004.jpg' | relative_url }}" alt="Sensor board with ADV212B80Z and mezzanine connector J4" />
    </a>
    <figcaption>Sensor board (P/N 132-000003 REV B) - Analog Devices ADV212B80Z and connector J4</figcaption>
  </figure>
  <figure class="figure">
    <a href="{{ '/assets/images/guides/damage/IMG_2975.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/damage/IMG_2975.jpg' | relative_url }}" alt="CPU_IO board edge label" />
    </a>
    <figcaption>CPU &amp; IO Board label: P/N 131-000000, date code 0838CP097</figcaption>
  </figure>
</div>

---

## See Also

- [Hardware Reference]({{ '/hardware' | relative_url }}) - full board documentation and IC list
- [Camera Will Not Boot diagnosis]({{ '/guides' | relative_url }}) - planned guide
