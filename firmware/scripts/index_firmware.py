"""
index_firmware.py — Chunk, embed, and index decompiled firmware functions into ChromaDB.

Reads all .c files from firmware/reverse/build_32/src/all_functions/ (produced by
ghidra_decompile_all.py), embeds each function with fastembed, and upserts into the
ChromaDB "firmware_functions" collection.

Runs incrementally: functions already indexed by file SHA256 are skipped unless
--reindex is passed.

Usage:
    python3 firmware/scripts/index_firmware.py             # index new files
    python3 firmware/scripts/index_firmware.py --reindex   # force re-index all
    python3 firmware/scripts/index_firmware.py --status    # show collection stats
    python3 firmware/scripts/index_firmware.py --src-dir /path/to/all_functions

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
from typing import Optional
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

# Paths
_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT   = _SCRIPT_DIR.parent
DEFAULT_SRC = REPO_ROOT / "reverse" / "build_32" / "src" / "all_functions"

# Load .env from repo root
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

CHROMA_HOST       = os.environ.get("CHROMA_HOST", "http://localhost:8000")
FASTEMBED_MODEL   = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
COLLECTION_NAME   = "firmware_functions"

CHUNK_TOKENS  = 512
CHUNK_OVERLAP = 50
BATCH_SIZE    = 64

_ADDR_NAME_RE = re.compile(r'^(0x[0-9a-f]{8})_(.*)$')
_META_RE      = re.compile(r'\*\s*address=(0x[0-9a-f]+)\s+name=(\S+)\s+size=(\d+)\s+xrefs=(\d+)')

_embed_model: Optional[TextEmbedding] = None

def get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        log.info("Loading embedding model %s ...", FASTEMBED_MODEL)
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


def chunk_text(text: str, chunk_size: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> list[str]:
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


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embed_model()
    return [vec.tolist() for vec in model.embed(texts)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def get_collection(client: chromadb.HttpClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def already_indexed(collection: chromadb.Collection, file_hash: str) -> bool:
    results = collection.get(where={"file_hash": file_hash}, limit=1, include=[])
    return bool(results["ids"])


def parse_file_metadata(path: Path) -> tuple[str, str, int, int]:
    """Return (address, function_name, size_bytes, xref_count) from filename + header."""
    stem = path.stem
    m = _ADDR_NAME_RE.match(stem)
    address = m.group(1) if m else "0x00000000"
    function_name = m.group(2) if m else stem

    size_bytes = 0
    xrefs = 0
    try:
        header = path.read_text(errors="replace")[:500]
        hm = _META_RE.search(header)
        if hm:
            address      = hm.group(1)
            function_name = hm.group(2)
            size_bytes   = int(hm.group(3))
            xrefs        = int(hm.group(4))
    except Exception:
        pass

    return address, function_name, size_bytes, xrefs


def index_function(
    c_path: Path,
    collection: chromadb.Collection,
    reindex: bool = False,
) -> int:
    """Index a single decompiled .c file. Returns number of chunks added (0 if skipped)."""
    file_hash = sha256(c_path)

    if not reindex and already_indexed(collection, file_hash):
        log.debug("Already indexed: %s", c_path.name)
        return 0

    if reindex:
        try:
            old = collection.get(where={"file_hash": file_hash}, include=[])
            if old["ids"]:
                collection.delete(ids=old["ids"])
        except Exception:
            pass

    text = c_path.read_text(errors="replace")
    if not text.strip():
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    address, function_name, size_bytes, xrefs = parse_file_metadata(c_path)
    total_chunks = len(chunks)

    total_added = 0
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        embeddings = embed_texts(batch)

        ids = [f"{file_hash}_{batch_start + i}" for i in range(len(batch))]
        metadatas = [
            {
                "address":       address,
                "function_name": function_name,
                "size_bytes":    size_bytes,
                "xref_count":    xrefs,
                "file_hash":     file_hash,
                "chunk_index":   batch_start + i,
                "total_chunks":  total_chunks,
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
            log.error("ChromaDB upsert failed for %s batch %d: %s", c_path.name, batch_start, e)

    return total_added


def wait_for_chroma(max_wait: int = 60) -> bool:
    url = f"{CHROMA_HOST}/api/v2/heartbeat"
    for attempt in range(max_wait // 5):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                log.info("ChromaDB is ready")
                return True
        except Exception:
            pass
        log.info("Waiting for ChromaDB... (%ds)", (attempt + 1) * 5)
        time.sleep(5)
    log.error("ChromaDB not reachable at %s after %ds", CHROMA_HOST, max_wait)
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Index decompiled firmware functions into ChromaDB")
    ap.add_argument("--src-dir", default=str(DEFAULT_SRC), help="Directory of .c files")
    ap.add_argument("--reindex", action="store_true", help="Force re-index all files")
    ap.add_argument("--status", action="store_true", help="Show collection stats and exit")
    args = ap.parse_args()

    src_dir = Path(args.src_dir)
    if not src_dir.is_dir() and not args.status:
        log.error("Source directory not found: %s", src_dir)
        log.error("Run ghidra_decompile_all.py first to generate .c files.")
        sys.exit(1)

    if not wait_for_chroma():
        sys.exit(1)

    try:
        parsed = urlparse(CHROMA_HOST)
        client = chromadb.HttpClient(
            host=parsed.hostname or "localhost",
            port=parsed.port or 8000,
        )
        collection = get_collection(client)
    except Exception as e:
        log.error("Cannot connect to ChromaDB at %s: %s", CHROMA_HOST, e)
        sys.exit(1)

    if args.status:
        count = collection.count()
        log.info("Collection '%s': %d chunks indexed", COLLECTION_NAME, count)
        try:
            results = collection.get(include=["metadatas"], limit=10000)
            names = [m.get("function_name", "?") for m in (results.get("metadatas") or [])]
            log.info("Sample functions: %s", ", ".join(names[:20]))
        except Exception:
            pass
        return

    c_files = sorted(src_dir.glob("*.c"))
    if not c_files:
        log.warning("No .c files found in %s", src_dir)
        log.warning("Run ghidra_decompile_all.py first.")
        return

    log.info("Found %d .c files in %s", len(c_files), src_dir)

    total_chunks = 0
    skipped = 0
    for i, c_path in enumerate(c_files):
        added = index_function(c_path, collection, reindex=args.reindex)
        if added:
            total_chunks += added
            if (i + 1) % 500 == 0:
                log.info("[%d/%d] %d new chunks so far", i + 1, len(c_files), total_chunks)
        else:
            skipped += 1

    log.info(
        "Done. %d files skipped (already indexed), %d new chunks added. "
        "Collection now has %d total chunks.",
        skipped, total_chunks, collection.count(),
    )


if __name__ == "__main__":
    main()
