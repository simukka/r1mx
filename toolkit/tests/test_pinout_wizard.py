"""Unit tests for _ReviewLabel and _ReviewPage in the pinout wizard.

Covers:
- _ReviewLabel: selection helpers, hit detection, multi-select state
- _ReviewPage: merge logic (centroid, spatial sort, label/pin concatenation),
  add pad, delete (single + multi), editor enabled/disabled state, merge preview

No real PDF files, subprocess calls, or screen rendering are used; all widget
methods are driven directly.  A QApplication is required for widget creation.
"""

from __future__ import annotations

import sys

import numpy as np
import pytest

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication

from toolkit.analysis.pinout import BBox, PadDetection, PinoutResult
from toolkit.gui.dialogs.pinout_wizard import _ReviewLabel, _ReviewPage


# ─── Shared fixtures / helpers ────────────────────────────────────────────────

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def _px(w: int = 200, h: int = 200) -> QPixmap:
    """Minimal solid-black pixmap for tests that need a QPixmap."""
    img = QImage(w, h, QImage.Format.Format_RGB888)
    img.fill(0)
    return QPixmap.fromImage(img)


def _pad(
    cx: float,
    cy: float,
    size: float = 0.05,
    *,
    pin: str = "",
    label: str = "",
    shape: str = "circle",
) -> PadDetection:
    return PadDetection(
        bbox=BBox(cx - size / 2, cy - size / 2, size, size),
        shape=shape,
        pin_number=pin,
        label=label,
    )


def _result(*pads: PadDetection) -> PinoutResult:
    return PinoutResult(
        pads=list(pads),
        image_width=200,
        image_height=200,
        source_page=1,
        source_bbox=BBox(0, 0, 1, 1),
    )


def _crop() -> np.ndarray:
    return np.zeros((100, 100, 3), dtype=np.uint8)


# ─── _ReviewLabel ─────────────────────────────────────────────────────────────

class TestReviewLabelSelection:
    def test_select_pad_sets_single_element_list(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.5, 0.5)), _px())
        lbl.select_pad(0)
        assert lbl._selection == [0]

    def test_select_pad_none_clears_selection(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.5, 0.5)), _px())
        lbl.select_pad(0)
        lbl.select_pad(None)
        assert lbl._selection == []

    def test_set_selection_stores_list(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.2, 0.2), _pad(0.8, 0.8)), _px())
        lbl.set_selection([0, 1])
        assert lbl._selection == [0, 1]

    def test_set_selection_empty(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.5, 0.5)), _px())
        lbl.set_selection([0])
        lbl.set_selection([])
        assert lbl._selection == []

    def test_set_result_resets_selection(self, qapp):
        lbl = _ReviewLabel()
        r = _result(_pad(0.5, 0.5))
        lbl.set_result(r, _px())
        lbl.set_selection([0])
        # Load same result again — selection must clear
        lbl.set_result(r, _px())
        assert lbl._selection == []

    def test_set_result_resets_drag_state(self, qapp):
        lbl = _ReviewLabel()
        lbl._dragging = True
        lbl._drag_pad_idx = 0
        lbl.set_result(_result(_pad(0.5, 0.5)), _px())
        assert not lbl._dragging
        assert lbl._drag_pad_idx is None


