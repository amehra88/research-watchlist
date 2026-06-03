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
    ticker            TEXT,                         -- PER-SEGMENT (§7); may differ from doc.primary_ticker; NULL for multi-ticker sector notes
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
CREATE INDEX IF NOT EXISTS chunks_ticker_idx   ON chunks (ticker);
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
-- Keyed ticker x period x metric. DDL ONLY in step 4 — POPULATED IN STEP 5
-- from FactSet (Fundamentals / EstimatesConsensus / Metrics). The
-- guidance-credibility score (§2a) is derived from this table.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metrics (
    ticker         TEXT NOT NULL,
    period         TEXT NOT NULL,                   -- fiscal period, e.g. 1Q27
    metric         TEXT NOT NULL,                   -- e.g. revenue, dc_gross_margin, eps
    actual         NUMERIC,                         -- reported actual
    consensus      NUMERIC,                         -- street consensus at the time
    guidance_low   NUMERIC,                         -- guided range (low)
    guidance_high  NUMERIC,                         -- guided range (high)
    beat_miss      TEXT,                            -- beat | miss | in_line (vs consensus/guide)
    magnitude      NUMERIC,                         -- beat/miss magnitude (e.g. % or abs)
    source         TEXT DEFAULT 'factset',
    as_of          DATE,
    PRIMARY KEY (ticker, period, metric)
);

CREATE INDEX IF NOT EXISTS metrics_ticker_metric_idx ON metrics (ticker, metric);

-- ---------------------------------------------------------------------------
-- THE JOIN that justifies one Postgres for both stores (§2, §2a) — the reason
-- this is pgvector and not a bare vector index. A retrieved `guidance` chunk
-- (the prose "what they guided") JOINs to that management team's quantitative
-- beat/miss track record (the quant "their history of hitting it"). Sketch
-- only — the credibility aggregation lands with Store B in step 5.
--
-- CREATE VIEW guidance_with_track_record AS
-- SELECT c.chunk_id, c.ticker, c.fiscal_quarter, c.answered_by, c.text,
--        m.metric, m.beat_miss, m.magnitude
-- FROM   chunks c
-- JOIN   metrics m
--   ON   m.ticker = c.ticker
-- WHERE  'guidance' = ANY (c.facets)
--   AND  c.time_orientation = 'forward';
