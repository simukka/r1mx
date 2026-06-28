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

## Original Toolchain — Byte-for-Bit Reconstruction

The exact compiler that built Build 32 — **Wind River GNU GCC 3.4.4** (`powerpc-wrs-vxworks`;
re_reference §0.0 confirms GCC, *not* Diab) — is set up and **proven to rebuild RED functions
byte-for-bit**. This is what makes the decompilation goal (readable C that is also bit-for-bit)
achievable, not a compromise.

- **`firmware/reverse/build_32/toolchain/`** — `Dockerfile` (i386 image `wr-build:3.4.4`),
  `in-container.sh` (runs `ccppc`/binutils in the container with the repo bind-mounted;
  rootless-Docker aware), `toolchain.mk` (tool paths + pinned flags), `README.md`. The compiler
  tree is extracted (gitignored) from
  `libraries/GCC3.4.4_VxWorks6.4/cum.vxw6-3.4.4-ppc.2009aug07.zip`.
- **`firmware/scripts/funcmatch.py`** — compiles a unit with `ccppc`, links each function at its
  absolute address (reuses `symbols.ld`), byte-compares to `software.bin`, and on a mismatch
  shows an objdump diff + a `--sweep` flag search.
- **`make -C firmware/reverse/build_32/src verify-units`** — 11/11 byte-exact (MMIO leaves +
  a real RED app function `FUN_004db598`).

```bash
cd firmware/reverse/build_32/toolchain && docker build -t wr-build:3.4.4 .   # one-time
firmware/reverse/build_32/toolchain/in-container.sh python3 \
  firmware/scripts/funcmatch.py firmware/reverse/build_32/src/units/red_app_proof.c
```

**Pinned RED app flags:** `-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic`. Vendor
libc/VxWorks/OpenSSL were built with *different* Wind River flags → keep them as blob; only
byte-match RED app code. Data-object addresses must be passed as linker symbols
(`units/data_symbols.ld`, `D_<addr>`) so gcc emits the `@ha/@l` (lis/addi) relocation.

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

The firmware binary is `firmware/reverse/build_32/extracted/software.patched.r1mx.bin`,
**built from source** with `make -C firmware/reverse/build_32/src install` (patches live
as flag-gated assembly in `firmware/reverse/build_32/src/patches/patches.S`; see that
tree's `README.md`). The legacy `patch_firmware.py` byte-patcher has been retired.

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
| `0xe1200000` | XPci_v3 host bridge | ✅ Phase 2 |
| `0xe0080000`–`0xe0200000` | RED histogram IP ×5 | ✅ Phase 3 |
| `0xf0000000` | NOR flash (128 MB, returns 0xFF) | ✅ Phase 4 |
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

## Live Hardware Access (host → XMD → PPC405)

The host can drive the **live PPC405** over JTAG directly (no hand-typing in the VM).
XMD (`connect ppc hw`, in the WinXP VM `r1mx_32`) is itself a **GDB stub on TCP 1234**; a
VirtualBox NAT port-forward exposes it to the host as `:2345`, and the same Python RSP client
that drives QEMU drives the silicon. This enables **lock-step diffing** of HW vs QEMU to
finish the Phase 1–5 device models.

```bash
# one-time per session: forward the VM's stub to the host
VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"
# step HW + QEMU together, report first divergence (an unmodeled peripheral read)
firmware/scripts/qemu_boot.sh --patched --debug          # QEMU stub :1234
python3 firmware/scripts/lockstep_diff.py --bp 0x36c350 --steps 500 \
        --watch 0xe0600000:16
```

- `firmware/scripts/rsp.py` — shared RSP client (read-only by default; **hardware**
  breakpoints only, so the camera's memory is never patched).
- `firmware/scripts/lockstep_diff.py` — HW↔QEMU instruction diff + `--mmio-capture`.
- `firmware/scripts/xmd_rpc.py` + `xmd_agent.tcl` — no-network fallback (Channel B) for
  XMD-only commands (`mrd`/SPRs/JTAG) via the shared folder.
- **Full runbook + READ-ONLY rules:** `firmware/reverse/build_32/host_xmd_bridge.md`.

---

## Key References

- **`firmware/reverse/build_32/re_reference.md`** — full memory map, driver versions, section 6d for embedded build paths
- **`plans/qemu_xilinx_drivers.md`** — peripheral emulation plan with register maps and self-test requirements
- **`plans/working_camera_jtag_analysis.md`** — SOP to capture live device behavior from a WORKING camera over JTAG (audio_pci/sensor/PCI/IRQ map) to finish the QEMU models
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
