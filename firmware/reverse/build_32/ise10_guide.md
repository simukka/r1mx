# ISE Design Tools 10.x — Step-by-Step Guide for RED ONE MX RE

**Purpose:** Detailed instructions for using the ISE 10.x toolchain on Windows XP to
advance the Build 32 reverse engineering work. Three distinct workflows:

1. **Platform Studio (EDK)** — reconstruct `xparameters.h` to complete the MMIO map
2. **File Collection** — copy IP core source and documentation from the ISE installation
3. **iMPACT** — JTAG readback from a physical camera (if hardware is available)

**Background:** The RED ONE MX firmware was compiled against a Xilinx EDK BSP whose full
source path is embedded in the firmware symbol table:
```
C:/sundance/SW/32_0_3/Sundance/bsp_ppc405_0_revB/ppc405_0_drv_csp/xsrc/<driver>.c
```
This means the camera developers used Xilinx EDK (likely 10.x–12.x) on Windows. The
`xparameters.h` they compiled against defines the exact base addresses and parameters
for every IP core in the design.

---

## Part 1 — Platform Studio (EDK): Reconstruct xparameters.h

### What you will create

A Virtex-4 FX100 EDK project that mirrors the RED ONE MX FPGA design. You are not trying
to recreate the full design — just instantiate the right IP cores at the right addresses
and generate BSP headers. The output `xparameters.h` will contain:

- Exact register base addresses for all 9 confirmed IP cores
- Clock frequencies (critical for UART baud rate divisors)
- Number of interrupt channels in XIntc
- DMA channel configuration
- Confirmation or correction of the anomalous `0x64010000` DMA address

### What we already know (enter these exactly)

| IP Core | Base Address | Key Parameter |
|---------|-------------|---------------|
| XUartLite | `0xe0600000` | baud=115200, clock=100MHz, 8N1, no parity |
| XUartNs550 #1 | `0xe0640000` | clock=100MHz |
| XUartNs550 #2 | `0xe0650000` | clock=100MHz |
| XIntc | `0xe0800000` | 32 interrupt inputs |
| XEmacLite | `0xe1020000` | TxPingPong=1, RxPingPong=1, no MDIO |
| XIic | `0xb2600000` | standard config |
| XPci v3 | `0xe1200000` | standard config |
| XDmaChannel | `0x64010000` | UNCERTAIN — note what bus Platform Studio assigns |
| OPB arbiter | — | needed if XIic or DMA go on OPB |
| PLB arbiter | — | standard PLB v4.6 |

---

### Step 1 — Launch Platform Studio

- Start → All Programs → Xilinx ISE Design Tools → EDK 10.x → Xilinx Platform Studio
- Or from ISE Project Navigator: Tools → Launch Platform Studio

If XPS opens to an existing project, close it: File → Close Project.

---

### Step 2 — Create New Project

1. File → New Project
2. In the wizard, choose **"I would like to create a new design"** (NOT the Base System
   Builder option — that adds unwanted components)
