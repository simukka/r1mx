/*
 * connection_dispatch.c
 * Connection::ProcessRxMessage — authenticate or dispatch an incoming XML command.
 *
 * Source address: 0x0011EBC4  (was FUN_0011ebc4)
 *
 * Entry point for every inbound XML command received from the Flash GUI.
 * The function has two stages:
 *
 *   Stage 1 — Auth gate (runs first, before any command dispatch):
 *     If the connection is not yet authenticated (conn[0x75] == 0):
 *       Compare the command name against ADD_TERM (BSS 0xEA0640).
 *       If cmd != ADD_TERM AND auth_state != AUTH_STATE_DONE:
 *         → route to Connection_Authenticate and return.
 *       Otherwise (it IS ADD_TERM, or auth is already at state 2):
 *         fall through to Stage 2 as normal.
 *     ADD_TERM is the only command permitted before authentication completes.
 *
 *   Stage 2 — Command dispatch (for authenticated sessions or allowed ADD_TERM):
 *     Command names are compared against the static std::string objects
 *     (BSS 0xEA0624–0xEA06CC) in this priority order:
 *
 *       SYNC    @ 0xEA0624  → append to internal buffer, call vtable[2] (sendReply)
 *       GET_FILE@ 0xEA06B0  → check arg type; call FUN_0011d16c (file retrieval)
 *                             or, if arg==connection-type-str AND auth_result==admin,
 *                             call FUN_000b382c instead (admin file access path)
 *       ?@0xEA0694          → walk the GPDB parameter linked list and return value(s)
 *                             (string at this BSS slot is "GET_PARAM" or similar)
 *       ADD_TERM@ 0xEA0640  → compare arg against connection-type string; set
 *                             conn[0x1e] = (arg matches) to enable/disable terminal
 *       (no match)          → log "%s: unknown command" and return
 *
 * Function pointer sentinel:
 *   piStack_1ac[0x13] is the per-parameter handler vtable entry.  When it equals
 *   reset_vector, no handler is registered and the entry is skipped.
 *
 * Connection object offsets used here (word indices unless noted):
 *   conn+0x75  (byte)  — authenticated flag
 *   conn[0x20]         — auth_state
 *   conn[0x21]         — auth_result (2 = admin)
 *   conn[0x1e]         — ADD_TERM subscription flag (bool)
 *   conn[0x26]         — reply std::string buffer
 *   conn[0x2b]         — reply buffer size
 *   conn[0x2c]         — reply buffer capacity
 *   conn[0x1b]         — GPDB linked-list sentinel / null node
 *   conn[0x1e]         — GPDB linked-list root? (traversed in GET_PARAM loop)
 *
 * BSS command-name std::string objects (initialised by Connection_StaticInit):
 *   ADD_TERM  0xEA0640  → size @0xEA0654, cap @0xEA0658, buf @0xEA0644
 *   SYNC      0xEA0624  → size @0xEA0638, cap @0xEA063C, buf @0xEA0628
 *   GET_FILE  0xEA06B0  → size @0xEA06C4, cap @0xEA06C8, buf @0xEA06B4
 *   ?@0xEA0694          → size @0xEA06A8, cap @0xEA06AC, buf @0xEA0698
 *
 * Connection-type string at BSS 0xE9F534 (size @0xE9F544, cap @0xE9F548):
 *   Used as a filter argument in GET_FILE and ADD_TERM comparisons.
 *
 * GPDB linked-list node layout (accessed via puStack_74):
 *   puStack_74[0]   next pointer
 *   puStack_74[3]   key string inline buf
 *   puStack_74[7]   key string .size
 *   puStack_74[8]   key string .capacity
 *   puStack_74[0xe] value string .size
 *   puStack_74[9]   value string start (for SSO check)
 *   puStack_74[10]  value string heap ptr (if capacity >= 16)
 *   puStack_74[0xf] value string .capacity
 *
 * Ghidra hash:
 *   0xdeadbeef is used as the starting value for the FNV-like hash in the
 *   GPDB lookup loop (lines around uVar4 = 0xdeadbeef).
 */

#include "connection_protocol.h"

