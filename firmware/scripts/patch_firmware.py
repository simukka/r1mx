#!/usr/bin/env python3
"""
patch_firmware.py — Binary patcher for RED ONE MX firmware binaries

Applies NOP patches to stub out hardware init sequences that crash QEMU.
Defaults to Build 32 (software.bin).  Pass --build13 for Build 13.

Usage:
    python3 scripts/patch_firmware.py [--input PATH] [--output PATH]
                                      [--list] [--probe ADDR] [--phase N]
                                      [--build13]

Strategy:
  PPC big-endian NOP = 0x60000000 (ori r0, r0, 0)
  PPC return (blr)   = 0x4E800020

  We NOP individual instructions that access hardware not present in QEMU,
  or replace function preambles with blr to skip entire init routines.

Build 32 patch summary:
  Phase 1 (always apply):
    0x000084   SP relocation: lis r1,1 → lis r1,0x800
    0x36C388   NOP canary wait bne #1
    0x36C394   NOP canary wait bne #2
  Phase 2 (apply as crash sites are discovered):
    0x36FA1C   Always-branch past bogus SSL verify-callback dispatch
    ... (10 more QEMU-compatibility patches)
  Phase 3 (SSD model-string bypass):
    0x5D552C   SSD bypass site A: li r3,1 over bl IsCompatible (hotplug handler)
    0x5D58E8   SSD bypass site B: li r3,1 over bl IsCompatible (state re-validate)

Build 13 patches are preserved for reference (--build13 flag).
"""

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PPC_NOP = b"\x60\x00\x00\x00"   # ori r0, r0, 0
PPC_BLR = b"\x4e\x80\x00\x20"   # blr (return)
PPC_LI_R3_0_BLR = b"\x38\x60\x00\x00\x4e\x80\x00\x20"  # li r3,0; blr (return 0)


@dataclass
class Patch:
    offset: int
    original: bytes     # expected original bytes (safety check)
    replacement: bytes
    description: str
    phase: int = 1      # which boot phase this patch is for
    bamboo_only: bool = False  # True = only needed for bamboo/unmapped MMIO machine


# ---------------------------------------------------------------------------
# Known patches — organised by boot phase
# ---------------------------------------------------------------------------
# Phase 1: DCR-level hardware init (SDRAM0, EBC0, CPC0, UIC0).
#   QEMU bamboo silently ignores unknown DCR writes via `mtdcr`, so these
#   may not actually crash. Include as safeguards.
#
# Phase 2: MMIO peripheral init (timer, interrupt controller, FPGA registers).
#   These WILL crash — QEMU will generate machine checks on unmapped MMIO.
#   Add patches here as crash addresses are discovered via r2 debug session.
#
# Patch format:
#   offset      — file offset (= runtime address since binary loads at 0x0)
#   original    — first 4 bytes at that offset (verify before patching)
#   replacement — NOP or BLR
#   description — what is being stubbed

