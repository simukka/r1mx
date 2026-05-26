"""
server.py — MCP server exposing r1mx reverse-engineering tools.

Tools available to MCP clients (Claude Code, Claude Desktop, etc.):

  Datasheets
    search_datasheets(query, top_k=5)
        Semantic search across all indexed component datasheets.
    lookup_component(reference, board=None)
        Find a component by BOM reference designator (e.g. 'U7').
    ask_component(question)
        RAG Q&A over datasheets via Ollama/mistral:7b.
    list_datasheets()
        List all indexed PDFs with board and chunk count.

  Firmware (requires ghidra_decompile_all.py + index_firmware.py)
    search_firmware(query, top_k=10)
        Semantic search over decompiled PowerPC 405F6 / VxWorks 6.x functions.
    lookup_function(name_or_address)
        Find a function by hex address or name fragment.

  SWF GUI (requires index_swf_gui.py)
    search_gui(query, top_k=8)
        Semantic search over ActionScript 2 source + panels.xml.

Transport: stdio (compatible with Claude Code, Claude Desktop, etc.).

Usage:
    python -m toolkit.mcp                  # recommended
    python toolkit/mcp/server.py           # direct

.mcp.json entry:
    {
      "mcpServers": {
        "r1mx": {
          "command": "/path/to/r1mx/.venv/bin/python",
          "args": ["-m", "toolkit.mcp"],
          "cwd": "/path/to/r1mx"
        }
      }
    }
"""

from __future__ import annotations

import csv
import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from fastembed import TextEmbedding
from mcp.server.fastmcp import FastMCP

from toolkit.paths import REPO_ROOT

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)-5s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

BOM_CSV = REPO_ROOT / "bom_master.csv"

# Load .env
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

