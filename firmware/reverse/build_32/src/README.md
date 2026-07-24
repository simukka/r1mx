# RED ONE MX Build 32 — reconstructed firmware source

This tree is the **reconstructed source** for Build 32. The decompilation goal is to
rebuild proprietary RED functions as **readable C/C++ that is also bit-for-bit
identical** to the shipped firmware, using the *carve-out relink* model against the
original `../extracted/software.bin`. There is **no binary-patch build** — the original
`software.bin` boots unmodified in QEMU once loaded at base `0x10000`; the obsolete
byte-patch image has been retired (see git history / [[qemu-load-base-0x10000]]).

## Layout (mirrors the firmware `__FILE__` module tree)

```
red/                    reconstructed RED functions (provenance == red)
  app_modules/…           e.g. ui_engine/flashvx.cpp, common/utils_thunks.c,
                          digmag/red_app_proof.c, ui_ip/xmlsocket_conn_ops.c,
                          flashutils/upgrade_verify.c
  lib/libsensor/…         sensor_slot_ioctl.c
hw/                     provenance-unknown MMIO leaves (mmio_leaves.c)
include/                shared decls for clangd (vx_types.h, red_types.h, symbols.h)
ghidra/                 10.5k Ghidra pseudocode files (lift.py intake)
data_symbols.ld         D_/B_<addr> data-symbol addresses for @ha/@l relocations
functional.txt          manual functional-tier badges (read by recon_status.py)
manifest.json/.csv      provenance map + absolute-address symbol table
recon_status.json       reconstruction coverage dashboard output
../attic/               archived exploratory trees (not built)
```

## Build

```bash
make verify           # BIT-FOR-BIT GATE: relink byte-exact units, assert sha256 == software.bin
make relink           # working reconstructed image (byte-exact + functional overlays)
make verify-relink    # assert every non-functional unit is byte-identical to base
make verify-units     # byte-match the fully-byte-exact units with the ORIGINAL compiler
make recon-status     # reconstruction coverage dashboard -> recon_status.json
make manifest         # regenerate the provenance map (manifest.json/csv) from ghidra/
make compile-commands # generate compile_commands.json for clangd (host, no container)
make clean
```

`relink` / `verify` / `verify-relink` / `verify-units` / `recon-status` run the
**original compiler** (Wind River `ccppc` 3.4.4) inside the i386 toolchain container
(`../toolchain/`); the Makefile wraps them via `$(WR)`. `manifest` and
`compile-commands` are pure host scripts.

## Carve-out relink model

The original image is the substrate; each proprietary RED function is progressively
promoted from binary blob to real source that compiles and links at its **original
absolute address**, calling the rest of the unchanged image by name. Third-party code
(VxWorks, OpenSSL, Xilinx) stays as blob.

How it works (`scripts/relink.py` + `scripts/gen_symbols_ld.py`):

1. `gen_symbols_ld.py` turns the manifest into `build/symbols.ld`
   (`PROVIDE(<name> = <abs addr>)` for all ~10.5k functions), so a reconstructed unit
   can `bl` / call any image function by name and the linker wires the PC-relative
   branch to the real image. Data/string addresses resolve the same way via
   `data_symbols.ld` (`D_<addr>`/`B_<addr>`), reproducing the original `@ha/@l`
   (`lis/addi`) relocations.
2. `relink.py` reuses `funcmatch`'s linking with the original `ccppc`. Units are
   discovered by `funcmatch.discover_units()` — every `*.c`/`*.S` under `red/` + `hw/`.
   Each function matching a manifest entry is linked at its absolute address.
3. **Overlay policy:** byte-`identical` units and `functional`-badged units
   (`functional.txt`, intentional differences) are overlaid; plain `draft` units are
   linked (proving they resolve) but left as original blob so an incomplete
   reconstruction can't corrupt the image.
   - `make verify-relink` passes when the relinked image differs from base *only* at
     the intentionally-badged functional units.
   - `make verify` (`relink.py --identity`) overlays **only** byte-exact units and
     asserts the result is byte-identical to `software.bin` — the north-star gate. As
     more functions reach byte-exact, the overlaid fraction grows while identity holds.

Run `make recon-status` for the live byte_exact/functional/draft breakdown. The full
workflow, fidelity tiers, and byte-matching rules are in `../RECONSTRUCTION.md`.

## Language server (clangd)

`make compile-commands` writes `compile_commands.json` (gitignored — machine-specific
absolute paths) with the pinned toolchain flags plus `-I include`, and `.clangd`
adapts clang's PPC frontend to the GCC-3.4.4 flags. Open any unit under `red/`/`hw/`
in VS Code with the clangd extension and cross-references / shared types resolve.

## Adding a function

`firmware/scripts/lift.py <addr> --scaffold` writes a starter unit at
`red/<module>/<name>.c` (module derived from the manifest), pre-wired with `extern`
decls and the Ghidra pseudocode. Iterate against
`firmware/scripts/funcmatch.py red/<module>/<name>.c` until the byte diff is zero.
