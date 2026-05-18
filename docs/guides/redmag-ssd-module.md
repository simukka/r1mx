---
layout: guide
title: "REDMAG SSD Replacement Module"
subtitle: "Community-designed replacement for the original RED iVDR SSD module, using modern SSD drives."
difficulty: Hard
time: "2-4 hours (first build)"
tools:
  - 3D printer (FDM, 0.2mm layer height recommended)
  - Soldering iron (fine tip)
  - Flux (no-clean)
  - Small flathead screwdriver
  - Calipers (for fit verification)
  - CA adhesive (cyanoacrylate, for assembly)
parts:
  - "Custom PCB (Gerber files in r1mx repository)"
  - "Amphenol 10079510 iVDR connector (replacement for EOL 10033998-002LF)"
  - "M.2 NVMe SSD (compatible drive, see notes below)"
  - "M.2 to mSATA or SATA adapter (per chosen PCB design)"
  - "3D printed enclosure (STEP/STL files in r1mx repository)"
  - "M2 or M3 hardware (screws and inserts, per BOM)"
category: media
status: available
permalink: /guides/redmag-ssd-module/
---

## Overview

Original RED iVDR SSD REDMAG modules used spinning hard drives or early SSDs that are
now end-of-life. The iVDR connector itself (Amphenol 10033998-002LF) is also discontinued.
This guide documents a community-designed replacement module that uses a modern M.2 SSD
inside a 3D-printed enclosure with a replacement iVDR connector.

This design was pioneered by **Troy Grundstad** and documented on REDuser.net. The r1mx
project has incorporated these findings and is developing updated files.

<div class="callout callout--warn">
  This is a complex build requiring soldering, 3D printing, and careful mechanical fitting.
  The r1mx project is actively refining the design files. Before committing to a full build,
  check the <a href="https://github.com/simukka/r1mx" target="_blank" rel="noopener">r1mx repository</a>
  for the latest design revision.
</div>

<div class="guide-attribution">
  <strong>Source:</strong> Original design and images by <strong>Troy Grundstad</strong> at
  <a href="https://reduser.net/threads/diy-redmag-ssd-replacement-module.3773957/" target="_blank" rel="noopener">DIY REDMAG SSD Replacement Module</a>
  (REDuser.net, thread 3773957, Stavanger, Norway).
  Design concept continued and extended by the r1mx project.
</div>

---

## Background: The iVDR Standard

REDMAG modules use the **iVDR** (Information Versatile Disc for Removable usage) interface,
which is a hot-swappable storage interface standard developed in the early 2000s for
consumer electronics. RED ONE used iVDR as a removable storage bay.

The original Amphenol iVDR connector (10033998-002LF) is end-of-life. The replacement
connector is the **Amphenol 10079510**, which has a compatible footprint and pinout.

---

## Design Evolution

Troy Grundstad's original build documents the full design process from CAD model to
finished module:

<div class="thumb-grid">
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-cad-model.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-cad-model.jpg' | relative_url }}" alt="CAD model of REDMAG enclosure" />
    </a>
    <div class="thumb-label">CAD model of the replacement enclosure</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-3dprint-rough.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-3dprint-rough.jpg' | relative_url }}" alt="First rough 3D print test fit" />
    </a>
    <div class="thumb-label">First rough 3D print, test fitting</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-prototype-pcb.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-prototype-pcb.jpg' | relative_url }}" alt="Prototype PCB with iVDR connector" />
    </a>
    <div class="thumb-label">Prototype PCB with iVDR connector soldered</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-pcb-connectors.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-pcb-connectors.jpg' | relative_url }}" alt="PCB connector detail" />
    </a>
    <div class="thumb-label">PCB connector detail</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-pcb-v2.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-pcb-v2.jpg' | relative_url }}" alt="Revised PCB v2 layout" />
    </a>
    <div class="thumb-label">Revised PCB v2</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-original-18in.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-original-18in.jpg' | relative_url }}" alt="Original REDMAG module for reference" />
    </a>
    <div class="thumb-label">Original REDMAG module (18-pin iVDR shown)</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-enclosure-logo.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-enclosure-logo.jpg' | relative_url }}" alt="Final enclosure with r1mx branding" />
    </a>
    <div class="thumb-label">Final enclosure with logo panel</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-v1-finished-1.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-v1-finished-1.jpg' | relative_url }}" alt="Finished v1 module" />
    </a>
    <div class="thumb-label">Finished v1 module</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-v1-finished-2.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-v1-finished-2.jpg' | relative_url }}" alt="Finished v1 module side view" />
    </a>
    <div class="thumb-label">V1 module, side view</div>
  </div>
  <div class="thumb-item">
    <a href="{{ '/assets/images/guides/redmag-v1-finished-3.jpg' | relative_url }}" target="_blank">
      <img src="{{ '/assets/images/guides/redmag-v1-finished-3.jpg' | relative_url }}" alt="Finished v1 module connector end" />
    </a>
    <div class="thumb-label">V1 module, connector end</div>
  </div>
</div>

*Images: Troy Grundstad / REDuser.net thread 3773957. Used with attribution.*

