---
layout: guide
title: "SWF GUI Feature Reference"
subtitle: "Complete menu tree and feature reference for the RED ONE MX on-camera Flash GUI, derived from decompiled Build 32 ActionScript source."
difficulty: Easy
time: "Reference"
tools:
  - SWF GUI Mock Server (see running guide)
parts: []
category: firmware
status: available
permalink: /guides/swf-gui-reference/
---

## Overview

The RED ONE MX on-camera display is driven by a Flash SWF (ActionScript 2) that runs
inside the VxWorks RTOS. It communicates with the firmware over a raw XMLSocket on TCP
port 49152. All menus, parameter controls, button handling, and monitoring overlays
are implemented in this SWF.

This reference was derived by:
- Decompiling `firmware/reverse/build_32/assets/swf_gui_1.swf` with JPEXS
- Parsing `firmware/tools/factory_defaults.xml` (893 camera parameters)
- Analysing `firmware/reverse/build_32/assets/panels.xml` (full menu definition)
- Reading the decompiled ActionScript managers in `firmware/reverse/build_32/assets/swf_gui_1_as/`

<div class="callout callout--info">
  <strong>Notation:</strong> Parameter names in parentheses (e.g. <code>GUI.PAINT.EXPOSURE.ISO</code>)
  are the internal GPDB (Global Parameter Data Block) identifiers sent over the XMLSocket
  protocol. They can be used directly with the mock server or the camera's TCP interface.
</div>

---

## Boot Sequence

When the SWF connects to the camera, it goes through a fixed handshake before the GUI
becomes interactive:

| Stage | Event | Description |
|---|---|---|
| 1 | TCP connect | SWF connects to port 49152 |
| 2 | AUTH_SEED | Server sends a random OTP seed |
| 3 | AUTH_PASS | SWF sends OTP-encrypted MD5 password hash |
| 4 | GET_FILE | Server delivers `factory_defaults.xml` — all 893 param definitions |
| 5 | GET_PARAM * | Server delivers current values for all params |
| 6 | SYNC_EVENT_0/1/2 | Three synchronisation events trigger `GoSplash()` then `GoCamera()` |
| 7 | panels.xml | SWF fetches the menu definition via HTTP |
| 8 | GUI_STATE_5_READY | Full interactive state; all menus and button injection active |

The authentication supports two roles: **admin** (password hash `1b772ea5a3dc1e140c4240b335b1d8b8`)
and a lower-privilege **user** role.

---

## Hardware Button Mapping

The camera body exposes dedicated buttons that the firmware reports to the SWF as GPDB
boolean events. Each button fires its parameter to `"true"` on press.

### Fixed-function Buttons

| Button | Parameter | Action |
|---|---|---|
| RECORD | `GUI.RAWINPUT.BUTTON.RECORD` | Start/stop recording (or burst in BURST mode) |
| SENSOR | `GUI.RAWINPUT.BUTTON.MENU.SENSOR` | Open SENSOR menu |
| VIDEO | `GUI.RAWINPUT.BUTTON.MENU.VIDEO` | Open AV (audio/video) menu |
| SYSTEM | `GUI.RAWINPUT.BUTTON.MENU.SYSTEM` | Open SYSTEM menu (disabled while recording) |
| SYSTEM (hold) | `GUI.RAWINPUT.BUTTON.MENU.SYSTEM_LONG` | Long-press system (unimplemented in Build 32) |
| Supergrip REC | `SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.REC` | Same as RECORD button |

### User-Assignable Menu Buttons

User buttons A, B, and C jump to a stored menu panel on **press** and assign the
current panel on **hold** (via SET_A/B/C):

| Button | Parameter (press) | Parameter (hold/set) | Stored in |
|---|---|---|---|
| USER A | `GUI.RAWINPUT.BUTTON.USER_DEFINED.A` | `GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_A` | `GUI.KEYMAP.USER_A.MENU` |
| USER B | `GUI.RAWINPUT.BUTTON.USER_DEFINED.B` | `GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_B` | `GUI.KEYMAP.USER_B.MENU` |
| USER C | `GUI.RAWINPUT.BUTTON.USER_DEFINED.C` | `GUI.RAWINPUT.BUTTON.USER_DEFINED.SET_C` | `GUI.KEYMAP.USER_C.MENU` |

### Mappable Buttons (USER KEYS menu)

These buttons execute a configurable `KEYFNC_*` function. Each has an enable checkbox
and a function selector in **SETUP > PREFERENCES > KEYMAP > USER KEYS**.

