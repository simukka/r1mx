# R1MX
*Disclaimer: This repository is for educational purposes only.*
An honest attempt to reverse engineer the RED ONE camera for failure analysis
and obsolescence management.

**[View the documentation site](https://simukka.github.io/r1mx/)** &nbsp;|&nbsp; Specifications, components, firmware history, and repair guides.

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

## Setup

### System prerequisites

Install the following packages with your system package manager before creating the Python environment:

```bash
sudo apt install \
    python3 python3-venv \
    kicad \
    tesseract-ocr tesseract-ocr-eng \
    libgl1
```

- **python3 / python3-venv** - Python 3.12 or later
- **kicad** - provides `pcbnew` (the KiCad Python API used by the toolkit); not available on PyPI
- **tesseract-ocr** - OCR engine used by `pytesseract`
- **libgl1** - OpenGL runtime required by OpenCV

### Python environment

The project uses a virtual environment at `.venv/`. Create and populate it once:

```bash
# Create the venv
python3 -m venv .venv

# Install Python dependencies
.venv/bin/pip install -r requirements.txt
```

Then add the KiCad Python bindings to the venv so `import pcbnew` works:

```bash
echo /usr/lib/python3/dist-packages > .venv/lib/python3.12/site-packages/kicad.pth
```

> If your Python version differs, replace `python3.12` with the output of `.venv/bin/python --version`.

### Verify

```bash
.venv/bin/python -c "import cv2, PyQt6, pcbnew, easyocr; print('OK')"
.venv/bin/pytest toolkit/tests/ -q
```

### Running the toolkit

```bash
.venv/bin/python -m toolkit
```

---

## Reverse Engineering

### Decompiling firmware and indexing for semantic search

`firmware/scripts/ghidra_decompile_all.py`
Bulk Ghidra decompiler. Iterates every non-thunk function in software.bin, 
writes 0x{addr:08x}_{name}.c to reverse/build_32/src/all_functions/. 
Adds a metadata comment header with address, size, xref count. 
Supports incremental mode (skip existing files unless DECOMPILE_FORCE=1). 
Run standalone via pyghidra or as an analyzeHeadless postScript.

`firmware/scripts/index_firmware.py` 
ChromaDB indexer. Reads the .c files, chunks by 512 whitespace tokens with 
overlap, embeds via fastembed, upserts to the firmware_functions collection 
with address, function_name, size_bytes, xref_count metadata. 
Fully incremental (SHA256 dedup). 
Run with --status to check progress.

`toolkit/datasheets/mcp_server.py` 
search_firmware(query, top_k=10) for semantic search over decompiled C, 
and lookup_function(name_or_address) which does exact address lookup 
via ChromaDB where filter or semantic name search.

#### Run order:
.venv/bin/pip install -r requirements.txt

1. Seed known symbols (already exists)
python3 firmware/scripts/ghidra_seed_symbols.py

2. Bulk decompile (~2-4 hours)
GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC \
python3 firmware/scripts/ghidra_decompile_all.py

3. Index into ChromaDB (~15-30 min)
python3 firmware/scripts/index_firmware.py

4. Restart MCP server


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
