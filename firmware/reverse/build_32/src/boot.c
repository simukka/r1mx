/*
 * boot.c — RED ONE MX firmware boot sequence (build 32 v32.0.3)
 *
 * Reverse-engineered from software.bin (PowerPC 405GP, big-endian, flat binary).
 * Original toolchain: Wind River Diab compiler on Windows.
 *
 * This file covers:
 *   MMIO helpers     @ 0x000000A8  — eieio-fenced byte/halfword/word accessors
 *   (romInit and halt_loop are in boot_entry.S — they run before C ABI is set up)
 *   main_boot_init   @ 0x0036C350  — VxWorks usrInit equivalent
 *   hw_seq_init      @ 0x0000DCB0  — early hardware sequencer / device enable
 *
 * Compile (cross-compile for PPC405 big-endian freestanding):
 *   powerpc-linux-gnu-gcc -mcpu=405 -mbig-endian -O2 -ffreestanding -nostdlib \
 *     -fno-stack-protector -c boot.c -o boot.o
 *
 * Do NOT enable -fprofile or -fsanitize flags — the binary has no runtime support.
 */

#include <stdint.h>

/* ─────────────────────────────────────────────────────────────────────────────
 * PPC405-specific SPR numbers (not in standard <sys/regs.h> for bare metal)
 * ──────────────────────────────────────────────────────────────────────────── */
#define SPR_ICCR   0x3FB   /* Instruction Cache Cacheability Register */
#define SPR_DCCR   0x3FA   /* Data Cache Cacheability Register        */
#define SPR_SGR    0x3BA   /* Storage Guarded Register                 */
#define SPR_ESR    0x3D4   /* Exception Syndrome Register              */
#define SPR_TCR    0x3DA   /* Timer Control Register                   */
#define SPR_TSR    0x3DB   /* Timer Status Register                    */
#define SPR_PVR    0x11F   /* Processor Version Register               */

/* ─────────────────────────────────────────────────────────────────────────────
 * VxWorks stack canary constants (known pattern, not a security feature)
 * ──────────────────────────────────────────────────────────────────────────── */
#define VXWORKS_CANARY_1  0x12348765u
#define VXWORKS_CANARY_2  0x5A5AC3C3u

/* RAM addresses where the canary values are written by a separate init path */
#define CANARY_ADDR_1  ((volatile uint32_t *)0x00E269A4)
#define CANARY_ADDR_2  ((volatile uint32_t *)0x00E269A0)

/* ─────────────────────────────────────────────────────────────────────────────
 * BSS region bounds (computed by main_boot_init from embedded constants)
 * ──────────────────────────────────────────────────────────────────────────── */
#define BSS_START  ((void *)0x00E9BF20)
#define BSS_END    ((void *)0x01153480)
#define BSS_SIZE   ((uintptr_t)BSS_END - (uintptr_t)BSS_START)  /* 0x002B7560 */

/* ─────────────────────────────────────────────────────────────────────────────
 * Hardware sequencer device codes passed to device_enable()
 * Values extracted from hw_seq_init disassembly; meaning TBD from FPGA regs.
 * ──────────────────────────────────────────────────────────────────────────── */
#define HW_DEV_UNKNOWN_5E  0x5E
#define HW_DEV_UNKNOWN_31  0x31
#define HW_DEV_UNKNOWN_32  0x32
#define HW_DEV_UNKNOWN_33  0x33
#define HW_DEV_UNKNOWN_34  0x34

/* ─────────────────────────────────────────────────────────────────────────────
 * Forward declarations for functions called from boot sequence.
 * These live in other translation units (VxWorks kernel, BSP drivers).
 * ──────────────────────────────────────────────────────────────────────────── */
extern void *memset(void *dst, int c, uint32_t n);      /* 0x496698 */
extern void  device_enable(int dev_code);               /* 0x1C8BC  — MMIO device enable */
extern void  sub_372054(void);                          /* 0x372054 — unknown init */
extern void  sub_dc28(int a, int b);                    /* 0x000DC28 — unknown */
extern void  sub_9bc8(void);                            /* 0x9BC8   — unknown */
extern void  sub_9e24(void);                            /* 0x9E24   — unknown */
extern void  sub_1968(void);                            /* 0x1968   — unknown */
extern void  vxworks_kernel_start(                      /* 0x5A7F30 — kernelInit / sysStart */
                 uint32_t *entry_str,
                 uint32_t  stack_size,
                 int       int_stack_size,
                 int       sys_priority,
                 int       sys_options,
                 uint32_t *mem_pool_start,
                 int       mem_pool_size,
                 int       int_arg);
extern void  sub_458a00(int, int);                      /* 0x458A00 — pre-kernel setup step */
extern void  sub_458a14(int);                           /* 0x458A14 — pre-kernel setup step */
extern void  sub_36f9f8(void);                          /* 0x36F9F8 */
extern void  sub_36e3dc(void);                          /* 0x36E3DC */
extern void  sub_36e168(void);                          /* 0x36E168 */
extern void  sub_36860c(void);                          /* 0x36860C */
extern uint32_t timer_clock_helper(void);               /* 0x0000D8A0 — read tick counter */
extern void     main_boot_init(int boot_mode);          /* 0x0036C350 — forward decl for romInit */