| Button label | Parameter | Keymap param |
|---|---|---|
| USER-1 / Side D | `GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.D` | `GUI.KEYMAP.USER_D.*` |
| USER-2 / Side E | `GUI.RAWINPUT.BUTTON.SIDE.USER_DEFINED.E` | `GUI.KEYMAP.USER_E.*` |
| USER-3 / EVF B | `SYSTEM.DEV.EVF.RAWINPUT.BUTTON.B` | `GUI.KEYMAP.EVF_B.*` |
| USER-4 / EVF C | `SYSTEM.DEV.EVF.RAWINPUT.BUTTON.C` | `GUI.KEYMAP.EVF_C.*` |
| USER-5 / LCD SW1 | `SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1` | `GUI.KEYMAP.LCD_A.*` |
| Side Record | `GUI.RAWINPUT.BUTTON.SIDE.RECORD` | `GUI.KEYMAP.SIDE_RECORD.*` |

### Assignable Key Functions (KEYFNC_*)

| Function | Description |
|---|---|
| `KEYFNC_RECORD` | Start/stop recording (respects SIDE_RECORD.ENABLED) |
| `KEYFNC_TOGGLE_RECORD` | Toggle recording |
| `KEYFNC_UNMOUNT_MEDIA` | Unmount active storage |
| `KEYFNC_GOTO_MENU_A/B/C` | Jump to user-saved menu A, B, or C |
| `KEYFNC_DO_AUTO_WHITE_BALANCE` | Trigger auto white balance |
| `KEYFNC_DO_RAMP` | Trigger varispeed ramp |
| `KEYFNC_DO_BURST` | Trigger burst record |
| `KEYFNC_TOGGLE_MAGNIFICATION` | Toggle 1:1 pixel magnification |
| `KEYFNC_TOGGLE_COLOR` | Toggle false colour overlay |
| `KEYFNC_TOGGLE_METER` | Toggle assist exposure meter |
| `KEYFNC_TOGGLE_VIEW_RAW` | Toggle Raw / REDcolor monitor view |
| `KEYFNC_TOGGLE_ZEBRA_1/2` | Toggle zebra 1 or 2 overlay |
| `KEYFNC_INC/DEC_ISO` | Step ISO up or down (wraps) |
| `KEYFNC_INC/DEC_SHUTTER_SPEED` | Step shutter speed up or down (wraps) |
| `KEYFNC_INC/DEC_AUDIO_1/2` | Adjust Ch1 or Ch2 audio gain |
| `KEYFNC_MULTI` | Cycle multi-function key state 0→1→2→3→0 |
| `KEYFNC_DISABLED` | No-op |

### Combo Keys

Held button combinations trigger system actions:

| Combo parameter | Action |
|---|---|
| `GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD` | Trigger pre-record |
| `GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM` | Return to previous menu |
| `GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT` | Unmount active media |
| `GUI.RAWINPUT.BUTTON.COMBOKEY.USER_G` | Toggle preview output: HD-SDI ↔ HDMI |
| `GUI.RAWINPUT.BUTTON.COMBOKEY.USER_F` | Toggle LCD 5:4 scaling |
| `GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H` | Open Engineering (developer) menu |

---

## Menu Tree

The GUI presents three top-level menus accessed by physical buttons:

```
SENSOR button ──→ Panel_Sensor
                     ├─ SENSITIVITY → Panel_Sensitivity
                     ├─ COLOR TEMP  → Panel_WhiteBalance
                     ├─ SHUTTER     → Panel_Shutter
                     ├─ VARISPEED   → Panel_VariSpeed
                     └─ TIME LAPSE  → Panel_TimeLapse

VIDEO button ───→ Panel_AV
                     ├─ VIEW        (color mode selector)
                     ├─ VIDEO       → Panel_Video
                     │    ├─ LOOK   → Panel_Look
                     │    ├─ COLOR  → Panel_Color
                     │    ├─ GAIN   → Panel_VideoGain
                     │    ├─ TONE   → Panel_UserTone
                     │    └─ FLUT   (inline selector)
                     ├─ VIEWFINDER  → Panel_Viewfinder
                     │    ├─ FALSE COLOR
                     │    ├─ METERS → Panel_Meters
                     │    ├─ ZEBRAS → Panel_Zebras
                     │    ├─ INTENSITY
                     │    └─ OPEN GATE
                     ├─ AUDIO       → Panel_Audio (ch1-4 levels)
                     └─ HEADPHONE   → Panel_Headphone

SYSTEM button ──→ Panel_System
                     ├─ SOUND       → Panel_Audio_Setup
                     │    ├─ REC ENABLE → Panel_Rec_Enable
                     │    ├─ OUTPUT LEVEL
                     │    └─ 48V MIC → Panel_Rec_48V
                     ├─ MEDIA       → Panel_Magazine
                     ├─ PROJECT     → Panel_Project
                     │    ├─ STATUS
                     │    ├─ SLATE
                     │    ├─ CONFIGURE → Panel_New_Project
                     │    ├─ TIMECODE  → Panel_Proj_Timecode
                     │    └─ QT PROXIES
                     ├─ MONITOR     → Panel_Monitoring
                     │    ├─ FRAME GUIDE → Panel_Frame_Guide
                     │    ├─ PREVIEW (output selector)
                     │    ├─ TEST SIGNAL
                     │    ├─ PVW REFRESH
                     │    └─ EVF REFRESH
                     └─ SETUP       → Panel_Setup
                          ├─ PREFERENCES → Panel_Preferences
                          │    ├─ USER PROFILE
                          │    ├─ KEYMAP → Panel_Keymap
                          │    ├─ GPIO   → Panel_GPIO
                          │    ├─ PLAYBACK
                          │    └─ DISPLAY
                          ├─ MAINTENANCE → Panel_Maintenance
                          │    ├─ FAN
                          │    ├─ BLK SHADING
                          │    ├─ RESTORE (look/user/system)
                          │    ├─ UPDATE SW
                          │    └─ WRITE LOG
                          ├─ SET CLOCK
                          ├─ REMOTE
                          └─ PROGRAM
```

