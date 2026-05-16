# Build 32 Reverse Engineering — Implementation Plan

## Problem Statement

The RED ONE MX Build 32 (v32.0.3, software.bin, 15.25 MB, PPC405 BE) has been decrypted and
loaded into QEMU. The goal is to boot to VxWorks `kernelInit` (0x5a7f30) and then reach the
WDB agent at 192.168.0.2:17185.

Strategy: decompile first, patch second.

---

## Current State (session 20)

- **54 patches** in firmware/scripts/patch_firmware.py (committed to `reverse-build-32`)
- Boot progress (fully confirmed):
  - fn_36e168 completes — VxWorks exception handlers installed ✓
  - fn_DCB0 completes — hardware sequencer runs ✓
  - fn_458a14(r3=0/1) returns 0 (Patch #44) ✓
  - fn_36860c completes — conditional task spawns skipped at cold boot ✓
  - usrInit fully completes — UART output `^^^123456789\r\n` seen TWICE ✓
  - kernelInit(0x5a7f30) called — VxWorks multitasking started ✓
  - Root task TCB 0x0ff9bd30 created and dispatched ✓
  - Root task running in 60ms polling loop (fn_382bec / fn_3801cc) ✓
  - **No crashes or infinite loops observed**

**ROOT TASK is alive** — but descriptor at 0x020390d0 is all-zeros, so fn_382e80
dispatches nothing and the task idles.

---

## Key Addresses

usrInit layout (0x36c350):
  0x36c3cc: bl fn_36e3dc         <- pre-init
  0x36c3d0: bl fn_36e168         <- VxWorks exc handler install
  0x36c3d4: bl fn_DCB0           <- hardware sequencer
  0x36c3d8: li r3, 0
  0x36c3dc: bl fn_458a14 (r3=0)  <- driver dispatch (Patch #44)
  0x36c3e0: li r3, 1
  0x36c3e4: bl fn_458a14 (r3=1)  <- driver dispatch (Patch #44)
  0x36c3ec: bl fn_36860c         <- conditional task spawns (all skipped)
  0x36c3f0: bl fn_0000d8a0       <- timer/clock helper
  0x36c424: bl 0x5a7f30          <- kernelInit MILESTONE ✓ PASSED

Root task dispatch chain:
  TCB = 0x0ff9bd30
  ctx+0x8c (PC) = 0x381a8c  (fn_381a8c prologue - Patch #53a)
  fn_381a8c → fn_381a38 → fn_381824 → fn_382e80 (main dispatcher)
  fn_382e80 → fn_382bec → fn_3801cc(r3=60) [60ms sleep] → loops

---

## IMMEDIATE NEXT STEPS

### Step 1: Understand the root task descriptor format

The root task context descriptor at 0x020390d0 is all-zeros. With no `__L` tokens,
fn_382e80 has no commands to dispatch, so no VxWorks services are initialized.

Options:
1. **Search for writes to 0x020390d0**: Use GDB write-watchpoint `Z2,20390d0,4` to
   catch any runtime write. If nothing writes, the descriptor is meant to be populated
   by the boot path before kernelInit.
2. **Disassemble fn_382e80 body**: Find the message-queue wait/read call. Identify
   if it's `msgQReceive` or `semTake`. If messages must arrive from another task,
   trace what task sends them.
3. **Search firmware for `__L` patterns**: `strings software.bin | grep '__L'` to find
   candidate command strings. One of these may be the correct initial descriptor.

### Step 2: Find WDB agent initialization

The WDB target agent is started by `usrWdbInit()`. Search for it:
- `strings software.bin | grep -i wdb` — look for "wdb", "WDB", "tWdbTask"
- Look for UDP port 17185 (0x4321): `grep -a $'\x43\x21' software.bin | od -A x -t x1z`
- Cross-reference to find the function that calls socket()/bind()/recvfrom()

### Step 3: Connect via WDB once reachable

Once tWdbTask is started:
- Add tuntap networking to QEMU launch
- Connect: `wdbrpc 192.168.0.2 17185`
- Via WDB: `lkup "DEBUG.USB.CONNECTION"` → write 1 to BSS addr

---

## Constraints

- SW BPs (Z0) only — QEMU PPC405 HW BPs broken
- Write watchpoints (Z2/Z4) DO work on QEMU PPC405
- NEVER place SW BPs inside a function that will run at full speed
- QEMU launch: use `setsid ./qemu-system-ppc ... > /tmp/qemu-r1mx.log 2>&1 &`
- SPR encoding: spr = ((w >> 11) & 0x1f) << 5 | ((w >> 16) & 0x1f)
- GDB RSP: send `$c#63`, do NOT recv — let wait_bp() drain
- Clear ALL stale BPs at start of each session (use z0,addr,4 for known-used addresses)


- **44 patches** in firmware/scripts/patch_firmware.py
  - sha256: `b2a63a78d7606a0cb75486cbc03038e08f0f0470b43e8a270c4c325611bc8d8c`
- Boot progress (confirmed with single-step tracing):
  - fn_36e168 completes — VxWorks exception handlers installed
  - fn_DCB0 completes — hardware sequencer runs to completion
  - fn_458a14(r3=0) returns 0 ✓
  - fn_458a14(r3=1) returns 0 ✓
  - fn_36860c has been entered — not yet confirmed to complete
- **Current blocker**: fn_36860c (0x36860c) — needs run-time test to confirm it passes;
  if it stalls, need to disassemble the 8 sub-functions for MMIO poll loops.

**CRITICAL lesson learned (session 8):** Never place SW BPs inside a function you then run at
full speed. QEMU's SW BP trap instruction fires into VxWorks's exception vector table.
Before kernelInit the handlers at 0x100-0xd00 are the binary's raw (garbage) code, causing
instant crashes. Exception vectors are only properly installed by fn_36e168 (at usrInit step 2).
The safe pattern is BPs at call/return boundaries ONLY (never inside a function being called
at speed).

---

## Key Addresses

usrInit layout (0x36c350):
  0x36c3cc: bl fn_36e3dc         <- pre-init
  0x36c3d0: bl fn_36e168         <- VxWorks exc handler install
  0x36c3d4: bl fn_DCB0           <- hardware sequencer
  0x36c3d8: li r3, 0
  0x36c3dc: bl fn_458a14 (r3=0)  <- driver dispatch (PATCHED: Patch #44 → returns 0)
  0x36c3e0: li r3, 1
  0x36c3e4: bl fn_458a14 (r3=1)  <- driver dispatch (same patch, returns 0)
  0x36c3e8: addis r29,r0,0xea    <- return value ignored
  0x36c3ec: bl fn_36860c         <- CURRENT TARGET (entered; unknown if it completes)
  0x36c3f0: bl fn_0000d8a0       <- timer/clock helper
  ...
  0x36c424: bl 0x5a7f30          <- kernelInit MILESTONE
  0x36c43c: blr

Key functions:
  0x00458A14  fn_458a14    Driver dispatch; PATCHED (Patch #44: bctrl → li r3,0)
  0x0036860C  fn_36860c    CURRENT TARGET; 8 sub-calls; likely VxWorks memory pool init
  0x005A7F30  kernelInit   VxWorks kernel init MILESTONE

---

## fn_36860c — Known Structure

fn_36860c (entry 0x36860c, returns at 0x368d0, 16-byte frame) makes 8 sub-calls:
  0x36860c: mfspr r0,LR / stwu r1,-16(r1)   [standard prologue]
  0x368650: bl 0x445434
  0x368654: bl 0x5acc58
  0x368658: bl 0x43c4fc
  0x36865c: bl 0x448520
  0x36867c: bl 0x5b0a84   (called with r3=8192, r4-r9=4096 each — large memory pool?)
  0x3686b8: bl 0x498cd8
  0x3686c0: bl 0x5b75e8   (called with r3=512)
  0x3686d0: blr           [end of function]

None of the calls have obvious MMIO patterns in their call-site setup code. Most likely this is
VxWorks memory pool / cache init. Probably completes without stalling.

---

## dispatch table: fn_458a14 runtime detail

*(0xe29310) at runtime = 0x0037cd4c  (set by init code at 0x36cc64-0x36cc68)
*(0xe29314) at runtime = 0x0037ce78  (entry 1)
Static binary values are stale: 0x548d78 / 0x5489f8 — overwritten before fn_458a14 is called.
fn_37cd4c is the epilogue of fn_37cc94 (40-byte frame) — calling it from fn_458a14's 16-byte
frame causes a stack frame size mismatch crash. Patch #44 bypasses this entirely.

---

## IMMEDIATE NEXT STEPS

### Step 1: Confirm fn_36860c passes (or identify blocker)

Run with BPs ONLY at call/return boundaries — NOT inside any function:
  - BP at 0x36c3f0 (fn_36860c returns)
  - BP at 0x36c424 (kernelInit)

If 0x36c3f0 fires → fn_36860c completed. Move to Step 3.
If neither fires within 120s → fn_36860c is stalling. Move to Step 2.

```python
# Clean BP pattern (NEVER put BPs inside fn_36860c's sub-functions):
bps = {0x36c3f0: "fn_36860c returned", 0x36c424: "kernelInit"}
```

### Step 2: If fn_36860c stalls — trace sub-calls

Single-step through fn_36860c's 8 bl sites to find which sub-call doesn't return.
Then disassemble that sub-function for MMIO poll loops (look for `lwz; cmpw; bne`
with MMIO base in 0x40xxxxxx range) and add a NOP patch.

### Step 3: After fn_36860c — reach kernelInit

Run with BP at 0x36c424. The gap (0x36c3f0–0x36c424) includes fn_0000d8a0 and
other helpers. If any stall, trace and patch.

### Step 4: kernelInit → WDB

Once 0x36c424 fires:
  - Add tuntap networking to QEMU launch
  - Connect: wdbrpc 192.168.0.2 17185
  - Via WDB: lkup "DEBUG.USB.CONNECTION" → write 1 to BSS addr

---

## Constraints

- SW BPs (Z0) only — QEMU PPC405 HW BPs broken
- Write watchpoints (Z2/Z4) DO work on QEMU PPC405
- NEVER place SW BPs inside a function that will run at full speed — exception vector
  table (0x100-0xd00) contains garbage code before fn_36e168 runs at 0x36c3d0;
  after fn_36e168 runs, VxWorks handlers are installed but Program Check (0x700)
  handler still may not handle QEMU's trap instruction correctly
- fn_36e168 overwrites 0x200 with MC handler; re-arm BPs if needed after 0x36c3d4
- fn_548d78: copied by fn_36e168 as handler stubs — do NOT patch
- GDB RSP: send $c#63, do NOT recv — let wait_bp() drain
- Clear ALL stale BPs at start of each session (use z0,addr,4 for known-used addresses)
- QEMU launch: use `nohup ... & disown` pattern (setsid blocked in this environment)
- SPR encoding: spr = ((w >> 11) & 0x1f) << 5 | ((w >> 16) & 0x1f)
