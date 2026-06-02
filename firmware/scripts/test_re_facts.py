#!/usr/bin/env python3
"""test_re_facts.py -- Layer 1 of the RED ONE MX Build 32 test suite.

Static-fact assertions read STRAIGHT FROM THE BINARY -- no QEMU, no GDB, runs in
milliseconds.  This is the cheapest source of truth: every check here encodes a
specific claim from re_reference.md so that documentation discrepancies are
settled by running this script instead of re-reading prose.

Two kinds of fact are asserted:
  * Binary identity  -- SHA-256 of each image (re_reference.md §0.1).  If these
    fail, every downstream doc/test claim is suspect because the binary drifted.
  * Boot-flow disassembly -- the exact branch/return instructions that define the
    reset -> usrInit -> kernelInit -> halt-loop control flow (re_reference.md §0,
    §8; build32_static_analysis.md).

Layered test suite (see re_reference.md §0.5):
    Layer 1  test_re_facts.py   <-- this file   (static / RE facts, no QEMU)
    Layer 2  smoke_test.py                      (dynamic boot in QEMU)
    Layer 3  (planned) emulator device tests    (r1mx-virtex4 peripherals)

Usage:
    .venv/bin/python firmware/scripts/test_re_facts.py
    .venv/bin/python firmware/scripts/test_re_facts.py -v   # show every check

Exit code 0 if all assertions pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_EXTRACTED = _REPO_ROOT / "firmware/reverse/build_32/extracted"

# Canonical SHA-256 identities (re_reference.md §0.1).
SHA_ORIGINAL = "416e148c9eb4b818bef004ebe6294dcbb1e74026604fdb964178fe9e2b65d9cd"
# 2026-06-02: regenerated after DISABLING the wrong patch #57 (the NOP at
# 0x5a8190 that broke root-task dispatch).  See patch_firmware.py #57 and
# re_reference.md §0.
SHA_PATCHED_R1MX = "281ef88ac558c459fa6ec500ea3be9c1dc253f9baa660a2e81b6d31502597d7c"

PPC_BLR = 0x4E800020   # blr  (branch to link register)


# ---------------------------------------------------------------------------
# PPC instruction decode (only what we assert on)
# ---------------------------------------------------------------------------

def decode_branch(word: int, addr: int) -> tuple[str | None, int | None, bool]:
    """Decode an I-form branch (primary opcode 18).

    Returns (mnemonic, target, absolute) where mnemonic is 'b' or 'bl', or
    (None, None, False) if *word* is not an I-form branch.
    """
    if (word >> 26) != 18:
        return (None, None, False)
    li = word & 0x03FFFFFC
    if li & 0x02000000:               # sign-extend 26-bit displacement
        li -= 0x04000000
    aa = bool((word >> 1) & 1)
    lk = bool(word & 1)
    target = (li if aa else addr + li) & 0xFFFFFFFF
    return ("bl" if lk else "b", target, aa)


# ---------------------------------------------------------------------------
# Assertion model
# ---------------------------------------------------------------------------

@dataclass
class Check:
    """One static assertion against a firmware image."""
    kind: str           # "sha" | "branch" | "word" | "hi16"
    binary: str         # filename under extracted/
    desc: str           # human description of the claim
    ref: str            # where the claim is documented
    addr: int = 0       # instruction address (file offset == vaddr; image loads at 0)
    want: int = 0       # expected word / hi16 / branch target
    link: bool = False  # for "branch": expect 'bl' (True) vs 'b' (False)
    want_sha: str = ""  # for "sha"


# All facts below are verified against the current binaries (2026-06-02).
# Add a row here whenever a claim in the docs should be machine-checkable.
CHECKS: list[Check] = [
    # -- binary identity ----------------------------------------------------
    Check("sha", "software.bin", "original Build 32 v32.0.3 image identity",
          "re_reference.md §0.1 / header", want_sha=SHA_ORIGINAL),
    Check("sha", "software.patched.r1mx.bin", "patched QEMU-boot binary identity",
          "re_reference.md §0.1", want_sha=SHA_PATCHED_R1MX),

    # -- boot-flow control flow (original image; patches don't touch these) --
    Check("branch", "software.bin", "boot stub @0xa4 -> usrInit (0x36c350)",
          "build32_static_analysis.md L73; re_reference.md §0.5",
          addr=0x0000A4, want=0x0036C350, link=True),
    Check("branch", "software.bin", "boot stub @0xa8 -> halt loop (0x124)",
          "build32_static_analysis.md L74", addr=0x0000A8, want=0x000124, link=True),
    Check("branch", "software.bin", "halt loop @0x124 = b 0x124 (branch-to-self)",
          "re_reference.md §0.2; build32_static_analysis.md L107",
          addr=0x000124, want=0x000124, link=False),
    Check("branch", "software.bin", "usrInit @0x36c3d4 -> fn_DCB0 hardware sequencer (0xdcb0)",
          "plan.md 'usrInit layout'", addr=0x36C3D4, want=0x00DCB0, link=True),
    Check("branch", "software.bin", "usrInit @0x36c424 -> kernelInit (0x5a7f30)",
          "re_reference.md §0.2, §10", addr=0x36C424, want=0x5A7F30, link=True),
    Check("word", "software.bin", "usrInit epilogue @0x36c43c = blr",
          "re_reference.md §10 (body ends 0x36c43c)", addr=0x36C43C, want=PPC_BLR),

    # -- kernelInit dispatch call (the fix: patch #57 disabled) --------------
    # In the ORIGINAL image, kernelInit's last call (0x5a8190) is bl 0x5b11ac
    # (taskActivate -> first context switch into the root task).
    Check("branch", "software.bin", "kernelInit @0x5a8190 -> taskActivate (0x5b11ac)",
          "re_reference.md §0; trace_dispatch_path.py", addr=0x5A8190, want=0x5B11AC, link=True),
    # The PATCHED r1mx image MUST preserve that call (the wrong patch #57 used
    # to NOP it, which made kernelInit return -> 0x124 halt).  This asserts the
    # dispatch call survives patching so the root task is actually dispatched.
    Check("branch", "software.patched.r1mx.bin",
          "patched kernelInit @0x5a8190 still = bl taskActivate (patch #57 disabled)",
          "re_reference.md §0; patch_firmware.py #57", addr=0x5A8190, want=0x5B11AC, link=True),

    # -- function-entry prologues (sanity: these addresses are real entries) -
    Check("word", "software.bin", "usrInit entry @0x36c350 = mflr r0 (prologue)",
          "re_reference.md §10", addr=0x36C350, want=0x7C0802A6),
    Check("hi16", "software.bin", "kernelInit entry @0x5a7f30 = stwu r1,-N(r1)",
          "re_reference.md §0.2, §10", addr=0x5A7F30, want=0x9421),
    Check("hi16", "software.bin", "usrRoot entry @0x36c440 = stwu r1,-N(r1)",
          "re_reference.md §10 (usrRoot/sysClk caller)", addr=0x36C440, want=0x9421),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_C = {"PASS": "\033[32m", "FAIL": "\033[31m", "RST": "\033[0m"}


def _col(status: str, text: str) -> str:
    return f"{_C[status]}{text}{_C['RST']}" if sys.stdout.isatty() else text


def _word_at(blob: bytes, addr: int) -> int | None:
    if addr < 0 or addr + 4 > len(blob):
        return None
    return struct.unpack(">I", blob[addr:addr + 4])[0]


def run_check(c: Check, blob: bytes) -> tuple[bool, str]:
    """Return (passed, detail)."""
    if c.kind == "sha":
        got = hashlib.sha256(blob).hexdigest()
        return (got == c.want_sha, f"sha256={got[:12]}… want {c.want_sha[:12]}…")

    word = _word_at(blob, c.addr)
    if word is None:
        return (False, f"addr 0x{c.addr:x} out of range (size 0x{len(blob):x})")

    if c.kind == "branch":
        mnem, target, _ = decode_branch(word, c.addr)
        want_mnem = "bl" if c.link else "b"
        ok = (mnem == want_mnem and target == c.want)
        got = f"{mnem} 0x{target:08x}" if mnem else f"raw 0x{word:08x} (not a branch)"
        return (ok, f"@0x{c.addr:06x} {got}  want {want_mnem} 0x{c.want:08x}")

    if c.kind == "word":
        return (word == c.want, f"@0x{c.addr:06x} word=0x{word:08x} want 0x{c.want:08x}")

    if c.kind == "hi16":
        hi = word >> 16
        return (hi == c.want, f"@0x{c.addr:06x} word=0x{word:08x} hi16=0x{hi:04x} want 0x{c.want:04x}")

    return (False, f"unknown check kind {c.kind!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build 32 static-fact assertions (Layer 1)")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every check, not just failures")
    args = ap.parse_args()

    print("RED ONE MX Build 32 — Static Fact Suite (Layer 1, no QEMU)")
    print(f"  extracted dir: {_EXTRACTED}\n")

    # Load each referenced binary once.
    blobs: dict[str, bytes] = {}
    missing: set[str] = set()
    for name in {c.binary for c in CHECKS}:
        p = _EXTRACTED / name
        if p.is_file():
            blobs[name] = p.read_bytes()
        else:
            missing.add(name)

    passed = failed = 0
    for c in CHECKS:
        if c.binary in missing:
            ok, detail = False, f"binary not found: {c.binary}"
        else:
            ok, detail = run_check(c, blobs[c.binary])
        status = "PASS" if ok else "FAIL"
        passed += ok
        failed += (not ok)
        if not ok or args.verbose:
            tag = f"[{status}]"
            print(f"  {_col(status, tag):16s} {c.desc}")
            print(f"           {detail}")
            print(f"           ref: {c.ref}  [{c.binary}]")

    print()
    print("=" * 60)
    total = passed + failed
    summary = "PASS" if failed == 0 else "FAIL"
    print(f"  {_col(summary, f'Result: {passed}/{total} static facts verified')}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