---

## The SSD Side Module Requirement

To use a REDMAG SSD module, the camera must have the **SSD Side Module** installed.
The SSD Side Module is the physical casing that provides the REDMAG bay and facilitates
the iVDR connector interface. It replaces the CF Module or Hard Drive Module on the
camera's left side.

This module is not a failure point - it is simply the required physical bay for REDMAG
operation. If your camera currently uses a CF Module or RED DRIVE, you will need the
SSD Side Module before a REDMAG will function.

The r1mx project is developing open-source replacement designs for the SSD Side Module
enclosure. See the [Firmware and Storage]({{ '/firmware' | relative_url }}) page for current status.

---

## SSD Compatibility Notes

Not all M.2 SSDs work with the RED ONE MX. The camera was designed for ATA/SATA storage
and has specific timing and model-string requirements.

Key findings from the r1mx research:

| Drive type | Compatibility | Notes |
|---|---|---|
| Original Toshiba HG3 SSD (from RED) | Confirmed working | Hard to source; typically sourced from dead modules |
| Other SATA SSDs with ATA model string reprogramming | May work | Firmware patch (build 32.1, in development) aims to remove this restriction |
| NVMe SSDs via M.2 adapter | Not currently compatible | SATA only interface |

The r1mx firmware project (build 32.1) is specifically targeting expanded SSD compatibility.
See the [Firmware Reference]({{ '/firmware' | relative_url }}) page for details.

---

## Build Steps

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Download the current design files from the r1mx repository.</strong>
    <p>Visit <a href="https://github.com/simukka/r1mx" target="_blank" rel="noopener">github.com/simukka/r1mx</a>
    and download the REDMAG module design files from the <code>ssd_drive/</code> directory.
    Review the README for the current revision status before ordering parts or starting a print.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Order the PCB and source components.</strong>
    <p>The Gerber files can be uploaded to any PCB fabricator (JLCPCB, PCBWay, OSH Park, etc.).
    Order the Amphenol 10079510 iVDR connector from Mouser or Digi-Key. The iVDR connector
    is the most critical component - verify the part number before ordering.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Print the enclosure.</strong>
    <p>Print with PETG or ABS for heat resistance (PLA may soften in a warm camera bag or
    in-camera). A 0.2mm layer height provides sufficient detail for the connector cutout
    and slot tolerances. Print with at least 3 perimeters and 40% infill for rigidity.</p>
    <p>Print a test fit piece first before committing to a full enclosure print. The iVDR
    connector cutout dimensions are critical.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>Solder the iVDR connector to the PCB.</strong>
    <p>The Amphenol 10079510 is a fine-pitch surface mount connector. Apply flux liberally
    to the pads. Tack two corner pins first to align the connector, then solder across all pins.
    Inspect under magnification for solder bridges. Clean flux residue with isopropyl alcohol.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Install the SSD on the PCB and assemble into the enclosure.</strong>
    <p>Following the PCB layout, install the M.2 SSD or adapter. Assemble the PCB into the
    3D printed enclosure per the assembly notes in the repository. Verify that the iVDR
    connector is correctly aligned with the enclosure cutout before final assembly.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">6</div>
  <div class="guide-step-body">
    <strong>Test fit in the SSD Side Module before final assembly.</strong>
    <p>Insert the module into the SSD Side Module bay (on the camera) without the enclosure
    screws fully tightened. Verify it seats fully and the iVDR connector engages. Look for
    any interference in the bay. Adjust the print or enclosure dimensions if needed before
    fully assembling.</p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">7</div>
  <div class="guide-step-body">
    <strong>Test with the camera.</strong>
    <p>Insert the assembled module into the camera. Power on and check the media menu.
    If the drive is detected, attempt a format and test recording. If the drive shows as
    "INCOMPATIBLE", the drive model string may need to be reprogrammed. See the
    <a href="{{ '/firmware' | relative_url }}">Firmware Reference</a> for current compatibility research.</p>
  </div>
</div>

---

## Troubleshooting

| Problem | Possible cause | Action |
|---|---|---|
| Module not detected at all | iVDR connector not seated / soldering issue | Check connector seating; inspect solder joints |
| Drive shows "INCOMPATIBLE" | SSD model string not on RED approved list | Reprogram model string (advanced); or wait for firmware 32.1 |
| Module fits loosely in bay | Print tolerance too loose | Reprint enclosure with slightly reduced tolerances |
| Camera freezes when module inserted | Power issue or connector short | Check for solder bridges; test with different SSD |

---

## Contributing

This guide is actively being updated as the r1mx project develops the design files.
If you have built a module, your photos, measurements, and notes are valuable.
See the [Contributing Guide]({{ '/guides/contributing' | relative_url }}) for how to submit.

---

## See Also

- [Firmware Reference]({{ '/firmware' | relative_url }}) - SSD compatibility and firmware 32.1 development
- [Components Reference]({{ '/components' | relative_url }}) - original REDMAG specifications
- [r1mx Repository](https://github.com/simukka/r1mx) - design files, Gerbers, BOM
