"""Unit tests for toolkit.analysis.footprint_match."""

from __future__ import annotations

import pytest

from toolkit.analysis.footprint_match import (
    DatasheetDimensions,
    FieldScore,
    FootprintDimensions,
    MatchScore,
    extract_datasheet_dimensions,
    extract_kicad_dimensions,
    score_match,
    _snap_pitch,
)
from toolkit.analysis.kicad_footprint import KicadFootprint, KicadPad
from pathlib import Path


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_fp(name: str, pads: list[KicadPad] | None = None) -> KicadFootprint:
    return KicadFootprint(
        name=name,
        library="Test",
        path=Path("/dev/null"),
        description="",
        tags="",
        pads=pads or [],
    )


def _make_pad(number: str, x: float = 0.0, y: float = 0.0) -> KicadPad:
    return KicadPad(number=number, x_mm=x, y_mm=y, w_mm=0.6, h_mm=1.6, shape="rect")


# ─── _snap_pitch ─────────────────────────────────────────────────────────────

class TestSnapPitch:
    def test_snaps_to_127(self):
        assert _snap_pitch(1.27) == 1.27

    def test_snaps_close_to_127(self):
        assert _snap_pitch(1.265) == 1.27

    def test_snaps_to_0_5(self):
        assert _snap_pitch(0.5) == 0.5

    def test_passthrough_unknown(self):
        assert _snap_pitch(3.7) == 3.7


# ─── extract_kicad_dimensions ─────────────────────────────────────────────────

class TestExtractKicadDimensions:
    def test_soic8_name(self):
        fp = _make_fp("SOIC-8_3.9x4.9mm_P1.27mm")
        dims = extract_kicad_dimensions(fp)
        assert dims.body_w_mm == pytest.approx(3.9)
        assert dims.body_h_mm == pytest.approx(4.9)
        assert dims.pitch_mm  == pytest.approx(1.27)

    def test_pad_count_from_loaded_pads(self):
        pads = [_make_pad(str(i)) for i in range(1, 9)]
        fp = _make_fp("SOIC-8_3.9x4.9mm_P1.27mm", pads=pads)
        dims = extract_kicad_dimensions(fp)
        assert dims.pad_count == 8

    def test_ep_pad_excluded_from_count(self):
        pads = [_make_pad(str(i)) for i in range(1, 9)] + [_make_pad("EP")]
        fp = _make_fp("SOIC-8_3.9x4.9mm_P1.27mm", pads=pads)
        dims = extract_kicad_dimensions(fp)
        assert dims.pad_count == 8

    def test_pad_count_from_name_when_no_pads(self):
        fp = _make_fp("SOIC-16_3.9x9.9mm_P1.27mm")
        dims = extract_kicad_dimensions(fp)
        assert dims.pad_count == 16

    def test_tssop20_pitch_0_65(self):
        fp = _make_fp("TSSOP-20_4.4x6.5mm_P0.65mm")
        dims = extract_kicad_dimensions(fp)
        assert dims.pitch_mm == pytest.approx(0.65)

    def test_qfn_no_pitch_in_name(self):
        fp = _make_fp("QFN-16_3x3mm_Pitch0.5mm")
        dims = extract_kicad_dimensions(fp)
        # "P0.5mm" variant — still parsed
        assert dims.body_w_mm == pytest.approx(3.0)
        assert dims.body_h_mm == pytest.approx(3.0)

    def test_no_body_in_name(self):
        fp = _make_fp("SOIC-8")
        dims = extract_kicad_dimensions(fp)
        assert dims.body_w_mm is None
        assert dims.body_h_mm is None

    def test_no_pitch_in_name(self):
        fp = _make_fp("DIP-8_W7.62mm")
        dims = extract_kicad_dimensions(fp)
        assert dims.pitch_mm is None

    def test_body_always_w_le_h(self):
        fp = _make_fp("SOIC-8_4.9x3.9mm_P1.27mm")
        dims = extract_kicad_dimensions(fp)
        assert dims.body_w_mm <= dims.body_h_mm


# ─── extract_datasheet_dimensions ─────────────────────────────────────────────

