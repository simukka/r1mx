---
title: "Getting the Original Compiler Back"
summary: "Before you can understand a binary, you need to rebuild it. Tracking down the exact compiler that made the RED ONE MX firmware — and proving it, byte for byte."
tags: [toolchain, reconstruction]
---

There is a RED ONE MX sitting on a bench right now, somewhere, with a cracked LCD housing and a dead CF slot and a sensor that still sees light perfectly. The person who owns it is not a collector. They are a working cinematographer who bought this camera when it cost more than a car, who built a business around it, who made films with it that got into festivals and paid crew and meant something to someone. The camera works. The company that made it moved on years ago.

The question is what "moving on" actually means when the tool still functions.

It means the firmware is frozen. It means the parts are harder to find every year. It means if you want to understand what's running inside that camera — what decisions the software is making, what the sensor pipeline is actually doing, whether a bug you've been living with for three years is fixable — you are entirely on your own. No source code. No documentation. No support contract that covers this category of question. Just a 10-megabyte binary and however much patience you have.

This is where reconstruction starts.

---

## The Compiler

Before you can understand a binary, you need to rebuild it. Not read it — rebuild it. Disassemble it, translate a function back to C, compile it, and compare the output byte for byte. If the bytes match, your mental model is correct. If they don't, you're guessing.

To match bytes, you need the same compiler, the same flags, the same toolchain version that RED used in 2009. The firmware binary contains embedded build paths that point to Wind River's toolchain: **GCC 3.4.4**, target `powerpc-wrs-vxworks`, the compiler Wind River shipped with VxWorks 6.4. Not Diab (another common embedded compiler). GCC specifically — which means the output is in principle reproducible.

Wind River's GCC 3.4.4 lives inside the Xilinx ISE 14.7 EDK package. The file is `cum.vxw6-3.4.4-ppc.2009aug07.zip`. Once extracted, it builds inside a 32-bit container because GCC 3.4.4 predates 64-bit host toolchains:

```bash
# One-time setup — build the container image
cd firmware/reverse/build_32/toolchain
docker build -t wr-build:3.4.4 .
```

The [`Dockerfile`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/toolchain/Dockerfile) sets up an i386 Debian environment and extracts `ccppc`, `ldppc`, `objcopyppc`, and `objdumpppc` from the Wind River archive. The [`in-container.sh`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/toolchain/in-container.sh) wrapper mounts the repo into the container so the compiler can see source files without copying anything.

The pinned flags for RED app code — the functions we can actually byte-match — are:

```
-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic
```

Vendor libraries (VxWorks kernel, OpenSSL, Xilinx drivers) were compiled differently. They stay as binary blobs. We only byte-match RED's own application code.

---

## Proving It

The verification tool is [`funcmatch.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/funcmatch.py). It takes a reconstructed C source file, compiles it inside the container, links each function at its original absolute address using [`src/manifest.json`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/src/manifest.json) and [`data_symbols.ld`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/src/units/data_symbols.ld), extracts the bytes, and compares them byte-for-byte against [`software.bin`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/extracted/software.bin). On a mismatch it shows a side-by-side disassembly so you can massage the C until the bytes align.

```bash
# Run funcmatch on a reconstructed source file
firmware/reverse/build_32/toolchain/in-container.sh \
  python3 firmware/scripts/funcmatch.py \
  firmware/reverse/build_32/src/units/red_app_proof.c

# Run all units at once (the CI gate)
make -C firmware/reverse/build_32/src verify-units
```

`verify-units` runs across the current set of reconstructed units. **18 of 18 byte-exact matches.** Exit code 0. The compiler model is confirmed.

Data objects need special handling: when a function references a global variable, GCC emits a two-instruction `lis`/`addi` (or `lis`/`lwz`) pair that encodes the address as a 16-bit hi/lo split. That split is determined at link time by the symbol's absolute address. If we compile a function in isolation, the linker doesn't know where the global lives — it places it somewhere arbitrary, and the instruction encoding differs.

The fix is [`data_symbols.ld`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/src/units/data_symbols.ld): a linker script that `PROVIDE`s every global as an absolute symbol at its real runtime address (`D_<hex_addr>`). GCC then emits the correct `@ha`/`@l` split, and the bytes match.

---

## The RSA Problem

The firmware upgrade package is RSA-1024 signed. Two keys are embedded in the binary at `0x6726F0` and `0x9D29A8`. They appear in every known build — never rotated across the entire product lifetime. `redone.1` is `AES-256-CBC(gzip(software.bin))`. `redone.2` is a 128-byte RSA signature over it.

You can extract the firmware. You can reconstruct it. You cannot repackage a modified firmware for OTA upgrade without RED's private key.

This is not a security discovery. It is a description of the relationship between a camera manufacturer and the people who bought cameras. The camera works. The sensor sees light. The image is still beautiful. But if you want to run modified firmware, you need a JTAG cable and a working knowledge of NOR flash programming. The tool still functions. The right to modify what's running inside it was never in the box.

Understanding the binary is the first step toward changing that. The toolchain is confirmed. Reconstruction can begin.

---

## Following Along

All source files are in [`firmware/reverse/build_32/src/`](https://github.com/simukka/r1mx/tree/master/firmware/reverse/build_32/src/). The reconstruction pipeline runs through [`lift.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/lift.py) (disassembly and scaffolding) → `funcmatch.py` → [`recon_status.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/recon_status.py) (tracking fidelity tiers). The toolchain setup is documented in [`toolchain/README.md`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/toolchain/README.md).
