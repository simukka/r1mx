# RED ONE Build 32 — Debug Interface Analysis
**Status: Initial findings complete**

---

## Summary

Build 32 has **three distinct live debug surfaces** confirmed by static analysis:
1. **WDB over Ethernet (UDP 17185)** — always-on, no build flag disables it
2. **USB serial shell** — activatable by changing `DEBUG.USB.CONNECTION` param
3. **XUartNs550 UART** — hardware serial, TTY0 assigned to internal (lens/RS-232)

---

## 1. VxWorks WDB Agent (Wind River Debug)

### Status: **ALWAYS-ON** in release builds

**Function: `usrWdbInit` at `0x0036B3DC`**  
Called unconditionally from the main BSP init function at `0x0036B7EC`. No build-time or runtime conditional disables it.

### Transport
- **Protocol:** UDP (Ethernet)
- **Device:** `xemaclite(0,0)` — Xilinx XEmacLite (Ethernet MAC Lite FPGA core)
- **Camera IP:** `192.168.0.2`
- **Host IP:** `192.168.0.1` (default boot config)
- **UDP Port:** `17185` (0x4321) — stored to BSS at `0xE9C4BC`
- **Boot config string:** `xemaclite(0,0)host:vxWorks h=192.168.0.1 e=192.168.0.2 u=xemhost`

### Key Disassembly — `usrWdbInit` (0x36B3DC)
```
0036B3DC:  stwu  r1, -0x20(r1)       ; frame
0036B3E0:  mflr  r0
0036B3E8:  lis   r31, 0x101          ; BSS base 0x1010000
... [parse Ethernet device name from config string] ...
0036B4CC:  li    r0, 0x4321          ; WDB port = 17185
0036B4D4:  addi  r3, r3, -0x3120    ; r3 → WDB comm if struct (BSS)
0036B4DC:  li    r4, 5               ; WDB_COMM_END = 5 (Ethernet END driver)
0036B4E0:  li    r6, 5
0036B4E4:  sth   r0, -0x3b44(r9)    ; store port to 0xE9C4BC (BSS)
0036B4E8:  bl    0x5a153c            ; wdbEndPktDevInit()
0036B4FC:  cmpwi cr7, r3, -1        ; check success
0036B500:  beq   cr7, 0x36b57c      ; on fail → return -1
[success path continues to wdb task init calls]
```

### Caller — BSP Init at `0x36B7EC`
```
0036B7FC:  bl    0x36b3dc            ; usrWdbInit()
0036B800:  cmpwi cr7, r3, -1
... [set up taskSpawn args] ...
0036B824:  beq   cr7, 0x36b8c0      ; if WDB init failed, exit
0036B828:  bl    0x5a2a28            ; spawn WDB task (priority=3, stack=8K)
; followed by many more WDB init calls:
0036B830:  bl    0x59e4b8            ; wdbEvtptLibInit or similar
0036B834:  bl    0x59b140            ; ...
0036B838:  bl    0x59b558
0036B83C:  bl    0x59af48
... [10+ more WDB sub-init calls]
0036B884:  bl    0x36b5c4            ; wdbIsInitialized check / bp install
```

### Exploitation
To connect WindRiver Workbench (or `wdbrpc` client):
1. Connect Ethernet to camera (straight or cross cable; camera is 192.168.0.2)
2. Set host to 192.168.0.1/24
3. Connect WDB target: UDP 192.168.0.2:17185
4. Grants full read/write memory access, task listing, breakpoints, symbol lookup

**Security note:** The WDB protocol has no authentication. Any host on the same subnet can connect.

---

## 2. USB Serial Shell (`UiUsbSerial`)

### Class
- **Source:** `app_modules/ui_usb/uiusbserial.cpp`
- **Symbol string:** `_ZTV11UiUsbSerial` at `0xDCB3BC` (VTable)
- **Symbol strings:** `_ZN11UiUsbSerial14runTargetShellEv`, `_ZN11UiUsbSerial21ProcessUsbDebugChangeER8ParamRef`

