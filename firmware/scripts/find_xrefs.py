#!/usr/bin/env python3
"""Find xrefs to digmag string addresses using PPC405 lis/addi patterns."""
import struct, re

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"
with open(BIN, "rb") as f:
    data = f.read()

def u32(off): return struct.unpack_from(">I", data, off)[0]

# All string addresses share lis rX, 0x00D3 (since all are 0xD2Exxxx and E... > 0x8000)
# In PPC: lis rD, imm = addis rD, r0, imm
# Encoding: (15<<26) | (rD<<21) | (rA<<16) | (imm & 0xFFFF)
# lis rD, 0x00D3 → upper byte 0x3C, lower bits of first halfword = rD<<5|0, second halfword = 0x00D3

# Search for lis rX, 0x00D3 (any register)
# Byte pattern: 0x3C [b0000101 for r5..], 0x00, 0xD3
# Actually: inst[31:26]=001111, inst[25:21]=rD, inst[20:16]=rA=0, inst[15:0]=0x00D3
# So bytes[0] = 0x3C, bytes[1] = rD<<5 (high 3 bits of rD in low bits of byte... wait)
# PPC big-endian: bit 0 is MSB
# bytes[0] = inst[31:24] = (15<<2) | (rD>>3) = 0x3C | (rD>>3)
# bytes[1] = inst[23:16] = (rD & 7)<<5 | (rA>>0... rA=0 so (rD&7)<<5)
# bytes[2] = inst[15:8] = 0x00
# bytes[3] = inst[7:0] = 0xD3

# So: bytes[0] in {0x3C, 0x3D} (rD can be 0..31, but rD>>3 is 0..3, so 0x3C or 0x3C+{0,1,2,3}=0x3C..0x3F)
# bytes[2:4] = 0x00 0xD3

print("=== Searching for lis rX, 0x00D3 ===")
lis_d3_positions = []
for i in range(0, len(data)-4, 4):
    b = data[i:i+4]
    if (b[0] & 0xFC) == 0x3C and b[1] & 0x1F == 0x00 and b[2] == 0x00 and b[3] == 0xD3:
        rD = ((b[0] & 0x03) << 3) | (b[1] >> 5)
        lis_d3_positions.append((i, rD))

print(f"Found {len(lis_d3_positions)} lis rX, 0x00D3 instructions")

# Now for each, look for addi rD, rD, imm16 (or addi rX, rD, imm16) in next few instructions
# addi = opcode 14 = 0b001110
# addi rD, rA, imm → (14<<26)|(rD<<21)|(rA<<16)|imm
# Bytes: [0]=(0x38|rD>>3), [1]=(rD&7)<<5|(rA&0x1F) wait...
# bytes[0] = (14<<2)|(rD>>3) = 0x38|(rD>>3)
# bytes[1] = (rD&7)<<5 | (rA&0x1F) ... where rA = rD (same reg), rD = rD

# Key string addrs and their expected addi imm16:
# addi to reach 0x00D2Exxxx from base 0x00D30000:
# imm16 (signed) = addr - 0xD30000 = addr - 0xD30000
# e.g. 0xD2E3F8 - 0xD30000 = -0x1C08 → 0xE3F8
# 0xD2E434 - 0xD30000 = -0x1BCC → 0xE434
# 0xD2E4F8 - 0xD30000 = ... 

TARGET_STRINGS = {
    0xD2E3F8: "LEXAR ATA FLASH CARD",
    0xD2E410: "RED 16GB CF",
    0xD2E41C: "RED 32GB CF",
    0xD2E428: "RED 64GB CF",
    0xD2E434: "RED 55GB SSD",
    0xD2E444: "RED 64GB SSD",
    0xD2E454: "RED 128GB SSD",
    0xD2E464: "RED 256GB SSD",
    0xD2E474: "RED 512GB SSD",
    0xD2E7B4: "Bad S/N format char",
    0xD2E7F0: "CP-5723_",
    0xD2E7FC: "_X_F",
    0xD2E804: "Bad S/N format full",
    0xD2E840: "XXXXXXXX",
    0xD2E84C: "Invalid Red RAID capacity",
    0xD2E87C: "Invalid drive type",
    0xD2E8A0: "Capacity mismatch",
    0xD2E8D8: "DigMagMgr",
    0xD2E8EC: "ATA Model log",
    0xD2E908: "ATA Serial log",
    0xD2E928: "ATA Revision log",
    0xD2E720: "digmagmgr.cpp",
    0xD2E5D4: "RED 16GB REV B",
    0xD2E5F4: "RED 64GB REV A1",
    0xD2E6B8: "RED 512GB V1",
    0xD2E6F8: "RED 55GB V1",
}

target_imm16s = {}
for addr, label in TARGET_STRINGS.items():
    imm16 = (addr - 0xD30000) & 0xFFFF
    target_imm16s[imm16] = (addr, label)

print("\n=== Checking each lis + following addi ===")
all_xrefs = {}  # addr -> [(code_offset, context)]
for (lis_off, rD) in lis_d3_positions:
    # scan up to 8 instrs ahead for addi rX, rD, imm16
    for lookahead in range(1, 9):
        ni = lis_off + lookahead * 4
        if ni + 4 > len(data):
            break
        b = data[ni:ni+4]
        # addi: opcode=14, bytes[0] = 0x38|(rDst>>3), bytes[1]=(rDst&7)<<5|(rSrc&0x1F)
        op = b[0] >> 2
        if op != 14:  # not addi
            continue
        rSrc = ((b[1]) & 0x1F)  # rA field
        if rSrc != rD:  # source must be our register
            continue
        imm16 = (b[2] << 8) | b[3]
        if imm16 in target_imm16s:
            addr, label = target_imm16s[imm16]
            rDst = ((b[0] & 0x03) << 3) | (b[1] >> 5)
            # Get context: 8 instrs before lis through 8 instrs after addi
            ctx_start = max(0, lis_off - 32)
            ctx_end = min(len(data), ni + 64)
            context_bytes = data[ctx_start:ctx_end]
            if addr not in all_xrefs:
                all_xrefs[addr] = []
            all_xrefs[addr].append((lis_off, ni, rD, rDst, imm16))
            break

print(f"\nFound xrefs to {len(all_xrefs)} string addresses:")
for addr in sorted(all_xrefs.keys()):
    label = TARGET_STRINGS.get(addr, "?")
    refs = all_xrefs[addr]
    print(f"\n  0x{addr:08X} [{label}]: {len(refs)} xref(s)")
    for (lis_off, addi_off, rS, rD2, imm16) in refs:
        print(f"    Code: lis @ 0x{lis_off:08X}, addi @ 0x{addi_off:08X} (r{rS}->r{rD2}, imm=0x{imm16:04X})")
