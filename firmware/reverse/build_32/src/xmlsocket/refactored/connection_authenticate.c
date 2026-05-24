/*
 * connection_authenticate.c
 * Connection::Authenticate — AUTH_INIT seed generation and AUTH_PASS OTP verification.
 *
 * Source address: 0x001157FC  (was FUN_001157fc)
 *
 * Called from Connection_ProcessRxMessage when the incoming command is an
 * AUTH command (AUTH_INIT or AUTH_PASS).  The function inspects
 * conn[0x20] (auth_state) to determine which phase of the handshake is
 * in progress:
 *
 *   auth_state == 0  (AUTH_STATE_INITIAL):
 *     Received AUTH_INIT.  Compare the supplied command name against the
 *     AUTH_INIT static string at BSS 0xEA0678.  If matched, call rand()
 *     twice to build a 32-bit seed, XOR-encode it with the JJRC1 key, and
 *     send the hex-encoded seed back to the client.  Set auth_state = 1.
 *
 *   auth_state == 1  (AUTH_STATE_AWAIT_PASS):
 *     Received AUTH_PASS.  Hex-decode the client's argument, XOR with the
 *     stored seed to recover the plaintext password.  Try to look up the
 *     ADMIN password in GPDB ("SYSTEM.MANUFACTURING.PASSWORD.ADMIN").  If
 *     not found, try the USER password (".USER").  Compare the recovered
 *     plaintext against each stored password and set conn[0x21]
 *     (auth_result) accordingly:
 *       2 = admin authenticated
 *       1 = user authenticated
 *       0 = authentication failed
 *     On success, copy the reply string into conn[0x26] (reply buffer),
 *     set conn[0x75] = 1 (authenticated flag), and auth_state = 2.
 *
 * Key Connection object offsets (in int32_t words unless noted):
 *   conn[0x1f]  — seed (32-bit OTP seed, set during AUTH_INIT)
 *   conn[0x20]  — auth_state (0=initial, 1=await_pass, 2=done)
 *   conn[0x21]  — auth_result (0=none, 1=user, 2=admin)
 *   conn[0x10]  — SSO string inline buffer (connection name)
 *   conn[0x15]  — SSO capacity for name string
 *   conn[0x26]  — reply string buffer (conn+0x98 bytes, SSO)
 *   conn+0x75   — authenticated byte flag (char, 1 = authenticated)
 *
 * Rodata address map (Ghidra +0x10000 bias for lo16 >= 0x8000):
 *   0xD4B698  → actual 0xD3B698  "SYSTEM.MANUFACTURING.PASSWORD.ADMIN"
 *   0xD4B710  → actual 0xD3B710  "SYSTEM.MANUFACTURING.PASSWORD.USER"
 *   0xD4B678  → actual 0xD3B678  XML reply format prefix
 *   0xD4B688  → actual 0xD3B688  XML reply format middle
 *   0xD4B690  → actual 0xD3B690  XML reply format suffix
 *
 * Helper functions:
 *   FUN_001149bc — hex-decode the client argument into a temp buffer
 *   FUN_001149b0 — XOR the decoded buffer with the stored seed
 *   FUN_00114970 — XOR-encode buffer with seed (for building reply)
 *   FUN_00115728 — format the XOR-encoded seed into reply string fragments
 *   FUN_0039a414 — rand() producing 16-bit value (called twice for seed)
 *   FUN_005ea3bc — std::string::assign(char *)
 *   FUN_005e8e00 — std::string destructor (release)
 *   FUN_005f3808 — std::string::assign(ptr, len, sentinel)
 *   FUN_005f0030 — std::string::reserve_and_assign
 *   FUN_0039ac2c — memcmp
 *   FUN_0039ac74 — memcpy
 *   FUN_005e817c — GPDB lookup helper (get param by name)
 *   FUN_005ea8a8 — GPDB param value accessor
 *   FUN_001d9204 — semTake wrapper
 *   FUN_001d92bc — semGive wrapper
 *   FUN_0005e784 — log/error reporting
 *   FUN_0005e890 — get current Connection* (from global context)
 */

#include "connection_protocol.h"

