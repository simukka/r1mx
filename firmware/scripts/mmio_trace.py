#!/usr/bin/env python3
"""
mmio_trace.py — Phase 3A of plans/working_camera_jtag_analysis.md.

READ-ONLY breakpoint-driven MMIO capture: set a HW breakpoint inside a driver,
single-step, and log every load/store — decoding each instruction from the IMAGE
(at pc-D_text, since live .text is not data-readable here) and resolving the
effective address from the LIVE registers. This is the only way to read device
registers on this camera (a peripheral page is mapped only in its driver's own
context; see firmware/reverse/build_32/camera_reports/cam-working-01/PHASE3_targets.md).

Default D_text=0x10180 (cam-working-01). camera_probe's auto-reloc can't run here
(.text is I-side-only), so D_text is passed explicitly.

SAFETY: read-only — only stop/con/rrd/mrd/bps..hw/bpremove/stp. HW breakpoints
only (no memory patching). Never resets. On a working camera, operator does any
power-cycle.

Usage (camera booted, agent_loop running in XMD):
  python3 firmware/scripts/mmio_trace.py --addr 0x001e9140 --steps 120 \\
      --label "sensor accessor FUN_001d8fc0"
"""
from __future__ import annotations
import argparse, csv, json, re, sys, time, bisect
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import xmd_rpc  # noqa: E402
import capstone  # noqa: E402
_MD = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_32 | capstone.CS_MODE_BIG_ENDIAN)

# EA classified as MMIO/peripheral (above DDR; DDR is ~0x0..0x10000000 incl stacks).
def is_mmio(ea):
    return ea >= 0x10000000 and ea < 0xfffff000

_FORBID = ("rst", "mwr", "rwr", "dow", "program", "erase")


class Bridge:
    def __init__(self, d, t): self.dir, self.timeout = d, t
    def rpc(self, c):
        for tok in re.split(r"[;\s]+", c.strip().lower()):
            if tok in _FORBID: raise PermissionError(f"refused: {c!r}")
        return xmd_rpc.rpc(c, dir_=self.dir, timeout=self.timeout)
    def alive(self):
        return "Debug Operation Not Supported" not in self.rpc("rrd")
    def regs(self):
        return {k: int(v, 16) for k, v in re.findall(
            r'(r\d+|pc|msr|lr|ctr):\s*([0-9A-Fa-f]+)', self.rpc("stop; set o [rrd]; set o"))}
    def word(self, a):
        m = re.search(r':\s+([0-9A-Fa-f]+)', self.rpc(f"set o [mrd 0x{a:x} 1]; set o"))
        return int(m.group(1), 16) if m else None
    def set_bp(self, a):
        out = self.rpc(f"bps 0x{a:x} hw"); m = re.search(r'\b(\d+)\b', out)
        return m.group(1) if m else None
    def clear_bp(self, bid, a):
        try: self.rpc(f"bpremove {bid if bid else hex(a)}")
        except Exception: pass
    def step(self): self.rpc("stp")
    def resume(self):
        try: self.rpc("con")
        except Exception: pass
    def run_to(self, addr, timeout):
        bid = self.set_bp(addr); self.rpc("con")
        dl = time.time() + timeout
        try:
            while time.time() < dl:
                out = self.rpc("rrd")
                if "Running" not in out and "ERROR" not in out:
                    return {k: int(v, 16) for k, v in re.findall(
                        r'(r\d+|pc|msr|lr|ctr):\s*([0-9A-Fa-f]+)', out)}
                time.sleep(0.3)
            return None
        finally:
            self.clear_bp(bid, addr)


def load_funcs(manifest):
    fa, fr = [], []
    for r in csv.DictReader(open(manifest)):
        try: a = int(r["addr"], 16)
        except (KeyError, ValueError): continue
        fa.append(a); fr.append((a, int(r.get("size") or 0), r["name"]))
    o = sorted(range(len(fa)), key=lambda i: fa[i])
    return [fa[i] for i in o], [fr[i] for i in o]


