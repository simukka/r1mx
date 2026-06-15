#!/usr/bin/env python3
"""harvest_slots.py — read post-init values of .data fn-ptr slots from a live
BOOTED RED ONE MX camera, classify + relocation-translate them, and emit a
seedable table for QEMU (the seed_boot.py SEEDS format).

WHY: QEMU's cold boot wedges on a circular bootstrap — the natural root-task
dispatch (FUN_00371cd0 else-path -> FUN_00371c74 calls *0xE293F4) reads garbage
.data fn-ptr slots that the C++ init phase (which runs only inside the dispatched
task) is supposed to install. The live booted camera is PAST that init, so each
slot holds its post-init ground-truth value. Reading those, translating code
pointers by the camera's relocation delta (D_text), and seeding them into QEMU
may let the natural dispatch reach the real root entry. See
plans/can-we-inspect-the-spicy-hartmanis.md and
firmware/reverse/build_32/boot_reconstruction_status.md (2026-06-14).

READ-ONLY: the camera client is constructed with allow_write=False; this script
has no write path to the camera. It only READS. Translation/seeding happens
offline (the emitted table is applied to QEMU by a separate harness).

RELOCATION (per-camera; re-derive every session via camera_probe.py reloc phase):
  cam-working-01: D_text = 0x10180, D_data ~= 0.
  - A live value that points into .text/.rodata is relocated: QEMU = live - D_text.
  - A live value that points into .data/.bss is absolute (D_data~=0): QEMU = live.
  - A live value >= file end (0xE8BF20) that is NOT a fixed BSS global is a
    camera-specific HEAP object -> NOT copyable; flagged for an Option-B structure
    read instead.
This tool surfaces BOTH candidate interpretations (live-D_text and live) plus a
file disassembly at live-D_text so the operator can cross-check (plan Stage D).

USAGE (dispatch-critical first session, Channel A = XMD gdb stub on :2345):
  python3 firmware/scripts/harvest_slots.py \
      --id cam-working-01 --d-text 0x10180 --port 2345 \
      --slots 0xE293F4=dispatch_fnptr,0xE3A790=dispatch_selector,\
0xE295C4=allocator_obj,0xE9C34C=alloc_fnptr,0xE9C648=free_fnptr,\
0xE26978=dev_count,0xE3A624=dev_table,0xE3A630=dev_ctx_count \
      --rounds 4

A dynamic address (e.g. the root task's TCB+0xC0, found first via task_walker.py)
can be passed the same way:  --slots 0x0FF96340=root_tcb_entry
"""
import argparse
import json
import struct
import sys
import time
from pathlib import Path

from rsp import RSP

FILE_END  = 0xE8BF20    # software.bin size; values >= this are not file-backed
BSS_START = 0xE9BF20
HEAP_START = 0x01153480  # bss end / heap start (per r1mx_firmware.ld)
CODE_LO   = 0x00001000
CODE_HI   = 0x00600000   # main .text upper bound (matches scan_null_guarded_dispatch)
VECTOR_HI = 0x00002000

# Valid PPC primary opcodes for a plausible code target — copied verbatim from
# scan_null_guarded_dispatch.py:looks_like_code (kept in sync intentionally).
_CODE_OPS = frozenset((14, 15, 16, 17, 18, 19, 31, 32, 33, 34, 36, 37, 38, 40,
                       44, 11, 10, 7, 8, 12, 13, 24, 25, 26, 27, 28, 29, 21, 23, 20))


def looks_like_code(image: bytes, off: int) -> bool:
    """Does the file at offset `off` look like a function entry / valid code?
    Mirrors scan_null_guarded_dispatch.py. Evaluated against the FILE, never the
    camera's .text (which is I-side-only mapped at idle -> reads 0)."""
    if off < 0 or off + 4 > len(image):
        return False
    w = struct.unpack(">I", image[off:off + 4])[0]
    if w == 0:
        return False
    return (w >> 26) in _CODE_OPS


def file_disasm(image: bytes, off: int, n: int = 3):
    """First n instructions at file offset `off`, if capstone is available."""
    try:
        from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN
    except Exception:
        return None
    if off < 0 or off + 4 > len(image):
        return None
    md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
    out = []
    for ins in md.disasm(image[off:off + 0x10], off):
        out.append(f"0x{ins.address:08x}: {ins.mnemonic} {ins.op_str}")
        if len(out) >= n:
            break
    return out


