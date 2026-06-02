# Session — Blocker Investigation

> ⚠️ **SUPERSEDED (2026-06-02).** The "tight reset loop / 18,701 `^^^` / kernelInit never
> reached" finding below was observed on an **older binary** (sha `76ca28…`, 59 patches). The
> current `software.patched.r1mx.bin` (sha `f7be6c2a…`) does **not** reset-loop: free-run emits
> 1 `^^^`, and kernelInit is reached in ~0.1 s (it then returns → `0x124` halt loop). See
> `re_reference.md` §0 and `firmware/scripts/smoke_test.py` for current truth. The
> static-analysis findings below (descriptor at `0x020390d0`, the arg-passing path) remain valid.

## Goal

Find what populates the root-task descriptor at `0x020390d0` so `fn_382e80`
has commands to dispatch and the system progresses beyond the root-task
60ms idle loop.

## Outcome

Investigation surfaced a **new, more immediate blocker**: the firmware no
longer boots past `sysHwInit_seq`. The state described in plan.md as
"Session 21+, WDB task reached autonomously, system runs stably" is **not
reproducible** with the current `software.patched.r1mx.bin`
(sha256 `76ca289177fac4f6de60421477b8b7d6a2adb87b19d7df1ea914d72163c66b88`,
59 patches applied, identical to what `patch_firmware.py --r1mx` produces
right now).

---

## Static-analysis findings (still valid)

`0x020390d0` is **not** stored as an immediate or pointer literal anywhere
in `software.bin` / `software.patched.r1mx.bin`:

- 0 occurrences of `lis r?,0x0203` followed by an `addi`/`ori` low-half
  pattern that resolves to `0x020390d0`
- 0 raw big-endian occurrences of the 4 bytes `02 03 90 d0`
- The single `lis r7,0x0204` at vaddr `0x7b587c` is a false positive in a
  data region (surrounding bytes are random)

`0x020390d0` is **outside BSS** (BSS = `0x00E9BF20`–`0x01153480`). It lives
~32 MB into RAM, in the heap region — meaning the descriptor is a
**dynamically allocated buffer**.

`__L` command tokens are **not stored as string literals**: only 6 `__L`
substrings exist in the binary and all are parts of unrelated identifiers
(`__LedBlinkIntervalID`, `__LETTERdelay`, `__LSG__`, ...). The command
tokens that `fn_382e80` looks for must be **constructed at runtime**.

The descriptor pointer reaches `fn_381a8c` as `r3` via the standard
PPC ABI task-arg path:

