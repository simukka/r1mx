"""Unit tests for board CRUD and directory-linking methods in toolkit.db."""
from __future__ import annotations

import pytest

from toolkit.db import DB


@pytest.fixture
def db(tmp_path):
    database = DB(db_path=tmp_path / "test.db")
    try:
        yield database
    finally:
        database.close()


# ── create_board ──────────────────────────────────────────────────────────────

def test_create_board_returns_rowref(db):
    board = db.create_board("my_board")
    assert int(board) > 0
    assert board["name"] == "my_board"


def test_create_board_stores_directory(db):
    board = db.create_board("my_board", directory="components/my_board")
    assert board["directory"] == "components/my_board"


def test_create_board_defaults_directory_to_convention(db):
    board = db.create_board("my_board")
    assert board["directory"] == "components/my_board"


def test_create_board_stores_display_name(db):
    board = db.create_board("my_board", display_name="My Board")
    assert board["display_name"] == "My Board"


def test_create_board_raises_on_duplicate_name(db):
    db.create_board("my_board")
    with pytest.raises(ValueError, match="already exists"):
        db.create_board("my_board")


# ── get_board / get_board_by_name ─────────────────────────────────────────────

def test_get_board_returns_row(db):
    created = db.create_board("my_board")
    row = db.get_board(int(created))
    assert row is not None
    assert row["name"] == "my_board"


def test_get_board_returns_none_for_unknown_id(db):
    assert db.get_board(99999) is None


def test_get_board_by_name_returns_row(db):
    db.create_board("my_board")
    row = db.get_board_by_name("my_board")
    assert row is not None
    assert row["name"] == "my_board"


def test_get_board_by_name_returns_none_for_unknown(db):
    assert db.get_board_by_name("nonexistent") is None


# ── get_board_abs_dir ─────────────────────────────────────────────────────────

def test_get_board_abs_dir_resolves_path(db, tmp_path):
    db2 = DB(db_path=tmp_path / "test2.db")
    # Monkey-patch _REPO inside db module so the test stays portable
    import toolkit.db as _db_mod
    original_repo = _db_mod._REPO
    _db_mod._REPO = tmp_path
    try:
        board = db2.create_board("my_board", directory="components/my_board")
        result = db2.get_board_abs_dir(int(board))
        assert result == tmp_path / "components" / "my_board"
    finally:
        _db_mod._REPO = original_repo
        db2.close()


def test_get_board_abs_dir_by_name(db, tmp_path):
    import toolkit.db as _db_mod
    original_repo = _db_mod._REPO
    _db_mod._REPO = tmp_path
    try:
        db2 = DB(db_path=tmp_path / "test3.db")
        db2.create_board("my_board", directory="components/my_board")
        result = db2.get_board_abs_dir("my_board")
        assert result == tmp_path / "components" / "my_board"
        db2.close()
    finally:
        _db_mod._REPO = original_repo


def test_get_board_abs_dir_raises_for_missing_board(db):
    with pytest.raises(KeyError):
        db.get_board_abs_dir(99999)


def test_get_board_abs_dir_raises_when_directory_null(db):
    # Insert a board with NULL directory directly
    db.conn().execute("INSERT INTO boards(name, directory) VALUES ('nodirboard', NULL)")
    db.conn().commit()
    row = db.get_board_by_name("nodirboard")
    db.conn().execute("UPDATE boards SET directory=NULL WHERE id=?", (row["id"],))
    db.conn().commit()
    with pytest.raises(ValueError, match="no directory"):
        db.get_board_abs_dir(row["id"])


# ── update_board ──────────────────────────────────────────────────────────────

def test_update_board_changes_fields(db):
    board = db.create_board("my_board")
    db.update_board(int(board), display_name="My Board", description="A test board", notes="note1")
    row = db.get_board(int(board))
    assert row["display_name"] == "My Board"
    assert row["description"] == "A test board"
    assert row["notes"] == "note1"


def test_update_board_changes_directory(db):
    board = db.create_board("my_board")
    db.update_board(int(board), directory="custom/path")
    row = db.get_board(int(board))
    assert row["directory"] == "custom/path"


