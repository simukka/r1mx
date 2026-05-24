/*
 * connection_static_init.c
 * One-time init and teardown of Connection class static std::string members.
 *
 * Source address: 0x00120F6C  (was FUN_00120f6c)
 *
 * VxWorks / GCC calls this from __static_initialization_and_destruction_0
 * during task start-up.  It is called twice:
 *   param_2 == 0xFFFF  →  initialise all static members
 *   param_1 == 0 AND param_2 == 0xFFFF → only tear-down (see note below)
 *
 * Ghidra note: "unaff_cr3" is an untracked condition-register fragment.
 * The guard expression
 *     ((uint)(param_2 == 0xffff) & ((unaff_cr3 & 0xf) << 16) >> 17 & 1) != 0
 * is Ghidra's representation of a VxWorks atexit / priority-guard that
 * ensures each block runs exactly once.  The logic is preserved verbatim.
 *
 * Ghidra address-translation note:
 *   Ghidra shows rodata literals with a +0x10000 bias for addresses whose
 *   lo16 >= 0x8000 (sign-extension in lis+addi pair).  The actual binary
 *   addresses are:
 *     0xD4BBF4 → 0xD3BBF4  "GET_FILE"
 *     0xD4BC00 → 0xD3BC00  "GET_PARAM"
 *     0xD4BBE0 → 0xD3BBE0  "ADD_TERM"
 *     0xD4BBEC → 0xD3BBEC  "SYNC"
 *     0xD49DE4 → 0xD39DE4  "AUTH_INIT"
 *     0xD49DD0 → 0xD39DD0  "AUTH_PASS"
 *     0xD49DDC → 0xD39DDC  "JJRC1"
 *   The Ghidra-emitted values are kept here so the code matches the
 *   decompiler output exactly.
 *
 * BSS layout of the static std::string objects:
 *   0xEA0608   JJRC1_str        — OTP key / default user password
 *   0xEA0624   SYNC_str
 *   0xEA0640   ADD_TERM_str
 *   0xEA065C   AUTH_PASS_str
 *   0xEA0678   AUTH_INIT_str
 *   0xEA0694   (unknown label)
 *   0xEA06B0   GET_FILE_str
 *   0xEA06CC   GET_PARAM_str
 *   0xEA06E8   ADMIN_PASSWORD_param_name
 *   0xEA0704   (unknown)
 *   0xEA0720   (unknown)
 *   0xEA073C   USER_PASSWORD_param_name
 *   0xEA0758   container object (holds the above, allocated via FUN_0024ba14)
 */

#include "connection_protocol.h"

/*
 * Connection_StaticInit — init (param_2==0xFFFF) or dtor (param_1==0,param_2==0xFFFF)
 *
 * The ref-count triplets (uRam01153xxx) are VxWorks atexit priority guards.
 * Each triplet is { high_word, low_word, init_flag }.
 * The pattern `bVar1 = 0xfffffffe < low_word; low_word++; high_word += bVar1;`
 * is an atomic 64-bit increment of the guard counter.
 */
