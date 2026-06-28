#!/usr/bin/env python3
"""Channel A (RSP/gdb stub) capture of the FlashVx OSD render buffer.

Why RSP not XMD: the OSD bitmap lives in the FlashVx RTP's private virtual
memory, and FrameBufferBlit must be caught with a real HW breakpoint (the XMD
file-queue agent can do neither). gdb/RSP sets IAC HW breakpoints with no ELF and
reads memory in the *current* (RTP) context — so at the bp we are inside FlashVx,
where r29=this and this+0x9c (the BGRA buffer) are mapped.

Relocation is per-boot. We derive the live FrameBufferBlit address straight from
the vtable slot value (it always holds the live, relocated code pointer):
objdump vtable blit-slot = 0xe08e0c; its live DATA address is 0xe08e0c + D_data.
We probe both D_data candidates (0, +0x180) and take whichever slot holds a code
pointer in the .text range.

READ-ONLY: rsp.py defaults to read-only + hardware breakpoints (Z1/IAC).

Usage (after relay up + host:2345 reachable):
  python3 probe_osd_capture_rsp.py --grab --max-bytes 0x60000
"""
import argparse, json, os, sys, struct
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp import RSP  # noqa: E402

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "reverse", "build_32", "camera_reports", "cam-working-01")
VTABLE_BLIT_SLOT = 0xe08e0c  # objdump addr of FrameBufferBlit ptr in FlashVx vtable
TEXT_LO, TEXT_HI = 0x100000, 0x600000


def derive_blit_addr(t):
    for d in (0x0, 0x180):
        try:
            v = t.read_word(VTABLE_BLIT_SLOT + d)
        except Exception:
            continue
        if TEXT_LO <= v <= TEXT_HI:
            print(f"[reloc] vtable slot @0x{VTABLE_BLIT_SLOT+d:x} -> blit=0x{v:08x} (D_data={d:#x})")
            return v
    return None


def catch_idle(t, tries=40):
    """Land the CPU in the idle/kernel context (pc in the idle-spin region) so
    high firmware data (vtables/BSS) is mapped for reads. Returns pc or None."""
    import time
    for i in range(tries):
        t.interrupt()
        pc = t.regs().get("pc", 0)
        if 0x5bb000 <= pc <= 0x5bb400:
            print(f"[idle] caught idle context at pc=0x{pc:08x} (try {i+1})")
            return pc
        t.send("c")          # resume briefly without waiting for a stop reply
        time.sleep(0.05)
    print(f"[idle] not caught after {tries} tries (last pc=0x{pc:08x})")
    return None


def chunked(t, addr, n, cw=0x800):
    out = bytearray()
    while len(out) < n:
        k = min(cw, n - len(out))
        out += t.read_mem(addr + len(out), k)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345)
    ap.add_argument("--grab", action="store_true")
    ap.add_argument("--max-bytes", type=lambda x: int(x, 0), default=0x60000)
    args = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    t = RSP(host=args.host, port=args.port).connect()
    try:
        t.interrupt()
        catch_idle(t)               # land in kernel context so vtable maps
        blit = derive_blit_addr(t)
        if not blit:
            print("[!] could not derive FrameBufferBlit address from vtable; "
                  "is the camera booted past GUI init?")
            return 1
        print(f"[bp] hw breakpoint @0x{blit:08x}")
        t.set_bp(blit, hw=True)
        print("[cont] waiting for a blit (interact with the UI if static) ...")
        stop = t.cont(timeout=180)
        print(f"[hit] stop={stop.strip()[:40]}")
        regs = t.regs()
        pc = regs.get("pc", 0)
        # bp is at the ENTRY (0x14f35c): this=r3 here; r29=this only after 0x14f3cc
        this = regs.get("r3", 0)
        print(f"[ctx] pc=0x{pc:08x} r3(this)=0x{this:08x} r29=0x{regs.get('r29',0):08x}")

        fields = chunked(t, this + 0x8c, 0x18)
        rect = struct.unpack(">4I", fields[:16])
        fbptr, bpp = struct.unpack(">2I", fields[16:24])
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        print(f"[obj] rect={[hex(x) for x in rect]} fb=0x{fbptr:08x} bpp={bpp} -> {w}x{h}")
        report = {"ts": ts, "pc": pc, "this": this, "rect": rect,
                  "fb_ptr": fbptr, "bpp": bpp, "width": w, "height": h}

        if args.grab and fbptr and bpp:
            total = w * h * bpp
            cap = min(total, args.max_bytes) if total else args.max_bytes
            print(f"[grab] {cap}/{total} bytes from 0x{fbptr:08x} (~{cap/560:.0f}s halt)")
            data = chunked(t, fbptr, cap)
            raw = os.path.join(OUTDIR, f"osd_rtp_{ts}.bin")
            with open(raw, "wb") as f:
                f.write(data)
            report["raw"] = os.path.relpath(raw, OUTDIR)
            report["raw_bytes"] = len(data)
            print(f"[grab] -> {raw}")

        jp = os.path.join(OUTDIR, f"osd_rtp_{ts}.json")
        with open(jp, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[done] {jp}")
    finally:
        try:
            if 'blit' in dir() and blit:
                t.clear_bp(blit, hw=True)
        except Exception:
            pass
        try:
            t.send("c")  # resume without waiting for a stop reply (non-blocking)
            print("[resume] camera continued")
        except Exception as e:
            print(f"[warn] resume: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
