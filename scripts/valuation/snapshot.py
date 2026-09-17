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
calls before market_value (capped at 50 ids/call, see __init__.py) is even counted.

BATCH CAPS come from the live FactSet_GlobalPrices/_EstimatesConsensus tool schemas
(fetched via ToolSearch 2026-09-17), not just the brief's "≤100" gloss — see __init__.py.

QUALITY (amendment v1.1): every row gets `quality` = "ok" or "fail:<reason>" from
`check_price_quality`/`check_consensus_quality` (range checks: price>0, mcap>0, count>=1)
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

Row schemas (module constants — see PRICE_FIELDS/CONSENSUS_FIELDS):
    prices:     {ticker, fsym, date, price, volume, mcap, currency, quality}
    consensus:  {ticker, fsym, date, metric, rel_period, fiscal_end, mean, median,
                 count, up, down, quality}

`latest.json` (tracked; the dated raw files are gitignored) is built ONLY from
quality=="ok" rows: `{as_of, universe_size, skipped: [{id, reason}], summary: {priced,
consensus_only}, tickers: {T: {...}}}`. Per ticker: price, mcap, fy{1,2,3}_sales,
fy{1,2,3}_eps (consensus MEAN), plus nested `counts`/`up`/`down` dicts keyed by the same
"fy1_sales"/"fy2_eps"/... labels — the brief's flat `counts, up, down` keys are read as
per-(metric,period) breakdowns (a single scalar would not say which of the 6 periods it
described); flagged as an interpretive call. **A ticker can appear with `price: None,
mcap: None`** — a consensus row surviving quality alone (count>=1) is enough to seat a
ticker in `tickers` even when its price/market_value batch failed or that id had no
covered price quote; `build_latest` never requires BOTH legs to be `"ok"` (fix round 1,
coordinator review — this is deliberate, not an oversight: A5 owns null-checking these
before doing math on them). `summary.priced` counts tickers with a real price;
`summary.consensus_only` counts tickers seated only via a consensus row.

CLI:
    python3 scripts/valuation/snapshot.py --dry-run                 # fake runner, no claude -p
    python3 scripts/valuation/snapshot.py                            # live daily run
    python3 scripts/valuation/snapshot.py --state-dir /tmp/out       # override for smoke tests
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
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
    PRICE_TIMEOUT, MARKET_VALUE_TIMEOUT, CONSENSUS_TIMEOUT,
    CONSENSUS_METRICS, RELATIVE_FISCAL_START, RELATIVE_FISCAL_END, PERIODICITY,
)

ToolUnavailableError = claude_p.ToolUnavailableError

PRICES_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_GlobalPrices"
CONSENSUS_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_EstimatesConsensus"

STATE_DIR = REPO / "state" / "valuation"

PRICE_FIELDS = ("ticker", "fsym", "date", "price", "volume", "mcap", "currency", "quality")
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


def _consensus_args(fids: list[str], metric: str) -> dict:
    return {"ids": fids, "estimate_type": "consensus_rolling", "metrics": [metric],
           "periodicity": PERIODICITY, "relativeFiscalStart": RELATIVE_FISCAL_START,
           "relativeFiscalEnd": RELATIVE_FISCAL_END}


def _consensus_prompt(fids: list[str], metric: str) -> str:
    a = _consensus_args(fids, metric)
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
    return [], f"tool_result unusable: {(blocks or [stdout])[-1][-200:]}"


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


def make_consensus_runner(repo_root=REPO, timeout=CONSENSUS_TIMEOUT):
    def run(fids: list[str], metric: str):
        return _run_and_parse(_consensus_prompt(fids, metric), CONSENSUS_TOOL,
                              _consensus_args(fids, metric), repo_root, timeout)
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


def check_price_quality(price, mcap) -> str:
    if not isinstance(price, (int, float)) or price <= 0:
        return "fail:price<=0"
    if not isinstance(mcap, (int, float)) or mcap <= 0:
        return "fail:mcap<=0"
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


# Candidate key names for the market_value row's cap field -- the live schema does not
# document one (fields/currency/calendar are all "fixed schema, NOT USED" for this
# data_type). Tried in order; the first live run pins the real key (see module docstring).
_MCAP_KEYS = ("marketValue", "mktVal", "market_value", "mcap", "value")


def normalize_market_value_rows(raw: list[dict], fid_to_ticker: dict) -> dict[str, dict]:
    """{ticker: {mcap, date}}."""
    out: dict[str, dict] = {}
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        mcap = None
        for k in _MCAP_KEYS:
            if isinstance(r.get(k), (int, float)):
                mcap = r[k]
                break
        out[tk] = {"mcap": mcap, "date": r.get("date")}
    return out


def build_price_rows(price_by_tk: dict, mcap_by_tk: dict, fid_to_ticker: dict,
                     ticker_to_fid: dict, as_of: str) -> list[dict]:
    rows = []
    for tk, fid in sorted(ticker_to_fid.items()):
        p = price_by_tk.get(tk, {})
        m = mcap_by_tk.get(tk, {})
        price, mcap = p.get("price"), m.get("mcap")
        rows.append({
            "ticker": tk, "fsym": fid, "date": p.get("date") or as_of,
            "price": price, "volume": p.get("volume"), "mcap": mcap,
            "currency": p.get("currency"),
            "quality": check_price_quality(price, mcap),
        })
    return rows