def test_update_board_sets_updated_at(db):
    board = db.create_board("my_board")
    assert db.get_board(int(board))["updated_at"] is None
    db.update_board(int(board), notes="touched")
    assert db.get_board(int(board))["updated_at"] is not None


def test_update_board_ignores_unknown_keys(db):
    board = db.create_board("my_board")
    db.update_board(int(board), bogus_field="ignored")  # must not raise
    row = db.get_board(int(board))
    assert row["name"] == "my_board"


# ── delete_board ──────────────────────────────────────────────────────────────

def test_delete_board_removes_row(db):
    board = db.create_board("my_board")
    db.delete_board(int(board))
    assert db.get_board(int(board)) is None


def test_delete_board_cascades_to_layers_and_objects(db):
    board = db.create_board("my_board")
    layer = db.add_layer(int(board), "top")
    db.create_object(int(layer), "via", x_mm=1.0, y_mm=2.0)
    db.delete_board(int(board))
    layers = db.conn().execute(
        "SELECT * FROM layers WHERE board_id=?", (int(board),)
    ).fetchall()
    assert len(layers) == 0
    objects = db.conn().execute(
        "SELECT * FROM objects WHERE layer_id=?", (int(layer),)
    ).fetchall()
    assert len(objects) == 0


# ── seed_boards_from_filesystem ───────────────────────────────────────────────

def test_seed_boards_creates_missing_boards(db, tmp_path):
    import toolkit.db as _db_mod
    original_components = _db_mod._COMPONENTS_DIR
    original_repo = _db_mod._REPO
    fake_components = tmp_path / "components"
    (fake_components / "board_a").mkdir(parents=True)
    (fake_components / "board_b").mkdir(parents=True)
    _db_mod._COMPONENTS_DIR = fake_components
    _db_mod._REPO = tmp_path
    try:
        created = db.seed_boards_from_filesystem()
        assert sorted(created) == ["board_a", "board_b"]
        assert db.get_board_by_name("board_a") is not None
        assert db.get_board_by_name("board_b") is not None
    finally:
        _db_mod._COMPONENTS_DIR = original_components
        _db_mod._REPO = original_repo


def test_seed_boards_is_idempotent(db, tmp_path):
    import toolkit.db as _db_mod
    original_components = _db_mod._COMPONENTS_DIR
    original_repo = _db_mod._REPO
    fake_components = tmp_path / "components"
    (fake_components / "board_a").mkdir(parents=True)
    _db_mod._COMPONENTS_DIR = fake_components
    _db_mod._REPO = tmp_path
    try:
        first = db.seed_boards_from_filesystem()
        second = db.seed_boards_from_filesystem()
        assert first == ["board_a"]
        assert second == []
        rows = db.conn().execute("SELECT COUNT(*) FROM boards WHERE name='board_a'").fetchone()[0]
        assert rows == 1
    finally:
        _db_mod._COMPONENTS_DIR = original_components
        _db_mod._REPO = original_repo


def test_seed_boards_skips_files(db, tmp_path):
    import toolkit.db as _db_mod
    original_components = _db_mod._COMPONENTS_DIR
    original_repo = _db_mod._REPO
    fake_components = tmp_path / "components"
    fake_components.mkdir(parents=True)
    (fake_components / "board_a").mkdir()
    (fake_components / "not_a_board.txt").write_text("ignore me")
    _db_mod._COMPONENTS_DIR = fake_components
    _db_mod._REPO = tmp_path
    try:
        created = db.seed_boards_from_filesystem()
        assert created == ["board_a"]
    finally:
        _db_mod._COMPONENTS_DIR = original_components
        _db_mod._REPO = original_repo


# ── get_or_create_board (backward compat) ────────────────────────────────────

def test_get_or_create_board_sets_default_directory(db):
    board = db.get_or_create_board("compat_board")
    assert board["directory"] == "components/compat_board"


