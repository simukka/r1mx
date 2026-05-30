# QEMU Emulator — Xilinx Peripheral Driver Plan

**Target:** Complete MMIO peripheral emulation for the RED ONE MX Build 32 firmware  
**Machine:** `r1mx-virtex4` (QEMU `hw/ppc/r1mx_virtex4.c`)  
**CPU:** PowerPC 405F6 (Virtex-4 FX hard-macro), big-endian, 400 MHz  
**OS:** VxWorks 6.4 / Wind River Platform 2.6  
**Source reference:** `firmware/reverse/build_32/xsrc/` (43 exact driver sources)  
**Register maps:** `~/src/RED/drivers/<package>/src/*_l.h` headers  

**QEMU fork:** https://github.com/simukka/qemu-r1mx — branch `r1mx` (based on QEMU 8.2.2 `main`)

```bash
# Clone and build
git clone -b r1mx git@github.com:simukka/qemu-r1mx.git
cd qemu-r1mx && mkdir build && cd build
../configure --target-list=ppc-softmmu --enable-debug --disable-docs --disable-werror
make -j$(nproc)
```

---

## Peripheral Status Summary

| Peripheral | MMIO Base | Driver Package | QEMU Status | Priority |
|---|---|---|---|---|
| XUartLite | `0xe0600000` | `uartlite_v1_12_a` | ✅ Implemented | — |
| XUartNs550 #1 | `0xe0640000` | `uartns550_v1_11_a` | ✅ Implemented | — |
| XUartNs550 #2 | `0xe0650000` | `uartns550_v1_11_a` | ✅ Implemented | — |
| XIntc | `0xe0800000` | `intc_v1_10_c` | ✅ Implemented | — |
| XEmacLite | `0xe1020000` | `emaclite_v1_12_a` | ✅ Implemented | — |
| XIic | `0xb2600000` | `iic_v1_13_b` | ✅ Implemented | — |
| XDmaChannel / XDmaMulti | `0x64010000` | `dma_v1_10_b` | ✅ Implemented (`xlnx.opb-dma-channel`) | ~~P1~~ |
| XPci_v3 | `0xe1200000` | `pci_v1_02_a` | ✅ Implemented (`xlnx.opb-pci-host`) | ~~P2~~ |
| RED Histogram IP ×5 | `0xe0080000`–`0xe0200000` | Custom RED FPGA | ✅ Implemented (`red.histogram-ip`) | ~~P3~~ |
| XOpbArb | (DCR-internal) | `opbarb_v1_02_a` | ➖ Not needed | — |
| XPlbArb | (DCR-internal) | `plbarb_v1_01_a` | ➖ Not needed | — |
| IPIF layer | — | `ipif_v1_23_b` | ➖ Library only | — |
| NOR Flash | `0xf0000000` | EBC peripheral | ✅ Returns 0xFF (erased state) | ~~P4~~ |
| PCI memory window | `0xa0000000` | — | ⚠ Unmapped (no devices) | P2 |
| PCI config aperture | `0xe2000000` | — | ⚠ Unmapped | P2 |

---

## Phase 1: XDmaChannel / XDmaMulti (Priority 1)

### Why it matters
The firmware uses `xps_central_dma` at `0x64010000` (confirmed: `XPAR_DMACHANNEL_0_BASEADDR`
in xparameters.h). The DMA driver is used for bulk data transfers in the camera pipeline.
Without a stub, any DMA initialisation or transfer attempt will Machine Check Exception.

### Source files
```
xsrc/xdma_channel.c          — single-channel DMA init, transfer, interrupt
xsrc/xdma_channel_sg.c       — scatter-gather extension
xsrc/xdma_multi.c            — multi-channel wrapper
xsrc/xdma_multi_sg.c         — multi-channel scatter-gather
```

### Register map (from `dma_v1_10_b/src/xdma_channel.h` + IPIF v1.23b)

The OPB central DMA uses the IPIF framework. The interrupt/status registers follow the
standard IPIF layout at base, with DMA-specific registers at base+0x00..+0x28:

| Offset | Register | Description |
|--------|----------|-------------|
| `+0x00` | DMASR | DMA Status Register (bit0=Busy, bit1=BusError, bit2=DBTOut, bit3=L, bit4=SG) |
| `+0x04` | DMACR | DMA Control Register (bit0=Enable, bit11=SGEnable) |
| `+0x08` | SA | Source Address |
| `+0x0C` | DA | Destination Address |
| `+0x10` | LENGTH | Byte count |
| `+0x14` | SWCR | Software Control (bit0=SWReq for SG transfer) |
| `+0x18` | UPC | Unserviced Packet Count (SG mode) |
| `+0x1C` | PCT | Packet Count Threshold |
| `+0x20` | PWB | Packet Waitbound |
| `+0x24` | ISR | Interrupt Status Register (shared IPIF pattern) |
| `+0x28` | IER | Interrupt Enable Register |

**Scatter-gather descriptor format** (from `xdma_channel.h` `XBufDescriptor` struct):
```c
typedef struct {
    u32 NextPtr;        // +0x00: next descriptor physical address (0 = end of chain)
    u32 SourceAddr;     // +0x04
    u32 DestinationAddr;// +0x08
    u32 Control;        // +0x0C: byte count + flags (XDC_CONTROL_LAST_BD_MASK etc.)
    u32 Status;         // +0x10: written by hardware on completion
    u32 DevicePriv[4];  // +0x14..+0x23: device-specific (XEmacLite fills these)
    u32 Rsvd[4];        // padding
} XBufDescriptor;       // total 64 bytes
```

### QEMU implementation plan

**File:** `hw/dma/xilinx_dma_channel.c` (new)  
**Bus:** Add to `r1mx_virtex4.c` memory map at `0x64010000`, size `0x10000`

Minimum viable model (passes `XDmaChannel_SelfTest`):
1. Implement register read/write for all offsets above
2. On write to `LENGTH` (with SA/DA already set): simulate immediate transfer complete
   - Copy `LENGTH` bytes from SA to DA using `cpu_physical_memory_rw()`  
   - Set DMASR `Busy` → 0, `Done` → 1
3. Assert XIntc IRQ line (connected to appropriate XIntc input) on completion
4. SG mode: walk descriptor chain on `SWCR[SWReq]` write, mark each descriptor Status=done

**Self-test sequence** (from `xdma_channel.c:XDmaChannel_SelfTest()`):
- Writes a test pattern to a local buffer, sets up a simple transfer
- Checks DMASR `Busy` clears and `Done` sets within a timeout
- **QEMU must clear `Busy` and set `Done` synchronously** (or the selftest will timeout-loop)

---

## Phase 2: XPci_v3 + PCI Devices (Priority 2)

### Why it matters
The PCI bridge connects to:
- **Silicon Image SiI3512** — SATA controller → CF card / SSD storage
- **Philips ISP1562** — USB OHCI host controller → USB peripherals

Without PCI, the firmware cannot initialise storage or USB. WDB agent network transport
(XEmacLite) works without PCI, but the full camera boot path requires file system access.

### Register spaces

| Region | Address | Size | Purpose |
|---|---|---|---|
| PCI register space | `0xe1200000` | 64KB | XPci_v3 IP core registers |
| PCI config aperture | `0xe2000000` | 256KB | Type 0/1 config cycles |
| PCI memory (primary) | `0xa0000000` | 64MB | Device BARs (SiI3512, ISP1562) |
| PCI memory (secondary) | `0x80000000` | 512MB | Extended PCI aperture |

### Source files
```
xsrc/xpci.c          — PCI bridge init, scan, map
xsrc/xpci_config.c   — config read/write (header type 0/1)
xsrc/xpci_intr.c     — interrupt dispatch
xsrc/xpci_selftest.c — self-test (checks bridge responds to config cycles)
xsrc/xpci_v3.c       — V3 semiconductor PCI bridge register layer
```

### QEMU implementation plan

**Approach:** Use QEMU's existing `hw/pci/` infrastructure.

1. Implement `xilinx_pci_host.c` as a PCI host bridge:
   - Expose `0xe1200000` as bridge control registers  
   - Expose `0xe2000000` as PCI config space using `pci_host_conf_register_mmio()`  
   - Map `0xa0000000` as PCI memory using `pci_host_data_register_mmio()`

2. Add **SiI3512 stub** (`hw/ide/sii3512_stub.c`):
   - Vendor/device 0x1095:0x3512, class 0x0101 (IDE controller)  
   - Implement ATA command set: `IDENTIFY`, `READ_SECTORS`, `WRITE_SECTORS`
   - Back with a QCOW2/raw image file for the SSD  
   - **Critical:** VxWorks ATA driver will probe at the SiI3512's BARs — must respond to
     `CMD` register reads at BAR0+7 with `DRDY` (0x40) for ATA identify to succeed

