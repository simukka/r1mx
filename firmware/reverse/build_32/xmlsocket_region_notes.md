# xmlsocket / UiIp connection region — reconstruction notes

The xmlsocket subsystem (the UiIp module's XML-over-TCP connection handling: the
`Connection` class — dispatch / authenticate / process-GUI-command — and the
`MasterModule` glue) lives mostly in the **0x1f000–0x39000** code region, ~133
functions, plus the larger `Connection_*` / `MasterModule_*` methods at 0x47xxx /
0xf2xxx–0xf9xxx.

Readable (not-yet-byte-exact) reconstructions of the big methods already exist under
`src/xmlsocket/` (per-function analysis) and `src/xmlsocket/refactored/`
(`connection_authenticate.c`, `connection_dispatch.c`, `connection_protocol.h`, …) —
the annotation quality bar. This note covers bringing the region into the **byte-exact
pipeline** (`units/xmlsocket_conn_ops.c`) and what the original codegen does.

## Build profile (what the sweep established)

The region is **`-O2`**, same family as the rest of the RED app
(`-mcpu=405 -O2 -ffreestanding -ffunction-sections -fno-pic`):

- `-O1` is strictly worse and even breaks an otherwise-byte-exact wrapper
  (`FUN_0003975c`), so the region is not `-O1`/`-Os`.
- `-fno-gcse` produces output identical to plain `-O2` here.
- C++-with-exceptions, `-fno-exceptions`, `-O0`, and `-fno-omit-frame-pointer` were
  each ruled out against `FUN_00033d94` / `FUN_0002ed24` (none reproduce the frames).

So the flags are right; the residual mismatches are **source-structure**, not flag,
differences — the territory of per-function matching decompilation.

## Region codegen traits (why straight transliteration doesn't byte-match)

Observed by `funcmatch` diffing the Ghidra transliteration vs the original:

| Trait | Example | Effect |
|---|---|---|
| Phantom leaf frame | `FUN_00033d94` (just stores a constant to a global) | original brackets the body in `stwu r1,-16` / `addi r1,16` with no stack use; `-O2` here emits none |
| Phantom callee-save | `FUN_0002ed24` | saves/restores an **unused** `r31` (32-byte frame) |
| Sibling-call variance | `FUN_0002ed24` | original tail-calls (`b`) the final `return g(arg)`; this compiler emits `bl`+return from the equivalent C |
| No-CSE re-load | `FUN_0002ba90` | original re-loads `*conn` for each use instead of caching it in one register |
| Default-value staging | `FUN_00029ddc` | original stages the default `0` in `r0` then `mr r3,r0`; the C emits `li r3,0` directly |

Each is behaviour-preserving (the *logic* matches 36–67%), so these are register-
allocation / value-placement / instruction-selection artifacts of the exact source
the compiler saw. Constants that are really code/data addresses must also be passed as
linker symbols (e.g. `FUN_00033d94` sets a global to `&FUN_00043a44`; `0x43a44`
materializes with `lis/addi`, the `@ha/@l` symbol form, not `lis/ori`).

## Status (`units/xmlsocket_conn_ops.c`)

| addr | what it does | fidelity |
|---|---|---|
| `0x0003975c` | wrapper: run work item `FUN_004edc2c`, return | **byte_exact** |
| `0x0002ed24` | gated dispatch (readiness check → forward, else -1) | draft (sibcall/r31) |
| `0x0002ba90` | semaphore-guarded refcount decrement | draft (no-CSE reload) |
| `0x0002df3c` | semaphore-guarded 16-bit field swap | draft |
| `0x00029ddc` | sub-object state probe (0/0x23 = OK) | draft (r0-staging) |

`FUN_005accf4` = semTake (timeout 0xffffffff = WAIT_FOREVER); `FUN_005ad104` = semGive.

## Next steps for whoever continues

1. Pin the source idioms that reproduce the region traits above on one or two
   functions (the phantom frame is the highest-leverage: it recurs across the region's
   leaves and small thunks — solve it once and many small functions fall).
2. Then sweep the clean non-leaf helpers (wrapper/forwarder shape, like `FUN_0003975c`)
   — those already byte-match on the pinned flags.
3. The big `Connection_*` methods: reconcile the `refactored/` readable C with the
   byte-exact tier once the region idioms are pinned.