### Methods (C++ mangled names → addresses TBD)
| Method | Demangled | Purpose |
|--------|-----------|---------|
| `_ZN11UiUsbSerial14runTargetShellEv` | `runTargetShell()` | Spawns VxWorks shell over USB |
| `_ZN11UiUsbSerial21ProcessUsbDebugChangeER8ParamRef` | `ProcessUsbDebugChange(ParamRef&)` | Callback triggered by param change |
| `_ZN11UiUsbSerial18IsConnectionActiveEv` | `IsConnectionActive()` | Check USB CDC-ACM link state |
| `_ZN11UiUsbSerial12WriteMessageERKSsb` | `WriteMessage(const string&, bool)` | Write to USB serial |
| `_ZN11UiUsbSerial11ReadMessageEPv` | `ReadMessage(void*)` | Read from USB serial |

### Trigger Parameter
```xml
<Param name = "DEBUG.USB.CONNECTION" type = "integer" value = "0"/>
```
- **Default value:** 0 (shell disabled)
- **Changing to non-zero value** triggers `ProcessUsbDebugChange()` → calls `runTargetShell()`
- Changeable via WDB, or via camera's parameter set API over Ethernet

### Hardware: NET2280 USB-to-PCI Bridge
- `usbNET2280Debug` symbol present
- PLX/NetChip NET2280 chip bridges USB device port to PCI bus in FPGA
- Camera appears as USB device (not host) to connected PC
- Likely enumerates as CDC-ACM (virtual COM port) when debug enabled

### How to Enable
Option 1 (via WDB):
```
wdbMemWrite(DEBUG_USB_CONNECTION_ADDR, 1, 4)  ; write 1 to DEBUG.USB.CONNECTION
```
Option 2 (via Ethernet REST/param API if exposed).

**Once enabled:** Connect USB cable, find `/dev/ttyUSB0` (Linux) or COM port (Windows), open at configured baud rate → get VxWorks shell prompt.

---

## 3. UART Hardware (Xilinx FPGA UARTs)

### Two UART Drivers Present

#### XUartLite (Xilinx UART Lite)
- Simple, fixed baud rate (baked into FPGA bitstream)
- Functions: `XUartLite_CfgInitialize`, `XUartLite_Send`, `XUartLite_Recv`, etc.
- Source: `xuartlite.c`, `xuartlite_sio_adapter.c` (BSP driver)
- **Config table:** `XUartLite_ConfigTable` (symbol string at `0xDF7930`) — actual MMIO address in ConfigTable (TBD)

#### XUartNs550 (16550-Compatible UART)
- Programmable baud, data format, FIFO
- Functions: `XUartNs550_SetBaud`, `XUartNs550_SetDataFormat`, `XUartNs550_SetFifoThreshold`, etc.
- Source: `xuartns550.c`, `xuartns550_adapter.c` (BSP driver)
- **Config table:** `XUartNs550_ConfigTable` (symbol string at `0xDF7B3C`)
- More likely to be the external UART (RS-232 or LVTTL serial connector)

### TTY0 Assignment
- Parameter: `SYSTEM.DEV.TTY0.ASSIGNMENT` (default value: `"INTERNAL"`)
- When `"INTERNAL"`: used for internal (lens control?) serial
- Likely accepts `"EXTERNAL"` or `"CONSOLE"` to expose as debug terminal
- The `ttyswitch` driver manages redirecting TTY0 between modes:
  - `ttyswitchInit` / `ttyswitchPresent` / `ttyswitchSetChannel`

### Physical Location
RED ONE camera has a 26-pin "CONTROL" connector that includes RS-232 signals (TX/RX). The XUartNs550 likely maps to this connector. A USB-to-RS232 or direct RS-232 adapter to the CONTROL connector could give serial console access if TTY0 can be redirected.

---

## 4. altshell (`/tffs0/altshell`)

### Mechanism
- Loaded from **TFFS flash filesystem** (`tffs0` = True Flash File System)
- Path: `/tffs0/altshell` — if this file exists on camera flash, it's loaded at boot
- String: `*** Will use alternate shell ***` suggests this replaces the standard shell
- The altshell binary is NOT present in the `roFs` embedded filesystem; it must be written to flash manually

