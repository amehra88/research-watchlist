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
# NOT the single-day-prices case — it is "all other data types" — so its real
# hard cap is 50, not 100. Sending 100 ids on a market_value call would be
# rejected or silently truncated; the schema quote is the source of truth over
# the brief's blanket "≤100 ids/call" gloss.
PRICE_BATCH = 100
MARKET_VALUE_BATCH = 50
CONSENSUS_BATCH = 100                # consensus_rolling ids cap is 3000; 100 per the brief

# ── Timeouts ───────────────────────────────────────────────────────────────
PRICE_TIMEOUT = 180
MARKET_VALUE_TIMEOUT = 180
CONSENSUS_TIMEOUT = 240               # 3 fiscal periods per id, larger payload
FUNDAMENTALS_TIMEOUT = 240
METRICS_PROBE_TIMEOUT = 120

# ── Consensus ──────────────────────────────────────────────────────────────
CONSENSUS_METRICS = ("SALES", "EPS")
RELATIVE_FISCAL_START = 1
RELATIVE_FISCAL_END = 3               # FY1..FY3 in one call per metric (task brief)
PERIODICITY = "ANN"

__all__ = [
    "MODEL", "PRICE_BATCH", "MARKET_VALUE_BATCH", "CONSENSUS_BATCH",
    "PRICE_TIMEOUT", "MARKET_VALUE_TIMEOUT", "CONSENSUS_TIMEOUT",
    "FUNDAMENTALS_TIMEOUT", "METRICS_PROBE_TIMEOUT",
    "CONSENSUS_METRICS", "RELATIVE_FISCAL_START", "RELATIVE_FISCAL_END", "PERIODICITY",
]
