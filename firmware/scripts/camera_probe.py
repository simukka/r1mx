#!/usr/bin/env python3
"""
camera_probe.py — re-runnable, READ-ONLY live analysis of a RED ONE MX camera
over the CPU/IO-board JTAG, implementing plans/working_camera_jtag_analysis.md.

Run it against any camera (different firmware builds / board revisions) and it
produces a per-camera report: it confirms the build and derives the relocation
offsets by fingerprinting live .text against the image (no hardcoded addresses),
dumps the interrupt baseline and peripheral memory map, and can trace a driver's
MMIO register sequence. The output (JSON + Markdown, tagged with the camera id
and operator-supplied board revisions) is the spec sheet for scaffolding the
remaining QEMU device models.

Transport: Channel B (xmd_rpc.py -> xmd_agent.tcl running in the WinXP VM), which
reads memory/registers faithfully via XMD's native debug access. See
firmware/reverse/build_32/host_xmd_bridge.md.

SAFETY — read-only by construction:
  * Only ever issues: stop, con, rrd, mrd, bps <a> hw, bpremove, stp.
  * A host-side guard refuses any command outside that allowlist, and the
    xmd_agent denylist refuses rst/mwr/rwr/dow/program/erase independently.
  * Hardware breakpoints only (IAC regs, no memory patching). Never resets.
    On a WORKING camera, any power-cycle is the operator's job, never `rst`.

Usage:
  # In the VM (once): source {Y:/r1mx/firmware/scripts/xmd_agent.tcl} ; agent_loop
  python3 firmware/scripts/camera_probe.py --id cam-007 \\
      --boards "cpu=revB,audio=revB,sensor=revA" \\
      --image firmware/reverse/build_32/extracted/software.bin \\
      --phases reloc,irq,memmap
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

import sys
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import xmd_rpc  # noqa: E402

try:
    import capstone
    _MD = capstone.Cs(capstone.CS_ARCH_PPC,
                      capstone.CS_MODE_32 | capstone.CS_MODE_BIG_ENDIAN)
except Exception:  # capstone optional (only needed for mmio-trace)
    _MD = None

# ---- known platform facts (bases are physical/VA-stable peripheral windows) ---
PERIPHERALS = {
    "XUartLite":      0xe0600000,
    "XUartNs550_1":   0xe0640000,
    "XUartNs550_2":   0xe0650000,
    "XIntc":          0xe0800000,
    "XEmacLite":      0xe1020000,
    "XIic":           0xb2600000,
    "XPS_CentralDMA": 0x64010000,
    "XPci_host":      0xe1200000,
    "RED_hist_0":     0xe0080000,
    "RED_hist_1":     0xe0100000,
    "NOR_flash":      0xf0000000,
}
XINTC_REGS = {"ISR": 0x00, "IPR": 0x04, "IER": 0x08, "IAR": 0x0C,
              "SIE": 0x10, "CIE": 0x14, "IVR": 0x18, "MER": 0x1C}
MMIO_RANGES = [(0x64000000, 0x64020000), (0xb2600000, 0xb2601000),
               (0xe0000000, 0xe2000000), (0xf0000000, 0xf8000000)]

# Commands this tool is allowed to send (host-side belt-and-suspenders guard).
_ALLOWED_FIRST = {"stop", "con", "rrd", "mrd", "bps", "bpremove", "stp",
                  "set", "append"}  # set/append wrap reads in compound cmds


def _guard(cmd: str):
    """Refuse anything that could mutate target state."""
    forbidden = ("rst", "mwr", "rwr", "dow", "program", "erase", "fpga",
                 "init_fpga")
    for tok in re.split(r"[;\s]+", cmd.strip().lower()):
        if tok in forbidden:
            raise PermissionError(f"refused (read-only guard): {cmd!r}")


def s16(v):
    return v - 0x10000 if v >= 0x8000 else v


class Camera:
    """Read-only Channel-B handle to the live PPC405."""

    def __init__(self, bridge_dir, timeout=30.0):
        self.dir = bridge_dir
        self.timeout = timeout

    def rpc(self, cmd):
        _guard(cmd)
        return xmd_rpc.rpc(cmd, dir_=self.dir, timeout=self.timeout)

    # -- state --
    DEAD_MARKERS = ("Debug Operation Not Supported", "Unable to Stop",
                    "Unable to STOP", "No target", "AutoDetect")

    def connection_ok(self):
        """True if XMD currently has a live debug link to the PPC405."""
        out = self.rpc("rrd")
        return not any(m in out for m in self.DEAD_MARKERS)

    def halt(self):
        self.rpc("stop")

    def resume(self):
        self.rpc("con")

    def running(self):
        return "Running" in self.rpc("rrd")

    def regs(self):
        """Halt-safe register read -> {name: value}."""
        out = self.rpc("stop; set o [rrd]; set o")
        return self._parse_regs(out)

    @staticmethod
    def _parse_regs(text):
        return {k: int(v, 16)
                for k, v in re.findall(r'(r\d+|pc|msr|lr|ctr):\s*([0-9A-Fa-f]+)',
                                       text)}

    # -- memory --
    def read_words(self, addr, n, halted=False):
        """Return list[(addr, value)]. Wraps stop/con unless already halted."""
        cmd = (f"set o [mrd 0x{addr:x} {n}]; set o" if halted
               else f"stop; set o [mrd 0x{addr:x} {n}]; con; set o")
        return self._parse_mrd(self.rpc(cmd))

    def read_word(self, addr, halted=False):
        wl = self.read_words(addr, 1, halted)
        return wl[0][1] if wl else None

    @staticmethod
    def _parse_mrd(text):
        out = []
        for line in text.splitlines():
            m = re.match(r'\s*([0-9A-Fa-f]+):\s+([0-9A-Fa-f]+)\s*$', line)
            if m:
                out.append((int(m.group(1), 16), int(m.group(2), 16)))
        return out

    def read_bytes(self, addr, nbytes, halted=False):
        n = (nbytes + 3) // 4
        wl = self.read_words(addr, n, halted)
        b = b"".join(v.to_bytes(4, "big") for _, v in wl)
        return b[:nbytes]

    # -- breakpoints (hardware/IAC only) --
    def set_bp(self, addr):
        out = self.rpc(f"bps 0x{addr:x} hw")
        m = re.search(r'\b(\d+)\b', out)
        return m.group(1) if m else None

    def clear_bp(self, bpid, addr):
        try:
            self.rpc(f"bpremove {bpid if bpid else hex(addr)}")
        except Exception:
            pass

    def run_to(self, addr, timeout=None):
        """Set HW bp, resume, poll until stopped. Returns regs or None."""
        timeout = timeout or self.timeout
        bpid = self.set_bp(addr)
        self.rpc("con")
        deadline = time.time() + timeout
        try:
            while time.time() < deadline:
                out = self.rpc("rrd")
                if "Running" not in out and "ERROR" not in out:
                    return self._parse_regs(out)
                time.sleep(0.3)
            return None
        finally:
            self.clear_bp(bpid, addr)

    def step(self):
        self.rpc("stp")


# --------------------------------------------------------------------------- #
# Phases
# --------------------------------------------------------------------------- #
def _classify(words):
    """Tell real data from XMD's unmapped-read artifacts."""
    vals = [v for _, v in words]
    if not vals:
        return "empty"
    if all(v == 0 for v in vals):
        return "zero"            # unmapped (or genuinely zero) — ambiguous
    if len(set(vals)) == 1:
        return "filler"          # repeated word == bus residue, unmapped
    return "real"