### Access Path
- Could be written to flash via WDB memory write + TFFS file create calls
- No evidence of this being enabled in stock firmware

---

## 5. Telnetd

### Status
- VxWorks telnetd fully compiled in
- Error message: `"telnetd: A shell has not been installed - can't initialize library"`
- Requires shell to be installed first (via `shellInit()` or `usbShell`)
- **DEPENDENT** on USB shell or altshell being enabled first
- Port: standard 23 (telnet)

---

## 6. Network Configuration

### Default VxWorks Boot Config
```
xemaclite(0,0)host:vxWorks h=192.168.0.1 e=192.168.0.2 u=xemhost
```
- **Target (camera):** `192.168.0.2`
- **Host:** `192.168.0.1`
- **Device:** `xemaclite` unit 0 (XEmacLite Ethernet MAC in FPGA)
- Boot user: `xemhost`

### Ethernet MAC
- Xilinx XEmacLite — simple, interrupt-driven Ethernet MAC IP core
- Source: `xemaclite.c` (BSP), built for PPC405 at `C:/sundance/SW/32_0_3/...`
- The Ethernet port on the camera is likely the 10/100 Ethernet jack for file offload

---

## 7. JTAG / On-Chip Debug — Physical Interfaces & Safe Procedure

> Added 2026-06-05. The camera has **multiple independent JTAG chains** (one or more per
> board). Map and exercise them on the known-broken / boot-looping unit first; only then
> touch a working camera, using the read-only procedure below.

### Boards in this unit (each a candidate JTAG chain)
`audio_pci_board`, `cpu_io_board`, `power_board`, `sd_board`, `sensor_board`,
`ssd_board`, `ssd_drive`, `ui_board`, **`video_processor_board`**.
The **video_processor_board** is the prime unknown: it almost certainly carries the
second Virtex (VP-FPGA), whose package bitstream `redone.2` is RSA-signed/encrypted — a
*live* readback there would bypass the package entirely (see upgrade-rsa-signed memory).

### Confirmed chain — CPU/IO board
| Pos | Device | IDCODE | IR len | Notes |
|-----|--------|--------|--------|-------|
| 1 | XC2C256 (CoolRunner-II CPLD) | `0x16d4a093` | 8 | config/reset/power sequencing; design captured → `components/cpu_io_board/xc2c256_readback.jed` |
| 2 | XC4VFX100 (Virtex-4 FX) | `0x01ee4093` | 14 | contains PPC405 (PVR `0x20011470`); config **unencrypted** (status reg: Decryptor security=0, DONE=1, mode pins M2:M1:M0=110 slave); XMD `connect ppc hw` works with no `jtagppc_cntlr` |

DDR base `0x0`; firmware is flat-loaded so static-analysis VAs == live addresses. XMD
address-map gotcha (launch standalone, no project) + read recipe: see jtag-xmd-live-access memory.

### SAFE interfacing procedure (mandatory on a working camera)

**A. Before touching the header — voltage is the #1 physical risk.**
1. Identify the pinout (schematic or continuity): TCK, TMS, TDI, TDO, **Vref/Vtarget**, GND, (nTRST). Confirm pin 1.
2. **Measure Vref** with a multimeter. Virtex-4 / CoolRunner JTAG banks are typically 2.5 V or 3.3 V — but verify (CoolRunner-II can run 1.8 V).
3. Use a **Vref-sensing / adaptive cable** (Platform Cable USB II senses Vtarget). Confirm its Vref range covers the measured voltage. **Never** drive a fixed-voltage cable into a lower-voltage bank.

**B. Connection hygiene.**
4. Prefer **target powered OFF** when seating the connector; GND first; verify orientation; power on after the cable is seated.
5. Start at a **conservative TCK** (750 kHz–1 MHz). One cable, one chain at a time.

**C. Read-only command whitelist (safe on a live camera).**
- iMPACT: *Initialize Chain*, *Get Device ID*, *ReadIdcode*, *Get Device Signature/Usercode*, *Read Device DNA*, *read Status Register*. (CPLD `.jed` readback is read-only.)
- XMD: `connect ppc hw`, `mrd`, `rrd`, `dis`. Use `stop`/`con` only briefly; always `con` and clear breakpoints before leaving.

