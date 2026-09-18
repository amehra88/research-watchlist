#!/usr/bin/env python3
"""valuation/fundamentals.py — weekly FactSet Fundamentals pull (RIS5 A3).

Sunday (staged, not installed — see docs/portal/cron.txt): net debt, cash, gross margin,
operating margin, FCF margin for the same valuation universe as snapshot.py. Writes
state/valuation/fundamentals_<date>.jsonl (gitignored, dated raw file — same convention
as prices_<date>.jsonl/consensus_<date>.jsonl).

ORCHESTRATION (RIS5 A3 fix 5): `main()` runs the full weekly pull end to end -- universe
via `valuation.snapshot.build_universe()` (same T1/T2/T3-minus-.pvt-and-unmapped universe
as the daily snapshot), TWO `FactSet_Fundamentals` calls (`BALANCE_SHEET_METRICS` at QTR,
`FLOW_METRICS` at LTM -- see the periodicity note below for why two, not one),
`≤FUNDAMENTALS_BATCH` (250) ids per call with a 408/5xx retried once via the same
`_retry_once`/argument-drift machinery `snapshot.py` uses, a session-limit/429 abort that
writes nothing, `compute_fcf_margin_rows()` for the derived margin, then an idempotent
`write_jsonl()`. Every live pull before fix 5 was run via a throwaway `/tmp` driver
script that duplicated this logic ad hoc; this is that logic, committed and tested.

CLI:
    python3 scripts/valuation/fundamentals.py --dry-run          # print the planned
                                                                  # calls, no claude -p,
                                                                  # nothing written
    python3 scripts/valuation/fundamentals.py                    # live weekly pull
    python3 scripts/valuation/fundamentals.py --state-dir /tmp/x # override output dir
    python3 scripts/valuation/fundamentals.py --out /tmp/f.jsonl # override output path

PERIODICITY = LTM for FLOW_METRICS, still QTR for BALANCE_SHEET_METRICS (RIS5 A3 fix 4,
coordinator review). A5's first live run showed derived FCF margins ~4x understated
(NVDA 3.8%, AVGO 10%) and 20 names skipped as cash-negative: FF_FREE_CF was pulled at
QTR (one quarter's cash flow) while the SALES it was being divided against elsewhere
was an ANNUAL consensus figure -- a quarter-over-year mismatch, not a real margin.
Fixed by (a) pulling gross_margin/operating_margin/fcf/sales at `LTM` periodicity
(confirmed a valid enum value on this tool's own schema: ANN/ANN_R/QTR/QTR_R/SEMI/
SEMI_R/LTM/LTM_R/LTMSG/LTM_SEMI/LTM_SEMI_R/YTD -- trailing-twelve-months, dimensionally
an annual figure) so FF_FREE_CF is itself already a 12-month number, and (b) pulling
`FF_SALES` in the SAME call/row set so `fcf_margin` is derived as FF_FREE_CF / FF_SALES
from ONE period's data, never mixing a quarterly numerator against an annual (or any
other period's) denominator again -- see `compute_fcf_margin_rows()`, which matches the
two by (ticker, fiscal_end), not just by ticker, so a period mismatch is caught rather
than silently computed. net_debt/total_debt/cash STAY at QTR: they are balance-sheet
snapshots, not flows, and a live full-universe LTM attempt against them returned 0/178
ok for all three (discovered running this very fix, not guessed) -- see
BALANCE_SHEET_METRICS/FLOW_METRICS below. A full pull is therefore TWO
FactSet_Fundamentals calls (one per periodicity group), not one.

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
`metric` is the short label (net_debt/total_debt/cash/gross_margin/operating_margin/fcf/
sales/fcf_margin), not the raw FF_ code (kept in FUNDAMENTALS_METRICS for the prompt
only) -- `fcf_margin` is the one DERIVED label (compute_fcf_margin_rows, fix 4), never a
raw FactSet metric. No amendment-v1.1 range check is specified for fundamentals in the
task brief (only price>0/mcap>0/count>=1 are named, all specific to snapshot.py's own
rows) — quality is "ok" unless the value is missing/non-numeric ("fail:missing"), or,
for the derived `fcf_margin` row only, "fail:period_mismatch" (fcf/sales fiscal_end
disagree) or "fail:sales<=0" (can't divide by a non-positive/missing sales figure) --
the minimum honest bar until the operator specifies real thresholds (e.g. a plausible
net-debt/cash range) for this endpoint.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path("/root/research-watchlist")
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "lib"))
import claude_p                                                      # noqa: E402
from etfflows.factset_flows import _tool_result_blocks, resolve_payload, rows_of  # noqa: E402
from valuation.snapshot import (                                     # noqa: E402
    argument_drift, _run_and_parse, _retry_once, id_chunks, build_universe,
    write_jsonl, SessionLimitError,
)
from valuation import (                                              # noqa: E402
    MODEL, FUNDAMENTALS_TIMEOUT, METRICS_PROBE_TIMEOUT, FUNDAMENTALS_BATCH,
    RETRY_WAIT_SECONDS,
)

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
# "free cash flow". It is DERIVED (fix 4: now IN this module, via compute_fcf_margin_rows,
# not downstream) as FF_FREE_CF / FF_SALES -- FF_SALES IS now in this dict (fix 4;
# previously assumed to come from snapshot.py's consensus pull / ingest_metrics.py's
# actuals, which is exactly the cross-source period mismatch that caused the ~4x
# understated margins) so both halves of the ratio come from the SAME
# FactSet_Fundamentals call, at the SAME periodicity, for the SAME fiscal period.
#
# TWO GROUPS, TWO PERIODICITIES (fix 4 round 2 -- discovered live, not guessed): net_debt/
# total_debt/cash are BALANCE-SHEET items -- a point-in-time snapshot, not something that
# accumulates "trailing twelve months" of. The live full-universe LTM pull that motivated
# this split returned 0/178 ok for all three balance-sheet metrics (every row came back
# with no value) while gross_margin/operating_margin/fcf/sales -- all income-statement/
# cash-flow FLOW metrics, which DO have a meaningful trailing-12-month figure -- were
# ~95%+ ok. Balance-sheet metrics stay on QTR (their original, working periodicity,
# unchanged by fix 4); only the flow metrics move to LTM. This means a full pull now
# takes TWO FactSet_Fundamentals calls (one per periodicity), not one -- a tool constraint
# (periodicity is one value per call, applying to every metric requested), not a choice.
BALANCE_SHEET_METRICS: dict[str, str] = {
    "net_debt": "FF_NET_DEBT",
    "total_debt": "FF_DEBT",
    "cash": "FF_CASH_GENERIC",
}
FLOW_METRICS: dict[str, str] = {
    "gross_margin": "FF_GROSS_MGN",
    "operating_margin": "FF_OPER_MGN",
    "fcf": "FF_FREE_CF",
    "sales": "FF_SALES",   # fix 4: pulled alongside fcf so fcf_margin divides same-period data
}
# Combined view -- kept for main()'s "are metrics confirmed at all" guard and any caller
# that just wants the full label->code map without caring which periodicity group a
# label belongs to.
FUNDAMENTALS_METRICS: dict[str, str] = {**BALANCE_SHEET_METRICS, **FLOW_METRICS}

BALANCE_SHEET_PERIODICITY = "QTR"   # unchanged by fix 4 -- point-in-time snapshot, correct as-is
# LTM (trailing twelve months), not QTR, for FLOW_METRICS only (RIS5 A3 fix 4 -- see
# module docstring for the understated-margin incident this fixes). Confirmed a valid
# enum value on this session's own FactSet_Fundamentals tool schema fetch (not guessed):
# ANN, ANN_R, QTR, QTR_R, SEMI, SEMI_R, LTM, LTM_R, LTMSG, LTM_SEMI, LTM_SEMI_R, YTD. The
# tool's own "QTR -> SEMI -> ANN" fallback ladder only applies when periodicity is
# UNSPECIFIED ("User does NOT specify a periodicity... you MUST execute this fallback
# sequence") -- this module always specifies a periodicity explicitly, so that ladder is
# never in play; FUNDAMENTALS_FALLBACK below is not an LTM fallback, just the ANN-ladder
# order retained for reference in case a name ever has no LTM coverage and a future
# session wants to add one.
FLOW_PERIODICITY = "LTM"
FUNDAMENTALS_PERIODICITY = FLOW_PERIODICITY   # back-compat default (see make_fundamentals_runner)
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
    requestId + metric code (`metric`/`metricCode`, defensive over both spellings) + value.

    `fiscal_end` FIX (RIS5 A3 fix 4, found while testing the period-match logic in
    compute_fcf_margin_rows): the real raw-row field is `fiscalEndDate` (confirmed live,
    this task's own earlier 3-id probe: {"metric": "FF_NET_DEBT", "periodicity": "QTR",
    "fiscalPeriod": 2, "fiscalYear": 2026, "fiscalPeriodLength": 91, "fiscalEndDate":
    "2026-07-31", "reportDate": "2026-07-26", "epsReportDate": "2026-08-26", ...}) --
    `fiscalPeriodEnd` (the guessed key this function used to read) does not exist on any
    real row, so `fiscal_end` was silently `None` on every fundamentals row ever written,
    including the live full-universe pulls before this fix. This went unnoticed until
    fix 4's compute_fcf_margin_rows started actually COMPARING fiscal_end between two
    rows -- None == None trivially "matched" without verifying anything. `date` is now
    `reportDate` (when the figure was reported) with `fiscalEndDate` as a fallback,
    matching the same reportDate/fiscalEndDate distinction the raw payload itself makes."""
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
        fiscal_end = r.get("fiscalEndDate") or r.get("fiscalPeriodEnd") or r.get("date")
        out.append({
            "ticker": tk, "fsym": fid, "date": r.get("reportDate") or fiscal_end,
            "metric": label, "value": value, "periodicity": periodicity,
            "fiscal_end": fiscal_end,
            "currency": r.get("currency"),
            "quality": "ok" if value is not None else "fail:missing",
        })
    return out