class TestExtractDatasheetDimensions:
    def test_pitch_from_e_notation(self):
        ds = extract_datasheet_dimensions("e = 1.27 mm nominal")
        assert 1.27 in ds.pitches_mm

    def test_pitch_from_explicit_mm(self):
        ds = extract_datasheet_dimensions("1.27 mm pitch between leads")
        assert 1.27 in ds.pitches_mm

    def test_pitch_from_P_notation(self):
        ds = extract_datasheet_dimensions("P = 0.65 mm")
        assert 0.65 in ds.pitches_mm

    def test_pitch_from_center_to_center(self):
        ds = extract_datasheet_dimensions("center-to-center spacing 0.5 mm")
        assert 0.5 in ds.pitches_mm

    def test_pitch_out_of_range_ignored(self):
        ds = extract_datasheet_dimensions("e = 50 mm spacing")
        assert 50.0 not in ds.pitches_mm

    def test_body_size_detected(self):
        ds = extract_datasheet_dimensions("Package body: 3.9 mm × 4.9 mm")
        assert (3.9, 4.9) in ds.body_sizes or any(
            abs(w - 3.9) < 0.01 and abs(h - 4.9) < 0.01
            for w, h in ds.body_sizes
        )

    def test_body_size_x_separator(self):
        ds = extract_datasheet_dimensions("3.9 x 4.9 mm package")
        assert any(abs(w - 3.9) < 0.01 for w, h in ds.body_sizes)

    def test_pin_count_detected(self):
        ds = extract_datasheet_dimensions("8-pin SOIC package")
        assert 8 in ds.pad_counts

    def test_multiple_pitches(self):
        ds = extract_datasheet_dimensions(
            "e = 0.5 mm for bottom pads; outer lead pitch = 0.65 mm"
        )
        assert len(ds.pitches_mm) >= 1

    def test_empty_text(self):
        ds = extract_datasheet_dimensions("")
        assert ds.pitches_mm == []
        assert ds.body_sizes == []
        assert ds.pad_counts == []

    def test_no_match(self):
        ds = extract_datasheet_dimensions("The quick brown fox.")
        assert ds.pitches_mm == []


# ─── score_match ─────────────────────────────────────────────────────────────

def _fp(pad_count=8, pitch=1.27, body_w=3.9, body_h=4.9) -> FootprintDimensions:
    return FootprintDimensions(pad_count=pad_count, pitch_mm=pitch,
                               body_w_mm=body_w, body_h_mm=body_h)


def _ds(pad_counts=None, pitches=None, bodies=None) -> DatasheetDimensions:
    return DatasheetDimensions(
        pad_counts=pad_counts or [],
        pitches_mm=pitches or [],
        body_sizes=bodies or [],
    )


class TestScoreMatch:
    def test_perfect_match(self):
        result = score_match(_fp(8, 1.27, 3.9, 4.9),
                              _ds([8], [1.27], [(3.9, 4.9)]))
        assert result.total == pytest.approx(1.0)
        assert result.has_data is True

    def test_pad_mismatch_zero(self):
        result = score_match(_fp(8), _ds([16]))
        pad_f = next(f for f in result.fields if f.name == "Pads")
        assert pad_f.score == 0.0

    def test_pad_close_partial(self):
        result = score_match(_fp(8), _ds([9]))
        pad_f = next(f for f in result.fields if f.name == "Pads")
        assert 0 < pad_f.score < 1.0

    def test_pitch_within_5pct_full_score(self):
        result = score_match(_fp(pitch=1.27), _ds(pitches=[1.27]))
        pitch_f = next((f for f in result.fields if f.name == "Pitch"), None)
        assert pitch_f is not None
        assert pitch_f.score == 1.0

    def test_pitch_far_off_zero(self):
        result = score_match(_fp(pitch=0.5), _ds(pitches=[1.27]))
        pitch_f = next((f for f in result.fields if f.name == "Pitch"), None)
        assert pitch_f is not None
        assert pitch_f.score == 0.0

    def test_body_match(self):
        result = score_match(_fp(body_w=3.9, body_h=4.9),
                              _ds(bodies=[(3.9, 4.9)]))
        body_f = next((f for f in result.fields if f.name == "Body"), None)
        assert body_f is not None
        assert body_f.score == 1.0

    def test_body_off_zero(self):
        result = score_match(_fp(body_w=3.9, body_h=4.9),
                              _ds(bodies=[(10.0, 12.0)]))
        body_f = next((f for f in result.fields if f.name == "Body"), None)
        assert body_f is not None
        assert body_f.score == 0.0

    def test_no_data_returns_has_data_false(self):
        result = score_match(_fp(8, 1.27, 3.9, 4.9), _ds())
        assert result.has_data is False
        assert result.total == 0.0

    def test_only_pad_count_available(self):
        result = score_match(_fp(8, None, None, None), _ds([8]))
        assert result.total == pytest.approx(1.0)
        assert result.has_data is True

    def test_details_have_one_line_per_field(self):
        result = score_match(_fp(8, 1.27, 3.9, 4.9),
                              _ds([8], [1.27], [(3.9, 4.9)]))
        assert len(result.details) == len(result.fields)

    def test_total_between_0_and_1(self):
        result = score_match(_fp(8, 1.27, 3.9, 4.9),
                              _ds([16], [0.5], [(10.0, 10.0)]))
        assert 0.0 <= result.total <= 1.0

    def test_pad_count_has_highest_weight(self):
        # pad mismatch should drag total below 0.5 even with pitch/body matching
        result = score_match(_fp(8, 1.27, 3.9, 4.9),
                              _ds([64], [1.27], [(3.9, 4.9)]))
        assert result.total <= 0.5
