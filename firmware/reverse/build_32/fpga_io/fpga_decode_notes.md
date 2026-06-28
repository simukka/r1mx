# FPGA Bitstream Decode Notes — XC4VFX100 IO-FPGA

## Phase 0: Header & Frame Geometry (verified 2026-06-28)

**File:** `firmware/reverse/build_32/extracted/fpga.bin`  
**Size:** 4,133,176 bytes (confirmed)  
**SHA-256:** `497d8f37613b235469666557edc0eadf0d96f8a6f784817284ec0dfdd2827f10`

### Packet Sequence (correcting re_reference.md §21)

| Offset | Packet | Value | Notes |
|--------|--------|-------|-------|
| `0x00` | Sync pad | `FF FF FF FF` | |
| `0x04` | Sync word | `AA 99 55 66` | **Offset is 0x4, NOT 0x55** (typo in §21) |
| `0x0C` | CMD RCRC | — | Reset CRC |
| `0x1C` | COR | `0x000435E5` | |
| `0x24` | **IDCODE** | `0x01EE4093` | **IDCODE IS present** (§21 claimed "no WRITE_IDCODE") |
| `0x2C` | CMD SWITCH | — | |
| `0x38` | MASK | `0x00000600` | |
| `0x40` | CTL | `0x00000600` | PERSIST bit |
| `0x125C` | FAR | `0x00000000` | Start at frame 0 |
| `0x1264` | CMD WCFG | — | Begin frame write |
| `0x1270` | FDRI wc=0 | — | Type2 header follows |
| `0x1274` | Type2 FDRI | wc=1031970 | 4,127,880 bytes = **25170 frames** |
| `0x1278` | **Frame data start** | — | **Used by fpga_bram_extract.py** |

### Frame Geometry (Virtex-4, UG071)

| Parameter | Value |
|-----------|-------|
| Frame size | 41 × 32-bit words = 164 bytes = 1312 bits |
| Total frames | 25170 (1031970 words / 41) |
| Frame data offset | `0x1278` |
| Frame data size | 4,127,880 bytes |

**FAR bit layout (UG071 Table 2-5):**

| Bits | Field | Notes |
|------|-------|-------|
| [26:23] | Reserved | |
| [22] | Top/Bottom | 0=top half, 1=bottom half |
| [21:19] | Block type | 000=CLB/IOB/CLK, 001=BRAM-interconnect, 010=BRAM-data, 011=CFG_CLK |
| [18:14] | Row address | 5 bits |
| [13:9] | Column address | 5 bits |
| [8:7] | Reserved | |
| [6:0] | Minor address | 7 bits (CLB=31 minors, BRAM-int=20 minors, BRAM-data=64 minors) |

---

## Phase 1: BRAM Data Analysis (empirical, 2026-06-28)

### Frame distribution (25170 total)

| Category | Frames | % | Notes |
|----------|--------|---|-------|
| All-zero | 6644 | 26.4% | Empty CLB slices + BRAM INIT=0 |
| High-entropy (>3.5 bits/byte) | 8077 | 32.1% | CLB/routing configuration |
| Low-entropy, non-zero | 3693 | 14.7% | Partially-used slices or BRAM overhead |
| Medium-entropy | remaining | ~27% | Mixed/boundary regions |

### BRAM data block location

From entropy windowing (64-frame windows), the **Block type 010 (BRAM data) section** starts at approximately **frame 19136** and continues to the end of the bitstream (~frame 25170):

- **Frames 0–~18750**: CLB/IOB/CLK/DSP configuration (BT=0) — high entropy
- **Frames ~18750–19135**: Transition zone (BT=1 BRAM interconnect? or CLB tail)
- **Frames 19136–~22015**: **BRAM data, top-half, mostly INIT=0** (~2880 frames = ~45 column-rows)
- **Frames 22016–22270**: **Non-zero BRAM content** (4 sub-blocks — see below)
- **Frames ~22272–25170**: **BRAM data, bottom-half(?), mostly INIT=0** (~2898 frames)

### Structural invariant: BRAM data frame marker

**Critical finding:** In Virtex-4 BRAM data frames (BT=010), word[20] is always 0x00000000.  
This is consistent with UG071 which describes word[20] as the frame center divider in BRAM data frames.

Verified empirically:
- BRAM data region (frames 19136–22015): word[20]=0 in **2880/2880** frames (100%)
- Non-zero BRAM region (frames 22088–22127): word[20]=0 in **40/40** frames (100%)
- CLB region (frames 1000–1099): word[20]=0 in **0/100** frames (0%)