def compute_fcf_margin_rows(rows: list[dict]) -> list[dict]:
    """RIS5 A3 fix 4: derives one `fcf_margin` row per ticker from that SAME ticker's
    `fcf` and `sales` rows (both already normalized by normalize_fundamentals_rows,
    both pulled in the same FactSet_Fundamentals call at the same periodicity) --
    NEVER from a different source's SALES figure, which is exactly the QTR-fcf-vs-ANN-
    sales mismatch that understated margins ~4x. Matched by (ticker, fiscal_end): a
    ticker whose `fcf` and `sales` rows disagree on `fiscal_end` (should not happen from
    a single call, but defensively checked rather than assumed) gets
    `fail:period_mismatch` instead of a silently-wrong ratio. Returns ONLY the derived
    `fcf_margin` rows -- callers append these to the rows list passed in, they are not
    replacing anything.

    Value convention matches `gross_margin`/`operating_margin` (already FactSet
    percentages, e.g. NVDA gross_margin ~74.98): `fcf_margin` is `fcf / sales * 100`,
    a percentage, not a 0-1 fraction."""
    by_ticker: dict[str, dict[str, dict]] = {}
    for r in rows:
        if r["metric"] in ("fcf", "sales"):
            by_ticker.setdefault(r["ticker"], {})[r["metric"]] = r

    out = []
    for tk, legs in sorted(by_ticker.items()):
        fcf_row, sales_row = legs.get("fcf"), legs.get("sales")
        if fcf_row is None or sales_row is None:
            continue   # one leg never came back for this ticker -- nothing to derive
        base = {"ticker": tk, "fsym": fcf_row.get("fsym"), "metric": "fcf_margin",
               "periodicity": fcf_row.get("periodicity"), "currency": fcf_row.get("currency")}
        if fcf_row["quality"] != "ok" or sales_row["quality"] != "ok":
            out.append({**base, "date": fcf_row.get("date"), "value": None,
                       "fiscal_end": fcf_row.get("fiscal_end"), "quality": "fail:missing"})
            continue
        if fcf_row.get("fiscal_end") != sales_row.get("fiscal_end"):
            out.append({**base, "date": fcf_row.get("date"), "value": None,
                       "fiscal_end": fcf_row.get("fiscal_end"), "quality": "fail:period_mismatch"})
            continue
        sales_value = sales_row["value"]
        if not isinstance(sales_value, (int, float)) or sales_value <= 0:
            out.append({**base, "date": fcf_row.get("date"), "value": None,
                       "fiscal_end": fcf_row.get("fiscal_end"), "quality": "fail:sales<=0"})
            continue
        margin = (fcf_row["value"] / sales_value) * 100.0
        out.append({**base, "date": fcf_row.get("date"), "value": margin,
                   "fiscal_end": fcf_row.get("fiscal_end"), "quality": "ok"})
    return out


