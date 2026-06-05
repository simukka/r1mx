/*
 * patches.S -- RED ONE MX Build 32 firmware patches as toolchain-built source.
 *
 * Migrated from legacy firmware/scripts/patch_firmware.py.  Each patch is a section
 * .patch_<fileoffset> whose bytes overlay the base image (extracted/software.bin) at
 * that offset.  The Makefile assembles the -D-selected groups, then objcopy/dd each
 * section onto a copy of the base image.
 *
 * Groups (define to INCLUDE): GROUP_CPU_CORE GROUP_SNAPSHOT_DATA GROUP_DISPATCH_SCAFFOLD
 *   GROUP_CRYPTO_BYPASS GROUP_DEVICE_GAP(bamboo;off for r1mx) INCLUDE_DISABLED(off)
 *
 * NECESSITY: 27 patches are tagged [REDUNDANT for dispatch] (bisected unnecessary), and
 * #1/#2/#3 are tagged [MOVED TO qemu-r1mx] (now supplied by the machine).  The default
 * `make r1mx` build excludes all of these (29 sections); `make full` keeps them (59).
 * The [REDUNDANT] patches were bisected to be
 * unnecessary to reach the boot dispatch+liveness state (the r1mx image boots
 * identically without them).  `make minimal` excludes them.  See re_reference §0.3.
 */

/* ===== CPU_CORE (5) ===== */
#ifdef GROUP_CPU_CORE
  /* #1 @0x00000084: Relocate romInit SP: lis r1,1 → lis r1,0x800 (SP=0x07FFFFF0) [MOVED TO qemu-r1mx 2026-06-02: implemented in hw/ppc/r1mx_virtex4.c r1mx_apply_boot_env_fixups; excluded from default build] */
  .section .patch_00000084,"a"
  .long 0x3c200800   /* lis r1, 0x800 */

  /* #2 @0x0036c388: NOP canary bne #1 (0x36C380 loop, tests 0x00E269A4) [MOVED TO qemu-r1mx 2026-06-02: implemented in hw/ppc/r1mx_virtex4.c r1mx_apply_boot_env_fixups; excluded from default build] */
  .section .patch_0036c388,"a"
  .long 0x60000000   /* nop */

  /* #3 @0x0036c394: NOP canary bne #2 (0x36C380 loop, tests 0x00E269A0) [MOVED TO qemu-r1mx 2026-06-02: implemented in hw/ppc/r1mx_virtex4.c r1mx_apply_boot_env_fixups; excluded from default build] */
  .section .patch_0036c394,"a"
  .long 0x60000000   /* nop */

  /* #62 @0x00000700: Replace fn_0700 Program Exception handler (li r4,0; bl fn_0B8; li r29,0; b fn_0658) with rfi skip handler (mfspr r2,SRR0; addi r2,r2,4; mtspr SRR0,r2; rfi): original handler corrupts [r3] via fn_0B8 (r3 holds ROM addr or 0 in QEMU) and uses fn_0x5a4 stack epilogue which reads wrong LR when exception fires outside fn_0x5a4 context, causing SP to grow at 2.8 MB/s; rfi skip handler advances SRR0 past the faulting instruction and returns cleanly [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00000700,"a"
  .long 0x7c5a02a6   /* mfspr r2, 0x1a */
  .long 0x38420004   /* addi r2, r2, 4 */
  .long 0x7c5a03a6   /* mtspr 0x1a, r2 */
  .long 0x4c000064   /* rfi */

  /* #63 @0x00000734: NOP bctrl at 0x734 in fn_0x5a4 hardware-dispatch path: CTR=mem[0xe1c314]=0 (BSS not yet initialised) causes bctrl to jump to address 0x0 = romInit restart; NOP allows fall-through to r29=0 / b fn_0658 which returns hardware-unavailable (0) to the caller [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00000734,"a"
  .long 0x60000000   /* nop */

#endif /* GROUP_CPU_CORE */

