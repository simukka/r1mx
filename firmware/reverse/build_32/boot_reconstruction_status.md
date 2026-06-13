# QEMU Boot Reconstruction — Status & Next Plan

**Status: PAUSED 2026-06-11.** Read this before resuming the "cold-boot `software.bin`
in QEMU past the root-task dispatch" effort. Companion detail lives in `re_reference.md`
§0.3 (chronological log); this file is the clean current-state + plan.

---

## TL;DR

`software.bin` is the **firmware program image RED ships** — extracted (decrypted) from the
official `redone.su` Build 32 upgrade installer (`redone.su` tar → AES-256-CBC `redone.1` →
gzip → `software.bin`). It is the image flashed to NOR and loaded into RAM at cold boot; it is
**NOT a memory snapshot of a booted camera** (see [[firmware-image-and-framing]]). Booting it in
QEMU stalls because the **cold-boot init sequence has not run to completion**, so the runtime
state it would build is absent: BSS (`0xE9BF20`–`0x1153480`) lies **above the `0xE8BF20` file end
→ zero in QEMU** and the heap is unallocated (both normal for a program image, runtime-populated
by a cold boot), several `.data` slots hold cold-boot-dependent values the init would overwrite,
and the **device layer isn't modelled**. Every path we tried (natural dispatch, forced-`usrRoot`
+ seeding, build-the-allocator, run-the-init) advances a bit, then hits the *next* prerequisite
that the not-yet-run init would have built. The work is real and the mechanism is now precisely
understood; a fully functional cold boot needs the early init + device layer to actually run
(model the device layer / flash→RAM boot path), not more per-slot seeding.

The boot already reaches a **stable, non-crashing dispatched+running** state (smoke_test
7/7). This effort was about going *past* that to the authentic `usrRoot` path.

---

## Map of the authentic boot path (verified)

