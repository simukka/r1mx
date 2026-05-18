---
layout: page
title: Firmware History
subtitle: Complete release history for RED ONE and RED ONE MX camera firmware
permalink: /firmware/
---

RED ONE firmware is distributed as encrypted `.zip` archives containing a single upgrade
file (`redone.su`). The camera applies upgrades from a CompactFlash card at boot.
This page documents all known production and pre-production builds.

<div class="callout callout--info">
  Firmware files for production builds are preserved in the
  <a href="https://github.com/simukka/r1mx/tree/main/firmware/builds">r1mx firmware archive</a>.
  The decryption key and extraction method are documented in
  <a href="https://github.com/simukka/r1mx/blob/main/firmware/README.md">firmware/README.md</a>.
</div>

---

## Upgrade Instructions

These steps apply to all production builds:

1. Format a CF card using the camera (or a compatible build - see per-build notes)
2. Copy the `upgrade/` folder from the build archive onto the CF card root
3. Do **not** rename the `upgrade/` folder - the camera only reads a folder named `upgrade`
4. Do **not** decompress `redone.su` - the camera handles that itself
5. Power down the camera and insert the CF card
6. Power on - the rear status display will show **"New Firmware"**
7. Press the joystick to confirm; the display will show **"Upgrading"**
8. A blue progress bar runs for approximately 5 minutes
9. When complete, the display shows **"O.K. Cycle Power"**
10. Power cycle the camera and verify the build number on the status display

<div class="callout callout--warn">
  <strong>After any firmware upgrade or downgrade:</strong> Reformat a CF card and perform
  a BLACK SHADING calibration. Operating without a fresh black shade after a firmware change
  usually causes significant color errors.
</div>

---

## Compatibility Rules

| Rule | Detail |
|---|---|
| Mysterium-X cameras | Cannot use firmware prior to Build 30 |
| Mysterium cameras (downgrade) | Cannot downgrade below Build 16 |
| Build 21 upgrade path | Must be on Build 16 or later before upgrading to Build 21 |
| Build 21 downgrade | Cannot roll back to Build 15 or earlier after upgrading |
| Media compatibility | After upgrading, media formatted by older builds may be incompatible |
| CF cards (non-speed-verified) | Limited to 2K record resolution |

---

## Production Builds

