# Original toolchain — Wind River GNU GCC 3.4.4 (powerpc-wrs-vxworks)

This is the **exact compiler that built the RED ONE MX Build 32 firmware**, hosted in a
small i386 Docker container for hermetic, byte-for-bit rebuilds.

## Why this is the original compiler

The firmware's embedded symbol table carries GNU GCC fingerprints — `_savegpr_14..31` /
`_restgpr_14..31` (GCC's out-of-line prologue/epilogue helpers), the libgcc `__divdi3 /
__udivdi3 / __moddi3` family, and `__gnu_cplusplus_std_libraryInit`. (The `__x_diab_*`
strings are statically-linked Diab soft-float runtime helpers from a Wind River prebuilt
libc, **not** evidence the app was Diab-built.) The driver self-identifies as
`Wind River vxworks-6.x 3.4.4-86`, target `powerpc-wrs-vxworks` — and it reproduces the
original firmware bytes for the `mmio_leaves` accessors exactly (see `funcmatch.py`).

## Layout

```
toolchain/
  Dockerfile            i386 build image (debian + 32-bit runtime). Toolchain is NOT copied in.
  in-container.sh       run any command inside the image with the toolchain on PATH + repo mounted
  wr-gcc-3.4.4-ppc/     extracted x86-linux2 compiler tree (GITIGNORED, ~34 MB)
  toolchain.mk          ccppc/binutils paths + the matching CFLAGS (consumed by Makefile/relink)
  README.md             this file
```

## One-time setup

```bash
# 1. extract the Linux-host compiler from the bundle (gitignored target dir)
cd firmware/reverse/build_32/toolchain
unzip -p ../../../../libraries/GCC3.4.4_VxWorks6.4/cum.vxw6-3.4.4-ppc.2009aug07.zip \
      cum.vxw6-3.4.4-ppc.2009aug07.tgz | tar -C wr-gcc-3.4.4-ppc -xzf - x86-linux2

# 2. build the container (once)
docker build -t wr-build:3.4.4 .
```

## Use

```bash
# any toolchain command:
toolchain/in-container.sh ccppc --version
toolchain/in-container.sh objdumpppc -d foo.o

# the byte-for-bit matcher:
toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
        firmware/reverse/build_32/src/units/mmio_leaves.c
```

## Gotchas

- **`WIND_BASE` must be defined.** The driver's header spec calls `getenv(WIND_BASE /target/h)`;
  if unset the compile aborts. `in-container.sh`/`funcmatch.py` set a stub if you don't. For
  reconstructions that include real VxWorks headers, point it at an extracted target tree
  (`cum.tgt.vxw6-3.4.4-powerpc…` / `cum.vxw6-3.4.4-ppc-target…` inside the same zip).
- **`cs-license: error trying to exec 'get_feature'`** on stderr is **benign** — this CodeSourcery
  license check fails open; compilation completes normally.
- Binaries are 2009 32-bit x86 ELF (`/lib/ld-linux.so.2`) → that's why they run in the i386
  container, not on the bare 64-bit host.
- A 2015 PPC respin (`cum.vxw6-3.4.4-ppc.2015feb12.zip`) and full gcc-3.4.4 source are in the
  bundle as fallbacks if the 2009 binaries ever misbehave.
