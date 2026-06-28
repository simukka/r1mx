#!/usr/bin/env python3
"""Does FlashVx (the OSD UI engine) come up in QEMU, and does it blit?

Arms HW breakpoints at the FlashVx ctor and FrameBufferBlit, boots, and reports
every hit (with the object geometry on a blit). This tells us whether the OSD
render path is reachable at all in QEMU, or whether it's dormant (no UI client /
boot stalls before UI init).

Addresses are objdump == QEMU live (base 0x10000, D=0):
  0x14f03c  FlashVx::FlashVx ctor  (_ZN7FlashVxC1E9FlashRectPKc)
  0x14f35c  FlashVx::FrameBufferBlit
"""
import argparse, os, struct, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp import RSP  # noqa: E402

CTOR = 0x14f03c
BLIT = 0x14f35c


def read_obj(t, this):
    f = t.read_mem(this + 0x8c, 0x18)
    rect = struct.unpack(">4I", f[:16])
    fbptr, bpp = struct.unpack(">2I", f[16:24])
    return rect, fbptr, bpp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=1234)
    ap.add_argument("--deadline", type=int, default=900, help="wall seconds total")
    ap.add_argument("--per", type=int, default=120, help="per-cont timeout")
    args = ap.parse_args()

    t = RSP(port=args.port).connect()
    t.set_bp(CTOR, hw=True)
    t.set_bp(BLIT, hw=True)
    print(f"[arm] ctor@0x{CTOR:08x} blit@0x{BLIT:08x}; booting (deadline {args.deadline}s)")
    start = time.time()
    hits = 0
    while time.time() - start < args.deadline:
        remaining = args.deadline - (time.time() - start)
        try:
            stop = t.cont(timeout=min(args.per, remaining))
        except Exception:
            print(f"[..] no hit yet ({time.time()-start:.0f}s elapsed)")
            continue
        regs = t.regs()
        pc = regs.get("pc", 0)
        hits += 1
        if pc == CTOR:
            this = regs.get("r3", 0)
            print(f"[ctor] t={time.time()-start:.0f}s this=0x{this:08x} (FlashVx instantiated)")
        elif pc == BLIT:
            this = regs.get("r3", 0)
            try:
                rect, fbptr, bpp = read_obj(t, this)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                head = t.read_mem(fbptr, 0x40) if fbptr else b""
                nz = sum(1 for b in head if b)
                print(f"[BLIT] t={time.time()-start:.0f}s this=0x{this:08x} "
                      f"rect={[hex(x) for x in rect]} fb=0x{fbptr:08x} bpp={bpp} "
                      f"{w}x{h}  head_nz={nz}/64 head={head[:16].hex()}")
            except Exception as e:
                print(f"[BLIT] this=0x{this:08x} obj read failed: {e}")
            break  # got what we came for
        else:
            print(f"[?] stop at pc=0x{pc:08x} stop={stop.strip()[:20]}")
        if hits > 50:
            print("[!] >50 hits; stopping")
            break
    else:
        print(f"[timeout] no blit within {args.deadline}s (hits={hits})")
    t.clear_bp(CTOR, hw=True)
    t.clear_bp(BLIT, hw=True)
    t.send("c")
    return 0


if __name__ == "__main__":
    sys.exit(main())
