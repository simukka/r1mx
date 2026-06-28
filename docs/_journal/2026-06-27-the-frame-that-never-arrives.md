---
title: "The Frame That Never Arrives"
summary: "The camera has booted. The display drivers initialized. The FPGA is scanning a framebuffer at 0x840000. But the pixels are noise — and the OSD render buffer is somewhere we can't reach."
tags: [framebuffer, jtag, fpga]
---

Every film is a sequence of frames. The frame is the unit of cinema — the thing the light burned into, the image the projector threw at the screen, the moment a shutter opened and closed and something in the world was arrested and preserved. A filmmaker makes decisions at the level of the frame. Is this composition right? Is this the right light? Does this face, in this instant, say what the story needs it to say?

The RED ONE MX produces frames at up to 120 per second. Each frame is a matrix of photosite values from a 14-megapixel sensor, processed through a color science pipeline, written to media. The HDMI output — the monitor feed that the operator watches, the focus puller checks, the director leans over to see — is a different representation of that data: a 327,680-byte region of memory that the FPGA reads autonomously and converts to electrical signal.

The emulated camera has been running for a week. The framebuffer at physical address `0x840000` is allocated and ready. The FPGA model is scanning it. The output: random pixels. Max-entropy noise. Every frame is a different pattern of garbage.

The last major gap is getting real data into that buffer. And the path there is more complicated than it looks.

---

## The DMA Architecture

The display pipeline is a two-stage system:

1. **CPU side**: the RED application renders OSD elements (menus, timecode, status indicators) into a private buffer using FlashVx, the SWF-based UI engine. It then initiates a DMA transfer via the XPS Central DMA controller at `0x64014000` to move frame data into the shared framebuffer.

2. **FPGA side**: the IO-FPGA reads autonomously from `0x840000` on its own clock, composites any hardware overlays, and drives HDMI/SDI. The CPU doesn't touch this path at frame rate.

The DMA is interrupt-driven. After the firmware calls into the DMA subsystem, it blocks on `semTake(frame_dma_sem, 4000)` — wait up to 4 seconds for the completion interrupt.

The completion interrupt is never delivered. The IO-FPGA's interrupt controller isn't modeled yet. The semaphore fires. The DMA subsystem logs a timeout. The framebuffer stays random.

---

## The DMA Fix (Partial)

Before the IRQ gap can be addressed, the QEMU opb-dma model had two faithfulness bugs:

```bash
# Before fix: guest errors during DMA register access
firmware/scripts/qemu_boot.sh 2>&1 | grep -c "unsupported write"
# 84

# After fix: zero errors
firmware/scripts/qemu_boot.sh 2>&1 | grep -c "unsupported write"
# 0
```

Bug 1: the model rejected accesses to register offsets `+0x4000` and `+0x8000` (the frame buffer bank registers) as out-of-range. The fix expands the register window to `0x10000` slots.

Bug 2: the model rejected 16-bit (`uint16_t`) memory accesses with an error. The fix sets `min_access_size = 1` in the memory region ops.

These are correct fixes — the hardware supports both. But fixing them didn't fix the timeout, because the timeout is caused by the missing completion IRQ, not by the register model. The guest errors dropped to zero. The semaphore still fires at 4 seconds.

---

## The OSD Buffer

The framebuffer at `0x840000` handles the video signal. The OSD — menus, timecode, status overlays, everything the operator actually reads — is composited separately, in a completely different memory region.

`FlashVx` is the RED application's UI engine: an ActionScript player that interprets SWF animation files and rasterizes them into a private BGRA8888 bitmap. That bitmap lives in RTP (Real-Time Processing) memory — a VxWorks memory partition allocated at boot from a private heap. The FlashVx object holds a pointer to its bitmap at offset `+0x9c`. The object's address is different every boot.

To capture a live OSD frame from the real camera:

```bash
# Probe the live FlashVx OSD buffer (needs Channel A / RSP hardware breakpoint)
python3 firmware/scripts/probe_osd_capture.py \
  --port 2345 \
  --reloc 0x10180 \
  --image firmware/reverse/build_32/extracted/software.bin \
  --out firmware/reverse/build_32/camera_reports/cam-working-01/osd_$(date +%Y%m%dT%H%M%SZ).json
```

The result from the June 27 probe ([`osd_rtp_20260627T182932Z.json`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/camera_reports/cam-working-01/osd_rtp_20260627T182932Z.json)):

```json
{
  "ts": "20260627T182932Z",
  "pc": 1373020,
  "this": 198990000,
  "rect": [0, 0, 0, 0],
  "fb_ptr": 0,
  "bpp": 0,
  "width": 0,
  "height": 0
}
```

`fb_ptr` is zero. The probe hit before FlashVx had initialized its bitmap — or at a point where the per-boot relocation had shifted the object address beyond the probe's expected range. RTP memory is MMU-context-dependent: accessible only when the CPU is executing in the FlashVx render task's TLB context.

At idle, in the WIND idle task, those pages aren't mapped. XMD reads return zeros. The buffer exists. We can't reach it without a hardware breakpoint set inside the FlashVx render path, which requires Channel A (the RSP/GDB connection) rather than Channel B (the file-queue fallback that's been doing most of the JTAG work).

```bash
# The capture script that would work with Channel A:
python3 firmware/scripts/probe_osd_capture_rsp.py \
  --hw-port 2345 \
  --bp-addr 0x14f35c \   # FrameBufferBlit — FlashVx render entry
  --reloc 0x10180 \
  --image firmware/reverse/build_32/extracted/software.bin
```

The Channel A routing through the VBox NAT loopback has its own problem — a loopback-bound NAT configuration that blocks the RSP connection. That's the next thing to fix.

---

## What the Noise Means

The framebuffer exists. It's the right size. It's at the right address. The FPGA is reading from it on the right clock. The infrastructure is correct.

The noise in the output is not a failure — it's an accurate picture of the current state. The DMA is configured. The completion interrupt hasn't arrived. When it does arrive — when the IO-FPGA interrupt model is complete and the DMA controller can signal correctly — the pixels will be real.

Think of it this way: the camera makes images of faces. The faces belong to real people — people who were in a room with a filmmaker who thought the moment was worth recording. The emulator is not yet showing those faces. But it's showing the space where they should be. The geometry is right. The address is right. The architecture is understood.

The frame will arrive. This is what preserving a tool actually looks like up close: not a clean restore, not a triumphant reveal, but a careful excavation where each piece has to be understood before the next one can be reached. The image is there. We're still clearing the path to it.
