# cam-working-01 — allocator / memory-partition structure (Option B spec)

Harvested 2026-06-14 from the live booted camera (D_text=0x10180), read in the
allocator context (HW bp at `FUN_0045b974` live `0x46BAF4` so the heap is D-TLB-mapped;
at idle the `0xFCxxxx` heap reads zero). Raw dump: `heap_structures_<ts>.json`.

This is the ground truth for **Option B** — hand-construct an allocator + pool in reserved
QEMU RAM and point `*0xE295C4` at it, so usrRoot's allocations work and the boot proceeds
past the heap-construction keystone (the wall now reached via the natural dispatch).

## The allocator object (a RED custom tree-based memory partition)

`*0xE295C4 = 0x00FC2530` (heap object, ~`0x110` bytes; `+0x11C = 0x110` = its size).
It is consumed by `FUN_0045B974` → `FUN_0045B6B8` (default path, since `+0xCC = 0`) →
`FUN_0045A428` (alloc from the `+0x40` free tree). Key fields (live values):

| offset | live value | role |
|---|---|---|
| `+0x04` | `0x00FC2530` | self-pointer |
| `+0x24/+0x28` | `0x00FC9580` | related object (== the dispatch selector `*0xE3A790`!) |
| `+0x40/+0x44` | `0x08A5D8B0` / `0` | **free-tree root** (`FUN_0045A428` searches via `FUN_00495F18`) |
| `+0x48` | `0x085A8F78` | node-pool area (tree nodes) |
| `+0x4C` | `0x00000119` | node count (281) |
| `+0x50` | `0` | lock/semaphore (free) — `FUN_005AE644(part+0x50)` takes it |
| `+0x80` | `0x0108BFC0` | a pool boundary |
| `+0x90` | `0x010D0000` | a pool boundary |
| `+0xC0` | `0x00000BB0` | flags (`FUN_0045B6B8` tests `& 0x10`, `0x1800`, `0x100`) |
| `+0xC4` | `0x020390D0` | the OpenSSL/CONF buffer (§0.3) — a trace/scratch ptr |
| `+0xE8` | `0x0001BCCD` | alloc count stat |
| `+0xEC/+0x100` | `0x03EF2F6C` / `0x03F6D70C` | cumulative / high-water size stats |
| `+0x108` | `0x00000F78` | base value (`FUN_0045B6B8` adds to `+0xEC`) |
| `+0x11C` | `0x00000110` | object size |

## Free-tree node format (root `@0x08A5D8B0`)

`[0]=0x08AF31D8 (left)  [1]=0x08B31990 (right)  [2]=0x5 (color/flag)  [3]=0x478 (block size=1144)  [4]/[5]=0x09E3B480 (block ptr)  ...`
— a balanced (red-black/AVL) tree of free blocks keyed by size; the `0x495xxx`/`0x496xxx`
module holds the tree ops (`FUN_00495F18` search, `FUN_004963CC` insert, `FUN_00495ED4`
remove). `FUN_0045A384` inserts a free block, `FUN_0045A2C0` removes one.

## Pool / sysMemTop

- `sysMemTop *0xE0C37C = 0x10000000` (256 MB) — **matches QEMU** (`-m 2G`, computed at boot).
- `*0xE0C380 = 0x0FF9C000` (usable top / a pool boundary).
- Live free blocks sit in `~0x08xxxxxx`–`0x0Axxxxxx` (heap pool, ~135–165 MB).
- Confirmed: alloc/free fn-ptrs `*0xE9C34C=0x5652D0`, `*0xE9C648=0x565518`; align `0x8`.

## Option-B construction sketch (for QEMU)

1. Reserve a pool region in QEMU RAM (the heap band, e.g. `0x08000000`–`0x0FF9C000`).
2. Build the partition object at a fixed reserved address: zero it, set `+0xC0=0xBB0`,
   `+0xCC=0`, `+0x11C=0x110`, init `+0x50` lock, init the `+0x40` free tree EMPTY.
3. Insert ONE free block spanning the pool into the tree (via the firmware's
   `FUN_0045A384`/`FUN_004963CC` with a correctly-formed boundary-tagged block, OR replicate
   the node format above). Set `+0x4C` node count accordingly.
