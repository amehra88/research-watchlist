#!/usr/bin/env python3
"""valuation/fundamentals.py — weekly FactSet Fundamentals pull (RIS5 A3).

Sunday (staged, not installed — see docs/portal/cron.txt): net debt, cash, gross margin,
operating margin, FCF margin for the same valuation universe as snapshot.py. Writes
state/valuation/fundamentals_<date>.jsonl (gitignored, dated raw file — same convention
as prices_<date>.jsonl/consensus_<date>.jsonl).

MANDATORY TWO-STEP WORKFLOW (the FactSet_Fundamentals tool's own contract, not a choice
made here): FactSet_Metrics must be called FIRST to discover the exact FF_* metric codes;
Fundamentals must NEVER be called with a guessed/abbreviated code. `discover_metrics()`
does step 1 (FactSet_Metrics, text search, data_products=['fundamentals']); the FF_* codes
it returns are then HARDCODED into FUNDAMENTALS_METRICS below after being confirmed live
(see docs/portal/mcp_schemas.md) — discovery is a one-time probe, not something production
re-runs every week (a metric's code does not change week to week, and re-discovering it
would spend a call for nothing).

Two separate `claude -p` sessions per probe/pull (one per tool), never folded into one —
same "no two tool calls in one session" reasoning as snapshot.py's module docstring
(argument-drift guard blindness + partial-result risk).

Row schema: {ticker, fsym, date, metric, value, periodicity, fiscal_end, currency, quality}.
`metric` is the short label (net_debt/cash/gross_margin/operating_margin/fcf_margin), not
the raw FF_ code (kept in FUNDAMENTALS_METRICS for the prompt only). No amendment-v1.1
range check is specified for fundamentals in the task brief (only price>0/mcap>0/count>=1
are named, all specific to snapshot.py's own rows) — quality is "ok" unless the value is
missing/non-numeric ("fail:missing"), which is the minimum honest bar until the operator
specifies real thresholds (e.g. a plausible net-debt/cash range) for this endpoint.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/root/research-watchlist")
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "lib"))
import claude_p                                                      # noqa: E402
from etfflows.factset_flows import _tool_result_blocks, resolve_payload, rows_of  # noqa: E402
from valuation.snapshot import argument_drift, _run_and_parse         # noqa: E402
from valuation import MODEL, FUNDAMENTALS_TIMEOUT, METRICS_PROBE_TIMEOUT  # noqa: E402

ToolUnavailableError = claude_p.ToolUnavailableError

METRICS_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_Metrics"
FUNDAMENTALS_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_Fundamentals"

STATE_DIR = REPO / "state" / "valuation"

# Confirmed live 2026-09-17 (RIS5 A3 live run): a combined FactSet_Metrics discovery call
# (data_products=["fundamentals","estimates"], batched text queries) resolved these codes;
# a 3-id FactSet_Fundamentals verification call (NVDA-US/AVGO-US/COHR-US) confirmed all six
# return real, non-null values at QTR periodicity. See docs/portal/mcp_schemas.md for the
# full discovery results and the raw verification-row shape.
#
# fcf_margin has NO dedicated FF_ code -- FactSet_Metrics' "free cash flow margin" query
# top match was FF_FREE_CF (Free Cash Flow, a dollar amount, not a margin/ratio); no
# FCF-margin-specific metric ranked in the top 10 for either "free cash flow margin" or
# "free cash flow". It is DERIVED downstream (not pulled) as FF_FREE_CF / FF_SALES --
# FF_SALES is not in this dict (it belongs to snapshot.py's own consensus SALES pull /
# ingest_metrics.py's actuals, not a Fundamentals code fetched here); whatever consumes
# fcf_margin must divide the raw FF_FREE_CF row by a SALES actual it sources itself.
FUNDAMENTALS_METRICS: dict[str, str] = {
    "net_debt": "FF_NET_DEBT",
    "total_debt": "FF_DEBT",
    "cash": "FF_CASH_GENERIC",
    "gross_margin": "FF_GROSS_MGN",
    "operating_margin": "FF_OPER_MGN",
    "fcf": "FF_FREE_CF",   # fcf_margin = fcf / sales, derived downstream -- see note above
}

FUNDAMENTALS_PERIODICITY = "QTR"   # tool's own mandatory fallback ladder: QTR -> SEMI -> ANN
FUNDAMENTALS_FALLBACK = ("QTR", "SEMI", "ANN")


# ---------------------------------------------------------------------------
# Step 1: metric-code discovery (FactSet_Metrics)
# ---------------------------------------------------------------------------
def discover_metrics_prompt(queries: list[str], data_products: list[str] = ("fundamentals",)) -> str:
    a = discover_metrics_args(queries, data_products)
    return (
        "Call the FactSet_Metrics tool EXACTLY ONCE with these arguments:\n"
        f"  text: {json.dumps(a['text'])}\n"
        "  target: 'metric'\n"
        f"  data_products: {json.dumps(a['data_products'])}\n"
        f"  limit: {a['limit']}\n"
        "Do NOT call the tool more than once.\n\n"
        "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat "
        "any of the data — it is read directly from the tool output, not from your reply."
    )


def discover_metrics_args(queries: list[str], data_products: list[str] = ("fundamentals",)) -> dict:
    return {"text": queries, "target": "metric", "data_products": list(data_products), "limit": 10}


def make_discover_runner(repo_root=REPO, timeout=METRICS_PROBE_TIMEOUT,
                         data_products: list[str] = ("fundamentals",)):
    """data_products defaults to fundamentals-only (this module's own weekly Fundamentals
    pull); the live A3 driver overrides to ("fundamentals", "estimates") for a single
    COMBINED probe that also resolves snapshot.py's consensus FCF metric code before any
    consensus batch call is spent on a guessed name (coordinator advisory, 2026-09-17)."""
    def run(queries: list[str]):
        return _run_and_parse(discover_metrics_prompt(queries, data_products), METRICS_TOOL,
                              discover_metrics_args(queries, data_products), repo_root, timeout)
    return run


# ---------------------------------------------------------------------------
# Step 2: Fundamentals pull
# ---------------------------------------------------------------------------
def _fundamentals_args(fids: list[str], codes: list[str], periodicity: str) -> dict:
    return {"data_type": "fundamentals", "ids": fids, "metrics": codes,
           "periodicity": periodicity, "audit": None}


def _fundamentals_prompt(fids: list[str], codes: list[str], periodicity: str) -> str:
    a = _fundamentals_args(fids, codes, periodicity)
    return (
        "Call the FactSet_Fundamentals tool EXACTLY ONCE with these arguments:\n"
        f"  data_type: '{a['data_type']}'\n"
        f"  ids: {json.dumps(a['ids'])}\n"
        f"  metrics: {json.dumps(a['metrics'])}\n"
        f"  periodicity: '{a['periodicity']}'\n"
        "  audit: null\n"
        "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with a "
        "different periodicity or a different set of metrics.\n\n"
        "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat "
        "any of the data — it is read directly from the tool output, not from your reply."
    )


def make_fundamentals_runner(repo_root=REPO, timeout=FUNDAMENTALS_TIMEOUT):
    def run(fids: list[str], codes: list[str], periodicity: str = FUNDAMENTALS_PERIODICITY):
        return _run_and_parse(_fundamentals_prompt(fids, codes, periodicity), FUNDAMENTALS_TOOL,
                              _fundamentals_args(fids, codes, periodicity), repo_root, timeout)
    return run


def normalize_fundamentals_rows(raw: list[dict], fid_to_ticker: dict, code_to_label: dict,
                                periodicity: str) -> list[dict]:
    """One row per (ticker, metric) -- FactSet_Fundamentals rows are typically keyed by
    requestId + metric code (`metric`/`metricCode`, defensive over both spellings) + value."""
    out = []
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        code = r.get("metric") or r.get("metricCode") or r.get("ffMetric")
        label = code_to_label.get(code, code)
        value = r.get("value")
        value = value if isinstance(value, (int, float)) else None
        out.append({
            "ticker": tk, "fsym": fid, "date": r.get("date") or r.get("fiscalPeriodEnd"),
            "metric": label, "value": value, "periodicity": periodicity,
            "fiscal_end": r.get("fiscalPeriodEnd") or r.get("date"),
            "currency": r.get("currency"),
            "quality": "ok" if value is not None else "fail:missing",
        })
    return out


def main(argv=None) -> int:
    if not FUNDAMENTALS_METRICS:
        print("FUNDAMENTALS_METRICS is empty -- run the FactSet_Metrics probe and hardcode "
             "the confirmed FF_ codes (see module docstring / docs/portal/mcp_schemas.md) "
             "before this CLI can pull live data.", file=sys.stderr)
        return 1
    print("fundamentals.py: metrics confirmed:", FUNDAMENTALS_METRICS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
