---
title: "First Contact"
summary: "QEMU loads the firmware and immediately jumps into a string. The first crash is at address 0xD7E680 — and what's there is not code."
tags: [qemu, boot, firmware]
---

You need to understand something about the RED ONE MX before we go any further: it was never a cheap camera. When it came out, it cost more than most people's annual salary. Cinematographers who bought one did not buy it the way you buy a consumer device. They bought it the way you sign a professional relationship. They built workflows around it, bought accessories for it, trained crews on it, built businesses on the image it produced.

Then RED moved on. New bodies. New sensors. New ecosystems. The old cameras kept working — they still work — but the institutional support that justified the investment quietly ended. Firmware frozen at Build 32. Parts getting harder to find. No path forward except the community.

The binary we're working with is called `software.bin`. It's extracted from the `.su` upgrade file using a key that the community already reverse-engineered. Ten megabytes of PowerPC instructions, the complete camera OS, compiled in 2009 by people who almost certainly never expected anyone to read it this carefully.

---

## Extracting the Firmware

The upgrade archive (`redone.su`) is AES-256-CBC encrypted and gzip compressed. Once decrypted and decompressed, `software.bin` is the raw stripped binary — no ELF headers, no symbol names, no debug information. Just code and data, laid out in memory order.

```bash
# The extraction key is documented in firmware/README.md
# Resulting file: firmware/reverse/build_32/extracted/software.bin
ls -lh firmware/reverse/build_32/extracted/software.bin
# -rw-r--r-- 1 user user 9.8M Jun  4 software.bin
```

Two independent builds — Build 31 and Build 32 — show the same structural patterns in `.data`. The inconsistencies aren't artifacts of how we extracted the file. They're properties of the file itself.

---

## Loading It

The QEMU emulator is a fork of QEMU 8.2.2 built for the Xilinx Virtex-4 FX platform. Clone it, build it, and point it at the binary:

```bash
git clone -b r1mx git@github.com:simukka/qemu-r1mx.git
cd qemu-r1mx && mkdir build && cd build
../configure --target-list=ppc-softmmu --enable-debug --disable-docs --disable-werror
make -j$(nproc)
```

Or use the boot script from this repo, which handles all the flags:

```bash
# Boot the original (unpatched) firmware — this is what you want
firmware/scripts/qemu_boot.sh

# Boot with a GDB stub open on port 1234
firmware/scripts/qemu_boot.sh --debug
```

The first time you run this, the firmware loads, the PPC405 core starts executing from the reset vector, and approximately 200 instructions later it crashes.

---

## The Crash

The crash is at `fn_36f9f8`. This function loads a function pointer from `.data` at `0xE26D28`, reads whatever is stored there, and calls it via `bctrl` — branch to count register, the PowerPC indirect call instruction.

At cold boot, `0xE26D28` holds `0xD7E680`. The processor branches to `0xD7E680` and tries to execute what it finds:

```bash
# Disassemble what's at 0xD7E680 in the binary
# (file offset = 0xD7E680 - 0x10000 = 0xD6E680)
powerpc-linux-gnu-objdump \
  -D -b binary -m powerpc:403 -EB \
  --start-address=0xD6E680 --stop-address=0xD6E690 \
  --adjust-vma=0x10000 \
  firmware/reverse/build_32/extracted/software.bin
```

The output:

```
   d7e680:  63 65 72 74    andi.   r5,r27,0x7274
   d7e684:  20 64 65 70    subfic  r3,r4,0x6570
   d7e688:  74 68 3d 25    andis.  r8,r4,0x3d25
```

That is not code. Those bytes are `"cert depth=%d %s\n"` — an OpenSSL error string, stored in rodata. The processor is trying to execute a diagnostic message.

A Program Exception fires at `0x700`. VxWorks's machine check handler. Boot fails.

---

## The .data Mystery

That `0xE26D28` slot holds a string pointer because the entire `.data` section looks wrong. Not one or two slots — systematically wrong. A scan of dispatch tables, function pointer arrays, and initialization guards finds roughly 48 to 62 entries that look like they were captured mid-execution rather than set at link time.

The first hypothesis, reasonable and wrong: C++ static constructors didn't run. VxWorks initializes C++ objects through a constructor registration mechanism. If that mechanism doesn't fire, objects stay in their linker-initial state — which can include stale pointer values.

```bash
# Scan for null-guarded dispatch slots with non-zero values
python3 firmware/scripts/scan_null_guarded_dispatch.py \
  firmware/reverse/build_32/extracted/software.bin
# Prints: 62 slots with non-null values at link-time
```

62 dirty slots. All consistent with a system that initialized and then was captured. Or consistent with a system loaded at the wrong address. We don't know which yet.

---

## Who This Crash Belongs To

The crash at `0xD7E680` is not a physics problem. The hardware works. The sensor sees light. The CPU executes instructions exactly as designed. The crash is a software problem — specifically, a mystery about why a data section that should contain cold-boot values doesn't.

And the mystery matters because of the camera sitting on that bench. The one with the cracked LCD and the working sensor. The one that still makes beautiful images. If we can't understand this binary well enough to understand why it crashes in emulation, we can't understand it well enough to fix the things that are actually broken in the camera.

The crash is the beginning of a conversation. The conversation will take two weeks. The answer, when it comes, will be embarrassingly simple.
