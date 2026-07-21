#!/usr/bin/env python3
"""
Chunk store — the backend seam (docs/chunking-strategy.md step 4).

`Store` is the interface the retriever talks to. Two implementations:

  * FileStore  — TODAY. Persists to state/chunk_store/ (chunks.jsonl +
                 embeddings.npy), exact in-process numpy cosine. Correct and
                 sub-millisecond at the current ~2,300-vector scale; stays in
                 the repo's flat-files-in-git ethos (no daemon).
  * PgStore    — STEP 5 stub. The managed-pgvector backend, swapped in when
                 Store B (FactSet guidance-beat) lands and the Store-A<->B JOIN
                 (schema.sql, §2) becomes real. Same interface; the retriever
                 does not change.

Pick via env: CHUNK_STORE_BACKEND = file (default) | pg.

The FileStore columns mirror schema.sql / chunker.py::Chunk exactly, and its
ranking reproduces the PROVEN retriever from embed_experiment.py: cosine +
soft facet boost (NOT a hard facet gate — §7, §11b-c). The §7 operator-opinion
and recency boosts are additional, default-OFF weights so the gold eval stays
an apples-to-apples reproduction of the documented numbers; retrieve.py turns
them on for production.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np

STORE_DIR = Path("/root/research-watchlist/state/chunk_store")
_CHUNKS_FILE = "chunks.jsonl"      # all chunks (parents + children), git-trackable
_EMB_FILE = "embeddings.npy"       # float32 matrix, children only (gitignored, regenerable)
_EMB_INDEX_FILE = "emb_index.json"  # row -> chunk_id, aligned with embeddings.npy

# §11d source-quality re-ranking. A mild multiplier on the cosine score so that
# primary sources (earnings calls, operator notes, filings) win ties over the
# secondary commentary (news / substack) that flooded the corpus as it grew
# ~3K -> 40K chunks. Because the gold eval is ticker-scoped, that growth is a
# WITHIN-ticker dilution (NVDA scope became ~80% news+substack) that pushed the
# lone gold earnings chunk of single-match queries past k, dropping the eval
# 14/28/28 -> 13/23/24. This restores it without pruning the corpus. ON by
# default (part of the base ranking, NOT gated by production_boosts); keys must
# match chunks.doc_type exactly, anything unlisted keeps raw cosine (weight 1.0).
#
# Tuned against eval_store.py on the 40K corpus (see eval_baseline_restored):
# the effective lever is boosting PRIMARY sources, not penalizing news — a 1.05
# primary boost alone restores 15/28/28, while a news-only 0.90 penalty does not
# (14/26/26). 1.10 is chosen over the 1.05 floor for margin as the corpus keeps
# growing; sec 1.05 / news 0.95 keep the source-quality ordering.
_DOC_TYPE_WEIGHTS = {
    "earnings_transcript":           1.10,
    "earnings_transcript_synthesis": 1.10,
    "operator_note":                 1.10,
    "conference_transcript":         1.10,
    "sec_filing":                    1.05,
    "conference_summary":            1.00,
    "podcast_summary":               1.00,
    "substack_post":                 1.00,
    "runbook":                       1.00,
    "news":                          0.95,
    "news_event":                    0.95,
}


def _dt_weight(doc_type: Optional[str]) -> float:
    """Source-quality multiplier for a chunk's doc_type (default 1.0)."""
    return _DOC_TYPE_WEIGHTS.get(doc_type or "", 1.0)


@dataclass
class Hit:
    chunk: dict          # the matched child chunk (all Chunk fields)
    score: float
    parent: Optional[dict] = None  # auto-merge target (§3a), filled by retriever
    track_record: Optional[list] = None  # A<->B JOIN: mgmt quant history (guidance chunks only)
    credibility: Optional[dict] = None   # A<->B JOIN: mgmt credibility score (guidance chunks only)