Normal boot dispatches the root task into an **OpenSSL X.509 artifact** at `0x381A8C`
(forced by patches #53a/c; not the real boot — see §0.3). To exercise the *real* path we
force `PC = usrRoot (0x37C440)` after booting to `0x381A8C`, keeping the live task stack.
`usrRoot` then runs and diverges in sequence:

| # | Where | What it needs | Cold-boot truth | Seed that advanced it |
|---|-------|---------------|-----------------|------------------------|
| 1 | `FUN_0037D87C` spins @`0x37D8B0` | a deferred-write list @ head `0xE9C5C0` (nodes `{addr+0xc, val+0x10, flags+0x1c}`; walk *writes val→addr*) | empty self-referential circular list | `*0xE9C5C0=*0xE9C5C4=0xE9C5C0` ✓ |
| 2 | `0x700` from `FUN_00555488` | alloc fn-ptr `*0xE9C34C` (NULL → `bctrl 0`) | set to `0x5652D0` by `FUN_005555EC` | `*0xE9C34C=0x5652D0`, `*0xE9C648=0x565518` (gets *past* zalloc) |
| 3 | `0x700` inside the allocator `0x5652D0` | a valid **context** in `r27`/`r28` | established by the real caller chain | **OPEN — this is the keystone** |

Seeds #1/#2 live in `firmware/scripts/seed_boot.py` (the iterative harness).

---

## The keystone open question (= the plan for "#1")

**The allocator fn-ptr `*0xE9C34C` = `0x5652D0`. Calling it in isolation returns `-7`.**
Verified facts (and only these — see Retractions):

- `0x5652D0` is **mid-function** (no prologue) inside `FUN_005651E8` (real entry `0x5651E8`).
  It reads `r28`/`r27` as a pre-set context (`lbz r12,9(r28)`; `lwzx r3,r27,0x14bf4`) and
  returns `-7` when `r28->[9]` isn't 1/3.
- The wrappers `FUN_005552A4` and `FUN_00555488` both just `lwz`+`bctrl` `*0xE9C34C`; they do
  **not** set `r27`/`r28`.
- `r27`/`r28` are **ordinary callee-saved registers** (0 at root-task dispatch, then take
  stack values) — NOT reserved globals. So `0x5652D0` is reachable legitimately only via a
  caller chain that establishes `r27`/`r28` first.

**PLAN (resume here), low-risk static-first:**

1. **Read `FUN_005651E8`'s prologue (`0x5651E8`)** — how does it derive `r27`/`r28` from its
   params (`param_1`, `param_2`)? That defines the "context" the allocator needs. (Pull it
   clean if needed: `ghidra_decompile_addrs.py 0x5651e8` — it's already in the corpus as the
   18 KB merged function; disassemble `0x5651E8..0x5652D0` directly to see the reg setup.)
2. **Find who calls `0x5652D0` legitimately** with a valid context. Static: `callgraph.py`
   has no `bl` to it (it's pointer-called via `0xE9C34C`); so trace the callers of
   `FUN_00555488`/`FUN_005552A4` and see what sets `r27`/`r28` before them. Empirical option:
   breakpoint `0x5652D0` and run a path that legitimately allocates, capture `r27`/`r28`.
3. Once the context object is known, decide: seed it (if it's a small static structure) or
   accept that it chains into the device layer (then this confirms Path C).
4. Re-run `seed_boot.py` with the new seed; observe the next divergence.

---

## Retractions — do NOT repeat these (all empirically refuted this session)

- ❌ "the allocator is a memory partition / free-list" — it isn't.
- ❌ "it builds a 16 M-entry / 1.4 TB device table" — that read the `.data` value
  `*(0xE26978)=0x01000000` (which sits in a `0x10101010` fill region) literally. It is a
  fill/padding value the cold-boot enumeration would overwrite with a real device count, not a table size.
- ❌ "`r27`/`r28` are reserved global registers" — refuted: they're callee-saved locals.
- The "device/channel-context manager" reading (`FUN_005651E8` indexes `iRam00E3A624[idx]`,
  84 KB contexts via `FUN_00560544`/descriptor table `0x10CF458`) is **plausible but not
  load-bearing** for the keystone; treat as a hint, re-verify before relying on it.

---

## Key addresses (so future sessions don't re-derive)

| Addr | Meaning |
|------|---------|
| `0x37C440` | `usrRoot` (rootRtn; `b 0x37C290`; NOT a Ghidra function) |
| `0x381A8C` | artifact dispatch entry (force `usrRoot` here, keep stack) |
| `0xE9C5C0` | deferred-write list head (#1); seed self-referential |
| `FUN_0037D87C` | the list walker that spins |
| `0xE9C34C` / `0xE9C648` | alloc / free fn-ptrs → `0x5652D0` / `0x565518` |
| `0x5652D0` | alloc entry (mid-`FUN_005651E8`@`0x5651E8`); needs `r27`/`r28`; returns `-7` cold |
| `FUN_00555488`, `FUN_005552A4` | call `*0xE9C34C` |
| `FUN_005555EC` | sets the fn-ptrs (guard `*0xE3A600`, was 0) |
| `FUN_00552BF4` | once-guarded module init (guard `*0xE3A5E4`=`0xDAAEAC` non-cold) |
| `FUN_00563B58` | builds device table: base `0xE3A624`, count `0xE3A630`; per-entry `FUN_00560544` (84 KB `0x14C48`, descriptors `0x10CF458`) |
| `0xE26978` | table-entry count source (`0x01000000` = fill-region garbage; cold boot sets the real count) |
| `~0x35A964` | init dispatcher region: `bl FUN_00552BF4`@`0x35A9FC`, `bl FUN_00563B58`@`0x35AA28` (NOT a Ghidra function) |

---

## Tooling delivered this session (durable, reusable)

- **`firmware/scripts/callgraph.py`** — complete PPC call graph from the binary (Ghidra's
  corpus is incomplete). `--callers/--func/--climb/--dump-entries/--stats`. Caveat: false
  `bl` edges in data; verify hops by disassembly.
- **`firmware/scripts/ghidra_decompile_addrs.py`** — pull any function Ghidra has but the
  corpus lacks, on demand (Ghidra's DB has ~12.3 k fns; corpus had 10.5 k). **No
  `analyzeHeadless` needed** — use pyghidra in `.venv`:
  `GHIDRA_INSTALL_DIR=~/Downloads/ghidra_12.0.4_PUBLIC .venv/bin/python firmware/scripts/ghidra_decompile_addrs.py 0x<addr> …`
- **`firmware/scripts/seed_boot.py`** — the iterative force-`usrRoot` + seed harness.
- **`firmware/scripts/probe_usrroot.py`** — force `usrRoot`, trace to first divergence.
- **`rsp.py`** — `write_reg` now uses a `G` read-modify-write (PC writes work; the old
  `P{word-index}` silently hit the wrong reg — pc is gdb regnum 64, word-index 32).
- **`qemu_boot.sh --background` / `--stop`** — daemonized headless QEMU for scripted runs
  (detached chardevs + own pidfile). NB: never `pkill -f qemu` (matches the launcher's own
  cmdline → kills the caller); use `pkill -x qemu-system-ppc`.

## Reproduce the current frontier

```bash
./firmware/scripts/qemu_boot.sh --patched --debug --background   # stub :1234, daemonized
cd firmware/scripts && python3 seed_boot.py                       # forces usrRoot, applies seeds, traces
cd .. && ./firmware/scripts/qemu_boot.sh --stop
```
