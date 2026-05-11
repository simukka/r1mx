"""
kicad.py — Generate a KiCad .kicad_pcb file from r1mx.db.

Reads extracted PCB objects from the SQLite database (r1mx.db) produced by
the r1mx Toolkit app and creates a KiCad PCB file containing:
  - Board outline (Edge.Cuts)
  - Via holes
  - SMD/THT pad footprints (generic)
  - Copper track segments (F.Cu / B.Cu)

IMPORTANT: This script uses the pcbnew Python API which is only available on
the *system* Python (not in the .venv):

    /usr/bin/python3 toolkit/analysis/kicad.py --board cpu_io_board

Usage:
    /usr/bin/python3 toolkit/analysis/kicad.py --board cpu_io_board
    /usr/bin/python3 toolkit/analysis/kicad.py --board cpu_io_board \\
        --layer top --output /tmp/cpu_io_board.kicad_pcb
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from toolkit.paths import COMPONENTS_DIR, REPO_ROOT, SCHEMATICS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# pcbnew import — available in the venv via kicad.pth
# ---------------------------------------------------------------------------

def _require_pcbnew():
    try:
        import pcbnew  # noqa: F401
        return pcbnew
    except ImportError:
        print(
            "ERROR: pcbnew module not found.\n"
            "Ensure the venv has kicad.pth pointing to /usr/lib/python3/dist-packages,\n"
            "or run with the system Python that has KiCad installed.",
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

# ---------------------------------------------------------------------------
# Load layout from r1mx.db
# ---------------------------------------------------------------------------

def load_layout_from_db(board_name: str, layer_name: str) -> dict:
    """Reconstruct a layout dict from objects stored in r1mx.db.

    The returned dict mirrors the structure previously produced by
    extract_pcb_layers.py so that generate() can consume it unchanged.
    """
    import json as _json
    import sqlite3

    db_path = REPO_ROOT / "r1mx.db"
    if not db_path.exists():
        log.error("r1mx.db not found at %s — run the r1mx Toolkit app first", db_path)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    board_row = conn.execute(
        "SELECT id FROM boards WHERE name=?", (board_name,)
    ).fetchone()
    if not board_row:
        conn.close()
        log.error("Board '%s' not found in r1mx.db", board_name)
        sys.exit(1)

    layer_row = conn.execute(
        "SELECT id FROM layers WHERE board_id=? AND name=?",
        (board_row["id"], layer_name),
    ).fetchone()
    if not layer_row:
        conn.close()
        log.error("Layer '%s' for board '%s' not found in r1mx.db", layer_name, board_name)
        sys.exit(1)

    layer_id = layer_row["id"]
    objects = conn.execute(
        "SELECT * FROM objects WHERE layer_id=?", (layer_id,)
    ).fetchall()
    conn.close()

    is_front = layer_name in ("top", "front")
    pad_key   = "pads_front"   if is_front else "pads_back"
    track_key = "tracks_front" if is_front else "tracks_back"

    layout: dict = {
        "board": board_name,
        "vias": [],
        "board_outline": [],
        pad_key: [],
        track_key: [],
    }

    for obj in objects:
        props = _json.loads(obj["properties"] or "{}")
        t = obj["type"]

        if t == "via":
            layout["vias"].append({
                "x_mm":       obj["x_mm"] or 0,
                "y_mm":       obj["y_mm"] or 0,
                "drill_mm":   props.get("drill_mm", 0.3),
                "annular_mm": props.get("annular_mm", 0.15),
            })

        elif t == "pad":
            layout[pad_key].append({
                "x_mm":  obj["x_mm"] or 0,
                "y_mm":  obj["y_mm"] or 0,
                "w_mm":  obj["width_mm"] or 0.5,
                "h_mm":  obj["height_mm"] or 0.5,
                "ref":   obj["label"] or "",
                "layer": props.get("kicad_layer", "F_Cu" if is_front else "B_Cu"),
            })

        elif t == "trace":
            s = props.get("start")
            e = props.get("end")
            if s and e:
                layout[track_key].append({
                    "start":     s,
                    "end":       e,
                    "width_mm":  props.get("width_mm", 0.2),
                    "layer":     props.get("kicad_layer", "F_Cu" if is_front else "B_Cu"),
                })

        elif t == "outline":
            pts = props.get("points", [])
            if pts:
                layout["board_outline"] = pts

    log.info(
        "Loaded from DB: %d vias, %d pads, %d traces, outline=%s",
        len(layout["vias"]),
        len(layout[pad_key]),
        len(layout[track_key]),
        "yes" if layout["board_outline"] else "no",
    )
    return layout


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
        log.warning("  No board outline in DB — add manually in KiCad")

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