class TestReviewLabelHitDetection:
    def test_hit_at_pad_centre(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.5, 0.5)), _px(200, 200))
        # Pad centre = (100, 100)
        assert lbl._find_pad_at(QPoint(100, 100)) == 0

    def test_miss_far_from_pad(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(_pad(0.5, 0.5)), _px(200, 200))
        assert lbl._find_pad_at(QPoint(5, 5)) is None

    def test_hit_within_radius(self, qapp):
        """Clicking within the hit radius (pad half-width + 8 px) still hits."""
        lbl = _ReviewLabel()
        # 10 % size pad centred at (100, 100); half-width = 10px; radius = 18px
        lbl.set_result(_result(_pad(0.5, 0.5, size=0.10)), _px(200, 200))
        assert lbl._find_pad_at(QPoint(115, 100)) == 0

    def test_returns_nearest_of_two_pads(self, qapp):
        lbl = _ReviewLabel()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        lbl.set_result(r, _px(200, 200))
        # 0.2*200=40  0.8*200=160 — click at x=50 is nearer to first pad
        assert lbl._find_pad_at(QPoint(50, 100)) == 0
        # click at x=150 is nearer to second pad
        assert lbl._find_pad_at(QPoint(150, 100)) == 1

    def test_no_pads_returns_none(self, qapp):
        lbl = _ReviewLabel()
        lbl.set_result(_result(), _px())
        assert lbl._find_pad_at(QPoint(100, 100)) is None

    def test_no_pixmap_returns_none(self, qapp):
        lbl = _ReviewLabel()
        assert lbl._find_pad_at(QPoint(0, 0)) is None


# ─── _ReviewPage — merge ──────────────────────────────────────────────────────