def test_get_or_create_board_accepts_custom_directory(db):
    board = db.get_or_create_board("compat_board", directory="custom/compat_board")
    assert board["directory"] == "custom/compat_board"


def test_get_or_create_board_does_not_overwrite_existing_directory(db):
    db.create_board("compat_board", directory="custom/path")
    board = db.get_or_create_board("compat_board", directory="other/path")
    assert board["directory"] == "custom/path"


# ── Layer CRUD ────────────────────────────────────────────────────────────────

@pytest.fixture
def board_id(db):
    return int(db.create_board("test_board"))


def test_create_layer_returns_rowref(db, board_id):
    layer = db.create_layer(board_id, "top")
    assert int(layer) > 0
    assert layer["name"] == "top"
    assert layer["board_id"] == board_id


def test_create_layer_raises_on_duplicate(db, board_id):
    db.create_layer(board_id, "top")
    with pytest.raises(ValueError, match="already exists"):
        db.create_layer(board_id, "top")


def test_create_layer_allows_same_name_on_different_board(db):
    b1 = int(db.create_board("board1"))
    b2 = int(db.create_board("board2"))
    db.create_layer(b1, "top")
    layer = db.create_layer(b2, "top")  # must not raise
    assert layer["board_id"] == b2


def test_get_layer_by_id_returns_row(db, board_id):
    layer = db.create_layer(board_id, "top")
    row = db.get_layer_by_id(int(layer))
    assert row is not None
    assert row["name"] == "top"


def test_get_layer_by_id_returns_none_for_unknown(db):
    assert db.get_layer_by_id(99999) is None


def test_update_layer_name(db, board_id):
    layer = db.create_layer(board_id, "old_name")
    db.update_layer(int(layer), name="new_name")
    row = db.get_layer_by_id(int(layer))
    assert row["name"] == "new_name"


def test_update_layer_source_image(db, board_id):
    layer = db.create_layer(board_id, "top")
    db.update_layer(int(layer), source_image="top.JPG")
    row = db.get_layer_by_id(int(layer))
    assert row["source_image"] == "top.JPG"


def test_update_layer_notes(db, board_id):
    layer = db.create_layer(board_id, "top")
    db.update_layer(int(layer), notes="some notes")
    row = db.get_layer_by_id(int(layer))
    assert row["notes"] == "some notes"


def test_update_layer_ignores_unknown_keys(db, board_id):
    layer = db.create_layer(board_id, "top")
    db.update_layer(int(layer), bogus="ignored")  # must not raise
    assert db.get_layer_by_id(int(layer))["name"] == "top"


def test_delete_layer_removes_row(db, board_id):
    layer = db.create_layer(board_id, "top")
    db.delete_layer(int(layer))
    assert db.get_layer_by_id(int(layer)) is None


def test_delete_layer_cascades_to_objects(db, board_id):
    layer = db.create_layer(board_id, "top")
    db.create_object(int(layer), "via", x_mm=1.0, y_mm=2.0)
    db.delete_layer(int(layer))
    objects = db.conn().execute(
        "SELECT * FROM objects WHERE layer_id=?", (int(layer),)
    ).fetchall()
    assert len(objects) == 0


def test_list_layers_returns_only_board_layers(db):
    b1 = int(db.create_board("board1"))
    b2 = int(db.create_board("board2"))
    db.create_layer(b1, "top")
    db.create_layer(b1, "bottom")
    db.create_layer(b2, "top")
    layers = db.list_layers(b1)
    assert len(layers) == 2
    assert all(l["board_id"] == b1 for l in layers)


# ── Pin helpers ──────────────────────────────────────────────────────────────

def test_add_pin_returns_object_id(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=5.0, y_mm=5.0)
    pin   = db.add_pin(int(layer), int(comp), 5.5, 5.5)
    assert isinstance(pin, int) and pin > 0


def test_add_pin_stores_type_and_component_link(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 1.0, 2.0)
    row   = db.get_object(int(pin))
    assert row["type"] == "pin"
    import json
    props = json.loads(row["properties"])
    assert props["component_id"] == int(comp)