3. Project location: create a folder on the desktop, e.g. `C:\r1mx_mmio\`
4. Project name: `r1mx_mmio`
5. Click OK

---

### Step 3 — Add the Target Device

In the "Board and Device Selection" panel (or System Assembly View):

1. Click on **"System"** in the left panel → Properties (or right-click → Edit System)
2. Under "Target Device":
   - Family: **Virtex4**
   - Device: **xc4vfx100** (if not available, try xc4vfx60)
   - Package: **ff1517** (for fx100) or **ff1152** (for fx60)
   - Speed Grade: **-11**
3. Click OK

> Note: If the exact device is not available in 10.x, xc4vfx60 works fine — the IP
> core addresses are independent of the specific FX variant.

---

### Step 4 — Add the PPC405 Processor

1. In the IP Catalog (View → IP Catalog), search for **"ppc405"**
2. Find: **ppc405_0** (or "Hard-Core PowerPC Processor" for Virtex-4 FX)
3. Double-click to instantiate
4. Name it: `ppc405_0`
5. Leave all settings at defaults — we only need the peripheral addresses, not a working design

---

### Step 5 — Add PLB v4.6 Bus

1. IP Catalog → search **"plb"**
2. Find: **plb_v46** (PLB Version 4.6 Bus)
3. Double-click to instantiate; name it `plb`
4. In the System Assembly View, connect `ppc405_0` as a PLB master to `plb`

This is the primary peripheral bus. All the 0xE0xxxxxx peripherals attach here.

---

### Step 6 — OPB Bus (SKIP)

> The PPC405 hard macro has no native OPB master port — it is PLB-only. Connecting OPB
> peripherals requires a `plb2opb_bridge` between the buses, which adds complexity with no
> benefit for our goal (generating `xparameters.h`).
>
> **Skip this step. Connect XIic and XDmaChannel directly to `plb` in Steps 8 and 9.**
> The addresses in `xparameters.h` come from the Address Editor entries, not from which bus
> the peripheral is on. We already have the XIic address confirmed from the firmware binary.

---

---

### Step 7 — Add IP Cores (7 confirmed PLB cores)

For each core below: IP Catalog → search name → double-click → configure as listed.

> **Address Editor note:** Platform Studio shows both a **Base Address** and a **High Address**
> column. Set Base as listed; set High = Base + `0xFFFF` (i.e. Base + 64KB - 1).
> Platform Studio may auto-fill the High address when you tab away from Base — just verify it.
>
> | Peripheral | Base | High |
> |-----------|------|------|
> | XUartLite | `0xe0600000` | `0xe060FFFF` |
> | XUartNs550 #1 | `0xe0640000` | `0xe064FFFF` |
> | XUartNs550 #2 | `0xe0650000` | `0xe065FFFF` |
> | XIntc | `0xe0800000` | `0xe080FFFF` |
> | XEmacLite | `0xe1020000` | `0xe102FFFF` |
> | XPci v3 | `0xe1200000` | `0xe120FFFF` |
> | XIic | `0xb2600000` | `0xb260FFFF` |
> | XDmaChannel | `0x64010000` | `0x6401FFFF` |

#### 7a. XUartLite (xps_uartlite)

1. IP Catalog → search **"uartlite"**
2. Find: **xps_uartlite** (any version available; use highest)
3. Instantiate; name: `UartLite_0`
4. Configure:
   - **C_BAUDRATE**: `115200`
   - **C_DATA_BITS**: `8`
   - **C_USE_PARITY**: `0` (no parity)
   - **C_ODD_PARITY**: `0`
   - **C_CLK_FREQ**: `100000000` (100 MHz)
5. Connect to `plb` bus
6. In Address Editor: Base **`0xe0600000`**, High **`0xe060FFFF`**

#### 7b. XUartNs550 #1 (xps_uartns550)

1. IP Catalog → search **"uartns550"** or **"uart16550"**
2. Find: **xps_uartns550** (highest version)
3. Instantiate; name: `UartNs550_0`
4. Configure:
   - **C_CLK_FREQ**: `100000000` (100 MHz)
   - Leave baud, data bits at defaults (these are runtime-configurable in NS550)
5. Connect to `plb` bus
6. Address Editor: Base **`0xe0640000`**, High **`0xe064FFFF`**

#### 7c. XUartNs550 #2

1. Instantiate another **xps_uartns550**; name: `UartNs550_1`
2. Same config as #1 (C_CLK_FREQ=100MHz)
3. Address Editor: Base **`0xe0650000`**, High **`0xe065FFFF`**

#### 7d. XIntc (xps_intc)

1. IP Catalog → search **"intc"**
2. Find: **xps_intc** (highest version available)
3. Instantiate; name: `Intc_0`
4. Configure:
   - **C_NUM_INTR_INPUTS**: `32`
   - **C_HAS_IPR**: `1` (include Interrupt Pending Register)
   - **C_HAS_SIE**: `1`
   - **C_HAS_CIE**: `1`
   - **C_HAS_IVR**: `1`
   - **C_IRQ_IS_LEVEL**: `0xFFFFFFFF` (all level-triggered; adjust if needed)
5. Connect to `plb` bus
6. Address Editor: Base **`0xe0800000`**, High **`0xe080FFFF`**

> **Do NOT try to connect `Intc_0` interrupt output to `ppc405_0` from the GUI.**
> The PPC405 hard macro interrupt pin is not exposed as a connectable port in Platform
> Studio 10.x. The interrupt wiring is handled via the MHS PORT section instead.
> You will fix this in the MHS file in Step 10a below.

#### 7e. XEmacLite (xps_ethernetlite)

1. IP Catalog → search **"ethernetlite"** or **"ethernet"** (with "Show All" enabled)
2. Find: **xps_ethernetlite** (note: NOT `xps_emaclite` — that name is used in ISE 14.x)
3. Instantiate; name: `EmacLite_0`
4. Configure:
   - **C_TX_PING_PONG**: `1`
   - **C_RX_PING_PONG**: `1`
   - **C_INCLUDE_MDIO**: `0` (no MDIO — confirmed from firmware config)
   - **C_CLK_FREQ**: `100000000`
5. Connect to `plb` bus
6. Address Editor: Base **`0xe1020000`**, High **`0xe102FFFF`**

#### 7f. XPci (xps_pci or xps_pci32)

1. IP Catalog → search **"pci"** (with "Show All" enabled)
2. Look for: **`xps_pci`**, **`xps_pci32`**, or **`plb_pci`** — the exact name varies by ISE version
3. If found: instantiate; name: `Pci_0`; leave defaults; connect to `plb`
4. Address Editor: Base **`0xe1200000`**, High **`0xe120FFFF`**
5. **If not found: skip entirely.** The address `0xe1200000` is already confirmed from the
   firmware PLB table. The PCI driver source files (`xpci.c`) will still be on disk.

---

### Step 8 — Add XIic

1. IP Catalog (with "Show All" enabled) → search **"iic"**
2. Find: **xps_iic** (highest version)
3. Instantiate; name: `Iic_0`
4. Leave defaults
5. Connect to **`plb`** bus
6. Address Editor: Base **`0xb2600000`**, High **`0xb260FFFF`**

---

### Step 9 — Add XDmaChannel (UNCERTAIN base address)

1. IP Catalog (with "Show All" enabled) → search **"dma_channel"** or **"central_dma"**
2. Find: **xps_central_dma** (or **xps_dma_channel**)
3. Instantiate; name: `DmaChannel_0`
4. Leave defaults
5. The DMA has two bus ports — connect **both** to `plb`:
   - **`splb`** (Slave PLB) — CPU access to DMA control registers → connect to `plb`
   - **`mplb`** (Master PLB) — DMA engine bus mastering for data movement → connect to `plb`
6. Address Editor: set the **`splb`** row — Base **`0x64010000`**, High **`0x6401FFFF`**
   (the `mplb` row has no address — it is a master port, not a slave)

Note whatever address ends up in the generated `xparameters.h` — if Platform Studio
auto-corrects the address it will tell us something about the valid PLB range.

---

### Step 10 — Generate Addresses

1. Tools → Generate Addresses (or click the "Generate Addresses" toolbar button)
2. If any conflicts appear, note them — they indicate our address assignments are wrong
3. If Platform Studio reassigns any address automatically, **write down what it changed**

---

### Step 10a — Fix system.mhs: Wire One Interrupt to XIntc

> **Why:** libgen's TCL script for the XIntc driver validates that the number of interrupt
> sources connected to `Intc_0` matches `C_NUM_INTR_INPUTS`. If you have not connected any
> interrupt source port, the count mismatch causes this fatal error:
> ```
> ERROR:MDT - intc () - Internal error: Number of interrupt inputs on Intc_0 (1)
>    is not the same as length of total number of interrupt sources (0).
> ```
> The fix: connect UartLite's interrupt output to Intc_0's input by editing `system.mhs`.

1. Close Platform Studio (or at minimum close and reopen the project after editing)
2. Open `Y:\r1mx_mmio\system.mhs` in Notepad (or any text editor)
3. Find the `BEGIN xps_uartlite` section (the `UartLite_0` instance); add one PORT line:
   ```
   PORT Interrupt = xps_uartlite_0_ip2intc_irpt
   ```
   The section should look like:
   ```
    BEGIN xps_uartlite
     PARAMETER INSTANCE = UartLite_0
     ...
     PORT Interrupt = xps_uartlite_0_ip2intc_irpt
    END
   ```
4. Find the `BEGIN xps_intc` section (`Intc_0`); add one PORT line using the **same net name**:
   ```
   PORT Intr = xps_uartlite_0_ip2intc_irpt
   ```
5. Save the file
6. Reopen in Platform Studio: File → Open Project → select `system.xmp`

The net name `xps_uartlite_0_ip2intc_irpt` is arbitrary — it just must match in both PORT
lines. This creates a 1-bit signal satisfying the libgen interrupt count check.

---

### Step 11 — Generate BSP

1. Software → Generate Libraries and BSPs (or Tools → Generate BSP)
2. In the BSP dialog, select **ppc405_0** as the processor
3. Click **Generate**

This creates the `xparameters.h` file and all driver header files.

---

### Step 12 — Find the Output Files

After generation, look for these files in your project directory (`C:\r1mx_mmio\`):

```
C:\r1mx_mmio\
  system.mhs                       ← Microprocessor Hardware Spec (your IP config)
  system.mss                       ← Microprocessor Software Spec (BSP config)
  ppc405_0\
    include\
      xparameters.h                ← THE KEY FILE — copy this to Linux
    libsrc\
      xuartlite_v1_00_a\src\       ← UartLite driver source
      xps_uartns550_v1_00_a\src\   ← NS550 driver source
      xintc_v2_01_d\src\           ← Interrupt controller driver source
      xemaclite_v1_01_b\src\       ← Ethernet driver source
      xiic_v2_03_a\src\            ← I2C driver source
