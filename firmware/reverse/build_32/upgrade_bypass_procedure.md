# Procedure: Install Modified Firmware via JTAG Signature-Bypass

**Goal (right-to-repair):** prove we can make the *stock* Build-32 firmware accept a
**modified** upgrade package by intervening over JTAG at the signature-verification step,
so we can continue to maintain this camera with our own firmware.

This is the validation gate described in `../../../plans/can-we-use-xmd-peaceful-crown.md`.
It is the go/no-go test before investing in the permanent path (embedding our own RSA key —
see the end of this doc). Background and addresses: `upgrade_install_analysis.md`. JTAG
bridge: `host_xmd_bridge.md`.

The whole procedure is driven by **`firmware/scripts/upgrade_bypass_test.py`**, which
gates on a live bridge and walks you through each step with confirm-then-verify
checkpoints. This document is the operator narrative around that script.

---

## 0. How it works (one paragraph)

At boot, `GoSplash() → UpgradeMC::SmartUpgrade()` scans the upgrade media (including the
USB type-A mount `/usbd0/upgrade/redone.su`), and if it finds a package it shows an
on-screen upgrade prompt. When you confirm, the firmware: untars → AES-decrypts → gunzips
→ **RSA-verifies the signature** → erases+writes flash. The signature (`redone.2`) covers
the MD5 of the *decompressed* `software.bin`, so changing one byte of the image makes the
original signature invalid and verification fails. We catch the verifier wrapper
`FUN_000af634` at a **hardware breakpoint** over JTAG and force it to report success for
this one install (registers `r3←0`, `PC←LR`). The firmware then flashes our modified
image and reboots — and because our one change is a bumped version string, the new version
on the splash is unambiguous proof it worked.

---

## 1. Safety & prerequisites — read first

- **Target the WORKING camera, idle (not recording).** The verify/flash is a setup-phase
  operation, so the sub-second halt is safe (cf. `recording-halt-disrupts-realtime`). The
  bench unit boot-loops on missing boards and may never reach `SmartUpgrade` — it is only
  good for the Stage-A packaging dry run, not the live flash.
- **This erases and writes NOR flash.** A bad image can brick the camera. Mitigations:
  - the modification is exactly one version byte;
  - keep the **original** `redone.su` and a JTAG/NOR-programmer recovery path ready;
  - run **Stage A** (unmodified round-trip) before **Stage B** (the bypass).
- **You will lift the bridge read-only guard** for this test (the script uses
  `RSP(allow_write=True)` and writes one register set). This is deliberate and authorized;
  it still uses **hardware** breakpoints only (never a software bp, which would itself
  patch memory).

**You need:**
- The host, the WinXP VM `r1mx_32` with XMD, and the USB-JTAG pod attached to the camera.
- A FAT32 USB stick.
- The stock package at
  `firmware/reverse/build_32/build_32_v32.0.3/upgrade/redone.su`.
- `openssl`, `gzip`, `tar`, `python3` on the host.
- The camera's **`.text` relocation** offset for `--reloc` (see step 4). For
  cam-working-01 this is `0x10180` (`working-camera-reloc`); the bench unit is `0x10040`.

---

## 2. Build the packages

Both packages are built with **`firmware/scripts/repackage_firmware.sh`**, which does the
gzip + AES-256-CBC re-encrypt + tar (with the exact member names `redone.1`..`redone.4`
the firmware looks for) and keeps the original `redone.2`/`redone.3`/`redone.4`. Its
`--verify` flag decrypts the output back and checks the SHA round-trip.

First, stage the original components and the decrypted payload once (paths are relative to
`firmware/`):

```bash
cd firmware
PASS='M1H5gwOXh757rIRVY6Gj2tN080AYSX03'   # AES key (public; transport obfuscation only)

# extract the original redone.1..4 into the dir the script reads (--build-dir)
mkdir -p reverse/build_32/extracted
tar xf reverse/build_32/build_32_v32.0.3/upgrade/redone.su -C reverse/build_32/extracted

# decrypt the software payload so we can edit it (reused by both stages)
openssl enc -d -aes-256-cbc -md md5 -pass "pass:$PASS" \
    -in reverse/build_32/extracted/redone.1 | gunzip \
    > reverse/build_32/extracted/software.bin
```

### 2a. Stage-A package (UNMODIFIED — for the dry run)

Repackage the **unmodified** payload. This exercises the same packaging path we'll use for
Stage B (re-encryption uses a fresh salt, but the plaintext — and therefore the signature —
is unchanged), and `--verify` confirms the round-trip:

```bash
cd firmware
scripts/repackage_firmware.sh \
    --input     reverse/build_32/extracted/software.bin \
    --build-dir reverse/build_32/extracted \
    --output    /tmp/redone.A.su \
    --verify
```

### 2b. Stage-B package (MODIFIED — bump the version)

Edit the version **byte-length-preserving**, then repackage. The script keeps the original
`redone.2` (now mismatched against the modified payload — that's exactly what Stage B is
designed to defeat):

