#!/usr/bin/env python3
"""
Deep analysis: jump table at 0xD2E444, find SDA/TOC patterns,
find strlen/strcmp calls near string refs, find IsCompatible function.
"""
import struct, subprocess

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"
with open(BIN, "rb") as f:
    data = f.read()

def u32(off): return struct.unpack_from(">I", data, off)[0]
def hexdump(off, n=64):
    b = data[off:off+n]
    return ' '.join(f'{x:02X}' for x in b)

# 1. What's actually at 0xD2E444?
print("=== Bytes at 0xD2E444 (alleged jump table / RED 64GB SSD) ===")
for i in range(8):
    off = 0xD2E444 + i*4
    v = u32(off)
    b = data[off:off+4]
    s = ''.join(chr(x) if 0x20<=x<0x7F else '.' for x in b)
    print(f"  [{i}] 0x{off:08X}: 0x{v:08X}  '{s}'")

# 2. Check the jump table indexing: r29 - 0x15, range 0..5
# If this is a drive type switch: types 0x15..0x1A = 21..26
# Jump table at 0xD2E444, 6 entries, RELATIVE to r9 (= 0xD2E444)
print("\n=== Jump table entries if base = 0xD2E444, entries at 0..5 ===")
for i in range(6):
    off = 0xD2E444 + i*4
    v = u32(off)
    signed_v = struct.unpack_from(">i", data, off)[0]
    target = (0xD2E444 + signed_v) & 0xFFFFFFFF
    print(f"  [{i}] offset=0x{v:08X} (signed {signed_v:+d}) -> abs target 0x{target:08X}")

# 3. Now look at WHAT is at those jump targets
print("\n=== Disasm at jump targets ===")
def r2dis(addr, n=20):
    full = f"s 0x{addr:X}\npd {n}\nq\n"
    result = subprocess.run(
        ["r2", "-a", "ppc", "-b", "32", "-e", "cfg.bigendian=true", "-q", BIN],
        input=full, capture_output=True, text=True, timeout=30
    )
    return result.stdout[:1500]

# First jump target
for i in range(6):
    off = 0xD2E444 + i*4
    v = u32(off)
    signed_v = struct.unpack_from(">i", data, off)[0]
    target = (0xD2E444 + signed_v) & 0xFFFFFFFF
    if 0x400000 <= target <= 0xF00000:
        print(f"\n  Case {i} (type {i+0x15}=={i+21}) -> 0x{target:08X}:")
        print(r2dis(target, 12))