---

## SENSOR Menu

### Sensitivity (`Panel_Sensitivity`)

| Control | Type | Parameter | Notes |
|---|---|---|---|
| ISO RATING | Selector (prefix: ISO) | `GUI.PAINT.EXPOSURE.ISO` | Continuous update |

### Color Temperature (`Panel_WhiteBalance`)

| Control | Type | Parameter / Action | Notes |
|---|---|---|---|
| AUTO WB | Button | Dispatch `WHITE_BALANCE` | Triggers firmware auto WB |
| TUNGSTEN | Button | Dispatch `WHITE_BALANCE` | Preset WB |
| DAYLIGHT | Button | Dispatch `WHITE_BALANCE` | Preset WB |
| MANUAL WB | Selector (suffix: °K) | `PAINT.WHITE_BALANCE.CURRENT` | Continuous update |
| TRIM | Button | → Panel_Trim | Slave/tint fine-tuning |

**Trim panel** (`Panel_Trim`) — used for multi-camera slave offset:

| Control | Parameter |
|---|---|
| TINT | `PAINT.TINT.CURRENT` |
| S TINT | `PAINT.SLAVE.TINT.CURRENT` |
| S WBAL | `PAINT.SLAVE.WHITE_BALANCE.CURRENT` |
| S FLUT | `GUI.PAINT.SLAVE.SHADOWFLUT` |

### Shutter (`Panel_Shutter`)

| Control | Type | Parameter |
|---|---|---|
| GENLOCK | Checkbox | `SYSTEM.DEV.GENLOCK.REQUESTED` |
| MODE | Selector | `VIDEO.RECORD.SHUTTER_SPEED.MODE` |
| SPEED | Selector | `GUI.RECORD.SHUTTER_SPEED` |
| SYNCRO | Selector | `VIDEO.RECORD.SHUTTER_SPEED.SYNC_ADJUST` |
| PHASE | Selector (suffix: °) | `VIDEO.RECORD.SHUTTER_PHASE.DEGREES` |

Shutter speed display format (1/SEC or degrees) is controlled by `GUI.USER_PREF.SHUTTER_SPEED_FORMAT`.
When set to degrees, `GUI.RECORD.SHUTTER_SPEED_DEG` is used instead.

### Varispeed (`Panel_VariSpeed`)

| Control | Type | Parameter |
|---|---|---|
| VARISPEED | Checkbox | `VIDEO.RECORD.VARISPEED.ENABLED` |
| RAMP | Checkbox | `VIDEO.RECORD.VARISPEED.RAMP.ENABLED` |
| RAMP TRIGGER | Selector | `VIDEO.RECORD.VARISPEED.RAMP.TRIGGER` |
| FRAMERATE | Selector (suffix: fps) | `GUI.RECORD.VARISPEED.FRAME_RATE` |
| TIME | Selector (suffix: sec) | `VIDEO.RECORD.VARISPEED.RAMP.RAMP_1.DURATION` |
| END RATE | Selector (suffix: fps) | `GUI.RECORD.VARISPEED.RAMP.END_FRAME_RATE` |

Varispeed ramp can be triggered by a mappable button (`KEYFNC_DO_RAMP`) or a GPIO input.

### Timelapse (`Panel_TimeLapse`)

