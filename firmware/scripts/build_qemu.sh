#!/usr/bin/env bash
# build_qemu.sh — Build the r1mx-patched QEMU 8.2.2
#
# Downloads QEMU 8.2.2 tarball, applies r1mx patches, configures, and
# builds a ppc-softmmu QEMU binary.
#
# Output: ~/src/qemu-r1mx/build/qemu-system-ppc
#
# Usage:
#   ./firmware/scripts/build_qemu.sh          # normal build
#   ./firmware/scripts/build_qemu.sh --clean  # wipe and rebuild from scratch

set -euo pipefail

QEMU_VERSION="8.2.2"
QEMU_TARBALL="qemu-${QEMU_VERSION}.tar.xz"
QEMU_URL="https://download.qemu.org/${QEMU_TARBALL}"
QEMU_SHA256="847346c1b82c1a54b2c38f6edbd85549edeb17430b7d4d3da12620e2962bc4f3"
DEST="$HOME/src/qemu-r1mx"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PATCH_DIR="${REPO_ROOT}/firmware/patches/qemu"

CLEAN=0
for arg in "$@"; do
  [[ "$arg" == "--clean" ]] && CLEAN=1
done

if [[ $CLEAN -eq 1 && -d "$DEST" ]]; then
  echo "-- Removing $DEST for clean build"
  rm -rf "$DEST"
fi

if [[ ! -d "$DEST" ]]; then
  TMPDIR=$(mktemp -d)
  trap 'rm -rf "$TMPDIR"' EXIT

  echo "-- Downloading QEMU ${QEMU_VERSION}..."
  cd "$TMPDIR"
  curl -L --progress-bar -o "$QEMU_TARBALL" "$QEMU_URL"

  echo "-- Verifying checksum..."
  echo "${QEMU_SHA256}  ${QEMU_TARBALL}" | sha256sum --check

  echo "-- Extracting to ${DEST}..."
  tar xf "$QEMU_TARBALL"
  mv "qemu-${QEMU_VERSION}" "$DEST"

  echo "-- Applying r1mx patches..."
  cd "$DEST"

  # Apply meson.build patch (register r1mx_virtex4.c)
  patch -p1 < "${PATCH_DIR}/0001-r1mx-virtex4-machine.patch"

  # Apply upstream bug fixes
  patch -p1 < "${PATCH_DIR}/0002-ppc32-tlb-vaddr-truncation.patch"
  patch -p1 < "${PATCH_DIR}/0003-ppc32-crosspage-addr-truncation.patch"

  # PPC405 FSL instruction support (APU/FCM - required for VxWorks boot)
  patch -p1 < "${PATCH_DIR}/0004-ppc405-fsl-instructions.patch"

  # Silence SLER abort: firmware uses 0x7c as a countdown counter during early boot,
  # causing transient mtspr SLER encoding that would otherwise abort QEMU
  patch -p1 < "${PATCH_DIR}/0005-silence-sler-abort.patch"

  # Copy new machine file (not patchable - it is entirely new)
  cp "${PATCH_DIR}/src/hw/ppc/r1mx_virtex4.c" "${DEST}/hw/ppc/r1mx_virtex4.c"
  echo "   hw/ppc/r1mx_virtex4.c installed"

  echo "-- All patches applied."
else
  echo "-- ${DEST} already exists, skipping download/patch (use --clean to start over)"
fi

echo "-- Configuring QEMU (ppc-softmmu only, debug build)..."
cd "$DEST"
mkdir -p build
cd build
../configure \
  --target-list="ppc-softmmu" \
  --enable-debug \
  --disable-docs \
  --disable-werror \
  --audio-drv-list="" \
  2>&1 | tail -5

echo "-- Building (this takes a few minutes)..."
make -j"$(nproc)" 2>&1 | tail -20

BINARY="${DEST}/build/qemu-system-ppc"
if [[ -x "$BINARY" ]]; then
  echo ""
  echo "=== Build successful ==="
  echo "Binary: ${BINARY}"
  "$BINARY" --version | head -1
  echo ""
  echo "Supported machines (r1mx):"
  "$BINARY" -M help 2>/dev/null | grep -i "r1mx\|virtex\|ppc4"
else
  echo "ERROR: Build failed — ${BINARY} not found" >&2
  exit 1
fi
