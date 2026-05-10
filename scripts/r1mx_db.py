#!/usr/bin/env python3
"""
r1mx_db.py — SQLite database layer for the r1mx toolkit.

Database file: r1mx.db at the repository root.

All extraction results, calibration data, component information, and
workflow history land here. The schema is designed so AI agents can
query the full project state without touching the filesystem.

Usage (module):
    from r1mx_db import DB
    db = DB()          # opens r1mx.db in the repo root
    board = db.get_or_create_board("cpu_io_board")
    db.migrate_calibration_json("cpu_io_board")

Usage (CLI migration):
    python scripts/r1mx_db.py --migrate-all
    python scripts/r1mx_db.py --migrate cpu_io_board
"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Repo root is one level above this script.
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _REPO_ROOT / "r1mx.db"

# ─── Schema ─────────────────────────────────────────────────────────────────

_SCHEMA = """
-- Top-level inventory of PCB boards
CREATE TABLE IF NOT EXISTS boards (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Physical PCB layers (one row per image / layer combo)
CREATE TABLE IF NOT EXISTS layers (
    id              INTEGER PRIMARY KEY,
    board_id        INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,          -- "top", "bottom", "inner1", …
    source_image    TEXT,                   -- filename within board dir
    calibrated      INTEGER DEFAULT 0,      -- 1 when warp is done
    calibration     TEXT,                   -- JSON blob (warp matrix, px_per_mm, etc.)
    notes           TEXT,                   -- free-form notes from the user
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(board_id, name)
);

-- Every extracted or human-verified object on a layer
CREATE TABLE IF NOT EXISTS objects (
    id              INTEGER PRIMARY KEY,
    layer_id        INTEGER NOT NULL REFERENCES layers(id) ON DELETE CASCADE,
    type            TEXT NOT NULL,          -- "via","pad","component","trace","copper_area","outline"
    x_mm            REAL,
    y_mm            REAL,
    width_mm        REAL,
    height_mm       REAL,
    rotation_deg    REAL DEFAULT 0,
    label           TEXT,                   -- ref designator or net name
    confidence      REAL,                   -- 0–1, from automation; NULL = human-added
    verified        INTEGER DEFAULT 0,      -- 1 = human confirmed
    properties      TEXT,                   -- JSON: diameter_mm, net, layer_name, …
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Component details (one row per object of type "component")
CREATE TABLE IF NOT EXISTS components (
    id              INTEGER PRIMARY KEY,
    object_id       INTEGER UNIQUE REFERENCES objects(id) ON DELETE CASCADE,
    board_id        INTEGER REFERENCES boards(id),
    ref_designator  TEXT,
    part_number     TEXT,
    manufacturer    TEXT,
    value           TEXT,
    package         TEXT,
    description     TEXT,
    datasheet_id    INTEGER REFERENCES datasheets(id),
    mcp_data        TEXT,                   -- JSON from last MCP query
    verified        INTEGER DEFAULT 0,
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Datasheet files on disk
CREATE TABLE IF NOT EXISTS datasheets (
    id              INTEGER PRIMARY KEY,
    part_number     TEXT,
    manufacturer    TEXT,
    file_path       TEXT,                   -- relative to repo root
    url             TEXT,
    fetched_at      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Workflow step execution history
CREATE TABLE IF NOT EXISTS workflow_runs (
    id              INTEGER PRIMARY KEY,
    board_id        INTEGER REFERENCES boards(id),
    layer_id        INTEGER REFERENCES layers(id),
    step            TEXT NOT NULL,          -- "calibrate","extract_layers","extract_bom","generate_kicad"
    status          TEXT DEFAULT 'pending', -- pending / running / complete / failed
    log             TEXT,
    started_at      TEXT,
    completed_at    TEXT
);

-- App UI state (current board, layer, zoom, etc.)
CREATE TABLE IF NOT EXISTS app_state (
    key     TEXT PRIMARY KEY,
    value   TEXT
);

-- FTS index for full-text search across component labels and notes
CREATE VIRTUAL TABLE IF NOT EXISTS components_fts USING fts5(
    ref_designator,
    part_number,
    manufacturer,
    description,
    notes,
    content='components',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS components_ai AFTER INSERT ON components BEGIN
    INSERT INTO components_fts(rowid, ref_designator, part_number, manufacturer, description, notes)
    VALUES (new.id, new.ref_designator, new.part_number, new.manufacturer, new.description, new.notes);
END;
CREATE TRIGGER IF NOT EXISTS components_ad AFTER DELETE ON components BEGIN
    INSERT INTO components_fts(components_fts, rowid, ref_designator, part_number, manufacturer, description, notes)
    VALUES ('delete', old.id, old.ref_designator, old.part_number, old.manufacturer, old.description, old.notes);
END;
CREATE TRIGGER IF NOT EXISTS components_au AFTER UPDATE ON components BEGIN
    INSERT INTO components_fts(components_fts, rowid, ref_designator, part_number, manufacturer, description, notes)
    VALUES ('delete', old.id, old.ref_designator, old.part_number, old.manufacturer, old.description, old.notes);
    INSERT INTO components_fts(rowid, ref_designator, part_number, manufacturer, description, notes)
    VALUES (new.id, new.ref_designator, new.part_number, new.manufacturer, new.description, new.notes);
END;
"""


# ─── DB class ────────────────────────────────────────────────────────────────

class DB:
    """Thin wrapper around the r1mx.db SQLite database."""

    def __init__(self, path: Path | str = DB_PATH):
        self.path = Path(path)
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    # ── Connection management ──────────────────────────────────────────────

    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _ensure_schema(self):
        c = self.conn()
        c.executescript(_SCHEMA)
        # Incremental migrations for existing databases
        existing_cols = {r[1] for r in c.execute("PRAGMA table_info(layers)").fetchall()}
        if "notes" not in existing_cols:
            c.execute("ALTER TABLE layers ADD COLUMN notes TEXT")
        c.commit()

    # ── Boards ─────────────────────────────────────────────────────────────

    def get_or_create_board(self, name: str, description: str = "") -> int:
        """Return board id, creating the row if needed."""
        c = self.conn()
        row = c.execute("SELECT id FROM boards WHERE name=?", (name,)).fetchone()
        if row:
            return row["id"]
        cur = c.execute(
            "INSERT INTO boards(name, description) VALUES (?,?)",
            (name, description),
        )
        c.commit()
        return cur.lastrowid

    def list_boards(self) -> list[sqlite3.Row]:
        return self.conn().execute("SELECT * FROM boards ORDER BY name").fetchall()

    # ── Layers ─────────────────────────────────────────────────────────────

    def get_or_create_layer(self, board_id: int, name: str) -> int:
        c = self.conn()
        row = c.execute(
            "SELECT id FROM layers WHERE board_id=? AND name=?", (board_id, name)
        ).fetchone()
        if row:
            return row["id"]
        cur = c.execute(
            "INSERT INTO layers(board_id, name) VALUES (?,?)", (board_id, name)
        )
        c.commit()
        return cur.lastrowid

    def save_layer_calibration(
        self,
        board_id: int,
        layer_name: str,
        source_image: str,
        calibration: dict,
    ) -> int:
        """Write or update calibration data for a layer. Returns layer id."""
        c = self.conn()
        layer_id = self.get_or_create_layer(board_id, layer_name)
        c.execute(
            """UPDATE layers SET source_image=?, calibrated=1, calibration=?
               WHERE id=?""",
            (source_image, json.dumps(calibration), layer_id),
        )
        c.commit()
        return layer_id

    def get_layer(self, board_id: int, layer_name: str) -> sqlite3.Row | None:
        return self.conn().execute(
            "SELECT * FROM layers WHERE board_id=? AND name=?", (board_id, layer_name)
        ).fetchone()

    def list_layers(self, board_id: int) -> list[sqlite3.Row]:
        return self.conn().execute(
            "SELECT * FROM layers WHERE board_id=? ORDER BY name", (board_id,)
        ).fetchall()

    # ── Objects ────────────────────────────────────────────────────────────

    def insert_objects(self, rows: list[dict]) -> int:
        """Bulk insert objects. Returns number inserted."""
        if not rows:
            return 0
        c = self.conn()
        cols = (
            "layer_id", "type", "x_mm", "y_mm", "width_mm", "height_mm",
            "rotation_deg", "label", "confidence", "verified", "properties",
        )
        placeholders = ",".join(["?"] * len(cols))
        data = [
            tuple(r.get(col) for col in cols)
            for r in rows
        ]
        c.executemany(
            f"INSERT INTO objects({','.join(cols)}) VALUES ({placeholders})", data
        )
        c.commit()
        return len(data)

    def list_objects(
        self, layer_id: int, type_filter: str | None = None
    ) -> list[sqlite3.Row]:
        c = self.conn()
        if type_filter:
            return c.execute(
                "SELECT * FROM objects WHERE layer_id=? AND type=? ORDER BY id",
                (layer_id, type_filter),
            ).fetchall()
        return c.execute(
            "SELECT * FROM objects WHERE layer_id=? ORDER BY type, id", (layer_id,)
        ).fetchall()

    def delete_objects(self, layer_id: int, type_filter: str | None = None):
        c = self.conn()
        if type_filter:
            c.execute(
                "DELETE FROM objects WHERE layer_id=? AND type=?",
                (layer_id, type_filter),
            )
        else:
            c.execute("DELETE FROM objects WHERE layer_id=?", (layer_id,))
        c.commit()

    def save_layout_objects(self, layer_id: int, layout: dict, layer_key: str):
        """Import a layout dict (from extract_pcb_layers.process_board) into
        the objects table.

        Existing objects for this layer_id are deleted first so re-running is
        idempotent.

        Parameters
        ----------
        layer_id  : row id from the layers table
        layout    : dict returned by process_board()
        layer_key : "top" or "bottom" — determines which side of the layout
                    dict to read (front/back for pads/tracks)
        """
        import json as _json

        c = self.conn()
        c.execute("DELETE FROM objects WHERE layer_id=?", (layer_id,))

        rows = []

        is_front = (layer_key == "top")
        pad_key   = "pads_front"   if is_front else "pads_back"
        track_key = "tracks_front" if is_front else "tracks_back"

        # Vias (only stored on the front/top layer to avoid duplicates)
        if is_front:
            for v in layout.get("vias", []):
                d = v["drill_mm"] + 2 * v.get("annular_mm", 0.15)
                rows.append((
                    layer_id, "via",
                    v["x_mm"], v["y_mm"], d, d, 0.0,
                    None, None,
                    _json.dumps({"drill_mm": v["drill_mm"],
                                 "annular_mm": v.get("annular_mm", 0.15)}),
                ))

        # Pads
        for p in layout.get(pad_key, []):
            rows.append((
                layer_id, "pad",
                p["x_mm"], p["y_mm"], p["w_mm"], p["h_mm"],
                p.get("rotation_deg", 0.0),
                p.get("ref", "") or None, None,
                _json.dumps({"kicad_layer": p.get("layer", "")}),
            ))

        # Board outline (only on front/top)
        pts = layout.get("board_outline", [])
        if is_front and pts:
            rows.append((
                layer_id, "outline",
                None, None, None, None, 0.0,
                None, None,
                _json.dumps({"points": pts}),
            ))

        # Traces — stored as individual segments (start/end in mm)
        for t in layout.get(track_key, []):
            s, e = t["start"], t["end"]
            mx = (s[0] + e[0]) / 2
            my = (s[1] + e[1]) / 2
            rows.append((
                layer_id, "trace",
                mx, my, t.get("width_mm", 0.1), t.get("width_mm", 0.1), 0.0,
                None, None,
                _json.dumps({"start": s, "end": e,
                             "width_mm": t.get("width_mm", 0.1),
                             "kicad_layer": t.get("layer", "")}),
            ))

        c.executemany(
            """INSERT INTO objects
               (layer_id, type, x_mm, y_mm, width_mm, height_mm, rotation_deg,
                label, confidence, properties)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            rows,
        )
        c.commit()
        return len(rows)

    # ── Components ─────────────────────────────────────────────────────────

    def upsert_component(
        self,
        board_id: int,
        ref_designator: str,
        *,
        object_id: int | None = None,
        part_number: str | None = None,
        manufacturer: str | None = None,
        value: str | None = None,
        package: str | None = None,
        description: str | None = None,
        notes: str | None = None,
    ) -> int:
        c = self.conn()
        row = c.execute(
            "SELECT id FROM components WHERE board_id=? AND ref_designator=?",
            (board_id, ref_designator),
        ).fetchone()
        if row:
            c.execute(
                """UPDATE components SET object_id=COALESCE(?,object_id),
                   part_number=COALESCE(?,part_number),
                   manufacturer=COALESCE(?,manufacturer),
                   value=COALESCE(?,value), package=COALESCE(?,package),
                   description=COALESCE(?,description), notes=COALESCE(?,notes)
                   WHERE id=?""",
                (
                    object_id, part_number, manufacturer, value, package,
                    description, notes, row["id"],
                ),
            )
            c.commit()
            return row["id"]
        cur = c.execute(
            """INSERT INTO components
               (board_id, object_id, ref_designator, part_number, manufacturer,
                value, package, description, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                board_id, object_id, ref_designator, part_number, manufacturer,
                value, package, description, notes,
            ),
        )
        c.commit()
        return cur.lastrowid

    def list_components(self, board_id: int) -> list[sqlite3.Row]:
        return self.conn().execute(
            "SELECT * FROM components WHERE board_id=? ORDER BY ref_designator",
            (board_id,),
        ).fetchall()

    def search_components(self, query: str) -> list[sqlite3.Row]:
        return self.conn().execute(
            """SELECT c.* FROM components c
               JOIN components_fts f ON c.id = f.rowid
               WHERE components_fts MATCH ?
               ORDER BY rank""",
            (query,),
        ).fetchall()

    def save_mcp_data(self, component_id: int, data: dict):
        self.conn().execute(
            "UPDATE components SET mcp_data=? WHERE id=?",
            (json.dumps(data), component_id),
        )
        self.conn().commit()

    # ── Datasheets ─────────────────────────────────────────────────────────

    def get_or_create_datasheet(
        self, part_number: str, file_path: str, manufacturer: str = "", url: str = ""
    ) -> int:
        c = self.conn()
        row = c.execute(
            "SELECT id FROM datasheets WHERE file_path=?", (file_path,)
        ).fetchone()
        if row:
            return row["id"]
        cur = c.execute(
            """INSERT INTO datasheets(part_number, manufacturer, file_path, url, fetched_at)
               VALUES (?,?,?,?,?)""",
            (part_number, manufacturer, file_path, url, datetime.now().isoformat()),
        )
        c.commit()
        return cur.lastrowid

    def find_datasheet(self, part_number: str) -> sqlite3.Row | None:
        return self.conn().execute(
            "SELECT * FROM datasheets WHERE part_number=? LIMIT 1", (part_number,)
        ).fetchone()

    # ── Workflow runs ──────────────────────────────────────────────────────

    def start_workflow(self, step: str, board_id: int, layer_id: int | None = None) -> int:
        c = self.conn()
        cur = c.execute(
            """INSERT INTO workflow_runs(board_id, layer_id, step, status, started_at)
               VALUES (?,?,?,'running',?)""",
            (board_id, layer_id, step, datetime.now().isoformat()),
        )
        c.commit()
        return cur.lastrowid

    def finish_workflow(self, run_id: int, status: str, log: str = ""):
        c = self.conn()
        c.execute(
            """UPDATE workflow_runs SET status=?, log=?, completed_at=?
               WHERE id=?""",
            (status, log, datetime.now().isoformat(), run_id),
        )
        c.commit()

    # ── App state ──────────────────────────────────────────────────────────

    def get_state(self, key: str, default: str = "") -> str:
        row = self.conn().execute(
            "SELECT value FROM app_state WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_state(self, key: str, value: str):
        self.conn().execute(
            "INSERT OR REPLACE INTO app_state(key, value) VALUES (?,?)", (key, value)
        )
        self.conn().commit()

    def save_visibility_state(self, state: dict):
        """Persist the full visibility state dict as JSON.

        Structure::

            {
              "cpu_io_board": {
                "top": {"__layer__": True, "photo": True, "via": False, …},
                "__board__": True
              },
              …
            }
        """
        self.set_state("visibility_state", json.dumps(state))

    def load_visibility_state(self) -> dict:
        """Return the persisted visibility state, or {} if none saved."""
        raw = self.get_state("visibility_state", "")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            return {}

    # ── Migration ─────────────────────────────────────────────────────────

    def migrate_calibration_json(self, board_name: str) -> bool:
        """Import a calibration.json file into the database. Returns True if imported."""
        board_dir = _REPO_ROOT / "components" / board_name
        cal_path = board_dir / "calibration.json"
        if not cal_path.exists():
            return False

        with cal_path.open() as f:
            cal = json.load(f)

        board_id = self.get_or_create_board(board_name)

        for layer_name, layer_data in cal.get("layers", {}).items():
            calibration = {
                "corners_px": layer_data.get("corners_px"),
                "warp_matrix": layer_data.get("warp_matrix"),
                "warped_size": layer_data.get("warped_size"),
                "px_per_mm": layer_data.get("px_per_mm"),
                "ref_points_warped_px": layer_data.get("ref_points_warped_px"),
                "ref_distance_mm": layer_data.get("ref_distance_mm"),
                "hsv_overrides": cal.get("hsv_overrides", {}),
            }
            source_image = layer_data.get("source_image", "")
            self.save_layer_calibration(board_id, layer_name, source_image, calibration)
            print(f"  imported  {board_name}/{layer_name}  ({source_image})")

        return True

    def migrate_all_calibration_jsons(self):
        """Walk components/ and import every calibration.json found."""
        components_dir = _REPO_ROOT / "components"
        imported = 0
        for board_dir in sorted(components_dir.iterdir()):
            if (board_dir / "calibration.json").exists():
                print(f"Importing {board_dir.name} …")
                if self.migrate_calibration_json(board_dir.name):
                    imported += 1
        print(f"\nDone — {imported} board(s) migrated to {self.path}")

    def index_datasheets(self):
        """Walk */datasheets/ dirs and register every PDF in the datasheets table."""
        components_dir = _REPO_ROOT / "components"
        added = 0
        for pdf in sorted(components_dir.rglob("datasheets/*.pdf")):
            rel = str(pdf.relative_to(_REPO_ROOT))
            part = pdf.stem
            did = self.get_or_create_datasheet(part, rel)
            print(f"  datasheet  {rel}  (id={did})")
            added += 1
        # Also scan ssd_drive/datasheets etc.
        for extra_dir in ("ssd_drive/datasheets", "ssd_board/datasheets",
                          "firmware/reference"):
            for pdf in sorted((_REPO_ROOT / extra_dir).rglob("*.pdf")):
                rel = str(pdf.relative_to(_REPO_ROOT))
                part = pdf.stem
                did = self.get_or_create_datasheet(part, rel)
                print(f"  datasheet  {rel}  (id={did})")
                added += 1
        print(f"\n{added} datasheets indexed.")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def _cli():
    parser = argparse.ArgumentParser(description="r1mx database utilities")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--migrate-all", action="store_true",
                     help="Import all calibration.json files into r1mx.db")
    grp.add_argument("--migrate", metavar="BOARD",
                     help="Import a single board's calibration.json")
    grp.add_argument("--index-datasheets", action="store_true",
                     help="Walk */datasheets/ and register all PDFs in r1mx.db")
    grp.add_argument("--list-boards", action="store_true",
                     help="Print all boards in r1mx.db")
    grp.add_argument("--list-layers", metavar="BOARD",
                     help="Print all layers for a board")
    args = parser.parse_args()

    db = DB()

    if args.migrate_all:
        db.migrate_all_calibration_jsons()
    elif args.migrate:
        ok = db.migrate_calibration_json(args.migrate)
        if not ok:
            print(f"No calibration.json found for board: {args.migrate}")
    elif args.index_datasheets:
        db.index_datasheets()
    elif args.list_boards:
        for row in db.list_boards():
            print(f"  [{row['id']}] {row['name']}")
    elif args.list_layers:
        board_id = db.get_or_create_board(args.list_layers)
        for row in db.list_layers(board_id):
            cal = "✓" if row["calibrated"] else "✗"
            print(f"  [{row['id']}] {row['name']:10s}  calibrated={cal}  src={row['source_image']}")


if __name__ == "__main__":
    _cli()