**D. FORBIDDEN on a working camera (can crash, corrupt, or permanently brick).**
- iMPACT: **Program, Erase, Blank Check, Verify(+program), Assign-and-Program, SVF/XSVF playback, eFUSE/BBRAM/key ops.** Erasing a CPLD or config PROM is *permanent* — we may have no reflashable image.
- Avoid **Readback-with-capture** (issues GCAPTURE; perturbs live state). Plain static config readback needs a `.msk` we don't have.
- XMD: **`rst`, `mwr`, `rwr`, `dow`/`dnld`**, long `stop` (watchdog), or leaving the CPU halted / breakpoints set.
- Do **not** `Program` even with our generated `fpga.bit` — it would reconfigure the running FPGA.

**E. Clean disconnect.** `con` (resume CPU) → `disconnect` all XMD targets → close the tool owning the cable → unplug.

### Per-header enumeration steps (run on the broken sandbox unit)
1. Locate header; measure Vref; set cable.
2. iMPACT → **Initialize Chain**; record device list, **IDCODEs**, IR lengths, order.
3. FPGAs: read **Status Register** (encryption? DONE? mode pins). CPLDs: ReadIdcode/usercode.
4. If a PPC/MicroBlaze is present: XMD `connect ppc hw` (read-only) — note PVR.
5. Record in the topology table below; save console logs.

### JTAG topology — fill in as you probe
| Board | Header (loc) | Vref | Devices (IDCODE) | PPC? | Status | Logged |
|-------|-------------|------|------------------|------|--------|--------|
| cpu_io_board | (connected) | measure | XC2C256 `16d4a093`, XC4VFX100 `01ee4093` | yes (PVR `20011470`) | FX100 unencrypted, DONE=1 | 2026-06-05 |
| video_processor_board | (VP bd header) | FX JTAG bank | XC4VFX100 `01ee4093` (2nd FX100) | not probed | configured, DONE=1, **FPGA decryptor OFF** (loaded bitstream plaintext), slave mode (M=110), usercode `ffffffff` | 2026-06-05 |
| sensor_board | — | — | none found | — | no JTAG header (bench survey) | 2026-06-05 |
| power_board | (power bd header) | ~3.3 V (XPLA3) | XCR3064XL `0484c093` (CoolRunner XPLA3, 64 MC) | no | chain valid; readback + checksum FAILED (read-protected) | 2026-06-05 |
| audio_pci_board | — | — | none found | — | **no JTAG header** (corrected 2026-06-05). Physically missing on the test unit (boot-loop cause), but not a JTAG target. | 2026-06-05 |
| ui_board | (UI bd header) | ~3.3 V (XPLA3) | XCR3032XL `0480c093` (CoolRunner XPLA3, 32 MC) | no | chain valid; **readback FAILED** (INFO:2488 — likely read-protected); checksum failed too | 2026-06-05 |
| sd_board / ssd_board | — | — | none found | — | no JTAG header (bench survey) | 2026-06-05 |

**Survey status (2026-06-05): COMPLETE.** 4 of 9 boards carry JTAG TAPs — cpu_io,
video_processor, ui, power. audio_pci / sensor / sd / ssd have **no JTAG header**. Only
unrecovered design: the VP-FPGA config (needs a live readback — **procedure:
`vp_fpga_readback.md`**). XPLA3 CPLDs (ui, power) are read-protected; CPU/IO XC2C256 was not.

---

## Debug Access Quickstart

### Step 1: WDB (immediate, no camera modification needed)
```bash
# Set your host to 192.168.0.1/24
ip addr add 192.168.0.1/24 dev eth0

# Connect WindRiver Workbench OR use wdbrpc/wtxtcl
# WDB UDP target: 192.168.0.2:17185

# Via wdbrpc (open-source WDB client):
wdbrpc 192.168.0.2 17185
```

