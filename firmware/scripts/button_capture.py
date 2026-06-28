#!/usr/bin/env python3
"""
button_capture.py — interactive, READ-ONLY capture of physical control events
(buttons, the multi-axis nav switch, and the REC/OK LEDs) on a live RED ONE MX,
so they can be modelled in QEMU. Implements the "physical controls" phase of
plans/working_camera_jtag_analysis.md.

How it works (and WHY this way)
-------------------------------
On this camera there is NO memory-mapped GPIO: re_reference.md notes `xgpio.c`
is absent and GPIO expansion is done with **PCA9698 I2C I/O-expanders driven by
the XIic driver (0xb2600000)**. So a button is not a register you can poll — its
state arrives over I2C and the firmware caches the *decoded* state in DDR.

Therefore the only truly read-only way to observe a press is to **diff DDR**
across a held button: snapshot a candidate RAM window, have the operator press &
hold, snapshot again, diff. The changed bit is the software-visible button state.
We deliberately do NOT read XIic data/status registers directly — reading an I2C
RX-FIFO or status register has SIDE EFFECTS (pops the FIFO / clears flags) and
would corrupt the live driver. DDR reads have no side effects.

The flow is interactive: it prompts the operator to press/hold/release each
control and confirm with Enter, then reports, per control:
  window address, byte offset, bit(s), polarity, and whether release reverted it.
The LEDs are PCA9698 *outputs*: same diff, but the operator drives the camera
between LED-off and LED-on states.

Soft power button
-----------------
The power button is a SOFT button: a press hands a shutdown/standby event to the
firmware, which may power the camera down and END the JTAG session. It is
therefore opt-in (`--include-power`), TAP-only (never hold), and warned. Capture
it last.

Output: per-camera JSON + Markdown under
firmware/reverse/build_32/camera_reports/<id>/buttons_*.{json,md} — the spec for
the QEMU PCA9698/expander model and button-injection wiring.

SAFETY: read-only by construction — reuses camera_probe.Camera (host-side
allowlist guard + xmd_agent denylist; HW breakpoints only; never resets). Only
DDR/word reads are issued; no peripheral FIFO is touched.

Usage
-----
  # In the VM once:  source {Y:/r1mx/firmware/scripts/xmd_agent.tcl} ; agent_loop

  # Step 1 — auto-locate the button-state DDR global (hold one reference button
  # across rounds while sweeping a bounded region; prints --watch windows to use):
  python3 firmware/scripts/button_capture.py --id cam-007 --auto-locate \
      --region 0x010d0000:0x4000 --ref-control record_left --rounds 4

  # Step 2 — capture every control by diffing the located window(s):
  python3 firmware/scripts/button_capture.py --id cam-007 \
      --boards "cpu=revB,ui=revA,sd=revA" \
      --watch 0x010d0038:0x14 \
      --controls record_left,b1,b2,ui_a,ui_b,ui_c,select_press \
      --leds rec,ok
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from camera_probe import Camera  # noqa: E402  (reuse the read-only handle)


# --- control inventory (operator-facing names -> where it lives / notes) ------
# board: where the switch is wired; prog: user-programmable; power: soft-power.
CONTROLS = {
    # Left side, wired to the SD-card board
    "record_left": dict(board="sd", label="Record (left side)"),
    "b1":          dict(board="sd", label="Button 1 (programmable)", prog=True),
    "b2":          dict(board="sd", label="Button 2 (programmable)", prog=True),
    # Back "UI board"
    "ui_a":        dict(board="ui", label="A (programmable?)", prog=True),
    "ui_b":        dict(board="ui", label="B (programmable?)", prog=True),
    "ui_c":        dict(board="ui", label="C (programmable?)", prog=True),
    "sensor":      dict(board="ui", label="Sensor"),
    "exit":        dict(board="ui", label="Exit"),
    "video":       dict(board="ui", label="Video"),
    # Select = multi-axis nav switch: 4 directions + center press
    "select_up":    dict(board="ui", label="Select toggle: Up"),
    "select_down":  dict(board="ui", label="Select toggle: Down"),
    "select_left":  dict(board="ui", label="Select toggle: Left"),
    "select_right": dict(board="ui", label="Select toggle: Right"),
    "select_press": dict(board="ui", label="Select: center press"),
    "undo":        dict(board="ui", label="Undo"),
    "system":      dict(board="ui", label="System"),
    "record_ui":   dict(board="ui", label="Record (UI board)"),
    "previous":    dict(board="ui", label="Previous"),
    "backwards":   dict(board="ui", label="Backwards"),
    "play":        dict(board="ui", label="Play"),
    "forwards":    dict(board="ui", label="Forwards"),
    "next":        dict(board="ui", label="Next"),
    # Soft power — special-cased
    "power":       dict(board="?", label="Power (SOFT)", power=True),
}
LEDS = {
    "rec": "REC LED (next to LCD)",
    "ok":  "OK LED (next to LCD)",
}


def parse_window(spec: str):
    a, _, l = spec.partition(":")
    return int(a, 0), (int(l, 0) if l else 0x100)


def snapshot(cam: Camera, windows):
    """Read each window once -> {base: bytes}. DDR reads only (no side effects)."""
    snap = {}
    for base, length in windows:
        snap[base] = cam.read_bytes(base, length)
    return snap


def diff_snaps(a, b):
    """List per-byte changes: (addr, old, new, set_bits, cleared_bits)."""
    out = []
    for base in a:
        ba, bb = a[base], b.get(base, b"")
        for i in range(min(len(ba), len(bb))):
            if ba[i] != bb[i]:
                old, new = ba[i], bb[i]
                setb = [k for k in range(8) if (new & ~old) & (1 << k)]
                clrb = [k for k in range(8) if (old & ~new) & (1 << k)]
                out.append((base + i, old, new, setb, clrb))
    return out


def snapshot_region(cam: Camera, base: int, length: int, chunk_words: int):
    """Read [base, base+length) as {addr: byte}. Halts ONCE for the whole sweep
    then resumes, so the firmware runs (and keeps polling the I2C expanders)
    between snapshots. DDR reads only — no side effects."""
    d = {}
    cam.halt()
    try:
        a, end = base, base + length
        while a < end:
            n = min(chunk_words, (end - a + 3) // 4)
            for wa, v in cam.read_words(a, n, halted=True):
                for k in range(4):                 # big-endian byte order
                    d[wa + k] = (v >> (8 * (3 - k))) & 0xff
            a += n * 4
    finally:
        cam.resume()
    return d


def changed_bytes(a: dict, b: dict):
    """Addresses present in both snapshots whose byte value differs -> {addr:(old,new)}."""
    return {addr: (a[addr], b[addr]) for addr in a
            if addr in b and a[addr] != b[addr]}


def winnow(rounds_changes, max_distinct=1):
    """Given a list of per-round {addr:(released,pressed)} dicts, keep only the
    addresses that look like a clean on/off bit:
      * changed in EVERY round,
      * the pressed value-set and released value-set are DISJOINT, and
      * each set has at most `max_distinct` value(s) across all rounds.
    A real momentary-button bit has exactly one pressed and one released value
    (1/1); a free-running counter/timer accumulates many distinct values and is
    rejected — that stability test is what beats the constant DDR churn.
    Returns {addr: {pressed, released}}."""
    acc = None
    for ch in rounds_changes:
        if acc is None:
            acc = {addr: {"released": {o}, "pressed": {n}}
                   for addr, (o, n) in ch.items()}
            continue
        nxt = {}
        for addr, (o, n) in ch.items():
            if addr in acc:                        # must change every round
                acc[addr]["released"].add(o)
                acc[addr]["pressed"].add(n)
                nxt[addr] = acc[addr]
        acc = nxt
    if not acc:
        return {}
    return {addr: v for addr, v in acc.items()
            if len(v["pressed"]) <= max_distinct
            and len(v["released"]) <= max_distinct
            and v["pressed"].isdisjoint(v["released"])}


def suggest_windows(addrs, pad=0x8):
    """Group found byte addresses into compact --watch windows (word-aligned, padded)."""
    if not addrs:
        return []
    addrs = sorted(addrs)
    groups, start, prev = [], addrs[0], addrs[0]
    for a in addrs[1:]:
        if a - prev <= pad * 2:
            prev = a
        else:
            groups.append((start, prev)); start = prev = a
    groups.append((start, prev))
    out = []
    for lo, hi in groups:
        base = (lo - pad) & ~3
        length = ((hi + 1 + pad - base) + 3) & ~3
        out.append((base, length))
    return out


def auto_locate(cam: Camera, base: int, length: int, chunk: int, rounds: int,
                ref_label: str, report: dict):
    """Find the DDR global that mirrors button state: hold a reference button
    across several press/release rounds, sweep the region each round, keep only
    bytes that toggle consistently with the button. Returns suggested windows."""
    print(f"\n[auto-locate] reference control: {ref_label}")
    print(f"    sweeping 0x{base:08x}..0x{base + length:08x} "
          f"({length} bytes) for {rounds} round(s)")
    if length > 0x40000:
        print("    [i] large region — each round re-reads it over Channel B; "
              "consider a tighter --region for speed.")
    changes = []
    for r in range(1, rounds + 1):
        if not ask(f"round {r}/{rounds}: make sure {ref_label} is RELEASED, then Enter"):
            break
        rel = snapshot_region(cam, base, length, chunk)
        if not ask(f"round {r}/{rounds}: press and HOLD {ref_label}, then Enter"):
            break
        prs = snapshot_region(cam, base, length, chunk)
        ch = changed_bytes(rel, prs)
        changes.append(ch)
        print(f"    round {r}: {len(ch)} byte(s) changed on hold")
    found = winnow(changes)
    windows = suggest_windows(found.keys())
    report["auto_locate"] = {
        "ref_control": ref_label,
        "region": f"0x{base:08x}:0x{length:x}",
        "rounds": len(changes),
        "found": [
            {"addr": f"0x{a:08x}",
             "released": sorted(f"0x{x:02x}" for x in v["released"]),
             "pressed": sorted(f"0x{x:02x}" for x in v["pressed"]),
             "toggle_bits": [k for k in range(8)
                             if (min(v["pressed"]) ^ min(v["released"])) & (1 << k)]}
            for a, v in sorted(found.items())],
        "suggested_watch": [f"0x{b:08x}:0x{l:x}" for b, l in windows],
    }
    print(f"\n[auto-locate] {len(found)} consistent button-state byte(s) found.")
    if windows:
        print("    Re-run capture with the located window(s):")
        print("      " + " ".join(f"--watch 0x{b:08x}:0x{l:x}" for b, l in windows))
    else:
        print("    None — widen --region, add rounds, or the state lives outside "
              "the swept range (try near D_data from camera_probe).")
    return windows


def ask(msg: str) -> bool:
    """Prompt the operator; return False if they ask to skip/abort."""
    try:
        r = input(f"    >>> {msg} [Enter=done, s=skip]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return r != "s"


def capture_control(cam: Camera, name: str, meta: dict, windows):
    """Hold/release diff for one button. Returns a result dict."""
    is_power = meta.get("power")
    label = meta["label"]
    print(f"\n[control] {name} — {label}")
    res = {"control": name, "label": label, "board": meta.get("board"),
           "programmable": bool(meta.get("prog")), "soft_power": bool(is_power)}

    if is_power:
        print("    !! SOFT POWER BUTTON: a press may shut the camera down and end")
        print("    !! the JTAG session. TAP it briefly — do NOT hold. Capture last.")

    base = snapshot(cam, windows)
    hold_msg = ("TAP power now, then Enter (it may power off)" if is_power
                else f"press and HOLD {label}, keep holding, then Enter")
    if not ask(hold_msg):
        res["skipped"] = True
        return res
    pressed = snapshot(cam, windows)

    # camera may have powered off / link dropped on a power tap
    if not cam.connection_ok():
        res["link_lost_after"] = True
        res["pressed_diff"] = [_fmt_d(d) for d in diff_snaps(base, pressed)]
        return res

    dprs = diff_snaps(base, pressed)
    res["pressed_diff"] = [_fmt_d(d) for d in dprs]

    released = None
    if not is_power:
        if ask(f"now RELEASE {label}, then Enter"):
            released = snapshot(cam, windows)
            drel = diff_snaps(pressed, released)
            res["released_diff"] = [_fmt_d(d) for d in drel]
            # a real button: the pressed-set bits revert on release
            reverted = {d[0] for d in dprs} & {d[0] for d in drel}
            res["reverted_addrs"] = [f"0x{a:08x}" for a in sorted(reverted)]
            res["confirmed"] = bool(reverted)
    if not dprs:
        res["note"] = ("no DDR change in the watched windows — widen --watch / "
                       "add the I2C input-state global, or the bit lives elsewhere")
    return res


def capture_led(cam: Camera, name: str, label: str, windows):
    """LEDs are PCA9698 outputs: diff between OFF and ON states the operator sets."""
    print(f"\n[led] {name} — {label}")
    res = {"led": name, "label": label}
    if not ask(f"put the camera in the state where {label} is OFF, then Enter"):
        res["skipped"] = True
        return res
    off = snapshot(cam, windows)
    if not ask(f"now make {label} turn ON, then Enter"):
        res["skipped"] = True
        return res
    on = snapshot(cam, windows)
    d = diff_snaps(off, on)
    res["on_diff"] = [_fmt_d(x) for x in d]
    if not d:
        res["note"] = "no DDR change — the LED output mirror isn't in --watch windows"
    return res


def _fmt_d(d):
    addr, old, new, setb, clrb = d
    return {"addr": f"0x{addr:08x}", "old": f"0x{old:02x}", "new": f"0x{new:02x}",
            "set_bits": setb, "cleared_bits": clrb}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", help="camera identifier (report key)")
    ap.add_argument("--boards", default="", help='e.g. "cpu=revB,ui=revA,sd=revA"')
    ap.add_argument("--watch", action="append", default=[],
                    help="candidate DDR window ADDR[:LEN] to diff (repeatable). "
                         "LEN defaults to 0x100. These are where the firmware "
                         "caches decoded button/LED state.")
    ap.add_argument("--region", default=None,
                    help="DDR window ADDR:LEN to sweep. With --auto-locate it is "
                         "searched for the button-state global; otherwise it is "
                         "chunked into --watch windows (coarse, slow).")
    ap.add_argument("--chunk", default="0x400",
                    help="words per mrd read when sweeping --region (default 0x400)")
    ap.add_argument("--auto-locate", action="store_true",
                    help="find the button-state DDR global: hold --ref-control "
                         "across --rounds press/release cycles, sweep --region, "
                         "keep bytes that toggle consistently. Prints --watch "
                         "windows to use for the real capture.")
    ap.add_argument("--ref-control", default="record_left",
                    help="control to hold during --auto-locate (default record_left)")
    ap.add_argument("--rounds", type=int, default=3,
                    help="--auto-locate press/release cycles (more = less noise)")
    ap.add_argument("--controls", default="",
                    help="comma list of control names (default: all non-power). "
                         "Names: " + ",".join(CONTROLS))
    ap.add_argument("--leds", default="", help="comma list of LED names (rec,ok)")
    ap.add_argument("--include-power", action="store_true",
                    help="also capture the SOFT power button (tap-only, risky)")
    ap.add_argument("--list", action="store_true", help="list control names, exit")
    ap.add_argument("--bridge-dir", default=None)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--out", default=str(
        _HERE.parent / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    if args.list:
        for n, m in CONTROLS.items():
            print(f"  {n:14s} {m['label']}")
        for n, l in LEDS.items():
            print(f"  led:{n:10s} {l}")
        return 0

    if not args.id:
        ap.error("--id is required (except with --list)")

    chunk_words = int(args.chunk, 0)
    auto = args.auto_locate

    # ---- input validation ----
    if auto:
        if not args.region:
            ap.error("--auto-locate requires --region ADDR:LEN to sweep")
        if args.ref_control not in CONTROLS:
            ap.error(f"--ref-control '{args.ref_control}' unknown (see --list)")
        windows = []                       # discovered, not supplied
    else:
        windows = [parse_window(w) for w in args.watch]
        if args.region:                    # coarse: chunk region into --watch windows
            base, length = parse_window(args.region)
            step = chunk_words * 4
            windows += [(a, min(step, base + length - a))
                        for a in range(base, base + length, step)]
        if not windows:
            print("[!] no --watch/--region windows given. A button is observed by "
                  "DIFFING DDR; pass a candidate window, or use --auto-locate "
                  "--region to find the state global. See "
                  "plans/working_camera_jtag_analysis.md Phase 3E.")
            return 1

    # which controls (capture mode only)
    names, leds = [], []
    if not auto:
        if args.controls:
            names = [c.strip() for c in args.controls.split(",") if c.strip()]
        else:
            names = [n for n, m in CONTROLS.items() if not m.get("power")]
        if args.include_power and "power" not in names:
            names.append("power")
        unknown = [n for n in names if n not in CONTROLS]
        if unknown:
            print(f"[!] unknown control(s): {unknown}\n    valid: {', '.join(CONTROLS)}")
            return 1
        leds = [l.strip() for l in args.leds.split(",") if l.strip()]

    from xmd_rpc import DEFAULT_DIR
    cam = Camera(args.bridge_dir or DEFAULT_DIR, timeout=args.timeout)

    report = {
        "camera_id": args.id,
        "boards": dict(kv.split("=", 1) for kv in args.boards.split(",") if "=" in kv),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "transport": "ChannelB/xmd_rpc",
        "mode": "auto-locate" if auto else "capture",
        "method": "DDR-diff (PCA9698 buttons are read over I2C; state cached in DDR)",
        "watch_windows": [f"0x{b:08x}:0x{l:x}" for b, l in windows],
        "controls": [], "leds": [],
    }

    if auto:
        print(f"[*] button_capture '{args.id}' — AUTO-LOCATE button-state global")
    else:
        print(f"[*] button_capture '{args.id}' — {len(names)} control(s), "
              f"{len(leds)} LED(s)")
    try:
        cam.halt()
        if not cam.connection_ok():
            print("[!] XMD has NO live debug link to the PPC405 (target reports "
                  "'Debug Operation Not Supported').\n"
                  "    Re-run  connect ppc hw  in the VM's XMD console, then retry.")
            return 2
        cam.resume()  # keep it running so the firmware keeps polling the expanders
    except Exception as e:
        print(f"[!] no response from xmd_agent ({e}). Is agent_loop running?")
        return 1

    print("    Keep the camera fully booted & running; the firmware must be "
          "actively polling the I2C expanders for a press to change DDR.\n")

    try:
        if auto:
            base, length = parse_window(args.region)
            auto_locate(cam, base, length, chunk_words, args.rounds,
                        CONTROLS[args.ref_control]["label"], report)
        else:
            for n in names:
                report["controls"].append(
                    capture_control(cam, n, CONTROLS[n], windows))
                if CONTROLS[n].get("power") and report["controls"][-1].get(
                        "link_lost_after"):
                    print("    [i] link lost after power tap (expected if it "
                          "powered off). Stopping.")
                    break
            for l in leds:
                if l in LEDS:
                    report["leds"].append(capture_led(cam, l, LEDS[l], windows))
                else:
                    print(f"[!] unknown LED '{l}' (valid: {', '.join(LEDS)})")
    finally:
        try:
            cam.resume()
        except Exception:
            pass

    outdir = Path(args.out) / args.id
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "").replace("-", "")
    jpath = outdir / f"buttons_{stamp}.json"
    jpath.write_text(json.dumps(report, indent=2))
    mpath = outdir / f"buttons_{stamp}.md"
    mpath.write_text(_render_md(report))
    print(f"\n[*] report written:\n    {jpath}\n    {mpath}")
    return 0


def _render_md(r: dict) -> str:
    L = [f"# Physical-control capture — {r['camera_id']}", "",
         f"- when: {r['timestamp']}",
         f"- boards: {r.get('boards')}",
         f"- mode: {r.get('mode', 'capture')}",
         f"- method: {r['method']}",
         f"- watched windows: {', '.join(r['watch_windows']) or '—'}", ""]
    al = r.get("auto_locate")
    if al:
        L += ["## Auto-locate (button-state DDR global)", "",
              f"- reference control: **{al['ref_control']}**",
              f"- region swept: {al['region']}  ({al['rounds']} round(s))",
              f"- suggested `--watch`: `{' '.join(al['suggested_watch']) or '(none)'}`",
              "", "| addr | released | pressed | toggle bits |",
              "|---|---|---|---|"]
        for f in al["found"]:
            L.append(f"| {f['addr']} | {','.join(f['released'])} | "
                     f"{','.join(f['pressed'])} | {f['toggle_bits']} |")
        if not al["found"]:
            L.append("| _none found_ | | | |")
        L.append("")
        return "\n".join(L)
    L += ["## Buttons", "",
         "| control | board | prog | change (addr: bit) | confirmed |",
         "|---|---|---|---|---|"]
    for c in r["controls"]:
        chg = "; ".join(
            f"{d['addr']}:set{d['set_bits'] or d['cleared_bits']}"
            for d in c.get("pressed_diff", [])) or "—"
        L.append(f"| {c['control']} | {c.get('board')} | "
                 f"{'Y' if c.get('programmable') else ''} | {chg} | "
                 f"{c.get('confirmed', c.get('skipped') and 'skip' or '?')} |")
    if r["leds"]:
        L += ["", "## LEDs (PCA9698 outputs)", "",
              "| led | change (addr: bit) |", "|---|---|"]
        for e in r["leds"]:
            chg = "; ".join(f"{d['addr']}:bit{d['set_bits'] or d['cleared_bits']}"
                            for d in e.get("on_diff", [])) or "—"
            L.append(f"| {e['led']} | {chg} |")
    L += ["", "## QEMU follow-up",
          "- Map each `addr:bit` back to the PCA9698 chip/port the I2C driver "
          "writes it from (cross-ref the XIic/PCA9698 path), so the QEMU expander "
          "model and `qom-set` button injection reproduce it.",
          "- LEDs are expander outputs: surface their state on the QEMU device "
          "so a UI/log shows REC/OK."]
    notes = [c for c in r["controls"] if c.get("note")]
    if notes:
        L += ["", "## Notes",
              *[f"- {c['control']}: {c['note']}" for c in notes]]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
