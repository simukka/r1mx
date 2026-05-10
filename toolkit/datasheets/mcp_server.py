"""
mcp_server.py — MCP server for querying component datasheets.

Exposes 4 tools to MCP clients (Claude Desktop, Copilot CLI agents, etc.):

  search_datasheets(query, top_k=5)
      Semantic search across all indexed datasheet chunks.
      Returns matching text excerpts with source PDF and board info.

  lookup_component(reference, board=None)
      Given a component reference (e.g. "U7") and optional board name,
      finds the part number from bom_master.csv and searches its datasheet.

  ask_component(question)
      Full RAG: semantic search -> build context -> answer via mistral:7b.
      Best for natural-language questions like "What is the I2C address of PCA9698?"

  list_datasheets()
      List all indexed PDFs with board and chunk count.

Transport: stdio (compatible with Claude Desktop and Copilot CLI).

Usage (Claude Desktop config):
    {
      "mcpServers": {
        "r1mx-datasheets": {
          "command": "/path/to/r1mx/.venv/bin/python",
          "args": ["/path/to/r1mx/toolkit/datasheets/mcp_server.py"]
        }
      }
    }
"""

from __future__ import annotations

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import requests
from fastembed import TextEmbedding
from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)-5s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
BOM_CSV = REPO_ROOT / "bom_master.csv"

# Load .env
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "http://localhost:8000")
FASTEMBED_MODEL = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
LLM_MODEL = os.environ.get("OLLAMA_LLM_MODEL", "mistral:7b")
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "datasheets")

# ── ChromaDB REST helpers (v2 API) ────────────────────────────────────────────

CHROMA_API_BASE = f"{CHROMA_HOST}/api/v2/tenants/default_tenant/databases/default_database"

_collection_id: Optional[str] = None

def _get_collection_id() -> str:
    global _collection_id
    if _collection_id is None:
        r = requests.get(f"{CHROMA_API_BASE}/collections/{COLLECTION_NAME}", timeout=10)
        if r.status_code == 200:
            _collection_id = r.json()["id"]
        else:
            # Create it
            r = requests.post(
                f"{CHROMA_API_BASE}/collections",
                json={"name": COLLECTION_NAME, "metadata": {"hnsw:space": "cosine"}},
                timeout=10,
            )
            r.raise_for_status()
            _collection_id = r.json()["id"]
    return _collection_id