/* ===== DEVICE_GAP (5) ===== */
#ifdef GROUP_DEVICE_GAP
  /* #37 @0x0001b9e0: NOP XUartLite TX-FULL poll loop in fn_1b9b0 (0xe0600008 unmapped in QEMU bamboo → reads 0xFFFFFFFF → bit3=TX_FULL=1 → infinite spin) */
  .section .patch_0001b9e0,"a"
  .long 0x60000000   /* nop */

  /* #38 @0x0001b9ec: NOP XUartLite TX-FIFO write in fn_1b9b0 (0xe0600004 unmapped in QEMU bamboo → write triggers Machine Check at 0x10 → romInit re-runs → infinite boot loop) */
  .section .patch_0001b9ec,"a"
  .long 0x60000000   /* nop */

  /* #39 @0x0001b9d8: NOP XUartLite status read in fn_1b9b0 (0xe0600008 unmapped → Machine Check per character through VxWorks MChk handler; result unused after Patch #37 killed the TX-FULL poll loop) */
  .section .patch_0001b9d8,"a"
  .long 0x60000000   /* nop */

  /* #40 @0x00009b9c: NOP error-counter write to 0xe0be00 in fn_9b78 early-return path (0x9b9c): unmapped MMIO write triggers Machine Check → VxWorks restart loop; counter is optional telemetry */
  .section .patch_00009b9c,"a"
  .long 0x60000000   /* nop */

  /* #41 @0x00009bc0: NOP error-counter write to 0xe0be00 in fn_9b78 normal path (0x9bc0): same unmapped MMIO address as Patch #40; RAM log stores above remain intact */
  .section .patch_00009bc0,"a"
  .long 0x60000000   /* nop */

#endif /* GROUP_DEVICE_GAP */

