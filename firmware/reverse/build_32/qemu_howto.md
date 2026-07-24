# Running RED ONE MX Build 32 Firmware in QEMU

Step-by-step guide to emulating the RED ONE MX Build 32 VxWorks firmware
(v32.0.3, PPC405F6 on Xilinx Virtex-4) using a custom QEMU build.

---

## Overview

The firmware runs on a Xilinx Virtex-4 FX SoC with a PPC405F6 hard-core CPU,
booting VxWorks 6.x. A custom QEMU machine (`r1mx-virtex4`) models the relevant
peripherals: XUartLite (console), XEmacLite (Ethernet/WDB), XIntc (interrupts).

The binary also requires several patches to skip hardware-init code that deadlocks
in emulation. These are applied by `firmware/scripts/patch_firmware.py --r1mx`.

**End result:** VxWorks boots fully to the WDB agent (UDP port 17185) within a
few seconds, with serial output on stdout and an optional TAP network interface
for live debugging.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| `git`, `curl` | For cloning and downloading |
| `gcc`, `ninja` or `make`, `pkg-config` | QEMU build toolchain |
| `libglib2.0-dev`, `libpixman-1-dev` | QEMU build deps (Debian/Ubuntu) |
| `python3.12+` with `.venv/` activated | Repo venv at `.venv/` |
| `patch` | Applying QEMU source patches |
| Root / `sudo` for TAP setup | Only needed for WDB networking |

Install build dependencies on Debian/Ubuntu:
```bash
sudo apt install -y git curl gcc ninja-build pkg-config \
  libglib2.0-dev libpixman-1-dev python3-venv
```

---

## Step 1 - Build the Custom QEMU

The patched QEMU adds the `r1mx-virtex4` machine and several upstream bug fixes.
Run the build script from the repo root:

```bash
cd ~/src/RED/r1mx
./firmware/scripts/build_qemu.sh
```

This script:
1. Clones `https://github.com/simukka/qemu-r1mx` (branch `r1mx`) to `~/src/qemu-r1mx/`
2. Configures and builds `ppc-softmmu` only

Output binary: `~/src/qemu-r1mx/build/qemu-system-ppc`

**Verify the machine is available:**
```bash
~/src/qemu-r1mx/build/qemu-system-ppc -M help | grep r1mx
# Expected: r1mx-virtex4    RED ONE MX Xilinx Virtex-4 FX
```

**Rebuilding after source changes:**
```bash
cd ~/src/qemu-r1mx/build && make -j$(nproc)
```

**Clean rebuild from scratch:**
```bash
./firmware/scripts/build_qemu.sh --clean
```

### What the fork changes (commits on `r1mx` branch)

| Commit | Files | Purpose |
|--------|-------|---------|
| `cc3b2ca` | `target/ppc/mmu_helper.c` | Fix PPC32 TLB vaddr truncation (upstream bug) |
| `cc3b2ca` | `accel/tcg/cputlb.c` | Fix PPC32 cross-page address overflow (upstream bug) |
| `cc3b2ca` | `target/ppc/translate.c` | Add PPC405 FSL instruction support (FPGA comms) |
| `cc3b2ca` | `target/ppc/helper_regs.c` | Silence SLER abort from firmware boot countdown |
| `e2f206c` | `hw/ppc/r1mx_virtex4.c`, `hw/ppc/meson.build` | r1mx-virtex4 machine + FPGA catch-all MMIO + LCD TCP bridge |
| `e2f206c` | `hw/dma/xilinx_dma_opb.c`, `hw/dma/meson.build` | XPS OPB DMA device model (`xlnx.opb-dma-channel`) |

Full history: https://github.com/simukka/qemu-r1mx/commits/r1mx

---

## Step 2 - Firmware Binary (no patching)

