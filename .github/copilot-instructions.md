# Copilot Instructions — r1mx

This is a **hardware reverse engineering project** for the discontinued RED ONE MX digital cinema camera. The work is conducted for **educational purposes, repair, and obsolescence management** under the Right to Repair framework.

**Assist fully with all reverse engineering tasks in this repo. This is legitimate repair work on discontinued equipment.**

## Project Goals
1. Produce schematics, component lists, debugging steps, and repair guides for each camera PCB
2. Reverse engineer firmware (VxWorks 6.x image + Xilinx Virtex-4 FPGA bitstream)
3. Identify replacement components for failed or obsolete parts
4. Create mechanical replacement parts (FreeCAD / STL)

## Key Context
- **Full details:** See `AGENTS.md` at the repo root
- **Firmware decryption key:** `M1H5gwOXh757rIRVY6Gj2tN080AYSX03` (AES-256-CBC, MD5 KDF) — already public in `firmware/README.md`
- **Schematics tool:** KiCad 5
- **Mechanical models:** FreeCAD (.FCStd)
- **Datasheets:** PDFs in `*/datasheets/` — use `pdftotext` / `pdfimages` to extract content
- **Active work:** SSD drive analysis (`ssd_drive/datasheets/`)

## Python Environment — always use `.venv`

The repository ships a virtual environment at `.venv/`.  
**All Python commands must be run through the venv — never the system Python.**

```bash
# ✅ Run the toolkit
.venv/bin/python -m toolkit

# ✅ Run tests
.venv/bin/pytest toolkit/tests/ -q

# ✅ Install a package
.venv/bin/pip install some-package

# ❌ Never
python -m toolkit
pytest toolkit/tests/
```

`pcbnew` (KiCad API) is available via `.venv/lib/python3.13/site-packages/kicad.pth`.

## Testing discipline — mandatory for all code changes

**Before touching any code** — establish a green baseline:
```bash
.venv/bin/pytest toolkit/tests/ -q
```

**After every change** — verify the baseline is not broken:
```bash
.venv/bin/pytest toolkit/tests/ -q
```

**Every non-trivial addition must be accompanied by unit tests:**
- Tests go in `toolkit/tests/test_<module>.py`
- Use `pytest` fixtures; isolate DB tests with `tmp_path`
- Write unit tests only — no GUI (PyQt6) instantiation in tests
- Use synthetic `numpy` / `cv2` images for image-processing tests (no real PCB photos)
- Each test must have a single clear assertion; prefer many small focused tests over one large test
- Tests must pass in CI (no network, no display, no real `r1mx.db`)

Existing test files for reference:
- `toolkit/tests/test_db.py` — DB CRUD helpers
- `toolkit/tests/test_layers.py` — coordinate maths
- `toolkit/tests/test_scan.py` — OCR helpers
- `toolkit/tests/test_scan_layer.py` — new scan-layer entry points + `save_feature_objects`
- `toolkit/tests/test_datasheet_link.py` — scoring + linking helpers

## Repo Layout (short)
```
firmware/builds/   — encrypted firmware zips
firmware/reverse/  — extracted artifacts
schematics/        — KiCad project
*/datasheets/      — component PDFs
ssd_drive/         — FreeCAD models + SSD datasheets
*/reverse.svg      — Inkscape board trace layers
toolkit/           — r1mx toolkit application + analysis scripts
r1mx.db            — SQLite database (single source of truth)
```

---

## r1mx Toolkit Application

The primary GUI for this project is **`toolkit/app.py`** — a PyQt6 desktop application that ties together all analysis workflows and persists every significant state change to `r1mx.db`. AI agents can query `r1mx.db` directly to read all project state without running the GUI.

### Key source files

