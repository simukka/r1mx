---
title: "Inside the FPGA"
summary: "The firmware is not the whole story. The IO-FPGA bitstream contains 25,170 frames of configuration data — hiding four blocks of high-entropy content that are almost certainly color pipeline coefficients."
tags: [fpga, bram, reverse-engineering]
---

The RED ONE MX advertisement said "cinema-quality color." What it did not say — because no manufacturer says this — is: the color science is baked into the FPGA bitstream, initialized once at power-on from configuration data that we have never documented, which you cannot read, which we will never release, and which will disappear from support infrastructure on a timeline we have not disclosed.

The image looks the way it does because someone made choices. Choices about tone mapping, gamut, highlight rolloff, shadow behavior. Choices encoded in floating-point coefficients, baked into lookup tables, hardwired into the Virtex-4 fabric before the camera ever shipped. Those choices are the aesthetic of the RED ONE MX. They're why cinematographers chose it over the alternatives. They're why films shot on this camera have a particular look that still holds up.

Those choices are sitting in a 4.1-megabyte bitstream file that has been in the firmware archive since the beginning. Nobody looked at it until now.

---

## The Bitstream

The IO-FPGA bitstream ships inside the upgrade package as `redone.3` — AES-encrypted alongside the PPC firmware. Once decrypted, it's a raw Xilinx Virtex-4 bitstream. Unencrypted. Readable.

```bash
# The bitstream lives alongside software.bin after extraction
ls -lh firmware/reverse/build_32/extracted/
# -rw-r--r--  9.8M  software.bin     (PPC firmware)
# -rw-r--r--  4.1M  fpga.bin         (IO-FPGA bitstream)
```

Virtex-4 bitstreams are organized as fixed-width frames — configuration records transmitted sequentially to program the device. For the XC4VFX100:

- Frame width: 41 × 32-bit words = **164 bytes**
- Frame data starts at file offset `0x1278` (after the sync word and header packets)
- Total frames: **25,170**

```bash
# Run the BRAM extraction script — Phase 0 verifies geometry, Phase 1 extracts content
python3 firmware/scripts/fpga_bram_extract.py \
  firmware/reverse/build_32/extracted/fpga.bin \
  --outdir firmware/reverse/build_32/fpga_io/bram/
```

The script is documented in its header: [`fpga_bram_extract.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/fpga_bram_extract.py). It parses the Type2 FDRI packet, walks all 25,170 frames, identifies BRAM data frames by structural signature, and extracts each non-zero block as a raw blob.

---

## Frame Geometry and the BRAM Boundary

The first ~19,000 frames configure CLB (Configurable Logic Block) fabric — the LUTs, flip-flops, and routing that implement the custom RED IP blocks at `0xE0080000`–`0xE0200000`. The remaining frames configure BRAM.

A structural invariant emerges immediately:

```
word[20] = 0x00000000 in 100% of BRAM frames
word[20] varies        in  CLB frames
```

Zero. Every BRAM frame. Not occasionally — always. This is a bit-position artifact of how Virtex-4 encodes BRAM frame data versus CLB frame data. It's a cheap classifier: if `word[20]` is zero, you're in BRAM territory.

14 of the 18 BRAM columns in the FX100 are all-zero: initialized to `INIT=0x0...0`, 36 bits wide, every bit cleared. These are blank — memory that the firmware will write at runtime. They're the camera's working RAM for the image pipeline.

---

## The Four Non-Zero Blocks

Four blocks contain real data. Frames `22024`, `22088`, `22152`, `22216`:

```bash
# After running fpga_bram_extract.py:
ls -lh firmware/reverse/build_32/fpga_io/bram/
# -rw-r--r--  8.2K  bram_frame_22024.bin
# -rw-r--r--  8.2K  bram_frame_22088.bin
# -rw-r--r--  8.2K  bram_frame_22152.bin
# -rw-r--r--  8.2K  bram_frame_22216.bin

# Entropy analysis on each block
python3 - <<'EOF'
import math, struct
from pathlib import Path

for f in sorted(Path('firmware/reverse/build_32/fpga_io/bram').glob('*.bin')):
    data = f.read_bytes()
    if not any(data): continue
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    n = len(data)
    H = -sum((c/n)*math.log2(c/n) for c in freq.values())
    print(f'{f.name:30s}  entropy={H:.2f} bits/byte  size={n}')
EOF
```

Output:
```
bram_frame_22024.bin          entropy=5.10 bits/byte  size=8192
bram_frame_22088.bin          entropy=6.28 bits/byte  size=8192
bram_frame_22152.bin          entropy=7.18 bits/byte  size=8192
bram_frame_22216.bin          entropy=5.82 bits/byte  size=8192
```

Entropy between 5.1 and 7.2 bits per byte. For reference: fully random data is 8.0 bits/byte, ASCII text is 4–5 bits/byte, structured numeric data like floating-point coefficients or fixed-point lookup tables typically falls in the 5–7 range. Not encrypted. Not readable text. Structured numeric data with non-uniform distribution.

The 64-frame spacing between blocks matches the Virtex-4 BRAM column stride — these are four adjacent BRAM columns in the fabric.

---

## What the Data Probably Is

The RED application maps five custom IP blocks at `0xE0080000`–`0xE0200000`, documented in [`re_reference.md`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/re_reference.md) as "RED histogram IP." But histogram processing doesn't need pre-initialized lookup table coefficients. A display color pipeline does.

The RED ONE MX processes RAW sensor data through a color science transform before outputting to the preview monitors. Those transforms involve multi-dimensional lookup tables — typically 17×17×17 or 33×33×33 grids mapping input RGB triplets to output triplets. At the sizes we see (four 8KB BRAM blocks = 32KB total), a 17³ grid of 3×uint16 entries fits exactly.

The hypothesis: these four BRAM blocks are initialization data for the 3D LUT at the heart of RED's color science. Baked into the bitstream. Loaded by the FPGA configuration, not by firmware at runtime. Present in every camera of this generation, unchanged across every Build 32 upgrade.

---

## What Comes Next

The blobs are in [`firmware/reverse/build_32/fpga_io/bram/`](https://github.com/simukka/r1mx/tree/master/firmware/reverse/build_32/fpga_io/bram/). They're raw — the Virtex-4 BRAM frame encoding interleaves bits from multiple memory cells in a way that doesn't map directly to logical memory order. De-interleaving requires knowing the exact frame address routing for the XC4VFX100, which the Debit device database doesn't include (it only ships LX variants). The options are TORC (the Xilinx bitstream analysis library) or ISE 14.7's `xdl` utility.

This is the next phase. And it matters in a way that goes beyond the technical:

The color science of the RED ONE MX is not proprietary in any useful sense — no patent protects it, RED has moved on to other color pipelines, and the cameras that use it are a decade past their commercial lifecycle. But it exists nowhere in any documented form. It lives only inside these bitstream files, on cameras that are slowly going offline as parts fail and repairs become impossible.

When we de-interleave these frames and read the coefficients, we will know, in precise numeric terms, what the RED ONE MX sees. What the image is actually doing on the way from the sensor to the monitor. Why it looks the way it does.

The cinematographers who made careers with this camera made choices about light and color that were partially mediated by choices someone at RED made in 2009 and encoded in silicon. Those choices can now be recovered. Not because anyone at RED thinks it matters. Because the work that people did with this camera matters, and the tools they used to do it deserve to be understood.

The camera did not fail. The support model did. The image survives.
