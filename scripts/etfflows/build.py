"""
build — turns stored series into the report dict that render.py consumes. No I/O beyond
reading the universe YAML; no LLM calls. This is the whole 07:00 path.

The ordering here is the part worth reading carefully:

    raw USD flow  ->  rolling window sum  ->  normalise to bps of PRIOR-period AUM
                  ->  robust z against the baseline of THAT SAME bps series

Normalising AFTER the window sum (not before) keeps the denominator interpretable: "this
week's creations were 88 bps of the fund as it stood when the week began". And the baseline
is built from the identical pipeline, so the z-score compares like with like — see
metrics.step_aum_series for why consistency beats precision on the denominator.
"""
from __future__ import annotations

import os

import yaml

from . import HORIZONS, LONG_HORIZON, SHORT_HORIZON
from . import metrics as m
from . import store
from . import triggers as tg


# ── universe ──────────────────────────────────────────────────────────────────

class Universe:
    """Flattened view of config/etf_universe.yaml."""

    def __init__(self, cfg: dict):
        self.raw = cfg
        self.tier: dict[str, str] = {}
        self.sleeve: dict[str, str] = {}
        self.baseline_years: dict[str, int] = {}
        for tier_name, tier in (cfg.get("tiers") or {}).items():
            years = tier.get("baseline_years", 3)
            for sleeve_key, sleeve in (tier.get("sleeves") or {}).items():
                for t in sleeve.get("tickers") or []:
                    self.tier[t] = tier_name
                    self.sleeve[t] = sleeve_key
                    self.baseline_years[t] = years
        self.overrides = cfg.get("overrides") or {}
        self.pairs = cfg.get("pairs") or []

    @property
    def tickers(self) -> list[str]:
        return sorted(self.tier)

    def trigger_tickers(self) -> list[str]:
        return sorted(t for t, v in self.tier.items() if v == "trigger")

    def context_tickers(self) -> list[str]:
        return sorted(t for t, v in self.tier.items() if v == "context")

    def synthetic(self, t: str) -> bool:
        return bool(self.overrides.get(t, {}).get("synthetic", False))

    def min_history_ok(self, t: str) -> bool:
        return bool(self.overrides.get(t, {}).get("min_history_ok", True))

    def factor_tickers(self) -> list[str]:
        sleeve = ((self.raw.get("tiers", {}).get("trigger", {}).get("sleeves", {})
                   .get("factor")) or {})
        return list(sleeve.get("tickers") or [])


def load_universe(path: str) -> Universe:
    with open(path) as fh:
        return Universe(yaml.safe_load(fh))


# ── per-ticker computation ────────────────────────────────────────────────────

def ticker_metrics(state: dict, ticker: str, as_of: str) -> dict:
    """All horizons for one ticker, as of `as_of`.

    Returns a dict of per-horizon readings plus the raw series positions used, so the caller
    can build both the table row and the trigger Reading without recomputing.
    """
    dates, flows = store.series_for(state, "flows", ticker)
    # NAVs are looked up BY DATE, never positionally: the price series can have a different
    # length and different holidays than the flow series, so zipping the two by index would
    # quietly pair a flow with the wrong day's NAV and corrupt every divergence reading.
    nav_by_date = dict(zip(*store.series_for(state, "prices", ticker)))
    anchors = store.month_end_aum(state, ticker)

    out: dict = {"ticker": ticker, "dates": dates, "has_data": bool(dates), "horizons": {}}
    if not dates or as_of not in dates:
        out["has_data"] = False
        return out

    idx = dates.index(as_of)
    navs_aligned = [nav_by_date.get(d) for d in dates]

    for h in HORIZONS:
        sums = m.rolling_sums(flows, h)
        denom = m.step_aum_series(dates, anchors, h)
        bps_series = [m.to_bps(sums[i], denom[i]) for i in range(len(dates))]

        cur_usd = sums[idx]
        cur_bps = bps_series[idx]

        # Baseline excludes the current point so a reading is never compared against itself.
        baseline = [v for i, v in enumerate(bps_series) if i < idx and v is not None]
        z = m.robust_z(cur_bps, baseline) if cur_bps is not None else None

        ret = m.window_return(navs_aligned[: idx + 1], h)

        out["horizons"][h] = {
            "flow_usd": cur_usd,
            "bps": cur_bps,
            "z": z.z if z else None,
            "percentile": z.percentile if z else None,
            "degraded": (z.degraded if z else True),
            "degrade_reason": (z.reason if z else "no_reading"),
            "window_return": ret,
            "divergence": m.divergence(cur_usd, ret),
            "baseline_n": len(baseline),
            "series_bps": bps_series,
            "series_dates": dates,
        }
    return out


