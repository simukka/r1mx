---
layout: page
title: Troubleshooting
subtitle: Known failure modes and diagnostic procedures for the RED ONE MX
permalink: /troubleshooting/
---

This page documents known failure modes and diagnostic approaches based on the
[r1mx reverse engineering project](https://github.com/simook/r1mx). The RED ONE MX is
a complex precision instrument and failures can have multiple causes; always approach
diagnostics systematically.

<div class="callout callout--warn">
  <strong>Safety first:</strong> The RED ONE MX contains capacitors that can hold charge
  after power-off. Always power down fully and wait before opening the camera body.
  Electrostatic discharge (ESD) can damage sensitive components; use appropriate precautions.
</div>

---

## Symptom Index

| Symptom | Likely cause | Section |
|---|---|---|
| No HD-SDI output | CPU_IO/AUDIO_PCI mezzanine | [Mezzanine interconnect failure](#mezzanine-interconnect-failure) |
| No HDMI output | CPU_IO/AUDIO_PCI mezzanine | [Mezzanine interconnect failure](#mezzanine-interconnect-failure) |
| No XLR audio input | CPU_IO/AUDIO_PCI mezzanine | [Mezzanine interconnect failure](#mezzanine-interconnect-failure) |
| Cannot detect SSD/CF/RED DRIVE | CPU_IO/AUDIO_PCI mezzanine | [Mezzanine interconnect failure](#mezzanine-interconnect-failure) |
| Drive not recognised at boot | SSD model string validation | [SSD not recognised](#ssd-not-recognised) |
| Camera will not upgrade firmware | CF card formatting / folder structure | [Firmware upgrade fails](#firmware-upgrade-fails) |
| Significant color errors after firmware change | Missing black shade calibration | [Color errors after firmware update](#color-errors-after-firmware-update) |
| Camera does not boot | Power system, battery, or board fault | [Camera will not boot](#camera-will-not-boot) |

---

## Mezzanine Interconnect Failure

### Symptom

The following issues occur **simultaneously**:
- No HD-SDI video output
- No HDMI video output
- No audio input via XLR
- Unable to detect CF card, SSD module, or RED DRIVE

### Cause

The CPU_IO board and AUDIO_PCI board are connected by a 180-position high-speed mezzanine
connector. This connector routes all of these signals across a single interface. Broken or
damaged traces on the CPU_IO board at or near this connector cause simultaneous loss of
all attached subsystems.

This is the most commonly reported multi-symptom failure on RED ONE MX cameras.

### Diagnosis

1. Confirm all four symptoms are present simultaneously (not one or two)
2. Inspect the CPU_IO board around the 180-position mezzanine connector for:
   - Visible cracked or lifted traces
   - Cold solder joints or connector damage
   - Physical deformation from impact or flexing
3. Reseat the mezzanine connector carefully (connector part number TBD - see
   [repository](https://github.com/simook/r1mx))
4. If reseating does not resolve the issue, inspect traces under magnification

### Status

The exact mezzanine connector part number is under active research in the r1mx project.
Repair options include trace repair via bridging wire and connector replacement.
See the [repository issues](https://github.com/simook/r1mx/issues) for current status.

---

## SSD Not Recognised

### Symptom

Camera boots normally but does not detect the REDMAG SSD. The media menu shows no drive,
or the drive shows as "INCOMPATIBLE".

### Cause

At boot, the camera firmware reads the drive's ATA model string and compares it against a
hardcoded approved-drive list embedded in the firmware image. Drives not on the approved
list are rejected.

This affects:
- Replacement drives with different model strings
- SSD upgrades where the original drive has failed

### Diagnosis

1. Confirm the drive is mechanically seated correctly in the iVDR connector
2. Test with a known-good REDMAG if available
3. If the drive is a replacement: check whether the model string matches an approved drive

### Resolution

Options for non-approved replacement drives:
- Source a drive with a matching approved model string (e.g. Toshiba HG3 THNSNC256GBSJ)
- Patch the firmware approved-drive list (research ongoing in the r1mx project)

Full research is documented in
[ssd_drive/README.md](https://github.com/simook/r1mx/blob/main/ssd_drive/README.md).

---

## Firmware Upgrade Fails

### Symptom

Camera does not detect the firmware on the CF card, or upgrade fails partway through.

### Common Causes and Fixes

| Cause | Fix |
|---|---|
| CF card formatted by wrong build | Format the CF card using the camera before copying upgrade files |
| `upgrade/` folder renamed | Folder must be named exactly `upgrade` (lowercase) |
| `redone.su` decompressed | Do not extract the file; the camera handles decompression |
| CF card not ejected properly from computer | Always eject/unmount before removing from card reader |
| Non-speed-verified CF card | Some cards are limited to 2K - use a known-good card |

### Notes

- Mysterium-X cameras **cannot** use firmware prior to Build 30
- Mysterium (original) cameras cannot downgrade below Build 16
- After a failed upgrade, attempt to boot with a previously working build on CF

---

## Color Errors After Firmware Update

### Symptom

After upgrading or downgrading firmware, footage has significant color casts,
incorrect exposure, or unusual color artifacts.

### Cause

Each firmware build uses calibration data from the Black Shading process. After
any firmware change, the stored black shade data may not match the new firmware's
expected format or values.

### Resolution

1. Format a fresh CF card using the new firmware
2. Navigate to: **SYSTEM > MAINTENANCE > BLACK SHADE**
3. Run the Black Shading calibration (camera must be on, lens cap on, stable temperature)
4. Power cycle the camera after Black Shading completes
5. Verify color on a test recording

<div class="callout callout--warn">
  Black Shading must be performed after <strong>every</strong> firmware upgrade or downgrade.
  This is mandatory, not optional.
</div>

---

## Camera Will Not Boot

### Symptom

Camera does not complete the boot sequence. Rear status display shows an error,
is blank, or shows partial text. RED-EVF or RED-LCD may show no signal.

### Initial Checks

1. **Battery charge:** Confirm battery (RED BRICK or AC adaptor) is fully charged and
   seated correctly. The camera requires significant power to boot.
2. **Battery contacts:** Inspect V-Mount contacts for corrosion or damage.
3. **Firmware corruption:** If the camera was interrupted during a firmware upgrade,
   the firmware may be corrupt. Attempt a fresh upgrade from CF.

### Power Sequence

The RED ONE MX has a specific power-on sequence. If the camera partially boots and then
stops, note the exact state of the rear status display and any EVF/LCD output - these
messages are diagnostic.

### Next Steps

If the above checks do not resolve the issue, the fault likely lies in the POWER board
or a board-level component. The r1mx project is actively researching the POWER board.
Contribute your findings at [github.com/simook/r1mx](https://github.com/simook/r1mx).

---

## Contributing Repair Knowledge

This troubleshooting guide is built from community findings. If you have:

- Diagnosed a failure not documented here
- Successfully repaired a RED ONE MX
- Identified component part numbers that are missing

Please contribute to the [r1mx repository](https://github.com/simook/r1mx) by opening
an issue or pull request. Every repair documented here helps the next owner.