def test_add_pin_with_number_and_label(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 1.0, 2.0, pin_number="1", label="VCC")
    row   = db.get_object(int(pin))
    import json
    props = json.loads(row["properties"])
    assert props["pin_number"] == "1"
    assert props["label"] == "VCC"
    assert row["label"] == "1"   # display label is pin_number when set


def test_get_pins_for_component_returns_correct_pins(db, board_id):
    layer  = db.create_layer(board_id, "top")
    comp1  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    comp2  = db.create_object(int(layer), "component", x_mm=10.0, y_mm=0.0)
    db.add_pin(int(layer), int(comp1), 1.0, 1.0)
    db.add_pin(int(layer), int(comp1), 2.0, 2.0)
    db.add_pin(int(layer), int(comp2), 5.0, 5.0)
    pins = db.get_pins_for_component(int(comp1))
    assert len(pins) == 2
    assert all(p["type"] == "pin" for p in pins)


def test_get_pins_for_component_empty_when_none(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    assert db.get_pins_for_component(int(comp)) == []


def test_update_pin_changes_number_and_label(db, board_id):
    import json
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 1.0, 1.0, pin_number="1")
    db.update_pin_object(int(pin), pin_number="A2", label="GND")
    row   = db.get_object(int(pin))
    props = json.loads(row["properties"])
    assert props["pin_number"] == "A2"
    assert props["label"] == "GND"
    assert row["label"] == "A2"


def test_update_pin_clear_number(db, board_id):
    import json
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 1.0, 1.0, pin_number="5", label="CLK")
    db.update_pin_object(int(pin), pin_number=None)
    row   = db.get_object(int(pin))
    props = json.loads(row["properties"])
    assert props["pin_number"] is None
    assert props["label"] == "CLK"
    assert row["label"] == "CLK"   # falls back to label when pin_number cleared


def test_delete_object_removes_pin(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 1.0, 1.0)
    db.delete_object(int(pin))
    assert db.get_object(int(pin)) is None


def test_pin_always_has_component_id_in_properties(db, board_id):
    """Every pin must carry component_id in its JSON properties."""
    import json
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 3.0, 4.0)
    row   = db.get_object(int(pin))
    props = json.loads(row["properties"])
    assert "component_id" in props
    assert props["component_id"] == int(comp)


def test_get_pins_for_component_does_not_return_other_component_pins(db, board_id):
    """Pins from a different component must not appear in get_pins_for_component."""
    layer  = db.create_layer(board_id, "top")
    comp1  = db.create_object(int(layer), "component", x_mm=0.0,  y_mm=0.0)
    comp2  = db.create_object(int(layer), "component", x_mm=10.0, y_mm=0.0)
    db.add_pin(int(layer), int(comp1), 1.0, 1.0)
    db.add_pin(int(layer), int(comp2), 11.0, 1.0)
    pins1 = db.get_pins_for_component(int(comp1))
    assert len(pins1) == 1
    import json
    assert json.loads(pins1[0]["properties"])["component_id"] == int(comp1)


def test_delete_component_leaves_no_orphan_pins(db, board_id):
    """Deleting a component object must also remove its pins."""
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin1  = db.add_pin(int(layer), int(comp), 1.0, 1.0)
    pin2  = db.add_pin(int(layer), int(comp), 2.0, 2.0)
    db.delete_object(int(comp))
    # Component itself gone
    assert db.get_object(int(comp)) is None
    # Pins must also be gone — no orphans
    assert db.get_object(int(pin1)) is None
    assert db.get_object(int(pin2)) is None


# ── shift_layer_objects tests ─────────────────────────────────────────────────

def test_shift_zero_noop(db, board_id):
    layer = db.create_layer(board_id, "top")
    obj   = db.create_object(int(layer), "component", x_mm=5.0, y_mm=3.0)
    count = db.shift_layer_objects(int(layer), 0.0, 0.0)
    assert count == 0
    row = db.get_object(int(obj))
    assert row["x_mm"] == 5.0
    assert row["y_mm"] == 3.0