- `fn_371cd0` is the TCB context-setup helper. It calls
  `memset(TCB + 0x1c0, 0, 0xa4)` to clear the saved register block, then
  writes `0x381a8c` (Patch #53a) to `TCB[0x24c]` (PC slot) and `TCB[0x244]`
  (LR slot, Patch #53c).
- `fn_371c14` is an argument-copy helper that walks 10 words backwards
  from `TCB[0xC4]` (the stack top) into a buffer at `r1+8`. Those 10 words
  are the `arg1..arg10` taskSpawn argument set; **`arg1` becomes `r3` at
  task dispatch — that's our descriptor pointer.**
- Callers of `fn_371cd0`: `0x5b24bc` and `0x5b3498` — both inside what
  looks like the standard VxWorks task-init machinery. Both call as
  `fn_371cd0(r3=TCB, r4=TCB[0xC4])`.

**Conclusion of static phase:** the descriptor buffer is `malloc`'d by
some init code, populated with `__L` records by that same init code, and
its pointer is passed as `arg1` to the root task's `taskSpawn`. Patches
#55/#56/#57 (RTTI bypass, deferred-ctor NOP, WDB-init NOP) are the most
likely culprits for skipping the populator — but dynamic confirmation is
required and was blocked (see below).

---

## Dynamic-analysis attempt — blocked by boot regression

QEMU build at `~/src/qemu-r1mx/build/qemu-system-ppc` (built 2026-05-17).
Firmware as above. Launched with `./scripts/qemu_boot.sh --patched`.

### Observation

- Non-debug run for 20 s emits **18,701 `^^^123456789` lines** — that's
  ~935 boot-sequencer cycles per second, i.e. a tight reset loop.
- Each `^^^123456789` is one full `sysHwInit_seq` execution (`fn_DCB0`,
  `0xDCB0`–`0xDDB4`).
- `kernelInit` is never reached. Root task is never created. BP at
  `0x381a8c` does not fire in 90 s.

### Halt-and-sample (QEMU running, --debug + interactive `\x03`)

| Sample | PC          | LR   | CTR        | MSR  | SP         | First 4 insns @ PC      |
|--------|-------------|------|------------|------|------------|-------------------------|
| 1      | `0x0000_0004` | 0    | `0x00542974` | 0    | `0x07FFFC00` | `00000001 00000029 00000000 00000000` |
| 2      | `0x0000_0700` | 0    | `0x00542974` | 0    | `0x07FFFC00` | `7c5a02a6 38420004 7c5a03a6 4c000064` (Patch #58 rfi-skip) |
| 3      | `0x0000_0004` | 0    | `0x00542974` | 0    | `0x07FFFC00` | (same as #1) |
| 4      | `0x0000_0014` | 0    | `0x00542974` | 0    | `0x07FFFC00` | `00000000 4e800020 00e3004e 800020a6` |

PC oscillates between low addresses (0x0..0x20) and the Program Check
vector at 0x700. Patch #58's rfi-skip handler is firing but only walks
SRR0 forward 4 bytes at a time through more invalid instructions.

### Memory snapshot (live RAM)

| Address    | Live RAM contents (first 32 B)                            | Static binary contents                                  |
|------------|-----------------------------------------------------------|---------------------------------------------------------|
| `0x0000`   | `c0000000 00000001 00000029 00000000 00000000 00000000 4e800020 00e3004e` | `48000008 00000000 38800000 7c800124 4c00012c 7c9c43a6 7c9d43a6 7c9bfba6` |
| `0x0100`   | `7c801f2c 7c0006ac 4e800020 ...` (valid handler code)     | (matches)                                                |
| `0x0200`   | `2f8a0002 419d0034 ...` (valid)                            | (matches)                                                |
| `0x0500`   | `7c640378 8069c708 ...` (valid)                            | (matches)                                                |
| `0x0700`   | `7c5a02a6 38420004 7c5a03a6 4c000064` (Patch #58 intact)   | (matches)                                                |
| `0x020390d0` | `00000000 00000000 ...` (all zeros)                      | (in heap region, not in file)                            |

**The first 32 bytes at `0x0` are clobbered with non-zero, non-instruction
data at runtime** — specifically `0xc0000000` (looks like a SLER value),
`0x00000001`, `0x00000029`. The exception vectors at `0x100`+ are intact.

`0xc0000000` is the same value that triggered QEMU patch #5 (silence
SLER abort). Its appearance at virtual address 0 suggests something is
storing register state (SLER write target, a counter, etc.) to address 0
— most likely via a **NULL TCB / NULL self-pointer dereference** inside
either VxWorks's task-init code or one of our patched bypass paths.

---

## Status of patches vs reality

- `patch_firmware.py --r1mx` is **idempotent** — re-running produces the
  same SHA `76ca28...`. The on-disk binary already includes patches #55–58.
- `re_reference.md` and `plan.md` both claim "Session 21+: WDB task reached
  autonomously, no GDB BPs needed for basic boot." This is **not what the
  current build does**. Either:
  1. The Session 21+ run used a different QEMU build (patches 0001–0006
     reflect 6 QEMU patches; the QEMU source repo at `~/src/qemu-r1mx` is
     empty git-history, so its current state is opaque).
  2. A condition that previously held (heap layout, MMIO read return, etc.)
     no longer does.

---

## What to try next

In priority order — each item is small and independently informative:

1. **Find what writes to address 0.** Set a write watchpoint at `0x0`
   (`Z2,0,4`) from PC=0x0 halt, resume, and capture the first writer.
   `firmware/scripts/trace_descriptor_writer.py --addr 0x0` already does
   exactly this. The writer's PC is the regression's smoking gun.
2. **Bisect QEMU patches.** Rebuild QEMU with patches 0001–0005 only
   (drop 0006-fpga-catchall-tcp-bridge), retry boot. If the loop
   disappears, patch #6 caused it.
3. **Selectively un-patch firmware patch #58 (the rfi-skip at 0x700)** to
   surface the underlying Program Check exception. With #58 active, the
   handler silently masks every fault by skipping it, so the real cause
   is hidden.
4. **Re-introduce one of the recently NOP'd code paths** (#55, #56, #57)
   to see whether one of them is the bypass that *was* maintaining the
   reset vector and is now the one breaking it.

---

## Repro commands

```bash
# Repro the reset loop (20 s sample)
./firmware/scripts/qemu_boot.sh --patched > /tmp/boot.log 2>&1 &
sleep 20; pkill qemu-system-ppc; grep -c '\^\^\^' /tmp/boot.log
# expected: 2  ; actual: 18701

# Halt+sample
./firmware/scripts/qemu_boot.sh --patched --debug &
python3 firmware/scripts/gdb_halt_inspect.py --samples 4

# Dump live RAM
./firmware/scripts/qemu_boot.sh --patched --debug &
python3 firmware/scripts/gdb_dump_mem.py --ranges 0x0:64 0x700:32 0x020390d0:32

# Watchpoint trace (use to find the writer to addr 0)
./firmware/scripts/qemu_boot.sh --patched --debug &
python3 firmware/scripts/trace_descriptor_writer.py --addr 0x0 --max-hits 5
```

## Scripts added this session

- `firmware/scripts/trace_descriptor_writer.py` — GDB-RSP write-watchpoint
  tracer. Sets `Z2,addr,len`, captures every store with PC + GPRs + the
  faulting instruction bytes.
- `firmware/scripts/probe_root_task_args.py` — SW BP at fn_381a8c
  (root-task entry) and dumps arg registers; optionally chains into a
  watchpoint on the descriptor pointer that r3 turned out to be.
- `firmware/scripts/gdb_halt_inspect.py` — minimal halt/sample/resume
  loop for figuring out *where* a runaway firmware is spinning.
- `firmware/scripts/gdb_dump_mem.py` — halt + dump arbitrary memory
  ranges + detach. No state mutation.
