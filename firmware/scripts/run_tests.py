#!/usr/bin/env python3
"""run_tests.py -- run the full RED ONE MX Build 32 test suite and roll up results.

Three layers (re_reference.md §0.5), in increasing cost:
  Layer 1  test_re_facts.py          static / RE facts    (no QEMU, instant)
  Layer 2  smoke_test.py             dynamic firmware boot (QEMU)
  Layer 3  test_emulator_devices.py  emulator device map  (QEMU, no firmware)

Use this to settle documentation discrepancies by running tests rather than
re-reading notes.  Treat re_reference.md §0 as the authoritative current state.

Usage:
    .venv/bin/python firmware/scripts/run_tests.py            # all layers
    .venv/bin/python firmware/scripts/run_tests.py --static   # Layer 1 only (no QEMU)
    .venv/bin/python firmware/scripts/run_tests.py -v         # forward -v to each layer

Exit code 0 only if every run layer passes.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# (title, script, needs_qemu)
LAYERS = [
    ("Layer 0: hardware-safety (read-only)", "test_hw_safety.py",  False),
    ("Layer 1: static / RE facts",    "test_re_facts.py",         False),
    ("Layer 2: firmware boot (QEMU)", "smoke_test.py",            True),
    ("Layer 3: emulator devices",     "test_emulator_devices.py", True),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the Build 32 test suite (all layers)")
    ap.add_argument("--static", action="store_true", help="run only Layer 1 (no QEMU)")
    ap.add_argument("-v", "--verbose", action="store_true", help="forward -v to each layer")
    args = ap.parse_args()

    py = sys.executable
    rollup: list[tuple[str, int | None, str]] = []
    for title, script, needs_qemu in LAYERS:
        if args.static and needs_qemu:
            rollup.append((title, None, "skipped (--static)"))
            continue
        cmd = [py, str(_HERE / script)]
        if args.verbose:
            cmd.append("-v")
        print("\n" + "#" * 64)
        print(f"# {title}  ({script})")
        print("#" * 64)
        t0 = time.monotonic()
        rc = subprocess.run(cmd).returncode
        rollup.append((title, rc, f"{time.monotonic() - t0:.1f}s"))

    GREEN, RED, YEL, RST = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
    tty = sys.stdout.isatty()
    print("\n" + "=" * 64)
    print("  SUITE ROLL-UP")
    failed = 0
    for title, rc, info in rollup:
        if rc is None:
            tag, col = "SKIP", YEL
        elif rc == 0:
            tag, col = "PASS", GREEN
        else:
            tag, col = "FAIL", RED
            failed += 1
        line = f"  [{tag}]  {title}  ({info})"
        print(col + line + RST if tty else line)
    print("=" * 64)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
