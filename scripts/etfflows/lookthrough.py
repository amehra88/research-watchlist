"""
lookthrough — Phase 2. Decomposes a crowded ETF into the names it mechanically buys or sells,
sizes that demand against each name's own liquidity, and intersects it with the BCTK book.

THE QUESTION THIS ANSWERS is the operator's: when momentum posts an extreme move, what is
actually driving the stocks, and do we own them? A dollar figure does not answer it —
"$4.1B of implied demand" means nothing without knowing whether that is a rounding error or
three days of the stock's entire volume. So the unit here is DAYS OF ADV.

    implied demand_i = ETF net flow x weight_i
    days of ADV_i    = implied demand_i / (mean daily volume_i x price_i)

CONDITIONAL BY DESIGN. This runs only for ETFs that actually fired a Block-A alert, never as
a daily per-ticker dump. Each run costs holdings + ADV calls, and a decomposition of an
unremarkable flow is noise that trains the reader to skip the section.

THREE LIMITS, ALL LOAD-BEARING — surface them, do not quietly average them away:

1. WEIGHTS ARE MONTH-END. FactSet `fund_holdings` reports as of the last month end (verified:
   SMH returned 2026-07-31). After a sharp move the true weights have drifted, and drift is
   worst exactly when a flow alert fires. Every output carries the weights' as-of date.

2. SYNTHETIC FUNDS ARE EXCLUDED ENTIRELY. DRAM and LYTE are swap/forward backed, so a
   creation does NOT buy the underlying shares. Running look-through on them would invent
   demand that never reaches the tape.

3. MTUM RECONSTITUTES SEMI-ANNUALLY. A rebalance mechanically changes which momentum names
   are bought and will look exactly like a flow event if it is not labelled. Any MTUM
   decomposition near a reconstitution date carries a standing warning.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from typing import NamedTuple, Sequence

from .factset_flows import _claude_env, _extract_json_array, MODEL

_OWNERSHIP_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_Ownership"
_PRICES_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_GlobalPrices"

# FactSet returns market tickers as TICKER-REGION ("NVDA-US", "ASML-US"). The BCTK book and
# the watchlist use bare tickers, so the suffix must come off before anything can be matched.
_REGION_SUFFIX = re.compile(r"-[A-Z]{2}$")

HOLDINGS_TIMEOUT = 180
ADV_TIMEOUT = 180
ADV_WINDOW_DAYS = 30      # calendar days of volume history used for the ADV mean
MAX_ADV_IDS = 50          # GlobalPrices cap for multi-day requests
MAX_NAMES = 20            # constituents carried into the ADV step, by |implied demand|
MIN_WEIGHT_PCT = 0.5      # ignore dust positions — they cannot move a stock


def normalize_ticker(t: str) -> str:
    """'NVDA-US' -> 'NVDA'. Leaves an already-bare ticker untouched.

    Only a trailing two-letter region code is stripped, so genuine hyphenated tickers
    (BF-B, BRK-B) survive.
    """
    return _REGION_SUFFIX.sub("", (t or "").strip().upper())


class Demand(NamedTuple):
    ticker: str
    name: str
    weight_pct: float
    implied_usd: float
    adv_usd: float | None
    days_of_adv: float | None
    in_portfolio: bool
    portfolio_weight: float | None


# ── transports ────────────────────────────────────────────────────────────────

def _run(cmd_prompt: str, tool: str, repo_root, timeout: int):
    result = subprocess.run(
        ["claude", "-p", cmd_prompt, "--allowedTools", tool, "--model", MODEL],
        capture_output=True, text=True, timeout=timeout, cwd=str(repo_root),
        env=_claude_env(),
    )
    if result.returncode != 0:
        raise RuntimeError(f"rc={result.returncode}: {(result.stderr or '').strip()[:200]}")
    parsed = _extract_json_array(result.stdout or "")
    if parsed is None:
        raise ValueError(f"unparseable: {(result.stdout or '').strip()[:200]}")
    return [r for r in parsed if isinstance(r, dict)]


def make_holdings_runner(repo_root, timeout: int = HOLDINGS_TIMEOUT):
    def run(etfs: Sequence[str], topn: int):
        prompt = (
            "Call the FactSet_Ownership tool EXACTLY ONCE with these arguments:\n"
            f"  ids: {json.dumps(list(etfs))}\n"
            "  data_type: 'fund_holdings'\n"
            "  assetType: 'EQ'\n"
            f"  topn: '{topn}'\n"
            "Do NOT call the tool more than once. Do NOT paginate.\n\n"
            "Then return ONLY a JSON array (no prose, no markdown, no code fences) of the "
            'tool\'s result elements, each as {"requestId": str, "date": "YYYY-MM-DD", '
            '"securityTicker": str, "securityName": str, "weightClose": number, '
            '"adjHolding": number}. '
            "Copy every value VERBATIM — do not summarise, reword, filter, re-rank, round or "
            "invent. Include every element returned. Return [] if the tool returned none."
        )
        return _run(prompt, _OWNERSHIP_TOOL, repo_root, timeout)
    return run


def make_adv_runner(repo_root, timeout: int = ADV_TIMEOUT):
    def run(tickers: Sequence[str], start: str, end: str):
        prompt = (
            "Call the FactSet_GlobalPrices tool EXACTLY ONCE with these arguments:\n"
            f"  ids: {json.dumps(list(tickers))}\n"
            "  data_type: 'prices'\n"
            f"  startDate: '{start}'\n"
            f"  endDate: '{end}'\n"
            "  fields: ['price', 'volume']\n"
            "Do NOT call the tool more than once. Do NOT paginate.\n\n"
            "Then return ONLY a JSON array (no prose, no markdown, no code fences) of the "
            'tool\'s result elements, each as {"requestId": str, "date": "YYYY-MM-DD", '
            '"price": number-or-null, "volume": number-or-null}. '
            "Copy every value VERBATIM. If a value is null, return null — do NOT substitute 0. "
            "Include every element returned. Return [] if the tool returned none."
        )
        return _run(prompt, _PRICES_TOOL, repo_root, timeout)
    return run


# ── parsing ───────────────────────────────────────────────────────────────────

def parse_holdings(rows) -> dict[str, dict]:
    """-> {etf: {'as_of': date, 'holdings': [{ticker, name, weight_pct}]}}"""
    out: dict[str, dict] = {}
    for r in rows:
        etf = (r.get("requestId") or "").strip().upper()
        tk = normalize_ticker(r.get("securityTicker") or "")
        w = r.get("weightClose")
        if not etf or not tk or not isinstance(w, (int, float)):
            continue
        entry = out.setdefault(etf, {"as_of": r.get("date"), "holdings": []})
        entry["holdings"].append({
            "ticker": tk,
            "name": (r.get("securityName") or "").strip(),
            "weight_pct": float(w),
        })
    for e in out.values():
        e["holdings"].sort(key=lambda h: -h["weight_pct"])
    return out


def compute_adv(rows) -> dict[str, float]:
    """Mean DOLLAR volume per ticker: mean(volume x price) over the returned window.

    Dollar volume, not share volume — implied demand is a dollar figure, and comparing it to
    share counts would silently mix units and make a $900 stock look 30x more liquid than a
    $30 one.
    """
    acc: dict[str, list[float]] = {}
    for r in rows:
        tk = normalize_ticker(r.get("requestId") or "")
        v, p = r.get("volume"), r.get("price")
        if not tk or not isinstance(v, (int, float)) or not isinstance(p, (int, float)):
            continue
        acc.setdefault(tk, []).append(float(v) * float(p))
    return {t: sum(vals) / len(vals) for t, vals in acc.items() if vals}


# ── portfolio ─────────────────────────────────────────────────────────────────

def bctk_holdings(db_path: str, etf: str = "BCTK") -> dict[str, float]:
    """{ticker: weight_pct} for the latest scraped date. {} if unavailable.

    Source is /root/ws's scraper, which already runs daily and carries weights and share
    counts. Note it can NEVER measure flows — it has no fund-level shares-outstanding and
    market_value is 0.0 in practice — but weights are exactly what the intersection needs.
    """
    if not os.path.exists(db_path):
        return {}
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            cur = con.execute(
                "SELECT symbol, weight FROM holdings WHERE etf_ticker = ? AND date = "
                "(SELECT MAX(date) FROM holdings WHERE etf_ticker = ?)", (etf, etf))
            return {normalize_ticker(s): float(w) for s, w in cur.fetchall() if s}
        finally:
            con.close()
    except sqlite3.Error:
        return {}


# ── the computation ───────────────────────────────────────────────────────────

def implied_demand(flow_usd: float, holdings: Sequence[dict],
                   adv: dict[str, float] | None = None,
                   portfolio: dict[str, float] | None = None,
                   min_weight_pct: float = MIN_WEIGHT_PCT,
                   max_names: int = MAX_NAMES) -> list[Demand]:
    """Per-constituent implied demand, ranked by absolute size.

    Weights arrive as percentages (21.38 == 21.38%), so the /100 is deliberate and is the
    single easiest thing to get wrong here — a missing divide overstates every figure 100x.
    """
    adv = adv or {}
    portfolio = portfolio or {}
    out: list[Demand] = []
    for h in holdings:
        w = h.get("weight_pct")
        if not isinstance(w, (int, float)) or abs(w) < min_weight_pct:
            continue
        tk = h["ticker"]
        implied = flow_usd * (float(w) / 100.0)
        a = adv.get(tk)
        out.append(Demand(
            ticker=tk, name=h.get("name", ""), weight_pct=float(w),
            implied_usd=implied, adv_usd=a,
            days_of_adv=(implied / a) if a else None,
            in_portfolio=tk in portfolio,
            portfolio_weight=portfolio.get(tk),
        ))
    out.sort(key=lambda d: -abs(d.implied_usd))
    return out[:max_names]


def needs_reconstitution_warning(etf: str, as_of: str) -> bool:
    """MTUM reconstitutes semi-annually (late May / late November).

    A rebalance reshuffles which momentum names are held and will read as a flow event if
    unlabelled, so any MTUM decomposition inside those months is flagged.
    """
    if etf.upper() != "MTUM" or not as_of or len(as_of) < 7:
        return False
    return as_of[5:7] in ("05", "06", "11", "12")


def analyse(alerts, universe, holdings_by_etf: dict, adv: dict[str, float],
            portfolio: dict[str, float]) -> list[dict]:
    """One decomposition per alerting, non-synthetic ETF."""
    seen: set[str] = set()
    results = []
    for a in alerts:
        etf = a.ticker
        if etf in seen or universe.synthetic(etf):
            continue
        seen.add(etf)
        entry = holdings_by_etf.get(etf)
        if not entry or not entry.get("holdings"):
            continue
        demands = implied_demand(a.flow_usd or 0.0, entry["holdings"], adv, portfolio)
        held = [d for d in demands if d.in_portfolio]
        results.append({
            "etf": etf,
            "horizon": a.horizon,
            "flow_usd": a.flow_usd,
            "direction": a.direction,
            "weights_as_of": entry.get("as_of"),
            "demands": demands,
            "held": held,
            "reconstitution_warning": needs_reconstitution_warning(etf, entry.get("as_of")),
        })
    return results


def etfs_to_decompose(alerts, universe) -> list[str]:
    """Distinct non-synthetic ETFs worth a holdings call."""
    out: list[str] = []
    for a in alerts:
        if a.ticker not in out and not universe.synthetic(a.ticker):
            out.append(a.ticker)
    return out
