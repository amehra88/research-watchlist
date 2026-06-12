-- ===========================================================================
-- Chunking & retrieval — canonical store schema (Store A + Store B)
--
-- This is the DURABLE TARGET SPEC for docs/chunking-strategy.md §9 ("Store =
-- pgvector"). It is intentionally NOT executed today: at ~2,300 chunks the
-- step-4 ingestion/retrieval job runs against a file-backed store
-- (scripts/chunking/store.py :: FileStore, in-process numpy cosine), which
-- mirrors these tables column-for-column. This file is the contract that
-- backend honours, and the DDL a managed-pgvector instance loads verbatim when
-- the swap is triggered.
--
-- WHEN TO MIGRATE (the swap trigger): step 5 — when Store B (FactSet
-- guidance-beat time series, §2a) lands and the Store-A <-> Store-B JOIN (§2,
-- view at bottom) becomes real. That JOIN — narrative `guidance` chunk to its
-- management's quantitative beat/miss history — is the whole reason pgvector
-- was chosen over a flat vector index; until it exists, numpy is sub-ms and a
-- daemon buys nothing. At swap time: provision managed pgvector, run this file,
-- set CHUNK_STORE_BACKEND=pg, re-run ingest.py.
--
-- Embedding model: Gemini `gemini-embedding-001`, dim 3072 (confirmed).
-- ===========================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------------
-- STORE A — narrative chunks (the prose: transcripts, conf, operator notes).
-- One row per chunk. Columns mirror scripts/chunking/chunker.py :: Chunk
-- exactly (parent + child rows; children carry the embedding, parents are the
-- auto-merge return target, §3a).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chunks (
    -- identity / lineage -----------------------------------------------------
    chunk_id          TEXT PRIMARY KEY,             -- stable, deterministic (e.g. NVDA-1Q27-qa-07)
    doc_id            TEXT NOT NULL,                -- sha256 of source doc; FK -> document-index.jsonl / DocMetadata
    parent_id         TEXT REFERENCES chunks(chunk_id) ON DELETE CASCADE,  -- self-FK; NULL for parents
    kind              TEXT NOT NULL CHECK (kind IN ('parent', 'child')),
    text              TEXT NOT NULL,

    -- provenance / structural (inherited from the parent doc) ----------------
    tickers           TEXT[] NOT NULL DEFAULT '{}', -- PER-CHUNK ticker array (§v3 multi-ticker); [] for macro/sector notes. Mirrors chunker.py Chunk.tickers.
    doc_type          TEXT NOT NULL,                -- earnings_transcript | conference_transcript | operator_note | ...
    event_date        DATE,
    fiscal_quarter    TEXT,                         -- e.g. 1Q27
    section           TEXT,                         -- the source `## ` header

    -- prepared-remarks speaker (NULL on Q&A) ---------------------------------
    speaker           TEXT,
    speaker_role      TEXT,

    -- Q&A: the ANSWERER is first-class signal; the asker is non-ranking cite --
    answered_by       TEXT,                         -- exec who RESPONDED (signal)
    answerer_role     TEXT,                         -- CEO | CFO | COO | CBO | IR
    answer_directness TEXT,                         -- direct | partial | evasive | new_disclosure | reiteration
    asker_citation    TEXT,                         -- analyst (Firm) — provenance ONLY, never ranked/filtered/boosted

    -- the two operator-endorsed conviction axes ------------------------------
    claim_source      TEXT NOT NULL DEFAULT 'operator_opinion',  -- operator_opinion | management | analyst_question | sell_side | media
    time_orientation  TEXT NOT NULL DEFAULT 'current',           -- backward | current | forward

    -- Axis 2 (facets, enum-validated, <=4) + Axis 3 (themes) -----------------
    facets            TEXT[] NOT NULL DEFAULT '{}',
    themes            TEXT[] NOT NULL DEFAULT '{}',

    -- the vector (children only; parents stored with embedding NULL) ---------
    embedding         vector(3072)
);

-- Metadata filters used as hard scopes where correct (§7: ticker/date/quarter).
CREATE INDEX IF NOT EXISTS chunks_tickers_idx  ON chunks USING GIN (tickers);
CREATE INDEX IF NOT EXISTS chunks_event_date_idx ON chunks (event_date);
CREATE INDEX IF NOT EXISTS chunks_doc_id_idx   ON chunks (doc_id);
-- Soft-boost ranking signals (§7, §11b-c): facet/theme overlap, not a hard gate.
CREATE INDEX IF NOT EXISTS chunks_facets_idx   ON chunks USING GIN (facets);
CREATE INDEX IF NOT EXISTS chunks_themes_idx   ON chunks USING GIN (themes);

-- ANN index — NOT needed at a few-thousand vectors (exact scan is sub-ms) and
-- deferred until the corpus grows. HNSW with cosine distance when enabled:
-- CREATE INDEX chunks_embedding_hnsw ON chunks
--   USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)
--   WHERE kind = 'child';