3. Add **ISP1562 stub** (`hw/usb/isp1562_stub.c`):
   - Vendor/device 0x04CC:0x1562, class 0x0C03 (USB OHCI)  
   - Return vendor ID on config read; NAK all OHCI register accesses initially  
   - Full OHCI implementation optional (VxWorks USB stack can be disabled)

**Self-test sequence** (from `xpci_selftest.c:XPci_SelfTest()`):
- Reads the bridge's vendor/device ID register
- Performs a PCI config read cycle to check the bridge is operational
- QEMU must respond to `0xe1200000` register reads with valid bridge ID

**Self-test pass condition:** `XPci_SelfTest()` returns `XST_SUCCESS` (0).  
Minimum: bridge register space at `0xe1200000` returns non-0xFFFFFFFF on first read.

---

## Phase 3: RED Custom FPGA IP Stubs (Priority 3)

### Why it matters
Five custom histogram/waveform IP blocks are registered in the PLB table and have named
interrupt entries. The firmware's `sysHwInit_seq` (fn_DCB0) initialises them.  
Without stubs, register accesses will Machine Check Exception.

### Blocks and addresses

| Address | Device string (from firmware) | IRQ line |
|---|---|---|
| `0xe0080000` | "Luma Histogram" | XIntc IRQ (TBD) |
| `0xe00a0000` | "RGB Histogram" | XIntc IRQ (TBD) |
| `0xe0100000` | "RGB Comp Histo" | XIntc IRQ (TBD) |
| `0xe0120000` | "Mono Histogram" / "Raw Histogram" | XIntc IRQ (TBD) |
| `0xe0200000` | "Luma Waveform" / "RGBRaw Histo" | XIntc IRQ (TBD) |

These are **proprietary RED FPGA IP cores** with no public register documentation.  
Behavior is inferred from firmware access patterns (via Ghidra decompilation).

### QEMU implementation plan

**File:** `hw/misc/red_histogram_ip.c` (one model, instantiated 5 times)

Minimum viable stub:
1. Expose 64KB MMIO region per block
2. Return 0 for all reads (histogram data = empty/zero)
3. Silently discard all writes
4. Never assert IRQ (histogram done interrupts will never fire; firmware must not hang on them)

**Risk:** If the firmware busy-polls a "FIFO not empty" status bit in a histogram IP block,
the stub's read-all-zeros behavior will cause a hang. Mitigation:
- Run firmware under QEMU with `strace`-equivalent MMIO logging to identify any poll loops
- Add firmware patches for any confirmed poll loops (similar to existing MCE patches)

**Register map recovery strategy:**
- `mcp__r1mx__search_firmware` for "histogram" to find driver functions
- Trace all MMIO accesses in the `0xe0080000`–`0xe0200000` range from QEMU log
- Cross-reference with the FSL `cget/cput` channel assignments (FCM channels 0–11
  carry sensor data from FPGA — histogram IPs likely feed these)

---

## Phase 4: NOR Flash Stub (Priority 4)

### Why it matters
`0xf0000000` — 128MB NOR flash window (boot ROM, firmware storage).  
VxWorks TFFS (True Flash File System) may probe this region during `usrRoot()`.  
Currently returns `0x00000000` on reads (unmapped) — should return `0xFF` (erased flash).

### Implementation

Add to `r1mx_virtex4.c`:
```c
/* NOR Flash: 128MB of 0xFF (erased state) */
static uint64_t nor_flash_read(void *opaque, hwaddr addr, unsigned size) {
    return 0xFFFFFFFF;  /* All-ones = unprogrammed NOR flash */
}
static void nor_flash_write(void *opaque, hwaddr addr, uint64_t val, unsigned size) {
    /* Discard: no persistent flash in emulation */
}
```

For a fuller implementation: use QEMU's `hw/block/pflash_cfi02.c` (CFI-compatible flash)
backed by a file image, which allows VxWorks TFFS to format and use the flash.

---

## Phase 5: VxWorks Tick Clock (PPC405 internal PIT)

### Status: ✅ no new QEMU device needed — investigation reframed