Additional structural zero positions (constant across all BRAM data frames):
- word[2] bits[15:0] = 0x0000 (100% of BRAM frames)
- word[12] bits[15:0] = 0x0000 (100% of BRAM frames)
- word[23] bits[15:0] = 0x0000 (100% of BRAM frames)
- word[33] bits[15:0] = 0x0000 (100% of BRAM frames)

These 96 bits/frame (4×16 + 1×32) are BRAM mode/configuration overhead; the remaining 1216 bits/frame contain actual BRAM data bits.

### Non-zero BRAM sub-blocks

Within the otherwise all-zero BRAM data region, **four sub-blocks** contain non-zero BRAM initialization data:

| Block | Frames | Length | Entropy (active bits) | Popcount | Interpretation |
|-------|--------|--------|-----------------------|----------|----------------|
| B | 22024–22063 | 40 | 5.09 bits/byte | 0.234 | Structured table (65% mono-rising u16) |
| A | 22088–22125 | 38 | 7.17 bits/byte | 0.359 | Dense/random data (3D LUT candidate) |
| C | 22152–22189 | 38 | 7.25 bits/byte | 0.360 | Dense/random data (second 3D LUT?) |
| D | 22216–22253 | 38 | 4.75 bits/byte | 0.177 | Structured table (65% mono-rising u16) |

Saved to `fpga_io/bram/block_{A,B,C,D}_f22*.bin` (active bits only, structural zeros removed).

**Entropy notes:**
- 7.17–7.25 bits/byte is near-maximum entropy → pseudorandom or dense coefficient data
- 65% monotonic-rising u16 pairs in blocks B and D is above random (50%) → possible LUT/ramp portion
- Size (~5000 bytes active per block) consistent with a 1D LUT at 10-12 bit output depth

**Possible BRAM contents in IO-FPGA context:**
- Histogram accumulation tables (RED histogram IP blocks at 0xe0080000–0xe0200000)
- Color science 3D LUT for SDI/HDMI display pipeline
- Gamma correction tables for EVF/OSD output
- Waveform monitor scaling coefficients

### All-zero BRAM columns (14 confirmed)

All of the remaining BRAM data is INIT=0 (default). These 14 blocks of exactly 64 frames each represent BRAMs initialized to all-zeros:

| Blob idx | Start frame | Notes |
|----------|------------|-------|
| [0] | 3616 | Within CLB region? Or scattered BRAM column |
| [1] | 11981 | |
| [2] | 18748 | |
| [3–6] | 19134–19584 | Large cluster (258+64+64 frames = 4× BRAM columns) |
| [7–13] | 20042–24721 | Scattered in BRAM data block |

Note: blobs [0] and [1] appear to be scattered within the CLB region (before frame 19136) which is unexpected if BRAM data is contiguous. These may be either: (a) BRAM data columns that appear out-of-order due to the exact FX100 column layout, or (b) empty CLB regions with all-zero routing configuration.

---

## Round-trip Verification

All candidate blobs pass round-trip verification: raw frame bytes re-extracted from `fpga.bin` using the saved frame indices match the blob files byte-for-byte.

```bash
python3 firmware/scripts/fpga_bram_extract.py --no-blobs
# Phase 0 PASS + 20 blobs verified (0 round-trip errors)
```

---

## Tools

| Tool | Purpose |
|------|---------|
| `firmware/scripts/fpga_bram_extract.py` | Packet parser, entropy scan, blob extractor |
| `firmware/reverse/build_32/fpga_io/bram/frame_entropy.csv` | Per-frame entropy/zero/ASCII flags |
| `firmware/reverse/build_32/fpga_io/bram/bram_index.md` | Blob summary table |
| `firmware/tools/debit/` | Containerized Debit (LX variant DB only — FX100 unsupported) |

---

## Open Issues for Phase 2

1. **Exact FAR sequence for XC4VFX100** not determined — Debit DB only has LX variants, not FX. Need either: (a) TORC with FX100 database, (b) ISE 14.7 `xdl -device_report`, or (c) empirical lock-step alignment.
2. **BRAM bit de-interleaving** not yet implemented: the UG071 bit mapping within 64-frame BRAM columns is needed to recover the exact BRAM INIT values.
3. **Frames 3616, 11981** (scattered all-zero 64-frame runs within the CLB region): need to confirm whether these are truly BRAM data or just empty CLB.
4. **Blocks A, B, C, D** content identification: need firmware cross-reference to confirm which hardware blocks use these BRAMs (histogram IP? colorspace pipeline?).
