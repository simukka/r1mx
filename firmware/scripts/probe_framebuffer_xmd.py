#!/usr/bin/env python3
"""Read-only bulk frame-buffer capture over Channel B (file-queue / mrd).

Channel A (RSP) is unreachable through the VBox NAT (stub bound to guest
loopback), but the file-queue agent (xmd_agent.tcl `agent_loop`) is live, so we
pull DDR over `mrd`. The display buffers are static at idle (verified), so a slow
serial scan does not tear.

  python3 probe_framebuffer_xmd.py --addr 0x840000 --len 0x50000 --out fb0.bin

READ-ONLY: only issues `mrd`; the agent denylist refuses any write.
"""
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xmd_rpc import rpc, parse_mrd  # noqa: E402


def capture(addr, length, out, chunk_words=8192, timeout=180):
    total = 0
    got = bytearray()
    nwords = length // 4
    t0 = time.time()
    while total < nwords:
        n = min(chunk_words, nwords - total)
        a = addr + total * 4
        txt = rpc(f"mrd 0x{a:x} {n}", timeout=timeout)
        b = parse_mrd(txt)
        if len(b) != n * 4:
            print(f"[warn] @0x{a:x} expected {n*4} got {len(b)} bytes")
        got += b
        total += n
        el = time.time() - t0
        print(f"  {total*4}/{length} bytes  ({len(got)/max(el,1e-9):.0f} B/s)",
              flush=True)
        with open(out, "wb") as f:   # incremental save (resumable inspection)
            f.write(got)
    print(f"[done] {len(got)} bytes -> {out} in {time.time()-t0:.0f}s")
    return bytes(got)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--addr", type=lambda x: int(x, 0), default=0x840000)
    ap.add_argument("--len", type=lambda x: int(x, 0), default=0x50000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk", type=int, default=8192)
    args = ap.parse_args()
    capture(args.addr, args.len, args.out, args.chunk)


if __name__ == "__main__":
    main()