def classify(live, d_text, image):
    """Return (klass, qemu_seed_or_None, detail-dict). klass in
    null/vector/code/data/bss/heap/unknown."""
    detail = {}
    if live is None:
        return "unread", None, detail
    if live == 0:
        return "null", 0, detail
    if live < VECTOR_HI:
        return "vector", None, detail   # reset/exc vector — calling it resets CPU

    # Candidate 1: relocated .text code pointer (subtract D_text). A function
    # pointer relocates into the live range [CODE_LO+D_text, CODE_HI+D_text];
    # absolute rodata/data globals sit ABOVE that range and must NOT be treated
    # as code (that was a false-positive source). We still record the candidate +
    # disasm for operator cross-check (plan Stage D) even when not classified code.
    code_off = (live - d_text) & 0xFFFFFFFF
    in_reloc_text = (CODE_LO + d_text) <= live < (CODE_HI + d_text)
    is_code = in_reloc_text and looks_like_code(image, code_off)
    detail["candidate_code_qemu"] = code_off
    detail["looks_like_code"] = looks_like_code(image, code_off) if CODE_LO <= code_off < FILE_END else False
    detail["in_reloc_text_range"] = in_reloc_text
    detail["file_disasm_at_code"] = file_disasm(image, code_off) if (CODE_LO <= code_off < FILE_END) else None

    if is_code:
        return "code", code_off, detail

    # Candidate 2: absolute data/bss pointer (D_data ~= 0).
    if CODE_LO <= live < FILE_END:
        # in-file but not codeish: rodata/data global, absolute
        return "data", live, detail
    if BSS_START <= live < HEAP_START:
        # fixed BSS global address: same in QEMU, but the OBJECT it points at is
        # runtime-populated -> seed the pointer, but target may be empty in QEMU.
        return "bss", live, detail
    if live >= HEAP_START:
        return "heap", None, detail     # camera-specific malloc'd object — not copyable

    return "unknown", None, detail


def parse_slots(spec):
    """'0xADDR=label,0xADDR2' -> [(addr, label)]."""
    out = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if "=" in tok:
            a, lbl = tok.split("=", 1)
        else:
            a, lbl = tok, ""
        out.append((int(a, 0), lbl.strip()))
    return out


def ensure_halted(cam):
    """Halt the target only if it's running. The XMD stub often leaves the
    camera already halted (stop reply S/T); interrupting an already-halted
    target hangs waiting for a reply that never comes."""
    try:
        s = cam.stop_reply(timeout=3.0)
    except Exception:
        s = ""
    if s and s[0] in "ST":
        return  # already halted
    try:
        cam.interrupt(timeout=5.0)
    except Exception:
        pass


def harvest(cam, slots, rounds):
    """Read each slot over `rounds` halt/read/resume cycles; keep the first
    consistent non-ambiguous value (mode of readings)."""
    readings = {addr: [] for addr, _ in slots}
    for r in range(rounds):
        ensure_halted(cam)
        for addr, _ in slots:
            try:
                v = cam.read_word(addr)
            except Exception:
                v = None
            readings[addr].append(v)
        # resume between rounds so different task contexts page-in different TLBs
        if r < rounds - 1:
            try:
                cam.cont(timeout=2.0)
            except Exception:
                pass
            time.sleep(0.3)
    # collapse: prefer the most common non-None value
    final = {}
    for addr, vals in readings.items():
        good = [v for v in vals if v not in (None,)]
        if not good:
            final[addr] = None
        else:
            final[addr] = max(set(good), key=good.count)
    return final, readings


