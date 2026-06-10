# cam-working-01 — Phase 3 breakpoint targets (from source provenance)

**Date:** 2026-06-08  **D_text:** 0x10180  → **live = img + 0x10180**

## Why breakpoint-driven (not passive)
Read-only XMD from an idle halt can read ONLY: GPRs + pc + msr (via `rrd`), and the
**currently-TLB-resident** memory (kernel data + current task pages). It CANNOT
reliably read `.text`, most peripheral registers (XIntc/etc.), non-resident heap,
or ANY SPR (XMD exposes no SPRs; timer TCR/TSR/PIT unreadable). Therefore Phase 3
capture MUST be **breakpoint-driven**: HW-bp inside the driver so its peripheral
page is mapped in *that* context, then single-step logging MMIO (decode each insn
from the IMAGE at `pc−D_text`, resolve EA from live GPRs — works despite .text
being unreadable as data). `camera_probe.py phase_mmio_trace` already implements this.

## How targets were found
Firmware embeds `__FILE__` source paths in log/assert strings. `build_provenance_map.py`
materializes those → manifest.csv `module` column (93 high-confidence `red` funcs).
Full subsystem source map (from `strings`): see below.

## Subsystem → source file (Phase 3/5 relevance)
| QEMU need | source file(s) | notes |
|---|---|---|
| **sensor** | `lib/libsensor/sensor.c`, `app_modules/calibrate`, `vpimgproc/VpSensorChip.cpp` | 12 funcs tagged (below) |
| **audio_pci** | `app_modules/audio/audiomgr.cpp`, `videomgr/AudioInterface.cpp`, `CodecInterface.cpp` | not yet tagged — expand provenance |
| **timer (Phase 5 critical)** | `drivers/frametimer/frametimer.c` | not yet tagged — expand provenance |
| **HDMI (has ISR)** | `drivers/hdmi/ad9889_interrupt_handler.c`, `hdmidrv.c` | ISR = clean IRQ-line capture target |
| **buttons (Phase 3E)** | `ui_engine/UiButton.cpp/UiDial.cpp/UiJoystick.cpp` | PCA9698 over XIic |
| **fpga loader** | `drivers/fpgaloader/fpgaLoader.c` | |
| pipeline / codec | `lib/libpipeline/*`, `lib/libcodec/RdvFormat.cpp` | |

## Sensor driver functions (lib/libsensor) — img addr → live (img+0x10180)
0x000eb12c→0xfb2ac, 0x000eb60c→0xfb78c, 0x000eb690→0xfb810, 0x000eb72c→0xfb8ac,
0x000eb854→0xfb9d4, 0x000eb8e4→0xfba64, 0x000ec4d0→0xfc650, 0x000ec7bc→0xfc93c,
0x000ef1e4→0xff364, 0x000ef4f0→0xff670, 0x001b1c70→0x1c1df0, 0x001b1cd0→0x1c1e50

## Phase 3 capture procedure (per device)
1. `make` the provenance cover the target (or hand-find its functions via the
   source-string xref) → driver init / poll / ISR addresses.
2. HW-bp at `img+0x10180`. Many drivers are quiescent on an IDLE camera → the
   capture likely needs the **operator to activate the device** (start recording
   for sensor/audio/codec; press a control for UI/buttons) so the bp is hit.
3. On hit: read the now-mapped peripheral regs; single-step N insns logging MMIO
   (`camera_probe.py --phases mmio_trace --driver-addr <live>`).
4. Capture init seq (3A), ready handshake (3B), ISR (3C) per the plan.

## Next
- Pick first live capture; bases are runtime handles, so capture reveals them.

---

## Offline static analysis results (2026-06-08, camera off)
Method fix: **per-function aligned disasm** (linear disasm desyncs on inter-function
data and silently drops `lis/addi`). With that, audio/sensor/codec/HDMI all resolve.

### frametimer — NOT statically locatable (definitive)
No `lis/addi`, `lwz`, or pointer-word reference to ANY frametimer string
(`drivers/frametimer/frametimer.c`@0xd664ac, `"Initializing frametimer"`@0xd4081c,
`frametimerMax`@0xd470a8) exists anywhere in the image. `frametimer.c` (and
`ad9889`/`hdmidrv`) are compiled **position-independent** (PC-relative string refs
→ no absolute constant to scan). Find it instead via: live capture of the video
tasks that consume frame events, or its MMIO base at a runtime breakpoint.

### HDMI / AD9889 — I²C device, modelled cleanly
- `FUN_003486c4` (live 0x358844): AD9889 audio-infoframe handler.
- `FUN_0034c004` (live 0x35c184): **I²C bitfield RMW** — `(devaddr,reg,mask,shift,val)`,
  devaddr **0x72** = AD9889. Reads via `[*0xe9c5a0]`, writes via `[*0xe9c134]`
  (the XIic transfer primitives, runtime func-ptrs). Block writes too:
  `(*[0xe9c134])(0x72, reg, buf, len)`.
- **→ QEMU: model AD9889 as an I²C device at addr 0x72 on the XIic bus (0xb2600000).**

### Audio functions (breakpoint targets; device base = runtime handle in a struct)
- `FUN_0034d15c` (live 0x35d2dc): audio/codec state dump (`Running/Valid/Audio/Fmt/Rate`).
- `FUN_000ef4f0` (0xff670): `HdsdiEnableAudio`. `FUN_000ee96c` (0xfeaec): audio config.
- `FUN_000d971c` (0xe989c): audio event MQ. `FUN_000dc764` (0xec8e4): audio buffer alloc.
- output-audio cluster: `FUN_00147a2c/47c40/4806c/484dc/4a3e4/4b964` (live +0x10180).
- `FUN_0004e6fc` (0x5e87c): `/audio/0` device path.

### Sensor functions
- `FUN_001bcd88` (0x1ccf08): "Mysterium Sensor Type". `FUN_001e4ad0` (0x1f4c50):
  "sensor pixel clock". `FUN_000837a0` (0x93920): "Sensor DAC Values Setup".
  `FUN_00105cd0`/`10d48c`: VpSensorChip. + 12 lib/libsensor funcs (above).

### Codec
- `FUN_0014da94` (0x15dc14): CodecInterface "no frame detected" (per-frame path).

**Pattern confirmed:** device bases (audio, sensor) are passed as runtime handles in
context structs — invisible statically. The live `mmio_trace.py` capture (EA from
live regs at a breakpoint) is the only way to get them. Best first captures when the
camera is back + active: AD9889 I²C path (HDMI), or the codec per-frame function.
