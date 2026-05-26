"""
index_notes.py — Chunk, embed, and index reverse-engineering markdown notes into ChromaDB.

Reads all .md files from firmware/reverse/build_32/ (or a custom directory),
splits by markdown heading section, and upserts into the ChromaDB "re_notes" collection.

Usage:
    python3 firmware/scripts/index_notes.py             # index new/changed files
    python3 firmware/scripts/index_notes.py --reindex   # force re-index all
    python3 firmware/scripts/index_notes.py --status    # show collection stats
    python3 firmware/scripts/index_notes.py --src-dir /path/to/dir

Environment variables (also loaded from repo root .env):
    CHROMA_HOST       ChromaDB base URL (default: http://localhost:8000)
    FASTEMBED_MODEL   Model name (default: BAAI/bge-small-en-v1.5)
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
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

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT   = _SCRIPT_DIR.parent
DEFAULT_SRC = REPO_ROOT / "reverse" / "build_32"

_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

CHROMA_HOST     = os.environ.get("CHROMA_HOST",     "http://localhost:8000")
FASTEMBED_MODEL = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
COLLECTION_NAME = "re_notes"

CHUNK_TOKENS  = 512
CHUNK_OVERLAP = 50
BATCH_SIZE    = 64

_HEADING_RE = re.compile(r'^#{1,6} ', re.MULTILINE)

_embed_model = None


def get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        log.info("Loading embedding model %s ...", FASTEMBED_MODEL)
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return [v.tolist() for v in get_embed_model().embed(texts)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def split_by_heading(text: str) -> list[tuple[str, str]]:
    """Split markdown into (section_title, section_text) pairs.

    Each section starts at a heading and runs until the next heading of the
    same or higher level. The heading line is included in the section text so
    embeddings carry its label.
    """
    # Find all heading positions
    boundaries = [m.start() for m in _HEADING_RE.finditer(text)] + [len(text)]
    if not boundaries[:-1]:
        # No headings — treat entire file as one section
        return [("", text)]

    sections = []
    for i, start in enumerate(boundaries[:-1]):
        end = boundaries[i + 1]
        section = text[start:end].strip()
        if not section:
            continue
        # Extract the heading line as title
        first_line = section.splitlines()[0]
        title = first_line.lstrip("#").strip()
        sections.append((title, section))

    # Capture any preamble before the first heading
    preamble = text[: boundaries[0]].strip()
    if preamble:
        sections.insert(0, ("(preamble)", preamble))

    return sections


def chunk_tokens(text: str, chunk_size: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping token-count chunks."""
    tokens = text.split()
    if not tokens:
        return []
    chunks, start = [], 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(" ".join(tokens[start:end]))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


def make_chunks(text: str, filename: str) -> list[tuple[str, str]]:
    """Return [(section_title, chunk_text), ...] for a markdown file."""
    result = []
    for title, section_text in split_by_heading(text):
        if len(section_text.split()) <= CHUNK_TOKENS:
            result.append((title, section_text))
        else:
            for chunk in chunk_tokens(section_text):
                result.append((title, chunk))
    return result


def get_collection(client: chromadb.HttpClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def already_indexed(collection: chromadb.Collection, file_hash: str) -> bool:
    results = collection.get(where={"file_hash": file_hash}, limit=1, include=[])
    return bool(results["ids"])


def index_file(
    path: Path,
    collection: chromadb.Collection,
    reindex: bool = False,
) -> int:
    file_hash = sha256(path)

    if not reindex and already_indexed(collection, file_hash):
        log.debug("Already indexed: %s", path.name)
        return 0

    if reindex:
        try:
            old = collection.get(where={"file_hash": file_hash}, include=[])
            if old["ids"]:
                collection.delete(ids=old["ids"])
        except Exception:
            pass

    text = path.read_text(errors="replace")
    if not text.strip():
        return 0

    chunks = make_chunks(text, path.name)
    if not chunks:
        return 0

    total_added = 0
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        texts      = [c[1] for c in batch]
        embeddings = embed_texts(texts)

        ids = [f"{file_hash}_{batch_start + i}" for i in range(len(batch))]
        metadatas = [
            {
                "filename":      path.name,
                "section_title": batch[i][0],
                "file_hash":     file_hash,
                "chunk_index":   batch_start + i,
                "total_chunks":  len(chunks),
            }
            for i in range(len(batch))
        ]

        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            total_added += len(batch)
        except Exception as e:
            log.error("ChromaDB upsert failed for %s batch %d: %s", path.name, batch_start, e)

    return total_added


def wait_for_chroma(max_wait: int = 60) -> bool:
    url = f"{CHROMA_HOST}/api/v2/heartbeat"
    for attempt in range(max_wait // 5):
        try:
            if requests.get(url, timeout=5).status_code == 200:
                log.info("ChromaDB is ready")
                return True
        except Exception:
            pass
        log.info("Waiting for ChromaDB... (%ds)", (attempt + 1) * 5)
        time.sleep(5)
    log.error("ChromaDB not reachable at %s after %ds", CHROMA_HOST, max_wait)
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Index RE markdown notes into ChromaDB")
    ap.add_argument("--src-dir", default=str(DEFAULT_SRC), help="Directory to scan for .md files")
    ap.add_argument("--reindex", action="store_true", help="Force re-index all files")
    ap.add_argument("--status",  action="store_true", help="Show collection stats and exit")
    args = ap.parse_args()

    if not wait_for_chroma():
        sys.exit(1)

    try:
        parsed = urlparse(CHROMA_HOST)
        client = chromadb.HttpClient(host=parsed.hostname or "localhost", port=parsed.port or 8000)
        collection = get_collection(client)
    except Exception as e:
        log.error("Cannot connect to ChromaDB at %s: %s", CHROMA_HOST, e)
        sys.exit(1)

    if args.status:
        count = collection.count()
        log.info("Collection '%s': %d chunks indexed", COLLECTION_NAME, count)
        try:
            results = collection.get(include=["metadatas"], limit=10000)
            files = sorted({m.get("filename", "?") for m in (results.get("metadatas") or [])})
            log.info("Files: %s", ", ".join(files))
        except Exception:
            pass
        return

    src_dir = Path(args.src_dir)
    md_files = sorted(src_dir.rglob("*.md"))
    if not md_files:
        log.warning("No .md files found under %s", src_dir)
        return

    log.info("Found %d markdown files", len(md_files))

    total_chunks = 0
    skipped = 0
    for path in md_files:
        added = index_file(path, collection, reindex=args.reindex)
        if added:
            total_chunks += added
            log.info("  [+] %s  %d chunks", path.name, added)
        else:
            skipped += 1
            log.debug("  [=] %s  (already indexed)", path.name)

    log.info(
        "Done. %d files skipped (already indexed), %d new chunks added. "
        "Collection now has %d total chunks.",
        skipped, total_chunks, collection.count(),
    )


if __name__ == "__main__":
    main()
