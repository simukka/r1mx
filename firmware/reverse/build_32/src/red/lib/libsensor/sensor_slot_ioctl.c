/* sensor_slot_ioctl.c -- reconstructed lib/libsensor per-slot ioctl accessors.
 *
 * Module  : lib/libsensor   Provenance: red (call-graph)
 * Fidelity: byte_exact (target)
 *
 * Two sibling accessors that issue a control request to one sensor slot, guarded by
 * a "slot present" bitmask. Both share the same shape:
 *
 *   - B_00e13504 is a bitmask with one bit per sensor slot; bit `idx` set means the
 *     slot is populated. If clear, the accessor returns -1 without touching hardware.
 *   - B_00e1333c is a table of per-slot descriptors, stride 0x4c (76) bytes; the
 *     first word of entry `idx` is the handle passed to the worker FUN_0044e510.
 *   - FUN_0044e510(handle, code, arg) performs the request; the accessor normalizes
 *     its result to 0 (success) / -1 (failure) via -(result != 0).
 *
 * They differ only in the control code and argument:
 *   0x001b1c70  code 0x6a010004, arg = caller's `arg`   (a setter: passes a value)
 *   0x001b1cd0  code 0x6a010008, arg = 0                (a getter/trigger)
 *
 * The signed shift `(B_00e13504 >> idx) & 1` compiles to `sraw` (PPC masks the shift
 * count to 6 bits, matching Ghidra's `>> (idx & 0x3f)`). The two globals and the
 * table base are linker symbols (data_symbols.ld, B_00e13504 / B_00e1333c) so
 * ccppc emits the original @ha/@l (lis + lwz, lis + addi) sequences.
 *
 * Two codegen-shape constraints (found via funcmatch byte-diff):
 *   - the present-slot path must be the inline fall-through, so it is written as an
 *     early `return -1` for the absent case (not a default-then-overwrite), which
 *     makes gcc keep the worker call inline (`beq` to the epilogue, body inline);
 *   - the failure normalization `-(rc != 0)` must materialize the 0/1 boolean into a
 *     variable before negating to get the original `addic/subfe/neg` (negating the
 *     comparison directly emits a different, equally-correct `subfic/adde` pair).
 *
 * Reconstructed and verified BYTE-IDENTICAL with the original compiler:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
 *       red/lib/libsensor/sensor_slot_ioctl.c
 */

extern int B_00e13504;             /* sensor-present bitmask (signed: shift is sraw) */
extern unsigned char B_00e1333c[]; /* sensor descriptor table, 0x4c-byte stride */

/* The per-slot request worker: (slot handle, control code, argument). */
extern int FUN_0044e510(int handle, unsigned int code, int arg);

/* Handle word (first field) of descriptor table entry `idx`. */
static inline int slot_handle(unsigned int idx)
{
    return *(unsigned int *)(B_00e1333c + idx * 0x4c);
}

/* 0x001b1c70: set request (code 0x6a010004) on slot `idx`, carrying `arg`. */
int FUN_001b1c70(unsigned int idx, int arg)
{
    if ((B_00e13504 >> idx) & 1) {
        int rc = FUN_0044e510(slot_handle(idx), 0x6a010004, arg);
        unsigned failed = (rc != 0);
        return -failed;
    }
    return -1;
}

/* 0x001b1cd0: get/trigger request (code 0x6a010008) on slot `idx`. */
int FUN_001b1cd0(unsigned int idx)
{
    if ((B_00e13504 >> idx) & 1) {
        int rc = FUN_0044e510(slot_handle(idx), 0x6a010008, 0);
        unsigned failed = (rc != 0);
        return -failed;
    }
    return -1;
}
