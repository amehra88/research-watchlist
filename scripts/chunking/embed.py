#!/usr/bin/env python3
"""
Shared embedding helper for the chunk store (Store A).

Single source of truth for: loading the Gemini key, calling
`gemini-embedding-001`, and caching embeddings by content hash so re-ingest
only embeds changed chunks. `embed_experiment.py` and `ingest.py` both import
from here — no duplicated embedding code.

Embeddings: Gemini `gemini-embedding-001` (dim 3072) — the only embedding
access available; key from /root/podcasts/.env per the enrich_sidecars
convention (the shell GEMINI_API_KEY is expired).

task_type matters: documents are embedded `retrieval_document`, queries
`retrieval_query` — asymmetric embedding is how the model aligns a short
question to a long passage.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

MODEL = "models/gemini-embedding-001"
EMBED_DIM = 3072
_CACHE_PATH = Path("/root/research-watchlist/state/chunk_store/embed_cache.json")


def load_key() -> None:
    """Populate GEMINI_API_KEY, preferring /root/podcasts/.env (known-valid)
    over the expired shell key. Idempotent."""
    if os.environ.get("GEMINI_API_KEY"):
        return
    envf = Path("/root/podcasts/.env")
    if envf.exists():
        for line in envf.read_text().splitlines():
            line = line.strip()
            if line.startswith(("GEMINI_API_KEY=", "export GEMINI_API_KEY=")):
                os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
                break
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("no GEMINI_API_KEY available (checked shell + /root/podcasts/.env)")


def _client():
    load_key()
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai


def _cache_key(text: str, task_type: str) -> str:
    return hashlib.sha256(f"{MODEL}|{task_type}|{text}".encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if _CACHE_PATH.exists():
        try:
            return json.loads(_CACHE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(cache))


def embed(texts: list[str], task_type: str, *, use_cache: bool = True,
          genai=None) -> list[list[float]]:
    """Embed `texts` (task_type = retrieval_document | retrieval_query).

    Cache hit by sha256(model|task_type|text) means re-running ingest after a
    content edit only spends API calls on the chunks that actually changed.
    """
    cache = _load_cache() if use_cache else {}
    keys = [_cache_key(t, task_type) for t in texts]
    todo = [i for i, k in enumerate(keys) if k not in cache]

    if todo:
        genai = genai or _client()
        for i in todo:
            for attempt in range(3):
                try:
                    r = genai.embed_content(model=MODEL, content=texts[i],
                                            task_type=task_type)
                    cache[keys[i]] = r["embedding"]
                    break
                except Exception:  # noqa: BLE001 — transient API errors; retry w/ backoff
                    if attempt == 2:
                        raise
                    time.sleep(1.5 * (attempt + 1))
        if use_cache:
            _save_cache(cache)

    return [cache[k] for k in keys]


def embed_one(text: str, task_type: str) -> list[float]:
    return embed([text], task_type)[0]
