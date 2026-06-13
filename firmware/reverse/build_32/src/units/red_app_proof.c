/* red_app_proof.c -- byte-for-bit reconstructions of RED *application* functions.
 *
 * Unlike libc_leaves.c (vendor blobs built with Wind River's own flags), these are
 * genuine RED app/lib functions -- the actual reconstruction targets. Matching them
 * pins the RED app build flags and proves the toolchain reproduces RED's compiled C.
 *
 * Verify:
 *   toolchain/in-container.sh python3 firmware/scripts/funcmatch.py units/red_app_proof.c
 */

/* 0x004db598 (app_modules/digmag): registers/looks up the digmag param-name string
 * at 0xD2E724 via the VxWorks param helper at 0x4B4B80. Frame-16 leaf-caller:
 * mflr (scheduled ahead of stwu), load the string ADDRESS via the @ha/@l pair
 * (lis 0xd3 ; addi -0x18dc), bl, restore LR. Arg passes in r3.
 *
 * The argument is a pointer to a data symbol (D_00d2e724, see data_symbols.ld), not a
 * raw integer -- that is what makes gcc emit lis/addi (a relocated symbol address)
 * rather than lis/ori, matching the original byte-for-byte. */
extern char D_00d2e724[];               /* the param-name string at 0x00D2E724 */
extern void FUN_004b4b80(const void *name);

void FUN_004db598(void)
{
    FUN_004b4b80(D_00d2e724);
}
