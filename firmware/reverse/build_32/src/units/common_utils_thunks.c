/* common_utils_thunks.c -- reconstructed app_modules/common "utils.h" thunks.
 *
 * Module  : app_modules/common (utils.h)   Provenance: red (source-path xref)
 * Fidelity: byte_exact (target)
 *
 * A family of tiny forwarding thunks that each inject the address of the string
 * "utils.h" (0x00d2db9c -- the __FILE__ of the header that defines the inlined
 * helper/assert) into one argument register and tail-into a worker, preserving the
 * return address across the call. This is the classic expansion of a logging/assert
 * helper that is `inline` in utils.h: every translation unit that uses it gets its
 * own copy whose embedded __FILE__ is "utils.h" (the header), and the worker is the
 * out-of-line implementation (the formatter / assert-failed handler).
 *
 * Each thunk differs only in WHICH argument slot carries the file pointer and which
 * incoming arguments pass through unchanged -- determined from the disassembly:
 *
 *   addr        worker        file in   incoming passthrough -> call
 *   0x004caf48  FUN_004b7bd8  r6 (#4)   r3,r4,r5  -> w(a,b,c, "utils.h")
 *   0x004caf70  FUN_004b600c  r5 (#3)   r3,r4     -> w(a,b,    "utils.h")
 *   0x004caf98  FUN_004b4b80  r3 (#1)   --        -> w("utils.h")
 *   0x004cafc0  FUN_004b50dc  r4 (#2)   r3        -> w(a,      "utils.h")
 *   0x004cafe8  FUN_004c9238  r3 (#1)   r3->r4    -> w("utils.h", a)
 *
 * The compiler keeps a frame (mflr/stwu -16/stw r0,20(r1) ... lwz/mtlr/blr) rather
 * than sibling-calling: the worker's return value (r3) is propagated unchanged, and
 * these were built without sibcall optimization. Reconstructed and verified
 * BYTE-IDENTICAL with the original compiler (ccppc 3.4.4, powerpc-wrs-vxworks):
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
 *       units/common_utils_thunks.c
 *
 * The "utils.h" pointer is supplied as a linker symbol (units/data_symbols.ld,
 * D_00d2db9c) so ccppc materializes it with the original lis/addi (@ha/@l) pair.
 */

/* The __FILE__ string "utils.h" at 0x00d2db9c (see data_symbols.ld). */
extern const char D_00d2db9c[];
#define FILE_UTILS_H (D_00d2db9c)

/* Out-of-line workers (the real implementations behind the inlined helper). The
 * final pointer argument of each is the source-file string. */
extern int FUN_004b7bd8(int a, int b, int c, const char *file);
extern int FUN_004b600c(int a, int b, const char *file);
extern int FUN_004b4b80(const char *file);
extern int FUN_004b50dc(int a, const char *file);
extern int FUN_004c9238(const char *file, int a);

/* 0x004caf48: file in r6 (4th arg); r3,r4,r5 pass through. */
int FUN_004caf48(int a, int b, int c)
{
    return FUN_004b7bd8(a, b, c, FILE_UTILS_H);
}

/* 0x004caf70: file in r5 (3rd arg); r3,r4 pass through. */
int FUN_004caf70(int a, int b)
{
    return FUN_004b600c(a, b, FILE_UTILS_H);
}

/* 0x004caf98: file is the only argument (r3). */
int FUN_004caf98(void)
{
    return FUN_004b4b80(FILE_UTILS_H);
}

/* 0x004cafc0: file in r4 (2nd arg); r3 passes through. */
int FUN_004cafc0(int a)
{
    return FUN_004b50dc(a, FILE_UTILS_H);
}

/* 0x004cafe8: incoming r3 moves to r4 (2nd arg); file goes in r3 (1st arg). */
int FUN_004cafe8(int a)
{
    return FUN_004c9238(FILE_UTILS_H, a);
}
