---
title: "Fifteen Fixes in One Session"
summary: "Boot stalls at 'Initializing status display.' One I²C transaction never completes. Five interdependent device-model bugs, all on the same path. Fix one, find another."
tags: [qemu, i2c, emulation]
---

The status display on the RED ONE MX body is a small LCD that shows the camera's state: build number, record mode, remaining media, battery level. It is not a glamorous piece of hardware. It's the kind of component that nobody thinks about until it stops working — and when it stops working, the camera is suddenly very hard to use. You can still record. You just can't see what you're recording to, or for how long.

A rental house tech once described replacing a status LCD connector as "the most important repair nobody wants to pay for." The camera still works. The display is a convenience. Until the shoot is in progress and the AC can't tell the operator how much card is left, and then it is not a convenience, it is the entire difference between a problem and a crisis.

The status display is driven by a PCA9698 I²C GPIO expander. The firmware talks to it over the Xilinx XIic controller. In the emulator, this transaction took two minutes and twenty-seven seconds to happen once — and then stopped happening forever.

---

## The Wall

Boot reaches "Initializing status display..." and parks there. No error. No timeout log. Silence. The firmware has called into the I²C subsystem, issued a transaction, and is blocking on a semaphore waiting for completion. The semaphore has a 1-second timeout. It fires. The firmware retries. Fires again. After enough retries, the initialization path declares the display absent and continues — except it doesn't continue, because the retry count is high enough that the boot stalls waiting for the display to respond.

One second per transaction. Dozens of transactions in the initialization sequence. The boot effectively hangs for minutes, then stalls. Not useful.

The I²C controller is the Xilinx `xlnx-xps-iic` model in the QEMU source. The firmware uses it in interrupt-driven mode. Five separate bugs, all on the same code path.

---

## Bug 1: Dead Switch Cases

The XIic interrupt handler dispatches on status bits using an if-else chain in the QEMU model. In the C translation, three case handlers — for `R_CR` (control register, `0x100`), `R_DTR` (TX data register), and `R_RFD` (RX FIFO depth) — had been placed after an unconditional `break` statement. Three handlers: unreachable dead code.

Writes to `R_CR` — the register that initiates an I²C transfer by setting the MSMS bit — were silently discarded. No transfer ever started.

```bash
# The commit that fixed this (in qemu-r1mx):
git -C ~/src/qemu-r1mx log --oneline | grep "switch-label"
# e5b5c5196f hw/i2c: xlnx_xps_iic: fix dead switch labels, add deferred-int BH
```

Three lines rearranged. The switch cases moved above the break. Writes to `R_CR` now fire.

---

## Bug 2: Unconnected IRQ

The XIic driver initiates a transfer, then calls `semTake(send_sem, 1000)` — wait up to 1000ms for the interrupt that signals completion. The interrupt is supposed to arrive on XIntc line 23.

In the QEMU machine definition, line 23 was never wired:

```c
/* In hw/ppc/r1mx_virtex4.c — the fix */
DeviceState *iic  = qdev_new("xlnx.xps-iic");
DeviceState *intc = /* XIntc instance */;

/* Connect XIic interrupt output → XIntc input line 23 */
qdev_connect_gpio_out(iic, 0, qdev_get_gpio_in(intc, 23));
```

Without the wire, every interrupt the XIic asserted went nowhere. Every semaphore timed out.

---

## Bug 3: Single-Slot TX FIFO

Before asserting MSMS (Master Start), the XIic driver preloads the TX FIFO with `[slave_address, register_pointer]` — two bytes. The QEMU model had a one-slot FIFO. The second write clobbered the first. When the controller transmitted, it sent `[register_pointer]` as the slave address byte — wrong address, NAK, transaction failed.

Fix: expand to a 16-element circular TX FIFO with proper head/tail tracking. The Xilinx driver documentation describes the real FIFO depth; the model just hadn't implemented it.

---

## Bug 4: Deferred Interrupt Delivery

The XIic asserts `TX_EMPTY` and `RX_FULL` after the FIFO state changes, not synchronously with the FIFO write. In hardware, these edges arrive asynchronously while the CPU is doing other things. In QEMU, the guest and device models share a thread — the device can only deliver interrupts safely between guest instruction boundaries.

The fix: a QEMU bottom-half (BH) callback that schedules the interrupt delivery for the next safe point:

```bash
# The second commit that added the BH model:
git -C ~/src/qemu-r1mx log --oneline | grep "RSTA"
# a38d0d9bd5 hw/i2c: xlnx_xps_iic: gate RSTA on MSMS
```

When the IIC model needs to assert `TX_EMPTY` or `RX_FULL`, it calls `qemu_bh_schedule(iic->bh)` instead of firing the IRQ directly. The bottom-half fires between guest instructions. The guest sees the interrupt at a point where it's safe to receive it.

---

## Bug 5: Missing Device Models

The firmware initializes two I²C devices during boot: the **PCA9698** GPIO expander at address `0x20` (which drives the status display hardware) and a **DS1339A** RTC at `0x68` (used for boot timing). Without models for either, every transaction produced NAKs. The initialization stalled waiting for the display to acknowledge.

Both are simple enough to stub: the PCA9698 responds with initial output state (all high), the DS1339A responds with plausible RTC register values (January 1, 2009, 00:00:00).

---

## The Debugging Lesson

During development of the BH model, every test run under GDB showed 100% failure. Every transaction. Every time. Under GDB, `SendByteCount` was stuck at 1. `TX_EMPTY` fired 201 times in a row. `MasterRecv` was called zero times across 40 send attempts.

Run free — no GDB, with QEMU log instrumentation — the same model showed this:

```
[iic] Over 105s of boot:
  transfer_begin (0x39):   245
  TX_EMPTY completions:    302
  RX_FULL events:          649
  (0x97,0x97) NAK errors:    5   ← intermittent, firmware retries, boot proceeds
```

97% success rate. Five intermittent failures in 105 seconds, all retried successfully. The "100% failure under GDB" was a measurement artifact: GDB breakpoints halt the CPU, which delays when the bottom-half fires, which changes the sequence the driver sees. The model was correct. The debugger was lying.

```bash
# Correct way to validate timing-sensitive device models: free-run with logging
firmware/scripts/qemu_boot.sh --no-net 2>&1 | grep -E "\[iic\]|FrmBuf|status display"
# Do NOT use --debug (GDB stub) when validating I2C BH timing
```

The rule: **never validate timing-sensitive device models under GDB.** GDB is for structure — call graphs, struct offsets, control flow. For anything involving asynchronous interrupt delivery, free-run with log instrumentation.

---

## After All Five

With all five bugs fixed, the boot cascades. Status display initializes. VPFPGA driver loads. Sensor subsystem starts. HDMI output hardware initializes. The full initialization sequence that had been stalled for days resolves in seconds.

The camera's status display — the one nobody thinks about until it stops working — blinked on in emulation for the first time. A small thing. The kind of repair nobody wants to pay for. Exactly the kind of repair that makes a tool usable for the people who depend on it.
