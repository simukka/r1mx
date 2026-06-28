#!/usr/bin/env bash
# qemu_boot.sh — Boot RED ONE MX Build 32 firmware (software.bin) in QEMU
#
# Usage:
#   ./scripts/qemu_boot.sh [--debug] [--patched] [--usernet|--net|--no-net] [--build13]
#                          [--background] [--stop] [--serial-log=PATH] [--pidfile=PATH]
#
# --debug        Halt at PC=0x0 and open GDB stub on port 1234 for r2/gdb-multiarch
# --patched      Use software.patched.r1mx.bin instead of the original.
#   WARNING: the patched image is BROKEN at the correct load base (0x10000). Its
#   patches (#47 zero-intCnt, SP reloc, canary NOPs) were symptom-fixes for the OLD
#   base-0 error; at base 0x10000 they corrupt a correct boot -> dead-spin at 0x10124.
#   The ORIGINAL software.bin (default, no flag) boots fully. Use --patched only for
#   regression checks, never for normal boots.
# Networking (XEmacLite @ 0xe1020000; camera is 192.168.0.2):
# --usernet      DEFAULT. SLIRP user networking — no root, no host setup. Forwards
#                host :2323 -> guest telnet :23 and host udp :17185 -> guest WDB :17185.
#                Override the telnet port with R1MX_TELNET_HOSTPORT (default 2323).
# --net          Use TAP networking instead (host tap0, needs root one-time setup).
#                Best for raw WDB/low-latency; gives the host 192.168.0.1 on the wire.
# --no-net       Disable networking entirely.
# --gui          Also launch the MMIO activity GUI (python3 -m toolkit.gui.emulator),
#                which connects to QEMU's activity broker on TCP localhost:17187.
#                Runs in the background; GUI stderr -> /tmp/r1mx-gui.log.
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
# Build 32 key addresses (confirmed: software.bin is LINKED FOR BASE 0x10000):
#   Load base  : 0x00010000  (-device loader addr=0x10000; hreset_vector=0x10000)
#   romInit    : file offset 0 -> runtime 0x00010000 (runs first at reset)
#   usrInit    : 0x0036C350   (symtab values are already runtime — do NOT +0x10000)
#   BSS start  : 0x00E9BF20
#   BSS end    : 0x01153480
#   UART Lite  : 0xe0600000 (XPS UARTLite console, PLB bus)
#   XIntc      : 0xe1200000 (interrupt controller — drives the vec-0x500 path)
#   XEmacLite  : 0xe1020000 (XPS EthernetLite — WDB transport / telnet)
#   WDB port   : UDP 17185 (0x4321) at camera IP 192.168.0.2
#
# NO source patches are required: the ORIGINAL software.bin boots unmodified once it
# is loaded at base 0x10000. The old SP-reloc / canary-NOP / zero-intCnt patches were
# symptom-fixes for the base-0 load error and now BREAK the boot — see --patched above.
# All the real work is in the QEMU device models (r1mx-virtex4 machine), not byte patches.
#
# Expected boot behaviour (original software.bin, default):
#   Reset vector executes DCR writes (SDRAM0/EBC0/CPC0/UIC0 init); QEMU ignores unknown
#   DCRs. Stack canaries are satisfied by RAM init; BSS is zero-initialised. The early
#   polled putc prints a few chars, then the interrupt-driven sio path takes over and the
#   full VxWorks banner + Sundance app init appear (status display / battery / USB / SDMC).
#   The VxWorks "->" shell prompt prints once the XIntc vec-0x500 path is live.
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
# The toolkit package lives at the project root, one level above firmware/.
PROJECT_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
GUI_LOG="${R1MX_GUI_LOG:-/tmp/r1mx-gui.log}"
GUI_PID=""    # set by launch_gui; used by the foreground cleanup trap

# Launch the MMIO activity GUI in the background. It connects to QEMU's broker on
# TCP localhost:17187 and retries every 3 s, so launch order vs. QEMU doesn't matter.
launch_gui() {
    if ! python3 -c 'import PyQt6' >/dev/null 2>&1; then
        echo "[!] --gui: PyQt6 not available; skipping GUI launch" >&2
        return
    fi
    ( cd "$PROJECT_ROOT" && python3 -m toolkit.gui.emulator.monitor ) >"$GUI_LOG" 2>&1 &
    GUI_PID=$!
    echo "[*] GUI: python3 -m toolkit.gui.emulator.monitor (pid $GUI_PID, log: $GUI_LOG)"
}

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
GUI=0
NET_MODE="usernet"   # default: SLIRP user networking (no root/host setup)
BUILD13=0
BACKGROUND=0
STOP=0
PIDFILE="${R1MX_QEMU_PIDFILE:-/tmp/r1mx-qemu.pid}"
SERIAL_LOG="${R1MX_QEMU_SERIAL:-/tmp/r1mx-qemu-serial.log}"
TELNET_HOSTPORT="${R1MX_TELNET_HOSTPORT:-2323}"

