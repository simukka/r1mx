#!/usr/bin/env python3
"""
datasheet_mcp_server.py — MCP server for querying component datasheets.

Exposes 4 tools to MCP clients (Claude Desktop, Copilot CLI agents, etc.):

  search_datasheets(query, top_k=5)
      Semantic search across all indexed datasheet chunks.
      Returns matching text excerpts with source metadata.

  lookup_component(reference, board=None)
      Given a component reference (e.g. "U7") and optional board name,
      finds the part number from bom_master.csv and searches its datasheet.

  ask_component(question)
      Full RAG: semantic search → build context → answer via mistral:7b.
      Best for natural-language questions like "What is the I2C address of PCA9698?"

  list_datasheets()
      List all indexed PDFs with board and chunk count.

Transport: stdio (compatible with Claude Desktop and Copilot CLI).

Usage (Claude Desktop config):
    {
      "mcpServers": {
        "r1mx-datasheets": {
          "command": "/path/to/.venv/bin/python",
          "args": ["/path/to/r1mx/scripts/datasheet_mcp_server.py"]
        }
      }
    }

Usage (direct test):
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_datasheets","arguments":{}}}' \\
      | python scripts/datasheet_mcp_server.py
"""

import csv
import logging
import os
import sys
from pathlib import Path

import requests
from fastembed import TextEmbedding

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)-5s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
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

# ── ChromaDB HTTP helpers (raw REST — avoids SDK version conflicts) ───────────

CHROMA_API_BASE = f"{CHROMA_HOST}/api/v2/tenants/default_tenant/databases/default_database"

# ── ChromaDB HTTP helpers (raw REST — avoids SDK version conflicts) ───────────