```

> Note: The version suffix in folder names (e.g. `_v1_00_a`) will vary by your ISE
> version. Just look for folders starting with `xuartlite`, `xintc`, etc.

**If the `ppc405_0\include\` path doesn't exist**, look in:
```
C:\r1mx_mmio\implementation\ppc405_0\include\xparameters.h
```
or search the project directory for `xparameters.h`.

---

### Step 13 — What to Read in xparameters.h

Open the file in Notepad and look for these defines. Record all of them for the Linux side:

```c
/* These confirm or correct our MMIO map */
XPAR_UARTLITE_0_BASEADDR         /* should be 0xe0600000 */
XPAR_UARTLITE_0_BAUDRATE         /* should be 115200 */
XPAR_UARTLITE_0_CLOCK_FREQ_HZ   /* should be 100000000 */
XPAR_UARTNS550_0_BASEADDR        /* should be 0xe0640000 */
XPAR_UARTNS550_0_CLOCK_FREQ_HZ  /* should be 100000000 */
XPAR_UARTNS550_1_BASEADDR        /* should be 0xe0650000 */
XPAR_INTC_0_BASEADDR             /* should be 0xe0800000 */
XPAR_INTC_0_NUM_INTR_INPUTS      /* should be 32 */
XPAR_EMACLITE_0_BASEADDR         /* should be 0xe1020000 */
XPAR_EMACLITE_0_TX_PING_PONG     /* should be 1 */
XPAR_EMACLITE_0_RX_PING_PONG     /* should be 1 */
XPAR_IIC_0_BASEADDR              /* should be 0xb2600000 */
XPAR_PCI_0_BASEADDR              /* should be 0xe1200000 */
XPAR_DMA_CHANNEL_0_BASEADDR      /* should be 0x64010000 -- confirm or deny */
```

Also record:
```c
XPAR_CPU_PPC405_CORE_CLOCK_FREQ_HZ   /* CPU clock */
XPAR_INTC_MAX_NUM_INTR_INPUTS        /* interrupt lines */
```

---

### Step 14 — Save the MHS File

`system.mhs` is a text file describing your complete hardware configuration. Copy it to Linux
as reference — it shows the exact EDK syntax for connecting these IP cores and serves as
a starting point if you ever want to re-open the project.

---

## Part 2 — Collecting IP Core Source and Documentation

### BSP Source Files (Already Installed)

The full IP core source code is installed with EDK. This is the code the firmware was
compiled against. Copy the following to a USB drive or network share:

**IP core source code (one folder per core):**
```
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_uartlite_v1_00_a\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_uartns550_v1_00_a\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_intc_v2_01_d\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_emaclite_v1_01_b\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_iic_v2_03_a\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_pci_v3_v1_02_a\
C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\xps_central_dma_v2_02_a\
```

> Note: version suffixes (e.g. `_v1_00_a`) may differ in your installation. Browse to
> `C:\Xilinx\10.1\EDK\hw\XilinxProcessorIPLib\pcores\` and find folders starting with
> the names above. Copy all of them.

**Also collect the driver library headers:**
```
C:\Xilinx\10.1\EDK\sw\lib\bsp\standalone_v1_00_a\src\xuartlite.h
C:\Xilinx\10.1\EDK\sw\lib\bsp\standalone_v1_00_a\src\xintc.h
C:\Xilinx\10.1\EDK\sw\lib\bsp\standalone_v1_00_a\src\xemaclite.h
C:\Xilinx\10.1\EDK\sw\lib\bsp\standalone_v1_00_a\src\xiic.h
```

If the `standalone_v1_00_a` path does not exist, look in:
```
C:\Xilinx\10.1\EDK\sw\lib\drivers\
```
There should be one folder per driver: `uartlite_v1_xx`, `intc_v2_xx`, etc.

**Documentation (if present):**
```
C:\Xilinx\10.1\EDK\doc\
```
Look for PDFs named after each IP core: `xps_uartlite.pdf`, `xps_intc.pdf`, etc.
These contain register maps and initialization sequences.

### What to Look for in the Source Files

For each driver, the most important files are:

| File pattern | What it tells us |
|---|---|
| `x<core>.h` | All register offsets as `#define`s |
| `x<core>_selftest.c` | Exact register sequence the selftest runs (critical for QEMU) |
| `x<core>_sinit.c` | Static init — shows how `XFoo_ConfigTable` is structured |
| `x<core>_hw.h` | Raw hardware register bit definitions |

