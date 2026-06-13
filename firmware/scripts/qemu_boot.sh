#!/usr/bin/env bash
# qemu_boot.sh — Boot RED ONE MX Build 32 firmware (software.bin) in QEMU
#
# Usage:
#   ./scripts/qemu_boot.sh [--debug] [--patched] [--net] [--build13]
#                          [--background] [--stop] [--serial-log=PATH] [--pidfile=PATH]
#
# --debug        Halt at PC=0x0 and open GDB stub on port 1234 for r2/gdb-multiarch
# --patched      Use software.patched.bin instead of the original
# --net          Enable TAP networking for WDB Ethernet access (requires tap0 to exist)
# --build13      Use Build 13 SundanceBootable.bin instead (legacy)
# --background   Daemonize: detach from stdio, serial→log file, write a pidfile.
#   (aka --daemon, -d)  Use this for automated/scripted runs (driving the gdb stub
#                from another process). A backgrounded -nographic QEMU has no TTY and
#                dies instantly, so this mode swaps in -display none / -serial file /
#                -daemonize.  Default serial log: /tmp/r1mx-qemu-serial.log
# --stop         Cleanly terminate a backgrounded instance (via pidfile, else by exact
#                process name — never `pkill -f`, which would also kill this script).
# --serial-log=PATH / --pidfile=PATH   Override the background log / pidfile locations.
#
# Example (background + gdb stub, then drive it):
#   ./scripts/qemu_boot.sh --patched --debug --background
#   python3 scripts/smoke_test.py        # or any rsp.py client on :1234
#   ./scripts/qemu_boot.sh --stop
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
# Required patches before booting (built from reverse/build_32/src; see its README):
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
BACKGROUND=0
STOP=0
PIDFILE="${R1MX_QEMU_PIDFILE:-/tmp/r1mx-qemu.pid}"
SERIAL_LOG="${R1MX_QEMU_SERIAL:-/tmp/r1mx-qemu-serial.log}"

for arg in "$@"; do
    case "$arg" in
        --debug)   DEBUG=1 ;;
        --patched) USE_PATCHED=1 ;;
        --net)     USE_NET=1 ;;
        --background|--daemon|-d) BACKGROUND=1 ;;
        --stop)    STOP=1 ;;
        --serial-log=*) SERIAL_LOG="${arg#*=}" ;;
        --pidfile=*)    PIDFILE="${arg#*=}" ;;
        --build13)
            BUILD13=1
            FW_DIR="$REPO_ROOT/reverse/Upgrade_Build 13/Upgrade"
            BIN_NAME="SundanceBootable.bin"
            PATCHED_NAME="SundanceBootable.patched.bin"
            ;;
    esac
done

# --stop: cleanly terminate a backgrounded instance. Match by PID file, or fall
# back to the EXACT process name (never `pkill -f`, which also matches this very
# script's command line and would kill the caller).
if [[ $STOP -eq 1 ]]; then
    QPID=""
    [[ -f "$PIDFILE" ]] && QPID="$(cat "$PIDFILE" 2>/dev/null)"
    if [[ -n "$QPID" ]] && kill -0 "$QPID" 2>/dev/null; then
        kill "$QPID" && echo "[*] stopped QEMU pid $QPID"
        rm -f "$PIDFILE"
    elif pgrep -x qemu-system-ppc >/dev/null; then
        # No valid pidfile — fall back to exact process name (never `pkill -f`,
        # which would also match this script's own command line and kill the caller).
        pkill -x qemu-system-ppc && echo "[*] stopped qemu-system-ppc (by name)"
        rm -f "$PIDFILE"
    else
        echo "[*] no running r1mx QEMU found"
    fi
    exit 0
fi

if [[ $USE_PATCHED -eq 1 ]]; then
    FIRMWARE="$FW_DIR/$PATCHED_NAME"
else
    FIRMWARE="$FW_DIR/$BIN_NAME"
fi

if [[ ! -f "$FIRMWARE" ]]; then
    echo "ERROR: firmware not found: $FIRMWARE"
    if [[ $USE_PATCHED -eq 1 ]]; then
        echo "  Run first:"
        echo "    make -C reverse/build_32/src install"
    fi
    exit 1
fi

QEMU_ARGS=(
    -machine r1mx-virtex4
    -m 2G

    # Load firmware flat binary at physical 0x00000000.
    # The PPC405 reset vector (hreset_vector) is patched to 0x0 in r1mx_virtex4.c
    # so no separate PC-setter loader is needed — and such a loader would clobber
    # the first instruction of the firmware by writing data to address 0x0.
    -device "loader,file=$FIRMWARE,addr=0x0,force-raw=on"
)

# Console handling differs by mode:
#   foreground : -nographic maps the XUartLite console + monitor onto stdio (mux).
#   background : stdio has no controlling TTY, so a backgrounded `-nographic` QEMU
#                dies immediately. Detach every chardev (display/monitor off, serial
#                to a log file) and let QEMU daemonize itself with a PID file.
if [[ $BACKGROUND -eq 1 ]]; then
    # NB: QEMU's own -pidfile is unreliable with -daemonize (the forking parent can
    # unlink it on exit), so we write our own pidfile from pgrep after launch.
    QEMU_ARGS+=(
        -display none
        -monitor none
        -serial "file:$SERIAL_LOG"
        -daemonize
    )
else
    # -nographic: serial0 → stdio (mon:stdio mux). Don't add -serial stdio too.
    QEMU_ARGS+=(-nographic)
fi

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

if [[ $BACKGROUND -eq 1 ]]; then
    # -daemonize double-forks; this invocation returns once QEMU is initialized.
    "$QEMU" "${QEMU_ARGS[@]}" </dev/null
    rc=$?
    if [[ $rc -ne 0 ]]; then
        echo "ERROR: QEMU failed to start (rc=$rc)"; exit $rc
    fi
    # Record the daemon's PID ourselves (newest qemu-system-ppc) for clean --stop.
    sleep 0.3
    QPID="$(pgrep -nx qemu-system-ppc || true)"
    [[ -n "$QPID" ]] && echo "$QPID" > "$PIDFILE"
    echo "[*] QEMU daemonized."
    [[ -n "$QPID" ]] && echo "[*]   PID:    $QPID  (pidfile: $PIDFILE)"
    echo "[*]   serial: $SERIAL_LOG"
    [[ $DEBUG -eq 1 ]] && echo "[*]   gdb stub: tcp::1234"
    echo "[*] Stop with: $0 --stop${PIDFILE:+ --pidfile=$PIDFILE}"
    exit 0
fi

exec "$QEMU" "${QEMU_ARGS[@]}"
