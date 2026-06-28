---
title: "The Blit That Never Fires"
summary: "If you want to see what the camera is drawing, hook the function that draws it. The hook is correct, the address is correct — and it never fires. The OSD doesn't exist until the video pipeline does."
tags: [qemu, osd, flashvx, emulation, display]
---

The goal was simple, or it sounded simple: get the emulated camera to render *something*
we could put in a preview window. Not the live sensor view — that needs a whole video
front-end QEMU doesn't have. Just the OSD. The menu. The status overlay. The pixels the
firmware draws on top of the picture.

The OSD is software-rendered. A class called `FlashVx` — the UI engine, the thing that
plays the camera's Flash-based GUI — draws the overlay into a plain BGRA8888 buffer in CPU
memory, then blits it to the display. We even know the exact mechanics from probing the
live camera over JTAG last session: `FlashVx::FrameBufferBlit` at `0x14f35c` copies from
`*(this+0x9c)` — the bitmap — using the bounds rectangle at `this+0x8c` for width and
height.

So the plan wrote itself. Boot QEMU. Set a breakpoint on `0x14f35c`. When it fires, read
`r3` (the `this` pointer), follow `+0x9c` to the bitmap, dump it, render a PNG. No JTAG, no
MMU contexts, no read-only discipline, no 560-bytes-per-second throughput ceiling. Just
guest RAM, sitting there, ours to read.

---

## The hook is right

First, prove the address. The firmware loads at base `0x10000`, and the twenty bytes at
`0x14f35c` are exactly the `FrameBufferBlit` prologue:

```
7c0802a6   mflr   r0
9421ff88   stwu   r1,-120(r1)
3d2000ea   lis    r9,0xea
9001007c   stw    r0,124(r1)
80090de4   lwz    r0,3556(r9)
```

That last instruction is the tell. `0xea0de4` — offset 3556 from `0xea0000` — is the
display-ready flag the blit checks before it does anything. The hook is on the right
function at the right address. Whatever happens next, it isn't a typo.

## Then it doesn't fire

Boot under GDB with two hardware breakpoints — one on the blit, one on the `FlashVx`
constructor at `0x14f03c`, to catch the object even being *created*. Fifteen minutes. The
guest clock crawls to 00:02:30 and sticks in the AD9889 HDMI retry loop. Neither breakpoint
fires. The constructor is never called. The object never exists. There is no `this`, so
there is no `this+0x9c`.

That much could be blamed on the debugger. We learned the hard way, [five sessions
ago]({{ '/journal/2026-06-23-fifteen-fixes-in-one-session/' | relative_url }}), that GDB
breakpoints wreck the timing of the I²C bottom-halves — the AD9889 reads that pass free-running fail under a
debugger. So maybe the breakpoints themselves were holding the boot back.

Boot again. No GDB. No breakpoints. Free-running, just the serial log. The boot clears the
VPFPGA give-up at 00:00:57, enters HDMI init, prints its first AD9889 `(0x97,0x97)` line at
00:01:17 — and then the guest clock **freezes**. Five minutes of wall-clock time, QEMU
pinned at 100% CPU, the emulated clock motionless at 00:01:17. Not a retry loop politely
logging once a second. A busy-spin that never comes back.

Either way, the destination is the same. The firmware never reaches the code that builds the
OSD.

---

## Why nothing draws

Pull the thread and the whole tangle comes up at once. The display subsystem is a chain of
gates, and every one of them is shut:

1. `FrameBufferBlit` early-returns unless `0xea0de4` (display-ready) is set. It's zero.
2. The only thing that sets `0xea0de4` is the display-enable function `0x14faf8` — which is
   *itself* gated on another flag, `0xea0de8`, and returns immediately if that's zero. It
   is. And `0x14faf8` is never even called.
3. The `FlashVx` constructor and the GUI-init function `0xd4394` that would allocate the
   object never run either.

These aren't memory-mapped registers we could fake with a device stub. They're internal RAM
flags, flipped by the firmware's own event and task machinery — and that machinery only runs
once the camera believes it has reached an operational state. Which requires the VPFPGA, the
video and display pipeline, to come up. Which, with no sensor and no display hardware on the
other end, it never does.

So the headless camera renders nothing. Not the sensor view, not the OSD, not a single
frame. Every visual path in the firmware is gated, directly or transitively, on a video
pipeline that cannot start in an empty room.

---

## What this rules out, and what it doesn't

The seductive shortcut is dead. There is no "just hook the blit and screenshot the guest" —
the blit is the *last* link in a chain that never gets built. You can't read a buffer that
was never allocated by an object that was never constructed.

What's left are the honest paths. Bring the VPFPGA up for real in QEMU, register by
register, until the firmware flips its own gates — deep, but it's the actual boot sequence.
Or go back to the working camera over JTAG, where the OSD genuinely renders, and grab the
real `this+0x9c` bitmap — the route we were one memory read away from finishing last time.
Or patch the gates open and watch the GUI render against a display that isn't there, which
will almost certainly crash the same way the faked DMA completion did.

The frame is still out there. It's just on the far side of the video pipeline, and there's
no climbing around it.
