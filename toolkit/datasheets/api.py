"""
api.py — Clean Python API for datasheet search and RAG queries.

Designed for use by GUI features (Inspector, Pinout Wizard, etc.) that need
to query component datasheets without going through the MCP stdio layer.

Wraps the ChromaDB HTTP REST API and Ollama directly — the same logic as
``mcp_server.py`` but exposed as plain importable functions.

Usage
-----
    from toolkit.datasheets.api import datasheet_api

    results = datasheet_api.search("I2C address PCA9698", top_k=5)
    answer  = datasheet_api.ask("What is the I2C address of PCA9698?")
    answer  = datasheet_api.ask_for_object(db, object_id,
                  "What are the power supply requirements?")
"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

import requests

from toolkit.paths import REPO_ROOT

if TYPE_CHECKING:
    from toolkit.db import DB

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config (mirrors mcp_server.py)
# ---------------------------------------------------------------------------

_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

OLLAMA_HOST      = os.environ.get("OLLAMA_HOST",       "http://localhost:11434")
CHROMA_HOST      = os.environ.get("CHROMA_HOST",       "http://localhost:8000")
FASTEMBED_MODEL  = os.environ.get("FASTEMBED_MODEL",   "BAAI/bge-small-en-v1.5")
LLM_MODEL        = os.environ.get("OLLAMA_LLM_MODEL",  "mistral:7b")
COLLECTION_NAME  = os.environ.get("CHROMA_COLLECTION", "datasheets")

CHROMA_API_BASE = (
    f"{CHROMA_HOST}/api/v2/tenants/default_tenant/databases/default_database"
)

# ---------------------------------------------------------------------------
# DatasheetAPI
# ---------------------------------------------------------------------------

class DatasheetAPI:
    """Lazy singleton for datasheet search and RAG.

    Embedding model and ChromaDB collection ID are initialised on first use
    so that import has zero startup cost.
    """

    def __init__(self):
        self._embed_model = None
        self._collection_id: str | None = None

    # ── Embedding ────────────────────────────────────────────────────────────

    def _get_embed_model(self):
        if self._embed_model is None:
            from fastembed import TextEmbedding
            self._embed_model = TextEmbedding(FASTEMBED_MODEL)
        return self._embed_model

    def _embed(self, text: str) -> list[float]:
        return next(self._get_embed_model().embed([text])).tolist()

    # ── ChromaDB ─────────────────────────────────────────────────────────────

    def _get_collection_id(self) -> str:
        if self._collection_id is None:
            r = requests.get(
                f"{CHROMA_API_BASE}/collections/{COLLECTION_NAME}", timeout=10
            )
            if r.status_code == 200:
                self._collection_id = r.json()["id"]
            else:
                r2 = requests.post(
                    f"{CHROMA_API_BASE}/collections",
                    json={"name": COLLECTION_NAME, "metadata": {"hnsw:space": "cosine"}},
                    timeout=10,
                )
                r2.raise_for_status()
                self._collection_id = r2.json()["id"]
        return self._collection_id

    def _chroma_query(
        self, query_embedding: list[float], n_results: int = 5
    ) -> dict:
        cid = self._get_collection_id()
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

    def _chroma_query_filtered(
        self,
        query_embedding: list[float],
        part_numbers: list[str],
        n_results: int = 5,
    ) -> dict:
        """Query restricted to specific part numbers (when known)."""
        cid = self._get_collection_id()
        where: dict = (
            {"part_number": {"$in": part_numbers}}
            if len(part_numbers) > 1
            else {"part_number": {"$eq": part_numbers[0]}}
        )
        r = requests.post(
            f"{CHROMA_API_BASE}/collections/{cid}/query",
            json={
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "where": where,
                "include": ["documents", "metadatas", "distances"],
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    # ── LLM ──────────────────────────────────────────────────────────────────

    def _ask_llm(self, question: str, context: str) -> str:
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

    # ── Public API ───────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Semantic search across all indexed datasheets.

        Returns a list of result dicts with keys:
            text, part_number, board, pdf_filename, chunk_index, similarity
        """
        if not query.strip():
            return []
        try:
            vec  = self._embed(query)
            raw  = self._chroma_query(vec, n_results=top_k)
            docs = raw.get("documents",  [[]])[0]
            meta = raw.get("metadatas",  [[]])[0]
            dist = raw.get("distances",  [[]])[0]
            return [
                {
                    "text":        d,
                    "part_number": m.get("part_number", ""),
                    "board":       m.get("board", ""),
                    "pdf_filename":m.get("pdf_filename", ""),
                    "chunk_index": m.get("chunk_index", 0),
                    "similarity":  round(1 - s, 4),
                }
                for d, m, s in zip(docs, meta, dist)
            ]
        except Exception as e:
            log.warning("DatasheetAPI.search error: %s", e)
            return []

    def ask(self, question: str, top_k: int = 5) -> str:
        """RAG: retrieve relevant chunks, answer via Ollama.

        Returns a plain-text answer string (or an error message prefixed
        with "Error:").
        """
        if not question.strip():
            return "Error: empty question"
        try:
            vec     = self._embed(question)
            raw     = self._chroma_query(vec, n_results=top_k)
            docs    = raw.get("documents", [[]])[0]
            metas   = raw.get("metadatas", [[]])[0]
            if not docs:
                return "No relevant datasheet chunks found."
            context = "\n\n---\n\n".join(
                f"[Source: {m.get('pdf_filename','?')} / {m.get('part_number','?')}]\n{d}"
                for d, m in zip(docs, metas)
            )
            answer  = self._ask_llm(question, context)
            sources = sorted({m.get("pdf_filename", "?") for m in metas})
            return f"{answer}\n\nSources: {', '.join(sources)}"
        except Exception as e:
            return f"Error: {e}"

    def ask_for_object(self, db: "DB", object_id: int, question: str) -> str:
        """Answer a question scoped to the datasheets linked to *object_id*.

        Looks up the component's part_number and any linked datasheet PDFs
        from the DB, restricts the ChromaDB query to those part numbers, then
        calls the LLM with the retrieved context.

        Falls back to a global search if no part numbers are found.
        """
        if not question.strip():
            return "Error: empty question"

        # Gather part numbers from component + linked datasheets
        part_numbers: list[str] = []
        try:
            # Try components table first
            comp = db.conn().execute(
                "SELECT part_number FROM components WHERE object_id=?",
                (object_id,)
            ).fetchone()
            if comp and comp["part_number"]:
                part_numbers.append(comp["part_number"])

            # Also look at linked datasheets (filename stem as part number)
            ds_rows = db.get_object_datasheets(object_id)
            for row in ds_rows:
                from pathlib import Path as _P
                stem = _P(row["filename"] or "").stem
                if stem and stem not in part_numbers:
                    part_numbers.append(stem)
        except Exception as e:
            log.warning("ask_for_object: DB lookup failed: %s", e)

        try:
            vec = self._embed(question)
            if part_numbers:
                raw = self._chroma_query_filtered(vec, part_numbers, n_results=5)
            else:
                raw = self._chroma_query(vec, n_results=5)

            docs  = raw.get("documents", [[]])[0]
            metas = raw.get("metadatas", [[]])[0]
            if not docs:
                # Broaden search if filtered result is empty
                if part_numbers:
                    raw   = self._chroma_query(vec, n_results=5)
                    docs  = raw.get("documents", [[]])[0]
                    metas = raw.get("metadatas", [[]])[0]

            if not docs:
                return "No relevant datasheet chunks found for this component."

            context = "\n\n---\n\n".join(
                f"[Source: {m.get('pdf_filename','?')} / {m.get('part_number','?')}]\n{d}"
                for d, m in zip(docs, metas)
            )
            answer  = self._ask_llm(question, context)
            sources = sorted({m.get("pdf_filename", "?") for m in metas})
            return f"{answer}\n\nSources: {', '.join(sources)}"
        except Exception as e:
            return f"Error: {e}"

    def is_available(self) -> bool:
        """Return True if ChromaDB is reachable (minimum requirement)."""
        try:
            r = requests.get(f"{CHROMA_HOST}/api/v2/heartbeat", timeout=3)
            return r.status_code == 200
        except Exception:
            return False


# Module-level singleton — import and use directly
datasheet_api = DatasheetAPI()
