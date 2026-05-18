"""Unit tests for toolkit.analysis.datasheet_package.

All tests use synthetic text or mock pdftotext — no real PDFs required.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from toolkit.analysis.datasheet_package import (
    PackageHint,
    _count_matches,
    _most_common_pin_count,
    _PATTERNS,
    _pdf_to_text,
    extract_package_hints,
)


# ─── _pdf_to_text ─────────────────────────────────────────────────────────────

class TestPdfToText:
    def test_returns_stdout_on_success(self, tmp_path):
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF dummy")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "SOIC-8 package"
            result = _pdf_to_text(dummy_pdf)
        assert result == "SOIC-8 package"

    def test_returns_empty_on_nonzero_returncode(self, tmp_path):
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF dummy")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = "something"
            result = _pdf_to_text(dummy_pdf)
        assert result == ""

    def test_returns_empty_when_pdftotext_missing(self, tmp_path):
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF dummy")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = _pdf_to_text(dummy_pdf)
        assert result == ""

    def test_returns_empty_on_timeout(self, tmp_path):
        import subprocess
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF dummy")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pdftotext", 30)):
            result = _pdf_to_text(dummy_pdf)
        assert result == ""

    def test_passes_max_pages_arg(self, tmp_path):
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF dummy")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            _pdf_to_text(dummy_pdf, max_pages=2)
        args = mock_run.call_args[0][0]
        assert "-l" in args
        assert "2" in args


# ─── _count_matches ───────────────────────────────────────────────────────────

class TestCountMatches:
    def test_returns_pin_count_strings(self):
        import re
        pat = re.compile(r"\bSOIC[- ]?(\d+)\b", re.I)
        result = _count_matches("SOIC-8 and SOIC-16 and SOIC8", pat)
        assert sorted(result) == ["16", "8", "8"]

    def test_returns_empty_when_no_match(self):
        import re
        pat = re.compile(r"\bSOIC[- ]?(\d+)\b", re.I)
        assert _count_matches("nothing here", pat) == []

    def test_case_insensitive(self):
        import re
        pat = re.compile(r"\bsoic[- ]?(\d+)\b", re.I)
        result = _count_matches("SOIC-8 soic-16 Soic-20", pat)
        assert len(result) == 3


# ─── _most_common_pin_count ───────────────────────────────────────────────────

class TestMostCommonPinCount:
    def test_returns_most_frequent(self):
        assert _most_common_pin_count(["8", "8", "16"]) == 8

    def test_returns_0_on_empty(self):
        assert _most_common_pin_count([]) == 0

    def test_ignores_out_of_range(self):
        # values below 2 or above 1024 are excluded
        assert _most_common_pin_count(["1", "0", "2000"]) == 0

    def test_handles_non_numeric(self):
        assert _most_common_pin_count(["abc", "8", "8"]) == 8

    def test_tiebreak_picks_one(self):
        result = _most_common_pin_count(["8", "16"])
        assert result in (8, 16)


# ─── extract_package_hints ────────────────────────────────────────────────────

def _fake_pdf(text: str):
    """Context manager that patches _pdf_to_text to return *text*."""
    return patch("toolkit.analysis.datasheet_package._pdf_to_text", return_value=text)


class TestExtractPackageHints:
    def _run(self, text: str) -> list[PackageHint]:
        with _fake_pdf(text):
            return extract_package_hints(Path("dummy.pdf"))

    def test_returns_empty_on_blank_text(self):
        assert self._run("") == []
        assert self._run("   ") == []

    def test_detects_soic8(self):
        hints = self._run("The device comes in SOIC-8 package.")
        names = [h.name for h in hints]
        assert any("SOIC" in n for n in names)

    def test_detects_pin_count(self):
        hints = self._run("SOIC-8 SOIC-8 SOIC-8")
        soic = next((h for h in hints if "SOIC" in h.name), None)
        assert soic is not None
        assert soic.pin_count == 8

    def test_dominant_package_has_highest_confidence(self):
        # SOIC-8 mentioned 5×, QFN-16 mentioned 1×
        text = "SOIC-8 " * 5 + "QFN-16"
        hints = self._run(text)
        assert hints[0].name.startswith("SOIC")

    def test_confidence_between_0_and_1(self):
        hints = self._run("SOIC-8 TSSOP-20 QFP-44")
        for h in hints:
            assert 0.0 <= h.confidence <= 1.0

    def test_sorted_descending_by_confidence(self):
        hints = self._run("SOIC-8 SOIC-8 SOIC-8 QFN-16")
        confs = [h.confidence for h in hints]
        assert confs == sorted(confs, reverse=True)

    def test_tssop_maps_to_package_so(self):
        hints = self._run("TSSOP-20 TSSOP-20 TSSOP-20")
        assert hints[0].name.startswith("TSSOP")

    def test_qfp_detected(self):
        hints = self._run("64-lead LQFP-64 package, LQFP64, LQFP-64")
        names = [h.name for h in hints]
        assert any("LQFP" in n or "QFP" in n for n in names)

    def test_qfn_detected(self):
        hints = self._run("QFN-32 exposed pad, QFN32, QFN-32")
        names = [h.name for h in hints]
        assert any("QFN" in n for n in names)

    def test_bga_detected(self):
        hints = self._run("256-ball BGA-256 package")
        names = [h.name for h in hints]
        assert any("BGA" in n for n in names)

    def test_dip_detected(self):
        hints = self._run("PDIP-8 or DIP-8 package")
        names = [h.name for h in hints]
        assert any("DIP" in n for n in names)

    def test_sot_detected(self):
        hints = self._run("SOT-23 three-terminal package")
        names = [h.name for h in hints]
        assert any("SOT" in n for n in names)

    def test_kicad_query_contains_name(self):
        hints = self._run("SOIC-8 SOIC-8")
        soic = next((h for h in hints if "SOIC" in h.name), None)
        assert soic is not None
        assert "SOIC" in soic.kicad_query

    def test_no_match_returns_empty(self):
        hints = self._run("The quick brown fox jumped over the lazy dog.")
        assert hints == []

    def test_multiple_packages_all_returned(self):
        hints = self._run("SOIC-8 SOIC-8 TSSOP-20 TSSOP-20 QFN-16")
        names = [h.name for h in hints]
        assert any("SOIC" in n for n in names)
        assert any("TSSOP" in n for n in names)
        assert any("QFN" in n for n in names)

    def test_package_hint_is_sorted_type(self):
        """PackageHint must support comparison (for list.sort())."""
        h1 = PackageHint(name="A", pin_count=8, kicad_query="A", confidence=0.8)
        h2 = PackageHint(name="B", pin_count=16, kicad_query="B", confidence=0.2)
        assert h1 < h2  # higher confidence sorts earlier (_sort_key = -confidence)