```bash
cd firmware
# find the version string and bump it in place (same byte length)
grep -abo '32\.0\.3' reverse/build_32/extracted/software.bin    # note the OFFSET(s)
cp reverse/build_32/extracted/software.bin reverse/build_32/extracted/software.patched.bin
printf '32.0.4' | dd of=reverse/build_32/extracted/software.patched.bin \
    bs=1 seek=<OFFSET> conv=notrunc
# (repeat for each occurrence you intend to change; the splash one is what you'll read)

scripts/repackage_firmware.sh \
    --input     reverse/build_32/extracted/software.patched.bin \
    --build-dir reverse/build_32/extracted \
    --output    /tmp/redone.B.su \
    --verify
```

> The version string lives inside `software.bin` (it may appear more than once; the one
> shown on the splash comes from `SYSTEM.VERSION.RED_RELEASE`). Keep the replacement the
> **same byte length** so nothing else shifts. Do **not** touch `redone.3`/`redone.4`.
> `--verify` here only confirms the AES round-trip (our encryption), not the RSA signature
> — the camera is what will reject the bad signature unless we intervene in Stage B.

Put the package for the stage you're running on the stick under a root-level `upgrade/`
folder (`/tmp/redone.A.su` for Stage A, `/tmp/redone.B.su` for Stage B):

```bash
# FAT32 stick mounted at /media/usb
mkdir -p /media/usb/upgrade && cp /tmp/redone.B.su /media/usb/upgrade/redone.su
sync
```

---

## 3. Stage A — packaging + trigger dry run (no JTAG)

Proves the media, the boot-time auto-detect, and the UI-confirm path before any
hardware intervention. Use the **Stage-A (unmodified)** package on the stick.

```bash
python3 firmware/scripts/upgrade_bypass_test.py --stage a --expect-version 32.0.3
```

The script will tell you to: insert the stick → **power-cycle** the camera → confirm the
upgrade at the splash prompt → let it flash and reboot → type the version you see. It
PASSes when the camera reboots to `32.0.3` (unchanged, signature still valid). If this
fails, fix media/format/trigger before going further.

---

## 4. Bring up the JTAG bridge

In the **WinXP VM** (`r1mx_32`):

```
xmd
xmd% connect ppc hw        ;# prints: GDB server ... at TCP port no 1234
```

On the **host** (one-time per session — forwards the VM stub to `:2345`):

```bash
VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"
# verify the camera is reachable and find context
python3 firmware/scripts/gdb_halt_inspect.py --port 2345 --samples 1
```

**Determine `--reloc`:** the verifier's runtime address is `0xAF634 + reloc`. Derive the
per-unit `.text` relocation from the data path (`working-camera-reloc`); for cam-working-01
it is `0x10180`. You can sanity-check by halting in the upgrade path and disassembling
around `0xAF634 + reloc` to confirm the wrapper prologue.

---

## 5. Stage B — the signature-bypass test

Put the **Stage-B (modified)** package on the stick (step 2b), then:

```bash
python3 firmware/scripts/upgrade_bypass_test.py \
    --stage b \
    --wrapper-addr 0xAF634 \
    --reloc 0x10180 \
    --expect-version 32.0.4
```

What the script does, and what you do:

1. **Preflight (automatic, blocking).** Confirms the VM is running, `:2345` is reachable,
   and the XMD stub returns a live register set (halts, reads PC/LR, reads the DRAM canary,
   resumes). It then runs a **hardware-breakpoint self-test**: it arms a bp at the current
   (idle-loop) PC and confirms it re-traps, so a later "no waypoint hit" can be read as
   "the path wasn't taken" rather than "Z1 never armed". (`--no-bp-selftest` skips it.) It
   exits with the exact fix if any check fails.
2. **Prompt:** *insert the modified-package USB, then on the camera press SYSTEM → SETUP →
   MAINTENANCE and highlight `UPDATE SW` — do NOT select it yet.* Press Enter. The script
   halts the core and arms **four pipeline breakpoints** (the PPC405 exposes exactly four
   IAC slots), then resumes:

   | waypoint | fn | `img + reloc` | meaning if it traps |
   |---|---|---|---|
   | `extract` | `FUN_000a8bdc` | `0x0A8BDC + reloc` | reached extract/decrypt/verify |
   | `verify`  | `FUN_00210800` | `0x210800 + reloc` | reached per-file signature verify |
   | `wrapper` | `FUN_000af634` | `0x0AF634 + reloc` | reached the verify wrapper (**override point**) |
   | `flash`   | `FUN_000adc28` | `0x0ADC28 + reloc` | verification passed → erasing+programming |

   (Each is tunable via `--extract-addr` / `--verify-addr` / `--wrapper-addr` / `--flash-addr`.)
