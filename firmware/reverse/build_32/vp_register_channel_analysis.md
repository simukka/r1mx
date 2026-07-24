# VP-FPGA read path — what QEMU must return to clear the RIO/RegPeek wall

_Session 2026-07-02. Static decode (r2) of the read paths that fail **after** the
three bring-up status bits (DONE / RocketIO / FIFO-ready) were modelled. This is the
"Step 4 frontier" of `qemu_frmbuf_dma.md`, now decoded to the register level._

## TL;DR

The bring-up **status bits** are satisfied (config DONE `0xe200028c`, RocketIO
channel-up `0xe20000f8`, comm-FIFO ready `0xe0080018` b10). What fails next are
**data reads** — the firmware asks the VP-FPGA for actual *register values* and
*RIO payload words* and QEMU's catch-all returns `0`. Zero is a legal-looking answer
that the app then treats as a null pointer / invalid handle, so three tasks call
through it and die at **PC 0**.

There are **two independent read channels**, both currently answering `0`:

| Channel | Physical | Carries | Completion gate | Data QEMU returns now |
|---|---|---|---|---|
| **RIO FIFO** | `0xe0080000` block | bulk words (`vpfpgaRioRead/Word`) | `+0x18` bit10 = RX-ready | `+0x10/+0x14` payload = **0** |
| **VP reg window** | `0xe2000xxx` (reg#→addr) | register peek/poke (`VpRegPeek`) | byte-count `== 4` | register value = **0** |

To clear the wall we must return **real data**, not more status bits:
- RIO: for each command written to `+0x04/+0x08`, put the correct 32-bit response
  words at `0xe0080010/0xe0080014` and pulse `+0x18` b10.
- Reg window: return real register contents for the `0xe2000xxx` addresses the
  `0xabxx`/`0xa1xx` reg numbers map to (version, caps, state), not 0.

Those values are the VP-FPGA's internal state — a board we don't have — so they must
be **modelled from how the firmware consumes each one** (minimum self-consistent
value) or **captured from a live camera over JTAG and replayed** (`vp_fpga_readback.md`).

---

## Channel 1 — RIO FIFO (`0xe0080000`), `vpfpgaRioRead` / `vpfpgaRioReadWord`

`vpfpgaRioRead` @ `0x374d80`, `vpfpgaRioReadWord` @ `0x375680`. Both operate on a
device struct whose MMIO base is the `0xe0080000` block (same block the driver-init
FIFO spin @ `0x374ba4` uses). Register layout (offsets from the block base):

| Offset | Role | Firmware use |
|---|---|---|
| `+0x04` | TX command | `stw` cmd with `oris …,0xc000` flag bits (`0x375754`) |
| `+0x08` | TX trigger/arg | `stw 0` (`0x375764`) |
| `+0x0c` | status nibble | `andi. r,0xf` — link/error; **0 = idle/ok** |
| `+0x10` | RX data word 0 | drained/read as payload (`0x375670`,`0x374dd4`) |
| `+0x14` | RX data word 1 | drained/read as payload |
| `+0x18` | FIFO status | `andi. r,0x400` — **bit10 = RX word available** |

**Timeout logic (both fns):** wait for `+0x18` b10, bounded by *either* an
iteration count `> 0x200` (512) *or* an elapsed `sysTimestamp` (`0x1e9aa0`) delta
`> 0x14` (20 ticks). On timeout →
`vpfpgaRioReadWord: rx buffer timeout` (fmt `0xd6bb30`, arg str `0xd238b8`) /
`vpfpgaRioRead: Timeout…` (fmt `0xd6bab4`, arg `0xd23898`), logger `0x3db350`,
return `-1`.

**Current QEMU state:** `red_histogram_ip.c` forces `0xe0080018` → `0x400`, so b10
is *always* set → the wait exits on the first pass and **does not time out**. But
`+0x10/+0x14` still return `0`, so the caller gets a **zero payload**. If a
post-fix run still shows a *timeout* (vs. zero data), the RIO data channel is a
**different block base** than `0xe0080000` (the b10 fix wouldn't cover it) — confirm
with a free-run MMIO capture (below). Either way the fix is the same class of work:
present real RX words, not just the ready bit.

**What QEMU must do (RIO):** model a command→response FIFO. On a write to `+0x04`
(command) decode the requested VP address/opcode, then make the next reads of
`+0x10`/`+0x14` return that address's value and set `+0x18` b10 for exactly one
drain. Returning a *constant* (even nonzero) will not satisfy the app — it reads
distinct registers and validates them.

---

## Channel 2 — VP register window (`0xe2000xxx`), `VpRegPeek`

Call chain:

```
VpRegPeek 0x232c68
  └─ 0x22edd4  (worker; gated on global 0xe15550 != 0 "VP enabled")
       ├─ 0x45e510(handle=*0xe15554, reg=0xab01, out)   ; set peek address
       │    └─ 0x4605b4 (reg dispatch)
       │         └─ handle->vtable[0x54][0x18](handle->ctx[0x44], reg, val)  ; driver xfer
       └─ 0x45e144(handle=*0xe15554, buf, len=4)          ; read the 4 result bytes
            └─ handle->vtable[0x54][0x10](ctx, buf, 4)     ; driver read
```

`0x22edd4` returns **0 (success) only if** the `0x45e510` setup returns `0` **and**
`0x45e144` returns exactly **`4`** (4 bytes read). Any other outcome →
`VpRegPeek: operation failed` (fmt `0xd6d798`, arg str `0xcd3e40`, at wrapper
`0x232c68`; log `0x3db350`), return `-1`.

**Register-number → physical address.** `0x4605b4` handles a few *low* logical IDs
specially (`0x12`,`0xa`,`0x2f`,`0x3a`,`0x3b`,`0x20`, `0x3e`); everything else
(the `0xa1xx`/`0xabxx` VP regs) falls to the generic tail `0x460898`, which calls
the driver's read/write method via **`handle->vtable[0x54][0x18]`** (read) /
**`[0x1c]`** (write), with ctx `handle->[0x44]`. That method maps reg#→MMIO in the
`0xe2000000` window. **Empirically confirmed:** reg `0xa104` (RocketIO channel-up,
via `VpConfigVerifyRio 0x234c14`, handle `*0xe15588`) maps to physical
**`0xe20000f8`**. So the VP "register file" is **memory-mapped** at `0xe2000xxx`,
addressed by `(reg & 0xff)`-style indexing — *not* the GPIO bit-bang.

Note there are **multiple VP handles**: `0xe15588` (config/RocketIO space, reg
`0xa1xx`) and `0xe15554` (peek space, reg `0xabxx`), the latter written once at
`0x232a0c`. Enable-gate global is `0xe15550`.

**Current QEMU state:** the `0xe2000xxx` catch-all returns 0 for every reg. The
peek "succeeds" for status bits we hardwired but returns **0 for every data
register**, and for un-hardwired addresses the app's downstream validity checks
fail → the peek path reports failure or hands back a null value.

**What QEMU must do (reg window):** return the VP-FPGA's real register contents for
the `0xe2000xxx` addresses the app reads post-bringup (chip/firmware version,
sensor/capability descriptors, pipeline state enums). These are internal FPGA state.

---

## The GPIO bit-bang channels are a *separate* subsystem (not VpRegPeek)

`0x366798` (16-bit, GPIO `0xe2000224`) and `0x366588` (8-bit, GPIO `0xe200022c`)
are RMW bit-bang serial engines (CS/CLK/DATA on 3 lines, `0x1d920` = µs delay,
`0x37fd0c/0x37fd24` = lock). They shift data **out** (MOSI). These drive a slow
serial peripheral (CPLD/strap logic), **not** the VP register peek — that goes
through the memory-mapped `0xe2000xxx` window above. Earlier notes attributed the
RegPeek channel to `0x3667c0`; the decode shows RegPeek is memory-mapped. QEMU's
catch-all already absorbs the bit-bang writes fine; if a bit-bang **read-back**
(MISO sample) ever gates boot it will need the sampled input bit driven, but that is
not the current wall.

---

## Why the three tasks die at PC 0 (the crash, precisely)

`tMaster` (`0x556dd50`), `tAudioMgr` (`0x5555d10`), `tEvtLog` (`0x54e2b50`) each
peek a VP register expecting a **pointer / handle / vtable / state-object**, get
back `0` (or a failed peek), and then **call through it** — exception **PC
`0x00000000`**, DEAR `0x38610040`/`0x64205b78` (a null base + small struct offset,
i.e. `*(NULL + field)`). This is the signature of *"peeked value used as a pointer,
value was zero."* It is **not** a QEMU MMU/model bug; it is the firmware faithfully
dereferencing the empty answer we gave it.

**Consequence for the fix — two tiers:**

- **Tier A (keep the tasks alive, no real video):** return, for each register these
  three tasks read, a value that passes their validity check (non-null handle / a
  benign state enum / a version the code accepts). Requires enumerating *which*
  registers each task reads and *what* value each consumer treats as valid — a
  per-task RE effort. Returning a blanket nonzero constant will **not** work (some
  values are used as table indices/lengths and would fault differently).
- **Tier B (real preview):** model the VP register file + RIO frame responses, or
  replay a JTAG capture from a live camera. This is the true ceiling toward a
  picture.

---

## Values derivable from the firmware alone (NO JTAG) — 2026-07-02 addendum

The firmware *encodes* what a valid answer is (poll targets, magic bytes, table
bounds). Deriving those gets us most of the boot path without ever touching a camera.
Key structural finding: **VpRegPeek addresses a `0x07000000`-based VP-internal
register space** (e.g. `lis r3,0x700; ori r3,r3,0x40` → peek `0x7000040`), plus a few
low addresses (`0x0`,`0x4`,`0xc`…`0x68`). The transport is the link; QEMU must decode
the requested VP address from the command and return the value below.

### A. Most peeks only need to *succeed* (return 4 bytes)
The VpConfig block-read (`0x233f00–0x234130`) reads `0x7000000/10/14/18/1c/30` and
after **each** checks only `cmpwi r3,0; bne → bail` — i.e. it wants the peek to
*succeed*, not a specific value. So a model that returns **any** 4-byte value (even 0)
for those addresses passes the read; the values are stored and consumed later. This is
the cheap 80%.

### B. The few addresses that demand a specific VALUE (all derived from poll/compare)
| VP reg | Required | Where / how derived |
|---|---|---|
| **`0x7000008` bit0** | **`= 1`** | polled ≤100× at `0x234020` (`andi. r,1; bne exit`), else config-error path. "sub-block ready/lock." |
| **`0x7000040`** | **`= 1`** | polled ≤2× at `0x234274` (`cmpwi r0,1; beq done; bgt retry`). "VP ready." |
| `0x7000000` | read-ok | control/status base, read `len=8` (`0x22eeb8`) at `0x233fc0`; value stored. |
| low `0x4` | bitfield | **40** single-bit accessors (`0x22f4a0`+) each do `rlwinm r0,N,0x1f,0x1f` → one boolean; **polarity is per-consumer**, no global magic. Model as a status word whose bits are set per what each caller waits for. |

So the *entire* value-specific requirement for VP bring-up is essentially **two "ready"
bits = 1** (`0x7000008` b0, `0x7000040`) plus "let every other peek succeed."

### C. Sensor identity — "Sensor detected as UNKNOWN" is a SEPARATE bus, also derivable
`"Sensor detected as MYSTERIUM…"` (str `0xd40508`, used at `0x8fc2c`) is gated on a
**byte global `0xe149b4` = sensor type**: `cmpwi 7 → MYSTERIUM`, `cmpwi 8 → alt`, else
UNKNOWN (`0x8fc08`). That byte is written at **`0x1f4b14`** from the result of
**`0x1f3d6c`**, which reads the **sensor-head bus** via **`0x1f3adc(reg=0x40, len=3,
flag=1)`** — *not* the VP peek path; it's the sensor's own I²C/serial interface (also
unmodelled → returns 0 → type ≠ 7/8 → UNKNOWN). **Exact signature decoded** from
`0x1f3d6c` (reads sensor reg `0x40` twice → `byte0`@`r1+8`, `byte1`@`r1+9`):

```
r11 = byte0 & 0x1c                 ; rlwinm r11,byte0,0,0x1b,0x1d
if (r11 == 0x10)  and  ((byte1>>5) == 0)   →  type = 7  (MYSTERIUM)   *0xea29e0 = 7
```

So a sensor-bus model returning **`byte0 = 0x10, byte1 = 0x00`** for reg `0x40`
detects MYSTERIUM (other patterns → type 8 / other). Type is cached in word
`0xea29e0` (7/8) and flag byte `0xe149c4`; type mirror at `0xe149b4`. Fully static,
no JTAG needed.

### D. The PC-0 crash is a null callback, not a magic mismatch
The three tasks read a value (VP or sensor), get `0`, store it as a
pointer/callback/handle, and later `bctrl` through it → **PC 0** (DEAR `*(NULL+off)`).
Returning "succeed + 0" is what *causes* this; the fix is to return a **non-null,
self-consistent** value for the specific register each task uses as a handle. Those
registers are reachable by the capture in the next section (they sit just before the
first exception line). Blanket-nonzero is unsafe (some values index tables/lengths).

### Bottom line on "how far can we get without JTAG"
- **Fully derivable now:** the two VP "ready" bits, "all block peeks succeed," and the
  sensor Mysterium signature byte-pattern (static constant in `0x1f3d6c`). That should
  clear config-verify + flip "UNKNOWN"→"MYSTERIUM".
- **Derivable with more static tracing:** the per-task handle registers behind the
  PC-0 crashes (follow each task's peek→store→call chain; tedious but static).
- **NOT derivable statically:** actual frame/pixel payload and any register used as
  opaque data with no in-firmware validation — but those don't crash, they just
  produce wrong images. A picture still needs modelled/replayed frame data.

## FREE-RUN CAPTURE RESULTS (2026-07-02) — plan corrected by evidence

Instrumented `red_hist_read/write` (0xe0080000) and `fpga_catchall_read/write`
(0xe2000xxx) with an env-gated `VPTRACE`, free-ran to the sensor/splash phase, and
captured every FPGA MMIO access. **Three static hypotheses were wrong; the real
blocker moved:**

1. **Boot already runs far past the old wall** — with the 3 committed bits it reaches
   VPFPGA-config-OK, ADV/HD-SDI/HDMI×3/audio/timecode/sync init, Sensor library,
   profile handlers, `Processed [893] parameters`, and **`Loading splash screen for
   REDONE`**, then hits `FrmBuf: DMA timeout`, `PipeInit() failed`, and finally the
   **`tAudioMgr` exception** (DEAR `0x38610040`, task `0x5555d10` — exactly the memory's
   record). So the crash is real and reproducible free-running (not a gdb artifact).

2. **The two VpConfig "ready" bits (`0x7000008`/`0x7000040`) never appear in the
   trace** and VP config already reports success — that verify path isn't on the live
   critical path. Implementing them is moot.

3. **Sensor identity does NOT come via the `0x1f3adc` bus** — it arrives over the RIO
   link. `"Sensor detected as UNKNOWN"` is printed right after a `vpfpgaRioRead:
   Timeout`, and `"Sensor Rev Read = 0x8"` shows the sensor path partially reads.

**The actual wall = the RIO register/response protocol at `0xe0080000`:**
```
W e0080000 = c30000RR    ; command: opcode 0xc3 (read) + VP reg RR in low byte
W e0080004 = <trigger>   ; arg/trigger
R e0080008 = 00000000    ; poll Rx response — always 0 → "waiting for Rx buffer
                         ;   to get anything" → vpfpgaRioRead Timeout
```
Read opcodes seen: top byte `0xc0–0xc7`, `0xe6`; reg bytes `0x14,0x78,0x7c,0x80,0x84,
0x88,0x8c,…`. The VPFPGA **version** read uses this path and lands garbage on the stack
(`Current VPFPGA version : 201515_1515_1515_25` = uninitialised `r1+0xa4/0xa8`; target
`2009_07_01`). There are **two RIO sub-channels**: the register read (poll `+0x08`) and
the bulk read `vpfpgaRioRead` (poll `+0x18` b10, data `+0x10/+0x14`).

### Probe experiment — transport model CONFIRMED, garbage is HARMFUL
Modelled a one-shot response: latch cmd at `+0x00`, arm on `+0x04` trigger, return a
non-zero probe word (`0xabcd00RR`) at `+0x08`. Result on free-run: the firmware
**consumed** it (proving the transport model is correct) and took a *new* path —
`Configuring VPFPGA (sensor board Unknown)... Reboot Detected VPFPGA forced to
restart`. I.e. a **wrong** value is read as a bad version/status and triggers a VP
reconfigure/reboot — strictly worse than the timeout. The bulk `vpfpgaRioRead`
(`+0x10/+0x14`) still returned 0 → `tAudioMgr` still crashed. **Reverted** (net
regression; tree back to the 3 committed bits).

### Conclusion (empirical): real per-register values are required, and this is the ceiling
- Transport is now proven: write `0xCC0000RR` → `+0x00`, trigger → `+0x04`, read Rx at
  `+0x08` (register channel) / `+0x10/+0x14` after `+0x18` b10 (bulk channel).
- A model must return the **correct** value per VP register `RR` — garbage causes a
  reconfigure/reboot. The only value known from the image is the **version target
  `2009_07_01`**; the sensor ID, board revs, and frame payload are VP-internal state
  **not statically derivable** and (as predicted) need a full VP register-file model or
  a JTAG replay. The user's "no-JTAG" derivation bottoms out here: we can derive the
  *transport* and a *few* targets, but not the per-register data the pipeline needs.

### Approach (a) experiment — version-only correct value (2026-07-03): NEGATIVE
Decoded the version encoding: format fn `0x6f24c` prints the word's nibbles as BCD, so
**`2009_07_01` = word `0x20090701`** (a genuine no-JTAG value). The current version is
read by `verFn 0x722fc`: word1 ← `0x1e1ce4`→`0x1dcc50(reg 0xff0)` (`r1+0xa4`), word2 ←
`0x22f47c`→`VpRegPeek(reg 0)` (`r1+0xa8`, pre-seeded `0xDEADBEEF`). Re-ran the probe
returning `0x20090701` at `0xe0080008`. **Result:**
- `Current VPFPGA version : 201515_1515_1515_25` — **UNCHANGED**. The version read does
  **not** ride the `0xe0080000` FIFO; it uses the VpRegPeek/`0x1dcc50` transport (reg 0 /
  reg 0xff0), a *different* physical window (likely `0xe2000xxx`). The `+0x08` response
  never reached it.
- `Reboot Detected VPFPGA forced to restart` — **still fires**, with the plausible
  `0x20090701` just as with garbage `0xabcd00RR`. So merely *responding* to the
  `0xe0080000` c3-commands triggers the VP reconfigure **independent of the value**.

**Verdict:** injecting the (correctly-derived) version word requires first pinning the
version register's real physical address (VpRegPeek reg 0 / `0x1dcc50` reg 0xff0 → a
`0xe2000xxx` port), which needs a targeted capture on the noisy IOFPGA window
(dominated by 8.3M writes to `0xe2000290`). And the `0xe0080000` register channel must
be modelled as a *full* command→response map (any partial/echo response reboots).
Probe reverted; tree clean at the 3 committed bits.

## Recommended next action — free-run MMIO capture keyed to the fault

Static tracing bottoms out at table-driven dispatch (the reg#→addr driver method and
the per-task consumers are indirect; cf. the `param-and-dispatch-table-driven`
finding). The efficient way to get the **exact** address list + expected values is a
**free-run** capture (never under gdb — timing/BH distortion, per
`qemu-bh-model-debugging-method`):

1. Run patched QEMU free-running with `qemu_log` MMIO tracing on `0xe0080000`
   (RIO block) and `0xe2000000–0xe2000fff` (VP reg window).
2. Bracket the log against the `vpfpgaRioReadWord`/`VpRegPeek`/first task-exception
   serial lines to get the **precise addresses read** just before each failure and
   the command words written to `0xe0080004/8`.
3. Cross-reference those addresses with a **live-camera JTAG read** of the same
   registers in the operational state (`0xe200028c`, `0xe20000f8`,
   `0xe0080010/14/18`, plus the newly-enumerated `0xe2000xxx` regs) to obtain the
   *true* expected values, and the live `0x840000` frame as a target image.

That yields a concrete `{address → value}` table to hardcode/replay in the device
models — deterministic, instead of guessing bit-by-bit.
