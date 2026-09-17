#!/usr/bin/env python3
"""valuation/expectations.py — the expectations-gap valuation module (RIS5 A5).

The "thoughtful valuation" the operator asked for: what growth the price implies
versus what the evidence supports. NEVER a price target — every card shows implied
vs. supported growth, the gap, multiples vs. history/peers, and the revision trend,
each with its date and inputs.

Three layers, per ticker, built from A3's daily snapshot (`state/valuation/latest.json`,
see scripts/valuation/snapshot.py):

  Layer 1 — what is priced (`implied_growth`): a reverse-DCF-lite. Given EV, a stated
  discount rate/terminal growth (config/valuation.yaml), and a margin path that
  converges linearly from today's FCF margin to a stated terminal margin over 5 years,
  solve by bisection for the constant 5-year revenue growth g that reproduces EV.

  Layer 2 — what the evidence supports (`supported_growth`): base = the 2-year CAGR of
  consensus FY1->FY3 sales, extended by a bounded "durability multiplier" built from
  (a) theme-lifecycle stage rank vs. peer-median stage, (b) guidance/consensus
  credibility, (c) the last-2-quarter structured-reads trend (each gated on minimum
  history, each independently clipped) — with an explicit downside path when a
  competition/margin-themed assumption is `status: challenged`.

  Layer 3 — the gap: `implied_growth_5y - supported.base`, in percentage points.
  Positive = the price needs more growth than the evidence gives it.

Plus lenses (forward EV/Sales, P/E, a PEG-like ratio, z-scores vs. own history and vs.
theme peers, revision breadth) and a `valuation_extreme` flag.

Every numeric default not explicitly given by the task brief (fcf_margin_now-by-family,
the downside haircut, the sector-keyword map, durability-term bounds, bisection bounds,
z-score minimums) lives in config/valuation.yaml with its rationale in a comment there —
see that file and the A5 report for the full list of interpretive calls.

Fundamentals (net debt, margins) are OPTIONAL: scripts/valuation/fundamentals.py's
FUNDAMENTALS_METRICS is empty pending a live FactSet metric-code probe, so on the first
live run of this module every card falls back to the sector-family defaults (flagged
"no_net_debt" / "margin_default") — not a bug, the documented v1 state.

CLI:
    python3 scripts/valuation/expectations.py --dry-run                 # fixture-only smoke
    python3 scripts/valuation/expectations.py --state-dir /tmp/snap ... # explicit fixture run
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from datetime import date
from pathlib import Path

import yaml

REPO = Path("/root/research-watchlist")   # canonical vault root -- READ-ONLY config/notes/state
                                          # paths only. NEVER used to resolve sibling imports
                                          # below (see snapshot.py's own "REPO trap" docstring):
                                          # this worktree's copies must win until merge.
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_SCRIPTS_DIR / "chunking"))
sys.path.insert(0, str(_SCRIPTS_DIR / "portal"))
sys.path.insert(0, str(_SCRIPTS_DIR / "thesis"))

import identity as pid                          # noqa: E402  scripts/portal/identity.py
from valuation import snapshot as vsnap         # noqa: E402  scripts/valuation/snapshot.py
import store_b                                  # noqa: E402  scripts/chunking/store_b.py
import theme_polarity                           # noqa: E402  scripts/thesis/theme_polarity.py

CONFIG_PATH = REPO / "config" / "valuation.yaml"
STATE_DIR = REPO / "state" / "valuation"
WATCHLIST_PATH = REPO / "config" / "watchlist.yaml"
NOTES_DIR = REPO / "notes"
READS_PATH = REPO / "state" / "thesis" / "reads.jsonl"
POLARITY_PATH = REPO / "config" / "theme_polarity.yaml"
STAGES_PATH = REPO / "state" / "topics" / "stages.json"

_FM_RE = __import__("re").compile(r"^---\n(.*?)\n---\n", __import__("re").S)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config(path: Path = CONFIG_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Sector family (interpretive call -- config/valuation.yaml `sector_keywords`
# docstring has the full rationale; watchlist.yaml carries no `sector` field)
# ---------------------------------------------------------------------------
def theme_family(slug: str, cfg: dict) -> str | None:
    """First family in `sector_family_priority` whose keyword list contains a
    substring of `slug`. None if no keyword matches."""
    priority = cfg.get("sector_family_priority") or []
    keywords = cfg.get("sector_keywords") or {}
    for fam in priority:
        for kw in keywords.get(fam) or []:
            if kw in slug:
                return fam
    return None


def sector_family(themes: list[str], cfg: dict) -> str:
    """Majority vote of theme_family() across a ticker's themes; ties break to
    `sector_family_priority` order; zero votes -> 'default'."""
    priority = cfg.get("sector_family_priority") or []
    votes: dict[str, int] = {}
    for t in themes or []:
        fam = theme_family(t, cfg)
        if fam:
            votes[fam] = votes.get(fam, 0) + 1
    if not votes:
        return "default"
    best = max(votes.values())
    for fam in priority:
        if votes.get(fam) == best:
            return fam
    return "default"


def margin_defaults(ticker: str, sector_fam: str, cfg: dict) -> tuple[float, float]:
    """-> (fcf_margin_now_default, terminal_margin_default) for `sector_fam`,
    from config/valuation.yaml (per-ticker `overrides` win when present)."""
    ov = (cfg.get("overrides") or {}).get(ticker) or {}
    now_tbl = cfg.get("fcf_margin_now_by_family") or {}
    term_tbl = cfg.get("terminal_margin_by_family") or {}
    now = ov.get("fcf_margin_now", now_tbl.get(sector_fam, now_tbl.get("default")))
    term = ov.get("terminal_margin", term_tbl.get(sector_fam, term_tbl.get("default")))
    return now, term


# ---------------------------------------------------------------------------
# Theme universe / peers
# ---------------------------------------------------------------------------
def load_ticker_themes(watchlist_path: Path = None, notes_dir: Path = None) -> dict[str, list[str]]:
    """{ticker: [themes]} for every tier_1/2/3 watchlist entry (identity.load_universe's
    own scope) -- includes `.pvt` ids harmlessly (they never carry a price/consensus row
    so never produce a card, but their themes still count in the theme-level peer pool)."""
    out: dict[str, list[str]] = {}
    for e in pid.load_universe(watchlist_path, notes_dir):
        out[e["ticker"]] = list(e.get("themes") or [])
    return out


def theme_peers(ticker: str, ticker_themes: dict[str, list[str]], min_shared: int = 2) -> list[str]:
    """Tickers sharing >= `min_shared` themes with `ticker` (brief's lens-peer definition)."""
    mine = set(ticker_themes.get(ticker) or [])
    if not mine:
        return []
    out = []
    for other, themes in ticker_themes.items():
        if other == ticker:
            continue
        if len(mine & set(themes or [])) >= min_shared:
            out.append(other)
    return sorted(out)


# ---------------------------------------------------------------------------
# Stage reader (state/topics/stages.json) -- isolated per the task brief: the
# real file's shape disagrees with the brief's own description (bare int per
# pair, not a dict of fields), so both shapes are tolerated here, one place.
# ---------------------------------------------------------------------------
def read_stage(stages: dict, theme: str, ticker: str) -> int | None:
    """Ordinal stage (1-4) for (theme, ticker), or None if UNOBSERVED (never 0/1).

    `gated` entries may be theme-level (bare theme name, e.g. "agentic_commerce" --
    gates every ticker under that theme) or pair-level ("theme|TICKER" -- gates just
    that pair); both forms are checked. `pairs` values are tolerated as a bare int
    (the live 2026-09-16 shape) or a dict carrying a `stage` key (the brief's
    documented shape) -- a one-line adaptation if PR #6 changes this again.
    """
    gated = set(stages.get("gated") or [])
    if theme in gated or f"{theme}|{ticker}" in gated:
        return None
    v = (stages.get("pairs") or {}).get(f"{theme}|{ticker}")
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("stage")
    return v if isinstance(v, int) else None


# ---------------------------------------------------------------------------
# Credibility reader (Store B) -- wrapped so "no credibility" degrades to a
# neutral term + flag, never requires a live DB.
# ---------------------------------------------------------------------------
def read_credibility(ticker: str, metric: str = "SALES", store=None) -> tuple[dict | None, list[str]]:
    """`store` is duck-typed (`.credibility(ticker, metric) -> dict|None`) so tests
    inject a fixture without a live DB. When `store` is None, lazily resolves
    `store_b.get_metrics_store()` (whatever CHUNK_STORE_BACKEND is already set to --
    this module never sets that env var itself); any resolve/connect/read failure
    degrades to (None, ["no_credibility"]) rather than raising."""
    try:
        st = store if store is not None else store_b.get_metrics_store()
        cred = st.credibility(ticker, metric)
    except Exception:                                                    # noqa: BLE001
        return None, ["no_credibility"]
    if not cred:
        return None, ["no_credibility"]
    return cred, []


# ---------------------------------------------------------------------------
# Reads-trend reader (state/thesis/reads.jsonl)
# ---------------------------------------------------------------------------
_DIRECTION_SIGN = {"up": 1.0, "flat": 0.0, "down": -1.0}


def _read_signed(row: dict) -> float:
    sign = _DIRECTION_SIGN.get(row.get("direction"), 0.0)
    mag = row.get("magnitude") or 0
    return sign * (mag / 2.0)   # magnitude 0-2 -> normalized to [-1, 1] combined with sign


def reads_term(ticker: str, reads_rows: list[dict], cfg: dict) -> tuple[float, list[str], dict]:
    """Amendment-measured 2026-09-17: only 8/178 tickers clear >=3 dated reads on any
    SINGLE axis, but they clear it on every one of the 5 structured-read axes (same
    source notes). Average across every axis for this ticker that individually clears
    the `reads_min_dated` gate; omit axes that don't. Zero qualifying axes -> term 0.0,
    flagged "insufficient history: reads trend" (never silently 0 without saying so)."""
    min_dated = (cfg.get("supported_growth") or {}).get("reads_min_dated", 3)
    bound = ((cfg.get("supported_growth") or {}).get("durability") or {}).get("reads_term_bound", 0.10)

    by_axis: dict[str, list[dict]] = {}
    for r in reads_rows:
        if r.get("ticker") != ticker or not r.get("date"):
            continue
        by_axis.setdefault(r["axis"], []).append(r)

    axis_terms: dict[str, float] = {}
    for axis, rows in by_axis.items():
        if len(rows) < min_dated:
            continue
        rows_sorted = sorted(rows, key=lambda r: r["date"])
        last2 = rows_sorted[-2:]
        axis_terms[axis] = sum(_read_signed(r) for r in last2) / len(last2)

    if not axis_terms:
        return 0.0, ["insufficient history: reads trend"], {"axes_used": []}

    raw = statistics.mean(axis_terms.values()) * bound
    term = _clip(raw, -bound, bound)
    return term, [], {"axes_used": sorted(axis_terms), "axis_terms": axis_terms}


# ---------------------------------------------------------------------------
# Stage-rank durability term
# ---------------------------------------------------------------------------
def stage_rank_term(ticker: str, themes: list[str], stages: dict,
                    ticker_themes_all: dict[str, list[str]], cfg: dict) -> tuple[float, list[str], dict]:
    """Ordinal stage rank vs. the ticker's peer-median stage, per theme (amendment
    v1.1 #6: NEVER a linear stage number). For each of the ticker's themes with an
    observed stage, peers = every other ticker tagged with that theme with an observed
    stage; delta = peer_median - ticker_stage (positive = ticker is EARLIER stage than
    peers = longer runway = more durable). Averaged across themes, scaled by
    `stage_term_per_level`, clipped to `stage_term_bound`."""
    durability = (cfg.get("supported_growth") or {}).get("durability") or {}
    bound = durability.get("stage_term_bound", 0.15)
    per_level = durability.get("stage_term_per_level", 0.05)

    deltas = []
    themes_used = []
    for theme in themes or []:
        my_stage = read_stage(stages, theme, ticker)
        if my_stage is None:
            continue
        peer_stages = []
        for other, other_themes in ticker_themes_all.items():
            if other == ticker or theme not in (other_themes or []):
                continue
            s = read_stage(stages, theme, other)
            if s is not None:
                peer_stages.append(s)
        if not peer_stages:
            continue
        peer_median = statistics.median(peer_stages)
        deltas.append(peer_median - my_stage)
        themes_used.append(theme)

    if not deltas:
        return 0.0, ["no_stage_data"], {"themes_used": []}

    avg_delta = statistics.mean(deltas)
    term = _clip(avg_delta * per_level, -bound, bound)
    return term, [], {"themes_used": themes_used, "avg_stage_rank_delta": avg_delta}


def credibility_term(ticker: str, cfg: dict, store=None) -> tuple[float, list[str], dict]:
    durability = (cfg.get("supported_growth") or {}).get("durability") or {}
    bound = durability.get("credibility_term_bound", 0.10)
    cred, flags = read_credibility(ticker, store=store)
    if not cred:
        return 0.0, flags, {}
    rates = [r for r in (cred.get("consensus_beat_rate"), cred.get("guide_hit_rate")) if r is not None]
    if not rates:
        return 0.0, ["no_credibility"], {}
    avg_rate = statistics.mean(rates)
    term = _clip((avg_rate - 0.5) * 0.20, -bound, bound)
    return term, [], {"avg_rate": avg_rate, "n_rates": len(rates)}


def durability_multiplier(stage_t: float, cred_t: float, reads_t: float, cfg: dict) -> float:
    lo, hi = ((cfg.get("supported_growth") or {}).get("durability") or {}).get("multiplier_bounds", [0.5, 1.5])
    return _clip(1.0 + stage_t + cred_t + reads_t, lo, hi)


# ---------------------------------------------------------------------------
# Thesis frontmatter reader (own tiny loader, mirroring thesis_io.py's regex
# convention -- copied rather than imported so tests can point at a fixture
# path; thesis_io.load() hardcodes REPO/notes with no override).
# ---------------------------------------------------------------------------
def load_thesis_fm(ticker: str, notes_dir: Path = NOTES_DIR) -> dict | None:
    p = Path(notes_dir) / ticker / "_thesis.md"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def challenged_downside_assumptions(thesis_fm: dict | None, downside_theme_slugs: set[str]) -> list[str]:
    """Assumption ids with status=='challenged' whose `themes` intersect
    competition_slugs() union bearish_themes() (brief: "any assumption with a
    competition/margin theme is challenged")."""
    if not thesis_fm:
        return []
    out = []
    for a in thesis_fm.get("assumptions") or []:
        if a.get("status") != "challenged":
            continue
        if set(a.get("themes") or []) & downside_theme_slugs:
            out.append(a.get("id"))
    return out


# ---------------------------------------------------------------------------
# Layer 2 — supported_growth
# ---------------------------------------------------------------------------
def near_term_cagr(fy1_sales, fy3_sales) -> float | None:
    if not fy1_sales or not fy3_sales or fy1_sales <= 0 or fy3_sales <= 0:
        return None
    return (fy3_sales / fy1_sales) ** (1.0 / 2.0) - 1.0


def supported_growth(ticker: str, entry: dict, cfg: dict, *, stages: dict,
                     ticker_themes_all: dict[str, list[str]], reads_rows: list[dict],
                     thesis_fm: dict | None, downside_theme_slugs: set[str],
                     credibility_store=None) -> dict:
    """base = near_term_cagr * durability_multiplier (bounded); downside = base minus
    the configured haircut when >=1 qualifying assumption is challenged."""
    themes = ticker_themes_all.get(ticker) or []
    flags: list[str] = []

    cagr = near_term_cagr(entry.get("fy1_sales"), entry.get("fy3_sales"))
    if cagr is None:
        return {"base": None, "downside": None, "near_term_cagr": None,
                "durability_multiplier": None, "drivers": {}, "challenged_assumption_ids": [],
                "flags": ["missing fy1/fy3 sales for CAGR"]}

    st_term, st_flags, st_detail = stage_rank_term(ticker, themes, stages, ticker_themes_all, cfg)
    cr_term, cr_flags, cr_detail = credibility_term(ticker, cfg, store=credibility_store)
    rd_term, rd_flags, rd_detail = reads_term(ticker, reads_rows, cfg)
    flags.extend(st_flags); flags.extend(cr_flags); flags.extend(rd_flags)

    mult = durability_multiplier(st_term, cr_term, rd_term, cfg)
    lo, hi = (cfg.get("supported_growth") or {}).get("base_bounds", [-0.5, 2.0])
    base_raw = cagr * mult
    base = _clip(base_raw, lo, hi)
    if base != base_raw:
        flags.append("supported_growth_clipped")

    haircut = (cfg.get("supported_growth") or {}).get("downside_haircut_pp", 5.0) / 100.0
    challenged_ids = challenged_downside_assumptions(thesis_fm, downside_theme_slugs)
    downside = _clip(base - haircut, lo, hi) if challenged_ids else base

    return {
        "base": base, "downside": downside, "near_term_cagr": cagr,
        "durability_multiplier": mult,
        "drivers": {
            "stage_rank": {"term": st_term, **st_detail},
            "credibility": {"term": cr_term, **cr_detail},
            "reads_trend": {"term": rd_term, **rd_detail},
        },
        "challenged_assumption_ids": challenged_ids,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Layer 1 — implied_growth (reverse-DCF-lite, solved by bisection)
# ---------------------------------------------------------------------------
def _margin_path(fcf_margin_now: float, terminal_margin: float, years: int) -> list[float]:
    return [fcf_margin_now + (terminal_margin - fcf_margin_now) * (t / years) for t in range(1, years + 1)]


def _pv_for_growth(g: float, fy0_sales: float, margins: list[float], discount_rate: float,
                   terminal_growth: float, years: int) -> float:
    pv = 0.0
    fcf_years = 0.0
    for t in range(1, years + 1):
        sales_t = fy0_sales * (1.0 + g) ** t
        fcf_t = sales_t * margins[t - 1]
        pv += fcf_t / (1.0 + discount_rate) ** t
        if t == years:
            fcf_years = fcf_t
    tv = fcf_years * (1.0 + terminal_growth) / (discount_rate - terminal_growth)
    pv += tv / (1.0 + discount_rate) ** years
    return pv


def solve_implied_growth(ev: float, fy0_sales: float, fcf_margin_now: float, terminal_margin: float,
                         discount_rate: float, terminal_growth: float, years: int,
                         bisection_cfg: dict) -> dict:
    """-> {growth, pv_at_growth, flags}. `growth` is None when a guard fails (nonpositive
    margin path, invalid Gordon denominator, or fy0_sales<=0); otherwise bisected to
    `tol_relative` on |PV(g)-EV|/EV, clipped to [g_lo, g_hi] with a flag if EV falls
    outside the bracket PV(g_lo)..PV(g_hi) (PV is monotonically increasing in g only
    while every margin_t > 0 and discount_rate > terminal_growth)."""
    if fy0_sales is None or fy0_sales <= 0:
        return {"growth": None, "pv_at_growth": None, "flags": ["fy0_sales<=0"]}
    if discount_rate - terminal_growth <= 0:
        return {"growth": None, "pv_at_growth": None, "flags": ["invalid_gordon_denominator"]}
    margins = _margin_path(fcf_margin_now, terminal_margin, years)
    if any(m <= 0 for m in margins):
        return {"growth": None, "pv_at_growth": None, "flags": ["margin_path_nonpositive"]}

    g_lo, g_hi = bisection_cfg.get("g_lo", -0.9), bisection_cfg.get("g_hi", 5.0)
    max_iter = bisection_cfg.get("max_iter", 100)
    tol_rel = bisection_cfg.get("tol_relative", 1e-6)

    def pv(g):
        return _pv_for_growth(g, fy0_sales, margins, discount_rate, terminal_growth, years)

    pv_lo, pv_hi = pv(g_lo), pv(g_hi)
    flags: list[str] = []
    if ev <= pv_lo:
        return {"growth": g_lo, "pv_at_growth": pv_lo, "flags": ["implied_growth_out_of_bracket_low"]}
    if ev >= pv_hi:
        return {"growth": g_hi, "pv_at_growth": pv_hi, "flags": ["implied_growth_out_of_bracket_high"]}

    lo, hi = g_lo, g_hi
    mid, pv_mid = lo, pv_lo
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        pv_mid = pv(mid)
        if abs(pv_mid - ev) <= tol_rel * abs(ev):
            break
        if pv_mid < ev:
            lo = mid
        else:
            hi = mid
    return {"growth": mid, "pv_at_growth": pv_mid, "flags": flags}


def implied_growth(ev: float, fy0_sales: float, fcf_margin_now: float, terminal_margin: float,
                   discount_rate: float = 0.10, terminal_growth: float = 0.03, years: int = 5,
                   cfg: dict | None = None) -> dict:
    """Brief's exact signature. `cfg` supplies bisection bounds/tolerance and the
    sensitivity deltas (config/valuation.yaml); defaults match that file's shipped
    values if `cfg` is omitted."""
    cfg = cfg or {}
    bisection_cfg = cfg.get("bisection") or {}
    sens_cfg = cfg.get("sensitivity") or {}
    dr_delta = sens_cfg.get("discount_rate_delta", 0.01)
    tm_delta = sens_cfg.get("terminal_margin_delta", 0.03)

    core = solve_implied_growth(ev, fy0_sales, fcf_margin_now, terminal_margin,
                                discount_rate, terminal_growth, years, bisection_cfg)

    def _g(**overrides):
        kwargs = dict(ev=ev, fy0_sales=fy0_sales, fcf_margin_now=fcf_margin_now,
                      terminal_margin=terminal_margin, discount_rate=discount_rate,
                      terminal_growth=terminal_growth, years=years)
        kwargs.update(overrides)
        return solve_implied_growth(kwargs["ev"], kwargs["fy0_sales"], kwargs["fcf_margin_now"],
                                    kwargs["terminal_margin"], kwargs["discount_rate"],
                                    kwargs["terminal_growth"], kwargs["years"], bisection_cfg)["growth"]

    sensitivity = {
        "dr_plus": _g(discount_rate=discount_rate + dr_delta),
        "dr_minus": _g(discount_rate=discount_rate - dr_delta),
        "tm_plus": _g(terminal_margin=terminal_margin + tm_delta),
        "tm_minus": _g(terminal_margin=terminal_margin - tm_delta),
    }
    return {
        "implied_growth_5y": core["growth"],
        "implied_terminal_margin": terminal_margin,   # echoed input, not solved (2 unknowns, 1 equation)
        "pv_at_growth": core["pv_at_growth"],
        "flags": core["flags"],
        "sensitivity": sensitivity,
    }


# ---------------------------------------------------------------------------
# Layer 3 — gap
# ---------------------------------------------------------------------------
def compute_gap(implied_growth_5y, supported_base, supported_downside) -> dict:
    gap_pp = None if implied_growth_5y is None or supported_base is None else \
        round((implied_growth_5y - supported_base) * 100, 4)
    gap_downside_pp = None if implied_growth_5y is None or supported_downside is None else \
        round((implied_growth_5y - supported_downside) * 100, 4)
    return {"gap_pp": gap_pp, "gap_downside_pp": gap_downside_pp}


# ---------------------------------------------------------------------------
# Lenses
# ---------------------------------------------------------------------------
def ev_sales_fy1(ev, fy1_sales) -> float | None:
    if ev is None or not fy1_sales or fy1_sales <= 0:
        return None
    return ev / fy1_sales


def pe_fy1(price, fy1_eps) -> tuple[float | None, list[str]]:
    if price is None or fy1_eps is None or fy1_eps <= 0:
        return None, ["pe_na: eps<=0 or missing"]
    return price / fy1_eps, []


def peg_like(multiple: float | None, growth_pct: float | None) -> tuple[float | None, list[str]]:
    if multiple is None:
        return None, ["peg_na: multiple missing"]
    if growth_pct is None or growth_pct <= 0:
        return None, ["peg_na: growth<=0"]
    return multiple / growth_pct, []


def zscore_history(current_value: float | None, series_values: list[float], min_days: int) -> dict:
    n_days = len(series_values)
    if current_value is None or n_days < min_days or n_days < 2:
        return {"z": None, "n_days": n_days, "flags": ["insufficient history"]}
    mean = statistics.mean(series_values)
    stdev = statistics.pstdev(series_values)
    if stdev == 0:
        return {"z": None, "n_days": n_days, "flags": ["zero_variance"]}
    return {"z": (current_value - mean) / stdev, "n_days": n_days, "flags": []}


def peer_lens(value: float | None, peer_values: list[float], min_peers_for_z: int) -> dict:
    peer_values = [v for v in peer_values if v is not None]
    if not peer_values:
        return {"peer_median": None, "peer_z": None, "n_peers": 0, "flags": ["no_peers"]}
    median = statistics.median(peer_values)
    if len(peer_values) < min_peers_for_z or value is None:
        return {"peer_median": median, "peer_z": None, "n_peers": len(peer_values),
                "flags": ["insufficient peers for z"]}
    stdev = statistics.pstdev(peer_values)
    if stdev == 0:
        return {"peer_median": median, "peer_z": None, "n_peers": len(peer_values), "flags": ["zero_variance"]}
    return {"peer_median": median, "peer_z": (value - median) / stdev, "n_peers": len(peer_values), "flags": []}


# ---------------------------------------------------------------------------
# History scanning (accrued snapshots under state_dir)
# ---------------------------------------------------------------------------
def dated_snapshot_dates(state_dir: Path) -> list[str]:
    """Every date with BOTH a prices_<date>.jsonl and consensus_<date>.jsonl under
    state_dir, ascending."""
    state_dir = Path(state_dir)
    prices = {p.stem.split("prices_", 1)[1] for p in state_dir.glob("prices_*.jsonl")}
    consensus = {p.stem.split("consensus_", 1)[1] for p in state_dir.glob("consensus_*.jsonl")}
    return sorted(prices & consensus)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_dated_tickers(state_dir: Path, dated: str) -> dict[str, dict]:
    """Reuses snapshot.build_latest() against a single dated day's raw rows -- same
    shape as latest.json's `tickers`, so lens functions work unchanged against history."""
    state_dir = Path(state_dir)
    price_rows = _read_jsonl(state_dir / f"prices_{dated}.jsonl")
    consensus_rows = _read_jsonl(state_dir / f"consensus_{dated}.jsonl")
    latest = vsnap.build_latest(price_rows, consensus_rows, len(price_rows), [], dated)
    return latest["tickers"]


def history_series(ticker: str, state_dir: Path, lens_fn, exclude_date: str | None = None) -> list[float]:
    """lens_fn(entry) -> float|None, applied to every dated snapshot's ticker entry.
    Dates where the ticker is absent, or lens_fn returns None, are skipped (not
    counted toward n_days). `exclude_date` skips the current as_of day itself so
    "own history" doesn't include the point being scored."""
    out = []
    for d in dated_snapshot_dates(state_dir):
        if d == exclude_date:
            continue
        entry = load_dated_tickers(state_dir, d).get(ticker)
        if entry is None:
            continue
        v = lens_fn(entry)
        if v is not None:
            out.append(v)
    return out


def revision_breadth(ticker: str, entry_now: dict, state_dir: Path, as_of: str,
                     weeks: int, key: str = "fy1_sales", tolerance_days: int = 5) -> dict:
    """(up_now - down_now) - (up_then - down_then) for the nearest dated snapshot
    within `tolerance_days` of `weeks` weeks before `as_of`. "n/a" until that much
    history has accrued (brief's own sanctioned degrade)."""
    up_now = (entry_now.get("up") or {}).get(key)
    down_now = (entry_now.get("down") or {}).get(key)
    if up_now is None or down_now is None:
        return {"delta": None, "note": "n/a"}
    target = date.fromisoformat(as_of) - __import__("datetime").timedelta(days=weeks * 7)
    best_d, best_gap = None, None
    for d in dated_snapshot_dates(state_dir):
        try:
            dd = date.fromisoformat(d)
        except ValueError:
            continue
        gap = abs((dd - target).days)
        if gap <= tolerance_days and (best_gap is None or gap < best_gap):
            best_d, best_gap = d, gap
    if best_d is None:
        return {"delta": None, "note": "n/a"}
    then_entry = load_dated_tickers(state_dir, best_d).get(ticker)
    if not then_entry:
        return {"delta": None, "note": "n/a"}
    up_then = (then_entry.get("up") or {}).get(key)
    down_then = (then_entry.get("down") or {}).get(key)
    if up_then is None or down_then is None:
        return {"delta": None, "note": "n/a"}
    return {"delta": (up_now - down_now) - (up_then - down_then), "note": None, "compared_to": best_d}


# ---------------------------------------------------------------------------
# Fundamentals reader (optional -- see fundamentals.py; row schema
# {ticker, fsym, date, metric, value, periodicity, fiscal_end, currency, quality})
# ---------------------------------------------------------------------------
def load_fundamentals(state_dir: Path, as_of: str = None) -> dict[str, dict]:
    """{ticker: {metric: value}} from the newest fundamentals_<date>.jsonl <= as_of
    under state_dir (weekly cadence -- glob-for-latest, same convention as
    state_bundles._latest_dated). {} if none present (the expected v1 state --
    FUNDAMENTALS_METRICS is empty pending the live probe)."""
    state_dir = Path(state_dir)
    best, best_date = None, ""
    for p in state_dir.glob("fundamentals_*.jsonl"):
        d = p.stem.split("fundamentals_", 1)[1]
        if as_of and d > as_of:
            continue
        if d > best_date:
            best, best_date = p, d
    if not best:
        return {}
    out: dict[str, dict] = {}
    for r in _read_jsonl(best):
        if r.get("quality") != "ok":
            continue
        out.setdefault(r["ticker"], {})[r["metric"]] = r.get("value")
    return out


# ---------------------------------------------------------------------------
# Quality-fail reason lookup (amendment v1.1 #19: exclude quality:fail:* rows
# from the gap, show the reason). build_latest() already dropped fail rows
# from latest.json's `tickers`, so the REASON string, when one exists, lives
# only in the dated raw rows -- read them if present, else a generic reason.
# ---------------------------------------------------------------------------
def _quality_fail_reason(state_dir: Path, as_of: str, ticker: str, field: str) -> str | None:
    metric_map = {"fy1_sales": "SALES", "fy2_sales": "SALES", "fy3_sales": "SALES",
                  "fy1_eps": "EPS", "fy2_eps": "EPS", "fy3_eps": "EPS"}
    period_map = {"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3,
                  "fy1_eps": 1, "fy2_eps": 2, "fy3_eps": 3}
    metric, rel = metric_map.get(field), period_map.get(field)
    if metric is None:
        return None
    for r in _read_jsonl(Path(state_dir) / f"consensus_{as_of}.jsonl"):
        if (r.get("ticker") == ticker and r.get("metric") == metric and r.get("rel_period") == rel
                and str(r.get("quality", "")).startswith("fail:")):
            return r["quality"]
    return None


def is_valuation_extreme(gap_pp: float | None, peg_history_z: float | None, cfg: dict) -> bool:
    """Brief's exact thresholds, verbatim: gap > +8pp OR PEG-vs-history z > +2."""
    thresh = cfg.get("valuation_extreme") or {}
    gap_thresh = thresh.get("gap_pp_threshold", 8)
    peg_z_thresh = thresh.get("peg_history_z_threshold", 2)
    return bool((gap_pp is not None and gap_pp > gap_thresh) or
               (peg_history_z is not None and peg_history_z > peg_z_thresh))


# ---------------------------------------------------------------------------
# Card builder
# ---------------------------------------------------------------------------
_REQUIRED_SALES = ("fy1_sales", "fy2_sales", "fy3_sales")


def build_card(ticker: str, entry: dict | None, cfg: dict, *, state_dir: Path, as_of: str,
               stages: dict, ticker_themes_all: dict[str, list[str]], downside_theme_slugs: set[str],
               reads_rows: list[dict], notes_dir: Path = NOTES_DIR, credibility_store=None,
               fundamentals: dict | None = None, all_entries: dict | None = None) -> dict:
    """One ticker's full card, or {"ticker", "skipped": True, "reason": ...}."""
    if entry is None:
        return {"ticker": ticker, "skipped": True, "reason": "not in snapshot"}
    if entry.get("price") is None or entry.get("mcap") is None:
        return {"ticker": ticker, "skipped": True, "reason": "no price/mcap"}
    for field in _REQUIRED_SALES:
        if entry.get(field) is None:
            reason = _quality_fail_reason(state_dir, as_of, ticker, field)
            return {"ticker": ticker, "skipped": True,
                    "reason": f"quality fail: {reason}" if reason else f"missing {field}"}

    themes = ticker_themes_all.get(ticker) or []
    fam = sector_family(themes, cfg)
    now_default, term_default = margin_defaults(ticker, fam, cfg)

    fundamentals = fundamentals or {}
    fnd = fundamentals.get(ticker, {})
    flags: list[str] = []

    net_debt = fnd.get("net_debt")
    ev = entry["mcap"] + net_debt if net_debt is not None else entry["mcap"]
    if net_debt is None:
        flags.append("no_net_debt")

    fcf_margin_now = fnd.get("fcf_margin", now_default)
    if "fcf_margin" not in fnd:
        flags.append("margin_default")
    terminal_margin = term_default   # overrides already folded into margin_defaults()

    l1 = implied_growth(ev, entry["fy1_sales"], fcf_margin_now, terminal_margin,
                        discount_rate=cfg.get("discount_rate", 0.10),
                        terminal_growth=cfg.get("terminal_growth", 0.03),
                        years=cfg.get("years", 5), cfg=cfg)

    thesis_fm = load_thesis_fm(ticker, notes_dir)
    l2 = supported_growth(ticker, entry, cfg, stages=stages, ticker_themes_all=ticker_themes_all,
                          reads_rows=reads_rows, thesis_fm=thesis_fm,
                          downside_theme_slugs=downside_theme_slugs, credibility_store=credibility_store)

    gap = compute_gap(l1["implied_growth_5y"], l2["base"], l2["downside"])

    ev_sales = ev_sales_fy1(ev, entry["fy1_sales"])
    pe, pe_flags = pe_fy1(entry["price"], entry.get("fy1_eps"))
    growth_pct = l2["near_term_cagr"] * 100 if l2["near_term_cagr"] is not None else None
    peg, peg_flags = peg_like(pe, growth_pct)

    min_days = (cfg.get("history") or {}).get("min_days_for_z", 60)
    ev_sales_hist = zscore_history(
        ev_sales, history_series(ticker, state_dir, lambda e: ev_sales_fy1(
            (e["mcap"] + net_debt) if (e.get("mcap") is not None and net_debt is not None) else e.get("mcap"),
            e.get("fy1_sales")), exclude_date=as_of), min_days)
    pe_hist = zscore_history(
        pe, history_series(ticker, state_dir, lambda e: pe_fy1(e.get("price"), e.get("fy1_eps"))[0],
                           exclude_date=as_of), min_days)

    def _peg_lens(e):
        pe_e, _ = pe_fy1(e.get("price"), e.get("fy1_eps"))
        cagr_e = near_term_cagr(e.get("fy1_sales"), e.get("fy3_sales"))
        gp_e = cagr_e * 100 if cagr_e is not None else None
        peg_e, _ = peg_like(pe_e, gp_e)
        return peg_e

    peg_hist = zscore_history(peg, history_series(ticker, state_dir, _peg_lens, exclude_date=as_of), min_days)

    peers = theme_peers(ticker, ticker_themes_all, (cfg.get("peer") or {}).get("min_shared_themes", 2))
    min_peers_for_z = (cfg.get("peer") or {}).get("min_peers_for_z", 3)
    all_entries = all_entries or {}
    peer_ev_sales_vals, peer_peg_vals = [], []
    for p in peers:
        pe_entry = all_entries.get(p)
        if pe_entry is None:
            continue
        p_net_debt = fundamentals.get(p, {}).get("net_debt")
        p_ev = pe_entry["mcap"] + p_net_debt if p_net_debt is not None and pe_entry.get("mcap") is not None \
            else pe_entry.get("mcap")
        peer_ev_sales_vals.append(ev_sales_fy1(p_ev, pe_entry.get("fy1_sales")))
        p_pe, _ = pe_fy1(pe_entry.get("price"), pe_entry.get("fy1_eps"))
        p_cagr = near_term_cagr(pe_entry.get("fy1_sales"), pe_entry.get("fy3_sales"))
        p_gp = p_cagr * 100 if p_cagr is not None else None
        p_peg, _ = peg_like(p_pe, p_gp)
        peer_peg_vals.append(p_peg)

    ev_sales_peers = peer_lens(ev_sales, peer_ev_sales_vals, min_peers_for_z)
    peg_peers = peer_lens(peg, peer_peg_vals, min_peers_for_z)

    breadth_4w = revision_breadth(ticker, entry, state_dir, as_of, 4)
    breadth_13w = revision_breadth(ticker, entry, state_dir, as_of, 13)

    valuation_extreme = is_valuation_extreme(gap["gap_pp"], peg_hist["z"], cfg)

    all_flags = sorted(set(flags + l1["flags"] + l2["flags"] + pe_flags + peg_flags))

    return {
        "ticker": ticker, "skipped": False, "as_of": as_of, "sector_family": fam,
        "flags": all_flags,
        "inputs": {
            "price": entry["price"], "mcap": entry["mcap"], "net_debt": net_debt, "ev": ev,
            "fy1_sales": entry["fy1_sales"], "fy2_sales": entry["fy2_sales"], "fy3_sales": entry["fy3_sales"],
            "fy1_eps": entry.get("fy1_eps"),
            "fcf_margin_now": fcf_margin_now, "terminal_margin": terminal_margin,
            "discount_rate": cfg.get("discount_rate", 0.10), "terminal_growth": cfg.get("terminal_growth", 0.03),
            "years": cfg.get("years", 5),
        },
        "layer1_priced": l1,
        "layer2_supported": l2,
        "gap": gap,
        "lenses": {
            "ev_sales_fy1": ev_sales, "pe_fy1": pe, "peg": peg,
            "ev_sales_vs_history": ev_sales_hist, "pe_vs_history": pe_hist, "peg_vs_history": peg_hist,
            "ev_sales_vs_peers": ev_sales_peers, "peg_vs_peers": peg_peers, "n_theme_peers": len(peers),
            "revision_breadth": {"4w": breadth_4w, "13w": breadth_13w},
        },
        "valuation_extreme": valuation_extreme,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def build_expectations(snapshot: dict, cfg: dict, *, state_dir: Path, as_of: str,
                       watchlist_path: Path = None, notes_dir: Path = NOTES_DIR,
                       reads_path: Path = READS_PATH, polarity_path: Path = POLARITY_PATH,
                       stages_path: Path = STAGES_PATH, credibility_store=None,
                       fundamentals: dict | None = None) -> dict:
    tickers_snapshot = snapshot.get("tickers") or {}

    ticker_themes_all = load_ticker_themes(watchlist_path, notes_dir)
    stages = {}
    stages_path = Path(stages_path)
    if stages_path.exists():
        stages = json.loads(stages_path.read_text(encoding="utf-8"))
    reads_rows = _read_jsonl(Path(reads_path)) if Path(reads_path).exists() else []

    try:
        downside_theme_slugs = theme_polarity.competition_slugs(polarity_path, watchlist_path or theme_polarity.WATCHLIST_PATH) | \
            theme_polarity.bearish_themes(polarity_path, watchlist_path or theme_polarity.WATCHLIST_PATH)
    except (FileNotFoundError, ValueError):
        downside_theme_slugs = set()

    fundamentals = fundamentals if fundamentals is not None else load_fundamentals(state_dir, as_of)

    cards: dict[str, dict] = {}
    skipped: list[dict] = []
    universe = sorted(set(tickers_snapshot) | set(ticker_themes_all))
    for tk in universe:
        if tk.endswith(".pvt"):
            continue
        entry = tickers_snapshot.get(tk)
        card = build_card(tk, entry, cfg, state_dir=state_dir, as_of=as_of, stages=stages,
                          ticker_themes_all=ticker_themes_all, downside_theme_slugs=downside_theme_slugs,
                          reads_rows=reads_rows, notes_dir=notes_dir, credibility_store=credibility_store,
                          fundamentals=fundamentals, all_entries=tickers_snapshot)
        if card.get("skipped"):
            skipped.append({"ticker": tk, "reason": card["reason"]})
        else:
            cards[tk] = card

    return {"as_of": as_of, "universe_size": len(universe), "cards": cards, "skipped": skipped}


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def write_json(obj: dict, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".valuation-exp-", suffix=".tmp", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, default=str)
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_jsonl(rows: list[dict], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".valuation-exp-", suffix=".tmp", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def expectations_latest(result: dict) -> dict:
    """The tracked rollup shape (state/valuation/expectations_latest.json)."""
    return {"as_of": result["as_of"], "universe_size": result["universe_size"],
           "skipped": result["skipped"], "tickers": result["cards"]}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=None, help="override state/valuation/ (fixtures/tests)")
    ap.add_argument("--config", default=None, help="override config/valuation.yaml")
    ap.add_argument("--watchlist", default=None, help="override config/watchlist.yaml")
    ap.add_argument("--notes-dir", default=None, help="override notes/")
    ap.add_argument("--reads-path", default=None, help="override state/thesis/reads.jsonl")
    ap.add_argument("--polarity-path", default=None, help="override config/theme_polarity.yaml")
    ap.add_argument("--stages-path", default=None, help="override state/topics/stages.json")
    ap.add_argument("--date", default=None, help="override as_of date (YYYY-MM-DD)")
    ap.add_argument("--print-tickers", default="", help="comma-separated tickers to pretty-print")
    args = ap.parse_args(argv)

    state_dir = Path(args.state_dir) if args.state_dir else STATE_DIR
    cfg_path = Path(args.config) if args.config else CONFIG_PATH
    watchlist_path = Path(args.watchlist) if args.watchlist else None
    notes_dir = Path(args.notes_dir) if args.notes_dir else NOTES_DIR
    reads_path = Path(args.reads_path) if args.reads_path else READS_PATH
    polarity_path = Path(args.polarity_path) if args.polarity_path else POLARITY_PATH
    stages_path = Path(args.stages_path) if args.stages_path else STAGES_PATH

    latest_path = state_dir / "latest.json"
    if not latest_path.exists():
        print(f"ABORTED: {latest_path} not found -- run snapshot.py first", file=sys.stderr)
        return 1
    snapshot = json.loads(latest_path.read_text(encoding="utf-8"))
    as_of = args.date or snapshot.get("as_of") or date.today().isoformat()
    cfg = load_config(cfg_path)

    result = build_expectations(snapshot, cfg, state_dir=state_dir, as_of=as_of, watchlist_path=watchlist_path,
                                notes_dir=notes_dir, reads_path=reads_path, polarity_path=polarity_path,
                                stages_path=stages_path)
    write_jsonl(list(result["cards"].values()), state_dir / f"expectations_{as_of}.jsonl")
    write_json(expectations_latest(result), state_dir / "expectations_latest.json")
    print(f"expectations_latest.json: {len(result['cards'])} cards, {len(result['skipped'])} skipped "
         f"(universe {result['universe_size']})")

    for tk in [t.strip() for t in args.print_tickers.split(",") if t.strip()]:
        card = result["cards"].get(tk)
        if not card:
            skip = next((s for s in result["skipped"] if s["ticker"] == tk), None)
            print(f"\n=== {tk}: SKIPPED ({skip['reason'] if skip else 'not found'}) ===")
            continue
        print(f"\n=== {tk} ===")
        print(json.dumps(card, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
