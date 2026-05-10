"""
index.py — Chunk, embed, and index all datasheet PDFs into ChromaDB.

For each PDF in components/*/datasheets/*.pdf:
  1. Extract text with pdftotext (system binary).
  2. Split into overlapping 512-token chunks (whitespace-tokenised).
  3. Embed each chunk with fastembed (BAAI/bge-small-en-v1.5, runs in-process).
  4. Upsert into ChromaDB collection "datasheets" with metadata.

Runs incrementally: PDFs already indexed (by SHA256) are skipped.

Usage:
    python -m toolkit.index.py                    # index everything
    python -m toolkit.index.py --board cpu_io_board
    python -m toolkit.index.py --reindex          # force re-index all
    python -m toolkit.index.py --status           # show index stats
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import chromadb
import requests
from fastembed import TextEmbedding

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPONENTS_DIR = REPO_ROOT / "components"

# Service endpoints — override via env or .env file
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

CHROMA_HOST = os.environ.get("CHROMA_HOST", "http://localhost:8000")
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "datasheets")
FASTEMBED_MODEL = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")

CHUNK_TOKENS = 512
CHUNK_OVERLAP = 50
BATCH_SIZE = 64  # fastembed handles large batches efficiently

# Lazy-loaded embedding model
_embed_model: TextEmbedding | None = None

def get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        log.info("Loading embedding model %s ...", FASTEMBED_MODEL)
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


# ── PDF text extraction ──────────────────────────────────────────────────────

def pdf_to_text(pdf_path: Path) -> str:
    """Extract text from a PDF using system pdftotext. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return result.stdout
        log.warning("pdftotext failed for %s: %s", pdf_path.name, result.stderr[:200])
    except FileNotFoundError:
        log.error("pdftotext not found — install poppler-utils: sudo apt install poppler-utils")
    except subprocess.TimeoutExpired:
        log.warning("pdftotext timed out for %s", pdf_path.name)
    return ""


# ── Chunking ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by whitespace-token count."""
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(" ".join(tokens[start:end]))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


# ── Embedding ────────────────────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts in-process using fastembed (BAAI/bge-small-en-v1.5)."""
    if not texts:
        return []
    model = get_embed_model()
    return [vec.tolist() for vec in model.embed(texts)]


# ── ChromaDB helpers ─────────────────────────────────────────────────────────

def get_collection(client: chromadb.HttpClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def already_indexed(collection: chromadb.Collection, file_hash: str) -> bool:
    """Check if any chunk from this PDF hash is already in the collection."""
    results = collection.get(
        where={"file_hash": file_hash},
        limit=1,
        include=[],
    )
    return bool(results["ids"])


def index_pdf(
    pdf_path: Path,
    board: str,
    collection: chromadb.Collection,
    reindex: bool = False,
) -> int:
    """
    Index a single PDF. Returns number of chunks added (0 if skipped).
    """
    file_hash = sha256(pdf_path)

    if not reindex and already_indexed(collection, file_hash):
        log.debug("Already indexed: %s", pdf_path.name)
        return 0

    # If re-indexing, remove old chunks for this file first
    if reindex:
        try:
            old = collection.get(where={"file_hash": file_hash}, include=[])
            if old["ids"]:
                collection.delete(ids=old["ids"])
                log.debug("Removed %d old chunks for %s", len(old["ids"]), pdf_path.name)
        except Exception:
            pass

    text = pdf_to_text(pdf_path)
    if not text.strip():
        log.warning("No text extracted from %s", pdf_path.name)
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    part_number = pdf_path.stem  # filename without extension = part number

    log.info("Indexing %s (%s) — %d chunks", pdf_path.name, board, len(chunks))

    # Process in batches
    total_added = 0
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        embeddings = embed_texts(batch)

        ids = [
            f"{file_hash}_{batch_start + i}"
            for i in range(len(batch))
        ]
        metadatas = [
            {
                "board": board,
                "part_number": part_number,
                "pdf_filename": pdf_path.name,
                "chunk_index": batch_start + i,
                "total_chunks": len(chunks),
                "file_hash": file_hash,
            }
            for i in range(len(batch))
        ]

        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=batch,
                metadatas=metadatas,
            )
            total_added += len(batch)
        except Exception as e:
            log.error("ChromaDB upsert failed for %s batch %d: %s", pdf_path.name, batch_start, e)

    return total_added


# ── Main ─────────────────────────────────────────────────────────────────────

def find_pdfs(board_filter: str | None) -> list[tuple[Path, str]]:
    """Return [(pdf_path, board_name), ...] for all datasheets."""
    pdfs = []
    if board_filter:
        search_dirs = [COMPONENTS_DIR / board_filter]
    else:
        search_dirs = list(COMPONENTS_DIR.iterdir())

    for board_dir in sorted(search_dirs):
        if not board_dir.is_dir():
            continue
        board = board_dir.name
        ds_dir = board_dir / "datasheets"
        if not ds_dir.is_dir():
            continue
        for pdf in sorted(ds_dir.glob("*.pdf")):
            pdfs.append((pdf, board))
    return pdfs


def wait_for_services(max_wait: int = 60) -> bool:
    """Wait for chromadb to be reachable."""
    for service, url in [("chromadb", f"{CHROMA_HOST}/api/v2/heartbeat")]:
        for attempt in range(max_wait // 5):
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    log.info("%s is ready", service)
                    break
            except Exception:
                pass
            log.info("Waiting for %s... (%ds)", service, (attempt + 1) * 5)
            time.sleep(5)
        else:
            log.error("%s not reachable at %s after %ds", service, url, max_wait)
            return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Index datasheet PDFs into ChromaDB")
    ap.add_argument("--board", help="Only index datasheets for this board")
    ap.add_argument("--reindex", action="store_true", help="Force re-index all PDFs")
    ap.add_argument("--status", action="store_true", help="Show index statistics and exit")
    args = ap.parse_args()

    if not wait_for_services():
        sys.exit(1)

    try:
        # Parse host/port from CHROMA_HOST env var
        from urllib.parse import urlparse
        _parsed = urlparse(CHROMA_HOST)
        _chroma_host = _parsed.hostname or "localhost"
        _chroma_port = _parsed.port or 8000
        client = chromadb.HttpClient(host=_chroma_host, port=_chroma_port)
        collection = get_collection(client)
    except Exception as e:
        log.error("Cannot connect to ChromaDB at %s: %s", CHROMA_HOST, e)
        sys.exit(1)

    if args.status:
        count = collection.count()
        log.info("Collection '%s': %d chunks indexed", COLLECTION_NAME, count)
        # Show per-board breakdown
        try:
            boards = set()
            results = collection.get(include=["metadatas"], limit=10000)
            for m in results.get("metadatas") or []:
                boards.add(m.get("board", "?"))
            log.info("Boards: %s", ", ".join(sorted(boards)))
        except Exception:
            pass
        return

    pdfs = find_pdfs(args.board)
    if not pdfs:
        log.warning("No PDFs found under %s", COMPONENTS_DIR)
        return

    log.info("Found %d PDFs to process", len(pdfs))

    total_chunks = 0
    skipped = 0
    for pdf_path, board in pdfs:
        added = index_pdf(pdf_path, board, collection, reindex=args.reindex)
        if added:
            total_chunks += added
        else:
            skipped += 1

    log.info(
        "Done. %d PDFs skipped (already indexed), %d new chunks added. "
        "Collection now has %d total chunks.",
        skipped, total_chunks, collection.count(),
    )


if __name__ == "__main__":
    main()