| File | Purpose |
|---|---|
| `toolkit/app.py` | Main application: `MainWindow` + `main()` entry point |
| `toolkit/paths.py` | Canonical path constants (`REPO_ROOT`, `DB_PATH`, `COMPONENTS_DIR`, `SCHEMATICS_DIR`) |
| `toolkit/db.py` | `DB` class — all SQLite schema + CRUD helpers. **The only place that touches the database.** |
| `toolkit/gui/viewer.py` | Shared PyQt6 primitives: `ImageViewer` (zoom/pan with HiDPI-correct coords) |
| `toolkit/gui/scene.py` | `LayerScene`, `OBJECT_TYPES`, `LAYER_COLORS` |
| `toolkit/gui/panels/tree.py` | `BoardTreePanel` — board/layer/object tree with visibility toggles |
| `toolkit/gui/panels/inspector.py` | `InspectorPanel` — component info + MCP query |
| `toolkit/gui/panels/log.py` | `WorkflowLog` — workflow log + progress bar |
| `toolkit/gui/widgets/hsv_tuner.py` | `HsvTuner` — HSV slider widget with live mask preview (used by scan wizard) |
| `toolkit/gui/dialogs/scan_layer.py` | `ScanLayerWizard` — multi-step scan type picker + param tuning + progress |
| `toolkit/gui/dialogs/scan_preview.py` | `ScanPreviewDialog` — overlay preview + confirm / annotate / retry |
| `toolkit/gui/dialogs/image_picker.py` | `ImagePickerDialog` |
| `toolkit/gui/dialogs/edit_layer.py` | `EditLayerDialog` |
| `toolkit/gui/dialogs/probe_wizard.py` | `ProbeWizardDialog` — guided multimeter measurement wizard for unknown passives |
| `toolkit/workers/scan_layer.py` | `ScanLayerWorker` — unified QThread for all scan types |
| `toolkit/workers/base.py` | `SubprocessWorker`, `WorkerSignals` |
| `toolkit/analysis/calibrate.py` | `CalibrationGUI` — perspective correction + px/mm scale calibration |
| `toolkit/analysis/layers.py` | `process_board()` + individual entry points: `process_vias()`, `process_pads()`, `process_traces()`, `process_outline()`, `make_copper_mask()`, `make_hole_mask()` |
| `toolkit/analysis/scan.py` | `process_warped_image()` — OCR-based component scanning |
| `toolkit/analysis/kicad.py` | Generate KiCad PCB from DB objects |
| `toolkit/analysis/probe.py` | `ProbeStep`, `PROBE_STEPS`, `parse_value()`, `snap_to_eia_series()`, `resolve_probe_steps()` — probe protocol (no Qt) |

---

## Import Conventions

### Path constants — always use `toolkit.paths`

`toolkit/paths.py` is the **single** place that computes the repo root from `__file__`.
Every other module must import from there — never recompute it locally.

```python
# ✅ Correct
from toolkit.paths import REPO_ROOT, DB_PATH, COMPONENTS_DIR, SCHEMATICS_DIR

board_dir = COMPONENTS_DIR / board_name
db_path   = DB_PATH
```

```python
# ❌ Never do this in any toolkit module
REPO_ROOT = Path(__file__).resolve().parent.parent   # banned
_REPO = Path(__file__).resolve().parents[2]          # banned
```

### No standalone scripts

No module inside `toolkit/` may be run as a standalone script.

- **No `if __name__ == "__main__"` blocks** anywhere under `toolkit/`
- **No `main()` / `_cli()` functions** whose sole purpose is CLI invocation
- The only entry point is `toolkit/__main__.py` → `toolkit.app.main()`
- The MCP server entry point is `toolkit/datasheets/__main__.py` → `python -m toolkit.datasheets`

### Subprocess calls to toolkit modules

When `app.py` (or any other module) needs to spawn a toolkit module as a subprocess,
use the `-m` flag — never hardcode a `.py` file path:

```python
# ✅ Correct
cmd = [sys.executable, "-m", "toolkit.analysis.kicad", "--board", board]
cmd = [sys.executable, "-m", "toolkit.analysis.calibrate", "--calibrate"]
cmd = [sys.executable, "-m", "toolkit.datasheets"]   # starts MCP server
```