<ul class="build-list">

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 32</span>
      <span class="build-version">v32.0.3</span>
      <span class="build-date">Release date: unknown</span>
    </div>
    <div class="build-body">
      <p class="build-summary">Final known production build for RED ONE MX.</p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 31</span>
      <span class="build-version">v31.6.16</span>
      <span class="build-date">Release date: unknown</span>
    </div>
    <div class="build-body">
      <p class="build-summary">Late production build.</p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 30</span>
      <span class="build-version">v30.7.0 / v30.5.0</span>
      <span class="build-date">April 2, 2010 (v30.5.0)</span>
    </div>
    <div class="build-body">
      <p class="build-summary">
        Major release: first official support for the Mysterium-X sensor. Introduces FLUT color
        science, REDcolor, expanded ISO range, REDCODE 42 for 3K/2K, false color MULTI user key,
        LOOK file import from REDCINE-X, CLEAN feed output, monitor FLIP, Edge Code in HANC,
        shutter entry in degrees.
      </p>
      <ul>
        <li>Support for Mysterium-X sensor in RED ONE body</li>
        <li>FLUT Color Science with RGB and RAW metering updates</li>
        <li>ISO 2500-6400 options (Mysterium-X only)</li>
        <li>REDcolor VIEW mode added to AV/VIEW menu</li>
        <li>REDCODE 42 quality option for all 3K and 2K recordings</li>
        <li>Exposure (RAW sensor check), Focus, and Video false color modes</li>
        <li>LOOK (.RLK) file import from REDCINE-X</li>
        <li>SETUP/PROGRAM menu: VIDEO flip, CLEAN feed output, TALLY control</li>
        <li>Remote enable/disable of COLOR via GPI/O</li>
        <li>UNMOUNT added as a USER KEY option</li>
        <li>Time-of-day timecode output freezes when not in Record</li>
        <li>Edge Code value added to LTC location on HD-SDI outputs</li>
        <li>Shutter (exposure time) in Degrees or 1/Sec format</li>
        <li>MAX resolution selector removed (all resolutions now record in MAX mode)</li>
      </ul>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 21</span>
      <span class="build-version">v21.4.1</span>
      <span class="build-date">December 17, 2009</span>
    </div>
    <div class="build-body">
      <p class="build-summary">
        Adds 4.5K WS resolution; REDCODE 42 for 4.5K WS, 4K 2:1, 4K ANA, 4K HD;
        color space VIEW indicator; Video Genlock for HD-SDI; Cooke S4/i lens data support;
        enhanced USER PROFILE; CONFIGURATION function; camera STATUS overview;
        REPEAT FRAME and IN-RECORD flags.
      </p>
      <ul>
        <li>4.5K WS (4480x1920) resolution added</li>
        <li>REDCODE 42 available at 4.5K WS, 4K 2:1, 4K ANA, 4K HD</li>
        <li>Video Genlock for HD-SDI preview output</li>
        <li>Support for S4/i metadata from Cooke Prime and Zoom lenses</li>
        <li>Enhanced USER PROFILE function</li>
        <li>Project CONFIGURATION function and camera STATUS overview</li>
        <li>REPEAT FRAME and IN-RECORD flags in HANC VITC-2 metadata</li>
        <li>CLIP NAME added as HANC metadata in preview HD-SDI output</li>
        <li>Edge highlight color changed from red to blue</li>
        <li>Variable OPACITY for LOOK AROUND area</li>
      </ul>
      <p><strong>Upgrade requirement:</strong> Must be on Build 16 or later. Cannot roll back to Build 15 or earlier.</p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 20</span>
      <span class="build-version">v20.1.6 / v20.1.3</span>
      <span class="build-date">2009</span>
    </div>
    <div class="build-body">
      <p class="build-summary">
        Introduced REDcolor color science and updated post-production color pipeline.
        Other post tools needed updates to reflect the new color science.
      </p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 17</span>
      <span class="build-version">v3.4.1</span>
      <span class="build-date">2008/2009</span>
    </div>
    <div class="build-body">
      <p class="build-summary">Production build in the v3.x series.</p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 16</span>
      <span class="build-version">v3.2.5</span>
      <span class="build-date">2008/2009</span>
    </div>
    <div class="build-body">
      <p class="build-summary">
        Minimum build required before upgrading to Build 21. Minimum downgrade target
        for Mysterium-sensor cameras.
      </p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 15</span>
      <span class="build-version">v2.2.5</span>
      <span class="build-date">2008</span>
    </div>
    <div class="build-body">
      <p class="build-summary">Last build in the v2.x series before the v3.x platform update.</p>
    </div>
  </li>

  <li class="build-item">
    <div class="build-header">
      <span class="build-number">Build 13</span>
      <span class="build-version">v1.8.8</span>
      <span class="build-date">2008</span>
    </div>
    <div class="build-body">
      <p class="build-summary">
        First production build of the v1.8 series. Equivalent feature set to Build 12
        but as an official production release.
      </p>
      <ul>
        <li>SYNCED or FIXED refresh rates for RED-EVF in SYSTEM/MONITOR</li>
        <li>RECORD MODE parameter: NORMAL / VARISPEED / TIMELAPSE in SETUP</li>
        <li>Enable checkbox for USER 1 and USER 2 keys in KEYMAP submenu</li>
        <li>Variable fan speed mode in SYSTEM/SETUP/MAINTENANCE/FAN</li>
        <li>On-camera playback of recorded clips</li>
        <li>Cue to beginning, step through clip list, Normal/Fast Forward/Reverse playback</li>
      </ul>
    </div>
  </li>

</ul>

---

## Pre-Production Builds

These builds were distributed before general availability. Contact the project if you
have firmware images not listed here.

| Build | Version | Notes |
|---|---|---|
| Build 12 | v1.8.8 | Pre-production equivalent of Build 13 |
| Build 11 | v1.8.6 | Pre-production |
| Build 10 | v1.7.0 | Pre-production |
| Build 8 | v1.3.6 | Pre-production |
| Build 7 | v1.3.5 | Pre-production |
| Build 6 | v1.2.1 | Pre-production |
| Build 5 | v1.1.3 | Pre-production |
| Build 4 | v1.1.2 | Pre-production |
| Build 3 | v1.0.4 | Earliest known build |

---

## Companion Software

These software tools were distributed free from red.com/support alongside camera firmware:

| Software | Purpose |
|---|---|
| REDCINE-X | Primary post-production application for R3D files; exports DPX, TIFF, OpenEXR, H.264 |
| ROCKETCINE-X | REDCINE-X variant accelerated by the RED ROCKET PCIe card |
| RED ALERT! | Early RED post tool (superseded by REDCINE-X) |
| REDCODE QuickTime Codec | Codec for native R3D playback in QuickTime / Final Cut Pro |
| RED Final Cut Studio 2/3 Installer | Integration package for Apple Final Cut Pro |
| RED Adobe CS4 Installer | Integration package for Adobe Creative Suite 4 |
