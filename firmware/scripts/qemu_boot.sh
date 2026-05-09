#!/usr/bin/env bash
# qemu_boot.sh — Boot RED ONE MX Build 32 firmware (software.bin) in QEMU
#
# Usage:
#   ./scripts/qemu_boot.sh [--debug] [--patched] [--net] [--build13]
#
# --debug    Halt at PC=0x0 and open GDB stub on port 1234 for r2/gdb-multiarch
# --patched  Use software.patched.bin instead of the original
# --net      Enable TAP networking for WDB Ethernet access (requires tap0 to exist)
# --build13  Use Build 13 SundanceBootable.bin instead (legacy)
#
# Debugger attach (in a second terminal):
#   r2 -a ppc -b 32 -e cfg.bigendian=true \
#      -D gdb gdb://localhost:1234 \
#      -i scripts/r2_debug.r2
#
# QEMU machine: bamboo (PPC405EP/GP, 256 MB SDRAM at 0x0)
# CPU: 405gp (matches firmware DCR set: SDRAM0, EBC0, CPC0, UIC0)
#
# Build 32 key addresses (confirmed from static analysis):
#   Load base  : 0x00000000
#   Entry point: 0x00000000 (reset vector / exception table)
#   usrInit    : 0x0036C350
#   BSS start  : 0x00E9BF20
#   BSS end    : 0x01153480
#   UART Lite  : 0x40600000 (Xilinx UART Lite IP, 8-bit MMIO)
#   XEmacLite  : 0x40C00000 (Xilinx Ethernet MAC — WDB transport)
#   WDB port   : UDP 17185 (0x4321) at camera IP 192.168.0.2
#
# Required patches before booting (see scripts/patch_firmware.py):
#   1. SP relocation: offset 0x84 — lis r1,1 → lis r1,0x800
#   2. Canary NOP:    offset 0x36C388 — bne cr7,loop → NOP
#   3. Canary NOP:    offset 0x36C394 — bne cr7,loop → NOP
#   + Phase 2 MMIO patches as crash sites are discovered
#
# Expected first-boot behaviour (patched binary):
#   Reset vector executes DCR writes (SDRAM0/EBC0/CPC0/UIC0 init).
#   QEMU bamboo silently ignores unknown DCR accesses — these pass.
#   Stack canary wait loop is NOP'd → falls through to BSS zero-init.
#   First real crash is at MMIO peripheral init (~0xDCB0 or 0x12DB4).
#   Use --debug + r2 to step through and identify crash addresses for patching.
#
# TAP networking setup (one-time, as root):
#   ip tuntap add dev tap0 mode tap
#   ip addr add 192.168.0.1/24 dev tap0
#   ip link set tap0 up
#
# WDB connection (after camera boots):
#   wdbrpc 192.168.0.2 17185
#   # OR: Wind River Workbench → UDP target 192.168.0.2:17185

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Defaults — Build 32
FW_DIR="$REPO_ROOT/reverse/build_32/extracted"
BIN_NAME="software.bin"
PATCHED_NAME="software.patched.bin"

DEBUG=0
USE_PATCHED=0
USE_NET=0
BUILD13=0

for arg in "$@"; do
    case "$arg" in
        --debug)   DEBUG=1 ;;
        --patched) USE_PATCHED=1 ;;
        --net)     USE_NET=1 ;;
        --build13)
            BUILD13=1
            FW_DIR="$REPO_ROOT/reverse/Upgrade_Build 13/Upgrade"
            BIN_NAME="SundanceBootable.bin"
            PATCHED_NAME="SundanceBootable.patched.bin"
            ;;
    esac
done

if [[ $USE_PATCHED -eq 1 ]]; then
    FIRMWARE="$FW_DIR/$PATCHED_NAME"
else
    FIRMWARE="$FW_DIR/$BIN_NAME"
fi

if [[ ! -f "$FIRMWARE" ]]; then
    echo "ERROR: firmware not found: $FIRMWARE"
    if [[ $USE_PATCHED -eq 1 ]]; then
        echo "  Run first:"
        echo "    python3 scripts/patch_firmware.py"
    fi
    exit 1
fi

QEMU_ARGS=(
    -machine bamboo
    -m 256M
    -nographic

    # Load firmware flat binary at physical 0x00000000
    -device "loader,file=$FIRMWARE,addr=0x0,force-raw=on"
    # Set reset PC to 0x0
    -device "loader,cpu-num=0,data=0x0,data-len=4,data-be=on"
)

if [[ $USE_NET -eq 1 ]]; then
    if ! ip link show tap0 &>/dev/null; then
        echo "ERROR: tap0 not found. Create it first (as root):"
        echo "  ip tuntap add dev tap0 mode tap"
        echo "  ip addr add 192.168.0.1/24 dev tap0"
        echo "  ip link set tap0 up"
        exit 1
    fi
    QEMU_ARGS+=(
        -netdev "tap,id=net0,ifname=tap0,script=no,downscript=no"
        -device "xemaclite,netdev=net0,mac=00:0a:35:00:00:01"
    )
    echo "[*] Networking: TAP (tap0 → xemaclite) — camera will be 192.168.0.2"
    echo "[*] WDB connect: wdbrpc 192.168.0.2 17185"
    echo ""
fi

if [[ $DEBUG -eq 1 ]]; then
    echo "[*] Debug mode — halting at PC=0x0, GDB stub on :1234"
    echo "[*] In a second terminal, run:"
    echo "      r2 -a ppc -b 32 -e cfg.bigendian=true \\"
    echo "         -D gdb gdb://localhost:1234 \\"
    echo "         -i scripts/r2_debug.r2"
    echo ""
    QEMU_ARGS+=(-S -gdb tcp::1234)
fi

LABEL="Build 32 v32.0.3"
[[ $BUILD13 -eq 1 ]] && LABEL="Build 13 (legacy)"
[[ $USE_PATCHED -eq 1 ]] && LABEL="$LABEL [PATCHED]"

echo "[*] RED ONE MX QEMU Boot — $LABEL"
echo "[*] Firmware: $FIRMWARE"
echo "[*] Launching: qemu-system-ppc ${QEMU_ARGS[*]}"
echo ""

exec qemu-system-ppc "${QEMU_ARGS[@]}"
