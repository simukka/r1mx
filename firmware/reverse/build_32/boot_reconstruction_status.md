# QEMU Boot Reconstruction — Status & Next Plan

**Status: 2026-06-21 — ORIGINAL `software.bin` FULLY BOOTS; patched image is BROKEN; one
wall left = external-interrupt delivery.** Read this section first; it supersedes the
"XIntc interrupt delivery" framing of the 2026-06-20 console notes.

### 1. Use `software.bin`, NOT `software.patched.r1mx.bin`
Booted both in QEMU at base `0x10000` (correct), gdb stub, `-d int`:

| | patched `.r1mx.bin` | **original `software.bin`** |
|---|---|---|
| end state | `usrInit`→kernelInit **returns** → bootstrap **dead-spins at `0x10124`** (`b 0x10124`) | **WIND scheduler idle `PC=0x5bb0dc`** |
| PIT clock | 0 ticks | **6420+ ticks** (system clock running) |
| tasks | none | **15 live** (tShell0, tNetTask, tTelnetd, usrApp, tSataMon, tTffsPTask, …) |

The patched image regresses. Cause: the r1mx patch set (e.g. patch #47 zeroing `intCnt`
@`0xE2942C`, the canary NOPs, SP reloc) were **symptom-fixes for the OLD wrong load base
`0x0`**. At the correct base `0x10000` the `.data` (incl. `intCnt`) loads correctly, so the
patches now **corrupt an otherwise-correct boot** (zeroed/forced state → kernelInit returns →
`0x124` spin — the exact symptom patch #47 was meant to cure). **Action: retire/regenerate the
r1mx patches; boot the unmodified `software.bin`.** (`qemu_boot.sh` default is already
`software.bin`; do NOT pass `--patched`.)

### 2. The boot is real — full task set at clean idle
`qemu_task_walk.py` on the original: `taskIdCurrent=…, readyQ=0, 15 tasks` — full VxWorks
daemon set + shell + net + telnet + RED `usrApp` + storage. PIT (internal, vec 0x1000) drives
the scheduler; this needs **no** XIntc (that's why the system runs fully without external IRQs).

### 3. The remaining wall: external interrupts (vec 0x500) are never delivered
Console (XUartLite) and telnet (XEmacLite) are interrupt-driven; both are dead because the
**XIntc never forwards** to the CPU:
- Peripherals DO assert their XIntc input lines — **UartLite→line 0, XEmacLite→line 1**
  (confirmed: a telnet SYN to the slirp-forwarded guest asserts `pin 1`). But **MER=0 / IER=0**
  the entire boot, so `CPU_IRQ` never asserts and **no vec-0x500 exception is ever taken**.
- The firmware **does** call `XIntc_Start` (runtime `0x26b3c`) and connects a vec-0x500 cascade
  handler via `excIntConnect` (r3=`0x500`, handler r4=`0x19dc4`). **But the XIntc instance
  struct it passes (`r3=0xfcaa14`) is uninitialised** — fill patterns `+0x04=0x11111111`,
  `+0x08=0x22222222`, `+0x00=0xe1200000` (PCI base, not the XIntc base). It was **never
  populated by `XIntc_CfgInitialize`**, so `XIntc_Start` writes MER to a garbage base — there
  are **zero MMIO accesses to the real XIntc at `0xe0800000` all boot** (the base IS correct in
  the static config record at runtime `0xe103f4`; the live instance just never gets it).
- `XIntc_Connect`/`XIntc_Enable`/`intConnect`/`intEnable` for the actual peripheral lines are
  never reached either → per-line IER bits also never set.
- This is the same family as the long-standing finding that the **cold-boot device-init /
  enumeration that builds driver instance structs hasn't fully run** (re_reference §0.3;
  [[qemu-coldboot-ctor-allocator-keystone]]).

**NEXT:** find `XIntc_Initialize`/`XIntc_CfgInitialize` and what gates it (why instance
`0xfcaa14` is left as fill). If that instance is initialised with `BaseAddress=0xe0800000`,
`XIntc_Start` will set MER, the per-device `XIntc_Enable` calls will set IER, and external
interrupts (UART RX, EmacLite RX) will flow → interactive shell on serial0 + telnet at once.

**Addressing gotcha (verified):** the embedded **symtab VALUE is already a runtime address**
(do NOT add `0x10000`). Confirmed: `usrRoot` symtab value `0x37c440` == the `rootRtn` constant
baked into `usrInit`'s `kernelInit` call. (The `+0x10000` in [[vxworks-symtab-address-resolution]]
applies only to the *name string* lookup, not the symbol value.) Other resolved runtime addrs:
`XIntc_Start 0x26b3c`, `XIntc_Enable 0x26f00`, `XIntc_Connect 0x26cf0`, `excIntConnect 0x37dd2c`,
`intEnable 0x37fb08`, `intConnect 0x453634`, `sysHwInit2 0x1d764`, `usrInit 0x37c350`.

QEMU XIntc model (`hw/intc/xilinx_intc.c`) and CPU wiring are CORRECT (verified: `x2vp4`→
`init_proc_405`→`ppc40x_irq_init` registers `PPC40x_INPUT_INT`; XIntc output wired to it; PIT
proves vec-0x500 delivery works once asserted). A debug trace is gated behind `R1MX_INTC_TRACE`
(set 0) in that file.

---

**Status: BREAKTHROUGH 2026-06-20 — the load base was wrong by 0x10000.** See the
2026-06-20 section below FIRST. `software.bin` is a position-dependent VxWorks RAM image
**linked for load base `0x10000`**; QEMU loaded it flat at `0x0`. Every "cold-.data
garbage" value, every "mid-function / garbage fn-ptr", the entire "irreducible circular
bootstrap", the hand-built allocator, and all the base-0 boot fixups were **symptoms of
this one off-by-0x10000 load error**. With the image loaded at `0x10000` the firmware
boots **natively into usrRoot** (no patches, no seeds, no forced dispatch). Everything
below dated 2026-06-11..06-19 is the base-0 investigation and is now **superseded**;
keep it for history but do not act on its plans.

_(Prior status was: PAUSED 2026-06-11, "cold-boot past the root-task dispatch". Companion
detail in `re_reference.md` §0.3; this file is the clean current-state + plan.)_

---

## TL;DR

`software.bin` is the **firmware program image RED ships** — extracted (decrypted) from the
official `redone.su` Build 32 upgrade installer (`redone.su` tar → AES-256-CBC `redone.1` →
gzip → `software.bin`). It is the image flashed to NOR and loaded into RAM at cold boot; it is
**NOT a memory snapshot of a booted camera** (see [[firmware-image-and-framing]]). Booting it in
QEMU stalls because the **cold-boot init sequence has not run to completion**, so the runtime
state it would build is absent: BSS (`0xE9BF20`–`0x1153480`) lies **above the `0xE8BF20` file end
→ zero in QEMU** and the heap is unallocated (both normal for a program image, runtime-populated
by a cold boot), several `.data` slots hold cold-boot-dependent values the init would overwrite,
and the **device layer isn't modelled**. Every path we tried (natural dispatch, forced-`usrRoot`
+ seeding, build-the-allocator, run-the-init) advances a bit, then hits the *next* prerequisite
that the not-yet-run init would have built. The work is real and the mechanism is now precisely
understood; a fully functional cold boot needs the early init + device layer to actually run
(model the device layer / flash→RAM boot path), not more per-slot seeding.

The boot already reaches a **stable, non-crashing dispatched+running** state (smoke_test
7/7). This effort was about going *past* that to the authentic `usrRoot` path.

---

## 2026-06-20 — THE LOAD BASE: software.bin is linked for 0x10000, QEMU loaded it at 0x0

**Root cause of essentially the entire effort.** `software.bin` is a position-dependent
VxWorks RAM image **linked for load base `0x10000`** (RAM_LOW_ADRS). QEMU loaded it flat at
phys `0x0` (`qemu_boot.sh -device loader,addr=0x0`). The image is internally self-consistent
only at `0x10000`. Early boot *appears* to work at base-0 because intra-code branches are
PC-relative (`bl`); but every **absolute** reference is off by exactly `0x10000`:

- **Data reads** (`lis/addi` → logical addr `L`): at base-0 they hit file offset `L`, but the
  real initialiser lives at file offset `L − 0x10000`. → the "cold-.data garbage".
- **Code pointers** (stored in `.data` or built with `lis/addi`): logical = `0x10000`-based;
  at base-0 a `bctrl` jumps `0x10000` too high → lands mid-function. → the "garbage fn-ptrs".

**Proof (all static, from `software.bin`):**
- `0xE8BF20` (file size) `+ 0x10000 = 0xE9BF20` = **exactly the BSS origin**. A flat image at
  `0x10000` ends where BSS begins.
- **12/13** firmware-computed code pointers (the 11 `FUN_00563B58` vtable handlers + the
  alloc/free in `FUN_005555ec`) land on **exact function prologues** at delta `0x10000`
  (free `0x565518`→`0x555518` is the only 4-byte-off straggler).
- **Every** "cold-garbage" `.data` slot becomes its correct cold value at `addr − 0x10000`:
  config gate `E0BDFC`=`0xFFFFFFFF`; guard-zone `E295E4`=`0`; usrRoot flag `E2706C`=`0`;
  dispatch ptr `E293F4`=`0`; dev count `E26978`=`0`; once-counter `E3A5E4`=`0`; **alloc-object
  ptr `E295C4`=`0x00FC2530`** (the value Option B hand-built!); canary `E169A4`=`0x12348765`.
- `rootRtn=0x37C440` (firmware-computed) → file `0x36C440` = a clean `stwu r1,-112` prologue =
  the real usrRoot (so the `#6` "0x37C440 is a resume label, redirect to 0x37BF78" was a
  base-0 ghost). And `0xE269A4 − 0x10180` (the camera D_text) = garbage → the file base is
  `0x10000`, **NOT** the camera's `0x10180` (that's a separate live placement; testing only
  `0x10180`/base-0 is why relocation was dismissed as a "red herring" in §2026-06-13).