**Critical for QEMU stubs:** `x<core>_selftest.c` shows exactly what values the
firmware reads back to decide if hardware init passed. If QEMU returns wrong values,
`XFoo_SelfTest()` returns `XST_FAILURE` and VxWorks halts.

### Register Offset Quick Reference (confirm against source)

After copying the files, search for these patterns in the `.h` files:

```
# In xuartlite.h or xuartlite_hw.h:
XUL_RX_FIFO_OFFSET        # should be 0x00
XUL_TX_FIFO_OFFSET        # should be 0x04
XUL_STATUS_REG_OFFSET     # should be 0x08
XUL_CONTROL_REG_OFFSET    # should be 0x0C

# Status register bits:
XUL_SR_RX_FIFO_VALID_DATA # bit 0 — RX data ready
XUL_SR_TX_FIFO_FULL       # bit 3 — TX full
XUL_SR_TX_FIFO_EMPTY      # bit 2 — TX empty

# In xintc.h or xintc_hw.h:
XIN_ISR_OFFSET            # should be 0x00
XIN_IPR_OFFSET            # should be 0x04
XIN_IER_OFFSET            # should be 0x08
XIN_IAR_OFFSET            # should be 0x0C
XIN_MER_OFFSET            # should be 0x1C
XIN_MER_ME_MASK           # bit 0 — master enable
XIN_MER_HIE_MASK          # bit 1 — hardware interrupt enable
```

