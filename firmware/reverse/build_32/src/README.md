# RED ONE MX Build 32 — firmware source & patch build

This tree is the **authoritative source** for the patched Build 32 firmware. The
patched QEMU-boot image is **built from here**, not produced by an external
byte-patching script. (The legacy `firmware/scripts/patch_firmware.py` has been
retired; its byte patches now live in `patches/patches.S` as toolchain-built,
flag-gated source.)

## Build

```bash
make r1mx      # default: the image QEMU boots (extracted/software.patched.r1mx.bin)
make verify    # build r1mx and assert SHA-256 == 281ef88a… (re_reference §0.1)
make install   # build + verify, then copy to ../extracted/software.patched.r1mx.bin
make all       # every group incl. bamboo device-gap (generic PPC machine)
make bare      # base image, no patches (sanity: == ../extracted/software.bin)
make GROUPS="CPU_CORE SNAPSHOT_DATA"   # arbitrary subset
make clean
```

## How it works

`patches/patches.S` defines each patch as a named section `.patch_<fileoffset>`
whose bytes overlay the base image (`../extracted/software.bin`) at that offset.
The Makefile assembles the groups selected by `-DGROUP_*` flags
(`powerpc-linux-gnu-gcc -x assembler-with-cpp`), then `objcopy`/`dd`s each section
onto a fresh copy of the base image. Before overlaying, each target's existing
bytes are checked against `patches/originals.txt` (drift guard). `make verify`
proves the result is byte-identical to the committed image.

The patch bytes are authoritative (`.long`); the trailing comment on each is the
disassembly, and the per-patch header carries the full rationale (migrated from
the old script). Where the replacement is real code (e.g. `CPU_CORE` #62, the
Program-Exception handler) the disassembly is genuine PPC mnemonics.

## Build-flag groups

| Group (`-DGROUP_*`) | r1mx default | What it is |
|---|---|---|
| `CPU_CORE` | on | PPC405 core / boot-stub / exception-vector adaptations. #62/#63 may indicate real qemu-r1mx TCG gaps. |
| `SNAPSHOT_DATA` | on | Fixes for `.data`/BSS values a cold boot would set but that QEMU hasn't run the init to produce (BSS sentinels, C++ vtable ptrs, sysMemTop/intCnt slots, the bctrl bypasses those cause). *Group name is legacy:* `software.bin` is the shipped firmware program image, **not** a RAM snapshot — see re_reference §0.3 / [[firmware-image-and-framing]]. |
| `DISPATCH_SCAFFOLD` | on | Forces a non-crashing first context switch given the not-yet-initialized root-task TCB/globals (lands in OpenSSL X.509v3 — a patch artifact). |
| `CRYPTO_BYPASS` | on | Bypasses signature / SSD-compat / SSL-callback checks that can't complete in emulation. |
| `DEVICE_GAP` | **off** | Workarounds for MMIO unmapped on the OLD generic 'bamboo' machine (XUartLite, RAM-size). The r1mx-virtex4 machine maps the real devices, so these are skipped. |
| `INCLUDE_DISABLED` | off | Patches proven WRONG, kept for the record only (e.g. #57). |

See `firmware/reverse/build_32/re_reference.md` §0.3 for the patch audit and the
boot analysis behind these groups.

## Carve-out relink build (reconstructed source → firmware)

The patch overlay above is a QEMU-boot crutch. The real decompilation goal —
**rebuilding firmware from reconstructed C/C++** — uses the *carve-out relink*
model: the original image is the substrate; each proprietary RED function is
progressively promoted from binary blob to real source that compiles and links
at its **original absolute address**, calling the rest of the unchanged image by
name. Third-party code (VxWorks, OpenSSL, Xilinx) stays as blob.

```bash
make manifest        # (re)build the provenance map src/manifest.{json,csv}
make relink          # compile src/units/*, overlay onto base -> build/software.relinked.bin
make verify-relink   # additionally assert every unmodified unit is byte-identical
```

How it works (`scripts/relink.py` + `scripts/gen_symbols_ld.py`):

1. `gen_symbols_ld.py` turns the provenance manifest into `build/symbols.ld`:
   `PROVIDE(<name> = <abs addr>)` for all 10.5k functions — so a reconstructed
   unit can `bl main_boot_init` / call `FUN_0036c350` and the linker wires the
   PC-relative branch to the real image. Data/string addresses resolve the same way
   via `units/data_symbols.ld` (`D_<addr>`/`B_<addr>`), giving the original `@ha/@l`
   (`lis/addi`) relocations.
2. `relink.py` reuses `funcmatch`'s linking with the **original `ccppc`** (so it runs
   in the toolchain container — `make relink`/`verify-relink` wrap it). Each function
   in `src/units/*.c|*.S` matching a manifest entry is linked at its absolute address.
3. **Overlay policy:** byte-`identical` units and `functional`-badged units
   (`units/functional.txt`, intentional differences) are overlaid; plain `draft`
   units are linked (proving they resolve) but left as original blob so an incomplete
   reconstruction can't corrupt the image. `make verify-relink` passes when the
   relinked image differs from base *only* at the intentionally-badged units.

The full workflow, fidelity tiers, and byte-matching rules are in
`firmware/reverse/build_32/RECONSTRUCTION.md`. As of now, 18 reconstructed functions
rebuild byte-identical (MMIO leaves, the `common_utils_thunks`, the
`sensor_slot_ioctl` libsensor accessors, and `FUN_004db598`); see
`firmware/reverse/build_32/PROVENANCE.md` for the provenance taxonomy.

## Other contents

`boot.c`, `boot_entry.S`, `uart.c`, `ssd.c`, `usrRoot/`, `xmlsocket/`,
`all_functions/` are the earlier in-progress C/asm reconstruction (Ghidra-assisted);
`r1mx_firmware.ld` is an aspirational whole-image linker script (superseded by the
per-unit relink model above for practical work). The patch build does not depend
on them.