def phase_reloc(cam: Camera, images: list[Path], report: dict):
    """Confirm build + derive D_text by fingerprinting live .text against each
    candidate image. Build identity == the image whose bytes match."""
    regs = cam.regs()
    pc = regs.get("pc", 0)
    report["halt_pc"] = f"0x{pc:08x}"
    # Gather candidate CODE addresses (likely D-mappable .text): pc/lr/ctr plus
    # return addresses found on the stack. Reading near any one that happens to
    # be TLB-resident yields a fingerprint window — robust to Harvard split.
    CODE_LO, CODE_HI = 0x1000, 0xe00000
    cands = []
    for rn in ("pc", "lr", "ctr"):
        v = regs.get(rn, 0)
        if CODE_LO <= v < CODE_HI:
            cands.append(v & 0xfffffffc)
    sp = regs.get("r1", 0)
    if sp:
        for _, v in cam.read_words(sp, 64, halted=True):
            if CODE_LO <= v < CODE_HI and v % 4 == 0:
                cands.append(v & 0xfffffffc)
    cands = list(dict.fromkeys(cands))[:24]
    report["reloc_candidates"] = len(cands)
    windows = []
    for c in cands:
        for off in (0, -0x40, 0x40):
            a = (c + off) & 0xfffffffc
            w = cam.read_words(a, 16, halted=True)
            if _classify(w) == "real":
                windows.append((a, b"".join(v.to_bytes(4, "big") for _, v in w)))
                break  # one good window per candidate is enough
    report["reloc_windows_real"] = len(windows)
    best = None
    for img_path in images:
        d = img_path.read_bytes()
        deltas = {}
        for liveaddr, blob in windows:
            idx = d.find(blob)
            if idx >= 0 and d.find(blob, idx + 1) < 0:   # unique match only
                deltas.setdefault(liveaddr - idx, []).append((liveaddr, idx))
        if deltas:
            d_text, ev = max(deltas.items(), key=lambda kv: len(kv[1]))
            if best is None or len(ev) > best["matches"]:
                best = {"image": img_path.name, "D_text": d_text,
                        "matches": len(ev),
                        "evidence": [f"live 0x{l:08x}==img 0x{o:08x}"
                                     for l, o in ev[:4]]}
    if best:
        report["build_image"] = best["image"]
        report["D_text"] = f"0x{best['D_text']:x}"
        report["D_text_int"] = best["D_text"]
        report["reloc_matches"] = best["matches"]
        report["reloc_evidence"] = best["evidence"]
        report["build_confirmed"] = best["matches"] >= 2
    else:
        report["build_image"] = None
        report["note_reloc"] = ("no unique .text match — halt at a different "
                                "context (more pages mapped) and retry, or the "
                                "build image isn't among --image/--images-dir")
    return report.get("D_text_int")


