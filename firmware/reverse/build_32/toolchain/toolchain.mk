# toolchain.mk -- the ORIGINAL compiler that built RED ONE MX Build 32:
# Wind River GNU GCC 3.4.4, target powerpc-wrs-vxworks. Runs in the i386 container
# (see Dockerfile / in-container.sh). Include from a Makefile to compile/link units
# with the exact toolchain so reconstructions rebuild byte-for-byte.
#
#   include ../toolchain/toolchain.mk
#   $(CCPPC) $(WR_CFLAGS) -c foo.c -o foo.o

WR         := $(dir $(lastword $(MAKEFILE_LIST)))in-container.sh
CCPPC      := $(WR) ccppc
GXXPPC     := $(WR) c++ppc
OBJCOPYPPC := $(WR) objcopyppc
OBJDUMPPPC := $(WR) objdumpppc
LDPPC      := $(WR) ldppc
READELFPPC := $(WR) readelfppc
NMPPC      := $(WR) nmppc

# RED *application* build flags, pinned by funcmatch:
#   - units/mmio_leaves.c   10/10 byte-exact (incl. indexed/byte-reversed inline asm)
#   - units/red_app_proof.c  1/1 byte-exact (app_modules/digmag thunk @0x4db598:
#                            frame-16 ABI, scheduled prologue, @ha/@l data reloc)
# NOTE: vendor libc/VxWorks/OpenSSL were built by Wind River with DIFFERENT flags
# (e.g. libc memcmp uses a CTR bdnz loop unreachable from these flags) -- those stay
# blob; do not flag-pin against them. See units/libc_leaves.c.
WR_CFLAGS  := -mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic
WR_CXXFLAGS := $(WR_CFLAGS) -fno-exceptions -fno-rtti
