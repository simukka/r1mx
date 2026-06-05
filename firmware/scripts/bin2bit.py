#!/usr/bin/env python3
"""Wrap a raw Xilinx configuration .bin into a .bit so iMPACT will accept it
for assignment to an SRAM FPGA (which enables the Readback/Verify operations
that are otherwise greyed out for a device with no config file assigned).

A .bit file is simply an ASCII-keyed header followed by the exact bytes of the
.bin.  Header field keys:
    a = design name      b = part name
    c = date             d = time
    e = 4-byte big-endian bitstream length, then the raw config data

Usage: bin2bit.py <in.bin> <out.bit> [part] [design]
"""
import struct
import sys
import datetime


def field(key: bytes, value: str) -> bytes:
    payload = value.encode() + b"\x00"
    return key + struct.pack(">H", len(payload)) + payload


def wrap(bin_path: str, bit_path: str,
         part: str = "4vfx100ff1517",
         design: str = "fpga;UserID=0xFFFFFFFF") -> None:
    raw = open(bin_path, "rb").read()
    now = datetime.datetime.now()

    hdr = struct.pack(">H", 9)
    hdr += bytes([0x0f, 0xf0, 0x0f, 0xf0, 0x0f, 0xf0, 0x0f, 0xf0, 0x00])
    hdr += struct.pack(">H", 1)
    hdr += field(b"a", design)
    hdr += field(b"b", part)
    hdr += field(b"c", now.strftime("%Y/%m/%d"))
    hdr += field(b"d", now.strftime("%H:%M:%S"))
    hdr += b"e" + struct.pack(">I", len(raw))

    with open(bit_path, "wb") as f:
        f.write(hdr + raw)
    print(f"wrote {bit_path}: header {len(hdr)} + data {len(raw)} "
          f"= {len(hdr) + len(raw)} bytes (part={part})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    wrap(*sys.argv[1:])