void Connection_StaticInit(int param_1, uint32_t param_2)
{
    bool bVar1;
    byte unaff_cr3;  /* condition-register bits — untracked by Ghidra */

    /* ── Block 1: initialise the command-name string objects ──────────── */
    if (((uint)(param_2 == 0xffff) &
         ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {

        FUN_0024ba14(0xea0758);   /* initialise outer container object */

        /* Assign each static std::string its initial value from rodata */
        FUN_005ea3bc(0xea073c, 0xd38c84);  /* USER_PASSWORD_param_name ← rodata str */
        FUN_005ea3bc(0xea0720, 0xd38c84);  /* (unknown) ← same rodata str */
        FUN_005ea3bc(0xea0704, 0xd38c90);  /* (unknown) */
        FUN_005ea3bc(0xea06e8, 0xd38c88);  /* ADMIN_PASSWORD_param_name */
        FUN_005ea3bc(0xea06cc, 0xd769bc);  /* GET_PARAM_str   ← "GET_PARAM"  */
        FUN_005ea3bc(0xea06b0, 0xd4bbf4);  /* GET_FILE_str    ← "GET_FILE"   (Ghidra: 0xD4BBF4, actual 0xD3BBF4) */
        FUN_005ea3bc(0xea0694, 0xd4bc00);  /* (unknown str)   ← "GET_PARAM"? (Ghidra: 0xD4BC00, actual 0xD3BC00) */
        FUN_005ea3bc(0xea0678, 0xd49de4);  /* AUTH_INIT_str   ← "AUTH_INIT"  (Ghidra: 0xD49DE4, actual 0xD39DE4) */
        FUN_005ea3bc(0xea065c, 0xd49dd0);  /* AUTH_PASS_str   ← "AUTH_PASS"  (Ghidra: 0xD49DD0, actual 0xD39DD0) */
    }

    /* ── Block 2: initialise remaining command strings + first guard ───── */
    if (((uint)(param_2 == 0xffff) &
         ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {

        FUN_005ea3bc(0xea0640, 0xd4bbe0);  /* ADD_TERM_str ← "ADD_TERM" (actual 0xD3BBE0) */
        FUN_005ea3bc(0xea0624, 0xd4bbec);  /* SYNC_str     ← "SYNC"    (actual 0xD3BBEC) */
        FUN_005ea3bc(0xea0608, 0xd49ddc);  /* JJRC1_str    ← "JJRC1"   (actual 0xD39DDC) */

        /* Atomic 64-bit increment of atexit guard counter #0 */
        bVar1          = 0xfffffffe < uRam011533ec;
        uRam011533ec   = uRam011533ec + 1;
        iRam011533e8   = iRam011533e8 + (uint)bVar1;
        if ((iRam011533e8 == 0) && (uRam011533ec == 1)) {
            uRam011533f8 = 0;   /* mark guard as initialised */
        }
    }

    /* ── Block 3: atexit guard counter #1 ─────────────────────────────── */
    if (((uint)(param_2 == 0xffff) &
         ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {

        bVar1        = 0xfffffffe < uRam01153414;
        uRam01153414 = uRam01153414 + 1;
        iRam01153410 = iRam01153410 + (uint)bVar1;
        if ((iRam01153410 == 0) && (uRam01153414 == 1)) {
            uRam01153418 = 0;
        }
    }

    /* ── Block 4: atexit guard counter #2 ─────────────────────────────── */
    if (((uint)(param_2 == 0xffff) &
         ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {

        bVar1        = 0xfffffffe < uRam01153404;
        uRam01153404 = uRam01153404 + 1;
        iRam01153400 = iRam01153400 + (uint)bVar1;
        if ((iRam01153400 == 0) && (uRam01153404 == 1)) {
            uRam01153408 = 0;
        }
    }

    /* ── Block 5: atexit guard counter #3 ─────────────────────────────── */
    if (((uint)(param_2 == 0xffff) &
         ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {

        bVar1        = 0xfffffffe < uRam011533e4;
        uRam011533e4 = uRam011533e4 + 1;
        iRam011533e0 = iRam011533e0 + (uint)bVar1;
        if ((iRam011533e0 == 0) && (uRam011533e4 == 1)) {
            uRam011533f0 = 0;
        }
    }

    /* ── Destructor path: only runs when param_2==0xFFFF AND param_1==0 ── */
    if (param_2 != 0xffff || param_1 != 0) {
        return;
    }

    /* Destroy all static std::string members in reverse construction order */
    FUN_005e8e00(0xea0608);   /* ~JJRC1_str        */
    FUN_005e8e00(0xea0624);   /* ~SYNC_str         */
    FUN_005e8e00(0xea0640);   /* ~ADD_TERM_str      */
    FUN_005e8e00(0xea065c);   /* ~AUTH_PASS_str     */
    FUN_005e8e00(0xea0678);   /* ~AUTH_INIT_str     */
    FUN_005e8e00(0xea0694);   /* ~(unknown)         */
    FUN_005e8e00(0xea06b0);   /* ~GET_FILE_str      */
    FUN_005e8e00(0xea06cc);   /* ~GET_PARAM_str     */
    FUN_005e8e00(0xea06e8);   /* ~admin param name  */
    FUN_005e8e00(0xea0704);   /* ~(unknown)         */
    FUN_005e8e00(0xea0720);   /* ~(unknown)         */
    FUN_005e8e00(0xea073c);   /* ~user param name   */
    FUN_0024b634(0xea0758);   /* destroy container  */
}
