#!/usr/bin/env python3
"""valuation/snapshot.py — daily FactSet price / market-cap / consensus snapshot (RIS5 A3).

RIS5's ideas engine has price/mcap/consensus scoring assumptions but no producer feeding
them — this is that producer. Weekdays 05:45 ET (staged, not installed — see
docs/portal/cron.txt): pulls same-day price+volume, current market cap, and FY1-FY3
consensus SALES/EPS for the full valuation universe, writes dated raw files, and updates
the tracked `state/valuation/latest.json` rollup the portal/ideas engine reads.

UNIVERSE (task brief): `chunking.ingest_metrics.universe()` (T1+T2) UNION every
`portal.identity.load_universe()` entry whose tier is tier_1/2/3 (adds T3), MINUS `.pvt`
ids and ids `portal.identity.factset_ids()` cannot map to a FactSet id (foreign/digit
tickers with no explicit `ticker_identity.yaml` override — see identity.py's own
docstring). Every dropped id is recorded in `skipped` with a reason; nothing is silently
missing.

TRANSPORT — one `claude -p` per (id-batch, endpoint), never two tool calls folded into one
session. See this package's `__init__.py` docstring for why: `claude_p.tool_use_input()`
returns only the FIRST matching tool_use block, so a two-call session has no working
argument-drift guard, and a session where call 1 lands and call 2 doesn't produces a
structurally-valid PARTIAL result. The task brief's "at most 3 live sessions ... (prices
+market_value, consensus SALES, consensus EPS)" is therefore read as three LOGICAL pull
stages, not a literal subprocess ceiling — at this worktree's real filtered universe
(178 ids mapped 2026-09-17), ≤100-id batching alone needs 2 prices + 2 SALES + 2 EPS
calls before market_value (capped at 25 ids/call as of RIS5 A3 fix 2 -- tightened from 50
after a live 408 Request Timeout on a 50-id batch, see __init__.py) is even counted.

BATCH CAPS come from the live FactSet_GlobalPrices/_EstimatesConsensus tool schemas
(fetched via ToolSearch 2026-09-17), not just the brief's "≤100" gloss — see __init__.py.

RETRY (amendment v1.2 / RIS5 A3 fix 2): a FactSet-server-side 408/5xx on any batch call
(any of prices/market_value/consensus) is retried ONCE after a 20s wait
(RETRY_WAIT_SECONDS), then the batch is marked failed and the run continues — see
`_retry_once`/`_is_retryable_error`. This is a distinct error class from the
session-limit/429 abort below: a 408/5xx is a single flaky request, a 429 drains the
whole subscription quota and is never retried.

CONSENSUS METRICS (amendment v1.2): daily consensus now pulls SALES/EPS/EBITDA/FCF
(FY1-FY3) — EBITDA and FCF are unprefixed FactSet Estimates codes (confirmed live; see
docs/portal/mcp_schemas.md). Weekly (Sunday, `--weekly`): the same four metrics at
FY4-FY5, with counts, merged into the existing daily latest.json via
`merge_weekly_consensus` rather than rebuilding it — see run_weekly().

QUALITY (amendment v1.1): every row gets `quality` = "ok" or "fail:<reason>" from
`check_price_quality`/`check_consensus_quality` (range checks: price>0, count>=1)
and, where a row carries the FactSet surprise-identity trio, `check_surprise_identity`
(surpriseBefore + surpriseAmount == surpriseAfter, tolerance 1e-6). NEITHER endpoint this
module pulls (`prices`, `market_value`, `consensus_rolling`) returns
surpriseBefore/surpriseAmount/surpriseAfter — those three fields are unique to
`estimate_type='surprise'`, which is `scripts/chunking/ingest_metrics.py`'s weekly pull,
not this module's. `check_surprise_identity` is implemented and unit-tested against a
synthetic row (proving the logic), and called from the quality pipeline for completeness/
forward-compat, but on every real row this module writes it is a no-op (fields absent ->
"n/a", never gates on it) — this is reported explicitly, not silently satisfied. `sentiment`
is never read: rows are built by explicit key assignment against the module-constant
schema below, never a dict-splat of the raw FactSet payload.

MCAP QUALITY (RIS5 A3 fix 3, coordinator review, HIGH): `mcap`'s validity is judged
INDEPENDENTLY of `price`'s via `check_mcap_quality` -> `mcap_quality` = "ok" |
"fail:mcap<=0" | "fail:currency_mismatch" | "fail:mcap_scale". The live run showed
SONY/TSM/UMC/ASX/TCEHY with implied share counts (mcap/price) in the 61B-925B range --
physically impossible for any real company -- because `market_value` returns the
security's LOCAL-exchange market cap while `prices` can return a USD ADR quote for the
same ticker; nothing checked that the two legs were even in the same currency. A bad
mcap no longer drops the ticker's price: `build_latest` seats `price` whenever
`quality=="ok"` and independently nulls `mcap` whenever `mcap_quality!="ok"`, recording
why in `summary.mcap_missing` (count) and `skipped_mcap` (per-ticker reasons). FX
conversion is explicitly NOT attempted here (see mcp_schemas.md for a follow-up: the
`FactSet_GlobalPrices` `currency` PARAMETER is documented as usable for `prices` but NOT
for `market_value` -- there is no direct fetch-time fix, only a downstream conversion or
a `shares_outstanding` x price computation, neither built here).

Row schemas (module constants — see PRICE_FIELDS/CONSENSUS_FIELDS):
    prices:     {ticker, fsym, date, price, volume, mcap, price_currency, mcap_currency,
                 quality, mcap_quality}
    consensus:  {ticker, fsym, date, metric, rel_period, fiscal_end, mean, median,
                 count, up, down, quality}

`latest.json` (tracked; the dated raw files are gitignored) is built from price rows with
`quality=="ok"` (price-only gate; see MCAP QUALITY above for why mcap has its own,
independent gate) plus consensus rows with `quality=="ok"`: `{as_of, universe_size,
skipped: [{id, reason}], summary: {priced, consensus_only, mcap_missing},
skipped_mcap: [{ticker, reason}], tickers: {T: {...}}}`. Per ticker: price, mcap (None
when `mcap_quality!="ok"` even though price is fine — fix 3), price_currency,
mcap_currency, fy{1,2,3}_sales, fy{1,2,3}_eps (consensus MEAN), plus nested
`counts`/`up`/`down` dicts keyed by the same "fy1_sales"/"fy2_eps"/... labels — the
brief's flat `counts, up, down` keys are read as per-(metric,period) breakdowns (a single
scalar would not say which of the 6 periods it described); flagged as an interpretive
call. **A ticker can appear with `price: None, mcap: None`** — a consensus row surviving
quality alone (count>=1) is enough to seat a ticker in `tickers` even when its
price/market_value batch failed or that id had no covered price quote; `build_latest`
never requires BOTH legs to be `"ok"` (fix round 1, coordinator review — this is
deliberate, not an oversight: A5 owns null-checking these before doing math on them).
`summary.priced` counts tickers with a real price; `summary.consensus_only` counts
tickers seated only via a consensus row; `summary.mcap_missing` (fix 3) counts PRICED
tickers whose mcap is null for any reason (missing, currency mismatch, or scale) —
`skipped_mcap` names each one with its specific reason.

CLI:
    python3 scripts/valuation/snapshot.py --dry-run                 # fake runner, no claude -p
    python3 scripts/valuation/snapshot.py                            # live daily run
    python3 scripts/valuation/snapshot.py --state-dir /tmp/out       # override for smoke tests
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

REPO = Path("/root/research-watchlist")   # canonical vault root -- READ-ONLY paths only
                                          # (config/watchlist.yaml etc via identity/ingest_metrics).
                                          # NEVER used to resolve sibling imports below -- see the
                                          # RIS5 A2/A4 "REPO trap" precedent (structure_reads.py,
                                          # insider_pull.py docstrings): this worktree's own copy of
                                          # ingest_metrics.py must win over the main checkout's until
                                          # merge, so imports resolve via __file__, not REPO.
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]   # this file's own scripts/ dir
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "lib"))
sys.path.insert(0, str(_SCRIPTS_DIR / "chunking"))
import ingest_metrics                                        # noqa: E402  -- worktree copy first,
                                                              # so portal.identity's own internal
                                                              # `import ingest_metrics` (which inserts
                                                              # REPO/scripts/chunking, the MAIN
                                                              # checkout) hits sys.modules cache
                                                              # instead of re-resolving against main.
import claude_p                                              # noqa: E402
from portal import identity as pid                            # noqa: E402
from etfflows.factset_flows import _tool_result_blocks, resolve_payload, rows_of  # noqa: E402
from newsdigest.classify_llm import _detect_session_limit, SessionLimitError  # noqa: E402

from valuation import (                                       # noqa: E402
    MODEL, PRICE_BATCH, MARKET_VALUE_BATCH, CONSENSUS_BATCH,
    PRICE_TIMEOUT, MARKET_VALUE_TIMEOUT, CONSENSUS_TIMEOUT, RETRY_WAIT_SECONDS,
    CONSENSUS_METRICS, RELATIVE_FISCAL_START, RELATIVE_FISCAL_END, PERIODICITY,
    WEEKLY_CONSENSUS_METRICS, WEEKLY_RELATIVE_FISCAL_START, WEEKLY_RELATIVE_FISCAL_END,
)

ToolUnavailableError = claude_p.ToolUnavailableError

PRICES_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_GlobalPrices"
CONSENSUS_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_EstimatesConsensus"

STATE_DIR = REPO / "state" / "valuation"

PRICE_FIELDS = ("ticker", "fsym", "date", "price", "volume", "mcap",
                "price_currency", "mcap_currency", "quality", "mcap_quality")
CONSENSUS_FIELDS = ("ticker", "fsym", "date", "metric", "rel_period", "fiscal_end",
                    "mean", "median", "count", "up", "down", "quality")


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------
def build_universe(watchlist_path=None, notes_dir=None) -> tuple[list[tuple[str, str]], list[dict]]:
    """-> ([(ticker, fsym_id), ...] mapped, [{"id": ticker, "reason": ...}, ...] skipped).

    Union of ingest_metrics.universe() (T1+T2) and every tier_1/2/3 entry from
    identity.load_universe() (adds T3); `.pvt` ids and ids identity.factset_ids()
    cannot map are skipped with a reason, never silently dropped.
    """
    t12 = set(ingest_metrics.universe())
    for e in pid.load_universe(watchlist_path, notes_dir):
        if e.get("tier") in ("tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist"):
            t12.add(e["ticker"])
    tickers = sorted(t12)
    fids = pid.factset_ids(tickers, watchlist_path, notes_dir)

    mapped: list[tuple[str, str]] = []
    skipped: list[dict] = []
    for tk in tickers:
        if tk.endswith(".pvt"):
            skipped.append({"id": tk, "reason": "pvt"})
            continue
        fid = fids.get(tk)
        if not fid:
            skipped.append({"id": tk, "reason": "no factset mapping"})
            continue
        mapped.append((tk, fid))
    return mapped, skipped


def id_chunks(pairs: list[tuple[str, str]], size: int) -> list[list[tuple[str, str]]]:
    return [pairs[i:i + size] for i in range(0, len(pairs), size)]


# ---------------------------------------------------------------------------
# Argument-drift guard (copied convention: scripts/v3_ingest/transcript_ingest.py
# argument_drift/_arg_norm -- kept local per the repo's "copy small transport
# helpers rather than cross-import" convention, see factset_flows._claude_env)
# ---------------------------------------------------------------------------
def _arg_norm(v):
    if isinstance(v, (list, tuple)):
        return sorted(str(x) for x in v)
    # Python None (an expected arg value, e.g. fundamentals.py's audit=None meaning
    # "omit auditing") and the literal string "null" (how the live FactSet_Fundamentals
    # call actually placed it, per RIS5 A3's live 3-id probe -- claude_p.tool_use_input's
    # extracted args dict held {"audit": "null"}, not JSON null) must compare equal, or
    # every real Fundamentals call would false-positive as argument drift on `audit`
    # alone. Confirmed this is the ONLY None-valued expected arg anywhere in this module.
    if v is None or (isinstance(v, str) and v.lower() == "null"):
        return "null"
    return str(v)


def argument_drift(placed: dict | None, expected: dict) -> list[str]:
    """Names of expected arguments the model did not place as given (or placed at all)."""
    if placed is None:
        return ["<no tool_use>"]
    bad = []
    for k, want in expected.items():
        if k not in placed or _arg_norm(placed[k]) != _arg_norm(want):
            bad.append(k)
    return bad


# ---------------------------------------------------------------------------
# Transport: prices
# ---------------------------------------------------------------------------
def _prices_args(fids: list[str], on_date: str) -> dict:
    return {"ids": fids, "data_type": "prices", "startDate": on_date, "endDate": on_date,
           "fields": ["price", "volume"]}


def _prices_prompt(fids: list[str], on_date: str) -> str:
    a = _prices_args(fids, on_date)
    return (
        "Call the FactSet_GlobalPrices tool EXACTLY ONCE with these arguments:\n"
        f"  ids: {json.dumps(a['ids'])}\n"
        f"  data_type: '{a['data_type']}'\n"
        f"  startDate: '{a['startDate']}'\n"
        f"  endDate: '{a['endDate']}'\n"
        f"  fields: {json.dumps(a['fields'])}\n"
        "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different "
        "arguments.\n\nThen reply with the single word DONE. Do NOT summarise, quote, "
        "reformat or repeat any of the data — it is read directly from the tool output, "
        "not from your reply."
    )


def _market_value_args(fids: list[str]) -> dict:
    return {"ids": fids, "data_type": "market_value"}


def _market_value_prompt(fids: list[str]) -> str:
    a = _market_value_args(fids)
    return (
        "Call the FactSet_GlobalPrices tool EXACTLY ONCE with these arguments:\n"
        f"  ids: {json.dumps(a['ids'])}\n"
        f"  data_type: '{a['data_type']}'\n"
        "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different "
        "arguments.\n\nThen reply with the single word DONE. Do NOT summarise, quote, "
        "reformat or repeat any of the data — it is read directly from the tool output, "
        "not from your reply."
    )


def _consensus_args(fids: list[str], metric: str, rel_start: int = RELATIVE_FISCAL_START,
                    rel_end: int = RELATIVE_FISCAL_END) -> dict:
    return {"ids": fids, "estimate_type": "consensus_rolling", "metrics": [metric],
           "periodicity": PERIODICITY, "relativeFiscalStart": rel_start,
           "relativeFiscalEnd": rel_end}


def _consensus_prompt(fids: list[str], metric: str, rel_start: int = RELATIVE_FISCAL_START,
                      rel_end: int = RELATIVE_FISCAL_END) -> str:
    a = _consensus_args(fids, metric, rel_start, rel_end)
    return (
        "Call the FactSet_EstimatesConsensus tool EXACTLY ONCE with these arguments:\n"
        f"  ids: {json.dumps(a['ids'])}\n"
        f"  estimate_type: '{a['estimate_type']}'\n"
        f"  metrics: {json.dumps(a['metrics'])}\n"
        f"  periodicity: '{a['periodicity']}'\n"
        f"  relativeFiscalStart: {a['relativeFiscalStart']}\n"
        f"  relativeFiscalEnd: {a['relativeFiscalEnd']}\n"
        "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different "
        "arguments.\n\nThen reply with the single word DONE. Do NOT summarise, quote, "
        "reformat or repeat any of the data — it is read directly from the tool output, "
        "not from your reply."
    )


# ---------------------------------------------------------------------------
# 408/5xx retry (RIS5 A3 fix 2, coordinator ruling): a FactSet-server-side
# timeout or server error on any batch -- observed live as httpx's own
# raise_for_status string, "Client error '408 Request Timeout' for url ..." or
# "Server error '502 Bad Gateway' for url ..." -- is retried ONCE after a wait,
# then the batch is marked failed and the run continues. This is a DIFFERENT
# error class from SessionLimitError (429/session-limit): that one is
# non-retryable and aborts the whole run; this one is a single flaky request.
# ---------------------------------------------------------------------------
_HTTP_STATUS_RE = re.compile(r"error '(\d{3})", re.IGNORECASE)
_RETRYABLE_STATUS_RE = re.compile(r"http_status=(408|5\d{2})\b")


def _extract_http_status(text: str) -> str | None:
    """Scans the FULL (untruncated) response text for httpx's own error-string shape,
    not the tail-truncated error message a caller might log -- truncating first and
    pattern-matching after would risk cutting the status code out of the visible window
    on a longer payload."""
    m = _HTTP_STATUS_RE.search(text or "")
    return m.group(1) if m else None


def _is_retryable_error(err: str | None) -> bool:
    """True only for an explicit 'http_status=408' or 'http_status=5xx' marker placed by
    _run_and_parse below -- never a bare digit match against the error string (a price,
    volume or row count could easily contain '500' or '408' and would false-positive)."""
    return bool(err) and bool(_RETRYABLE_STATUS_RE.search(err))


def _run_mcp_checked(prompt: str, tool: str, model, cwd, timeout: int) -> str:
    """Same transport as claude_p.run_mcp, plus a subscription-429 precheck claude_p.run_mcp
    itself doesn't have (fix round 1, coordinator review). claude_p.run() takes a
    `precheck=` callback specifically so a 429 (which can arrive with rc!=0 AND with the
    session-limit text on stdout, not stderr -- see claude_p.py's own module docstring:
    "Auth/usage errors land on STDOUT") is checked BEFORE the returncode; claude_p.run_mcp()
    has no such hook, so without this wrapper a 429 here would surface as an indistinct
    RuntimeError from run_mcp's own rc!=0 branch (which only captures truncated STDERR --
    the actual session-limit text would never even be seen) and get silently caught into
    the ordinary per-batch (rows, error) tuple downstream, logged-and-continued like any
    other transport hiccup, and burn the rest of a drained quota on doomed retries across
    the remaining batches. Duplicates claude_p.run_mcp's body deliberately (repo convention:
    copy small transport helpers rather than grow a cross-module dependency, e.g.
    factset_flows._claude_env) rather than changing the shared claude_p.py."""
    cmd = claude_p.build_cmd(prompt, mcp_tool=tool, system_prompt=claude_p.MCP_SYSTEM_PROMPT,
                             model=model)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                            cwd=cwd, env=claude_p.claude_env())
    hint = _detect_session_limit(result.stdout)
    if hint is not None:
        raise SessionLimitError(hint)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} "
                           f"stderr={(result.stderr or '').strip()[:200]!r}")
    stdout = result.stdout or ""
    if not claude_p.tool_was_called(stdout, tool):
        raise ToolUnavailableError(
            f"no {tool.rsplit('__', 1)[-1]} tool_use in transcript — the tool was never "
            f"called: {stdout.strip()[-200:]}")
    return stdout


def _run_and_parse(prompt: str, tool: str, expected_args: dict, repo_root, timeout: int) -> tuple[list[dict], str | None]:
    """-> (rows, error). error is None on success; a drift/unusable-payload/transport error
    is reported and rows is []. Never raises for a single call EXCEPT SessionLimitError
    (fix round 1, coordinator review): a subscription 429 is non-retryable and
    non-splittable (see newsdigest/classify_llm.py's own SessionLimitError docstring for
    the 2026-07-20 storming incident that established this), so it propagates uncaught
    here and the caller (fetch_prices/fetch_market_value/fetch_consensus, then main())
    aborts the whole run rather than logging-and-continuing like an ordinary transport
    error."""
    try:
        stdout = _run_mcp_checked(prompt, tool, MODEL, str(repo_root), timeout)
    except SessionLimitError:
        raise
    except (ToolUnavailableError, RuntimeError) as e:
        return [], f"transport: {type(e).__name__}: {str(e)[:160]}"

    placed = claude_p.tool_use_input(stdout, tool)
    drift = argument_drift(placed, expected_args)
    if drift:
        shown = {k: (placed or {}).get(k) for k in drift}
        return [], f"argument drift in {', '.join(drift)}: placed {shown!r}"

    blocks = _tool_result_blocks(stdout)
    for text in reversed(blocks):
        rows = rows_of(resolve_payload(text))
        if rows is not None:
            return [r for r in rows if isinstance(r, dict)], None
    full_text = (blocks or [stdout])[-1]
    status = _extract_http_status(full_text)
    tail = full_text[-200:]
    if status:
        return [], f"tool_result unusable (http_status={status}): {tail}"
    return [], f"tool_result unusable: {tail}"


def make_prices_runner(repo_root=REPO, timeout=PRICE_TIMEOUT):
    def run(fids: list[str], on_date: str):
        return _run_and_parse(_prices_prompt(fids, on_date), PRICES_TOOL,
                              _prices_args(fids, on_date), repo_root, timeout)
    return run


def make_market_value_runner(repo_root=REPO, timeout=MARKET_VALUE_TIMEOUT):
    def run(fids: list[str]):
        return _run_and_parse(_market_value_prompt(fids), PRICES_TOOL,
                              _market_value_args(fids), repo_root, timeout)
    return run


def make_consensus_runner(repo_root=REPO, timeout=CONSENSUS_TIMEOUT,
                          rel_start: int = RELATIVE_FISCAL_START,
                          rel_end: int = RELATIVE_FISCAL_END):
    def run(fids: list[str], metric: str):
        return _run_and_parse(_consensus_prompt(fids, metric, rel_start, rel_end), CONSENSUS_TOOL,
                              _consensus_args(fids, metric, rel_start, rel_end), repo_root, timeout)
    return run


# ---------------------------------------------------------------------------
# Quality checks (amendment v1.1)
# ---------------------------------------------------------------------------
def check_surprise_identity(row: dict, tol: float = 1e-6) -> str:
    """"ok" | "n/a" | "fail:surprise_identity". "n/a" when the row carries none of the
    three surprise fields (the case for every row this module actually writes -- see
    module docstring); the check only gates a row that HAS all three and disagrees."""
    keys = ("surpriseBefore", "surpriseAmount", "surpriseAfter")
    if not all(k in row for k in keys):
        return "n/a"
    try:
        before, amount, after = (float(row[k]) for k in keys)
    except (TypeError, ValueError):
        return "fail:surprise_identity"
    return "ok" if abs((before + amount) - after) <= tol else "fail:surprise_identity"


def check_price_quality(price) -> str:
    """PRICE-only gate (RIS5 A3 fix 3, coordinator review): used to decide whether a
    ticker seats AT ALL. mcap validity is now judged INDEPENDENTLY by
    check_mcap_quality() -- a currency-mismatched or scale-impossible mcap must not drop
    a perfectly good price (see that function's docstring for why)."""
    if not isinstance(price, (int, float)) or price <= 0:
        return "fail:price<=0"
    return "ok"


# `currentMarketValue` is reported in MILLIONS of the row's currency (RIS5 A3 fix 3
# round 2, coordinator review) -- confirmed by reconciling 6 well-known USD names'
# implied share counts (mcap/price) against their real, public share counts, computed
# from the live rows already on disk (state/valuation/prices_2026-09-17.jsonl) with NO
# further FactSet calls:
#   ticker  raw mcap        price    implied_shares(raw)   x1e6 -> real shares   actual (~)
#   NVDA    5,154,990.0     219.34   23,502.28              23.50B                ~24.3B
#   AAPL    4,851,251.4     337.00   14,395.40              14.40B                ~14.8B
#   MSFT    3,640,745.0     497.75    7,314.40               7.31B                ~7.43B
#   WMT       852,877.7     106.79    7,986.49               7.99B                ~8.0B
#   ZS         31,238.0     197.47      158.19               0.158B               ~0.15B
#   COHR       56,777.6     295.98      191.83               0.192B               ~0.16B
# Every one lands in the right ballpark ONLY after multiplying the raw value by 1e6 --
# this also matches the tool's own schema text ("market_value=current market cap,
# millions") and the independent "factor": "1000000" FactSet_Metrics reported for the
# analogous FF_NET_DEBT/FF_DEBT/FF_CASH_GENERIC fundamentals metrics (docs/portal/
# mcp_schemas.md).
#
# CRITICAL: this multiplier is used ONLY inside check_mcap_quality's implied-share-count
# arithmetic, to compare against a RAW share-count threshold. The `mcap` value actually
# PERSISTED in the dated file / latest.json is deliberately left UNSCALED (still in
# millions) -- `scripts/valuation/expectations.py`'s `_entry_ev()` computes
# `ev = entry["mcap"] + net_debt`, and `net_debt` (FactSet_Fundamentals' FF_NET_DEBT,
# `fundamentals_<date>.jsonl`) is ALSO natively in millions with no rescaling applied
# anywhere in this codebase (confirmed: fundamentals.py's normalize_fundamentals_rows
# stores `r.get("value")` verbatim) -- as are the consensus SALES/EBITDA/FCF figures
# this module itself writes. Multiplying only mcap to raw dollars would silently break
# every downstream EV/multiple computation by 6 orders of magnitude. Scaling the STORED
# mcap is explicitly OUT of scope for this fix.
MCAP_UNIT_MULTIPLIER = 1_000_000

# implied shares outstanding = (mcap * MCAP_UNIT_MULTIPLIER) / price must fall in this
# range for ANY real public company (1e6 = a micro-cap with a low share count; 5e10 =
# above the largest real share counts seen, e.g. mega-caps with ~1-2e10 shares after
# splits) -- an implied share count outside this band is not a valuation signal, it is
# proof mcap and price are not denominated in the same currency (or otherwise not
# comparable).
MCAP_IMPLIED_SHARES_MIN = 1e6
MCAP_IMPLIED_SHARES_MAX = 5e10


def check_mcap_quality(mcap, price, price_currency, mcap_currency) -> str:
    """"ok" | "fail:mcap<=0" | "fail:currency_mismatch" | "fail:mcap_scale".

    RIS5 A3 fix 3 (coordinator review, HIGH): the live run's market_value pull returns
    the security's LOCAL-exchange market cap while `prices` can return an ADR's USD
    quote -- SONY/TSM/UMC/ASX/TCEHY all showed a currency mismatch (caught below) and,
    separately, EVERY OTHER ticker in the universe initially showed a physically
    impossible implied share count too, because `mcap` is reported in MILLIONS
    (see MCAP_UNIT_MULTIPLIER above) and the very first version of this check divided
    the raw (unscaled) mcap by price directly -- comparing a "thousands of millions of
    shares" figure against a threshold calibrated for raw share counts. Fixed by scaling
    mcap up by MCAP_UNIT_MULTIPLIER for this comparison ONLY (the persisted `mcap` field
    itself stays in millions -- see the constant's own docstring for why). This whole
    function is INDEPENDENT of check_price_quality: a ticker whose mcap fails here still
    seats with a real price in latest.json, just with mcap: null (see build_latest) -- a
    bad mcap must never take a good price down with it.

    Order: missing/non-positive mcap first (can't evaluate anything else about it), then
    a currency mismatch (cheap, decisive -- no need for the price to even be valid), then
    the implied-share-count scale check (needs a valid price to divide by; skipped,
    not failed, when price itself is unusable -- check_price_quality already keeps such
    a row out of latest.json entirely, so the scale verdict here is moot but still
    honestly "ok" rather than a manufactured failure)."""
    if not isinstance(mcap, (int, float)) or mcap <= 0:
        return "fail:mcap<=0"
    if price_currency and mcap_currency and price_currency != mcap_currency:
        return "fail:currency_mismatch"
    if isinstance(price, (int, float)) and price > 0:
        implied_shares = (mcap * MCAP_UNIT_MULTIPLIER) / price
        if not (MCAP_IMPLIED_SHARES_MIN <= implied_shares <= MCAP_IMPLIED_SHARES_MAX):
            return "fail:mcap_scale"
    return "ok"


def check_consensus_quality(count) -> str:
    if not isinstance(count, (int, float)) or count < 1:
        return "fail:count<1"
    return "ok"


# ---------------------------------------------------------------------------
# Normalize + join
# ---------------------------------------------------------------------------
def _num(v):
    return v if isinstance(v, (int, float)) else None


def normalize_price_rows(raw: list[dict], fid_to_ticker: dict) -> dict[str, dict]:
    """{ticker: {price, volume, currency, date}} -- last row wins per ticker (single-day
    pull, so normally exactly one)."""
    out: dict[str, dict] = {}
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        out[tk] = {"fsym": fid, "date": r.get("date"), "price": _num(r.get("price")),
                  "volume": _num(r.get("volume")), "currency": r.get("currency")}
    return out


# Candidate key names for the market_value row's cap field. CONFIRMED live 2026-09-17
# (RIS5 A3 live run): the real key is `currentMarketValue` -- none of the pre-live guesses
# matched (raw row: {"fsymId": "SZG8SG-R", "requestId": "000660-KR",
# "currentMarketValue": 1240826747.5, "currency": "KRW", "date": "2026-09-17"}). The
# guessed keys are kept as a defensive fallback (harmless if FactSet ever adds one of
# them) but `currentMarketValue` is tried first. See docs/portal/mcp_schemas.md.
_MCAP_KEYS = ("currentMarketValue", "marketValue", "mktVal", "market_value", "mcap", "value")


def normalize_market_value_rows(raw: list[dict], fid_to_ticker: dict, log=print) -> dict[str, dict]:
    """{ticker: {mcap, currency, date}}. `currency` (RIS5 A3 fix 3) is the market_value
    row's OWN currency -- confirmed present live alongside `currentMarketValue`
    (`{"currentMarketValue": ..., "currency": "KRW", ...}`) even though the tool schema
    marks the request-side `currency` PARAMETER "NOT USED" for this data_type; that note
    is about the request, not the response. This is the local-exchange currency, which
    for an ADR ticker can differ from `prices`' own currency -- see check_mcap_quality.

    LOW (coordinator review): logs a WARNING via `log` when a FALLBACK key (anything
    after `_MCAP_KEYS[0]`) is used, since that would mean FactSet's response shape
    changed from the confirmed live one and deserves attention, not silent tolerance."""
    out: dict[str, dict] = {}
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        mcap = None
        matched_key = None
        for k in _MCAP_KEYS:
            if isinstance(r.get(k), (int, float)):
                mcap = r[k]
                matched_key = k
                break
        if matched_key is not None and matched_key != _MCAP_KEYS[0]:
            log(f"WARNING: market_value used fallback key {matched_key!r} for id "
               f"{fid!r} instead of the confirmed {_MCAP_KEYS[0]!r} -- FactSet's "
               f"response shape may have changed; see docs/portal/mcp_schemas.md")
        out[tk] = {"mcap": mcap, "currency": r.get("currency"), "date": r.get("date")}
    return out


def build_price_rows(price_by_tk: dict, mcap_by_tk: dict, fid_to_ticker: dict,
                     ticker_to_fid: dict, as_of: str) -> list[dict]:
    """RIS5 A3 fix 3 (coordinator review, HIGH): `price_currency`/`mcap_currency` are now
    carried on every row, and mcap's own validity (`mcap_quality`) is judged
    INDEPENDENTLY of price's (`quality`) -- a currency-mismatched or scale-impossible
    mcap (the SONY/TSM/UMC/ASX/TCEHY incident: local-currency market_value against a
    USD ADR price, implied share counts in the tens/hundreds of billions) no longer
    drops a perfectly good price. See build_latest for how `mcap_quality` gates what
    actually reaches latest.json."""
    rows = []
    for tk, fid in sorted(ticker_to_fid.items()):
        p = price_by_tk.get(tk, {})
        m = mcap_by_tk.get(tk, {})
        price, mcap = p.get("price"), m.get("mcap")
        price_currency, mcap_currency = p.get("currency"), m.get("currency")
        rows.append({
            "ticker": tk, "fsym": fid, "date": p.get("date") or as_of,
            "price": price, "volume": p.get("volume"), "mcap": mcap,
            "price_currency": price_currency, "mcap_currency": mcap_currency,
            "quality": check_price_quality(price),
            "mcap_quality": check_mcap_quality(mcap, price, price_currency, mcap_currency),
        })
    return rows


def normalize_consensus_rows(raw: list[dict], fid_to_ticker: dict, metric: str) -> list[dict]:
    """Every relativePeriod row FactSet returned, quality-checked per row.
    `up`/`down`/`mean`/`median` come straight off the response; a null MEAN (no analysts
    yet for a far-out period) survives as None, never coerced to 0.

    CONFIRMED live 2026-09-17 (RIS5 A3 live run, fix 2 follow-up): the response's analyst
    count field is `estimateCount`, NOT `count` -- a guess baked into the pre-live code
    that made every single row in the first live run fail quality (`fail:count<1`, 2124/
    2124 rows) even though `mean`/`median`/`up`/`down` were all populated with real,
    plausible values. Likewise the per-row date is `estimateDate` (the date the consensus
    snapshot was taken), not `date` -- the raw response has no top-level `date` key at
    all. See docs/portal/mcp_schemas.md for the full confirmed raw-row shape."""
    out = []
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        count = _num(r.get("estimateCount"))
        out.append({
            "ticker": tk, "fsym": fid, "date": r.get("estimateDate"), "metric": metric,
            "rel_period": r.get("relativePeriod"), "fiscal_end": r.get("fiscalEndDate"),
            "mean": _num(r.get("mean")), "median": _num(r.get("median")),
            "count": count, "up": _num(r.get("up")), "down": _num(r.get("down")),
            "quality": check_consensus_quality(count),
        })
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def _retry_once(runner_call, fids: list[str], label: str, log, retry_wait: int, sleep):
    """Calls runner_call() (already bound to its args); on a retryable 408/5xx error,
    waits `retry_wait`s and calls it exactly ONCE more, then returns whatever that second
    call produced (success or the same/another failure) -- never a third attempt. A
    SessionLimitError raised by the runner propagates through untouched (fetch_* callers
    never catch it; main() aborts the whole run on it, per the existing precedent)."""
    rows, err = runner_call()
    if err and _is_retryable_error(err):
        log(f"RETRY {label} {fids[0]}..{fids[-1]} after {retry_wait}s "
           f"(retryable: {err[:100]})")
        sleep(retry_wait)
        rows, err = runner_call()
    return rows, err


def fetch_prices(pairs: list[tuple[str, str]], on_date: str, runner, log=print,
                 retry_wait: int = RETRY_WAIT_SECONDS, sleep=time.sleep) -> tuple[dict, list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: dict[str, dict] = {}
    errors: list[dict] = []
    for chunk in id_chunks(pairs, PRICE_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = _retry_once(lambda: runner(fids, on_date), fids, "prices", log, retry_wait, sleep)
        if err:
            log(f"FAIL prices {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "error": err})
            continue
        out.update(normalize_price_rows(rows, fid_to_tk))
        log(f"ok prices {len(fids)}ids -> {len(rows)} rows")
    return out, errors


def fetch_market_value(pairs: list[tuple[str, str]], runner, log=print,
                       retry_wait: int = RETRY_WAIT_SECONDS, sleep=time.sleep) -> tuple[dict, list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: dict[str, dict] = {}
    errors: list[dict] = []
    for chunk in id_chunks(pairs, MARKET_VALUE_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = _retry_once(lambda: runner(fids), fids, "market_value", log, retry_wait, sleep)
        if err:
            log(f"FAIL market_value {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "error": err})
            continue
        out.update(normalize_market_value_rows(rows, fid_to_tk, log=log))
        log(f"ok market_value {len(fids)}ids -> {len(rows)} rows")
    return out, errors


def fetch_consensus(pairs: list[tuple[str, str]], metric: str, runner, log=print,
                    retry_wait: int = RETRY_WAIT_SECONDS, sleep=time.sleep) -> tuple[list[dict], list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: list[dict] = []
    errors: list[dict] = []
    for chunk in id_chunks(pairs, CONSENSUS_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = _retry_once(lambda: runner(fids, metric), fids, f"consensus {metric}",
                                log, retry_wait, sleep)
        if err:
            log(f"FAIL consensus {metric} {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "metric": metric, "error": err})
            continue
        out.extend(normalize_consensus_rows(rows, fid_to_tk, metric))
        log(f"ok consensus {metric} {len(fids)}ids -> {len(rows)} rows")
    return out, errors


# ---------------------------------------------------------------------------
# latest.json
# ---------------------------------------------------------------------------
_REL_LABEL = {1: "fy1", 2: "fy2", 3: "fy3", 4: "fy4", 5: "fy5"}   # fy4/fy5 = weekly (v1.2)


def build_latest(price_rows: list[dict], consensus_rows: list[dict],
                 universe_size: int, skipped: list[dict], as_of: str) -> dict:
    """RIS5 A3 fix 3 (coordinator review, HIGH): a price row's `mcap_quality` is checked
    INDEPENDENTLY of `quality` (price-only) -- a ticker with a good price but a bad mcap
    (currency mismatch or an impossible implied share count) still seats with a real
    `price` here, just `mcap: None`, instead of losing the whole ticker the way any mcap
    failure used to. `price_currency`/`mcap_currency` are carried through even when mcap
    itself is nulled (so a reader can see WHY mcap is missing without re-reading the
    dated file). `summary.mcap_missing` counts seated (priced) tickers whose mcap ended
    up None for any reason; `skipped_mcap` names each one with its `mcap_quality`
    failure reason."""
    tickers: dict[str, dict] = {}
    mcap_missing: dict[str, str] = {}   # ticker -> reason, built while iterating price_rows
    for r in price_rows:
        if r["quality"] != "ok":
            continue
        mcap_ok = r.get("mcap_quality") == "ok"
        if not mcap_ok:
            mcap_missing[r["ticker"]] = r.get("mcap_quality") or "fail:unknown"
        tickers[r["ticker"]] = {
            "price": r["price"], "mcap": r["mcap"] if mcap_ok else None,
            "price_currency": r.get("price_currency"), "mcap_currency": r.get("mcap_currency"),
            "counts": {}, "up": {}, "down": {},
        }
    for r in consensus_rows:
        if r["quality"] != "ok":
            continue
        label = _REL_LABEL.get(r["rel_period"])
        if not label:
            continue
        key = f"{label}_{r['metric'].lower()}"
        entry = tickers.setdefault(r["ticker"], {"price": None, "mcap": None,
                                                 "price_currency": None, "mcap_currency": None,
                                                 "counts": {}, "up": {}, "down": {}})
        entry[key] = r["mean"]
        entry["counts"][key] = r["count"]
        entry["up"][key] = r["up"]
        entry["down"][key] = r["down"]
    priced = sum(1 for t in tickers.values() if t["price"] is not None)
    consensus_only = len(tickers) - priced
    skipped_mcap = [{"ticker": tk, "reason": reason} for tk, reason in sorted(mcap_missing.items())]
    return {"as_of": as_of, "universe_size": universe_size, "skipped": skipped,
           "summary": {"priced": priced, "consensus_only": consensus_only,
                      "mcap_missing": len(mcap_missing)},
           "skipped_mcap": skipped_mcap,
           "tickers": tickers}


def merge_weekly_consensus(latest: dict, consensus_rows: list[dict], weekly_as_of: str) -> dict:
    """Amendment v1.2 weekly path: folds FY4/FY5 consensus rows into an EXISTING
    latest.json (as produced by build_latest for the daily FY1-FY3 run) in place, using
    the identical nested metric/rel_period shape (`fy4_sales`/`fy5_ebitda`/... +
    counts/up/down) -- never rebuilding price/mcap/fy1-3 fields, which this function does
    not touch. A ticker with FY4/FY5 coverage but no daily entry yet (rare: weekly
    consensus exists but the ticker never seated via the daily price/FY1-3 run) gets a
    consensus-only entry created the same way build_latest does. Adds
    `weekly_as_of` (the date the weekly pull ran) alongside the daily `as_of` rather than
    overwriting it -- the two runs answer different questions ("when was this priced" vs
    "when was FY4/FY5 last refreshed")."""
    tickers = latest.setdefault("tickers", {})
    for r in consensus_rows:
        if r["quality"] != "ok":
            continue
        label = _REL_LABEL.get(r["rel_period"])
        if not label:
            continue
        key = f"{label}_{r['metric'].lower()}"
        entry = tickers.setdefault(r["ticker"], {"price": None, "mcap": None,
                                                 "price_currency": None, "mcap_currency": None,
                                                 "counts": {}, "up": {}, "down": {}})
        entry[key] = r["mean"]
        entry.setdefault("counts", {})[key] = r["count"]
        entry.setdefault("up", {})[key] = r["up"]
        entry.setdefault("down", {})[key] = r["down"]
    latest["weekly_as_of"] = weekly_as_of
    return latest


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def write_jsonl(rows: list[dict], path: Path) -> None:
    """Overwrite (not append) -- re-running the same day for the same universe/data is
    idempotent. Atomic via a sibling temp file + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".valuation-", suffix=".tmp", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".valuation-", suffix=".tmp", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, default=str)
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _fake_runners():
    """--dry-run: no claude -p, deterministic fixture data so the CLI is smoke-testable
    without spending quota."""
    def prices(fids, on_date):
        return [{"requestId": f, "date": on_date, "price": 100.0 + i, "volume": 1_000_000,
                 "currency": "USD"} for i, f in enumerate(fids)], None

    def market_value(fids):
        # key/currency match the CONFIRMED live response shape (currentMarketValue +
        # currency); USD here matches the fake prices() below so --dry-run rows are
        # mcap_quality "ok" by default (no synthetic currency mismatch). Value is in
        # FactSet's native MILLIONS convention (RIS5 A3 fix 3 round 2 --
        # MCAP_UNIT_MULTIPLIER), e.g. 500_000.0 = $500B against the ~100-178 fake prices
        # below -> ~5B implied shares, well inside [MCAP_IMPLIED_SHARES_MIN,
        # MCAP_IMPLIED_SHARES_MAX]. A raw-dollars value here would trip fail:mcap_scale
        # on every dry-run row.
        return [{"requestId": f, "currentMarketValue": (500_000.0 + i * 10),
                "currency": "USD"} for i, f in enumerate(fids)], None

    def consensus(fids, metric):
        rows = []
        for f in fids:
            for rp in (1, 2, 3):
                # keys match the CONFIRMED live response shape (estimateCount/estimateDate,
                # not count/date -- see normalize_consensus_rows' docstring for why that
                # distinction matters).
                rows.append({"requestId": f, "estimateDate": "2026-09-17", "relativePeriod": rp,
                            "fiscalEndDate": f"202{6+rp}-12-31", "mean": 1000.0 * rp,
                            "median": 990.0 * rp, "estimateCount": 10, "up": 3, "down": 1})
        return rows, None
    return prices, market_value, consensus


def run_weekly(pairs: list[tuple[str, str]], as_of: str, state_dir: Path,
              consensus_runner, log=print) -> int:
    """Amendment v1.2 weekly path: FY4-FY5 for WEEKLY_CONSENSUS_METRICS (the same four
    metrics as the daily pull), with counts. Reads the existing (daily-written)
    latest.json, merges in the FY4/FY5 fields via merge_weekly_consensus (never touching
    price/mcap/fy1-3), and writes both the dated raw file and the updated latest.json
    back. Refuses (exit 1, writes nothing) if no daily latest.json exists yet -- FY4/FY5
    alone, with no FY1-3/price anchor, is not something the ideas engine has ever been
    asked to consume standalone."""
    latest_path = state_dir / "latest.json"
    if not latest_path.exists():
        print(f"no {latest_path} to merge into -- run the daily snapshot first", file=sys.stderr)
        return 1
    latest = json.loads(latest_path.read_text(encoding="utf-8"))

    try:
        consensus_rows: list[dict] = []
        consensus_errs: list[dict] = []
        for metric in WEEKLY_CONSENSUS_METRICS:
            rows, errs = fetch_consensus(pairs, metric, consensus_runner, log=log)
            consensus_rows.extend(rows)
            consensus_errs.extend(errs)
    except SessionLimitError as e:
        print(f"ABORTED (session limit 429): {e} -- remaining batches skipped, "
             f"nothing written to state/valuation/", file=sys.stderr)
        return 1

    ok_cons = sum(1 for r in consensus_rows if r["quality"] == "ok")
    fail_cons = len(consensus_rows) - ok_cons
    print(f"weekly consensus (FY4-FY5): {ok_cons} ok, {fail_cons} quality-failed, "
         f"{len(consensus_errs)} batch errors")

    write_jsonl(consensus_rows, state_dir / f"consensus_weekly_{as_of}.jsonl")
    merge_weekly_consensus(latest, consensus_rows, as_of)
    write_json(latest, latest_path)
    print(f"latest.json updated with weekly FY4-FY5: {len(latest['tickers'])} tickers")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="fake runner, no claude -p, no quota")
    ap.add_argument("--state-dir", default=None, help="override state/valuation/ (tests/smoke)")
    ap.add_argument("--date", default=None, help="override as_of date (YYYY-MM-DD)")
    ap.add_argument("--weekly", action="store_true",
                   help="amendment v1.2: FY4-FY5 consensus only, merged into an existing "
                        "latest.json (Sunday cron; NOT the daily prices+market_value+FY1-3 run)")
    args = ap.parse_args(argv)

    as_of = args.date or date.today().isoformat()
    state_dir = Path(args.state_dir) if args.state_dir else STATE_DIR

    pairs, skipped = build_universe()
    print(f"universe: {len(pairs)} mapped, {len(skipped)} skipped")
    for s in skipped:
        print(f"  skip {s['id']}: {s['reason']}")

    if args.dry_run:
        prices_runner, mv_runner, consensus_runner = _fake_runners()
        weekly_consensus_runner = consensus_runner
    else:
        prices_runner = make_prices_runner()
        mv_runner = make_market_value_runner()
        consensus_runner = make_consensus_runner()
        weekly_consensus_runner = make_consensus_runner(
            rel_start=WEEKLY_RELATIVE_FISCAL_START, rel_end=WEEKLY_RELATIVE_FISCAL_END)

    if args.weekly:
        return run_weekly(pairs, as_of, state_dir, weekly_consensus_runner)

    # A subscription 429 is non-retryable/non-splittable (fix round 1, coordinator review):
    # abort the WHOLE remaining run at the first one and exit non-zero, rather than the
    # ordinary per-batch log-and-continue precedent -- and never write latest.json/the
    # dated raw files from a run that didn't finish (a partial-looking-complete file is
    # worse than no file).
    try:
        price_by_tk, price_errs = fetch_prices(pairs, as_of, prices_runner)
        mcap_by_tk, mv_errs = fetch_market_value(pairs, mv_runner)
        ticker_to_fid = {tk: fid for tk, fid in pairs}
        fid_to_ticker = {fid: tk for tk, fid in pairs}
        price_rows = build_price_rows(price_by_tk, mcap_by_tk, fid_to_ticker, ticker_to_fid, as_of)

        consensus_rows: list[dict] = []
        consensus_errs: list[dict] = []
        for metric in CONSENSUS_METRICS:
            rows, errs = fetch_consensus(pairs, metric, consensus_runner)
            consensus_rows.extend(rows)
            consensus_errs.extend(errs)
    except SessionLimitError as e:
        print(f"ABORTED (session limit 429): {e} -- remaining batches skipped, "
             f"nothing written to state/valuation/", file=sys.stderr)
        return 1

    ok_prices = sum(1 for r in price_rows if r["quality"] == "ok")
    fail_prices = len(price_rows) - ok_prices
    ok_cons = sum(1 for r in consensus_rows if r["quality"] == "ok")
    fail_cons = len(consensus_rows) - ok_cons
    print(f"prices: {ok_prices} ok, {fail_prices} quality-failed, {len(price_errs)} batch errors")
    print(f"consensus: {ok_cons} ok, {fail_cons} quality-failed, {len(consensus_errs)} batch errors")

    write_jsonl(price_rows, state_dir / f"prices_{as_of}.jsonl")
    write_jsonl(consensus_rows, state_dir / f"consensus_{as_of}.jsonl")

    latest = build_latest(price_rows, consensus_rows, len(pairs) + len(skipped), skipped, as_of)
    write_json(latest, state_dir / "latest.json")
    print(f"latest.json: {len(latest['tickers'])} tickers "
         f"(priced={latest['summary']['priced']}, consensus_only={latest['summary']['consensus_only']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