4. Set `*0xE295C4` = the object address; set `*0xE9C34C/*0xE9C648` (already harvested).
5. Validate by calling `FUN_0045B974` in QEMU and checking it returns a pool pointer.

NB: this is intricate (balanced-tree + boundary tags); the safest route is to drive the
firmware's own `addToPool`/insert path rather than hand-format the tree. The live structure
above is the reference to validate against.

## Allocator internals (decompiled 2026-06-14) — refines the construction plan

**Dependency chain (the wall order in the natural boot, dispatch fix applied):**
`usrRoot → FUN_00552bf4 (module init) → zalloc FUN_00555488(0x54) → *0xE9C34C` faults
(NULL → `bctrl 0` → 0x700). `*0xE9C34C` should be `0x5652D0` (= mid-`FUN_005651E8`, a
**device-context** fetch that reads `r27/r28` context + the device table `iRam00e3a624`),
NOT a size allocator. So this first alloc needs the **device table built**, which needs PCI
enum (`FUN_00367f54`, now satisfiable by the ISP1562 model), which needs the **tree
partition** (`FUN_0045B974`/`*0xE295C4`) for descriptors. **The tree partition is the
foundation — build it first.**

**Tree allocator format (verified):**
- `FUN_00495F18(root, size)` = best-fit BST: `node[0]`=left, `node[1]`=right, `node[3]`
  (`+0xC`)=block size (key), `node[0x10]`=pointer to the actual heap chunk. Returns the
  smallest node with size ≥ requested.
- Heap chunk boundary tags: `chunk[0]`=prev/back, `chunk[1]` (`+0x4`)=`size | inuse-bit`,
  `chunk[2]` (`+0x8`)=owner (set to the partition on alloc), user data at `chunk+0x10`
  (returned pointer = `chunk+0x10`; `free` checks `*(ptr-8)==part`).
- Nodes live in a SEPARATE node pool at `part+0x48` (count `part+0x4C`), refilled by
  `FUN_0045A644` (which itself calls `FUN_0045A428` → bootstrap recursion).
- `FUN_0045A428` finds a node, removes it (`FUN_0045A384`→tree `FUN_00495ED4`), splits the
  chunk, re-inserts the remainder (`FUN_0045A2C0`→needs a free node from the node pool).

**Why hand-building is fragile:** the split path re-inserts the remainder, which needs a free
tree node from `part+0x48`; populating that pool calls back into the allocator. Getting the
node-pool bootstrap + boundary tags exactly right is error-prone.

**Recommended construction (next step): drive the firmware's own partition init.**
1. Find RED's `memPartInit`/create (takes pool+size, builds the empty partition struct,
   seeds the node pool, inserts the pool as one free chunk). Candidates to pull/trace:
   the `0x459xxx` module create path; or breakpoint the partition-build on the camera is
   impossible (built once at boot), so locate it statically (it sets `part+0xC0=0xBB0`,
   inits `part+0x40` tree, calls `FUN_0045A384`). `*0xE295C4` has no `lis`+`stw` writer →
   the create likely returns the partId and a C++ ctor stores it; pull via
   `ghidra_decompile_addrs.py` around the `0x4595xx`/`0x4596xx` create + `FUN_00552BF4`/
   `FUN_005555EC` module-init that wires `*0xE9C34C`.
2. Reserve a QEMU pool (e.g. `0x08000000`–`0x0C000000`, unused RAM; sysMemTop=0x10000000).
3. Call create(pool,size) from the gdb-stub harness, set `*0xE295C4`, then test
   `FUN_0045B974(0x54)` returns a `chunk+0x10` pointer in the pool.
4. With malloc working, let usrRoot reach PCI enum (ISP1562) → device table → the device-ctx
   alloc (`0x5652D0`) succeeds; trace the next wall.

**Status:** Option B STARTED — dependency chain scoped, live structure harvested, allocator
internals decompiled, construction plan refined. The build itself (find+call create, or a
careful hand-build) is the next concrete step.
