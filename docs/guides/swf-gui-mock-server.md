---
layout: guide
title: "Running the SWF GUI Mock Server"
subtitle: "Interactively explore the RED ONE MX on-camera Flash GUI on a modern PC using Ruffle and the bundled mock camera server."
difficulty: Easy
time: "15 minutes"
tools:
  - Python 3.9+
  - Ruffle binary (libraries/ruffle)
  - Firmware reverse assets (firmware/reverse/build_32/assets/)
parts: []
category: firmware
status: available
permalink: /guides/swf-gui-mock-server/
---

## Overview

The RED ONE MX on-camera GUI is a Flash SWF (ActionScript 2 / AVM1) that runs inside
the VxWorks RTOS and communicates with the camera firmware over a raw XMLSocket on TCP
port 49152. The SWF handles all menus, sensor controls, media management, and button
input for the camera's monitor output.

This guide explains how to run the SWF on a modern PC using
[Ruffle](https://ruffle.rs/) (an open-source Flash runtime) and the mock camera server
in this repository. The result is a fully interactive camera GUI that responds to menu
navigation, parameter changes, and button injection — without real camera hardware.

<div class="callout callout--info">
  <strong>Source material:</strong> The SWF and all assets are from Build 32 (v32.0.3),
  the final known production firmware for the RED ONE MX. The ActionScript source was
  recovered by decompiling the SWF using
  <a href="https://github.com/vorpaljs/vorpaljs">JPEXS Free Flash Decompiler</a>.
</div>

---

## How It Works

```
Ruffle (Flash runtime)                    mock_camera_server.py
       │                                         │
       │  TCP connect → port 49152               │
       │─────────────────────────────────────────▶│
       │                                         │
       │  AUTH_SEED (OTP seed)                   │
       │◀─────────────────────────────────────────│
       │                                         │
       │  AUTH_PASS (OTP-encrypted MD5 hash)     │
       │─────────────────────────────────────────▶│
       │                                         │
       │  GET_FILE factory_defaults.xml (893 params)
       │◀─────────────────────────────────────────│
       │                                         │
       │  GET_PARAM * (all param values)         │
       │◀─────────────────────────────────────────│
       │                                         │
       │  SYNC_EVENT_0 / 1 / 2                   │
       │◀─────────────────────────────────────────│
       │                                         │
       │  panels.xml (menu definition, 53 KB)    │
       │◀── HTTP GET :8000/panels.xml ───────────│
       │                                         │
       │  GUI_STATE_5_READY (fully interactive)  │
       │◀─────────────────────────────────────────│
```

The mock server also serves static assets (SWF file, panels.xml, any other files the
SWF loads) over HTTP on a second port so Ruffle can resolve relative URLs.

---

## Prerequisites

<div class="guide-step">
  <div class="guide-step-num">1</div>
  <div class="guide-step-body">
    <strong>Confirm the required files are present.</strong>
    <p>From the repository root:</p>
    <pre><code>ls libraries/ruffle
ls firmware/reverse/build_32/assets/swf_gui_1.swf
ls firmware/reverse/build_32/assets/panels.xml
ls firmware/tools/factory_defaults.xml</code></pre>
    <p>If the Ruffle binary is missing, download it from
    <a href="https://ruffle.rs/#downloads" target="_blank" rel="noopener">ruffle.rs</a>
    and place it at <code>libraries/ruffle</code>. Make it executable:
    <code>chmod +x libraries/ruffle</code></p>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">2</div>
  <div class="guide-step-body">
    <strong>Install Python dependencies.</strong>
    <pre><code>pip install -r requirements.txt</code></pre>
    <p>The mock server only requires Python standard library modules, but the repo
    may have other dependencies. The key module is <code>firmware/tools/mock_camera_server.py</code>.</p>
  </div>
</div>

---

## Starting the GUI

<div class="guide-step">
  <div class="guide-step-num">3</div>
  <div class="guide-step-body">
    <strong>Check for port conflicts.</strong>
    <p>The mock server uses port 8000 (HTTP assets) and 49152 (XMLSocket) by default.
    If port 8000 is occupied (common if <code>chroma</code> or another local service is running),
    use <code>--http-port</code> to choose a free port:</p>
    <pre><code># Check what's using port 8000
lsof -i :8000

# Use a different HTTP port if needed
python3 firmware/tools/swf_gui.py --http-port 8765</code></pre>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">4</div>
  <div class="guide-step-body">
    <strong>Launch the GUI.</strong>
    <pre><code>python3 firmware/tools/swf_gui.py</code></pre>
    <p>This starts the mock server and launches Ruffle with the SWF loaded over HTTP.
    The terminal streams tagged log output from both processes:</p>
    <pre><code>[HH:MM:SS][MOCK  ] Listening on 0.0.0.0:49152 (HTTP on 0.0.0.0:8000)
[HH:MM:SS][swf_gui] Ruffle PID=12345 — enter IP 127.0.0.1, click Camera</code></pre>
  </div>
</div>

<div class="guide-step">
  <div class="guide-step-num">5</div>
  <div class="guide-step-body">
    <strong>Connect through the RemoteConnect dialog.</strong>
    <p>Ruffle opens the splash / connect screen. Enter IP <strong>127.0.0.1</strong>
    and click <strong>Camera</strong>. If Ruffle pre-fills a different IP (e.g.
    <code>10.3.2.1</code>), this is from a stored SharedObject cookie — clear it and
    type <code>127.0.0.1</code>.</p>
    <p>The GUI will boot through the full authentication and initialisation sequence.
    Watch the terminal for boot milestones:</p>
    <pre><code>==================================================================
  >>> AUTH OK — admin session
==================================================================
  >>> BOOT COMPLETE — GoSplash / GoCamera about to run
==================================================================
  >>> GOREADY FIRED — panels.xml parsed, splash clearing
==================================================================
  >>> FULLY READY — button injection enabled
==================================================================</code></pre>
  </div>
</div>

---

## Navigating the GUI

Once the **FULLY READY** milestone appears, the GUI is fully interactive. Use the Ruffle
window to click menu buttons. The complete menu structure is documented in the
[SWF GUI Feature Reference]({{ '/guides/swf-gui-reference' | relative_url }}).

Key buttons you can explore immediately:

| Physical button | Menu opened |
|---|---|
| SENSOR | Sensitivity, color temp, shutter, varispeed, timelapse |
| VIDEO (AV) | View mode, look, color, gain, tone, audio, viewfinder |
| SYSTEM | Sound, media, project, monitor, setup |

---

## Button Injection

The mock server reads button commands from stdin. While the GUI is running, type commands
in the same terminal and press Enter:

| Command | Effect |
|---|---|
| `record` | Toggle recording on/off |
| `sensor` | Open SENSOR menu |
| `video` | Open AV (video/audio) menu |
| `menu` | Open SYSTEM menu |
| `user_a` / `user_b` / `user_c` | Activate user-defined menu button |
| `set_a` / `set_b` / `set_c` | Assign current menu to user button A/B/C |
| `side_record` | Side record button |

Commands are forwarded to the mock server which injects them as camera firmware param
events (`GUI.RAWINPUT.BUTTON.*`).

---

## Verbose and Timeout Modes

```bash
# Extra logging from mock server + Ruffle debug output
python3 firmware/tools/swf_gui.py -v

# Stop automatically after N seconds (for scripted/agentic runs)
python3 firmware/tools/swf_gui.py --timeout 30

# Override specific camera parameters at startup
python3 firmware/tools/swf_gui.py --set VIDEO.RECORD.STATE=RECORDING

# Use original RED ONE (non-MX) sensor splash
python3 firmware/tools/swf_gui.py --sensor-orig
```

---

## Session Summary

When the GUI exits (Ctrl-C, or `--timeout` elapsed), the terminal prints a session
summary showing which boot milestones were reached:

```
[swf_gui] ── Session summary ──
  ✓ AUTH OK — admin session
  ✓ BOOT COMPLETE — GoSplash / GoCamera about to run
  ✓ GOREADY FIRED — panels.xml parsed, splash clearing
  ✓ INIT GUI STATE
  ✓ FULLY READY — button injection enabled
  All milestones reached!
```

A milestone marked **✗** indicates a boot failure. The most common causes are a missing
parameter in `factory_defaults.xml` or a port conflict preventing `panels.xml` from
loading over HTTP.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| GUI shows splash, never clears | panels.xml HTTP GET failed | Check HTTP port is free; use `--http-port 8765` |
| `AUTH FAILED — wrong password` | Password hash mismatch | Verify `ADMIN_MD5` in `mock_camera_server.py` matches `Authenticate.as` |
| Ruffle exits immediately | SWF path or base URL wrong | Check `--swf` and `--assets` defaults |
| `no subscribed clients` logged | Bug in old mock server version | Update to current `mock_camera_server.py` |
| Button commands have no effect | GUI not at FULLY READY | Wait for milestone 5 before injecting buttons |

---

## See Also

- [SWF GUI Feature Reference]({{ '/guides/swf-gui-reference' | relative_url }}) — complete menu tree and parameter reference
- [Black Shading Calibration]({{ '/guides/black-shading-calibration' | relative_url }}) — real camera calibration procedure
- `firmware/tools/mock_camera_server.py` — mock server source
- `firmware/reverse/build_32/src/xmlsocket/` — decompiled XMLSocket protocol code