3. **Prompt:** *now select `UPDATE SW` in the camera UI.* Press Enter. The script **traces**
   the upgrade: each time a waypoint traps it prints `name / PC / r3 / LR` plus the verify
   error flag (`*0xE9E85C`), then continues to the next — up to `--bp-timeout` (default
   600 s) per step.
4. **Override (automatic):** when the `wrapper` waypoint traps, `r3←0` (the wrapper's
   success value) and `PC←LR` (return immediately). The wrapper runs once per signed file
   (`redone.2` software sig, `redone.4` FPGA sig), so it is overridden each time it traps;
   the bp stays armed to catch both. On the `flash` hit the script clears all bps and
   resumes for the erase/write.
5. **Trace summary.** The script prints which waypoints fired and in what order, and
   interprets it: reached flashing / reached verify-but-didn't-flash (override
   missing/ineffective) / extraction-only (packaging problem before the signature) /
   nothing (wrong trigger or `--reloc`, or — if the self-test failed — the bp never armed).
6. **Prompt:** *wait for the reboot; type the version on the splash.* PASS when it reads
   `32.0.4`.

### Method options
- `--method regs` (default, **recommended**): register override — no PPC405 I-cache
  concern because we change CPU context, not code.
- `--method patch`: writes `li r3,0; blr` (`386000004e800020`) into the verifier in RAM.
  Works only if the I-cache hasn't already cached the original instruction — the script
  warns; prefer `regs`.

---

## 6. Negative control (do this once)

Prove that the *bypass* — not luck or a packaging quirk — is what made Stage B pass. Run
Stage B with the **same modified package** but withhold the override:

```bash
python3 firmware/scripts/upgrade_bypass_test.py \
    --stage b --negative-control \
    --wrapper-addr 0xAF634 --reloc 0x10180 --expect-version 32.0.3
```

The waypoints still arm (so you get the same pipeline trace), but the script does **not**
override `r3`/`PC` at `wrapper`. Expected: the trace reaches `verify`/`wrapper` but **not**
`flash`, the firmware reports `Verification Failure` / `Error Verifying Data`, skips the
flash, and the version stays `32.0.3`. The script PASSes the negative control when the
version is **unchanged**.

---

## 7. Optional pre-flight on QEMU

Rehearse the halt so the live override is minimal:

```bash
firmware/scripts/qemu_boot.sh --patched --debug          # gdbstub :1234
# breakpoint 0xAF634 (no reloc under QEMU), practice the r3/PC override
python3 firmware/scripts/upgrade_bypass_test.py --stage b \
    --port 1234 --no-vm-check --wrapper-addr 0xAF634 --reloc 0
```

(QEMU won't run the real flash, but you can confirm the breakpoint address, the register
layout, and the override mechanics against the emulated core.)

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Preflight: VM not running | Start `r1mx_32` in VirtualBox; then `xmd; connect ppc hw`. |
| Preflight: `:2345` unreachable | Re-run the `VBoxManage … natpf1` forward; check `connect ppc hw` is live. If the stub binds `127.0.0.1` only, use Channel B / a relay (`host_xmd_bridge.md` Troubleshooting). |
| Preflight: no PC / wrong reg block | XMD not attached to the core, or `g`-block size unexpected — see `rsp_discover.py`. |
| Breakpoint never hits | Wrong `--reloc` (address off); or the operator confirmed before the bp was armed; or the upgrade didn't start (file not found at `/usbd0/upgrade/redone.su`). |
| Halts at the wrong PC | `--reloc` mismatch — the script warns and prints the actual PC; recompute the relocation. |
| `write_reg … 'P' not supported` | Stub lacks the `P` packet — switch to `--method patch`. |
| Camera reboots mid-test | Watchdog tripped on a long halt — keep the override instant; the script does hit→write→continue with no extra dwell. |
| `--method patch` had no effect | I-cache held the original instruction — use `--method regs`. |

---

## 9. Recovery if the flash goes bad

If the modified image bricks the camera, reflash a known-good `software.bin` directly to
NOR (`0xF0000000`) via an external NOR programmer / iMPACT JTAG (the path that bypasses
SmartUpgrade entirely — `upgrade_install_analysis.md` §#4). Keep the original `redone.su`
and a verified `software.bin` (`SHA-256 416e148c…`) on hand before you start.

---

## 10. After this validates — the permanent path

This test only bypasses verification for a single, JTAG-attended install. To maintain the
camera **without JTAG every time**, do the one-time enrolment (`upgrade_install_analysis.md`
§Implication #4+#5):

1. Build a modified image that replaces the embedded upgrade public key at `0x9D29A8`
   (`/roFs/Red.pem`) — and `0x6726F0` — with **our** RSA-1024 public key (via the relink
   build, `relink-build-model`), keeping the PEM byte-length ≤ original.
2. Install that image once (by this JTAG bypass, or an external reflash).
3. Thereafter, sign our own `redone.su` upgrades with **our** private key — normal OTA
   over USB/SD works, no JTAG. We own the signing chain.
