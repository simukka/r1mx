"""
index_swf_gui.py — Chunk, embed, and index the SWF GUI ActionScript source into ChromaDB.

Reads all .as files from swf_gui_1_as/ and swf_gui_2_as/ plus panels.xml, and upserts
them into the ChromaDB "swf_gui" collection. Tiny stub files (< 80 chars) are skipped.
When the same class appears in both SWFs, the larger version wins.

Usage:
    python3 firmware/scripts/index_swf_gui.py             # index new files
    python3 firmware/scripts/index_swf_gui.py --reindex   # force re-index all
    python3 firmware/scripts/index_swf_gui.py --status    # show collection stats

Environment variables (also loaded from repo root .env):
    CHROMA_HOST       ChromaDB base URL (default: http://localhost:8000)
    FASTEMBED_MODEL   Model name (default: BAAI/bge-small-en-v1.5)
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

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
ASSETS_DIR  = REPO_ROOT / "reverse" / "build_32" / "assets"
SWF_DIRS    = [ASSETS_DIR / "swf_gui_1_as", ASSETS_DIR / "swf_gui_2_as"]
PANELS_XML  = ASSETS_DIR / "panels.xml"

_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

CHROMA_HOST     = os.environ.get("CHROMA_HOST", "http://localhost:8000")
FASTEMBED_MODEL = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
COLLECTION_NAME = "swf_gui"

CHUNK_TOKENS  = 512
CHUNK_OVERLAP = 50
BATCH_SIZE    = 64
MIN_FILE_BYTES = 80  # skip one-liner stubs like Object.registerClass(...)

_embed_model = None

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
    chunks, start = [], 0
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
    return [v.tolist() for v in get_embed_model().embed(texts)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def class_name_from_path(path: Path, swf_root: Path) -> str:
    """Derive a human-readable class/module name from the file path.

    __Packages/GUI/OSD_Components/OsdXml.as → GUI.OSD_Components.OsdXml
    %3Cdefault package%3E/MenuPanelMC.as   → MenuPanelMC
    DefineSprite_100_.../frame_1/DoAction  → DefineSprite_100_.../frame_1
    """
    rel = path.relative_to(swf_root / "scripts")
    parts = [unquote(p) for p in rel.parts]

    if parts[0] == "__Packages":
        # __Packages/GUI/OSD_Components/OsdXml.as → GUI.OSD_Components.OsdXml
        return ".".join(parts[1:]).removesuffix(".as")
    if parts[0] == "<default package>":
        return path.stem
    # DefineSprite frame scripts — join with /
    return "/".join(parts).removesuffix(".as")


def collect_files() -> list[tuple[Path, str, str]]:
    """Return [(path, class_name, swf_source), ...], deduplicating by class_name.

    When the same class appears in both SWFs, keep the larger file (gui_2 typically
    has full implementations while gui_1 has stubs).
    """
    seen: dict[str, tuple[Path, str]] = {}  # class_name → (path, swf_source)

    for swf_dir in SWF_DIRS:
        if not swf_dir.is_dir():
            continue
        swf_source = swf_dir.name  # "swf_gui_1_as" or "swf_gui_2_as"
        scripts_dir = swf_dir / "scripts"
        for path in sorted(scripts_dir.rglob("*.as")):
            if not path.is_file():
                continue
            if path.stat().st_size < MIN_FILE_BYTES:
                continue
            cn = class_name_from_path(path, swf_dir)
            if cn in seen:
                existing_path, _ = seen[cn]
                if path.stat().st_size > existing_path.stat().st_size:
                    seen[cn] = (path, swf_source)
            else:
                seen[cn] = (path, swf_source)

    result = [(path, cn, src) for cn, (path, src) in seen.items()]

    # Add panels.xml as a single document
    if PANELS_XML.exists():
        result.append((PANELS_XML, "panels.xml", "panels"))

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
    class_name: str,
    swf_source: str,
    collection: chromadb.Collection,
    reindex: bool = False,
) -> int:
    file_hash = sha256(path)

    if not reindex and already_indexed(collection, file_hash):
        log.debug("Already indexed: %s", class_name)
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

    chunks = chunk_text(text)
    if not chunks:
        return 0

    file_type = "xml" if path.suffix == ".xml" else "actionscript"
    total_chunks = len(chunks)
    total_added = 0

    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        embeddings = embed_texts(batch)
        ids = [f"{file_hash}_{batch_start + i}" for i in range(len(batch))]
        metadatas = [
            {
                "class_name":   class_name,
                "swf_source":   swf_source,
                "file_type":    file_type,
                "file_hash":    file_hash,
                "chunk_index":  batch_start + i,
                "total_chunks": total_chunks,
            }
            for i in range(len(batch))
        ]
        try:
            collection.upsert(ids=ids, embeddings=embeddings, documents=batch, metadatas=metadatas)
            total_added += len(batch)
        except Exception as e:
            log.error("ChromaDB upsert failed for %s batch %d: %s", class_name, batch_start, e)

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
    ap = argparse.ArgumentParser(description="Index SWF GUI ActionScript into ChromaDB")
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
            classes = sorted({m.get("class_name", "?") for m in (results.get("metadatas") or [])})
            log.info("%d unique classes/files. Sample: %s", len(classes), ", ".join(classes[:15]))
        except Exception:
            pass
        return

    files = collect_files()
    if not files:
        log.warning("No .as files found under %s", ASSETS_DIR)
        return

    log.info("Found %d ActionScript files/documents to index", len(files))

    total_chunks = 0
    skipped = 0
    for path, class_name, swf_source in files:
        added = index_file(path, class_name, swf_source, collection, reindex=args.reindex)
        if added:
            total_chunks += added
            log.debug("  [+] %s (%s)  %d chunks", class_name, swf_source, added)
        else:
            skipped += 1

    log.info(
        "Done. %d files skipped (already indexed), %d new chunks added. "
        "Collection now has %d total chunks.",
        skipped, total_chunks, collection.count(),
    )


if __name__ == "__main__":
    main()
