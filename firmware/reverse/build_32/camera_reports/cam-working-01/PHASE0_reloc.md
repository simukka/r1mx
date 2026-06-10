# cam-working-01 — Phase 0 relocation (manual derivation)

**Date:** 2026-06-08
**Build:** Build 32 (matches `software.bin`), confirmed by code-structure match (below).
**`D_text = 0x10180`**  → `image_fileoff = live_VA − 0x10180`
**`D_data ≈ 0`** for absolutely-addressed globals/BSS (live data sits at the
image-encoded absolute address; the readable kernel structures are BSS).

> Note: this differs from the bench unit's `D_text=+0x10040` — relocation is
> per-camera, exactly as the plan warned. Re-derive for every unit.

## Why camera_probe's auto-reloc returned D_text=None
`camera_probe` fingerprints by reading live `.text` as data via XMD `mrd`. On a
**healthy, idle camera** that fails: `.text` (`0x10_0000`–`0x5b_xxxx`) is
**I-side-only mapped** at the idle context — no DTLB entry — so `mrd` of any code
VA returns `0x00000000`. Verified: `mrd 0x5bb0dc` (the live PC region) and
`mrd 0x473700`, `0x400000`, `0x100000` all read zero, while **data** reads fine
(stack `0x57exxxx`, kernel ctx `0xe9xxxx`). `XMD dis` did not round-trip through
the agent either. So the live-`.text` fingerprint method is unusable at idle.

## How D_text was derived instead (data-readable path)
At halt: `pc=0x5bb0dc`, `r21=0x00e9c6a0`, `r24=0x010d0584` (readyQ), kernel ctx
`r27=0x00e9c3e0`.

1. Live `pc 0x5bb0dc − 0x10180 = img 0x5aaf5c`, which disassembles to a function
   **prologue** (`FUN_005aaf5c`, the kernel idle/root loop per the plan):
   `stwu r1,-0x40(r1); mflr r0; stmw r21,0x14(r1); lis r21,0xea; addi r21,r21,-0x3960; lwz r9,0(r21)`
2. `lis 0xea; addi -0x3960` builds **`0xe9c6a0`** — equal to the **live `r21`**.
   The CPU must have executed that prologue ⇒ it *is* in this function ⇒ `D_text`
   confirmed independently of the PC-position guess.
3. Cross-check: a code pointer in the kernel ctx, `0x004737b0 − 0x10180 =
   img 0x463630`, disassembles to a clean function tail (`cmpwi/bne/li r3,-1/blr`).

The idle spin itself is at img `0x5ab0dc` (live `0x5bb25c`):
`lwz r12,0(r24); cmpwi r12,0; beq` — i.e. wait while `readyQHead (0x010d0584)==0`.

## Memory-read ground rules for this camera (idle context)
- **Data is readable** (`mrd`): VxWorks kernel structs ~`0xe9xxxx`, task stacks
  ~`0x57exxxx`, peripheral regs (`XUartLite 0xe0600000` real; `XIntc 0xe0800000`
  read back as bus-residue `0x0532d3dc` — needs a mapped context).
- **`.text` is NOT data-readable here.** To translate/inspect code, use
  `img = live − 0x10180` against `software.bin` (capstone) — do not `mrd` code VAs.
- To follow Phase 2/3, read code POINTERS out of data structures, translate by
  `−0x10180`, and disassemble from the file.

## Phase-0 gate: PASSED (D_text=0x10180, build=32). Proceed to Phase 1/2.