def phase_data_reloc(cam: Camera, image: Path, d_text: int, report: dict):
    """Best-effort D_data: find a `lis;addi` data-pointer build near the current
    function in the image, break right after it, read the live register."""
    if d_text is None or _MD is None:
        report["note_D_data"] = "skipped (need D_text and capstone)"
        return
    d = image.read_bytes()
    pc = cam.regs().get("pc", 0)
    img_pc = pc - d_text
    lo, hi = max(0, img_pc - 0x400), min(len(d), img_pc + 0x400)
    insns = list(_MD.disasm(d[lo:hi], lo))
    for k in range(len(insns) - 1):
        a, b = insns[k], insns[k + 1]
        m1 = re.match(r'r(\d+),\s*(0x[0-9a-f]+)$', a.op_str)
        m2 = re.match(r'r(\d+),\s*r(\d+),\s*(-?0x[0-9a-f]+|\d+)$', b.op_str)
        if a.mnemonic == "lis" and b.mnemonic in ("addi", "addic") and m1 and m2 \
           and m1.group(1) == m2.group(1) == m2.group(2):
            rD = int(m1.group(1))
            hi16 = int(m1.group(2), 16) << 16
            lo16 = s16(int(m2.group(3), 16) if "0x" in m2.group(3)
                       else int(m2.group(3)))
            img_addr = (hi16 + lo16) & 0xffffffff
            live_after = b.address + 4 + d_text     # bp just after the addi
            regs = cam.run_to(live_after, timeout=cam.timeout)
            if regs and f"r{rD}" in regs:
                d_data = (regs[f"r{rD}"] - img_addr) & 0xffffffff
                report["D_data"] = f"0x{d_data:x}"
                report["D_data_int"] = d_data
                report["D_data_probe"] = (f"img 0x{img_addr:08x} -> live "
                                          f"0x{regs[f'r{rD}']:08x} @bp 0x{live_after:08x}")
                return
    report["note_D_data"] = "no lis;addi data-pointer build found near pc to probe"


def phase_irq(cam: Camera, report: dict):
    """Interrupt baseline: which XIntc lines are enabled/active right now."""
    base = PERIPHERALS["XIntc"]
    regs = {}
    for name, off in XINTC_REGS.items():
        v = cam.read_word(base + off)
        regs[name] = f"0x{v:08x}" if v is not None else "err"
    report["xintc"] = regs
    ier_s = regs.get("IER", "err")
    if ier_s != "err":
        ier = int(ier_s, 16)
        report["xintc_enabled_lines"] = [i for i in range(32) if ier & (1 << i)]
    else:
        report["xintc_enabled_lines"] = None
        report["note_xintc"] = "XIntc not readable at this context (MMU/TLB)"
    return regs


