/* symbols.h -- extern declarations for cross-image DATA symbols that reconstructed
 * units reference by address (mirrors src/data_symbols.ld). Editor aid for clangd so
 * D_/B_<addr> references resolve; the real addresses are wired by the linker at relink
 * time (via data_symbols.ld), not by these decls.
 *
 * Function cross-references (FUN_<addr>) are declared per-unit with their recovered
 * signatures — a blanket declaration here would conflict with those (return type /
 * arity), so only data symbols live in this shared header.
 */
#ifndef R1MX_SYMBOLS_H
#define R1MX_SYMBOLS_H

extern char D_00d2e724[];  /* app_modules/digmag param-name string */
extern char D_00d5bbcc[];  /* libflashutils per-file verify log format string */
extern char D_00d2db9c[];  /* app_modules/common "utils.h" __FILE__ string */
extern char D_00d2dce4[];  /* app_modules/common "on/utils.cpp" __FILE__ string */
extern char B_00e13504[];  /* libsensor: sensor-present bitmask (one bit per slot) */
extern char B_00e1333c[];  /* libsensor: sensor descriptor table, stride 0x4c bytes */

#endif /* R1MX_SYMBOLS_H */
