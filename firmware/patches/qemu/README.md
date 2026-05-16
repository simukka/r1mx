# QEMU patches for RED ONE MX firmware emulation

These files modify **QEMU 8.2.2** to emulate the RED ONE MX hardware
(Xilinx Virtex-4, PPC405F6 core, VxWorks 2.10).

## Files

```
src/
  hw/ppc/r1mx_virtex4.c     — new: custom r1mx-virtex4 machine (249 lines)
0001-r1mx-virtex4-machine.patch          — hw/ppc/meson.build: register r1mx_virtex4.c
0002-ppc32-tlb-vaddr-truncation.patch    — upstream bug fix: ppc_cpu_tlb_fill
0003-ppc32-crosspage-addr-truncation.patch — upstream bug fix: mmu_lookup
0004-ppc405-fsl-instructions.patch       — PPC405 FSL (Fast Simplex Link) instruction support
0005-silence-sler-abort.patch            — silence SLER abort caused by firmware boot countdown
```

## Quick start

```bash
cd ~/src/RED/r1mx
./firmware/scripts/build_qemu.sh
# produces: ~/src/qemu-r1mx/build/qemu-system-ppc
```

Then boot the firmware:

```bash
cd ~/src/RED/r1mx/firmware
.venv/bin/python scripts/patch_firmware.py --r1mx
./scripts/qemu_boot.sh --patched
```

For the full boot guide (GDB, WDB networking, crash diagnosis) see:
`firmware/reverse/build_32/qemu_howto.md`

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
submitted upstream.

The FSL patch (`0004`) applies to all PPC405 emulation targets — any design
using Xilinx EDK with FSL/FCM IP would hit the same gen_invalid() crash.
It is a reasonable upstream candidate for `target/ppc/translate.c`.

The machine file (`r1mx_virtex4.c`) is too niche for upstream but is a
natural addition for any PPC405/Virtex-4 emulation project.

### `0004-ppc405-fsl-instructions.patch`

**PPC405 FSL (Fast Simplex Link / FCM) instruction support** (`target/ppc/translate.c`).

The RED ONE MX firmware uses the PPC405F6 APU/FCM interface for FPGA communication
via FSL channel instructions. All 16 FSL opcode variants are exercised 3,145 times
during VxWorks boot. Without this patch all FSL instructions hit `gen_invalid()`,
generating a 0x700 Program Check exception storm that prevents VxWorks from booting.

FSL instruction encoding:
- Primary opcode 31 (0x1F), XO = 0x130-0x13F
- opc1=0x1F, opc2=0x09, opc3=0x10-0x1F
- 8 "get" variants (read from FCM channel): `tget nget tnget cget ncget tcget tncget get`
- 8 "put" variants (write to FCM channel): `tput nput tnput cput ncput tcput tncput put`

With no FPGA fabric in the emulator:
- `gen_fsl_get`: sets `rD = 0` (empty channel). VxWorks BSP uses `fsl_isinvalid(x)` =
  `addic. rD, x, 0`; with rD=0, CR0.EQ=1, so the firmware takes the "unavailable" path.
- `gen_fsl_put`: NOP (silently discards the write).

Registered under `PPC_405_MAC` flag so handlers only activate on PPC405 CPUs and
do not conflict with ISA300/ISA206 handlers at the same opcode table slots.

### `0005-silence-sler-abort.patch`

**Silence SLER abort caused by firmware boot countdown** (`target/ppc/helper_regs.c`).

The RED ONE MX firmware uses physical address 0x7c as a 32-bit countdown counter
during early boot initialisation (function `fn_5b1940`). The initial counter value
is loaded from whatever bytes reside at that address; at boot time those bytes happen
to be the instruction `mtspr ICCR, r4` (0x7c9bfba6). The firmware decrements this
value and writes it back in a tight loop:

```
fn_5b1940:
  0x5b1940  cmplwi  r30, 0          ; if r30 == 0, skip
  0x5b1944  beq     +0xcc
  0x5b1948  addic.  r30, r30, -1    ; r30--
  0x5b194c  stw     r30, 0x7c(r31)  ; r31=0, writes countdown to 0x7c
  0x5b1950  bne     -0x8            ; loop until zero
```

Each store to address 0x7c invalidates QEMU's translation block (TB) cache for
page 0. When the TB containing address 0x7c is re-translated during the countdown,
QEMU reads the transient value 0x7c9beba7 (5119 iterations in) and decodes it as
`mtspr SLER, r4` (SPR 0x3BB). QEMU's `store_40x_sler` then aborts with
"Little-endian regions are not supported by now".

The SLER (Storage Little-Endian Register) controls byte-lane reversal for PPC405
memory regions. The firmware does not use little-endian memory regions; the apparent
SLER write is a transient artefact of the countdown overwriting instruction bytes.
Silently accepting non-zero SLER values (just storing in the SPR array) is correct:
QEMU has no LE memory region support to protect, and the firmware does not rely on it.

Without this patch the emulator aborts immediately after usrInit returns.
With this patch, VxWorks boots fully to the WDB task (0x37c440) and runs stably.

