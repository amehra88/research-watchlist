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

Three properties this module exists to guarantee, each learned the hard way:

  * **Batched.** `embed_content` takes a list and returns one vector per item,
    bit-identical to embedding them singly (verified). One call per text put a
    16k-phrase pass at ~10.7 hours.
  * **Read once, written atomically.** The chunk-store cache is ~319MB. It is
    loaded once per process and saved via a tmp file + `os.replace`. A
    non-atomic save is genuinely dangerous here: `_read_cache_file` swallows
    `JSONDecodeError` and returns `{}`, so a kill mid-write makes a truncated
    cache read as EMPTY, and the next save then overwrites 319MB of real
    embeddings with whatever small dict that run happened to build.
  * **Separately addressable.** `cache_path` lets a caller keep its own cache.
    New callers (the topic path) should pass one rather than pay — or risk —
    the chunk store.
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

#: texts per API call. The endpoint caps a batch request; 100 is well inside it.
BATCH_SIZE = 100
#: persist every N batches so a usage cliff costs one batch, not the whole pass.
FLUSH_EVERY = 5

# path -> cache dict, loaded at most once per process.
_CACHES: dict[Path, dict] = {}
# paths with unsaved entries.
_DIRTY: set[Path] = set()


def load_key() -> None:
    """Populate GEMINI_API_KEY, preferring /root/podcasts/.env (known-valid)
    over the expired shell key. Idempotent.

    The .env value, when present, OVERRIDES any pre-existing shell
    GEMINI_API_KEY: the shell key is documented-stale, so an early return on
    `os.environ.get(...)` would silently embed against the expired key."""
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


# ───────────────────────── cache ─────────────────────────

def _read_cache_file(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _cache_for(path: Path) -> dict:
    """Load `path` at most once per process. Re-reading a 319MB JSON per call
    is what took a probe to exit 137 (OOM)."""
    if path not in _CACHES:
        _CACHES[path] = _read_cache_file(path)
    return _CACHES[path]


def _save_cache(cache: dict, path: Path) -> None:
    """Atomic: same-directory tmp then `os.replace`, so a kill leaves the old
    cache intact rather than a truncated one that silently reads as empty."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp{os.getpid()}")
    try:
        tmp.write_text(json.dumps(cache))
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def flush_cache(path: Path | str | None = None) -> None:
    """Persist dirty caches. `path=None` flushes every dirty cache."""
    targets = [Path(path)] if path is not None else list(_DIRTY)
    for p in targets:
        if p in _DIRTY:
            _save_cache(_CACHES[p], p)
            _DIRTY.discard(p)


# ───────────────────────── embedding ─────────────────────────

def _call(genai, content, task_type):
    """One request, with backoff. `content` may be a str or a list of str."""
    for attempt in range(3):
        try:
            return genai.embed_content(model=MODEL, content=content,
                                       task_type=task_type)
        except Exception:  # noqa: BLE001 — transient API errors; retry w/ backoff
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))


def _embed_batch(genai, batch: list[tuple[str, str]], task_type: str,
                 cache: dict) -> None:
    """Fill `cache` for one batch of (cache_key, text).

    Batch first; on ANY batch-level failure fall back to embedding each text
    on its own. Evidence units are MD&A prose blocks of uneven length, so a
    single over-long block would otherwise cost the other 99 embeddings in its
    request.
    """
    if len(batch) > 1:
        try:
            vecs = _call(genai, [t for _, t in batch], task_type)["embedding"]
            if len(vecs) != len(batch):
                raise ValueError(
                    f"batch returned {len(vecs)} vectors for {len(batch)} texts")
            for (k, _), v in zip(batch, vecs):
                cache[k] = v
            return
        except Exception:  # noqa: BLE001 — degrade to per-text, below
            pass
    first_error = None
    for k, text in batch:
        try:
            cache[k] = _call(genai, text, task_type)["embedding"]
        except Exception as e:  # noqa: BLE001
            # Keep going: a bad text must not cost the texts QUEUED BEHIND it
            # either. Raising here would abandon the rest of the batch, which
            # is the same loss the per-text fallback exists to prevent.
            first_error = first_error or e
    if first_error is not None:
        raise first_error


def embed(texts: list[str], task_type: str, *, use_cache: bool = True,
          genai=None, cache_path: Path | str | None = None,
          batch_size: int = BATCH_SIZE) -> list[list[float]]:
    """Embed `texts` (task_type = retrieval_document | retrieval_query).

    Cache hit by sha256(model|task_type|text) means re-running ingest after a
    content edit only spends API calls on the chunks that actually changed.

    Duplicates in `texts` cost one call between them: phrase extraction emits
    the same phrase from many filers by design — that repetition is the signal
    `MIN_CANDIDATE_COMPANIES` counts, not something to pay for twice.
    """
    path = Path(cache_path) if cache_path is not None else _CACHE_PATH
    cache = _cache_for(path) if use_cache else {}
    keys = [_cache_key(t, task_type) for t in texts]

    todo: dict[str, str] = {}
    for k, t in zip(keys, texts):
        if k not in cache and k not in todo:
            todo[k] = t

    if todo:
        genai = genai or _client()
        items = list(todo.items())
        batches = [items[i:i + batch_size]
                   for i in range(0, len(items), batch_size)]
        try:
            for n, batch in enumerate(batches, 1):
                _embed_batch(genai, batch, task_type, cache)
                if use_cache:
                    _DIRTY.add(path)
                    if n % FLUSH_EVERY == 0:
                        flush_cache(path)
        finally:
            # flush even when a text ultimately fails, so the batches that DID
            # succeed are not re-bought on the next run.
            if use_cache:
                flush_cache(path)

    return [cache[k] for k in keys]


def embed_one(text: str, task_type: str, *, use_cache: bool = False,
              cache_path: Path | str | None = None) -> list[float]:
    """Embed a single text (the query path). Cache defaults OFF: a query is a
    one-off string that almost never hits the 319MB cache, so loading it per
    query is pure memory waste (the query-path OOM). Callers may force it on."""
    return embed([text], task_type, use_cache=use_cache,
                 cache_path=cache_path)[0]
