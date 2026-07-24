/* upgrade_verify.c -- RED firmware-upgrade signature-verification path.
 *
 * Module: lib/libflashutils (extract.c) + the per-file verify gate. This is the
 * security-critical right-to-repair surface: these functions decide whether a
 * firmware image's RSA-1024 / MD5 signature (redone.2 / redone.4) is accepted before
 * the flash is erased and written. See ../../upgrade_install_analysis.md for the full
 * package format and the verify/install flow.
 *
 * Reconstructed byte-for-bit with the original compiler (ccppc 3.4.4); verify with
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py red/app_modules/flashutils/upgrade_verify.c
 *
 * Image functions are resolved at their absolute addresses via symbols.ld; data
 * (format strings) via data_symbols.ld so the @ha/@l (lis/addi) relocations match.
 *
 * VERIFY CALL GRAPH (traced from the disassembly; [R] = reconstructed in this file):
 *
 *   FUN_00210800  per-file verify dispatch                         [R, body byte-exact]
 *     -> FUN_0005e8a8()                      obtain verify context
 *     -> FUN_000af634  THE GATE              [R, functional-tier; one-line BYPASS here]
 *          -> FUN_000a8bdc  verifier orchestration (3196B C++/SJLJ; not reconstructed)
 *               -> new(0x78) + ctor          build a verifier object
 *               -> FUN_000a8138              trust-anchor lookup by name
 *                    -> FUN_0039ac2c (memcmp, std::string::compare)  [R in libc_leaves.c]
 *                    -> FUN_005fbc34 (map::find) -> FUN_000a6dd8 (process matched key)
 *               -> FUN_00232498 / vtable dispatch -> ... OpenSSL EVP_VerifyInit/Update/Final
 *               -> result = 0 on a valid signed match, else -1
 *     -> FUN_0005da9c(result == -1, ...)     log + raise global error flag 0xE9E85C
 *
 * The OpenSSL EVP_Verify* crypto (the "link against libcrypto" target) lives several
 * vtable hops below FUN_000a8bdc; tracing it to the leaf is the next reconstruction
 * step. The security DECISION, however, is entirely in FUN_000af634's return value.
 */

extern int  FUN_0005e8a8(void);                 /* obtain the per-verify context/handle */
extern int  FUN_000af634(int ctx, void *file);  /* run the RSA/MD5 verify; returns -1 on FAIL */
/* logger: (failed?, printf-style fmt, ...). Variadic -- its body does va_start over
 * the incoming stack args -- so the caller reserves an outgoing parameter-save area
 * (the original's frame is 24 bytes, not 16). Sets the global upgrade-error flag
 * 0xE9E85C on failure. */
extern void FUN_0005da9c(int failed, const char *fmt, ...);
extern char D_00d5bbcc[];                        /* log format string @0x00D5BBCC */

/* 0x00210800: verify one upgrade file and report the outcome.
 *
 * Runs the signature check (FUN_000af634) and forwards the result -- failed when it
 * returns -1 -- together with the file's name to the logger, which raises the global
 * upgrade-error flag on failure (so the master install flow then skips the flash).
 *
 * `file` points at a RED string-like object (short-string optimisation): the byte
 * length is at +0x18; the name characters are inline at +4, or, when the length
 * exceeds 15, on the heap via *(char**)(file+4).
 *
 * FIDELITY: body BYTE-IDENTICAL (every instruction 0x210814..0x210848 matches, incl.
 * the @ha/@l format-string reloc, the (result==-1) idiom, and the SSO branch). The
 * only diff is the frame size -- the original reserves a 24-byte frame (an 8-byte
 * outgoing param-save area its body never touches) where gcc here picks 16. That
 * reservation is a register-pressure/param-area codegen decision on call-heavy
 * functions, not a flag (no -mcall-X, -meabi, or -mno-prototype variant changes it);
 * it needs per-function source permutation to match exactly. Functional-tier now. */
void FUN_00210800(void *file)
{
    unsigned char *s = (unsigned char *)file;
    int ctx    = FUN_0005e8a8();
    int result = FUN_000af634(ctx, file);

    const char *name = (const char *)(s + 4);
    if (*(unsigned int *)(s + 0x18) > 15)
        name = *(const char **)(s + 4);

    FUN_0005da9c(result == -1, D_00d5bbcc, name);
}

