#!/usr/bin/env python3
"""
probe_serial.py — RED ONE MX USB serial interface probe tool

Probes /dev/ttyACM0 (CDC-ACM, VID=1c56:5232) at multiple baud rates,
sending both AT-command probes and VxWorks shell openers, and logging
any response in hex + ASCII.

Prerequisites:
  pip install pyserial
  sudo usermod -aG dialout $USER  (then re-login or: newgrp dialout)

Usage:
  python3 probe_serial.py [--port /dev/ttyACM0] [--timeout 1.0]

Context:
  The camera enumerates CDC-ACM unconditionally.  The VxWorks shell
  (runTargetShell) is only active when DEBUG.USB.CONNECTION != 0.
  Use WDB over Ethernet (192.168.0.2:17185 UDP) to set that param first.
  See: firmware/reverse/build_32/debug_interfaces.md
"""

import argparse
import serial
import time
import sys


BAUD_RATES = [115200, 57600, 38400, 19200, 9600]

PROBES = [
    (b"\r\n",                     "bare CRLF"),
    (b"AT\r\n",                   "AT probe"),
    (b"ATE0\r\n",                 "AT echo off"),
    (b"ATI\r\n",                  "AT identify"),
    (b"\r\n",                     "CRLF again"),
    (b"help\r\n",                 "VxWorks: help"),
    (b"i\r\n",                    "VxWorks: i (task list)"),
    (b"devs\r\n",                 "VxWorks: devs"),
    (b"version\r\n",              "VxWorks: version"),
    (b"lkup \"DEBUG\"\r\n",       "VxWorks: lkup DEBUG"),
]


def hexdump(data: bytes, indent: str = "    ") -> str:
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{indent}{i:04X}  {hex_part:<48}  {asc_part}")
    return "\n".join(lines)


def probe_port(port: str, baud: int, timeout: float) -> bool:
    """Returns True if any response was received."""
    got_response = False
    try:
        ser = serial.Serial(
            port, baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        ser.flushInput()
        ser.flushOutput()

        for probe_bytes, probe_name in PROBES:
            ser.write(probe_bytes)
            time.sleep(timeout)
            response = ser.read(ser.in_waiting or 512)
            if response:
                print(f"  [BAUD={baud}] probe={probe_name!r}  → {len(response)} bytes:")
                print(hexdump(response))
                got_response = True

        ser.close()
    except serial.SerialException as e:
        print(f"  [BAUD={baud}] ERROR: {e}")
    return got_response


def main():
    parser = argparse.ArgumentParser(description="RED ONE MX ttyACM0 serial probe")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--timeout", type=float, default=0.5, help="Read timeout (s)")
    parser.add_argument("--baud", type=int, nargs="+", default=BAUD_RATES,
                        help="Baud rate(s) to try")
    args = parser.parse_args()

    print(f"Probing {args.port}  baud rates: {args.baud}")
    print(f"Timeout per probe: {args.timeout}s\n")

    any_response = False
    for baud in args.baud:
        print(f"--- Baud {baud} ---")
        if probe_port(args.port, baud, args.timeout):
            any_response = True

    if not any_response:
        print("\nNo response on any baud rate.")
        print("The VxWorks USB shell is not active (DEBUG.USB.CONNECTION = 0).")
        print("Next step: enable via WDB over Ethernet — see debug_interfaces.md")
        sys.exit(1)
    else:
        print("\nResponse received — shell may be active!")
        sys.exit(0)


if __name__ == "__main__":
    main()