# ── report assembly ───────────────────────────────────────────────────────────

def build_report(state: dict, uni: Universe, as_of: str,
                 trigger_state: dict | None = None,
                 fear_greed_line: str = "") -> tuple[dict, dict]:
    """(report, new_trigger_state). Pure — persistence is the caller's job."""
    trigger_state = trigger_state or {}
    per_ticker: dict[str, dict] = {}
    rows: list[dict] = []
    readings: list[tg.Reading] = []
    warnings: list[str] = []
    quadrants: dict[str, str] = {}
    divergences: dict[str, str] = {}

    for t in uni.tickers:
        tm = ticker_metrics(state, t, as_of)
        per_ticker[t] = tm
        if not tm["has_data"]:
            warnings.append(f"{t}: no flow data for {as_of}")
            continue

        short = tm["horizons"][SHORT_HORIZON]
        long_ = tm["horizons"][LONG_HORIZON]

        if not uni.min_history_ok(t):
            warnings.append(f"{t}: insufficient history — raw flow only, no z-score")
        if uni.synthetic(t):
            warnings.append(f"{t}: synthetically backed — excluded from z-scores")

        q = m.crowding_quadrant(short["z"], long_["z"])
        if q and q != "neutral":
            quadrants[t] = q
        if short["divergence"]:
            divergences[t] = short["divergence"]

        rows.append({
            "ticker": t, "tier": uni.tier[t],
            "flow_short_usd": short["flow_usd"], "bps_short": short["bps"],
            "z_short": short["z"], "degraded_short": short["degraded"],
            "flow_long_usd": long_["flow_usd"], "bps_long": long_["bps"],
            "z_long": long_["z"], "degraded_long": long_["degraded"],
            "quadrant": q,
        })

        for h in HORIZONS:
            hh = tm["horizons"][h]
            readings.append(tg.Reading(
                ticker=t, horizon=h, z=hh["z"], percentile=hh["percentile"],
                flow_usd=hh["flow_usd"], flow_bps=hh["bps"],
                divergence=hh["divergence"], tier=uni.tier[t],
                synthetic=uni.synthetic(t), min_history_ok=uni.min_history_ok(t),
                degraded=hh["degraded"], degrade_reason=hh["degrade_reason"],
            ))

    alerts, new_state, suppressed = tg.evaluate(readings, trigger_state, as_of)

    # Breadth over the TRIGGER TIER only — context names duplicate exposure (VGT/IYW/IGM are
    # ~90% XLK) and would let one move vote three times.
    breadth: dict[int, dict] = {}
    for h in HORIZONS:
        flows_by = {t: per_ticker[t]["horizons"][h]["flow_usd"]
                    for t in uni.trigger_tickers()
                    if per_ticker.get(t, {}).get("has_data")}
        p, pos, n = m.breadth(flows_by)
        breadth[h] = {"pct": p, "positive": pos, "measured": n}

    pairs = []
    for pair in uni.pairs:
        lead, against = pair.get("lead"), pair.get("against") or []
        entry = {"name": pair.get("name") or lead}
        for key, h in (("short", SHORT_HORIZON), ("long", LONG_HORIZON)):
            lb = _bps_of(per_ticker, lead, h)
            ab = [_bps_of(per_ticker, a, h) for a in against]
            entry[key] = m.pair_spread(lb, ab)
        pairs.append(entry)

    factor = [{"ticker": t, "bps": _bps_of(per_ticker, t, LONG_HORIZON)}
              for t in uni.factor_tickers()
              if per_ticker.get(t, {}).get("has_data")]

    report = {
        "as_of": as_of,
        "fear_greed_line": fear_greed_line,
        "alerts": alerts,
        "suppressed": suppressed,
        "breadth": breadth,
        "pairs": pairs,
        "factor_rotation": factor,
        "quadrants": quadrants,
        "divergence": divergences,
        "rows": sorted(rows, key=lambda r: (r["tier"] != "trigger", r["ticker"])),
        "warnings": sorted(set(warnings)),
        "table_notes": ["DRAM and LYTE are synthetically backed — excluded from z-scores."],
    }
    return report, new_state


def _bps_of(per_ticker: dict, ticker: str, horizon: int) -> float | None:
    tm = per_ticker.get(ticker)
    if not tm or not tm.get("has_data"):
        return None
    return tm["horizons"][horizon]["bps"]


def default_universe_path(repo_root: str) -> str:
    return os.path.join(repo_root, "config", "etf_universe.yaml")
