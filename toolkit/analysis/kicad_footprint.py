"""
kicad_footprint.py — Index and parse KiCad .kicad_mod footprint files.

Usage
-----
    from toolkit.analysis.kicad_footprint import build_index, load_pads, search_index

    index = build_index()                          # scan system + user dirs
    hits  = search_index(index, "SOIC-8", pin_count=8)
    fp    = load_pads(hits[0])                     # KicadFootprint with full pad list
    for pad in fp.pads:
        print(pad.number, pad.x_mm, pad.y_mm)

Notes
-----
* Parses the S-expression (.kicad_mod) format with regex — no external library needed.
* Pad positions are in mm, centred at the footprint origin.
* BGA footprints use alphanumeric pad numbers ("A1", "B2", …).
* Thermal / exposed pads often have number "" or "EP" — included as-is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ─── Default search directories ──────────────────────────────────────────────

_SYSTEM_DIRS: list[Path] = [
    Path("/usr/share/kicad/footprints"),
    Path("/usr/local/share/kicad/footprints"),
]

_USER_DIRS: list[Path] = [
    Path.home() / ".local" / "share" / "kicad" / "footprints",
    Path.home() / ".kicad" / "footprints",
]

# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class KicadPad:
    """One pad from a .kicad_mod footprint."""
    number: str         # pad number or name ("1", "A3", "EP")
    x_mm:   float       # position relative to footprint origin
    y_mm:   float
    w_mm:   float       # pad width
    h_mm:   float       # pad height
    shape:  str         # "circle", "rect", "roundrect", "oval", "trapezoid"


@dataclass
class KicadFootprint:
    """Metadata (and optionally pads) for a single .kicad_mod footprint file."""
    name:        str             # footprint name (filename without .kicad_mod)
    library:     str             # containing library folder name (without .pretty)
    path:        Path            # absolute path to the .kicad_mod file
    description: str = ""
    tags:        str = ""
    pads:        list[KicadPad] = field(default_factory=list)

    @property
    def pad_count(self) -> int:
        return len(self.pads)

    @property
    def display_name(self) -> str:
        return f"{self.library}  /  {self.name}"


# ─── Regex patterns ───────────────────────────────────────────────────────────

_RE_DESC  = re.compile(r'\(descr\s+"([^"]*)"')
_RE_TAGS  = re.compile(r'\(tags\s+"([^"]*)"')

# Matches:  (pad "1" smd roundrect
#               (at -2.475 -1.905)         ← no rotation
#               (at -2.475 -1.905 90)      ← with rotation
#               (size 1.95 0.6)
_RE_PAD = re.compile(
    r'\(pad\s+"([^"]*)"\s+\w+\s+(\w+)\s*'   # number, type, shape
    r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+[-\d.]+)?\)\s*'  # x, y (optional rot)
    r'\(size\s+([-\d.]+)\s+([-\d.]+)\)',     # w, h
    re.MULTILINE,
)

_SHAPE_MAP = {
    "circle":    "circle",
    "oval":      "circle",
    "rect":      "rect",
    "roundrect": "rect",
    "trapezoid": "rect",
    "custom":    "rect",
}


# ─── Public API ───────────────────────────────────────────────────────────────

def build_index(
    extra_dirs: list[Path] | None = None,
    *,
    dirs: list[Path] | None = None,
) -> list[KicadFootprint]:
    """Scan KiCad footprint directories and return lightweight stubs (no pads loaded).

    Parameters
    ----------
    extra_dirs:
        Additional directories to scan alongside the system defaults.
    dirs:
        If given, replace all defaults and scan only these directories.
        Useful in tests to avoid touching the system installation.
    """
    search_dirs = dirs if dirs is not None else (_SYSTEM_DIRS + _USER_DIRS + (extra_dirs or []))
    stubs: list[KicadFootprint] = []

    for base in search_dirs:
        if not base.is_dir():
            continue
        for lib_dir in sorted(base.iterdir()):
            if not lib_dir.is_dir() or not lib_dir.name.endswith(".pretty"):
                continue
            lib_name = lib_dir.name[:-len(".pretty")]
            for mod_file in sorted(lib_dir.glob("*.kicad_mod")):
                stubs.append(_load_stub(mod_file, lib_name))

    return stubs


def load_pads(stub: KicadFootprint) -> KicadFootprint:
    """Parse pads from the .kicad_mod file and return a new KicadFootprint with pads."""
    try:
        text = stub.path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return stub

    pads: list[KicadPad] = []
    for m in _RE_PAD.finditer(text):
        number, shape_raw, x, y, w, h = m.groups()
        pads.append(KicadPad(
            number=number,
            x_mm=float(x),
            y_mm=float(y),
            w_mm=float(w),
            h_mm=float(h),
            shape=_SHAPE_MAP.get(shape_raw, "rect"),
        ))

    return KicadFootprint(
        name=stub.name,
        library=stub.library,
        path=stub.path,
        description=stub.description,
        tags=stub.tags,
        pads=pads,
    )


def search_index(
    index: list[KicadFootprint],
    query: str = "",
    *,
    pin_count: int | None = None,
    max_results: int = 200,
) -> list[KicadFootprint]:
    """Filter ``index`` stubs by name/tag substring and optional pin count.

    Stubs do not have pads loaded.  Call ``load_pads()`` on the result you want.

    Parameters
    ----------
    query:
        Case-insensitive substring matched against ``name``, ``library``, and ``tags``.
    pin_count:
        If given, only entries whose *filename* contains the pin count as a
        standalone number are returned (e.g. query pin_count=8 matches
        "SOIC-8_…" and "TSSOP-8-1EP_…" but not "SOIC-18_…").
    max_results:
        Cap the number of returned stubs.
    """
    query_lower = query.strip().lower()
    results: list[KicadFootprint] = []

    # Exclude decimal context: "2.8" must not match pin_count=8
    pin_pattern = re.compile(rf"(?<![.\d]){pin_count}(?![.\d])") if pin_count else None

    for stub in index:
        searchable = f"{stub.name} {stub.library} {stub.tags}".lower()
        if query_lower and query_lower not in searchable:
            continue
        if pin_pattern and not pin_pattern.search(stub.name):
            continue
        results.append(stub)
        if len(results) >= max_results:
            break

    return results


def footprint_to_pad_detections(fp: KicadFootprint):
    """Convert a loaded KicadFootprint's pads to a list of PadDetection objects.

    Positions are normalised to [0, 1] relative to the footprint bounding box.
    Returns (pad_detections, bbox_mm) where bbox_mm = (min_x, min_y, w, h) in mm.
    """
    from toolkit.analysis.pinout import BBox, PadDetection

    if not fp.pads:
        return [], (0.0, 0.0, 1.0, 1.0)

    # Compute bounding box in mm (pad centres ± half size)
    xs = [p.x_mm - p.w_mm / 2 for p in fp.pads] + [p.x_mm + p.w_mm / 2 for p in fp.pads]
    ys = [p.y_mm - p.h_mm / 2 for p in fp.pads] + [p.y_mm + p.h_mm / 2 for p in fp.pads]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)

    detections: list[PadDetection] = []
    for pad in fp.pads:
        cx_norm = (pad.x_mm - min_x) / span_x
        cy_norm = (pad.y_mm - min_y) / span_y
        w_norm  = pad.w_mm / span_x
        h_norm  = pad.h_mm / span_y
        detections.append(PadDetection(
            bbox=BBox(
                x=cx_norm - w_norm / 2,
                y=cy_norm - h_norm / 2,
                w=w_norm,
                h=h_norm,
            ),
            shape=pad.shape,
            pin_number=pad.number,
            label="",
        ))

    return detections, (min_x, min_y, span_x, span_y)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _load_stub(path: Path, lib_name: str) -> KicadFootprint:
    """Read only description + tags from a .kicad_mod (fast, no pad parsing)."""
    try:
        # Read only the first 4 KB — header contains desc/tags
        with path.open(encoding="utf-8", errors="replace") as f:
            header = f.read(4096)
    except OSError:
        header = ""

    desc  = (_RE_DESC.search(header) or _RE_TAGS.search(header))
    tags  = _RE_TAGS.search(header)
    return KicadFootprint(
        name=path.stem,
        library=lib_name,
        path=path,
        description=_RE_DESC.search(header).group(1) if _RE_DESC.search(header) else "",
        tags=tags.group(1) if tags else "",
    )
