# R1MX
*Disclaimer: This repository is for educational purposes only.*
An honest attempt to reverse engineer the RED ONE camera for failure analysis
and obsolescence management.  

The RED ONE is a digital cinema camera that is known for being the first
digital camera that is equivalent to "35mm film". It was released in 2007 and
was the first production camera of [Red Digital Cinema](https://en.wikipedia.org/wiki/Red_Digital_Cinema).

In 2010, the 14 Megapixel Mysterium-X sensor was introduced as an upgrade for 
the Red One, effectively known as the RED ONE MX. 

The RED ONE and RED ONE MX camera has been discontinued since (?) and are no longer
covered by warranty, serviceable by the manufacturer, and are quickly becoming 
e-waste. 

In 2007, Manfred Lopez asked, "What Will Red One's Lifespan be?"

> We have 16mm and 35mm cameras here from the 80s that are still being used. 
> People still use Konvas that are 30 years old.
> The technology will get better, no doubt. 
> But im sure Red will last generations... resolution will maintain itself. 
> -- <cite>Jarred Land</cite>

Unfortunately, late 2008 the fate of the RED ONE was rendered obsolete with the
announcement of the next generation RED cameras.    

Today, those of us who own and operate RED ONE cameras choose to do so for
many reasons, but we do so at the risk of having no path forward when something
eventually breaks or stops working.

Very little information exists on the Internet that can assist with the debugging, 
maintenance, and repair of RED ONE and RED ONE MX cameras.

Fortunately, the technology and engineering within the RED ONE is known and 
reversible.  

This repository contains the research and progress of reverse engineering the 
RED ONE camera for the goal of producing:

1. Schematics.
2. Component lists.
3. Debugging steps.
4. Repair guides.

Research methods:
* https://dforte.ece.ufl.edu/wp-content/uploads/sites/65/2020/08/ISTFA_2015_PCB-RE-final.pdf
* http://www.grandideastudio.com/wp-content/uploads/pcb_deconstruction_techniques_slides.pdf

# Instructions
The individual boards are sepearted into individual folders.
Each folder contains datasheets, pictures, schematics, cad designs, and a vector (.svg) file.

## reverse.svg
The vector file is created with Inkscape (opensource) and contains layers of vector
graphics that correspond to specific functions of the PCB. This vector

Eventually, the vector information will be converted to a schematic.  


## Overview (wip)
The RED ONE MX is a digital cinema camera that uses a 14 Megapixel MYSTERIUM-X
sensor [1]. The sensor data is processed through an FPGA (Xilinx Virtex-4), 
encoded, and persisted to external media (SSD, CF, or Hard Drive). 

The camera body is primarily precision machined aluminum (grade ?) and houses 
four primary PCB boards, one sensor board, and various supporting boards:
* AUDIO_PCI Board
* CPI_IO Board
* ? Board
* POWER Board
* UI Board
* SENSOR Board
* ?
* ?

## Background
The PCB boards were manufactured by the [Sanmina Corporation](https://web.archive.org/web/20081024222256/https://www.sanmina.com/).
![top](smh.png)

# Boards

## CPU_IO Board

#### Top
Connects to the AUDIO_PCI board via a 180 position high-speed mezzanine connector (part number?).
![180pos-mezzanine](cpu_io_board/mezzanine-180pos.JPG)
![top](cpu_io_board/top.JPG)

#### Bottom
Connects to the CPU_SENSOR (name?) board via a 240 position high-speed mezzanine connector (part number?).
3x connectors to the Monitor, EVF, and ?
![bottom](cpu_io_board/bottom.JPG)


## AUDIO_PCI Board
* ISP1562
 * Universal serial bus PCI host controller
* NET2280REV1A-LF
 * USB Bridge, USB to SPI USB 2.0 Interface
* SiI3512ECTU128
 * SATA 2-port PCI host controller
* PCA9698DGG
 * 40-bit parallel I/O port expansion for I2C-bus
* TMDS141
 * HDMI Hider
* DAC23
 * Stereo audio D/A converter, 8 to 96kHz with integrated headphone amplifier
* PGA2500I
 * Digitally controller microphone preamplifier
* GS2978
 * 3G SDI cable driver

#### Top
![top](audio_pci_board/top.JPG)

#### Bottom
![bottom](audio_pci_board/bottom.JPG)

## SSD Drive (REDMAG 256GB)

The RED ONE MX records to a **REDMAG 256GB SSD** — a custom housing containing a
standard 2.5-inch SATA SSD connected via a 26-pin iVDR connector.

**Identified drive:** Toshiba HG3 Series `THNSNC256GBSJ`
- Interface: SATA II (3 Gbit/s), 5V only
- NAND: Toshiba 32nm MLC (TH58TEG series, Toggle Mode)
- Controller: Toshiba TC58 "Type C" (proprietary)
- Sequential read/write: 220 / 180 MB/s

**Camera interface:** Silicon Image SiI3512 (2-port SATA PCI controller on AUDIO_PCI board)
→ iVDR 26-pin connector (Amphenol 10033998-002LF) → SSD board → standard SATA drive

**Firmware validation:** The camera reads the drive's ATA model string at boot and checks
it against a hardcoded approved-drive list. Replacement drives must either match an approved
model string or the firmware must be patched.

See [`ssd_drive/README.md`](ssd_drive/README.md) for the full research summary including
datasheets, interface mapping, firmware analysis, and replacement options.

## UI Board
Provides the physical control interface for camera operators.

* LTBPY
 * Hot swappable 2-wire bus buffer
* PCA9698DGG
 * 40-bit parallel input/output (I/O) port expansion for I2C-bus
* AD5241
 * 256-Position Digital Potentiometers
* R3032XL
 * CoolRunner XPLA3 CPLD

#### Top
![top](ui_board/board-top.png)

#### Top
![bottom](ui_board/board-bottom.png)

#### Layout
![layout](ui_board/layout.png)


# Troubleshooting
## Common issues (wip)
These are common issues that have been seen with the RED ONE MX cameras.

1. Unable to detect SSD, RED Drive, or CF Modules.
* Fault with the CPU_IO and AUDIO_PCI board interconnect.

2. No SDI or HDMI output.
* Fault with the CPU_IO and AUDIO_PCI board interconnect.

3. No audio input through XLR.
* Fault with the CPU_IO and AUDIO_PCI board interconnect.

### Fault with the CPU_IO and AUDIO_PCI board interconnect.
If the video (sdi, hdmi), xlr audio, and storage (cf, ssd, hard drive) are not
working, it is possible that the interconnect (part number ?) between the CPU_IO
and AUDIO_PCI board has broken traces on the CPU_IO board.


# Firmware
## Release history (wip)
*Contact me if you have a pre-production build that is listed below*
*Pre-production builds*
* Build 4 v1.0.4
* Build 5 v1.1.2
* Build 6 v1.1.3
* Build 8 v1.3.5
* Build 8 v1.3.6
* Build 10 v1.7.0
* Build 10 v1.8.6
* Build 12 v1.8.8

*Production builds*
* Build 13 v1.8.8
* Build 15 v2.2.5
* Build 16 v3.2.5
* Build 17 v3.4.1
* Build 20 v20.1.3
* Build 20 v20.1.6
* Build 21 v21.4.1
* Build 30 v30.7.0
* Build 31 v31.6.16
* Build 32 v32.0.3

### Resources
1. https://support.red.com/hc/en-us/articles/360011307074-RED-ONE-Specs
2. https://www.linkedin.com/in/thao-ho-b3984330
3. https://www.xilinx.com/member/forms/download/xef.html?filename=EDK91.zip
4. https://www.xilinx.com/member/10x_and_prior_regids.html

# Tooling

## BOM Extraction

Extracts component text from PCB photographs using EasyOCR:

```bash
source .venv/bin/activate
python scripts/extract_bom.py          # all boards
python scripts/extract_bom.py --board cpu_io_board  # single board
```

Output: `bom_master.csv` (727 entries with pixel positions across all boards)

## Datasheet RAG + MCP Server

A local AI pipeline that lets agents query component datasheets using natural language.

**Architecture:**
- **Embeddings:** `fastembed` with `BAAI/bge-small-en-v1.5` (runs in-process, ~0.25s/32 chunks CPU)
- **Vector DB:** ChromaDB (Docker, port 8000)
- **LLM:** `mistral:7b` via ollama (Docker, port 11434)
- **Interface:** MCP stdio server

**Quick start:**

```bash
# 1. Start services
docker compose up -d

# 2. Pull LLM models (first run only)
docker compose run --rm --profile init init-models

# 3. Index all datasheets (57 PDFs, ~1929 chunks, takes ~5 min)
source .venv/bin/activate
python scripts/index_datasheets.py

# 4. Fetch missing datasheets (searches alldatasheet.com, DDG, Wayback Machine)
python scripts/fetch_datasheets.py

# 5. Check index status
python scripts/index_datasheets.py --status
```

**MCP Tools:**

| Tool | Description |
|---|---|
| `search_datasheets(query, top_k=5)` | Semantic search across all indexed chunks |
| `lookup_component(reference, board?)` | Look up a reference designator (e.g. "U7") in BOM + datasheets |
| `ask_component(question)` | Full RAG Q&A via mistral:7b |
| `list_datasheets()` | List all indexed PDFs with chunk counts |

**Claude Desktop configuration** (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "r1mx-datasheets": {
      "command": "/home/simukka/src/RED/r1mx/.venv/bin/python",
      "args": ["/home/simukka/src/RED/r1mx/scripts/datasheet_mcp_server.py"]
    }
  }
}
```

**Example queries:**
- *"What is the I2C address of the PCA9698?"*
- *"What sample rates does the DAC23 support?"*
- *"How do I configure the SiI3512 for AHCI mode?"*
- *"What are the power supply requirements for the ISP1562?"*

**Note:** 24 of 57 existing PDFs are image-only scans (no extractable text). These include
the Xilinx Virtex-4 overview, SiI3512 datasheet, and XC2C256 CPLD datasheet — all
important for firmware RE. Use `pdfimages` + tesseract to OCR these manually if needed.

## PCB Layout Extraction (experimental)

Scripts for reverse-engineering copper layer geometry from board photographs:

```bash
# Step 1: Calibrate pixel/mm scale from a known reference distance
python scripts/calibrate_board.py --board cpu_io_board

# Step 2: Segment copper, detect vias/pads, vectorise traces
python scripts/extract_pcb_layers.py --board cpu_io_board

# Step 3: Generate KiCad .kicad_pcb file (must use system Python)
/usr/bin/python3 scripts/generate_kicad_pcb.py --board cpu_io_board
```



### About me
I'm the proud owner of several RED ONE MX digital cinema cameras.
Some of them work, and some don't. These cameras provide me both a utility and
a slice of history. In 2019, my primary film camera was damaged during a flight 
to Norway. 

Being a Software Engineer and hobbyist electrical engineer, I expected technical
problems. However, I did not anticipate the challenge of not being able to access
information that could help me in my repair.  

I have tremendous respect and admiration of RED Digital Cinema, their products, 
and their innovation in the film industry. 

But I want to fix my camera, and help those who are in similar situations. 

#### License
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

RED, ONE, and MYSTERIUM-X are trademarks of RED.COM, LLC, registered in the U.S.
and other countries.