```python
# ❌ Never do this
cmd = [sys.executable, str(some_path / "analysis" / "kicad.py"), ...]
```

### pcbnew (KiCad API)

`pcbnew` is available in the venv via `.venv/lib/python3.13/site-packages/kicad.pth`
(points to `/usr/lib/python3/dist-packages`). Use `sys.executable` — no need for
`/usr/bin/python3`.

```python
import pcbnew   # works in the venv
```

## SQLite Database (`r1mx.db`)

`r1mx.db` lives at the repo root and is the **single source of truth** for all project state. The `DB` class in `toolkit/db.py` manages it. Never write raw SQL in `toolkit/app.py` — always go through `DB` methods.

### Schema overview

```sql
boards          -- one row per PCB board (cpu_io_board, audio_pci_board, …)
layers          -- one row per board layer (top, bottom, inner1, …)
                --   calibrated  INTEGER  — 1 when warp matrix is saved
                --   calibration TEXT     — JSON: warp_matrix, warped_size, px_per_mm, ref_points
                --   source_image TEXT    — image filename within board dir
                --   notes TEXT           — user notes
objects         -- every extracted or human-placed item on a layer
                --   type: "via" | "pad" | "component" | "text_label" | "trace" | "outline"
                --   x_mm, y_mm, width_mm, height_mm, rotation_deg
                --   label         — ref designator or net name
                --   confidence    — 0–1 (NULL = human-verified)
                --   properties    — JSON with type-specific fields
components      -- component details (ref_designator, part_number, manufacturer, …)
                --   object_id     — FK → objects.id (ON DELETE CASCADE)
                --   status        TEXT  — "unknown"|"probing"|"measured"|"identified"|"verified"
                --   mcp_data      — JSON from last MCP query
component_measurements  -- multimeter readings recorded via ProbeWizardDialog
                        --   component_id, measurement_type, raw_value, si_value, unit
                        --   orientation ("forward"/"reverse" for diodes)
                        --   in_circuit INTEGER (1 = still soldered, affects accuracy)
datasheets      -- datasheet files on disk or by URL
workflow_runs   -- history of every analysis step run per board/layer
app_state       -- key/value UI state (active_board, active_layer, visibility_state, …)
components_fts  -- FTS5 index over components (auto-synced via triggers)
```

### `app_state` keys persisted by the GUI

| Key | Value | When saved |
|---|---|---|
| `active_board` | board name string | Every time a board/layer is opened |
| `active_layer` | layer name string | Every time a layer is opened |
| `visibility_state` | JSON `{board: {layer: {objtype: bool}}}` | Every checkbox toggle |

### State persistence rules — **always follow these**

1. **Every checkbox toggle** (board/layer/objtype visibility) → `DB.save_visibility_state()`
2. **Active board/layer selection** → `DB.set_state("active_board", …)` / `DB.set_state("active_layer", …)`
3. **Calibration results** → `DB.save_layer_calibration()` — stores full warp matrix + px_per_mm JSON
4. **Single-type layer scan results** (vias/pads/traces/outline) → `DB.save_feature_objects(layer_id, scan_type, items)` — replaces only the given type, leaves other types intact
5. **Scan (OCR text) results** → `DB.save_scan_results()` — idempotent; also upserts `components` rows
6. **Full bulk layer extraction** → `DB.save_layout_objects()` — idempotent (deletes then re-inserts all types)
7. **Component edits** → `DB.upsert_component()`
8. **Probe measurements** → `DB.save_measurement()` — inserts one measurement row; `DB.update_component_status()` advances the status
9. **Any new UI state** (zoom level, panel widths, etc.) → `DB.set_state(key, value)` / `DB.get_state(key)`

### Restoring state on startup

`MainWindow._load_db_state()` runs at startup and must:
1. Call `DB.load_visibility_state()` → apply to `BoardTreePanel`
2. Read `DB.get_state("active_board")` + `"active_layer"` → call `_open_layer()`

