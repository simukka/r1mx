"""Unit tests for toolkit.gui.dialogs.datasheet_find — pure-logic helpers.

We test _render_page() and _count_pages() by mocking subprocess.run so no
real PDFs or system tools are needed.  Qt widgets are not instantiated.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from toolkit.gui.dialogs.datasheet_find import _count_pages, _render_page


# ─── _count_pages ────────────────────────────────────────────────────────────

class TestCountPages:
    def _make_pdfinfo_result(self, stdout: str) -> MagicMock:
        m = MagicMock()
        m.stdout = stdout
        m.returncode = 0
        return m

    def test_parses_single_digit(self):
        with patch("subprocess.run", return_value=self._make_pdfinfo_result("Pages:  5\n")):
            assert _count_pages(Path("x.pdf")) == 5

    def test_parses_multi_digit(self):
        with patch("subprocess.run", return_value=self._make_pdfinfo_result("Pages: 128\n")):
            assert _count_pages(Path("x.pdf")) == 128

    def test_pages_among_other_lines(self):
        stdout = (
            "Creator:  Adobe Acrobat\n"
            "Pages:    42\n"
            "File size: 1234 bytes\n"
        )
        with patch("subprocess.run", return_value=self._make_pdfinfo_result(stdout)):
            assert _count_pages(Path("x.pdf")) == 42

    def test_returns_1_when_pages_line_absent(self):
        with patch("subprocess.run", return_value=self._make_pdfinfo_result("Creator: Word\n")):
            assert _count_pages(Path("x.pdf")) == 1

    def test_returns_1_when_pdfinfo_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert _count_pages(Path("x.pdf")) == 1

    def test_returns_1_on_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pdfinfo", 10)):
            assert _count_pages(Path("x.pdf")) == 1

    def test_returns_1_on_other_exception(self):
        with patch("subprocess.run", side_effect=OSError("no such file")):
            assert _count_pages(Path("x.pdf")) == 1

    def test_calls_pdfinfo_with_correct_path(self):
        pdf = Path("/some/dir/test.pdf")
        with patch("subprocess.run", return_value=self._make_pdfinfo_result("Pages: 1\n")) as mock_run:
            _count_pages(pdf)
        args = mock_run.call_args[0][0]
        assert "pdfinfo" in args
        assert str(pdf) in args


# ─── _render_page ────────────────────────────────────────────────────────────

class TestRenderPage:
    """Test _render_page() logic without actually running pdftoppm or loading PNG."""

    def test_returns_none_when_pdftoppm_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = _render_page(Path("x.pdf"), page_number=1)
        assert result is None

    def test_returns_none_on_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pdftoppm", 15)):
            result = _render_page(Path("x.pdf"), page_number=1)
        assert result is None

    def test_returns_none_when_output_file_missing(self, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            # No PNG is created in tmp_path, so _render_page should return None.
            result = _render_page(Path("x.pdf"), page_number=1)
        assert result is None

    def test_passes_correct_page_numbers_to_pdftoppm(self):
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _render_page(Path("/a/b.pdf"), page_number=7)

        args = mock_run.call_args[0][0]
        # -f and -l flags must both be "7"
        assert "-f" in args
        assert "-l" in args
        f_idx = args.index("-f")
        l_idx = args.index("-l")
        assert args[f_idx + 1] == "7"
        assert args[l_idx + 1] == "7"

    def test_passes_pdf_path_to_pdftoppm(self):
        mock_result = MagicMock(returncode=0)
        pdf = Path("/my/data/part.pdf")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _render_page(pdf, page_number=1)

        args = mock_run.call_args[0][0]
        assert str(pdf) in args

    def test_uses_png_flag(self):
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _render_page(Path("x.pdf"), page_number=1)

        args = mock_run.call_args[0][0]
        assert "-png" in args

    def test_uses_singlefile_flag(self):
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _render_page(Path("x.pdf"), page_number=1)

        args = mock_run.call_args[0][0]
        assert "-singlefile" in args

    def test_dpi_argument_present(self):
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _render_page(Path("x.pdf"), page_number=1, dpi=72)

        args = mock_run.call_args[0][0]
        assert "-r" in args
        r_idx = args.index("-r")
        assert args[r_idx + 1] == "72"