void Connection_Authenticate(int *conn, int msg)
{
    uint    uVar1;
    undefined4 *****pppppuVar2;
    undefined4 *****pppppuVar3;
    undefined4  uVar4;
    uint    uVar5;
    undefined4  uVar6;
    int     iVar7;
    int    *piVar8;

    /* ── Exception frame and string temporaries ─────────────────────────── */
    undefined1  auStack_408[8];
    int     aiStack_400[7];    /* AUTH_PASS string obj (std::string) */
    int    *piStack_3e4;
    int    *piStack_3e0;
    int    *piStack_3d4;
    int    *piStack_3d0;
    int    *piStack_3c4;
    int    *piStack_3c0;
    int     iStack_3b8;
    uint    uStack_3b4;
    undefined4  auStack_3ac[10];
    int     iStack_384;
    int     aiStack_370[7];    /* AUTH_INIT string obj (std::string) */
    undefined4 *puStack_354;
    undefined4 *puStack_350;
    undefined4 *puStack_344;
    undefined4 *puStack_340;
    undefined4 *puStack_334;
    undefined4 *puStack_330;
    undefined4  uStack_328;
    uint    uStack_324;
    undefined4  auStack_31c[15];

    /* ── Working string buffers (std::string objects on stack) ───────────── */
    int     iStack_2e0;        /* tmp std::string for XOR'd arg */
    undefined4 ****appppuStack_2dc[4];
    uint    uStack_2cc;        /* .size of above */
    uint    uStack_2c8;        /* .capacity of above */
    int     iStack_2c0;        /* tmp std::string for reply assembly */
    undefined4 ****appppuStack_2bc[4];
    uint    uStack_2ac;        /* .size of reply */
    uint    uStack_2a8;        /* .capacity of reply */

    /* ── GPDB password comparison buffers ───────────────────────────────── */
    undefined1  auStack_2a0[32];   /* GPDB admin password string */
    undefined1  auStack_280[32];   /* GPDB user password string */
    undefined1  auStack_260[4];    /* admin param value */
    undefined4 ****appppuStack_25c[4];
    uint    uStack_24c;
    uint    uStack_248;
    undefined1  auStack_240[4];    /* user param value */
    undefined4 ****appppuStack_23c[4];
    uint    uStack_22c;
    uint    uStack_228;
    undefined1  auStack_220[4];    /* decoded arg */
    undefined4 ****appppuStack_21c[4];
    uint    uStack_20c;
    uint    uStack_208;

    /* ── GPDB semaphore ref holders ─────────────────────────────────────── */
    undefined1  auStack_1f0[4];
    int    *piStack_1ec;           /* admin GPDB param ref */
    undefined1  auStack_1e0[4];
    int    *piStack_1dc;           /* user GPDB param ref */

    /* ── XOR / encode temporaries ───────────────────────────────────────── */
    undefined1  auStack_1d0[32];
    undefined1  auStack_1b0[32];
    undefined1  auStack_190[32];
    undefined1  auStack_170[32];
    undefined1  auStack_150[32];

    /* ── Exception / misc locals ────────────────────────────────────────── */
    undefined1  auStack_130[4];
    undefined4  uStack_12c;
    undefined4  uStack_118;
    undefined4  uStack_114;
    undefined1 *puStack_110;
    undefined4  uStack_10c;
    undefined1 *puStack_108;
    undefined1 *puStack_104;
    undefined4  uStack_fc;

    /* ── Core locals (named by role) ────────────────────────────────────── */
    int    *piStack_f8;   /* conn pointer (saved param_1) */
    int     iStack_f4;   /* msg  pointer (saved param_2) */
    int     iStack_f0;   /* heap buffer for cmd name arg */
    int     iStack_ec;   /* heap buffer for password arg */
    int     iStack_e8;
    int     iStack_e4;
    int     iStack_e0;
    int     iStack_dc;
    uint    uStack_d8;
    undefined4  uStack_d4;
    uint    uStack_d0;
    uint    uStack_cc;
    uint    uStack_c4;   /* high 16 bits of seed (rand() << 16) */
    undefined4 ****ppppuStack_c0;
    uint    uStack_bc;
    int     iStack_b8;
    int    *piStack_b4;
    int    *piStack_b0;
    uint    uStack_ac;
    int    *piStack_a8;
    uint    uStack_a4;
    undefined4  uStack_a0;
    uint    uStack_9c;
    uint    uStack_98;
    char    cStack_94;   /* flag: user password matched */
    undefined4  uStack_90;
    undefined4  uStack_8c;
    int     iStack_88;
    int     iStack_84;
    int    *piStack_78;
    int    *piStack_68;
    uint    uStack_64;
    uint    uStack_60;
    undefined4 ****ppppuStack_5c;
    uint    uStack_58;
    uint    uStack_54;
    undefined4 ****ppppuStack_50;
    uint    uStack_4c;
    int    *piStack_48;
    int    *piStack_44;
    uint    uStack_40;
    int    *piStack_3c;
    int     iStack_38;   /* auth_state = conn[0x20] */
    int    *piStack_24;

    /* ── Prologue: save params, init exception frame, allocate arg buffers ─ */
    puStack_104 = &stack0xfffffbe0;
    uStack_118  = 0x25710c;
    puStack_110 = auStack_408;
    uStack_114  = 0xe98da9;
    uStack_10c  = 0x125e60;
    puStack_108 = (undefined1 *)register0x00000004;
    piStack_f8  = conn;
    iStack_f4   = msg;
    FUN_003d1214(auStack_130);    /* push exception frame */
    uStack_12c  = 0xffffffff;
    FUN_006142e4(aiStack_400, 3); /* init AUTH_PASS string obj */
    uStack_12c  = 0x2f;
    FUN_006142e4(aiStack_370, 3); /* init AUTH_INIT string obj */

    /* Allocate working heap buffers sized to the cmd/arg string lengths */
    iStack_f0 = FUN_002482e0((*(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1) + 1, 0xef9080);
    iStack_ec = FUN_002482e0((*(uint *)(*(int *)(iStack_f4 + 8) + 0x14) >> 1) + 1, 0xef9080);

    if (iStack_f0 == 0 || iStack_ec == 0) {
        /* Allocation failure — log error and fall through to cleanup */
        piVar8 = piStack_f8 + 0x10;
        if (0xf < (uint)piStack_f8[0x15]) {
            piVar8 = (int *)piStack_f8[0x10];
        }
        uVar6 = 0xd4b820;
        uVar4 = 0x385;
    }
    else {
        iStack_38 = piStack_f8[0x20]; /* auth_state */

        if (iStack_38 != 0) {
            if (iStack_38 == 1) {
                /* ── AUTH_PASS path ─────────────────────────────────────── */

                uStack_12c = 0x2e;

                /* Hex-decode arg[0] (client-supplied OTP) into iStack_f0 */
                FUN_001149bc(piStack_f8, *(int *)(iStack_f4 + 4), iStack_f0,
                             *(undefined4 *)(*(int *)(iStack_f4 + 4) + 0x14));
                /* XOR decoded buffer with stored seed to recover plaintext */
                FUN_001149b0(piStack_f8, iStack_f0,
                             *(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1,
                             piStack_f8[0x1f]);

                /* Same for arg[1] */
                FUN_001149bc(piStack_f8, *(int *)(iStack_f4 + 8), iStack_ec,
                             *(undefined4 *)(*(int *)(iStack_f4 + 8) + 0x14));
                FUN_001149b0(piStack_f8, iStack_ec,
                             *(uint *)(*(int *)(iStack_f4 + 8) + 0x14) >> 1,
                             piStack_f8[0x1f]);

                /* Copy decoded arg into auStack_220 for comparison */
                FUN_005ea3bc(auStack_220, iStack_f0);

                /* Compare against AUTH_PASS std::string at BSS 0xEA065C */
                uStack_a0 = 0xea0660;
                if (0xf < uRam00ea0674) {
                    uStack_a0 = uRam00ea0660;
                }
                uStack_9c  = uRam00ea0670;
                uStack_a4  = uStack_20c;
                uVar1 = 0;
                if (uStack_20c != 0) {
                    pppppuVar2 = appppuStack_21c;
                    if (0xf < uStack_208) {
                        pppppuVar2 = (undefined4 *****)appppuStack_21c[0];
                    }
                    uVar1 = uRam00ea0670;
                    if (uStack_20c < uRam00ea0670) {
                        uVar1 = uStack_20c;
                    }
                    uVar1 = FUN_0039ac2c(pppppuVar2, uStack_a0, uVar1);
                }
                if ((uVar1 == 0) && (uVar1 = (uint)(uStack_a4 != uStack_9c), uStack_a4 < uStack_9c)) {
                    uVar1 = 0xffffffff;
                }
                uStack_98 = (uint)(uVar1 == 0); /* 1 = command name matched AUTH_PASS */
                FUN_005e8e00(auStack_220);

                if (uStack_98 == 0) {
                    /* Command name did not match AUTH_PASS — log mismatch */
                    piVar8 = piStack_f8 + 0x10;
                    if (0xf < (uint)piStack_f8[0x15]) {
                        piVar8 = (int *)piStack_f8[0x10];
                    }
                    uStack_12c = 0x2e;
                    FUN_0005e784(0, 3, 8, 0xd4b744, 0x662514, 0x375, 0xd4b844, piVar8);
                }
                else {
                    /* ── Password verification ──────────────────────────── */
                    uStack_248 = 0xf;
                    appppuStack_25c[0] = (undefined4 ****)((uint)appppuStack_25c[0] & 0xffffff);
                    uStack_12c = 0x24;
                    uStack_228 = 0xf;
                    uStack_22c = 0;
                    appppuStack_23c[0] = (undefined4 ****)((uint)appppuStack_23c[0] & 0xffffff);
                    uStack_24c = 0;
                    cStack_94  = '\0'; /* user-password-matched flag */

                    /* Look up admin password in GPDB */
                    uStack_90 = FUN_0005e890();
                    FUN_005ea3bc(auStack_280, 0xd4b698);  /* "SYSTEM.MANUFACTURING.PASSWORD.ADMIN" */
                    uStack_12c = 0x23;
                    FUN_005e817c(auStack_1f0, uStack_90, auStack_280); /* GPDB get param */
                    uStack_12c = 0x21;
                    iStack_88  = 0;
                    iStack_84  = 0;
                    iVar7 = FUN_005ea8a8(auStack_1f0, auStack_240); /* get param value */
                    if (iVar7 == 0) {
                        /* Admin param not found; try user password */
                        uStack_8c = FUN_0005e890();
                        FUN_005ea3bc(auStack_2a0, 0xd4b710); /* "SYSTEM.MANUFACTURING.PASSWORD.USER" */
                        iStack_88 = 1;
                        FUN_005e817c(auStack_1e0, uStack_8c, auStack_2a0);
                        iStack_84 = 1;
                        iVar7 = FUN_005ea8a8(auStack_1e0, auStack_260);
                        if (iVar7 == 0) {
                            cStack_94 = '\x01'; /* user password found */
                        }
                    }

                    /* Release GPDB semaphores */
                    if ((iStack_84 != 0) && (piStack_1dc != (int *)0x0)) {
                        piStack_78 = piStack_1dc;
                        iVar7 = -1;
                        if (piStack_1dc[3] != 0) {
                            uStack_12c = 0x22;
                            iVar7 = FUN_001d9204(piStack_1dc[3], 0xffffffff);
                        }
                        if ((iVar7 == 0) && (*piStack_78 = *piStack_78 + -1, piStack_78[3] != 0)) {
                            uStack_12c = 0x22;
                            FUN_001d92bc();
                        }
                    }
                    if (iStack_88 != 0) {
                        FUN_005e8e00(auStack_2a0);
                    }
                    if (piStack_1ec != (int *)0x0) {
                        piStack_68 = piStack_1ec;
                        iVar7 = -1;
                        if (piStack_1ec[3] != 0) {
                            uStack_12c = 0x23;
                            iVar7 = FUN_001d9204(piStack_1ec[3], 0xffffffff);
                        }
                        if ((iVar7 == 0) && (*piStack_68 = *piStack_68 + -1, piStack_68[3] != 0)) {
                            uStack_12c = 0x23;
                            FUN_001d92bc();
                        }
                    }
                    FUN_005e8e00(auStack_280);

                    if (cStack_94 == '\0') {
                        /* Neither admin nor user password found in GPDB */
                        piVar8 = piStack_f8 + 0x10;
                        if (0xf < (uint)piStack_f8[0x15]) {
                            piVar8 = (int *)piStack_f8[0x10];
                        }
                        uStack_12c = 0x24;
                        FUN_0005e784(0, 3, 8, 0xd4b744, 0x662514, 0x36f, 0xd4b6bc, piVar8);
                    }
                    else {
                        /* ── Compare client OTP against stored passwords ── */
                        uStack_2a8 = 0xf;
                        appppuStack_2bc[0] = (undefined4 ****)((uint)appppuStack_2bc[0] & 0xffffff);
                        uStack_12c = 0x20;
                        uStack_2ac = 0;
                        FUN_005ea3bc(&iStack_2e0, iStack_ec); /* copy decoded arg */
                        uStack_64 = uStack_2cc;
                        if (&iStack_2c0 == &iStack_2e0) {
                            uStack_12c = 0x1f;
                            FUN_005f3808(&iStack_2c0, uStack_2cc, 0xffffffff);
                            FUN_005f3808(&iStack_2c0, 0, 0);
                        }
                        else {
                            uStack_12c = 0x1f;
                            iVar7 = FUN_005f0030(&iStack_2c0, uStack_2cc, 0);
                            if (iVar7 != 0) {
                                pppppuVar2 = appppuStack_2bc;
                                if (0xf < uStack_2a8) {
                                    pppppuVar2 = (undefined4 *****)appppuStack_2bc[0];
                                }
                                pppppuVar3 = appppuStack_2dc;
                                if (0xf < uStack_2c8) {
                                    pppppuVar3 = (undefined4 *****)appppuStack_2dc[0];
                                }
                                FUN_0039ac74(pppppuVar2, pppppuVar3, uStack_64);
                                pppppuVar2 = appppuStack_2bc;
                                if (0xf < uStack_2a8) {
                                    pppppuVar2 = (undefined4 *****)appppuStack_2bc[0];
                                }
                                uStack_2ac = uStack_64;
                                *(undefined1 *)((int)pppppuVar2 + uStack_64) = 0;
                            }
                        }
                        FUN_005e8e00(&iStack_2e0);

                        /* Compare decoded arg against admin password */
                        ppppuStack_5c = appppuStack_23c;
                        if (0xf < uStack_228) {
                            ppppuStack_5c = appppuStack_23c[0];
                        }
                        uStack_58 = uStack_22c;
                        uStack_60 = uStack_2ac;
                        uVar1 = 0;
                        if (uStack_2ac != 0) {
                            pppppuVar2 = appppuStack_2bc;
                            if (0xf < uStack_2a8) {
                                pppppuVar2 = (undefined4 *****)appppuStack_2bc[0];
                            }
                            uVar1 = uStack_22c;
                            if (uStack_2ac < uStack_22c) {
                                uVar1 = uStack_2ac;
                            }
                            uVar1 = FUN_0039ac2c(pppppuVar2, ppppuStack_5c, uVar1);
                        }
                        if ((uVar1 == 0) && (uVar1 = (uint)(uStack_60 != uStack_58), uStack_60 < uStack_58)) {
                            uVar1 = 0xffffffff;
                        }
                        if (uVar1 == 0) {
                            piStack_f8[0x21] = 2; /* auth_result = admin */
                        }
                        else {
                            /* Compare against user password */
                            ppppuStack_50 = appppuStack_25c;
                            if (0xf < uStack_248) {
                                ppppuStack_50 = appppuStack_25c[0];
                            }
                            uStack_4c = uStack_24c;
                            uStack_54 = uStack_2ac;
                            uVar1 = 0;
                            if (uStack_2ac != 0) {
                                pppppuVar2 = appppuStack_2bc;
                                if (0xf < uStack_2a8) {
                                    pppppuVar2 = (undefined4 *****)appppuStack_2bc[0];
                                }
                                uVar1 = uStack_24c;
                                if (uStack_2ac < uStack_24c) {
                                    uVar1 = uStack_2ac;
                                }
                                uVar1 = FUN_0039ac2c(pppppuVar2, ppppuStack_50, uVar1);
                            }
                            if ((uVar1 == 0) && (uVar1 = (uint)(uStack_54 != uStack_4c), uStack_54 < uStack_4c)) {
                                uVar1 = 0xffffffff;
                            }
                            if (uVar1 == 0) {
                                piStack_f8[0x21] = 1; /* auth_result = user */
                            }
                            else {
                                piStack_f8[0x21] = 0; /* auth_result = none */
                            }
                        }

                        if (piStack_f8[0x21] == 0) {
                            /* Authentication failed — log error */
                            piVar8 = piStack_f8 + 0x10;
                            if (0xf < (uint)piStack_f8[0x15]) {
                                piVar8 = (int *)piStack_f8[0x10];
                            }
                            uStack_12c = 0x20;
                            FUN_0005e784(0, 3, 8, 0xd4b744, 0x662514, 0x369, 0xd4b6d8, piVar8);
                        }
                        else {
                            /* ── Authentication succeeded ──────────────── */

                            /* XOR-encode the arg with seed for the reply */
                            FUN_00114970(piStack_f8, iStack_f0,
                                         *(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1,
                                         piStack_f8[0x1f]);
                            uStack_12c = 0x20;
                            FUN_00115728(piStack_f8, aiStack_370, iStack_f0,
                                         *(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1);

                            /* Build reply: copy JJRC1 key string from BSS 0xEA060C */
                            uVar4 = 0xea060c;
                            if (0xf < uRam00ea0620) {
                                uVar4 = uRam00ea060c;
                            }
                            FUN_0039ac74(iStack_ec, uVar4, uRam00ea061c);
                            FUN_00114970(piStack_f8, iStack_ec, uRam00ea061c, piStack_f8[0x1f]);
                            uStack_12c = 0x20;
                            FUN_00115728(piStack_f8, aiStack_400, iStack_ec, uRam00ea061c);

                            /* Assemble XML reply from format strings */
                            piStack_48 = piStack_f8 + 0x26;
                            FUN_00613d04(auStack_170, aiStack_370 + 3);
                            uStack_12c = 0x1e;
                            FUN_006140c0(auStack_190, 0xd4b678, auStack_170);
                            uStack_12c = 0x1d;
                            FUN_005f0cd8(auStack_1b0, auStack_190, 0xd4b688);
                            uStack_12c = 0x1c;
                            FUN_00613d04(auStack_150, aiStack_400 + 3);
                            uStack_12c = 0x1b;
                            FUN_005f43dc(auStack_1d0, auStack_1b0, auStack_150);
                            uStack_12c = 0x1a;
                            FUN_005f0cd8(&iStack_2e0, auStack_1d0, 0xd4b690);

                            /* Write assembled reply string into conn[0x26] */
                            uStack_40 = uStack_2cc;
                            piStack_44 = piStack_48;
                            if (piStack_48 == &iStack_2e0) {
                                uStack_12c = 0x19;
                                FUN_005f3808(piStack_48, uStack_2cc, 0xffffffff);
                                FUN_005f3808(piStack_44, 0, 0);
                            }
                            else {
                                uStack_12c = 0x19;
                                iVar7 = FUN_005f0030(piStack_48, uStack_2cc, 0);
                                if (iVar7 != 0) {
                                    piVar8 = piStack_f8 + 0x27;
                                    if (0xf < (uint)piStack_44[6]) {
                                        piVar8 = (int *)piStack_44[1];
                                    }
                                    pppppuVar2 = appppuStack_2dc;
                                    if (0xf < uStack_2c8) {
                                        pppppuVar2 = (undefined4 *****)appppuStack_2dc[0];
                                    }
                                    FUN_0039ac74(piVar8, pppppuVar2, uStack_40);
                                    piVar8 = piStack_44 + 1;
                                    if (0xf < (uint)piStack_44[6]) {
                                        piVar8 = (int *)piStack_44[1];
                                    }
                                    piStack_44[5] = uStack_40;
                                    *(undefined1 *)((int)piVar8 + uStack_40) = 0;
                                }
                            }

                            /* Release temporary strings */
                            FUN_005e8e00(&iStack_2e0);
                            FUN_005e8e00(auStack_1d0);
                            FUN_005e8e00(auStack_150);
                            FUN_005e8e00(auStack_1b0);
                            FUN_005e8e00(auStack_190);
                            FUN_005e8e00(auStack_170);

                            /* Call vtable[3] to send reply (conn->sendReply) */
                            uStack_12c = 0x20;
                            piStack_3c = piStack_f8 + 0x26;
                            (**(code **)(*piStack_f8 + 0xc))(piStack_f8, piStack_3c);
                            FUN_005f3808(piStack_3c, 0, 0xffffffff);

                            /* Mark connection as fully authenticated */
                            *(undefined1 *)((int)piStack_f8 + 0x75) = 1; /* conn->authenticated = true */
                            piStack_f8[0x20] = 2;                         /* auth_state = AUTH_STATE_DONE */

                            piVar8 = piStack_f8 + 0x10;
                            if (0xf < (uint)piStack_f8[0x15]) {
                                piVar8 = (int *)piStack_f8[0x10];
                            }
                            uStack_12c = 0x20;
                            FUN_0005e784(3, 0x10, 8, 0xd4b744, 0x662514, 0x365, 0xd4b6fc, piVar8);
                        }
                        FUN_005e8e00(&iStack_2c0);
                    }
                    FUN_005e8e00(auStack_260);
                    FUN_005e8e00(auStack_240);
                }

                /* If authentication did not succeed, reset auth_state to 0 */
                if (*(char *)((int)piStack_f8 + 0x75) == '\0') {
                    piStack_f8[0x20] = 0; /* auth_state = AUTH_STATE_INITIAL */
                }
            }
            goto LAB_00115bd4;
        }

        /* ── AUTH_INIT path (auth_state == 0, command should be AUTH_INIT) ─ */
        iStack_e8 = *(int *)(iStack_f4 + 8);
        if ((uStack_3b4 & 1) != 0) {
            FUN_00245c34(*piStack_3e4);
        }
        *piStack_3c4 = iStack_38;
        *piStack_3c0 = iStack_38;
        uVar1  = uStack_3b4 & 0xfffffffe;
        uVar5  = *(uint *)(iStack_e8 + 0x18);
        *piStack_3e4 = iStack_38;
        *piStack_3d4 = iStack_38;
        *piStack_3e0 = iStack_38;
        iStack_e4 = iStack_e8 + 4;
        *piStack_3d0 = iStack_38;
        if (0xf < uVar5) {
            iStack_e4 = *(int *)(iStack_e8 + 4);
        }
        iStack_e0    = *(int *)(iStack_e8 + 0x14);
        iStack_3b8   = 0;
        if ((iStack_e0 != 0) && ((uStack_3b4 & 6) != 6)) {
            uStack_12c = 0x2e;
            uStack_3b4 = uVar1;
            iStack_dc  = FUN_00248640(iStack_e0);
            FUN_0039ac74(iStack_dc, iStack_e4, iStack_e0);
            iStack_3b8 = iStack_dc + iStack_e0;
            if ((uStack_3b4 & 4) == 0) {
                *piStack_3e4 = iStack_dc;
                *piStack_3c4 = iStack_3b8 - iStack_dc;
                *piStack_3d4 = iStack_dc;
            }
            if ((uStack_3b4 & 2) == 0) {
                *piStack_3e0 = iStack_dc;
                *piStack_3d0 = iStack_dc;
                iVar7 = *piStack_3d4;
                *piStack_3c0 = iStack_3b8 - iStack_dc;
                if (iVar7 == 0) {
                    *piStack_3e4 = iStack_dc;
                    *piStack_3c4 = iStack_dc;
                    *piStack_3d4 = 0;
                }
            }
            uVar1 = uStack_3b4 | 1;
        }
        uStack_3b4 = uVar1;

        /* Process AUTH_INIT argument string */
        uStack_12c = 0x2e;
        FUN_00614fa8(aiStack_400, &uStack_fc);
        FUN_001149bc(piStack_f8, *(int *)(iStack_f4 + 4), iStack_f0,
                     *(undefined4 *)(*(int *)(iStack_f4 + 4) + 0x14));
        FUN_001149b0(piStack_f8, iStack_f0,
                     *(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1, uStack_fc);

        /* Compare cmd name against AUTH_INIT std::string at BSS 0xEA067C */
        FUN_005ea3bc(&iStack_2e0, iStack_f0);
        uStack_d4 = 0xea067c;
        if (0xf < uRam00ea0690) {
            uStack_d4 = uRam00ea067c;
        }
        uStack_d0 = uRam00ea068c;
        uStack_d8 = uStack_2cc;
        uVar1 = 0;
        if (uStack_2cc != 0) {
            pppppuVar2 = appppuStack_2dc;
            if (0xf < uStack_2c8) {
                pppppuVar2 = (undefined4 *****)appppuStack_2dc[0];
            }
            uVar1 = uRam00ea068c;
            if (uStack_2cc < uRam00ea068c) {
                uVar1 = uStack_2cc;
            }
            uVar1 = FUN_0039ac2c(pppppuVar2, uStack_d4, uVar1);
        }
        if ((uVar1 == 0) && (uVar1 = (uint)(uStack_d8 != uStack_d0), uStack_d8 < uStack_d0)) {
            uVar1 = 0xffffffff;
        }
        uStack_cc = (uint)(uVar1 == 0); /* 1 = command name matched AUTH_INIT */
        FUN_005e8e00(&iStack_2e0);

        if (uStack_cc != 0) {
            /* ── Generate seed and send AUTH_INIT reply ──────────────────── */

            /* seed = (rand16() << 16) | rand16() */
            iVar7    = FUN_0039a414();
            uStack_c4 = iVar7 << 0x10;
            uVar1    = FUN_0039a414();
            uVar5    = *(uint *)(*(int *)(iStack_f4 + 4) + 0x14);
            piStack_f8[0x1f] = uStack_c4 | uVar1; /* store seed in conn */

            /* XOR-encode the cmd arg with the new seed */
            FUN_00114970(piStack_f8, iStack_f0, uVar5 >> 1, uStack_c4 | uVar1);
            uStack_12c = 0x2e;
            FUN_00115728(piStack_f8, aiStack_370, iStack_f0,
                         *(uint *)(*(int *)(iStack_f4 + 4) + 0x14) >> 1);

            uStack_12c = 0x2e;
            FUN_0024a2dc(auStack_3ac, (uint)(iStack_384 == 0) << 2, 0);
            FUN_005ea3bc(&iStack_2c0, 0xd6f55c);
            if ((uStack_3b4 & 1) != 0) {
                FUN_00245c34(*piStack_3e4);
            }
            *piStack_3c4 = 0;
            *piStack_3c0 = 0;
            *piStack_3e4 = 0;
            uVar1 = uStack_3b4 & 0xfffffffe;
            *piStack_3d4 = 0;
            *piStack_3e0 = 0;
            ppppuStack_c0 = appppuStack_2bc;
            *piStack_3d0 = 0;
            if (0xf < uStack_2a8) {
                ppppuStack_c0 = appppuStack_2bc[0];
            }
            uStack_bc  = uStack_2ac;
            iStack_3b8 = 0;
            if ((uStack_2ac != 0) && ((uStack_3b4 & 6) != 6)) {
                uStack_12c = 0x2c;
                uStack_3b4 = uVar1;
                iStack_b8  = FUN_00248640(uStack_2ac);
                FUN_0039ac74(iStack_b8, ppppuStack_c0, uStack_bc);
                iStack_3b8 = iStack_b8 + uStack_bc;
                if ((uStack_3b4 & 4) == 0) {
                    *piStack_3e4 = iStack_b8;
                    *piStack_3c4 = iStack_3b8 - iStack_b8;
                    *piStack_3d4 = iStack_b8;
                }
                if ((uStack_3b4 & 2) == 0) {
                    *piStack_3e0 = iStack_b8;
                    *piStack_3d0 = iStack_b8;
                    iVar7 = *piStack_3d4;
                    *piStack_3c0 = iStack_3b8 - iStack_b8;
                    if (iVar7 == 0) {
                        *piStack_3e4 = iStack_b8;
                        *piStack_3c4 = iStack_b8;
                        *piStack_3d4 = 0;
                    }
                }
                uVar1 = uStack_3b4 | 1;
            }
            uStack_3b4 = uVar1;
            FUN_005e8e00(&iStack_2c0);

            /* Assemble hex-encoded seed reply */
            uStack_12c = 0x2e;
            FUN_0060f2d0(aiStack_400 + 2, piStack_f8[0x1f]); /* format seed as hex */
            piStack_b4 = piStack_f8 + 0x26;
            FUN_00613d04(auStack_240, aiStack_370 + 3);
            uStack_12c = 0x2b;
            FUN_006140c0(auStack_260, 0xd4b678, auStack_240);
            uStack_12c = 0x2a;
            FUN_005f0cd8(auStack_280, auStack_260, 0xd4b688);
            uStack_12c = 0x29;
            FUN_00613d04(auStack_220, aiStack_400 + 3);
            uStack_12c = 0x28;
            FUN_005f43dc(auStack_2a0, auStack_280, auStack_220);
            uStack_12c = 0x27;
            FUN_005f0cd8(&iStack_2c0, auStack_2a0, 0xd4b690);

            /* Write assembled reply into conn[0x26] */
            uStack_ac = uStack_2ac;
            piStack_b0 = piStack_b4;
            if (piStack_b4 == &iStack_2c0) {
                uStack_12c = 0x26;
                FUN_005f3808(piStack_b4, uStack_2ac, 0xffffffff);
                FUN_005f3808(piStack_b0, 0, 0);
            }
            else {
                uStack_12c = 0x26;
                iVar7 = FUN_005f0030(piStack_b4, uStack_2ac, 0);
                if (iVar7 != 0) {
                    piVar8 = piStack_f8 + 0x27;
                    if (0xf < (uint)piStack_b0[6]) {
                        piVar8 = (int *)piStack_b0[1];
                    }
                    pppppuVar2 = appppuStack_2bc;
                    if (0xf < uStack_2a8) {
                        pppppuVar2 = (undefined4 *****)appppuStack_2bc[0];
                    }
                    FUN_0039ac74(piVar8, pppppuVar2, uStack_ac);
                    piVar8 = piStack_b0 + 1;
                    if (0xf < (uint)piStack_b0[6]) {
                        piVar8 = (int *)piStack_b0[1];
                    }
                    piStack_b0[5] = uStack_ac;
                    *(undefined1 *)((int)piVar8 + uStack_ac) = 0;
                }
            }

            /* Clean up and send reply via vtable[3] */
            FUN_005e8e00(&iStack_2c0);
            FUN_005e8e00(auStack_2a0);
            FUN_005e8e00(auStack_220);
            FUN_005e8e00(auStack_280);
            FUN_005e8e00(auStack_260);
            FUN_005e8e00(auStack_240);
            uStack_12c = 0x2e;
            piStack_a8 = piStack_f8 + 0x26;
            (**(code **)(*piStack_f8 + 0xc))(piStack_f8, piStack_a8);
            FUN_005f3808(piStack_a8, 0, 0xffffffff);

            piStack_f8[0x20] = 1; /* auth_state = AUTH_STATE_AWAIT_PASS */
            goto LAB_00115bd4;
        }

        /* AUTH_INIT command name did not match — log error */
        piVar8 = piStack_f8 + 0x10;
        if (0xf < (uint)piStack_f8[0x15]) {
            piVar8 = (int *)piStack_f8[0x10];
        }
        uVar6 = 0xd4b7fc;
        uVar4 = 0x334;
    }

    uStack_12c = 0x2e;
    FUN_0005e784(0, 3, 8, 0xd4b744, 0x662514, uVar4, uVar6, piVar8);

LAB_00115bd4:
    /* ── Cleanup: free heap arg buffers ────────────────────────────────── */
    if (iStack_ec != 0) {
        FUN_00245be8(iStack_ec);
    }
    if (iStack_f0 != 0) {
        FUN_00245be8(iStack_f0);
    }

    /* ── Cleanup: destroy string objects and pop exception frame ────────── */
    aiStack_370[0] = 0xe085dc;
    auStack_31c[0] = 0xe08604;
    aiStack_370[2] = 0xe085f0;
    aiStack_370[3] = 0xe084d8;
    if ((uStack_324 & 1) != 0) {
        FUN_00245c34(*puStack_354);
    }
    *puStack_334 = 0;
    *puStack_354 = 0;
    *puStack_330 = 0;
    *puStack_344 = 0;
    *puStack_350 = 0;
    uStack_324 = uStack_324 & 0xfffffffe;
    *puStack_340 = 0;
    uStack_328 = 0;
    uStack_12c = 0x11;
    FUN_005fb758(aiStack_370 + 3);
    *(undefined4 *)((int)aiStack_370 + *(int *)(iRam00e085ac + -0xc)) = uRam00e085c0;
    aiStack_370[2] = iRam00e085b8;
    *(undefined4 *)((int)aiStack_370 + *(int *)(iRam00e085b8 + -0xc) + 8) = uRam00e085bc;
    aiStack_370[0] = iRam00e085b0;
    *(undefined4 *)((int)aiStack_370 + *(int *)(iRam00e085b0 + -0xc)) = uRam00e085b4;
    uStack_12c = 0x2f;
    piStack_24 = aiStack_370;
    FUN_005fb11c(auStack_31c);
    aiStack_400[0] = 0xe085dc;
    auStack_3ac[0] = 0xe08604;
    aiStack_400[2] = 0xe085f0;
    aiStack_400[3] = 0xe084d8;
    if ((uStack_3b4 & 1) != 0) {
        FUN_00245c34(*piStack_3e4);
    }
    *piStack_3c4 = 0;
    *piStack_3e4 = 0;
    *piStack_3c0 = 0;
    *piStack_3d4 = 0;
    *piStack_3e0 = 0;
    uStack_3b4 = uStack_3b4 & 0xfffffffe;
    *piStack_3d0 = 0;
    iStack_3b8 = 0;
    uStack_12c = 5;
    FUN_005fb758(aiStack_400 + 3);
    *(undefined4 *)((int)aiStack_400 + *(int *)(iRam00e085ac + -0xc)) = uRam00e085c0;
    aiStack_400[2] = iRam00e085b8;
    *(undefined4 *)((int)aiStack_400 + *(int *)(iRam00e085b8 + -0xc) + 8) = uRam00e085bc;
    aiStack_400[0] = iRam00e085b0;
    *(undefined4 *)((int)aiStack_400 + *(int *)(iRam00e085b0 + -0xc)) = uRam00e085b4;
    uStack_12c = 0xffffffff;
    FUN_005fb11c(auStack_3ac);
    FUN_003d12b8(auStack_130); /* pop exception frame */
    return;
}