| Control | Type | Parameter |
|---|---|---|
| ENABLE | Checkbox | `GUI.RECORD.TIMELAPSE.ENABLED` |
| TRIGGER MODE | Selector | `GUI.RECORD.TIMELAPSE.TRIGGER_MODE` |
| SPEED | Selector (suffix: sec) | `GUI.RECORD.TIMELAPSE.SHUTTER_SPEED` |
| STEP PRINT | Selector (suffix: frames) | `VIDEO.RECORD.TIMELAPSE.BURST_SIZE` |
| INTERVAL | Selector (suffix: sec) | `VIDEO.RECORD.TIMELAPSE.INTERVAL` |
| BURST TYPE | Selector | `VIDEO.RECORD.TIMELAPSE.BURST_TYPE` |

---

## AV Menu (Video/Audio)

### Monitor View (`Panel_AV` — inline)

| Control | Parameter | Notes |
|---|---|---|
| VIEW (color mode) | `GUI.MONITOR.VIEW_MODE` | Raw, REDcolor, etc. Mirrored to `VIDEO.MONITOR.VIEW_MODE` |

### Video Look (`Panel_Look`)

| Control | Action / Parameter |
|---|---|
| CLEAR | Dispatch `CLEAR_LOOK_DOIT` |
| IMPORT | File selector — `GUI.PROFILE.IMPORT_PATHNAME.LOOK` (items from `SYSTEM.PROFILE.FILE_LIST.LOOK`) |
| EXPORT | Dispatch `EXPORT_LOOK_PROFILE` |

Look profiles are `.RLK` files imported from REDCINE-X.

### Color (`Panel_Color`)

| Control | Parameter |
|---|---|
| SATURATION | `GUI.PAINT.SATURATION` |
| EXPOSURE | `GUI.PAINT.EXPOSURE.COMPENSATION` |
| BRIGHTNESS | `GUI.PAINT.BRIGHTNESS` |
| CONTRAST | `GUI.PAINT.CONTRAST` |
| SHADOW | `GUI.PAINT.SHADOWFLUT` |

### Gain (`Panel_VideoGain`)

| Control | Parameter |
|---|---|
| RED GAIN | `GUI.PAINT.GAIN.RED_VALUE` |
| GREEN GAIN | `GUI.PAINT.GAIN.GREEN_VALUE` |
| BLUE GAIN | `GUI.PAINT.GAIN.BLUE_VALUE` |

### Tone (`Panel_UserTone`)

Custom per-point tonal response curve:

| Control | Parameter |
|---|---|
| CURVE (enable) | `GUI.PAINT.TONE.APPLY_CUSTOM` |
| CURVE POINT | `GUI.SOFTKEY.TONAL_RESPONSE.POINT` |
| TOE X | `GUI.SOFTKEY.TONAL_RESPONSE.X` |
| TOE Y | `GUI.SOFTKEY.TONAL_RESPONSE.Y` |

### FLUT (Shadow Rolloff)

| Control | Parameter |
|---|---|
| FLUT | `GUI.PAINT.EXPOSURE.FLUT` |

FLUT (Film Log Unified Transform) adjusts shadow rolloff in the REDCOLOR colour science pipeline.

### Viewfinder (`Panel_Viewfinder`)

| Control | Type | Parameter |
|---|---|---|
| FALSE COLOR | Checkbox | `GUI.MONITOR.OUTPUT_EFFECTS.ENABLED` |
| FALSE COLOR mode | Selector | `GUI.MONITOR.OUTPUT_EFFECTS.MODE` |
| INTENSITY | Selector | `SYSTEM.DEV.EVF.CONTRAST_VALUE` |
| OPEN GATE | Checkbox | `SYSTEM.DEV.EVF.OPEN_GATE_ENABLED` |

**Analysis Meters** (`Panel_Meters`):

| Control | Parameter |
|---|---|
| METER (HUD meter) | `GUI.SOFTKEY.IMAGE_ANALYSIS.HUD_METER` |
| ASSISTS (enable) | `GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED` |
| ASSIST METER type | `GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER` |

**Zebras** (`Panel_Zebras`): Two independent zebra overlays, each independently enabled.

| Control | Parameter |
|---|---|
| ZEBRA 1 enable | `SYSTEM.DEV.EVF.ZEBRA.1_ENABLE` |
| ZEBRA 1 lo IRE | `SYSTEM.DEV.EVF.ZEBRA.1_LOWER_IRE` |
| ZEBRA 1 hi IRE | `SYSTEM.DEV.EVF.ZEBRA.1_UPPER_IRE` |
| ZEBRA 2 enable | `SYSTEM.DEV.EVF.ZEBRA.2_ENABLE` |
| ZEBRA 2 lo IRE | `SYSTEM.DEV.EVF.ZEBRA.2_LOWER_IRE` |
| ZEBRA 2 hi IRE | `SYSTEM.DEV.EVF.ZEBRA.2_UPPER_IRE` |