**This SUPERSEDES:** the "circular bootstrap"/"unbuilt allocator object"/"needs the scheduler"
keystone, the dispatch-artifact saga (#4/#5/#6), the hand-built allocator (Option B), the
PCI-gate/guard-zone/canary seeds, and the "hand-fabricate the device table" plan. All were
symptoms of the load-base error.

**Fix (LANDED 2026-06-20, qemu-r1mx working tree):**
1. `qemu_boot.sh`: `-device loader,...,addr=0x10000` (was `0x0`).
2. `hw/ppc/r1mx_virtex4.c`: `env->hreset_vector = 0x00010000` (romInit, file 0 → runtime
   `0x10000`).
3. `r1mx_apply_boot_env_fixups` **disabled** (registration commented out) — every fixup was a
   base-0 symptom-patch; the code-patching ones would corrupt the wrong instructions now.

**Result (verified, unpatched `software.bin`, no seeds/patches/fixups):** reset PC `0x10000` →
romInit → prints `^^^123456789\r\n` on the console → **natural task dispatch into usrRoot**
(back-chain: `usrRoot 0x36c440 ← dispatch 0x371ac8`), which runs its real body
(`FUN_0036bcf8 → FUN_0045dc14`, the cache/MMU memory-region mapper). The exception vectors are
correctly copied to low RAM (runtime `0x1100` holds a real DTLB-miss handler; EVPR=0) and the
**data MMU comes on** (`MSR[DR]=1`) with TLB misses handled. This is **far** past anything the
base-0 effort reached, with zero fixups.

**Address-space convention going forward (IMPORTANT):** the corpus/Ghidra was built at base-0.
- **Function names `FUN_xxxxx` = FILE OFFSETS.** Runtime PC = file + `0x10000`
  (e.g. usrRoot file `0x36c440` runs at `0x37c440`).
- **Global names `uRam/iRam_xxxxx` = LOGICAL addresses = runtime** (read them from QEMU
  directly; their *initialiser* is at file offset `name − 0x10000`).
- All base-0 tooling breakpoints (`rsp.py`/`drive_enum.py`/`seed_boot.py`/`boot_orchestrate.py`)
  and the harvested live addresses need re-basing by `+0x10000`; the device-layer device models
  (PCI/ISP1562 endianness etc.) remain valid — they're MMIO, unaffected by the RAM load base.

### THE "NEW WALL" WAS A QEMU MMU BUG — DTLB-miss livelock (ROOT-CAUSED + FIXED 2026-06-20)

The 100%-CPU hang in the cache/MMU region mapper was **not** TCG-slowness or a wrong loop
bound — it was a genuine **DTLB-miss livelock**, and the cause was a bug in QEMU's PPC405
(4xx-softmmu) `tlbwe` emulation. Confirmed by `-d mmu` trace:

```
store to 0xE26EA4 (MSR[DR]=1, PID=1) → DTLB miss → vector 0x1100 → SW handler (file 0x371754)
  helper_4xx_tlbwe_hi entry N val 00e260c0 → set up TLB N EPN e26000 size 1000 prot rwx[v]  ← VALID
  helper_4xx_tlbwe_lo entry N val 00e26300 → set up TLB N EPN e26000 size 1000 prot rwx[-]  ← VALID CLEARED
  mmu40x_get_physical_address: access refused 00e26ea4 ... -1   → re-fault → ∞ (round-robin slots 7,8,9…)
```

The handler installs a **perfect** entry (EPN `0xe26000`, 4 KB, covers `0xe26ea4`, PID 0 =
global, rwx) yet the very next access is **refused**. Reason: the firmware's VxWorks 6.4 405
DTLB-miss handler writes the tag word **first** (`tlbwehi`, file `0x3717f0`) then the data word
(`tlbwelo`, `0x3717f4`). On real 405 the valid bit lives only in TLBHI, so the lo-write doesn't
touch it — but QEMU's `helper_4xx_tlbwe_lo` did `tlb->prot = PAGE_READ …`, rebuilding `prot`
from scratch and **discarding `PAGE_VALID`** that the hi-write had set. So `ppcemb_tlb_check`'s
`if (!(tlb->prot & PAGE_VALID)) return false;` rejected every freshly-installed entry. (Latent
for years because U-Boot / Linux ppc40x write lo-then-hi; only a hi-then-lo writer like this
VxWorks handler triggers it.) The PID-juggling in the handler (`0x3717c8`–`0x3717f8`, sets PID=0
for global entries then restores) is correct and consistent with QEMU — *not* the bug.

**Fix (LANDED in qemu-r1mx working tree, `target/ppc/mmu_helper.c` `helper_4xx_tlbwe_lo`):**
`tlb->prot = (tlb->prot & PAGE_VALID) | PAGE_READ;` — preserve the valid bit across the lo-write.

**Result — boot now sails past:** DTLB livelock gone (`access refused 00e26ea4` fires once, not
millions of times; log 84 MB/6 s → 6.8 MB/5 s). PC advances into device init (PCI/UART/NOR MMIO
at `0xe0641000`,`0xe1200008`,`0xf0000000`…), and **the PIT system-clock tick now fires** (`-d int`
shows `PIT (74)` interrupts repeating) — Phase 5 milestone reached, scheduler is alive. Serial
emits the banner + `E`.

### CURRENT WALL — VxWorks ATA/IDE driver `ataPiWait` (`FUN_000206bc`)

Mainline now spins in `FUN_000206bc` = **`ataPiWait`** (proven by its log string `0xD357CC`
`"ataPiWait: ctrl=%d request=0x%x astatus=0x%x ..."`). The poll loop (`0x20894`–`0x2096c`)
reads an MMIO **ATA Status register** via the byte accessor `FUN_0000a05c` (`eieio; lbz`,
file `0xac`) and waits on textbook ATA status bits — `0x80`=BSY, `0x40`=DRDY, `0x10`=DSC,
`0x08`=DRQ — that the (absent) QEMU device never asserts. `iRam00e107b4` is the ATA driver
**debug-verbosity level** (default 0; the `<5`/`<9`/`<0x46` tests gate `logMsg`), *not* a unit
count.

Driver layout (from register-map init `FUN_00023ad8`): per-controller resource table at logical
`0xe0ba64` (cmd-block base, stride `100`/ctrl), `0xe0ba68` (control-block / alt-status base),
`0xe0bab0` (DMA). The static initialisers are the **legacy PC IDE port layout**: cmd block
`0x1F0`(+0..7 → Data/Features/SecCnt/LBA/Device/`0x1F7`=Status), control block `0x3F6`
(alt-status). Only the **primary controller** is populated (`0x1F0`/`0x3F6`); secondary entries
are 0. Bounds in `FUN_00023ad8` (`param_1<2`, `param_2<2`) → ≤2 controllers × 2 drives.

**Timeout-path investigation (2026-06-20) — there is NO software timeout in `ataPiWait`.**
Both loop styles are pure register polls:
- *flag-gated:* `do { s = read(altstatus); if ((s & BIT)==target) break; } while (*(+0x108e9d4) != 0)`
- *pattern-gated:* `do { s = read(altstatus); if (...) break; r = FUN_0000a6ec(ctrl,0); } while ((r & 0xf0f)==0x103)`

`FUN_0000a6ec` is **not** a tick/timeout helper — it's a jump-table register accessor (`bctr`
through table `0x66c6c8`; each case returns a read of `base + ctrl*0x80 + offset`), so the
`==0x103` loop just polls a *second* controller register. The gate `*(+0x108e9d4)` is the
per-controller **present flag**, written `=1` at init and **never cleared to 0** anywhere in the
corpus. ⇒ a working PIT does **not** rescue this path; the firmware trusts the controller to
always answer with valid ATA states.

**Live ground truth (QEMU gdb stub, stuck in the spin):** the register pointers are the **raw
legacy ports, un-rebased** — `[0x108ea24]`=`0x1F7` (Status), `[0x108ea2c]`=`0x3F6` (AltStatus),
table `0xe0ba64`=`0x1F0`/`0xe0ba68`=`0x3F6`/`0xe0ba6c`=`0x1F7`, present-flag=1. Those addresses are
**plain DRAM** in QEMU (the low exception-vector page: `0x1F4`=`addi r1,r1,16`, `0x1F8`=`blr`), so
the byte reads return *code* — Status@`0x1F7`=`0xA1`, AltStatus@`0x3F6`=`0x08` — which never settle
to a valid ATA idle/ready state ⇒ infinite poll. **No ATA/SATA controller is modeled in QEMU**
(the only `SiI3512`/`R1MX_DEV_SSD` reference is a GUI activity-telemetry ID, not a device).

**Hot-plug architecture (confirmed):** ATA init spawns task **`tSataMon`** (string `0xD35D4C`
`"tSataMon"`) and logs `"ataDrv: Calling sysAtaInit (if present)"` — the firmware is built for
**removable** media (ATA HDD / SATA HDD / SATA-to-CF), media attachable/detachable at any time.
So with a *responding* controller and no media, `tSataMon`/`sysAtaInit` would detect "no drive"
and boot would continue. The wall is purely the **absent controller** returning garbage.

**Open contradiction to resolve first (decisive next experiment):** the firmware polls bare
`0x1F0`/`0x3F6`, which overlap the `0x0–0x2000` exception-vector page — impossible on real HW
unless either (a) the ATA controller's command/control block is decoded at those CPU-physical
legacy addresses (EBC/FPGA chip-select winning over DRAM for data-side reads), or (b) the BSP
`sysAtaInit` (vendor code, not in corpus) rebases the table to a PCI-I/O window after reading the
SATA controller's BAR — a step that produced `0x1F0` here because no PCI SATA device exists to
program the BAR. **Read the same table `0xe0ba64` + poll `0x1F0/0x3F6/0x1F7` on the LIVE camera
over JTAG** (read-only, existing host-XMD bridge) to settle (a) vs (b). Then either overlay a
high-priority ATA model at the real decode addresses, or add the PCI SATA controller so the
BAR-rebase + presence-detect path runs — returning a "controller present, no media" status so
`tSataMon` continues.

---

### ATA empty-bay PROTOTYPE — clears the storage wall (2026-06-20)

Implemented in qemu-r1mx (`hw/ppc/r1mx_virtex4.c`, `ata_empty_ops`): a minimal "empty IDE/SATA
channel" overlaid at the bare legacy ports the firmware polls — command block `0x1F0-0x1F7`,
control block `0x3F6-0x3F7` — high-priority over the low RAM page. Reads return `0xFF` (floating
bus = no media); writes (incl. SRST to DevControl) are discarded.

**Result — the ATA wall is cleared.** Verified live (gdb stub): overlay is hit
(AltStatus@`0x3F6`=`0xFF`, Status@`0x1F7`=`0xFF`), and the reset/probe `FUN_0001f8f0` now returns
`r3 = 0xFFFFFFFF` (= "no drive") instead of falsely detecting a ready drive and hanging in the
no-timeout `ataPiWait`. The `ataPiWait` spin loop (`0x20894-0x2096c`) no longer appears in `-d int`
traces. Boot then executes a broad multi-task init burst (interrupted PCs now spread across the
*entire* firmware — `0x37xxxx/0x46xxxx/0x4axxxx/0x5bxxxx/0x5fxxxx/0x64xxxx` + hundreds of one-shot
low-address DTLB misses) and settles **cleanly idle at 0.0% CPU** in the VxWorks WIND scheduler
idle loop (`FUN_005aaf5c`, `do {} while (readyQ==0)` at runtime `0x5bb0dc`).

This is a prototype (overlay at literal legacy addresses) pending the live-HW read
(`plans/ata_live_hw_read.md`) to confirm decode (a) low-address vs (b) PCI-I/O-window rebase; the
empty-bay return value is faithful regardless.

### FULL BOOT ACHIEVED — TCB walk shows a running VxWorks system (2026-06-20)

The "stuck at `E`" was a **misread**: it's not blocked, it's a **fully booted, idle** VxWorks
camera. A TCB walk inside QEMU (`firmware/scripts/qemu_task_walk.py`, gdb stub) enumerates **15
live tasks** — the complete system-daemon set plus shell, networking, telnet and the RED app:

| prio | task | entry | note |
|---|---|---|---|
| 0 | tSataMon | `FUN_00027e90+0x354` | storage monitor — **alive** (ATA fix worked) |
| 0 | tNbioLog / tLogTask / tJobTask / tExcTask | `FUN_00445274 / 004442cc / 004437ac / 00442c80` | VxWorks system daemons |
| 10 | tErfTask | `FUN_003c8e38+0xc8` | RED task |
| 30 | usrApp | `FUN_0000e188+0x1c0` | **RED application task** |
| 40 | tShell0 | `FUN_0047ea74` | **VxWorks shell** |
| 50 | tNetTask | `FUN_003d74e8+0x128` | TCP/IP |
| 50/50/51 | tAioIoTask0/1 / tAioWait | `FUN_00484cc0 / 004849b8` | async I/O |
| 55 | tTelnetd | `FUN_003d63a0+0x788` | **telnet daemon** |
| 75 | tCciTask | `FUN_003bddc0+0xc4` | RED camera-control IF |
| 100 | tTffsPTask | `FUN_0054f444+0x28` | TrueFFS (status DELAY = sleeping) |

All tasks PEND/DELAY (normal idle-daemon state); `readyQ` empty ⇒ clean idle, not a hang. So the
DTLB livelock + load-base + ATA-empty-bay fixes carried the firmware **all the way from cold-boot
crash to a running VxWorks with shell + network + telnet + the RED app**.

**Why serial stops at `^^^…E`:** the captured console is the **XUartLite** (boot-ROM diagnostics);
the **XUartNs550** UARTs (`0xe0640000`/`0xe0650000`) are `create_unimplemented_device` (no model,
no chardev) — so a VxWorks shell/banner routed there is discarded. The interactive console is
either an NS550 (needs a real 16550 model + `-serial`) or **telnet over the emulated Ethernet**
(`tTelnetd` is up; needs `qemu_boot.sh --net` + a telnet client to `192.168.0.2`).

**Active-list node offset for this image = TCB+0x1c** (next@+0x1c, prev@+0x20), TCB sig
`0x00810600` @+0x08, prio @+0x48, static ENTRY @+0xc0 — re-derived here (cam-working-01's
`task_walker.py` used +0x50; differs by build/state). `qemu_task_walk.py` encodes these.

**NEXT:** get an interactive console — either model the XUartNs550 (16550) and capture its serial,
or bring up `--net` + telnet — to confirm the shell prompt and drive the booted system; then check
whether `usrApp` reaches its steady state or waits on sensor/FPGA events.

### Console + networking attempts → XIntc interrupt delivery is the next blocker (2026-06-20)

Pursued both consoles; both dead-end at the **same root cause: XIntc→CPU external interrupts are
never delivered.**

- **Networking (no root):** rebuilt QEMU with the meson `slirp` option (user-mode net, no TAP).
  The camera's IP is `192.168.0.2` — confirmed from the image's **compiled bootline**
  `xemaclite(0,0)host:vxWorks h=192.168.0.1 e=192.168.0.2 u=xemhost` (file `0xd5c608`), matching the
  SLIRP subnet. `-net user,...,hostfwd=tcp:127.0.0.1:2323-192.168.0.2:23` forwards and TCP-connects,
  but the **guest is silent** (no telnet banner).
- **NS550:** modeled both XUartNs550 cores as serial-mm 16550s (committed). But the firmware
  references **only the XUartLite** (`0xe0600000`; corpus grep: 1 ref in `hw_seq_init`, 0 for either
  NS550) — the NS550s stay empty. The console is the **XUartLite**.
- **Console path:** `^^^123456789` + the trailing `E` come from `hw_seq_init` via the *polled* putc
  `FUN_0001b9b0` (waits STATUS&0x08=TXFULL, writes TX@base+4) → `FUN_0001c8bc(0xe0600000)`. The
  VxWorks *runtime* banner/shell use the **interrupt-driven sio** path instead, which writes one
  char then waits for a TX interrupt.
- **Smoking gun:** `-d int` over a full boot shows **only PIT (vector 0x1000, internal PPC405
  timer) and DTLB — never an EXTERNAL interrupt (vector 0x500)**. The XIntc output *is* wired to the
  CPU (`sysbus_connect_irq(intc_sbd, 0, cpu_irq)`, `PPC40x_INPUT_INT`), yet nothing arrives. So every
  XIntc-routed source (UartLite RX/TX, **XEmacLite RX**, DMA) cannot interrupt the CPU — which
  explains BOTH the console stalling after the first runtime char AND the telnet/network silence
  (EthLite RX IRQ never fires → SYN never processed).

**NEXT (unifying):** debug XIntc external-interrupt delivery — does the firmware program the XIntc
(MER master-enable + IER per-line) and the peripheral IE bits; does `xlnx.xps-intc` propagate an
asserted input to its CPU output; is `PPC40x_INPUT_INT` honored with `MSR[EE]` set (PIT works, so
EE is on — points at the XIntc model or its programming, not the CPU). Fixing this should unblock
the interrupt-driven console (shell prompt on XUartLite serial0) and networking/telnet at once.

## 2026-06-13 — ROOT CAUSE LOCALIZED: the "device layer" is PCI USB enumeration

Two results this session, both verified statically against `software.bin`:

**(1) The relocation/LMA hypothesis is a RED HERRING for QEMU.** The `cam-working-01`
`D_text=0x10180` is a *live-camera* load placement; for QEMU, base-0 is the correct,
self-consistent frame (`usrInit`/`kernelInit` run at base-0 addresses; the boot-env
canary patch at base-0 `0xE269A4` works and matches live `0x12348765`). `D_data≈0`:
globals/BSS live at the image-encoded absolute address. **Do not chase a load-offset.**

**(2) The §0.3 "keystone" (allocator `0x5652D0`/`FUN_005651E8` returns `-7`) and the
"device layer QEMU doesn't model" are the SAME thing: missing PCI devices.** The causal
chain, fully traced:

```
FUN_002096a4 (driver-table entry, no static caller — lazy first-access)
  → FUN_0035aba0/ab0c (lazy get-or-init of the device table)
    → FUN_003682e4 → FUN_00367f54   ← THE PCI ENUMERATOR
        for idx in 0..4:  (count caps at 5, NOT 0x01000000)
          FUN_00367340(0xc,3,progif,idx,…) → FUN_00000b3c → FUN_000005a4
            = textbook PCI config scan (bus 0..max × dev 0..31 × fn 0..7):
              cfg off 0x00 = Vendor/Device (0xFFFF ⇒ empty slot)
              cfg off 0x08 = Class code; match  class>>8 == 0x0C03  (USB host ctlr)
              cfg off 0x0E = Header type (multifunction bit)
          on FIRST failed query →  break  → count 0xE26978 stays 0
        writes descriptors into 0x10CF458[idx], sets count 0xE26978
    → FUN_00563B58 (gated `iRam00e3a624==0 && uRam00e26978!=0`):
        builds per-device 84 KB contexts (FUN_00560544) into iRam00E3A624[]
  → FUN_005651E8 / 0x5652D0 indexes iRam00E3A624[count]; count==0 ⇒ returns -7
```

So: **QEMU's XPci_v3 host bridge has NO PCI devices attached** (the Phase-2 ISP1562 USB
stub, class `0x0C03`, was marked "optional"). Every config slot reads `0xFFFF` →
enumeration finds nothing → device count `0xE26978` = 0 → `FUN_00563B58` builds no
contexts → the keystone allocator returns `-7`. The "device layer" is **not** unmodelable
custom silicon — it is **standard PCI**, which QEMU's bridge already handles; only the
*leaf device* is missing.

**Config access (`FUN_000005a4`) supports 3 mechanisms via `iRam00e0bdf8`; the firmware
uses mechanism #1**: write `CONFIG_ADDRESS = bdf|off|0x80000000` to `*0xE9C708`, read
`CONFIG_DATA` from `*0xE9C70C` (both BSS, set at runtime by PCI init; gate `*0xE0BDFC`
must be 0, max bus `*0xE0BDF4`).

**The probe is more than ID-only** (so a "NAK-all" stub is insufficient). After matching
class `0x0C03`, `FUN_00367f54` (2nd loop): enables the device (`cfg cmd |= 6` = Mem+BusMaster),
reads a BAR, calls the device's own register read at `BAR+8`, and if the returned byte
`(val>>8)&0xff > 0x40` it issues a reset and **polls a status register up to 1000×** for
`(reg & 0x10000)==0 && (reg>>24 & 1)!=0`. The ISP1562 stub must satisfy these reads.

**Recommended next step (emulator-side, replaces "Path C" pessimism):** attach a PCI
device of class `0x0C03xx` to the XPci_v3 bridge in `qemu-r1mx` (the deferred ISP1562
stub — now shown **load-bearing for cold boot, not optional**) with enough register
behavior to pass the enable→BAR→reset→poll sequence above.

**Open caveat (verify before/while implementing):** the enumeration is triggered *lazily*
by a driver-table entry (`FUN_002096a4`, no static `bl`) during the `usrRoot` device-init
cascade — which the current QEMU boot does NOT reach naturally (dispatch artifact). So
either (a) reach it via the forced-`usrRoot` harness to test the device fix in isolation,
or (b) confirm the dispatch artifact itself is downstream of the same empty-heap/allocator
state. Fixing PCI may cascade to unblock the dispatch, but that is unproven until tried.

### 2026-06-13 (cont.) — ISP1562 stub IMPLEMENTED + config-discovery VALIDATED

Implemented two ISP1562 USB host-controller leaf devices on the XPci_v3 bridge
(`qemu-r1mx` `hw/pci-host/xilinx_opb_pci.c`): bus0/dev1/fn0 class `0x0C03A0` (enumerator
loop 1) and bus0/dev2/fn0 class `0x0C0320` (loop 2, with BAR0=`0xA0000000` backed by a
zero-returning register block so the post-match probe's `(reg>>8)&0xff > 0x40` test is
false and the reset/poll path is skipped). VID/DID `0x04CC:0x1562`. Command-reg writes
(`cmd |= 6`) are shadowed.

**Validated** with `firmware/scripts/pci_isp1562_probe.py` — drives CAR/CDR via a
CPU-executed PPC stub (gdb-stub *debug* writes to MMIO do NOT reach device models;
use real execution): **9/9** config cycles correct (both devices discoverable, BAR0
reads back, empty slots → `0xFFFFFFFF`).

**KEY DEPENDENCY DISCOVERED — the firmware's PCI subsystem init does NOT run in the
reachable boot.** At the stable dispatched state (bp `0x382bec`), the PCI globals are
all still at their cold `.data`/BSS values (so config access is not even set up):

| global | meaning | observed | cold `.data` | state |
|---|---|---|---|---|
| `0xE0BDFC` | config gate (0 ⇒ open) | `0x943C5669` | `0x943C5669` | **untouched** |
| `0xE0BDF8` | mechanism (1/2/0) | `0x5C134C9C` | `0x5C134C9C` | **untouched** |
| `0xE9C708` | CAR reg MMIO addr | `0` | (BSS) | **unset** |
| `0xE9C70C` | CDR reg MMIO addr | `0` | (BSS) | **unset** |
| `0xE26978` | device count | `0x01000000` | `0x01000000` | **untouched** |

