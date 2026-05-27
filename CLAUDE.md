# RED ONE MX Reverse Engineering — Project Guide

## Overview

Reverse engineering the **RED ONE MX** digital cinema camera firmware.
Target: PPC405F6 (Xilinx Virtex-4 FX), VxWorks 6.4, Build 32 (v32.0.3).

---

## Repository Layout

```
firmware/
  reverse/build_32/        — disassembly, notes, patched binaries
    re_reference.md        — master reference: memory map, drivers, findings
    xsrc/                  — symlinks to exact Xilinx driver sources found in firmware
    extracted/             — raw extracted firmware blobs
  scripts/                 — analysis and patching scripts
  reference/               — datasheets and Wind River manuals
plans/
  qemu_xilinx_drivers.md   — QEMU peripheral implementation plan (Phases 1–5)
```

---

## QEMU Emulator

### Fork

**GitHub:** https://github.com/simukka/qemu-r1mx  
**Base:** QEMU 8.2.2 (`main` branch = upstream `v8.2.2` tag)  
**Working branch:** `r1mx`

### Clone and Build

```bash
git clone -b r1mx git@github.com:simukka/qemu-r1mx.git
cd qemu-r1mx

# Configure (PPC softmmu only, minimal deps)
mkdir build && cd build
../configure \
  --target-list=ppc-softmmu \
  --enable-debug \
  --disable-docs \
  --disable-werror

make -j$(nproc)
```

> **Tip:** On Ubuntu/Debian, install build deps first:
> `sudo apt install build-essential libglib2.0-dev libpixman-1-dev python3 ninja-build`

### Run Firmware

```bash
./build/qemu-system-ppc \
  -machine r1mx-virtex4 \
  -bios /path/to/firmware.bin \
  -serial mon:stdio \
  -nographic
```

The firmware binary is `firmware/reverse/build_32/extracted/software.patched.r1mx.bin`
(patched to boot in QEMU; see `firmware/scripts/patch_firmware.py`).

### Machine: `r1mx-virtex4`

Source: `hw/ppc/r1mx_virtex4.c` in the `r1mx` branch.

| Address | Peripheral | Status |
|---------|-----------|--------|
| `0xe0600000` | XUartLite (console) | ✅ |
| `0xe0640000` | XUartNs550 #1 | ✅ |
| `0xe0650000` | XUartNs550 #2 | ✅ |
| `0xe0800000` | XIntc (interrupt controller) | ✅ |
| `0xe1020000` | XEmacLite (Ethernet) | ✅ |
| `0xb2600000` | XIic (I2C) | ✅ |
| `0x64010000` | XPS Central DMA | ✅ Phase 1 |
| `0xe1200000` | XPci_v3 host bridge | ⏳ Phase 2 |
| `0xe0080000`–`0xe0200000` | RED histogram IP ×5 | ⏳ Phase 3 |
| `0xf0000000` | NOR flash | ⏳ Phase 4 |
| TBD | External timer (VxWorks tick) | ⏳ Phase 5 — **critical** |

See `plans/qemu_xilinx_drivers.md` for full implementation plan.

### PPC405 Core Patches (also on `r1mx` branch)

| File | Fix |
|------|-----|
| `accel/tcg/cputlb.c` | Truncate `page[1].addr` to 32-bit to prevent bogus host address on page splits at `0xFFFFFFFF` |
| `target/ppc/mmu_helper.c` | Cast `eaddr` to `target_ulong` before masking in `ppc_cpu_tlb_fill` |
| `target/ppc/helper_regs.c` | Silence `cpu_abort` on non-zero SLER writes (firmware writes transiently during early boot) |
| `target/ppc/translate.c` | Add PPC405 FSL instruction stubs (XO 0x130–0x13F) |

---

## Key References

- **`firmware/reverse/build_32/re_reference.md`** — full memory map, driver versions, section 6d for embedded build paths
- **`plans/qemu_xilinx_drivers.md`** — peripheral emulation plan with register maps and self-test requirements
- **`firmware/reverse/build_32/xsrc/`** — 43 exact Xilinx driver source files as found in the firmware binary
- Xilinx ISE 14.7 EDK drivers: `~/src/RED/drivers/`
- VxWorks 6.4 BSP sources: `~/src/RED/Xilinx_ISE_DS_Lin_14.7_1015_1/`

---

## Contributing Changes to QEMU Fork

```bash
cd ~/src/qemu-r1mx
git checkout r1mx
# make changes ...
git add <files>
git commit -m "hw/xxx: description

Detailed explanation.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin r1mx
```
