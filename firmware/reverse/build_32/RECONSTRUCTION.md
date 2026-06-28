# RED ONE MX — Firmware Reconstruction Workflow

How to turn proprietary RED functions from Ghidra pseudocode into **readable,
documented, byte-exact C** using the in-repo tooling. This is the operational
companion to `PROVENANCE.md` (what's RED vs. blob) and `src/README.md` (the
carve-out relink build).

The goal for each RED function: C that a human can read *and* that the original
compiler rebuilds **bit-for-bit identical** to `software.bin`. Where byte-exact is
infeasible (codegen nondeterminism, hand-asm), fall back to a behaviourally
validated `functional` tier. Both ride the same per-unit overlay substrate.

---

## The pieces

| Tool | Runs | Purpose |
|---|---|---|
| `scripts/lift.py` | host | Assemble a **reconstruction packet** for one function (disasm + pseudocode + call graph + data refs) and scaffold a unit. |
| `scripts/funcmatch.py` | **container** | The byte-exact gate: compile a unit with the original `ccppc`, link each function at its absolute address, byte-compare to `software.bin`. |
| `scripts/funcdiff.py` | host + QEMU | The functional gate: run original vs. reconstructed under QEMU, compare return value + side effects. |
| `scripts/recon_status.py` | **container** | Rebuild every unit, report coverage per fidelity tier, write `src/recon_status.json`. |
| `scripts/build_provenance_map.py` | host | (Re)build `src/manifest.{json,csv}`; merges `recon_status.json` into each record's `fidelity` field. |
| `make -C src verify-units` | host | CI gate: every byte-exact unit still matches (wraps `funcmatch`). |
| `make -C src recon-status` | host | Print the coverage dashboard (wraps `recon_status.py`). |

**Container** = the Wind River GCC 3.4.4 i386 build container; drive it with
`toolchain/in-container.sh <cmd>`. It owns the deterministic build (`ccppc`,
binutils). `lift.py` and `build_provenance_map.py` are pure host scripts.

### Fidelity tiers (the per-function badge in the manifest)

| Tier | Meaning | Gate |
|---|---|---|
| `byte_exact` | rebuilds to the original bytes | `funcmatch` diff == 0 — **the default target** |
| `functional` | different bytes, proven equivalent | `funcdiff` / `lockstep_diff` |
| `draft` | compiles + links, not yet byte-identical | match% shown |
| `raw` | still only Ghidra pseudocode | — |

`recon_status.py` emits `byte_exact` / `draft` directly; `functional` is an
intentional badge for units that are validated behaviourally (e.g. a bug fix, or a
function that resists matching). `raw` is everything not yet in `src/units/`.

---

## The loop

```
lift.py <addr>  ─▶  read packet  ─▶  write/iterate units/<x>.c  ─▶  funcmatch
       ▲                                                              │
       └──────────────── not byte-exact yet (read the asm diff) ◀─────┘
                                   │ byte-exact
                                   ▼
                    recon-status  ─▶  build_provenance_map.py  ─▶  manifest fidelity
```

### 1. Pick a target

Tractable RED functions, smallest first:

```bash
python3 - <<'PY'
import json
m=json.load(open('firmware/reverse/build_32/src/manifest.json'))
red=[r for r in m if r['provenance']=='red' and r['confidence']>=2 and r['fidelity']=='raw']
red.sort(key=lambda r:r['size'])
for r in red[:25]:
    print(f"0x{r['addr']:08x} {r['size']:5}B xrefs={r['xrefs']:<3} {r['module']}")
PY
```