void Connection_ProcessRxMessage(int *conn, int msg)
{
    uint    uVar1;
    uint    uVar2;
    int     iVar3;
    uint    uVar4;
    undefined4  uVar5;
    undefined4 *puVar6;
    undefined4 ****ppppuVar7;
    undefined4 ****ppppuVar8;
    int     iVar9;
    int    *piVar10;
    uint    uVar11;

    /* ── Stack-allocated string temporaries ────────────────────────────── */
    undefined1  auStack_238[8];      /* exception frame area */
    int     iStack_230;              /* tmp std::string (reply assembly) */
    undefined4 ***apppuStack_22c[4]; /* cmd name string inline buf SSO region */
    uint    uStack_21c;              /* cmd name .size */
    uint    uStack_218;              /* cmd name .capacity */
    undefined1  auStack_210[4];      /* param value str (get_param) */
    undefined4 ***apppuStack_20c[4];
    uint    uStack_1fc;
    uint    uStack_1f8;
    undefined4  uStack_1f0;          /* tmp string obj for SYNC buffer append */
    undefined4 ***apppuStack_1ec[4]; /* uStack_1f0 inline buf */
    uint    uStack_1dc;              /* uStack_1f0 .size */
    uint    uStack_1d8;              /* uStack_1f0 .capacity */
    undefined4 *puStack_1c0;         /* GPDB linked-list cursor */
    int     iStack_1bc;              /* saved context pointer (for GPDB loop) */
    undefined1  auStack_1b0[4];      /* param name str object */
    int    *piStack_1ac;             /* GPDB param node pointer */
    undefined1  auStack_1a0[32];     /* param full-path string (GET_PARAM) */
    undefined1  auStack_180[4];      /* assembled path string obj */
    undefined4 ***apppuStack_17c[4];
    uint    uStack_16c;
    uint    uStack_168;
    undefined1  auStack_160[4];      /* exception frame object */
    undefined4  uStack_15c;          /* current try-block index */
    undefined4  uStack_148;
    undefined4  uStack_144;
    undefined1 *puStack_140;
    undefined4  uStack_13c;
    uint    uStack_120;              /* cmd name string .size (for comparison) */
    undefined4 *puStack_11c;         /* pointer to ADD_TERM buf (for comparison) */
    uint    uStack_110;              /* cmd name .size (SYNC comparison) */
    undefined4 *puStack_10c;         /* pointer to SYNC buf (for comparison) */
    uint    uStack_fc;               /* SYNC arg size */
    uint    uStack_dc;               /* cmd name .size (GET_FILE comparison) */
    uint    uStack_cc;               /* arg size (GET_FILE comparison) */
    uint    uStack_b4;               /* cmd name .size (?@0xEA0694 comparison) */
    int     iStack_94;               /* result of handler vtable call */
    int     iStack_88;               /* result flag in GPDB loop */
    uint    uStack_84;               /* arg .size for path append */
    undefined4 *puStack_74;          /* GPDB linked-list node cursor */
    uint    uStack_68;               /* GPDB node key .size */
    uint    uStack_1c;               /* cmd name .size (ADD_TERM comparison) */

    /* ── Prologue: init exception frame ────────────────────────────────── */
    uStack_148 = 0x25710c;
    puStack_140 = auStack_238;
    uStack_144  = 0xe98f31;
    uStack_13c  = 0x12f93c;
    FUN_003d1214(auStack_160);

    /* ── Stage 1: Auth gate ─────────────────────────────────────────────
     * If not authenticated, check whether the command is ADD_TERM.
     * Only ADD_TERM is permitted unauthenticated; all other commands are
     * routed to Connection_Authenticate (which handles AUTH_INIT/AUTH_PASS).
     */
    uVar4 = uRam00ea0654;  /* ADD_TERM.size */
    if (*(char *)((int)conn + 0x75) == '\0') {
        iVar9 = *(int *)(msg + 4);
        if (uRam00ea0658 < 0x10) {
            puStack_11c = &uRam00ea0644; /* ADD_TERM inline buf */
        }
        else {
            puStack_11c = uRam00ea0644;  /* ADD_TERM heap ptr */
        }
        uStack_120 = *(uint *)(iVar9 + 0x14);
        if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
            uStack_120 = *(uint *)(iVar9 + 0x14);
        }
        uVar2 = 0;
        if (uStack_120 != 0) {
            iVar3 = iVar9 + 4;
            if (0xf < *(uint *)(iVar9 + 0x18)) {
                iVar3 = *(int *)(iVar9 + 4);
            }
            uVar2 = uRam00ea0654;
            if (uStack_120 < uRam00ea0654) {
                uVar2 = uStack_120;
            }
            uVar2 = FUN_0039ac2c(iVar3, puStack_11c, uVar2);
        }
        if ((uVar2 == 0) && (uVar2 = (uint)(uStack_120 != uVar4), uStack_120 < uVar4)) {
            uVar2 = 0xffffffff;
        }
        /* cmd != ADD_TERM AND auth not yet complete → route to authenticate */
        if ((uVar2 != 0) && (conn[0x20] != 2)) {
            uStack_15c = 0xffffffff;
            FUN_001157fc(conn, msg);  /* Connection_Authenticate */
            goto LAB_0011ed28;
        }
    }

    /* ── Stage 2: Command dispatch ──────────────────────────────────────
     * Reached for: authenticated connections, or unauthenticated ADD_TERM.
     */

    /* ── Check SYNC ─────────────────────────────────────────────────── */
    uVar4 = uRam00ea0638;  /* SYNC.size */
    iVar9 = *(int *)(msg + 4);
    if (uRam00ea063c < 0x10) {
        puStack_10c = &uRam00ea0628; /* SYNC inline buf */
    }
    else {
        puStack_10c = uRam00ea0628;  /* SYNC heap ptr */
    }
    uStack_110 = *(uint *)(iVar9 + 0x14);
    if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
        uStack_110 = *(uint *)(iVar9 + 0x14);
    }
    uVar2 = 0;
    if (uStack_110 != 0) {
        iVar3 = iVar9 + 4;
        if (0xf < *(uint *)(iVar9 + 0x18)) {
            iVar3 = *(int *)(iVar9 + 4);
        }
        uVar2 = uRam00ea0638;
        if (uStack_110 < uRam00ea0638) {
            uVar2 = uStack_110;
        }
        uVar2 = FUN_0039ac2c(iVar3, puStack_10c, uVar2);
    }
    uVar11 = uRam00ea06c4; /* GET_FILE.size (loaded early for later use) */
    if ((uVar2 == 0) && (uVar2 = (uint)(uStack_110 != uVar4), uStack_110 < uVar4)) {
        uVar2 = 0xffffffff;
    }
    if (uVar2 == 0) {
        /* ── SYNC handler ─────────────────────────────────────────────
         * Append the arg value to the SYNC buffer (conn[0x26] + append),
         * then call vtable[3] to send the assembled reply.
         */
        iVar9 = *(int *)(msg + 8);
        uStack_15c = 0xffffffff;
        FUN_005ea3bc(&uStack_1f0, 0xd4bbc0); /* load SYNC reply prefix string */
        piVar10 = conn + 0x26;               /* reply buffer */
        uStack_fc = 0xffffffff;
        if (*(uint *)(iVar9 + 0x14) != 0xffffffff) {
            uStack_fc = *(uint *)(iVar9 + 0x14);
        }
        if (~uStack_1dc <= uStack_fc) {
            uStack_15c = 0xc;
            FUN_002513e0(&uStack_1f0); /* reserve for overflow */
        }
        if (uStack_fc != 0) {
            uVar4 = uStack_1dc + uStack_fc;
            if (0xfffffffe < uVar4) {
                uStack_15c = 0xc;
                FUN_002513e0(&uStack_1f0);
            }
            if (uStack_1d8 < uVar4) {
                uStack_15c = 0xc;
                FUN_005e7bb8(&uStack_1f0, uVar4, uStack_1dc); /* grow buffer */
            }
            else if (uVar4 == 0) {
                ppppuVar7 = apppuStack_1ec;
                if (0xf < uStack_1d8) {
                    ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                }
                uStack_1dc = 0;
                *(undefined1 *)ppppuVar7 = 0;
            }
            if (uVar4 != 0) {
                ppppuVar7 = apppuStack_1ec;
                if (0xf < uStack_1d8) {
                    ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                }
                iVar3 = iVar9 + 4;
                if (0xf < *(uint *)(iVar9 + 0x18)) {
                    iVar3 = *(int *)(iVar9 + 4);
                }
                FUN_0039ac74((undefined1 *)((int)ppppuVar7 + uStack_1dc), iVar3, uStack_fc);
                ppppuVar7 = apppuStack_1ec;
                if (0xf < uStack_1d8) {
                    ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                }
                uStack_1dc = uVar4;
                *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
            }
        }
        uStack_15c = 0xc;
        FUN_005f4290(auStack_210, &uStack_1f0); /* copy assembled buffer */
        FUN_005e8e00(&uStack_1f0);
        uStack_15c = 0xb;
        FUN_005f0cd8(&iStack_230, auStack_210, 0xd4b690); /* append closing tag */
        if (piVar10 == &iStack_230) {
            uStack_15c = 10;
            FUN_005f3808(piVar10, uStack_21c, 0xffffffff);
            FUN_005f3808(piVar10, 0, 0);
        }
        else {
            uStack_15c = 10;
            iVar9 = FUN_005f0030(piVar10, uStack_21c, 0);
            if (iVar9 != 0) {
                piVar10 = conn + 0x27;
                if (0xf < (uint)conn[0x2c]) {
                    piVar10 = (int *)conn[0x27];
                }
                ppppuVar7 = apppuStack_22c;
                if (0xf < uStack_218) {
                    ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                }
                FUN_0039ac74(piVar10, ppppuVar7, uStack_21c);
                piVar10 = conn + 0x27;
                if (0xf < (uint)conn[0x2c]) {
                    piVar10 = (int *)conn[0x27];
                }
                conn[0x2b] = uStack_21c;
                *(undefined1 *)((int)piVar10 + uStack_21c) = 0;
            }
        }
        FUN_005e8e00(&iStack_230);
        FUN_005e8e00(auStack_210);
        uStack_15c = 0xffffffff;
        (**(code **)(*conn + 0xc))(conn, conn + 0x26); /* vtable[3]: sendReply */
    }
    else {
        /* ── Not SYNC — check GET_FILE ───────────────────────────────── */
        iVar9 = *(int *)(msg + 4);
        puVar6 = &uRam00ea06b4; /* GET_FILE inline buf */
        if (0xf < uRam00ea06c8) {
            puVar6 = uRam00ea06b4; /* GET_FILE heap ptr */
        }
        uStack_dc = *(uint *)(iVar9 + 0x14);
        if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
            uStack_dc = *(uint *)(iVar9 + 0x14);
        }
        uVar4 = 0;
        if (uStack_dc != 0) {
            iVar3 = iVar9 + 4;
            if (0xf < *(uint *)(iVar9 + 0x18)) {
                iVar3 = *(int *)(iVar9 + 4);
            }
            uVar4 = uRam00ea06c4;
            if (uStack_dc < uRam00ea06c4) {
                uVar4 = uStack_dc;
            }
            uVar4 = FUN_0039ac2c(iVar3, puVar6, uVar4);
        }
        uVar1 = uRam00ea06a8; /* ?@0xEA0694 .size (loaded for later) */
        uVar2 = uRam00e9f544; /* connection-type string .size */
        if ((uVar4 == 0) && (uVar4 = (uint)(uStack_dc != uVar11), uStack_dc < uVar11)) {
            uVar4 = 0xffffffff;
        }

        if (uVar4 != 0) {
            /* ── Not GET_FILE — check command @0xEA0694 (GET_PARAM?) ────
             * This static string slot holds a second command-name literal
             * (initialised to a GET_PARAM-class string by Connection_StaticInit).
             */
            iVar9 = *(int *)(msg + 4);
            puVar6 = &uRam00ea0698; /* ?@0xEA0694 inline buf */
            if (0xf < uRam00ea06ac) {
                puVar6 = uRam00ea0698; /* ?@0xEA0694 heap ptr */
            }
            uStack_b4 = *(uint *)(iVar9 + 0x14);
            if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
                uStack_b4 = *(uint *)(iVar9 + 0x14);
            }
            uVar4 = 0;
            if (uStack_b4 != 0) {
                iVar3 = iVar9 + 4;
                if (0xf < *(uint *)(iVar9 + 0x18)) {
                    iVar3 = *(int *)(iVar9 + 4);
                }
                uVar4 = uRam00ea06a8;
                if (uStack_b4 < uRam00ea06a8) {
                    uVar4 = uStack_b4;
                }
                uVar4 = FUN_0039ac2c(iVar3, puVar6, uVar4);
            }
            uVar2 = uRam00ea0654; /* ADD_TERM.size (re-loaded for next check) */
            if ((uVar4 == 0) && (uVar4 = (uint)(uStack_b4 != uVar1), uStack_b4 < uVar1)) {
                uVar4 = 0xffffffff;
            }

            if (uVar4 == 0) {
                /* ── Command @0xEA0694 matched ────────────────────────────
                 * Get arg and compare against the connection-type string at
                 * BSS 0xD95178 (using FUN_0039b0f0 = strlen to get its length).
                 */
                iVar9 = *(int *)(msg + 8);
                uVar11 = *(uint *)(iVar9 + 0x14);
                uVar2 = FUN_0039b0f0(uRam00d95178); /* strlen(conn_type_str) */
                uVar4 = 0;
                if (uVar11 != 0) {
                    iVar3 = iVar9 + 4;
                    if (0xf < *(uint *)(iVar9 + 0x18)) {
                        iVar3 = *(int *)(iVar9 + 4);
                    }
                    uVar4 = uVar2;
                    if (uVar11 < uVar2) {
                        uVar4 = uVar11;
                    }
                    uVar4 = FUN_0039ac2c(iVar3, uRam00d95178, uVar4);
                }
                if ((uVar4 == 0) && (uVar4 = (uint)(uVar11 != uVar2), uVar11 < uVar2)) {
                    uVar4 = 0xffffffff;
                }

                if (uVar4 == 0) {
                    /* Arg matched connection-type string — walk GPDB param list */
                    uStack_1d8 = 0xf;
                    uStack_1dc = 0;
                    apppuStack_1ec[0] = (undefined4 ***)((uint)apppuStack_1ec[0] & 0xffffff);
                    uStack_15c = 9;
                    iVar9 = FUN_0005e890();   /* get global context */
                    puStack_1c0 = (undefined4 *)0x0;
                    iStack_1bc = iVar9;
                    if (*(int *)(iVar9 + 0x70) != 0) {
                        uStack_15c = 9;
                        FUN_001d9204(*(int *)(iVar9 + 0x70), 0xffffffff); /* semTake */
                    }
                    puStack_1c0 = (undefined4 *)**(undefined4 **)(iVar9 + 0x4c); /* list head */
                    uStack_15c = 8;
                    FUN_00115394(conn); /* GPDB param list lock acquire */
                    while (puStack_1c0 != *(undefined4 **)(iStack_1bc + 0x4c)) {
                        /* Iterate linked list of GPDB parameters */
                        uStack_15c = 8;
                        uVar5 = FUN_0005e890();
                        FUN_005f4290(auStack_210, puStack_1c0 + 2); /* copy node param name */
                        uStack_15c = 7;
                        FUN_005e817c(auStack_1b0, uVar5, auStack_210); /* look up in GPDB */
                        FUN_005e8e00(auStack_210);
                        uStack_15c = 6;
                        iVar9 = FUN_0011c098(conn, auStack_1b0); /* GPDB lookup result */
                        if (iVar9 != 0) {
                            FUN_005ea3bc(auStack_210, 0xddda54); /* load reply separator */
                            piVar10 = piStack_1ac;
                            iStack_94 = -1;
                            if (piStack_1ac != (int *)0x0) {
                                /* ── Build GET_PARAM reply: assemble path string ── */
                                uStack_15c = 5;
                                iStack_88 = -1;
                                FUN_005f0cd8(auStack_1a0, 0xea06e8, 0xdb8b44); /* param path */
                                uStack_15c = 4;
                                FUN_005f4290(auStack_180, auStack_1a0); /* copy path */
                                uStack_84 = 0xffffffff;
                                if (uStack_1fc != 0xffffffff) {
                                    uStack_84 = uStack_1fc;
                                }
                                if (~uStack_16c <= uStack_84) {
                                    uStack_15c = 3;
                                    FUN_002513e0(auStack_180);
                                }
                                if (uStack_84 != 0) {
                                    uVar4 = uStack_16c + uStack_84;
                                    if (0xfffffffe < uVar4) {
                                        uStack_15c = 3;
                                        FUN_002513e0(auStack_180);
                                    }
                                    if (uStack_168 < uVar4) {
                                        uStack_15c = 3;
                                        FUN_005e7bb8(auStack_180, uVar4, uStack_16c);
                                    }
                                    else if (uVar4 == 0) {
                                        ppppuVar7 = apppuStack_17c;
                                        if (0xf < uStack_168) {
                                            ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                                        }
                                        uStack_16c = 0;
                                        *(undefined1 *)ppppuVar7 = 0;
                                    }
                                    if (uVar4 != 0) {
                                        ppppuVar7 = apppuStack_17c;
                                        if (0xf < uStack_168) {
                                            ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                                        }
                                        ppppuVar8 = apppuStack_20c;
                                        if (0xf < uStack_1f8) {
                                            ppppuVar8 = (undefined4 ****)apppuStack_20c[0];
                                        }
                                        FUN_0039ac74((undefined1 *)((int)ppppuVar7 + uStack_16c),
                                                     ppppuVar8, uStack_84);
                                        ppppuVar7 = apppuStack_17c;
                                        if (0xf < uStack_168) {
                                            ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                                        }
                                        uStack_16c = uVar4;
                                        *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
                                    }
                                }
                                uStack_15c = 3;
                                FUN_005f4290(&iStack_230, auStack_180);
                                FUN_005e8e00(auStack_180);
                                FUN_005e8e00(auStack_1a0);
                                iVar9 = -1;
                                if (piVar10[5] != 0) {
                                    uStack_15c = 2;
                                    iVar9 = FUN_001d9204(piVar10[5], 0xffffffff);
                                }
                                if (iVar9 == 0) {
                                    /* ── GPDB hash-based lookup in param map ─ */
                                    uVar4 = 0xdeadbeef; /* FNV-like hash seed */
                                    if (uStack_21c != 0) {
                                        iVar9 = (uStack_21c >> 4) + 1;
                                        uVar2 = 0;
                                        do {
                                            ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                                            if (uStack_218 < 0x10) {
                                                ppppuVar7 = apppuStack_22c;
                                            }
                                            uVar11 = uVar2 + iVar9;
                                            uVar4 = uVar4 + *(byte *)((int)ppppuVar7 + uVar2);
                                            uVar2 = uVar11;
                                        } while (uVar11 <= uStack_21c - iVar9);
                                    }
                                    /* Map hash to bucket index */
                                    uVar4 = uVar4 & piVar10[0x21];
                                    if ((uint)piVar10[0x22] <= uVar4) {
                                        uVar4 = (uVar4 - ((uint)piVar10[0x21] >> 1)) - 1;
                                    }
                                    /* Walk hash bucket chain */
                                    for (puStack_74 = *(undefined4 **)(piVar10[0x1e] + uVar4 * 4);
                                         uVar2 = uStack_21c,
                                         puStack_74 != *(undefined4 **)(piVar10[0x1e] + (uVar4 + 1) * 4);
                                         puStack_74 = (undefined4 *)*puStack_74) {
                                        ppppuVar7 = apppuStack_22c;
                                        if (0xf < uStack_218) {
                                            ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                                        }
                                        uStack_68 = puStack_74[7]; /* node key .size */
                                        if ((uint)puStack_74[7] < (uint)puStack_74[7]) {
                                            uStack_68 = puStack_74[7];
                                        }
                                        uVar11 = 0;
                                        if (uStack_68 != 0) {
                                            puVar6 = puStack_74 + 3;
                                            if (0xf < (uint)puStack_74[8]) {
                                                puVar6 = (undefined4 *)puStack_74[3];
                                            }
                                            uVar11 = uStack_21c;
                                            if (uStack_68 < uStack_21c) {
                                                uVar11 = uStack_68;
                                            }
                                            uVar11 = FUN_0039ac2c(puVar6, ppppuVar7, uVar11);
                                        }
                                        uVar1 = uStack_21c;
                                        if ((uVar11 == 0) &&
                                            (uVar11 = (uint)(uStack_68 != uVar2), uStack_68 < uVar2)) {
                                            uVar11 = 0xffffffff;
                                        }
                                        if (-1 < (int)uVar11) {
                                            /* Key >= search key — check exact match */
                                            puVar6 = puStack_74 + 3;
                                            if (0xf < (uint)puStack_74[8]) {
                                                puVar6 = (undefined4 *)puStack_74[3];
                                            }
                                            uVar2 = puStack_74[7];
                                            uVar4 = 0;
                                            if (uStack_21c != 0) {
                                                ppppuVar7 = apppuStack_22c;
                                                if (0xf < uStack_218) {
                                                    ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                                                }
                                                uVar4 = uVar2;
                                                if (uStack_21c < uVar2) {
                                                    uVar4 = uStack_21c;
                                                }
                                                uVar4 = FUN_0039ac2c(ppppuVar7, puVar6, uVar4);
                                            }
                                            if ((uVar4 == 0) &&
                                                (uVar4 = (uint)(uVar1 != uVar2), uVar1 < uVar2)) {
                                                uVar4 = 0xffffffff;
                                            }
                                            if ((int)uVar4 < 0) {
                                                /* Exact match: get value from node */
                                                puStack_74 = (undefined4 *)piVar10[0x1b];
                                            }
                                            goto LAB_00120100;
                                        }
                                    }
                                    puStack_74 = (undefined4 *)piVar10[0x1b]; /* sentinel = not found */
LAB_00120100:
                                    if (puStack_74 != (undefined4 *)piVar10[0x1b]) {
                                        /* Found: copy value string into reply buffer */
                                        uVar4 = puStack_74[0xe]; /* node value .size */
                                        if (&uStack_1f0 == puStack_74 + 9) {
                                            uStack_15c = 2;
                                            FUN_005f3808(&uStack_1f0, uVar4, 0xffffffff);
                                            FUN_005f3808(&uStack_1f0, 0, 0);
                                        }
                                        else {
                                            uStack_15c = 2;
                                            iVar9 = FUN_005f0030(&uStack_1f0, uVar4, 0);
                                            if (iVar9 != 0) {
                                                ppppuVar7 = apppuStack_1ec;
                                                if (0xf < uStack_1d8) {
                                                    ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                                                }
                                                puVar6 = puStack_74 + 10;
                                                if (0xf < (uint)puStack_74[0xf]) {
                                                    puVar6 = (undefined4 *)puStack_74[10];
                                                }
                                                FUN_0039ac74(ppppuVar7, puVar6, uVar4);
                                                ppppuVar7 = apppuStack_1ec;
                                                if (0xf < uStack_1d8) {
                                                    ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                                                }
                                                *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
                                                uStack_1dc = uVar4;
                                            }
                                        }
                                        iStack_88 = 0;
                                    }
                                    if (piVar10[5] != 0) {
                                        uStack_15c = 2;
                                        FUN_001d92bc(); /* semGive */
                                    }
                                }
                                FUN_005e8e00(&iStack_230);
                                iStack_94 = iStack_88;
                            }
                            FUN_005e8e00(auStack_210);
                            if (iStack_94 != 0) {
                                /* Call per-parameter vtable handler if registered */
                                iVar9 = -1;
                                if ((piStack_1ac != (int *)0x0) &&
                                    ((code *)piStack_1ac[0x13] != reset_vector)) {
                                    uStack_15c = 6;
                                    iVar9 = (*(code *)piStack_1ac[0x13])
                                                (piStack_1ac + 10, piStack_1ac[0x12], conn + 0x26);
                                }
                                if (iVar9 == 0) {
                                    uStack_15c = 6;
                                    (**(code **)(*conn + 8))(conn, conn + 0x26); /* vtable[2] */
                                    FUN_005f3808(conn + 0x26, 0, 0xffffffff);
                                }
                            }
                        }
                        piVar10 = piStack_1ac;
                        puStack_1c0 = (undefined4 *)*puStack_1c0; /* advance to next node */
                        if (piStack_1ac != (int *)0x0) {
                            iVar9 = -1;
                            if (piStack_1ac[3] != 0) {
                                uStack_15c = 8;
                                iVar9 = FUN_001d9204(piStack_1ac[3], 0xffffffff);
                            }
                            if ((iVar9 == 0) && (*piVar10 = *piVar10 + -1, piVar10[3] != 0)) {
                                uStack_15c = 8;
                                FUN_001d92bc();
                            }
                        }
                    } /* end while GPDB list */
                    uStack_15c = 8;
                    FUN_00115000(conn); /* GPDB param list lock release */
                    if (*(int *)(iStack_1bc + 0x70) != 0) {
                        uStack_15c = 9;
                        FUN_001d92bc(); /* semGive context sem */
                    }
                    FUN_005e8e00(&uStack_1f0);
                }
                else {
                    /* Arg did not match connection-type string — single-item lookup */
                    uStack_15c = 0xffffffff;
                    uVar5 = FUN_0005e890();
                    FUN_005e817c(auStack_1b0, uVar5, *(undefined4 *)(msg + 8));
                    uStack_15c = 1;
                    iVar9 = FUN_0011c098(conn, auStack_1b0);
                    if (iVar9 != 0) {
                        FUN_00115394(conn);
                        iVar9 = -1;
                        if ((piStack_1ac != (int *)0x0) &&
                            ((code *)piStack_1ac[0x13] != reset_vector)) {
                            uStack_15c = 1;
                            iVar9 = (*(code *)piStack_1ac[0x13])
                                        (piStack_1ac + 10, piStack_1ac[0x12], conn + 0x26);
                        }
                        if (iVar9 == 0) {
                            uStack_15c = 1;
                            (**(code **)(*conn + 8))(conn, conn + 0x26); /* vtable[2] */
                            FUN_005f3808(conn + 0x26, 0, 0xffffffff);
                        }
                        uStack_15c = 1;
                        FUN_00115000(conn);
                    }
                    if (piStack_1ac != (int *)0x0) {
                        iVar9 = -1;
                        if (piStack_1ac[3] != 0) {
                            uStack_15c = 0xffffffff;
                            iVar9 = FUN_001d9204(piStack_1ac[3], 0xffffffff);
                        }
                        if ((iVar9 == 0) && (*piStack_1ac = *piStack_1ac + -1, piStack_1ac[3] != 0)) {
                            uStack_15c = 0xffffffff;
                            FUN_001d92bc();
                        }
                    }
                }
            }
            else {
                /* ── Not ?@0xEA0694 — check ADD_TERM ──────────────────────
                 * ADD_TERM enables/disables terminal subscription.
                 * The arg is compared against the connection-type string; the
                 * result (matched or not) is stored as a boolean at conn[0x1e].
                 */
                iVar9 = *(int *)(msg + 4);
                puVar6 = &uRam00ea0644; /* ADD_TERM inline buf */
                if (0xf < uRam00ea0658) {
                    puVar6 = uRam00ea0644; /* ADD_TERM heap ptr */
                }
                uStack_1c = *(uint *)(iVar9 + 0x14);
                if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
                    uStack_1c = *(uint *)(iVar9 + 0x14);
                }
                uVar4 = 0;
                if (uStack_1c != 0) {
                    iVar3 = iVar9 + 4;
                    if (0xf < *(uint *)(iVar9 + 0x18)) {
                        iVar3 = *(int *)(iVar9 + 4);
                    }
                    uVar4 = uRam00ea0654;
                    if (uStack_1c < uRam00ea0654) {
                        uVar4 = uStack_1c;
                    }
                    uVar4 = FUN_0039ac2c(iVar3, puVar6, uVar4);
                }
                if ((uVar4 == 0) && (uVar4 = (uint)(uStack_1c != uVar2), uStack_1c < uVar2)) {
                    uVar4 = 0xffffffff;
                }
                if (uVar4 == 0) {
                    /* IS ADD_TERM — check arg against connection-type string */
                    iVar9 = *(int *)(msg + 8);
                    uVar11 = *(uint *)(iVar9 + 0x14);
                    uVar2 = FUN_0039b0f0(uRam00d9517c); /* strlen(conn_type_str) */
                    uVar4 = 0;
                    if (uVar11 != 0) {
                        iVar3 = iVar9 + 4;
                        if (0xf < *(uint *)(iVar9 + 0x18)) {
                            iVar3 = *(int *)(iVar9 + 4);
                        }
                        uVar4 = uVar2;
                        if (uVar11 < uVar2) {
                            uVar4 = uVar11;
                        }
                        uVar4 = FUN_0039ac2c(iVar3, uRam00d9517c, uVar4);
                    }
                    if ((uVar4 == 0) && (uVar4 = (uint)(uVar11 != uVar2), uVar11 < uVar2)) {
                        uVar4 = 0xffffffff;
                    }
                    *(bool *)(conn + 0x1e) = uVar4 == 0; /* subscribe = (arg matched type) */
                }
                else {
                    /* Unknown command — log error */
                    piVar10 = conn + 0x10;
                    if (0xf < (uint)conn[0x15]) {
                        piVar10 = (int *)conn[0x10];
                    }
                    uStack_15c = 0xffffffff;
                    FUN_0005e784(0, 3, 8, 0xd4b744, 0x662588, 0x218, 0xd4bbcc, piVar10);
                }
            }
        }
        else {
            /* ── IS GET_FILE ─────────────────────────────────────────────
             * Compare the arg against the connection-type-filter string at
             * BSS 0xE9F534.  If matched AND auth_result == admin, use the
             * admin file access path; otherwise call the normal GET_FILE handler.
             */
            iVar9 = *(int *)(msg + 8);
            puVar6 = &uRam00e9f534;
            if (0xf < uRam00e9f548) {
                puVar6 = uRam00e9f534;
            }
            uStack_cc = *(uint *)(iVar9 + 0x14);
            if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
                uStack_cc = *(uint *)(iVar9 + 0x14);
            }
            uVar4 = 0;
            if (uStack_cc != 0) {
                iVar3 = iVar9 + 4;
                if (0xf < *(uint *)(iVar9 + 0x18)) {
                    iVar3 = *(int *)(iVar9 + 4);
                }
                uVar4 = uRam00e9f544;
                if (uStack_cc < uRam00e9f544) {
                    uVar4 = uStack_cc;
                }
                uVar4 = FUN_0039ac2c(iVar3, puVar6, uVar4);
            }
            if ((uVar4 == 0) && (uVar4 = (uint)(uStack_cc != uVar2), uStack_cc < uVar2)) {
                uVar4 = 0xffffffff;
            }
            if (uVar4 == 0) {
                /* Arg matches connection-type filter — require admin auth */
                if (conn[0x21] != 2) goto LAB_0011ed28;
                uStack_15c = 0xffffffff;
                uVar5 = FUN_0005e8a8();                     /* get admin context */
                FUN_000b382c(uVar5, conn + 0x26);           /* admin file handler */
                (**(code **)(*conn + 0xc))(conn, conn + 0x26); /* vtable[3]: sendReply */
            }
            else {
                /* Normal GET_FILE — call the standard file retrieval handler */
                uStack_15c = 0xffffffff;
                FUN_0011d16c(conn, conn + 0x26, *(undefined4 *)(msg + 8));
                (**(code **)(*conn + 0xc))(conn, conn + 0x26); /* vtable[3]: sendReply */
            }
        }
    }

    /* ── Clear reply buffer and return ─────────────────────────────────── */
    FUN_005f3808(conn + 0x26, 0, 0xffffffff);

LAB_0011ed28:
    FUN_003d12b8(auStack_160); /* pop exception frame */
    return;
}
