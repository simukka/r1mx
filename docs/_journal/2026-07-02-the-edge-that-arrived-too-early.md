---
title: "The Edge That Arrived Too Early"
summary: "For weeks the emulated camera complained about its HDMI transmitter three times a second. The failure was a race measured in microseconds that don't exist — and when it was finally fixed, the cure looked exactly like a hang."
tags: [qemu, i2c, ad9889, hdmi, emulation, timing]
---

There is a line that anyone who has booted this firmware in QEMU knows by heart, the way
you know the hum of a bad ballast or the click of a dying drive:

```
! ad9889_interrupt_handler:105 :/hdmi/evf, pass 1: Failed to read AD9889 status registers (0x97, 0x97) via I2C bus
```

Once a second, rotating through three names — `evf`, `lcd`, `mhd`. The electronic
viewfinder. The fold-out LCD. The monitor output. The three ways a camera operator ever
sees what the sensor sees. Behind each name is the same chip: an Analog Devices AD9889B,
an HDMI transmitter, a small square of silicon whose entire job is to carry the picture
from the machine to the human.

A detail worth savoring: the `(0x97, 0x97)` in that message is not data. We disassembled
the handler weeks ago. It's a hardcoded literal in the format string — the firmware
apologizing with fabricated evidence. The camera never got any bytes at all. It just
wanted the log line to look like it had.

## Ninety microseconds that don't exist

The firmware talks to these chips over I2C, through a Xilinx controller core, using
Xilinx's own 2007 driver — we know, because we found the exact source files byte-for-byte
inside the firmware image. The read is a small ceremony: send the register pointer,
repeated start, clock two status bytes back, stop. Interrupt-driven, one byte per
interrupt, each interrupt acknowledged when serviced.

On real hardware this dance is safe for a reason nobody had to think about in 2007. At
I2C speeds, a byte takes something like ninety microseconds to crawl across two wires.
Ninety microseconds is an eternity. The interrupt handler feeds the next byte, tidies up,
acknowledges the interrupt that woke it, and returns — with time to spare before the wire
finishes and the next completion edge arrives. The driver even does something that looks
reckless: at the end of the transmit path it re-reads the interrupt status register and
clears any transmit-empty bit it finds. On silicon, that bit can only be the *old* edge.
The new one is still out on the wire, taking its time.

In the emulator, there is no wire. There is no time. Our model deferred those completion
edges to a QEMU bottom-half — a callback on the main loop, which runs whenever the main
loop feels like it, unsynchronized with the emulated CPU. Usually it fired after the
guest's interrupt handler had finished. Occasionally it fired *inside* it. And then that
harmless-on-silicon cleanup — re-read, clear whatever's there — ate the new edge alive.
The transfer stalled, a semaphore timed out a second later, and the camera wrote another
line about `(0x97, 0x97)`.

The edge arrived too early, and the acknowledgment meant for its predecessor swallowed it.
A race condition between a 2007 driver that trusted physics and a 2024 emulator that had
abolished physics.

## Fix the ordering, not the timing

You cannot out-schedule a race like this. Make the bottom-half later, make it a timer,
tune the delay — you shrink the window, you never close it. The fix is to stop pretending
to have a clock and model the *guarantee* instead: on hardware, the next edge always
lands after the current interrupt is acknowledged. So hold the edge. Don't schedule it.
When the guest is inside a service pass, latch the new completion in a pocket the guest
can't see, and release it at the exact moment the driver signs off — the write-1-to-clear
of the interrupt status register that ends every service pass in this driver, every path,
polled or interrupt-driven. The ack becomes the release. The ack can no longer swallow
what it releases.

I got it wrong on the first try, and the failure mode is worth recording. "Is the guest
inside an interrupt handler?" is answered by looking at the pending interrupt bits — but
reading the receive data register *pops the very bit that proves it*. Sample the evidence
after the read and the mid-transfer refill looks like ordinary task context, asserts its
edge immediately, and the handler's exit ack eats it. Every time, not occasionally. The
intermittent failure became a continuous one — a regression with the courtesy to be
deterministic. Sample before you pop. One line of ordering, the whole bug.

## The silence

Then the part that had me convinced I'd broken the boot entirely.

With the fix in, the serial log went quiet at `Initializing VPFPGA driver...` and stayed
quiet. Minutes of nothing. The old build kept scrolling past that point; mine just
stopped. I stopped the run, added instrumentation, chased phantom deadlocks through a
polled send path, drafted theories about starved spin loops.

Then I ran the unmodified baseline for fifteen minutes and actually read its output.
Everything it printed after that VPFPGA line — every single line — was the AD9889 failure
message. That was it. The spam *was* the heartbeat. For weeks, the error had been the
only proof of life at that stage of boot, and I had learned to read it as progress. Fix
the error and the heartbeat stops, because success, here, prints nothing.

The machine wasn't hung. It was, for the first time, quietly doing its job.

Ten minutes, side by side, identical boots: the old model logged **37** failed status
reads. The new one logged **zero** — with the three HDMI polls completing once a second
each, every register-pointer write and both status bytes clocking through, all the way
down. Committed as `89cc50affe`.

## What's actually restored

It's a status read. Two bytes from a transmitter chip. On the scale of this project —
byte-exact compiler resurrection, JTAG probes of a living camera, FPGA bitstream
archaeology — it is a small thing.

But those two bytes are how the firmware decides whether a monitor is plugged in, whether
the viewfinder is alive, whether to bring up the picture path at all. Every camera that
still shoots — every R1 MX bought as an investment by someone who believed a professional
tool implied professional permanence — runs this exact handshake three times a second,
forever. The emulator now honors it. One more subsystem where the reference platform
behaves like the real machine instead of apologizing with fake hex.

The boot has a new wall now — the VPFPGA driver, sitting silent where the config retries
give up. That's next. The errors will be different, and if today taught anything, it's
this: when they finally stop, check whether you fixed the machine or just silenced the
witness. Sometimes, if you've done the ordering right, they're the same thing.
