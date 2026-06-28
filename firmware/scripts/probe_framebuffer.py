#!/usr/bin/env python3
"""Read-only live-camera frame-buffer + display-gate probe (Channel A / :2345).

On a *running* working camera the display double-buffers and the display-ready
RAM flags live in mapped DDR, so they are readable at idle via `m` (no
breakpoint, no writes). This grabs:

  * 0x840000 / 0x890000  display double-buffers (0x50000 = 327680 B each)
  * the display-ready gate words (0xea0de4, 0xea0de8) + a small window

It dumps the raw buffers, computes coarse structure stats (byte entropy +
row-stride autocorrelation) so we can tell a real frame from noise/zeros, and
writes a JSON+MD report into camera_reports/cam-working-01/.

READ-ONLY: uses rsp.py with allow_write defaulted off; never sets a breakpoint.
"""
import argparse, json, math, os, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp import RSP  # noqa: E402

FB = [("fb0", 0x840000, 0x50000), ("fb1", 0x890000, 0x50000)]
FLAGS = [0xea0de4, 0xea0de8]
REPORT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "reverse", "build_32", "camera_reports", "cam-working-01")


def chunked_read(t, addr, length, chunk=0x400):
    out = bytearray()
    off = 0
    while off < length:
        n = min(chunk, length - off)
        out += t.read_mem(addr + off, n)
        off += n
    return bytes(out)


def entropy(b):
    if not b:
        return 0.0
    hist = [0] * 256
    for x in b:
        hist[x] += 1
    h = 0.0
    n = len(b)
    for c in hist:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def row_autocorr(b, stride):
    """Mean abs-diff between consecutive `stride`-byte rows. Low => structured
    (rows resemble neighbours, i.e. a real image); high/0x80-ish => noise."""
    rows = len(b) // stride
    if rows < 2:
        return None
    diffs = []
    for r in range(1, min(rows, 64)):
        a = b[(r - 1) * stride:r * stride]
        c = b[r * stride:(r + 1) * stride]
        diffs.append(sum(abs(x - y) for x, y in zip(a, c)) / stride)
    return sum(diffs) / len(diffs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345)
    ap.add_argument("--outdir", default=REPORT_DIR)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    t = RSP(host=args.host, port=args.port).connect()
    try:
        _probe(t, args, ts)
    finally:
        try:
            t.cont()  # resume the camera; never leave it halted (watchdog)
            print("[resume] core continued")
        except Exception as e:
            print(f"[warn] resume failed: {e}")


def _probe(t, args, ts):
    t.interrupt()  # halt (idempotent if already halted); liveness check
    regs = t.regs()
    print(f"[ok] live PC=0x{regs.get('pc', 0):08x}")

    report = {"ts": ts, "pc": regs.get("pc"), "buffers": [], "flags": {}}

    for name, addr, length in FB:
        try:
            data = chunked_read(t, addr, length)
        except Exception as e:
            print(f"[fail] {name}@0x{addr:08x}: {e}")
            report["buffers"].append({"name": name, "addr": addr, "error": str(e)})
            continue
        raw_path = os.path.join(args.outdir, f"{name}_{ts}.bin")
        with open(raw_path, "wb") as f:
            f.write(data)
        nz = sum(1 for x in data if x)
        ent = entropy(data)
        # try a few plausible row strides for a ~preview-size buffer
        ac = {str(s): row_autocorr(data, s) for s in (640, 720, 1280, 1024)}
        info = {"name": name, "addr": addr, "len": length,
                "nonzero_frac": round(nz / len(data), 4),
                "entropy_bits": round(ent, 3),
                "row_autocorr": {k: (round(v, 2) if v is not None else None)
                                 for k, v in ac.items()},
                "raw": os.path.relpath(raw_path, args.outdir)}
        report["buffers"].append(info)
        print(f"[{name}] @0x{addr:08x} nz={info['nonzero_frac']} "
              f"H={info['entropy_bits']}b autocorr={info['row_autocorr']}")

    win = chunked_read(t, 0xea0dc0, 0x80)
    report["flag_window_0xea0dc0"] = win.hex()
    for fa in FLAGS:
        v = t.read_word(fa)
        report["flags"][hex(fa)] = v
        print(f"[flag] 0x{fa:08x} = 0x{v:08x}")

    jpath = os.path.join(args.outdir, f"framebuffer_{ts}.json")
    with open(jpath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[done] report -> {jpath}")


if __name__ == "__main__":
    main()
