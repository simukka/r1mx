# attic — archived, not built

Superseded reconstruction experiments and the obsolete standalone boot/driver stubs,
kept only for reference. Nothing here is part of any build. The live source tree is
`../src/` (carve-out relink of the original `software.bin`); see `../src/README.md`.

- `xmlsocket/`, `usrRoot/` — exploratory per-function intake, superseded by the maintained
  units under `../src/red/`.
- `boot.c`, `boot_entry.S`, `uart.c`, `ssd.c` (+ `.o`), `r1mx_firmware.ld` — standalone
  bring-up experiments from before the base-`0x10000` load was understood.
- `libc_leaves.c` — illustrative vendor (VxWorks/Dinkum libc) near-matches, not a real
  reconstruction target.