for arg in "$@"; do
    case "$arg" in
        --debug)   DEBUG=1 ;;
        --patched) USE_PATCHED=1 ;;
        --usernet) NET_MODE="usernet" ;;
        --net)     NET_MODE="tap" ;;
        --no-net)  NET_MODE="none" ;;
        --gui)     GUI=1 ;;
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

    # Load firmware flat binary at physical 0x00010000.
    # software.bin is a position-dependent VxWorks RAM image LINKED FOR BASE 0x10000
    # (proven 2026-06-20: .data initialisers + 12/13 firmware-computed code pointers +
    # BSS origin = filesize+0x10000 all resolve ONLY at this base; the camera's 0x10180
    # is a separate live placement).  hreset_vector is set to 0x10000 in
    # r1mx_virtex4.c so romInit (file offset 0 -> runtime 0x10000) runs first.
    -device "loader,file=$FIRMWARE,addr=0x10000,force-raw=on"
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
    # Foreground console: serial0 + monitor muxed onto stdio, same as -nographic.
    # We deliberately DON'T use -nographic here: -nographic forces the stdio chardev
    # to signal=off (so Ctrl-C is passed to the guest and you must use Ctrl-A X to
    # quit).  Using "-display none -serial mon:stdio" keeps the mux but leaves
    # signal=on (the default), so Ctrl-C delivers SIGINT -> QEMU exits, and the
    # cleanup trap below tears down the GUI too.  (Ctrl-A C still reaches the monitor;
    # Ctrl-A X still quits.)
    QEMU_ARGS+=(-display none -serial mon:stdio -d guest_errors)
fi

case "$NET_MODE" in
    usernet)
        # SLIRP user networking — no root, no host setup. Guest is 192.168.0.2 (from
        # the firmware bootline); SLIRP serves it on a private net behind the host.
        # Forward host -> guest for telnet (TCP 23) and WDB (UDP 17185).
        QEMU_ARGS+=(
            -nic "user,model=xlnx.xps-ethernetlite,net=192.168.0.0/24,host=192.168.0.1,mac=00:0a:35:00:00:01,hostfwd=tcp::${TELNET_HOSTPORT}-192.168.0.2:23,hostfwd=udp::17185-192.168.0.2:17185"
        )
        echo "[*] Networking: SLIRP user-net (XEmacLite) — camera is 192.168.0.2"
        echo "[*] Telnet: telnet 127.0.0.1 ${TELNET_HOSTPORT}   (-> guest :23)"
        echo "[*] WDB:    wdbrpc 127.0.0.1 17185                 (-> guest udp :17185)"
        echo ""
        ;;
    tap)
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
        ;;
    none)
        echo "[*] Networking: disabled (--no-net)"
        echo ""
        ;;
esac

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
    [[ $GUI -eq 1 ]] && launch_gui
    exit 0
fi

# Foreground: run QEMU as a child (NOT exec) so this shell survives to clean up the
# GUI when QEMU exits or the user hits Ctrl-C.  Ctrl-C sends SIGINT to the whole
# foreground process group (this shell + QEMU, same group since job control is off):
# QEMU quits on SIGINT (signal=on, set above) and the trap kills the GUI.
QEMU_PID=""
CLEANED=0
cleanup() {
    [[ $CLEANED -eq 1 ]] && return
    CLEANED=1
    trap - INT TERM EXIT   # disarm so cleanup runs once
    if [[ -n "$QEMU_PID" ]] && kill -0 "$QEMU_PID" 2>/dev/null; then
        kill "$QEMU_PID" 2>/dev/null || true
    fi
    if [[ -n "$GUI_PID" ]] && kill -0 "$GUI_PID" 2>/dev/null; then
        echo ""
        echo "[*] stopping GUI (pid $GUI_PID)"
        kill "$GUI_PID" 2>/dev/null || true
    fi
}
trap cleanup INT TERM EXIT

[[ $GUI -eq 1 ]] && launch_gui

"$QEMU" "${QEMU_ARGS[@]}" &
QEMU_PID=$!
wait "$QEMU_PID" || true   # INT/TERM trap, or the EXIT trap, runs cleanup