Zebra 1 and 2 can each be toggled by mappable buttons (`KEYFNC_TOGGLE_ZEBRA_1/2`).

### Audio Input Levels (`Panel_Audio`)

Four independent input channels. Each channel has separate microphone and line gain:

| Control | Parameter (Ch N) |
|---|---|
| MICROPHONE gain (dB) | `AUDIO.INPUT.CHANNEL_N.GAIN.MICROPHONE` |
| LINE gain (dB) | `AUDIO.INPUT.CHANNEL_N.GAIN.LINE` |

### Headphone (`Panel_Headphone`)

| Control | Parameter |
|---|---|
| VOLUME (master) | `AUDIO.HEADPHONE.MASTER` |
| VOLUME LEFT | `AUDIO.HEADPHONE.VOLUME_LEFT` |
| VOLUME RIGHT | `AUDIO.HEADPHONE.VOLUME_RIGHT` |
| OUTPUT MIX | `AUDIO.HEADPHONE.MIX` |

---

## SYSTEM Menu

### Sound Setup (`Panel_Audio_Setup`)

| Control | Notes |
|---|---|
| REC ENABLE | Per-channel enable + input source selection |
| OUTPUT LEVEL | Headphone volume master (`AUDIO.HEADPHONE.VOLUME_MASTER`) |
| 48V MIC | Per-channel phantom power enable |

**Rec Enable** (`Panel_Rec_Enable`): Four channels, each with:

| Control | Parameter |
|---|---|
| CHANNEL N enable | `AUDIO.INPUT.CHANNEL_N.ENABLE` |
| INPUT TYPE | `AUDIO.INPUT.CHANNEL_N.SOURCE` |

**48V Phantom** (`Panel_Rec_48V`): Per channel — `AUDIO.INPUT.CHANNEL_N.PHANTOM48V_ENABLE`

### Media / Magazine (`Panel_Magazine`)

| Control | Action / Parameter | Notes |
|---|---|---|
| PRE-RECORD | `GUI.RECORD.PRERECORD.ENABLED` | Enable pre-record buffer |
| DURATION | `GUI.RECORD.PRERECORD.DURATION` (sec) | Buffer length |
| UNMOUNT | Dispatch `UNMOUNT_DIGMAG` | Safe-eject storage |
| FORMAT | Dispatch `FORMAT_DIGMAG` | Format active drive (prompts if clips present) |
| CHANGE | → Panel_Magazine_New | Format with a new reel number |
| RESET | → Panel_Magazine_Reset | Format and reset reel counter |

**Media states** tracked by firmware: `NOTPRESENT`, `UNCONFIGURED`, `MOUNTED`, `NOTMOUNTED`, `UNMOUNTED`, `EXPORTED`, `INCOMPATIBLE`.

### Project (`Panel_Project`)

#### Project Status (`Panel_Status`)

| Control | Action | Notes |
|---|---|---|
| VIEW | Dispatch `VIEW_STATUS` | Display current project/camera status |
| SAVE | Dispatch `EXPORT_PROJECT_PROFILE` | Save project config to media |
| RECALL | File selector | `GUI.PROFILE.IMPORT_PATHNAME.PROJECT` from `SYSTEM.PROFILE.FILE_LIST.PROJECT` |

#### Slate (`Panel_Slate`)

| Control | Parameter |
|---|---|
| CAMERA (ID) | `PROJECT.SLATE.CAMERA` |

#### Configure (`Panel_New_Project`)

| Control | Parameter |
|---|---|
| RESOLUTION | `PROJECT.MODE_MATRIX.RESOLUTION` |
| TIME BASE | `GUI.SOFTKEY.MODE_MATRIX.FRAME_RATE` |
| QUALITY | `PROJECT.MODE_MATRIX.QUALITY` |
| VALID SETTINGS (flag) | `MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE` |

Resolutions available include 4.5K WS, 4K 2:1, 4K ANA, 4K HD, 3K, 2K (Mysterium-X). Quality options include REDCODE 28, 36, 42. Not all combinations are valid — the GUI shows a VALID SETTINGS indicator.

#### Timecode (`Panel_Proj_Timecode`)

