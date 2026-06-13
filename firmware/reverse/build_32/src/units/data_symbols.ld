/* data_symbols.ld -- absolute addresses of DATA objects (strings, tables, BSS) that
 * reconstructed units reference by address. Providing these lets the linker emit the
 * @ha/@l (lis/addi) relocation pair the original used, so address materialization is
 * byte-exact (a raw integer constant instead compiles to lis/ori and will NOT match).
 *
 * Hand-maintained for now; Phase 1 will generate it from a data manifest. Naming:
 * D_<addr> for read-only data/strings, B_<addr> for BSS. PROVIDE so a unit may also
 * define its own. */
PROVIDE(D_00d2e724 = 0x00d2e724);  /* app_modules/digmag param-name string */
PROVIDE(D_00d5bbcc = 0x00d5bbcc);  /* libflashutils per-file verify log format string */
