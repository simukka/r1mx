---
title: "Fifteen False Theories"
summary: "An ISP1562 USB stub. A hand-seeded allocator. A patched dispatcher. Every fix revealed another problem. None of them were real problems."
tags: [qemu, boot, debugging]
---

The launch video for the RED ONE MX showed the camera in slow motion, rotated dramatically, scored with something cinematic. It did not show the two engineers at Wind River who built the VxWorks 6.4 memory allocator. It did not show the Xilinx team who designed the Virtex-4 PCI bridge. It did not show whoever at RED spent six months debugging the C++ initialization sequence in firmware that would ultimately be frozen in 2012 and never touched again.

This is how technology always works. The visible face is the product. The invisible face is the people. When the product is abandoned, the people's work doesn't disappear — it gets sealed inside a binary and handed, silently, to whoever is willing to dig.

We have been digging. And for two weeks, we have been wrong.

---

## Theory One: The PCI Enumerator

VxWorks enumerates PCI devices during boot. Static analysis of the initialization code found a section that allocates a device context table indexed by PCI device count. The RED ONE MX's PCI bus connects to an ISP1562 USB host controller (class `0x0C03`). If QEMU doesn't present that device, the enumerator finds zero devices, the context table allocation fails with error -7, and the boot stalls.

Theory: add an ISP1562 stub to the QEMU machine model.

```bash
# ISP1562 probe script — verifies PCI enumeration finds the device
python3 firmware/scripts/pci_isp1562_probe.py --port 1234
# Before stub: 0 PCI devices found, allocator returns -7
# After stub:  ISP1562 found at 00:0a.0, class 0c03
```

The stub went into `hw/ppc/r1mx_virtex4.c` in [qemu-r1mx](https://github.com/simukka/qemu-r1mx/blob/r1mx/hw/ppc/r1mx_virtex4.c). It fixed real PCI bridge endianness bugs along the way. The allocator still returned -7. The device table was empty for a completely different reason.

---

## Theory Two: The Dispatcher

The root task dispatch mechanism loads a function pointer from a table and jumps to it via `r30`. `r30` is supposed to hold a base address set up in the function's true prologue at `0x37BF78`. The firmware was jumping to a resume label at `0x37C440` — mid-function, after the `r30` setup — so `r30` was zero.

With `r30 = 0`, the dispatcher read through address zero, got whatever happened to be in memory there, and corrupted the PCI configuration registers at offset `0x274`. Every PCI config read was wrong. The enumerator made decisions based on garbage.

Theory: patch the jump target to redirect `0x37C440 → 0x37BF78`.

```bash
# Boot with the dispatch patch applied
firmware/scripts/qemu_boot.sh --patched
```

The dispatcher ran correctly. `r30` was initialized. PCI config reads were intact. The boot still didn't proceed past the device initialization wall. Something deeper.

---

## Theory Three: The Circular Bootstrap

The allocator is a heap object — an instance of some internal class that must be constructed before it can allocate. The constructor requires a working allocator. This is the classic embedded RTOS problem.

The object pointer at `*0xE295C4` held `0xD8FA64`. In the binary at base `0x0`, that address pointed into the string table — not the heap. No valid allocator object. No allocation. No device contexts. No boot.

Theory: the C++ constructor phase never ran, leaving the allocator uninitialized. Fix: hand-build a valid allocator object in memory before boot.

```bash
# Allocator seeder — pre-populates the heap with a valid object
# (this was the wrong approach, but it required correctly reverse-engineering
#  the allocator class layout first)
python3 firmware/scripts/build_allocator.py \
  --port 1234 \
  --base 0xE295C4 \
  firmware/reverse/build_32/extracted/software.bin
```

This required understanding the allocator's internal layout: the vtable pointer at `+0x0`, the free-list head at `+0x8`, the partition handle at `+0x14`. The analysis was correct. The allocator class model was accurate. The boot still didn't work.

---

## What Was Actually Wrong

`*0xE295C4 = 0xD8FA64`. At base `0x0`.

At the correct load base of `0x10000`, the same file location holds a different value. Because the file hasn't changed — the interpretation has. `0xE295C4` at base `0x10000` corresponds to file offset `0xE295C4 - 0x10000 = 0xE195C4`. And at that file offset, the stored value is `0x00FC2530`. A valid heap object pointer. A correctly initialized allocator.

Every `.data` slot we catalogued — all 62 — was correct. At the right address. Read through the wrong base address, they looked like garbage. Built through that frame, we constructed an elaborate theory about a problem that didn't exist.

The ISP1562 stub fixed real bugs. The dispatch analysis documented real control flow. The allocator reverse-engineering produced an accurate model of a real data structure. All of it correct. All of it solving the wrong problem.

---

## On the False Theory Tax

Two weeks of careful, methodical work, most of it now superseded. The institutional version of this story — the one a company would tell — is that this represents waste. Time that should have been spent on something productive.

The independent version is different. Every abandoned product that a community has to reverse-engineer extracts this tax from the people willing to do the work. The company that locked the firmware paid the cost once. The community pays it every time someone starts fresh without access to the documentation that would have made this a two-hour problem instead of a two-week one.

The false theories were not waste. They were the price of secrecy.

The correct answer is next.