---

## Part 3 — iMPACT: JTAG Readback from a Physical Camera

**Prerequisite:** Camera powered on and accessible. JTAG cable connected to the camera's
JTAG header on the CPU/IO board. See schematics work to identify the JTAG header location.

**Cable options (in order of preference):**
1. Xilinx Platform Cable USB (DLC9G) — natively supported by iMPACT 10.x
2. Digilent JTAG-HS2 / HS3 — supported via Digilent plugin for iMPACT

**The JTAG TAP chain is confirmed accessible while the camera runs** because `fpga.bin`
sets CTL register bit 9 (PERSIST) = 1. This means you do NOT need to power-cycle
the camera for JTAG access.

---

### Step 1 — Launch iMPACT

- Start → All Programs → Xilinx ISE Design Tools → iMPACT

---

### Step 2 — Create a New iMPACT Project

1. File → New Project
2. Choose **Boundary Scan** mode
3. Click OK

---

### Step 3 — Connect and Detect the JTAG Chain

1. In the Boundary Scan window, right-click → **Initialize Chain** (or press Ctrl+I)
2. iMPACT will scan the JTAG chain and detect all TAP devices
3. **Expected result:** Two Xilinx Virtex-4 FX devices should appear (iofpga + vpfpga)
4. For each device, iMPACT shows the IDCODE — record these

