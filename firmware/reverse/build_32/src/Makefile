# Makefile -- reconstruct the RED ONE MX Build 32 firmware from source.
#
# The "carve-out relink" model: reconstructed C/asm units under red/ and hw/ are
# compiled with the ORIGINAL compiler (Wind River ccppc 3.4.4, in the i386 container),
# each function is linked at its absolute address and overlaid onto the original
# software.bin. As functions reach byte_exact fidelity the reconstructed fraction
# grows while the image stays bit-for-bit identical to the original. See README.md.
#
#   make verify           # BIT-FOR-BIT GATE: overlay byte-exact units, assert sha256 == original
#   make relink           # working reconstructed image (byte-exact + functional overlays)
#   make verify-relink    # assert every non-functional unit is byte-identical to base
#   make verify-units     # byte-match the fully-byte-exact units with the original compiler
#   make recon-status     # reconstruction coverage dashboard -> recon_status.json
#   make manifest         # regenerate the provenance map (manifest.json/csv) from ghidra/
#   make compile-commands # generate compile_commands.json for clangd (host, no container)
#   make clean
#
# relink / verify / verify-relink / verify-units / recon-status run inside the
# toolchain container (via $(WR)); manifest and compile-commands are pure host scripts.

SCRIPTS := ../../../scripts

include ../toolchain/toolchain.mk

.PHONY: verify relink verify-relink verify-units recon-status manifest \
        compile-commands clean help

# --- provenance map --------------------------------------------------------
# Regenerate manifest.json/csv (the absolute-address symbol table + fidelity map)
# from the Ghidra intake in ghidra/ merged with recon_status.json.
manifest:
	python3 $(SCRIPTS)/build_provenance_map.py

# --- carve-out relink build ------------------------------------------------
# relink        : reconstructed image (byte-exact + intentional functional overlays)
# verify-relink : assert every non-functional unit is byte-identical to the original
# verify        : BIT-FOR-BIT GATE -- overlay ONLY byte-exact units and assert the
#                 relinked image is byte-identical to ../extracted/software.bin.
relink: manifest
	$(WR) python3 $(SCRIPTS)/relink.py

verify-relink: manifest
	$(WR) python3 $(SCRIPTS)/relink.py --verify

verify: manifest
	$(WR) python3 $(SCRIPTS)/relink.py --identity

# --- byte-for-bit unit matching with the ORIGINAL compiler -----------------
# Compile the fully-byte-exact units with Wind River ccppc 3.4.4 (in the i386
# container) and assert each function rebuilds to the original firmware bytes. Units
# that still contain draft functions (e.g. xmlsocket_conn_ops.c, diag_thunks.c) are
# tracked by `recon-status`, not here -- funcmatch would report their drafts as
# mismatches (non-zero exit).
verify-units:
	$(WR) python3 $(SCRIPTS)/funcmatch.py \
		hw/mmio_leaves.c \
		red/app_modules/digmag/red_app_proof.c \
		red/app_modules/common/utils_thunks.c \
		red/lib/libsensor/sensor_slot_ioctl.c

# Reconstruction dashboard: rebuild every unit under red/ + hw/ with the original
# compiler, report byte_exact/functional/draft coverage, and write recon_status.json
# (the manifest fidelity source). funcdiff.py (behavioural validation) needs a live
# QEMU target -- run it by hand against firmware/scripts/qemu_boot.sh --debug.
recon-status:
	$(WR) python3 $(SCRIPTS)/recon_status.py

# --- language server (clangd) ----------------------------------------------
# Emit compile_commands.json (gitignored; machine-specific absolute paths) so clangd /
# IntelliSense can navigate and type-check the reconstructed C/C++. Pure host script.
compile-commands:
	python3 $(SCRIPTS)/gen_compile_commands.py

clean:
	rm -rf build

help:
	@grep '^#   make' Makefile | sed 's/^#   //'
