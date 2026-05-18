#!/usr/bin/env python3
"""
Analyze RED ONE firmware (PPC405 big-endian flat binary) for DigMag SSD validation.
Base address: 0x0, binary is loaded as-is.
"""
import struct
import sys

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"

with open(BIN, "rb") as f:
    data = f.read()

def u32(off):
    return struct.unpack_from(">I", data, off)[0]

def u16(off):
    return struct.unpack_from(">H", data, off)[0]

def s(off, n=64):
    """Read null-terminated string at offset."""
    end = data.index(b'\x00', off, off+n)
    return data[off:end].decode('latin-1', errors='replace')

def sraw(off, n=64):
    return data[off:off+n]

# Known string addresses from problem statement
KNOWN_STRINGS = {
    0xD2E3F8: "LEXAR ATA FLASH CARD",
    0xD2E720: "digmagmgr.cpp (file string)",
    0xD2E7F0: "CP-5723_ (serial prefix)",
    0xD2E7B4: "bad serial format #1",
    0xD2E804: "bad serial format #2",
    0xD2E490: "GUI state string",
    0xD2E53C: "INCOMPATIBLE state string",
    0xD2E8EC: "ATA log string #1",
    0xD2E908: "ATA log string #2",
    0xD2E928: "ATA log string #3",
}

print("=== Known string dumps ===")
for addr, label in sorted(KNOWN_STRINGS.items()):
    try:
        raw = data[addr:addr+80]
        null = raw.find(b'\x00')
        txt = raw[:null if null>=0 else 80].decode('latin-1', errors='replace')
        print(f"  0x{addr:08X}  [{label}]: {repr(txt)}")
    except Exception as e:
        print(f"  0x{addr:08X}  [{label}]: ERROR {e}")

# Dump the full whitelist area
print("\n=== Whitelist string block (0xD2E3F8 - 0xD2E720) ===")
off = 0xD2E3F8
while off < 0xD2E730:
    raw = data[off:off+48]
    null = raw.find(b'\x00')
    if null == 0:
        # skip nulls, find next non-null
        skip = 0
        while skip < 48 and raw[skip] == 0:
            skip += 1
        off += skip if skip > 0 else 4
        continue
    txt = raw[:null if null >= 0 else 48].decode('latin-1', errors='replace')
    print(f"  0x{off:08X}: {repr(txt)}")
    off += (null + 1 + 3) & ~3  # align to 4 bytes after null

# Dump serial/capacity strings
print("\n=== Serial/capacity string block (0xD2E7B4 - 0xD2E960) ===")
off = 0xD2E7B4
while off < 0xD2E960:
    raw = data[off:off+80]
    null = raw.find(b'\x00')
    if null == 0:
        off += 4
        continue
    if raw[0] < 0x20 or raw[0] > 0x7E:
        off += 4
        continue
    txt = raw[:null if null >= 0 else 80].decode('latin-1', errors='replace')
    if len(txt) > 2:
        print(f"  0x{off:08X}: {repr(txt)}")
    off += (null + 1 + 3) & ~3