def main():
    ap = argparse.ArgumentParser(description="Harvest live-camera .data slot values for QEMU seeding")
    repo = Path(__file__).resolve().parents[1]
    ap.add_argument("--id", default="cam-working-01", help="camera id (report subdir)")
    ap.add_argument("--d-text", required=True, help="relocation delta D_text (re-derive per session)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=2345, help="XMD gdb stub via NAT pf (Channel A)")
    ap.add_argument("--slots", required=True,
                    help="comma list of 0xADDR or 0xADDR=label")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--bin", default=str(repo / "reverse/build_32/extracted/software.bin"))
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--out", default=str(repo / "reverse/build_32/camera_reports"))
    args = ap.parse_args()

    d_text = int(args.d_text, 0)
    image = Path(args.bin).read_bytes()
    slots = parse_slots(args.slots)

    print(f"[*] harvest: {len(slots)} slot(s), D_text=0x{d_text:x}, camera {args.host}:{args.port}")
    cam = RSP(args.host, args.port, allow_write=False, timeout=args.timeout, label="camera").connect()
    try:
        # sanity: confirm we're talking to a live target and not QEMU on the wrong port
        try:
            pc = cam.regs().get("pc")
            print(f"    connected; current pc=0x{(pc or 0):08x}")
        except Exception as e:
            print(f"    WARN: could not read regs ({e})")
        final, readings = harvest(cam, slots, args.rounds)
    finally:
        # always resume + detach so the camera is left running
        try:
            cam.cont(timeout=2.0)
        except Exception:
            pass
        cam.close()

    rows = []
    seed_table = []     # (addr, qemu_seed, note) in seed_boot.py format
    heap_objects = []
    for addr, label in slots:
        live = final[addr]
        klass, seed, detail = classify(live, d_text, image)
        row = {
            "slot": addr, "label": label,
            "live_value": live, "class": klass,
            "qemu_seed": seed,
            "readings": readings[addr],
            **detail,
        }
        rows.append(row)
        livestr = "None" if live is None else f"0x{live:08x}"
        seedstr = "-" if seed is None else f"0x{seed:08x}"
        print(f"  0x{addr:08x} {label:<18s} live={livestr:>10s}  class={klass:<7s}  qemu={seedstr}")
        if detail.get("file_disasm_at_code"):
            for d in detail["file_disasm_at_code"]:
                print(f"        {d}")
        if klass in ("code", "data", "bss", "null"):
            note = f"harvested {label or hex(addr)} ({klass}" + (f", -D_text" if klass == "code" else "") + ")"
            seed_table.append((addr, seed, note))
        elif klass == "heap":
            heap_objects.append({"slot": addr, "label": label, "live_value": live})

    ts = time.strftime("%Y%m%dT%H%M%S")
    outdir = Path(args.out) / args.id
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        "camera_id": args.id, "timestamp": ts, "d_text": d_text,
        "host": args.host, "port": args.port, "bin": args.bin,
        "n_slots": len(slots), "slots": rows,
        "seed_table": [[a, s, n] for a, s, n in seed_table],
        "heap_objects": heap_objects,
    }
    jpath = outdir / f"harvest_{ts}.json"
    jpath.write_text(json.dumps(report, indent=2))

    # Markdown + paste-ready SEEDS block
    md = [f"# {args.id} — slot harvest {ts}", "",
          f"- D_text = 0x{d_text:x}", f"- camera {args.host}:{args.port}", "",
          "| slot | label | live | class | qemu_seed |",
          "|---|---|---|---|---|"]
    for r in rows:
        lv = "None" if r["live_value"] is None else f"0x{r['live_value']:08x}"
        qs = "-" if r["qemu_seed"] is None else f"0x{r['qemu_seed']:08x}"
        md.append(f"| 0x{r['slot']:08x} | {r['label']} | {lv} | {r['class']} | {qs} |")
    md += ["", "## Paste-ready SEEDS (seed_boot.py format)", "```python", "HARVESTED_SEEDS = ["]
    for a, s, n in seed_table:
        md.append(f"    (0x{a:08X}, 0x{s:08X}, {n!r}),")
    md += ["]", "```"]
    if heap_objects:
        md += ["", "## Heap objects (NOT seedable — Option B structure read)"]
        for h in heap_objects:
            md.append(f"- 0x{h['slot']:08x} {h['label']}: live=0x{h['live_value']:08x} (camera heap)")
    mpath = outdir / f"harvest_{ts}.md"
    mpath.write_text("\n".join(md))

    print(f"\n[*] {len(seed_table)} seedable, {len(heap_objects)} heap-flagged")
    print(f"[*] report: {jpath}")
    print(f"[*] report: {mpath}")


if __name__ == "__main__":
    main()
