#!/usr/bin/env python3
"""
Patch modified SWF or splash screen assets back into software.bin.

Usage examples:
    # Replace splash_mx with a modified version:
    python3 firmware/scripts/patch_assets.py splash_mx path/to/new_image.png

    # Replace splash_orig:
    python3 firmware/scripts/patch_assets.py splash_orig path/to/new_image.png

    # Replace SWF gui 1 with a modified .swf:
    python3 firmware/scripts/patch_assets.py swf_gui_1 path/to/modified.swf

    # Replace SWF gui 2:
    python3 firmware/scripts/patch_assets.py swf_gui_2 path/to/modified.swf
"""
import argparse
import gzip
import pathlib
import struct
import sys

FIRMWARE_PATH = pathlib.Path("firmware/reverse/build_32/extracted/software.bin")

# Asset definitions: (offset_in_binary, region_size_in_binary, asset_type)
ASSETS = {
    "splash_mx":   (0x942B88,  516_909, "splash"),
    "splash_orig": (0x9C0EDC,   72_360, "splash"),
    "swf_gui_1":   (0x9E03BC, 1_329_944, "swf"),
    "swf_gui_2":   (0xB24EF8, 1_346_327, "swf"),
}

SPLASH_WIDTH  = 1280
SPLASH_HEIGHT = 848
SPLASH_FORMAT = "rgba"  # RGBA 32-bit


def load_splash_raw(path: pathlib.Path) -> bytes:
    """Load a splash image. Accepts .raw (already correct format) or .png/.jpg (converts)."""
    if path.suffix.lower() == ".raw":
        raw = path.read_bytes()
        expected = SPLASH_WIDTH * SPLASH_HEIGHT * 4
        if len(raw) != expected:
            sys.exit(f"ERROR: {path} is {len(raw)} bytes, expected {expected} (1280×848 RGBA)")
        return raw
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow required for image conversion: pip install Pillow")
    img = Image.open(path).convert("RGBA")
    if img.size != (SPLASH_WIDTH, SPLASH_HEIGHT):
        print(f"  Resizing from {img.size} to {SPLASH_WIDTH}×{SPLASH_HEIGHT}", file=sys.stderr)
        img = img.resize((SPLASH_WIDTH, SPLASH_HEIGHT), Image.LANCZOS)
    return img.tobytes()  # RGBA bytes


def patch_binary(firmware: pathlib.Path, offset: int, new_bytes: bytes, region_size: int):
    """Write new_bytes into firmware at offset, zero-padding to region_size."""
    if len(new_bytes) > region_size:
        sys.exit(
            f"ERROR: Replacement ({len(new_bytes):,} B) exceeds region size ({region_size:,} B).\n"
            f"       Use 'splash_mx' region ({ASSETS['splash_mx'][1]:,} B) for more headroom."
        )
    data = bytearray(firmware.read_bytes())
    data[offset:offset + len(new_bytes)] = new_bytes
    if len(new_bytes) < region_size:
        data[offset + len(new_bytes):offset + region_size] = bytes(region_size - len(new_bytes))
    firmware.write_bytes(data)
    print(f"  Patched {len(new_bytes):,} bytes at 0x{offset:x} (region={region_size:,})")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("asset", choices=list(ASSETS), help="Asset to replace")
    ap.add_argument("replacement", help="Path to replacement file")
    ap.add_argument("--firmware", default=str(FIRMWARE_PATH),
                    help=f"Path to software.bin (default: {FIRMWARE_PATH})")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would happen without writing")
    args = ap.parse_args()

    firmware = pathlib.Path(args.firmware)
    if not firmware.exists():
        sys.exit(f"Firmware not found: {firmware}")

    replacement = pathlib.Path(args.replacement)
    if not replacement.exists():
        sys.exit(f"Replacement file not found: {replacement}")

    offset, region_size, asset_type = ASSETS[args.asset]
    print(f"Asset:    {args.asset} @ 0x{offset:x}, region={region_size:,} B")
    print(f"Firmware: {firmware}")
    print(f"Input:    {replacement}")

    if asset_type == "splash":
        print("  Loading splash image...")
        raw = load_splash_raw(replacement)
        print(f"  Compressing {len(raw):,} raw bytes → gzip...")
        try:
            import zopfli
            c = zopfli.ZopfliCompressor(zopfli.ZOPFLI_FORMAT_GZIP)
            gz = c.compress(raw) + c.flush()
            print(f"  Compressed (zopfli): {len(gz):,} bytes")
        except ImportError:
            gz = gzip.compress(raw, compresslevel=9)
            print(f"  Compressed (gzip-9): {len(gz):,} bytes")
            print("  Tip: pip install zopflipy for better compression (~6% smaller)")
        print(f"  Headroom: {region_size - len(gz):,} bytes")
        if args.dry_run:
            print("  [dry-run] would patch firmware")
            return
        patch_binary(firmware, offset, gz, region_size)

    elif asset_type == "swf":
        new_swf = replacement.read_bytes()
        sig = new_swf[:3]
        if sig not in (b"FWS", b"CWS"):
            sys.exit(f"ERROR: {replacement} does not look like a SWF file (sig={sig!r})")
        swf_size = struct.unpack_from("<I", new_swf, 4)[0]
        if swf_size != len(new_swf):
            print(f"  WARNING: SWF header says {swf_size} bytes but file is {len(new_swf)} bytes")
        print(f"  SWF: sig={sig.decode()} ver={new_swf[3]} size={len(new_swf):,} B")
        if args.dry_run:
            print("  [dry-run] would patch firmware")
            return
        patch_binary(firmware, offset, new_swf, region_size)

    print("Done. Run repackage_firmware.sh to rebuild redone.su.")


if __name__ == "__main__":
    main()
