# Frame-buffer DMA — QEMU model gap & boot UART errors

_Session 2026-06-25. Driving Build 32 (software.bin) in qemu-r1mx, monitoring UART._

## Summary

Build 32 boots all the way to the VxWorks shell (`->` prompt) and through the
full RED application device-init sequence. The remaining UART errors are
missing-/incomplete-peripheral paths, all currently **non-fatal** (the firmware
times out or NAKs and continues). This note documents the **frame-buffer DMA**
error in detail (root-caused) plus the I²C NAK map, and records the QEMU fix
landed this session.

## UART error inventory (boot of unmodified `software.bin`)

| UART line | Cause | Fatal? |
|---|---|---|
| `usrNetBootConfig: Invalid Argument` / `wdbConfig: error …` | bootline parse + WDB iface | no |
| `tffsDevCreate failed` / `InitTffs: Error …` | NOR/TFFS flash not backed (0xFF stub) | no |
| `Error initializing the USB host driver` (`OHCI=0, EHCI=2`) | EHCI/PCI USB keystone (known) | no |
| `Error setting time-of-day from RTC` | DS1339 @0x68 present but content rejected (see below) | no |
| `LT1840: cannot set DACA` / `Error initializing the fan control library` | no I²C slave at 0x40/0x41 | no |
| **`FrmBuf: DMA timeout, STAT=00000000 DMACTRL=00000000`** | **frame-buffer DMA not IRQ-modelled (this note)** | no |
| `VpConfigProgram:168 VPFPGA failed to load (DONE signal …)` ×3 | VP-FPGA config DONE strap not modelled | no |
| `ad9889_interrupt_handler … (0x97,0x97)` | known AD9889 occasional read (see memory) | no |

## Frame-buffer DMA — root cause

### Firmware side (resolved by disassembly)

The frame-buffer blit path (`FlashVx::FrameBufferBlit` @0x14F35C and the lower
`/roFs` splash loader) kicks a DMA and then **waits on a VxWorks semaphore**,
*not* a busy-poll:

* **Waiter** `0x003534e8`: `semTake(*(dev+0x2c), timeout=4000)` (call `0x1e9204`).
  On return it reads STAT (`*(dev+0x24) + 0x08`, via MMIO read helper `0x100dc`
  = `eieio; lwzx`), checks `& 0xf`. If the semaphore **timed out** it reads
  DMACTRL (`*(dev+0x24) + 0x28`) and prints
  `FrmBuf: DMA timeout, STAT=%08x DMACTRL=%08x` (fmt string runtime VA
  `0xd660d4`, built at `0x35357c`).
* **ISR / completion handler** `0x0035347c`: reads pending at `base+0x04`
  (`& 1`), writes `base+0x04` to ack (helper `0x100e8` = `stwx; eieio`), reads
  `base+0x08` (`& 8`); when clear it `semGive`s `*(dev+0x2c)` (`0x1e92bc`). The
  handler is registered into a **software handler list** by `0xbdc28` (a
  list-insert under a mutex — *not* a direct `XIntc_Connect`), so the hardware
  IRQ flows: device IRQ → an IOFPGA XIntc line → top-level ISR → dispatcher →
  this handler.

DMA register base = `*(dev+0x24)`. Observed guest-physical accesses (from a
`-d guest_errors` capture) place the engine inside the **XPS-Central-DMA PLB
slot** (`0x64010000`, 64 KB) at **+0x4000 (channel A)** and **+0x8000
(channel B)**, base ≈ `0x64014408` / `0x64018408`:

| reg | offset (chan A) | role | observed |
|---|---|---|---|
| pending/ack | `0x6401440c` (+0x04) | IRQ pending; written to ack | r/w |
| control+status | `0x64014410` (+0x08) | control writes; STAT polled `&0xf`,`&8` | w `0x78000000`/`0x70000000`/`0x08000000`, r |
| config | `0x64014428` (+0x20) | length/stride | w `0x00001311` |
| DMACTRL | `0x64014430` (+0x28) | read for the error print | r |

### QEMU side (why it times out)

`hw/dma/xilinx_dma_opb.c` modelled only the 13 XPS-Central-DMA registers
(`0x00–0x30`) of the slot and treated everything else as **out of range**
(reads → 0, writes dropped), and declared `valid.min_access_size = 4` so the
driver's 16-bit register accesses (`lhbrx`/`sthbrx`) were rejected as
`Invalid write … invalid size`. Net effect: the kick writes were dropped, the
completion **IRQ was never asserted**, the `semTake` ran its full 4000-tick
timeout, and the diagnostic printed STAT/DMACTRL = 0 (because those reads also
returned 0). One 4 s stall per blit; the splash also fails to display.

## Fix landed this session

Commit on `qemu-r1mx` `r1mx`: make `xlnx.opb-dma-channel` decode the full
0x10000 slot and accept sub-word accesses.

