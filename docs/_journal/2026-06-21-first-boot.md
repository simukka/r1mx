---
title: "First Boot"
summary: "The firmware runs. VxWorks immediately hangs in a DTLB-miss livelock. Is this a firmware bug? No — it's a bug in QEMU's own PPC405 MMU emulation, hiding as firmware behavior."
tags: [qemu, vxworks, emulation]
---

Imagine a film projector that someone spent six months restoring. New lamp, cleaned gate, aligned optics, fresh belts. They thread the film, turn it on, and the projector runs perfectly — until, forty seconds in, it stops. Not a mechanical failure. The motor is turning. The sprockets are engaging. Something in the electrical path is misfiring, cycling, going nowhere.

Is it the film? Is it the projector? The restoration work was correct. The film stock is fine. But the projector and the film are interacting in a way that produces a loop instead of an image.

This is where we are after the load-base fix. The firmware is correct. The emulator is running it. And approximately four seconds into boot, VxWorks hangs in a DTLB-miss livelock that looks, from the outside, exactly like a firmware problem and is not one.

---

## The TLB Bug

VxWorks 6.4 manages the PPC405's Translation Lookaside Buffer through a two-step write: first the high word (virtual address, ASID, page size, the `PAGE_VALID` flag that marks the entry as live), then the low word (physical address, protection bits).

QEMU's implementation in `accel/tcg/cputlb.c` handles both. The high-word handler sets everything correctly, including `PAGE_VALID`. The low-word handler — `helper_4xx_tlbwe_lo` — was rebuilding the protection field from scratch instead of updating the existing entry. Rebuilding from scratch did not preserve `PAGE_VALID`.

Every TLB entry VxWorks wrote became invalid the moment the low word was written. DTLB lookup fails. The exception handler fires. The exception handler writes new TLB entries — hi then lo — which also discard `PAGE_VALID`. The exception handler calls its own handler. Livelock.

The fix is one line in the QEMU source, in the `r1mx` branch of [qemu-r1mx](https://github.com/simukka/qemu-r1mx):

```c
/* helper_4xx_tlbwe_lo in target/ppc/mmu_helper.c */

/* Before: rebuilds prot from scratch, losing PAGE_VALID */
prot = PAGE_READ;
if (!(tlb_lo & TLB_RD))
    prot |= PAGE_WRITE;

/* After: preserve existing flags, then update */
prot = env->tlb_table[mmu_idx][tlb_index].prot;
prot &= PAGE_VALID;   /* keep only the valid bit from hi-word write */
if (tlb_lo & TLB_RD)
    prot |= PAGE_READ;
if (!(tlb_lo & TLB_WR))
    prot |= PAGE_WRITE;
```

After that fix, VxWorks's TLB entries survive both writes. DTLB lookups succeed. Boot continues to the device initialization phase.

---

## The ATA Problem

QEMU has no ATA controller. The RED ONE MX doesn't need one — CompactFlash over the CF interface is not IDE. But VxWorks 6.4's storage subsystem includes legacy `ataDrv` code that probes the traditional IDE ports at boot: `0x1F0` (data/status register) and `0x3F6` (device control).

Without a model, those addresses return whatever DRAM happens to hold. The IDE status register's "busy" bit (`0x80`) is frequently set in random DRAM values. `ataDrv` sees a device claiming to be perpetually busy and waits indefinitely.

The fix is an intentionally fake model — `ata_empty_ops` — that returns `0xFF` for all reads:

```bash
# The boot script handles this automatically with the correct QEMU machine flags.
# To see the raw boot without network (faster startup):
firmware/scripts/qemu_boot.sh --no-net
```

`0xFF` on the status register means "no device present." The probe times out in under a second, `ataDrv` gives up, and boot continues. This is not emulation. It's a controlled lie in the right direction.

---

## Fifteen Tasks

With the TLB bug fixed and ATA probe satisfied, the boot sequence completes. Connect to the QEMU GDB stub and walk the task list:

```bash
# In terminal 1: boot with debug stub
firmware/scripts/qemu_boot.sh --debug

# In terminal 2: walk running tasks
python3 firmware/scripts/qemu_task_walk.py --port 1234
```

Output:

```
Task list (15 entries):
  tTffsPTask        pri=100  entry=0x005aaf5c  (flash filesystem)
  tUiIpServer       pri=110  entry=0x001f0320  (remote TCP)
  tNetTask          pri=50   entry=0x...        (network stack)
  tShell            pri=1    entry=0x...        (VxWorks shell)
  tTelnetd          pri=2    entry=0x...        (Telnet server)
  usrApp            pri=100  entry=0x...        (RED application)
  WIND_taskIdle     pri=255  entry=0x5aaf5c     (idle spin)
  ...
```

Fifteen tasks. The Telnet server is up. The shell is up. The RED application is initializing its device subsystem. VxWorks, complete, running in an emulator that is not and has never been a RED camera.

---

## The Interrupt Storm

Getting the shell to actually respond over Telnet required one more fix: the XIntc interrupt controller.

The XIntc instance pointer in the firmware's BSS held a garbage base address from uninitialized memory. The firmware called `XIntc_CfgInitialize` with that garbage address, which failed silently, which meant the Master Enable Register and Interrupt Enable Register were never set at `0xE0800000`, which meant no external interrupts were ever delivered. No IRQs. No console. No Telnet response.

Fix: initialize the XIntc correctly in the QEMU machine model with base address `0xE0800000`, and wire all the IRQ lines before the firmware starts.

Separately: the XUartLite model had a level-triggered ISR storm. The TX interrupt stayed high after firing, creating a loop that locked out the CPU. Fix: `STATUS_IE` mirrors `CONTROL_IE` (it's a status bit, not a pending flag), and TX/RX use pulse delivery instead of level.

```bash
# After all fixes: boot and verify the Telnet shell responds
firmware/scripts/qemu_boot.sh --usernet &
sleep 8   # let VxWorks finish booting
telnet 127.0.0.1 2323   # port 2323 → camera port 23 via SLIRP forward
# -> VxWorks shell prompt: ->
```

---

## The Bench Unit

A second camera — the bench unit, missing its audio PCI board and sensor board — boot-loops. Power on, initialize, poll for missing boards, fail, watchdog fires, reset, repeat.

This is not an emulation problem. This is a camera accurately reporting that its organs are missing. With XMD attached, the watchdog is masked (debug mode suppresses it) and the system idles at the failed poll instead of resetting — useful for analysis, not useful for shooting. The bench unit has a fixed job: support analysis. It doesn't need to work as a camera.

The working camera is still on the shelf. Its sensor still sees light. The emulator now has a second ghost running alongside it — imperfect, incomplete, but recognizably the same system. A camera that cannot be abandoned, because enough people understand it well enough to keep it alive.