def test_shift_moves_component(db, board_id):
    layer = db.create_layer(board_id, "top")
    obj   = db.create_object(int(layer), "component", x_mm=10.0, y_mm=20.0)
    db.shift_layer_objects(int(layer), 1.5, -2.25)
    row = db.get_object(int(obj))
    assert abs(row["x_mm"] - 11.5)  < 1e-9
    assert abs(row["y_mm"] - 17.75) < 1e-9


def test_shift_returns_total_count(db, board_id):
    layer = db.create_layer(board_id, "top")
    for i in range(4):
        db.create_object(int(layer), "component", x_mm=float(i), y_mm=0.0)
    result = db.shift_layer_objects(int(layer), 1.0, 1.0)
    assert result == 4


def test_shift_moves_via_and_pad(db, board_id):
    layer = db.create_layer(board_id, "top")
    via   = db.create_object(int(layer), "via",  x_mm=0.0, y_mm=0.0)
    pad   = db.create_object(int(layer), "pad",  x_mm=5.0, y_mm=5.0)
    db.shift_layer_objects(int(layer), 2.0, 3.0)
    via_row = db.get_object(int(via))
    pad_row = db.get_object(int(pad))
    assert abs(via_row["x_mm"] - 2.0) < 1e-9
    assert abs(via_row["y_mm"] - 3.0) < 1e-9
    assert abs(pad_row["x_mm"] - 7.0) < 1e-9
    assert abs(pad_row["y_mm"] - 8.0) < 1e-9


def test_shift_trace_updates_start_and_end(db, board_id):
    import json
    layer = db.create_layer(board_id, "top")
    trace = db.create_object(
        int(layer), "trace", x_mm=0.0, y_mm=0.0,
        properties={"start": [1.0, 2.0], "end": [3.0, 4.0], "width": 0.2},
    )
    db.shift_layer_objects(int(layer), 0.5, 1.0)
    row = db.get_object(int(trace))
    p   = json.loads(row["properties"])
    assert abs(p["start"][0] - 1.5) < 1e-9
    assert abs(p["start"][1] - 3.0) < 1e-9
    assert abs(p["end"][0]   - 3.5) < 1e-9
    assert abs(p["end"][1]   - 5.0) < 1e-9


def test_shift_outline_updates_points(db, board_id):
    import json
    layer   = db.create_layer(board_id, "top")
    outline = db.create_object(
        int(layer), "outline", x_mm=0.0, y_mm=0.0,
        properties={"points": [[0.0, 0.0], [10.0, 0.0], [10.0, 8.0], [0.0, 8.0]]},
    )
    db.shift_layer_objects(int(layer), 1.0, 2.0)
    row = db.get_object(int(outline))
    pts = json.loads(row["properties"])["points"]
    assert abs(pts[0][0] - 1.0)  < 1e-9
    assert abs(pts[0][1] - 2.0)  < 1e-9
    assert abs(pts[1][0] - 11.0) < 1e-9
    assert abs(pts[2][1] - 10.0) < 1e-9


def test_shift_pin_coordinates(db, board_id):
    layer = db.create_layer(board_id, "top")
    comp  = db.create_object(int(layer), "component", x_mm=0.0, y_mm=0.0)
    pin   = db.add_pin(int(layer), int(comp), 3.0, 4.0)
    db.shift_layer_objects(int(layer), -1.0, 0.5)
    row = db.get_object(int(pin))
    assert abs(row["x_mm"] - 2.0) < 1e-9
    assert abs(row["y_mm"] - 4.5) < 1e-9


def test_shift_does_not_affect_other_layer(db, board_id):
    layer_a = db.create_layer(board_id, "top")
    layer_b = db.create_layer(board_id, "bottom")
    obj_b   = db.create_object(int(layer_b), "component", x_mm=7.0, y_mm=7.0)
    db.shift_layer_objects(int(layer_a), 100.0, 100.0)
    row = db.get_object(int(obj_b))
    assert abs(row["x_mm"] - 7.0) < 1e-9
    assert abs(row["y_mm"] - 7.0) < 1e-9