**Virtex-4 FX IDCODE values:**
| Device | IDCODE |
|--------|--------|
| xc4vfx20 | `0x01658093` |
| xc4vfx40 | `0x0167c093` |
| xc4vfx60 | `0x01684093` |
| xc4vfx100 | `0x01694093` |
| xc4vfx140 | `0x016b4093` |

The IDCODEs tell us exactly which FX variant is in the camera — this is valuable
hardware information for the emulator (affects memory block counts, DSP counts, etc.).

If iMPACT shows "UNKNOWN DEVICE", the TAP chain is present but iMPACT does not
recognize the device. Record the raw IDCODE from the boundary scan output window.

---

### Step 4 — Assign Bitstream to the FPGA (for readback)

1. Double-click the first FPGA device icon in the boundary scan view
2. When prompted "Assign New Configuration File?" — click **No** (we want readback, not programming)
3. Right-click the device → **Device Properties**
4. Note the IDCODE and device name

---

### Step 5 — Perform Configuration Readback

1. Right-click on the FPGA device → **Read Device** (or **Read Back**)
2. In the dialog:
   - Output file: choose a location, e.g. `C:\r1mx_readback\fpga_readback.bit`
   - Readback file type: **BITFILE** (.bit) or **RBT** (readback data)
   - Leave "Verify" unchecked for the initial read
3. Click OK
4. iMPACT will perform the readback and save the file

**Alternative in older iMPACT:** Right-click → Create Readback Data File.
Choose format `.rbt` (ASCII bitstream). This is easier to parse manually.

> Note: The readback file will be ~4MB (same as fpga.bin). The frame data starts
> with a one-frame pad of zeros before the actual configuration data.

---

### Step 6 — Compare Readback with fpga.bin

Transfer the readback file to Linux, then:

```bash
# The raw frame data in .bin format should match fpga.bin:
sha256sum firmware/reverse/build_32/extracted/fpga.bin

# For .rbt format (ASCII), convert to binary first:
# iMPACT can also save directly as .bin — use that format

# Quick sanity check — should see the same sync word:
xxd fpga_readback.bin | head -5
# Expected: ff ff ff ff  aa 99 55 66  (sync word)
```

