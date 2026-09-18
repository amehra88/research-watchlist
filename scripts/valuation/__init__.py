"""valuation — daily FactSet price/market-cap/consensus snapshots (RIS5 A3).

RIS5's ideas engine has no price, market-cap or consensus time series today —
`scripts/valuation/snapshot.py` is the producer. Tunable constants live here,
mirroring the `scripts/etfflows/__init__.py` / `scripts/newsdigest/__init__.py`
convention.

Transport: mcp-lean (`scripts/lib/claude_p.py` `run_mcp`), one `claude -p`
session per (id-batch, endpoint) call, verbatim-transport prompts identical in
spirit to `scripts/etfflows/factset_flows.py` — "call the tool EXACTLY ONCE,
then reply DONE" — never two tool calls folded into one session. Two tool
calls in one session would leave `claude_p.tool_use_input()` (which returns
only the FIRST matching tool_use block) blind to the second call's arguments,
so the argument-drift guard could not cover it, and a session where call 1
lands and call 2 doesn't produces a structurally-valid PARTIAL result — the
exact silent-failure shape every docstring in factset_flows.py exists to
prevent. See snapshot.py's module docstring for why "at most 3 live sessions"
in the task brief is read as the three logical pull stages (prices+market_value
counted together as one), not a literal subprocess-count ceiling: at the
worktree's real filtered universe (178 mapped ids), even ≤100-id batching
alone requires 2 prices + 2 SALES + 2 EPS calls before market_value is
considered at all.
"""

MODEL = "claude-sonnet-4-6"          # matches etfflows/newsdigest transport convention

# ── Batch sizes ────────────────────────────────────────────────────────────
# FactSet_GlobalPrices schema (fetched live via ToolSearch 2026-09-17): "500 for
# single-day prices, 50 for all other data types and multi-day requests." We
# batch prices at 100 (well under 500, per the task brief) but market_value is
# NOT the single-day-prices case — it is "all other data types". RIS5 A3 fix 2
# (coordinator ruling, 2026-09-17 19:30 ET): the live run hit a real 408 Request
# Timeout on a 50-id market_value batch, so the cap is tightened to 25 — smaller
# batches, more calls, but each one is cheaper to retry and less quota is lost
# to a single timed-out request.
PRICE_BATCH = 100
MARKET_VALUE_BATCH = 25
CONSENSUS_BATCH = 100                # consensus_rolling ids cap is 3000; 100 per the brief
FUNDAMENTALS_BATCH = 250             # FactSet_Fundamentals' own documented max ids/call

# ── Timeouts ───────────────────────────────────────────────────────────────
PRICE_TIMEOUT = 180
MARKET_VALUE_TIMEOUT = 180
CONSENSUS_TIMEOUT = 240               # 3 fiscal periods per id, larger payload
FUNDAMENTALS_TIMEOUT = 240
METRICS_PROBE_TIMEOUT = 120

# ── Retry (RIS5 A3 fix 2) ────────────────────────────────────────────────────
# A FactSet-server-side 408/5xx on any batch call: wait this long, retry ONCE,
# then mark the batch failed and continue (never retried a second time — a
# session-limit/429 is a different, non-retryable error class that aborts the
# whole run instead, see snapshot.py's SessionLimitError handling).
RETRY_WAIT_SECONDS = 20

# ── Consensus ──────────────────────────────────────────────────────────────
# Amendment v1.2: daily consensus also pulls EBITDA and FCF alongside SALES/EPS
# (FY1-FY3). "FCF" is the unprefixed FactSet Estimates code for consensus free
# cash flow (confirmed via the live FactSet_Metrics discovery probe — see
# docs/portal/mcp_schemas.md); EBITDA is confirmed directly from the
# FactSet_EstimatesConsensus tool's own schema text ("SALES, EPS, EBITDA,
# PRICE_TGT" are given as unprefixed estimate metric examples).
CONSENSUS_METRICS = ("SALES", "EPS", "EBITDA", "FCF")
RELATIVE_FISCAL_START = 1
RELATIVE_FISCAL_END = 3               # FY1..FY3 in one call per metric (task brief)
PERIODICITY = "ANN"

# Weekly (Sunday, amendment v1.2): FY4-FY5 for the same four metrics, with counts.
# Code path implemented in snapshot.py (--weekly); NOT run live today per the
# coordinator's instruction -- staged cron line only (docs/portal/cron.txt).
WEEKLY_CONSENSUS_METRICS = CONSENSUS_METRICS
WEEKLY_RELATIVE_FISCAL_START = 4
WEEKLY_RELATIVE_FISCAL_END = 5

__all__ = [
    "MODEL", "PRICE_BATCH", "MARKET_VALUE_BATCH", "CONSENSUS_BATCH", "FUNDAMENTALS_BATCH",
    "PRICE_TIMEOUT", "MARKET_VALUE_TIMEOUT", "CONSENSUS_TIMEOUT",
    "FUNDAMENTALS_TIMEOUT", "METRICS_PROBE_TIMEOUT", "RETRY_WAIT_SECONDS",
    "CONSENSUS_METRICS", "RELATIVE_FISCAL_START", "RELATIVE_FISCAL_END", "PERIODICITY",
    "WEEKLY_CONSENSUS_METRICS", "WEEKLY_RELATIVE_FISCAL_START", "WEEKLY_RELATIVE_FISCAL_END",
]