OLLAMA_HOST     = os.environ.get("OLLAMA_HOST",     "http://localhost:11434")
CHROMA_HOST     = os.environ.get("CHROMA_HOST",     "http://localhost:8000")
FASTEMBED_MODEL = os.environ.get("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
LLM_MODEL       = os.environ.get("OLLAMA_LLM_MODEL","mistral:7b")

DATASHEET_COLLECTION = os.environ.get("CHROMA_COLLECTION", "datasheets")
FIRMWARE_COLLECTION  = "firmware_functions"
GUI_COLLECTION       = "swf_gui"
NOTES_COLLECTION     = "re_notes"

# ── ChromaDB REST helpers (v2 API) ─────────────────────────────────────────────

CHROMA_API_BASE = f"{CHROMA_HOST}/api/v2/tenants/default_tenant/databases/default_database"

_collection_ids: dict[str, str] = {}


def _get_collection_id(name: str) -> str:
    if name not in _collection_ids:
        r = requests.get(f"{CHROMA_API_BASE}/collections/{name}", timeout=10)
        if r.status_code == 200:
            _collection_ids[name] = r.json()["id"]
        else:
            r = requests.post(
                f"{CHROMA_API_BASE}/collections",
                json={"name": name, "metadata": {"hnsw:space": "cosine"}},
                timeout=10,
            )
            r.raise_for_status()
            _collection_ids[name] = r.json()["id"]
    return _collection_ids[name]


def _chroma_query(collection: str, query_embedding: list[float], n_results: int) -> dict:
    cid = _get_collection_id(collection)
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


def _chroma_get(collection: str, where: dict, limit: int = 20) -> dict:
    cid = _get_collection_id(collection)
    r = requests.post(
        f"{CHROMA_API_BASE}/collections/{cid}/get",
        json={"where": where, "include": ["documents", "metadatas"], "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _chroma_list(collection: str, limit: int = 10000) -> dict:
    cid = _get_collection_id(collection)
    r = requests.post(
        f"{CHROMA_API_BASE}/collections/{cid}/get",
        json={"include": ["metadatas"], "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


# ── Embedding ──────────────────────────────────────────────────────────────────

_embed_model: Optional[TextEmbedding] = None


def _get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


def embed(text: str) -> list[float]:
    return next(_get_embed_model().embed([text])).tolist()


# ── BOM lookup ─────────────────────────────────────────────────────────────────

_bom_cache: Optional[list[dict]] = None


def _load_bom() -> list[dict]:
    global _bom_cache
    if _bom_cache is None:
        _bom_cache = []
        if BOM_CSV.exists():
            with BOM_CSV.open() as f:
                _bom_cache = list(csv.DictReader(f))
    return _bom_cache


def _find_component(reference: str, board: Optional[str] = None) -> list[dict]:
    ref = reference.upper().strip()
    return [
        r for r in _load_bom()
        if r.get("reference", "").upper() == ref
        and (board is None or r.get("board", "").lower() == board.lower())
    ]


# ── LLM Q&A ───────────────────────────────────────────────────────────────────

def _ask_llm(question: str, context: str) -> str:
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


# ── Format helpers ─────────────────────────────────────────────────────────────

def _fmt_datasheet_results(results: dict, query: str) -> str:
    docs      = results.get("documents", [[]])[0]
    metas     = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    if not docs:
        return f"No results found for: {query}"
    lines = [f"Search results for: {query!r}\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        score   = 1 - dist
        excerpt = doc[:400].replace("\n", " ").strip()
        lines.append(
            f"[{i}] {meta.get('part_number','?')} ({meta.get('board','?')}) — "
            f"{meta.get('pdf_filename','?')} chunk {meta.get('chunk_index','?')}  "
            f"[similarity: {score:.3f}]\n    {excerpt}...\n"
        )
    return "\n".join(lines)


def _fmt_firmware_results(results: dict, query: str) -> str:
    docs      = results.get("documents", [[]])[0]
    metas     = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    if not docs:
        return f"No firmware functions found for: {query!r}"
    lines = [f"Firmware search results for: {query!r}\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        score      = 1 - dist
        chunk_idx  = meta.get("chunk_index", 0)
        total      = meta.get("total_chunks", 1)
        chunk_info = f"  chunk {chunk_idx + 1}/{total}" if total > 1 else ""
        lines.append(
            f"[{i}] {meta.get('function_name','?')} @ {meta.get('address','?')}  "
            f"xrefs={meta.get('xref_count','?')}  size={meta.get('size_bytes','?')}B"
            f"{chunk_info}  [similarity: {score:.3f}]\n{doc[:800]}\n"
        )
    return "\n".join(lines)


def _fmt_gui_results(results: dict, query: str) -> str:
    docs      = results.get("documents", [[]])[0]
    metas     = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    if not docs:
        return f"No GUI source found for: {query!r}"
    lines = [f"GUI source search results for: {query!r}\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        score      = 1 - dist
        chunk_idx  = meta.get("chunk_index", 0)
        total      = meta.get("total_chunks", 1)
        chunk_info = f"  chunk {chunk_idx + 1}/{total}" if total > 1 else ""
        lines.append(
            f"[{i}] {meta.get('class_name','?')}  [{meta.get('swf_source','?')}]"
            f"{chunk_info}  [similarity: {score:.3f}]\n{doc[:800]}\n"
        )
    return "\n".join(lines)


# ── FastMCP server ─────────────────────────────────────────────────────────────

mcp = FastMCP("r1mx")


# — Datasheets —

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
        return _fmt_datasheet_results(
            _chroma_query(DATASHEET_COLLECTION, embed(query), top_k), query
        )
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
    rows = _find_component(reference, board)
    if not rows:
        return f"Component {reference!r} not found in BOM."
    query = " ".join({r["reference"] for r in rows})
    lines = [
        f"BOM entries for {reference}:",
        *[f"  board={r['board']} part={r['reference']} source={r.get('source_image','?')}" for r in rows],
        "",
    ]
    try:
        lines.append(_fmt_datasheet_results(
            _chroma_query(DATASHEET_COLLECTION, embed(query), 5), query
        ))
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
        results = _chroma_query(DATASHEET_COLLECTION, embed(question), top_k)
        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return "No relevant datasheet chunks found for this question."
        context = "\n\n---\n\n".join(
            f"[Source: {m.get('pdf_filename','?')} / {m.get('part_number','?')}]\n{d}"
            for d, m in zip(docs, metas)
        )
        answer  = _ask_llm(question, context)
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
        metas = _chroma_list(DATASHEET_COLLECTION).get("metadatas") or []
        if not metas:
            return "No datasheets indexed yet. Run: python firmware/scripts/index_firmware.py"
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


# — Firmware —

@mcp.tool()
def search_firmware(query: str, top_k: int = 10) -> str:
    """
    Semantic search over all decompiled firmware functions (PowerPC 405F6, VxWorks 6.x).
    Returns matching C pseudocode excerpts with function addresses and cross-reference counts.
    Use for questions like 'where is the histogram FIFO read', 'find UART write functions',
    'what accesses MMIO at 0xE0001000', or 'show me task priority assignment code'.
    Requires ghidra_decompile_all.py + index_firmware.py to have been run first.
    """
    if not query.strip():
        return "Error: query is required"
    try:
        return _fmt_firmware_results(
            _chroma_query(FIRMWARE_COLLECTION, embed(query), top_k), query
        )
    except Exception as e:
        return f"Firmware search error: {e}"


@mcp.tool()
def lookup_function(name_or_address: str) -> str:
    """
    Find a decompiled firmware function by exact hex address (e.g. '0x00d94000') or
    by name fragment (e.g. 'uart', 'GPDB_Get', 'xmlUtil'). Returns full C pseudocode.
    Address lookup is exact; name lookup is semantic (finds the closest match).
    Requires ghidra_decompile_all.py + index_firmware.py to have been run first.
    """
    s = name_or_address.strip()
    if not s:
        return "Error: name or address is required"
    try:
        if re.match(r'^0[xX][0-9a-fA-F]+$', s):
            normalized = f"0x{int(s, 16):08x}"
            data  = _chroma_get(FIRMWARE_COLLECTION, {"address": {"$eq": normalized}}, limit=10)
            docs  = data.get("documents") or []
            metas = data.get("metadatas") or []
            if not docs:
                return f"No function found at address {normalized}"
            lines = [f"Function at {normalized}:\n"]
            for doc, meta in zip(docs, metas):
                lines.append(
                    f"name={meta.get('function_name','?')}  "
                    f"size={meta.get('size_bytes','?')}B  xrefs={meta.get('xref_count','?')}\n"
                )
                lines.append(doc)
            return "\n".join(lines)
        else:
            return _fmt_firmware_results(
                _chroma_query(FIRMWARE_COLLECTION, embed(s), 5), s
            )
    except Exception as e:
        return f"Lookup error: {e}"


# — SWF GUI —

@mcp.tool()
def search_gui(query: str, top_k: int = 8) -> str:
    """
    Semantic search over the RED ONE MX SWF GUI source (ActionScript 2 + panels.xml).
    Returns matching source excerpts with class name and SWF origin.
    Use for questions like 'how does the menu panel render', 'where is the histogram
    display updated', 'how does OsdXml parse panels', 'what sends XML commands to camera',
    or 'find the record button handler'.
    Requires index_swf_gui.py to have been run first.
    """
    if not query.strip():
        return "Error: query is required"
    try:
        return _fmt_gui_results(
            _chroma_query(GUI_COLLECTION, embed(query), top_k), query
        )
    except Exception as e:
        return f"GUI search error: {e}"


# — RE Notes —

@mcp.tool()
def search_notes(query: str, top_k: int = 8) -> str:
    """
    Semantic search over reverse-engineering notes for the RED ONE MX firmware
    (build_32). Covers: re_reference.md (architecture, MMIO map, boot sequence,
    QEMU patches, calling convention), build32_subsystem_map.md, debug_interfaces.md,
    qemu_howto.md, and other build_32 markdown notes.
    Use for questions like 'what is the SDA base address', 'how do QEMU patches work',
    'what are the VxWorks task priorities', or 'how is the firmware package encrypted'.
    Requires index_notes.py to have been run first.
    """
    if not query.strip():
        return "Error: query is required"
    try:
        results = _chroma_query(NOTES_COLLECTION, embed(query), top_k)
        docs      = results.get("documents", [[]])[0]
        metas     = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        if not docs:
            return f"No notes found for: {query!r}"
        lines = [f"RE notes search results for: {query!r}\n"]
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
            score     = 1 - dist
            filename  = meta.get("filename", "?")
            section   = meta.get("section_title", "")
            location  = f"{filename} § {section}" if section else filename
            chunk_idx = meta.get("chunk_index", 0)
            total     = meta.get("total_chunks", 1)
            chunk_info = f"  chunk {chunk_idx + 1}/{total}" if total > 1 else ""
            lines.append(f"[{i}] {location}{chunk_info}  [similarity: {score:.3f}]\n{doc[:800]}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"Notes search error: {e}"


def run() -> None:
    """Start the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
