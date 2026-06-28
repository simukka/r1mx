#!/usr/bin/env python3
"""QEMU-side check: does the firmware populate the FlashVx OSD render buffer?

Boots are driven by qemu_boot.sh --debug (stub :1234, halted at reset). We set a
HW breakpoint at FrameBufferBlit (objdump 0x14f35c; QEMU loads software.bin at
base 0x10000 == objdump --adjust-vma, so the live address == the objdump address,
D=0), continue the boot, and at the first blit read:
  r3            = this (FlashVx*) at the entry (mr r29,r3 is later @0x14f3cc)
  this+0x8c..   = bounds rect (x0,y0,x1,y1)
  this+0x9c     = framebuffer ptr (BGRA8888)
  this+0xa0     = bytesPerPixel
Then we dump a capped slice of the buffer so we can tell whether it holds real
rendered pixels (non-zero, structured) vs. zeros/garbage.

Unlike the live camera this has no JTAG/MMU/halt-cost limits, so we can grab the
whole buffer and resume freely.
"""
import argparse, json, os, struct, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp import RSP  # noqa: E402

BLIT = 0x14f35c  # FrameBufferBlit entry (objdump == QEMU live addr, base 0x10000)
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "reverse", "build_32", "camera_reports", "qemu")


def chunked(t, addr, n, cw=0x1000):
    out = bytearray()
    while len(out) < n:
        k = min(cw, n - len(out))
        out += t.read_mem(addr + len(out), k)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--boot-timeout", type=int, default=240)
    ap.add_argument("--grab", action="store_true")
    ap.add_argument("--max-bytes", type=lambda x: int(x, 0), default=0x100000)
    args = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    t = RSP(port=args.port).connect()
    # QEMU stub: software breakpoints are fine here, but HW works too and matches HW path.
    print(f"[bp] hw breakpoint @0x{BLIT:08x}; continuing boot (timeout {args.boot_timeout}s)")
    t.set_bp(BLIT, hw=True)
    try:
        stop = t.cont(timeout=args.boot_timeout)
    except Exception as e:
        print(f"[!] no blit within {args.boot_timeout}s ({e}); FlashVx OSD likely "
              f"dormant in QEMU (no UI trigger). Check serial log for boot stage.")
        t.clear_bp(BLIT, hw=True)
        return 2
    print(f"[hit] stop={stop.strip()[:40]}")
    regs = t.regs()
    pc = regs.get("pc", 0)
    this = regs.get("r3", 0)
    print(f"[ctx] pc=0x{pc:08x} r3(this)=0x{this:08x}")

    fields = chunked(t, this + 0x8c, 0x18)
    rect = struct.unpack(">4I", fields[:16])
    fbptr, bpp = struct.unpack(">2I", fields[16:24])
    w, h = rect[2] - rect[0], rect[3] - rect[1]
    word0 = t.read_word(this)  # vtable ptr — sanity
    print(f"[obj] vtable=0x{word0:08x} rect={[hex(x) for x in rect]} "
          f"fb=0x{fbptr:08x} bpp={bpp} -> {w}x{h}")
    report = {"ts": ts, "pc": pc, "this": this, "vtable": word0, "rect": rect,
              "fb_ptr": fbptr, "bpp": bpp, "width": w, "height": h}

    if fbptr:
        # quick populated-check: sample first 256 bytes regardless of --grab
        head = chunked(t, fbptr, 0x100)
        nz = sum(1 for b in head if b)
        print(f"[fb] first 256B: {nz}/256 non-zero  hex[0:32]={head[:32].hex()}")
        report["head_nonzero"] = nz
        report["head_hex"] = head[:64].hex()
        if args.grab:
            total = w * h * bpp if (w > 0 and h > 0 and bpp) else 0
            cap = min(total, args.max_bytes) if total else args.max_bytes
            data = chunked(t, fbptr, cap)
            raw = os.path.join(OUTDIR, f"osd_qemu_{ts}.bin")
            with open(raw, "wb") as f:
                f.write(data)
            report["raw"] = os.path.relpath(raw, OUTDIR)
            report["raw_bytes"] = len(data)
            print(f"[grab] {len(data)}/{total} bytes -> {raw}")

    jp = os.path.join(OUTDIR, f"osd_qemu_{ts}.json")
    with open(jp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[done] {jp}")
    t.clear_bp(BLIT, hw=True)
    t.send("c")  # leave it running
    return 0


if __name__ == "__main__":
    sys.exit(main())