`FUN_000005a4` early-returns `0xFFFFFFFF` while `0xE0BDFC != 0`, so *no* config cycle
fires until PCI init runs — and PCI init is itself in the `usrRoot` device cascade that
the dispatch artifact never reaches. **Consequence:** the ISP1562 stub is correct and
necessary but cannot be exercised by the natural boot; the next step to actually reach
the enumeration is the forced-`usrRoot` harness (`seed_boot.py`), which must first get
past the allocator keystone (`0x5652D0` → `-7`) — itself the empty-device-table symptom
this stub addresses. Validation tooling: `pci_isp1562_probe.py` (model-level, passing).

### 2026-06-13 (cont.2) — endianness bug FIXED; firmware scanner now finds the devices

Drove the firmware's OWN PCI primitives from the dispatched state (seed the PCI
mechanism globals above, then call into them via the gdb stub):

1. **Found + fixed a real emulator bug.** The XPci_v3 bridge MMIO region was
   `DEVICE_BIG_ENDIAN`, but the firmware accesses CAR/CDR exclusively through
   little-endian byte-swapping accessors (`FUN_00000118`/`FUN_0000010c` =
   `XPci_mWriteReg`/`mReadReg`). So the firmware's swapped CAR (`0x80000800` →
   stored `0x00080080`) lost its enable bit and *every* config cycle returned
   `0xFFFFFFFF`. (The bug was latent: `XPci_SelfTest` does no HW access, so config
   cycles were never exercised before.) Changed the region to `DEVICE_LITTLE_ENDIAN`
   (`hw/pci-host/xilinx_opb_pci.c`).
2. **Verified the firmware's scanner finds the ISP1562s:** `FUN_00000b3c(0x0C03A0)`
   → ret 0, bus0/dev1; `FUN_00000b3c(0x0C0320)` → ret 0, bus0/dev2;
   `FUN_00367340(0xc,3,0xa0)` → 1 (success). The device model is correctly integrated.
3. **Next blocker pinpointed = the heap allocator / C++ ctor phase.** Running the full
   enumerator `FUN_00367f54` faults (Alignment 0x600) before incrementing the count,
   because it allocates descriptors via `FUN_0045b974`, which dispatches through the
   allocator OBJECT `*0xE295C4 = 0xD8FA64`. That pointer holds its cold `.data` value
   and points at **rodata** — `*(0xD8FA64+0xCC) = 0x6E745036` (ASCII `"ntP6"`), not a
   code pointer — so `FUN_0045b974(0x24)` does `bctrl 0x6E745036` → **0x700**. The
   allocator object is a C++ global whose vtable/method slots a static constructor
   patches at boot; that ctor has not run. **This is the same C++-ctor/memInit
   foundation as the §0.3 keystone** — the allocator, the device tables, and the
   deferred lists are all built by it. Until it runs, no per-slot seeding can make the
   device enumeration (or the natural root-task dispatch) work.

**Bottom line for "make Build 32 boot":** the device-layer modelling is now done and
correct (PCI + ISP1562, endianness right, firmware scanner satisfied). The remaining
frontier is singular and foundational: **run the C++ static-constructor / module-init /
memInit phase** (§0.3 Path A) so the allocator object, memory partition, and kernel
lists exist. With the PCI device now modelled, re-attempting Path A may get further than
the original §0.3 try (which stalled at the unmodelled device enumeration). PCI mechanism
seeds are staged (disabled) in `seed_boot.py` `PCI_SEEDS` for when the allocator works.

### 2026-06-14 — Init-phase / dispatch investigation (where the ctors live)

Goal: find and run the init phase so the allocator object + the ~264 null-guarded
`.data` fn-ptr slots get built. Traced the full early boot statically:

- **`usrInit` (0x36C350) and `kernelInit` (0x5A7F30) do NOT run a C++ ctor phase.**
  `usrInit` = canary-spin → **bzero BSS** (`bl 0x496698`) → a handful of *individual*
  registrations (`0x458A00` sets `*0xE29428=0x468DD0`; `0x36E3DC` sets two slots;
  `hw_seq_init`/`0xDCB0` does clock/SDRAM/FPGA setup) → `kernelInit`. `kernelInit`
  computes the memory pool, `taskInit`s the root task (`FUN_005B2880`), and
  `taskActivate`s it (`thunk_FUN_005b0ff4`). **No `__CTOR_LIST__` walk in either.**
- **There is no classic GCC ctor list.** The 123-pointer run at `0xE166CC` (null-
  terminated, looked like `__CTOR_LIST__`) is **not** ctors — several entries are
  mid-function addresses (`0x46B580` uses `r31` unset). Ruled out.
- **Conclusion: the foundational objects are built by init/registration calls scattered
  through the ROOT TASK's own sequence** — the part the dispatch artifact (`0x381A8C`,
  patches #53/55) bypasses. The root-task entry `0x37C440` is `b 0x37C290` into a large
  flag-driven dispatcher loop (no clean prologue in `0x37C060..0x37C290`), so there is no
  obvious "function start" to force that runs the allocator build first.
- **The dispatch is itself a garbage-fn-ptr victim (circular dependency).** Disabling
  #53/55 → the natural path calls `*0xE293F4 = 0x542974`, which is a **function epilogue**
  (`lwz r31,0x1c(r1); mtlr; addi r1,0x20; blr`) — calling it just returns to a garbage
  `lr` → the reset loop §0.3 saw. On real HW `0xE293F4` holds a valid handler installed by
  init. So: the **dispatch needs init, and init runs inside the dispatched task** — the
  bootstrap circularity that makes this the hard wall.

**Net:** confirmed the blocker is a circular bootstrap (root-task init builds the
allocator + dispatch fn-ptrs, but reaching that init needs a working dispatch + allocator).
Not crackable by per-slot seeding or by forcing a single entry. **Recommended approaches
(decision for the owner):**
1. **Harvest from the live working camera** (already booted): read the *post-init* values
   of the static (code/rodata) fn-ptr slots — `0xE293F4`, the registration slots, etc. —
   and seed them. Works for slots pointing at static handlers; **not** for heap objects
   (e.g. the allocator object `*0xE295C4`, whose live value is a camera-heap address absent
   in QEMU). Cold-boot HW lockstep is infeasible ([[rst-is-core-only-no-cold-boot]]).