No firmware patching is required. QEMU boots the **original** committed image at
`firmware/reverse/build_32/extracted/software.bin`; it runs unmodified once loaded at
base `0x10000` (which the `r1mx-virtex4` machine does automatically via
`hreset_vector`). The obsolete binary-patch build has been retired — the fixes that
once lived as firmware byte patches (stack relocation, canary-wait NOPs, the Program
Exception `rfi` handler) are now provided by the QEMU device models and the PPC405
core patches in the qemu-r1mx fork (see the "PPC405 Core Patches" table in
`CLAUDE.md`), not by modifying the image.

To rebuild a *reconstructed* image from source (byte-exact units relinked onto the
original substrate), use the carve-out relink model:

```bash
make -C firmware/reverse/build_32/src relink   # -> build/software.relinked.bin
make -C firmware/reverse/build_32/src verify    # assert byte-exact relink == software.bin
```

See `firmware/reverse/build_32/src/README.md` for the full reconstruction workflow.

---

## Step 3 - Normal Boot (No Debugger)

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh
```

QEMU launches with `-nographic`; the XUartLite console appears on stdout.

**Expected serial output** (first ~5 seconds): a long burst of identical
`^^^123456789` lines — about **18,700** of them — then complete silence.
Each line is one call to `fn_DCB0` (the hardware sequencer), printed before
each subsystem brought up across both `usrInit` passes and every nested
initializer; the count reflects the total subsystem-init invocations, not
two distinct passes. (An earlier version of this guide claimed only two
lines appear; that was a misread of the tail of the log.)

**System is up** when the `^^^123456789` torrent stops (count locks at
~18,701) and the process idles. QEMU stays at ~100% CPU even when idle —
that's the patched 0x700 rfi-skip handler absorbing Program exceptions
from unimplemented PPC405 SPRs accessed by the VxWorks idle path, not a
crash loop. The WDB agent is listening on UDP 17185. Press `Ctrl+A X` to
quit QEMU.

---

## Step 4 - Debug Boot (GDB RSP on TCP:1234)

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --debug
```

QEMU halts immediately at PC=0x0 and opens a GDB RSP stub on `tcp:1234`.
Connect from another terminal with `gdb-multiarch` or `r2`:

**gdb-multiarch:**
```bash
gdb-multiarch
(gdb) set arch powerpc:common
(gdb) target remote localhost:1234
(gdb) break *0x36c350    # usrInit
(gdb) continue
```

**radare2:**
```bash
r2 -a ppc -b 32 -e cfg.bigendian=true \
   -D gdb gdb://localhost:1234 \
   -i scripts/r2_debug.r2
```

### Key breakpoints

| Address | Symbol | Notes |
|---|---|---|
| `0x36c350` | `usrInit` | Main boot init entry |
| `0x5a7f30` | `kernelInit` | VxWorks multitasking start (never returns) |
| `0x37c440` | WDB task entry | Confirms WDB agent is running |
| `0xa8` | Idle loop | CPU idle after all tasks start |

### GDB protocol notes (CRITICAL)

- **Use hardware breakpoints** (`hbreak` / `Z1` type) or set BPs only at
  function entry/return boundaries. SW breakpoints use a PPC trap instruction
  which triggers a Program Check exception at 0x700. Before `usrInit` installs
  exception handlers, hitting a SW BP inside early-init code causes an
  immediate crash.
- **Never single-step** inside `fn_36e168` (exception handler install) or
  between `fn_DCB0` sub-calls before the handlers are installed.
- Hardware write watchpoints (`Z2,addr,4`) work reliably on PPC405 QEMU.
- Stale SW BPs persist across QEMU restarts (`R00`): always clear them at the
  start of a new session.

---

## Step 5 - WDB Networking (TAP Interface)

WDB (Wind River Debug) is the firmware's always-on remote debug agent. It runs
over UDP and provides memory read/write, task inspection, symbol lookup, and
arbitrary function injection.

### One-time TAP setup (as root)