/* ===== SNAPSHOT_DATA (39) ===== */
#ifdef GROUP_SNAPSHOT_DATA
  /* #5 @0x0036c3ac: Skip BSS zero-fill memset: QEMU RAM is already zero; saves ~15 s of emulated stw loop */
  .section .patch_0036c3ac,"a"
  .long 0x60000000   /* nop */

  /* #6 @0x00e26d2c: Zero bogus restart callback at 0xE26D2C: value 0x8 was mistaken for a fn ptr to ROM-init (0x0008), causing unconditional restart loop in fn_36FA7C */
  .section .patch_00e26d2c,"a"
  .long 0x00000000

  /* #7 @0x00e293b4: Null C++ RTTI table ptr at 0xE293B4: value 0xE38B4C is a typeinfo table (illegal instr), not a function; nulling causes cmpwi/beq in fn_36D9A4 to skip the bctrl */
  .section .patch_00e293b4,"a"
  .long 0x00000000

  /* #8 @0x00e293bc: Null C++ type-dispatch ptr at 0xE293BC (struct+0x20): 0x5477B8 corrupts stack via shared tail 0x547474 (addi r1,r1,0x10 assumes 0x10 frame but callers alloc 0x20) */
  .section .patch_00e293bc,"a"
  .long 0x00000000

  /* #9 @0x00e293b0: Null C++ type-dispatch ptr at 0xE293B0 (struct+0x14): 0x5470E8 corrupts stack via shared tail 0x547474 in fn_36DA74's second bctrl; nulling causes cmpwi/beq to skip it */
  .section .patch_00e293b0,"a"
  .long 0x00000000

  /* #10 @0x00388280: Guard bcopy count load: replace 'lwz r5,0x14(r10)' with 'cmpwi r10,0' so NULL r10 sets EQ for the beq skip below (Patch #10) [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00388280,"a"
  .long 0x2c0a0000   /* cmpwi r10, 0 */

  /* #11 @0x00388284: Guard bcopy call: replace 'add r4,r4,r11' with 'beq 0x388294' to skip bl bcopy when r10=0 (Patch #11) [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00388284,"a"
  .long 0x41820010   /* beq 0x388294 */

  /* #12 @0x003878cc: Unconditional branch at fn_387834+0x98 to its own epilogue: both the beq-taken (0x387B0C) and fallthrough (0x3878D0) paths crash when r26=2; caller discards return value [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_003878cc,"a"
  .long 0x48000208   /* b 0x387ad4 */

  /* #13 @0x0036e028: Bypass corrupted bctrl at 0x36E038: *(0xE2932C)=0x38826C (wrong vtable, caused by Patches #7-#9). bctrl→0x38826C loops forever (CTR=3.7M→0→wrap→∞). Convert conditional beq to unconditional b so the dispatch is always skipped. */
  .section .patch_0036e028,"a"
  .long 0x48000014   /* b 0x36e03c */

  /* #14 @0x0036e11c: Bypass 2nd corrupted bctrl dispatch at 0x36E12C: *(0xE2932C)=0x38826C → infinite loop. Confirmed via LR=0x36E130 after Patch #13. */
  .section .patch_0036e11c,"a"
  .long 0x48000014   /* b 0x36e130 */

  /* #15 @0x0036dc24: Bypass 3rd corrupted bctrl at 0x36DC2C: beq→b at 0x36DC24 skips bctrl that loads CTR=*(0xE2932C)=0x38826C. */
  .section .patch_0036dc24,"a"
  .long 0x480000cc   /* b 0x36dcf0 */

  /* #16 @0x0036dcd8: Bypass 4th corrupted bctrl at 0x36DCEC: beq→b at 0x36DCD8 skips bctrl. */
  .section .patch_0036dcd8,"a"
  .long 0x48000018   /* b 0x36dcf0 */

  /* #17 @0x00370e88: Bypass 5th corrupted bctrl at 0x370EDC: beq→b at 0x370E88. */
  .section .patch_00370e88,"a"
  .long 0x4800005c   /* b 0x370ee4 */

  /* #18 @0x00370ed0: Bypass 6th corrupted bctrl at 0x370EE0: beq→b at 0x370ED0. */
  .section .patch_00370ed0,"a"
  .long 0x48000014   /* b 0x370ee4 */

  /* #19 @0x00370f4c: Bypass 7th corrupted bctrl at 0x370FD0: beq→b at 0x370F4C. */
  .section .patch_00370f4c,"a"
  .long 0x4800008c   /* b 0x370fd8 */

  /* #20 @0x00370fc4: Bypass 8th corrupted bctrl at 0x370FD4: beq→b at 0x370FC4. */
  .section .patch_00370fc4,"a"
  .long 0x48000014   /* b 0x370fd8 */

  /* #21 @0x00e26d38: Null BSS sentinel at 0xE26D38: 0xFFFFFFFF → 0 (uninitialized callback, BSS memset was patched away) */
  .section .patch_00e26d38,"a"
  .long 0x00000000

  /* #22 @0x00e26ddc: Null BSS sentinel at 0xE26DDC [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e26ddc,"a"
  .long 0x00000000

  /* #23 @0x00e27000: Null BSS sentinel at 0xE27000 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e27000,"a"
  .long 0x00000000

  /* #24 @0x00e276b8: Null BSS sentinel at 0xE276B8 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e276b8,"a"
  .long 0x00000000

  /* #25 @0x00e27bd4: Null BSS sentinel at 0xE27BD4 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e27bd4,"a"
  .long 0x00000000

  /* #26 @0x00e29438: Null BSS sentinel at 0xE29438 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e29438,"a"
  .long 0x00000000

  /* #27 @0x00e2a3c8: Null BSS sentinel at 0xE2A3C8 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2a3c8,"a"
  .long 0x00000000

  /* #28 @0x00e2a748: Null BSS sentinel at 0xE2A748 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2a748,"a"
  .long 0x00000000

  /* #29 @0x00e2a918: Null BSS sentinel at 0xE2A918 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2a918,"a"
  .long 0x00000000

  /* #30 @0x00e2a994: Null BSS sentinel at 0xE2A994 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2a994,"a"
  .long 0x00000000

  /* #31 @0x00e2a9b4: Null BSS sentinel at 0xE2A9B4 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2a9b4,"a"
  .long 0x00000000

  /* #32 @0x00e2b590: Null BSS sentinel at 0xE2B590 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2b590,"a"
  .long 0x00000000

  /* #33 @0x00e2b7d8: Null BSS sentinel at 0xE2B7D8 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00e2b7d8,"a"
  .long 0x00000000

  /* #36 @0x000062cc: NOP null bctrl in fn_6288: fn_2748 clears *(r30+64) as side-effect, making CTR=0; bctrl→0x0 resets CPU. NOP allows retry/exit logic at 0x62D0 to handle the empty-queue case. */
  .section .patch_000062cc,"a"
  .long 0x60000000   /* nop */

  /* #42 @0x00548d80: NOP bl fn_4a6438 in fn_548d78: skips fn_4a6438→fn_4a5f00 crash (bctrl to 0x203c6000 outside 256MB QEMU RAM). fn_548d78 next does li r3,0 so fn_4a6438 return value is irrelevant. */
  .section .patch_00548d80,"a"
  .long 0x60000000   /* nop */

  /* #43 @0x00548d88: Replace b 0x548b04 with blr in fn_548d78: fn_548b04 epilogue expects 316-byte frame but fn_458a14 only allocates 16 bytes → reads garbage LR and crashes. blr correctly returns to fn_458a14's LR (0x458a44). NOTE: fn_548d78 is NOT called at runtime — *(0xe29310) is set to 0x37cd4c (not 0x548d78) by init code at 0x36cc64. This patch is harmless dead-code safety. */
  .section .patch_00548d88,"a"
  .long 0x4e800020   /* blr */

  /* #44 @0x00458a40: fn_458a14 bctrl→li r3,0: dispatch table *(0xe29310)=0x37cd4c at runtime (epilogue of 40-byte-frame fn_37cc94). Calling it from fn_458a14's 16-byte frame corrupts stack and crashes. usrInit ignores return value so returning 0 is safe. */
  .section .patch_00458a40,"a"
  .long 0x38600000   /* li r3, 0 */

  /* #45 @0x0044c720: NOP self-referential bctrl in fn_44c660: *(0xe9bf80)=0x44c70c at runtime points mid-function → infinite loop. Guard bne at 0x44c6f0 should skip this call but guard value 0xe9bffc is set by driver init. NOP skips the bad call; fn falls through to b 0x44c728. */
  .section .patch_0044c720,"a"
  .long 0x60000000   /* nop */

  /* #46 @0x0044c6a8: NOP null-deref stw at fn_44c660+0x48: r12=*(0xeac3e0)=NULL → stw r11,0x7c(r12=0) corrupts PPC405 Machine Check vector at 0x7c, causing infinite Program Check exception storm. NOP prevents the corrupt write. */
  .section .patch_0044c6a8,"a"
  .long 0x60000000   /* nop */

  /* #51 @0x00e0c37c: Zero live-camera sysPhysMemTop cache at 0xE0C37C: fn_d87c returns this cached value directly when non-zero, yielding 0x395944A3 (outside QEMU 256MB RAM). Zeroing forces fn_d87c fallback: lis r3,0x1000 → 0x10000000 (256MB top). */
  .section .patch_00e0c37c,"a"
  .long 0x00000000

  /* #52 @0x00e0c380: Zero live-camera sysMemTop cache at 0xE0C380: fn_d8a0 returns this cached value immediately when non-zero, yielding 0x4CCECBD7 (~1.2GB, outside QEMU 256MB RAM). usrInit passes this to kernelInit as the heap object pointer; fn_5b0ff4 then accesses *(ptr+0x70) → ISI crash. Zeroing forces fn_d8a0 to call fn_d87c and compute heapEnd = 0x0FF9C000 (well within QEMU RAM). */
  .section .patch_00e0c380,"a"
  .long 0x00000000

  /* #53 @0x00e2942c: Zero pre-seeded intCnt at 0xE2942C: live-camera snapshot value 0x00552F30 causes taskInit (fn_5b231c) to return -1 for every task, making kernelInit fail → 0x124 spin-loop. VxWorks exception entry/exit (0x36eb38/0x36eea8) correctly maintains this counter once it starts at 0. */
  .section .patch_00e2942c,"a"
  .long 0x00000000

  /* #65 @0x00371c9c: NOP bne in fn_371c74: suppresses indirect call via corrupt fn-ptr at BSS[0xe293f4]=0x542974 (mid-epilogue of fn_542910); the bctrl over-unwinds r1 by 0x10, corrupting fn_371cd0's frame and causing blr→0x0 reset loop; NOP forces the safe r31=-1 path [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00371c9c,"a"
  .long 0x60000000   /* nop */