class TestReviewPageMerge:
    def test_merge_two_pads_centroid_x(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert len(r.pads) == 1
        assert r.pads[0].cx == pytest.approx(0.5, abs=0.02)

    def test_merge_two_pads_centroid_y(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.1), _pad(0.5, 0.9))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].cy == pytest.approx(0.5, abs=0.02)

    def test_merge_labels_left_to_right(self, qapp):
        """Pad with smaller cx should contribute its label first."""
        page = _ReviewPage()
        # index 0 is on the RIGHT, index 1 is on the LEFT
        r = _result(_pad(0.8, 0.5, label="B"), _pad(0.2, 0.5, label="A"))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].label == "AB"

    def test_merge_labels_top_to_bottom(self, qapp):
        """Pad with smaller cy (higher on image) contributes first."""
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.8, label="D"), _pad(0.5, 0.1, label="G"))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].label == "GD"

    def test_merge_three_labels_in_spatial_order(self, qapp):
        page = _ReviewPage()
        r = _result(
            _pad(0.3, 0.5, label="G"),
            _pad(0.5, 0.5, label="N"),
            _pad(0.7, 0.5, label="D"),
        )
        page.load_result(r, _crop())
        page._apply_selection([0, 1, 2])
        page._merge_selected()
        assert len(r.pads) == 1
        assert r.pads[0].label == "GND"

    def test_merge_pin_numbers_concatenated(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5, pin="1"), _pad(0.8, 0.5, pin="4"))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].pin_number == "14"

    def test_merge_skips_empty_labels(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5, label="GN"), _pad(0.8, 0.5, label=""))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].label == "GN"

    def test_merge_uses_max_size(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5, size=0.02), _pad(0.8, 0.5, size=0.08))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert r.pads[0].bbox.w == pytest.approx(0.08, abs=0.001)

    def test_merge_result_is_auto_selected(self, qapp):
        """After merging, the resulting pad should be selected."""
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        page._merge_selected()
        assert page._selection == [0]

    def test_merge_noop_with_single_selection(self, qapp):
        """Merge should not fire when fewer than 2 pads are selected."""
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5, label="GND"), _pad(0.3, 0.3))
        page.load_result(r, _crop())
        page._apply_selection([0])
        page._merge_selected()
        assert len(r.pads) == 2   # unchanged

    def test_merge_noop_with_empty_selection(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._merge_selected()
        assert len(r.pads) == 1


# ─── _ReviewPage — add / delete ───────────────────────────────────────────────

class TestReviewPageAddDelete:
    def test_add_pad_increases_count(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._add_pad(0.2, 0.3)
        assert len(r.pads) == 2

    def test_add_pad_position(self, qapp):
        page = _ReviewPage()
        r = _result()
        page.load_result(r, _crop())
        page._add_pad(0.3, 0.7)
        assert r.pads[0].cx == pytest.approx(0.3, abs=0.001)
        assert r.pads[0].cy == pytest.approx(0.7, abs=0.001)

    def test_add_pad_default_shape_is_circle(self, qapp):
        page = _ReviewPage()
        r = _result()
        page.load_result(r, _crop())
        page._add_pad(0.5, 0.5)
        assert r.pads[0].shape == "circle"

    def test_add_pad_selects_new_pad(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._add_pad(0.2, 0.8)
        assert page._selection == [1]

    def test_delete_single_selected(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0])
        page._delete_selected()
        assert len(r.pads) == 1
        assert r.pads[0].cx == pytest.approx(0.8, abs=0.01)

    def test_delete_multi_selected(self, qapp):
        """All selected pads should be removed."""
        page = _ReviewPage()
        r = _result(_pad(0.1, 0.5), _pad(0.5, 0.5), _pad(0.9, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 2])
        page._delete_selected()
        assert len(r.pads) == 1
        assert r.pads[0].cx == pytest.approx(0.5, abs=0.01)

    def test_delete_clears_selection(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0])
        page._delete_selected()
        assert page._selection == []

    def test_delete_noop_when_nothing_selected(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._delete_selected()
        assert len(r.pads) == 1


# ─── _ReviewPage — editor / UI state ─────────────────────────────────────────

class TestReviewPageEditorState:
    def test_editor_disabled_on_load(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        assert not page._editor_box.isEnabled()

    def test_merge_box_hidden_on_load(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        assert page._merge_box.isHidden()

    def test_single_selection_enables_editor(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5, pin="3", label="CLK"))
        page.load_result(r, _crop())
        page._apply_selection([0])
        assert page._editor_box.isEnabled()

    def test_single_selection_populates_fields(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5, pin="3", label="CLK", shape="rect"))
        page.load_result(r, _crop())
        page._apply_selection([0])
        assert page._pin_num_edit.text() == "3"
        assert page._pin_lbl_edit.text() == "CLK"
        assert page._shape_combo.currentText() == "rect"

    def test_single_selection_hides_merge_box(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0])
        assert page._merge_box.isHidden()

    def test_multi_selection_shows_merge_box(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        assert not page._merge_box.isHidden()

    def test_multi_selection_disables_editor(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        assert not page._editor_box.isEnabled()

    def test_merge_preview_contains_merged_label(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5, label="GN"), _pad(0.8, 0.5, label="D"))
        page.load_result(r, _crop())
        page._apply_selection([0, 1])
        assert "GND" in page._merge_preview_lbl.text()

    def test_merge_preview_shows_pad_count(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.5, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 1, 2])
        assert "3" in page._merge_preview_lbl.text()

    def test_save_pad_edits_updates_result(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0])
        page._pin_num_edit.setText("7")
        page._pin_lbl_edit.setText("MOSI")
        page._shape_combo.setCurrentText("rect")
        page._save_pad_edits()
        assert r.pads[0].pin_number == "7"
        assert r.pads[0].label == "MOSI"
        assert r.pads[0].shape == "rect"

    def test_save_pad_edits_noop_without_selection(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.5, 0.5, label="OLD"))
        page.load_result(r, _crop())
        page._pin_lbl_edit.setText("NEW")
        page._save_pad_edits()   # no selection — should not write
        assert r.pads[0].label == "OLD"

    def test_apply_selection_syncs_list(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([1])
        selected_rows = [
            page._pad_list.row(item)
            for item in page._pad_list.selectedItems()
        ]
        assert selected_rows == [1]

    def test_apply_multi_selection_syncs_list(self, qapp):
        page = _ReviewPage()
        r = _result(_pad(0.2, 0.5), _pad(0.5, 0.5), _pad(0.8, 0.5))
        page.load_result(r, _crop())
        page._apply_selection([0, 2])
        selected_rows = sorted(
            page._pad_list.row(item)
            for item in page._pad_list.selectedItems()
        )
        assert selected_rows == [0, 2]