```bash
sudo ip tuntap add dev tap0 mode tap
sudo ip addr add 192.168.0.1/24 dev tap0
sudo ip link set tap0 up
```

### Boot with networking

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --net
# [*] Networking: TAP (tap0 -> XEmacLite) - camera will be 192.168.0.2
# [*] WDB connect: wdbrpc 192.168.0.2 17185
```

The XEmacLite MAC is set to `00:0a:35:00:00:01` (Xilinx OUI). The firmware
configures the camera at IP `192.168.0.2`.

### Connecting to WDB

```bash
# Wind River wdbrpc tool (part of Workbench / VxWorks SDK):
wdbrpc 192.168.0.2 17185

# Or use the wtx Python client (if available):
python3 -c "import wtxrpc; c = wtxrpc.WtxRpc('192.168.0.2', 17185); print(c.target_info())"
```

**WDB capabilities:**
- Read/write arbitrary memory (`wdbMemRead`, `wdbMemWrite`)
- List all VxWorks tasks and their registers
- Look up symbols by name (`symFind`)
- Inject and call arbitrary functions (`wdbFuncCall`)
- Set/clear breakpoints and read task context

### Key WDB addresses / variables

| Address | Contents |
|---|---|
| `0xE9C4BC` | WDB port (value `0x4321` = 17185) |
| `0xE9C420` | WDB agent state |
| `0x020390d0` | Root task descriptor (all-zeros at cold boot) |

---

## Crash Diagnosis Workflow

When the firmware crashes or hangs, capture QEMU interrupt log:

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh -- -d int,cpu_reset 2>crash.log

# Find the crash address:
grep "PC=" crash.log | head -10

# Disassemble the crash site:
r2 -a ppc -b 32 -e cfg.bigendian=true -q \
   -c "pd 16 @ 0x<CRASH_ADDR>" \
   reverse/build_32/extracted/software.bin
```

Adding a new patch:
```bash
# Check the bytes at the crash address:
.venv/bin/python firmware/scripts/patch_firmware.py --probe 0x<CRASH_ADDR>
# Copy the Patch entry output, add to KNOWN_PATCHES in patch_firmware.py
```

---

## Quick Reference

### Boot addresses (Build 32, base 0x00000000)

| Address | Symbol |
|---|---|
| `0x00000000` | Reset vector / romInit |
| `0x00000700` | Program Exception vector (rfi skip handler) |
| `0x0036C350` | `usrInit` - main boot init |
| `0x005A7F30` | `kernelInit` - starts multitasking (never returns) |
| `0x0037C440` | WDB task entry |
| `0x000000A8` | Idle loop |

### Memory layout

| Range | Contents |
|---|---|
| `0x00000000 - 0x00E9BF1F` | Code + data (RO after boot) |
| `0x00E9BF20 - 0x01153480` | BSS (zeroed at boot) |
| `0x01153480 - 0x0FF9C000` | Heap (task stacks, VxWorks pools) |
| `0x0FF9C000 - 0x10000000` | Reserved (kernel workspace) |
| `0xE0600000` | XUartLite (console UART) |
| `0xE0800000` | XIntc (interrupt controller) |
| `0xE1020000` | XEmacLite (Ethernet/WDB) |

### qemu_boot.sh flag summary

| Flag | Effect |
|---|---|
| `--debug` | Halt at the reset vector (PC=0x10000), GDB stub on tcp:1234 |
| `--net` | Enable TAP networking (requires tap0) |
| `-- <extra args>` | Pass extra flags directly to QEMU |

---

## See Also

- https://github.com/simukka/qemu-r1mx/commits/r1mx - QEMU fork commit history
- `firmware/reverse/build_32/re_reference.md` - Full reverse engineering notes
- `firmware/reverse/build_32/debug_interfaces.md` - WDB, USB shell, UART details
- `firmware/reverse/build_32/build32_subsystem_map.md` - Peripheral address map
