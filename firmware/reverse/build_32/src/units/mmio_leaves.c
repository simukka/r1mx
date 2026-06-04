/* mmio_leaves.c — reconstructed ordered-MMIO accessor leaves (carve-out unit).
 *
 * These tiny helpers sit right after romInit (0x0ac..0x123) and wrap single
 * memory accesses in PPC `eieio` storage-ordering barriers — the classic
 * Xilinx Xil_In8/Xil_Out8 pattern.
 *
 * Reconstructed from software.bin and verified BYTE-IDENTICAL to the original
 * when built with:  -mcpu=405 -O2 -ffreestanding -nostdlib  (see scripts/relink.py).
 * This is the proof that proprietary code lifted back to C rebuilds into the
 * exact same firmware machine code.
 *
 * NOTE: the 16/32-bit siblings (0x0c4.. lhzx/sthx/lwzx/stwx) use *indexed*
 * loads/stores in the original; plain C emits lhz/sth/lwz/stw, so they are not
 * byte-identical from C and are intentionally left as blob for now.
 */
typedef unsigned char u8;

/* 0x000000ac: eieio ; lbz r3,0(r3) ; blr  — ordered MMIO read8 */
u8 FUN_000000ac(volatile u8 *p)
{
    __asm__ volatile("eieio");
    return *p;
}

/* 0x000000b8: stb r4,0(r3) ; eieio ; blr  — ordered MMIO write8
 * (PPC ABI: first arg r3 = ptr, second arg r4 = value) */
void FUN_000000b8(volatile u8 *p, u8 v)
{
    *p = v;
    __asm__ volatile("eieio");
}