# ---------------------------------------------------------------------------
# Orchestration (RIS5 A3 fix 5): the weekly full-universe pull, exactly as the ad-hoc
# live drivers did it (fix 4's /tmp/a3_fundamentals_ltm.py + a3_fundamentals_balance.py)
# but now a committed, tested CLI instead of a throwaway script.
# ---------------------------------------------------------------------------
def fetch_fundamentals_group(pairs: list[tuple[str, str]], codes: list[str],
                             code_to_label: dict, periodicity: str, runner, log=print,
                             retry_wait: int = RETRY_WAIT_SECONDS, sleep=time.sleep,
                             batch: int = FUNDAMENTALS_BATCH) -> tuple[list[dict], list[dict]]:
    """-> (normalized_rows, batch_errors). Same shape/conventions as snapshot.py's
    fetch_prices/fetch_market_value/fetch_consensus: batches ids at `batch` (<=250, the
    tool's own documented max), retries a 408/5xx ONCE per batch via `_retry_once`
    (never a second retry), and lets SessionLimitError propagate uncaught -- the caller
    (main()) aborts the whole run on it rather than logging-and-continuing."""
    fid_to_ticker = {fid: tk for tk, fid in pairs}
    out: list[dict] = []
    errors: list[dict] = []
    for chunk in id_chunks(pairs, batch):
        fids = [fid for _, fid in chunk]
        rows, err = _retry_once(lambda: runner(fids, codes, periodicity), fids,
                                f"fundamentals[{periodicity}]", log, retry_wait, sleep)
        if err:
            log(f"FAIL fundamentals[{periodicity}] {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "periodicity": periodicity, "error": err})
            continue
        out.extend(normalize_fundamentals_rows(rows, fid_to_ticker, code_to_label, periodicity))
        log(f"ok fundamentals[{periodicity}] {len(fids)}ids -> {len(rows)} rows")
    return out, errors


def _dry_run_plan(pairs: list[tuple[str, str]], log=print) -> None:
    """Prints the calls that WOULD be made -- no claude -p spawned, nothing written."""
    for group_name, metrics, periodicity in (
        ("balance_sheet", BALANCE_SHEET_METRICS, BALANCE_SHEET_PERIODICITY),
        ("flow", FLOW_METRICS, FLOW_PERIODICITY),
    ):
        codes = list(metrics.values())
        chunks = id_chunks(pairs, FUNDAMENTALS_BATCH)
        log(f"  [{group_name}] periodicity={periodicity} ids={len(pairs)} "
           f"metrics={codes} batches={len(chunks)} (<= {FUNDAMENTALS_BATCH} ids/batch)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the planned calls, spawn no claude -p, write nothing")
    ap.add_argument("--state-dir", default=None, help="override state/valuation/ (tests/smoke)")
    ap.add_argument("--out", default=None, help="exact output file path (overrides --state-dir/date naming)")
    ap.add_argument("--date", default=None, help="override as_of date (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    if not FUNDAMENTALS_METRICS:
        print("FUNDAMENTALS_METRICS is empty -- run the FactSet_Metrics probe and hardcode "
             "the confirmed FF_ codes (see module docstring / docs/portal/mcp_schemas.md) "
             "before this CLI can pull live data.", file=sys.stderr)
        return 1

    as_of = args.date or date.today().isoformat()
    state_dir = Path(args.state_dir) if args.state_dir else STATE_DIR
    out_path = Path(args.out) if args.out else state_dir / f"fundamentals_{as_of}.jsonl"

    pairs, skipped = build_universe()
    print(f"universe: {len(pairs)} mapped, {len(skipped)} skipped")
    for s in skipped:
        print(f"  skip {s['id']}: {s['reason']}")

    if args.dry_run:
        print("DRY RUN -- would call FactSet_Fundamentals as follows (no claude -p spawned):")
        _dry_run_plan(pairs)
        return 0

    bs_codes = list(BALANCE_SHEET_METRICS.values())
    bs_code_to_label = {v: k for k, v in BALANCE_SHEET_METRICS.items()}
    flow_codes = list(FLOW_METRICS.values())
    flow_code_to_label = {v: k for k, v in FLOW_METRICS.items()}
    runner = make_fundamentals_runner()

    try:
        bs_rows, bs_errs = fetch_fundamentals_group(
            pairs, bs_codes, bs_code_to_label, BALANCE_SHEET_PERIODICITY, runner)
        flow_rows, flow_errs = fetch_fundamentals_group(
            pairs, flow_codes, flow_code_to_label, FLOW_PERIODICITY, runner)
    except SessionLimitError as e:
        print(f"ABORTED (session limit 429): {e} -- remaining batches skipped, "
             f"nothing written to state/valuation/", file=sys.stderr)
        return 1

    margin_rows = compute_fcf_margin_rows(bs_rows + flow_rows)
    all_rows = bs_rows + flow_rows + margin_rows

    ok = sum(1 for r in all_rows if r["quality"] == "ok")
    print(f"fundamentals: {len(all_rows)} rows ({len(bs_rows)} balance-sheet + "
         f"{len(flow_rows)} flow + {len(margin_rows)} derived fcf_margin), {ok} ok, "
         f"{len(all_rows) - ok} quality-failed, "
         f"{len(bs_errs) + len(flow_errs)} batch errors")

    write_jsonl(all_rows, out_path)
    print(f"written {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
