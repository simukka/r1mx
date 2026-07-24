/* xmlsocket_conn_ops.c -- reconstructed UiIp / xmlsocket connection-state helpers.
 *
 * Module  : app_modules/ui_ip (xmlsocket connection handling)   Provenance: red (region)
 * Fidelity: MIXED -- FUN_0003975c is byte_exact; the rest are draft (see below).
 *
 * Small non-leaf helpers from the socket/connection region (0x1f000–0x39000) that
 * guard per-connection state with a binary semaphore. Two VxWorks primitives recur:
 *   FUN_005accf4(sem, timeout)  == semTake  (timeout 0xffffffff = WAIT_FOREVER)
 *   FUN_005ad104(sem)           == semGive
 * (named from the call shape; the connection objects carry their guard semaphore at
 * a fixed offset and these take/give it around a short critical section).
 *
 * Reverify with:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
 *       red/app_modules/ui_ip/xmlsocket_conn_ops.c
 *
 * REGION BUILD-PROFILE FINDINGS (see xmlsocket_region_notes.md). This region is
 * -O2 (confirmed: -O1 is worse and even breaks the byte-exact wrapper below;
 * -fno-gcse is identical to -O2; C++ exceptions / frame-pointer / -O0 ruled out),
 * but its functions show source-structure traits the straightforward Ghidra
 * transliteration doesn't reproduce, so most are draft pending per-function refinement:
 *   - leaf functions carry a phantom stack frame (stwu/addi around no stack use);
 *   - *param is re-loaded (not CSE'd) when used in two places (FUN_0002ba90);
 *   - an extra callee-saved reg (r31) is saved unused, and the tail call is a
 *     sibling call, where this compiler won't sibcall the equivalent C (FUN_0002ed24);
 *   - the default return value is staged through r0 then moved to r3 (FUN_00029ddc).
 * These are register-allocation / value-placement / no-CSE artifacts (the logic
 * matches to 36–67%); cracking them is per-function matching-decompilation work.
 *
 * FUN_0003975c is a genuine clean non-leaf (normal frame) and is BYTE-EXACT on the
 * pinned RED app flags.
 */

/* VxWorks-style guard primitives (semTake/semGive). */
extern int FUN_005accf4(int sem, int timeout);   /* semTake; returns 0 ok / -1 timeout */
extern int FUN_005ad104(int sem);                /* semGive */

/* 0x0003975c: thin wrapper — run the FUN_004edc2c work item and return. */
extern void FUN_004edc2c(void);
void FUN_0003975c(void)
{
    FUN_004edc2c();
}

/* 0x0002ed24: gated dispatch — only forward to FUN_000306c0 when the readiness
 * check FUN_0002e4a0 reports ready (0); otherwise fail with -1. */
extern int FUN_0002e4a0(void);
extern int FUN_000306c0(int arg);
int FUN_0002ed24(int arg)
{
    if (FUN_0002e4a0() == 0)
        return FUN_000306c0(arg);
    return -1;
}

/* 0x0002ba90: take the connection guard, decrement a 16-bit refcount on a peer
 * object, clear a slot, release the guard. conn[0] = guarded object (sem at +0x34),
 * conn[1] = peer (counter at +0x40), conn[0x11] = the cleared slot. */
void FUN_0002ba90(int *conn)
{
    int obj = conn[0];
    FUN_005accf4(*(int *)(obj + 0x34), -1);
    *(short *)(conn[1] + 0x40) -= 1;
    conn[0x11] = 0;
    FUN_005ad104(*(int *)(obj + 0x34));
}

/* 0x0002df3c: take the guard at +0x168; on success swap a 16-bit field with the
 * caller's record, release two guards, return 0. Returns -1 if the take fails. */
int FUN_0002df3c(int conn, int rec)
{
    int ret = -1;
    if (FUN_005accf4(*(int *)(conn + 0x168), -1) != -1) {
        *(short *)(rec + 0x36) = *(short *)(conn + 0x16c);
        *(short *)(conn + 0x16c) = *(short *)(rec + 0x34);
        FUN_005ad104(*(int *)(conn + 0x164));
        FUN_005ad104(*(int *)(conn + 0x168));
        ret = 0;
    }
    return ret;
}

/* 0x00029ddc: probe a sub-object's state via FUN_005b804c; treat 0 and 0x23 as OK,
 * anything else as an error (raise via FUN_00442990, return -1). */
extern int FUN_005b804c(int handle, int code, int arg);
extern void FUN_00442990(void);
int FUN_00029ddc(int conn)
{
    int st = FUN_005b804c(*(int *)(*(int *)(conn + 0x10) + 0x28), 0x15, 0);
    int ret = 0;
    if (st != 0x23 && st != 0) {
        FUN_00442990();
        ret = -1;
    }
    return ret;
}
