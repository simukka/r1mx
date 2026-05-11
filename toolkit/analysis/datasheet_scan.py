"""
datasheet_scan.py — Score PDF files against a part-number query.

Two independent signals are combined:

  1. **Filename similarity** — longest-common-subsequence of the normalised
     part number against the PDF stem.  Fast, no I/O.

  2. **Content match** — `pdftotext -q -l 3 <pdf> -` is called as a
     subprocess; the extracted text is searched for the normalised part
     number as a substring.  Gracefully skipped when pdftotext is absent
     or the PDF is image-only.

Combined score::

    score = max(fn, ct) + 0.2 * fn * ct   # bonus when both agree

Thresholds used by the UI:
  - score ≥ 0.6  → pre-checked (strong match)
  - score ≥ 0.2  → unchecked/dimmed (weak match, shown by default)
  - score < 0.2  → hidden unless "Show all" is enabled
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Generator


# ── normalisation ────────────────────────────────────────────────────────────

def normalise(text: str) -> str:
    """Lowercase and strip all non-alphanumeric characters."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


# ── signal 1: filename similarity (LCS ratio) ────────────────────────────────

def _lcs_length(a: str, b: str) -> int:
    """Length of the longest common subsequence of two strings."""
    if not a or not b:
        return 0
    # Use a rolling 1-D DP to keep memory O(min(|a|,|b|))
    if len(a) < len(b):
        a, b = b, a
    prev = [0] * (len(b) + 1)
    for ca in a:
        curr = [0] * (len(b) + 1)
        for j, cb in enumerate(b, 1):
            curr[j] = prev[j - 1] + 1 if ca == cb else max(prev[j], curr[j - 1])
        prev = curr
    return prev[len(b)]


def score_filename(part_number: str, pdf_path: Path) -> float:
    """Return 0–1 similarity between the part number and the PDF file stem."""
    norm_part = normalise(part_number)
    norm_stem = normalise(pdf_path.stem)
    if not norm_part or not norm_stem:
        return 0.0
    lcs = _lcs_length(norm_part, norm_stem)
    return lcs / max(len(norm_part), len(norm_stem))


# ── signal 2: content match via pdftotext ────────────────────────────────────

def score_content(part_number: str, pdf_path: Path, max_pages: int = 3) -> float:
    """Return 1.0 if the part number appears in the first *max_pages* pages, else 0.0.

    Uses ``pdftotext`` (poppler-utils).  Returns 0.0 silently when:
    - pdftotext is not installed
    - the PDF is image-only (no extractable text)
    - any subprocess error occurs
    """
    norm_part = normalise(part_number)
    if not norm_part:
        return 0.0
    try:
        result = subprocess.run(
            ["pdftotext", "-q", "-l", str(max_pages), str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return 0.0
        text = normalise(result.stdout)
        return 1.0 if norm_part in text else 0.0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return 0.0


# ── combined score ────────────────────────────────────────────────────────────

def score_pdf(part_number: str, pdf_path: Path) -> float:
    """Combined 0–1 score for a PDF against a part number.

    Score formula::

        score = max(fn, ct) + 0.2 * fn * ct

    The additive bonus rewards PDFs where both filename *and* content match.
    """
    fn = score_filename(part_number, pdf_path)
    ct = score_content(part_number, pdf_path)
    return min(1.0, max(fn, ct) + 0.2 * fn * ct)


# ── folder scanner ────────────────────────────────────────────────────────────

def scan_folder(
    part_number: str,
    folder: Path,
    *,
    recursive: bool = True,
) -> Generator[tuple[float, Path], None, None]:
    """Yield ``(score, pdf_path)`` for every PDF found in *folder*.

    Results are yielded as they are scored (not pre-sorted) so the caller
    (typically a QThread worker) can stream them to the UI in real time.
    Sort by score descending after collecting all results if needed.

    Parameters
    ----------
    part_number:
        The label to search for (e.g. ``"SII3512ECTU128"``).
    folder:
        Directory to scan.  Only files with ``.pdf`` / ``.PDF`` extension
        are considered.
    recursive:
        When True (default), recurse into sub-directories.
    """
    glob_fn = folder.rglob if recursive else folder.glob
    for pdf in sorted(glob_fn("*.pdf")) + sorted(glob_fn("*.PDF")):
        if pdf.is_file():
            yield score_pdf(part_number, pdf), pdf