-- ---------------------------------------------------------------------------
-- STORE B — structured metrics (the numbers: actuals, consensus, guidance).
-- Keyed ticker x period x metric. POPULATED in step 5b from FactSet (guidance +
-- surprise endpoints) via ingest_metrics.py. The guidance-credibility score
-- (§2a) is derived from these rows and cached in metrics_credibility.
--
-- RECONCILED 2026-06-10 (step 5b): the original step-4 DDL (actual/consensus/
-- guidance_low/guidance_high/beat_miss/magnitude — 11 cols) had drifted from the
-- evolved file-backed store_b.py record shape, which carries the full three-
-- relationship model (actual-vs-consensus, actual-vs-own-guide, guide-vs-
-- consensus) verified against live FactSet 2026-06-09. Columns below now mirror
-- scripts/chunking/store_b.py :: build_metrics() output EXACTLY. The earlier
-- "loaded verbatim" claim no longer held; this is the corrected contract.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metrics (
    ticker                 TEXT NOT NULL,
    period                 TEXT NOT NULL,           -- fiscal label, e.g. 1Q27 (store_b.fiscal_label)
    metric                 TEXT NOT NULL,           -- e.g. SALES
    fiscal_end             DATE,                    -- fiscalEndDate (the period dedupe key)
    -- guidance side ----------------------------------------------------------
    guidance_date          DATE,
    guidance_low           NUMERIC,
    guidance_mid           NUMERIC,
    guidance_high          NUMERIC,
    consensus_at_guide     NUMERIC,                 -- FactSet meanBefore
    guide_vs_consensus_pct NUMERIC,                 -- decimal fraction (sandbag-at-guide tell)
    -- actual side ------------------------------------------------------------
    actual                 NUMERIC,                 -- surpriseAfter
    consensus_at_print     NUMERIC,                 -- surpriseBefore
    beat_vs_consensus_pct  NUMERIC,                 -- decimal fraction (normalized from surprisePercent)
    surprise_date          DATE,
    -- derived: actual vs their OWN guidance (the §2a credibility signal) ------
    beat_vs_guidance       TEXT CHECK (beat_vs_guidance IN ('above','below','in_range')),
    beat_vs_guidance_pct   NUMERIC,
    source                 TEXT DEFAULT 'factset',
    as_of                  DATE,
    PRIMARY KEY (ticker, period, metric)
);

CREATE INDEX IF NOT EXISTS metrics_ticker_metric_idx ON metrics (ticker, metric);
CREATE INDEX IF NOT EXISTS metrics_fiscal_end_idx    ON metrics (fiscal_end);

-- §2a guidance-credibility score, aggregated per (ticker, metric) by
-- store_b.credibility_score(). Cached here as JSONB (mirrors the file-backed
-- credibility.json) so the A<->B JOIN is fully pg-native — no Python recompute
-- needed to attach a management team's credibility to a guidance chunk.
CREATE TABLE IF NOT EXISTS metrics_credibility (
    ticker  TEXT NOT NULL,
    metric  TEXT NOT NULL,
    score   JSONB NOT NULL,                         -- the full credibility_score() dict
    PRIMARY KEY (ticker, metric)
);

-- ---------------------------------------------------------------------------
-- THE JOIN that justifies one Postgres for both stores (§2, §2a) — the reason
-- this is pgvector and not a bare vector index. A retrieved `guidance`/forward
-- chunk (the prose "what they guided") JOINs to that management team's
-- quantitative beat/miss track record (the quant "their history of hitting
-- it"). Reproduces store_b.join_guidance_chunk() as a SQL view. ACTIVE as of
-- step 5b: each forward guidance chunk -> its most recent judged metric rows.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW guidance_with_track_record AS
SELECT c.chunk_id, c.tickers, c.fiscal_quarter, c.answered_by, c.text,
       m.period, m.metric, m.fiscal_end,
       m.beat_vs_guidance, m.beat_vs_guidance_pct, m.beat_vs_consensus_pct
FROM   chunks c
JOIN   metrics m
  ON   m.ticker = ANY (c.tickers)
WHERE  'guidance' = ANY (c.facets)
  AND  c.time_orientation = 'forward'
  AND  m.beat_vs_guidance IS NOT NULL;

GRANT SELECT ON guidance_with_track_record TO research;
