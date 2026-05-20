---
name: re-build32
description: This skill should be used when the user asks to "reverse engineer the firmware", "load the RE context", "run build 32 in QEMU", "debug the firmware", "add a patch", "continue the RE session", "boot the emulator", "connect WDB", or mentions build_32, patch_firmware, VxWorks, PPC405, or the RED ONE MX camera firmware. Provides the full RE workflow for Build 32 v32.0.3 emulation and decompilation.
version: 0.1.0
---

# RED ONE MX Build 32 — Reverse Engineering Skill

**Goal:** Decompile and reverse-engineer the RED ONE MX Build 32 firmware (v32.0.3, PPC405F6, VxWorks 6.x), run it fully in a custom QEMU emulator, and test firmware modifications before deploying to real hardware.

**Firmware:** `firmware/reverse/build_32/extracted/software.bin`  
**Patched binary:** `firmware/reverse/build_32/extracted/software.patched.r1mx.bin`  
**QEMU machine:** `r1mx-virtex4` (custom-patched build via `firmware/scripts/build_qemu.sh`)

## Current Boot State (Session 21+)

The firmware boots fully unattended with 59/64 patches applied (`--r1mx`):

- romInit → usrInit → kernelInit (0x5a7f30) → rootTask (0x37c440) → WDB task ✓
- Serial output `^^^123456789` appears twice (once per usrInit call) ✓
- System idles at PC=0x10 after all tasks start ✓
- WDB agent listening on UDP 17185 — **not yet connected via TAP**

**Next milestone:** Connect WDB via TAP networking, use it to inspect the root task descriptor at `0x020390d0` (all-zeros at cold boot).

## Quick Start

### Boot (no debugger)
```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --patched
# Ctrl+A X to quit
```

### Boot with networking (for WDB)
```bash
# One-time TAP setup (as root):
sudo ip tuntap add dev tap0 mode tap
sudo ip addr add 192.168.0.1/24 dev tap0
sudo ip link set tap0 up

cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --patched --net
# WDB: wdbrpc 192.168.0.2 17185
```

### Boot with GDB debugger
```bash
cd ~/src/RED/r1mx/firmware
./scripts/qemu_boot.sh --patched --debug
# In second terminal: gdb-multiarch, target remote localhost:1234
```

### Regenerate patched binary (after adding patches)
```bash
cd ~/src/RED/r1mx
.venv/bin/python firmware/scripts/patch_firmware.py --r1mx
```

### Build / rebuild QEMU
```bash
cd ~/src/RED/r1mx
./firmware/scripts/build_qemu.sh           # normal build (downloads + patches + compiles)
./firmware/scripts/build_qemu.sh --clean   # wipe and rebuild from scratch
```

QEMU patches live in `firmware/patches/qemu/`. To fix or improve QEMU behaviour, edit a patch file there and re-run `build_qemu.sh`. Never edit `~/src/qemu-r1mx/` directly — those changes are lost on a clean build.

## GDB RSP Critical Rules

- **SW BPs (Z0) only** — QEMU PPC405 HW BPs broken
- **Write watchpoints (Z2,addr,4) DO work** — use for "who writes this memory?" questions
- **Never place SW BPs inside a function run at full speed** — trap fires into exception vectors; before fn_36e168 completes (0x36c3d0) they crash immediately
- **GDB RSP send `$c#63`, do NOT recv** — `wait_bp()` drains the T05 response; calling recv() after send drops the breakpoint notification
- **Always clear stale BPs at session start** — `z0,addr,4` for every address used previously; QEMU preserves SW BPs across `R00` restarts

```python
# Correct resume/wait pattern:
def resume(s):
    s.send(b'$c#63')  # DO NOT recv here

def wait_bp(s, timeout=90):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            d = s.recv(4096)
            if b'T05' in d or b'T03' in d:
                return True
        except socket.timeout:
            pass
    return False
```

## Patch Workflow

To add a new patch when the firmware crashes or hangs:

```bash
# 1. Find the crash address from QEMU interrupt log:
./scripts/qemu_boot.sh --patched -- -d int,cpu_reset 2>crash.log
grep "PC=" crash.log | head -5

# 2. Probe current bytes at that address:
.venv/bin/python firmware/scripts/patch_firmware.py --probe 0x<CRASH_ADDR>

# 3. Add the Patch() entry to BUILD32_PATCHES in patch_firmware.py

# 4. Regenerate and verify:
.venv/bin/python firmware/scripts/patch_firmware.py --r1mx
```

`Patch` fields: `offset` (= runtime address), `original` (4 bytes safety check), `replacement`, `description`, `phase`, `bamboo_only=False`.

NOP = `b'\x60\x00\x00\x00'` (PPC `ori r0,r0,0`).  
BLR = `b'\x4e\x80\x00\x20'`.

## Key Addresses

| Address | Symbol |
|---------|--------|
| `0x00000000` | Reset vector / romInit |
| `0x0036C350` | `usrInit` — main boot init |
| `0x005A7F30` | `kernelInit` — starts multitasking (never returns) |
| `0x0037C440` | `rootTask` / WDB task entry |
| `0x0036B3DC` | `usrWdbInit` |
| `0x020390d0` | Root task descriptor (all-zeros at cold boot) |
| `0xE9C4BC` | WDB port variable (value = 17185 = 0x4321) |
| `0xE9C420` | WDB agent state |
| `0x010D0584` | workQ flag (set by timer ISR) |

## Memory Layout

| Range | Contents |
|-------|----------|
| `0x00000000 – 0x00E8BF1F` | Firmware code + data |
| `0x00E9BF20 – 0x01153480` | BSS (zero-init at boot) |
| `0x01153480 – 0x0FF9C000` | Heap / task stacks |
| `0xE0600000` | XUartLite (console) |
| `0xE0800000` | XIntc (interrupt controller) |
| `0xE1020000` | XEmacLite (Ethernet / WDB) |

## QEMU Launch (manual, background)

Always go through `qemu_boot.sh`, which resolves the QEMU binary internally:

```bash
cd ~/src/RED/r1mx/firmware
nohup ./scripts/qemu_boot.sh --patched > /tmp/qemu-r1mx.log 2>&1 & disown
echo "log: /tmp/qemu-r1mx.log"
```

Flag combinations:
- `--patched` — use `software.patched.r1mx.bin` (required)
- `--debug` — halt at 0x0, GDB stub on tcp:1234
- `--net` — enable TAP networking (requires tap0)
- `-- -d int,cpu_reset` — pass extra args to QEMU (e.g. for crash logging)

## Open Problems (Session 21+)

1. **Root task descriptor `0x020390d0` is all-zeros** — `fn_382e80` dispatches nothing; camera subsystems never initialize. Need to find what should populate it (`__L` records, another task, or a live descriptor from real hardware).
2. **WDB not yet tested over TAP** — boot with `--net` and `wdbrpc 192.168.0.2 17185` to validate; use WDB memory read to inspect `0x020390d0`.
3. **Watchdog loop risk** — if the system prints `^^^123456789` more than ~2 times, a restart loop is active; check QEMU interrupt log for `TSR=0xC0000000` (WDT fired).

## Additional Resources

Load these references for deeper context:

- **`references/re_reference.md`** — Full RE reference: architecture, MMIO map, all 64 patches with rationale, session history, VxWorks internals
- **`references/plan.md`** — Current session plan with next steps and open questions
- **`references/qemu_howto.md`** — Step-by-step QEMU setup, boot, networking, and crash diagnosis guide