### Step 2: USB Shell (requires WDB first)
```
# Via WDB: set DEBUG.USB.CONNECTION param to 1
# (exact BSS address of param needs to be located — TBD)
# Then connect USB and open virtual COM port
```

### Step 3: Serial console (hardware access)
- Locate RS-232 pins on CONTROL connector
- Connect at 9600 or 115200 baud (baud rate depends on XUartLite config — TBD)
- May need to change TTY0.ASSIGNMENT to "EXTERNAL" or "CONSOLE"

---

## Live USB Connection — Confirmed Findings (2026-05-09)

The camera was connected to a Linux host via USB. The following was confirmed:

### USB Enumeration
- Device: `/dev/ttyACM0` (`crw-rw---- root dialout 166,0`)
- VID:PID: `1c56:5232` (RED RED ONE)
- Speed: High Speed (480 Mbps) via xhci_hcd
- Class: CDC-ACM (bDeviceClass=2, bInterfaceSubClass=2, bInterfaceProtocol=1 AT-commands)
- Bulk IN: EP4 `0x84` — 512 B max packet
- Interrupt IN: EP5 `0x85` — 64 B max packet, 1 ms interval
- Power: Self-powered, draws 0 mA from bus

### Probe Results
The port was opened and probed at {9600, 19200, 38400, 57600, 115200} baud.
Probes sent: `\r\n`, `AT\r\n`, `ATE0\r\n`, `i\r\n`, `help\r\n`.
**No response received on any baud rate.** The USB CDC-ACM interface enumerates
unconditionally, but the VxWorks shell (`runTargetShell()`) is NOT active until
`DEBUG.USB.CONNECTION` is set to a non-zero value.

### Binary Analysis
- String `DEBUG.USB.CONNECTION` confirmed at file offset `0xD35928` (= VA, flat binary)
- Second occurrence in XML param definition at `0xC769DA`
- **No direct code pointer to `0xD35928` found in the binary** — the param is
  accessed either via the XML-driven param registry (not a direct lis/addi load)
  or via VxWorks symbol table lookup at runtime
- `_ZTV11UiUsbSerial` at `0xDCB3BC` is a **symbol name string**, not the actual vtable
- Method name strings found at `0x0064F4E8–0x0064F554`:
  `ProcessMessage`, `RunPhase`, `SocketWatch`, `runTargetShell`, `WriteMessage`,
  `ReadMessage`, `ParamRef`, `Set` — packed string constants, part of VxWorks task naming

---

## Live USB + WDB Session — Deep Probe (2026-06-03)

Re-probed the connected camera with two new, self-contained tools and a much
broader stimulus set than the 2026-05-09 pass.

### Tooling (both in `firmware/scripts/`)
- **`probe_serial.py`** (extended) — passive-listen mode, line-ending matrix
  (`\r` / `\n` / `\r\n` / Ctrl-C), DTR/RTS toggling, BREAK, modem-line readback,
  timestamped capture logs under `firmware/reverse/build_32/captures/`.
- **`wdb_probe.py`** (new) — minimal WDB ONC-RPC/UDP client (stdlib only):
  `TARGET_CONNECT` (agent/runtime/CPU/bootline/RAM-layout), `MEM_READ`, and a
  gated `MEM_WRITE`. Wire format verified against Metasploit's WDBRPC mixin;
  packet checksum self-validates as a correct one's-complement (folds to
  `0xFFFF`). Includes a `--selftest` that reads RE-map addresses from live RAM.

### USB CDC-ACM — what it can do (confirmed)
- **CDC-ACM is virtual**: baud rate is a no-op over the NET2280 USB link, so the
  old multi-baud sweep was redundant — silence at 115200 is conclusive.
- **The device acknowledges the link at the control-line level.** At open it
  reports `CTS=1`; once the host asserts **DTR**, the camera latches **`DSR=1`
  and `CD=1` (carrier detect)**. So the USB stack and `UiUsbSerial` link layer
  are alive — only the *shell data path* is gated.
