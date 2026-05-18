#!/usr/bin/env python3
"""
Find SDA base register (r13) initialization and access patterns for string refs.
Also disassemble the 'invalid drive type' function cluster.
"""
import struct, subprocess

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"
with open(BIN, "rb") as f:
    data = f.read()

def u32(off): return struct.unpack_from(">I", data, off)[0]
def r2dis(addr, n=40, extra_cmds=None):
    cmds = [f"s 0x{addr:X}", f"pd {n}"]
    if extra_cmds: cmds.extend(extra_cmds)
    full = "\n".join(cmds) + "\nq\n"
    result = subprocess.run(
        ["r2", "-a", "ppc", "-b", "32", "-e", "cfg.bigendian=true", "-q", BIN],
        input=full, capture_output=True, text=True, timeout=30
    )
    return result.stdout[:3000]

# Find r13 initialization: lis r13, X; addi r13, r13, Y
print("=== Looking for r13 SDA initialization ===")
# lis r13: opcode=15(addis), rD=13, rA=0
# bytes: (15<<2)|(13>>3)=0x3D, (13&7)<<5=0x20, hi16...
# 0x3D20XXYY
sda_inits = []
for i in range(0, len(data)-8, 4):
    if data[i] == 0x3D and data[i+1] == 0xA0:  # lis r13
        # Next instruction: addi r13, r13, Y = 0x39AD XXYY
        next4 = data[i+4:i+8]
        if next4[0] == 0x39 and next4[1] == 0xAD:  # addi r13, r13
            hi16 = (data[i+2]<<8)|data[i+3]
            lo16 = (next4[2]<<8)|next4[3]
            sda_base = hi16 * 0x10000 + struct.unpack(">h", next4[2:4])[0]
            sda_inits.append((i, sda_base))
for (off, sda) in sda_inits[:10]:
    print(f"  0x{off:08X}: lis r13 / addi r13 -> SDA base = 0x{sda & 0xFFFFFFFF:08X}")

# Also check r2 (TOC): lis r2 = 0x3C40, addi r2 = 0x3842
print("\n=== Looking for r2/TOC initialization ===")
for i in range(0, len(data)-8, 4):
    if data[i] == 0x3C and data[i+1] == 0x40:  # lis r2
        next4 = data[i+4:i+8]
        if next4[0] == 0x38 and next4[1] == 0x42:  # addi r2, r2
            hi16 = (data[i+2]<<8)|data[i+3]
            lo16 = (next4[2]<<8)|next4[3]
            toc = hi16 * 0x10000 + struct.unpack(">h", next4[2:4])[0]
            print(f"  0x{i:08X}: lis r2 / addi r2 -> TOC = 0x{toc & 0xFFFFFFFF:08X}")
            break

# Also search for addi rD, r13, X where X+SDA = one of our string addresses
# And addi rD, r13, X in general (check if r13 base makes sense)
print("\n=== All unique SDA r13 initializations ===")
for (off, sda) in sorted(set((i, s) for i,s in sda_inits))[:20]:
    print(f"  0x{off:08X}: SDA = 0x{sda & 0xFFFFFFFF:08X}")

