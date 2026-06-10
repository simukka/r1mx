# cam-working-01 — Phase 2 task enumeration (status, CORRECTED)

**Date:** 2026-06-08  **D_text:** 0x10180  **Tool:** firmware/scripts/task_walker.py

## What is RELIABLE
- **Enumeration**: multi-round union (halt/walk/resume ×N, merge) defeats the
  TLB-residency limit (XMD `mrd` only reads TLB-resident pages) + transient tasks.
  Converges to a **stable ~13–14 task set** by round 2.
- **TCB fields (grounded)**: sig `*(tcb+0x08)==0x810600`; priority `+0x48`;
  stack base/lim/end `+0x60/+0x64/+0x68`; **ENTRY point `+0xc0`** (static).
  `+0x50/+0x54` = a scheduling DL-node that reorders (NOT the active list).
- **PC→function** via manifest.csv + prologue back-scan for gaps.
- Reliable per-camera relocation: uniform `D_text=0x10180` for text+data; BSS beyond file.

## CRITICAL CORRECTION
`+0xc0` is the **static entry point**, NOT the live PC. VERIFIED: the current
task's `+0xc0`=0x598408 while the live CPU pc=0x5bb0e0 (scheduler) — different.
- Tasks sharing a `+0xc0` value are **instances of the same task type** (shared entry).
- `+0xc8` = static stackEnd, NOT live SP.
- An earlier draft claimed "5 tasks semTake-blocked at FUN_00179344+0x9f8". That
  was a **manifest-gap misresolution**: the real entry `sub_179620` is C++
  `std::string`-init code (`FUN_005ea3bc` = std::string::assign, xrefs 1169), and
  `+0xc0` is the entry, not a pend PC. Those 5 tasks (pri 30/32/34/34/50) are a
  **worker pool sharing one C++ entry**, not semaphore-blocked tasks.

## Task table — by ENTRY point (task type), reliable
| TCB(s) | pri | entry → fn | name |
|---|---|---|---|
| 0x02281358 | 100 | FUN_0054f2dc | tTffsPTask (TrueFFS) |
| 0x055b98f8 | 50 | FUN_006035e0 | tUiIpServer |
| 0x057e4ad0, 0x057de570 | 45 | FUN_005880e8 | pair (same type) |
| 0x085d9dc0/085d4b10/085ca5c0/085d0870/08455090 | 30/32/34/34/50 | sub_179620 (C++) | worker pool (5) |
| 0x0240fe18 | 2 | FUN_001d9aa0 | |
| 0x05520c30 | 50 | FUN_005f1804 | |
| 0x0855d670 | 50 | FUN_005f4d94 | |
| 0x085a5d70 | 50 | FUN_0061dbb0 | |
| 0x023caee8 | 50 | FUN_0043a7ec | |
| 0x059579b8 | 50 | FUN_00353604 | |
| 0x086f0170 | 50 | FUN_00603904 | |

## What is NOT obtainable from TCB field reads
Live PC / live SP / pend-object / which-device-a-task-waits-on. The live REG_SET is
saved by context-switch ASSEMBLY (windExit) at an offset not located; stack-unwind
could not be anchored (stacks are only partially TLB-resident anyway). Names are
registry-based (not a TCB field) → best-effort scan only.

## Recommendation
For `task→device→IRQ` (the QEMU goal), do NOT push further on static TCB
interpretation. Use **Phase 3**: breakpoint the actual driver code (known MMIO
bases + xsrc/ sources) and capture MMIO/IRQ behavior live. Optionally enrich this
table by statically identifying each ENTRY function's subsystem/driver.
