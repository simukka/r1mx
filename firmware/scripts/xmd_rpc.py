#!/usr/bin/env python3
"""
xmd_rpc.py — host driver for the Channel B file-queue bridge (xmd_agent.tcl).

Sends one XMD command to the agent running inside XMD in the WinXP VM and
returns its output, using only the shared folder (no networking). Use this for
XMD-only commands the GDB stub doesn't expose: gated `mrd` of DCR/peripheral
registers, JTAG ops, SPR reads XMD supports.

    python3 firmware/scripts/xmd_rpc.py "rrd"
    python3 firmware/scripts/xmd_rpc.py "mrd 0xe0600000 4"
    python3 firmware/scripts/xmd_rpc.py --parse-mrd "mrd 0x0 16"   # -> bytes

The agent enforces a read-only denylist (rst/mwr/rwr/dow/program/erase/...),
so a mutating command round-trips as an ERROR rather than executing.
"""

import argparse
import os
import sys
import time

# Host side of the Y:\r1mx\ <-> repo share, plus the bridge scratch dir.
DEFAULT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scratch", "xmd_bridge")
DONE = "__DONE__"


def rpc(cmd, dir_=DEFAULT_DIR, timeout=30.0, poll=0.1):
    os.makedirs(dir_, exist_ok=True)
    cmd_f = os.path.join(dir_, "xmd_cmd.txt")
    out_f = os.path.join(dir_, "xmd_out.txt")
    # Clear any stale result, then post the command atomically.
    for f in (out_f, cmd_f):
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
    tmp = cmd_f + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(cmd)
    os.replace(tmp, cmd_f)

    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(out_f):
            with open(out_f, "r", errors="replace") as fh:
                text = fh.read()
            if DONE in text:
                return text.split(DONE)[0].rstrip("\n")
        time.sleep(poll)
    raise TimeoutError(f"no agent response within {timeout}s "
                       f"(is agent_loop running in XMD? dir={dir_})")


def parse_mrd(text):
    """Parse XMD `mrd` output ('ADDR: VAL VAL ...') into big-endian bytes."""
    out = bytearray()
    for line in text.splitlines():
        ci = line.find(":")
        if ci < 0:
            continue
        for tok in line[ci + 1:].split():
            try:
                out += int(tok, 16).to_bytes(4, "big")
            except ValueError:
                pass
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", help="XMD command to run (quote it)")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="bridge scratch dir")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--parse-mrd", action="store_true",
                    help="parse mrd output and print hex bytes")
    args = ap.parse_args()

    try:
        res = rpc(args.command, args.dir, args.timeout)
    except TimeoutError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 1

    if args.parse_mrd:
        print(parse_mrd(res).hex())
    else:
        print(res)
    return 1 if res.startswith("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