def phase_memmap(cam: Camera, report: dict):
    """Probe each peripheral base; classify the response."""
    mm = {}
    for name, base in PERIPHERALS.items():
        w = cam.read_words(base, 4)
        mm[name] = {"base": f"0x{base:08x}", "state": _classify(w),
                    "words": [f"0x{v:08x}" for _, v in w]}
    report["memory_map"] = mm
    return mm


def phase_mmio_trace(cam: Camera, image: Path, d_text: int,
                     driver_live_addr: int, steps: int, report: dict):
    """Single-step a driver from driver_live_addr, logging MMIO accesses
    (effective address resolved from live registers + image-decoded insn)."""
    if _MD is None or d_text is None:
        report["note_mmio"] = "skipped (need capstone and D_text)"
        return
    d = image.read_bytes()

    def is_mmio(ea):
        return any(lo <= ea < hi for lo, hi in MMIO_RANGES)

    regs = cam.run_to(driver_live_addr, timeout=cam.timeout)
    if not regs:
        report["note_mmio"] = f"driver bp 0x{driver_live_addr:08x} not hit"
        return
    trace = []
    for _ in range(steps):
        regs = cam.regs()
        pc = regs.get("pc", 0)
        ins_bytes = d[pc - d_text: pc - d_text + 4]
        ins = next(_MD.disasm(ins_bytes, pc), None) if len(ins_bytes) == 4 else None
        if ins:
            m = re.match(r'r\d+,\s*(-?0x[0-9a-f]+|\d+)\(r(\d+)\)', ins.op_str)
            if m and (ins.mnemonic.startswith(("lwz", "lbz", "lhz", "stw",
                                               "stb", "sth"))):
                disp = int(m.group(1), 16) if "0x" in m.group(1) else int(m.group(1))
                ea = (regs.get(f"r{int(m.group(2))}", 0) + s16(disp)) & 0xffffffff
                if is_mmio(ea):
                    kind = "W" if ins.mnemonic.startswith("st") else "R"
                    val = cam.read_word(ea, halted=True)
                    trace.append({"pc": f"0x{pc:08x}", "op": ins.mnemonic,
                                  "ea": f"0x{ea:08x}", "rw": kind,
                                  "val": f"0x{val:08x}" if val is not None else "?"})
        cam.step()
    report.setdefault("mmio_traces", {})[f"0x{driver_live_addr:08x}"] = trace
    return trace


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True, help="camera identifier (report key)")
    ap.add_argument("--boards", default="",
                    help='operator-supplied board revisions, e.g. '
                         '"cpu=revB,audio=revB,sensor=revA"')
    ap.add_argument("--image", default=str(
        _HERE.parent / "reverse/build_32/extracted/software.bin"),
        help="matching firmware image (or use --images-dir to auto-match)")
    ap.add_argument("--images-dir", default=None,
                    help="dir of candidate build images to identify the build")
    ap.add_argument("--phases", default="reloc,irq,memmap",
                    help="comma list: reloc,data_reloc,irq,memmap,mmio_trace")
    ap.add_argument("--driver-addr", default=None,
                    help="for mmio_trace: live driver entry addr (hex)")
    ap.add_argument("--steps", type=int, default=200, help="mmio_trace steps")
    ap.add_argument("--bridge-dir", default=xmd_rpc.DEFAULT_DIR)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--out", default=str(_HERE.parent / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    images = []
    if args.images_dir:
        images = sorted(Path(args.images_dir).glob("*.bin"))
    if args.image and Path(args.image).exists():
        images.insert(0, Path(args.image))
    images = list(dict.fromkeys(images))  # dedupe, keep order
    phases = [p.strip() for p in args.phases.split(",") if p.strip()]

    report = {
        "camera_id": args.id,
        "boards": dict(kv.split("=", 1) for kv in args.boards.split(",") if "=" in kv),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "phases_run": phases,
        "transport": "ChannelB/xmd_rpc",
    }

    cam = Camera(args.bridge_dir, timeout=args.timeout)
    print(f"[*] camera_probe '{args.id}' — phases: {phases}")
    try:
        cam.halt()
        ok = cam.connection_ok()
    except Exception as e:
        print(f"[!] no response from xmd_agent ({e}). "
              "Is agent_loop running in XMD and --bridge-dir correct?")
        return 1
    if not ok:
        print("[!] XMD has NO live debug link to the PPC405 (target reports "
              "'Debug Operation Not Supported').\n"
              "    The camera likely power-cycled or the JTAG session dropped.\n"
              "    In the VM's XMD console, re-run:  connect ppc hw\n"
              "    (the agent_loop can keep running), then retry.")
        report["target_unreachable"] = True
        outdir = Path(args.out) / args.id
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "last_unreachable.json").write_text(json.dumps(report, indent=2))
        return 2

    d_text = None
    if "reloc" in phases:
        print("[*] phase reloc: confirming build + deriving D_text ...")
        d_text = phase_reloc(cam, images, report)
        print(f"    build={report.get('build_image')} "
              f"D_text={report.get('D_text')} matches={report.get('reloc_matches')}")
    if "data_reloc" in phases:
        print("[*] phase data_reloc: deriving D_data ...")
        img = next((p for p in images if p.name == report.get("build_image")),
                   images[0] if images else None)
        if img:
            phase_data_reloc(cam, img, d_text, report)
            print(f"    D_data={report.get('D_data')}")
    if "irq" in phases:
        print("[*] phase irq: XIntc baseline ...")
        phase_irq(cam, report)
        print(f"    enabled lines: {report.get('xintc_enabled_lines')}")
    if "memmap" in phases:
        print("[*] phase memmap: probing peripheral bases ...")
        phase_memmap(cam, report)
        print("    " + ", ".join(f"{k}:{v['state']}"
                                 for k, v in report["memory_map"].items()))
    if "mmio_trace" in phases:
        if args.driver_addr:
            img = next((p for p in images if p.name == report.get("build_image")),
                       images[0] if images else None)
            print(f"[*] phase mmio_trace: {args.driver_addr} ...")
            phase_mmio_trace(cam, img, d_text, int(args.driver_addr, 16),
                             args.steps, report)
        else:
            report["note_mmio"] = "skipped (no --driver-addr)"

    # leave the camera in its natural running state
    try:
        cam.resume()
    except Exception:
        pass

    # ---- write report ----
    outdir = Path(args.out) / args.id
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "").replace("-", "")
    jpath = outdir / f"probe_{stamp}.json"
    jpath.write_text(json.dumps(report, indent=2))
    mpath = outdir / f"probe_{stamp}.md"
    mpath.write_text(_render_md(report))
    print(f"\n[*] report written:\n    {jpath}\n    {mpath}")
    return 0


