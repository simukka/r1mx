# VP-FPGA Config Readback Procedure

**Target:** the second `XC4VFX100` on the **video_processor_board** (IDCODE `0x01ee4093`,
single-device JTAG chain, IR len 14, max TCK 33 MHz).

## Why this is worth doing

The VP-FPGA design is the **only camera design we don't already have**:

- **Not in `redone.su`** — `redone.3` decrypts to a bitstream that is **byte-identical to
  `fpga.bin`** (the *iofpga*), confirmed by sha256. The package ships only software + iofpga.
- **Not raw in `software.bin`** — 0 occurrences of the Virtex sync word `aa995566`.
- The live VP-FPGA reports config **unencrypted** (status reg: Decryptor security = 0,
  DONE = 1, mode pins M2:M1:M0 = 110 slave). So a JTAG readback yields **plaintext** frames.

## Safety (read-only — see debug_interfaces.md §7)

- Single-device chain. **Measure Vref before connecting.** Never Program / Erase / Blank Check.
- Readback is non-destructive and does **not** stop the FPGA. Confirm the Status Register first
  (DONE = 1, Decryptor security = 0) — already done 2026-06-05.

## The obstacle

iMPACT only offers **Readback** on an SRAM FPGA once a `.bit` is assigned **and** it finds the
companion mask `<basename>.msk` in the same folder. With `fpga.bit` alone we saw only **Program**.
Key fact that makes a stand-in legal: **readback geometry (frame count, frame length) is a
property of the *device*, not the design.** Both FX100s are identical, so our existing
`fpga.bit` is a valid stand-in — iMPACT uses only its device geometry; Readback reads the actual
VP silicon's frames.

Staged files (already on `Y:`):
- `firmware/reverse/build_32/extracted/fpga.bit` — XC4VFX100 stand-in (from `fpga.bin` via `bin2bit.py`)
- `firmware/reverse/build_32/extracted/fpga.msk` — zero mask, same length, to unlock Readback

---

## Method A — iMPACT GUI readback (primary)

> **Status 2026-06-05: NOT viable as-is.** The fabricated zero `fpga.msk` did **not** unlock the
> Readback menu in iMPACT 10.1 — it requires genuine bitgen readback files (`.msk`/`.rbb`) derived
> from the original `.ncd`, which we don't have. Keep the steps for reference, but the real path is
> **Method B (raw JTAG)** or **Method C (offline)**.

1. Move the cable to the **video_processor_board** header; measure Vref; iMPACT → **Initialize
   Chain** (expect the single `xc4vfx100`, IDCODE `01ee4093`).
2. Double-click it → **Assign New Configuration File** → `Y:\r1mx\firmware\reverse\build_32\extracted\fpga.bit`.
   Decline SPI/BPI PROM, **BMM**, and **ELF** prompts (read-only; we never program).
3. Confirm `fpga.msk` is in that same `extracted\` folder (iMPACT auto-finds it and unlocks
   Readback/Verify).
4. Right-click the device → **Readback** → save to
   `Y:\r1mx\components\video_processor_board\vpfpga_readback.bin` (prefer `.bin`; `.rbt` ASCII also OK).
5. **Do NOT click Program.** Transfer the file to Linux.

*If Readback still doesn't appear* (mask length mismatch): regenerate `fpga.msk` to the device's
exact readback length and retry; if it still refuses → Method B.

Expected: ~4.1 MB output, beginning with a pad frame of zeros then real frame data.

---

## Method B — raw JTAG readback (fallback)

Drive the documented Virtex-4 readback sequence directly (via an SVF played in iMPACT, or an
open JTAG tool). Outline — **verify exact opcodes against Xilinx UG071 "Readback" before driving**
(read-only, so a wrong sequence merely fails):

1. JTAG instruction **CFG_IN**, shift in (32-bit words):
   `FFFFFFFF` dummy · `AA995566` sync · `20000000` NOP ·
   write **CMD**=RCRC (`30008001`,`00000007`) · write **FAR**=0 (`30002001`,`00000000`) ·
   write **CMD**=RCFG (`30008001`,`00000004`) · NOP ·
   **FDRO** read packet: Type-1 read reg 0x03 count 0 (`28006000`) + Type-2 read with
   `word_count` = device readback length.
2. JTAG instruction **CFG_OUT**, shift out `word_count × 32` bits → capture TDO = frame data.

Config registers: FAR `0x01`, FDRO `0x03`, CMD `0x04`. CMD ops: RCFG `0x04`, RCRC `0x07`.
`word_count` for XC4VFX100 ≈ full config array (~1.03M words, 41-word frames) — prefer the
iMPACT-derived length.

---

## Method C — offline avenues (no hardware; pursue in parallel)

1. **roFs gzip scan:** the VP bitstream may be stored gzipped (like `redone.3`) inside
   `software.bin`. Scan for `1f8b` members, decompress, grep for `aa995566`:
   ```bash
   python3 - <<'PY'
   d=open('firmware/reverse/build_32/extracted/software.bin','rb').read()
   import zlib,struct
   i=0
   while True:
       i=d.find(b'\x1f\x8b\x08',i)
       if i<0: break
       try:
           dec=zlib.decompress(d[i:], 16+zlib.MAX_WBITS)
           if b'\xaa\x99\x55\x66' in dec[:64]:
               print(f"BITSTREAM gzip @0x{i:x} -> {len(dec)} bytes")
       except Exception: pass
       i+=1
   PY
   ```
2. **NOR flash dump** (working camera): `xmd_dump.tcl` the flash region, then scan for the VP
   bitstream — it is pushed into the VP-FPGA via slave SelectMAP from somewhere CPU-accessible.
3. **SelectMAP capture:** on a working camera, halt during VP config load and dump the source
   buffer from CPU DDR.

---

## Post-processing (Linux)

1. Strip the leading **pad frame** (one Virtex-4 frame = 41 words = 164 bytes of zeros).
2. Align frames; data carries configured LUT/routing + BRAM state.
3. **Verify it's the VP design:** sha256 must **differ** from `fpga.bin` (else it's accidentally
   the iofpga).
4. Analyze: Virtex-4 has no Project X-Ray DB — use ISE `FPGA_Editor` / `xdl`, or TORC, on the
   reconstructed config. **BRAM** (calibration / coefficient tables) is extractable from block-type
   `010` frames (FAR layout per `ise10_guide.md` Part 3, Step 8).

## Outputs
- `components/video_processor_board/vpfpga_readback.bin` — raw readback
- (derived) reconstructed VP bitstream + extracted BRAM tables
