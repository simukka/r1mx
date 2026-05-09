#!/usr/bin/env python3
"""
analyze_build.py — RED ONE MX firmware build analyzer

Usage:
    python3 analyze_build.py <build.zip> [--output-dir DIR] [--extract] [--json]

Handles both unencrypted builds (≤16, su.tar) and encrypted builds (≥17, redone.su).
Runs binwalk, extracts embedded components, and produces a structured report.

Dependencies:
    pip install binwalk   (or install system binwalk)
    openssl must be on PATH for encrypted builds
"""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import zlib
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Decryption key — used for Build 17+ (AES-256-CBC, MD5 KDF)
# ---------------------------------------------------------------------------
REDONE_DECRYPT_PASS = "M1H5gwOXh757rIRVY6Gj2tN080AYSX03"
REDONE_ALGO = "aes-256-cbc"

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FirmwareComponent:
    name: str
    size: int
    sha256: str
    role: str

@dataclass
class BinwalkEntry:
    offset_dec: int
    offset_hex: str
    description: str

@dataclass
class BuildReport:
    zip_file: str
    build_format: str                        # "unencrypted" | "encrypted"
    upgrade_package: str                     # su.tar | redone.su
    components: list[FirmwareComponent] = field(default_factory=list)
    version_string: Optional[str] = None     # SUNDANCEMAGIC release name
    vxworks_version: Optional[str] = None
    bsp_path: Optional[str] = None           # source path embedded in binary
    cpu_arch: Optional[str] = None
    fpga_type: Optional[str] = None
    swf_count: int = 0
    xml_offsets: list[int] = field(default_factory=list)
    splash_raw_bytes: Optional[int] = None
    splash_dimensions: Optional[str] = None
    encrypted_sections: list[str] = field(default_factory=list)
    upgrade_strings: list[str] = field(default_factory=list)
    debug_strings: list[str] = field(default_factory=list)
    copyright_strings: list[str] = field(default_factory=list)
    binwalk_entries: list[BinwalkEntry] = field(default_factory=list)
    readme_text: Optional[str] = None
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], input_data: bytes = None) -> tuple[int, bytes, bytes]:
    result = subprocess.run(cmd, input=input_data, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def find_strings(data: bytes, min_len: int = 6) -> list[str]:
    """Extract printable ASCII strings from a byte buffer."""
    pattern = rb"[ -~]{" + str(min_len).encode() + rb",}"
    return [m.group().decode("ascii", errors="replace") for m in re.finditer(pattern, data)]


def dimensions_for_raw(size: int) -> list[str]:
    """Return plausible WxH@bpp strings for a raw framebuffer of given byte size."""
    results = []
    for w in [800, 1024, 1280, 1920]:
        for bpp in [3, 4]:
            if size % (w * bpp) == 0:
                h = size // (w * bpp)
                results.append(f"{w}x{h} @ {bpp * 8}bpp")
    return results


def run_binwalk(binary_path: Path) -> list[BinwalkEntry]:
    """Run binwalk on a file and parse the output table."""
    entries: list[BinwalkEntry] = []
    rc, out, err = run(["binwalk", str(binary_path)])
    if rc != 0 and not out:
        return entries
    for line in out.decode(errors="replace").splitlines():
        m = re.match(r"^(\d+)\s+(0x[0-9A-Fa-f]+)\s+(.+)$", line)
        if m:
            entries.append(BinwalkEntry(
                offset_dec=int(m.group(1)),
                offset_hex=m.group(2),
                description=m.group(3).strip(),
            ))
    return entries


def extract_with_binwalk(binary_path: Path, out_dir: Path) -> Path:
    """Run binwalk -eM to carve out embedded files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    run(["binwalk", "-eM", "--directory", str(out_dir), str(binary_path)])
    # binwalk places results in a subdirectory named _<filename>.extracted
    extracted = out_dir / f"_{binary_path.name}.extracted"
    return extracted if extracted.exists() else out_dir


# ---------------------------------------------------------------------------
# Firmware analysis
# ---------------------------------------------------------------------------

def analyze_firmware(data: bytes, report: BuildReport, label: str) -> None:
    """Scan a firmware binary and populate the report."""
    strings = find_strings(data)

    # Version / release name
    for s in strings:
        m = re.search(r"SUNDANCEMAGIC[^=]+=(.+)", s)
        if m:
            report.version_string = m.group(1).strip()
            break

    # VxWorks version
    for s in strings:
        m = re.search(r'VxWorks WIND kernel version "([^"]+)"', s)
        if m:
            report.vxworks_version = m.group(1)
            break

    # BSP source path
    for s in strings:
        if "/home/sundance/" in s or "bsp_ppc" in s:
            report.bsp_path = s.strip()
            report.cpu_arch = "PowerPC 405"
            break

    # FPGA detection (handled separately via binwalk on iofpga file)

    # SWF count — look for FWS or CWS magic
    report.swf_count += data.count(b"FWS") + data.count(b"CWS")

    # Encrypted sections
    for s in strings:
        if "mcrypt" in s.lower() or "blowfish" in s.lower():
            report.encrypted_sections.append(s.strip())

    # Copyright strings
    for s in strings:
        if "Copyright" in s and s not in report.copyright_strings:
            report.copyright_strings.append(s.strip())

    # Upgrade state machine strings
    upgrade_patterns = [
        r"UPGRADE", r"SmartUpgrade", r"GoSplash", r"su\.tar", r"redone\.su",
    ]
    for s in strings:
        for pat in upgrade_patterns:
            if re.search(pat, s):
                if s.strip() not in report.upgrade_strings:
                    report.upgrade_strings.append(s.strip())
                break

    # Debug / maintenance strings
    debug_patterns = [
        r"xemaclite", r"vxWorks h=", r"usbTarg", r"/tffs", r"192\.168\.",
    ]
    for s in strings:
        for pat in debug_patterns:
            if re.search(pat, s):
                if s.strip() not in report.debug_strings:
                    report.debug_strings.append(s.strip())
                break

    # Splash raw — look for gzip with "splash.raw" original name (magic 0x1f8b)
    pos = 0
    while True:
        idx = data.find(b"\x1f\x8b", pos)
        if idx == -1:
            break
        # Check FNAME flag (bit 3 of flags byte at offset 3)
        if idx + 10 < len(data) and (data[idx + 3] & 0x08):
            # Read original filename
            fname_start = idx + 10
            fname_end = data.find(b"\x00", fname_start)
            if fname_end != -1:
                fname = data[fname_start:fname_end].decode("ascii", errors="replace")
                if "splash" in fname.lower():
                    try:
                        decompressed = gzip.decompress(data[idx:])
                        report.splash_raw_bytes = len(decompressed)
                        dims = dimensions_for_raw(len(decompressed))
                        report.splash_dimensions = ", ".join(dims) if dims else "unknown"
                    except Exception:
                        pass
        pos = idx + 2

    # XML offsets
    xml_positions = [m.start() for m in re.finditer(rb"<\?xml version", data)]
    report.xml_offsets.extend(xml_positions)


def analyze_fpga(data: bytes, report: BuildReport) -> None:
    """Detect FPGA bitstream type."""
    # Xilinx bitstream starts with 0xFF FF FF FF AA 99 55 66 (sync word)
    if data[:4] == bytes([0xFF, 0xFF, 0xFF, 0xFF]) or data[:2] == bytes([0x00, 0x09]):
        report.fpga_type = "Xilinx Virtex/Spartan bitstream"
    elif data[:4] == b"\x00\x00\x00\x00":
        # Try reading Xilinx header further in
        if b"\xaa\x99\x55\x66" in data[:64]:
            report.fpga_type = "Xilinx bitstream (sync word found)"
        else:
            report.fpga_type = "Unknown / raw binary"
    else:
        report.fpga_type = "Unknown"

    # Check for Xilinx design metadata strings
    for s in find_strings(data, min_len=4):
        if any(k in s for k in ["Xilinx", "Spartan", "Virtex", "iofpga", "Design"]):
            report.fpga_type += f" [{s.strip()}]"
            break


# ---------------------------------------------------------------------------
# Package extraction
# ---------------------------------------------------------------------------

def decrypt_file(encrypted_path: Path, output_path: Path) -> bool:
    """Decrypt a redone.N file using OpenSSL AES-256-CBC."""
    rc, out, err = run([
        "openssl", "enc", "-d",
        f"-{REDONE_ALGO}", "-md", "md5",
        "-pass", f"pass:{REDONE_DECRYPT_PASS}",
        "-in", str(encrypted_path),
        "-out", str(output_path),
    ])
    return rc == 0


def extract_unencrypted_su(tar_path: Path, work_dir: Path) -> tuple[Optional[Path], Optional[Path]]:
    """
    Extract su.tar (Build 13–16).
    Returns (software_bin_path, fpga_bin_path).
    """
    sw_bin = None
    fpga_bin = None
    with tarfile.open(tar_path) as tf:
        for member in tf.getmembers():
            name = member.name.lower()
            dest = work_dir / Path(member.name).name
            f = tf.extractfile(member)
            if f is None:
                continue
            data = f.read()
            # Decompress if gzip
            if dest.suffix == ".gz" or data[:2] == b"\x1f\x8b":
                try:
                    data = gzip.decompress(data)
                    dest = dest.with_suffix("")  # strip .gz
                except Exception:
                    pass
            dest.write_bytes(data)
            if "sundance" in name or "software" in name or "sw" in name:
                sw_bin = dest
            elif "iofpga" in name or "fpga" in name:
                fpga_bin = dest
    return sw_bin, fpga_bin


def extract_encrypted_su(tar_path: Path, work_dir: Path) -> tuple[Optional[Path], Optional[Path]]:
    """
    Extract redone.su (Build 17+): tar → redone.1 (sw, AES) + redone.3 (fpga, AES).
    Returns (software_bin_path, fpga_bin_path).
    """
    sw_bin = None
    fpga_bin = None
    with tarfile.open(tar_path) as tf:
        tf.extractall(work_dir, filter="data")

    for enc_name, role in [("redone.1", "sw"), ("redone.3", "fpga")]:
        enc_path = work_dir / enc_name
        if not enc_path.exists():
            continue
        dec_gz = work_dir / f"{enc_name}.gz"
        if not decrypt_file(enc_path, dec_gz):
            print(f"  [!] Decryption failed for {enc_name} — skipping", file=sys.stderr)
            continue
        dec_bin = work_dir / (f"software.bin" if role == "sw" else "fpga.bin")
        try:
            dec_bin.write_bytes(gzip.decompress(dec_gz.read_bytes()))
        except Exception as e:
            print(f"  [!] Gunzip failed for {dec_gz.name}: {e}", file=sys.stderr)
            continue
        if role == "sw":
            sw_bin = dec_bin
        else:
            fpga_bin = dec_bin

    return sw_bin, fpga_bin


def find_upgrade_package(zip_path: Path, work_dir: Path) -> tuple[Optional[Path], str]:
    """
    Extract the zip and locate the upgrade package (su.tar or redone.su).
    Returns (package_path, format_string).
    """
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            # Skip macOS metadata
            if "__MACOSX" in info.filename or info.filename.endswith(".DS_Store"):
                continue
            name_lower = info.filename.lower()
            if name_lower.endswith("su.tar") or name_lower.endswith("redone.su"):
                out_path = work_dir / Path(info.filename).name
                out_path.write_bytes(zf.read(info.filename))
                fmt = "unencrypted" if "su.tar" in name_lower else "encrypted"
                return out_path, fmt
    return None, "unknown"


def extract_readme(zip_path: Path) -> Optional[str]:
    """Pull the first .txt readme from the zip."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if "__MACOSX" in info.filename:
                continue
            if info.filename.lower().endswith(".txt"):
                return zf.read(info.filename).decode("utf-8", errors="replace")
    return None


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_report(report: BuildReport) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(f"  RED ONE MX Firmware Analysis — {Path(report.zip_file).name}")
    lines.append("=" * 70)
    lines.append(f"  Format       : {report.build_format}")
    lines.append(f"  Package      : {report.upgrade_package}")
    if report.version_string:
        lines.append(f"  Version      : {report.version_string}")
    if report.vxworks_version:
        lines.append(f"  VxWorks      : {report.vxworks_version}")
    if report.cpu_arch:
        lines.append(f"  CPU arch     : {report.cpu_arch}")
    if report.fpga_type:
        lines.append(f"  FPGA type    : {report.fpga_type}")
    if report.bsp_path:
        lines.append(f"  BSP path     : {report.bsp_path}")

    if report.components:
        lines.append("")
        lines.append("  Components:")
        for c in report.components:
            lines.append(f"    {c.name:<35} {c.size:>10} bytes  ({c.role})")
            lines.append(f"      sha256: {c.sha256}")

    if report.splash_raw_bytes:
        lines.append("")
        lines.append(f"  Splash screen: {report.splash_raw_bytes} bytes raw")
        lines.append(f"    Dimensions : {report.splash_dimensions}")

    if report.swf_count:
        lines.append(f"  Flash SWF    : {report.swf_count} SWF signatures found")

    if report.xml_offsets:
        lines.append(f"  XML docs     : {len(report.xml_offsets)} found at offsets "
                     + ", ".join(hex(o) for o in report.xml_offsets[:8]))

    if report.encrypted_sections:
        lines.append("")
        lines.append("  Encrypted sections:")
        for s in report.encrypted_sections[:5]:
            lines.append(f"    {s}")

    if report.upgrade_strings:
        lines.append("")
        lines.append("  Upgrade state machine strings:")
        seen = set()
        for s in report.upgrade_strings:
            key = s[:60]
            if key not in seen:
                lines.append(f"    {s[:80]}")
                seen.add(key)

    if report.debug_strings:
        lines.append("")
        lines.append("  Debug / maintenance strings:")
        for s in report.debug_strings[:8]:
            lines.append(f"    {s[:80]}")

    if report.copyright_strings:
        lines.append("")
        lines.append("  Copyright strings:")
        seen = set()
        for s in report.copyright_strings:
            key = s[:60]
            if key not in seen and len(seen) < 8:
                lines.append(f"    {s[:80]}")
                seen.add(key)

    if report.binwalk_entries:
        lines.append("")
        lines.append(f"  binwalk ({len(report.binwalk_entries)} entries, key ones shown):")
        keywords = [
            "VxWorks", "XML", "Flash SWF", "gzip", "mcrypt", "blowfish",
            "Copyright Wind River", "Xilinx", "FPGA", "StuffIt",
        ]
        shown = 0
        for e in report.binwalk_entries:
            if any(k.lower() in e.description.lower() for k in keywords):
                lines.append(f"    {e.offset_dec:>10}  {e.offset_hex:<12}  {e.description[:60]}")
                shown += 1
        if shown == 0:
            for e in report.binwalk_entries[:20]:
                lines.append(f"    {e.offset_dec:>10}  {e.offset_hex:<12}  {e.description[:60]}")

    if report.errors:
        lines.append("")
        lines.append("  Errors / warnings:")
        for e in report.errors:
            lines.append(f"    [!] {e}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze(zip_path: Path, output_dir: Optional[Path], do_extract: bool, as_json: bool) -> BuildReport:
    report = BuildReport(
        zip_file=str(zip_path),
        build_format="unknown",
        upgrade_package="",
    )

    if not zip_path.exists():
        report.errors.append(f"File not found: {zip_path}")
        return report

    work_dir = Path(tempfile.mkdtemp(prefix="red_firmware_"))
    print(f"[*] Working directory: {work_dir}", file=sys.stderr)

    try:
        # 1. Locate the upgrade package inside the zip
        print("[*] Extracting upgrade package…", file=sys.stderr)
        pkg_path, fmt = find_upgrade_package(zip_path, work_dir)
        if pkg_path is None:
            report.errors.append("No su.tar or redone.su found in zip")
            return report

        report.build_format = fmt
        report.upgrade_package = pkg_path.name
        report.readme_text = extract_readme(zip_path)

        # 2. Extract firmware components
        print(f"[*] Format: {fmt} — extracting firmware…", file=sys.stderr)
        if fmt == "unencrypted":
            sw_bin, fpga_bin = extract_unencrypted_su(pkg_path, work_dir)
        else:
            sw_bin, fpga_bin = extract_encrypted_su(pkg_path, work_dir)

        for path, role in [(sw_bin, "Main OS + app firmware"), (fpga_bin, "I/O FPGA bitstream")]:
            if path and path.exists():
                data = path.read_bytes()
                report.components.append(FirmwareComponent(
                    name=path.name,
                    size=len(data),
                    sha256=sha256_of(data),
                    role=role,
                ))

        # 3. Analyze the software binary
        if sw_bin and sw_bin.exists():
            print("[*] Analyzing software binary…", file=sys.stderr)
            sw_data = sw_bin.read_bytes()
            analyze_firmware(sw_data, report, sw_bin.name)

            print("[*] Running binwalk on software binary…", file=sys.stderr)
            report.binwalk_entries = run_binwalk(sw_bin)

            if do_extract and output_dir:
                print("[*] Running binwalk extraction…", file=sys.stderr)
                extract_with_binwalk(sw_bin, output_dir)
        else:
            report.errors.append("Software binary not found/extracted")

        # 4. Analyze FPGA binary
        if fpga_bin and fpga_bin.exists():
            print("[*] Analyzing FPGA binary…", file=sys.stderr)
            analyze_fpga(fpga_bin.read_bytes(), report)
        else:
            report.errors.append("FPGA binary not found/extracted")

        # 5. Copy extracted binaries to output_dir if requested
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            for comp_path in [sw_bin, fpga_bin]:
                if comp_path and comp_path.exists():
                    dest = output_dir / comp_path.name
                    shutil.copy2(comp_path, dest)
                    print(f"[*] Saved {comp_path.name} → {dest}", file=sys.stderr)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RED ONE MX firmware build analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("zip_file", type=Path, help="Path to the build .zip file")
    parser.add_argument(
        "--output-dir", "-o", type=Path, default=None,
        help="Directory to save extracted firmware components",
    )
    parser.add_argument(
        "--extract", "-e", action="store_true",
        help="Also run binwalk -eM to carve embedded files (requires --output-dir)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        help="Output report as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    report = analyze(args.zip_file, args.output_dir, args.extract, args.json)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()