def _ensure_collection() -> str:
    """Get or create collection, return its UUID."""
    r = requests.get(f"{CHROMA_API_BASE}/collections/{COLLECTION_NAME}", timeout=10)
    if r.status_code == 200:
        return r.json()["id"]
    # Create it
    r = requests.post(
        f"{CHROMA_API_BASE}/collections",
        json={"name": COLLECTION_NAME, "metadata": {"hnsw:space": "cosine"}},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["id"]


_collection_id: str | None = None

def _get_collection_id() -> str:
    global _collection_id
    if _collection_id is None:
        _collection_id = _ensure_collection()
    return _collection_id


def _chroma_query(query_embedding: list[float], n_results: int = 5) -> dict:
    """Query ChromaDB REST API directly."""
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

_embed_model: TextEmbedding | None = None

def _get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(FASTEMBED_MODEL)
    return _embed_model


def embed(text: str) -> list[float]:
    """Embed a single text in-process using fastembed."""
    model = _get_embed_model()
    return next(model.embed([text])).tolist()


# ── BOM lookup ───────────────────────────────────────────────────────────────

_bom_cache: list[dict] | None = None

def load_bom() -> list[dict]:
    global _bom_cache
    if _bom_cache is None:
        _bom_cache = []
        if BOM_CSV.exists():
            with BOM_CSV.open() as f:
                _bom_cache = list(csv.DictReader(f))
    return _bom_cache


def find_component(reference: str, board: str | None = None) -> list[dict]:
    """Return BOM rows matching the given reference designator."""
    ref = reference.upper().strip()
    rows = load_bom()
    matches = [
        r for r in rows
        if r.get("reference", "").upper() == ref
        and (board is None or r.get("board", "").lower() == board.lower())
    ]
    return matches


# ── LLM Q&A ──────────────────────────────────────────────────────────────────

def ask_llm(question: str, context: str) -> str:
    """Send question + context to mistral:7b and return the answer."""
    prompt = (
        "You are a hardware engineer helping to reverse-engineer a discontinued "
        "RED ONE MX digital cinema camera. Use the datasheet excerpts below to "
        "answer the question accurately and concisely.\n\n"
        f"DATASHEET EXCERPTS:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "ANSWER:"
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


# ── Format helpers ────────────────────────────────────────────────────────────

def format_search_results(results: dict, query: str) -> str:
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not docs:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query!r}\n"]
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        board = meta.get("board", "?")
        part = meta.get("part_number", "?")
        pdf = meta.get("pdf_filename", "?")
        chunk = meta.get("chunk_index", "?")
        score = 1 - dist  # cosine similarity
        excerpt = doc[:400].replace("\n", " ").strip()
        lines.append(
            f"[{i}] {part} ({board}) — {pdf} chunk {chunk}  [similarity: {score:.3f}]\n"
            f"    {excerpt}...\n"
        )
    return "\n".join(lines)


# ── MCP server ────────────────────────────────────────────────────────────────

app = Server("r1mx-datasheets")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_datasheets",
            description=(
                "Semantic search across all indexed component datasheets. "
                "Returns relevant text excerpts with source PDF and board info. "
                "Use for finding specific pin descriptions, register maps, or specifications."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query or keyword to search for",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="lookup_component",
            description=(
                "Given a component reference designator (e.g. 'U7', 'IC3') and optional board name, "
                "find its part number from the BOM and return relevant datasheet excerpts. "
                "Use when you know the reference designator but not the part number."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "Component reference designator (e.g. 'U7', 'IC3', 'U12')",
                    },
                    "board": {
                        "type": "string",
                        "description": "Optional board name filter (e.g. 'cpu_io_board', 'audio_pci_board')",
                    },
                },
                "required": ["reference"],
            },
        ),
        Tool(
            name="ask_component",
            description=(
                "Ask a natural-language question about a component and get an AI-generated answer "
                "based on indexed datasheets. Uses RAG: retrieves relevant chunks, then answers "
                "with mistral:7b. Best for questions like 'What is the I2C address of PCA9698?' "
                "or 'How do I configure the SiI3512 for AHCI mode?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about a component or datasheet",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of datasheet chunks to use as context (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="list_datasheets",
            description=(
                "List all component datasheets currently indexed, grouped by board. "
                "Shows the part number, PDF filename, and number of indexed chunks."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    if name == "search_datasheets":
        query = arguments.get("query", "").strip()
        top_k = int(arguments.get("top_k", 5))
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        try:
            vec = embed(query)
            results = _chroma_query(vec, n_results=top_k)
            text = format_search_results(results, query)
        except Exception as e:
            text = f"Search error: {e}"
        return [TextContent(type="text", text=text)]

    elif name == "lookup_component":
        reference = arguments.get("reference", "").strip()
        board = arguments.get("board", None)
        if not reference:
            return [TextContent(type="text", text="Error: reference is required")]

        rows = find_component(reference, board)
        if not rows:
            return [TextContent(type="text", text=f"Component {reference!r} not found in BOM.")]

        # Build a query from the part numbers found
        parts = list({r["reference"] for r in rows})
        boards = list({r["board"] for r in rows})
        query = " ".join(parts)

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

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "ask_component":
        question = arguments.get("question", "").strip()
        top_k = int(arguments.get("top_k", 5))
        if not question:
            return [TextContent(type="text", text="Error: question is required")]

        try:
            vec = embed(question)
            results = _chroma_query(vec, n_results=top_k)
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            if not docs:
                return [TextContent(type="text", text="No relevant datasheet chunks found for this question.")]

            # Build context string
            context_parts = []
            for doc, meta in zip(docs, metas):
                part = meta.get("part_number", "?")
                pdf = meta.get("pdf_filename", "?")
                context_parts.append(f"[Source: {pdf} / {part}]\n{doc}")
            context = "\n\n---\n\n".join(context_parts)

            answer = ask_llm(question, context)

            # Include sources
            sources = list({m.get("pdf_filename", "?") for m in metas})
            text = f"{answer}\n\nSources: {', '.join(sorted(sources))}"

        except Exception as e:
            text = f"Error: {e}"

        return [TextContent(type="text", text=text)]

    elif name == "list_datasheets":
        try:
            data = _chroma_list_chunks()
            metas = data.get("metadatas") or []

            # Group by board → part_number
            index: dict[str, dict[str, int]] = {}
            for m in metas:
                board = m.get("board", "unknown")
                part = m.get("pdf_filename", "?")
                index.setdefault(board, {})
                index[board][part] = index[board].get(part, 0) + 1

            if not index:
                return [TextContent(type="text", text="No datasheets indexed yet. Run: python scripts/index_datasheets.py")]

            lines = [f"Indexed datasheets ({sum(sum(v.values()) for v in index.values())} total chunks):\n"]
            for board in sorted(index):
                lines.append(f"  {board}:")
                for pdf, count in sorted(index[board].items()):
                    lines.append(f"    {pdf}  ({count} chunks)")
            return [TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing datasheets: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