---

### Step 7 — Read the Second FPGA (vpfpga)

Repeat Steps 4–6 for the second FPGA device in the chain. This is the Video Processing
FPGA whose bitstream (`redone.2`) is still encrypted in the firmware package.

The live readback bypasses the encryption entirely — you get the raw running bitstream
directly from the silicon. This is valuable because:
- `redone.2` has not been decrypted (the AES key `M1H5gwOXh757rIRVY6Gj2tN080AYSX03`
  may not decrypt redone.2 — that component may use a different key or no encryption)
- Live readback gives us the VP-FPGA design we can analyze with TORC or ISE

---

### Step 8 — Extract BRAM Data (calibration tables)

The Virtex-4 BRAM content can be read back with iMPACT using the JTAG readback sequence.
The BRAM data frames are identified by FAR block type = `010` (bits 21:19 of the FAR).

iMPACT does not directly extract BRAM separately, but the full readback `.bin` file
contains all frames including BRAM. Post-process on Linux:

```python
# Quick BRAM frame extractor (run on Linux after transfer):
# Virtex-4 frame = 41 words × 4 bytes = 164 bytes
# FAR bit layout: [22]=top/bot [21:19]=block [18:14]=row [13:9]=col [5:0]=minor
#
# The full frame data starts at the Type2 WRITE packet (offset 0x1278 in fpga.bin)
# Filter for block type 010 (bits 21:19 of the incrementing FAR value)

import struct

with open("fpga.bin", "rb") as f:
    data = f.read()

# Type2 frame data starts at offset 0x1278 (after the WCFG+FDRI header)
FRAME_DATA_OFFSET = 0x1278
WORDS_PER_FRAME = 41
BYTES_PER_FRAME = WORDS_PER_FRAME * 4

frame_count = (len(data) - FRAME_DATA_OFFSET) // BYTES_PER_FRAME
bram_frames = []

for i in range(frame_count):
    # Approximate FAR: frames are written sequentially starting at FAR=0
    # Block type is in bits 21:19 of FAR
    # Rows increment slower, so BRAM frames appear in blocks
    # Simple heuristic: check for non-zero data (BRAM cells are initialized)
    offset = FRAME_DATA_OFFSET + i * BYTES_PER_FRAME
    frame = data[offset:offset + BYTES_PER_FRAME]
    if any(b != 0 for b in frame):
        bram_frames.append((i, frame))

print(f"Non-zero frames: {len(bram_frames)} of {frame_count}")
```

---

## Part 4 — Transferring to Linux and Integration

### Files to Transfer

Create a folder on USB: `r1mx_ise/`

```
r1mx_ise/
  xparameters.h              ← from Part 1 Step 12
  system.mhs                 ← from Part 1 Step 14
  ip_cores/
    xps_uartlite_v*/         ← from Part 2 (full folder)
    xps_uartns550_v*/
    xps_intc_v*/
    xps_emaclite_v*/
    xps_iic_v*/
    xps_pci_v3_v*/
    xps_central_dma_v*/
  docs/
    *.pdf                    ← any PDFs found in C:\Xilinx\10.1\EDK\doc\
  impact/
    fpga_readback.bin        ← from Part 3 (iofpga)
    vpfpga_readback.bin      ← from Part 3 (vpfpga, if performed)
```

### On Linux: Install the Files

