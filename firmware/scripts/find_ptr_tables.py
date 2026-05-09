#!/usr/bin/env python3
"""
Find pointer tables to whitelist strings, and search for all reference patterns.
Also search 32-bit embedded address values and ori patterns.
"""
import struct
BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"
with open(BIN, "rb") as f:
    data = f.read()

def u32(off): return struct.unpack_from(">I", data, off)[0]

# All whitelist string addrs
WHITELIST_ADDRS = [
    0xD2E3F8, 0xD2E410, 0xD2E41C, 0xD2E428,  # LEXAR, CF models
    0xD2E434, 0xD2E444, 0xD2E454, 0xD2E464, 0xD2E474,  # SSD models
    0xD2E5D4, 0xD2E5E4, 0xD2E5F4, 0xD2E604, 0xD2E618, 0xD2E62C,  # REV models
    0xD2E640, 0xD2E654, 0xD2E668, 0xD2E67C, 0xD2E690, 0xD2E6A4,
    0xD2E6B8, 0xD2E6C8, 0xD2E6D8, 0xD2E6E8,  # 512GB Vx
    0xD2E6F8, 0xD2E704,  # 55GB V1/V2
]

print("=== Searching for 32-bit embedded pointer values ===")
# Search entire binary for these address values as big-endian 32-bit words (in .rodata/.text)
for wa in WHITELIST_ADDRS:
    needle = struct.pack(">I", wa)
    pos = 0
    refs = []
    while True:
        idx = data.find(needle, pos)
        if idx < 0:
            break
        # only report if this looks like code/data (not part of the string itself)
        if idx < 0xD2E000 or idx > 0xD2F000:
            refs.append(idx)
        pos = idx + 1
    if refs:
        label = ""
        if wa == 0xD2E3F8: label = "LEXAR"
        elif wa == 0xD2E434: label = "RED 55GB SSD"
        elif wa == 0xD2E444: label = "RED 64GB SSD"
        elif wa == 0xD2E454: label = "RED 128GB SSD"
        elif wa == 0xD2E464: label = "RED 256GB SSD"
        elif wa == 0xD2E474: label = "RED 512GB SSD"
        print(f"  0x{wa:08X} [{label}]: ptr found at {[f'0x{r:08X}' for r in refs]}")

# Look for pointer table - consecutive pointers to whitelist strings
print("\n=== Looking for pointer table containing multiple whitelist addrs ===")
addr_set = set(WHITELIST_ADDRS)
for i in range(0, len(data)-4, 4):
    v = u32(i)
    if v in addr_set:
        # check if surrounded by other whitelist pointers
        neighbors = []
        for delta in range(-8, 12, 4):
            j = i + delta
            if 0 <= j < len(data) - 4:
                nv = u32(j)
                if nv in addr_set:
                    neighbors.append((j, nv))
        if len(neighbors) >= 3:
            print(f"  Pointer table candidate at 0x{i:08X}: {[(f'0x{a:08X}', f'0x{v2:08X}') for a,v2 in neighbors]}")

# Also search for ori pattern to reach these addresses
# ori rD, rA, imm16: opcode 24 = 0b011000
# Bytes: [0]=0x60|(rD>>3), [1]=(rD&7)<<5|(rA&0x1F), [2]=imm16_hi, [3]=imm16_lo
print("\n=== Searching lis+ori patterns for whitelist addrs ===")
TARGET_ADDRS = {
    0xD2E3F8: "LEXAR", 0xD2E434: "55GB SSD", 0xD2E444: "64GB SSD",
    0xD2E454: "128GB SSD", 0xD2E464: "256GB SSD", 0xD2E474: "512GB SSD",
    0xD2E7F0: "CP-5723_", 0xD2E804: "Bad S/N full",
    0xD2E84C: "Invalid capacity", 0xD2E87C: "Invalid drive type",
    0xD2E8A0: "Capacity mismatch", 0xD2E8D8: "DigMagMgr",
    0xD2E720: "digmagmgr.cpp",
}
for addr, label in TARGET_ADDRS.items():
    imm16 = addr & 0xFFFF
    # search for ori rD, rA, imm16
    needle_hi = (imm16 >> 8) & 0xFF
    needle_lo = imm16 & 0xFF
    found = []
    for i in range(0, len(data)-4, 4):
        b = data[i:i+4]
        if (b[0] & 0xFC) == 0x60 and b[2] == needle_hi and b[3] == needle_lo:
            # verify rA == rD (same reg)
            rD = ((b[0] & 0x03) << 3) | (b[1] >> 5)
            rA = b[1] & 0x1F
            if rA == rD:
                found.append(i)
    if found:
        print(f"  0x{addr:08X} [{label}]: ori xref(s) at {[f'0x{x:08X}' for x in found[:6]]}")
