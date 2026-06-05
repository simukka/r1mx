#!/usr/bin/env python3
"""
probe_serial.py — RED ONE MX USB serial interface probe tool

Deep-characterizes the camera's CDC-ACM serial port (/dev/ttyACM0,
VID:PID=1c56:5232).  Beyond the original baud/AT sweep this now does:

  * --listen N      passive listen for N seconds (no stimulus) — run this
                    while power-cycling the camera to catch a boot banner.
  * line-ending matrix (\\r, \\n, \\r\\n, lone Ctrl-C) for every shell probe
  * control-line manipulation: every DTR/RTS combination, read after each
  * BREAK condition (some firmwares gate console TX on it)
  * modem-status readback (CD/CTS/DSR/RI) after every step
  * timestamped capture log under firmware/reverse/build_32/captures/

Prerequisites:
  pip install pyserial
  sudo usermod -aG dialout $USER  (then re-login or: newgrp dialout)

Usage:
  python3 probe_serial.py                       # full active matrix
  python3 probe_serial.py --listen 30           # passive listen, 30 s
  python3 probe_serial.py --baud 115200         # single baud
  python3 probe_serial.py --no-control          # skip DTR/RTS/BREAK

Context:
  The camera enumerates CDC-ACM unconditionally.  The VxWorks shell
  (runTargetShell) is only active when DEBUG.USB.CONNECTION != 0.
  Use WDB over Ethernet (wdb_probe.py, 192.168.0.2:17185 UDP) to set that
  param first.  See: firmware/reverse/build_32/debug_interfaces.md
"""

import argparse
import datetime
import os
import sys
import time

import serial


BAUD_RATES = [115200, 57600, 38400, 19200, 9600]

# Stimuli that are appended with each line-ending in the matrix.
SHELL_PROBES = [
    ("",        "bare line-ending"),
    ("AT",      "AT probe"),
    ("ATI",     "AT identify"),
    ("help",    "VxWorks: help"),
    ("i",       "VxWorks: i (task list)"),
    ("devs",    "VxWorks: devs"),
    ("version", "VxWorks: version"),
    ('lkup "DEBUG"', "VxWorks: lkup DEBUG"),
]

LINE_ENDINGS = [
    (b"\r",   "CR"),
    (b"\n",   "LF"),
    (b"\r\n", "CRLF"),
]

# Default capture directory (relative to repo root, resolved from this file).
_THIS = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_DIR = os.path.normpath(
    os.path.join(_THIS, "..", "reverse", "build_32", "captures")
)