| Control | Type | Parameter |
|---|---|---|
| JAM SYNC | Checkbox | `SYSTEM.DEV.TIMECODE.JAMSYNC.REQUESTED` |
| OUTPUT | Checkbox | `SYSTEM.DEV.TIMECODE.OUTPUT.ENABLED` |
| CROSS | Checkbox | `SYSTEM.DEV.TIMECODE.CROSS.ENABLED` |
| CROSS MODE | Selector | `SYSTEM.DEV.TIMECODE.CROSS.MODE` |
| DISPLAY FORMAT | Selector | `GUI.USER_PREF.TIMECODE_FORMAT` |
| TIMEZONE | Checkbox | `GUI.SYSTEM_DATE.MODIFY_GMT_OFFSET` |
| GMT OFFSET | Selector (suffix: hours) | `GUI.SYSTEM_DATE.GMT_OFFSET` |

### Monitor (`Panel_Monitoring`)

| Control | Type | Parameter |
|---|---|---|
| FRAME GUIDE | Button | → Panel_Frame_Guide |
| PREVIEW output | Selector | `GUI.MONITOR.ACTIVE_DISPLAY` (HD-SDI / HDMI) |
| TEST SIGNAL | Checkbox | `VIDEO.MONITOR.TEST_PATTERN.ENABLED` |
| TEST SIGNAL name | Selector | `VIDEO.MONITOR.TEST_PATTERN.NAME` |
| PVW REFRESH | Selector | `VIDEO.MONITOR.FRAME_RATE` |
| EVF REFRESH | Selector | `SYSTEM.DEV.EVF.REFRESH_MODE` (SYNCED / FIXED) |

**Frame Guide** (`Panel_Frame_Guide`):

| Control | Parameter |
|---|---|
| FRAME GUIDE aspect | `GUI.OSD.RETICLE.FRAME_GUIDE.ASPECT` |
| FRAME GUIDE enable | `GUI.OSD.RETICLE.FRAME_GUIDE.ENABLE` |
| FRAME GUIDE color | `GUI.OSD.RETICLE.FRAME_GUIDE.COLOR` |
| SAFETY aspect | `GUI.OSD.RETICLE.TV_SAFE_AREA.ASPECT` |
| SAFETY enable | `GUI.OSD.RETICLE.TV_SAFE_AREA.ENABLE` |
| SAFETY color | `GUI.OSD.RETICLE.TV_SAFE_AREA.COLOR` |

**Custom reticle** (`Panel_Customize`):

| Control | Parameter / Action |
|---|---|
| LOOK AROUND opacity (%) | `GUI.USER_PREF.LOOKAROUND.ALPHA` |
| CURSORS → Panel_CustomizeCursors | Center, action-safe, title-safe cursors with style |
| USER ACTION | Dispatch `CUSTOM_RETICLE_ACTION` |
| USER TITLE | Dispatch `CUSTOM_RETICLE_TITLE` |

**Video Output enables** (`Panel_VideoOutput`):

| Control | Parameter |
|---|---|
| EVF | `SYSTEM.DEV.EVF.ENABLED` |
| LCD | `SYSTEM.DEV.LCD.ENABLED` |
| HD PREVIEW (HDMI) | `SYSTEM.DEV.MONITOR_HDMI.ENABLED` |
| HD-SDI | `SYSTEM.DEV.HDSDI.ENABLED` |

### Setup (`Panel_Setup`)

#### Preferences (`Panel_Preferences`)

**User Profile** (`Panel_User`):

| Control | Action |
|---|---|
| CLEAR | Dispatch `RESTORE_USER_DOIT` |
| IMPORT | File selector: `GUI.PROFILE.IMPORT_PATHNAME.USER` |
| EXPORT | Dispatch `EXPORT_USER_PROFILE` |

**Keymap** (`Panel_Keymap`):

| Control | Parameter |
|---|---|
| SIDE RECORD | `GUI.KEYMAP.SIDE_RECORD.ENABLED` |
| USER KEYS | → Panel_UserKeys |

User keys 1–5 each have an enable checkbox and a function selector (KEYFNC_* above).

**GPIO** (`Panel_GPIO`):

| Control | Parameter |
|---|---|
| INPUT A enable | `SYSTEM.DEV.GPIO.CONFIG.INPUT_1.ENABLED` |
| INPUT A function | `SYSTEM.DEV.GPIO.CONFIG.INPUT_1.MAPPED_FUNCTION` |
| INPUT B enable | `SYSTEM.DEV.GPIO.CONFIG.INPUT_2.ENABLED` |
| INPUT B function | `SYSTEM.DEV.GPIO.CONFIG.INPUT_2.MAPPED_FUNCTION` |
| OUTPUT A trigger | `SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER` |
| OUTPUT B trigger | `SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER` |
| Input/Output polarity | `SYSTEM.DEV.GPIO.CONFIG.INPUT/OUTPUT_N.POLARITY` |

GPIO inputs can be mapped to the same `KEYFNC_*` functions as user buttons.
GPIO outputs trigger on camera events (record state, etc.).