Good first targets: small (≤ ~120 B), few callees, a known module. Coherent
**families** (thunks sharing a string, a class's accessors) reconstruct together
into one well-documented unit.

### 2. Get the reconstruction packet

```bash
firmware/scripts/lift.py 0x004caf48              # print the packet
firmware/scripts/lift.py 0x004caf48 --scaffold   # also write src/units/FUN_004caf48.c
firmware/scripts/lift.py 0x004caf48 --scaffold --unit common_utils_thunks.c
```

The packet gives you, for the address:

- **manifest record** — provenance, module, size, current fidelity;
- **call graph** — callers (found by scanning the whole image for `bl` here) and
  callees with their provenance/module;
- **referenced data** — strings + data addresses the function materializes with a
  `lis`+`addi`/`ori` pair, each with the `D_<addr>` name `data_symbols.ld` needs;
- **original disassembly** of the function's bytes from `software.bin`;
- **Ghidra pseudocode** (`src/all_functions/0x..._*.c`).

`--scaffold` writes a starter unit (doc-header + extern decls for every callee +
the pseudocode as a comment). It refuses to overwrite an existing unit; use
`--unit <name>.c` to target/extend a family file (then merge by hand).

### 3. Write the C

Define each function with its **exact** Ghidra handle `FUN_<addr>` (or its real
name if the manifest has one) — that name is how `funcmatch`/`relink` recognize a
reconstructed unit and place it at its absolute address.

Rules that make bytes match:

- **Data/string addresses go through linker symbols.** A raw integer constant
  compiles to `lis/ori` and will *not* match; the original uses the `@ha/@l`
  (`lis/addi`) relocation pair. Declare `extern char D_<addr>[];`, reference it,
  and add `PROVIDE(D_<addr> = 0x<addr>);` to `units/data_symbols.ld`
  (`D_` = rodata/string, `B_` = BSS). `lift.py` tells you which symbols to add.
- **Match the calling convention by argument position.** Args are r3,r4,r5,…;
  read the disasm to see which register each value lands in and write the call with
  matching argument order (e.g. a `mr r4,r3` before the call means the incoming
  first arg becomes the *second* argument of the callee).
- **Pinned app flags** (`toolchain/toolchain.mk`, `funcmatch.DEFAULT_CFLAGS`):
  `-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic`. Don't change these
  for RED app code; if a function won't match, try `funcmatch --sweep` first.
- **Inline asm where the C idiom can't express it** — e.g. ordered-MMIO indexed
  loads (`lwzx`/`stwbrx`) that plain `*p` won't emit (see `units/mmio_leaves.c`).

### 4. Gate on byte-exactness

```bash
toolchain/in-container.sh python3 firmware/scripts/funcmatch.py \
    firmware/reverse/build_32/src/units/<x>.c
```

- All green → done. On a mismatch, `funcmatch` prints a side-by-side `ORIGINAL` vs
  `RECONSTRUCTED` disassembly and the first diverging offset — fix the C and rerun.
- `--only FUN_xxxx` restricts to one function; `--sweep` tries a flag grid and
  reports which flag set maximizes matches (use it to *discover* flags, not to ship
  a one-off — RED app code stays on the pinned flags).
- Exit code = number of functions that did **not** match, so it doubles as CI.

If a function genuinely won't match, validate it behaviourally instead
(`funcdiff.py` against QEMU, or `lockstep_diff.py` against QEMU/live HW per
`host_xmd_bridge.md`) and badge it `functional`.

### 5. Document to standard

Every unit carries a header (see `units/common_utils_thunks.c`, and the deeper
`src/xmlsocket/refactored/connection_*.c` as the quality bar): absolute address(es),
module/provenance, fidelity badge, one-line purpose, call graph, data-symbol
references, and the exact `funcmatch` command to reverify. Inline comments state
*why/constraints* (the register a value lands in, why a frame is kept), not
narration of the obvious.

### 6. Record the fidelity badge

```bash
toolchain/in-container.sh python3 firmware/scripts/recon_status.py  # -> recon_status.json
python3 firmware/scripts/build_provenance_map.py                    # merge into manifest
make -C firmware/reverse/build_32/src verify-units                  # CI gate stays green
```

Add new byte-exact units to the `verify-units` recipe in `src/Makefile` so they're
guarded by CI. (Draft/functional units are excluded from that pass/fail gate; track
them via `recon-status`.)

---

## Worked example — the `app_modules/common` "utils.h" thunks

`units/common_utils_thunks.c` reconstructs a family of five forwarding thunks
(`0x004caf48`, `0x004caf70`, `0x004caf98`, `0x004cafc0`, `0x004cafe8`). Each injects
the address of the string `"utils.h"` (`0x00d2db9c`, the `__FILE__` of the header
that defines an inlined assert/log helper) into one argument register and tail-into
its worker, preserving the return address. They differ only in *which* argument slot
carries the file pointer:

```
0x004caf48  FUN_004b7bd8  file in r6 (#4)   ->  w(a, b, c, "utils.h")
0x004caf98  FUN_004b4b80  file in r3 (#1)   ->  w("utils.h")
0x004cafe8  FUN_004c9238  file in r3 (#1)   ->  w("utils.h", a)   (incoming r3 -> r4)
```

`extern const char D_00d2db9c[];` + a `PROVIDE` in `data_symbols.ld` give the
`lis/addi` pair; the natural C (`return worker(a, b, c, D_00d2db9c);`) compiled
byte-exact on the first try under the pinned flags. This is the template for the
rest of the `__FILE__`-thunk families (e.g. the `"on/utils.cpp"` set at
`0x004d82e8`).

---

## Bug-fix workflow (the payoff)

1. Reconstruct the function → `verify-units` proves `byte_exact` (a faithful baseline).
2. Edit the C for the fix → `make relink` shows exactly that unit's bytes `CHANGED`.
3. Validate behaviour: `funcdiff.py` + `smoke_test.py` (QEMU) + live `lockstep_diff`.
4. Produce a flashable image — note the install constraint: modified firmware can't
   be repackaged through the signed updater without a JTAG/XMD reflash or an
   embedded-key swap (see `upgrade_install_analysis.md` and the upgrade-module work).

## The relink overlay build (`make relink` / `make verify-relink`)

`relink.py` builds `build/software.relinked.bin` by overlaying reconstructed units
onto the base image. It reuses `funcmatch`'s linking primitives, so it compiles with
the original `ccppc` and resolves `data_symbols.ld` exactly like the byte-exact gate
(both run in the container — the Makefile targets wrap them for you).

**Overlay policy** (so the rebuilt image stays faithful and bootable):

- `identical` (byte-exact) units → overlaid; the image slice is unchanged.
- `functional` units (declared in `units/functional.txt`) → overlaid; these are the
  *only* intentional differences from the base image.
- `draft` units → compiled and linked (which still proves their symbol/data-symbol
  resolution) but **left as original blob**, so an incomplete reconstruction can't
  corrupt the image.

`make verify-relink` passes when every overlaid unit is `identical` or
`functional` — i.e. the relinked image differs from base *only* at intentionally
badged functions. To land a **bug fix** in the image, badge its function `functional`
in `functional.txt` (with a one-line reason); otherwise it's treated as draft and
left as blob.

## Known gaps

- `recon_status.py` emits only `byte_exact`/`draft` from the compile; promoting a
  unit to `functional` is the manual `functional.txt` badge, which should be backed
  by a funcmatch reordering-only diff or a passing `funcdiff`/`lockstep_diff` run.