2. ~~Initialise the app allocator partition at `0xD8FA64`~~ **— VOID (2026-06-14, wrong
   premise).** `*0xE295C4` cold value `0xD8FA64` is **inside a C++ mangled-symbol STRING
   table** (`_Z14ParamSetString...`), not an object — a garbage placeholder. The real
   allocator is a **runtime-constructed heap object**; the init phase builds it and points
   `*0xE295C4` at it. (`FUN_0045B974` guard `*(obj+0xCC)==0`→default `FUN_0045B6B8`; zeroing
   `*(0xD8FA64+0xCC)` only stops the 0x700 by indexing into the string table → returns NULL.)
   **And there is no bootstrap allocator either:** `kernelInit`'s `FUN_0036cad0` is just
   `memset` (fills the root stack with `0xee`) — it does NOT create a system memory partition.
   So **nothing is allocatable at the dispatched state**, and there is no discrete pool/seed
   fix. The remaining real options are: (A) crack the circular dispatch so the natural init
   runs in order (deep research; §0.3 couldn't); (B) hand-construct an allocator + memory
   partition in reserved QEMU RAM and repoint `*0xE295C4` (very fragile; the registration
   cascade still follows); (C) accept Path C — the validated device modelling (PCI + ISP1562
   + bridge endianness) is the realistic ceiling.
3. Accept the device-layer work as complete and the boot as "reaches live multitasking +
   correct device models," and treat full cold-boot as out of scope (original §0.3 Path C).

---

## 2026-06-14 — DISPATCH ARTIFACT CRACKED via live-camera harvest (2 seeds)

Harvested the dispatch-critical `.data` slots from the live booted camera
(`cam-working-01`, D_text re-derived = `0x10180`; reads validated against the DRAM
canary `*0xE269A4=0x12348765`). **The "OpenSSL artifact dispatch" is just two
uninitialised `.data` slots** — not a deep problem:

| slot | QEMU cold | live camera | role |
|---|---|---|---|
| `*0xE3A790` (dispatch selector) | `0` | **`0x00FC9580`** (non-zero) | `FUN_00371cd0`: `if (*0xE3A790 == TCB+0x94)` → if-path artifact; else → `PC=TCB+0xC0` |
| `*0xE293F4` (else-path fn-ptr) | `0x542974` (stale epilogue) | **`0`** | `FUN_00371c74`: `if (ptr==0) skip; else call ptr` — real value 0 ⇒ skip |

In QEMU both `*0xE3A790` and the root `TCB+0x94` are `0` → they match → the **if-path**
fires (saved PC = `0x381AEC`, itself a function *epilogue*; patch #55 redirected it to
`0x381A8C`). The else-path was never taken. **Make-or-break check PASSED:** at the
dispatch, the root `TCB+0xC0` (entry) = **`0x0037C440` = usrRoot**, a static code pointer.

**Fix = 2 seeds, verified in QEMU:** seed `*0xE3A790 = 0x00FC9580` (non-zero ⇒ root
`TCB+0x94`=0 ≠ selector ⇒ **else-path**) and `*0xE293F4 = 0` (⇒ skip the stale call).
`FUN_00371cd0` then sets the root task's saved PC = `TCB+0xC0` = **`0x37C440`**. The
natural firmware dispatch reaches **usrRoot** with a real task context — **no patches
#53/55, no forced PC.** Continuing, usrRoot runs its early path and stalls at the
allocator (`0x700` in `FUN_00555488`, the `*0xE9C34C` call).

**Allocator fn-ptrs harvested (ground truth, confirm the old guesses):**
`*0xE9C34C = 0x005652D0`, `*0xE9C648 = 0x00565518` (== the `seed_boot.py` #2 values).
With those seeded too, usrRoot advances *past* the NULL-call into `0x5652D0` (the
device-context manager `FUN_005651E8`), which then faults (`0x700`, lr=0) **indexing the
empty device table** (`iRam00e3a624`, a heap object unbuilt in QEMU; live `dev_count=1`,
`*0xE295C4` allocator object = heap `0x00FC2530`).

**Net:** the dispatch circularity is **broken** (Option A success on the immediate
dispatch — the natural boot now reaches usrRoot). The remaining wall is exactly the
predicted **heap-object construction** (allocator pool + device table) = Option B —
now reached via the *natural* path, confirming the artifact dispatch was downstream of
the empty-allocator/device state all along.

**Emulator-side fix — IMPLEMENTED + VERIFIED 2026-06-14** (`qemu-r1mx`
`r1mx_apply_boot_env_fixups`). NOTE the 2-seed plan needed one correction: **`TCB+0x94`
is COPIED from `*0xE3A790` at task setup**, so seeding the selector propagates into
`TCB+0x94` and they re-match → if-path (verified: fixup-seeding `*0xE3A790=0xFC9580` made
`TCB+0x94=0xFC9580`). And the if-path target is NOT a trampoline (`0x381A8C` = a function
prologue, `0x381AEC` = mid-routine, both in the OpenSSL X.509 code). On HW `*0xE3A790`
changes between root creation and dispatch (no static writer) → else-path; a static seed
can't reproduce that timing. **Final fix = FORCE the else-path:** patch the branch at
`0x371D5C` (`bne 0x371D78` = `4082001C`) → `b 0x371D78` (`4800001C`), so every task
dispatches to its own `TCB+0xC0` entry (normal VxWorks behaviour; the if-path artifact +
patches #53/55 become dead code), and seed `*0xE293F4=0` (the else-path calls it only if
non-zero; stale `0x542974` would crash). Verified: boot-time fixup alone → root saved PC =
`0x37C440` = usrRoot, natural dispatch, no manual seeds. The boot then advances into early
usrRoot (DSI/0x700 at the deferred-write list / allocator — the Option-B heap wall).
Tooling: `firmware/scripts/harvest_slots.py` (read-only camera harvester), `seed_boot.py
--harvest` (+ documented `DISPATCH_SEEDS`), `rsp.py` (now drains/retries the flaky XMD
stub). Harvest reports in `camera_reports/cam-working-01/`.

## 2026-06-15 — Option B: ALLOCATOR CONSTRUCTED + WORKING in QEMU

The foundational heap allocator (`*0xE295C4`, RED's custom tree memory-partition at the
**fixed** address `0xFC2530`) is now built in QEMU and `malloc` returns real pool memory.

**Found the create path:** module-init `FUN_004593a8` (sets the default flags `0xBB0` +
alloc/free method fn-ptrs) → `FUN_0045acac` → `FUN_0043c570` (create the `0x110`-byte object)
+ **`FUN_0045aa38(0xFC2530, pool, size)`** = the partition init (memset, set `+0xC0` flags,
`semMInit` the `+0x50` lock via `FUN_005ada10`, register class, then `FUN_0045a74c` =
addToPool, which builds the free tree). `FUN_0045acac` is gated by `iRam00e295f8 != 0`
(garbage cold) and needs the object/class system, so we bypass it.

**Verified recipe** (`firmware/scripts/build_allocator.py`, run at the allocator wall):
1. `FUN_004593a8(0,0,0xBB0)` — set module globals (flags + method fn-ptrs).
2. seed `*0xE295D4 = *0xE26D3C` (min-align=granule), `*0xE295F4 = 0` (the method-setup
   fn-ptr is garbage cold `0xD8FB0C` and would be `bctrl`'d → fault; 0 = skip).
3. `FUN_0045aa38(0xFC2530, 0x08000000, 0x04000000)` — init the partition with a 64 MB pool
   carved from the heap band (sysMemTop=0x10000000).
4. `*0xE295C4 = 0xFC2530`.

**Result (verified):** partition built (`+0xC0=0xBB0`, free-tree root `+0x40=0x08000008`,
node count `+0x4C=7`); `FUN_0045B974(0x54)` returns `0x08D8FBB8` — **real, writable pool
memory** (write/read-back of `0xA5A5A5A5` confirmed). The tree allocator (general malloc)
WORKS.

**Cascade status (next):** the foundational malloc is done. The natural boot's first wall is
the **device-context** alloc `FUN_00555488 → *0xE9C34C=0x5652D0` (in module-init
`FUN_00552BF4`), which needs the **device table** built by PCI enumeration
(`FUN_00367f54`, satisfiable by the ISP1562 model).

### 2026-06-15 — The "byte-reverse MMIO 0x600 alignment fault" was a MISDIAGNOSIS (debunked)

The previously-recorded "context-dependent `0x600` Alignment fault in the PCI config access"
**does not exist**. There is no byte-reverse alignment fault. Three independent proofs (QEMU
booted with `-d int,mmu,guest_errors`; allocator built via `build_allocator.py`):

1. **Direct `lwbrx` from the CDR** (`FUN_0000010c`: `eieio; lwbrx r3,0,r3; blr`, r3=`0xe1200110`)
   at the `0x555488` context returns cleanly (`r3=0xffffffff`, no exception). MSR at that
   context is **`0x00000000` — the MMU is OFF**, contradicting the old "MMU on → guarded" story.
2. **Full byte-reverse CAR/CDR config cycle works and the ISP1562 model responds:**
   `mWriteReg(CAR=0xe120010c, 0x80000000|bus<<16|dev<<11)` (`FUN_00000118`=`stwbrx`) then
   `mReadReg(CDR=0xe1200110)` (`FUN_0000010c`=`lwbrx`) returns: dev0(bridge)=`0x000710ee`,
   **dev1=`0x156204CC`** (ISP1562 VID `0x04CC` DID `0x1562`), **dev2=`0x156204CC`**,
   dev3=`0xffffffff` (absent). Int log **clean — zero alignment exceptions**. The
   `DEVICE_LITTLE_ENDIAN` bridge fix + ISP1562 model are validated end-to-end at byte-reverse.
3. QEMU's `translate.c` does **not** emit `gen_align_no_le` for `lwbrx`/`stwbrx` (only `lmw`/
   `stmw`/string ops in LE mode), so QEMU never raises align for byte-reverse — period.

**Root cause of the false "0x600":** a debugging-harness artifact. The driver scripts set
breakpoints at `{0x100,0x200,…,0x600,0x700}` believing they were exception vectors. **They are
not** — the PPC405 relocates exception vectors via **EVPR**, and the firmware places its low
PCI/XPci config driver at `0x100–0x9000`. Physical `0x600` is the `beq 0x634` instruction
*inside* `FUN_000005a4`. With the config gate open, normal flow reaches `0x600` → the bp fires →
misread as "0x600 alignment fault." **Lesson for harnesses:** do not trap on `0x100–0x700`;
rely on the `-d int` log for real exceptions and a high CATCH address (e.g. `0xC`).

**The REAL prerequisites for enum** (all uninitialized cold `.data`, the same init-bypass class
as the dispatch slots / deferred-write list — set by the bypassed bridge/PCI init, NOT a QEMU
bug): seed before driving `FUN_00367f54`:
- `*0xE0BDFC = 0` — PCI config **gate** (cold garbage `0x943c5669`; `FUN_000005a4` returns `-1`
  immediately if nonzero). Set by `FUN_0000019c` (config-mechanism registration).
- `*0xE0BDF8 = 1` — config **mechanism #1** (CONFIG_ADDRESS/DATA byte-reverse path). Also
  `FUN_0000019c`.
- `*0xE26978 = 0` — **device count** (cold garbage `0x01000000`; enum's `cmplwi r0,4; bgt skip`
  skips the whole loop while it's >4).

With the gate seeded, the raw config path + ISP1562 model work (proof #2). The enum's
*higher-level* helper (`FUN_00367340`/`FUN_00367f54`) then still dereferences an uninitialized
stack/struct pointer — int log shows `Invalid write at 0xEEEEEEEE` (the `0xee` kernelInit stack
fill used as a pointer). **That is the next layer of the same irreducible init-bypass cascade**
(see [[qemu-coldboot-ctor-allocator-keystone]]), not a device/byte-reverse problem.

### 2026-06-15 (cont.) — PCI config init traced to the real bridge-init; TWO concrete blockers

Traced the real PCI config bring-up (not the synthetic forced-entry path). `hw_seq_init`
(`FUN_0000dcb0`, runs in `usrInit`, pre-dispatch) reaches its config-mechanism registration
`FUN_0000019c` at `0xdd3c` — verified live: it is called **once** as
`FUN_0000019c(mech=1, CAR=0xB260010C, CDR=0xB2600110, 0)`. (An earlier "stuck at `0xdcc0`"
reading was itself a breakpoint-loop methodology artifact — single-stepping shows `hw_seq_init`
progresses linearly; the post-code print `FUN_0001c8bc`→`0x1b9b0`→UARTLite returns fine.)

**Blocker A — config gate never set to `-1` (registration silently no-ops).** `FUN_0000019c`
first reads `*0xE0BDFC` and **returns immediately unless it is `-1`** (`0x1ac cmpwi -1;
beq …; else blr`). Cold `.data` `*0xE0BDFC = 0x943c5669` (garbage, high-entropy — looks like it
sits in a crypto/OpenSSL blob; *no* code outside `FUN_0000019c` ever writes it, so on real HW an
earlier init step — likely an `XPci_CfgInitialize`/reset not yet found — must pre-set it to `-1`,
OR `software.bin` is a runtime snapshot whose pristine `-1` initializer was overwritten).
**Verified fix:** seed `*0xE0BDFC = 0xFFFFFFFF` at reset → `hw_seq_init`'s `FUN_0000019c`
registers cleanly: gate→`0`, mech→`1`, CAR stored `*0xE9C708=0xB260010C`, CDR `*0xE9C70C=
0xB2600110`, base `*0xE9C710=0`. Persists to the allocator wall. Candidate one-line boot fixup
in `r1mx_apply_boot_env_fixups`.

**Blocker B — the firmware's PCI config-cycle port is `0xB2600000`, but QEMU maps it at
`0xe1200000` (and puts I2C at `0xB2600000`).** The two XPci apertures and their endianness:
- **`0xB2600000`** = PCI **config-cycle port** — CAR `+0x10C`, CDR `+0x110`, **little-endian**
  (byte-reverse `stwbrx`/`lwbrx` via `FUN_00000118`/`FUN_0000010c`). Used by the enum config-read
  path (`FUN_000005a4`). The firmware uses `0xB260xxxx` for **nothing else** — only **2** `lis
  0xb260` exist in the whole image, both the CAR/CDR setup in `hw_seq_init`.
- **`0xe1200000`** = XPci bridge **IPIF / interrupt / control** registers — **big-endian**
  (plain `lwzx`/`stwx` via `FUN_000000dc`). Accessed 9× in the `0x33fxxx` PCI-interrupt module.

So the QEMU machine has them **crossed**: `PCI_CFG_BASE=0xe1200000` (where a raw probe coincidentally
reads the ISP1562 because the bridge model lives there) is actually the IPIF/IRQ block, and
`I2C_BASE=0xb2600000` is actually the config port (firmware never uses `0xB2600000` for I2C → the
I2C base is a misattribution). Net: the firmware's enum config cycles hit the **I2C model**, never
the ISP1562 (config read returns `r3=0`/unwritten `0xeeeeeeee`). **Fix:** put the XPci config-cycle
port (CAR/CDR + the ISP1562 enumeration responder) at **`0xB2600000`** and keep IPIF/IRQ at
`0xe1200000`; re-evaluate where (if anywhere) XIic actually lives. This touches the
`hw/ppc/r1mx_virtex4.c` `PCI_CFG_BASE`/`I2C_BASE` defines + `hw/pci-host/xilinx_opb_pci.c`, and
contradicts the prior "validated" memory-map rows — needs a deliberate device-model decision.

**Cascade after A+B fixed:** registration legitimate → config cycles reach the ISP1562 at
`0xB2600000` → enum builds the device table → device-ctx alloc `0x5652D0`. The enum's higher-level
helper may still need its input/output struct seeded (the `0xEEEEEEEE` deref) — the residual
init-bypass cascade. Next: either seed the enum's struct pointers, or run more of the real init.

### 2026-06-15 (cont.) — Blockers A+B IMPLEMENTED in QEMU + validated

Both fixes are in the `qemu-r1mx` working tree (`r1mx` branch), rebuilt, and verified:
- **Blocker A — gate seed.** `r1mx_apply_boot_env_fixups` (`hw/ppc/r1mx_virtex4.c`) now also
  writes `*0xE0BDFC = 0xFFFFFFFF` at reset (`PCI_CFG_GATE_ADDR`). **Verified:** the natural boot's
  `hw_seq_init → FUN_0000019c` then registers the config mechanism on its own — at the dispatch the
  gate reads `0`, mech `1`, CAR `*0xE9C708=0xB260010C`, CDR `*0xE9C70C=0xB2600110` (no manual seed).
- **Blocker B — config-port alias.** `hw/pci-host/xilinx_opb_pci.c` now aliases the bridge's
  register block at `XPCI_CFG_PORT_BASE = 0xB2600000` (`memory_region_init_alias` +
  `add_subregion`), and the `xps-iic` `create_unimplemented_device` at `0xB2600000` is removed
  (firmware never uses `0xB260xxxx` for I2C). **Verified:** byte-reverse config cycles at the
  firmware's real port (`mWriteReg(0xB260010C,…)`/`mReadReg(0xB2600110)`) return bridge dev0
  `0x000710ee`, **ISP1562 #1/#2 `0x156204CC`** (VID 0x04CC/DID 0x1562), empty dev3 `0xffffffff`.
- **Sub-word config access.** Relaxed the bridge region `.valid.min_access_size` 4→1 with
  `.impl=4` (the firmware reads config data at byte/halfword granularity, e.g. `lbz`/`lhz` at
  CDR±n); removed the `Invalid read at 0x112 size 1` rejections.

**Still blocked at the same boundary (not a device bug):** the firmware's own config-read wrapper
`FUN_000005a4` cannot be driven cleanly from the synthetic forced-PC context — single-stepping
shows it loop and at `0x630 (blr)` return to a garbage lr `0xeeeeeeec` (the `0xee` kernelInit stack
fill), because the fabricated frame/loop-state isn't a faithful natural-boot context. The raw
config path proves the device model is correct; faithful enum validation needs the natural boot to
*reach* the enum (the device-init cascade deep in usrRoot, past the allocator wall). NB also found
`0x124 = b 0x124` (self-loop stub) reached by the byte-read config helper `FUN_000000a8` — the
dword byte-reverse path (`0x10c`/`0x118`) is the working one. Next: drive the device-init cascade
(`FUN_00552BF4`→…→enum) with a more faithful context, or seed forward.

### 2026-06-16 — ROOT CAUSE of the config-read failure: the `r30=0` / `0x274` corruption (FIXED), enum scan PROVEN correct, blocker narrowed to the allocator

The "`FUN_000005a4` can't be driven / enum finds 0 devices" wall is **not** a synthetic-frame
problem with the config wrapper. Single-stepping `FUN_000005a4` revealed the real cause and the
device/scan path is now proven end-to-end.

**The corruption.** Single-stepping showed `FUN_000005a4` reaching `0x274` and executing
`0x7c632b02` — an **illegal** instruction that vectors to the Program/exception base `0x700`,
then garbage-runs and returns to `0xeeeeeeec`. But the *real* firmware byte at `0x274` is
`0x7c632b78` = **`or r3,r3,r5`** (valid; in `FUN_00000260`, the config-address builder, returning
cleanly via `0x278/0x27c`). **QEMU RAM at `0x274` had been clobbered** (low byte `0x78`→`0x02`).

**Who clobbers it.** A `Z2` write-watchpoint on `0x274` caught the writer: `stw r3,0x278(r9)` at
**`0x37c2ac`, inside usrRoot's own dispatcher block at `0x37c290`**, with `r30=0`, `r9 =
*(r30-0x3c20) = *0xffffc3e0 = 0xffffffff`, `r3 = 0x020390d0`. So the store target = `r9+0x278 =
0x277`, writing `r3`'s MSB `0x02` into `0x274`'s low byte. **Why `r30=0`:** the forced dispatch
enters usrRoot at the **resume label `0x37c440` (`b 0x37c290`)**, which skips the prologue
(`0x37bf78`) AND the body's `lis r30,0xea` (`0x37c14c`/`0x37c300`) that the `0x37c290` block
depends on. `0x37c034` is the **epilogue** (mid-function); the function spans `0x37bf78..0x37c45c`
with non-linear flow. **`0x37c440` is a resume/loop-back label, NOT the cold entry** — so the
harvested `TCB+0xC0 = 0x37c440` (cam-working-01) is the live root task's *saved PC mid-loop*, not
the cold-boot entry (which is the prologue `0x37bf78`). ⚠️ This corruption also happens in the
**natural QEMU boot** (the machine's dispatch fix forces the else-path → `0x37c440` → `r30=0`), so
the device enum could never have worked there until `r30` is fixed.

**The fix (proven).** Run to `0x37c290` and set `r30 = r26 = 0x00EA0000` (their real base; `r26`
is the same base, used at `0x37c210`/`0x37c2fc`). Then `*0xE9C3E0 = 0x0ff9bd30` (a valid task-stack
ptr), the `stw` lands on the stack, `0x274` stays `0x7c632b78`, and **the entire config/scan path
works** (`drive_enum.py`, `probe_cfg.py`):
- `FUN_000005a4(0,d,0,0)` → dev0 `0x000710ee` (bridge), **dev1/dev2 `0x156204CC`** (ISP1562
  VID 0x04CC/DID 0x1562), dev3 `0xffffffff`. Returns cleanly to the catch (no more `0xeeeeeeec`).
- `FUN_00000b3c(0x0C03A0,0)` → **found, bus0/dev1/fn0**.
- `FUN_00367340(0xc,3,0xa0,0,…)` → **ret 1**, p5=bus0 p6=dev1 p7=fn0 (works with r30=`0xEA0000`
  *and* the enum's own `0xE20000`; these low funcs address globals via absolute `lis r9,0xe1`,
  not r30, so the device match is r30-independent).

**The device modelling + firmware PCI enumeration logic are therefore correct end-to-end.**

**Remaining (new) blocker — the allocator, not the device layer.** `FUN_00367f54` mallocs one
`0x24` descriptor per matched device via `FUN_0045b974`. Single-stepping the enum: the first
`FUN_00367340` returns 1 (found), then it dies at **`bl 0x45b974`** (step 34). The **hand-built**
allocator (`build_allocator.py`, which bypasses the real init `FUN_0045acac` + object/class system)
services only the **first** malloc — `FUN_0045b974(0x54)` returns a good pool ptr `0x08d8fbb8`, but
every **subsequent** `FUN_0045b974` returns garbage (`0x7c9c43a6`) or `0`. So the enum cannot
allocate its descriptors. This is the known hand-built-allocator fragility (Path-B caveat), a
synthetic-context artifact — **not** a device/config/byte-reverse bug.

**Net / next.** The "faithful enum" is now gated by exactly two characterised items, both
upstream of the device layer (which is done):
1. **Dispatch `r30`/`0x274` corruption** — RESOLVED via the true-entry path (below).
2. **Repeated-malloc-capable allocator** — either run the real allocator init (natural cascade /
   the object-class path `FUN_0045acac`), or extend `build_allocator.py` so the partition's free
   tree survives multiple allocations (investigate the partition lock `semTake`/free-tree update).

### 2026-06-16 (cont.) — Item #1 RESOLVED: enter usrRoot at the TRUE entry 0x37bf78 (faithful, no 0x274 corruption)

`0x37bf78` (not `0x37c440`) is usrRoot's real cold entry, and reaching the device init through it
needs **no register injection** — the prologue sets `r30` itself. Verified flow (`drive_enum.py`
`reach_wall_clean`, all with `0x274` staying `0x7c632b78`):

usrRoot is a **per-call state machine gated by `*0xE2706C`** (cold `0x005170c8`):
- **Call #1** (flag != 0): prologue (`bl 0x37d87c` = deferred-write walker, seeded empty) → the
  init branch `0x37c060` (calls `0x5bb134`/`0x36c134`/`0x37bb14`), which **clears `*0xE2706C = 0`**
  and returns via the epilogue `0x37c034`. (Returned cleanly to the catch with lr we set.)
- **Call #2** (flag == 0): falls through the main body → `lis r30,0xea` (`0x37c14c`) → dispatcher
  `0x37c290` **with r30 = `0x00EA0000`** (so the `stw r3,0x278(r9)` lands on the task stack, NOT
  `0x274`) → module init → **device-ctx alloc wall `0x555488`**, `lr = 0x00552f1c` (a genuine
  module-init return address — a faithful call chain, not a fabricated frame).

Replay: at the dispatch (`0x371cd0`) seed the deferred-write list, run to `0x37c440` to capture the
task's spawn-arg register context (`r3=0x020390d0`, `r6=r7=r8=0`, sp), then call usrRoot at
`0x37bf78` twice from that context (`lr=catch`). Call #2 reaches `0x555488` with `0x274` intact.
From there: `build_allocator.build`, then `FUN_00367340(0xc,3,0xa0,0)` → ret 1 (bus0/dev1) and the
enum runs until the descriptor malloc (item #2). **This is the faithful device-init path.**

**Emulator implication (for qemu-r1mx):** the current dispatch fix forces the else-path → the
root task starts at `TCB+0xC0 = 0x37c440` (the loop-back resume), which on a cold boot enters the
dispatcher with `r30=0` and corrupts `0x274`. The faithful fix is to dispatch the root task to its
**true entry `0x37bf78`** instead (so the prologue runs and `r30` is set every iteration). The
firmware itself stored `0x37c440` in `TCB+0xC0`; that is the live camera's *resume PC mid-loop*,
not the cold entry — so this likely means either taskInit's stored entry needs overriding to
`0x37bf78`, or `0x37c440` should be patched to set `r30` before `b 0x37c290`. (Owner decision:
how to land it — the two-call state machine means the natural re-invocation of usrRoot must also
work, which depends on the surrounding scheduler loop.)

Tooling: `firmware/scripts/drive_enum.py` (canonical enum harness, applies the r30 fix + documents
all of the above), `firmware/scripts/probe_cfg.py` (config-primitive tester). Key new addresses:
`0x37c290` (dispatcher block; set r30/r26=`0xEA0000` here), `0x37bf78` (true usrRoot prologue),
`0x37c034` (usrRoot epilogue), `0x274` (`or r3,r3,r5` config-addr builder, corruption canary),
`0xE9C3E0` (`= 0xEA0000-0x3c20`, the dispatcher's struct ptr).

### 2026-06-17 — Item #2 RESOLVED: repeated-malloc root cause = guard-zone global `*0xE295E4`; faithful enum now COMPLETES

The "hand-built allocator services only the first malloc" symptom was **not** a hand-build
limitation or a `semTake`/free-tree-without-scheduler problem. Root cause (found via
`firmware/scripts/probe_geom.py`): the memPartLib per-allocation **guard/red-zone size global
`iRam00e295e4` (`0xE295E4`)** was uninitialized cold garbage `0x00d8fad0` (~14 MB). Nothing in the
allocator init writes it — it is a read-only config const set by the bypassed early data init.
Consequences, all confirmed in the post-`addToPool` geometry:
- `addToPool` (`FUN_0045a74c`) reserved ~14 MB of red-zone at the pool front → the single free
  block started at `0x08d8fba8` (not `0x08000008`), size only `0x01750e98` (~24 MB).
- The carve overhead `uVar8 = e295e4 + … ≈ 0xd8faf0`; the split test in `FUN_0045a428`
  (`if (uVar4 < uVar3 + uVar8)`) compared ~24 MB available against ~28 MB needed → **true** → the
  no-split "allocate whole block" branch fired, so the remainder was never reinserted and the free
  tree emptied (`+0x40` `0x08000008` → `0`). Exactly **one** malloc was ever serviceable; the next
  ran on an empty tree and corrupted the partition struct.

**Fix (one line, in `build_allocator.py`):** seed `*0xE295E4 = 0` (guards off — the production
default) alongside the existing `*0xE295D4`/`*0xE295F4` seeds. Verified: 6/6 sequential mallocs now
return contiguous in-pool addresses, the free tree stays stable (`+0x40 = 0x08000008`, one big free
block remaining), `+0x4c` node count steady at 7.

**Faithful enum now completes** (`drive_enum.py`, canonical run): `FUN_00367f54` runs to a **clean
return** (`stop = lr = 0xC`), matches **both** modelled USB controllers (OHCI `0x0C03A0` dev1 and
EHCI `0x0C0320` dev2 — both `FUN_00367340` queries return 1), and **allocates a descriptor for each**
(`desc[0]=0x08000150` OHCI, `desc[1]=0x08000188` EHCI, in `0x10cf458[]`). The device model + config
scan + allocator + enumerator are now PROVEN correct end-to-end.

**Notes / residual.** (a) The real allocator init `FUN_0045acac` is **not** usable from this context
— it hangs in `FUN_00442e48` (object registration, `0x69`), which needs the object/class system /
a scheduler; the seeded hand-build is the faithful-enough path. (b) The enum's OHCI loop counter
`uRam00e26978` ends at 1 while both descriptors are allocated; the EHCI (loop-2) post-alloc init
is investigated in the next section (NOT a device-model gap, as first assumed). Tooling added:
`firmware/scripts/probe_malloc.py` (sequential-malloc tester, `--mode hand|real`),
`firmware/scripts/probe_geom.py` (pool/tree geometry dump).

### 2026-06-17 — Dispatch + allocator fixes LANDED in qemu-r1mx; natural boot reaches the device-init wall faithfully

Both fixes are now in the machine (`hw/ppc/r1mx_virtex4.c`, `r1mx_apply_boot_env_fixups`, fixups
#6/#7) so the NATURAL boot benefits — no manual seeding:
- **#6 usrRoot true-entry redirect.** usrInit calls `kernelInit(rootRtn=0x37C440, …)` (`main_boot_init`
  0x36C350); `0x37C440` is a mid-function RESUME label (`b 0x37c290`) that assumes `r30=0xEA0000`.
  With the else-path forced, the root task dispatched straight there with `r30=0` → the `0x37c290`
  block (`lwz r9,-0x3c20(r30); stw r3,0x278(r9)`) wrote through `*0xFFFFC3E0` and clobbered `0x274`.
  Fix: patch the immediate built at `0x36C414` `addi r3,r3,-0x3bc0` (0x37C440) → `addi r3,r3,-0x4088`
  (**0x37BF78**, usrRoot's true prologue, which sets `r30` itself), guarded on the original bytes
  `38 63 c4 40`. Companions (cold-`.data` garbage the bypassed early init would set): `*0xE2706C = 0`
  (usrRoot's per-call state flag — cold garbage `0x005170c8`; seed 0 so the true entry falls straight
  through the main body in ONE pass and sets `r30`) and the deferred-write list `0xE9C5C0/0xE9C5C4`
  → self (empty ring, needed by the prologue's walker `0x37d87c`).
- **#7 allocator guard-zone** `*0xE295E4 = 0` (see prior section).

**VERIFIED (clean boot, machine fixups only, no manual seeds):** dispatch `0x371cd0` → usrRoot TRUE
ENTRY `0x37bf78` → dispatcher `0x37c290` with **r30 = 0xEA0000** → **device-init wall `0x555488`**,
with `0x274` staying `0x7c632b78` THROUGHOUT (silent PCI-config corruption eliminated). From the
natural wall the allocator builds and services unlimited mallocs (5/5 contiguous). The free-run boot
then meets the broader init-bypass cascade (the `0x700` "walls" seen earlier are **false positives** —
physical `0x100–0x700` is normal low-address code, the documented harness gotcha — not exceptions).
`build_allocator.py` standalone now matches this machine path (`run_to 0x371cd0` → `0x555488`).

### 2026-06-17 — EHCI loop-2 post-alloc init: NOT a device-model gap (investigated)

Driving the now-complete enum through loop 2 (EHCI, class `0x0C0320`): it MATCHES dev2, mallocs the
`0x24` descriptor, enables it (`cmd|=Mem|BusMaster`), reads BAR0 — then calls the descriptor's first
method (`descriptor[0]`, built as the literal **`0x377C24`** by `lis r9,0x37; addi r9,r9,0x7c24` at
`0x368150`; called via `bctrl` at `0x3681D4` with arg `*(slot[5]+8)`, `slot[5]` relocated by
`FUN_00367bec`+`FUN_0036777c`). **`0x377C24` is a mid-function soft-float continuation** (no `stwu`
prologue; uses `0x375800`/`0x375714` = 64-bit mul/shift helpers; sign-flips via `xoris 0x8000`) with
**non-standard linkage**: its epilogue (`lwz r0,0(r1); mtlr r0; addi r1,r1,44; lmw r28,0(r1);
addi r1,r1,20; blr`) restores `lr` from a caller-prepared `0(r1)` slot, NOT a saved `lr`. Under a
forced/synthetic task frame `0(r1)` holds the stale back-chain, so the method returns there (verified:
`0(r1)=0x0ff9bc58`/`0`) instead of back into loop 2 → the enum stops with `count=1` and dev2's
descriptor allocated-but-un-incremented (benign; clean return to catch).

**Conclusion:** the EHCI BIOS→OS handoff (the `(>>8)&0xff > 0x40` branch — whose poll `FUN_0036744C`
is a **PCI-CONFIG read at the EECP offset**, handled by the bridge model, NOT an EHCI-MMIO access) is
**never reached** in any drivable context. So there is **no EHCI register model to implement**: dev2's
`BAR0`-reads-0 is sufficient, and the `count` 1-vs-2 difference is a **task-frame-fidelity artifact**
(same class as the broader init-bypass cascade), not a device-model gap. The model comment in
`hw/pci-host/xilinx_opb_pci.c` records this and notes the *only* future device-model need (a USBLEGSUP
extended capability in dev2 config at the EECP offset) is intentionally deferred — nothing exercises it.

### 2026-06-19 — Natural free-run boot characterised: device-init runs BEFORE its module-init (the alloc fn-ptr is NULL); keystone fn-ptrs proven to be mid-function r27-context handlers

Resumed with the landed machine fixups (#6 usrRoot true-entry, #7 guard-zone). Findings, all
fresh-verified against the running `r1mx-virtex4` (no manual seeds beyond what's noted):

- **The natural free-run boot fault-loops in the low PCI-config code** (`0x700`/`0x658`/`0x608`
  region) with `r1` climbing ~1.5 MB/sample — a repeated `bctrl` through a NULL/garbage fn-ptr
  that jumps to address 0 and garbage-runs the low code (the low `0x100–0x700` are normal
  EVPR-relocated code, the documented harness gotcha — NOT exception vectors).
- **Root cause = the device-context alloc fn-ptr `*0xE9C34C` is NULL at the device-init wall.**
  The natural boot reaches the wall `FUN_00555488` (`lr=0x552f1c`, clean task frame, `0x274`
  intact) with `*0xE9C34C = 0` and the alloc object `*0xE295C4 = 0xd8fa64` (cold garbage). The
  wall does `mtctr *0xE9C34C; bctrl` with only `r3 = param` → `bctrl 0` → the fault loop.
- **Why NULL: the fn-ptr setter never runs (out-of-order init).** `*0xE9C34C` is set to
  `0x5652D0` by `FUN_005555EC`, which is called **only** from `FUN_00552BF4`'s init body
  (`bl 0x5555ec` @ `0x552c4c`). `FUN_00552BF4` (caller `0x35a9fc`, inside `FUN_0035980c`, called
  from the `0xf7ea4`/`0xf913c` early-init region) is a once-init gated on counter `*0xE3A5E4`
  (`++; if !=1 skip body`). At the wall the counter is still its cold `.data` garbage `0xdaaeac`
  → **`FUN_00552BF4`'s prologue never executed** → fn-ptr never set. Yet the device-init that
  *consumes* it — `FUN_00552E88` (a SEPARATE function, `0x552e88..0x553088`; caller `0x3595c4`
  inside `FUN_0035905c`, which has **no static callers** = pointer-called via a driver-dispatch
  table reached from usrRoot's `FUN_0036c134` @ `0x37c36c`) — DOES run and reaches the alloc.
  So the **driver-method dispatch fires before its module-init prerequisite** — the documented
  "init runs inside the dispatched task, the dispatch isn't faithful" circular bootstrap, now
  pinned to a specific fn-ptr/once-guard pair. (NB: do NOT seed `*0xE3A5E4=0` — `FUN_00552E88`
  *also* reads it and early-returns `-1` when it's 0; the two functions share the counter with
  opposite polarity. Seeding it broke the boot in testing.)
- **Seeding the fn-ptr alone does NOT advance the boot — the keystone is real.** With
  `*0xE9C34C=0x5652D0` seeded, the wall `bctrl`s into `0x5652D0` which runs ~9 insns then calls
  NULL (the same fault loop), because `0x5652D0` is **mid-function** in `FUN_005651E8` and reads
  `r28`=0 / an empty device table (`*0xE3A630` count=0, `*0xE3A624` base). The real entry
  `0x5651E8` sets `r27`/`r28` from the device table itself (`r9=*0xE3A630 count; if count<=idx
  return -7; else r27=*(*0xE3A624 + idx*4); r28=param_2`). **Confirmed all four harvested
  fn-ptrs (`0x5652D0` alloc, `0x565518` free, plus the alternate-setter values `0x565458`/
  `0x565568` written by the func @ `0x555590`) are mid-function r27-context handlers** (each
  opens with `lwz …,(r27)` with no prologue) — they are vtable-style methods invoked from a
  context where `r27`=device-entry and `r28`=descriptor are already valid, NOT standalone
  entries. This concretely explains the keystone's long-open "0x5652D0 needs r27/r28 established
  by the caller chain": that chain is a populated device table (built by the PCI enum, which
  needs the general allocator) + the dispatcher in `FUN_005651E8` — none of which the natural
  dispatch builds. **The harness (`build_allocator.py`+`drive_enum.py`) proves every piece works
  when orchestrated from the wall context; the gap is purely orchestration/ordering.**

**Decision surfaced to owner (unchanged A/B/C, now sharper):** the realistic forward options are
(A) crack the circular dispatch so the natural init runs `FUN_00552BF4`/the PCI-enum lazy-init
*before* the driver-dispatch reaches `FUN_00552E88` (deep — needs the real driver-init ordering,
likely the `0xf7xxx` init region run pre-dispatch); (B) bake the proven harness orchestration
(build allocator → run `FUN_00367f54` to populate the device table → set fn-ptrs) into a
machine-side boot fixup so the natural boot's device-ctx alloc finds a real table — the only
option that yields visible boot progress, but it must also satisfy the `FUN_005651E8` r27/r28
context (still open); (C) accept the validated device-modelling as the ceiling.

### 2026-06-19 (cont.) — Option B attempted: allocator+enum orchestration works, the firmware device-table builder does NOT

Owner chose **Option B (machine-side orchestration)**. Built `firmware/scripts/boot_orchestrate.py`
to drive the proven pieces in order at the device-init wall, then drive the firmware's own
device-table builder so the natural boot's device-ctx alloc finds a populated table. Result:

- **Stages 1–2 work end-to-end from the natural wall context** (no scheduler needed):
  `build_allocator` → general malloc returns real in-pool memory; `FUN_00367f54` (bounded at the
  EHCI loop-2 divert `0x3681D4`) matches **both** USB controllers and allocates a `0x24`
  descriptor for each (`0x10cf458[0]=0x08000150`, `[1]=0x08000188`, count=1). Proven again.
- **Stage 3 — the firmware's device-table builder `FUN_00563B58` DIVERGES** into the keystone
  fault loop (PC bounces `0x700`/`0x36fd38` = the low EVPR-relocated config code reached by a
  `bctrl`-to-0), **whether the alloc fn-ptr `*0xE9C34C` is the mid-function handler `0x5652D0`
  or the true entry `0x5651E8`** (the latter got one clean-return sample but still mostly looped).
  Cause: `FUN_00563B58` builds the table (`*0xE3A624`/`*0xE3A630`) by calling the device-ctx
  alloc (`FUN_005552A4` → `*0xE9C34C`, a thin pass-through wrapper) and the per-device 84 KB
  context builder `FUN_00560544` + device-specific init (`0x5ab360`/`0x5ac50c`) — all of which
  need the running VxWorks scheduler + object/class system (the same dependency that hangs the
  real allocator init `FUN_0045acac` in `FUN_00442e48` object-registration). The device-ctx alloc
  `0x5651E8` indexes an as-yet-empty table (count=0 ⇒ −7 / faults) — the table-build and the
  alloc are mutually dependent and only resolvable by a live scheduler.

**Conclusion:** driving the firmware's *real* device-init from a synthetic forced-call frame is
**blocked at the device-table layer** (the documented irreducible circular bootstrap, now pinned
to `FUN_00563B58`). The validated, schedulerless pieces (general allocator, PCI config scan +
ISP1562, enum + descriptor alloc) are the ceiling of what a forced-call harness can build. The
only remaining Option-B avenue is to **fully hand-fabricate** the device table + the 84 KB
per-device contexts in RAM (reverse-engineer every field the boot reads from `iRam00E3A624[]`)
and seed them as machine fixups — large, fragile, low-confidence; not attempted. Tooling:
`firmware/scripts/boot_orchestrate.py` (stages 1–2 reusable; stage-3 divergence documented).

## Map of the authentic boot path (verified)

Normal boot dispatches the root task into an **OpenSSL X.509 artifact** at `0x381A8C`
(forced by patches #53a/c; not the real boot — see §0.3). To exercise the *real* path we
force `PC = usrRoot (0x37C440)` after booting to `0x381A8C`, keeping the live task stack.
`usrRoot` then runs and diverges in sequence:

| # | Where | What it needs | Cold-boot truth | Seed that advanced it |
|---|-------|---------------|-----------------|------------------------|
| 1 | `FUN_0037D87C` spins @`0x37D8B0` | a deferred-write list @ head `0xE9C5C0` (nodes `{addr+0xc, val+0x10, flags+0x1c}`; walk *writes val→addr*) | empty self-referential circular list | `*0xE9C5C0=*0xE9C5C4=0xE9C5C0` ✓ |
| 2 | `0x700` from `FUN_00555488` | alloc fn-ptr `*0xE9C34C` (NULL → `bctrl 0`) | set to `0x5652D0` by `FUN_005555EC` | `*0xE9C34C=0x5652D0`, `*0xE9C648=0x565518` (gets *past* zalloc) |
| 3 | `0x700` inside the allocator `0x5652D0` | a valid **context** in `r27`/`r28` | established by the real caller chain | **OPEN — this is the keystone** |

Seeds #1/#2 live in `firmware/scripts/seed_boot.py` (the iterative harness).

---

## The keystone open question (= the plan for "#1")

**The allocator fn-ptr `*0xE9C34C` = `0x5652D0`. Calling it in isolation returns `-7`.**
Verified facts (and only these — see Retractions):

- `0x5652D0` is **mid-function** (no prologue) inside `FUN_005651E8` (real entry `0x5651E8`).
  It reads `r28`/`r27` as a pre-set context (`lbz r12,9(r28)`; `lwzx r3,r27,0x14bf4`) and
  returns `-7` when `r28->[9]` isn't 1/3.
- The wrappers `FUN_005552A4` and `FUN_00555488` both just `lwz`+`bctrl` `*0xE9C34C`; they do
  **not** set `r27`/`r28`.
- `r27`/`r28` are **ordinary callee-saved registers** (0 at root-task dispatch, then take
  stack values) — NOT reserved globals. So `0x5652D0` is reachable legitimately only via a
  caller chain that establishes `r27`/`r28` first.

**PLAN (resume here), low-risk static-first:**

1. **Read `FUN_005651E8`'s prologue (`0x5651E8`)** — how does it derive `r27`/`r28` from its
   params (`param_1`, `param_2`)? That defines the "context" the allocator needs. (Pull it
   clean if needed: `ghidra_decompile_addrs.py 0x5651e8` — it's already in the corpus as the
   18 KB merged function; disassemble `0x5651E8..0x5652D0` directly to see the reg setup.)
2. **Find who calls `0x5652D0` legitimately** with a valid context. Static: `callgraph.py`
   has no `bl` to it (it's pointer-called via `0xE9C34C`); so trace the callers of
   `FUN_00555488`/`FUN_005552A4` and see what sets `r27`/`r28` before them. Empirical option:
   breakpoint `0x5652D0` and run a path that legitimately allocates, capture `r27`/`r28`.
3. Once the context object is known, decide: seed it (if it's a small static structure) or
   accept that it chains into the device layer (then this confirms Path C).
4. Re-run `seed_boot.py` with the new seed; observe the next divergence.

---

## Retractions — do NOT repeat these (all empirically refuted this session)

- ❌ "the allocator is a memory partition / free-list" — it isn't.
- ❌ "it builds a 16 M-entry / 1.4 TB device table" — that read the `.data` value
  `*(0xE26978)=0x01000000` (which sits in a `0x10101010` fill region) literally. It is a
  fill/padding value the cold-boot enumeration would overwrite with a real device count, not a table size.
- ❌ "`r27`/`r28` are reserved global registers" — refuted: they're callee-saved locals.
- The "device/channel-context manager" reading (`FUN_005651E8` indexes `iRam00E3A624[idx]`,
  84 KB contexts via `FUN_00560544`/descriptor table `0x10CF458`) is **plausible but not
  load-bearing** for the keystone; treat as a hint, re-verify before relying on it.

---

## Key addresses (so future sessions don't re-derive)

| Addr | Meaning |
|------|---------|
| `0x37C440` | `usrRoot` (rootRtn; `b 0x37C290`; NOT a Ghidra function) |
| `0x381A8C` | artifact dispatch entry (force `usrRoot` here, keep stack) |
| `0xE9C5C0` | deferred-write list head (#1); seed self-referential |
| `FUN_0037D87C` | the list walker that spins |
| `0xE9C34C` / `0xE9C648` | alloc / free fn-ptrs → `0x5652D0` / `0x565518` |
| `0x5652D0` | alloc entry (mid-`FUN_005651E8`@`0x5651E8`); needs `r27`/`r28`; returns `-7` cold |
| `FUN_00555488`, `FUN_005552A4` | call `*0xE9C34C` |
| `FUN_005555EC` | sets the fn-ptrs (guard `*0xE3A600`, was 0) |
| `FUN_00552BF4` | once-guarded module init (guard `*0xE3A5E4`=`0xDAAEAC` non-cold) |
| `FUN_00563B58` | builds device table: base `0xE3A624`, count `0xE3A630`; per-entry `FUN_00560544` (84 KB `0x14C48`, descriptors `0x10CF458`) |
| `0xE26978` | table-entry count source (`0x01000000` = fill-region garbage; cold boot sets the real count) |
| `~0x35A964` | init dispatcher region: `bl FUN_00552BF4`@`0x35A9FC`, `bl FUN_00563B58`@`0x35AA28` (NOT a Ghidra function) |

---

## Tooling delivered this session (durable, reusable)

- **`firmware/scripts/callgraph.py`** — complete PPC call graph from the binary (Ghidra's
  corpus is incomplete). `--callers/--func/--climb/--dump-entries/--stats`. Caveat: false
  `bl` edges in data; verify hops by disassembly.
- **`firmware/scripts/ghidra_decompile_addrs.py`** — pull any function Ghidra has but the
  corpus lacks, on demand (Ghidra's DB has ~12.3 k fns; corpus had 10.5 k). **No
  `analyzeHeadless` needed** — use pyghidra in `.venv`:
  `GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC .venv/bin/python firmware/scripts/ghidra_decompile_addrs.py 0x<addr> …`
- **`firmware/scripts/seed_boot.py`** — the iterative force-`usrRoot` + seed harness.
- **`firmware/scripts/probe_usrroot.py`** — force `usrRoot`, trace to first divergence.
- **`rsp.py`** — `write_reg` now uses a `G` read-modify-write (PC writes work; the old
  `P{word-index}` silently hit the wrong reg — pc is gdb regnum 64, word-index 32).
- **`qemu_boot.sh --background` / `--stop`** — daemonized headless QEMU for scripted runs
  (detached chardevs + own pidfile). NB: never `pkill -f qemu` (matches the launcher's own
  cmdline → kills the caller); use `pkill -x qemu-system-ppc`.

## Reproduce the current frontier

```bash
./firmware/scripts/qemu_boot.sh --patched --debug --background   # stub :1234, daemonized
cd firmware/scripts && python3 seed_boot.py                       # forces usrRoot, applies seeds, traces
cd .. && ./firmware/scripts/qemu_boot.sh --stop
```
