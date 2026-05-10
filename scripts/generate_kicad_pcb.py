#!/usr/bin/env python3
"""
generate_kicad_pcb.py — Generate a KiCad .kicad_pcb file from layout.json.

Reads the layout.json produced by extract_pcb_layers.py and creates a
KiCad PCB file containing:
  - Board outline (Edge.Cuts)
  - Via holes
  - SMD/THT pad footprints (generic)
  - Copper track segments (F.Cu / B.Cu)

IMPORTANT: This script uses the pcbnew Python API which is only available on
the *system* Python (not in the .venv):

    /usr/bin/python3 scripts/generate_kicad_pcb.py --board cpu_io_board

Usage:
    /usr/bin/python3 scripts/generate_kicad_pcb.py --board cpu_io_board
    /usr/bin/python3 scripts/generate_kicad_pcb.py --board cpu_io_board \
        --output /tmp/cpu_io_board.kicad_pcb
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
SCHEMATICS_DIR = REPO_ROOT / "schematics"


# ---------------------------------------------------------------------------
# pcbnew import — required; must run under /usr/bin/python3
# ---------------------------------------------------------------------------

def _require_pcbnew():
    try:
        import pcbnew  # noqa: F401
        return pcbnew
    except ImportError:
        print(
            "ERROR: pcbnew module not found.\n"
            "This script must be run with the system KiCad Python, e.g.:\n"
            "    /usr/bin/python3 scripts/generate_kicad_pcb.py --board <board>\n"
            "Do NOT run inside the .venv.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Unit helpers (pcbnew uses nanometres internally)
# ---------------------------------------------------------------------------

def mm(val: float):
    """Convert mm to pcbnew internal units (nanometres)."""
    import pcbnew
    return pcbnew.FromMM(val)


def wxp(x_mm: float, y_mm: float):
    """Create a pcbnew VECTOR2I from mm coordinates."""
    import pcbnew
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


# ---------------------------------------------------------------------------
# Layer helpers
# ---------------------------------------------------------------------------

LAYER_MAP = {
    "F_Cu":   "F.Cu",
    "B_Cu":   "B.Cu",
    "F.Cu":   "F.Cu",
    "B.Cu":   "B.Cu",
}

def get_layer_id(layer_str: str, board) -> int:
    import pcbnew
    kicad_name = LAYER_MAP.get(layer_str, "F.Cu")
    return board.GetLayerID(kicad_name)


# ---------------------------------------------------------------------------
# Board outline (Edge.Cuts)
# ---------------------------------------------------------------------------

def add_board_outline(board, outline_pts: list) -> None:
    """Add Edge.Cuts lines forming the board outline from a list of [x_mm, y_mm] pts."""
    import pcbnew
    if len(outline_pts) < 2:
        return

    edge_layer = board.GetLayerID("Edge.Cuts")
    pts = outline_pts + [outline_pts[0]]  # close the polygon

    for i in range(len(pts) - 1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(edge_layer)
        seg.SetStart(wxp(*pts[i]))
        seg.SetEnd(wxp(*pts[i + 1]))
        seg.SetWidth(mm(0.05))
        board.Add(seg)

    log.info("  Added board outline (%d segments)", len(pts) - 1)


# ---------------------------------------------------------------------------
# Vias
# ---------------------------------------------------------------------------

def add_vias(board, vias: list) -> None:
    import pcbnew
    for v in vias:
        via = pcbnew.PCB_VIA(board)
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetPosition(wxp(v["x_mm"], v["y_mm"]))
        drill = max(0.1, v.get("drill_mm", 0.3))
        annular = v.get("annular_mm", 0.15)
        via.SetDrillDefault()
        via.SetDrill(mm(drill))
        via.SetWidth(mm(drill + 2 * annular))
        board.Add(via)
    log.info("  Added %d vias", len(vias))


# ---------------------------------------------------------------------------
# Tracks (copper segments)
# ---------------------------------------------------------------------------

def add_tracks(board, tracks: list) -> None:
    import pcbnew
    skipped = 0
    added = 0
    for t in tracks:
        try:
            layer_id = get_layer_id(t.get("layer", "F_Cu"), board)
            track = pcbnew.PCB_TRACK(board)
            track.SetLayer(layer_id)
            track.SetStart(wxp(*t["start"]))
            track.SetEnd(wxp(*t["end"]))
            width = max(0.05, t.get("width_mm", 0.2))
            track.SetWidth(mm(width))
            board.Add(track)
            added += 1
        except Exception as e:
            skipped += 1
            if skipped <= 5:
                log.debug("  Skipping track: %s", e)
    log.info("  Added %d tracks (%d skipped)", added, skipped)


# ---------------------------------------------------------------------------
# Pads as minimal footprints
# ---------------------------------------------------------------------------

def add_pads(board, pads: list) -> None:
    """
    Each pad is added as a single-pad footprint.
    If a ref was assigned by extract_pcb_layers.py it is used; otherwise
    the footprint gets a sequential anonymous ref.
    """
    import pcbnew

    fp_count = 0
    for i, p in enumerate(pads):
        ref = p.get("ref", "") or f"FP{i + 1:04d}"
        layer_id = get_layer_id(p.get("layer", "F_Cu"), board)

        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference(ref)
        fp.SetValue("")
        fp.SetPosition(wxp(p["x_mm"], p["y_mm"]))

        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayer(layer_id)
        pad.SetLayerSet(pcbnew.LSET(layer_id))

        w = max(0.1, p.get("w_mm", 0.5))
        h = max(0.1, p.get("h_mm", 0.5))
        pad.SetSize(pcbnew.VECTOR2I(mm(w), mm(h)))
        pad.SetPosition(wxp(p["x_mm"], p["y_mm"]))
        fp.Add(pad)

        board.Add(fp)
        fp_count += 1

    log.info("  Added %d pad footprints", fp_count)


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate(layout: dict, output_path: Path) -> None:
    pcbnew = _require_pcbnew()

    board = pcbnew.BOARD()
    board_name = layout.get("board", "unknown")
    log.info("Generating PCB: %s", board_name)

    # Board outline
    outline = layout.get("board_outline", [])
    if outline:
        add_board_outline(board, outline)
    else:
        log.warning("  No board outline in layout.json — add manually in KiCad")

    # Vias
    vias = layout.get("vias", [])
    add_vias(board, vias)

    # Front copper
    add_pads(board, layout.get("pads_front", []))
    add_tracks(board, layout.get("tracks_front", []))

    # Back copper
    add_pads(board, layout.get("pads_back", []))
    add_tracks(board, layout.get("tracks_back", []))

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    board.Save(str(output_path))
    log.info("Wrote %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate KiCad .kicad_pcb from layout.json. "
                    "Must be run with /usr/bin/python3 (system KiCad Python)."
    )
    parser.add_argument("--board", required=True, metavar="NAME",
                        help="Board folder name under components/")
    parser.add_argument("--output", metavar="FILE",
                        help="Output .kicad_pcb path (default: components/<board>/<board>.kicad_pcb)")
    parser.add_argument("--layout", metavar="FILE",
                        help="Override layout.json path")
    args = parser.parse_args()

    board_dir = COMPONENTS_DIR / args.board
    if not board_dir.is_dir():
        log.error("Board not found: %s", board_dir)
        sys.exit(1)

    layout_path = Path(args.layout) if args.layout else board_dir / "layout.json"
    if not layout_path.exists():
        log.error(
            "layout.json not found. Run extract_pcb_layers.py first:\n"
            "    python scripts/extract_pcb_layers.py --board %s",
            args.board,
        )
        sys.exit(1)

    with layout_path.open() as f:
        layout = json.load(f)

    output_path = Path(args.output) if args.output else \
        board_dir / f"{args.board}.kicad_pcb"

    generate(layout, output_path)
    print(f"\nKiCad PCB written to: {output_path}")
    print("Open with: kicad or pcbnew")


if __name__ == "__main__":
    main()