**Playback** (`Panel_Playback`):

| Control | Parameter |
|---|---|
| HD-SDI resolution | `VIDEO.PLAYBACK.CONFIG.DISPLAY_MODE` |
| LOOK (use settings) | `VIDEO.PLAYBACK.CONFIG.LOOK` |

**Display** (`Panel_Display`):

| Control | Parameter | Notes |
|---|---|---|
| STATUS (upper HUD) | `GUI.OSD.SHOW.UPPER_HUD` | Toggle status bar visibility |
| Shutter format | `GUI.USER_PREF.SHUTTER_SPEED_FORMAT` | 1/SEC or DEGREES |
| LENS DATA | `GUI.OSD.SHOW.LENS_DATA` | Toggle lens info overlay |
| Lens units | `GUI.USER_PREF.LENS_UNITS` | |
| EVF MENU | `GUI.OSD.SHOW.EVF_FUNCTION_LADDER` | EVF button menu display |
| METERS (lower HUD) | `GUI.OSD.SHOW.LOWER_HUD` | Toggle meter bar |
| GREY SCALE | `GUI.OSD.SHOW.GREYRAMP_CHART` | Toggle grey ramp overlay |

#### Maintenance (`Panel_Maintenance`)

| Control | Action / Notes |
|---|---|
| FAN | Fan mode selector: `SYSTEM.THERMAL.FAN.CONTROL.MODE` |
| BLK SHADING | START: `USERCAL_START` / RESTORE: `USERCAL_RESTORE` |
| RESTORE LOOK | Dispatch `RESTORE_LOOK_DOIT` |
| RESTORE USER | Dispatch `RESTORE_USER_DOIT` |
| RESTORE SYSTEM | Dispatch `RESTORE_SYSTEM_DOIT` |
| UPDATE SW | Dispatch `UPGRADE_SOFTWARE` (reads upgrade from CF card) |
| WRITE LOG | Dispatch `FLUSH_LOG` (writes debug log to media) |

#### Set Clock (`Panel_DateTime`)

Date and time are set field-by-field. Each field has a modify-enable checkbox and
a value selector. After setting all fields, dispatch `SET_CLOCK` to commit.

Fields: YEAR, MONTH, DAY, HOUR, MINUTE, SECOND (all in GMT).

#### Remote (`Panel_Remote`)

| Control | Parameter |
|---|---|
| REMOTE PORT | `GUI.SOFTKEY.S4I_LENS_PORT_ACTIVE` (Cooke S4/i lens port) |
| LENS PORT | `GUI.SOFTKEY.LENS_PORT_ACTIVE` |

#### Program (`Panel_Program`)

Broadcast/production program output settings:

| Control | Parameter |
|---|---|
| POSITION (camera) | `GUI.PROGRAM.POSITION` |
| HD-SDI range | `GUI.PROGRAM.HDSDI` |
| VIDEO mode | `GUI.PROGRAM.VIDEO` |
| FEED | `GUI.PROGRAM.FEED` |
| TALLY | `GUI.PROGRAM.TALLY` |

---

## Engineering (Developer) Menu

The Engineering menu (`Panel_Developer`) requires the `EMENU` capability bit to be set
in the camera's OTP/capability register. It is accessed by the combo key
`GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H` (normally SYSTEM + RECORD held simultaneously).

<div class="callout callout--warn">
  <strong>Warning:</strong> Engineering menu parameters are not part of the normal user
  workflow. Incorrect values can affect sensor calibration and image quality. These are
  documented here for completeness from the decompiled source.
</div>

### Calibrate (`Panel_Calibrate`)

| Control | Action |
|---|---|
| GRAB LIGHT | `CALIBRATE_CAPTURE_LIGHT` — capture light frame for factory calibration |
| GRAB LIGHT F24 | `CALIBRATE_CAPTURE_LIGHT_F24` — light frame at F24 |
| GRAB DARK | `CALIBRATE_CAPTURE_DARK` — capture dark frame |
| APPLY CAL | `CALIBRATE_APPLY` — apply captured calibration data |
| CAL PRESENT | Checkbox (read-only): `CALIBRATE.FACTORY.FILE_AVAILABLE` |

### Sensor (`Panel_EngSensor`)

| Control | Parameter | Notes |
|---|---|---|
| MAGNIFY | → Panel_EngMagnify | 1:1 magnification position (X/Y) |
| BLK LOOP | `DEBUG.BLACKLOOP.ACTIVE` | Loop black frame output |
| CAL CAPTURE | `GUI.CALIBRATE.CAPTURE_FRAMECOUNT` | Frames to capture |
| S35 | → Panel_EngS35 | EPIC/S35 sensor debug |
| R1 | → Panel_EngR1 | RED ONE sensor debug |

