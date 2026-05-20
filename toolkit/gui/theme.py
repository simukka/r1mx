"""toolkit.gui.theme — centralised colour palette for the r1mx toolkit UI.

A single ``Theme`` dataclass holds every named colour used across the canvas,
tree panel, viewer, scan-preview overlays, and trace-routing feedback.

Usage
-----
    from toolkit.gui.theme import THEME

    pen = QPen(THEME.via_color)

To define a future dark theme, instantiate ``Theme`` with different colours
and reassign ``THEME`` before the GUI starts::

    import toolkit.gui.theme as _t
    _t.THEME = _t.Theme(
        via_color=QColor(0, 220, 255),
        ...
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtGui import QColor


def _c(r: int, g: int, b: int, a: int = 255) -> "QColor":
    return QColor(r, g, b, a)


@dataclass
class Theme:
    # ── Canvas object-type colours ──────────────────────────────────────────
    photo_color:        QColor = field(default_factory=lambda: _c(200, 200, 200))
    copper_color:       QColor = field(default_factory=lambda: _c(180, 120,   0))
    outline_color:      QColor = field(default_factory=lambda: _c(  0, 180, 255))
    via_color:          QColor = field(default_factory=lambda: _c(255, 255,   0))
    via_outline_color:  QColor = field(default_factory=lambda: _c( 40,  40,  40))
    via_fill_alpha:     int    = 200
    pad_color:          QColor = field(default_factory=lambda: _c(255, 200,   0))
    component_color:    QColor = field(default_factory=lambda: _c(  0, 255, 120))
    text_label_color:   QColor = field(default_factory=lambda: _c(255, 160,  50))
    trace_color:        QColor = field(default_factory=lambda: _c(  0, 120, 255))
    pin_color:          QColor = field(default_factory=lambda: _c(  0, 220, 220))

    # ── Layer tree colours ───────────────────────────────────────────────────
    layer_top_color:     QColor = field(default_factory=lambda: _c(  0, 200, 100))
    layer_bottom_color:  QColor = field(default_factory=lambda: _c(200, 100,   0))
    layer_default_color: QColor = field(default_factory=lambda: _c(150, 150, 150))
    tree_dim_color:      QColor = field(default_factory=lambda: _c(140, 140, 140))

    # ── Vignette ────────────────────────────────────────────────────────────
    vignette_color: QColor = field(default_factory=lambda: _c(0, 0, 0))
    vignette_alpha: int    = 190

    # ── Viewer crosshair & rubber-band ──────────────────────────────────────
    crosshair_color:         QColor = field(default_factory=lambda: _c(  0, 255, 255))
    crosshair_outline_color: QColor = field(default_factory=lambda: _c(  0,   0,   0))
    rubberband_color:        QColor = field(default_factory=lambda: _c(255,  20, 147))
    rubberband_outline_color:QColor = field(default_factory=lambda: _c(  0,   0,   0))

    # ── Calibration annotation colours (viewer helpers) ──────────────────────
    cal_corner_color:    QColor = field(default_factory=lambda: _c(  0, 255,   0))
    cal_ref_color:       QColor = field(default_factory=lambda: _c(255, 100,   0))
    cal_polyline_color:  QColor = field(default_factory=lambda: _c(  0, 200, 255))
    cal_crosshair_color: QColor = field(default_factory=lambda: _c(  0, 255, 255))
    cal_label_color:     QColor = field(default_factory=lambda: _c(255, 180,   0))
    cal_ref_label_color: QColor = field(default_factory=lambda: _c(  0, 220, 220))

    # ── Trace-routing feedback (ADD_TRACE mode) ──────────────────────────────
    trace_preview_color:   QColor = field(default_factory=lambda: _c(  0, 180, 255))
    trace_anchor_color:    QColor = field(default_factory=lambda: _c(255, 220,   0))
    trace_snap_ring_color: QColor = field(default_factory=lambda: _c(  0, 255, 120))

    # ── Footprint crosshair (ALIGN_FOOTPRINT mode) ───────────────────────────
    footprint_xhair_color: QColor = field(default_factory=lambda: _c(  0, 255, 220))

    # ── Scan-preview overlay colours ─────────────────────────────────────────
    scan_via_color:     QColor = field(default_factory=lambda: _c(255,  80,  80))
    scan_pad_color:     QColor = field(default_factory=lambda: _c(255, 200,   0))
    scan_trace_color:   QColor = field(default_factory=lambda: _c(  0, 140, 255))
    scan_text_color:    QColor = field(default_factory=lambda: _c(255, 160,  50))
    scan_outline_color: QColor = field(default_factory=lambda: _c(  0, 220, 255))
    scan_manual_color:  QColor = field(default_factory=lambda: _c(255, 255, 255))

    # ── Footprint overlay (FootprintOverlayItem) ─────────────────────────────
    fp_pad_color:        QColor = field(default_factory=lambda: _c(255, 200,   0, 220))
    fp_pad_outline_color:QColor = field(default_factory=lambda: _c(200, 100,   0, 255))
    fp_pin_label_color:  QColor = field(default_factory=lambda: _c(255, 255, 255, 230))
    fp_outline_color:    QColor = field(default_factory=lambda: _c(  0, 255, 120, 160))


# The active theme — replace this before the GUI starts to change the palette.
THEME: Theme = Theme()
