#!/usr/bin/env python3
"""Catch FlashVx::FrameBufferBlit on the live camera, read the FlashVx object,
and (optionally) grab the BGRA render buffer — over Channel B (file-queue).

The displayed frame is in FPGA/display memory at 0x840000 (NOT CPU-physical
0x840000, which reads as random heap). The CPU-readable copy is the *render
source*: a BGRA8888 buffer in CPU RAM that FrameBufferAlloc allocates and
FrameBufferBlit copies to the display. The buffer pointer lives in the FlashVx
object at +0x9C (bounds rect +0x8C..0x98, bytesPerPixel +0xA0).

Relocation (cam-working-01): live = symtab-nominal + 0x180 (D_text=0x10180),
so FrameBufferBlit (nominal 0x14F35C) is live 0x14F4DC. On entry r3=this,
r4..r7 = blit region x,y,w,h.

READ-ONLY: stop / bps (hardware) / con / rrd / mrd / bpr only. Never mwr/rwr/rst.

Usage (after `connect ppc hw` + `agent_loop` are up in the VM):
  python3 probe_osd_capture.py            # catch + report geometry, resume
  python3 probe_osd_capture.py --grab     # also dump the buffer (capped)
"""
import argparse, json, os, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xmd_rpc import rpc, parse_mrd  # noqa: E402

BP = 0x14F4DC  # live FrameBufferBlit
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "reverse", "build_32", "camera_reports", "cam-working-01")


def cmd(c, t=20):
    return rpc(c, timeout=t)


def state():
    return cmd("state", 12)


def rrd():
    """Return {regname:int} from XMD rrd."""
    txt = cmd("rrd", 15)
    regs = {}
    for tok in txt.replace("\t", " ").split():
        pass
    # parse "rN: hex" / "pc: hex" pairs
    import re
    for name, val in re.findall(r"([a-z]+[0-9]*):\s*([0-9a-fA-F]+)", txt):
        regs[name] = int(val, 16)
    return regs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp", type=lambda x: int(x, 0), default=BP)
    ap.add_argument("--wait", type=float, default=180, help="seconds to wait for the blit")
    ap.add_argument("--grab", action="store_true", help="also dump the render buffer")
    ap.add_argument("--max-bytes", type=lambda x: int(x, 0), default=0x60000,
                    help="cap on buffer bytes to read (Channel B ~560 B/s)")
    args = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"[state] {state().strip()[:80]}")
    print("[stop]", cmd("stop").strip() or "ok")
    print(f"[bps] hw @0x{args.bp:08x}:", cmd(f"bps 0x{args.bp:x} hw").strip() or "ok")
    print("[con] resuming; waiting for blit ...")
    cmd("con")

    hit = False
    t0 = time.time()
    while time.time() - t0 < args.wait:
        st = state()
        if "Stopped" in st:
            hit = True
            break
        time.sleep(1.0)
    if not hit:
        print(f"[!] no blit within {args.wait}s — removing bp, resuming.")
        cmd(f"bpr 0x{args.bp:x}")
        cmd("con")
        return 1

    regs = rrd()
    pc = regs.get("pc", 0)
    this = regs.get("r3", 0)
    region = (regs.get("r4"), regs.get("r5"), regs.get("r6"), regs.get("r7"))
    print(f"[HIT] pc=0x{pc:08x} r3(this)=0x{this:08x} region(x,y,w,h)={region}")

    obj = parse_mrd(cmd(f"mrd 0x{this+0x8c:x} 6"))  # 0x8c..0xa0 inclusive
    vals = [int.from_bytes(obj[i:i+4], "big") for i in range(0, len(obj), 4)]
    rect = vals[0:4]
    fbptr = vals[4] if len(vals) > 4 else 0
    bpp = vals[5] if len(vals) > 5 else 0
    print(f"[obj] rect(+0x8c..0x98)={[hex(v) for v in rect]} "
          f"fb(+0x9c)=0x{fbptr:08x} bpp(+0xa0)={bpp}")

    report = {"ts": ts, "pc": pc, "this": this, "region_xywh": region,
              "rect": rect, "fb_ptr": fbptr, "bpp": bpp}

    # infer geometry: rect likely (left,top,right,bottom)
    width = rect[2] - rect[0] if len(rect) >= 3 else 0
    height = rect[3] - rect[1] if len(rect) >= 4 else 0
    report["width"], report["height"] = width, height
    print(f"[geom] inferred width={width} height={height} "
          f"buffer={width*height*max(bpp,1)} bytes")

    if args.grab and fbptr and bpp:
        nbytes = width * height * bpp
        cap = min(nbytes, args.max_bytes) if nbytes else args.max_bytes
        print(f"[grab] reading {cap} of {nbytes} bytes from 0x{fbptr:08x} "
              f"(CPU stopped; ~{cap/560:.0f}s)")
        data = bytearray()
        cw = 8192
        while len(data) < cap:
            n = min(cw * 4, cap - len(data))
            a = fbptr + len(data)
            data += parse_mrd(cmd(f"mrd 0x{a:x} {n//4}", t=180))
            print(f"   {len(data)}/{cap}", flush=True)
        raw = os.path.join(OUTDIR, f"osd_fb_{ts}.bin")
        with open(raw, "wb") as f:
            f.write(data)
        report["raw"] = os.path.relpath(raw, OUTDIR)
        report["raw_bytes"] = len(data)
        print(f"[grab] -> {raw}")

    cmd(f"bpr 0x{args.bp:x}")
    print("[bpr] breakpoint removed")
    cmd("con")
    print("[con] camera resumed")

    jp = os.path.join(OUTDIR, f"osd_capture_{ts}.json")
    with open(jp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[done] {jp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