# ---------------------------------------------------------------------------
class Store:
    """Interface every backend implements. Records are plain dicts = a Chunk
    via dataclasses.asdict(), with an `embedding` key (list[float] or None)."""

    def upsert(self, records: list[dict]) -> int:
        raise NotImplementedError

    def search(self, query_vec, k, **kw) -> list[Hit]:
        raise NotImplementedError

    def get_parent(self, chunk_id: str) -> Optional[dict]:
        raise NotImplementedError

    def count(self) -> tuple[int, int]:
        """(parents, children)."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
class FileStore(Store):
    def __init__(self, store_dir: Path = STORE_DIR):
        self.dir = Path(store_dir)
        self.records: dict[str, dict] = {}   # chunk_id -> chunk dict (no embedding inline)
        self._emb_ids: list[str] = []        # row-aligned with self._emb
        self._emb: Optional[np.ndarray] = None  # (n_children, dim) L2-normalized
        self._load()

    # --- persistence --------------------------------------------------------
    def _load(self) -> None:
        cf = self.dir / _CHUNKS_FILE
        if cf.exists():
            for line in cf.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.records[r["chunk_id"]] = r
        ef, xf = self.dir / _EMB_FILE, self.dir / _EMB_INDEX_FILE
        if ef.exists() and xf.exists():
            self._emb = np.load(ef)
            self._emb_ids = json.loads(xf.read_text())
            self._normalize()

    def _normalize(self) -> None:
        if self._emb is not None and len(self._emb):
            norms = np.linalg.norm(self._emb, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self._emb = (self._emb / norms).astype(np.float32)

    def _save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with (self.dir / _CHUNKS_FILE).open("w", encoding="utf-8") as fh:
            for r in self.records.values():
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        if self._emb is not None and len(self._emb):
            np.save(self.dir / _EMB_FILE, self._emb)
            (self.dir / _EMB_INDEX_FILE).write_text(json.dumps(self._emb_ids))

    # --- writes -------------------------------------------------------------
    def upsert(self, records: list[dict]) -> int:
        """Idempotent by chunk_id. A record's `embedding` (if non-null) is
        stored in the matrix; parents (embedding None) are metadata only."""
        emb_map = dict(zip(self._emb_ids, self._emb)) if self._emb is not None else {}
        for r in records:
            r = dict(r)
            emb = r.pop("embedding", None)
            self.records[r["chunk_id"]] = r
            if emb is not None:
                emb_map[r["chunk_id"]] = np.asarray(emb, dtype=np.float32)
        # rebuild matrix from the merged map (only ids still present as records)
        ids = [cid for cid in emb_map if cid in self.records]
        self._emb_ids = ids
        self._emb = (np.vstack([emb_map[c] for c in ids]).astype(np.float32)
                     if ids else None)
        self._normalize()
        self._save()
        return len(records)

    def clear(self) -> None:
        self.records.clear()
        self._emb_ids, self._emb = [], None

    # --- reads --------------------------------------------------------------
    def get_parent(self, chunk_id: str) -> Optional[dict]:
        rec = self.records.get(chunk_id)
        if rec and rec.get("parent_id"):
            return self.records.get(rec["parent_id"])
        return None

    def count(self) -> tuple[int, int]:
        p = sum(1 for r in self.records.values() if r.get("kind") == "parent")
        c = sum(1 for r in self.records.values() if r.get("kind") == "child")
        return p, c

    def search(self, query_vec, k=5, *,
               query_facets: Optional[set] = None,
               ticker: Optional[str] = None,
               since: Optional[str] = None,
               themes: Optional[list] = None,
               facet_lambda: float = 0.05,
               operator_boost: float = 0.0,
               recency_lambda: float = 0.0,
               recency_halflife_days: float = 365.0,
               asof: Optional[str] = None) -> list[Hit]:
        """Rank children by cosine + soft facet boost (+ optional §7 boosts).

        - facet_lambda: the PROVEN soft boost (embed_experiment.py): cosine +
          lambda * (fraction of query facets carried by the chunk's top-level
          facets). NOT a hard gate.
        - operator_boost: §7 additive bonus for claim_source == operator_opinion.
        - recency_lambda / halflife: §7 recency decay (additive, half-life days).
        - ticker / since / themes: HARD scoping filters (correct as gates per §7).
          themes keeps only chunks carrying ANY of the given theme tags (set
          overlap); None/[] disables it (unchanged behavior). This is the single
          theme-filter site for BOTH backends — PgStore inherits this in-memory
          search (step-5b is a data-integrity swap, not a ranking/SQL change), so
          there is no separate SQL path; themes are already loaded into rec.
        The §7 operator/recency weights default OFF (production_boosts). The
        §11d source-quality doc_type multiplier (_DOC_TYPE_WEIGHTS) is ALWAYS
        applied — it is part of the base ranking, added to hold the gold
        baseline after the corpus grew 3K->40K and diluted single-match queries.
        """
        if self._emb is None or not len(self._emb):
            return []
        q = np.asarray(query_vec, dtype=np.float32)
        q = q / (np.linalg.norm(q) or 1.0)
        sims = self._emb @ q  # cosine (both normalized)

        qf = {f.split(".")[0] for f in (query_facets or set())}
        asof_d = _parse_date(asof) if asof else None

        scored = []
        for row, cid in enumerate(self._emb_ids):
            rec = self.records[cid]
            # hard scoping
            if ticker and ticker not in (rec.get("tickers") or []):
                continue
            if since and (rec.get("event_date") or "") < since:
                continue
            if themes and not (set(themes) & set(rec.get("themes") or [])):
                continue
            # §11d source-quality multiplier on cosine (before additive boosts)
            score = float(sims[row]) * _dt_weight(rec.get("doc_type"))
            if facet_lambda and qf:
                top = {f.split(".")[0] for f in rec.get("facets", [])}
                score += facet_lambda * (len(qf & top) / len(qf))
            if operator_boost and rec.get("claim_source") == "operator_opinion":
                score += operator_boost
            if recency_lambda and rec.get("event_date"):
                ed = _parse_date(rec["event_date"])
                if ed:
                    ref = asof_d or date.today()
                    age = max((ref - ed).days, 0)
                    score += recency_lambda * (0.5 ** (age / recency_halflife_days))
            scored.append((score, cid))

        scored.sort(key=lambda s: -s[0])
        return [Hit(chunk=self.records[cid], score=sc) for sc, cid in scored[:k]]


def _parse_date(s: str) -> Optional[date]:
    try:
        y, m, d = (int(x) for x in s.split("-")[:3])
        return date(y, m, d)
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
class PgStore(FileStore):
    """Managed-pgvector backend (step 5b). Durable rows live in Postgres
    (schema.sql `chunks`), but RANKING is inherited from FileStore unchanged:
    embeddings are loaded from pg into the SAME in-memory numpy structures and
    scored by the SAME cosine + soft-facet-boost code path (search/_normalize/
    get_parent/count are all inherited). The migration is therefore a pure
    data-integrity swap, NOT a ranking change — the gold eval must be byte-
    identical to the file backend. SQL/ANN ranking stays deferred until the
    corpus outgrows exact scan (schema.sql §ANN; vector(3072) is also past
    pgvector's 2000-dim index cap, so exact scan is the only option today).
    The pg-native win is the A<->B JOIN — see store_b.PgMetricsStore."""

    # the 20 Chunk fields (embedding handled separately, as FileStore does)
    _META_COLS = ["chunk_id", "doc_id", "parent_id", "kind", "text", "tickers",
                  "doc_type", "event_date", "fiscal_quarter", "section",
                  "speaker", "speaker_role", "answered_by", "answerer_role",
                  "answer_directness", "asker_citation", "claim_source",
                  "time_orientation", "facets", "themes"]

    def __init__(self):
        import pgconn
        self._conn = pgconn.connect()
        # Backend-agnostic self-descriptor (parity with FileStore.dir). Kept a
        # bare label — never interpolate DATABASE_URL here (would leak password
        # into ingest logs). ingest.py:76 prints this after upsert.
        self.dir = "pg://chunk_store"
        self.records = {}
        self._emb_ids = []
        self._emb = None
        self._load()

    # --- persistence (pg-backed; overrides FileStore's file I/O) ------------
    def _load(self) -> None:
        self.records.clear()
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(self._META_COLS)} FROM chunks")
            for row in cur.fetchall():
                rec = dict(zip(self._META_COLS, row))
                ed = rec.get("event_date")
                # DATE -> 'YYYY-MM-DD' str so search()'s string compares and
                # _parse_date behave EXACTLY as on the file backend.
                rec["event_date"] = ed.isoformat() if ed is not None else None
                rec["facets"] = rec.get("facets") or []   # TEXT[] -> list (NULL-safe)
                rec["themes"] = rec.get("themes") or []
                self.records[rec["chunk_id"]] = rec
            cur.execute("SELECT chunk_id, embedding FROM chunks "
                        "WHERE embedding IS NOT NULL")
            ids, vecs = [], []
            for cid, emb in cur.fetchall():
                ids.append(cid)
                vecs.append(np.asarray(emb, dtype=np.float32))
            self._emb_ids = ids
            self._emb = np.vstack(vecs).astype(np.float32) if vecs else None
        self._normalize()  # inherited; idempotent on already-normalized vectors

    def _save(self) -> None:  # writes go through upsert(); no file persistence
        pass

    def upsert(self, records: list[dict]) -> int:
        """Idempotent by chunk_id (ON CONFLICT). Mirrors FileStore.upsert
        semantics; parents are inserted before children to satisfy the
        self-referential parent_id FK across execute_values pages."""
        from psycopg2.extras import execute_values
        cols = self._META_COLS + ["embedding"]
        pid_i = self._META_COLS.index("parent_id")
        rows = []
        for r in records:
            r = dict(r)
            emb = r.get("embedding")
            row = [r.get(c) for c in self._META_COLS]
            row[self._META_COLS.index("event_date")] = r.get("event_date") or None
            row.append(np.asarray(emb, dtype=np.float32) if emb is not None else None)
            rows.append(row)
        rows.sort(key=lambda row: 0 if row[pid_i] is None else 1)  # parents first
        set_clause = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols if c != "chunk_id")
        with self._conn.cursor() as cur:
            execute_values(
                cur,
                f"INSERT INTO chunks ({', '.join(cols)}) VALUES %s "
                f"ON CONFLICT (chunk_id) DO UPDATE SET {set_clause}",
                rows)
        self._conn.commit()
        self._load()  # refresh in-memory view so search() reflects the write
        return len(records)

    def clear(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("TRUNCATE chunks CASCADE")
        self._conn.commit()
        self.records.clear()
        self._emb_ids, self._emb = [], None


# ---------------------------------------------------------------------------
def get_store() -> Store:
    backend = os.environ.get("CHUNK_STORE_BACKEND", "file").lower()
    if backend == "file":
        return FileStore()
    if backend == "pg":
        return PgStore()
    raise ValueError(f"unknown CHUNK_STORE_BACKEND: {backend!r} (file | pg)")
