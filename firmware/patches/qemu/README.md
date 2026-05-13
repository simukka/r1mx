# QEMU patches for RED ONE MX firmware emulation

These files modify **QEMU 8.2.2** to emulate the RED ONE MX hardware
(Xilinx Virtex-4, PPC405F6 core, VxWorks 2.10).

## Files

```
src/
  hw/ppc/r1mx_virtex4.c     — new: custom r1mx-virtex4 machine (249 lines)
0001-r1mx-virtex4-machine.patch  — hw/ppc/meson.build: register r1mx_virtex4.c
0002-ppc32-tlb-vaddr-truncation.patch   — upstream bug fix: ppc_cpu_tlb_fill
0003-ppc32-crosspage-addr-truncation.patch — upstream bug fix: mmu_lookup
```

## Quick start

```bash
cd ~/src
./r1mx/firmware/scripts/build_qemu.sh
# produces: ~/src/qemu-r1mx/build/qemu-system-ppc
```

Then boot the firmware:

```bash
cd ~/src/r1mx/firmware
python3 scripts/patch_firmware.py --r1mx
./scripts/qemu_boot.sh --patched
```

## What each patch does

### `src/hw/ppc/r1mx_virtex4.c` (new file)

Custom QEMU machine `r1mx-virtex4` matching the Xilinx Virtex-4 FX board used
in the RED ONE MX camera:

- CPU: `x2vp4` (PPC405F6), PVR overridden to `0x20011000`
- 256 MB SDRAM at `0x00000000`
- XUartLite at `0xe0600000` → host stdio
- XIntc at `0xe0800000`
- XEmacLite at `0xe1020000` → host TAP (for WDB UDP 17185)
- Silent stub regions for histogram IPs and PCI windows
- `hreset_vector = 0x00000000` (firmware loads at 0x0)

### `0001-r1mx-virtex4-machine.patch`

Adds `r1mx_virtex4.c` to `hw/ppc/meson.build` under `CONFIG_PPC405` so it
compiles with `ppc-softmmu`.

### `0002-ppc32-tlb-vaddr-truncation.patch`

**Bug fix in upstream QEMU 8.2.2** (`target/ppc/mmu_helper.c`).

`ppc_cpu_tlb_fill` receives `eaddr` as `vaddr` (uint64_t). For PPC32,
`target_ulong` is uint32_t and `TARGET_PAGE_MASK` is `(int32_t)-4096`.
When `eaddr = 0x100000000` (PPC32 PC wrap-around: `0xFFFFFFFC + 4`):

    eaddr & TARGET_PAGE_MASK
    = 0x100000000 & 0xFFFFFFFFFFFFF000  ← mask sign-extends to 64 bits
    = 0x100000000  ← WRONG (should be 0x00000000)

Fix: `(target_ulong)eaddr & TARGET_PAGE_MASK` truncates to 32 bits first.

Without this, the TLB entry for page 0 gets `xlat_section = 0xFFFF…` and
QEMU crashes with SIGSEGV in `notdirty_write`.

### `0003-ppc32-crosspage-addr-truncation.patch`

**Bug fix in upstream QEMU 8.2.2** (`accel/tcg/cputlb.c`).

`mmu_lookup` computes the second-page address for cross-page accesses:

    l->page[1].addr = (addr + size - 1) & TARGET_PAGE_MASK

For a 4-byte store at VA=`0xFFFFFFFF` on a 32-bit guest:

    (0xFFFFFFFF + 3) & PAGE_MASK = 0x100000002 & … = 0x100000000

This 64-bit "overflow" address is then passed to `mmu_lookup1`, which
computes:

    haddr = 0x100000000 + host_ram_base  ← 256 MB past RAM → SIGSEGV

Fix: after computing `size0` using the overflow value, truncate `page[1].addr`
to `target_ulong` (`0x00000000` for PPC32) before TLB lookup.

## Upstreaming

Both bug fixes (`0002`, `0003`) affect all 32-bit QEMU targets that make
cross-page accesses near the top of their address space. They should be
submitted upstream. The machine file (`r1mx_virtex4.c`) is too niche for
upstream but is a natural addition for any PPC405/Virtex-4 emulation project.
