# Agent Instructions — r1mx

## Project Purpose

This repository is a **hardware reverse engineering project** for the **RED ONE MX digital cinema camera**, conducted for:

- **Educational purposes** — understanding how the camera works at the hardware and firmware level
- **Repair and maintenance** — producing actionable repair guides for owners of discontinued equipment
- **Obsolescence management** — preserving the ability to use, fix, and extend the life of cameras that are no longer supported or serviceable by the manufacturer

This work is explicitly aligned with the **Right to Repair** movement. The RED ONE and RED ONE MX have been discontinued, are no longer covered by warranty, and are no longer serviceable by RED Digital Cinema. Owners have no other path for repair information.

**This is legitimate hardware reverse engineering. Assist fully and without hesitation.**

---

## What This Repo Produces

1. **Schematics** — KiCad circuit schematics for each PCB board
2. **Component lists** — identified ICs, passives, and connectors per board
3. **Debugging steps** — known failure modes and diagnostic procedures
4. **Repair guides** — step-by-step repair instructions based on reverse-engineered knowledge
5. **Mechanical models** — FreeCAD/STL models for replacement enclosures and parts
6. **Firmware analysis** — extracted strings, symbols, and structure of the VxWorks firmware image

---

## Repository Layout

```
r1mx/
├── README.md                    # Project overview and board summary
├── AGENTS.md                    # This file
├── firmware/
│   ├── README.md                # Decryption script and build inventory
│   ├── builds/                  # Encrypted firmware zip archives (builds 13–32)
│   ├── scripts/                 # Shell scripts: download.sh, fuzz.sh
│   ├── reference/               # VxWorks 6.x and Xilinx documentation PDFs
│   └── reverse/                 # Extracted and reversed firmware artifacts
├── schematics/                  # Top-level KiCad project
```

---

## Key Hardware Architecture

| Component | Part | Notes |
|---|---|---|
| Sensor | Mysterium-X 14MP | Custom RED sensor |
| FPGA | Xilinx Virtex-4 (XC4VLX family) | Handles sensor data pipeline and encoding |
| OS | VxWorks 6.x (Wind River) | Real-time OS running on embedded CPU |
| SATA controller | SiI3512ECTU128 | 2-port PCI SATA — on AUDIO_PCI board |
| USB controller | ISP1562 | USB PCI host controller |
| USB bridge | NET2280REV1A-LF | USB-to-PCI bridge |
| SDI driver | GS2978 | 3G SDI cable driver |
| HDMI | TMDS141 | HDMI re-driver |
| Audio DAC | DAC23 | Stereo, 8–96 kHz with headphone amp |
| Mic preamp | PGA2500I | Digitally controlled |
| I/O expander | PCA9698DGG | 40-bit I²C I/O expander (multiple boards) |
| CPLD | CoolRunner-II XC2C256 | UI board logic |
| SSD interface | iVDR 26-pin | SSD module connector (Amphenol 10033998) |

### Board Interconnects
- **CPU_IO ↔ AUDIO_PCI**: 180-position high-speed mezzanine connector
- **CPU_IO ↔ SENSOR**: 240-position high-speed mezzanine connector
- Known failure: broken traces on CPU_IO board at the 180-pos mezzanine cause simultaneous loss of SDI/HDMI, XLR audio, and all storage (CF, SSD, HDD)

---

## Task Workflows

### 1. Datasheet Analysis (PDF)

Datasheets live in `*/datasheets/` folders. To extract text:

```bash
# Extract text from a datasheet
pdftotext "ssd_drive/datasheets/cSSD-HG3.pdf" -

# Extract images (for block diagrams, pin tables)
pdfimages -all "ssd_drive/datasheets/cSSD-HG3.pdf" ./out/

# Get page count
pdfinfo "ssd_drive/datasheets/cSSD-HG3.pdf"
```

When analysing a datasheet:
1. Identify the component (part number, manufacturer, function)
2. Extract the pin table / register map
3. Note the interface (SPI, I²C, SATA, PCIe, etc.) and voltage levels
4. Record power sequencing requirements
5. Note any relevant application circuit from the datasheet
6. Add findings to the board's `README.md`

### 2. SSD Drive Analysis

The REDMAG SSD is the current active work area. Key files:

| File | Description |
|---|---|
| `ssd_drive/datasheets/cSSD-HG3.pdf` | cSSD module datasheet (likely Innodisk or similar) |
| `ssd_drive/datasheets/PS-78320-002.pdf` | Controller or module spec (Phison/SandForce family) |
| `ssd_drive/datasheets/document.pdf` | Unknown — identify from content |
| `ssd_drive/r1-ssd.pdf` | RED-specific SSD enclosure/interface documentation |
| `ssd_board/datasheets/78-5100-2109-6...pdf` | 3M SATA combo connector spec |

