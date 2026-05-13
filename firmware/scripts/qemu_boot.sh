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
# QEMU machine: r1mx-virtex4 (custom PPC405F6 machine matching Virtex-4 FX)
#   Binary: ~/src/qemu-r1mx/build/qemu-system-ppc
#   CPU: x2vp4, PVR overridden to 0x20011000 (Virtex-4 PPC405F6 hard-core)
#
# Build 32 key addresses (confirmed from static analysis):
#   Load base  : 0x00000000
#   Entry point: 0x00000000 (reset vector / exception table)
#   usrInit    : 0x0036C350
#   BSS start  : 0x00E9BF20
#   BSS end    : 0x01153480
#   UART Lite  : 0xe0600000 (XPS UARTLite, PLB bus)
#   XEmacLite  : 0xe1020000 (XPS EthernetLite — WDB transport)
#   WDB port   : UDP 17185 (0x4321) at camera IP 192.168.0.2
#
# Required patches before booting (see scripts/patch_firmware.py):
#   1. SP relocation: offset 0x84 — lis r1,1 → lis r1,0x800
#   2. Canary NOP:    offset 0x36C388 — bne cr7,loop → NOP
#   3. Canary NOP:    offset 0x36C394 — bne cr7,loop → NOP
#   (MMIO patches #37-42 are no longer needed — real device models handle them)
#
# Expected first-boot behaviour (patched binary):
#   Reset vector executes DCR writes (SDRAM0/EBC0/CPC0/UIC0 init).
#   QEMU silently ignores unknown DCR accesses — these pass.
#   Stack canary wait loop is NOP'd → falls through to BSS zero-init.
#   VxWorks boot banner appears on console (XUartLite → stdio).
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

# Custom QEMU binary with r1mx-virtex4 machine
QEMU="${QEMU:-${HOME}/src/qemu-r1mx/build/qemu-system-ppc}"
if [[ ! -x "$QEMU" ]]; then
    echo "ERROR: Custom QEMU not found at $QEMU"
    echo "  Build it first:"
    echo "    cd ~/src/qemu-r1mx && make -j\$(nproc)"
    exit 1
fi

# Defaults — Build 32
FW_DIR="$REPO_ROOT/reverse/build_32/extracted"
BIN_NAME="software.bin"
PATCHED_NAME="software.patched.r1mx.bin"  # r1mx-specific patch set (no bamboo-only NOPs)

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
        echo "    python3 scripts/patch_firmware.py --r1mx"
    fi
    exit 1
fi

QEMU_ARGS=(
    -machine r1mx-virtex4
    -m 256M
    -nographic

    # Load firmware flat binary at physical 0x00000000.
    # The PPC405 reset vector (hreset_vector) is patched to 0x0 in r1mx_virtex4.c
    # so no separate PC-setter loader is needed — and such a loader would clobber
    # the first instruction of the firmware by writing data to address 0x0.
    -device "loader,file=$FIRMWARE,addr=0x0,force-raw=on"

    # XUartLite console: -nographic already maps serial0→stdio (mon:stdio mux)
    # Adding -serial stdio here would conflict and fail; let QEMU use the default.
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
        -nic "tap,model=xlnx.xps-ethernetlite,netdev=net0,mac=00:0a:35:00:00:01"
    )
    echo "[*] Networking: TAP (tap0 → XEmacLite) — camera will be 192.168.0.2"
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
echo "[*] QEMU: $QEMU"
echo "[*] Launching: ${QEMU} ${QEMU_ARGS[*]}"
echo ""

exec "$QEMU" "${QEMU_ARGS[@]}"