* `regs[R_MAX]` → `regs[R_WINDOW]` (`0x10000>>2`): the frame-buffer DMA banks at
  +0x4000/+0x8000 are now plain read-back storage (control regs read back what
  was written), matching a real IPIF peripheral; the 13 active Central-DMA
  registers keep their special behaviour via the `switch()`.
* `valid.min_access_size = 1` (impl stays 4 → the memory core assembles
  sub-word accesses into our 32-bit reg ops).

**Verified:** `-d guest_errors` opb-dma lines **84 → 0** (`out of range` +
`invalid size` both gone); boot progresses identically (still reaches the
VPFPGA stage and onward), no regression.

This is a **faithfulness/correctness** fix. It does **not** by itself clear the
`FrmBuf: DMA timeout` — that needs the completion model below.

## Next step to actually clear the timeout (scoped)

**Kick sequence (firmware setup fn `0x0033ccf0`, matches the trace exactly):**
read `base+0x08`(`0x410`); write `0x410 = ctrl|0x08000000`; delay; write
`0x410 = 0x78000000`; write `0x410 = 0x70000000`; delay; **write
`base+0x20`(`0x428`) = `0x1311` ← this is the transfer trigger**; read
`base+0x04`(`0x40c`) and check `& 0xc` (error bits). The blocking wait is a
*separate* function (`0x3534e8`, `semTake`) called by the higher-level blit;
completion = ISR `0x35347c` does `semGive`.

ISR `0x35347c` semantics (so the model sets the right bits): reads `0x40c`
(`base+0x04`) `bit0` = interrupt-pending (then writes `0x40c` to ack), reads
`0x410` (`base+0x08`) and requires `& 8 == 0`, then `semGive`s `*(dev+0x2c)`.

Give the frame-buffer DMA a real IRQ-driven completion:

1. On the trigger write to `0x428`/`0x8428` (channel A/B), schedule a bottom-half
   that sets `0x40c`/`0x840c` `bit0` (pending), clears `0x410`/`0x8410` `bit3`,
   and **asserts the IRQ** (deferred so it lands after the firmware returns and
   calls `semTake`). ⚠️ **Open question — the DMA source:** the head registers
   carry only the *destination* framebuffer (`+0x7a`=`0x840000`); the *source*
   (the rendered/decompressed buffer) is **not** in this window, so faking
   completion unblocks the firmware but does **not** by itself fill `0x840000`
   with pixels. Either (a) the firmware CPU-renders into `0x840000` once
   unblocked (then no copy needed — verify by re-dumping `0x840000` after the
   timeout is cleared), or (b) the real DMA copies src→`0x840000` and the model
   must do that copy — then the source address must be found (trace the blit
   caller / FrameBufferBlit `0x14F35C` → `*(this+0x9c)`). Resolve (a) vs (b) by
   experiment right after the completion model lands.
2. Wire that IRQ to the correct **IOFPGA XIntc line** so the firmware's
   dispatcher routes it to handler `0x0035347c` (→ `semGive` → `semTake`
   returns success, no 4 s stall). The dispatch is **two-level**: handler
   `0x35347c` is inserted into a *software* handler list by `0xbdc28` (the
   frame-buffer init function at ~`0xbf350`, which registers four handlers
   `0x35340c/0x353414/0x35341c/0x35347c`), **not** a direct `XIntc_Connect`. So
   the real chain is: device IRQ → IOFPGA XIntc line → IOFPGA top-level ISR →
   reads an **IOFPGA interrupt-status register** → calls the matching list
   handler. To make this fire, the model must therefore *also*:
     - set the per-channel pending bit (`base+0x04 & 1`, what `0x35347c` checks),
     - set the matching bit in the **IOFPGA interrupt-status register** that the
       top-level ISR reads to decide whom to dispatch (this register is in the
       FPGA catch-all today → reads 0 → dispatches to nobody), and
     - assert the IOFPGA XIntc line.
   **XIntc line — narrowed (2026-06-26):** capturing the `IER` progression
   (`-d guest_errors`, distinct values in order) gives, beyond the idle set
   (0/4/22/24/26 + 23=IIC), these lines enabled during device init, in order:
   **bit 5 → bit 27 → bit 13 → bit 10** (`IER` walks
   `05400011→05400031→0d400031→0d402031→0dc02031→0dc02431…`). bit 5 is the
   earliest (enabled right after the always-on console/PCI/Emac set, before IIC),
   so it is the **most likely IOFPGA/frame-buffer line**; 27/13/10 are the
   fallbacks. Disambiguate definitively by modelling the completion (set channel
   pending + assert the candidate line) and checking which makes
   `FrmBuf: DMA timeout` disappear free-running. Then model the IOFPGA int-status
   reg if the top-level ISR demands it (if the list-walker just calls every
   handler and each self-checks `base+0x04 & 1`, the status reg may be
   unnecessary — check the top ISR first).
   Validate **free-running with `qemu_log`, never under gdb** (see the
   BH-model-debugging memory — breakpoints reorder deferred IRQs).