/* ========================================================================== *
 *  The verify GATE -- FUN_000af634
 * ========================================================================== */

/* The original C++ helpers this gate uses (resolved at their absolute addrs). */
extern int  FUN_000a8bdc(int ctx, void *file, void *out);  /* THE verifier (extract.c) */
extern void FUN_003d1214(void *eh);   /* _Unwind_SjLj_Register   -- enter try-scope */
extern void FUN_003d12b8(void *eh);   /* _Unwind_SjLj_Unregister -- leave try-scope */
extern void FUN_005e8e00(void *elem); /* destroy one 0x1C-byte error-vector element */
extern void FUN_00245c34(void *buf);  /* operator delete(buf) for the vector storage */

/* gcc SJLJ exception "function context" built on the stack. The image is compiled
 * with setjmp/longjmp exceptions (re_reference: gcc_personality_sj0), so each try
 * region pushes one of these onto a per-thread chain and pops it on exit. We model
 * the fields the gate writes; the landing pad 0x25710C is this function's catch. */
struct sjlj_func_context {
    void     *prev;            /* +0x00  previous context in the chain              */
    int       active;          /* +0x04  =1 while the protected region is live      */
    /* +0x08 begins a setjmp jmp_buf; the gate also stores: handler=0x25710C @+0x18,
     * an LSDA/personality word 0xE975FA @+0x1C, &jmpbuf @+0x20, 0xBF728 @+0x24,
     * the caller SP @+0x28 and this SP @+0x2C. Exact layout is gcc-internal. */
    unsigned  _eh[16];
};

/* A local std::vector gathered during verification: 0x1C-byte (28) records between
 * begin and end, capacity at cap. Emptied on the way out (each element destroyed,
 * then the storage freed) on both the normal and the exception path. */
struct err_vec { unsigned char *begin, *end, *cap; };

/* 0x000AF634: the firmware-upgrade signature GATE.
 *
 * Runs the RSA-1024 / MD5 verifier (FUN_000a8bdc -> OpenSSL EVP_Verify*, see
 * upgrade_install_analysis.md) inside a try-scope, cleans up the local error vector,
 * and RETURNS THE VERIFIER'S STATUS. The per-file dispatcher (FUN_00210800 above)
 * treats a return of -1 as failure and raises the global upgrade-error flag, which
 * makes the installer skip the flash. So this return value is the single decision
 * that accepts or rejects an image.
 *
 * RIGHT-TO-REPAIR / BYPASS: to install your own (unsigned or self-signed) firmware,
 * make this gate return a non-(-1) status -- e.g. `return 0;` -- so every signature
 * "passes". That is the documented in-RAM WDB patch (overwrite 0xAF634 with
 * `li r3,0; blr`); the clean source-level equivalent is the one-line change marked
 * below. (The principled alternative is to re-key: replace the embedded /roFs
 * public key with your own and keep verifying -- see the analysis doc.)
 *
 * FIDELITY: functional/readable tier. Byte-exact reconstruction is impractical here
 * because the SJLJ exception scaffolding (the function-context stores, landing pad,
 * and personality/LSDA references) is compiler-internal, type-info-dependent codegen
 * that plain C does not regenerate. The observable call sequence and the returned
 * status -- the parts that matter for understanding and modifying the gate -- are
 * modelled faithfully against the 0xAF634 disassembly. */
int FUN_000af634(int ctx, void *file)
{
    struct sjlj_func_context eh;
    struct err_vec errs = { 0, 0, 0 };
    unsigned char outbuf[16];           /* verifier's 3rd-arg output area (&auStack_a0) */
    unsigned char *p;
    int result;

    eh.active = 1;
    FUN_003d1214(&eh);                  /* enter try { */

    result = FUN_000a8bdc(ctx, file, outbuf);
    /* --- to bypass verification, replace the line above with: result = 0; --- */

    if (errs.begin) {                   /* ~err_vec: destroy elements, free storage */
        for (p = errs.begin; p != errs.end; p += 0x1c)
            FUN_005e8e00(p);
        FUN_00245c34(errs.begin);
    }
    errs.begin = errs.end = errs.cap = 0;

    FUN_003d12b8(&eh);                  /* } leave try-scope */
    return result;
}
