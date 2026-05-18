"""Cross-reference a KiCad footprint's dimensions against a datasheet.

Extracts dimensional metadata from:
  1. The KiCad footprint name (standardised: "SOIC-8_3.9x4.9mm_P1.27mm")
  2. The datasheet text (via pdftotext)

Then scores how well they agree.

Usage::

    from toolkit.analysis.footprint_match import (
        extract_kicad_dimensions,
        extract_datasheet_dimensions,
        score_match,
    )

    fp_dims = extract_kicad_dimensions(kicad_footprint)
    ds_dims = extract_datasheet_dimensions(datasheet_text)
    result  = score_match(fp_dims, ds_dims)
    print(f"Match: {result.total:.0%}")
    for line in result.details:
        print(" ", line)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from toolkit.analysis.kicad_footprint import KicadFootprint


# ─── Dimension containers ─────────────────────────────────────────────────────

@dataclass
class FootprintDimensions:
    """Dimensional metadata extracted from a KiCad footprint."""
    pad_count:  int
    pitch_mm:   Optional[float]      # centre-to-centre pad pitch (None if unknown)
    body_w_mm:  Optional[float]      # package body width  (None if unknown)
    body_h_mm:  Optional[float]      # package body height (None if unknown)


@dataclass
class DatasheetDimensions:
    """Dimensional metadata extracted from datasheet plain text."""
    pad_counts:  list[int]                  # all mentioned pin counts
    pitches_mm:  list[float]                # all mentioned pitches (mm)
    body_sizes:  list[tuple[float, float]]  # (w, h) pairs mentioned (mm)


@dataclass
class FieldScore:
    """Score for one dimension field."""
    name:   str
    score:  float        # 0.0–1.0
    weight: float        # relative importance
    detail: str          # human-readable line


@dataclass
class MatchScore:
    """Overall cross-reference result."""
    total:      float           # weighted average of field scores, 0.0–1.0
    fields:     list[FieldScore]
    details:    list[str]       # human-readable breakdown (one line per field)
    has_data:   bool            # False when datasheet had no parseable dimensions


# ─── KiCad name parser ────────────────────────────────────────────────────────

# Body dimensions: "3.9x4.9mm" or "3.9X4.9mm"
_BODY_RE  = re.compile(r"_([\d.]+)[xX]([\d.]+)mm")
# Pitch: "P1.27mm" or "p0.5mm"
_PITCH_RE = re.compile(r"[Pp]([\d.]+)mm")
# Pad count in name: "SOIC-8_", "-16_", etc. — first number after first "-" or at name start
_PADS_RE  = re.compile(r"[-_](\d+)(?:[-_]|$)")

# Known valid pitches (mm) — used to filter noise
_KNOWN_PITCHES = {
    0.4, 0.5, 0.65, 0.8, 1.0, 1.27, 1.5, 2.0, 2.54,
}

# Tolerance for pitch comparison (snap to nearest known value within 3%)
def _snap_pitch(p: float) -> float:
    for kp in sorted(_KNOWN_PITCHES):
        if abs(kp - p) / kp < 0.03:
            return kp
    return p


def extract_kicad_dimensions(fp: KicadFootprint) -> FootprintDimensions:
    """Extract dimensional metadata from a ``KicadFootprint``.

    Parses the standardised KiCad footprint *name* (e.g.
    ``"SOIC-8_3.9x4.9mm_P1.27mm"``) for body and pitch.  Pad count comes
    from ``fp.pads``; if pads are not loaded, falls back to the name.
    """
    name = fp.name

    # Pad count — prefer loaded pads (excludes EP/thermal), fall back to name
    if fp.pads:
        real_pads = [p for p in fp.pads if p.number and p.number not in ("", "EP")]
        pad_count = len(real_pads) if real_pads else len(fp.pads)
    else:
        m = _PADS_RE.search(name)
        pad_count = int(m.group(1)) if m else 0

    # Body size from name
    bm = _BODY_RE.search(name)
    body_w, body_h = None, None
    if bm:
        a, b = float(bm.group(1)), float(bm.group(2))
        body_w, body_h = (min(a, b), max(a, b))

    # Pitch from name
    pm = _PITCH_RE.search(name)
    pitch = _snap_pitch(float(pm.group(1))) if pm else None

    return FootprintDimensions(
        pad_count=pad_count,
        pitch_mm=pitch,
        body_w_mm=body_w,
        body_h_mm=body_h,
    )


# ─── Datasheet text parser ────────────────────────────────────────────────────

# Pitch — IPC notation (e, E) or explicit "pitch", "P ="
_DS_PITCH_PATTERNS: list[re.Pattern] = [
    re.compile(r"\be\s*=\s*([\d.]+)\s*mm",                    re.I),
    re.compile(r"\bpitch\s*=?\s*([\d.]+)\s*mm",               re.I),
    re.compile(r"([\d.]+)\s*mm\s+pitch",                       re.I),
    re.compile(r"\bP\s*=\s*([\d.]+)\s*mm",                    re.I),
    re.compile(r"center[- ]to[- ]center\s*\w*\s*([\d.]+)\s*mm", re.I),
    re.compile(r"lead\s+pitch\s*[=:]?\s*([\d.]+)\s*mm",       re.I),
]

# Body dimensions: "X.X × Y.Y mm", "X.X x Y.Y mm", "X.Xmm × Y.Ymm"
_DS_BODY_PATTERNS: list[re.Pattern] = [
    re.compile(r"([\d.]+)\s*mm\s*[×x]\s*([\d.]+)\s*mm",      re.I),
    re.compile(r"([\d.]+)\s*[×x]\s*([\d.]+)\s*mm",            re.I),
]

# Pin count
_DS_PIN_RE = re.compile(r"\b(\d+)[- ]?(?:pin|lead|ld|pad|ball)s?\b", re.I)


def extract_datasheet_dimensions(text: str) -> DatasheetDimensions:
    """Parse dimensional data from datasheet plain text.

    Parameters
    ----------
    text:
        Plain text extracted from the datasheet (e.g. via ``pdftotext``).

    Returns
    -------
    ``DatasheetDimensions`` with all plausible matches.  Lists may be empty
    if no matching data was found.
    """
    pitches:    list[float]               = []
    body_sizes: list[tuple[float, float]] = []
    pad_counts: list[int]                 = []

    # ── Pitches ──────────────────────────────────────────────────────────────
    for pat in _DS_PITCH_PATTERNS:
        for m in pat.finditer(text):
            try:
                p = float(m.group(1))
                # Only accept plausible IC pitches
                snapped = _snap_pitch(p)
                if 0.3 <= snapped <= 3.0 and snapped not in pitches:
                    pitches.append(snapped)
            except ValueError:
                pass

    # ── Body sizes ────────────────────────────────────────────────────────────
    for pat in _DS_BODY_PATTERNS:
        for m in pat.finditer(text):
            try:
                a, b = float(m.group(1)), float(m.group(2))
                # Sanity: only IC-plausible sizes (0.5mm – 50mm each side)
                if 0.5 <= a <= 50 and 0.5 <= b <= 50:
                    wh = (round(min(a, b), 3), round(max(a, b), 3))
                    if wh not in body_sizes:
                        body_sizes.append(wh)
            except ValueError:
                pass

    # ── Pin counts ────────────────────────────────────────────────────────────
    for m in _DS_PIN_RE.finditer(text):
        try:
            n = int(m.group(1))
            if 2 <= n <= 1024 and n not in pad_counts:
                pad_counts.append(n)
        except ValueError:
            pass

    return DatasheetDimensions(
        pad_counts=pad_counts,
        pitches_mm=pitches,
        body_sizes=body_sizes,
    )


# ─── Scoring ─────────────────────────────────────────────────────────────────

def _score_pad_count(fp: FootprintDimensions, ds: DatasheetDimensions) -> FieldScore | None:
    if not ds.pad_counts or fp.pad_count == 0:
        return None
    best = min(ds.pad_counts, key=lambda n: abs(n - fp.pad_count))
    diff = abs(best - fp.pad_count)
    if diff == 0:
        return FieldScore("Pads", 1.0, 3.0,
                          f"✓ Pads: {fp.pad_count} matches datasheet")
    if diff <= 2:
        return FieldScore("Pads", 0.6, 3.0,
                          f"≈ Pads: {fp.pad_count} (datasheet mentions {best})")
    return FieldScore("Pads", 0.0, 3.0,
                      f"✗ Pads: {fp.pad_count} (datasheet mentions {best})")


def _score_pitch(fp: FootprintDimensions, ds: DatasheetDimensions) -> FieldScore | None:
    if fp.pitch_mm is None or not ds.pitches_mm:
        return None
    best = min(ds.pitches_mm, key=lambda p: abs(p - fp.pitch_mm))
    ratio = abs(best - fp.pitch_mm) / max(fp.pitch_mm, 0.01)
    p_str = f"{fp.pitch_mm}mm"
    if ratio < 0.05:
        return FieldScore("Pitch", 1.0, 2.0,
                          f"✓ Pitch: {p_str} matches datasheet")
    if ratio < 0.15:
        return FieldScore("Pitch", 0.5, 2.0,
                          f"≈ Pitch: {p_str} (datasheet: {best}mm)")
    return FieldScore("Pitch", 0.0, 2.0,
                      f"✗ Pitch: {p_str} (datasheet: {best}mm)")


def _score_body(fp: FootprintDimensions, ds: DatasheetDimensions) -> FieldScore | None:
    if fp.body_w_mm is None or fp.body_h_mm is None or not ds.body_sizes:
        return None
    fp_area = fp.body_w_mm * fp.body_h_mm
    best = min(ds.body_sizes, key=lambda s: abs(s[0] * s[1] - fp_area))
    ds_area = best[0] * best[1]
    ratio = abs(ds_area - fp_area) / max(fp_area, 0.01)
    fp_str = f"{fp.body_w_mm}×{fp.body_h_mm}mm"
    if ratio < 0.10:
        return FieldScore("Body", 1.0, 1.0,
                          f"✓ Body: {fp_str} matches datasheet")
    if ratio < 0.25:
        return FieldScore("Body", 0.5, 1.0,
                          f"≈ Body: {fp_str} (datasheet: {best[0]}×{best[1]}mm)")
    return FieldScore("Body", 0.0, 1.0,
                      f"✗ Body: {fp_str} (datasheet: {best[0]}×{best[1]}mm)")


def score_match(
    fp_dims: FootprintDimensions,
    ds_dims: DatasheetDimensions,
) -> MatchScore:
    """Compute a weighted match score between footprint and datasheet dimensions.

    Fields
    ------
    - Pad count  (weight 3) — most diagnostic; exact count uniquely identifies the package
    - Pitch      (weight 2) — distinguishes e.g. SOIC from SSOP
    - Body size  (weight 1) — useful but often has multiple valid options in a datasheet

    Returns ``MatchScore.has_data = False`` when no dimension data was available
    to score against.
    """
    field_scores: list[FieldScore] = []

    for scorer in (_score_pad_count, _score_pitch, _score_body):
        fs = scorer(fp_dims, ds_dims)
        if fs is not None:
            field_scores.append(fs)

    if not field_scores:
        return MatchScore(
            total=0.0,
            fields=[],
            details=["No dimension data available in datasheet"],
            has_data=False,
        )

    total = (
        sum(fs.score * fs.weight for fs in field_scores)
        / sum(fs.weight for fs in field_scores)
    )

    return MatchScore(
        total=round(total, 3),
        fields=field_scores,
        details=[fs.detail for fs in field_scores],
        has_data=True,
    )