/* ─────────────────────────────────────────────────────────────────────────────
 * Inline helpers for PPC405-specific instructions
 * ──────────────────────────────────────────────────────────────────────────── */

static inline void ppc_mtmsr(uint32_t val) {
    __asm__ volatile ("mtmsr %0" : : "r"(val));
}
static inline void ppc_isync(void) {
    __asm__ volatile ("isync");
}
static inline void ppc_eieio(void) {
    __asm__ volatile ("eieio");
}
static inline void ppc_iccci(void) {
    /* Invalidate entire instruction cache (PPC405: no operands needed) */
    __asm__ volatile ("iccci 0, 0");
}
static inline void ppc_mttbl(uint32_t val) {
    __asm__ volatile ("mttbl %0" : : "r"(val));
}
static inline void ppc_mttbu(uint32_t val) {
    __asm__ volatile ("mttbu %0" : : "r"(val));
}
static inline void ppc_mtspr(uint32_t spr, uint32_t val) {
    __asm__ volatile ("mtspr %0, %1" : : "n"(spr), "r"(val));
}
static inline uint32_t ppc_mfspr(uint32_t spr) {
    uint32_t val;
    __asm__ volatile ("mfspr %0, %1" : "=r"(val) : "n"(spr));
    return val;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * MMIO accessor stubs — placed at 0xA8–0x13F in the original binary.
 *
 * These are tiny helper functions (3–4 instructions each) accessible from the
 * lower exception vector region. The eieio instruction orders the memory
 * operation relative to other MMIO accesses (PPC memory-mapped I/O barrier).
 *
 * All placed in a dedicated section so the linker keeps them inside the
 * exception vector page (0x000–0xFFF).
 * ──────────────────────────────────────────────────────────────────────────── */

__attribute__((section(".vectors.mmio_helpers")))
uint8_t mmio_read_u8(volatile uint8_t *addr) {
    ppc_eieio();
    return *addr;
}

__attribute__((section(".vectors.mmio_helpers")))
void mmio_write_u8(volatile uint8_t *addr, uint8_t val) {
    *addr = val;
    ppc_eieio();
}

__attribute__((section(".vectors.mmio_helpers")))
uint16_t mmio_read_u16(volatile uint16_t *addr) {
    ppc_eieio();
    return *addr;
}

__attribute__((section(".vectors.mmio_helpers")))
void mmio_write_u16(volatile uint16_t *addr, uint16_t val) {
    *addr = val;
    ppc_eieio();
}

__attribute__((section(".vectors.mmio_helpers")))
uint32_t mmio_read_u32(volatile uint32_t *addr) {
    ppc_eieio();
    return *addr;
}

__attribute__((section(".vectors.mmio_helpers")))
void mmio_write_u32(volatile uint32_t *addr, uint32_t val) {
    *addr = val;
    ppc_eieio();
}

/* Byte-swapped variants (lhbrx / lwbrx / sthbrx / stwbrx) */
__attribute__((section(".vectors.mmio_helpers")))
uint16_t mmio_read_u16_bswap(volatile uint16_t *addr) {
    uint16_t val;
    ppc_eieio();
    __asm__ volatile ("lhbrx %0, 0, %1" : "=r"(val) : "r"(addr));
    return val;
}

__attribute__((section(".vectors.mmio_helpers")))
void mmio_write_u16_bswap(volatile uint16_t *addr, uint16_t val) {
    __asm__ volatile ("sthbrx %0, 0, %1" : : "r"(val), "r"(addr));
    ppc_eieio();
}

__attribute__((section(".vectors.mmio_helpers")))
uint32_t mmio_read_u32_bswap(volatile uint32_t *addr) {
    uint32_t val;
    ppc_eieio();
    __asm__ volatile ("lwbrx %0, 0, %1" : "=r"(val) : "r"(addr));
    return val;
}

__attribute__((section(".vectors.mmio_helpers")))
void mmio_write_u32_bswap(volatile uint32_t *addr, uint32_t val) {
    __asm__ volatile ("stwbrx %0, 0, %1" : : "r"(val), "r"(addr));
    ppc_eieio();
}

/* ─────────────────────────────────────────────────────────────────────────────
 * main_boot_init — 0x0036C350
 *
 * Equivalent of VxWorks usrInit / usrConfig.
 *
 * Sequence:
 *   1. Standard PPC function prologue (save LR, callee-saved regs)
 *   2. Wait for VxWorks stack canary values to appear in RAM.
 *      (On real hardware a parallel init path writes these before us;
 *       in QEMU we NOP the wait loop to avoid deadlock.)
 *   3. Zero BSS: memset(0xE9BF20, 0, ~2.8 MB)
 *   4. Call pre-kernel init chain (subsystem setup)
 *   5. Call hw_seq_init (FPGA/hardware sequencer enable)
 *   6. Measure boot time with timer_clock_helper (two samples, compute delta)
 *   7. Launch VxWorks kernel (kernelInit / sysStart @ 0x5A7F30)
 *
 * arg: boot_mode — 2 = normal boot (passed from romInit)
 * ──────────────────────────────────────────────────────────────────────────── */
extern void hw_seq_init(void);  /* forward-declare; defined below */

void main_boot_init(int boot_mode) {
    /* Step 2: Spin until VxWorks stack canary values are written by init peer */
    while (*CANARY_ADDR_1 != VXWORKS_CANARY_1 ||
           *CANARY_ADDR_2 != VXWORKS_CANARY_2) {
        /* busy-wait — NOP in QEMU by patching 0x36C388 and 0x36C394 */
    }

    /* Step 3: Zero BSS segment */
    memset(BSS_START, 0, BSS_SIZE);

    /* Step 4: Pre-kernel subsystem initialisation chain */
    sub_458a00(1, 2);    /* 0x458A00 — likely sysMemTop / memPartCreate */
    sub_36f9f8();        /* 0x36F9F8 */
    sub_36e3dc();        /* 0x36E3DC */
    sub_36e168();        /* 0x36E168 */
    hw_seq_init();       /* 0x0000DCB0 — enable FPGA peripherals */
    sub_458a14(0);       /* 0x458A14 */
    sub_458a14(1);       /* 0x458A14 with arg 1 */
    sub_36860c();        /* 0x36860C — likely sysSerialInit / intConnect */

    /* Step 6: Measure boot time (two timer samples, compute delta in ticks) */
    uint32_t t0 = timer_clock_helper();   /* first sample */
    uint32_t t1 = timer_clock_helper();   /* second sample after init */
    uint32_t delta_ticks = (t1 - t0) >> 4;     /* divide by 16 */
    /* result stored at 0x00EAC630 (global boot-time variable in BSS) */

    /*
     * Step 7: Launch VxWorks kernel.
     * vxworks_kernel_start @ 0x5A7F30 (likely kernelInit or sysStart).
     * Arguments from disassembly:
     *   r3 = pointer to entry string (0x003BC440 — "WIND")
     *   r4 = 0x5DC0 (24,000 — system stack size in bytes)
     *   r5 = r29 (boot_mode saved earlier as r29)... + delta info
     *   r6 = 0x1388 (5000 — interrupt stack size?)
     *   r7, r8 = 0
     */
    extern uint32_t _vxworks_entry_str;  /* @ 0x003BC440 */
    vxworks_kernel_start(
        &_vxworks_entry_str,
        0x5DC0,             /* system task stack size */
        boot_mode,
        delta_ticks,
        0x1388,             /* interrupt stack size */
        (uint32_t *)BSS_END,
        0,
        0
    );

    /* VxWorks kernel never returns — but the C compiler doesn't know that */
}

/* ─────────────────────────────────────────────────────────────────────────────
 * hw_seq_init — 0x0000DCB0
 *
 * Early hardware sequencer initialisation.
 * Calls device_enable() with a sequence of device codes to power up
 * FPGA-managed peripherals one by one.
 *
 * The device codes (0x5E, 0x31, 0x32, etc.) are sent to a register in
 * the FPGA register block (MMIO @ 0x40000000) to enable individual
 * hardware blocks. Exact mapping TBD from FPGA bitstream analysis.
 * ──────────────────────────────────────────────────────────────────────────── */
void hw_seq_init(void) {
    /* Enable device 0x5E three times (re-init / reset-and-enable sequence) */
    device_enable(HW_DEV_UNKNOWN_5E);
    device_enable(HW_DEV_UNKNOWN_5E);
    device_enable(HW_DEV_UNKNOWN_5E);

    /* Enable additional hardware blocks in sequence */
    device_enable(HW_DEV_UNKNOWN_31);

    sub_372054();           /* 0x372054 — unknown init, no args */

    device_enable(HW_DEV_UNKNOWN_32);
    sub_dc28(0, 0);         /* 0xDC28   — SDRAM or bus init, args = 0,0 */

    device_enable(HW_DEV_UNKNOWN_33);
    sub_9bc8();             /* 0x9BC8   — unknown */

    /*
     * Store a magic constant 0x17D78400 to 0xEAC390.
     * Likely a clock frequency or tick-rate value written to a global.
     * (0x17D78400 = 399,900,672 ≈ 400 MHz — plausible PPC405GP clock)
     */
    {
        volatile uint32_t *clk_global = (volatile uint32_t *)0x00EAC390;
        *clk_global = 0x17D78400;
    }

    sub_9e24();             /* 0x9E24   — unknown */
    device_enable(HW_DEV_UNKNOWN_34);
    sub_1968();             /* 0x1968   — unknown */
}