#endif /* GROUP_SNAPSHOT_DATA */

/* ===== DISPATCH_SCAFFOLD (12) ===== */
#ifdef GROUP_DISPATCH_SCAFFOLD
  /* #47 @0x005b586c: fn_5b57b0: replace lwz r11,0xc(r3) with lis r11,0x46. First half of two-instruction sequence to load 0x0046bfec (stw r4,0(r3);blr) into r11, bypassing BSS vtable ptr *(0x010d0590)=0 that would cause a null-deref ISI crash. */
  .section .patch_005b586c,"a"
  .long 0x3d600046   /* lis r11, 0x46 */

  /* #48 @0x005b5874: fn_5b57b0: replace lwz r11,0x10(r11) with ori r11,r11,0xbfec. Completes r11=0x0046bfec. The subsequent bctrl calls stw-r4-0(r3);blr which stores TCB+0x40 into *(0x010d0584), satisfying the fn_5aaf5c spin-loop and allowing the scheduler to proceed. */
  .section .patch_005b5874,"a"
  .long 0x616bbfec   /* ori r11, r11, 0xbfec */

  /* #49 @0x005b5964: fn_5b58a8: replace lwz r11,0xc(r3) with lis r11,0x46. First half of two-instruction sequence to load 0x0046bfec into r11, bypassing BSS vtable ptr *(0x010d0590)=0. [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_005b5964,"a"
  .long 0x3d600046   /* lis r11, 0x46 */

  /* #50 @0x005b596c: fn_5b58a8: replace lwz r11,0x18(r11) with ori r11,r11,0xbfec. Completes r11=0x0046bfec. The bctrl calls stw-r4-0(r3);blr which writes TCB+0x40 into *(0x010d0584) (idempotent). fn_5b58a8 epilogue then sets bit 4 of *(TCB+0x70). [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_005b596c,"a"
  .long 0x616bbfec   /* ori r11, r11, 0xbfec */

  /* #54 @0x005ab128: fn_5aaf5c scheduler: replace lwz r31,0xd4c(r29) with li r31,0 to avoid null-ptr deref. When root task TCB+0x94=0, *(0+0xD4C)=0x9001004c (boot code) is misread as a TCB address, causing rfi to PC=0 → 0x700 crash. Forcing r31=0 makes the existing beq at 0x5ab130 skip preemption and select the workQ-head task (root task, 0x0ff9bd30) directly. */
  .section .patch_005ab128,"a"
  .long 0x3be00000   /* li r31, 0 */

  /* #55 @0x00371d64: Fix initial root-task PC: addi r12,r12,0x1aec → 0x1a8c in fn_371cd0 (0x381aec is fn_381a8c epilogue; dispatching there hits blr with LR=0 → crash. 0x381a8c is the correct prologue entry). */
  .section .patch_00371d64,"a"
  .long 0x398c1a8c   /* addi r12, r12, 0x1a8c */

  /* #56 @0x00381ad0: NOP fast-exit branch at fn_381a8c+0x44: bc 4,30 skips to epilogue when r4 (task descriptor) != 0. At first dispatch r4=ctx+0x10=0x0dcf5120 (non-zero), so the fast-exit fires before any descriptor processing. NOP forces the normal bl 0x381a38 path always. [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00381ad0,"a"
  .long 0x60000000   /* nop */

  /* #57 @0x00371d6c: fn_371cd0 root-task setup: replace 'li r11,1' with 'stw r12,0x244(r31)' to initialise ctx+0x84 (LR slot, TCB+0x244) with r12=0x381a8c (the wrapper prologue PC set by #53a). Without this, ctx+0x84=0 → hardware LR=0 at dispatch → fn_381a8c's mflr+blr returns to 0x0 → crash. Side-effect: ctx+0x9c flag becomes 0 (r11 remains 0 from li r11,0 at 0x371d48); SPR945 is set to 0 at dispatch (non-critical). */
  .section .patch_00371d6c,"a"
  .long 0x919f0244   /* stw r12, 0x244(r31) */

  /* #58 @0x0038042c: fn_38038c overflow-path redirect (part 1/2): replace 'mr r3,r29' (prepare fn_38029c arg) with 'li r31,0' to zero r31 before the unconditional return in patch #54b. When the hash accumulator overflows the table-size limit (always bogus because r5=NULL makes *(r5) read the PPC reset vector 0x48000008), r31 is forced to 0 so the output buffer receives 0, causing fn_381824 to see r11=0 and exit cleanly. [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_0038042c,"a"
  .long 0x3be00000   /* li r31, 0 */

  /* #59 @0x00380430: fn_38038c overflow-path redirect (part 2/2): replace 'bl 0x38029c' (fn_38029c resize call) with 'b 0x380404' (unconditional branch to return path). Combined with patch #54a (li r31,0), this ensures r31=0 is stored to the output buffer on every hash overflow, regardless of the descriptor content or r29 value. fn_381824 then reads r11=0 from SP+8, which satisfies the 'cmpli r11,7 / bng 0x381910' exit at 0x381874-0x381878. [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00380430,"a"
  .long 0x4bffffd4   /* b 0x380404 */

  /* #60 @0x00371d5c: NOP beq at 0x371d5c in fn_371cd0: prevents skip of 0x371d60-0x371d74 (ctx+0x8c/ctx+0x84 = 0x381a8c via Patches #53a/#53c). Original branch sent execution to fn_371c74 path, which uses a corrupt BSS fn-ptr (0xe293f4=0x542974) and over-unwinds r1 causing blr→0x0 reset loop. NOP forces fall-through to the if-path block which correctly sets task PC/LR then branches to epilogue, bypassing fn_371c74 entirely. [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_00371d5c,"a"
  .long 0x60000000   /* nop */

  /* #61 @0x0037c33c: NOP bl fn_37d87c in usrRoot: deferred-constructor list walk loops on NULL head (list unpopulated because fn_381a8c was bypassed by Patch #55); list is intentionally empty in QEMU [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_0037c33c,"a"
  .long 0x60000000   /* nop */

