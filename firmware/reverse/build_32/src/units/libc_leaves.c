/* libc_leaves.c -- reconstructed standard C-library leaf routines.
 *
 * These are vendor (VxWorks/Dinkum libc) functions, not RED code, so they are not
 * reconstruction *targets* per se -- but they are excellent byte-for-bit matching
 * tests: small, well-understood compiled C with real control flow and register
 * allocation. Matching them with the original compiler (ccppc 3.4.4) proves the
 * toolchain + flags reproduce genuine codegen, not just inline-asm leaves.
 *
 * Verify:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py units/libc_leaves.c
 */
typedef unsigned char u8;

/* 0x0039ac2c: memcmp(s1, s2, n) -> (int)s1[i] - (int)s2[i] at first differing byte.
 *
 * Frameless leaf. The original post-increments both pointers in the compare and
 * reloads the just-compared bytes via p1[-1]/p2[-1] on mismatch (lbz -1,...; subf),
 * so the reconstruction uses exactly that idiom. Args: r3=s1, r4=s2, r5=n.
 *
 * NEAR-MATCH (structure exact; loop form differs): the original uses a plain
 * `addic.`/`bne` decrement loop, but this ccppc emits a CTR `bdnz` loop and
 * -fno-branch-count-reg does NOT suppress it (verified: it has no effect even on a
 * trivial do-while). Conclusion: VxWorks libc is a PREBUILT Wind River vendor blob
 * built with different flags than the RED app, so it isn't reachable from our app
 * flag set -- and per the provenance model, vendor libc stays a blob anyway. Kept
 * here only as a funcmatch demo; flag-pinning must use RED app functions. */
int FUN_0039ac2c(const void *s1, const void *s2, int n)
{
    const u8 *p1 = (const u8 *)s1;
    const u8 *p2 = (const u8 *)s2;

    if (n == 0)
        return 0;
    do {
        if (*p1++ != *p2++)
            return p1[-1] - p2[-1];
    } while (--n);
    return 0;
}

/* 0x0039acec: a 3-arg tail wrapper -- calls FUN_0036cad0(a, c, b) with the 2nd and
 * 3rd arguments swapped, then returns the first argument unchanged. Non-leaf: the
 * stack frame + mflr/mtlr + a callee-saved reg exist solely to preserve `a` across
 * the call. The cross-function `bl 0x36cad0` resolves correctly through symbols.ld
 * (that word matches), but this is another vendor-libc NEAR-MATCH: the original uses
 * a 16-byte frame + r31, while our app flags give a 32-byte frame + r29 -- the same
 * "libc was built with different Wind River flags" story as memcmp above. For a
 * clean compiled-C byte-match on a real target, see units/red_app_proof.c. */
extern int FUN_0036cad0(unsigned a, unsigned b, unsigned c);

unsigned FUN_0039acec(unsigned a, unsigned b, unsigned c)
{
    FUN_0036cad0(a, c, b);
    return a;
}