**S35 debug** (`Panel_EngS35`):

| Control | Parameter |
|---|---|
| SSD ENABLE | `EPIC.DEBUG.SUNSPOT.ENABLE` |
| VREF_CLAMP (voltage) | `EPIC.DEBUG.SUNSPOT.VREFCLAMP` |
| VLN ENABLE | `EPIC.DEBUG.VLN.ENABLE` |
| VCL ENABLE | `EPIC.DEBUG.VCL.ENABLE` |

**R1 debug** (`Panel_EngR1`):

| Control | Parameter |
|---|---|
| SSD ENABLE | `REDONE.DEBUG.SUNSPOT.ENABLE` |
| VTXMID (voltage) | `REDONE.DEBUG.SUNSPOT.VTXMIDDAC` |

### Compression (`Panel_EngCompression`)

REDCODE compression bias adjustments:

| Control | Parameter |
|---|---|
| GRN BIAS | `DEBUG.COMPRESSION.RC.GREEN.BIAS` |
| RED BIAS | `DEBUG.COMPRESSION.RC.RED.BIAS` |
| BLUE BIAS | `DEBUG.COMPRESSION.RC.BLUE.BIAS` |
| PREEMPH | `DEBUG.IMGPROC.PREEMPH` |

### HDR (`Panel_HDR`)

| Control | Parameter |
|---|---|
| HDR ENABLE | `DEBUG.HDR.ENABLE` |
| NUM STEPS | `DEBUG.HDR.NUM_STEPS` |
| NUM STOPS (range) | `DEBUG.HDR.NUM_STOPS` |

### Patterns (`Panel_Patterns`)

Debug test patterns for monitor and playback:

| Control | Parameter |
|---|---|
| MON TEST enable | `DEBUG.MON_PATTERN.ENABLED` |
| MON TEST name | `DEBUG.MON_PATTERN.NAME` |
| PB TEST enable | `DEBUG.PB_PATTERN.ENABLED` |
| PB TEST name | `DEBUG.PB_PATTERN.NAME` |

---

## On-Screen Display (HUD) Widgets

The upper and lower HUD bars are composed of data widgets. These are visible when
`GUI.OSD.SHOW.UPPER_HUD` / `GUI.OSD.SHOW.LOWER_HUD` are enabled.

| Widget | Parameter(s) displayed |
|---|---|
| Record indicator | `VIDEO.RECORD.STATE` |
| Timecode | `VIDEO.RECORD.TC.*` |
| FPS / Time base | `VIDEO.RECORD.FRAME_RATE` |
| Shutter speed | `GUI.RECORD.SHUTTER_SPEED` or degrees |
| ISO (EI) | `GUI.PAINT.EXPOSURE.ISO` |
| F-stop (lens) | Lens data from S4/i or manual |
| Focus (lens) | Lens data from S4/i |
| White balance | `PAINT.WHITE_BALANCE.CURRENT` |
| Media capacity | `MEDIA.DIGMAG.CAPACITY.*` |
| Power (battery) | Power/battery params |
| Temperature | Sensor thermal params |
| Timecode genlock | TC genlock status |
| Volume meter | Audio input levels |
| Variseed (fps) | `VIDEO.RECORD.VARISPEED.*` |
| Timelapse | Timelapse state |
| Digital magnification | Magnify enable/position |
| SD card | External SD card state |
| USB thumb | USB thumb drive state |
| Drop frame | `GUI.USER_PREF.TIMECODE_FORMAT` |

---

## Recording Modes

The camera supports three recording modes set via `VIDEO.RECORD.MODE`:

| Mode | Description |
|---|---|
| `CONTINUOUS` | Normal start/stop recording |
| `TIMELAPSE` | Timelapse with configurable interval and burst size |
| `BURST` | Burst capture triggered by record button or `KEYFNC_DO_BURST` |

Pre-record (enabled via `GUI.RECORD.PRERECORD.ENABLED`) maintains a rolling buffer
so the camera effectively records a few seconds before the record button is pressed.

---

## See Also

- [Running the SWF GUI Mock Server]({{ '/guides/swf-gui-mock-server' | relative_url }}) — how to run this GUI on a PC
- [Black Shading Calibration]({{ '/guides/black-shading-calibration' | relative_url }}) — calibration guide (real camera)
- [Firmware History]({{ '/firmware' | relative_url }}) — Build 32 release notes
- `firmware/reverse/build_32/assets/swf_gui_1_as/` — full decompiled ActionScript source
- `firmware/reverse/build_32/assets/panels.xml` — raw menu definition XML
