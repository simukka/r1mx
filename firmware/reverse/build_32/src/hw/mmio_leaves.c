/* mmio_leaves.c -- reconstructed ordered-MMIO accessor leaves (carve-out unit).
 *
 * The PPC405 BSP's ordered memory-access primitives: tiny leaves at 0x0ac..0x123
 * that wrap a single load/store in 'eieio' storage-ordering barriers (read = eieio
 * then load; write = store then eieio). The classic Xilinx Xil_In/Xil_Out or
 * VxWorks sysIn/sysOut pattern.
 *
 * Reconstructed from software.bin and verified BYTE-IDENTICAL to the original by
 * the ORIGINAL compiler (Wind River GNU GCC 3.4.4, powerpc-wrs-vxworks):
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py hw/mmio_leaves.c
 *
 * Two sub-families:
 *   - 8-bit (0x0ac/0x0b8): displacement addressing (lbz/stb 0(r3)). Plain C "*p"
 *     reproduces these exactly.
 *   - 16/32-bit (0x0c4..0x123): the original uses INDEXED addressing
 *     (lhzx/sthx/lwzx/stwx with rA=0) and byte-reversed indexed (lhbrx ... stwbrx,
 *     for little-endian PCI access). Plain C emits the displacement forms
 *     (lhz/lwz), so these are written as the inline asm they actually are -- the
 *     faithful, idiomatic representation of an ordered-MMIO primitive.
 */
typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned int   u32;

/* ---- 8-bit, displacement addressing -------------------------------------- */

/* 0x000000ac: eieio ; lbz r3,0(r3) ; blr  -- ordered MMIO read8 */
u8 FUN_000000ac(volatile u8 *p)
{
    __asm__ volatile("eieio");
    return *p;
}

/* 0x000000b8: stb r4,0(r3) ; eieio ; blr  -- ordered MMIO write8
 * (PPC ABI: first arg r3 = ptr, second arg r4 = value) */
void FUN_000000b8(volatile u8 *p, u8 v)
{
    *p = v;
    __asm__ volatile("eieio");
}

/* ---- 16/32-bit, native-endian indexed addressing ------------------------- */

/* 0x000000c4: eieio ; lhzx r3,0,r3 ; blr  -- ordered MMIO read16.
 * Returns u32: lhzx already zero-extends the halfword into the 32-bit GPR, and the
 * original hands that register back as-is (no clrlwi narrowing). */
u32 FUN_000000c4(volatile void *p)
{
    u32 v;
    __asm__ volatile("eieio\n\tlhzx %0,0,%1" : "=r"(v) : "r"(p) : "memory");
    return v;
}

/* 0x000000d0: sthx r4,0,r3 ; eieio ; blr  -- ordered MMIO write16 */
void FUN_000000d0(volatile void *p, u16 v)
{
    __asm__ volatile("sthx %1,0,%0\n\teieio" : : "r"(p), "r"(v) : "memory");
}

/* 0x000000dc: eieio ; lwzx r3,0,r3 ; blr  -- ordered MMIO read32 */
u32 FUN_000000dc(volatile void *p)
{
    u32 v;
    __asm__ volatile("eieio\n\tlwzx %0,0,%1" : "=r"(v) : "r"(p) : "memory");
    return v;
}

/* 0x000000e8: stwx r4,0,r3 ; eieio ; blr  -- ordered MMIO write32 */
void FUN_000000e8(volatile void *p, u32 v)
{
    __asm__ volatile("stwx %1,0,%0\n\teieio" : : "r"(p), "r"(v) : "memory");
}

/* ---- 16/32-bit, byte-reversed indexed (little-endian / PCI) -------------- */

/* 0x000000f4: eieio ; lhbrx r3,0,r3 ; blr  -- ordered MMIO read16, byte-swapped.
 * Returns u32 for the same reason as FUN_000000c4 (lhbrx zero-extends; no narrowing). */
u32 FUN_000000f4(volatile void *p)
{
    u32 v;
    __asm__ volatile("eieio\n\tlhbrx %0,0,%1" : "=r"(v) : "r"(p) : "memory");
    return v;
}

/* 0x00000100: sthbrx r4,0,r3 ; eieio ; blr  -- ordered MMIO write16, byte-swapped */
void FUN_00000100(volatile void *p, u16 v)
{
    __asm__ volatile("sthbrx %1,0,%0\n\teieio" : : "r"(p), "r"(v) : "memory");
}

/* 0x0000010c: eieio ; lwbrx r3,0,r3 ; blr  -- ordered MMIO read32, byte-swapped */
u32 FUN_0000010c(volatile void *p)
{
    u32 v;
    __asm__ volatile("eieio\n\tlwbrx %0,0,%1" : "=r"(v) : "r"(p) : "memory");
    return v;
}

/* 0x00000118: stwbrx r4,0,r3 ; eieio ; blr  -- ordered MMIO write32, byte-swapped */
void FUN_00000118(volatile void *p, u32 v)
{
    __asm__ volatile("stwbrx %1,0,%0\n\teieio" : : "r"(p), "r"(v) : "memory");
}
