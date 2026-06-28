---
title: "The One Number That Explained Everything"
summary: "software.bin links for base address 0x10000. QEMU was loading it at 0x0. One 65,536-byte error was the root cause of every wrong theory, every garbage value, every false fix — for two weeks."
tags: [qemu, firmware, boot]
---

RED sold the ONE MX as a professional investment. The brochure language: *built for the long haul, an image quality that won't go out of style.* The cinematographers who bought it understood that to mean: buy this once, own this, work with this for years. Build your business around it.

What they didn't understand — what nobody told them — was that "professional investment" applied to the sensor and not the ecosystem. The image quality is still there. The support is not. The firmware is frozen. The documentation was never public. The source code lives on someone's hard drive at a company that has moved on.

This is what it costs to reverse-engineer an abandoned tool: you pay the tax on every assumption the manufacturer never bothered to document. For two weeks, we paid that tax on a single number.

The number is `0x10000`.

---

## What "Linked For" Means

A linker assumes a base address when it resolves a binary. Every absolute address in the output — every function pointer, every global variable address, every rodata string reference — is computed relative to that base. If the base is `0x10000`, a variable at link offset `0x5000` lives at address `0x15000`. A function at link offset `0x24F03C` lives at `0x25F03C`.

If you load the binary at address `0x0` instead of `0x10000`, nothing crashes immediately. The CPU starts fetching instructions from wherever the reset vector points. Early boot code is position-independent. For the first hundred instructions, everything looks fine.

Then you hit a `.data` reference. A function pointer slot. A dispatch table entry. The value stored there was written by the linker, which assumed the binary would live at `0x10000`. Loaded at `0x0`, you're reading it at the wrong address — and the value you get is 65,536 bytes off from what it should be. Not random. Not corrupted. Just shifted. By exactly one base address.

---

## The Evidence That Was There All Along

The embedded symbol table — the one we used to resolve driver function names — stores runtime addresses. Every symbol value in the table assumes the binary is loaded at `0x10000`. `XIic_MasterSend` is at `0x251EC` in the file; the symbol table says `0x261EC`.

The embedded build paths in the binary reference `0x10180` and `0x10040` as relocation anchors. The section addresses in the link map (recoverable from BSS region analysis) all start at `0x1xxxx`.

The evidence was in the binary from the beginning. We read it through the assumption that the base was `0x0`, so it looked like evidence that the system had been captured mid-execution rather than evidence of a wrong load address.

---

## The Fix

One line in the QEMU machine configuration. In [`hw/ppc/r1mx_virtex4.c`](https://github.com/simukka/qemu-r1mx/blob/r1mx/hw/ppc/r1mx_virtex4.c), the firmware loader is changed from:

```c
/* Before — loads at address 0x0 */
rom_add_file_fixed(bios_name, 0x00000000, -1);
```

to:

```c
/* After — loads at the correct link base */
rom_add_file_fixed(bios_name, 0x00010000, -1);
```

Or equivalently, via the QEMU command line using [`qemu_boot.sh`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/qemu_boot.sh):

```bash
# This is what qemu_boot.sh does internally — load at 0x10000
firmware/scripts/qemu_boot.sh
# (No --patched flag. The original software.bin. No patches needed.)
```

That's it. One number. After two weeks.

---

## What Was Instantly Resolved

Every `.data` slot that had looked like garbage:

```bash
# Verify the .data slots at correct base
python3 - <<'EOF'
import struct
from pathlib import Path

image = Path('firmware/reverse/build_32/extracted/software.bin').read_bytes()
base  = 0x10000

slots = {
    'gate':      0xE0BDFC,
    'guardzone': 0xE295E4,
    'usrRoot_flag': 0xE2706C,
    'canary':    0xE169A4,
    'allocator': 0xE295C4,
}

for name, va in slots.items():
    off   = va - base
    value = struct.unpack_from('>I', image, off)[0]
    print(f'{name:16s} {va:#010x} = {value:#010x}')
EOF
```

Output:
```
gate             0xe0bdfc = 0xffffffff   # disabled flag ✓
guardzone        0xe295e4 = 0x00000000   # zero at cold boot ✓
usrRoot_flag     0xe2706c = 0x00000000   # zero ✓
canary           0xe169a4 = 0x12348765   # integrity canary ✓
allocator        0xe295c4 = 0x00fc2530   # valid heap object pointer ✓
```

All correct. Every one. The "garbage" was our misread.

The ISP1562 stub: not needed for boot (though its PCI bridge fixes remain). The dispatch patch: the jump to `0x37C440` is the correct entry at the right address, no patch needed. The hand-built allocator: `0x00FC2530` is already a valid object, sitting in the binary waiting to be read correctly. The circular bootstrap mythology: dissolved. The firmware dispatches to `usrRoot` naturally. The allocator builds. Device enumeration runs.

---

## What It Means for the Camera

The camera's firmware is not broken. It never was. The emulator was reading it wrong.

This matters beyond the technical fix. It means the firmware — the actual VxWorks 6.4 OS plus seventeen years of RED application code — is a coherent, complete, cold-boot image that works exactly as designed. Every assumption the code makes about its own initialization is correct. The groundwork for understanding it is now solid.

The people who made their livelihood with this camera bet on a tool that still functions correctly. The institution around it was abandoned. The tool itself was not.