def s16(v): return v - 0x10000 if v >= 0x8000 else v


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--addr", required=True, help="live breakpoint address (hex)")
    ap.add_argument("--d-text", default="0x10180")
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--label", default="")
    ap.add_argument("--bp-timeout", type=float, default=25.0,
                    help="seconds to wait for the breakpoint to be hit")
    ap.add_argument("--image", default=str(
        _HERE.parent / "reverse/build_32/extracted/software.bin"))
    ap.add_argument("--manifest", default=str(
        _HERE.parent / "reverse/build_32/src/manifest.csv"))
    ap.add_argument("--bridge-dir", default=xmd_rpc.DEFAULT_DIR)
    ap.add_argument("--id", default="cam-working-01")
    ap.add_argument("--out", default=str(_HERE.parent / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    d_text = int(args.d_text, 16)
    addr = int(args.addr, 16)
    img = Path(args.image).read_bytes()
    fa, fr = load_funcs(args.manifest)
    def fname(img_a):
        i = bisect.bisect_right(fa, img_a) - 1
        if i < 0: return "?"
        a, s, n = fr[i]; return f"{n}+0x{img_a-a:x}" + ("(gap)" if s and img_a >= a+s else "")

    br = Bridge(args.bridge_dir, args.timeout if False else 30.0)
    try:
        if not br.alive():
            print("[!] no live debug link (XMD 'connect ppc hw' in the VM)."); return 2
    except Exception as e:
        print(f"[!] no agent ({e}); is agent_loop running?"); return 1

    print(f"[*] arming HW bp @ 0x{addr:08x} ({args.label or fname(addr-d_text)}); "
          f"waiting {args.bp_timeout:.0f}s for a hit ...")
    regs = br.run_to(addr, args.bp_timeout)
    if not regs:
        try:
            link = br.alive()
        except Exception:
            link = False
        if not link:
            print("[!] breakpoint NOT hit — the debug link is DEAD (camera powered\n"
                  "    off or JTAG dropped). Power the camera on and re-run\n"
                  "    'connect ppc hw' in the VM, then retry.")
            return 4
        print("[!] breakpoint NOT hit within timeout, but the link is live — this\n"
              "    code path is idle. The device likely needs to be active\n"
              "    (live preview / record / button press), then retry.")
        return 3
    print(f"[*] HIT. pc=0x{regs.get('pc',0):08x}  r3=0x{regs.get('r3',0):08x}  "
          f"r4=0x{regs.get('r4',0):08x}  r5=0x{regs.get('r5',0):08x}")

    trace, regs_at_hit = [], dict(regs)
    for _ in range(args.steps):
        regs = br.regs()
        pc = regs.get("pc", 0)
        off = pc - d_text
        ins_b = img[off:off+4] if 0 <= off < len(img)-4 else b""
        ins = next(_MD.disasm(ins_b, pc), None) if len(ins_b) == 4 else None
        if ins and ins.mnemonic.startswith(("lwz", "lbz", "lhz", "stw", "stb", "sth")):
            m = re.match(r'r\d+,\s*(-?0x[0-9a-f]+|-?\d+)\(r(\d+)\)', ins.op_str)
            if m:
                disp = int(m.group(1), 16) if "0x" in m.group(1) else int(m.group(1))
                ea = (regs.get(f"r{int(m.group(2))}", 0) + s16(disp)) & 0xffffffff
                if is_mmio(ea):
                    kind = "W" if ins.mnemonic.startswith("st") else "R"
                    val = br.word(ea)
                    rec = {"pc": f"0x{pc:08x}", "fn": fname(off), "op": ins.mnemonic,
                           "ea": f"0x{ea:08x}", "rw": kind,
                           "val": f"0x{val:08x}" if val is not None else "?"}
                    trace.append(rec)
                    print(f"    {kind} {rec['ea']}  {ins.mnemonic:5} {rec['val']}  @{rec['fn']}")
        br.step()
    br.resume()

    report = {"camera_id": args.id, "phase": "3A-mmio-trace",
              "timestamp": datetime.now().isoformat(timespec="seconds"),
              "bp_addr": f"0x{addr:08x}", "label": args.label,
              "d_text": f"0x{d_text:x}", "steps": args.steps,
              "regs_at_hit": {k: f"0x{v:08x}" for k, v in regs_at_hit.items()},
              "mmio": trace}
    outdir = Path(args.out) / args.id; outdir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "").replace("-", "")
    p = outdir / f"mmio_{addr:08x}_{stamp}.json"; p.write_text(json.dumps(report, indent=2))
    print(f"\n[*] {len(trace)} MMIO accesses -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
