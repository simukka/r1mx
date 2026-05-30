# Plan: Replacing the SWF GUI in RED ONE MX Firmware

## Context

The RED ONE MX camera firmware embeds Scaleform GFx 2.x (a proprietary, statically-linked, fully-stripped C++ Flash rendering library) to render its on-screen display. The GUI is authored as SWF v7 / ActionScript 2.0 and blitted to the FPGA via DMA for compositing with the live video signal.

The goal is to identify replacement approaches that are tractable given the hardware constraints: a **PowerPC 405F6** (in-order, ~400–500 MHz, no GPU, VxWorks 6.x RTOS). Scaleform itself is a CPU-only software rasterizer, so there is no hardware accelerator to lose — any replacement is on equal footing in that regard.

The key integration points to replace:
- SWF content + ActionScript 2 logic
- Scaleform GFx rendering engine
- `FlashVx` wrapper (framebuffer alloc → Scaleform → `FrameBufferBlit` → FPGA DMA)
- XML socket on TCP 49152 (parameter get/set, used by GUI to talk to firmware)

---

## Options (ordered easiest → hardest)

### Option A — Re-author the SWF (keep Scaleform, replace content only)

**What changes:** Only the SWF files at `0x9E03BC` / `0xB24EF8` and the OSD XML at `0x9D2AE0`.  
**What stays:** Scaleform GFx, `FlashVx`, the FPGA DMA path, TCP 49152 server — everything in the firmware C++ layer is untouched.

- Decompile existing SWF with JPEXS ffdec → use as reference
- Re-author GUI in ActionScript 2 (same SWF v7 format)
- Repack into firmware image at same offsets
- OSD XML (`panels.xml`) can also be edited declaratively

**PPC405 suitability:** Perfect — no change to runtime cost; Scaleform is already running fine.  
**Risk:** Low. Scaleform's AS2 rendering stays in the loop.  
**Constraint:** Stuck with Scaleform's feature set and AS2. No modern layout primitives.

---

### Option B — LVGL (replace Scaleform + SWF entirely)

**What changes:** Remove Scaleform + SWF; replace `FlashVx` internals with LVGL rendering to the same CPU framebuffer; `FrameBufferBlit` path to FPGA DMA remains untouched.

[LVGL](https://lvgl.io) is a lightweight embedded GUI library (pure C, ~300 KB ROM, ~64 KB RAM minimum). It has a VxWorks port, a software renderer that writes to a flat framebuffer, and was designed exactly for constrained CPUs like this. No OS or GPU dependencies.

**Integration sketch:**
1. Replace `FlashVx::FrameBufferAlloc` → call `lv_init()` + `lv_disp_buf_init()` with same CPU RAM buffer
2. Replace the Scaleform render tick → `lv_timer_handler()` in the VxWorks UI task
3. Replace `FrameBufferBlit` flush callback → existing FPGA DMA call unchanged
4. Replace `UiEngineModule::FlashLoadSwf` → load LVGL UI definitions (C code or XML via lv_xml)
5. Replace TCP 49152 XML server → keep same protocol or replace with simpler REST; LVGL UI calls same parameter API

**PPC405 suitability:** Excellent — LVGL was designed for Cortex-M4 class hardware and will be fast on a 400 MHz PPC405.  
**Risk:** Medium. Requires reimplementing the UI widget logic in C, but the architecture is clean.  
**Upside:** Modern, actively maintained, well-documented, no licensing issues.

---

### Option C — Dear ImGui (immediate-mode, software renderer)

Same structural approach as LVGL but using Dear ImGui with its built-in software renderer backend.

**PPC405 suitability:** Good. ImGui's software renderer is simple and portable.  
**Risk:** Medium-high. ImGui is C++11; VxWorks 6.x compiler support for C++11 needs verification. Also designed for developer tooling UIs, not production camera menus — the widget set is less polished.

---

### Option D — Raw framebuffer + custom renderer

Write a minimal C renderer directly into the `FlashVx` framebuffer. No third-party GUI library — just blit text, rectangles, and icons from a sprite atlas.

**PPC405 suitability:** Maximum. No overhead.  
**Risk:** High maintenance burden. Essentially writing a GUI toolkit from scratch.

---

## Recommended Approach

**Option A first, Option B if Scaleform needs to be removed.**

- If the goal is a new UI look/feel without firmware risk: **Option A** is the right call. The Scaleform + FPGA pipeline is working and understood; re-authoring the SWF is straightforward with JPEXS ffdec as a decompile reference.
- If Scaleform must be removed (licensing, binary size, or AS2 limitations): **Option B (LVGL)** is the best fit for the PPC405. It is the only option with a VxWorks port, designed for constrained CPUs, and requires only replacing the `FlashVx` internals while keeping the FPGA DMA blit path intact.

---

## Critical Files

| File / Address | Role |
|---|---|
| `firmware/reverse/build_32/extracted/software.patched.bin` | Firmware binary to patch |
| `0x9E03BC` (in binary) | Primary SWF — replace for Option A |
| `0x9D2AE0` (in binary) | OSD XML (`panels.xml`) — edit for Option A |
| `firmware/reverse/build_32/src/xmlsocket/` | TCP 49152 server — keep or replace |
| `FlashVx` C++ class (mangled symbols in binary) | Wrapper to replace for Option B |
| `UiEngineModule::FlashLoadSwf` | Entry point to swap for Option B |

---

## Verification

- **Option A:** Extract patched SWF with `binwalk`, decompile with JPEXS ffdec, verify ActionScript logic; boot in QEMU (see `qemu_howto.md` in RE notes) and confirm OSD renders.
- **Option B:** Build LVGL for `ccppc` (PPC603 target); verify framebuffer pixel output matches expected RGBA format (`FlashVx::FrameBufferPixelFormat` — currently unconfirmed); confirm `FrameBufferBlit` DMA path fires correctly by monitoring FPGA MMIO writes.
- Both options: Connect to TCP 49152 with the mock camera server (`firmware/tools/mock_camera_server.py`) to verify parameter get/set still works.
