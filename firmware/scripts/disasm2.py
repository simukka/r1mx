#!/usr/bin/env python3
import subprocess

BIN = "/home/simukka/src/RED/firmware/reverse/build_32/extracted/software.bin"

def r2cmd(cmds, timeout=120):
    full = "\n".join(cmds) + "\nq\n"
    result = subprocess.run(
        ["r2", "-a", "ppc", "-b", "32", "-e", "cfg.bigendian=true", "-q", BIN],
        input=full, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout

# Context around 64GB SSD ref and the full function
print("=== Function at 0x4D04D0 (contains RED 64GB SSD ref) ===")
out = r2cmd(["s 0x4D04D0", "pd 80"])
print(out)

print("\n=== Context around 0x4D0480 (before that area) ===")
out = r2cmd(["s 0x4D0450", "pd 50"])
print(out)

