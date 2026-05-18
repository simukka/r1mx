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
1. Downloads QEMU 8.2.2 (SHA-256 verified) to `~/src/qemu-r1mx/`
2. Applies 6 patches from `firmware/patches/qemu/`
3. Configures and builds `ppc-softmmu` only

Output binary: `~/src/qemu-r1mx/build/qemu-system-ppc`

**Verify the machine is available:**
```bash
~/src/qemu-r1mx/build/qemu-system-ppc -M help | grep r1mx
# Expected: r1mx-virtex4    RED ONE MX Xilinx Virtex-4 FX
```

**Rebuilding after source changes** (no re-download):
```bash
cd ~/src/qemu-r1mx/build && ninja qemu-system-ppc
```

**Clean rebuild from scratch:**
```bash
./firmware/scripts/build_qemu.sh --clean
```

### What the patches do

| Patch | File | Purpose |
|---|---|---|
| `0001` | `hw/ppc/meson.build` | Register `r1mx_virtex4.c` in build system |
| `0002` | `target/ppc/mmu_helper.c` | Fix PPC32 TLB vaddr truncation (upstream bug) |
| `0003` | `accel/tcg/cputlb.c` | Fix PPC32 cross-page address overflow (upstream bug) |
| `0004` | `target/ppc/translate.c` | Add PPC405 FSL instruction support (FPGA comms) |
| `0005` | `target/ppc/helper_regs.c` | Silence SLER abort from firmware boot countdown |
| `0006` | `hw/ppc/r1mx_virtex4.c` | FPGA catch-all MMIO (prevent MCE crashes) + LCD TCP bridge (port 17186) |

See `firmware/patches/qemu/README.md` for full descriptions.

---

## Step 2 - Patch the Firmware Binary

The patched binary is committed at `firmware/reverse/build_32/extracted/software.patched.bin`
and ready to use. To regenerate it (e.g. after adding new patches):

```bash
cd ~/src/RED/r1mx
.venv/bin/python firmware/scripts/patch_firmware.py --r1mx
# Output: firmware/reverse/build_32/extracted/software.patched.r1mx.bin
```

The `--r1mx` flag applies 59 of 64 patches (5 bamboo-machine MMIO NOPs are skipped
since the `r1mx-virtex4` machine models those peripherals with real device stubs).

### What the patches fix

The firmware was designed for real hardware. In QEMU, several things break without patches:

- **Stack relocation** (patch #1): Initial SP set to 256 MB rather than 1 MB, to
  avoid overwriting kernel BSS during early stack use
- **Stack canary wait** (patches #2, #3): Two loops that wait for canary values
  to appear in memory are NOP'd (they never appear in emulation)
- **Unimplemented SPR writes** (patch #58, rfi handler at 0x700): The Program
  Exception vector is replaced with `mfspr SRR0 / addi +4 / mtspr SRR0 / rfi`,
  cleanly skipping any unimplemented hardware register write
- **Various task-init and scheduler fixes** (patches #42-57): Null-pointer guards,
  scheduler selection fix, WDB network wait NOP, etc.

For the full patch table see `firmware/scripts/patch_firmware.py` or the
`### Patches Required` section of `re_reference.md`.

---

## Step 3 - Normal Boot (No Debugger)

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --patched
```

QEMU launches with `-nographic`; the XUartLite console appears on stdout.

**Expected serial output** (first 2-3 seconds):
```
^^^123456789
(VxWorks kernel banner)
^^^123456789
(second usrInit pass from root task)
```

The triple `^^^` followed by digits `1`-`9` is the hardware sequencer
(`fn_DCB0`) printing a progress marker before each subsystem init.

**System is up** when output stops and the process idles. The WDB agent is
listening on UDP 17185. Press `Ctrl+A X` to quit QEMU.

---

## Step 4 - Debug Boot (GDB RSP on TCP:1234)

```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --patched --debug
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
./scripts/qemu_boot.sh --patched --net
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
./scripts/qemu_boot.sh --patched -- -d int,cpu_reset 2>crash.log

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
| `--patched` | Use `software.patched.r1mx.bin` (required) |
| `--debug` | Halt at 0x0, GDB stub on tcp:1234 |
| `--net` | Enable TAP networking (requires tap0) |
| `--build13` | Use Build 13 legacy binary |
| `-- <extra args>` | Pass extra flags directly to QEMU |

---

## See Also

- `firmware/patches/qemu/README.md` - QEMU patch descriptions
- `firmware/reverse/build_32/re_reference.md` - Full reverse engineering notes
- `firmware/reverse/build_32/debug_interfaces.md` - WDB, USB shell, UART details
- `firmware/reverse/build_32/build32_subsystem_map.md` - Peripheral address map
