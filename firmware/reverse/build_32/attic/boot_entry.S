#
# boot_entry.S -- RED ONE MX firmware reset vector and halt loop
#
# PowerPC 405GP, big-endian, flat binary, load base 0x00000000.
#
# Assemble with:
#   powerpc-linux-gnu-as -a32 -mbig -mppc boot_entry.S -o boot_entry.o
#
# IMPORTANT: Use bare register numbers (0, 1, 3, 4 ...) NOT r-prefixed
# names (r0, r1 ...) -- the -mppc dialect treats r4 as a symbol, not a reg.
#
# PPC405-specific instructions not in mainline binutils are encoded as .long:
#   iccci  r0, r0   -> 0x7C00078C
#   dccci  r0, r3   -> 0x7C001B8C
#   mtesr  r4       -> 0x7C94F3A6  (ESR  SPR 0x3D4)
#   mticcr r4       -> 0x7C9BFBA6  (ICCR SPR 0x3FB)
#   mtdccr r4       -> 0x7C9AFBA6  (DCCR SPR 0x3FA)
#   mttcr  r4       -> 0x7C9AF3A6  (TCR  SPR 0x3DA)
#
    .section .text, "ax"
    .global romInit
    .global halt_loop
    .type   romInit,   @function
    .type   halt_loop, @function

# -----------------------------------------------------------------------
# romInit -- 0x00000000
# Verified byte-for-byte against software.bin build 32 v32.0.3.
# -----------------------------------------------------------------------
romInit:
    b       .L_romInit_entry        # skip padding word at 0x004
    .long   0x00000000              # 0x004: padding (invalid instruction)

.L_romInit_entry:
    # MSR = 0: disable all interrupts, exceptions, FP, translation
    li      4, 0
    mtmsr   4
    isync

    # Clear timebase
    mttbl   4
    mttbu   4

    # Clear cache/storage control SPRs (raw opcodes for PPC405-specific instrs)
    .long   0x7C9BFBA6              # mticcr r4  ICCR=0
    .long   0x7C9AFBA6              # mtdccr r4  DCCR=0
    mtspr   954, 4                  # SGR (0x3BA) = 0
    .long   0x7C94F3A6              # mtesr  r4  ESR=0
    .long   0x7C9AF3A6              # mttcr  r4  TCR=0
    mtspr   987, 4                  # TSR (0x3DB) = 0

    li      4, -1
    mtspr   984,  4                 # DCWR (0x3D8) = 0xFFFFFFFF
    mtspr   1008, 4                 # MMUCR/PID (0x3F0) = 0xFFFFFFFF

    # Enable I-cache prefetch: set bits 28-29 of SGR/DBCR0 (SPR 0x3B3 = 947)
    mfspr   0, 947
    oris    0, 0, 0x5000
    mtspr   947, 0

    # Invalidate instruction cache (PPC405-specific, raw opcode)
    .long   0x7C00078C              # iccci r0, r0

    # Invalidate data cache: 256 sets x 32 bytes = 8 KB
    li      3, 0
    li      4, 0x100
    mtctr   4
.L_dcache_inv_loop:
    .long   0x7C001B8C              # dccci r0, r3
    addi    3, 3, 32
    bdnz    .L_dcache_inv_loop

    # SGR=0 (non-guarded), ICCR bits 31:30=1 (cache lower 512MB)
    lis     4, 0
    addi    4, 4, 0
    mtspr   954, 4                  # SGR (0x3BA) = 0
    lis     4, -0x4000              # 0xC0000000 high halfword
    addi    4, 4, 0
    .long   0x7C9BFBA6              # mticcr r4  ICCR: cache lower 512MB
    isync

    # Temporary boot stack: SP = 0x00010000 - 0x10 = 0x0000FFF0
    # QEMU PATCH at file offset 0x84: bytes 3C200001 -> 3C200800
    # (moves SP to 0x07FFFFF0 to avoid collision with loaded binary)
    lis     1, 1                    # 3c200001 <- QEMU patch target
    addi    1, 1, 0
    addi    1, 1, -0x10             # SP = 0x0000FFF0

    # Clear boot-status flag at 0x4200
    lis     4, 0
    addi    4, 4, 0x4200
    li      3, 0
    stb     3, 0(4)

    # Call main VxWorks init with boot_mode=2
    li      3, 2
    bl      main_boot_init

    # Unreachable -- fatal halt if init returns
    bl      halt_loop
    eieio

# -----------------------------------------------------------------------
# halt_loop -- 0x00000124: b . (0x48000000)
# -----------------------------------------------------------------------
halt_loop:
    b       halt_loop

    .size romInit,   halt_loop - romInit
    .size halt_loop, 4