# ---------------------------------------------------------------------------
# Build 32 patches  (default — software.bin, 15,253,280 bytes)
# SHA-256: 416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd
# ---------------------------------------------------------------------------
BUILD32_PATCHES: list[Patch] = [
    # -----------------------------------------------------------------------
    # Phase 1 — SP relocation
    #
    # romInit at 0x84 sets SP = 0x10000 (64 KB).  With a 15 MB image and deep
    # VxWorks init call chains, the stack collides with code.  Relocate to the
    # 128 MB mark (well above the firmware image).
    #   lis r1, 0x0001  →  lis r1, 0x0800
    Patch(
        offset=0x000084,
        original=b'\x3c\x20\x00\x01',
        replacement=b'\x3c\x20\x08\x00',
        description="Relocate romInit SP: lis r1,1 → lis r1,0x800 (SP=0x07FFFFF0)",
        phase=1,
    ),
    # -----------------------------------------------------------------------
    # Phase 1 — Stack canary wait loop (0x36C380–0x36C394)
    #
    # usrInit at 0x36C350 spins waiting for:
    #   *(0x00E269A4) == 0x12348765
    #   *(0x00E269A0) == 0x5A5AC3C3
    # Set by secondary hardware init on real camera; never written in QEMU.
    # NOP both bne branches to fall through immediately.
    Patch(
        offset=0x36C388,
        original=b'\x40\x9e\xff\xf8',
        replacement=PPC_NOP,
        description="NOP canary bne #1 (0x36C380 loop, tests 0x00E269A4)",
        phase=1,
    ),
    Patch(
        offset=0x36C394,
        original=b'\x40\x9e\xff\xec',
        replacement=PPC_NOP,
        description="NOP canary bne #2 (0x36C380 loop, tests 0x00E269A0)",
        phase=1,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 — Crash patches discovered via QEMU CPU trace analysis
    # -----------------------------------------------------------------------
    #
    # Crash #1: bogus SSL/TLS verify-callback dispatch (0x36FA1C)
    #
    # Diagnosed via -d cpu,int QEMU trace. Execution path:
    #   usrInit (0x36C3C8) → bl 0x36F9F8 → bctrl at 0x36FA24 → 0xD7E680
    #
    # fn_36F9F8 loads a "function pointer" from 0xE26D28 (HA=0xE2, off=+0x6D28).
    # That address holds 0x00D7E680 — a pointer to the SSL string literal
    # "cert depth=%d %s\n".  This is clearly an X.509/SSL callback table
    # entry, NOT a function pointer.  The code does:
    #   if (ptr == 0) skip; else call(ptr);
    # but the entry is non-zero (it is the string address), so it tries to
    # call into the data segment.  Instruction at +16 (0xD7E690) = 0x0A000000
    # (opcode 2 = tdi, invalid on PPC32) → QEMU raises HV_EMU (96) → infinite
    # exception restart loop.
    #
    # Fix: change the `beq 0x36FA28` to unconditional `b 0x36FA28`, so the
    # bctrl is always bypassed regardless of the callback pointer value.
    Patch(
        offset=0x36FA1C,
        original=b'\x41\x82\x00\x0c',   # beq 0x36FA28 (skip if ptr==0)
        replacement=b'\x48\x00\x00\x0c', # b 0x36FA28 (always skip)
        description="Skip bogus SSL verify-callback dispatch: fn_36F9F8 reads a string ptr (0xD7E680) as a function ptr; always branch past bctrl",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #2 — Skip BSS zeroing (redundant under QEMU)
    # -----------------------------------------------------------------------
    #
    # At 0x36C3AC there is: bl 0x496698  (= bl memset)
    # Arguments set up just before:
    #   r3 = BSS_START (0x00E9BF20)
    #   r4 = 0  (fill value = zero)
    #   r5 = BSS_SIZE (~2.75 MB)
    #
    # QEMU initialises all RAM to zero at startup, so this memset is
    # entirely redundant.  In hardware it takes <1ms; in QEMU's TCG
    # the ~690k store-word iterations run at ~187 KB/s effective
    # bandwidth, blocking boot for 15+ seconds before the VxWorks
    # kernel even starts.
    #
    # Fix: NOP the bl so execution falls straight through to
    #   0x36C3B0: li r4, 2
    #   0x36C3B4: li r3, 1
    #   0x36C3B8: bl 0x458A00  (kernelInit / usrRoot entry)
    # Both r3 and r4 are unconditionally overwritten by li so there is
    # no dependency on the skipped memset return value.
    Patch(
        offset=0x36C3AC,
        original=b'\x48\x12\xa2\xed',   # bl 0x496698 (memset BSS)
        replacement=PPC_NOP,
        description="Skip BSS zero-fill memset: QEMU RAM is already zero; saves ~15 s of emulated stw loop",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #3 — Zero the bogus "restart" function pointer at 0xE26D2C
    # -----------------------------------------------------------------------
    #
    # fn_36FA7C (the "invoke restart callback" helper) does:
    #   r31 = *[0xE26D2C]
    #   if r31 != 0: mtctr r31; bctrl  ← call it as function pointer
    #   else: r3 = *[0xE26D48]; return
    #
    # The DATA segment at 0xE26D2C contains 0x00000008 — this is actually
    # an integer table column value (the sequence 5,6,7,8 appears at
    # offsets 0xE26D08, 0xE26D14, 0xE26D20, 0xE26D2C in an SSL callback
    # table), NOT a real function pointer.  In the QEMU/emulation context
    # no prior code writes a valid function address there, so the value 8
    # is taken as the ROM-init entry point (0x0008) and called — causing
    # an unconditional CPU reset on every call to fn_36FA7C.
    #
    # fn_36FA7C is called unconditionally from fn_36E168 (at 0x36E208 via
    # bl 0x36FA7C) during the VxWorks boot init sequence.  With the value
    # non-zero the boot loop restarts ~59 000 times per 10 seconds.
    #
    # Fix: zero the word at 0xE26D2C so fn_36FA7C takes the "no callback"
    # path → returns with r3 = *[0xE26D48] = 0x00000000 and does NOT
    # restart the CPU.  Boot proceeds to the next init stage.
    Patch(
        offset=0xE26D2C,
        original=b'\x00\x00\x00\x08',   # integer 8, mistaken for fn ptr → calls 0x0008
        replacement=b'\x00\x00\x00\x00', # null → fn_36FA7C skips bctrl, returns r3=0
        description="Zero bogus restart callback at 0xE26D2C: value 0x8 was mistaken for a fn ptr to ROM-init (0x0008), causing unconditional restart loop in fn_36FA7C",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #4 — Null C++ RTTI table pointer at 0xE293B4
    # -----------------------------------------------------------------------
    #
    # fn_36D9A4 (called during VxWorks init) reads a dispatch struct at
    # 0xE2939C and calls multiple function pointers from it:
    #
    #   r31 = *[0xE2939C+0x20] = 0x005477B8   ← valid code, returns in r3
    #   r31 = r3 (fn return value, used as divisor)
    #   r29 = *[0xE2939C+0x18] = 0x00E38B4C   ← NOT code! C++ RTTI table
    #   cmpwi r29, 0
    #   beq skip                               ← skip if null
    #   mtctr r29
    #   bctrl                                  ← CRASH: first word = 0x00000500
    #                                          ← raises HV_EMU (illegal instr)
    #
    # 0xE38B4C is a C++ typeinfo/RTTI registration table — 5-word entries:
    #   [0]=0x500(flags), [1]=0, [2]=string_ptr (mangled name), [3]=fn_ptr, [4]=0
    # Names include "iptObjectPKc", "tingsPanelENS_6EPanelE", etc.
    # The value 0x500 (primary opcode 0) is an illegal PPC instruction.
    #
    # The QEMU HV_EMU exception vector at 0x0700 (Program Check) eventually
    # calls the restart chain again → 6177 restarts per 5-second run.
    #
    # Fix: null the pointer at 0xE293B4 → cmpwi r29,0 is true → beq taken
    # → bctrl skipped entirely; function proceeds normally.
    Patch(
        offset=0xE293B4,
        original=b'\x00\xE3\x8B\x4C',   # C++ RTTI table addr: mistaken for fn ptr
        replacement=b'\x00\x00\x00\x00', # null → beq skip taken, bctrl avoided
        description="Null C++ RTTI table ptr at 0xE293B4: value 0xE38B4C is a typeinfo table (illegal instr), not a function; nulling causes cmpwi/beq in fn_36D9A4 to skip the bctrl",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #5 — Null C++ dispatch fn ptr at 0xE293BC (struct +0x20)
    # -----------------------------------------------------------------------
    #
    # The dispatch struct at 0xE2939C is used by fn_36D9A4 and fn_36DA74.
    # Both functions load *[0xE2939C + 0x20] = 0x005477B8 into r31, check it
    # non-zero, then call via bctrl (CTR = r31 = 0x5477B8).
    #
    # 0x5477B8 is a large C++ type-dispatch switch (checks cr7, loads r9=type
    # name ptr, branches through a chain ending at the shared tail 0x547474).
    # The shared tail does: addi r1, r1, 0x10; blr
    # This adds 0x10 to r1 before returning — designed for callers with a
    # 0x10 stack frame.  But fn_36D9A4 and fn_36DA74 allocate 0x20 frames
    # (stwu r1,-0x20(r1)), so the +0x10 leaves r1 0x10 too high.
    # Epilogue then restores LR from the wrong stack slot → junk return → restart.
    #
    # Fix: null the fn ptr at offset 0xE293BC so cmpwi r31,0; bne → beq skip
    # is taken. fn then uses r31=-1 (li r31,-1 fallback) as divisor in divwu
    # → result 0 → no stack corruption → epilogue restores correctly.
    Patch(
        offset=0xE293BC,
        original=b'\x00\x54\x77\xB8',   # 0x5477B8: C++ type-dispatch fn, shared tail adds +0x10 to r1
        replacement=b'\x00\x00\x00\x00', # null → cmpwi/beq in fn_36D9A4/fn_36DA74 skips bctrl → no stack corruption
        description="Null C++ type-dispatch ptr at 0xE293BC (struct+0x20): 0x5477B8 corrupts stack via shared tail 0x547474 (addi r1,r1,0x10 assumes 0x10 frame but callers alloc 0x20)",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #6 — Null C++ dispatch fn ptr at 0xE293B0 (struct +0x14)
    # -----------------------------------------------------------------------
    #
    # fn_36DA74 (same pattern as fn_36D9A4) has a SECOND bctrl after the first:
    #   After divwu/mullw using the +0x20 fn result, it loads:
    #     r30 = *[0xE2939C + 0x14] = 0x005470E8
    #   checks r30 != 0, then calls via bctrl (CTR = r30 = 0x5470E8).
    #
    # 0x5470E8 is another C++ type-dispatch chain entry; its exit paths also
    # go through the shared tail at 0x547474 (addi r1,r1,0x10;blr), causing
    # the same stack corruption bug in fn_36DA74's 0x20 frame.
    #
    # fn_36D9A4 also has this second bctrl path, but it is already guarded by
    # Patch #4 (r29 = *[+0x18] = 0 → beq skips to epilogue before reaching it).
    # fn_36DA74 is NOT guarded at this point — it always proceeds to the second
    # bctrl if *[+0x14] != 0.
    #
    # Fix: null the fn ptr at 0xE293B0 so cmpwi r30,0; beq taken in both
    # functions → second bctrl skipped → no further stack corruption.
    Patch(
        offset=0xE293B0,
        original=b'\x00\x54\x70\xE8',   # 0x5470E8: second C++ type-dispatch fn, same tail bug
        replacement=b'\x00\x00\x00\x00', # null → cmpwi r30,0/beq in fn_36D9A4+fn_36DA74 skips bctrl
        description="Null C++ type-dispatch ptr at 0xE293B0 (struct+0x14): 0x5470E8 corrupts stack via shared tail 0x547474 in fn_36DA74's second bctrl; nulling causes cmpwi/beq to skip it",
        phase=2,
    ),
    #
    # ── Patch #10 & #11 ── bcopy corrupt 2 GB count (fn_387DD8 epilogue)
    #
    # When the ROM→RAM relocation loop in fn_387DD8 exhausts its second list
    # (sp+0x8C = 0), the epilogue code still tries to bcopy using r10=0 as a
    # struct pointer.  The count is computed as:
    #
    #   lwz r5, 0x14(r10=0)  → r5 = *[0x14] = 0x7C9C43A6 (PPC exception vector code!)
    #   subf r5, r9, r5      → r5 = 0x7C9C43A6 - 0xE30000 = 0x7BB943A6 ≈ 2 GB
    #   bl bcopy(dst, src, 2 GB) → spins for ~163 min in QEMU
    #
    # Root cause: fn_387DD8 performs ROM→RAM data relocation (copying firmware
    # segments from their load address to their link address).  In QEMU the
    # binary is loaded flat at 0x0 so all segments are already at their link
    # addresses; these copies are unnecessary.  Skipping bcopy when r10=0 is
    # correct and safe for QEMU.
    #
    # Fix: Replace the two-instruction sequence that starts the corrupt
    # computation with a NULL-check + skip:
    #
    #   0x388280  lwz r5, 0x14(r10)   →  cmpwi r10, 0  (2c 0a 00 00)
    #   0x388284  add r4, r4, r11     →  beq   0x388294 (41 82 00 10)
    #
    # When r10=0: cmpwi sets EQ → beq branches to 0x388294 (after bl bcopy)
    # When r10≠0: cmpwi clears EQ → falls through to subf/bl; r5 is stale but
    #             the bcopy of 0 bytes is still safe for QEMU (no real hardware).
    Patch(
        offset=0x388280,
        original=b'\x80\xAA\x00\x14',   # lwz r5, 0x14(r10)  ← NULL deref when r10=0
        replacement=b'\x2C\x0A\x00\x00', # cmpwi r10, 0
        description="Guard bcopy count load: replace 'lwz r5,0x14(r10)' with 'cmpwi r10,0' so NULL r10 sets EQ for the beq skip below (Patch #10)",
        phase=2,
    ),
    Patch(
        offset=0x388284,
        original=b'\x7C\x84\x5A\x14',   # add r4, r4, r11
        replacement=b'\x41\x82\x00\x10', # beq 0x388294  (0x388294 - 0x388284 = 0x10)
        description="Guard bcopy call: replace 'add r4,r4,r11' with 'beq 0x388294' to skip bl bcopy when r10=0 (Patch #11)",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Phase 2 Patch #12 — Unconditional branch past crash paths in fn_387834
    # -----------------------------------------------------------------------
    #
    # fn_387834 (prologue at 0x387834: mflr r0 / stwu r1,-0x28(r1), frame=0x28)
    # processes options by calling fn_3969C4 in a loop.  At 0x3878C0 it calls
    # fn_3969C4(r3=1, r4=r29) and tests the return value at 0x3878CC.
    #
    # fn_3969C4 (0x3969C4) structure:
    #   cmpwi r4, 0       ← if r4=NULL, skip strcmp and return *(0xE27418)
    #   otherwise calls fn_39AD64 (strcmp) twice then returns 0
    # *(0xE27418) = 0x00D73178 (non-zero) so when r4=r29=0 (NULL), fn_3969C4
    # returns NON-zero.
    #
    # r26 = 2 (loop counter, not a struct ptr) because Patches #7–#9 nulled the
    # dispatch table (0xE293B0/B4/BC), preventing C++ object initialisation.
    # BOTH branches at 0x3878CC crash when r26=2:
    #
    #   beq taken  (r3=0) → 0x387B0C:
    #     addi r31, r26, 0x20  → r31=0x22 → lwz r9,0x18(r31) reads from 0x3A → CRASH
    #
    #   beq not-taken (r3≠0) → 0x3878D0:
    #     addi r30, r26, 0x20  → r30=0x22 → lwz r31,0x14(r30) reads from 0x36 → CRASH
    #
    # The caller at 0x388040 immediately overwrites r3 with `addi r3, r1, 0x20`,
    # so fn_387834's return value is irrelevant — we can safely exit via the
    # epilogue regardless of fn_3969C4's return.
    #
    # Fix: replace the conditional beq with an UNCONDITIONAL branch to fn_387834's
    # own correct epilogue at 0x387AD4:
    #
    #   0x387AD4: lwz  r0, 0x2C(r1)   ← load saved LR from sp+0x2C (correct for
    #                                     fn_387834's frame=0x28: old_sp=sp+0x28,
    #                                     LR save = old_sp+4 = sp+0x2C)
    #   0x387AD8: mr   r3, r26         ← return r26 as fn result (discarded by caller)
    #   0x387ADC–0x387AF4: restore r26–r31
    #   0x387AF8: addi r1, r1, 0x28   ← restore stack (frame=0x28)
    #   0x387AFC: blr                  ← return to caller (0x388040) ✓
    #
    # Previous patch history at this offset:
    #   v1 (0x419EFE8C): beq → 0x387758 (inside fn_387580), fell through to
    #      fn_387580's epilogue (frame=0xD0), sp+0xD4=0 → blr→0x0 → RESET.
    #   v2 (0x419E0208): beq cr7 → 0x387AD4 — only safe when fn_3969C4 returns 0;
    #      when r29=NULL fn_3969C4 returns 0xD73178 (non-zero) → fallthrough crash.
    #
    # Encoding: b 0x387AD4  from  0x3878CC
    #   offset  = 0x387AD4 - 0x3878CC = 0x208
    #   LI      = 0x208 (word-addressed, fits in 24-bit signed field)
    #   instruction = (18<<26)|(LI) = 0x48000000 | 0x208 = 0x48000208
    Patch(
        offset=0x3878CC,
        original=b'\x41\x9E\x02\x40',   # beq cr7, 0x387B0C (original, crashes with r26=2)
        replacement=b'\x48\x00\x02\x08', # b 0x387AD4 (unconditional → fn_387834 epilogue)
        description="Unconditional branch at fn_387834+0x98 to its own epilogue: both the beq-taken (0x387B0C) and fallthrough (0x3878D0) paths crash when r26=2; caller discards return value",
        phase=2,
    ),
    #
    # Known candidate crash sites (from static analysis — verify addresses):
    #   0x000012DB4  lis r0, 0x4010  → MMIO 0x4010E507 (unknown peripheral)
    #   0x000012DD4  lis r0, 0x4004  → MMIO 0x4004E505 (unknown peripheral)
    #   0x0000DCB0   sysHwInit_seq   → calls device enable sub-functions w/ MMIO
    #   0x001C18DC   sysSerialInit   → XUartLite at 0x40600000 (may work in QEMU)

    # -----------------------------------------------------------------------
    # Phase 2 Patch #13 — Bypass corrupted bctrl dispatch that causes infinite loop
    # -----------------------------------------------------------------------
    #
    # fn_36DEF0 at 0x36E024 loads a function pointer from BSS at 0xE2932C:
    #
    #   0x36E020: lwz  r29, -27860(r9)     ← r9=0xE30000, so r29=*(0xE2932C)
    #   0x36E024: cmpwi r29, 0
    #   0x36E028: beq   0x36E03C           ← skip bctrl if r29==0
    #   0x36E02C: add   r3, r3, r26        ← compute arg
    #   0x36E030: mtctr r29                ← CTR = function pointer = 0x38826C
    #   0x36E034: addi  r4, r0, 4
    #   0x36E038: bctrl                    ← call *(0xE2932C) = 0x38826C
    #   0x36E03C: ...                      ← continue after bctrl
    #
    # At runtime, *(0xE2932C) = 0x38826C (a code address within the loop body,
    # NOT a valid vtable function entry point).  This is a stale/corrupted value
    # caused by Patches #7-#9 nulling the C++ dispatch table, which disrupted
    # object construction so the vtable was never properly set up.
    #
    # The bctrl dispatches to 0x38826C — the middle of a bdnz loop body.
    # CTR = 0x38826C = 3,736,172 at entry.  fn_387834's inner bdnz exhausts
    # CTR to 0 on the first call (looping 3.7M times), then wraps to 0xFFFFFFFF.
    # The outer bdnz at 0x388240 sees CTR≠0 and loops again → INFINITE LOOP.
    #
    # Confirmed via GDB RSP: NIP=0x3882C4, CTR=0x38826C, LR=0x36E03C (from bctrl),
    # SP=0x07FFFF50 — firmware has been stuck for 60+ seconds.
    #
    # Fix: convert the conditional skip to an unconditional skip — always branch
    # past the bctrl, never calling the corrupted function pointer.
    #
    # Encoding:
    #   beq 0x36E03C from 0x36E028:  (18<<26)|(0x14) = 0x48000014
    #   offset = 0x36E03C - 0x36E028 = 0x14
    Patch(
        offset=0x36E028,
        original=b'\x41\x82\x00\x14',   # beq cr0, 0x36E03C  (conditional skip)
        replacement=b'\x48\x00\x00\x14', # b 0x36E03C  (always skip bctrl)
        description="Bypass corrupted bctrl at 0x36E038: *(0xE2932C)=0x38826C (wrong vtable, caused by Patches #7-#9). bctrl→0x38826C loops forever (CTR=3.7M→0→wrap→∞). Convert conditional beq to unconditional b so the dispatch is always skipped.",
        phase=2,
    ),

    # -----------------------------------------------------------------------
    # Patches #14–#20 — Bypass all remaining corrupted bctrl dispatch sites
    # -----------------------------------------------------------------------
    #
    # At runtime, *(0xE2932C) = 0x38826C (a code address in the middle of a
    # bdnz loop body, NOT a valid function pointer).  The file stores 0x00547150
    # at that offset, but C++ init code overwrites it with 0x38826C due to the
    # C++ dispatch table having been nulled by Patches #7–#9.
    #
    # Every call site uses the same pattern:
    #   addis rX, r0, 0xE3       ; rX = 0xE30000
    #   lwz   rY, -27860(rX)     ; rY = *(0xE2932C)
    #   cmpwi rY, 0
    #   beq   SKIP               ; ← PATCH: change to unconditional b SKIP
    #   [compute args]
    #   mtspr CTR, rY            ; CTR = 0x38826C = 3,736,172
    #   bctrl                    ; → 0x38826C = bdnz loop body → infinite loop
    # SKIP:
    #
    # Fix: convert each `beq SKIP` to `b SKIP` (always skip the bctrl).
    #
    # Patch #14 — second dispatch site (0x36E12C bctrl, confirmed via LR after Patch #13)
    Patch(
        offset=0x36E11C,
        original=b'\x41\x82\x00\x14',   # beq cr0, 0x36E130  (conditional skip)
        replacement=b'\x48\x00\x00\x14', # b 0x36E130          (always skip bctrl at 0x36E12C)
        description="Bypass 2nd corrupted bctrl dispatch at 0x36E12C: *(0xE2932C)=0x38826C → infinite loop. Confirmed via LR=0x36E130 after Patch #13.",
        phase=2,
    ),
    # Patch #15 — third dispatch site (0x36DC2C bctrl)
    Patch(
        offset=0x36DC24,
        original=b'\x41\x82\x00\xCC',   # beq cr0, 0x36DCF0
        replacement=b'\x48\x00\x00\xCC', # b 0x36DCF0
        description="Bypass 3rd corrupted bctrl at 0x36DC2C: beq→b at 0x36DC24 skips bctrl that loads CTR=*(0xE2932C)=0x38826C.",
        phase=2,
    ),
    # Patch #16 — fourth dispatch site (0x36DCEC bctrl)
    Patch(
        offset=0x36DCD8,
        original=b'\x41\x82\x00\x18',   # beq cr0, 0x36DCF0
        replacement=b'\x48\x00\x00\x18', # b 0x36DCF0
        description="Bypass 4th corrupted bctrl at 0x36DCEC: beq→b at 0x36DCD8 skips bctrl.",
        phase=2,
    ),
    # Patch #17 — fifth dispatch site (0x370EDC bctrl)
    Patch(
        offset=0x370E88,
        original=b'\x41\x82\x00\x5C',   # beq cr0, 0x370EE4
        replacement=b'\x48\x00\x00\x5C', # b 0x370EE4
        description="Bypass 5th corrupted bctrl at 0x370EDC: beq→b at 0x370E88.",
        phase=2,
    ),
    # Patch #18 — sixth dispatch site (0x370EE4 bctrl)
    Patch(
        offset=0x370ED0,
        original=b'\x41\x82\x00\x14',   # beq cr0, 0x370EE4
        replacement=b'\x48\x00\x00\x14', # b 0x370EE4
        description="Bypass 6th corrupted bctrl at 0x370EE0: beq→b at 0x370ED0.",
        phase=2,
    ),
    # Patch #19 — seventh dispatch site (0x370FD0 bctrl)
    Patch(
        offset=0x370F4C,
        original=b'\x41\x82\x00\x8C',   # beq cr0, 0x370FD8
        replacement=b'\x48\x00\x00\x8C', # b 0x370FD8
        description="Bypass 7th corrupted bctrl at 0x370FD0: beq→b at 0x370F4C.",
        phase=2,
    ),
    # Patch #20 — eighth dispatch site (0x370FD8 bctrl)
    Patch(
        offset=0x370FC4,
        original=b'\x41\x82\x00\x14',   # beq cr0, 0x370FD8
        replacement=b'\x48\x00\x00\x14', # b 0x370FD8
        description="Bypass 8th corrupted bctrl at 0x370FD4: beq→b at 0x370FC4.",
        phase=2,
    ),

    # -----------------------------------------------------------------------
    # Patches #21–#33 — Null BSS sentinel values (0xFFFFFFFF) skipped by Patch #5
    # -----------------------------------------------------------------------
    #
    # Patch #5 NOPs the BSS memset call (saves ~15s emulated time).  QEMU
    # pre-zeros RAM before loading the binary, but the firmware file stores
    # 0xFFFFFFFF at 13 locations in the BSS region as "uninitialized" sentinels.
    # When code checks `cmpwi rX, 0 / beq skip / bctrl`, a sentinel 0xFFFFFFFF
    # passes the non-zero test → bctrl to 0xFFFFFFFF → PPC exception → reset.
    #
    # Fix: zero all 13 sentinel locations in the binary so they behave as if
    # the memset had run.  Confirmed by crash at NIP=0x0 with LR=0x36FB74:
    #   0x36FB5C: lwz r31, 0x6D38(r31)  ; r31 = *(0xE26D38) = 0xFFFFFFFF
    #   0x36FB70: bctrl                  ; → 0xFFFFFFFF → exception → reset
    #
    Patch(offset=0xE26D38, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE26D38: 0xFFFFFFFF → 0 (uninitialized callback, BSS memset was patched away)", phase=2),
    Patch(offset=0xE26DDC, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE26DDC", phase=2),
    Patch(offset=0xE27000, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE27000", phase=2),
    Patch(offset=0xE276B8, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE276B8", phase=2),
    Patch(offset=0xE27BD4, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE27BD4", phase=2),
    Patch(offset=0xE29438, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE29438", phase=2),
    Patch(offset=0xE2A3C8, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2A3C8", phase=2),
    Patch(offset=0xE2A748, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2A748", phase=2),
    Patch(offset=0xE2A918, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2A918", phase=2),
    Patch(offset=0xE2A994, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2A994", phase=2),
    Patch(offset=0xE2A9B4, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2A9B4", phase=2),
    Patch(offset=0xE2B590, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2B590", phase=2),
    Patch(offset=0xE2B7D8, original=b'\xff\xff\xff\xff', replacement=b'\x00\x00\x00\x00',
          description="Null BSS sentinel at 0xE2B7D8", phase=2),

    # -----------------------------------------------------------------------
    # Phase 3 — SSD model-string bypass (DigMag compatibility check)
    # -----------------------------------------------------------------------
    #
    # The DigMag storage driver validates every attached drive against a
    # hardcoded approved-model table before allowing it to mount for
    # recording.  The validation function IsCompatible (0x4D1B64) returns
    # 0 if the drive's ATA IDENTIFY model string does not match any entry
    # in the table (0xD2E3E8–0xD2E484, 11 strings incl. "RED 64GB SSD ",
    # "LEXAR ATA FLASH ATA", "RedRAM", "RedRAID" variants, etc.).
    #
    # 0x4D1B64 DigMag_IsCompatible(drive_obj):
    #   • If drive_obj == NULL or *drive_obj == NULL → return 0
    #   • r3 = *((*drive_obj) + 24)   ← virtual method pointer from vtable
    #   • return IsApprovedModel(r3)   ← 0x4CA1E0, iterates approved table
    #
    # There are two call sites that set state=INCOMPATIBLE (6) on failure:
    #
    #   Site A — 0x5D552C (hotplug/mount handler):
    #     0x5D5528: mr  r3, r31          ← pass drive object
    #     0x5D552C: bl  0x4D1B64         ← IsCompatible()  ← PATCH SITE A
    #     0x5D5530: mr. r28, r3          ← r28 = result; test CR0
    #     0x5D5534: bne 0x5D5454         ← if compatible → success path
    #     0x5D5538: li  r0, 6            ← INCOMPATIBLE
    #     0x5D553C: stw r0, 92(r30)      ← drive->state = INCOMPATIBLE
    #
    #   Site B — 0x5D58E8 (re-validate on state change):
    #     0x5D58E4: mr  r3, r31          ← pass drive object
    #     0x5D58E8: bl  0x4D1B64         ← IsCompatible()  ← PATCH SITE B
    #     0x5D58EC: mr. r26, r3          ← r26 = result; test CR0
    #     0x5D58F0: beq 0x5D5A28         ← if NOT compatible → INCOMPATIBLE
    #     0x5D5A28: li  r0, 6            ← INCOMPATIBLE (second path)
    #     0x5D5A38: stw r0, 92(r31)      ← drive->state = INCOMPATIBLE
    #
    # Bypass strategy: replace each `bl 0x4D1B64` with `li r3, 1`.
    #   • li r3, 1  (0x38600001) leaves r3=1 (any non-zero = compatible)
    #   • The following `mr. r28/r26, r3` then sets CR0=NE
    #   • Site A: bne taken → success path (drive mounts)
    #   • Site B: beq NOT taken → execution continues past INCOMPATIBLE store
    #   • No other register is used between the bl and the mr.
    #
    # WARNING: This bypasses the entire model-string check.  Any SATA/ATA
    # device plugged into the iVDR slot will be treated as a compatible
    # recording medium.  Data integrity depends on the drive's own ATA
    # compliance; RED's write patterns (fixed-block sequential) are
    # standard SATA — no RED-proprietary commands are used post-mount.
    #
    # SSD bypass — Site A (hotplug/mount handler at 0x5D5574)
    Patch(
        offset=0x5D552C,
        original=b'\x4b\xef\xc6\x39',   # bl 0x4D1B64  (IsCompatible)
        replacement=b'\x38\x60\x00\x01', # li r3, 1     (always compatible)
        description="SSD bypass site A: replace bl IsCompatible with li r3,1; mr./bne at 0x5D5534 then branches to success path instead of setting INCOMPATIBLE state",
        phase=3,
    ),
    # SSD bypass — Site B (re-validate on state change at 0x5D5A64)
    Patch(
        offset=0x5D58E8,
        original=b'\x4b\xef\xc2\x7d',   # bl 0x4D1B64  (IsCompatible)
        replacement=b'\x38\x60\x00\x01', # li r3, 1     (always compatible)
        description="SSD bypass site B: replace bl IsCompatible with li r3,1; mr./beq at 0x5D58F0 then does NOT branch to the INCOMPATIBLE store at 0x5D5A28",
        phase=3,
    ),

    # -----------------------------------------------------------------------
    # Patch #36 — NOP null bctrl in fn_6288 (VxWorks callback dispatch)
    # -----------------------------------------------------------------------
    #
    # fn_6288 at 0x6288 dispatches callbacks stored in a struct field at r30+64.
    # The code does:
    #
    #   0x62A8: r0 = *(r30+64)           ← first read: check for null
    #   0x62AC: cmpwi cr7, r0, 0
    #   0x62B0: beq cr7, 0x62E8          ← skip if initially null (correct guard)
    #   ...
    #   0x62C0: bl fn_2748               ← fn_2748 DEQUEUES/CLEARS *(r30+64) as side-effect
    #   0x62C4: r0 = *(r30+64)           ← second read: now ZERO (fn_2748 consumed it)
    #   0x62C8: mtspr 288, r0            ← CTR = 0
    #   0x62CC: bctrl                    ← CRASH: calls address 0x0 (reset vector)
    #
    # fn_2748 is a VxWorks message-receive stub that pops a pending callback
    # from the queue, clearing the stored pointer as it dequeues. Since the
    # hardware queue is empty in QEMU, fn_2748 returns immediately without
    # installing a valid callback, leaving *(r30+64) == 0 for the second read.
    #
    # Observed crash pattern (NIP sampling):
    #   NIP=0x5C (dccci cache init loop) × 18/60 samples
    #   NIP=0x0  (reset vector re-entered via null bctrl) × 12/60 samples
    #   LR=0x62D0 during NIP=0x0 confirms the crash is at bctrl 0x62CC.
    #
    # Fix: NOP the bctrl. Execution falls through to 0x62D0 which checks
    # fn_2748's return value (r3) and the retry/exit loop logic. With r3
    # reflecting the message-receive result (likely an error code in empty-
    # queue QEMU), the loop exits cleanly without calling address 0.
    #
    # fn_6288 is called from fn_638C (0x63B0) and fn_6558 (0x6590).
    # Its return value is not used by fn_638C (caller checks a struct field
    # instead). NOP-ing the bctrl prevents the CPU reset while still
    # allowing the callback housekeeping (fn_2748 dequeue) to complete.
    Patch(
        offset=0x62CC,
        original=b'\x4e\x80\x04\x21',   # bctrl (CTR=0 after fn_2748 clears *(r30+64))
        replacement=PPC_NOP,             # nop → fall through to 0x62D0 post-call checks
        description="NOP null bctrl in fn_6288: fn_2748 clears *(r30+64) as side-effect, making CTR=0; bctrl→0x0 resets CPU. NOP allows retry/exit logic at 0x62D0 to handle the empty-queue case.",
        phase=2,
    ),
    # Patch #37 — NOP XUartLite TX-FULL poll loop in fn_1b9b0
    #
    # fn_1b9b0 is the XUartLite UART byte-write routine.  It polls the status
    # register at (r3 + 8) = 0xe0600008 waiting for TX_FULL (bit 3) to clear
    # before writing to the TX FIFO at (r3 + 4):
    #
    #   0x1b9d0: addi r31, r3, 8       ; r31 = UART_BASE+8 (status reg)
    #   0x1b9d4: mr   r3, r31          ; ← loop-back target
    #   0x1b9d8: bl   0xe898           ; MMIO read: r3 = *(UART_BASE+8)
    #   0x1b9dc: andi. r0, r3, 8       ; test TX_FULL bit
    #   0x1b9e0: bne  0x1b9d4          ; ← spin while TX_FULL=1  ← THIS PATCH
    #   0x1b9e4: addi r3, r30, 4       ; r3 = UART_BASE+4 (TX FIFO)
    #   0x1b9e8: mr   r4, r29          ; byte to write
    #   0x1b9ec: bl   0xe900           ; MMIO write: *(UART_BASE+4) = r4
    #
    # In QEMU's bamboo machine, physical address 0xe0600000 is not mapped.
    # QEMU returns all-Fs (0xFFFFFFFF) for reads from unmapped addresses,
    # making TX_FULL (bit 3) = 1 permanently → infinite spin.
    #
    # Fix: NOP the backward branch.  The firmware will always proceed to
    # write the byte — safe because QEMU silently discards the write anyway.
    Patch(
        offset=0x1b9e0,
        original=b'\x40\x82\xff\xf4',   # bne 0x1b9d4 (spin while TX_FULL=1)
        replacement=PPC_NOP,
        description="NOP XUartLite TX-FULL poll loop in fn_1b9b0 (0xe0600008 unmapped in QEMU bamboo → reads 0xFFFFFFFF → bit3=TX_FULL=1 → infinite spin)",
        phase=2,
        bamboo_only=True,
    ),
    # Patch #38 — NOP XUartLite TX-FIFO write in fn_1b9b0
    #
    # After the TX-FULL poll loop is NOP'd (Patch #37), fn_1b9b0 proceeds to
    # write the byte to the TX FIFO at (UART_BASE + 4) = 0xe0600004 via fn_e900:
    #
    #   0x1b9e4: addi r3, r30, 4       ; r3 = UART_BASE+4 (TX FIFO addr)
    #   0x1b9e8: mr   r4, r29          ; r4 = byte to write
    #   0x1b9ec: bl   0xe900           ; MMIO write: stw r4, 0(r3)  ← THIS PATCH
    #
    # fn_e900 executes:  stwu r1,-0x10(r1) / stw r4,0(r3) / eieio / blr
    # The "stw r4, 0(r3)" writes to physical address 0xe0600004.
    # QEMU's bamboo machine does not map 0xe0600000 — the write triggers a
    # PPC405 Machine Check exception (NIP → 0x00000010).
    #
    # The machine check vector at 0x10 is NOT a proper VxWorks handler — it is
    # the romInit SPR-clearing code that resets the stack pointer and calls
    # usrInit again, causing an infinite re-initialisation loop.
    #
    # Fix: NOP the "bl 0xe900" call.  UART output is already discarded by QEMU;
    # silently dropping the TX FIFO write is safe.
    Patch(
        offset=0x1b9ec,
        original=b'\x4b\xff\x2f\x15',   # bl 0xe900 (UART TX FIFO write)
        replacement=PPC_NOP,
        description="NOP XUartLite TX-FIFO write in fn_1b9b0 (0xe0600004 unmapped in QEMU bamboo → write triggers Machine Check at 0x10 → romInit re-runs → infinite boot loop)",
        phase=2,
        bamboo_only=True,
    ),
    # Patch #39 — NOP XUartLite status read in fn_1b9b0
    #
    # fn_1b9b0 structure after Patches #37 + #38:
    #
    #   0x1b9d4: mr   r3, r31             ; r3 = UART_BASE+8 (status reg addr)
    #   0x1b9d8: bl   0xe898              ; MMIO read: lwz r3, 0(r3)  ← THIS PATCH
    #   0x1b9dc: andi. r0, r3, 8          ; test TX_FULL bit (result used only by…)
    #   0x1b9e0: nop                      ; [Patch #37: was bne 0x1b9d4 poll loop]
    #   0x1b9e4: addi r3, r30, 4          ; TX FIFO addr
    #   0x1b9e8: mr   r4, r29             ; byte to write
    #   0x1b9ec: nop                      ; [Patch #38: was bl 0xe900 TX write]
    #
    # fn_e898 executes: stwu r1,-0x10(r1) / eieio / lwz r3,0(r3) / addi r1,r1,0x10 / blr
    # The "lwz r3, 0(r3)" reads from physical address 0xe0600008 (UART status reg).
    # QEMU's bamboo machine does not map 0xe0600000 — the read triggers a PPC405
    # Machine Check exception (NIP → machine check vector).
    #
    # With EVPR installed by fn_36e168, the machine check vector now points to the
    # VxWorks MChk handler at 0x200, which recovers via rfi back to 0xe8a4 — but
    # the per-character machine check + full handler overhead (~100 instructions)
    # makes each byte print extremely slow (effectively serialised through the
    # exception path), stalling fn_458a14's init sequence for many minutes.
    #
    # Fix: NOP the "bl 0xe898" call.  The TX-FULL test that follows (andi./bne) is
    # already dead code after Patch #37 NOP'd the branch, so removing the MMIO read
    # is fully safe and eliminates the per-character machine check.
    Patch(
        offset=0x1b9d8,
        original=b'\x4b\xff\x2e\xc1',   # bl 0xe898 (UART status read)
        replacement=PPC_NOP,
        description="NOP XUartLite status read in fn_1b9b0 (0xe0600008 unmapped → Machine Check per character through VxWorks MChk handler; result unused after Patch #37 killed the TX-FULL poll loop)",
        phase=2,
        bamboo_only=True,
    ),

    # Patch #40 — NOP error-counter MMIO write in fn_9b78 (early-return path)
    #
    # fn_9b78 is the shared boot-error logger called by every fn_DCB0 sub-function
    # (fn_9bc8, fn_9e24, …) when a hardware device is not found.  It maintains a
    # counter in MMIO register 0xe0be00 (= lis 0xe1 + d=-0x4200 → 0xe10000-0x4200).
    #
    # Structure:
    #   0x9b78: stwu  r1, -0x10(r1)
    #   0x9b7c: lis   r8, 0xe1           ; r8 = 0xe10000
    #   0x9b80: lwz   r9, -0x4200(r8)    ; r9 = *(0xe0be00) — MMIO READ (safe: ret 0xFF)
    #   0x9b84: cmpwi cr7, r9, 4         ; 0xFF > 4 → ble not taken
    #   ...
    #   0x9b94: ble   cr7, 0x9ba4        ; NOT taken (0xFF > 4) → fall through
    #   0x9b98: addi  r1, r1, 0x10       ; restore stack (early-return path)
    #   0x9b9c: stw   r11, -0x4200(r8)   ; ← WRITE to 0xe0be00 → Machine Check  THIS PATCH
    #   0x9ba0: blr
    #
    # 0xe0be00 is not mapped in QEMU bamboo; the write triggers a PPC405 Machine
    # Check exception.  After fn_36e168 has installed the VxWorks exception handler
    # at 0x200, that handler performs a controlled system restart → usrInit re-init
    # loop. fn_9b78 is called from 7 different error paths in fn_9bc8 and fn_9e24,
    # so this single write site stalls fn_DCB0 on every device-not-found error.
    #
    # Fix: NOP the stw — the counter write is optional telemetry; the RAM-based
    # error log arrays (written on the normal path below) remain intact.
    Patch(
        offset=0x9b9c,
        original=b'\x91\x68\xbe\x00',   # stw r11, -0x4200(r8) — write to 0xe0be00
        replacement=PPC_NOP,
        description="NOP error-counter write to 0xe0be00 in fn_9b78 early-return path (0x9b9c): unmapped MMIO write triggers Machine Check → VxWorks restart loop; counter is optional telemetry",
        phase=2,
        bamboo_only=True,
    ),

    # Patch #41 — NOP error-counter MMIO write in fn_9b78 (normal path)
    #
    # Same address 0xe0be00, normal-path write (counter ≤ 4 branch taken):
    #   0x9ba4: lis   r9, 0xea           ; RAM log array base
    #   ...
    #   0x9bb8: stwx  r4, r9, r0         ; store to RAM error log — safe
    #   0x9bbc: stwx  r3, r11, r0        ; store to RAM error log — safe
    #   0x9bc0: stw   r10, -0x4200(r8)   ; ← WRITE to 0xe0be00 → Machine Check  THIS PATCH
    #   0x9bc4: blr
    #
    # The RAM log stores at 0x9bb8/0x9bbc are fine (BSS area).  Only the
    # final counter-increment write to 0xe0be00 must be suppressed.
    Patch(
        offset=0x9bc0,
        original=b'\x91\x48\xbe\x00',   # stw r10, -0x4200(r8) — write to 0xe0be00
        replacement=PPC_NOP,
        description="NOP error-counter write to 0xe0be00 in fn_9b78 normal path (0x9bc0): same unmapped MMIO address as Patch #40; RAM log stores above remain intact",
        phase=2,
        bamboo_only=True,
    ),

    # Patches #42–43 — fix fn_548d78 driver-init dispatch (crashes via bad call chain)
    #
    # usrInit calls fn_458a14 twice (at 0x36c3dc r3=0, at 0x36c3e4 r3=1).
    # fn_458a14 allocates a 16-byte frame, reads *(0xe29310) = 0x00548d78, and
    # calls fn_548d78 via bctrl.
    #
    # fn_548d78 (0x548d78) is a MID-FUNCTION block in a larger function:
    #   0x548d78: li    r5, 0x8e    ; device type ID
    #   0x548d7c: li    r7, 0x11b   ; device subtype
    #   0x548d80: bl    fn_4a6438   ; ← Crash A: fn_4a6438→fn_4a5f00→bctrl 0x203c6000
    #   0x548d84: li    r3, 0       ; discards fn_4a6438 return value
    #   0x548d88: b     0x548b04    ; ← Crash B: fn_548b04 restores 316(r1) as LR,
    #                               ;   but fn_458a14 only allocated 16 bytes → reads
    #                               ;   garbage from caller's stack → branches to wrong addr
    #
    # fn_4a5f00 crash:
    #   *(0xe2b528)=0x117 → *(0x117+0x1c)=*(0x133)=0x203c6000 → bctrl outside 256MB RAM
    #
    # fn_548b04 epilogue crash:
    #   Designed for a function with 316-byte frame + callee-saves r12,r19-r31.
    #   fn_458a14 has only 16 bytes. fn_548b04:lwz r0,316(r1) reads junk LR → crash.
    #
    # CONFIRMED SAFE to patch fn_548d78 directly:
    #   - fn_36e168 does NOT copy fn_548d78 bytes. The exception-handler install
    #     loop in fn_36e168 is ALWAYS SKIPPED because *(0xe26a88)=0x00d7e0b4 ≠ 0.
    #   - fn_4a6438 has 600+ callers but NONE are in fn_36e168 (0x36xxxx) or
    #     fn_DCB0 (0x0-0x100000) ranges — confirmed by full-binary bl-target scan.
    #   - fn_548d78 is ONLY called via function pointer dispatch from fn_458a14.
    #
    # Fix A (Patch #42): NOP the bl fn_4a6438 at 0x548d80 → skips fn_4a5f00 crash.
    # Fix B (Patch #43): Replace b 0x548b04 at 0x548d88 with blr → fn_548d78 returns
    #   correctly to fn_458a14 (LR = 0x458a44) instead of crashing in fn_548b04.
    #
    # After both patches, fn_548d78 cleanly returns r3=0 to fn_458a14. ✓
    Patch(
        offset=0x548d80,
        original=b'\x4b\xf5\xd6\xb9',   # bl fn_4a6438 (4bf5d6b9)
        replacement=PPC_NOP,
        description="NOP bl fn_4a6438 in fn_548d78: skips fn_4a6438→fn_4a5f00 crash (bctrl to 0x203c6000 outside 256MB QEMU RAM). fn_548d78 next does li r3,0 so fn_4a6438 return value is irrelevant.",
        phase=2,
    ),
    # Patch #43 — fix fn_548d78 return (b fn_548b04 → blr)
    Patch(
        offset=0x548d88,
        original=b'\x4b\xff\xfd\x7c',   # b 0x548b04 (4bfffd7c)
        replacement=PPC_BLR,
        description="Replace b 0x548b04 with blr in fn_548d78: fn_548b04 epilogue expects 316-byte frame but fn_458a14 only allocates 16 bytes → reads garbage LR and crashes. blr correctly returns to fn_458a14's LR (0x458a44). NOTE: fn_548d78 is NOT called at runtime — *(0xe29310) is set to 0x37cd4c (not 0x548d78) by init code at 0x36cc64. This patch is harmless dead-code safety.",
        phase=2,
    ),
    # Patch #44 — fn_458a14: skip dispatch table call, return 0
    #
    # usrInit calls fn_458a14 twice (0x36c3dc r3=0, 0x36c3e4 r3=1). fn_458a14
    # reads *(0xe29310) at runtime and calls that address via bctrl (CTR dispatch).
    #
    # At runtime *(0xe29310) = 0x37cd4c (set by init code at 0x36cc64, NOT
    # the binary's static value 0x548d78).  fn_37cd4c is the EPILOGUE of the
    # function at 0x37cc94 (40-byte frame: saves r26-r31, LR at 44(r1)).
    # Calling fn_37cd4c from fn_458a14 (which has only a 16-byte frame) causes:
    #   - lwz r26-r31 from wrong stack slots (reads caller/garbage data)
    #   - mtspr LR, r0  (sets LR to garbage from 44(r1) = SP+28 above fn_458a14)
    #   - addi r1, r1, 40 (pops 40 bytes from a 16-byte frame → SP overshoots)
    #   - blr → branches to garbage address → crash / MCE
    #
    # usrInit does NOT check the return value of fn_458a14 (no comparison after
    # either bl — r3 is immediately overwritten by 'addis r29,0,0xea' at 0x36c3e8).
    # It is safe to make fn_458a14 return 0 without performing the dispatch.
    #
    # Fix: replace bctrl at 0x458a40 with 'li r3, 0'.
    # After the patch, fn_458a14 execution path:
    #   0x458a40: li r3, 0      ← was bctrl; now sets return value to 0
    #   0x458a44: mr r31, r3    ← r31 = 0
    #   0x458a48: mr r3, r31    ← r3 = 0
    #   0x458a4c: lwz r0, 20(r1) + mtspr LR,r0 + lwz r31 + addi SP + blr
    # Both fn_458a14(r3=0) and fn_458a14(r3=1) return 0. usrInit continues
    # to fn_36860c at 0x36c3ec without error.
    Patch(
        offset=0x458a40,
        original=b'\x4e\x80\x04\x21',   # bctrl (4e800421)
        replacement=b'\x38\x60\x00\x00', # li r3, 0 (38600000) — return success
        description="fn_458a14 bctrl→li r3,0: dispatch table *(0xe29310)=0x37cd4c at runtime (epilogue of 40-byte-frame fn_37cc94). Calling it from fn_458a14's 16-byte frame corrupts stack and crashes. usrInit ignores return value so returning 0 is safe.",
        phase=2,
    ),
    # Patch #45 — NOP self-referential bctrl in fn_44c660
    #
    # fn_44c660 is an interface-connect dispatch function. Its code at 0x44c6e0
    # checks guard flags in BSS (0xe9bffc) and, if set, loads a function pointer
    # from BSS (0xe9bf80) into CTR and calls it via bctrl at 0x44c720 with
    # r3=57 (interrupt vector 57) and r4-r10=0.
    #
    # At runtime the guard at 0xe9bffc has 0x10000001 set (set by driver init),
    # AND the function pointer at 0xe9bf80 = 0x0044c70c — the address of the
    # `li r6, 0` instruction INSIDE fn_44c660 itself (not a valid function
    # start). Calling CTR=0x0044c70c jumps back into the middle of fn_44c660,
    # which re-executes the argument-setup block and hits bctrl again with
    # CTR=0x44c70c → infinite loop.
    #
    # The function pointer was written to 0xe9bf80 by driver registration code
    # that computed the wrong address (off by the prologue offset). The callback
    # itself is optional — the code has two branches (`bne 0x44c728`) that skip
    # to the post-call section when the guards are unset.
    #
    # Fix: NOP the bctrl at 0x44c720. Execution falls through to `b 0x44c728`
    # at 0x44c724 and continues normally. The interrupt-vector registration the
    # callback was intended to perform is skipped; this is safe since the same
    # result (no callback installed) would occur on hardware where the driver
    # was not loaded.
    Patch(
        offset=0x44c720,
        original=b'\x4e\x80\x04\x21',   # bctrl (4e800421)
        replacement=PPC_NOP,
        description="NOP self-referential bctrl in fn_44c660: *(0xe9bf80)=0x44c70c at runtime points mid-function → infinite loop. Guard bne at 0x44c6f0 should skip this call but guard value 0xe9bffc is set by driver init. NOP skips the bad call; fn falls through to b 0x44c728.",
        phase=2,
    ),
    # -------------------------------------------------------------------------
    # Patch #46 — NOP null-dereference counter increment that corrupts 0x7c
    #
    # At 0x44c698, fn_44c660 loads a struct pointer from BSS (addr 0xeac3e0).
    # If the pointer is NULL (as it always is early in boot — BSS is zeroed),
    # the subsequent `lwz r11, 0x7c(r12=0)` / `addi` / `stw r11, 0x7c(r12=0)`
    # reads and writes to virtual address 0x7c — the PPC405 Machine Check
    # exception vector.
    #
    # Original: reads 0x7c9bfba6 (mticcr r4), adds 1 → 0x7c9bfba7 (Rc=1,
    # illegal instruction form), writes back.  On the next execution of the
    # vector at 0x7c a Program Check exception fires, jumping to the VxWorks
    # error handler at 0x36fd24 which loops forever, continuously triggering
    # TLB fills for page 0 and overflowing QEMU's dirty-page tracking.
    #
    # Fix: NOP the stw so address 0x7c is never overwritten.  The counter
    # increment is lost but the struct pointer is NULL so there is no valid
    # counter to increment anyway.
    # -------------------------------------------------------------------------
    Patch(
        offset=0x44c6a8,
        original=b'\x91\x6c\x00\x7c',   # stw r11, 0x7c(r12)
        replacement=PPC_NOP,
        description="NOP null-deref stw at fn_44c660+0x48: r12=*(0xeac3e0)=NULL → stw r11,0x7c(r12=0) corrupts PPC405 Machine Check vector at 0x7c, causing infinite Program Check exception storm. NOP prevents the corrupt write.",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # NOTE: Patch #47b (APU Unavailable / 0x700 skip handler) was removed in
    # session 10.  Originally needed to skip FSL/UDI instructions that QEMU
    # rejected at vector 0x700.  QEMU patch 0004 (0004-ppc405-fsl-instructions.patch)
    # added native FSL instruction support, so FSL no longer reaches 0x700.
    # The 0x700 skip handler also had a wrong SPR encoding (mfdcr DCR96 instead
    # of mfspr SRR0), causing it to loop forever on any genuine Program Check
    # exception rather than advancing past it.  With FSL handled by QEMU the
    # patch served no purpose and was actively harmful; removed entirely.
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Patches #48a/#48b — fn_5b57b0: hardcode vtable[4] dispatch target
    # -------------------------------------------------------------------------
    # Root cause: fn_5b57b0 contains a vtable dispatch guarded by TCB+0x70:
    #
    #   0x5b5858: lwz  r12, 0x70(r30)
    #   0x5b585c: cmpwi r12, 1
    #   0x5b5860: bne  0x5b5884        ; skip if *(r30+0x70) != 1
    #   0x5b5864: lis  r31, 0x10d
    #   0x5b5868: addi r3, r31, 0x584  ; r3 = 0x010d0584 (taskClassId)
    #   0x5b586c: lwz  r11, 0xc(r3)    ; r11 = *(0x010d0590) = taskClass vtable ptr
    #   0x5b5870: addi r4, r30, 0x40   ; r4 = TCB+0x40 (OBJ_CORE address)
    #   0x5b5874: lwz  r11, 0x10(r11)  ; r11 = vtable[4] = classObjInit method
    #   0x5b5878: lwz  r5, 0x74(r30)
    #   0x5b587c: mtctr r11
    #   0x5b5880: bctrl                ; call classObjInit(taskClassId, TCB+0x40, ...)
    #
    # The method at vtable[4] stores TCB+0x40 into *(taskClassId), making it
    # non-zero.  A spin loop in fn_5aaf5c waits on *(taskClassId) != 0 before
    # the scheduler can proceed.
    #
    # Problem: *(0x010d0590) is in BSS, so it is always 0 at cold boot.
    # fn_498cd8 (objCoreInit / classCreate) is supposed to populate it, but all
    # call paths fail: the parent-class self-referential check
    # (*(parentClass+0x38) == parentClass) finds no valid CLASS_DESC in the
    # firmware's static DATA.  BSS is zeroed every boot, so no static
    # initialisation is possible either.
    #
    # With the old Patch #50-era heap fix in place, taskInit succeeds and sets
    # *(TCB+0x70) = 1.  The guard falls through to the vtable dispatch, which
    # derefs a null pointer and raises an ISI exception.
    #
    # Fix: replace the two load instructions that dereference the null BSS
    # pointer with a two-instruction sequence that loads the address of
    # 0x0046bfec directly into r11.  0x0046bfec is:
    #
    #   0x0046bfec: stw r4, 0(r3)   ; *(r3) = r4  →  *(taskClassId) = TCB+0x40
    #   0x0046bff0: blr
    #
    # This is a standalone leaf function (preceded by blr at 0x0046bfe8) that
    # stores its second argument into the memory pointed to by its first
    # argument.  Calling it as vtable[4](taskClassId, TCB+0x40, ...) satisfies
    # the spin-loop invariant and is functionally equivalent to what the real
    # classObjInit would do at this call site.
    #
    #   0x5b586c: lis r11, 0x46       ; r11 = 0x00460000
    #   0x5b5874: ori r11, r11, 0xbfec ; r11 = 0x0046bfec
    # -------------------------------------------------------------------------
    Patch(
        offset=0x5b586c,
        original=b'\x81\x63\x00\x0c',   # lwz r11, 0xc(r3)  [loads BSS vtable ptr]
        replacement=b'\x3d\x60\x00\x46', # lis r11, 0x46     [r11 = 0x00460000]
        description="fn_5b57b0: replace lwz r11,0xc(r3) with lis r11,0x46. First half of two-instruction sequence to load 0x0046bfec (stw r4,0(r3);blr) into r11, bypassing BSS vtable ptr *(0x010d0590)=0 that would cause a null-deref ISI crash.",
        phase=2,
    ),
    Patch(
        offset=0x5b5874,
        original=b'\x81\x6b\x00\x10',   # lwz r11, 0x10(r11) [loads vtable[4] from null]
        replacement=b'\x61\x6b\xbf\xec', # ori r11, r11, 0xbfec [r11 = 0x0046bfec]
        description="fn_5b57b0: replace lwz r11,0x10(r11) with ori r11,r11,0xbfec. Completes r11=0x0046bfec. The subsequent bctrl calls stw-r4-0(r3);blr which stores TCB+0x40 into *(0x010d0584), satisfying the fn_5aaf5c spin-loop and allowing the scheduler to proceed.",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patches #49a/#49b — fn_5b58a8: hardcode vtable[6] dispatch target
    # -------------------------------------------------------------------------
    # Root cause: fn_5b58a8 is the companion to fn_5b57b0 with opposite guard
    # polarity.  fn_5b57b0's epilogue clears bit 0 of *(TCB+0x70):
    #   rlwinm r12, r12, 0, 0, 0x1e  ; clear bit 31 (bit 0)
    # So after fn_5b57b0, *(TCB+0x70) = 0.  fn_5b58a8 checks:
    #   0x5b5950: lwz  r12, 0x70(r30)
    #   0x5b5954: cmpwi r12, 0
    #   0x5b5958: bne  0x5b5978   ; skip if *(TCB+0x70) != 0
    # When *(TCB+0x70) == 0 (always after fn_5b57b0), the guard falls through
    # to an identical vtable dispatch using offset 0x18 (vtable[6]) instead of
    # 0x10 (vtable[4]):
    #   0x5b5964: lwz  r11, 0xc(r3)    ; r11 = *(0x010d0590) = 0 (BSS)
    #   0x5b596c: lwz  r11, 0x18(r11)  ; r11 = *(0 + 0x18) = *(0x18) → ISI crash
    #
    # fn_5b58a8's epilogue sets bit 4 (0x10) of *(TCB+0x70) after the call.
    # The vtable[6] method is a "post-init hook" that can safely be a no-op;
    # using the same 0x0046bfec leaf (stw r4,0(r3);blr) is idempotent because
    # *(taskClassId) = TCB+0x40 is already set by the vtable[4] call.
    #
    #   0x5b5964: lis r11, 0x46        ; r11 = 0x00460000
    #   0x5b596c: ori r11, r11, 0xbfec ; r11 = 0x0046bfec
    # -------------------------------------------------------------------------
    Patch(
        offset=0x5b5964,
        original=b'\x81\x63\x00\x0c',   # lwz r11, 0xc(r3)   [loads BSS vtable ptr]
        replacement=b'\x3d\x60\x00\x46', # lis r11, 0x46      [r11 = 0x00460000]
        description="fn_5b58a8: replace lwz r11,0xc(r3) with lis r11,0x46. First half of two-instruction sequence to load 0x0046bfec into r11, bypassing BSS vtable ptr *(0x010d0590)=0.",
        phase=2,
    ),
    Patch(
        offset=0x5b596c,
        original=b'\x81\x6b\x00\x18',   # lwz r11, 0x18(r11)  [loads vtable[6] from null]
        replacement=b'\x61\x6b\xbf\xec', # ori r11, r11, 0xbfec [r11 = 0x0046bfec]
        description="fn_5b58a8: replace lwz r11,0x18(r11) with ori r11,r11,0xbfec. Completes r11=0x0046bfec. The bctrl calls stw-r4-0(r3);blr which writes TCB+0x40 into *(0x010d0584) (idempotent). fn_5b58a8 epilogue then sets bit 4 of *(TCB+0x70).",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #50 — Zero live-camera "sysMemTop" cache at 0xE0C37C / 0xE0C380
    # -------------------------------------------------------------------------
    # Root cause: The DATA segment snapshot contains cached RAM-top values that
    # the real camera computed on a system with 1.25 GB of RAM.  Two consecutive
    # words hold these values:
    #
    #   0xE0C37C = 0x395944A3  — fn_d87c cache ("sysPhysMemTop" lower bound)
    #   0xE0C380 = 0x4CCECBD7  — fn_d8a0 cache ("sysMemTop"   upper bound)
    #
    # fn_d8a0 (0xD8A0): reads *(0xE0C380) and returns it immediately if non-zero.
    # fn_d87c (0xD87C): reads *(0xE0C37C) and returns it immediately if non-zero.
    # Both functions are called from usrInit to compute the VxWorks heap bounds:
    #
    #   heapEnd = fn_d8a0()        => 0x4CCECBD7 on live camera, ~ 1.2 GB
    #   r6 = heapEnd               => passed as arg-6 to kernelInit
    #   kernelInit saves r6 as r28 => used as the heap-region object pointer
    #   fn_5b0ff4(r3=r28)          => r3 = 0x4CCECBD7 (outside QEMU 256 MB RAM)
    #   *(r3+0x70)                 => ISI crash, PC stuck at 0x700
    #
    # QEMU maps 256 MB: 0x00000000-0x0FFFFFFF.  Any address >= 0x10000000 causes
    # an Instruction Storage Interrupt (ISI) on access.
    #
    # Fix: zero both cached words so the functions fall through to their fallback:
    #   fn_d87c fallback:  lis r3, 0x1000  => r3 = 0x10000000 (top of 256 MB RAM)
    #   fn_d8a0 fallback:  r3 = fn_d87c() - 0x60000 - 0x4000 = 0x0FF9C000
    #
    # 0x0FF9C000 is well within QEMU RAM, giving VxWorks ~238 MB of heap space.
    # -------------------------------------------------------------------------
    Patch(
        offset=0xE0C37C,
        original=b'\x39\x59\x44\xa3',   # 0x395944A3 — live-camera sysPhysMemTop
        replacement=b'\x00\x00\x00\x00',
        description="Zero live-camera sysPhysMemTop cache at 0xE0C37C: fn_d87c returns this cached value directly when non-zero, yielding 0x395944A3 (outside QEMU 256MB RAM). Zeroing forces fn_d87c fallback: lis r3,0x1000 → 0x10000000 (256MB top).",
        phase=2,
    ),
    Patch(
        offset=0xE0C380,
        original=b'\x4c\xce\xcb\xd7',   # 0x4CCECBD7 — live-camera sysMemTop
        replacement=b'\x00\x00\x00\x00',
        description="Zero live-camera sysMemTop cache at 0xE0C380: fn_d8a0 returns this cached value immediately when non-zero, yielding 0x4CCECBD7 (~1.2GB, outside QEMU 256MB RAM). usrInit passes this to kernelInit as the heap object pointer; fn_5b0ff4 then accesses *(ptr+0x70) → ISI crash. Zeroing forces fn_d8a0 to call fn_d87c and compute heapEnd = 0x0FF9C000 (well within QEMU RAM).",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #47 — Zero pre-seeded intCnt (exception nesting counter) at 0xE2942C
    # -------------------------------------------------------------------------
    # Root cause: The firmware binary's DATA segment (0x0–0xE9BF20) is extracted
    # from a live-running RED ONE MX camera, not a cold-boot ROM image.  The
    # interrupt/exception nesting counter `intCnt` at 0x00E2942C was snapshotted
    # in mid-operation and has value 0x00552F30 (5,582,640) in the binary.
    #
    # VxWorks' taskInit (fn_5b231c) checks: if (intCnt > 0) return -1
    # This prevents task creation from interrupt context.  With intCnt pre-seeded
    # to 5.5 million, kernelInit's taskInit call for the root task always fails,
    # kernelInit returns, and usrInit jumps to the 0x124 spin-loop.
    #
    # GDB confirmed (write watchpoint): nothing resets 0xE2942C to 0 during boot.
    #
    # Fix: zero it in the binary so the cold-boot value is 0 (correct behaviour).
    # The increment/decrement code at 0x36eb38 / 0x36eea8 (exception entry/exit)
    # will manage it correctly from that point forward.
    # -------------------------------------------------------------------------
    Patch(
        offset=0xE2942C,
        original=b'\x00\x55\x2f\x30',   # 0x00552F30 — snapshotted intCnt value
        replacement=b'\x00\x00\x00\x00',
        description="Zero pre-seeded intCnt at 0xE2942C: live-camera snapshot value 0x00552F30 causes taskInit (fn_5b231c) to return -1 for every task, making kernelInit fail → 0x124 spin-loop. VxWorks exception entry/exit (0x36eb38/0x36eea8) correctly maintains this counter once it starts at 0.",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #52 — Skip null priority-struct deref in fn_5aaf5c scheduler
    # -------------------------------------------------------------------------
    # Root cause: The root task TCB at 0x0ff9bd30 has TCB+0x94 = 0 (null pointer
    # to the CPU priority-queue struct).  The VxWorks scheduler (fn_5aaf5c) at
    # 0x5ab128 unconditionally dereferences *(TCB+0x94 + 0xD4C) to find the
    # highest-priority preemption candidate:
    #
    #   0x5ab124: lwz  r29, 0x94(r30)      ; r29 = *(TCB+0x94) = 0  (null!)
    #   0x5ab128: lwz  r31, 0xd4c(r29)     ; r31 = *(0+0xD4C) = 0x9001004c  ← CRASH
    #   0x5ab12c: cmpwi r31, 0             ; is there a preemption candidate?
    #   0x5ab130: beq  0x5ab160            ; if none (r31==0), skip preemption
    #
    # When r29=0: *(0xD4C) = 0x9001004c (boot-code instruction bytes misread as
    # a TCB address).  The scheduler selects 0x9001004c as "next task", loads its
    # all-zero context, and rfi jumps to PC=0 MSR=0 → 0x700 Program Exception.
    #
    # The existing beq at 0x5ab130 already handles the "no candidate" case: if
    # r31==0, it jumps to 0x5ab160 and selects the workQ-head task directly.
    # We just need to force r31=0 when r29=0 so the null dereference is avoided.
    #
    # Fix: replace the dangerous lwz r31,0xd4c(r29) with li r31,0.  This forces
    # the beq at 0x5ab130 to always be taken, selecting the workQ-head task
    # (0x0ff9bd30, the root task) without any preemption check.
    #
    # Trade-off: preemption via this scheduler path is disabled (any higher-
    # priority task in the priority-struct would not be noticed), making VxWorks
    # effectively cooperative at this code site.  For the emulation goal of
    # reaching the WDB debug agent this is acceptable; a full fix would require
    # tracking down where TCB+0x94 should be initialised and setting it to a
    # valid priority-queue descriptor.
    # -------------------------------------------------------------------------
    Patch(
        offset=0x5ab128,
        original=b'\x83\xfd\x0d\x4c',   # lwz r31, 0xd4c(r29) — crashes when r29=0
        replacement=b'\x3b\xe0\x00\x00', # li r31, 0 — force "no preemption candidate"
        description="fn_5aaf5c scheduler: replace lwz r31,0xd4c(r29) with li r31,0 to avoid null-ptr deref. When root task TCB+0x94=0, *(0+0xD4C)=0x9001004c (boot code) is misread as a TCB address, causing rfi to PC=0 → 0x700 crash. Forcing r31=0 makes the existing beq at 0x5ab130 skip preemption and select the workQ-head task (root task, 0x0ff9bd30) directly.",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #53a — Fix initial root-task PC: epilogue → prologue of fn_381a8c
    # -------------------------------------------------------------------------
    # fn_371cd0 ("task context init") builds the initial context for the root
    # task.  It computes the start PC with:
    #   0x371d60: addis r12, r0, 0x38      ; r12 = 0x380000
    #   0x371d64: addi  r12, r12, 0x1aec   ; r12 = 0x381aec  ← WRONG (epilogue)
    #   0x371d68: stw   r12, 0x24c(r31)    ; ctx+0x8c = PC = 0x381aec
    #
    # 0x381aec is in the MIDDLE of fn_381a8c's epilogue (restoring saved regs
    # and executing blr to LR).  Dispatching the task there immediately hits
    # blr with LR=0 (ctx+0x84 uninitialised), jumping to address 0 → crash.
    #
    # The correct entry point is the PROLOGUE at 0x381a8c:
    #   0x381a8c: mflr r0               ; save LR (needed for fn_381a8c to return)
    #   0x381a90: stwu r1, -0x50(r1)    ; allocate stack frame
    #   ...
    #   0x381a98: cmpwi cr7, r0, 0x51   ; check task type == 'Q'
    #   0x381aa0: stw   r4, 0x1c(r1)    ; save r4 (task descriptor pointer)
    #   ...
    #   0x381acc: cmpwi cr7, r4, 0      ; check task descriptor
    #   0x381ad0: bc 4,30 0x381b14      ; fast-exit if r4 != 0  (patched by #53b)
    #
    # Fix: change addi immediate from 0x1aec → 0x1a8c (difference = 0x60 = 96 bytes).
    # -------------------------------------------------------------------------
    Patch(
        offset=0x371d64,
        original=b'\x39\x8c\x1a\xec',   # addi r12, r12, 0x1aec  (epilogue PC 0x381aec)
        replacement=b'\x39\x8c\x1a\x8c', # addi r12, r12, 0x1a8c  (prologue PC 0x381a8c)
        description="Fix initial root-task PC: addi r12,r12,0x1aec → 0x1a8c in fn_371cd0 (0x381aec is fn_381a8c epilogue; dispatching there hits blr with LR=0 → crash. 0x381a8c is the correct prologue entry).",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #53b — NOP fast-exit branch in fn_381a8c wrapper
    # -------------------------------------------------------------------------
    # fn_381a8c checks the task descriptor pointer (r4) near the top:
    #   0x381acc: cmpwi cr7, r4, 0
    #   0x381ad0: bc 4,30 0x381b14    ; branch if cr7[EQ]=0  (i.e., r4 != 0)
    #
    # 0x381b14 is the function EPILOGUE (restores saved regs + blr).  If the
    # branch is taken with the saved-LR slot holding the return-to address from
    # ctx+0x84, then blr returns to LR = ctx+0x84 = 0x381a8c (set by #53c) and
    # the wrapper loops once, then correctly processes the descriptor.
    #
    # However, with r4 = ctx+0x10 (GPR4 at first dispatch) potentially non-zero
    # (the timer interrupt can save a non-zero r4 to ctx+0x10 before first
    # dispatch), the fast-exit fires before fn_381a8c does any work at all.
    # Confirmed: r4 = 0x0dcf5120 at the original crash site (0x381aec).
    #
    # Fix: NOP the bc so the normal processing path (bl 0x381a38 → fn_381824
    # → fn_38038c) always runs regardless of r4.
    # -------------------------------------------------------------------------
    Patch(
        offset=0x381ad0,
        original=b'\x40\x9e\x00\x44',   # bc 4,30 0x381b14 (fast-exit if r4 != 0)
        replacement=PPC_NOP,             # nop — always fall through to bl 0x381a38
        description="NOP fast-exit branch at fn_381a8c+0x44: bc 4,30 skips to epilogue when r4 (task descriptor) != 0. At first dispatch r4=ctx+0x10=0x0dcf5120 (non-zero), so the fast-exit fires before any descriptor processing. NOP forces the normal bl 0x381a38 path always.",
        phase=2,
    ),

    # -------------------------------------------------------------------------
    # Patch #53c — Initialise ctx+0x84 (LR slot) in fn_371cd0 root-task setup
    # -------------------------------------------------------------------------
    # The task context (TCB+0x1c0) stores the hardware LR as ctx+0x84 (TCB+0x244).
    # The dispatch code (0x372734) does:
    #   lwz r4, 0x0084(r3)   ; r4 = ctx+0x84 = LR
    #   mtspr LR, r4          ; set hardware LR before rfi
    # So when fn_381a8c executes "mflr r0" in its prologue, r0 = ctx+0x84.
    # fn_381a8c saves r0 (the LR) onto the stack and later restores it with
    # "blr" at its epilogue.  With ctx+0x84 = 0, blr jumps to address 0 → crash.
    #
    # fn_371cd0's if-path setup block (taken for the root task) has:
    #   0x371d60: addis r12, r0, 0x38     ; r12 = 0x380000
    #   0x371d64: addi  r12, r12, 0x1a8c  ; r12 = 0x381a8c (entry PC, after #53a)
    #   0x371d68: stw   r12, 0x24c(r31)   ; ctx+0x8c = PC
    #   0x371d6c: li    r11, 1            ; ← THIS SLOT (was: prepare flag=1 for ctx+0x9c)
    #   0x371d70: stw   r11, 0x25c(r31)   ; ctx+0x9c = flag (SPR945 value)
    #   0x371d74: b     0x371db8          ; end of if-path
    #
    # After #53a, r12 = 0x381a8c and is free to use.  The slot at 0x371d6c is
    # repurposed to store r12 into ctx+0x84 (TCB+0x244 = r31+0x244).
    #
    # Side-effect: r11 is still 0 (from `li r11, 0` at 0x371d48), so the
    # unchanged instruction at 0x371d70 now writes ctx+0x9c = flag = 0 instead
    # of 1.  SPR945 is set to 0 at dispatch instead of 1.  SPR945 is a VxWorks-
    # internal software register; its value affects only debug/trace behaviour,
    # not normal task execution.  Acceptable trade-off for the emulation goal.
    # -------------------------------------------------------------------------
    Patch(
        offset=0x371d6c,
        original=b'\x39\x60\x00\x01',   # li r11, 1  (was: flag=1 for ctx+0x9c)
        replacement=b'\x91\x9f\x02\x44', # stw r12, 0x244(r31)  (ctx+0x84/LR = 0x381a8c)
        description="fn_371cd0 root-task setup: replace 'li r11,1' with 'stw r12,0x244(r31)' to initialise ctx+0x84 (LR slot, TCB+0x244) with r12=0x381a8c (the wrapper prologue PC set by #53a). Without this, ctx+0x84=0 → hardware LR=0 at dispatch → fn_381a8c's mflr+blr returns to 0x0 → crash. Side-effect: ctx+0x9c flag becomes 0 (r11 remains 0 from li r11,0 at 0x371d48); SPR945 is set to 0 at dispatch (non-critical).",
        phase=2,
    ),

    # =========================================================================
    # Patch #54 — fn_38038c overflow-path redirect (fixes root-task infinite loop)
    # ============================================================================
    # Call chain at root-task dispatch:
    #
    #   fn_381a8c → fn_381a38 → fn_381824 → fn_38038c(r3=descriptor, r4=buf, r5=NULL)
    #
    # fn_38038c reads *(r5) as the hash-table size sentinel.  With r5=NULL it
    # reads the PPC reset vector at address 0 (= 0x48000008).  As bytes are
    # hashed (each iteration: r31 = r31*10 + char - 48) r31 eventually exceeds
    # 0x48000008, triggering the hash-table overflow branch at 0x3803f0:
    #
    #   0x3803ec: cmpl cr7, r8, r31      ; r8=0x48000008, r31=current hash
    #   0x3803f0: blt cr7, 0x38042c      ; if hash > table_size → resize
    #
    # The overflow path at 0x38042c/0x380430:
    #   0x38042c: mr r3, r29    ; r3 = r29 = original r5 = NULL
    #   0x380430: bl 0x38029c   ; fn_38029c(NULL) — CORRUPTS exception vectors!
    #   0x380434: lwz r31,0(r29); r31 = *(NULL) = 0x48000008 → output is 0x48000008
    #
    # Back in fn_381824:
    #   r11 = large value → r9 = descriptor_base + r11 wraps badly → INFINITE LOOP
    #
    # The prior implementation (cmpi+bc) only guarded when r29=NULL; for
    # descriptors with many bytes of the same value (e.g. 0xee uninitialized heap)
    # the hash grows past 0x48000008 over multiple iterations, and the value
    # stored in the output buffer is whatever r31 is at that point — not 0.
    # That large r31 causes the same infinite loop even though the branch fires.
    #
    # Fix (revised — 2 instruction patches at 0x38042c / 0x380430):
    #
    #   BEFORE:
    #     0x38042c: mr r3, r29          ; 0x7fa3eb78  prepare fn_38029c arg
    #     0x380430: bl 0x38029c         ; 0x4bfffe6d  hash-table resize
    #
    #   AFTER:
    #     0x38042c: li r31, 0           ; 0x3be00000  always zero the output value
    #     0x380430: b 0x380404          ; 0x4bffffd4  unconditionally return r31=0
    #
    # Effect: whenever the hash exceeds the (bogus) table-size limit, r31 is set
    # to 0 and the function returns immediately via the normal exit at 0x380404:
    #   0x38040c: stw r31, 0(r28)  → stores 0 to output buffer
    # Back in fn_381824:
    #   r11 = 0 → cmpli cr7, r11, 7 → bng cr7, 0x381910 (r11 ≤ 7 → exit) ✓
    #
    # Trade-off: fn_38029c (hash-table resize for non-NULL r29) is never called.
    # This is acceptable for emulation; all observed call sites pass r5=NULL.
    # -------------------------------------------------------------------------
    Patch(
        offset=0x38042c,
        original=b'\x7f\xa3\xeb\x78',   # mr r3, r29
        replacement=b'\x3b\xe0\x00\x00', # li r31, 0  — zero output before early return
        description="fn_38038c overflow-path redirect (part 1/2): replace 'mr r3,r29' (prepare fn_38029c arg) with 'li r31,0' to zero r31 before the unconditional return in patch #54b. When the hash accumulator overflows the table-size limit (always bogus because r5=NULL makes *(r5) read the PPC reset vector 0x48000008), r31 is forced to 0 so the output buffer receives 0, causing fn_381824 to see r11=0 and exit cleanly.",
        phase=2,
    ),
    Patch(
        offset=0x380430,
        original=b'\x4b\xff\xfe\x6d',   # bl 0x38029c  (hash-table resize)
        replacement=b'\x4b\xff\xff\xd4', # b 0x380404   (unconditional return with r31=0)
        description="fn_38038c overflow-path redirect (part 2/2): replace 'bl 0x38029c' (fn_38029c resize call) with 'b 0x380404' (unconditional branch to return path). Combined with patch #54a (li r31,0), this ensures r31=0 is stored to the output buffer on every hash overflow, regardless of the descriptor content or r29 value. fn_381824 then reads r11=0 from SP+8, which satisfies the 'cmpli r11,7 / bng 0x381910' exit at 0x381874-0x381878.",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Patch #55 — Force fn_371cd4 alternate path: skip fn_381a8c RTTI loop
    #
    # fn_371cd4 initialises a C++ typeinfo object. At 0x371d58 it reads a
    # kernel-BSS global (~0xe3ffa790). On real hardware this is set before
    # fn_371cd4 runs; in QEMU it is always 0.
    #
    # When the global == 0 the function stores fn_381a8c (0x381a8c) as the
    # typeinfo callback at offsets +580 and +588 of the object. fn_381a8c is
    # then invoked as an infinite VxWorks task that walks a C++ RTTI type
    # descriptor stream starting at 0x840600. In QEMU the stream never reaches
    # a Q0 terminator (only null bytes follow); r3 advances at ~800 KB/s
    # through the heap forever, starving usrRoot of CPU and preventing WDB.
    #
    # Fix: change the conditional branch at 0x371d5c from "bc (bne) 0x371d78"
    # to "b 0x371d78" (unconditional), so fn_371cd4 ALWAYS takes the alternate
    # path. That path calls fn_371c74 with a NULL global (returns -1 safely)
    # and stores obj[192]/obj[148][212] as the callbacks — both NULL from BSS,
    # so typeinfo processing is simply skipped without any crash.
    #
    #   0x371d5c: 0x4082001c  bc 0x371d78  (beq — take alt path if BSS global != 0)
    #   ->         0x4800001c  b  0x371d78  (always take alt path)
    Patch(
        offset=0x371d5c,
        original=b'\x40\x82\x00\x1c',
        replacement=b'\x48\x00\x00\x1c',
        description="Force fn_371cd4 alternate path: skip fn_381a8c RTTI infinite loop (BSS global ~0xe3ffa790 is 0 in QEMU; bc->b at 0x371d5c always takes the fn-ptr-copy path, never installs fn_381a8c)",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Patch #56 — NOP deferred-constructor list walk (fn_37d87c) in usrRoot
    #
    # usrRoot at 0x37c33c calls fn_37d87c, which walks a circular linked list
    # of pending C++ deferred constructors. In normal operation fn_381a8c
    # populates this list during RTTI processing. Because Patch #55 bypasses
    # fn_381a8c entirely, the list is never populated; its head pointer in BSS
    # at 0xe9ffc5c0 is 0 (NULL).
    #
    # fn_37d87c's loop exits when the current node pointer == sentinel (r30).
    # With the head = NULL the loop immediately reads *(NULL) = *(0x0) = 0
    # (PPC reset vector, which is 0 in RAM after boot-time patching), getting
    # stuck cycling 0 → 0 → 0 forever since NULL != sentinel.
    #
    # Fix: NOP the call. The list is intentionally empty — no deferred
    # constructors need running in QEMU. Skipping fn_37d87c is safe.
    #
    #   0x37c33c: 0x48001541  bl 0x37d87c
    #   ->         0x60000000  nop
    Patch(
        offset=0x37c33c,
        original=b'\x48\x00\x15\x41',
        replacement=PPC_NOP,
        description="NOP bl fn_37d87c in usrRoot: deferred-constructor list walk loops on NULL head (list unpopulated because fn_381a8c was bypassed by Patch #55); list is intentionally empty in QEMU",
        phase=2,
    ),
    # -----------------------------------------------------------------------
    # Patch #57 — NOP blocking WDB network init (fn_5a7f30) in usrInit
    #
    # usrInit (fn_36c350) at 0x36c424 calls fn_5a7f30, which:
    #   1. Spawns the WDB task (via fn_5b2880) with entry point 0x37c440
    #   2. Then blocks forever in a UDP socket wait for a network semaphore
    #      that never fires in QEMU (no real network / WDB UDP agent)
    #
    # Because fn_5a7f30 never returns, usrInit never completes, the root
    # task never exits, and the VxWorks scheduler never gets the opportunity
    # to run any other tasks (WDB, camera, etc.).
    #
    # Fix: NOP the call. The WDB task spawn inside fn_5a7f30 is lost, but
    # usrInit then returns normally and the scheduler runs all remaining
    # ready tasks. Further patches can stub out any WDB state that depends
    # on fn_5a7f30 having run.
    #
    #   0x36c424: 0x4823bb0d  bl 0x5a7f30
    #   ->         0x60000000  nop
    Patch(
        offset=0x36c424,
        original=b'\x48\x23\xbb\x0d',
        replacement=PPC_NOP,
        description="NOP bl fn_5a7f30 in usrInit: WDB network init blocks forever on UDP semaphore in QEMU; usrInit never returns without this NOP; skipping allows root task to complete and scheduler to run other tasks",
        phase=2,
    ),
]

# ---------------------------------------------------------------------------
# Build 13 patches  (legacy — SundanceBootable.bin, ~13 MB)
# Use: python3 scripts/patch_firmware.py --build13
# ---------------------------------------------------------------------------
BUILD13_PATCHES: list[Patch] = [
    Patch(
        offset=0x7C,
        original=b'\x3c\x20\x00\x01',
        replacement=b'\x3c\x20\x08\x00',
        description="Relocate romInit stack: lis r1,1 → lis r1,0x800 (SP=0x07FFFFF0)",
        phase=1,
    ),
    Patch(
        offset=0x2ED058,
        original=b'\x40\x9e\xff\xf8',
        replacement=PPC_NOP,
        description="NOP canary wait loop: bne cr7, 0x2ED050 (first branch)",
        phase=1,
    ),
    Patch(
        offset=0x2ED064,
        original=b'\x40\x9e\xff\xec',
        replacement=PPC_NOP,
        description="NOP canary wait loop: bne cr7, 0x2ED050 (second branch)",
        phase=1,
    ),
    Patch(
        offset=0x2F06D8,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x2F06B0 (skip exception-handler bctrl)",
        phase=1,
    ),
    Patch(
        offset=0x2F06DC,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x2F06B0 (skip call to 0x500 exception handler body)",
        phase=1,
    ),
    Patch(
        offset=0xDA80,
        original=b'\x4b\xff\xc1\x41',
        replacement=PPC_NOP,
        description="NOP: bl 0x9BC0 (IO/VP FPGA bitstream loader — no FPGA in QEMU)",
        phase=2,
    ),
    Patch(
        offset=0x3AB000,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x3AAFD8 path-1 (skip fptr call via *(0xBC5484))",
        phase=2,
    ),
    Patch(
        offset=0x3AB004,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x3AAFD8 path-1 (*(0xBC5484) default = 0x500 AE vector)",
        phase=2,
    ),
    Patch(
        offset=0x3AB04C,
        original=b'\x7f\xe9\x03\xa6',
        replacement=PPC_NOP,
        description="NOP: mtctr r31 in 0x3AAFD8 path-2 (skip fptr call via *(0xBC5488))",
        phase=2,
    ),
    Patch(
        offset=0x3AB050,
        original=b'\x4e\x80\x04\x21',
        replacement=PPC_NOP,
        description="NOP: bctrl in 0x3AAFD8 path-2 (*(0xBC5488) = 0x500 Alignment vector)",
        phase=2,
    ),
    Patch(
        offset=0x2ED0A0,
        original=b'\x48\x00\x1d\x81',
        replacement=PPC_NOP,
        description="NOP: bl 0x2EEE20 in usrInit — EVPR-relocating hardware init crashes QEMU",
        phase=2,
    ),
]

# Active patch set — selected by --build13 flag
KNOWN_PATCHES: list[Patch] = BUILD32_PATCHES


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_patches(data: bytearray, patches: list[Patch],
                  phase: Optional[int] = None,
                  skip_bamboo_only: bool = False) -> tuple[int, list[str]]:
    """
    Apply patches to a mutable bytearray.
    Returns (count_applied, list_of_warnings).
    skip_bamboo_only: when True, skip patches that are only needed for the
                      bamboo (unmapped-MMIO) machine; used with --r1mx.
    """
    applied = 0
    warnings = []
    for p in patches:
        if phase is not None and p.phase != phase:
            continue
        if skip_bamboo_only and p.bamboo_only:
            print(f"  [-] {hex(p.offset)}: SKIP (bamboo-only) {p.description[:60]}")
            continue
        end = p.offset + len(p.original)
        if end > len(data):
            warnings.append(f"SKIP offset {hex(p.offset)}: beyond file end")
            continue
        actual = bytes(data[p.offset:end])
        if actual != p.original:
            warnings.append(
                f"MISMATCH at {hex(p.offset)} '{p.description}': "
                f"expected {p.original.hex()} got {actual.hex()} — skipped"
            )
            continue
        data[p.offset:p.offset + len(p.replacement)] = p.replacement
        applied += 1
        print(f"  [+] {hex(p.offset)}: {p.description}")
    return applied, warnings


def add_patch(offset: int, fw_path: Path) -> None:
    """
    Helper: print the original bytes at an offset so a new Patch entry can
    be added to KNOWN_PATCHES.  Use during the r2 debug session:
        python3 scripts/patch_firmware.py --probe 0xADDRESS
    """
    with open(fw_path, "rb") as f:
        f.seek(offset)
        orig = f.read(4)
    print(f"Probe at {hex(offset)}: original bytes = {orig.hex()}")
    print(f"Add to KNOWN_PATCHES:")
    print(f"    Patch(")
    print(f"        offset=0x{offset:08x},")
    print(f"        original=b'{orig.hex()}',")
    print(f"        replacement=PPC_NOP,")
    print(f"        description='NOP: <describe what this does>',")
    print(f"        phase=2,")
    print(f"    ),")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch RED ONE MX firmware binary for QEMU hardware stubs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i", type=Path,
        default=None,
        help="Input firmware binary (default: Build 32 software.bin)",
    )
    parser.add_argument(
        "--output", "-o", type=Path,
        default=None,
        help="Output path (default: <input_dir>/software.patched.bin)",
    )
    parser.add_argument(
        "--build13", action="store_true",
        help="Use Build 13 patches (SundanceBootable.bin) instead of Build 32",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="List all known patches and exit",
    )
    parser.add_argument(
        "--probe", type=lambda x: int(x, 0),
        metavar="OFFSET",
        help="Print original bytes at OFFSET to help create a new Patch entry",
    )
    parser.add_argument(
        "--phase", type=int, default=None,
        help="Only apply patches for this phase number",
    )
    parser.add_argument(
        "--r1mx", action="store_true",
        help="Target r1mx-virtex4 QEMU machine: skip bamboo-only MMIO patches "
             "(patches #37-41) since XUartLite and error-counter devices are "
             "now modelled by the real machine. Output defaults to "
             "software.patched.r1mx.bin",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    # Select patch set and default paths
    if args.build13:
        patches = BUILD13_PATCHES
        default_input = repo_root / "reverse/Upgrade_Build 13/Upgrade/SundanceBootable.bin"
        default_output_name = "SundanceBootable.patched.bin"
        build_label = "Build 13"
    else:
        patches = BUILD32_PATCHES
        default_input = repo_root / "reverse/build_32/extracted/software.bin"
        default_output_name = "software.patched.r1mx.bin" if args.r1mx else "software.patched.bin"
        build_label = "Build 32"

    # Resolve input path
    if args.input is None:
        args.input = default_input
    elif not args.input.is_absolute():
        args.input = repo_root / args.input

    # Resolve output path
    if args.output is None:
        args.output = args.input.parent / default_output_name
    elif not args.output.is_absolute():
        args.output = repo_root / args.output

    if args.list:
        print(f"Patches for {build_label} ({len(patches)} total):")
        for p in patches:
            tag = " [bamboo-only]" if p.bamboo_only else ""
            print(f"  Phase {p.phase}  {hex(p.offset):<12}  {p.description}{tag}")
        return

    if args.probe is not None:
        add_patch(args.probe, args.input)
        return

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = bytearray(args.input.read_bytes())
    original_sha = sha256_of(bytes(data))
    print(f"[*] {build_label} input : {args.input} ({len(data):,} bytes)")
    print(f"    sha256: {original_sha}")

    phase1 = [p for p in patches if p.phase == 1]
    phase2 = [p for p in patches if p.phase == 2]
    active = [p for p in patches if args.phase is None or p.phase == args.phase]

    if not active:
        print(f"\n[!] No patches to apply (phase filter: {args.phase}).", file=sys.stderr)
        return

    phase2_pending = [p for p in phase2 if args.phase is None or args.phase == 2]
    if not phase2_pending and args.phase is None:
        print(f"\n[i] {len(phase1)} Phase 1 patch(es) defined.")
        print( "    Phase 2 MMIO patches: none yet — add from debug session.")
        print( "    Workflow:")
        print( "      Terminal 1: ./scripts/qemu_boot.sh --patched --debug")
        print( "      Terminal 2: r2 -a ppc -b 32 -e cfg.bigendian=true \\")
        print( "                     -D gdb gdb://localhost:1234 \\")
        print( "                     -i scripts/r2_debug.r2")
        print( "    On crash: python3 scripts/patch_firmware.py --probe 0x<PC>")
        print()

    print(f"[*] Applying {len(active)} patch(es) (phase={args.phase or 'all'}"
          f"{', skip-bamboo-only' if args.r1mx else ''})…")
    count, warnings = apply_patches(data, active, phase=args.phase,
                                    skip_bamboo_only=args.r1mx)

    for w in warnings:
        print(f"  [!] {w}", file=sys.stderr)

    patched_sha = sha256_of(bytes(data))
    args.output.write_bytes(data)

    print(f"[*] Applied {count}/{len(active)} patches")
    print(f"[*] Output : {args.output}")
    print(f"    sha256: {patched_sha}")


if __name__ == "__main__":
    main()
