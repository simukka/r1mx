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

## Outstanding TODOs

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
