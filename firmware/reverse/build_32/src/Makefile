# Makefile -- build the RED ONE MX Build 32 patched firmware from source.
#
# Replaces the legacy firmware/scripts/patch_firmware.py.  The patches live in
# patches/patches.S as toolchain-built sections; this Makefile assembles the
# groups selected by build flags and overlays them onto the base image.
#
#   make r1mx        # default: build the r1mx-virtex4 image (the one QEMU boots)
#   make all         # every group incl. bamboo device-gap (generic machine)
#   make bare        # base image, no patches (sanity)
#   make GROUPS="CPU_CORE SNAPSHOT_DATA"   # custom subset
#   make verify      # build r1mx and check SHA-256 == expected
#   make install     # build r1mx and copy to ../extracted/software.patched.r1mx.bin
#   make clean
#
# Per-group toggles map to -DGROUP_<NAME> passed to the assembler's preprocessor.
# See patches/patches.S for the group definitions.

CROSS    := powerpc-linux-gnu-
CC       := $(CROSS)gcc
OBJCOPY  := $(CROSS)objcopy
READELF  := $(CROSS)readelf

BASE     := ../extracted/software.bin
BUILDDIR := build
OUT      := $(BUILDDIR)/software.patched.r1mx.bin
OBJ      := $(BUILDDIR)/patches.o
SRC      := patches/patches.S
ORIG     := patches/originals.txt

# Expected SHA-256 of the default (lean) r1mx build (re_reference.md §0.1).
EXPECT_SHA := f97e33a17d802f4a4e9bc3f16411dcc0475e7afd6e9e0b46263fa9f1f8685550

# --- group selection ------------------------------------------------------
R1MX_GROUPS := CPU_CORE SNAPSHOT_DATA DISPATCH_SCAFFOLD CRYPTO_BYPASS
ALL_GROUPS  := CPU_CORE SNAPSHOT_DATA DISPATCH_SCAFFOLD CRYPTO_BYPASS DEVICE_GAP

GROUPS  ?= $(R1MX_GROUPS)
DEFINES := $(foreach g,$(GROUPS),-DGROUP_$(g))

# Patches bisected to be UNNECESSARY to reach the boot dispatch+liveness state
# (see re_reference §0.3 "patch necessity map").  Excluded from the default image.
REDUNDANT := \
  00e26ddc 00e27000 00e276b8 00e27bd4 00e29438 00e2a3c8 00e2a748 \
  00e2a918 00e2a994 00e2a9b4 00e2b590 00e2b7d8 \
  00388280 00388284 003878cc 00371c9c \
  005b5964 005b596c 00381ad0 0038042c 00380430 0037c33c 00371d5c \
  005d552c 005d58e8 \
  00000700 00000734

# Patches now IMPLEMENTED IN qemu-r1mx (boot SP relocate #1 + VxWorks canaries
# #2/#3; see hw/ppc/r1mx_virtex4.c r1mx_apply_boot_env_fixups).  The r1mx-virtex4
# machine supplies these at boot, so the firmware image no longer needs them.
# NOTE: only the r1mx machine implements them — the bamboo `make all`/`full`
# images keep them (EXCLUDE="").
MOVED_TO_QEMU := 00000084 0036c388 0036c394

# Default image excludes both sets (29 patch sections).  Override EXCLUDE to
# build variants; `make full` builds the legacy 59-patch image.
EXCLUDE ?= $(REDUNDANT) $(MOVED_TO_QEMU)

.PHONY: r1mx all bare full verify install clean help FORCE manifest relink verify-relink

r1mx: $(OUT)

# Legacy 59-patch image (no exclusions).  Boots on stock qemu, and also on the
# patched r1mx machine (the moved-in fixups are idempotent).
full:
	$(MAKE) EXCLUDE="" $(OUT)

all:
	$(MAKE) GROUPS="$(ALL_GROUPS)" EXCLUDE="" $(OUT)

bare:
	$(MAKE) GROUPS="" EXCLUDE="" $(OUT)

# Assemble the selected patch groups into one relocatable object.
# FORCE: always reassemble, since the group selection (DEFINES) is not a file dep.
$(OBJ): $(SRC) FORCE | $(BUILDDIR)
	$(CC) -mbig-endian -nostdlib -c -x assembler-with-cpp $(DEFINES) $(SRC) -o $@

FORCE:

# Overlay each .patch_<offset> section onto a fresh copy of the base image.
$(OUT): $(OBJ) $(BASE) | $(BUILDDIR)
	@cp $(BASE) $(OUT)
	@secs=$$($(READELF) -S $(OBJ) | grep -oE '\.patch_[0-9a-f]{8}' | sort -u); \
	n=0; \
	for s in $$secs; do \
	  raw=$${s#.patch_}; \
	  case " $(EXCLUDE) $(DROP) " in *" $$raw "*) continue;; esac; \
	  off=$$((0x$$raw)); \
	  $(OBJCOPY) -O binary --only-section=$$s $(OBJ) $(BUILDDIR)/frag.bin; \
	  exp=$$(grep -i "^0x$${s#.patch_} " $(ORIG) | awk '{print $$3}'); \
	  len=$$(stat -c%s $(BUILDDIR)/frag.bin); \
	  got=$$(dd if=$(OUT) bs=1 skip=$$off count=$$len status=none | xxd -p | tr -d '\n'); \
	  if [ -n "$$exp" ] && [ "$$got" != "$$exp" ]; then \
	    echo "VERIFY FAIL @$$s: base has $$got, expected original $$exp"; exit 1; fi; \
	  dd if=$(BUILDDIR)/frag.bin of=$(OUT) bs=1 seek=$$off conv=notrunc status=none; \
	  n=$$((n+1)); \
	done; \
	rm -f $(BUILDDIR)/frag.bin; \
	echo "applied $$n patch sections  [groups: $(GROUPS)]"
	@echo "built $(OUT)"
	@sha256sum $(OUT)

verify: $(OUT)
	@got=$$(sha256sum $(OUT) | cut -d' ' -f1); \
	if [ "$$got" = "$(EXPECT_SHA)" ]; then \
	  echo "SHA OK: $$got"; \
	else \
	  echo "SHA MISMATCH"; echo "  got:    $$got"; echo "  expect: $(EXPECT_SHA)"; exit 1; \
	fi

install: verify
	cp $(OUT) ../extracted/software.patched.r1mx.bin
	@echo "installed -> ../extracted/software.patched.r1mx.bin"

# --- carve-out relink build ------------------------------------------------
# Overlay reconstructed C/asm units (src/units/*) onto the base image, each
# function linked at its original absolute address (see scripts/relink.py and
# PROVENANCE.md).  `relink` builds software.relinked.bin; `verify-relink`
# additionally asserts every unmodified unit is byte-identical to the original
# (proving the reconstruction is exact).  `manifest` regenerates the provenance
# map that drives the absolute-address symbol table.
SCRIPTS := ../../../scripts

manifest:
	python3 $(SCRIPTS)/build_provenance_map.py

relink: manifest
	python3 $(SCRIPTS)/relink.py

verify-relink: manifest
	python3 $(SCRIPTS)/relink.py --verify

$(BUILDDIR):
	@mkdir -p $(BUILDDIR)

clean:
	rm -rf $(BUILDDIR)

help:
	@sed -n '3,20p' Makefile
