"""Unit tests for toolkit.analysis.kicad_footprint.

All tests use temporary .kicad_mod files written in-memory — no dependency on
installed KiCad libraries.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from toolkit.analysis.kicad_footprint import (
    KicadFootprint,
    KicadPad,
    _load_stub,
    build_index,
    footprint_to_pad_detections,
    load_pads,
    search_index,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_mod(tmp_path: Path, name: str, content: str) -> Path:
    """Write a fake .kicad_mod file and return its path."""
    lib_dir = tmp_path / "TestLib.pretty"
    lib_dir.mkdir(parents=True, exist_ok=True)
    p = lib_dir / f"{name}.kicad_mod"
    p.write_text(content, encoding="utf-8")
    return p


_SOIC8_MOD = """\
(footprint "SOIC-8_3.9x4.9mm_P1.27mm"
    (version 20241229)
    (descr "SOIC, 8 Pin (JEDEC MS-012AA)")
    (tags "SOIC SO")
    (pad "1" smd roundrect
        (at -2.475 -1.905)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "2" smd roundrect
        (at -2.475 -0.635)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "3" smd roundrect
        (at -2.475 0.635)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "4" smd roundrect
        (at -2.475 1.905)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "5" smd roundrect
        (at 2.475 1.905)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "6" smd roundrect
        (at 2.475 0.635)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "7" smd roundrect
        (at 2.475 -0.635)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
    (pad "8" smd roundrect
        (at 2.475 -1.905)
        (size 1.95 0.6)
        (layers "F.Cu" "F.Mask" "F.Paste")
    )
)
"""

_QFP_MOD = """\
(footprint "LQFP-32_7x7mm_P0.8mm"
    (descr "LQFP 32 pin")
    (tags "QFP LQFP")
    (pad "1" smd rect
        (at -4.1 -2.4 90)
        (size 1.5 0.4)
        (layers "F.Cu")
    )
    (pad "2" smd rect
        (at -4.1 -1.6 90)
        (size 1.5 0.4)
        (layers "F.Cu")
    )
)
"""

_BGA_MOD = """\
(footprint "BGA-9_3x3_P1mm"
    (descr "BGA 9 pin 3x3 grid")
    (tags "BGA")
    (pad "A1" smd circle
        (at -1.0 -1.0)
        (size 0.5 0.5)
        (layers "F.Cu")
    )
    (pad "A2" smd circle
        (at 0.0 -1.0)
        (size 0.5 0.5)
        (layers "F.Cu")
    )
    (pad "A3" smd circle
        (at 1.0 -1.0)
        (size 0.5 0.5)
        (layers "F.Cu")
    )
)
"""

_THERMAL_MOD = """\
(footprint "SOIC-8-1EP"
    (descr "SOIC with thermal pad")
    (tags "SOIC")
    (pad "1" smd roundrect
        (at -2.475 -1.905)
        (size 1.95 0.6)
        (layers "F.Cu")
    )
    (pad "" thru_hole circle
        (at 0 0)
        (size 2.0 2.0)
        (layers "*.Cu")
    )
    (pad "EP" smd rect
        (at 0 0)
        (size 2.3 3.0)
        (layers "F.Cu")
    )
)
"""

_NO_PADS_MOD = """\
(footprint "MountingHole_3mm"
    (descr "Mounting hole 3mm")
    (tags "MountingHole")
)
"""


# ─── _load_stub ───────────────────────────────────────────────────────────────

class TestLoadStub:
    def test_name_from_filename(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8_test", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        assert stub.name == "SOIC-8_test"

    def test_library_set(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8_test", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        assert stub.library == "TestLib"

    def test_description_parsed(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8_test", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        assert "SOIC" in stub.description

    def test_tags_parsed(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8_test", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        assert "SOIC" in stub.tags

    def test_no_pads_in_stub(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8_test", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        assert stub.pads == []

    def test_missing_file_returns_empty_stub(self, tmp_path):
        fake = tmp_path / "ghost.kicad_mod"
        stub = _load_stub(fake, "Lib")
        assert stub.name == "ghost"
        assert stub.description == ""


# ─── load_pads ────────────────────────────────────────────────────────────────

class TestLoadPads:
    def test_soic8_pad_count(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        fp = load_pads(stub)
        assert fp.pad_count == 8

    def test_soic8_pad_numbers(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        numbers = [pad.number for pad in fp.pads]
        assert numbers == ["1", "2", "3", "4", "5", "6", "7", "8"]

    def test_soic8_pad1_position(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        pad1 = fp.pads[0]
        assert pad1.x_mm == pytest.approx(-2.475)
        assert pad1.y_mm == pytest.approx(-1.905)

    def test_soic8_pad_size(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pads[0].w_mm == pytest.approx(1.95)
        assert fp.pads[0].h_mm == pytest.approx(0.6)

    def test_soic8_pad_shape_roundrect_maps_to_rect(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pads[0].shape == "rect"

    def test_qfp_pad_with_rotation(self, tmp_path):
        p = _write_mod(tmp_path, "QFP-32", _QFP_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pad_count == 2
        assert fp.pads[0].x_mm == pytest.approx(-4.1)
        assert fp.pads[0].y_mm == pytest.approx(-2.4)

    def test_bga_alphanumeric_pad_names(self, tmp_path):
        p = _write_mod(tmp_path, "BGA-9", _BGA_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pad_count == 3
        assert fp.pads[0].number == "A1"
        assert fp.pads[1].number == "A2"

    def test_bga_circle_shape(self, tmp_path):
        p = _write_mod(tmp_path, "BGA-9", _BGA_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pads[0].shape == "circle"

    def test_thermal_pad_included(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-1EP", _THERMAL_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        numbers = [pad.number for pad in fp.pads]
        assert "EP" in numbers

    def test_empty_number_pad_included(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-1EP", _THERMAL_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        numbers = [pad.number for pad in fp.pads]
        assert "" in numbers

    def test_no_pads_returns_empty_list(self, tmp_path):
        p = _write_mod(tmp_path, "MountHole", _NO_PADS_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        assert fp.pad_count == 0

    def test_metadata_preserved(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        stub = _load_stub(p, "TestLib")
        fp = load_pads(stub)
        assert fp.name == stub.name
        assert fp.library == stub.library
        assert fp.description == stub.description


# ─── build_index ──────────────────────────────────────────────────────────────

class TestBuildIndex:
    def test_finds_kicad_mod_files(self, tmp_path):
        _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        idx = build_index(extra_dirs=[tmp_path])
        names = [s.name for s in idx]
        assert "SOIC-8" in names

    def test_ignores_non_pretty_dirs(self, tmp_path):
        not_pretty = tmp_path / "randomdir"
        not_pretty.mkdir()
        (not_pretty / "foo.kicad_mod").write_text("(footprint)")
        idx = build_index(extra_dirs=[tmp_path])
        names = [s.name for s in idx]
        assert "foo" not in names

    def test_multiple_libraries(self, tmp_path):
        lib1 = tmp_path / "Lib1.pretty"
        lib2 = tmp_path / "Lib2.pretty"
        lib1.mkdir()
        lib2.mkdir()
        (lib1 / "FP_A.kicad_mod").write_text("")
        (lib2 / "FP_B.kicad_mod").write_text("")
        idx = build_index(extra_dirs=[tmp_path])
        names = [s.name for s in idx]
        assert "FP_A" in names
        assert "FP_B" in names

    def test_library_field_set_correctly(self, tmp_path):
        _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        idx = build_index(extra_dirs=[tmp_path])
        stub = next(s for s in idx if s.name == "SOIC-8")
        assert stub.library == "TestLib"

    def test_nonexistent_dir_skipped(self):
        idx = build_index(extra_dirs=[Path("/nonexistent/path")])
        # Should not raise; returns results from real system dirs only
        assert isinstance(idx, list)


# ─── search_index ─────────────────────────────────────────────────────────────

class TestSearchIndex:
    @pytest.fixture
    def idx(self, tmp_path) -> list[KicadFootprint]:
        lib = tmp_path / "TestLib.pretty"
        lib.mkdir()
        for name, content in [
            ("SOIC-8_3.9x4.9mm", _SOIC8_MOD),
            ("SOIC-16_3.9x9.9mm", _SOIC8_MOD),
            ("LQFP-32_7x7mm", _QFP_MOD),
            ("BGA-9_3x3", _BGA_MOD),
            ("MountingHole_3mm", _NO_PADS_MOD),
        ]:
            (lib / f"{name}.kicad_mod").write_text(content)
        return build_index(dirs=[tmp_path])

    def test_empty_query_returns_all(self, idx):
        results = search_index(idx, "")
        assert len(results) == 5  # exactly the 5 fixtures above

    def test_name_substring_match(self, idx):
        results = search_index(idx, "SOIC")
        assert all("soic" in r.name.lower() or "soic" in r.tags.lower() for r in results)
        assert len(results) >= 2

    def test_case_insensitive(self, idx):
        r1 = search_index(idx, "soic")
        r2 = search_index(idx, "SOIC")
        assert {r.name for r in r1} == {r.name for r in r2}

    def test_no_match_returns_empty(self, idx):
        results = search_index(idx, "XYZNONEXISTENT")
        assert results == []

    def test_pin_count_filter(self, idx):
        # "SOIC-8_…" has "8" as standalone number; "SOIC-16_…" has "16"
        results = search_index(idx, "SOIC", pin_count=8)
        names = [r.name for r in results]
        assert any("SOIC-8" in n for n in names)
        assert not any("SOIC-16" in n for n in names)

    def test_pin_count_not_partial_match(self, idx):
        # pin_count=1 must NOT match "SOIC-16" (16 contains 1 but not standalone)
        results = search_index(idx, "SOIC", pin_count=1)
        names = [r.name for r in results]
        assert not any("16" in n for n in names)

    def test_max_results_respected(self, idx):
        results = search_index(idx, "", max_results=2)
        assert len(results) == 2

    def test_tag_search(self, idx):
        results = search_index(idx, "BGA")
        names = [r.name for r in results]
        assert any("BGA" in n for n in names)


# ─── footprint_to_pad_detections ─────────────────────────────────────────────

class TestFootprintToPadDetections:
    def test_returns_correct_count(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        assert len(dets) == 8

    def test_positions_normalised_0_to_1(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        for d in dets:
            assert 0.0 <= d.cx <= 1.0, f"cx={d.cx} out of range"
            assert 0.0 <= d.cy <= 1.0, f"cy={d.cy} out of range"

    def test_pin_numbers_preserved(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        numbers = [d.pin_number for d in dets]
        assert numbers == ["1", "2", "3", "4", "5", "6", "7", "8"]

    def test_labels_empty(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        assert all(d.label == "" for d in dets)

    def test_bbox_mm_returned(self, tmp_path):
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        _, bbox = footprint_to_pad_detections(fp)
        min_x, min_y, span_x, span_y = bbox
        assert span_x > 0
        assert span_y > 0

    def test_empty_pads_returns_empty_list(self, tmp_path):
        p = _write_mod(tmp_path, "MountHole", _NO_PADS_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, bbox = footprint_to_pad_detections(fp)
        assert dets == []

    def test_pad1_is_left_of_pad8_in_soic8(self, tmp_path):
        """SOIC-8: pads 1-4 on left (x<0), pads 5-8 on right (x>0)."""
        p = _write_mod(tmp_path, "SOIC-8", _SOIC8_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        pad1 = dets[0]
        pad8 = dets[7]
        assert pad1.cx < pad8.cx

    def test_bga_alphanumeric_pads_preserved(self, tmp_path):
        p = _write_mod(tmp_path, "BGA-9", _BGA_MOD)
        fp = load_pads(_load_stub(p, "TestLib"))
        dets, _ = footprint_to_pad_detections(fp)
        assert dets[0].pin_number == "A1"
