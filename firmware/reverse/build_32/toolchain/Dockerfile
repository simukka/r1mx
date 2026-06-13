# Wind River GNU GCC 3.4.4 (target powerpc-wrs-vxworks) — i386 build container.
#
# The original RED ONE MX Build 32 firmware was compiled with THIS toolchain: the
# image's embedded symbol table carries GCC's out-of-line prologue helpers
# (_savegpr_/_restgpr_), the libgcc 64-bit arithmetic family (__divdi3 ...), and
# __gnu_cplusplus_std_libraryInit — all GNU GCC fingerprints, not Diab. (The
# __x_diab_* strings are statically-linked Diab soft-float runtime helpers from a
# Wind River prebuilt libc, not evidence the app was Diab-built.)
#
# The compiler binaries are 2009 32-bit x86 ELF (interpreter /lib/ld-linux.so.2),
# so we host them in a small i386-capable container. This makes byte-for-bit
# rebuilds hermetic and portable; the determinism comes from the fixed ccppc binary
# itself (its PPC codegen doesn't depend on the host) — the container only
# guarantees ccppc/cc1/binutils *run*.
#
# The toolchain tree is NOT copied into the image: it lives in the repo at
#   firmware/reverse/build_32/toolchain/wr-gcc-3.4.4-ppc/x86-linux2
# and is bind-mounted at run time by toolchain/in-container.sh. This image provides
# only the 32-bit runtime. Rebuild rarely; run often.
#
# TODO: pin by digest once settled, e.g. debian:bullseye-slim@sha256:<...>
FROM debian:bullseye-slim

RUN dpkg --add-architecture i386 \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      libc6:i386 libstdc++6:i386 zlib1g:i386 \
      make python3 xxd file binutils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
