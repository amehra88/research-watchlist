#!/usr/bin/env python3
"""Compact embedding store for topic mapping.

Why not scripts/chunking/embed.py's cache: that is a 334 MB JSON blob loaded whole
(the query-path OOM). Here vectors sit in a float16 .npy (12K × 3072 × 2 B ≈ 75 MB)
beside an ids.json, embedding is BATCHED (embed_content accepts a list — ~50× fewer
calls than embed.py's one-call-per-text), a 429 backs off instead of failing after
1.5 s, and the store is saved after every batch so a killed run loses ≤ one batch.
Same model and task_type as the pg chunks, so cosines against pg-derived anchors
are like-for-like."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "/root/research-watchlist/scripts/chunking")
import embed as chunk_embed  # noqa: E402  load_key(), MODEL, EMBED_DIM

MODEL = chunk_embed.MODEL
EMBED_DIM = chunk_embed.EMBED_DIM
RATE_LIMIT_SLEEP_S = 30
MAX_ATTEMPTS = 6


def is_rate_limit(exc: BaseException) -> bool:
    s = str(exc).lower()
    return "429" in s or "resource" in s and "exhaust" in s or "quota" in s


def embed_batch(client, texts: list[str], task_type: str) -> list[list[float]]:
    """One batched call with 429-aware backoff; other errors retry briefly then raise."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            r = client.embed_content(model=MODEL, content=texts, task_type=task_type)
            vecs = r["embedding"]
            if len(vecs) != len(texts):
                raise RuntimeError(f"embedding count {len(vecs)} != texts {len(texts)}")
            return vecs
        except Exception as e:  # noqa: BLE001
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(RATE_LIMIT_SLEEP_S * (attempt + 1) if is_rate_limit(e) else 2.0)
    raise RuntimeError("unreachable")


def _client():
    chunk_embed.load_key()
    import google.generativeai as genai
    import os
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai


class EmbedStore:
    def __init__(self, dir: Path):
        self.dir = Path(dir)
        self.ids_path, self.vec_path = self.dir / "ids.json", self.dir / "vectors.npy"
        if self.ids_path.exists() and self.vec_path.exists():
            self.ids = json.loads(self.ids_path.read_text())
            self.vecs = np.load(self.vec_path)
        else:
            self.ids, self.vecs = [], np.zeros((0, EMBED_DIM), dtype=np.float16)
        self._index = {i: n for n, i in enumerate(self.ids)}

    def has(self, id: str) -> bool:
        return id in self._index

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.vec_path.with_suffix(".npy.tmp")
        with open(tmp, "wb") as fh:               # np.save(path) would append .npy to the .tmp name
            np.save(fh, self.vecs)
        tmp.replace(self.vec_path)
        self.ids_path.write_text(json.dumps(self.ids))

    def ensure(self, items: list, task_type: str = "retrieval_document", batch: int = 50,
               client=None, log=None) -> int:
        todo = [(i, t) for i, t in items if i not in self._index]
        if not todo:
            return 0
        client = client or _client()
        done = 0
        for k in range(0, len(todo), batch):
            chunk = todo[k:k + batch]
            vecs = np.asarray(embed_batch(client, [t for _, t in chunk], task_type), dtype=np.float16)
            self.vecs = np.vstack([self.vecs, vecs])
            for i, _ in chunk:
                self._index[i] = len(self.ids); self.ids.append(i)
            self.save()
            done += len(chunk)
            if log:
                log(f"  embedded {done}/{len(todo)}")
        return done

    def matrix(self, ids: list[str]) -> np.ndarray:
        rows = np.asarray([self._index[i] for i in ids], dtype=np.int64)
        m = self.vecs[rows].astype(np.float32)
        n = np.linalg.norm(m, axis=1, keepdims=True); n[n == 0] = 1.0
        return m / n
