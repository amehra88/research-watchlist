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

Fundamentals (net debt, margins) are OPTIONAL: when scripts/valuation/fundamentals.py has
no row for a ticker, that ticker's card falls back to the sector-family defaults (flagged
"no_net_debt" / "margin_default"). As of RIS5 A5 fix round 3 (2026-09-17, after A3 fix
round 4's LTM/FF_SALES fix), fundamentals ARE live for 176/178 tickers: `net_debt` reads
straight off the `net_debt` row; `fcf_margin` is READ, not derived here any more --
`fundamentals.py` itself now derives it (`FF_FREE_CF / FF_SALES * 100`, both legs from the
same LTM-periodicity call) and this module just converts the percentage to a fraction
(see `read_fcf_margin()`). `no_net_debt`/`margin_default` still fire for the 2 tickers
with zero fundamentals coverage. A NEGATIVE `fcf_margin` (32 tickers on the live pull,
e.g. COHR -14.5%) is real FactSet data, not a bug: the margin PATH's starting point is
floored at 0 (flag `fcf_margin_floored`, raw value kept in `inputs.fcf_margin_now_raw`)
so the card still builds; if the LTM operating margin is ALSO <= 0 (genuinely pre-profit),
the card is marked `long_duration` with reason `pre_profit` instead of silently pretending
a real read on it is possible. `fcf_margin_floored` is NOT one of
`is_valuation_extreme()`'s veto flags (only `margin_default`/`no_net_debt` are, unchanged)
-- a floored-but-real margin is not a guess.

CLI:
    python3 scripts/valuation/expectations.py --state-dir /tmp/snap ... # explicit fixture/live run

Fix round 1 (RIS5 A5, this revision) rewrites Layer 2 (a fade, not a flat multiplier),
fixes valuation_extreme/priced-in to hold across the sensitivity band, moves PEG to
EPS-based growth, adds a forward growth-adjusted multiple LADDER (amendment v1.2) with a
`long_duration` gate, and adds provenance to every card. See task-5-report.md's "Fix
round 1" section for the full formula writeup and the binding-ruling-by-ruling mapping.
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

REPO = Path(__file__).resolve().parents[2]   # RIS5 A5 fix round 1, C2: derive from __file__
                                             # (parents[2]: scripts/valuation/expectations.py ->
                                             # scripts/valuation -> scripts -> repo root) so the
                                             # documented cron/CLI invocation reproduces the same
                                             # cards from WHICHEVER checkout this file lives in --
                                             # the previous hardcoded "/root/research-watchlist"
                                             # always pointed at the main checkout even when this
                                             # module was imported from a worktree, silently
                                             # reading the wrong config/notes/state. Explicit CLI
                                             # flags (--state-dir/--config/--watchlist/etc) still
                                             # override every default below. READ-ONLY
                                             # config/notes/state paths only -- NEVER used to
                                             # resolve sibling imports (see snapshot.py's own "REPO
                                             # trap" docstring): imports below resolve via
                                             # __file__/_SCRIPTS_DIR instead, unaffected by this.
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


def read_ltm_fcf_margin(fnd: dict) -> float | None:
    """The LTM FCF margin as a 0-1 FRACTION, or None when the ticker has no fundamentals
    row. `fundamentals_<date>.jsonl` carries `fcf_margin` PRE-DERIVED by A3's
    `fundamentals.py` (`FF_FREE_CF / FF_SALES * 100`, both legs from the SAME
    LTM-periodicity call, matched on `fiscal_end`) as a PERCENTAGE (e.g. NVDA `39.68`),
    matching `gross_margin`/`operating_margin`'s own convention -- this module converts,
    it derives nothing. May be NEGATIVE (32 tickers on the live pull, e.g. COHR -14.5%):
    real data, handled by select_start_margin()'s ladder, not a defect."""
    raw = fnd.get("fcf_margin")
    return None if raw is None else raw / 100.0


def select_terminal_margin(entry: dict, term_default: float) -> tuple[float, list[str]]:
    """RIS5 A5 fix round 4, V3: the margin END is NAME-SPECIFIC -- `fy3_fcf / fy3_sales`
    (consensus, the last forecast year on the working horizon) whenever both legs are
    positive, else the sector-family default from config/valuation.yaml. One sector
    number applied to every name in a family was the single largest unearned assumption
    in the reverse-DCF: it set how much of EV the terminal value explains, and therefore
    most of the implied growth. Flags: `terminal_margin_consensus` / `terminal_margin_default`
    (the latter is a VETO flag for `valuation_extreme` -- see _VALUATION_EXTREME_VETO_FLAGS)."""
    fy3_fcf, fy3_sales = entry.get("fy3_fcf"), entry.get("fy3_sales")
    if fy3_fcf is not None and fy3_sales is not None and fy3_fcf > 0 and fy3_sales > 0:
        return fy3_fcf / fy3_sales, ["terminal_margin_consensus"]
    return term_default, ["terminal_margin_default"]


def consensus_margin(fcf, sales) -> float | None:
    """fcf/sales when `sales` > 0 (the RAW margin, which may be negative); None when the
    denominator is missing/nonpositive."""
    if fcf is None or sales is None or sales <= 0:
        return None
    return fcf / sales


def select_start_margin(entry: dict, fnd: dict) -> tuple[float, float | None, list[str]]:
    """RIS5 A5 fix round 4, V3 (amendment v1.2: "every lens is computed on consensus
    estimates, never trailing figures"): the margin path's START is FORWARD, never
    trailing --
      1. `fy1_fcf / fy1_sales` when both > 0            -> flag `start_margin_consensus`
      2. else the LTM `fcf_margin` when > 0             -> flag `start_margin_ltm`
      3. else floored at 0                              -> flag `fcf_margin_floored`
    -> (used, raw, flags). `raw` is the unfloored number the floor replaced (the FORWARD
    consensus margin when computable at all, else the LTM one, else None) and is kept on
    the card as `inputs.fcf_margin_now_raw` so a reader sees both what was assumed and
    what the real number was. `fcf_margin_floored` is a VETO flag for `valuation_extreme`
    (V4: EQIX +25.5 / CEG +17.9 were floor artefacts, not valuation signals)."""
    fwd = consensus_margin(entry.get("fy1_fcf"), entry.get("fy1_sales"))
    ltm = read_ltm_fcf_margin(fnd)
    raw = fwd if fwd is not None else ltm
    if fwd is not None and fwd > 0:
        return fwd, fwd, ["start_margin_consensus"]
    if ltm is not None and ltm > 0:
        return ltm, raw, ["start_margin_ltm"]
    return 0.0, raw, ["fcf_margin_floored"]


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
_UNOBSERVED_MARKER_KEYS = ("gated", "stage4_not_assertable", "unheard")


def read_stage(stages: dict, theme: str, ticker: str) -> int | None:
    """Ordinal stage (1-4) for (theme, ticker), or None if UNOBSERVED (never 0/1).

    RIS5 A5 fix round 1, C6: THREE marker lists gate a pair to unobserved --
    `gated`, `stage4_not_assertable`, and `unheard` (amendment v1.1 #1's own list of
    what a consumer must honour) -- not just `gated` alone. Each may carry theme-level
    entries (bare theme name, e.g. "agentic_commerce" -- gates every ticker under that
    theme) or pair-level entries ("theme|TICKER" -- gates just that pair); both forms
    are checked against all three lists. `pairs` values are tolerated as a bare int
    (the live 2026-09-16 shape) or a dict carrying a `stage` key (the brief's
    documented shape) -- a one-line adaptation if PR #6 changes this again.
    """
    for key in _UNOBSERVED_MARKER_KEYS:
        markers = set(stages.get(key) or [])
        if theme in markers or f"{theme}|{ticker}" in markers:
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
def read_credibility(ticker: str, metric: str = "SALES", store=None) -> tuple[dict | None, list[str], str]:
    """-> (cred, flags, credibility_source). `credibility_source` is "pg" | "file" | "none"
    (RIS5 A5 fix round 0, item 2): honours `CHUNK_STORE_BACKEND` exactly the way
    `store_b.get_metrics_store()` itself does (this module never sets that env var --
    the production Sunday Store B cron sources /root/podcasts/.env, which pins
    CHUNK_STORE_BACKEND=pg; a live run of this module must be invoked the same way, see
    the CLI section / A5 report for the exact command). "none" means the lookup itself
    failed (store resolution/connection raised), not merely that no row was found for
    this ticker -- an empty-but-successful lookup still reports the real backend name
    and is separately flagged "no_credibility".

    `store` is duck-typed (`.credibility(ticker, metric) -> dict|None`) so tests inject a
    fixture without ever calling get_metrics_store() -- no live DB is opened in tests
    regardless of what CHUNK_STORE_BACKEND happens to be set to in the environment,
    because `store_b.get_metrics_store()` is only reached when `store is None`.
    """
    import os
    backend = os.environ.get("CHUNK_STORE_BACKEND", "file").lower()
    source = backend if backend in ("pg", "file") else "file"
    try:
        st = store if store is not None else store_b.get_metrics_store()
        cred = st.credibility(ticker, metric)
    except Exception:                                                    # noqa: BLE001
        return None, ["no_credibility"], "none"
    if not cred:
        return None, ["no_credibility"], source
    return cred, [], source


def build_credibility_cache(tickers: list[str], store=None) -> dict[str, tuple]:
    """{ticker: (cred, flags, source)} -- ONE store read per ticker, reused for both the
    per-ticker credibility_term() AND the cross-sectional median (F6: "same store
    read")."""
    return {tk: read_credibility(tk, store=store) for tk in tickers}


def _avg_rate_from_cred(cred: dict | None) -> float | None:
    if not cred:
        return None
    vals = [r for r in (cred.get("consensus_beat_rate"), cred.get("guide_hit_rate")) if r is not None]
    return statistics.mean(vals) if vals else None


def credibility_cross_median(cache: dict[str, tuple]) -> float | None:
    """F6: the cross-sectional median of the universe's avg_rate at run time, from the
    SAME store read as credibility_term() (via `cache` = build_credibility_cache()).
    None if the cross-section is unavailable (no ticker in the universe has usable
    credibility data this run)."""
    rates = [r for r in (_avg_rate_from_cred(cred) for cred, _flags, _source in cache.values())
            if r is not None]
    return statistics.median(rates) if rates else None


# ---------------------------------------------------------------------------
# Reads-trend reader (state/thesis/reads.jsonl)
# ---------------------------------------------------------------------------
_DIRECTION_SIGN = {"up": 1.0, "flat": 0.0, "down": -1.0}


def _read_signed(row: dict) -> float:
    sign = _DIRECTION_SIGN.get(row.get("direction"), 0.0)
    mag = row.get("magnitude") or 0
    return sign * (mag / 2.0)   # magnitude 0-2 -> normalized to [-1, 1] combined with sign


def reads_latest_date(ticker: str, reads_rows: list[dict]) -> str | None:
    """C5 provenance: the most recent dated read (any axis) for `ticker`, or None."""
    dates = [r["date"] for r in reads_rows if r.get("ticker") == ticker and r.get("date")]
    return max(dates) if dates else None


def reads_term(ticker: str, reads_rows: list[dict], cfg: dict) -> tuple[float, list[str], dict]:
    """Amendment-measured 2026-09-17: only 8/178 tickers clear >=3 dated reads on any
    SINGLE axis, but they clear it on every one of the 5 structured-read axes (same
    source notes). Average across every axis for this ticker that individually clears
    the `reads_min_dated` gate; omit axes that don't. Zero qualifying axes -> term 0.0,
    flagged "insufficient history: reads trend" (never silently 0 without saying so)."""
    min_dated = (cfg.get("supported_growth") or {}).get("reads_min_dated", 3)
    bound = ((cfg.get("supported_growth") or {}).get("durability") or {}).get("reads_term_bound", 1.0 / 6)

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
def stage_rank_term(ticker: str, stages: dict, cfg: dict) -> tuple[float, list[str], dict]:
    """Ordinal stage rank vs. the ticker's peer-median stage (amendment v1.1 #6: NEVER a
    linear stage number) -- RIS5 A5 fix round 0, item 1: the ticker's themes come from
    its OWN EVIDENCE-DERIVED pairs in `stages.json` (every `pairs` key ending in
    "|TICKER"), not `config/watchlist.yaml`'s static theme tags. The two are different
    association spaces (topic_map's detected exchange associations vs. an operator-set
    tag list) and the static tags rarely intersect stages.json's real coverage, which
    was starving this term to `no_stage_data` for almost every ticker.

    For each theme where the ticker has an observed (non-gated) stage: peers = every
    OTHER ticker with an observed, non-gated pair for that same theme (found by scanning
    `pairs` keys with the "theme|" prefix -- unobserved/gated tickers are excluded from
    both the ticker's own numerator and the peer set, via `read_stage()`'s own gating);
    delta = peer_median_stage - ticker_stage (positive = ticker is EARLIER stage than
    its peers = longer runway = more durable). Combined across the ticker's qualifying
    themes via the MEDIAN delta (not the mean -- one outlier theme should not swing the
    whole term), scaled by `stage_term_per_level`, clipped to `stage_term_bound`.

    `no_stage_data` fires only when the ticker has ZERO observed pairs of its own
    anywhere in `stages.json` -- not when its watchlist tags happen not to overlap.
    """
    durability = (cfg.get("supported_growth") or {}).get("durability") or {}
    bound = durability.get("stage_term_bound", 1.0 / 6)
    per_level = durability.get("stage_term_per_level", 0.05)

    pairs = stages.get("pairs") or {}
    my_themes = sorted({k.split("|", 1)[0] for k in pairs if k.endswith(f"|{ticker}")})

    deltas = []
    themes_used = []
    per_theme_deltas: dict[str, float] = {}
    for theme in my_themes:
        my_stage = read_stage(stages, theme, ticker)
        if my_stage is None:            # gated pair-level or theme-level -> unobserved
            continue
        prefix = f"{theme}|"
        peer_stages = []
        for key in pairs:
            if not key.startswith(prefix):
                continue
            other = key.split("|", 1)[1]
            if other == ticker:
                continue
            s = read_stage(stages, theme, other)
            if s is not None:
                peer_stages.append(s)
        if not peer_stages:
            continue
        peer_median = statistics.median(peer_stages)
        delta = peer_median - my_stage
        deltas.append(delta)
        themes_used.append(theme)
        per_theme_deltas[theme] = delta

    if not deltas:
        return 0.0, ["no_stage_data"], {"themes_used": [], "peer_basis": "evidence_pairs"}

    combined_delta = statistics.median(deltas)
    term = _clip(combined_delta * per_level, -bound, bound)
    return term, [], {"themes_used": themes_used, "combined_stage_rank_delta": combined_delta,
                      "per_theme_deltas": per_theme_deltas, "peer_basis": "evidence_pairs"}


def _cred_date_range_max(cred: dict) -> str | None:
    dr = cred.get("date_range")
    return max(dr) if isinstance(dr, list) and dr else None


def credibility_term(ticker: str, cfg: dict, store=None, cross_median: float | None = None,
                     cred_entry: tuple | None = None) -> tuple[float, list[str], dict]:
    """RIS5 A5 fix round 1, F6: centred on `cross_median` (the cross-sectional median of
    the universe's avg_rate at run time -- see credibility_cross_median()), not a fixed
    0.5. `cross_median is None` means the cross-section was unavailable (no ticker in the
    universe had usable credibility data) -- term is neutral (0.0) with flag
    `credibility_uncentred`, distinct from `no_credibility` (this ticker itself has no
    data). `cred_entry` (from build_credibility_cache()) lets the caller reuse the SAME
    store read used to compute `cross_median`, rather than a second read per ticker."""
    durability = (cfg.get("supported_growth") or {}).get("durability") or {}
    bound = durability.get("credibility_term_bound", 1.0 / 6)
    cred, flags, source = cred_entry if cred_entry is not None else read_credibility(ticker, store=store)
    if not cred:
        return 0.0, flags, {"source": source, "credibility_as_of": None}
    avg_rate = _avg_rate_from_cred(cred)
    as_of_val = _cred_date_range_max(cred)
    if avg_rate is None:
        return 0.0, ["no_credibility"], {"source": source, "credibility_as_of": as_of_val}
    if cross_median is None:
        return 0.0, ["credibility_uncentred"], {"avg_rate": avg_rate, "n_rates": 2 if cred.get("guide_hit_rate")
                                                is not None and cred.get("consensus_beat_rate") is not None else 1,
                                                "source": source, "credibility_as_of": as_of_val}
    n_rates = sum(1 for r in (cred.get("consensus_beat_rate"), cred.get("guide_hit_rate")) if r is not None)
    scale = bound / 0.5   # avg_rate in [0,1] -> max deviation from median is 0.5 -> hits `bound` at the extreme
    term = _clip((avg_rate - cross_median) * scale, -bound, bound)
    return term, [], {"avg_rate": avg_rate, "n_rates": n_rates, "source": source,
                      "cross_median": cross_median, "credibility_as_of": as_of_val}


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


def load_downside_theme_slugs(polarity_path: Path, watchlist_path: Path) -> tuple[set[str], bool]:
    """-> (slugs, polarity_unavailable). RIS5 A5 fix round 1, C1: a missing/unreadable
    config/theme_polarity.yaml must NEVER silently look like "no assumption challenged"
    -- callers check `polarity_unavailable` and null out challenged_assumption_ids/
    downside/gap_downside rather than treating an empty slug set as a real answer."""
    try:
        slugs = (theme_polarity.competition_slugs(polarity_path, watchlist_path) |
                theme_polarity.bearish_themes(polarity_path, watchlist_path))
        return slugs, False
    except (FileNotFoundError, ValueError, OSError):
        return set(), True


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
# Layer 2 — supported_growth (RIS5 A5 fix round 1, F3: a fade, not a flat
# multiplier)
# ---------------------------------------------------------------------------
def two_yr_cagr(v1: float | None, v3: float | None) -> float | None:
    """2-year CAGR from a FY1->FY3 pair (or any two values 2 periods apart) -- the
    generic form `near_term_cagr` and the amendment-v1.2 ladder rungs (EPS/EBITDA/FCF
    CAGR) all share."""
    if not v1 or not v3 or v1 <= 0 or v3 <= 0:
        return None
    return (v3 / v1) ** (1.0 / 2.0) - 1.0


def near_term_cagr(fy1_sales, fy3_sales) -> float | None:
    return two_yr_cagr(fy1_sales, fy3_sales)


def eps_breadth_ratio(entry: dict) -> tuple[float, list[str]]:
    """V1's `breadth_ratio` leg: `(up - down) / (up + down)` on the snapshot's FY1 **EPS**
    revision counts (the 4-week FactSet window the daily pull carries; the
    `breadth_semantics_unverified` caveat on every card applies here too). EPS, not sales
    and not FCF: the street's own conviction in the earnings line is what a growth haircut
    should lean on, and the three metrics genuinely disagree (NVDA fy1_eps 42up/2down =
    +0.909 vs fy1_fcf 5up/10down = -0.333). 0.0 + flag `lambda_breadth_na` when the counts
    are missing or nobody revised."""
    up = (entry.get("up") or {}).get("fy1_eps")
    down = (entry.get("down") or {}).get("fy1_eps")
    if up is None or down is None or (up + down) == 0:
        return 0.0, ["lambda_breadth_na"]
    return (up - down) / (up + down), []


def street_lambda(cred_avg_rate: float | None, breadth_ratio: float, fy1_sales_musd: float | None,
                  cfg: dict) -> tuple[float, dict, list[str]]:
    """RIS5 A5 fix round 4, V1 -- the STREET HAIRCUT, binding formula:

        lambda = clip(0.75 + 0.25*(2*cred - 1) + 0.15*breadth_ratio
                      - 0.20*clip(log10(fy1_sales_musd / 10000), 0, 1), 0.50, 1.00)

    Why it exists: through fix round 3 the "evidence" leg of supported growth was inert
    (median |base - neutral| was 0.00pp across the live universe -- the three durability
    terms cancelled to nothing almost everywhere), so `supported.base` was, in practice,
    the consensus CAGR restated. A haircut on the STREET's own forecast, driven by
    things that are actually observed per name -- the company's guidance/consensus track
    record (`cred`), the current direction of FY1 EPS revisions, and size (a $400bn-sales
    company cannot compound like a $2bn one) -- gives the gap a second leg that moves.

    `cred` is the credibility avg_rate (mean of consensus_beat_rate/guide_hit_rate);
    0.5 (neutral) with flag `lambda_cred_default` when the ticker has no record. The size
    term is 0 below $10bn of FY1 sales and reaches its full -0.20 at $100bn+ (log10 of the
    ratio to $10bn, clipped to [0,1]). lambda is then applied as a shrinkage of the street
    CAGR toward terminal growth: `cagr_used = tg + (cagr_street - tg) * lambda`.
    NOTE the shrinkage is toward tg in BOTH directions: for the rare name whose consensus
    CAGR is BELOW terminal growth, lambda < 1 raises it. That is inherent to shrinkage
    toward a central value and is left as written, not special-cased."""
    hc = (cfg.get("supported_growth") or {}).get("street_haircut") or {}
    base_const = hc.get("base_const", 0.75)
    cred_w = hc.get("cred_weight", 0.25)
    breadth_w = hc.get("breadth_weight", 0.15)
    size_w = hc.get("size_weight", 0.20)
    size_ref = hc.get("size_ref_musd", 10000.0)
    lo, hi = hc.get("bounds", [0.50, 1.00])

    flags: list[str] = []
    cred = cred_avg_rate
    if cred is None:
        cred = 0.5
        flags.append("lambda_cred_default")
    cred_term = cred_w * (2.0 * cred - 1.0)
    breadth_term = breadth_w * breadth_ratio
    if fy1_sales_musd and fy1_sales_musd > 0:
        size_raw = _clip(__import__("math").log10(fy1_sales_musd / size_ref), 0.0, 1.0)
    else:
        size_raw = 0.0
    size_term = -size_w * size_raw
    lam = _clip(base_const + cred_term + breadth_term + size_term, lo, hi)
    terms = {"base_const": base_const, "cred": cred, "cred_term": cred_term,
             "breadth_ratio": breadth_ratio, "breadth_term": breadth_term,
             "size_log10_clipped": size_raw, "size_term": size_term,
             "fy1_sales_musd": fy1_sales_musd}
    return lam, terms, flags


def fade_growth_path(cagr: float, terminal_growth: float, durability_score: float) -> dict:
    """F3's binding formula: years 1-3 at `cagr` (the consensus FY1->FY3 CAGR), years 4-5
    at `g_fade = tg + (cagr - tg) * persistence`, `persistence = clip(0.5 + durability_score,
    0, 1)`. At durability_score == 0 (neutral evidence), persistence == 0.5 and the path
    fades HALFWAY to terminal growth by year 4-5 -- the "centres on a fade" default.
    Positive evidence (durability_score > 0) moves persistence toward 1 (g_fade -> cagr,
    i.e. the near-term rate persists); negative evidence moves it toward 0 (g_fade -> tg,
    full fade). `base` is the single 5-year CAGR that compounds to the same terminal value
    as the two-stage path: (1+cagr)^3 * (1+g_fade)^2 = (1+base)^5."""
    persistence = _clip(0.5 + durability_score, 0.0, 1.0)
    g_fade = terminal_growth + (cagr - terminal_growth) * persistence
    factor = (1.0 + cagr) ** 3 * (1.0 + g_fade) ** 2
    base = factor ** (1.0 / 5.0) - 1.0
    return {"g_fade": g_fade, "persistence": persistence, "base": base}


def supported_growth(ticker: str, entry: dict, cfg: dict, *, stages: dict,
                     ticker_themes_all: dict[str, list[str]], reads_rows: list[dict],
                     thesis_fm: dict | None, downside_theme_slugs: set[str],
                     polarity_unavailable: bool = False, terminal_growth: float = 0.03,
                     credibility_store=None, credibility_cross_median: float | None = None,
                     credibility_entry: tuple | None = None) -> dict:
    """F3's fade path (see fade_growth_path()) extended by a durability_score built from
    3 independently-clipped terms (stage rank, credibility, reads trend; each +/- 1/6
    max, so durability_score in [-0.5, +0.5]). F5: downside = base * downside_multiplier
    (relative, default 0.85) applied once when >=1 qualifying assumption is `challenged`.
    C1: `polarity_unavailable` (config/theme_polarity.yaml missing/unreadable) nulls
    challenged_assumption_ids AND downside -- never silently reads as "no assumption
    challenged".

    `ticker_themes_all` is no longer read for the stage term (fix round 0, item 1 --
    stage_rank_term() derives the ticker's themes from stages.json's own evidence pairs,
    not watchlist.yaml's static tags); the parameter is kept for API stability (peer
    lenses / theme_peers() elsewhere still use it)."""
    flags: list[str] = []

    cagr_street = near_term_cagr(entry.get("fy1_sales"), entry.get("fy3_sales"))
    if cagr_street is None:
        base_flags = ["missing fy1/fy3 sales for CAGR"]
        if polarity_unavailable:
            base_flags.append("polarity_unavailable")
        return {"base": None, "base_street": None, "downside": None, "near_term_cagr": None,
                "cagr_street": None, "cagr_used": None, "lambda_street": None, "lambda_terms": {},
                "g_fade": None, "persistence": None, "durability_score": None,
                "drivers": {}, "challenged_assumption_ids": None if polarity_unavailable else [],
                "flags": base_flags}

    st_term, st_flags, st_detail = stage_rank_term(ticker, stages, cfg)
    cr_term, cr_flags, cr_detail = credibility_term(ticker, cfg, store=credibility_store,
                                                    cross_median=credibility_cross_median,
                                                    cred_entry=credibility_entry)
    rd_term, rd_flags, rd_detail = reads_term(ticker, reads_rows, cfg)
    flags.extend(st_flags); flags.extend(cr_flags); flags.extend(rd_flags)

    ds_lo, ds_hi = ((cfg.get("supported_growth") or {}).get("durability") or {}).get(
        "durability_score_bounds", [-0.5, 0.5])
    durability_score = _clip(st_term + cr_term + rd_term, ds_lo, ds_hi)

    # V1: haircut the STREET's own CAGR before extending it (see street_lambda()).
    cred_for_lambda = cr_detail.get("avg_rate")   # same store read as credibility_term()
    breadth_ratio, breadth_flags = eps_breadth_ratio(entry)
    lam, lambda_terms, lam_flags = street_lambda(cred_for_lambda, breadth_ratio,
                                                 entry.get("fy1_sales"), cfg)
    flags.extend(lam_flags); flags.extend(breadth_flags)
    cagr_used = terminal_growth + (cagr_street - terminal_growth) * lam

    fade = fade_growth_path(cagr_used, terminal_growth, durability_score)
    fade_street = fade_growth_path(cagr_street, terminal_growth, durability_score)
    lo, hi = (cfg.get("supported_growth") or {}).get("base_bounds", [-0.5, 2.0])
    base = _clip(fade["base"], lo, hi)
    if base != fade["base"]:
        flags.append("supported_growth_clipped")
    # V2: a hard cap on what the evidence is ever allowed to support. Uncapped, a handful
    # of very-early-revenue names (CBRS 153%, NBIS 118% on the fix-round-3 run) produced
    # supported bases no company sustains for five years and, being the subtrahend of
    # every gap, dominated the cross-section (and therefore gap_z for every OTHER card).
    # The cap is on `base` ONLY -- `base_street` is the printed lambda=1 diagnostic and is
    # left uncapped, so the haircut stays visible exactly where it does the most work.
    base_cap = (cfg.get("supported_growth") or {}).get("base_cap", 0.40)
    if base_cap is not None and base > base_cap:
        base = base_cap
        flags.append("supported_capped")
    base_street = _clip(fade_street["base"], lo, hi)

    downside_mult = (cfg.get("supported_growth") or {}).get("downside_multiplier", 0.85)
    if polarity_unavailable:
        challenged_ids = None
        downside = None
        flags.append("polarity_unavailable")
    else:
        challenged_ids = challenged_downside_assumptions(thesis_fm, downside_theme_slugs)
        downside_raw = base * downside_mult if challenged_ids else base
        downside = _clip(downside_raw, lo, hi)

    return {
        "base": base, "base_street": base_street, "downside": downside,
        # `near_term_cagr` is kept as an alias of `cagr_street` (the raw consensus FY1->FY3
        # CAGR) so nothing that already read it changes meaning; `cagr_used` is what the
        # fade path actually ran on after V1's haircut.
        "near_term_cagr": cagr_street, "cagr_street": cagr_street, "cagr_used": cagr_used,
        "lambda_street": lam, "lambda_terms": lambda_terms,
        "g_fade": fade["g_fade"], "persistence": fade["persistence"],
        "durability_score": durability_score,
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
    while every margin_t > 0 and discount_rate > terminal_growth).

    NOTE: `margin_path_nonpositive` is also checked directly in build_card() BEFORE this
    is even called, per C6 -- a nonpositive margin path SKIPS the whole ticker (no
    partial card), rather than building a card with growth=None. This function's own
    guard stays as defence-in-depth for direct callers (tests, sensitivity re-solves)."""
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


def terminal_share_of_ev(g: float | None, fy0_sales: float, fcf_margin_now: float, terminal_margin: float,
                         discount_rate: float, terminal_growth: float, years: int,
                         ev: float | None) -> float | None:
    """L2 (amendment v1.2): PV of the terminal value / EV, at the solved (or
    bracket-clipped) growth `g`. None if `g` is None (a guard already failed) or `ev` is
    falsy/None. Convention (F4): the terminal value is computed off the SAME margin path
    used by the explicit 5-year PV stream (years 1..5 all discounted -- there is no
    separate "year 0" FCF; fy0_sales is the anchor consensus FY1 sales estimate that
    year-1 growth is applied to, per the module's fy0_sales interpretive call)."""
    if g is None or not ev:
        return None
    margins = _margin_path(fcf_margin_now, terminal_margin, years)
    if any(m <= 0 for m in margins) or discount_rate - terminal_growth <= 0:
        return None
    fcf_years = fy0_sales * (1.0 + g) ** years * margins[-1]
    tv = fcf_years * (1.0 + terminal_growth) / (discount_rate - terminal_growth)
    tv_pv = tv / (1.0 + discount_rate) ** years
    return tv_pv / ev


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
    tshare = terminal_share_of_ev(core["growth"], fy0_sales, fcf_margin_now, terminal_margin,
                                  discount_rate, terminal_growth, years, ev)
    return {
        "implied_growth_5y": core["growth"],
        "implied_terminal_margin": terminal_margin,   # echoed input, not solved (2 unknowns, 1 equation)
        "pv_residual_check": core["pv_at_growth"],    # RIS5 A5 fix round 1, C7: renamed from
                                                       # pv_at_growth (a solve-quality residual
                                                       # check, not a valuation OUTPUT) -- build_card()
                                                       # drops it before it reaches a written card.
        "terminal_share_of_ev": tshare,               # amendment v1.2, L2: PV(terminal value) / EV
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


def compute_gap_ranges(sensitivity: dict, supported_base, supported_downside) -> tuple[list | None, list | None]:
    """RIS5 A5 fix round 1, F1: `gap_range`/`gap_downside_range` = [min, max] of the gap
    computed from EACH of the four sensitivity re-solves (dr_plus/dr_minus/tm_plus/
    tm_minus) against supported.base/downside -- NOT including the point-estimate
    implied_growth_5y itself (the brief's exact wording: "the four re-solves"). None
    values among the four re-solves (a guard tripped for that variant) are excluded, not
    treated as 0. None entirely if supported_base/downside itself is None, or if every
    re-solve failed."""
    def _range(supported):
        if supported is None:
            return None
        vals = [(g - supported) * 100 for g in sensitivity.values() if g is not None]
        return [round(min(vals), 4), round(max(vals), 4)] if vals else None
    return _range(supported_base), _range(supported_downside)


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


_MAD_CONSISTENCY = 1.4826   # scales MAD to be a consistent estimator of stdev under normality


def peer_lens(value: float | None, peer_values: list[float], min_peers_for_z: int) -> dict:
    """RIS5 A5 fix round 1, C7: named `peer_score` (not `peer_z`) and built from a
    median/MAD spread, not mean/stdev -- robust to the single outlier peer that a
    3-6-name theme-peer group is prone to (one wildly mispriced peer would otherwise blow
    up the whole group's stdev). `peer_score` is still interpretable like a z-score
    (MAD is scaled by the normal-consistency constant 1.4826) but is not literally one,
    hence the rename."""
    peer_values = [v for v in peer_values if v is not None]
    if not peer_values:
        return {"peer_median": None, "peer_score": None, "n_peers": 0, "flags": ["no_peers"]}
    median = statistics.median(peer_values)
    if len(peer_values) < min_peers_for_z or value is None:
        return {"peer_median": median, "peer_score": None, "n_peers": len(peer_values),
                "flags": ["insufficient peers for score"]}
    mad = statistics.median([abs(v - median) for v in peer_values])
    if mad == 0:
        return {"peer_median": median, "peer_score": None, "n_peers": len(peer_values), "flags": ["zero_variance"]}
    scaled_mad = mad * _MAD_CONSISTENCY
    return {"peer_median": median, "peer_score": (value - median) / scaled_mad,
           "n_peers": len(peer_values), "flags": []}


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


def load_history_cache(state_dir: Path, exclude_date: str | None = None) -> dict[str, dict[str, dict]]:
    """{date: {ticker: entry}} for every accrued dated snapshot under state_dir except
    `exclude_date` (the current as_of day, so "own history" never includes the point
    being scored). RIS5 A5 fix round 0, item 3: built ONCE per build_expectations() run
    and shared across every ticker and every lens (own-history z x3 + revision breadth
    x2 per ticker) -- before this, history_series()/revision_breadth() each re-scanned
    and re-parsed the SAME dated prices_*.jsonl/consensus_*.jsonl files independently,
    once per (ticker, lens): O(5 x N_tickers x N_days) full-universe build_latest()
    passes over what is really N_days of work. At the real ~178-ticker universe accruing
    daily for months this was the dominant cost; the cache makes it O(N_days)."""
    cache: dict[str, dict[str, dict]] = {}
    for d in dated_snapshot_dates(state_dir):
        if d == exclude_date:
            continue
        cache[d] = load_dated_tickers(state_dir, d)
    return cache


def history_series(ticker: str, history_cache: dict[str, dict[str, dict]], lens_fn) -> list[float]:
    """lens_fn(entry) -> float|None, applied to `ticker`'s entry on every cached date.
    Dates where the ticker is absent, or lens_fn returns None, are skipped (not counted
    toward n_days). `history_cache` comes from load_history_cache() -- already excludes
    the as_of day and is shared across every ticker/lens in one build_expectations() run."""
    out = []
    for tickers in history_cache.values():
        entry = tickers.get(ticker)
        if entry is None:
            continue
        v = lens_fn(entry)
        if v is not None:
            out.append(v)
    return out


def revision_breadth(ticker: str, entry_now: dict, history_cache: dict[str, dict[str, dict]], as_of: str,
                     weeks: int, key: str = "fy1_sales", tolerance_days: int = 5) -> dict:
    """(up_now - down_now) - (up_then - down_then) for the nearest cached date within
    `tolerance_days` of `weeks` weeks before `as_of`. "n/a" until that much history has
    accrued (brief's own sanctioned degrade). Reads `history_cache` (see
    load_history_cache()) instead of re-scanning state_dir itself (fix round 0, item 3).

    RIS5 A5 fix round 1, C4: the raw `up_now`/`down_now`/`up_then`/`down_then` counts are
    ALWAYS returned alongside `delta` (None where not yet knowable) -- the delta alone
    hides whether a swing came from more upgrades or fewer downgrades, which matters for
    reading the number. The card also carries a standing `breadth_semantics_unverified`
    flag (see build_card()): whether FactSet's `up`/`down` are CUMULATIVE (since the
    estimate's inception) or TRAILING (since the last snapshot) is not yet confirmed
    against two real production snapshots (TODO)."""
    up_now = (entry_now.get("up") or {}).get(key)
    down_now = (entry_now.get("down") or {}).get(key)
    if up_now is None or down_now is None:
        return {"delta": None, "note": "n/a", "up_now": up_now, "down_now": down_now,
               "up_then": None, "down_then": None}
    target = date.fromisoformat(as_of) - __import__("datetime").timedelta(days=weeks * 7)
    best_d, best_gap = None, None
    for d in history_cache:
        try:
            dd = date.fromisoformat(d)
        except ValueError:
            continue
        gap = abs((dd - target).days)
        if gap <= tolerance_days and (best_gap is None or gap < best_gap):
            best_d, best_gap = d, gap
    if best_d is None:
        return {"delta": None, "note": "n/a", "up_now": up_now, "down_now": down_now,
               "up_then": None, "down_then": None}
    then_entry = history_cache[best_d].get(ticker)
    if not then_entry:
        return {"delta": None, "note": "n/a", "up_now": up_now, "down_now": down_now,
               "up_then": None, "down_then": None}
    up_then = (then_entry.get("up") or {}).get(key)
    down_then = (then_entry.get("down") or {}).get(key)
    if up_then is None or down_then is None:
        return {"delta": None, "note": "n/a", "up_now": up_now, "down_now": down_now,
               "up_then": None, "down_then": None}
    return {"delta": (up_now - down_now) - (up_then - down_then), "note": None, "compared_to": best_d,
           "up_now": up_now, "down_now": down_now, "up_then": up_then, "down_then": down_then}


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


_VALUATION_EXTREME_VETO_FLAGS = ("margin_default", "terminal_margin_default",
                                 "fcf_margin_floored", "no_net_debt")
# RIS5 A5 fix round 4: V4 adds `fcf_margin_floored` (EQIX +25.5 / CEG +17.9 on the fix
# round 3 run were artefacts of a 0% assumed start margin, not valuation signals).
# `terminal_margin_default` is added for the same reason and is a ruling-gap this round
# closed deliberately: V3 retires the old `margin_default` code path entirely (the start
# ladder is consensus -> LTM -> floor, the terminal end falls back to the sector table
# under its OWN name), so without this the sector-default veto F1 established would have
# gone silently dead for the ~29 names with no positive FY3 consensus FCF. `margin_default`
# itself is kept in the tuple for compatibility although nothing emits it any more.


def is_valuation_extreme(gap_range: list | None, lens_history_z: float | None,
                         flags: list[str], cfg: dict) -> tuple[bool, str | None]:
    """RIS5 A5 fix round 1, F1 (fix round 2, item 2 adds the reason): the gap branch must
    hold across the WHOLE sensitivity band -- fires only when `min(gap_range) > 8` AND the
    card carries neither `margin_default` nor `no_net_debt` (both mean the reverse-DCF ran
    on a sector-default assumption, not real fundamentals -- not sound grounds to call a
    valuation extreme). The z-branch is UNCHANGED (a null z never fires) except that
    `peg_history_z` generalizes to `lens_history_z` -- the SELECTED ladder rung's
    own-history z (amendment v1.2 replaced the fixed PEG assumption with a printed
    selection; see build_ladder()/select_primary_lens()).

    -> (extreme, reason). `reason` is `None` except when the gap branch WOULD have fired
    on `min(gap_range)` alone but one of the veto flags blocked it AND the z-branch also
    didn't independently make the card extreme -- i.e. exactly the case where "not
    extreme" would otherwise be read as "verified not extreme" when it actually means
    "unverifiable with the fundamentals on hand". Then `reason = "vetoed: <flag[, flag]>"`
    naming every veto flag present. If the z-branch DOES independently fire, the card is
    genuinely extreme and no veto framing is needed (reason stays None)."""
    thresh = cfg.get("valuation_extreme") or {}
    gap_thresh = thresh.get("gap_pp_threshold", 8)
    z_thresh = thresh.get("peg_history_z_threshold", 2)
    veto_flags = [f for f in _VALUATION_EXTREME_VETO_FLAGS if f in flags]
    gap_would_fire = bool(gap_range and gap_range[0] is not None and gap_range[0] > gap_thresh)
    gap_fires = gap_would_fire and not veto_flags
    z_fires = lens_history_z is not None and lens_history_z > z_thresh
    extreme = bool(gap_fires or z_fires)
    reason = None
    if gap_would_fire and veto_flags and not z_fires:
        reason = "vetoed: " + ", ".join(veto_flags)
    return extreme, reason


# ---------------------------------------------------------------------------
# Amendment v1.2 — forward growth-adjusted multiple ladder (L1/L4)
# ---------------------------------------------------------------------------
RUNG_NAMES = ("peg", "ev_ebitda_to_growth", "ev_fcf_to_growth", "ev_sales_to_growth")


def ev_multiple_fwd(ev: float | None, v1: float | None, v2: float | None = None) -> float | None:
    """EV / mean(available of v1, v2) -- v1/v2 <= 0 excluded (a negative denominator
    multiple is not meaningful here). L1(b) explicitly averages FY1+FY2 EBITDA
    ("forward EV/EBITDA (FY1, FY2)"); L1(c)'s EV/FCF passes v2=None (FY1 only, same
    convention as pe_fy1)."""
    if ev is None:
        return None
    vals = [v for v in (v1, v2) if v is not None and v > 0]
    if not vals:
        return None
    return ev / statistics.mean(vals)


def _rung_raw_cagr(name: str, entry: dict, ev: float | None) -> tuple[float | None, float | None]:
    """(raw_multiple, cagr) for ladder rung `name`, from ANY entry dict (current-ticker
    or a historical/peer entry) + that entry's own EV -- the single function every rung,
    every history point, and every peer point goes through (one code path, per the
    coordinator review: "a parameterized rung loop, not four hand-written lenses")."""
    if name == "peg":
        raw, _ = pe_fy1(entry.get("price"), entry.get("fy1_eps"))
        cagr = two_yr_cagr(entry.get("fy1_eps"), entry.get("fy3_eps"))
    elif name == "ev_ebitda_to_growth":
        raw = ev_multiple_fwd(ev, entry.get("fy1_ebitda"), entry.get("fy2_ebitda"))
        cagr = two_yr_cagr(entry.get("fy1_ebitda"), entry.get("fy3_ebitda"))
    elif name == "ev_fcf_to_growth":
        raw = ev_multiple_fwd(ev, entry.get("fy1_fcf"))
        cagr = two_yr_cagr(entry.get("fy1_fcf"), entry.get("fy3_fcf"))
    elif name == "ev_sales_to_growth":
        raw = ev_sales_fy1(ev, entry.get("fy1_sales"))
        cagr = near_term_cagr(entry.get("fy1_sales"), entry.get("fy3_sales"))
    else:
        raise ValueError(f"unknown rung {name!r}")
    return raw, cagr


def _rung_adjusted(raw: float | None, cagr: float | None) -> float | None:
    """multiple / (CAGR * 100); None if the raw multiple is unavailable OR growth <= 0
    (F2/L1: "a rung with growth <= 0 is null with reason")."""
    if raw is None or cagr is None or cagr <= 0:
        return None
    return raw / (cagr * 100)


def _entry_ev(entry: dict, net_debt: float | None) -> float | None:
    if entry.get("mcap") is None:
        return None
    return entry["mcap"] + net_debt if net_debt is not None else entry["mcap"]


def select_primary_lens(entry: dict) -> str | None:
    """L1's literal waterfall, in priority order: (a) PEG when FY1 EPS > 0 and its own
    EPS-CAGR growth > 0; (b) EV/EBITDA-to-growth ONLY when EPS <= 0 (not merely when
    PEG's growth check failed) and EBITDA > 0 and growing; (c) EV/FCF-to-growth when
    FCF > 0 and growing (no EPS-sign gate); (d) EV/Sales-to-growth, last resort. Each
    rung's raw/adjusted values are computed independently in build_ladder() regardless
    of which one is primary -- e.g. EV/FCF-to-growth is still shown "next to PEG for
    cash-rich names" even when PEG is primary. None if no rung is eligible at all."""
    fy1_eps = entry.get("fy1_eps")
    eps_positive = fy1_eps is not None and fy1_eps > 0
    eps_cagr = two_yr_cagr(entry.get("fy1_eps"), entry.get("fy3_eps"))
    if eps_positive and eps_cagr is not None and eps_cagr > 0:
        return "peg"
    fy1_ebitda = entry.get("fy1_ebitda")
    ebitda_cagr = two_yr_cagr(entry.get("fy1_ebitda"), entry.get("fy3_ebitda"))
    if (not eps_positive) and fy1_ebitda is not None and fy1_ebitda > 0 \
            and ebitda_cagr is not None and ebitda_cagr > 0:
        return "ev_ebitda_to_growth"
    fy1_fcf = entry.get("fy1_fcf")
    fcf_cagr = two_yr_cagr(entry.get("fy1_fcf"), entry.get("fy3_fcf"))
    if fy1_fcf is not None and fy1_fcf > 0 and fcf_cagr is not None and fcf_cagr > 0:
        return "ev_fcf_to_growth"
    sales_cagr = near_term_cagr(entry.get("fy1_sales"), entry.get("fy3_sales"))
    if sales_cagr is not None and sales_cagr > 0:
        return "ev_sales_to_growth"
    return None


def build_ladder(entry: dict, ev: float | None, ticker: str, ticker_themes_all: dict[str, list[str]],
                 all_entries: dict, fundamentals: dict, history_cache: dict, peers: list[str],
                 min_days: int, min_peers_for_z: int) -> dict:
    """{rung_name: {raw_multiple, cagr, adjusted, history: {z,...}, peers: {peer_score,...},
    flags}} for every rung in RUNG_NAMES. L4: own-history (>=60-day gate, same as PEG
    always had) and theme-peer (median/MAD peer_score) comparisons apply identically to
    every rung -- EV/EBITDA and EV/FCF get exactly the same treatment PEG always did."""
    ladder: dict[str, dict] = {}
    for name in RUNG_NAMES:
        raw, cagr = _rung_raw_cagr(name, entry, ev)
        adjusted = _rung_adjusted(raw, cagr)
        flags: list[str] = []
        if raw is None:
            flags.append(f"{name}_unavailable")
        elif adjusted is None:
            flags.append("growth<=0 or missing")

        def _hist_fn(e, _name=name):
            e_net_debt = fundamentals.get(ticker, {}).get("net_debt")
            e_ev = _entry_ev(e, e_net_debt)
            r, c = _rung_raw_cagr(_name, e, e_ev)
            return _rung_adjusted(r, c)

        hist = zscore_history(adjusted, history_series(ticker, history_cache, _hist_fn), min_days)

        peer_vals = []
        for p in peers:
            pe_entry = all_entries.get(p)
            if pe_entry is None:
                continue
            p_net_debt = fundamentals.get(p, {}).get("net_debt")
            p_ev = _entry_ev(pe_entry, p_net_debt)
            r, c = _rung_raw_cagr(name, pe_entry, p_ev)
            peer_vals.append(_rung_adjusted(r, c))
        peer = peer_lens(adjusted, peer_vals, min_peers_for_z)
        peer["peer_basis"] = "watchlist_themes"

        ladder[name] = {"raw_multiple": raw, "cagr": cagr, "adjusted": adjusted,
                        "history": hist, "peers": peer, "flags": flags}
    return ladder


# ---------------------------------------------------------------------------
# Amendment v1.2 — horizon + long_duration (L2/L3)
# ---------------------------------------------------------------------------
def forward_years_available(entry: dict) -> int:
    """Count of FY1/FY2/FY3 SALES consensus present (quality-ok, survived into the
    snapshot's `tickers` entry) -- used for the general `horizon` display (L2), NOT for
    the long_duration gate as of fix round 2 (see forward_years_available_for_lens())."""
    return sum(1 for n in (1, 2, 3) if entry.get(f"fy{n}_sales") is not None)


_LENS_DENOMINATOR_METRIC = {"peg": "eps", "ev_ebitda_to_growth": "ebitda",
                            "ev_fcf_to_growth": "fcf", "ev_sales_to_growth": "sales"}


def forward_years_available_for_lens(entry: dict, primary_lens: str | None) -> int:
    """RIS5 A5 fix round 2, item 1: L3's "fewer than 3 forward years of consensus" is
    read against the SELECTED lens's own denominator (EPS for peg, EBITDA/FCF for those
    rungs, sales for ev_sales_to_growth) -- not always sales, which could show 3 years of
    SALES coverage while the actual multiple in use (say PEG) only has 1-2 years of EPS.
    `primary_lens is None` (no valid lens at all) falls back to the sales count -- the
    least surprising default, matching the pre-fix-round-2 behaviour for that edge case."""
    metric = _LENS_DENOMINATOR_METRIC.get(primary_lens)
    if metric is None:
        return forward_years_available(entry)
    return sum(1 for n in (1, 2, 3) if entry.get(f"fy{n}_{metric}") is not None)


def duration_note(terminal_share: float | None, years: int = 5) -> str | None:
    """RIS5 A5 fix round 2, item 1: a plain-English readout of `terminal_share_of_ev`
    shown on EVERY card (not just long_duration ones) so a reader sees how much of the
    valuation rests past the explicit window without needing the long_duration mark to
    notice. None only when terminal_share itself couldn't be computed (a Layer-1 guard
    failed)."""
    if terminal_share is None:
        return None
    return f"{round(terminal_share * 100)}% of EV rests beyond year {years}"


def horizon_info(entry: dict) -> dict:
    """L2: FY1-FY3 is the working horizon; FY4/FY5 extend it ONLY when present with
    count >= 3, never beyond year 5. NOTE (coordinator review): scripts/valuation/
    snapshot.py's RELATIVE_FISCAL_END is 3 and CONSENSUS_METRICS has no FY4/5 pull today,
    so `entry` never actually carries fy4_*/fy5_* fields in production yet -- this reads
    them defensively (so the branch activates the moment A3 extends the horizon) but is
    otherwise INERT; see the A5 report's Fix round 1 section."""
    years_available = forward_years_available(entry)
    counts = entry.get("counts") or {}
    fy4_count, fy5_count = counts.get("fy4_sales"), counts.get("fy5_sales")
    extended: list[int] = []
    if entry.get("fy4_sales") is not None and (fy4_count or 0) >= 3:
        extended.append(4)
        if entry.get("fy5_sales") is not None and (fy5_count or 0) >= 3:
            extended.append(5)
    return {"years_used": [1, 2, 3] + extended, "years_available": years_available,
           "fy4_count": fy4_count, "fy5_count": fy5_count, "extended": bool(extended)}


def is_pre_profit(fcf_margin_raw: float | None, operating_margin_pct: float | None) -> bool:
    """RIS5 A5 fix round 3, ruling 2: "genuinely pre-profit" = BOTH the raw (unfloored)
    FCF margin AND the LTM operating margin are <= 0 -- one negative line alone (e.g.
    COHR: FCF margin negative but operating margin positive, a capex/restructuring story,
    not a pre-profit one) is not enough. Missing data on EITHER leg means pre_profit is
    never ASSERTED (an unobserved margin is not evidence of pre-profit, same "unobserved
    is never a default value" convention as the stage reader)."""
    if fcf_margin_raw is None or operating_margin_pct is None:
        return False
    return fcf_margin_raw <= 0 and operating_margin_pct <= 0


def determine_long_duration(terminal_share: float | None, lens_forward_years: int,
                            primary_lens: str | None, cfg: dict, pre_profit: bool = False
                            ) -> tuple[bool, list[str]]:
    """L3 (RIS5 A5 fix round 2, item 1 -- recalibrated): long_duration when
    terminal_share_of_ev > threshold (default 0.90, was 0.75 -- at a 10% discount rate a
    30% grower legitimately carries ~80% of EV past year 5, so 0.75 was flagging ordinary
    growth names, not just genuinely long-duration ones), OR fewer than
    `min_forward_years` (default 3) forward years of consensus FOR THE SELECTED LENS'S
    OWN DENOMINATOR (`lens_forward_years`, see forward_years_available_for_lens() -- not
    always sales), OR the primary lens is the last-resort EV/Sales-to-growth rung, OR
    (fix round 3, ruling 2) the ticker is genuinely pre-profit (`pre_profit`, see
    is_pre_profit()) -- a floored margin path can still SOLVE, but a name with no real
    profitability signal on either FCF or operating margin has nothing solid under the
    reverse-DCF's margin assumption, so it is marked long_duration ("show only what is
    priced") rather than presented as an ordinary card. Any one reason is sufficient; all
    firing reasons are listed (not just the first)."""
    ld_cfg = cfg.get("long_duration") or {}
    thresh = ld_cfg.get("terminal_share_threshold", 0.90)
    min_years = ld_cfg.get("min_forward_years", 3)
    reasons = []
    if terminal_share is not None and terminal_share > thresh:
        reasons.append("terminal_share_of_ev>threshold")
    if lens_forward_years < min_years:
        reasons.append("lens_forward_years<min")
    if primary_lens == "ev_sales_to_growth":
        reasons.append("primary_lens_last_resort")
    if pre_profit:
        reasons.append("pre_profit")
    return bool(reasons), reasons


# ---------------------------------------------------------------------------
# F7 — priced-in component
# ---------------------------------------------------------------------------
def load_gap_history(state_dir: Path, exclude_date: str | None = None) -> dict[str, dict[str, float]]:
    """{date: {ticker: gap_pp}} from every expectations_<date>.jsonl under state_dir
    except `exclude_date` (today) -- the own-history side of F7's gap_z. A card whose
    gap was null that day (long_duration, skip, guard failure) simply has no entry for
    that date, same convention as the price/consensus history cache."""
    state_dir = Path(state_dir)
    out: dict[str, dict[str, float]] = {}
    for p in state_dir.glob("expectations_*.jsonl"):
        d = p.stem.split("expectations_", 1)[1]
        if d == exclude_date:
            continue
        entry: dict[str, float] = {}
        for r in _read_jsonl(p):
            gp = ((r.get("gap") or {}).get("gap_pp"))
            tk = r.get("ticker")
            if gp is not None and tk:
                entry[tk] = gp
        if entry:
            out[d] = entry
    return out


def compute_gap_z(ticker: str, gap_pp: float | None, gap_today: dict[str, float],
                  gap_history: dict[str, dict[str, float]], min_days: int) -> tuple[float | None, str, int]:
    """-> (gap_z, basis, n). F7: default is a CROSS-SECTIONAL z against every card's
    gap_pp on the date (including the ticker itself -- the standard cross-sectional-z
    reading of "z ... vs the cross-section of all cards"); switches to an OWN-HISTORY z
    once >= min_days daily gap_pp points have accrued for this ticker specifically."""
    own_series = [tickers[ticker] for tickers in gap_history.values() if ticker in tickers]
    if gap_pp is not None and len(own_series) >= min_days:
        r = zscore_history(gap_pp, own_series, min_days)
        return r["z"], "own_history", r["n_days"]
    all_today = [v for v in gap_today.values() if v is not None]
    n = len(all_today)
    if gap_pp is None or n < 2:
        return None, "cross_section", n
    mean = statistics.mean(all_today)
    stdev = statistics.pstdev(all_today)
    if stdev == 0:
        return None, "cross_section", n
    return (gap_pp - mean) / stdev, "cross_section", n


def combine_priced_in(gap_z: float | None, lens_history_z: float | None,
                      lens_peer_score: float | None) -> tuple[float | None, list[str]]:
    """F7: priced_in_valuation = clip(mean of available {gap_z, lens_history_z,
    lens_peer_score}, -3, 3), plus the list of which were available. (Generalized from
    the brief's literal `peg_history_z`/`peg_peer_z` -- amendment v1.2's ladder replaced
    the fixed PEG assumption with a printed selection; see is_valuation_extreme()'s own
    docstring for the same substitution.)"""
    named = {"gap_z": gap_z, "lens_history_z": lens_history_z, "lens_peer_score": lens_peer_score}
    available = [k for k in ("gap_z", "lens_history_z", "lens_peer_score") if named[k] is not None]
    if not available:
        return None, []
    return _clip(statistics.mean(named[k] for k in available), -3.0, 3.0), available


# ---------------------------------------------------------------------------
# Card builder
# ---------------------------------------------------------------------------
def build_card(ticker: str, entry: dict | None, cfg: dict, *, state_dir: Path, as_of: str,
               stages: dict, ticker_themes_all: dict[str, list[str]], downside_theme_slugs: set[str],
               polarity_unavailable: bool = False, reads_rows: list[dict] | None = None,
               notes_dir: Path = NOTES_DIR, credibility_store=None,
               credibility_cross_median: float | None = None, credibility_cache: dict | None = None,
               fundamentals: dict | None = None, all_entries: dict | None = None,
               history_cache: dict[str, dict[str, dict]] | None = None) -> dict:
    """One ticker's full card, or {"ticker", "skipped": True, "reason": ...}.

    `history_cache` (see load_history_cache()) is built ONCE by build_expectations() and
    shared across every ticker; defaults to {} (no history) for direct callers/tests that
    don't need it. `priced_in` is NOT set here -- it needs every card's gap_pp first, so
    build_expectations() attaches it in a second pass (see attach_priced_in())."""
    reads_rows = reads_rows or []
    history_cache = history_cache if history_cache is not None else {}
    if entry is None:
        return {"ticker": ticker, "skipped": True, "reason": "not in snapshot"}
    if entry.get("price") is None:
        return {"ticker": ticker, "skipped": True, "reason": "no price/mcap"}
    if entry.get("mcap") is None:
        # RIS5 A5 live run: A3's real build_latest() seats `price` whenever price quality
        # is "ok" and independently nulls `mcap` on its own quality failure (currency
        # mismatch, e.g. an ADR quoted in USD vs a local-exchange market_value in the home
        # currency; or a genuine fail:mcap<=0) -- see docs/portal/mcp_schemas.md and
        # task-3-report.md's "Fix round 3". A ticker in exactly this state has a real price
        # but no valuation card is possible without EV, so it's skipped with a SPECIFIC
        # reason (distinct from the "no price at all" case above) -- these 16 real-run
        # tickers (15 ADR currency mismatches + LAZR) return once FX conversion lands.
        return {"ticker": ticker, "skipped": True, "reason": "no_mcap"}
    if entry.get("fy1_sales") is None:
        # RIS5 A5 fix round 1, L3: ONLY fy1_sales is mandatory now (it anchors Layer 1 and
        # the ev_sales_to_growth rung) -- fy2/fy3 missing no longer skips the ticker, it
        # becomes a long_duration card instead (see below).
        reason = _quality_fail_reason(state_dir, as_of, ticker, "fy1_sales")
        return {"ticker": ticker, "skipped": True,
                "reason": f"quality fail: {reason}" if reason else "missing fy1_sales"}

    themes = ticker_themes_all.get(ticker) or []
    fam = sector_family(themes, cfg)
    now_default, term_default = margin_defaults(ticker, fam, cfg)

    fundamentals = fundamentals or {}
    fnd = fundamentals.get(ticker, {})
    flags: list[str] = []

    for field in ("fy2_sales", "fy3_sales"):
        if entry.get(field) is None:
            reason = _quality_fail_reason(state_dir, as_of, ticker, field)
            flags.append(f"missing_{field}:{reason}" if reason else f"missing_{field}")

    net_debt = fnd.get("net_debt")   # RIS5 A5 fix round 1, F4: may be NEGATIVE (net cash
                                     # reduces EV) -- `ev = mcap + net_debt` already handles
                                     # that by plain addition; `no_net_debt` fires only when
                                     # fundamentals carry no net_debt row at all, never on sign.
    ev = entry["mcap"] + net_debt if net_debt is not None else entry["mcap"]
    if net_debt is None:
        flags.append("no_net_debt")

    # RIS5 A5 fix round 4, V3: BOTH ends of the margin path are name-specific and FORWARD
    # where consensus allows it -- terminal from fy3_fcf/fy3_sales, start from
    # fy1_fcf/fy1_sales (never a trailing figure), each degrading with its own named flag.
    terminal_margin, term_flags = select_terminal_margin(entry, term_default)
    fcf_margin_now, fcf_margin_raw, start_flags = select_start_margin(entry, fnd)
    flags.extend(term_flags); flags.extend(start_flags)
    years = cfg.get("years", 5)
    discount_rate = cfg.get("discount_rate", 0.10)
    terminal_growth = cfg.get("terminal_growth", 0.03)

    # C3 (recalibrated, fix round 3 ruling 2): with the floored start above, the margin path is
    # monotonic and non-negative for any terminal_margin > 0 -- skip
    # (margin_path_nonpositive) ONLY when the terminal margin itself is <= 0 (a config/
    # override misconfiguration, not a real-data case observed live).
    if terminal_margin <= 0:
        return {"ticker": ticker, "skipped": True, "reason": "margin_path_nonpositive"}

    operating_margin_pct = fnd.get("operating_margin")
    # pre_profit stays a TRAILING read (LTM FCF margin AND LTM operating margin both <= 0)
    # -- it asks "has this company ever made money", which a forward estimate cannot answer.
    pre_profit = is_pre_profit(read_ltm_fcf_margin(fnd), operating_margin_pct)

    l1 = implied_growth(ev, entry["fy1_sales"], fcf_margin_now, terminal_margin,
                        discount_rate=discount_rate, terminal_growth=terminal_growth,
                        years=years, cfg=cfg)

    thesis_fm = load_thesis_fm(ticker, notes_dir)
    cred_entry = (credibility_cache or {}).get(ticker)
    l2 = supported_growth(ticker, entry, cfg, stages=stages, ticker_themes_all=ticker_themes_all,
                          reads_rows=reads_rows, thesis_fm=thesis_fm,
                          downside_theme_slugs=downside_theme_slugs,
                          polarity_unavailable=polarity_unavailable, terminal_growth=terminal_growth,
                          credibility_store=credibility_store, credibility_cross_median=credibility_cross_median,
                          credibility_entry=cred_entry)

    gap_pp_downside = compute_gap(l1["implied_growth_5y"], l2["base"], l2["downside"])
    gap_range, gap_downside_range = compute_gap_ranges(l1["sensitivity"], l2["base"], l2["downside"])
    # V1: BOTH readings are emitted. `gap_pp` (== `gap_vs_haircut_pp`) is the haircut gap --
    # the one B1 consumes and the one `gap_range`/`valuation_extreme`/`priced_in` are built
    # on. `gap_vs_street_pp` is the same difference against the UNHAIRCUT (lambda = 1)
    # supported base, so a reader can see how much of the gap is the haircut's doing.
    gap_vs_street = compute_gap(l1["implied_growth_5y"], l2.get("base_street"), None)
    gap = {**gap_pp_downside, "gap_vs_haircut_pp": gap_pp_downside["gap_pp"],
           "gap_vs_street_pp": gap_vs_street["gap_pp"],
           "gap_range": gap_range, "gap_downside_range": gap_downside_range}

    ev_sales = ev_sales_fy1(ev, entry["fy1_sales"])
    pe, pe_flags = pe_fy1(entry["price"], entry.get("fy1_eps"))

    min_days = (cfg.get("history") or {}).get("min_days_for_z", 60)
    ev_sales_hist = zscore_history(
        ev_sales, history_series(ticker, history_cache, lambda e: ev_sales_fy1(
            _entry_ev(e, net_debt), e.get("fy1_sales"))), min_days)
    pe_hist = zscore_history(
        pe, history_series(ticker, history_cache, lambda e: pe_fy1(e.get("price"), e.get("fy1_eps"))[0]),
        min_days)

    peers = theme_peers(ticker, ticker_themes_all, (cfg.get("peer") or {}).get("min_shared_themes", 2))
    min_peers_for_z = (cfg.get("peer") or {}).get("min_peers_for_z", 3)
    all_entries = all_entries or {}
    peer_ev_sales_vals = []
    for p in peers:
        pe_entry = all_entries.get(p)
        if pe_entry is None:
            continue
        p_ev = _entry_ev(pe_entry, fundamentals.get(p, {}).get("net_debt"))
        peer_ev_sales_vals.append(ev_sales_fy1(p_ev, pe_entry.get("fy1_sales")))
    ev_sales_peers = peer_lens(ev_sales, peer_ev_sales_vals, min_peers_for_z)
    ev_sales_peers["peer_basis"] = "watchlist_themes"

    ladder = build_ladder(entry, ev, ticker, ticker_themes_all, all_entries, fundamentals,
                          history_cache, peers, min_days, min_peers_for_z)
    primary = select_primary_lens(entry)
    ebitda_present = any(entry.get(f"fy{n}_ebitda") is not None for n in (1, 2, 3))
    fcf_present = any(entry.get(f"fy{n}_fcf") is not None for n in (1, 2, 3))
    if not ebitda_present and not fcf_present:
        flags.append("ebitda_fcf_unavailable")
    if primary == "ev_sales_to_growth":
        flags.append("no_profit_lens")
    elif primary is None:
        flags.append("no_valid_lens")
    lens_history_z = ladder[primary]["history"]["z"] if primary else None
    lens_peer_score = ladder[primary]["peers"]["peer_score"] if primary else None

    breadth_sales_4w = revision_breadth(ticker, entry, history_cache, as_of, 4, key="fy1_sales")
    breadth_sales_13w = revision_breadth(ticker, entry, history_cache, as_of, 13, key="fy1_sales")
    breadth_eps_4w = revision_breadth(ticker, entry, history_cache, as_of, 4, key="fy1_eps")
    breadth_eps_13w = revision_breadth(ticker, entry, history_cache, as_of, 13, key="fy1_eps")
    flags.append("breadth_semantics_unverified")

    valuation_extreme, valuation_extreme_reason = is_valuation_extreme(gap["gap_range"], lens_history_z, flags, cfg)

    horizon = horizon_info(entry)
    terminal_share = l1["terminal_share_of_ev"]
    lens_forward_years = forward_years_available_for_lens(entry, primary)
    horizon["lens_forward_years"] = lens_forward_years
    is_ld, ld_reasons = determine_long_duration(terminal_share, lens_forward_years, primary, cfg,
                                               pre_profit=pre_profit)

    l1_card = {k: v for k, v in l1.items() if k != "pv_residual_check"}   # C7: dropped from the card

    provenance = {
        "snapshot_as_of": as_of,
        "stages_as_of": stages.get("as_of"),
        "reads_latest_date": reads_latest_date(ticker, reads_rows),
        "credibility_as_of": l2["drivers"].get("credibility", {}).get("credibility_as_of"),
    }

    all_flags = sorted(set(flags + l1["flags"] + l2["flags"] + pe_flags))

    card = {
        "ticker": ticker, "skipped": False, "as_of": as_of, "sector_family": fam,
        "credibility_source": l2["drivers"].get("credibility", {}).get("source", "none"),
        "primary_lens": primary,
        "long_duration": is_ld, "long_duration_reasons": ld_reasons,
        "flags": all_flags,
        "provenance": provenance,
        "horizon": horizon,
        "duration_note": duration_note(terminal_share, years),
        "inputs": {
            "price": entry["price"], "mcap": entry["mcap"], "net_debt": net_debt, "ev": ev,
            "fy1_sales": entry["fy1_sales"], "fy2_sales": entry.get("fy2_sales"), "fy3_sales": entry.get("fy3_sales"),
            "fy1_eps": entry.get("fy1_eps"), "fy2_eps": entry.get("fy2_eps"), "fy3_eps": entry.get("fy3_eps"),
            "fy1_ebitda": entry.get("fy1_ebitda"), "fy2_ebitda": entry.get("fy2_ebitda"),
            "fy3_ebitda": entry.get("fy3_ebitda"),
            "fy1_fcf": entry.get("fy1_fcf"), "fy2_fcf": entry.get("fy2_fcf"), "fy3_fcf": entry.get("fy3_fcf"),
            "fcf_margin_now": fcf_margin_now, "fcf_margin_now_raw": fcf_margin_raw,
            "fy1_fcf_margin_consensus": consensus_margin(entry.get("fy1_fcf"), entry.get("fy1_sales")),
            "fy3_fcf_margin_consensus": consensus_margin(entry.get("fy3_fcf"), entry.get("fy3_sales")),
            "fcf_margin_ltm": read_ltm_fcf_margin(fnd),
            "terminal_margin": terminal_margin,
            "discount_rate": discount_rate, "terminal_growth": terminal_growth, "years": years,
        },
        "layer1_priced": l1_card,
        "layer2_supported": l2,
        "gap": gap,
        "lenses": {
            "ev_sales_fy1": ev_sales, "pe_fy1": pe,
            "ev_sales_vs_history": ev_sales_hist, "pe_vs_history": pe_hist,
            "ev_sales_vs_peers": ev_sales_peers, "n_theme_peers": len(peers),
            "ladder": {"primary": primary, **ladder},
            "revision_breadth": {
                "fy1_sales": {"4w": breadth_sales_4w, "13w": breadth_sales_13w},
                "fy1_eps": {"4w": breadth_eps_4w, "13w": breadth_eps_13w},
            },
        },
        "valuation_extreme": valuation_extreme,
        "valuation_extreme_reason": valuation_extreme_reason,
    }

    if is_ld:
        # L3: "show only what is priced" -- layer1_priced/lenses/inputs/provenance/horizon/
        # duration_note stay; supported/gap/valuation_extreme/priced_in null with reason
        # "long_duration" (valuation_extreme_reason nulled alongside valuation_extreme --
        # a card that isn't scored for extremity has no veto reason to report either).
        card["layer2_supported"] = None
        card["gap"] = None
        card["valuation_extreme"] = None
        card["valuation_extreme_reason"] = None
        card["priced_in"] = None

    return card


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def attach_priced_in(cards: dict[str, dict], state_dir: Path, as_of: str, min_days: int) -> None:
    """F7, second pass: needs every card's gap_pp before it can compute ANY card's gap_z
    (cross-sectional), so this runs after build_card() has produced every card in the
    run. long_duration cards are excluded from the gap cross-section pool (their gap is
    null) and get priced_in: null (already set in build_card(), reaffirmed here)."""
    eligible_gaps = {tk: c["gap"]["gap_pp"] for tk, c in cards.items()
                     if not c.get("long_duration") and c.get("gap") and c["gap"]["gap_pp"] is not None}
    gap_history = load_gap_history(state_dir, exclude_date=as_of)
    for tk, c in cards.items():
        if c.get("long_duration"):
            c["priced_in"] = None
            continue
        gap_pp = (c.get("gap") or {}).get("gap_pp")
        gap_z, basis, n = compute_gap_z(tk, gap_pp, eligible_gaps, gap_history, min_days)
        primary = c.get("primary_lens")
        ladder = c["lenses"]["ladder"]
        lens_history_z = ladder[primary]["history"]["z"] if primary else None
        lens_peer_score = ladder[primary]["peers"]["peer_score"] if primary else None
        piv, available = combine_priced_in(gap_z, lens_history_z, lens_peer_score)
        c["priced_in"] = {"gap_z": gap_z, "gap_z_basis": basis, "gap_z_n": n,
                          "lens_history_z": lens_history_z, "lens_peer_score": lens_peer_score,
                          "primary_lens": primary, "priced_in_valuation": piv, "available": available}


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

    watchlist_path = watchlist_path or WATCHLIST_PATH
    downside_theme_slugs, polarity_unavailable = load_downside_theme_slugs(polarity_path, watchlist_path)

    fundamentals = fundamentals if fundamentals is not None else load_fundamentals(state_dir, as_of)
    # Built ONCE and shared across every ticker/lens this run (fix round 0, item 3) --
    # see load_history_cache()'s own docstring for why this used to be the dominant cost.
    history_cache = load_history_cache(state_dir, exclude_date=as_of)

    universe = sorted(set(tickers_snapshot) | set(ticker_themes_all))
    non_pvt_universe = [tk for tk in universe if not tk.endswith(".pvt")]
    # F6: ONE store read per ticker (build_credibility_cache), reused for BOTH the
    # cross-sectional median AND every ticker's own credibility_term() call below.
    credibility_cache = build_credibility_cache(non_pvt_universe, store=credibility_store)
    cred_cross_median = credibility_cross_median(credibility_cache)

    cards: dict[str, dict] = {}
    skipped: list[dict] = []
    for tk in non_pvt_universe:
        entry = tickers_snapshot.get(tk)
        card = build_card(tk, entry, cfg, state_dir=state_dir, as_of=as_of, stages=stages,
                          ticker_themes_all=ticker_themes_all, downside_theme_slugs=downside_theme_slugs,
                          polarity_unavailable=polarity_unavailable, reads_rows=reads_rows, notes_dir=notes_dir,
                          credibility_store=credibility_store, credibility_cross_median=cred_cross_median,
                          credibility_cache=credibility_cache, fundamentals=fundamentals,
                          all_entries=tickers_snapshot, history_cache=history_cache)
        if card.get("skipped"):
            skipped.append({"ticker": tk, "reason": card["reason"]})
        else:
            cards[tk] = card

    min_days = (cfg.get("history") or {}).get("min_days_for_z", 60)
    attach_priced_in(cards, state_dir, as_of, min_days)

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
