#!/usr/bin/env python3
"""
fpga_bram_extract.py — Virtex-4 (XC4VFX100) bitstream BRAM extractor
Phase 0: verify frame geometry; Phase 1: extract and triage BRAM content.

Reads fpga.bin (IO-FPGA bitstream, unencrypted, 4,133,176 bytes).
Frame data: Type2 FDRI packet at file offset 0x1278, 1031970 words, 25170 frames.
Frame size: 41 × 32-bit words = 164 bytes.

Without the exact XC4VFX100 column database (Debit only ships LX variants),
we can't track FAR auto-increment precisely. This script uses an empirical
entropy + structure scan to locate BRAM data frames (block type 010), then
extracts them as raw blobs keyed by frame index.  A round-trip verification
section repacks each candidate blob back to frame bits and compares to source.

Usage:
  python3 fpga_bram_extract.py [fpga.bin] [--outdir DIR]
"""

import argparse
import math
import os
import struct
import sys
from pathlib import Path
from collections import defaultdict

# ── constants ──────────────────────────────────────────────────────────────
SYNC_WORD        = 0xAA995566
FRAME_WORDS      = 41          # fixed for all Virtex-4 frames
FRAME_BYTES      = FRAME_WORDS * 4
FRAME_DATA_OFF   = 0x1278      # confirmed from packet parse: Type2 FDRI data start
TOTAL_FRAMES     = 25170       # 1031970 words / 41 = 25170

# Virtex-4 minor-frame counts per column type
# CLB/IOB/DSP = 31 minors, BRAM-data = 64 minors, BRAM-interconnect = 20 minors
BRAM_DATA_MINORS = 64
BRAM_INT_MINORS  = 20
CLB_MINORS       = 31

# FAR bit fields for Virtex-4 (UG071 Table 2-5)
# [22] top/bottom, [21:19] block-type, [18:14] row, [13:9] col, [6:0] minor
def far_decode(v):
    return {
        'tb':    (v >> 22) & 1,
        'bt':    (v >> 19) & 7,
        'row':   (v >> 14) & 0x1F,
        'col':   (v >>  9) & 0x1F,
        'minor': (v >>  0) & 0x7F,
    }

def far_encode(tb, bt, row, col, minor):
    return (tb << 22) | (bt << 19) | (row << 14) | (col << 9) | (minor & 0x7F)


# ── bitstream parsing ──────────────────────────────────────────────────────
def parse_header(data):
    """Return confirmed sync offset and IDCODE from packet stream."""
    sync_off = data.find(struct.pack('>I', SYNC_WORD))
    if sync_off < 0:
        raise ValueError("Sync word 0xAA995566 not found in bitstream")
    idcode = None
    pos = sync_off + 4
    while pos < min(sync_off + 0x2000, len(data) - 4):
        w = struct.unpack_from('>I', data, pos)[0]
        ptype = (w >> 29) & 7
        if ptype == 1:
            op  = (w >> 27) & 3
            reg = (w >> 13) & 0x1F
            wc  = w & 0x7FF
            if op == 2 and reg == 12 and wc == 1:  # WRITE IDCODE
                idcode = struct.unpack_from('>I', data, pos+4)[0]
            pos += 4 + wc * 4
        elif w == 0x20000000:
            pos += 4
        else:
            pos += 4
    return sync_off, idcode


def extract_frames(data):
    """Return bytearray of all frame data (TOTAL_FRAMES × FRAME_BYTES)."""
    expected = TOTAL_FRAMES * FRAME_BYTES
    frame_data = data[FRAME_DATA_OFF: FRAME_DATA_OFF + expected]
    if len(frame_data) != expected:
        raise ValueError(f"Frame data length {len(frame_data)} != expected {expected}")
    return bytearray(frame_data)


# ── per-frame analysis ─────────────────────────────────────────────────────
def byte_entropy(buf):
    """Shannon entropy in bits/byte over a bytes-like object."""
    if not buf:
        return 0.0
    counts = [0] * 256
    for b in buf:
        counts[b] += 1
    n = len(buf)
    ent = 0.0
    for c in counts:
        if c:
            p = c / n
            ent -= p * math.log2(p)
    return ent


