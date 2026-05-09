#!/usr/bin/env python3
"""Disassemble key areas using r2."""
import subprocess, os

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"

def r2cmd(cmds):
    """Run r2 commands on the binary."""
    full = "\n".join(cmds) + "\nq\n"
    result = subprocess.run(
        ["r2", "-a", "ppc", "-b", "32", "-e", "cfg.bigendian=true", "-q", BIN],
        input=full, capture_output=True, text=True, timeout=60
    )
    return result.stdout

# 1. Disassemble context around the RED 64GB SSD reference
print("=== Context around RED 64GB SSD ref @ 0x4D0500 ===")
out = r2cmd([
    "s 0x4D04C0",
    "pd 60"
])
print(out[:4000])