#endif /* GROUP_DISPATCH_SCAFFOLD */

/* ===== CRYPTO_BYPASS (3) ===== */
#ifdef GROUP_CRYPTO_BYPASS
  /* #4 @0x0036fa1c: Skip bogus SSL verify-callback dispatch: fn_36F9F8 reads a string ptr (0xD7E680) as a function ptr; always branch past bctrl */
  .section .patch_0036fa1c,"a"
  .long 0x4800000c   /* b 0x36fa28 */

  /* #34 @0x005d552c: SSD bypass site A: replace bl IsCompatible with li r3,1; mr./bne at 0x5D5534 then branches to success path instead of setting INCOMPATIBLE state [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_005d552c,"a"
  .long 0x38600001   /* li r3, 1 */

  /* #35 @0x005d58e8: SSD bypass site B: replace bl IsCompatible with li r3,1; mr./beq at 0x5D58F0 then does NOT branch to the INCOMPATIBLE store at 0x5D5A28 [REDUNDANT for dispatch: bisected 2026-06-02; excluded by `make minimal`] */
  .section .patch_005d58e8,"a"
  .long 0x38600001   /* li r3, 1 */

#endif /* GROUP_CRYPTO_BYPASS */

/* ===== DISABLED_WRONG (1) ===== */
#ifdef INCLUDE_DISABLED
  /* #64 @0x005a8190: [DISABLED — WRONG] NOP bl taskActivate(0x5b0ff4) inside kernelInit; this NOP is what caused kernelInit to return → 0x124 halt. taskActivate triggers the first context switch into the root task; kernelInit must never return. See trace_dispatch_path.py. */
  .section .patch_005a8190,"a"
  .long 0x60000000   /* nop */

#endif /* INCLUDE_DISABLED */

