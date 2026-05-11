"""Extract IC package hints from a datasheet PDF.

Uses ``pdftotext`` (part of poppler-utils) to get plain text, then applies
regex patterns to identify package names (SOIC, QFP, TSSOP, QFN, BGA, …),
counts mentions, and returns a ranked list of ``PackageHint`` objects.

Usage::

    from toolkit.analysis.datasheet_package import extract_package_hints

    hints = extract_package_hints(Path("datasheet.pdf"))
    for h in hints:
        print(h.name, h.pin_count, h.kicad_query, h.confidence)
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


# ─── Data class ──────────────────────────────────────────────────────────────

@dataclass(order=True)
class PackageHint:
    """One package candidate extracted from a datasheet."""

    # sort key: descending confidence
    _sort_key: float = field(init=False, repr=False, compare=True)

    name:         str    # normalised package name, e.g. "SOIC-8"
    pin_count:    int    # 0 if unknown
    kicad_query:  str    # suggested search string for FootprintPickerDialog
    confidence:   float  # 0.0–1.0; based on mention frequency
    source:       str = "datasheet_text"

    def __post_init__(self) -> None:
        object.__setattr__(self, "_sort_key", -self.confidence)


# ─── Package pattern table ────────────────────────────────────────────────────
#
# Each entry: (canonical_prefix, kicad_family, regex_pattern)
# The pattern must capture an optional pin count in group 1.
# Ordered most-specific first to avoid shadowing.

_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    # SSOP / TSSOP / MSOP / HSOP
    ("TSSOP",  "Package_SO",      re.compile(r"\bTSSOP[- ]?(\d+)\b",      re.I)),
    ("SSOP",   "Package_SO",      re.compile(r"\bSSOP[- ]?(\d+)\b",       re.I)),
    ("MSOP",   "Package_SO",      re.compile(r"\bMSOP[- ]?(\d+)\b",       re.I)),
    ("HSOP",   "Package_SO",      re.compile(r"\bHSOP[- ]?(\d+)\b",       re.I)),
    # SOIC / SOP / SO variants
    ("SOIC",   "Package_SO",      re.compile(r"\bSOIC[- ]?(\d+)\b",       re.I)),
    ("SOP",    "Package_SO",      re.compile(r"\bSOP[- ]?(\d+)\b",        re.I)),
    ("SO",     "Package_SO",      re.compile(r"\bSO[- ](\d+)\b",          re.I)),  # require separator
    # QFP family
    ("LQFP",   "Package_QFP",    re.compile(r"\bLQFP[- ]?(\d+)\b",       re.I)),
    ("TQFP",   "Package_QFP",    re.compile(r"\bTQFP[- ]?(\d+)\b",       re.I)),
    ("QFP",    "Package_QFP",    re.compile(r"\bQFP[- ]?(\d+)\b",        re.I)),
    # QFN / DFN / MLF / LLP
    ("QFN",    "Package_DFN_QFN", re.compile(r"\bQFN[- ]?(\d+)\b",       re.I)),
    ("DFN",    "Package_DFN_QFN", re.compile(r"\bDFN[- ]?(\d+)\b",       re.I)),
    ("MLF",    "Package_DFN_QFN", re.compile(r"\bMLF[- ]?(\d+)\b",       re.I)),
    ("LLP",    "Package_DFN_QFN", re.compile(r"\bLLP[- ]?(\d+)\b",       re.I)),
    # BGA / CSP
    ("BGA",    "Package_BGA",     re.compile(r"\bBGA[- ]?(\d+)\b",        re.I)),
    ("WLCSP",  "Package_BGA",     re.compile(r"\bWLCSP[- ]?(\d+)\b",      re.I)),
    ("CSP",    "Package_BGA",     re.compile(r"\bCSP[- ]?(\d+)\b",        re.I)),
    # DIP / PDIP / SOIC-W
    ("SOICW",  "Package_SO",      re.compile(r"\bSOIC[- ]?W[- ]?(\d+)\b", re.I)),
    ("DIP",    "Package_DIP",     re.compile(r"\b(?:P|D)?DIP[- ]?(\d+)\b",re.I)),
    # SOT / SC
    ("SOT",    "Package_TO_SOT_SMD", re.compile(r"\bSOT[- ]?(\d+)[A-Z]?\b", re.I)),
    ("SC",     "Package_TO_SOT_SMD", re.compile(r"\bSC[- ]?(\d+)[A-Z]?\b",  re.I)),
    # TO (transistor outline — THT)
    ("TO",     "Package_TO_SOT_THT", re.compile(r"\bTO[- ](\d+)[A-Z]?\b",   re.I)),
    # Connector / module (broad fallback — low confidence)
    ("SIP",    "Connector_PinHeader_2.54mm", re.compile(r"\bSIP[- ]?(\d+)\b", re.I)),
    ("DIP",    "Package_DIP",     re.compile(r"\bDIL[- ]?(\d+)\b",        re.I)),
]

# Pin-count-only mention patterns: "8-pin", "16 pin", "8 lead", "8 ld"
_PIN_COUNT_RE = re.compile(
    r"\b(\d+)[- ]?(?:pin|lead|ld|pad|ball)s?\b", re.I
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _pdf_to_text(pdf_path: Path, max_pages: int = 4) -> str:
    """Return plain text from the first *max_pages* pages of *pdf_path*.

    Returns an empty string if ``pdftotext`` is not available or fails.
    """
    try:
        result = subprocess.run(
            ["pdftotext", f"-l", str(max_pages), str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout if result.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


def _count_matches(text: str, pattern: re.Pattern) -> list[str]:
    """Return all non-overlapping match group(1) values (pin counts as strings)."""
    return [m.group(1) for m in pattern.finditer(text) if m.group(1)]


def _most_common_pin_count(values: list[str]) -> int:
    """Return the most commonly mentioned integer, or 0 if *values* is empty."""
    if not values:
        return 0
    freq: dict[int, int] = {}
    for v in values:
        try:
            n = int(v)
            if 2 <= n <= 1024:
                freq[n] = freq.get(n, 0) + 1
        except ValueError:
            pass
    if not freq:
        return 0
    return max(freq, key=lambda k: freq[k])


# ─── Public API ───────────────────────────────────────────────────────────────

def extract_package_hints(
    pdf_path: Path,
    max_pages: int = 4,
) -> list[PackageHint]:
    """Extract and rank package hints from a datasheet PDF.

    Parameters
    ----------
    pdf_path:
        Path to a PDF file.
    max_pages:
        Number of pages to scan (default 4 — covers page 1 header + ordering
        information table where package names are densest).

    Returns
    -------
    List of ``PackageHint`` sorted by descending confidence.  May be empty if
    ``pdftotext`` is unavailable or the PDF contains no recognisable package names.
    """
    text = _pdf_to_text(pdf_path, max_pages=max_pages)
    if not text.strip():
        return []

    # --- First pass: per-pattern counts ----------------------------------------
    # counts[canonical_prefix] = {"mentions": int, "pin_counts": list[str], "kicad": str}
    totals: dict[str, dict] = {}
    total_matches = 0

    for canonical, kicad_family, pattern in _PATTERNS:
        pin_strings = _count_matches(text, pattern)
        if not pin_strings:
            # Also check if the bare prefix (no pin count) appears at all
            bare_re = re.compile(rf"\b{re.escape(canonical)}\b", re.I)
            bare_count = len(bare_re.findall(text))
            if bare_count == 0:
                continue
            pin_strings = []
            mention_count = bare_count
        else:
            mention_count = len(pin_strings)

        key = canonical.upper()
        if key not in totals:
            totals[key] = {"mentions": 0, "pin_strings": [], "kicad": kicad_family}
        totals[key]["mentions"]    += mention_count
        totals[key]["pin_strings"] += pin_strings
        total_matches              += mention_count

    if not totals or total_matches == 0:
        return []

    # --- Second pass: build PackageHint list ------------------------------------
    hints: list[PackageHint] = []
    for key, data in totals.items():
        pin = _most_common_pin_count(data["pin_strings"])
        # Normalised confidence: fraction of all package mentions
        confidence = min(data["mentions"] / total_matches, 1.0)

        # Build the KiCad search query: "Package_SO SOIC-8" or just "SOIC-8"
        if pin:
            name = f"{key}-{pin}"
            kicad_query = f"{name}"
        else:
            name = key
            kicad_query = f"{key}"

        hints.append(
            PackageHint(
                name=name,
                pin_count=pin,
                kicad_query=kicad_query,
                confidence=round(confidence, 3),
            )
        )

    # Sort by confidence descending (handled by __post_init__ _sort_key)
    hints.sort()
    return hints
