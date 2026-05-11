RED-ONE Build 32 v32.0.3         September 7, 2013

Note: Download the latest versions of REDCINE-X and RED Rocket installer/drivers from www.red.com/support. 

IMPORTANT:
* After upgrading to Build 32, on-camera playback of media recorded by earlier builds may not be possible, nor can you add additional clips to digital media formatted under an earlier build.
* Mysterium-X sensor based cameras may not use firmware prior to Build 30. 
* Mysterium sensor based cameras may be downgraded, but not to firmware prior to Build 16. 
* Ensure you reformat any digital media and Black Shade before shooting under Build 32. 
* Third party post tools may need to be updated to reflect FLUT and REDcolor color science.

Installation Instructions for RED-ONE Build 32 v32.0.3 camera firmware.

NOTES: 
* This upgrade is fully contained in the folder " build_31_v32.0.3
* In that folder is a copy of this Read Me file and the folder named "upgrade"
* The " upgrade " folder includes the camera firmware upgrade file "redone.su"
* DO NOT rename this folder, the camera only opens a folder named "upgrade" 
* Do NOT decompress the "redone.su" file, the camera will perform that task. 

1. Format a CF card using Build 20, 21, 30 or 31 (Build 20/21 used on Mysterium sensor based camera only)
2. Connect the CF card to your P.C or Macintosh via a CF card reader.
3. Copy the folder called " upgrade " onto the CF card.
4. Unmount the CF card from your computer (drag to the trash can).
5. Ensure your camera is powered down. 
6. Insert the CF card into the CF card slot of your RED-ONE camera.
7. Power up the camera. 
8. After booting up, the camera rear status display will report "New Firmware" and the RED-EVF or RED-LCD will report "A software update is available for your system" 
9. Press the joystick to confirm, and the rear status display will report "Upgrading"
10. During the upgrade process, a blue progress bar will be visible on the RED-EVF or RED-LCD. This bar will continue for the duration of the upgrade, which is approximately five minutes. 
11. At the end of the upgrade process, the rear status display will report "O.K. Cycle Power" The RED-LCD or RED-LCD will report " Upgrade complete. Power cycle the camera to continue. "
12. Power down the camera, wait five seconds, then power up the camera.
13. Verify that the camera rear status display and or monitors report back - PIN (value specific to camera)     Build 32 Version 32.0.3
14. Installation is now complete.

Note: After the firmware upgrade, it is mandatory that you re-format a CF card and perform a BLACK SHADING calibration. At the end of Black Shading remember to power cycle the camera. Operation without performing a BLACK SHADING calibration after firmware updates or downgrades usually creates significant color errors.

Significant changes since Build 31 series firmware.

* Added REDColor2, REDColor3 and REDLogFilm
* Fix ISO setting after MX restore
* Fix HANC metadata RECORD flag
* Fix Bomb EVF intensity range
* Added 512GB support

General operational notes regarding Build 32 series firmware.
* Mysterium-X sensor based camera may not be downgraded to firmware prior to Build 30.
* Mysterium sensor based camera may not be downgraded to firmware prior to Build 16.
* Non Build 31 formatted media may report as "INCOMPATIBLE". If so, reformat to clear.
* Non-speed verified CF cards are limited to 2K record resolution.
* RED 48GB SSD is not compatible with REDONE.
* Image Magnify is available during preview only.
* LOOK (.RLK) file format updated at Build 30, not compatible with Build 21 or earlier. 
* GUI on HD Preview is limited to LOOK AROUND if both EVF and LCD ports are active.
* FLUT parameter remains independent on Slave camera when in Master / Slave mode. 
* Audio parameters remain independent on Slave camera when in Master / Slave mode. 
* Under GPI trigger, Slave camera will enter record within +/- 1 frame of Master.
* Using RECORD key, Slave camera will enter record within +/- 2 frames of Master.
* HD-SDI and HDMI are True Progressive, no support for 1080i or 1080 PsF formats.
* Selecting V Flip or H + V flip VIDEO mode will delay the HD-SDI output by 1 frame. 
* Timecode in GUI is not frame accurate, always reference to HD-SDI or .R3D timecode.
* If using Master / Slave mode, ensure that both Master and Slave cameras are using identical size media and when formatting media, ensure that both the Master and Slave cameras have media attached. 
* RECORD tally in HD-SDI HANC indicates "in record" earlier than the first frame of the recorded .R3D file, and stays enabled a few frames after the last frame of the recorded .R3D file.
* Monitor path outputs may experience a temporary disturbance when:
 - Enabling first / disabling last audio channel
 - Entering and exiting Image Magnify
* RED-EVF in SYNC refresh mode will experience a temporary video blanking when: 
 - exiting OPEN GATE mode
 - exiting MAGNIFY at 4K resolution
 - changing Project RESOLUTION
 - changing Varispeed frame rate
* Bomb-EVF in SYNC refresh mode will experience a temporary video blanking when: 
 - exiting MAGNIFY at 4K resolution
 - changing Project RESOLUTION
 - changing Varispeed frame rate

Copyright (c) 2013 RED Digital Cinema, All Rights Reserved.