#!/usr/bin/env python3
"""
fetch_datasheets.py — Datasheet downloader for r1mx BOM components.

Reads a BOM CSV produced by extract_bom.py and attempts to find + download a
PDF datasheet for each distinct searchable component.  Sources tried in order:

  1. AllDatasheet.com           (HTML scrape, free)
  2. Datasheet-PDF.com          (HTML scrape, free)
  3. DatasheetsPDF.com          (HTML scrape, free)
  4. DuckDuckGo HTML search     (HTML scrape, finds direct PDF links, free)
  5. Wayback Machine CDX API    (archived PDF fallback, free)
  6. Octopart GraphQL API       (opt-in via --use-octopart; only 10 free
                                 requests/month — use sparingly for important ICs)

Results are saved to each board's  components/{board}/datasheets/  folder and
a summary CSV is written alongside the input BOM.

Usage:
    # All boards, all searchable components
    python scripts/fetch_datasheets.py

    # Single board
    python scripts/fetch_datasheets.py --board cpu_io_board

    # Dry run — show what would be searched
    python scripts/fetch_datasheets.py --dry-run

    # Force re-download of existing files
    python scripts/fetch_datasheets.py --force

    # Use a specific BOM file
    python scripts/fetch_datasheets.py --bom components/cpu_io_board/bom.csv

    # Also try Octopart (10 req/month limit — use carefully)
    python scripts/fetch_datasheets.py --use-octopart --octopart-token YOUR_TOKEN
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"

# ref_types worth searching for datasheets (skip plain passives)
DEFAULT_REF_TYPES = {"IC", "PartNumber", "Component", "Diode", "Transistor", "Fuse"}

# HTTP session shared across all requests
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (compatible; r1mx-datasheet-fetcher/1.0; "
        "+https://github.com/simook/r1mx)"
    )
})

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class BomEntry:
    board: str
    reference: str
    ref_type: str


@dataclass
class FetchResult:
    board: str
    reference: str
    ref_type: str
    source: str = ""
    datasheet_url: str = ""
    local_path: str = ""
    status: str = "not_found"   # found | downloaded | skipped | failed | not_found


# ---------------------------------------------------------------------------
# BOM loading
# ---------------------------------------------------------------------------

def load_bom(bom_path: Path, boards: list[str], ref_types: set[str]) -> list[BomEntry]:
    """Load BOM CSV and return deduplicated searchable entries."""
    entries: dict[tuple[str, str], BomEntry] = {}
    with bom_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            board = row.get("board", "").strip()
            reference = row.get("reference", "").strip()
            ref_type = row.get("ref_type", "").strip()

            if not board or not reference:
                continue
            if boards and board not in boards:
                continue
            if ref_type not in ref_types:
                continue

            key = (board, reference)
            if key not in entries:
                entries[key] = BomEntry(board=board, reference=reference, ref_type=ref_type)

    log.info("Loaded %d distinct searchable entries from %s", len(entries), bom_path)
    return list(entries.values())


# ---------------------------------------------------------------------------
# Source 1: AllDatasheet.com
# ---------------------------------------------------------------------------

ALLDATASHEET_SEARCH = "https://www.alldatasheet.com/view.jsp?Searchword={}"


def _alldatasheet_find(part_number: str) -> Optional[str]:
    """Scrape AllDatasheet.com and return a direct PDF URL, or None."""
    url = ALLDATASHEET_SEARCH.format(quote_plus(part_number))
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("AllDatasheet request failed for %s: %s", part_number, exc)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Look for links containing the part number that end with .pdf or point to
    # the datasheet detail page (e.g. /datasheet-html/…)
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if re.search(r"\.pdf$", href, re.IGNORECASE):
            return href if href.startswith("http") else urljoin(url, href)
        # AllDatasheet uses detail pages: /datasheet-pdf/{PART}.html
        if "datasheet-pdf" in href and part_number.lower() in href.lower():
            detail_url = href if href.startswith("http") else urljoin(url, href)
            pdf_url = _scrape_first_pdf_link(detail_url)
            if pdf_url:
                return pdf_url
    return None


# ---------------------------------------------------------------------------
# Source 2: Datasheet-PDF.com
# ---------------------------------------------------------------------------

DATASHEET_PDF_SEARCH = "https://www.datasheet-pdf.com/search.php?q={}"


def _datasheetpdf_find(part_number: str) -> Optional[str]:
    """Scrape Datasheet-PDF.com and return a direct PDF URL, or None."""
    url = DATASHEET_PDF_SEARCH.format(quote_plus(part_number))
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Datasheet-PDF request failed for %s: %s", part_number, exc)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if re.search(r"\.pdf$", href, re.IGNORECASE):
            return href if href.startswith("http") else urljoin(url, href)
    return None


# ---------------------------------------------------------------------------
# Source 4: DatasheetsPDF.com
# ---------------------------------------------------------------------------

DATASHEETSPDF_SEARCH = "https://datasheetspdf.com/search/?q={}"


def _datasheetspdf_find(part_number: str) -> Optional[str]:
    """Scrape DatasheetsPDF.com and return a direct PDF URL, or None."""
    url = DATASHEETSPDF_SEARCH.format(quote_plus(part_number))
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("DatasheetsPDF request failed for %s: %s", part_number, exc)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if re.search(r"\.pdf$", href, re.IGNORECASE):
            return href if href.startswith("http") else urljoin(url, href)
        # Detail page pattern: /pdf/{ID}/{PARTNAME}-datasheet.html
        if "datasheet" in href and part_number.lower() in href.lower():
            detail_url = href if href.startswith("http") else urljoin(url, href)
            pdf_url = _scrape_first_pdf_link(detail_url)
            if pdf_url:
                return pdf_url
    return None


# ---------------------------------------------------------------------------
# Source 5: DuckDuckGo HTML search
# ---------------------------------------------------------------------------

DDG_SEARCH = "https://html.duckduckgo.com/html/?q={}"

# Regex to pick out direct PDF URLs from DDG result pages
_PDF_URL_RE = re.compile(r'https?://[^\s"\'<>]+\.pdf', re.IGNORECASE)


def _duckduckgo_find(part_number: str) -> Optional[str]:
    """
    Scrape DuckDuckGo HTML search for a direct PDF link mentioning the part number.
    Searches for: {part_number} datasheet filetype:pdf
    """
    query = f"{part_number} datasheet filetype:pdf"
    url = DDG_SEARCH.format(quote_plus(query))
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("DuckDuckGo request failed for %s: %s", part_number, exc)
        return None

    # Look for direct PDF URLs embedded anywhere in the page
    for match in _PDF_URL_RE.finditer(resp.text):
        candidate = match.group(0)
        # Prefer URLs that contain the part number for relevance
        if part_number.lower() in candidate.lower():
            return candidate

    # Fallback: any PDF URL on the page
    m = _PDF_URL_RE.search(resp.text)
    return m.group(0) if m else None


# ---------------------------------------------------------------------------
# Source 6: Wayback Machine CDX API
# ---------------------------------------------------------------------------

WAYBACK_CDX = (
    "https://web.archive.org/cdx/search/cdx"
    "?url=*{part}*.pdf"
    "&output=json"
    "&fl=original,timestamp,statuscode"
    "&filter=statuscode:200"
    "&collapse=urlkey"
    "&limit=5"
)

WAYBACK_FETCH = "https://web.archive.org/web/{timestamp}/{url}"


def _wayback_find(part_number: str) -> Optional[str]:
    """Search the Wayback Machine CDX index for an archived datasheet PDF."""
    try:
        resp = SESSION.get(
            WAYBACK_CDX.format(part=quote_plus(part_number)),
            timeout=20,
        )
        resp.raise_for_status()
        rows = resp.json()
    except Exception as exc:
        log.debug("Wayback CDX request failed for %s: %s", part_number, exc)
        return None

    # rows[0] is the header row; skip it
    if len(rows) < 2:
        return None

    for row in rows[1:]:
        if len(row) < 3:
            continue
        original_url, timestamp, _status = row[0], row[1], row[2]
        # Prefer URLs that contain the part number in the filename
        if part_number.lower() in original_url.lower():
            return WAYBACK_FETCH.format(timestamp=timestamp, url=original_url)

    # Fallback: return first result regardless of filename
    orig, ts = rows[1][0], rows[1][1]
    return WAYBACK_FETCH.format(timestamp=ts, url=orig)


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _scrape_first_pdf_link(url: str) -> Optional[str]:
    """GET *url* and return the first .pdf href found on the page."""
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if re.search(r"\.pdf$", href, re.IGNORECASE):
            return href if href.startswith("http") else urljoin(url, href)
    return None


# ---------------------------------------------------------------------------
# Source 7: Octopart GraphQL API  (opt-in — only ~10 free requests/month)
# ---------------------------------------------------------------------------

OCTOPART_ENDPOINT = "https://octopart.com/api/v4/endpoint"

OCTOPART_QUERY = """
query DatasheetSearch($q: String!) {
  search(q: $q, limit: 3) {
    results {
      part {
        mpn
        manufacturer { name }
        document_collections {
          documents {
            name
            url
          }
        }
      }
    }
  }
}
"""


def _octopart_find(part_number: str, token: str) -> Optional[str]:
    """Return the URL of the first datasheet PDF found via Octopart, or None.

    WARNING: The Octopart free tier allows only ~10 requests/month.
    Enable with --use-octopart and use only for the most important ICs.
    """
    try:
        resp = SESSION.post(
            OCTOPART_ENDPOINT,
            json={"query": OCTOPART_QUERY, "variables": {"q": part_number}},
            headers={"token": token},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Octopart request failed for %s: %s", part_number, exc)
        return None

    data = resp.json()
    results = (data.get("data") or {}).get("search", {}).get("results", [])
    for result in results:
        part = result.get("part", {})
        for coll in part.get("document_collections", []):
            for doc in coll.get("documents", []):
                url = doc.get("url", "")
                name = doc.get("name", "").lower()
                if url.lower().endswith(".pdf") or "datasheet" in name:
                    return url
    return None


# ---------------------------------------------------------------------------
# PDF download
# ---------------------------------------------------------------------------

def download_pdf(url: str, dest: Path, timeout: int = 30) -> bool:
    """
    Download a PDF from *url* to *dest*.  Returns True on success.
    Performs a lightweight content-type check to reject non-PDF responses.
    """
    try:
        resp = SESSION.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Download failed for %s: %s", url, exc)
        return False

    content_type = resp.headers.get("Content-Type", "").lower()
    if "pdf" not in content_type and not url.lower().endswith(".pdf"):
        # Peek at first bytes to check magic
        first_bytes = next(resp.iter_content(chunk_size=8), b"")
        if not first_bytes.startswith(b"%PDF"):
            log.debug("Response is not a PDF for %s (Content-Type: %s)", url, content_type)
            return False
        # Write what we already have, then continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fh:
            fh.write(first_bytes)
            for chunk in resp.iter_content(chunk_size=65536):
                fh.write(chunk)
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=65536):
            fh.write(chunk)
    return True


# ---------------------------------------------------------------------------
# Results CSV
# ---------------------------------------------------------------------------

RESULTS_FIELDNAMES = [
    "board", "reference", "ref_type",
    "source", "datasheet_url", "local_path", "status",
]


def write_results(results: list[FetchResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=RESULTS_FIELDNAMES)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "board": r.board,
                "reference": r.reference,
                "ref_type": r.ref_type,
                "source": r.source,
                "datasheet_url": r.datasheet_url,
                "local_path": r.local_path,
                "status": r.status,
            })
    log.info("Results written to %s", output_path)


# ---------------------------------------------------------------------------
# Core fetch logic
# ---------------------------------------------------------------------------

def fetch_one(
    entry: BomEntry,
    use_octopart: bool,
    octopart_token: Optional[str],
    output_dir: Optional[Path],
    force: bool,
    dry_run: bool,
    delay: float,
) -> FetchResult:
    result = FetchResult(board=entry.board, reference=entry.reference, ref_type=entry.ref_type)

    # Determine output path
    if output_dir:
        dest = output_dir / f"{entry.reference}.pdf"
    else:
        board_dir = COMPONENTS_DIR / entry.board / "datasheets"
        dest = board_dir / f"{entry.reference}.pdf"

    # Skip if already downloaded
    if dest.exists() and not force:
        log.debug("Already exists, skipping: %s", dest)
        result.status = "skipped"
        result.local_path = str(dest)
        return result

    part = entry.reference
    log.debug("Searching for: %s (%s / %s)", part, entry.board, entry.ref_type)

    if dry_run:
        result.status = "dry_run"
        return result

    pdf_url: Optional[str] = None
    source_name: str = ""

    # --- Source 1: AllDatasheet ---
    if not pdf_url:
        pdf_url = _alldatasheet_find(part)
        if pdf_url:
            source_name = "alldatasheet"
        time.sleep(delay)

    # --- Source 2: Datasheet-PDF.com ---
    if not pdf_url:
        pdf_url = _datasheetpdf_find(part)
        if pdf_url:
            source_name = "datasheet-pdf.com"
        time.sleep(delay)

    # --- Source 3: DatasheetsPDF.com ---
    if not pdf_url:
        pdf_url = _datasheetspdf_find(part)
        if pdf_url:
            source_name = "datasheetspdf.com"
        time.sleep(delay)

    # --- Source 4: DuckDuckGo HTML search ---
    if not pdf_url:
        pdf_url = _duckduckgo_find(part)
        if pdf_url:
            source_name = "duckduckgo"
        time.sleep(delay)

    # --- Source 5: Wayback Machine ---
    if not pdf_url:
        pdf_url = _wayback_find(part)
        if pdf_url:
            source_name = "wayback"
        time.sleep(delay)

    # --- Source 6: Octopart (opt-in, ~10 req/month limit) ---
    if not pdf_url and use_octopart and octopart_token:
        pdf_url = _octopart_find(part, octopart_token)
        if pdf_url:
            source_name = "octopart"
        time.sleep(delay)

    if not pdf_url:
        result.status = "not_found"
        return result

    result.datasheet_url = pdf_url
    result.source = source_name

    # Download
    ok = download_pdf(pdf_url, dest)
    if ok:
        result.status = "downloaded"
        result.local_path = str(dest)
        log.info("✓ %s → %s  [%s]", part, dest.name, source_name)
    else:
        result.status = "failed"
        log.warning("✗ %s — download failed from %s", part, pdf_url)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find and download datasheets for components in a r1mx BOM CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--bom",
        type=Path,
        default=REPO_ROOT / "bom_master.csv",
        help="BOM CSV file to read.",
    )
    parser.add_argument(
        "--board",
        action="append",
        dest="boards",
        default=[],
        metavar="BOARD",
        help="Only process this board (can be repeated).",
    )
    parser.add_argument(
        "--ref-types",
        default=",".join(sorted(DEFAULT_REF_TYPES)),
        help="Comma-separated ref_type values to include.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override output directory (default: components/{board}/datasheets/).",
    )
    parser.add_argument(
        "--results-csv",
        type=Path,
        default=None,
        help="Path for the results summary CSV (default: fetch_results.csv next to --bom).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if file already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be searched/downloaded; no network calls.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Seconds to wait between requests per source.",
    )
    parser.add_argument(
        "--octopart-token",
        default=None,
        metavar="TOKEN",
        help="Octopart API token (overrides OCTOPART_TOKEN env var).",
    )
    parser.add_argument(
        "--use-octopart",
        action="store_true",
        help=(
            "Enable Octopart as a last-resort source. "
            "WARNING: the free tier has only ~10 requests/month. "
            "Requires --octopart-token or OCTOPART_TOKEN env var."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    bom_path: Path = args.bom
    if not bom_path.exists():
        log.error("BOM file not found: %s", bom_path)
        return 1

    ref_types = {rt.strip() for rt in args.ref_types.split(",") if rt.strip()}

    octopart_token: Optional[str] = (
        args.octopart_token or os.environ.get("OCTOPART_TOKEN")
    )
    use_octopart: bool = getattr(args, "use_octopart", False)
    if use_octopart and not octopart_token:
        log.warning(
            "--use-octopart set but no token found. "
            "Set OCTOPART_TOKEN env var or use --octopart-token. "
            "Octopart source will be skipped."
        )
        use_octopart = False
    if use_octopart:
        log.warning(
            "Octopart enabled. Free tier limit is ~10 requests/month — use sparingly."
        )

    entries = load_bom(bom_path, boards=args.boards, ref_types=ref_types)
    if not entries:
        log.warning("No matching entries found — check --board and --ref-types filters.")
        return 0

    results_path: Path = args.results_csv or bom_path.parent / "fetch_results.csv"

    if args.dry_run:
        log.info("Dry run — would search for %d components:", len(entries))
        for e in entries:
            dest = (
                args.output_dir / f"{e.reference}.pdf"
                if args.output_dir
                else COMPONENTS_DIR / e.board / "datasheets" / f"{e.reference}.pdf"
            )
            print(f"  {e.board}/{e.reference}  ({e.ref_type})  →  {dest}")
        return 0

    results: list[FetchResult] = []
    stats = {"downloaded": 0, "skipped": 0, "not_found": 0, "failed": 0}

    with tqdm(entries, unit="component", desc="Fetching datasheets") as pbar:
        for entry in pbar:
            pbar.set_postfix_str(f"{entry.board}/{entry.reference}")
            result = fetch_one(
                entry,
                use_octopart=use_octopart,
                octopart_token=octopart_token,
                output_dir=args.output_dir,
                force=args.force,
                dry_run=False,
                delay=args.delay,
            )
            results.append(result)
            stats[result.status] = stats.get(result.status, 0) + 1

    write_results(results, results_path)

    log.info(
        "Done. downloaded=%d  skipped=%d  not_found=%d  failed=%d",
        stats.get("downloaded", 0),
        stats.get("skipped", 0),
        stats.get("not_found", 0),
        stats.get("failed", 0),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