### Completion-model attempt + empirical sweep (2026-06-26)

A full completion model was built and tested (then reverted — it didn't yet
clear the timeout, and a wrong line *hangs* the boot, so it isn't safe to
commit):

* `xilinx_dma_opb.c`: added `fb_irq` (2nd sysbus irq) + a `QEMUBH`. On a write to
  `0x4428`/`0x8428` (the trigger) schedule the BH; the BH sets the channel's
  `0x40c`/`0x840c` `bit0` (pending), clears `0x410`/`0x8410` `bit3`, and asserts
  `fb_irq`. A write to `0x40c`/`0x840c` is treated as the ISR ack (clear bit0,
  drop the line). `r1mx_virtex4.c`: `sysbus_connect_irq(dma,1,intc_irqs[IRQ_FB_DMA])`.
  **Mechanics confirmed working** free-running: BH fires, `INTC pin N -> 1` logged,
  and the candidate line's `IER` bit *is* enabled by the firmware.

* **Sweep result — the line is NOT simply one of {5,27,13,10}:**
  - **line 5**: boot proceeds normally but the timeout **persists** and the line
    stays asserted with no ack → the firmware's line-5 handler never calls
    `0x35347c`. Most likely line 5 *is* the IOFPGA line **but the top-level ISR
    reads an IOFPGA interrupt-status register first** (FPGA catch-all → 0 →
    dispatches to nobody). So a pending bit on the channel alone isn't enough.
  - **line 27**: **hangs the boot** at "Initializing ADV codec driver" (~4.6 s) —
    asserting it runs the wrong/other ISR which deadlocks. Do **not** use.
  - 13/10 not tried (27's hang shows blind sweeping is unsafe).

* **Conclusion / next step:** the missing piece is the **IOFPGA interrupt-status
  register** that the line's top-level ISR reads to dispatch. Find it by tracing
  FPGA-region reads issued right after the line asserts (add a temporary log to
  the `fpga_catchall_read` in `r1mx_virtex4.c`, assert line 5 on the trigger, and
  see which IOFPGA address the ISR polls). Then model that register to return the
  frame-buffer-pending bit *and* assert line 5. Only then will `0x35347c` run →
  `semGive` → timeout cleared. Re-apply the (working, reverted) DMA-side model
  from this section once that register is known. **Do not commit the 2nd-irq
  wiring until a line is confirmed** — a wrong line hangs boot.

## Display-controller register decode + framebuffer location (2026-06-26)

Goal of this pass: get pixels out to a preview window (HDMI/SDI). Findings from a
full ordered register trace of the splash blit (temporary `FRMBUF_TRACE` stderr
logging added to `opb_dma_read/write` for `offset >= 0x4000`, then reverted):

The `0x64014000` bank (channel A; `0x64018000` = channel B is identical) holds
**three sub-blocks at +0x000 / +0x100 / +0x200 — the three HDMI heads
EVF / LCD / MHD** (matches "Found and initialized 3 HDMI device(s)" and the
`/hdmi/evf,/lcd,/mhd` AD9889 errors). Per-head registers seen, all three heads
programmed identically:

| reg (head A) | value | meaning (decoded) |
|---|---|---|
| `+0x72` | `0x00890000` | framebuffer **end** addr (= base + 0x50000) |
| `+0x7a` | `0x00840000` | framebuffer **base** addr |
| `+0x42` | `0x00050000` | length **0x50000 = 327680 bytes** |
| `+0x4a` | `0x00050000` | length (mirror) |
| `+0x32` | `0` | (cleared each blit) |

Plus the DMA-engine registers at base `0x64014408`: `+0x08`(`0x410`) control
(kick `0x08000000`/`0x78000000`/`0x70000000`), `+0x20`(`0x428`) config
`0x00001311`, `+0x04`(`0x40c`) pending/ack, status polled `&0xf`/`&8`.

**Framebuffer = guest-physical `0x00840000`, 0x50000 (327680) bytes**, shared by
all three heads (so the 3 HDMI outputs mirror one buffer). 327680 bytes →
candidate geometries: 640×512×1B, 512×320×2B (RGB565), 320×256×4B. Config
`0x1311` may encode width/format — not yet confirmed.

**Empirical check (QMP `xp`/`pmemsave` of physical RAM after full boot):** the
runtime content at `0x840000` is **random / max-entropy** (8.0 bits/byte, uniform
histogram, ~0 inter-row correlation across all candidate strides) — i.e. **NOT a
rendered image**. Reason: the display pipeline is **stalled** — every blit hits
the 4 s `FrmBuf` semaphore timeout, so the firmware never actually fills
`0x840000`. (The gdb stub can't read `0x840000` — `E22`/unmapped — because it
translates through the running task's MMU; it is a *physical* scanout buffer, so
read it with the QMP monitor's `xp`/`pmemsave`, not the gdb stub.)

**Conclusion / ordering:** the completion-IRQ model (next section) is a
**prerequisite** for a preview — there are no pixels to show until the firmware's
display pipeline stops stalling and renders into `0x840000`.

### Preview pipeline plan (toolkit already half-built)

`toolkit/gui/widgets/status_lcd.py` already listens on **TCP 17186** for `RLCD`
pixel frames: `magic 'RLCD'`, `u16 width`, `u16 height`, `u32 stride`,
`u8 pixfmt` (0=BGRA32 1=RGB24 2=MONO8 3=BGR565), `u8 display`
(0=StatusLCD 1=MainOSD/HDMI-SDI), then pixels. QEMU's `lcd_bridge` *uses* 17186
but currently emits raw `RFPG` MMIO records, **not** `RLCD` pixel frames. Plan:
1. Land the completion-IRQ model so the firmware fills `0x840000`.
2. In QEMU, on each blit completion, `address_space_read` the head framebuffer
   (`0x840000`, len from `+0x42`) and emit one `RLCD` frame on 17186 with the
   confirmed geometry/format (start with BGR565 512×320 and tune).
3. Run the toolkit `StatusLCDWidget` to view it (`display=1` MainOSD).

To reproduce the register trace: add, in `hw/dma/xilinx_dma_opb.c`
`opb_dma_read`/`opb_dma_write`, `if (offset >= 0x4000) fprintf(stderr, …)` and
boot with stderr captured.

### IOFPGA interrupt-status hunt — RESULTS (2026-06-26, session 2)

Re-applied the completion model with the 2nd irq on **line 5** plus a capture
window logging the reads the firmware issues right after the IRQ asserts. Findings:

* **Line 5 is CONFIRMED the frame-buffer / IOFPGA XIntc interrupt line.** After
  the IRQ asserts, handler `0x0035347c` runs and reads the channel pending reg —
  `opb-rd off=0x440c => 0x00000001` (the `bit0` the BH set). The first few blits'
  completions work and **`FrmBuf: DMA timeout` disappears** (semGive succeeds).
* **The IOFPGA is at `0xe2000000`** (unmodelled → FPGA catch-all). The reads after
  completion cluster there: `0xe2000224` (heavily), `0xe2000088/004c/0108/010c/
  0154/022c`.
* **`0xe2000224` is NOT the interrupt-status register — it is an IOFPGA GPIO /
  serial bit-bang register.** The reader (fn `0x003667c0`, found via LR capture)
  does read-modify-write of `0xe2000224` with delays, shifting **16 bits**
  (clock = bit0, data = bit2, MSB-first; ~`0x1d920` is the inter-bit delay). It
  tolerates the catch-all 0-reads and completes fine — it is configuring a serial
  display/DAC, not waiting on a status bit.
* **A naive "fake completion" is NON-VIABLE — it converts the benign 4 s timeout
  into a fatal crash.** Once the semaphore is given, the firmware enters the
  splash **success path** (which never ran before — the blit always timed out) and
  panics: PC ends in an infinite loop `0x0036320c` (`b .`), preceded by `intLock`
  + a fatal-event post (`0x001e11ac` → event `476`). The pre-panic backtrace is
  `usrRoot 0x37c89c → 0x5c49d4 → 0x5c6830 → panic`, i.e. **deep C++ vtable/dispatch
  code in the real display-output path** — it crashes because the framebuffer/
  display state is faked, not real.

**Revised conclusion / next direction:** clearing the timeout by IRQ alone is the
*wrong* fix — it unblocks a display path that then needs the work actually done.
To get pixels you must model the path **faithfully**:
  1. Find the DMA **source** buffer (the rendered pixels in guest RAM) — the head
     regs only give the dest `0x840000`. Trace the blit caller / `FrameBufferBlit
     0x14F35C → *(this+0x9c)`, or instrument guest RAM for the big write that
     precedes the trigger.
  2. On the trigger, **actually copy** source→`0x840000` and set the IOFPGA/display
     state the success path checks, *then* raise line 5. Validate the boot
     **doesn't panic** (no `0x36320c`) and that `0x840000` then holds an image.
  3. Only then emit `RLCD` from `0x840000`.
Alternatively, capture the live IOFPGA register values during a real blit on the
working camera (JTAG) to know the exact display state the success path expects.

The mechanism (BH on `0x4428`/`0x8428` trigger → pending `0x40c` bit0 + clear
`0x410` bit3 → assert line 5; ack on `0x40c` write) is correct and reusable; it is
just **insufficient alone**. Do not commit the 2nd-irq wiring — it makes boot panic.

### DMA source-buffer hunt — RESULTS (2026-06-26, session 3)

Goal: find the rendered-pixel source the frame-buffer DMA reads. Captured **every**
opb-dma register write during a blit (removed the earlier `offset>=0x4000` filter):

* The Central-DMA registers (`0x00–0x30`, incl. SA/DA/LEN `0x08/0x0c/0x10`) get only
  a couple of **zero** writes (self-test/reset) — **no source address there**.
* The **only addresses written anywhere** in the slot are **`0x00840000` (head reg
  `+0x7a`)** and **`0x00890000` (`+0x72`)**, with length **`0x50000` (`+0x42/+0x4a`)**.
  `0x890000 = 0x840000 + 0x50000` → **two adjacent 327680-byte buffers in guest RAM =
  double-buffering**. All three head sub-blocks (EVF/LCD/MHD) program the same pair.

**So there is no separate source pointer — the display double-buffers ARE
`0x840000` / `0x890000` (327680 B each, guest-physical).** The firmware composites/
renders into these directly; the DMA flips/scans them.

Runtime check (QMP `xp`/`pmemsave` + bulk dump):
* Both buffers are **written at runtime** (0% byte-match to the static image) and
  **differ from each other** (double-buffered) — they are genuine runtime buffers,
  not leftover static data.
* But the content is **high-entropy noise with zero spatial/row autocorrelation**
  (best corr ≈ 0.008 across every stride 320–4096, at 1/2/4 bpp) at every boot state
  sampled — i.e. **not a recognizable rendered image yet**.
* A CPU **write-watchpoint on (virtual) `0x840000` did not fire** in 10 s at the
  frame-buffer-init stage — so either the writes are infrequent, go via **DMA** (no
  CPU watchpoint), or the framebuffer is mapped at a **different virtual address**
  (PPC405 MMU is on). A *physical*-address watch would be needed to be sure.

**Interpretation / why no image:** `0x840000`/`0x890000` are the display scan-out
double-buffers, but they hold noise because the firmware never composites a real
frame in this state — there is **no sensor live-view** and the OSD/UI is not drawing
into them (the display pipeline is effectively idle/stalled; forcing completion
panics, see prior section). The source buffer is **located**; it is just **empty of
pixels** until the firmware actually renders.

**Next directions to get real pixels into `0x840000`:**
  1. Drive the firmware to render the OSD: it may need to reach full operational
     state (telnet/UiIp up) and/or an operator action; let boot settle for minutes
     and re-sample, or trigger a UI redraw over telnet/WDB.
  2. Confirm the writer with a **physical** 0x840000 watch (instrument QEMU RAM, or
     a TCG plugin) — distinguishes CPU-render (virtual remap) vs DMA-fill.
  3. Model a **sensor** so the live-view path produces frames to composite.
  4. Compare against the **working camera over JTAG**: dump its 0x840000 during a
     real blit to see the true format/content (and whether HW also double-buffers
     at exactly these addresses).

## Sensor / video front-end bringup (2026-06-27, session 4)

Goal: make the firmware believe a working image front-end is present so it
composites frames into `0x840000`/`0x890000` (then preview). The **sensor library
itself inits OK** ("Myseterium Sensor Type", `Sensor Rev Read = 0x8`, warning only).
The real gate is the **VPFPGA** (video-processing FPGA) bringup, a multi-step
verification cascade. Method used throughout: log every FPGA catch-all read +
caller LR (`POWERPC_CPU(current_cpu)->env.lr`), boot to the failing step, find the
spun-on register, disassemble the poll, model the expected value.

**Step 1 — VPFPGA config DONE — MODELLED + committed** (`8b4a9678c3`):
poll fn `0x352ce4` reads **`0xe200028c`** and waits for **bit8 (0x100) = DONE**
(`andi. r0,r3,256; beq loop`), 65535× then "VPFPGA failed to load (DONE signal was
not detected)". Catch-all now returns `0x100` for `0xe200028c`. Verified: DONE
failure gone, bringup advances; boot still reaches full init, no hang/panic.

**Step 2 — RocketIO/MGT channel "up" — RESOLVED (register found; not committed).**
`VpConfigVerifyRio` (`0x234c14`, line 197) reads RIO status via accessor
`0x45e510(dev=0x1e, reg=0xa104, 0)` (a generic `reg_read(device,register)` — the
"handle" `*(0xe15588)` is the small int **0x1e**, not a pointer) and checks **bit0**
= "channel up". Runtime-traced the accessor's MMIO read → it reads **`0xe20000f8`**.
Modelling `0xe20000f8` bit0=1 **makes VPFPGA config SUCCEED** (no retries, no "Error
configuring VP FPGA"; the AD9889 hot-plug loop disappears). (Red herring: fn
`0x3617a4` polls a different reg `0xe20001d8`==4; not the RIO check.)

**Step 3 — VPFPGA *driver* init poll — NEXT (the new wall).** With DONE+RocketIO,
config succeeds but the VPFPGA **driver** init then **hangs** (100% CPU) in a spin
at `0x374c30`–`0x374c4c` waiting for **bit10 (0x400)** of **`0xe0080018`** (in the
histogram/video IP region `0xe0080000`, a *different* device model than the IOFPGA
catch-all). It reads `0xe0080010/14/18` each iteration. ⚠️ Because this regresses
the boot (stable full-init → hard hang), the **RocketIO model was reverted**; only
the DONE model is committed. The recurring **serial bit-bang fn `0x3667c0`** (RMW of
the `0xe2000224` GPIO, 16-bit shift) strongly suggests the driver bit-bangs commands
to the VPFPGA and waits for *responses* — i.e. a point where faking status bits is
no longer enough and the VPFPGA's actual logic/response must be modelled.

**Cascade verdict:** each modelled status bit advances ~one step then hits the next
hang, across multiple device regions (IOFPGA `0xe2000000`, histogram `0xe0080000`),
trending toward a bit-bang/response wall. Tractable but multi-session, and partial
models regress boot. **Strongly recommend the JTAG reference** (dump the working
camera's `0xe200028c`,`0xe20000f8`,`0xe0080010/14/18`,… *operational* values +
the live `0x840000` frame) to get exact expected values and a target image, rather
than guessing bit-by-bit.

**Assessment:** full sensor/video bringup is a **deep, multi-session cascade** —
DONE → RocketIO → (more status/state checks, several behind dispatch-table
accessors) → and finally the firmware expects **real video data over the RocketIO
link** to composite. Faking each status advances the firmware but the end state
needs synthesized frame data. Each step is tractable with the LR-capture method but
there are many, and some are indirect.

**Faster alternative for "see what the firmware is doing":** the **OSD/UI** is
software-rendered by FlashVx into its own bitmap (independent of the sensor). Find
that render buffer (trace `FlashVx::FrameBufferBlit 0x14F35C → *(this+0x9c)`, or
watch for the big CPU fill) and stream it as `RLCD` — likely shows the menu/status
overlay without the whole video front-end. Recommended next pivot if a quick
visible result is wanted over a faithful live-view.

## OSD render-buffer pivot — RESULTS (2026-06-27, session 5)

Tried to grab the FlashVx OSD bitmap directly (independent of the sensor). The
blit source is confirmed: `FrameBufferBlit 0x14F35C` copies from **`*(this+0x9c)`
= the OSD bitmap**, stride **`*(this+0xa0)`**, region (x0,y0,x1,y1), via copy fn
`0x1f661c`. BUT:

* **`FrameBufferBlit` is gated** — it early-returns unless flag **`0xea0de4`**
  (display-ready, RAM/BSS) is set; it is 0, so the blit never runs.
* **The FlashVx constructor `0x14f03c` is NEVER called** in this boot — confirmed
  by a halt-at-start (`-S`) breakpoint left armed for ~2 min (boot ran to emulated
  00:00:59, well past the VPFPGA give-up + into the AD9889 loop). Its sole caller
  is the GUI-init fn at **`0xd4394`** (allocates the object, builds a FlashRect +
  name, calls the ctor) — that function does not run either.
* **The boot never reaches an operational/UI state.** It ends device init at
  "Initializing VPFPGA driver" (~46–59 s) and then **loops forever on the AD9889
  HDMI hotplug retry**; no GUI/OSD/UiIp markers ever appear.

**Unifying conclusion (both pivots):** in the headless / sensor-less state the
firmware renders **no frames at all** — neither sensor live-view nor OSD. Every
visual path is gated on the **video/display pipeline (VPFPGA) being operational**:
the OSD GUI subsystem (`0xd4394`→FlashVx) doesn't even start, and the blit is
gated on the display-ready flag. So there is nothing to capture until the pipeline
comes up.

**Realistic paths to any preview (in rough order of effort):**
  1. **Continue the VPFPGA bringup cascade** (DONE ✓ → RocketIO accessor → …) until
     the firmware considers the display ready, the GUI inits (`0xd4394`), and
     `0xea0de4` gets set. Deep but it's the firmware's real path.
  2. **Force the GUI to start**: find what gates `0xd4394`/`0xea0de4` and satisfy
     just those (may be far fewer registers than full video). Investigate next.
  3. **JTAG the working camera**: capture the real IOFPGA/VPFPGA register states +
     the live `0x840000`/OSD-bitmap contents during operation, then replay/seed
     them in QEMU — the most reliable ground truth.

## Display/OSD gate chain — RESULTS (2026-06-27, session 6)

Traced exactly what keeps the OSD/display subsystem dormant. The full gate chain:

1. **`FrameBufferBlit 0x14f35c`** (OSD→display blit) early-returns unless
   **`0xea0de4`** (display-ready) ≠ 0. It is 0.
2. **`0xea0de4` is set only by the display-enable fn `0x14faf8`** (`stw` @0x14fb5c),
   which *also* calls the GUI-init `0xd42f4` (→ FlashVx ctor). But `0x14faf8` is
   itself gated: it reads **`0xea0de8`** (offset 3560) and **returns immediately if
   it is 0** (`lwz r0,3560(r9); cmpwi r0,0; bne proceed; blr`). `0xea0de8` is 0.
3. **`0xea0de8` has no code writer** (grep found only stack `r1+3560`; the sole
   reader is the gate at `0x14fb00`) → it is set indirectly / by an event that does
   not occur headless, so it stays 0 (BSS).
4. **`0x14faf8` is never even called** — bp armed 60 s, no hit. The display-update
   task / event handler that would poll it does not run. (It has no direct `bl`
   caller and no stored function pointer `0x0014faf8`/`0x000d4394` in the image —
   reached via the event/dispatch machinery, [[param-and-dispatch-table-driven]].)

So the **entire display/OSD update subsystem is dormant**: blit gated, display-enable
gated *and* uncalled, GUI-init (`0xd42f4`)/FlashVx ctor (`0x14f03c`) never reached.
These gates are **RAM flags driven by the firmware's own event/task logic**, not
MMIO — they can't be satisfied by a QEMU device stub, and forcing them via gdb is
moot because the function that consumes them isn't called.

### Root cause (all 3 pivots agree)
Sensor live-view, OSD, and the display update loop are **all gated on the camera
reaching an operational state**, which requires the **video/display pipeline
(VPFPGA) to come up**. Until then the firmware sits in device-init + the AD9889
hotplug retry loop and runs no display/GUI code at all. There is no shortcut around
the VPFPGA bringup at the QEMU-device level — the gates are internal firmware state.

### Realistic options (revised)
* **A. VPFPGA bringup cascade** (the firmware's real path): continue
  DONE ✓ → RocketIO accessor → … until the pipeline is "up", which is what flips
  the internal gates and starts the display loop. Deep but principled.
* **B. JTAG the working camera** (recommended for ground truth): with the camera
  operational, dump `0xea0de4/0xea0de8`, the FlashVx object + `*(obj+0x9c)` bitmap,
  and `0x840000`, and the IOFPGA/VPFPGA status regs the bringup waits on. That
  gives both the exact values to make A converge **and** a real reference image.
* **C. Patch the firmware** (intrusive, last resort): NOP the gate at `0x14fb04`
  and force-call the display-enable/GUI-init path — but the GUI then renders against
  faked display state and likely crashes (cf. the FrmBuf fake-completion panic).

## I²C NAK map (separate, for later)

`-d guest_errors` shows `xlnx-iic: no slave at I2C addr 0x..` for: **0x40, 0x41**
(fan controller — the `LT1840 cannot set DACA` error), **0x0b, 0x2c, 0x72**
(unidentified). The RTC at **0x68** does **not** NAK (a `ds1338` slave is
attached and ACKs), so `Error setting time-of-day from RTC` is a **content**
rejection — likely a DS1339-specific register the `ds1338` model answers
differently (replace with a `ds1339` model or add the missing status/control
register). The AD9889 HDMI transmitters (0x39/0x3d) are attached and answer.

## Repro

```bash
# fixed binary already built at ~/src/qemu-r1mx/build/qemu-system-ppc
firmware/scripts/qemu_boot.sh --background \
  --serial-log=/tmp/frmbuf_serial.log
# for the guest-error capture add -d guest_errors -D <log> to a direct launch
grep -c opb-dma <log>      # 0 with the fix, 84 before
```

---

## Live working-camera JTAG probe (2026-06-27) — display arch confirmed, RTP wall

Probed cam-working-01 over Channel B (file-queue `agent_loop`; Channel A/RSP is
unreachable — the XMD gdb stub binds guest 127.0.0.1:1234, VBox NAT can't reach
guest loopback → reset/timeout). Hard-won operational facts:

**`mrd` is MMU-context-dependent.** XMD `mrd` translates through the *current*
task's MMU. Reliable kernel/BSS/image reads (0xe0_xxxx vtables, 0xea_xxxx BSS,
low-DDR scanout) require the CPU stopped in the **idle/kernel context**
(pc=idle spin). Stopped in a task/RTP context, those reads return bus residue
(= a stale register value) or zero.

**Relocation is PER-BOOT.** This boot D_code=D_data=0 (live == objdump address,
where objdump uses `--adjust-vma=0x10000`); a prior boot (PHASE0) was +0x180.
Always re-derive from the live idle PC vs the idle-spin objdump address
(`lwz r12,0(r24); cmpwi; beq` — r24=readyQ 0x010d0584). Verify the FlashVx
vtable: objdump `0xe08dc0..0xe08e84` holds nominal code ptrs
(`+0x44`=Alloc 0x14f1f0, `+0x50`=Blit 0x14f35c, ...) — if mrd of 0xe08e0c
returns 0x14f35c, D_code=0; if 0x14f4dc, D_code=+0x180.

**XMD `bps` is non-functional via the agent** ("No Elf file associated with
target") — breakpoints never fire (tested even on the constantly-executed idle
spin). Only manual `stop` + reads work over Channel B. Real HW breakpoints need
Channel A (RSP/gdb IAC), which needs a VM-side relay.

**Display architecture (confirmed on silicon):**
- Head/DMA MMIO live at `0x64014000`: head regs encode framebuffer **base
  0x84_0000 / end 0x89_0000** (top byte at +0x70/+0x78 sub-blocks). DMA engine
  at `0x64014400`: `+0x04`=`0x19691126` (id/magic), `+0x10`=`0x70000000`
  (control), `+0x20`=`0x01000100`, `+0x24`=`0x00FF0100`, `+0x28`=`0x1311`
  (config). Source reg is 0 at idle (latched only during a blit).
- **CPU-physical `0x840000` is NOT the framebuffer** — it's unrelated heap
  (random one boot, all-zero the next). The scan-out buffer at *display-space*
  `0x840000` is **FPGA-local memory**; the monitor shows it because the FPGA
  scans it autonomously (updates even while the PPC405 is halted — verified:
  live feed kept moving with CPU stopped).
- **OSD render buffer is RTP-private.** FlashVx (a VxWorks RTP) renders
  **BGRA8888** into a heap buffer; `this+0x9c`=fb ptr, `+0x8c..0x98`=bounds,
  `+0xa0`=bpp(4). In `FrameBufferBlit` (objdump 0x14f35c): `mr r29,r3` @0x14f3cc
  (this→r29 for the whole body), src load `lwz r3,0x9c(r29)` @0x14f404.
  Gate `0xea0de4` (display-ready) early-returns the blit when 0.
  Object caught as r29=`0x0597f960` in GUI context — reads **zero** from the
  idle/kernel context ⇒ confirms the buffer lives in the GUI **RTP's private
  virtual space**, unreachable from the kernel context via `mrd`.

**Verdict / next step to get a reference frame:** need Channel A (RSP gdb stub),
which (a) sets real HW breakpoints with no ELF, and (b) reads RTP/task-specific
memory by context. Requires a VM-side relay (`0.0.0.0:2345 -> 127.0.0.1:1234`)
since the stub is loopback-bound. Then: bp `FrameBufferBlit` (re-derive addr
from this-boot reloc), read `r29`=this in the RTP context, read `+0x9c` BGRA
buffer (bounds give w/h), dump + render PNG. The XMD/Channel-B route cannot
reach the RTP buffer.

## QEMU OSD-hook re-confirmation (2026-06-28, session 7)

Re-ran the "boot QEMU, hook `FrameBufferBlit 0x14f35c`, read `*(this+0x9c)`"
experiment to verify the session-5/6 conclusion. Three boots:

* **Hook validated.** `0x14f35c` in the loaded image holds the exact
  `FrameBufferBlit` prologue (`7c0802a6 9421ff88 3d2000ea 9001007c 80090de4`),
  i.e. firmware loaded at base 0x10000, D=0, address correct. So a no-fire = the
  firmware never *calls* the blit, not a bad address.
* **Under gdb (2 HW bps: ctor `0x14f03c` + blit `0x14f35c`, 15 min):** neither
  fired; guest stuck ~00:02:30 in the AD9889 loop. The armed bps + gdb distort the
  I²C bottom-half timing ([[qemu-bh-model-debugging-method]]), making AD9889 worse.
* **Genuinely free-running (no gdb, no bps) — NEW result:** boot clears VPFPGA
  give-up (00:00:57) and enters HDMI init, prints the **first** AD9889
  `(0x97,0x97)` line at 00:01:17, then the **guest clock freezes at 00:01:17 for
  5+ min with QEMU pinned at 100% CPU** — a busy-spin, *not* the gentle "occasional
  non-fatal retry" the memory described. So even free-running it never escapes the
  HDMI stage; FlashVx ctor/blit never reached.

**Conclusion unchanged & firmer:** the OSD render buffer (`this+0x9c`) is never
populated in QEMU because FlashVx is never constructed — the display/GUI subsystem
is gated on the VPFPGA pipeline coming up, which never happens headless. The
QEMU-side "hook the blit" path is a dead end until the VPFPGA bringup (option A) or
firmware patch (option C) flips the gates; option **B (JTAG the working camera)**
remains the ground-truth route. Probe scripts added: `probe_osd_qemu.py`,
`probe_flashvx_qemu.py`.