def normalize_consensus_rows(raw: list[dict], fid_to_ticker: dict, metric: str) -> list[dict]:
    """Every relativePeriod row FactSet returned, quality-checked per row.
    `count`/`up`/`down`/`mean`/`median` come straight off the response; a null MEAN
    (no analysts yet for a far-out period) survives as None, never coerced to 0."""
    out = []
    for r in raw:
        fid = r.get("requestId")
        tk = fid_to_ticker.get(fid)
        if not tk:
            continue
        count = _num(r.get("count"))
        out.append({
            "ticker": tk, "fsym": fid, "date": r.get("date"), "metric": metric,
            "rel_period": r.get("relativePeriod"), "fiscal_end": r.get("fiscalEndDate"),
            "mean": _num(r.get("mean")), "median": _num(r.get("median")),
            "count": count, "up": _num(r.get("up")), "down": _num(r.get("down")),
            "quality": check_consensus_quality(count),
        })
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def fetch_prices(pairs: list[tuple[str, str]], on_date: str, runner, log=print) -> tuple[dict, list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: dict[str, dict] = {}
    errors: list[dict] = []
    for chunk in id_chunks(pairs, PRICE_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = runner(fids, on_date)
        if err:
            log(f"FAIL prices {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "error": err})
            continue
        out.update(normalize_price_rows(rows, fid_to_tk))
        log(f"ok prices {len(fids)}ids -> {len(rows)} rows")
    return out, errors


def fetch_market_value(pairs: list[tuple[str, str]], runner, log=print) -> tuple[dict, list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: dict[str, dict] = {}
    errors: list[dict] = []
    for chunk in id_chunks(pairs, MARKET_VALUE_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = runner(fids)
        if err:
            log(f"FAIL market_value {fids[0]}..{fids[-1]}: {err}")
            errors.append({"ids": fids, "error": err})
            continue
        out.update(normalize_market_value_rows(rows, fid_to_tk))
        log(f"ok market_value {len(fids)}ids -> {len(rows)} rows")
    return out, errors


def fetch_consensus(pairs: list[tuple[str, str]], metric: str, runner, log=print) -> tuple[list[dict], list[dict]]:
    fid_to_tk = {fid: tk for tk, fid in pairs}
    out: list[dict] = []
    errors: list[dict] = []
    for chunk in id_chunks(pairs, CONSENSUS_BATCH):
        fids = [fid for _, fid in chunk]
        rows, err = runner(fids, metric)
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
_REL_LABEL = {1: "fy1", 2: "fy2", 3: "fy3"}


def build_latest(price_rows: list[dict], consensus_rows: list[dict],
                 universe_size: int, skipped: list[dict], as_of: str) -> dict:
    tickers: dict[str, dict] = {}
    for r in price_rows:
        if r["quality"] != "ok":
            continue
        tickers[r["ticker"]] = {"price": r["price"], "mcap": r["mcap"],
                                "counts": {}, "up": {}, "down": {}}
    for r in consensus_rows:
        if r["quality"] != "ok":
            continue
        label = _REL_LABEL.get(r["rel_period"])
        if not label:
            continue
        key = f"{label}_{r['metric'].lower()}"
        entry = tickers.setdefault(r["ticker"], {"price": None, "mcap": None,
                                                 "counts": {}, "up": {}, "down": {}})
        entry[key] = r["mean"]
        entry["counts"][key] = r["count"]
        entry["up"][key] = r["up"]
        entry["down"][key] = r["down"]
    priced = sum(1 for t in tickers.values() if t["price"] is not None)
    consensus_only = len(tickers) - priced
    return {"as_of": as_of, "universe_size": universe_size, "skipped": skipped,
           "summary": {"priced": priced, "consensus_only": consensus_only},
           "tickers": tickers}


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
        return [{"requestId": f, "marketValue": 50_000.0 + i * 10}
               for i, f in enumerate(fids)], None

    def consensus(fids, metric):
        rows = []
        for f in fids:
            for rp in (1, 2, 3):
                rows.append({"requestId": f, "date": "2026-09-17", "relativePeriod": rp,
                            "fiscalEndDate": f"202{6+rp}-12-31", "mean": 1000.0 * rp,
                            "median": 990.0 * rp, "count": 10, "up": 3, "down": 1})
        return rows, None
    return prices, market_value, consensus


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="fake runner, no claude -p, no quota")
    ap.add_argument("--state-dir", default=None, help="override state/valuation/ (tests/smoke)")
    ap.add_argument("--date", default=None, help="override as_of date (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    as_of = args.date or date.today().isoformat()
    state_dir = Path(args.state_dir) if args.state_dir else STATE_DIR

    pairs, skipped = build_universe()
    print(f"universe: {len(pairs)} mapped, {len(skipped)} skipped")
    for s in skipped:
        print(f"  skip {s['id']}: {s['reason']}")

    if args.dry_run:
        prices_runner, mv_runner, consensus_runner = _fake_runners()
    else:
        prices_runner = make_prices_runner()
        mv_runner = make_market_value_runner()
        consensus_runner = make_consensus_runner()

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