- **Zero data on every stimulus**: full line-ending matrix, Ctrl-C, all four
  DTR/RTS combinations, BREAK, and an 8 s idle passive listen all returned
  **0 bytes**. Captures:
  `captures/usb_serial_20260603T182807Z.log` (active matrix),
  `captures/usb_serial_20260603T182900Z.log` (passive listen).
- **Conclusion:** consistent with `DEBUG.USB.CONNECTION = 0` — `runTargetShell()`
  has not been called, so no shell is bound to the USB data endpoints.
- **Not yet done:** a passive-listen capture across a *power-cycle* to catch any
  early-boot banner (run `probe_serial.py --listen 60` while power-cycling).

### WDB-over-Ethernet — ready, pending physical link
`wdb_probe.py` is written and framing-validated but **not yet run against the
camera**: the host is on `10.0.1.0/24` and the camera's WDB IP is `192.168.0.2`.
To execute:
```bash
# wire Ethernet camera <-> host, then (sudo, separate iface keeps your LAN intact):
sudo ip addr add 192.168.0.1/24 dev <iface>
ip neigh                       # expect an ARP entry for 192.168.0.2 once it talks
python3 firmware/scripts/wdb_probe.py            # connect + info + self-test
```
Self-test validates live RAM against the static map (e.g. `0xE9C4BC` should read
`0x00004321`, the WDB UDP port). Once `MEM_READ` is confirmed, the path to waking
the USB shell is: locate the runtime address backing `DEBUG.USB.CONNECTION`
(still the open RE problem below) and `MEM_WRITE` a non-zero value.

---

## Outstanding TODOs

- [ ] **Run `wdb_probe.py` against the camera** (needs Ethernet link + host IP
  `192.168.0.1/24`); confirm `MEM_READ` of `0xE9C4BC` == `0x00004321`
- [ ] **Capture a power-cycle boot banner** over USB
  (`probe_serial.py --listen 60` while rebooting the camera)
- [ ] **Find actual BSS address of `DEBUG.USB.CONNECTION` variable** (to write via WDB)
  - The param is XML-driven; BSS addr requires either WDB symbol lookup or tracing
    the XML param registration path at runtime
  - Next approach: find `shellSpawn`/`shellInit` callers → trace back to `runTargetShell`
    function address → find its caller `ProcessUsbDebugChange` → find the param read
- [ ] **Connect via WDB over Ethernet** (camera IP: `192.168.0.2`, UDP port `17185`)
  - Once connected, use `lkup "DEBUG"` and `lkup "UiUsbSerial"` to get live addresses
  - This is the fastest path to activating the USB shell
- [ ] **Extract `XUartLite_ConfigTable` and `XUartNs550_ConfigTable` MMIO bases and baud rates** from binary
- [ ] **Find `ProcessUsbDebugChange` function address** via `shellSpawn`/`shellInit` call chain
- [ ] **Verify `runTargetShell` → what VxWorks API it calls** (`shellSpawn`? `shellInit`?)
- [ ] **Confirm camera IP is 192.168.0.2 and not overridden** by a non-volatile config on flash
- [ ] **Find the CONTROL connector UART** — match XUartNs550 to physical RS-232 connector
- [ ] **Test WDB connectivity** — verify WDB task is actually running (not gated by boot flag)

---

## Key Addresses

| Address      | Description                              |
|--------------|------------------------------------------|
| `0x0036B3DC` | `usrWdbInit` — WDB agent initialization  |
| `0x0036B7EC` | BSP init function, calls usrWdbInit      |
| `0x005A153C` | `wdbEndPktDevInit` — init WDB over END   |
| `0x00E9C4BC` | BSS: WDB port variable (= 17185)         |
| `0xD5C608`   | String: VxWorks boot config w/ IP        |
| `0xDF7930`   | Symbol name: XUartLite_ConfigTable       |
| `0xDF7B3C`   | Symbol name: XUartNs550_ConfigTable      |
| `0xD35928`   | String: `DEBUG.USB.CONNECTION`           |
| `0xD30044`   | String: `/tffs0/altshell`                |
| `0xD4C50C`   | String: `/roFs/tty0app.hex`              |
| `0xDCB3BC`   | Symbol name: `_ZTV11UiUsbSerial` (vtable)|
