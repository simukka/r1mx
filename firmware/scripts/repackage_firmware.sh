#!/usr/bin/env bash
# repackage_firmware.sh — Re-encrypt and repackage modified RED ONE MX firmware
#
# Takes a modified software.bin (or software.patched.bin), re-encrypts it,
# and produces a drop-in replacement redone.su ready to flash via SmartUpgrade.
#
# Usage:
#   ./scripts/repackage_firmware.sh [OPTIONS]
#
# Options:
#   --input PATH      Modified software.bin (default: reverse/build_32/extracted/software.patched.bin)
#   --build-dir PATH  Directory with original redone.2 and redone.4 files
#                     (default: reverse/build_32/extracted)
#   --output PATH     Output redone.su path (default: /tmp/redone.su)
#   --verify          Decrypt and verify the output before writing
#
# Camera installation:
#   1. Copy output redone.su to CF card: mkdir -p /mnt/cf/upgrade && cp redone.su /mnt/cf/upgrade/
#   2. Insert CF into camera and boot
#   3. SmartUpgrade() auto-detects upgrade/redone.su and applies it
#   4. Camera reboots with modified firmware
#
# Search order (camera checks all of these):
#   /tffs0/upgrade/redone.su    — internal NOR flash (highest priority)
#   /ata00:1/upgrade/redone.su  — CF card slot 0
#   /ata10:1/upgrade/redone.su  — CF card slot 1
#   /sdmc/upgrade/redone.su     — SD card
#   /usbd0/upgrade/redone.su    — USB mass storage
#
# Encryption:
#   Algorithm: AES-256-CBC with MD5 key derivation (OpenSSL -md md5 mode)
#   Key: M1H5gwOXh757rIRVY6Gj2tN080AYSX03
#   Format: gzip | openssl enc -e → redone.N file

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS='M1H5gwOXh757rIRVY6Gj2tN080AYSX03'

# Defaults
INPUT="$REPO_ROOT/reverse/build_32/extracted/software.patched.bin"
BUILD_DIR="$REPO_ROOT/reverse/build_32/extracted"
OUTPUT="/tmp/redone.su"
VERIFY=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input)     INPUT="$2"; shift 2 ;;
        --build-dir) BUILD_DIR="$2"; shift 2 ;;
        --output)    OUTPUT="$2"; shift 2 ;;
        --verify)    VERIFY=1; shift ;;
        -h|--help)
            sed -n '2,40p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "[*] RED ONE MX — Firmware Repackager"
echo ""

# Validate inputs
if [[ ! -f "$INPUT" ]]; then
    echo "ERROR: input not found: $INPUT" >&2
    echo "  Run first: python3 scripts/patch_firmware.py" >&2
    exit 1
fi

echo "[*] Input software.bin:  $INPUT"
echo "    size: $(wc -c < "$INPUT") bytes"
echo "    sha256: $(sha256sum "$INPUT" | cut -d' ' -f1)"
echo ""

# Locate supporting files
# redone.2: usually splash screen or VP-FPGA — keep original
# redone.3: I/O FPGA bitstream — keep original (we're only modifying software)
# redone.4: version manifest — keep original

check_file() {
    local path="$1"
    local label="$2"
    if [[ ! -f "$path" ]]; then
        echo "ERROR: $label not found: $path" >&2
        echo "  Decrypt original build_32_v32.0.3.zip first:" >&2
        echo "    cd firmware/builds && unzip build_32_v32.0.3.zip" >&2
        echo "    tar xf build_32_v32.0.3/redone.su -C reverse/build_32/extracted/" >&2
        return 1
    fi
    return 0
}

# Try to find redone.2/3/4 from the build dir or original extracted archive
ARCHIVE_DIR="$REPO_ROOT/builds/build_32_v32.0.3"
SRC_DIR=""
for d in "$BUILD_DIR" "$ARCHIVE_DIR" "$REPO_ROOT/reverse/build_32"; do
    if [[ -f "$d/redone.2" ]]; then
        SRC_DIR="$d"
        break
    fi
done

if [[ -z "$SRC_DIR" ]]; then
    echo "ERROR: Cannot find redone.2/3/4 (original encrypted components)." >&2
    echo "  Extract the original archive first:" >&2
    echo "    cd firmware/builds" >&2
    echo "    unzip build_32_v32.0.3.zip" >&2
    echo "    cd build_32_v32.0.3" >&2
    echo "    tar xf redone.su" >&2
    echo "    cp redone.2 redone.3 redone.4 $BUILD_DIR/" >&2
    exit 1
fi

echo "[*] Supporting files from: $SRC_DIR"
check_file "$SRC_DIR/redone.2" "redone.2 (splash/VP-FPGA)" || exit 1
check_file "$SRC_DIR/redone.3" "redone.3 (I/O FPGA bitstream)" || exit 1
check_file "$SRC_DIR/redone.4" "redone.4 (version manifest)" || exit 1

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo ""
echo "[*] Encrypting software.bin → redone.1 ..."
gzip -9 -c "$INPUT" | \
    openssl enc -e -aes-256-cbc -md md5 \
        -pass "pass:$PASS" \
        -out "$WORKDIR/redone.1"

echo "    redone.1 size: $(wc -c < "$WORKDIR/redone.1") bytes"

# Copy original components
cp "$SRC_DIR/redone.2" "$WORKDIR/redone.2"
cp "$SRC_DIR/redone.3" "$WORKDIR/redone.3"
cp "$SRC_DIR/redone.4" "$WORKDIR/redone.4"

echo ""
echo "[*] Packaging into redone.su ..."
(cd "$WORKDIR" && tar cf redone.su redone.1 redone.2 redone.3 redone.4)

if [[ $VERIFY -eq 1 ]]; then
    echo ""
    echo "[*] Verifying round-trip decrypt ..."
    VERIFY_DIR="$(mktemp -d)"
    tar xf "$WORKDIR/redone.su" -C "$VERIFY_DIR"

    openssl enc -d -aes-256-cbc -md md5 \
        -pass "pass:$PASS" \
        -in "$VERIFY_DIR/redone.1" | gunzip > "$VERIFY_DIR/software.verify.bin"

    ORIG_SHA="$(sha256sum "$INPUT" | cut -d' ' -f1)"
    VFY_SHA="$(sha256sum "$VERIFY_DIR/software.verify.bin" | cut -d' ' -f1)"
    rm -rf "$VERIFY_DIR"

    if [[ "$ORIG_SHA" == "$VFY_SHA" ]]; then
        echo "    [OK] Round-trip verified — sha256 matches"
    else
        echo "    [FAIL] SHA mismatch!" >&2
        echo "      original: $ORIG_SHA" >&2
        echo "      verified: $VFY_SHA" >&2
        exit 1
    fi
fi

cp "$WORKDIR/redone.su" "$OUTPUT"
echo ""
echo "[*] Output: $OUTPUT"
echo "    size: $(wc -c < "$OUTPUT") bytes"
echo "    sha256: $(sha256sum "$OUTPUT" | cut -d' ' -f1)"
echo ""
echo "[*] Camera installation:"
echo "    mkdir -p /mnt/cf/upgrade"
echo "    cp $OUTPUT /mnt/cf/upgrade/redone.su"
echo "    # Insert CF into camera and boot"
echo "    # SmartUpgrade() will detect and apply the firmware"