The original Phase 5 hypothesis (an external `xps_tmrctr` IP on the XIntc bus) is **wrong**.
Firmware disassembly (see `re_reference.md` §6c and the SPR stub table at offsets 0x381f7c /
0x382024 / 0x382034) shows the BSP tick is driven by the **PPC405 internal PIT** (SPR 0x3DB),
firing exception vector `0x00001000`. Confirming evidence:

- `xtmrctr.c` is absent from `xsrc/` — no `XTmrCtr_*` driver in the firmware.
- mtspr-PIT stub at `0x381f7c` is reached from `sysClkEnable` (`0x19474`),
  `sysClkDisable` (`0x194ec`), and `sysClkRateSet` (`0x19568`).
- `sysClkEnable` sequence (paraphrased): clear TSR(WIS), `mtspr PIT, reload`,
  `mtspr TCR, TCR | 0x04400000` (PIE | ARE).
- `sysTimerClkFreq = 100 MHz`; reload value lives at `[0xe9c7c0]`.

QEMU already implements the PPC405 PIT end-to-end:

- `hw/ppc/ppc.c` — `store_40x_pit`, `store_40x_tcr`, `store_40x_tsr`, `start_stop_pit`,
  `cpu_4xx_pit_cb`. Reload value, PIE bit (TCR[26]), and ARE bit (TCR[22]) are honoured.
- `target/ppc/cpu_init.c` — SPR 0x3DB/0x3DA/0x3D8 registered with the correct callbacks.
- `target/ppc/excp_helper.c` — `PPC_INTERRUPT_PIT` raises `POWERPC_EXCP_PIT` at vector 0x1000.

### Remaining investigation

The PIT interrupt is gated on `MSR.EE` (`async_deliver` in `excp_helper.c`). The blocker is
no longer hardware — it is firmware state.

**Call chain (static analysis, only path that programs the PIT):**
```
usrInit @ 0x36c350  →  bl kernelInit @ 0x5a7f30 (called from 0x36c424)
                          └── scheduler dispatches root task
                                └── usrRoot @ 0x36c440
                                      ├── bl sysClkRateSet @ 0x952c (0x36c4e4)
                                      └── bl sysClkEnable  @ 0x942c (0x36c4e8)
```

Confirmed addresses in `software.patched.r1mx.bin` (NOT 0x19460 — the summary's address was
based on the unpatched binary). Only one `bl 0x942c` exists in the binary; no data-word or
`lis+addi` reference builds the address anywhere else.

**Observed in 30 s `-d cpu,int --trace 'ppc40x_*'` run (65-patch `--r1mx` binary):**

1. Reached: `usrInit`, `kernelInit @ 0x5a7f30`, `taskInit @ 0x5b231c`, plus heavy activity in
   `0x44xxxx`/`0x49xxxx`/`0x5b0xxx-0x5bbxxx` (scheduler internals).
2. **Not** reached: `usrRoot @ 0x36c440`, `0x381a8c` (corrected root-task PC per re_ref §53a),
   `0x5ab0dc` (workQ spin), `0xddb8`/`0xdde0` (second-usrInit / rootTask wrapper).
3. MSR ∈ {`0x00000000`, `0x00000300`} only — `EE` never set.
4. PIT trace shows exactly one boot-time write (`PIT := 0`, `TCR := 0xFFFFFFFF → 0xFFC00000`,
   `TSR := 0`) and nothing else.

**Conclusion:** the firmware is stuck inside `kernelInit` before the scheduler dispatches the
root task. `sysClkEnable` and the workQ spin are both *downstream* of root-task dispatch — the
scheduler must bootstrap without a tick clock first. Therefore the remaining Phase 5 work is
**not** "add hardware in QEMU"; it is debugging why `kernelInit @ 0x5a7f30` does not complete
root-task dispatch in QEMU, downstream of the existing 65 `--r1mx` patches.

### Verification recipe

```
~/src/qemu-r1mx/build/qemu-system-ppc \
  -machine r1mx-virtex4 -m 2G -nographic \
  -device "loader,file=.../software.patched.r1mx.bin,addr=0x0,force-raw=on" \
  --trace 'ppc40x_*' --trace 'ppc4xx_pit*' -d int
```

A working tick clock will show repeated `ppc40x_store_tsr`/`ppc4xx_pit_start` events plus
`Raise exception at 00001000` deliveries once MSR.EE flips on. Today only the boot-time
write is observed.