class Logger:
    """Tee writer: everything goes to stdout and to a capture file."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._fh = open(path, "w", encoding="utf-8")
        self.log(f"# probe_serial.py capture — {_utc()}")

    def log(self, msg: str = ""):
        print(msg)
        self._fh.write(msg + "\n")
        self._fh.flush()

    def close(self):
        self._fh.close()


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def hexdump(data: bytes, indent: str = "    ") -> str:
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{indent}{i:04X}  {hex_part:<48}  {asc_part}")
    return "\n".join(lines)


def modem_state(ser: serial.Serial) -> str:
    """Read the input control lines; not all are supported everywhere."""
    parts = []
    for name in ("cts", "dsr", "cd", "ri"):
        try:
            parts.append(f"{name.upper()}={int(getattr(ser, name))}")
        except Exception:
            parts.append(f"{name.upper()}=?")
    return " ".join(parts)


def drain(ser: serial.Serial, settle: float) -> bytes:
    """Wait `settle` seconds then read whatever is buffered."""
    time.sleep(settle)
    return ser.read(ser.in_waiting or 4096)


def passive_listen(port: str, baud: int, seconds: float, log: Logger) -> bool:
    """Open the port and capture without sending anything."""
    log.log(f"\n=== PASSIVE LISTEN  baud={baud}  {seconds}s ===")
    log.log("Power-cycle the camera now to catch any boot banner.")
    got = False
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
    except serial.SerialException as e:
        log.log(f"  ERROR opening port: {e}")
        return False
    log.log(f"  lines @ open: {modem_state(ser)}")
    deadline = time.time() + seconds
    try:
        while time.time() < deadline:
            chunk = ser.read(4096)
            if chunk:
                got = True
                log.log(f"  [+{seconds - (deadline - time.time()):5.1f}s] "
                        f"{len(chunk)} bytes:")
                log.log(hexdump(chunk))
    finally:
        ser.close()
    if not got:
        log.log("  (silent — no bytes during listen window)")
    return got


def probe_baud(port: str, baud: int, timeout: float, do_control: bool,
               log: Logger) -> bool:
    """Active probe matrix at one baud rate. Returns True if any response."""
    log.log(f"\n=== ACTIVE PROBE  baud={baud} ===")
    got = False
    try:
        ser = serial.Serial(
            port, baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )
    except serial.SerialException as e:
        log.log(f"  ERROR opening port: {e}")
        return False

    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        log.log(f"  lines @ open: {modem_state(ser)}")

        # --- line-ending matrix --------------------------------------------
        for body, name in SHELL_PROBES:
            for ending, ename in LINE_ENDINGS:
                stim = body.encode() + ending
                ser.write(stim)
                resp = drain(ser, timeout)
                if resp:
                    got = True
                    log.log(f"  [{name} / {ename}] {stim!r} -> "
                            f"{len(resp)} bytes  ({modem_state(ser)}):")
                    log.log(hexdump(resp))

        # lone Ctrl-C — some shells only react to an interrupt
        ser.write(b"\x03")
        resp = drain(ser, timeout)
        if resp:
            got = True
            log.log(f"  [Ctrl-C] -> {len(resp)} bytes:")
            log.log(hexdump(resp))

        # --- control-line manipulation -------------------------------------
        if do_control:
            for dtr in (True, False):
                for rts in (True, False):
                    ser.dtr = dtr
                    ser.rts = rts
                    resp = drain(ser, timeout)
                    state = modem_state(ser)
                    line = f"  [DTR={int(dtr)} RTS={int(rts)}] {state}"
                    if resp:
                        got = True
                        log.log(line + f"  -> {len(resp)} bytes:")
                        log.log(hexdump(resp))
                    else:
                        log.log(line + "  (silent)")
            # restore asserted state and poke once more
            ser.dtr = True
            ser.rts = True
            ser.write(b"\r")
            resp = drain(ser, timeout)
            if resp:
                got = True
                log.log(f"  [DTR/RTS asserted + CR] -> {len(resp)} bytes:")
                log.log(hexdump(resp))

            # --- BREAK ------------------------------------------------------
            try:
                ser.send_break(duration=0.25)
                resp = drain(ser, timeout)
                if resp:
                    got = True
                    log.log(f"  [BREAK] -> {len(resp)} bytes:")
                    log.log(hexdump(resp))
                else:
                    log.log("  [BREAK] (silent)")
            except Exception as e:
                log.log(f"  [BREAK] not supported: {e}")
    finally:
        ser.close()

    if not got:
        log.log(f"  (silent on all stimuli @ baud={baud})")
    return got


def main():
    parser = argparse.ArgumentParser(description="RED ONE MX ttyACM0 serial probe")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="Settle/read timeout per stimulus (s)")
    parser.add_argument("--baud", type=int, nargs="+", default=BAUD_RATES,
                        help="Baud rate(s) to try")
    parser.add_argument("--listen", type=float, metavar="SECONDS",
                        help="Passive-listen for N seconds, then exit "
                             "(uses the first --baud value)")
    parser.add_argument("--no-control", action="store_true",
                        help="Skip DTR/RTS toggling and BREAK")
    parser.add_argument("--log-dir", default=DEFAULT_LOG_DIR,
                        help="Directory for the timestamped capture log")
    args = parser.parse_args()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = os.path.join(args.log_dir, f"usb_serial_{stamp}.log")
    log = Logger(log_path)
    log.log(f"port={args.port}  baud={args.baud}  timeout={args.timeout}s")
    log.log(f"capture -> {log_path}")

    any_response = False
    try:
        if args.listen:
            any_response = passive_listen(
                args.port, args.baud[0], args.listen, log
            )
        else:
            for baud in args.baud:
                if probe_baud(args.port, baud, args.timeout,
                              not args.no_control, log):
                    any_response = True

        log.log("")
        if any_response:
            log.log("Response received — shell may be active!")
        else:
            log.log("No response on any stimulus.")
            log.log("The VxWorks USB shell is likely dormant "
                    "(DEBUG.USB.CONNECTION = 0).")
            log.log("Next step: wake it via WDB over Ethernet — "
                    "see wdb_probe.py / debug_interfaces.md")
    finally:
        log.close()

    sys.exit(0 if any_response else 1)


if __name__ == "__main__":
    main()