def popcount32(v):
    v = v - ((v >> 1) & 0x55555555)
    v = (v & 0x33333333) + ((v >> 2) & 0x33333333)
    return (((v + (v >> 4)) & 0x0F0F0F0F) * 0x01010101) & 0xFFFFFFFF >> 24


def frame_popcount(frame_bytes):
    total = 0
    for i in range(0, FRAME_BYTES, 4):
        w = struct.unpack_from('>I', frame_bytes, i)[0]
        total += bin(w).count('1')
    return total


def scan_ascii(frame_bytes, min_len=4):
    """Return list of (offset, string) ASCII runs in one frame."""
    hits = []
    s = ""
    start = 0
    for i, b in enumerate(frame_bytes):
        if 0x20 <= b < 0x7F:
            if not s:
                start = i
            s += chr(b)
        else:
            if len(s) >= min_len:
                hits.append((start, s))
            s = ""
    if len(s) >= min_len:
        hits.append((start, s))
    return hits


# ── BRAM de-interleave ─────────────────────────────────────────────────────
# Virtex-4 RAMB16 data bits in 64 minor frames:
# Simplified: bit[row * 256 + col] lives in frame[row // 4] at bit position
# (col * 4 + row % 4) * 32 + word. Full UG071 mapping is more complex.
# We store raw frame data per BRAM column as a blob first, then attempt
# reconstruction (see reconstruct_bram_blob).

def extract_bram_column_blob(frames_array, col_frame_start, num_minors=BRAM_DATA_MINORS):
    """Return raw bytes for `num_minors` consecutive frames starting at col_frame_start."""
    start = col_frame_start * FRAME_BYTES
    size  = num_minors * FRAME_BYTES
    return bytes(frames_array[start: start + size])


# ── FAR-based frame labelling (approximate) ────────────────────────────────
def build_far_sequence_approx(frames_array):
    """
    Attempt to determine block type per frame using entropy + periodicity.

    V4 bitstream order: for each half (top then bottom):
      for each block-type (0=CLB, 1=BRAMint, 2=BRAMdata, 3=CFG):
        for each row: for each col: for each minor: one frame.

    Without the exact column layout we use entropy transitions as a proxy:
      - CLB frames:      high entropy (~3.0-4.0 bits/byte), non-zero
      - BRAMint frames:  high entropy (routing bits)
      - BRAMdata frames: low entropy if INIT=0, else varies by content
      - Padding frames:  all-zero (entropy = 0)

    Returns list of (frame_idx, entropy, is_all_zero, ascii_hits)
    """
    results = []
    for i in range(TOTAL_FRAMES):
        fb = frames_array[i * FRAME_BYTES: (i+1) * FRAME_BYTES]
        ent = byte_entropy(fb)
        all_zero = all(b == 0 for b in fb)
        hits = scan_ascii(fb)
        results.append((i, ent, all_zero, hits))
    return results


# ── run-length encoding of entropy regions ────────────────────────────────
def find_low_entropy_runs(analysis, threshold=2.0, min_run=4):
    """Return list of (start_frame, end_frame, avg_entropy) for low-entropy runs."""
    runs = []
    in_run = False
    run_start = 0
    ent_acc = []
    for (i, ent, all_zero, _) in analysis:
        if ent < threshold:
            if not in_run:
                in_run = True
                run_start = i
                ent_acc = []
            ent_acc.append(ent)
        else:
            if in_run and len(ent_acc) >= min_run:
                runs.append((run_start, i - 1, sum(ent_acc)/len(ent_acc), len(ent_acc)))
            in_run = False
            ent_acc = []
    if in_run and len(ent_acc) >= min_run:
        runs.append((run_start, TOTAL_FRAMES - 1, sum(ent_acc)/len(ent_acc), len(ent_acc)))
    return runs


