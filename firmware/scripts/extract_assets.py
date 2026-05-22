#!/usr/bin/env python3
"""
Extract embedded SWF and splash screen assets from software.bin.

Usage:
    python3 firmware/scripts/extract_assets.py [--firmware PATH] [--out DIR]

Outputs:
    <out>/swf_gui_N.swf       All SWF files found in the resource region
    <out>/splash_mx.raw       Mysterium-X splash screen (decompressed)
    <out>/splash_orig.raw     Original RED ONE splash screen (decompressed)
    <out>/splash_mx.gz        Raw gzip blob (for patching back)
    <out>/splash_orig.gz      Raw gzip blob (for patching back)
"""
import argparse
import gzip
import pathlib
import struct
import sys

FIRMWARE_DEFAULT = "firmware/reverse/build_32/extracted/software.bin"
OUT_DEFAULT = "firmware/reverse/build_32/assets"

# Known primary SWF offsets (from re_reference.md §20)
KNOWN_SWFS = [
    (0x9E03BC, "swf_gui_1"),
    (0xB24EF8, "swf_gui_2"),
]

# Known splash gzip offsets and names
KNOWN_SPLASHES = [
    (0x942B88, "splash_mx"),
    (0x9C0EDC, "splash_orig"),
]

# Resource region to scan for additional SWFs
RESOURCE_REGION_START = 0x900000
RESOURCE_REGION_END   = 0xD00000


def find_all_swfs(data: bytes, start: int, end: int) -> list[tuple[int, int, bytes]]:
    """Return list of (offset, size, sig) for every SWF in [start, end)."""
    results = []
    pos = start
    while pos < end:
        sig = data[pos:pos+3]
        if sig in (b"FWS", b"CWS"):
            if pos + 8 > len(data):
                break
            size = struct.unpack_from("<I", data, pos + 4)[0]
            if size > 0 and pos + size <= len(data):
                results.append((pos, size, sig))
                pos += size
                continue
        pos += 1
    return results


def extract_splash(data: bytes, offset: int, name: str, out: pathlib.Path) -> int:
    """Extract gzip blob at offset, decompress, write both .gz and .raw. Returns raw size."""
    if data[offset:offset+2] != b'\x1f\x8b':
        print(f"  WARNING: no gzip magic at 0x{offset:x} for {name}", file=sys.stderr)
        return 0

    # Find end of this gzip stream: next gzip header, or scan by decompressing
    # Try: next \x1f\x8b after offset+2
    next_gz = data.find(b'\x1f\x8b', offset + 2)
    # Decompress to find true end (gzip.decompress uses the full stream)
    # Use incremental approach: try increasing windows
    gz_blob = None
    raw_data = None
    for end in [next_gz, len(data)]:
        if end <= offset:
            continue
        try:
            candidate = data[offset:end]
            raw_data = gzip.decompress(candidate)
            gz_blob = candidate
            break
        except Exception:
            continue

    if raw_data is None:
        print(f"  ERROR: could not decompress gzip at 0x{offset:x} for {name}", file=sys.stderr)
        return 0

    (out / f"{name}.gz").write_bytes(gz_blob)
    (out / f"{name}.raw").write_bytes(raw_data)
    print(f"  {name}: gzip={len(gz_blob)} bytes → raw={len(raw_data)} bytes")
    return len(raw_data)


SPLASH_WIDTH  = 1280   # confirmed from pixel color analysis
SPLASH_HEIGHT = 848    # confirmed: 1280 * 848 * 4 = 4,341,760 bytes
SPLASH_FORMAT = "rgba" # confirmed: dominant color R=230,G=0,B=0 = RED logo red


def detect_splash_dimensions(raw_size: int) -> list[tuple[int,int,str]]:
    """Return plausible (w, h, pixel_format) given raw byte count."""
    if raw_size == SPLASH_WIDTH * SPLASH_HEIGHT * 4:
        return [(SPLASH_WIDTH, SPLASH_HEIGHT, SPLASH_FORMAT)]
    candidates = []
    for fmt, bpp in [("rgba", 4), ("bgra", 4), ("rgb24", 3)]:
        pixels = raw_size / bpp
        for w, h in [(1024, 1024), (1280, 720), (1280, 800), (1280, 848),
                     (1920, 1080), (800, 600), (1024, 768)]:
            if abs(w * h - pixels) < 100:
                candidates.append((w, h, fmt))
    return candidates


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--firmware", default=FIRMWARE_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()

    fw_path = pathlib.Path(args.firmware)
    if not fw_path.exists():
        sys.exit(f"Firmware not found: {fw_path}")

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Reading {fw_path} ({fw_path.stat().st_size:,} bytes)...")
    data = fw_path.read_bytes()

    # --- SWF extraction ---
    print("\n=== SWF Files ===")
    all_swfs = find_all_swfs(data, RESOURCE_REGION_START, RESOURCE_REGION_END)
    if not all_swfs:
        print("  No SWFs found in resource region scan.")
    else:
        print(f"  Found {len(all_swfs)} SWF(s) by scan:")

    # Match known names by offset
    known_by_offset = {off: name for off, name in KNOWN_SWFS}
    for i, (offset, size, sig) in enumerate(all_swfs):
        name = known_by_offset.get(offset, f"swf_{i+1}")
        out_path = out / f"{name}.swf"
        out_path.write_bytes(data[offset:offset+size])
        swf_ver = data[offset + 3]
        print(f"  0x{offset:08x}  {name}.swf  sig={sig.decode()}  ver={swf_ver}  size={size:,}")

    # Also extract by known offsets even if scan missed them
    for offset, name in KNOWN_SWFS:
        if not any(o == offset for o, _, _ in all_swfs):
            sig = data[offset:offset+3]
            if sig in (b"FWS", b"CWS"):
                size = struct.unpack_from("<I", data, offset + 4)[0]
                out_path = out / f"{name}.swf"
                out_path.write_bytes(data[offset:offset+size])
                print(f"  0x{offset:08x}  {name}.swf  sig={sig.decode()}  ver={data[offset+3]}  size={size:,}  (known offset)")

    # --- Splash screen extraction ---
    print("\n=== Splash Screens ===")
    for offset, name in KNOWN_SPLASHES:
        raw_size = extract_splash(data, offset, name, out)
        if raw_size:
            dims = detect_splash_dimensions(raw_size)
            if dims:
                print(f"    Likely dimensions: {dims}")
            else:
                print(f"    No standard dimension match for {raw_size} bytes")
            # Print ffmpeg conversion commands
            for w, h, fmt in dims[:2]:
                print(f"    Convert: ffmpeg -f rawvideo -pix_fmt {fmt} -video_size {w}x{h} "
                      f"-i {out}/{name}.raw {out}/{name}_{w}x{h}.png")

    print(f"\nOutput written to: {out}/")
    print("\nNext steps:")
    print("  1. Verify SWFs: file firmware/reverse/build_32/assets/*.swf")
    print("  2. Decompile: java -jar ffdec.jar -export script assets/swf_gui_1/as/ assets/swf_gui_1.swf")
    print("  3. View splash: use ffmpeg commands above to convert .raw → .png")


if __name__ == "__main__":
    main()
