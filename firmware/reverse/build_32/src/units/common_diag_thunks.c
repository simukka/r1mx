/* common_diag_thunks.c -- reconstructed app_modules/common diagnostic-record thunks.
 *
 * Module  : app_modules/common (utils.h / "on/utils.cpp")   Provenance: red (source-path)
 * Fidelity: functional (see note) -- the simpler members are in common_utils_thunks.c
 *
 * Sibling of common_utils_thunks.c: these are the slightly larger members of the
 * same inlined-helper family. Each unpacks a small context object (passed by pointer
 * or as loose fields) and forwards it -- together with the source-file string -- to
 * an out-of-line diagnostic/log worker (FUN_004e2###). They differ in the worker,
 * the source-file string, and how the context is destructured:
 *
 *   0x004d82e8  FUN_004e26d8  "on/utils.cpp"  w(file, p[1], p[2], p[0], arg2)
 *   0x004d83c8  FUN_004e203c  "on/utils.cpp"  w(file, *(p[0]+8), p[1], p[2], p[0], arg2, arg3)
 *   0x004d8d58  FUN_004e2490  "utils.h"       w(file, arg2, arg1, arg3, arg4)
 *
 * In 0x004d82e8/0x004d83c8 the first parameter is a pointer to a 3-word record
 * {p[0], p[1], p[2]}; 0x004d83c8 additionally chases p[0] as a pointer and reads its
 * field at +8 (an object whose word 2 is, e.g., a type/id). 0x004d8d58 simply
 * reorders four loose arguments (note arg1 and arg2 swap positions).
 *
 * Source-file strings are linker symbols (data_symbols.ld, D_00d2dce4 / D_00d2db9c)
 * so the @ha/@l (lis/addi) materialization matches.
 *
 * FIDELITY NOTE -- functional, not byte_exact. funcmatch shows these reconstruct to
 * the SAME instructions with the SAME operands as the original, differing ONLY in the
 * scheduling order of two independent prologue instructions (e.g. `mr r7,r4` saving
 * the clobbered argument vs. `stw r0,20(r1)` saving LR). The order is a gcc
 * post-reload-scheduler (`-fschedule-insns2`, on at -O2 -- confirmed: disabling it
 * matches nothing) tie-break we could not steer from C source. The result is provably
 * behaviourally identical (same callee, same argument values), so these are
 * functional-tier; the byte difference is cosmetic instruction reordering. Reverify:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
 *       units/common_diag_thunks.c
 */

extern const char D_00d2dce4[];   /* "on/utils.cpp" */
extern const char D_00d2db9c[];   /* "utils.h"      */

extern int FUN_004e26d8(const char *file, int a, int b, int c, int d);
extern int FUN_004e203c(const char *file, int a, int b, int c, int d, int e, int f);
extern int FUN_004e2490(const char *file, int a, int b, int c, int d);

/* 0x004d82e8: record = rec[0..2]; forward as (file, rec[1], rec[2], rec[0], arg2). */
int FUN_004d82e8(int *rec, int arg2)
{
    return FUN_004e26d8(D_00d2dce4, rec[1], rec[2], rec[0], arg2);
}

/* 0x004d83c8: as above plus chase rec[0] as a pointer, reading its word at +8. */
int FUN_004d83c8(int *rec, int arg2, int arg3)
{
    return FUN_004e203c(D_00d2dce4, *(int *)(rec[0] + 8), rec[1], rec[2],
                        rec[0], arg2, arg3);
}

/* 0x004d8d58: reorder four loose arguments (arg1/arg2 swap), prepend "utils.h". */
int FUN_004d8d58(int arg1, int arg2, int arg3, int arg4)
{
    return FUN_004e2490(D_00d2db9c, arg2, arg1, arg3, arg4);
}