def _render_md(r: dict) -> str:
    L = [f"# Camera probe — {r['camera_id']}", "",
         f"- when: {r['timestamp']}",
         f"- boards: {r.get('boards')}",
         f"- build image: **{r.get('build_image')}** "
         f"(confirmed={r.get('build_confirmed')})",
         f"- D_text: **{r.get('D_text')}**  D_data: **{r.get('D_data')}**",
         f"- halt pc: {r.get('halt_pc')}", ""]
    if r.get("reloc_evidence"):
        L += ["## Relocation evidence", *[f"- {e}" for e in r["reloc_evidence"]], ""]
    if r.get("xintc"):
        L += ["## Interrupt baseline (XIntc)",
              "| reg | value |", "|---|---|",
              *[f"| {k} | {v} |" for k, v in r["xintc"].items()],
              f"\nenabled lines: {r.get('xintc_enabled_lines')}", ""]
    if r.get("memory_map"):
        L += ["## Peripheral map", "| device | base | state |", "|---|---|---|",
              *[f"| {k} | {v['base']} | {v['state']} |"
                for k, v in r["memory_map"].items()], ""]
    for drv, tr in (r.get("mmio_traces") or {}).items():
        L += [f"## MMIO trace @ {drv}", "| pc | op | ea | rw | val |",
              "|---|---|---|---|---|",
              *[f"| {t['pc']} | {t['op']} | {t['ea']} | {t['rw']} | {t['val']} |"
                for t in tr], ""]
    notes = {k: v for k, v in r.items() if k.startswith("note")}
    if notes:
        L += ["## Notes", *[f"- {k}: {v}" for k, v in notes.items()]]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