def _chroma_query(query_embedding: list[float], n_results: int = 5) -> dict:
    cid = _get_collection_id()
    r = requests.post(
        f"{CHROMA_API_BASE}/collections/{cid}/query",
        json={
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _chroma_list_chunks(limit: int = 10000) -> dict:
    cid = _get_collection_id()
    r = requests.post(
        f"{CHROMA_API_BASE}/collections/{cid}/get",
        json={"include": ["metadatas"], "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


# ── Embedding ────────────────────────────────────────────────────────────────

_embed_model: Optional[TextEmbedding] = None

def _get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


def embed(text: str) -> list[float]:
    return next(_get_embed_model().embed([text])).tolist()


# ── BOM lookup ───────────────────────────────────────────────────────────────

_bom_cache: Optional[list[dict]] = None

def load_bom() -> list[dict]:
    global _bom_cache
    if _bom_cache is None:
        _bom_cache = []
        if BOM_CSV.exists():
            with BOM_CSV.open() as f:
                _bom_cache = list(csv.DictReader(f))
    return _bom_cache


def find_component(reference: str, board: Optional[str] = None) -> list[dict]:
    ref = reference.upper().strip()
    return [
        r for r in load_bom()
        if r.get("reference", "").upper() == ref
        and (board is None or r.get("board", "").lower() == board.lower())
    ]


# ── LLM Q&A ──────────────────────────────────────────────────────────────────

def ask_llm(question: str, context: str) -> str:
    prompt = (
        "You are a hardware engineer helping to reverse-engineer a discontinued "
        "RED ONE MX digital cinema camera. Use the datasheet excerpts below to "
        "answer the question accurately and concisely.\n\n"
        f"DATASHEET EXCERPTS:\n{context}\n\n"
        f"QUESTION: {question}\n\nANSWER:"
    )
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=300,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"LLM error: {e}"


# ── Format helper ─────────────────────────────────────────────────────────────

def format_search_results(results: dict, query: str) -> str:
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    if not docs:
        return f"No results found for: {query}"
    lines = [f"Search results for: {query!r}\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        score = 1 - dist
        excerpt = doc[:400].replace("\n", " ").strip()
        lines.append(
            f"[{i}] {meta.get('part_number','?')} ({meta.get('board','?')}) — "
            f"{meta.get('pdf_filename','?')} chunk {meta.get('chunk_index','?')}  "
            f"[similarity: {score:.3f}]\n    {excerpt}...\n"
        )
    return "\n".join(lines)


# ── FastMCP server ────────────────────────────────────────────────────────────

mcp = FastMCP("r1mx-datasheets")


@mcp.tool()
def search_datasheets(query: str, top_k: int = 5) -> str:
    """
    Semantic search across all indexed component datasheets.
    Returns relevant text excerpts with source PDF and board info.
    Use for finding specific pin descriptions, register maps, or specifications.
    """
    if not query.strip():
        return "Error: query is required"
    try:
        vec = embed(query)
        results = _chroma_query(vec, n_results=top_k)
        return format_search_results(results, query)
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def lookup_component(reference: str, board: Optional[str] = None) -> str:
    """
    Given a component reference designator (e.g. 'U7', 'IC3') and optional board name,
    find its part number from the BOM and return relevant datasheet excerpts.
    Use when you know the reference designator but not the part number.
    """
    if not reference.strip():
        return "Error: reference is required"
    rows = find_component(reference, board)
    if not rows:
        return f"Component {reference!r} not found in BOM."
    query = " ".join({r["reference"] for r in rows})
    lines = [
        f"BOM entries for {reference}:",
        *[f"  board={r['board']} part={r['reference']} source={r.get('source_image','?')}" for r in rows],
        "",
    ]
    try:
        vec = embed(query)
        results = _chroma_query(vec, n_results=5)
        lines.append(format_search_results(results, query))
    except Exception as e:
        lines.append(f"Datasheet search error: {e}")
    return "\n".join(lines)


@mcp.tool()
def ask_component(question: str, top_k: int = 5) -> str:
    """
    Ask a natural-language question about a component and get an AI-generated answer
    based on indexed datasheets. Uses RAG: retrieves relevant chunks, then answers
    with mistral:7b. Best for questions like 'What is the I2C address of PCA9698?'
    or 'How do I configure the SiI3512 for AHCI mode?'
    """
    if not question.strip():
        return "Error: question is required"
    try:
        vec = embed(question)
        results = _chroma_query(vec, n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return "No relevant datasheet chunks found for this question."
        context = "\n\n---\n\n".join(
            f"[Source: {m.get('pdf_filename','?')} / {m.get('part_number','?')}]\n{d}"
            for d, m in zip(docs, metas)
        )
        answer = ask_llm(question, context)
        sources = sorted({m.get("pdf_filename", "?") for m in metas})
        return f"{answer}\n\nSources: {', '.join(sources)}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_datasheets() -> str:
    """
    List all component datasheets currently indexed, grouped by board.
    Shows the PDF filename and number of indexed chunks.
    """
    try:
        data = _chroma_list_chunks()
        metas = data.get("metadatas") or []
        if not metas:
            return "No datasheets indexed yet. Run: python -m toolkit.index_datasheets.py"
        index: dict[str, dict[str, int]] = {}
        for m in metas:
            b = m.get("board", "unknown")
            p = m.get("pdf_filename", "?")
            index.setdefault(b, {})
            index[b][p] = index[b].get(p, 0) + 1
        total = sum(sum(v.values()) for v in index.values())
        lines = [f"Indexed datasheets ({total} total chunks):\n"]
        for board in sorted(index):
            lines.append(f"  {board}:")
            for pdf, count in sorted(index[board].items()):
                lines.append(f"    {pdf}  ({count} chunks)")
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing datasheets: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
