"""
db.py — SQLite database layer for the r1mx toolkit.

Database file: r1mx.db at the repository root.

All extraction results, calibration data, component information, and
workflow history land here. The schema is designed so AI agents can
query the full project state without touching the filesystem.

Usage (module):
    from toolkit.db import DB
    db = DB()          # opens r1mx.db in the repo root
    board = db.get_or_create_board("cpu_io_board")
    db.migrate_calibration_json("cpu_io_board")

Usage (CLI migration):
    python -m toolkit.db --migrate-all
    python -m toolkit.db --migrate cpu_io_board
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from toolkit.paths import REPO_ROOT as _REPO, DB_PATH, COMPONENTS_DIR as _COMPONENTS_DIR

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

-- Many-to-many: one object can have multiple linked datasheets
CREATE TABLE IF NOT EXISTS object_datasheets (
    object_id    INTEGER NOT NULL REFERENCES objects(id)    ON DELETE CASCADE,
    datasheet_id INTEGER NOT NULL REFERENCES datasheets(id) ON DELETE CASCADE,
    PRIMARY KEY (object_id, datasheet_id)
);

-- Measurements recorded via the probe wizard
CREATE TABLE IF NOT EXISTS component_measurements (
    id               INTEGER PRIMARY KEY,
    component_id     INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    measurement_type TEXT NOT NULL,  -- "resistance","capacitance","inductance","dcr",
                                     --   "forward_voltage","hfe","continuity","esr"
    raw_value        TEXT,           -- exactly what the user typed ("4.7k", "220nF")
    si_value         REAL,           -- normalised to SI base unit (Ω/F/H/V)
    unit             TEXT,           -- "Ω","F","H","V","dimensionless"
    notes            TEXT,
    orientation      TEXT,           -- "forward"/"reverse" for diodes
    in_circuit       INTEGER DEFAULT 1,
    created_at       TEXT DEFAULT (datetime('now'))
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


class RowRef(int):
    """Integer row identifier with dictionary-style access to row fields."""

    def __new__(cls, row: sqlite3.Row | dict):
        data = dict(row)
        obj = int.__new__(cls, data["id"])
        obj._data = data
        return obj

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def as_dict(self) -> dict:
        """Return the wrapped row as a plain dictionary."""
        return dict(self._data)


# ─── DB class ────────────────────────────────────────────────────────────────

class DB:
    """Thin wrapper around the r1mx.db SQLite database."""

    def __init__(self, db_path: Path | str = DB_PATH):
        """Open the toolkit database, creating the schema when needed."""
        self.path = Path(db_path)
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
        existing_layer_cols = {r[1] for r in c.execute("PRAGMA table_info(layers)").fetchall()}
        if "notes" not in existing_layer_cols:
            c.execute("ALTER TABLE layers ADD COLUMN notes TEXT")
        existing_comp_cols = {r[1] for r in c.execute("PRAGMA table_info(components)").fetchall()}
        if "status" not in existing_comp_cols:
            c.execute(
                "ALTER TABLE components ADD COLUMN status TEXT DEFAULT 'unknown'"
            )
        # object_datasheets may not exist in pre-existing databases
        self.migrate_add_object_datasheets()
        c.commit()

    # ── Boards ─────────────────────────────────────────────────────────────

    def get_or_create_board(self, name: str, description: str = "") -> RowRef:
        """Return a board row, creating it when needed."""
        c = self.conn()
        row = c.execute("SELECT * FROM boards WHERE name=?", (name,)).fetchone()
        if row:
            return RowRef(row)
        cur = c.execute(
            "INSERT INTO boards(name, description) VALUES (?,?)",
            (name, description),
        )
        c.commit()
        row = c.execute("SELECT * FROM boards WHERE id=?", (cur.lastrowid,)).fetchone()
        return RowRef(row)

    def list_boards(self) -> list[sqlite3.Row]:
        return self.conn().execute("SELECT * FROM boards ORDER BY name").fetchall()

    # ── Layers ─────────────────────────────────────────────────────────────

    def get_or_create_layer(self, board_id: int, name: str) -> RowRef:
        """Return a layer row, creating it when needed."""
        c = self.conn()
        row = c.execute(
            "SELECT * FROM layers WHERE board_id=? AND name=?", (int(board_id), name)
        ).fetchone()
        if row:
            return RowRef(row)
        cur = c.execute(
            "INSERT INTO layers(board_id, name) VALUES (?,?)", (int(board_id), name)
        )
        c.commit()
        row = c.execute("SELECT * FROM layers WHERE id=?", (cur.lastrowid,)).fetchone()
        return RowRef(row)

    def add_layer(self, board_id: int, name: str, source_image: str = "") -> RowRef:
        """Create or update a layer row and return it."""
        layer = self.get_or_create_layer(board_id, name)
        if source_image:
            self.conn().execute(
                "UPDATE layers SET source_image=? WHERE id=?",
                (source_image, int(layer)),
            )
            self.conn().commit()
            layer = self.conn().execute("SELECT * FROM layers WHERE id=?", (int(layer),)).fetchone()
            return RowRef(layer)
        return layer

    def save_layer_calibration(
        self,
        board_id: int,
        layer_name: str,
        source_image: str,
        calibration: dict,
    ) -> int:
        """Write or update calibration data for a layer. Returns layer id."""
        c = self.conn()
        layer_id = int(self.get_or_create_layer(board_id, layer_name))
        c.execute(
            """UPDATE layers SET source_image=?, calibrated=1, calibration=?
               WHERE id=?""",
            (source_image, json.dumps(calibration), layer_id),
        )
        c.commit()
        return layer_id

    def get_layer(self, board_id: int, layer_name: str) -> sqlite3.Row | None:
        """Return the layer row for a board/layer pair."""
        return self.conn().execute(
            "SELECT * FROM layers WHERE board_id=? AND name=?", (int(board_id), layer_name)
        ).fetchone()

    def save_calibration(self, board_id: int, layer_id: int, calibration: dict) -> None:
        """Persist calibration JSON for an existing layer row."""
        self.conn().execute(
            "UPDATE layers SET calibrated=1, calibration=? WHERE id=? AND board_id=?",
            (json.dumps(calibration), int(layer_id), int(board_id)),
        )
        self.conn().commit()

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

    def delete_objects(self, layer_id: int, type_filter: str | None = None, *, obj_type: str | None = None):
        """Delete objects for a layer, optionally filtered by object type."""
        if obj_type is not None:
            type_filter = obj_type
        c = self.conn()
        # Explicitly remove components linked to these objects so that boards
        # with foreign_keys=OFF (older DBs) still get cleaned up, and so that
        # components upserted from a different layer don't become orphaned.
        if type_filter:
            c.execute(
                """DELETE FROM components WHERE object_id IN (
                       SELECT id FROM objects WHERE layer_id=? AND type=?
                   )""",
                (layer_id, type_filter),
            )
            c.execute(
                "DELETE FROM objects WHERE layer_id=? AND type=?",
                (layer_id, type_filter),
            )
        else:
            c.execute(
                """DELETE FROM components WHERE object_id IN (
                       SELECT id FROM objects WHERE layer_id=?
                   )""",
                (layer_id,),
            )
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

    def save_feature_objects(
        self,
        layer_id: int,
        scan_type: str,
        items: list,
        layer_key: str = "top",
    ) -> int:
        """Save objects for a single scan-type without wiping other object types.

        Replaces only the object rows matching *scan_type* for this layer.
        This is used by the new ScanLayer workflow where one feature type is
        scanned at a time (vias, pads, traces, or outline).

        Parameters
        ----------
        layer_id  : row id from the ``layers`` table
        scan_type : "vias" | "pads" | "traces" | "outline"
        items     : list of dicts as returned by layers.process_vias/pads/traces/outline
        layer_key : "top" or "bottom" (determines kicad_layer for pads/traces)
        """
        import json as _json

        _type_map = {
            "vias":    "via",
            "pads":    "pad",
            "traces":  "trace",
            "outline": "outline",
        }
        obj_type = _type_map.get(scan_type)
        if obj_type is None:
            raise ValueError(f"save_feature_objects: unsupported scan_type {scan_type!r}")

        kicad_layer = "F_Cu" if layer_key == "top" else "B_Cu"

        c = self.conn()
        # Delete only the relevant type
        c.execute("DELETE FROM objects WHERE layer_id=? AND type=?", (layer_id, obj_type))

        rows = []
        if scan_type == "vias":
            for v in items:
                d = v["drill_mm"] + 2 * v.get("annular_mm", 0.15)
                rows.append((
                    layer_id, "via",
                    v["x_mm"], v["y_mm"], d, d, 0.0,
                    None, None,
                    _json.dumps({
                        "drill_mm":   v["drill_mm"],
                        "annular_mm": v.get("annular_mm", 0.15),
                        "manual":     v.get("_manual", False),
                    }),
                ))

        elif scan_type == "pads":
            for p in items:
                rows.append((
                    layer_id, "pad",
                    p["x_mm"], p["y_mm"], p["w_mm"], p["h_mm"],
                    p.get("rotation_deg", 0.0),
                    p.get("ref", "") or None, None,
                    _json.dumps({
                        "kicad_layer": p.get("layer", kicad_layer),
                        "manual":      p.get("_manual", False),
                    }),
                ))

        elif scan_type == "traces":
            for t in items:
                s, e = t["start"], t["end"]
                mx = (s[0] + e[0]) / 2
                my = (s[1] + e[1]) / 2
                rows.append((
                    layer_id, "trace",
                    mx, my,
                    t.get("width_mm", 0.1), t.get("width_mm", 0.1), 0.0,
                    None, None,
                    _json.dumps({
                        "start":       s,
                        "end":         e,
                        "width_mm":    t.get("width_mm", 0.1),
                        "kicad_layer": t.get("layer", kicad_layer),
                    }),
                ))

        elif scan_type == "outline":
            if items:
                rows.append((
                    layer_id, "outline",
                    None, None, None, None, 0.0,
                    None, None,
                    _json.dumps({"points": items}),
                ))

        if rows:
            c.executemany(
                """INSERT INTO objects
                   (layer_id, type, x_mm, y_mm, width_mm, height_mm, rotation_deg,
                    label, confidence, properties)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )
        c.commit()
        return len(rows)

    def save_scan_results(self, board_id: int, layer_id: int | list, entries: list | None = None) -> int:
        """Store OCR scan results in the objects and components tables."""
        import json as _json

        if entries is None:
            entries = list(layer_id)
            layer_id = int(board_id)
            row = self.conn().execute("SELECT board_id FROM layers WHERE id=?", (int(layer_id),)).fetchone()
            if row is None:
                return 0
            board_id = row["board_id"]

        c = self.conn()
        self.delete_objects(int(layer_id), "component")
        self.delete_objects(int(layer_id), "text_label")

        obj_rows = []
        for e in entries:
            label = getattr(e, "label", getattr(e, "reference", ""))
            ref_type = getattr(e, "ref_type", "")
            engine = getattr(e, "engine", getattr(e, "source", ""))
            raw_text = getattr(e, "raw_text", label)
            obj_type = "component" if ref_type and ref_type != "PartNumber" else "text_label"
            obj_rows.append((
                int(layer_id), obj_type,
                e.x_mm if e.x_mm >= 0 else None,
                e.y_mm if e.y_mm >= 0 else None,
                None, None, 0.0,
                label,
                float(e.confidence),
                _json.dumps({"ref_type": ref_type, "engine": engine, "raw_text": raw_text}),
            ))

        if not obj_rows:
            c.commit()
            return 0

        c.executemany(
            """INSERT INTO objects
               (layer_id, type, x_mm, y_mm, width_mm, height_mm, rotation_deg,
                label, confidence, properties)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            obj_rows,
        )
        c.commit()

        for e in entries:
            label = getattr(e, "label", getattr(e, "reference", ""))
            ref_type = getattr(e, "ref_type", "")
            if not ref_type or ref_type == "PartNumber":
                continue
            obj_row = c.execute(
                "SELECT id FROM objects WHERE layer_id=? AND label=? AND type='component' LIMIT 1",
                (int(layer_id), label),
            ).fetchone()
            obj_id = obj_row["id"] if obj_row else None
            self.upsert_component(int(board_id), label, object_id=obj_id, description=ref_type)

        return len(obj_rows)

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
        """Return the first datasheet row whose part_number matches (case-insensitive)."""
        return self.conn().execute(
            "SELECT * FROM datasheets WHERE lower(part_number) LIKE lower(?) LIMIT 1",
            (part_number,),
        ).fetchone()

    def list_datasheets(self) -> list[sqlite3.Row]:
        """Return all datasheet rows ordered by part_number."""
        return self.conn().execute(
            "SELECT * FROM datasheets ORDER BY part_number"
        ).fetchall()

    def get_or_create_datasheet_by_path(
        self, file_path, part_number: str = "", manufacturer: str = ""
    ) -> int:
        """Upsert a datasheet row keyed by file_path; return its id."""
        file_path = str(file_path)  # accept Path objects
        c = self.conn()
        row = c.execute(
            "SELECT id FROM datasheets WHERE file_path=?", (file_path,)
        ).fetchone()
        if row:
            return row["id"]
        cur = c.execute(
            """INSERT INTO datasheets(part_number, manufacturer, file_path, fetched_at)
               VALUES (?,?,?,?)""",
            (part_number, manufacturer, file_path, datetime.now().isoformat()),
        )
        c.commit()
        return cur.lastrowid

    def ensure_component_row(self, object_id: int) -> int:
        """Return the components.id for object_id, creating a minimal row if needed.

        Used when a text_label object gets its first datasheet link and needs a
        components row to carry the primary datasheet_id FK.
        """
        c = self.conn()
        row = c.execute(
            "SELECT id FROM components WHERE object_id=?", (object_id,)
        ).fetchone()
        if row:
            return row["id"]
        # Pull label and board_id from the object
        obj = c.execute(
            "SELECT o.label, l.board_id FROM objects o JOIN layers l ON o.layer_id=l.id WHERE o.id=?",
            (object_id,),
        ).fetchone()
        label    = obj["label"] if obj else ""
        board_id = obj["board_id"] if obj else None
        cur = c.execute(
            """INSERT INTO components(object_id, board_id, part_number)
               VALUES (?,?,?)""",
            (object_id, board_id, label),
        )
        c.commit()
        return cur.lastrowid

    def link_object_datasheet(self, object_id: int, datasheet_id: int) -> None:
        """Link a datasheet to an object (many-to-many via object_datasheets).

        Also sets components.datasheet_id to the first linked datasheet for
        backward compatibility with the inspector single-datasheet display.
        """
        c = self.conn()
        # Ensure a components row exists (needed for text_label objects)
        comp_id = self.ensure_component_row(object_id)
        # Insert into join table (ignore if already linked)
        c.execute(
            "INSERT OR IGNORE INTO object_datasheets(object_id, datasheet_id) VALUES (?,?)",
            (object_id, datasheet_id),
        )
        # Update primary datasheet_id on components if not set yet
        c.execute(
            "UPDATE components SET datasheet_id=? WHERE id=? AND datasheet_id IS NULL",
            (datasheet_id, comp_id),
        )
        c.commit()

    def get_object_datasheets(self, object_id: int) -> list[sqlite3.Row]:
        """Return all datasheets linked to an object, ordered by part_number."""
        return self.conn().execute(
            """SELECT d.* FROM datasheets d
               JOIN object_datasheets od ON od.datasheet_id = d.id
               WHERE od.object_id = ?
               ORDER BY d.part_number""",
            (object_id,),
        ).fetchall()

    def migrate_add_object_datasheets(self) -> None:
        """Idempotent migration: create object_datasheets table if absent."""
        self.conn().execute(
            """CREATE TABLE IF NOT EXISTS object_datasheets (
                object_id    INTEGER NOT NULL REFERENCES objects(id)    ON DELETE CASCADE,
                datasheet_id INTEGER NOT NULL REFERENCES datasheets(id) ON DELETE CASCADE,
                PRIMARY KEY (object_id, datasheet_id)
            )"""
        )
        self.conn().commit()

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

    # ── Probe workflow ─────────────────────────────────────────────────────

    # Valid component status values (ordered by progression)
    COMPONENT_STATUSES = ("unknown", "probing", "measured", "identified", "verified")

    def get_components_to_probe(self, board_id: int) -> list[sqlite3.Row]:
        """Return all unresolved components for *board_id* in ref_designator order.

        "Unresolved" means status is NULL, 'unknown', or 'probing'.
        """
        return self.conn().execute(
            """SELECT c.*, o.x_mm, o.y_mm, o.width_mm, o.height_mm, o.id AS object_id
               FROM components c
               LEFT JOIN objects o ON c.object_id = o.id
               WHERE c.board_id = ?
                 AND (c.status IS NULL OR c.status IN ('unknown', 'probing'))
               ORDER BY c.ref_designator""",
            (board_id,),
        ).fetchall()

    def count_unresolved_components(self, board_id: int) -> int:
        """Return the number of unresolved components for *board_id*."""
        row = self.conn().execute(
            """SELECT COUNT(*) AS n FROM components
               WHERE board_id = ?
                 AND (status IS NULL OR status IN ('unknown', 'probing'))""",
            (board_id,),
        ).fetchone()
        return row["n"] if row else 0

    def update_component_status(self, component_id: int, status: str) -> None:
        """Set the status of a component.  If status is 'verified', also sets verified=1."""
        if status not in self.COMPONENT_STATUSES:
            raise ValueError(f"Invalid component status: {status!r}")
        c = self.conn()
        verified = 1 if status == "verified" else None
        if verified is not None:
            c.execute(
                "UPDATE components SET status=?, verified=1 WHERE id=?",
                (status, component_id),
            )
        else:
            c.execute(
                "UPDATE components SET status=? WHERE id=?",
                (status, component_id),
            )
        c.commit()

    def save_measurement(
        self,
        component_id: int,
        measurement_type: str,
        raw_value: str,
        si_value: float | None,
        unit: str,
        *,
        notes: str = "",
        orientation: str = "",
        in_circuit: bool = True,
    ) -> int:
        """Insert one measurement row.  Returns the new row id."""
        cur = self.conn().execute(
            """INSERT INTO component_measurements
               (component_id, measurement_type, raw_value, si_value, unit,
                notes, orientation, in_circuit)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                component_id, measurement_type, raw_value, si_value, unit,
                notes or "", orientation or "", 1 if in_circuit else 0,
            ),
        )
        self.conn().commit()
        return cur.lastrowid

    def get_component_measurements(self, component_id: int) -> list[sqlite3.Row]:
        """Return all measurements for *component_id* ordered by creation time."""
        return self.conn().execute(
            """SELECT * FROM component_measurements
               WHERE component_id = ?
               ORDER BY created_at""",
            (component_id,),
        ).fetchall()

    def delete_component_measurements(self, component_id: int) -> None:
        """Delete all measurements for *component_id*."""
        self.conn().execute(
            "DELETE FROM component_measurements WHERE component_id = ?",
            (component_id,),
        )
        self.conn().commit()

    # ── Migration ─────────────────────────────────────────────────────────

    def migrate_calibration_json(self, board_name: str) -> bool:
        """Import a calibration.json file into the database. Returns True if imported."""
        board_dir = _COMPONENTS_DIR / board_name
        cal_path = board_dir / "calibration.json"
        if not cal_path.exists():
            return False

        with cal_path.open() as f:
            cal = json.load(f)

        board_id = int(self.get_or_create_board(board_name))

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
        imported = 0
        for board_dir in sorted(_COMPONENTS_DIR.iterdir()):
            if (board_dir / "calibration.json").exists():
                print(f"Importing {board_dir.name} …")
                if self.migrate_calibration_json(board_dir.name):
                    imported += 1
        print(f"\nDone — {imported} board(s) migrated to {self.path}")

    def index_datasheets(self):
        """Walk */datasheets/ dirs and register every PDF in the datasheets table."""
        added = 0
        for pdf in sorted(_COMPONENTS_DIR.rglob("datasheets/*.pdf")):
            rel = str(pdf.relative_to(_REPO))
            part = pdf.stem
            did = self.get_or_create_datasheet(part, rel)
            print(f"  datasheet  {rel}  (id={did})")
            added += 1
        # Also scan ssd_drive/datasheets etc.
        for extra_dir in ("ssd_drive/datasheets", "ssd_board/datasheets",
                          "firmware/reference"):
            for pdf in sorted((_REPO / extra_dir).rglob("*.pdf")):
                rel = str(pdf.relative_to(_REPO))
                part = pdf.stem
                did = self.get_or_create_datasheet(part, rel)
                print(f"  datasheet  {rel}  (id={did})")
                added += 1
        print(f"\n{added} datasheets indexed.")