### Optional debug-only fallback

If the goal is to prove the PIT path independent of BSP init: a small firmware patch that
manually does `mtspr PIT, N` + `mtspr TCR, 0x04400000` + `mtmsr (MSR | 0x8000)` (EE=1) at the
end of `usrInit` should produce a stream of PIT exceptions. This is for diagnosis, not
production — the real fix is to repair the BSP init path so `sysClkEnable` runs naturally.

---

## Implementation Order & Dependencies

```
Phase 1 (DMA)    ✅ done
Phase 2 (PCI)    ✅ done
Phase 3 (Histogram stubs) ✅ done
Phase 4 (NOR Flash) ✅ done
Phase 5 (Tick clock)      ⚠️ QEMU side complete (PPC405 internal PIT already modelled);
                             remaining work is firmware-side — trace why sysClkEnable is
                             never called and confirm MSR.EE re-enables before the workQ spin
```

---

## QEMU Source File Map

```
hw/ppc/r1mx_virtex4.c          — machine definition (add device instantiation here)
hw/dma/xilinx_dma_channel.c    — NEW: Phase 1 DMA
hw/ppc/xilinx_pci_host.c       — NEW: Phase 2 PCI host bridge
hw/ide/sii3512_stub.c          — NEW: Phase 2 SATA stub
hw/usb/isp1562_stub.c          — NEW: Phase 2 USB stub (optional)
hw/misc/red_histogram_ip.c     — NEW: Phase 3 histogram stubs (×5)
hw/ppc/ppc.c                   — PPC405 internal PIT (used as Phase 5 tick — no new file)
```

---

## Self-Test Pass Checklist

For each driver, `X*_SelfTest()` must return `XST_SUCCESS (0)`.  
The following MMIO responses are required at boot:

| Driver | SelfTest requirement | QEMU action |
|---|---|---|
| `XUartLite_SelfTest` | Read `base+0x08` returns `0x04` (TX FIFO empty) | ✅ Already handled |
| `XUartNs550_SelfTest` | MCR LOOP bit works; 32-byte loopback passes | ✅ Already handled |
| `XIntc_SelfTest` | ISR/IER read-write; MER write | ✅ Already handled |
| `XEmacLite_SelfTest` | Internal loopback TX→RX | ✅ Already handled |
| `XIic_SelfTest` | SOFTR write 0xA; CR/SR read | ✅ Already handled |
| `XDmaChannel_SelfTest` | Transfer completes; DMASR Busy=0 | ❌ Phase 1 |
| `XPci_SelfTest` | Bridge registers respond; config cycle ok | ❌ Phase 2 |
| `XOpbArb_SelfTest` | (DCR-internal; probably no MMIO test) | ➖ Likely N/A |
| `XPlbArb_SelfTest` | (DCR-internal; probably no MMIO test) | ➖ Likely N/A |

---

## Key Source Files for Reference

```
# Register maps (authoritative):
~/src/RED/drivers/dma_v1_10_b/src/xdma_channel.h       — DMA register offsets + struct
~/src/RED/drivers/pci_v1_02_a/src/xpci.h               — PCI bridge register map
~/src/RED/drivers/iic_v1_13_b/src/xiic_l.h             — IIC low-level register defs
~/src/RED/drivers/intc_v1_10_c/src/xintc_l.h           — INTC register map
~/src/RED/drivers/emaclite_v1_12_a/src/xemaclite_l.h   — EMAClite register map
~/src/RED/drivers/uartlite_v1_12_a/src/xuartlite_l.h   — UartLite register map
~/src/RED/drivers/uartns550_v1_11_a/src/xuartns550_l.h — NS550 register map

# Self-test implementations (QEMU must satisfy):
firmware/reverse/build_32/xsrc/xdma_channel.c   — DMA self-test at bottom
firmware/reverse/build_32/xsrc/xpci_selftest.c  — PCI self-test

# VxWorks BSP libsrc (exact versions compiled into firmware):
~/src/RED/r1mx_mmio/ppc405_0/libsrc/            — 9 packages confirmed by BSP project
```

---

*Created: 2026-05-27. Based on embedded build paths extracted from build_32 firmware binary.*  
*Cross-reference: `re_reference.md` §6 (MMIO map), §6b (xparameters.h), §6c (ISE source lib), §6d (build paths).*