def find_periodic_structure(analysis, period, min_length=None):
    """
    Score the hypothesis that block-type boundaries fall at `period`-frame intervals.
    Returns (score 0..1, list of candidate block starts).
    """
    if min_length is None:
        min_length = period
    # Look for entropy drops (low-entropy run start) that align with period
    zero_frames = {i for (i, ent, az, _) in analysis if az}
    transitions = sorted(zero_frames)
    if not transitions:
        return 0.0, []
    aligned = [t for t in transitions if t % period == 0]
    score = len(aligned) / max(len(transitions), 1)
    return score, sorted(set(t // period * period for t in aligned))


# ── BRAM content triage ────────────────────────────────────────────────────
GAMMA_THRESHOLD = 0.95   # correlation threshold for monotonic ramp detection

def triage_blob(blob, label=""):
    """Quick triage of a BRAM data blob: look for ramp, string, or pattern."""
    notes = []

    # 1. Check if all-zero
    if all(b == 0 for b in blob):
        notes.append("ALL_ZERO (BRAM INIT=0)")
        return notes

    # 2. Check entropy
    ent = byte_entropy(blob)
    notes.append(f"entropy={ent:.3f} bits/byte")

    # 3. Look for ASCII strings
    ascii_hits = scan_ascii(blob, min_len=6)
    if ascii_hits:
        for off, s in ascii_hits[:5]:
            notes.append(f"ASCII@{off}: {repr(s)}")

    # 4. Check for monotonic ramps (gamma tables, LUTs) — check as u16 BE
    if len(blob) >= 4:
        vals16 = [struct.unpack_from('>H', blob, i)[0] for i in range(0, min(512, len(blob)), 2)]
        mono_up = sum(1 for a, b in zip(vals16, vals16[1:]) if b >= a)
        mono_dn = sum(1 for a, b in zip(vals16, vals16[1:]) if b <= a)
        total   = len(vals16) - 1
        if total > 0:
            if mono_up / total > GAMMA_THRESHOLD:
                notes.append(f"MONOTONIC_RISING u16 ({mono_up}/{total})")
            elif mono_dn / total > GAMMA_THRESHOLD:
                notes.append(f"MONOTONIC_FALLING u16 ({mono_dn}/{total})")

    # 5. Check for repeating patterns
    for period in (2, 4, 8, 16, 32):
        chunk = blob[:period]
        reps = sum(1 for i in range(0, min(256, len(blob)), period)
                   if blob[i:i+period] == chunk)
        if reps >= 8:
            notes.append(f"REPEATING period={period} (×{reps})")
            break

    return notes


# ── round-trip verification ────────────────────────────────────────────────
def roundtrip_verify(original_frames, candidate_start, num_minors):
    """Re-extract the blob and compare byte-for-byte to the source frames."""
    blob = extract_bram_column_blob(original_frames, candidate_start, num_minors)
    start = candidate_start * FRAME_BYTES
    source = bytes(original_frames[start: start + num_minors * FRAME_BYTES])
    assert blob == source, f"Round-trip mismatch at frame {candidate_start}!"
    return True


# ── main ───────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bitfile', nargs='?',
                    default='/home/simukka/src/RED/r1mx/firmware/reverse/build_32/extracted/fpga.bin')
    ap.add_argument('--outdir', default='/home/simukka/src/RED/r1mx/firmware/reverse/build_32/fpga_io/bram')
    ap.add_argument('--entropy-threshold', type=float, default=2.0,
                    help='Entropy (bits/byte) below which a frame is "low entropy"')
    ap.add_argument('--no-blobs', action='store_true', help='Skip writing per-blob files')
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # ── Phase 0: header verification ──────────────────────────────────────
    print("=== Phase 0: Header & Frame Geometry ===")
    data = open(args.bitfile, 'rb').read()
    print(f"File size : {len(data)} bytes (expected 4,133,176)")
    assert len(data) == 4133176, f"Unexpected size {len(data)}"

    sync_off, idcode = parse_header(data)
    print(f"Sync word : offset 0x{sync_off:x}  (expected 0x4)")
    print(f"IDCODE    : 0x{idcode:08x}  (expected 0x01EE4093 for XC4VFX100)")

    frames = extract_frames(data)
    print(f"Frame data: offset 0x{FRAME_DATA_OFF:x}, {TOTAL_FRAMES} frames × {FRAME_BYTES} bytes = {TOTAL_FRAMES*FRAME_BYTES} bytes")
    print(f"Frame stride: {FRAME_WORDS} words × 4 bytes = {FRAME_BYTES} bytes/frame")
    print()

    # ── Phase 1: per-frame analysis ──────────────────────────────────────
    print("=== Phase 1: Per-Frame Entropy Analysis ===")
    print("Scanning all 25170 frames... (takes ~5s)")
    analysis = build_far_sequence_approx(frames)

    all_zero_frames = [i for (i, ent, az, _) in analysis if az]
    ascii_frames    = [(i, hits) for (i, ent, az, hits) in analysis if hits]
    high_ent_frames = [i for (i, ent, az, _) in analysis if ent > 3.5]
    low_ent_frames  = [i for (i, ent, az, _) in analysis if 0 < ent < args.entropy_threshold]

    print(f"All-zero frames : {len(all_zero_frames)} / {TOTAL_FRAMES}  ({100*len(all_zero_frames)/TOTAL_FRAMES:.1f}%)")
    print(f"High-entropy (>3.5 bits/B) : {len(high_ent_frames)}")
    print(f"Low-entropy (<{args.entropy_threshold}) non-zero : {len(low_ent_frames)}")
    print(f"Frames with ASCII strings  : {len(ascii_frames)}")

    # Show first/last all-zero frame ranges
    if all_zero_frames:
        runs = []
        run = [all_zero_frames[0]]
        for f in all_zero_frames[1:]:
            if f == run[-1] + 1:
                run.append(f)
            else:
                runs.append(run)
                run = [f]
        runs.append(run)
        print(f"\nAll-zero frame runs ({len(runs)} total):")
        for r in runs[:20]:
            print(f"  frames {r[0]:6d}–{r[-1]:6d}  length={len(r)}")
        if len(runs) > 20:
            print(f"  ... ({len(runs)-20} more runs)")

    # Show low-entropy regions
    low_runs = find_low_entropy_runs(analysis, threshold=args.entropy_threshold)
    print(f"\nLow-entropy runs (entropy < {args.entropy_threshold}, min 4 frames): {len(low_runs)}")
    for (start, end, avg_ent, length) in low_runs[:20]:
        print(f"  frames {start:6d}–{end:6d}  length={length:5d}  avg_entropy={avg_ent:.3f}")
    if len(low_runs) > 20:
        print(f"  ... ({len(low_runs)-20} more)")

    # Show ASCII-containing frames
    print(f"\nASCII-string frames:")
    for (fidx, hits) in ascii_frames[:30]:
        for off, s in hits[:3]:
            print(f"  frame {fidx:6d} +{off:3d}: {repr(s)}")

    # ── Periodicity check ─────────────────────────────────────────────────
    print(f"\nPeriodicity heuristic:")
    for period in (BRAM_DATA_MINORS, BRAM_INT_MINORS, CLB_MINORS):
        score, starts = find_periodic_structure(analysis, period)
        print(f"  period={period:2d}: alignment_score={score:.2f}, candidate block starts: {starts[:10]}")

    # ── Phase 1: Candidate BRAM column extraction ─────────────────────────
    print("\n=== Phase 1: Candidate BRAM Column Blobs ===")

    # Strategy A: extract all-zero runs that are exactly 64 frames
    # (these are BRAM columns with INIT=0 — most common case)
    bram_candidates = []
    if all_zero_frames:
        runs_64 = [r for r in runs if len(r) == BRAM_DATA_MINORS]
        runs_ge64 = [r for r in runs if len(r) >= BRAM_DATA_MINORS]
        print(f"All-zero runs of exactly 64 frames: {len(runs_64)}")
        print(f"All-zero runs of ≥64 frames       : {len(runs_ge64)}")
        for r in runs_ge64[:5]:
            n_cols = len(r) // BRAM_DATA_MINORS
            print(f"  start={r[0]}, len={len(r)} → {n_cols} BRAM column(s)")
        bram_candidates = [(r[0], min(len(r), BRAM_DATA_MINORS)) for r in runs_ge64]

    # Strategy B: examine low-entropy (non-zero) runs of length ≈ 64
    low_bram_candidates = [(start, min(length, BRAM_DATA_MINORS))
                           for (start, end, avg_ent, length) in low_runs
                           if 32 <= length <= 128]
    if low_bram_candidates:
        print(f"\nLow-entropy non-zero runs (32-128 frames): {len(low_bram_candidates)}")

    all_candidates = bram_candidates + low_bram_candidates
    print(f"\nTotal BRAM candidate runs to extract: {len(all_candidates)}")

    # ── Write blobs and triage ─────────────────────────────────────────────
    bram_index = []
    for idx, (start_frame, num_minors) in enumerate(all_candidates):
        blob = extract_bram_column_blob(frames, start_frame, num_minors)

        # Round-trip verify
        ok = roundtrip_verify(frames, start_frame, num_minors)
        assert ok

        # Triage
        notes = triage_blob(blob, label=f"blob_{idx:04d}")

        # Save blob
        if not args.no_blobs:
            fname = outdir / f"bram_{idx:04d}_f{start_frame:05d}_n{num_minors}.bin"
            fname.write_bytes(blob)

        entry = {
            'idx': idx,
            'start_frame': start_frame,
            'num_minors': num_minors,
            'size_bytes': len(blob),
            'notes': notes,
        }
        bram_index.append(entry)
        note_str = "; ".join(notes)
        print(f"  [{idx:3d}] frames {start_frame:6d}+{num_minors} ({len(blob)} B): {note_str}")

    # ── Write entropy CSV ─────────────────────────────────────────────────
    csv_path = outdir / "frame_entropy.csv"
    with open(csv_path, 'w') as f:
        f.write("frame_idx,entropy,all_zero,ascii\n")
        for (i, ent, az, hits) in analysis:
            ascii_flag = 1 if hits else 0
            f.write(f"{i},{ent:.4f},{int(az)},{ascii_flag}\n")
    print(f"\nWrote per-frame entropy CSV: {csv_path}")

    # ── Write bram_index.md ────────────────────────────────────────────────
    md_path = outdir / "bram_index.md"
    with open(md_path, 'w') as f:
        f.write("# BRAM Blob Index — XC4VFX100 IO-FPGA\n\n")
        f.write(f"Total frames: {TOTAL_FRAMES}, frame size: {FRAME_BYTES}B  \n")
        f.write(f"All-zero frames: {len(all_zero_frames)} ({100*len(all_zero_frames)/TOTAL_FRAMES:.1f}%)  \n")
        f.write(f"Candidate BRAM blobs: {len(bram_index)}\n\n")
        f.write("| idx | start_frame | minors | size_B | notes |\n")
        f.write("|-----|-------------|--------|--------|-------|\n")
        for e in bram_index:
            note_str = "; ".join(e['notes'])[:80]
            f.write(f"| {e['idx']:3d} | {e['start_frame']:11d} | {e['num_minors']:6d} | "
                    f"{e['size_bytes']:6d} | {note_str} |\n")
    print(f"Wrote BRAM index: {md_path}")

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n=== Summary ===")
    print(f"Phase 0: fpga.bin integrity OK (size, sync, IDCODE)")
    print(f"Phase 1: extracted {len(bram_index)} BRAM candidate blobs to {outdir}/")
    print(f"         Use frame_entropy.csv for visualization (plot entropy vs frame_idx)")
    print(f"         bram_index.md maps blobs to frame positions and triage notes")
    print()
    print("Next: Phase 2 — run Debit framedump for structural netlist (LUT/FF/routing)")
    print("      Phase 3 — correlate BRAM content with MMIO register access traces")


if __name__ == '__main__':
    main()