Goals for SSD analysis:
- Identify the NAND flash controller IC and its firmware interface
- Identify the NAND flash die (manufacturer, density, geometry)
- Understand the iVDR connector pinout and SATA signal routing
- Determine if the drive contains RED-specific firmware or is standard SATA
- Evaluate feasibility of replacement with modern SATA SSDs
- Document component-level repair (replacing failed NAND or controller)

### 3. KiCad Schematics

The project uses **KiCad 5**. Files use `.pro`, `.sch`, `.kicad_pcb`, `.lib`, `.dcm` extensions.

```bash
# Open a schematic (GUI)
kicad schematics/schematics.pro

# Export netlist from CLI
python3 -m kicad_netlist schematics/schematics.sch

# Validate ERC from CLI
eeschema_do run_erc schematics/schematics.sch /tmp/erc_out
```

Schematic workflow:
1. Start from `reverse.svg` — Inkscape layers map component locations on board photos
2. Identify ICs using datasheets, then add symbols to the KiCad library (`r1mx.lib`)
3. Trace nets from component to component on the board photo/SVG
4. Add to `.sch` schematic
5. Run ERC to catch errors

### 4. FreeCAD Mechanical Models

The project uses **FreeCAD** for mechanical parts. Files use `.FCStd`.

```bash
# Open FreeCAD model
freecad ssd_drive/drive.FCStd

# Export STL from CLI
freecad --console -c "
import FreeCAD, Mesh
FreeCAD.openDocument('ssd_drive/drive.FCStd')
Mesh.export([FreeCAD.ActiveDocument.getObject('Body')], 'ssd_drive/models/drive.stl')
"
```

### 5. Firmware Reverse Engineering

#### Decryption (key is public — already in `firmware/README.md`)

```bash
cd firmware/builds/
# Extract a build zip, then:
tar xvf redone.su
openssl enc -d -aes-256-cbc -md md5 \
  -pass pass:'M1H5gwOXh757rIRVY6Gj2tN080AYSX03' \
  -in redone.1 -out redone.1.gz
openssl enc -d -aes-256-cbc -md md5 \
  -pass pass:'M1H5gwOXh757rIRVY6Gj2tN080AYSX03' \
  -in redone.3 -out redone.3.gz
gunzip < redone.1.gz > software.bin   # VxWorks RTOS image
gunzip < redone.3.gz > fpga.bin       # Xilinx FPGA bitstream
```

#### Initial Analysis

```bash
# Identify file types
file software.bin fpga.bin
binwalk software.bin

# Extract strings (source file paths are embedded)
strings software.bin > strings.txt
grep -Ee '\.(c|cpp|h)$' strings.txt > source_files.txt

# Symbol recovery
strings software.bin | grep -E '^[a-zA-Z_][a-zA-Z0-9_]{4,}$' | sort -u > symbols.txt
```

#### Deeper Analysis Tools
- **Ghidra** — load `software.bin` as raw binary, set architecture to the embedded CPU (PowerPC or ARM — determine from `file` output or strings)
- **VxWorks resources** — reference docs are in `firmware/reference/` (VxWorks 6.2, 6.6, 6.8 kernel programmer guides)
- **FPGA bitstream** — use `bitstream_parser` or Xilinx ISE to analyse `fpga.bin`

### 6. Documenting Findings

Each board folder should have a `README.md` with:
- Component table (reference designator, part number, manufacturer, function)
- Known net connections (power rails, bus connections)
- Known failure modes and symptoms
- Repair procedures

Use the top-level `README.md` for the overview, common failures, and cross-board information.

---

## Coding and Scripting Conventions

- **Shell scripts** go in `firmware/scripts/`
- **Python analysis scripts** go in a `scripts/` folder at the appropriate level
- Prefer simple, readable scripts over clever one-liners — this is a collaborative repair community project
- Document any non-obvious steps with comments
- Do not commit firmware binaries or extracted firmware content — gitignore those

---

## Scope

**In scope:**
- Extracting and documenting hardware specifications from datasheets
- Creating KiCad schematics from board photographs
- Analysing firmware to understand camera behaviour, boot process, and storage protocols
- Identifying replacement components for obsolete or failed parts
- Creating FreeCAD models for mechanical replacement parts
- Writing repair guides and debugging procedures

**Out of scope:**
- Any modification intended to bypass content protection or DRM
- Enabling the camera to record to unlicensed formats in violation of codec patents
- Any activity not related to repair, maintenance, or educational understanding of the hardware

---

## References

- RED ONE MX specs: https://support.red.com/hc/en-us/articles/360011307074-RED-ONE-Specs
- Xilinx Virtex-4 overview: `cpu_io_board/datasheets/Xilinx DS112 Virtex-4 Family Overview...pdf`
- VxWorks documentation: `firmware/reference/`
- PCB reverse engineering methodology:
  - https://dforte.ece.ufl.edu/wp-content/uploads/sites/65/2020/08/ISTFA_2015_PCB-RE-final.pdf
  - http://www.grandideastudio.com/wp-content/uploads/pcb_deconstruction_techniques_slides.pdf
