/*
 * connection_process_gui_cmd.c
 * Connection::ProcessGuiCommand — dispatch a completed GUI command and send reply.
 *
 * Source address: 0x000F2C00  (was Connection_ProcessGuiCommand)
 *
 * This is a thin wrapper around the real vtable-based dispatcher
 * (FUN_00091d70 / Connection_VtableDispatch).  After dispatch, three
 * pending-reply flags are checked; if any are set the corresponding
 * pre-formatted reply string is sent back to the connected Flash GUI
 * client via FUN_005f3110 (connection_send_reply).
 *
 * The function takes no explicit C parameters — its Connection object
 * and a return-value slot are passed on the caller's stack (Ghidra
 * naming convention: in_stack_000000c4 = conn,
 * in_stack_00000094 = result slot).
 *
 * Reply strings and their meanings:
 *   conn[0x210b] != 0  → send XML_REPLY_CREATED   ("created\n")
 *   conn[0x317f] != 0  → send XML_REPLY_UNKNOWN_CMD ("%s: unknown command")
 *   conn[0x1097] != 0  → send XML_REPLY_CHANNEL_ID  ("ChannelID: %d\n")
 *
 * Stack-local objects cleaned up at exit:
 *   stack_50, stack_30  — std::string temporaries (FUN_005e75e4 = string_deref)
 *   stack_90            — exception frame object  (FUN_003d12b8 = frame_pop)
 *
 * Compile note:
 *   Ghidra emits "in_stack_*" and "stack0x*" names for values whose
 *   provenance it cannot resolve.  They are retained verbatim here and
 *   declared as locals so the translation unit compiles cleanly.
 */

#include "connection_protocol.h"

undefined4 Connection_ProcessGuiCommand(void)
{
    undefined4 cmd_handle;
    int        conn_str_ptr;

    /* Ghidra-unresolved stack-passed arguments */
    undefined4 in_stack_00000094;   /* return/result slot on caller stack  */
    int        in_stack_000000c4;   /* Connection* passed via caller stack */

    /* Local std::string temporaries (addresses taken and passed to cleanup) */
    undefined1 stack_50[8];
    undefined1 stack_30[8];
    undefined1 stack_90[8];

    /* ── Step 1: obtain current command handle and dispatch through vtable ── */
    cmd_handle = FUN_0005ea28();    /* get handle for the command being processed */
    FUN_00091d70(cmd_handle, *(undefined4 *)(in_stack_000000c4 + 0x31a8));
    /*
     * FUN_00091d70 is the real per-command dispatch entry.  It selects
     * the correct handler based on the command-type enum stored at
     * conn+0x31a8, then executes it and sets the pending-reply flags
     * at conn+0x210b, conn+0x317f, and conn+0x1097.
     */

    /* ── Step 2: send reply for "created" confirmation ──────────────────── */
    if (*(char *)(in_stack_000000c4 + 0x210b) != '\0') {
        /* SSO string pointer for the name field: use inline buf if capacity ≤ 15 */
        conn_str_ptr = in_stack_000000c4 + 0x28;
        if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
            conn_str_ptr = *(int *)(in_stack_000000c4 + 0x28);
        }
        in_stack_00000094 = 1;
        FUN_005f3110(0xd3bbb4,                    /* "created\n" reply string  */
                     in_stack_000000c4 + 0x10d4,  /* buf for full reply text   */
                     0xe,                          /* log level 14             */
                     conn_str_ptr);
    }

    /* ── Step 3: send reply for "unknown command" error ─────────────────── */
    if (*(char *)(in_stack_000000c4 + 0x317f) != '\0') {
        conn_str_ptr = in_stack_000000c4 + 0x28;
        if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
            conn_str_ptr = *(int *)(in_stack_000000c4 + 0x28);
        }
        in_stack_00000094 = 1;
        FUN_005f3110(0xd3bbcc,                    /* "%s: unknown command"     */
                     in_stack_000000c4 + 0x2148,
                     0xe,
                     conn_str_ptr);
    }

    /* ── Step 4: send reply with channel-ID information ─────────────────── */
    if (*(char *)(in_stack_000000c4 + 0x1097) != '\0') {
        conn_str_ptr = in_stack_000000c4 + 0x28;
        if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
            conn_str_ptr = *(int *)(in_stack_000000c4 + 0x28);
        }
        in_stack_00000094 = 1;
        FUN_005f3110(0xd3bb94,                    /* "ChannelID: %d\n"          */
                     in_stack_000000c4 + 0x60,
                     0xe,
                     conn_str_ptr);
    }

    /* ── Step 5: clean up local C++ temporaries ─────────────────────────── */
    FUN_005e75e4(stack_50, 1, 0);   /* release string ref at stack_50 */
    FUN_005e75e4(stack_30, 1, 0);   /* release string ref at stack_30 */
    FUN_003d12b8(stack_90);         /* pop exception registration frame */

    return 0;
}