```bash
cd ~/src/r1mx/firmware

# Create reference directory for ISE artifacts:
mkdir -p reference/ise10_ip_cores

# Copy xparameters.h:
cp /path/to/usb/r1mx_ise/xparameters.h reference/ise10_xparameters.h

# Archive IP core source:
cp -r /path/to/usb/r1mx_ise/ip_cores reference/ise10_ip_cores/
tar czf reference/ise10_ip_cores.tar.gz -C reference ise10_ip_cores/
rm -rf reference/ise10_ip_cores/  # keep only the archive in git

# FPGA readback:
cp /path/to/usb/r1mx_ise/impact/fpga_readback.bin \
   reverse/build_32/extracted/iofpga_readback.bin

# If vpfpga readback exists:
cp /path/to/usb/r1mx_ise/impact/vpfpga_readback.bin \
   reverse/build_32/extracted/vpfpga_readback.bin
```

### On Linux: Verify xparameters.h

```bash
# Quick check — all expected defines should be present:
grep -E "XPAR_(UARTLITE|UARTNS550|INTC|EMACLITE|IIC|PCI|DMA)" \
    firmware/reference/ise10_xparameters.h
```

### On Linux: Cross-Reference with Firmware Config Structs

The firmware embeds compiled copies of these defines in its data section. Verify they match:

```bash
# Check UartLite baud rate (expected: 0x0001C200 = 115200):
python3 -c "
import struct
d = open('firmware/reverse/build_32/extracted/software.bin','rb').read()
# Config struct is at file offset 0xe005dc (= VA 0xe005dc, flat load at 0)
off = 0xe005dc
print('DeviceId:', hex(struct.unpack_from('>H', d, off)[0]))
print('Base:', hex(struct.unpack_from('>I', d, off+4)[0]))
print('BaudRate:', struct.unpack_from('>I', d, off+8)[0])
print('DataBits:', struct.unpack_from('>I', d, off+12)[0])
"
# Expected: Base=0xe0600000, BaudRate=115200, DataBits=8

# Check XIntc config (expected: Base=0xe0800000, 32 inputs):
python3 -c "
import struct
d = open('firmware/reverse/build_32/extracted/software.bin','rb').read()
off = 0xe003f4
print('DeviceId:', hex(struct.unpack_from('>H', d, off)[0]))
print('Base:', hex(struct.unpack_from('>I', d, off+4)[0]))
print('NumIntr:', struct.unpack_from('>I', d, off+8)[0])
"
# Expected: Base=0xe0800000, NumIntr=32
```

### On Linux: Update MMIO Map Documentation

After verifying the data, update `re_reference.md` Section 6:

1. Change any `❓` or `🔵` entries to `✅ Confirmed` if xparameters.h agrees
2. Update the DMA base address entry if 0x64010000 was wrong
3. Note which bus XIic and DMA are on (PLB vs OPB)
4. Add a note at the top: "Confirmed against ISE 10.x xparameters.h [date]"

### On Linux: Update QEMU Machine Source

The QEMU machine source is at:
```
firmware/patches/qemu/src/hw/ppc/r1mx_virtex4.c
```

After confirming xparameters.h values, check that the MMIO stubs in the QEMU machine
use the correct addresses. The current addresses should already match, but verify:
- UartLite at `0xe0600000`
- XIntc at `0xe0800000`
- XEmacLite at `0xe1020000`
- Any addresses that xparameters.h corrected should be fixed in the QEMU machine

---

## Quick Reference: What xparameters.h Answers

| Question | xparameters.h define | Expected value |
|----------|---------------------|----------------|
| PLB bus clock | `XPAR_PLB_FREQ` | 100,000,000 |
| CPU clock | `XPAR_CPU_PPC405_CORE_CLOCK_FREQ_HZ` | 300,000,000+ |
| UartLite baud | `XPAR_UARTLITE_0_BAUDRATE` | 115200 |
| XIntc interrupt lines | `XPAR_INTC_0_NUM_INTR_INPUTS` | 32 |
| XIic bus type | which `XPAR_` prefix | PLB or OPB |
| DMA real address | `XPAR_DMA_CHANNEL_0_BASEADDR` | 0x64010000? |
| EthernetLite ping-pong | `XPAR_EMACLITE_0_TX_PING_PONG` | 1 |
