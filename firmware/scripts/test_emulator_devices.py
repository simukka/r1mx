#!/usr/bin/env python3
"""test_emulator_devices.py -- Layer 3 of the RED ONE MX Build 32 test suite.

Verifies the QEMU `r1mx-virtex4` machine's device map and MMIO behavior
INDEPENDENT of the firmware -- it loads no firmware, it just inspects the machine
the emulator builds.  This catches emulator regressions (a peripheral that moved,
got renamed, or was dropped) without needing a full firmware boot, and proves the
emulator's memory map matches the documented one.

Source of truth for the expected map: CLAUDE.md (machine table) + re_reference.md
§6 (MMIO peripheral map).

Method: launch QEMU halted (-S) with an HMP monitor on stdio, no firmware, then
  * `info mtree -f`  -> each documented peripheral is mapped at its base with the
                        expected device-model name; histogram IP appears ×5; NOR
                        is 128 MB; RAM is mapped at 0.
  * `xp` reads       -> NOR flash returns 0xFF, RAM returns 0x00.

`info mtree -f` emits one flatview per address space (a legacy "I/O" space rooted
at `io`, and the CPU "memory" space rooted at `system`).  Only the system space
holds RAM + peripherals, and flatview emission order is NOT stable -- so we filter
to the system space, otherwise the 0x0 lookup is non-deterministic (the I/O space
also has a region at 0x0).

Layered suite (re_reference.md §0.5):
    Layer 1  test_re_facts.py            (static / RE facts, no QEMU)
    Layer 2  smoke_test.py               (dynamic firmware boot in QEMU)
    Layer 3  test_emulator_devices.py    <-- this file (emulator device map/behavior)

Future extensions: per-device register reset values (e.g. XIntc MER==0, UARTLite
STAT), and write/read-back checks on r/w device registers.

Usage:
    .venv/bin/python firmware/scripts/test_emulator_devices.py [-v]
    .venv/bin/python firmware/scripts/test_emulator_devices.py --qemu /path/to/qemu-system-ppc

Exit code 0 if all assertions pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

DEFAULT_QEMU = Path.home() / "src/qemu-r1mx/build/qemu-system-ppc"
MACHINE = "r1mx-virtex4"

# Expected device map: base -> (model-name substring, human description).
# Each must appear as a region START in the system address space.  (CLAUDE.md / re_ref §6)
EXPECTED_DEVICES = [
    (0x64010000, "opb-dma-channel",  "XPS Central DMA"),
    (0xB2600000, "xps-iic",          "XIic (I2C)"),
    (0xE0600000, "xps-uartlite",     "XUartLite (console)"),
    (0xE0640000, "uart16550-0",      "XUartNs550 #1"),
    (0xE0650000, "uart16550-1",      "XUartNs550 #2"),
    (0xE0800000, "xps-intc",         "XIntc (interrupt controller)"),
    (0xE1020000, "xps-ethernetlite", "XEmacLite (Ethernet)"),
    (0xE1200000, "opb-pci-host",     "XPci_v3 host bridge"),
    (0xF0000000, "nor-flash",        "NOR flash"),
]

HISTOGRAM_NAME = "red.histogram-ip"            # CLAUDE.md: "RED histogram IP ×5"
HISTOGRAM_BASES = [0xE0080000, 0xE00A0000, 0xE0100000, 0xE0120000, 0xE0200000]

NOR_BASE = 0xF0000000
NOR_END = 0xF7FFFFFF        # 128 MB region
RAM_BASE = 0x00000000

# flat-mtree region line: "  <16hex>-<16hex> (prio N, type): name"
_MTREE_RE = re.compile(
    r"^\s*([0-9a-f]{16})-([0-9a-f]{16})\s+\(prio\s+(-?\d+),\s+[^)]+\):\s+(.+?)\s*$")
# address-space header: 'AS "memory", root: system'  or  'Root memory region: io'
_ROOT_RE = re.compile(r"root(?: memory region)?:\s*(\S+)", re.IGNORECASE)
# xp byte-dump line: "<hex>: 0xNN 0xNN ..."  (8 bytes/line)
_XP_RE = re.compile(r"^([0-9a-f]{8,16}):\s+((?:0x[0-9a-f]{2}\s*)+)$")


@dataclass
class Region:
    start: int
    end: int
    prio: int
    name: str


def run_qemu_monitor(qemu: Path, cmds: str, timeout: float = 30.0) -> str:
    proc = subprocess.run(
        [str(qemu), "-machine", MACHINE, "-m", "2048",
         "-display", "none", "-serial", "null", "-monitor", "stdio", "-S"],
        input=cmds, capture_output=True, text=True, timeout=timeout)
    return proc.stdout + proc.stderr


def parse_mtree(out: str) -> list[Region]:
    """Return regions from the *system* memory address space only, deduped.

    We track the current flatview's root (from its 'root: X' header) and keep
    region lines only while inside the `system` root.  This is stable regardless
    of the order QEMU emits flatviews in.
    """
    regions: list[Region] = []
    seen: set[tuple[int, int, str]] = set()
    current_root: str | None = None
    for line in out.splitlines():
        rm = _ROOT_RE.search(line)
        if rm:
            current_root = rm.group(1).strip().strip('",')
            continue
        if current_root != "system":
            continue
        m = _MTREE_RE.match(line)
        if m:
            key = (int(m.group(1), 16), int(m.group(2), 16), m.group(4))
            if key not in seen:
                seen.add(key)
                regions.append(Region(key[0], key[1], int(m.group(3)), key[2]))
    return regions


def parse_xp(out: str) -> dict[int, list[int]]:
    """Map dump start-address -> list of byte values."""
    reads = {}
    for line in out.splitlines():
        m = _XP_RE.match(line)
        if m:
            reads[int(m.group(1), 16)] = [int(b, 16) for b in m.group(2).split()]
    return reads


def main() -> int:
    ap = argparse.ArgumentParser(description="r1mx-virtex4 emulator device tests (Layer 3)")
    ap.add_argument("--qemu", type=Path, default=DEFAULT_QEMU)
    ap.add_argument("-v", "--verbose", action="store_true", help="show every check")
    args = ap.parse_args()

    print("RED ONE MX Build 32 — Emulator Device Suite (Layer 3)")
    print(f"  qemu:    {args.qemu}")
    print(f"  machine: {MACHINE}\n")
    if not args.qemu.exists():
        print(f"ERROR: QEMU not found: {args.qemu}")
        print("  Build it:  cd ~/src/qemu-r1mx && make -j$(nproc)")
        return 1

    cmds = f"info mtree -f\nxp/8xb 0x{NOR_BASE:x}\nxp/8xb 0x{RAM_BASE:x}\nquit\n"
    try:
        out = run_qemu_monitor(args.qemu, cmds)
    except subprocess.TimeoutExpired:
        print("ERROR: QEMU monitor timed out")
        return 1

    regions = parse_mtree(out)
    reads = parse_xp(out)
    if not regions:
        print("ERROR: could not parse a `system` flatview from `info mtree -f`. First 2 KB:")
        print(out[:2000])
        return 1

    starts: dict[int, list[Region]] = defaultdict(list)
    for r in regions:
        starts[r.start].append(r)

    def at(base: int) -> list[Region]:
        return starts.get(base, [])

    results: list[tuple[bool, str, str]] = []   # (passed, label, detail)

    # -- device map: each documented peripheral at its base ----------------
    for base, name_sub, desc in EXPECTED_DEVICES:
        rs = at(base)
        match = next((r for r in rs if name_sub in r.name), None)
        results.append((match is not None, f"{desc} @ 0x{base:08x} ({name_sub})",
                        f"-> {match.name!r}" if match
                        else (f"-> {[r.name for r in rs]}" if rs else "-> NOT MAPPED")))

    # -- RED histogram IP ×5 -----------------------------------------------
    hist = [r for r in regions if HISTOGRAM_NAME in r.name]
    results.append((len(hist) == 5, f"RED histogram IP ×5 ({HISTOGRAM_NAME})",
                    f"found {len(hist)} regions"))
    for base in HISTOGRAM_BASES:
        match = next((r for r in at(base) if HISTOGRAM_NAME in r.name), None)
        results.append((match is not None, f"histogram IP @ 0x{base:08x}",
                        f"-> {match.name!r}" if match else "-> NOT MAPPED"))

    # -- NOR size + RAM presence -------------------------------------------
    nor = next((r for r in at(NOR_BASE) if "nor" in r.name.lower()), None)
    results.append((bool(nor and nor.end == NOR_END),
                    f"NOR flash = 128 MB (ends 0x{NOR_END:08x})",
                    f"end=0x{nor.end:08x}" if nor else "NOT MAPPED"))
    ram = next((r for r in at(RAM_BASE) if "ram" in r.name.lower()), None)
    results.append((ram is not None, "RAM mapped at 0x0",
                    f"{ram.name!r} 0x{ram.start:08x}-0x{ram.end:08x}" if ram else "NOT MAPPED"))

    # -- MMIO behavior: NOR reads 0xFF, RAM reads 0x00 ---------------------
    nb = reads.get(NOR_BASE)
    results.append((bool(nb) and all(b == 0xFF for b in nb),
                    f"NOR @ 0x{NOR_BASE:08x} reads 0xFF",
                    " ".join(f"{b:02x}" for b in nb) if nb else "no read"))
    rb = reads.get(RAM_BASE)
    results.append((bool(rb) and all(b == 0x00 for b in rb),
                    f"RAM @ 0x{RAM_BASE:08x} reads 0x00 (zero-init)",
                    " ".join(f"{b:02x}" for b in rb) if rb else "no read"))

    # -- report ------------------------------------------------------------
    GREEN, RED, RST = "\033[32m", "\033[31m", "\033[0m"
    tty = sys.stdout.isatty()
    passed = 0
    for ok, label, detail in results:
        passed += ok
        if not ok or args.verbose:
            tag = f"[{'PASS' if ok else 'FAIL'}]"
            line = f"  {tag:8s} {label}\n           {detail}"
            print((GREEN if ok else RED) + line + RST if tty else line)

    total = len(results)
    print("\n" + "=" * 60)
    summ = f"Result: {passed}/{total} emulator facts verified"
    print(f"  {(GREEN if passed == total else RED) + summ + RST if tty else summ}")
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
