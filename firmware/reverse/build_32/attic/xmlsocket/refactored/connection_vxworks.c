/*
 * connection_vxworks.c
 * VxWorks OS wrappers used by the Connection class.
 *
 * Source addresses:
 *   Connection_semTake  @ 0x001D9204  (was FUN_001d9204)
 *   Connection_semGive  @ 0x001D92BC  (was FUN_001d92bc)
 *
 * These are thin wrappers around the underlying VxWorks semTake / semGive
 * kernel calls.  The only non-trivial logic in semTake is the millisecond →
 * tick-count conversion: the firmware stores timeouts as milliseconds but
 * VxWorks semTake() takes a tick count, so we must scale by sysClkRateGet().
 *
 * Special sentinel values for timeout_ms:
 *   0xFFFFFFFF  — WAIT_FOREVER (passed through unchanged)
 *   0           — NO_WAIT     (passed through unchanged)
 */

#include "connection_protocol.h"

/*
 * Connection_semTake — take a semaphore with a millisecond timeout
 *
 * @sem         VxWorks semaphore handle
 * @timeout_ms  Timeout in milliseconds.
 *              0xFFFFFFFF = WAIT_FOREVER, 0 = NO_WAIT (both bypass conversion).
 * @return      0 on success, negative (−1) on failure / timeout
 */
int Connection_semTake(uint32_t sem, uint32_t timeout_ms)
{
    int ticks;

    if (timeout_ms != 0xffffffff && timeout_ms != 0) {
        /* Convert milliseconds to VxWorks tick count via sysClkRateGet() */
        int clk_rate = FUN_00009518();          /* sysClkRateGet() → ticks/sec */
        timeout_ms   = (clk_rate * timeout_ms) / 1000;

        /* Guard: if rounding produced zero ticks, use 1 to avoid NO_WAIT */
        if (timeout_ms == 0) {
            ticks = FUN_005accf4(sem, 1);
            return -(uint)(ticks != 0);
        }
    }

    ticks = FUN_005accf4(sem, timeout_ms);
    return -(uint)(ticks != 0);
}

/*
 * Connection_semGive — release a semaphore
 *
 * No parameters: the semaphore handle is passed in a register that Ghidra
 * did not track (likely r3 from the caller's context, captured implicitly
 * by the VxWorks semGive ABI).
 *
 * @return  0 on success, negative on failure
 */
int Connection_semGive(void)
{
    int result = FUN_005ad104();   /* VxWorks semGive() */
    return -(uint)(result != 0);
}
