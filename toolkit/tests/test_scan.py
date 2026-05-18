"""Unit tests for toolkit.analysis.scan (OCR/BOM logic)."""
from __future__ import annotations

from toolkit.analysis.scan import filter_tokens, normalize_ref, ref_type_from_designator


def test_ref_type_resistor():
    assert ref_type_from_designator("R1") == "R"
    assert ref_type_from_designator("R123") == "R"


def test_ref_type_capacitor():
    assert ref_type_from_designator("C10") == "C"


def test_ref_type_ic():
    assert ref_type_from_designator("U7") == "U"


def test_ref_type_unknown():
    assert ref_type_from_designator("XYZ") == ""


def test_normalize_ref_strips_spaces():
    assert normalize_ref("  R 1  ") == "R1"


def test_normalize_ref_uppercase():
    assert normalize_ref("r1") == "R1"


def test_filter_tokens_separates():
    tokens = [("R1", 10, 20), ("C10", 30, 40), ("ABC123", 50, 60), ("3V3", 70, 80)]
    refs, parts = filter_tokens(tokens)
    ref_labels = [r[0] for r in refs]
    part_labels = [p[0] for p in parts]
    assert "R1" in ref_labels
    assert "C10" in ref_labels
    assert "ABC123" in part_labels
