---
title: "Three Bits and a Waking"
summary: "The emulated camera had been sleeping at the same line for weeks — a driver waiting on a chip that isn't there. Three flipped bits along its own bringup path woke it, and for a few hundred milliseconds it did everything a camera does at dawn, right up until it reached for a picture that no longer exists."
tags: [qemu, vpfpga, fpga, video, emulation, boot, preservation]
---

For weeks the machine has stopped in the same place, mid-sentence, like a projector
that reaches the end of the reel and just keeps turning:

```
  Initializing VPFPGA driver...
```

And then nothing. No error, no panic, no next line. A serial console that has gone
quiet is the most ambiguous thing in this whole endeavor — you cannot tell a corpse
from someone holding their breath. Earlier this same day I'd learned that lesson the
hard way, mistaking a *fixed* boot for a hung one because the errors I'd been reading
as progress had finally stopped. So this time I didn't trust the silence. I went
looking for what the machine was staring at.

## A driver waiting on a ghost

It was staring at a chip that isn't in the room.

The RED ONE MX has two big FPGAs. One — the IO-FPGA — we have; it ships in the
firmware package, and we've pulled it apart bitstream by bitstream. The other, the
VP-FPGA, the *video processor*, is the one design in this camera we've never held.
It lives on a board we don't have, doing the actual work of turning sensor readout
into a picture. In the emulator, that board is an empty socket.

The firmware doesn't know the socket is empty. It boots the way it always boots,
and partway through it tries to bring the video processor to life: check that the
config loaded, check that the high-speed serial link between the two chips is up,
initialize the driver, drain its command FIFO, and wait for the FIFO to report
ready. Every one of those checks is a read from a register that, in our emulator,
answers zero. Zero means *not done. link down. never ready.* So the driver sat in a
loop reading an address that would never change, forever, patient as a stone.

Three reads, three lies of omission. I found each one by following the firmware's
own disassembly to the exact instruction that tested the exact bit:

- The config-DONE bit, at `0xe200028c` — modeled weeks ago.
- The RocketIO "channel up" bit, at `0xe20000f8`, tested by a function that
  literally prints *"Rocket IO Channel is not up!"* when it reads zero. It reaches
  that register through a generic accessor, a little indirection layer that turns a
  logical register number into a physical address; I had to trace the number
  `0xa104` through the accessor to watch it land on `0xe20000f8`.
- And the FIFO-ready bit, bit ten of `0xe0080018`, that the driver-init routine
  spins on after draining the queue.

Set the three bits. Report done, report the link up, report the FIFO ready. It
sounds like cheating. It is, a little — but it is *cheating along the true path*.
These are the answers the real silicon gives when the real board is present and
healthy. I'm not rerouting the firmware around its bringup; I'm standing in for a
chip that would say yes, and letting the firmware do exactly what it was written to
do.

## The block that was never a histogram

One discovery on the way there is the kind that makes the whole map suddenly read
correctly. The address the FIFO lives at, `0xe0080000`, had been labeled in our
emulator as a *histogram* core — one of five little RED FPGA blocks we'd guessed at
and stubbed out to return zero. But the firmware carries its own device table, a
plain list of names and base addresses, and when I read it out, `0xe0080000` wasn't
a histogram at all. It was named `vpfpga`. And the four addresses beside it, all
labeled "histogram" in our code, were `sdio`, `audio`, `dma`, `frmBuf` — the frame
buffer among them. Five honest device names we'd papered over with a guess, because
a guess that returns zero is invisible right up until the day something waits on it.

So the fix is keyed to that one address, and the comment in the code now says what
the block actually is. Small act of cartography. The map is more true than it was.

## What a camera does at dawn

Then the machine woke up, and for a few hundred milliseconds it was wonderful.

The boot didn't just clear the wall — it *poured* past it. Every driver that had
been waiting behind the video processor came up in a rush: the codecs, the HD-SDI
path, the HDMI outputs, the audio, the timecode, the sync. And then the application
layer, the part that had never once run in emulation, started doing the small
domestic chores a camera does when it wakes: it loaded eight hundred and ninety-three
parameters from its factory defaults. It built its profile handlers — `look`, `user`,
`project`, `magazine`. It went looking for its sensor. For the first time, this dead
firmware image was *keeping house*.

I want to be honest about how brief that was.

Because the very next thing the camera did was reach for the picture. The comm
library started reading real data across that high-speed link — not status bits now,
actual words from the video processor — and got back nothing, because there is
nothing there. `rx buffer timeout`. `Timeout waiting for Rx buffer to get anything`.
`VpRegPeek: operation failed`, over and over. And three tasks that had woken up
expecting a working imaging chain — the master controller, the audio manager, the
event logger — reached into empty response buffers, followed a pointer that was
never filled in, and died where they stood. Fatal exception, instruction address
zero. They reached for a picture and fell through the floor.

## The socket and the memory of the board

That's the honest state: the camera now boots far enough to want its eyes, and
discovers it has none. Which is, if you sit with it, exactly the shape of the whole
project. This is a camera the manufacturer walked away from — a professional
instrument sold as an investment, then orphaned, its service dependent on a company
that would rather sell you the next one. What we're doing is rebuilding the room
around the orphaned firmware plank by plank, so that someday it can run without the
silicon that's been discontinued, without the boards you can't buy, without
anyone's permission.

Today we built enough of the room that the firmware woke up and started acting like
itself. The three status bits are committed. The device names are corrected on the
map. And the thing standing between here and a real picture is now named precisely:
the VP-FPGA's actual register file and frame responses — the one design we've never
held — which we'll either have to model from the disassembly or read straight off a
living camera over JTAG and replay.

The machine is no longer holding its breath at that quiet line. It gets up now. It
does its morning chores. It reaches for the picture and finds the socket empty — and
that reaching, that specific and repeatable failure, is the map to the last board we
have to rebuild. A camera that can tell you exactly what it's missing is a camera
much closer to seeing again.
