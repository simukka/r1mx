#!/usr/bin/env bash
# build_qemu.sh — Clone and build the r1mx QEMU fork
#
# Clones https://github.com/simukka/qemu-r1mx (branch: r1mx, based on QEMU 8.2.2)
# and builds a ppc-softmmu binary.
#
# Output: ~/src/qemu-r1mx/build/qemu-system-ppc
#
# Usage:
#   ./firmware/scripts/build_qemu.sh          # clone (if needed) and build
#   ./firmware/scripts/build_qemu.sh --clean  # wipe and re-clone from scratch

set -euo pipefail

FORK_URL="git@github.com:simukka/qemu-r1mx.git"
FORK_BRANCH="r1mx"
DEST="$HOME/src/qemu-r1mx"

CLEAN=0
LOCAL=0
for arg in "$@"; do
  [[ "$arg" == "--clean" ]] && CLEAN=1
  [[ "$arg" == "--local" ]] && LOCAL=1
done

if [[ $CLEAN -eq 1 && -d "$DEST" ]]; then
  echo "-- Removing $DEST for clean build"
  rm -rf "$DEST"
fi

if [[ $LOCAL -eq 0 ]]; then
  if [[ ! -d "$DEST/.git" ]]; then
    echo "-- Cloning ${FORK_URL} (branch: ${FORK_BRANCH})..."
    git clone --single-branch -b "$FORK_BRANCH" "$FORK_URL" "$DEST"
    echo "-- Clone complete."
  else
    echo "-- ${DEST} already exists."
    echo "-- Pulling latest changes on branch ${FORK_BRANCH}..."
    git -C "$DEST" fetch origin
    git -C "$DEST" checkout "$FORK_BRANCH"
    git -C "$DEST" merge --ff-only "origin/${FORK_BRANCH}"
  fi
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
