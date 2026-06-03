"""
newsdigest — dual-source (Google News RSS + FactSet ALL_NEWS) pre/post-market
news digest over the watchlist's scored tickers.

Spec: memory news-digest-phase-b-spec (Phase B approved 2026-06-02).
Tunable thresholds live here as named constants (spec §9).
"""

# ── Filter thresholds (v2: channel inversion — see filter.py) ─────────────────
HIGH_VOLUME = 4          # v2: story_volume >= this -> MEDIUM (Google volume NO LONGER earns HIGH)
MEDIUM_VOLUME = 2        # DEPRECATED in v2 (volume < HIGH_VOLUME now DROPs); kept to avoid import churn

# ── Fetch windows (spec §1) ───────────────────────────────────────────────────
PREMARKET_WINDOW_HOURS = 24
POSTMARKET_WINDOW_HOURS = 12
FEED_CAP = 100           # max items kept per Google RSS feed

# ── Clustering (spec §4) ──────────────────────────────────────────────────────
JACCARD_THRESHOLD = 0.6          # token-overlap to merge two headlines into one cluster
FACTSET_MATCH_JACCARD = 0.5      # looser overlap to call a Google cluster "corroborated" by FactSet

# ── FactSet channel (spec §1 operator decision, §9) ───────────────────────────
FACTSET_CONCURRENCY = 8          # max concurrent claude -p subprocesses
FACTSET_CACHE_HOURS = 6          # v2: DRY-RUN ONLY (separate cache dir). Production cron bypasses cache (always fresh).
FACTSET_TIMEOUT_SECONDS = 120    # per-ticker claude -p hard timeout

# ── State ledger (spec §10) ───────────────────────────────────────────────────
STALE_HOURS = 18         # skip clusters already surfaced within this many hours
LEDGER_PRUNE_HOURS = 72  # drop ledger entries older than this

# ── Sentiments that count as a signal on a matched FactSet article (§5c) ──────
SIGNAL_SENTIMENTS = {"Positive", "Negative", "Very Positive", "Very Negative"}

__all__ = [
    "HIGH_VOLUME", "MEDIUM_VOLUME",
    "PREMARKET_WINDOW_HOURS", "POSTMARKET_WINDOW_HOURS", "FEED_CAP",
    "JACCARD_THRESHOLD", "FACTSET_MATCH_JACCARD",
    "FACTSET_CONCURRENCY", "FACTSET_CACHE_HOURS", "FACTSET_TIMEOUT_SECONDS",
    "STALE_HOURS", "LEDGER_PRUNE_HOURS", "SIGNAL_SENTIMENTS",
]