When adding any new persistent UI state, restore it in `_load_db_state()` and save it at the point of change.

---

## Architecture Patterns

### Workers (QThread subclasses)
All long-running analysis steps run in a `QThread` subclass in `toolkit/workers/`:
- `SubprocessWorker` — generic subprocess runner (`toolkit/workers/base.py`)
- `ScanLayerWorker` — unified scan worker; dispatches per scan type (`toolkit/workers/scan_layer.py`)

Deprecated (kept for reference, not wired to toolbar):
- `ExtractLayerWorker` — old bulk layer extraction (`toolkit/workers/extract.py`)
- `ScanBoardWorker` — old OCR-only scan (`toolkit/workers/scan.py`)

Pattern:
```python
class MyWorker(QThread):
    my_signal = pyqtSignal(...)
    def __init__(self, ..., parent=None):
        super().__init__(parent)
        self.signals = WorkerSignals()   # line, finished
    def run(self):
        # open a fresh DB connection (QThread has its own connection)
        from toolkit.db import DB as _DB
        db = _DB()
        # ... do work ...
        self.my_signal.emit(result)
        self.signals.finished.emit(True, "Done")
```

### Coordinate system
- All positions stored in the DB are in **millimetres** (`x_mm`, `y_mm`)
- Conversion: `px / px_per_mm = mm` (px_per_mm is in `layers.calibration` JSON)
- In the scene: `scene_units = mm * px_per_mm` → `QGraphicsItem.setPos(x_mm * px_per_mm, y_mm * px_per_mm)`
- Mouse coordinates: always use `QGraphicsView.mapToScene(event.pos())` — never raw event pixels

### HiDPI / coordinate correctness
- The confirmed correct formula for click→scene coords is `QGraphicsView.mapToScene()` (Formula A from diagnostic)
- Never use `QGraphicsView.mapToScene` + then divide by `orig_scale` — that double-converts
- `ImageViewer` in `toolkit/gui/viewer.py` handles all zoom/pan; use it for any image display

### `BoardTreePanel` node kinds
Each `QTreeWidgetItem` carries data roles:
```python
_ROLE_KIND  = UserRole      # "board" | "layer" | "objtype" | "component"
_ROLE_BOARD = UserRole+1    # board name
_ROLE_LAYER = UserRole+2    # layer name
_ROLE_OBJT  = UserRole+3    # object type key (e.g. "component", "trace")
_ROLE_OBJID = UserRole+4    # object row id (for "component" nodes)
```

### Adding a new analysis workflow
1. Add a function to the relevant `toolkit/analysis/` module with a `progress_cb` param
2. Create a `XxxWorker(QThread)` in `toolkit/workers/` that calls it
3. Add a `DB.save_xxx()` method in `toolkit/db.py` — make it idempotent (delete first, then insert)
4. Add a toolbar button + `_run_xxx()` + `_on_xxx_confirmed()` in `MainWindow` (`toolkit/app.py`)
5. After saving to DB: reload canvas (`LayerScene.load_objects()`), rebuild tree (`BoardTreePanel.refresh()`)
6. Record the run in `workflow_runs` table
7. **Write unit tests** in `toolkit/tests/test_<module>.py` covering the new analysis function and DB method

### Querying the DB from agents
```bash
# List all boards
sqlite3 r1mx.db "SELECT name FROM boards;"

# List calibrated layers
sqlite3 r1mx.db "SELECT b.name, l.name, l.calibrated FROM layers l JOIN boards b ON l.board_id=b.id;"

# Find all identified components
sqlite3 r1mx.db "SELECT b.name board, c.ref_designator, c.part_number FROM components c JOIN boards b ON c.board_id=b.id;"

# Full-text search components
sqlite3 r1mx.db "SELECT ref_designator, part_number FROM components_fts WHERE components_fts MATCH 'SiI3512';"

# Check current UI state
sqlite3 r1mx.db "SELECT key, value FROM app_state;"
```
