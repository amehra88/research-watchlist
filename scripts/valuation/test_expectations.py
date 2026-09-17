"""Tests for scripts/valuation/expectations.py (RIS5 A5). No claude -p, no live DB —
run directly:
    python3 scripts/valuation/test_expectations.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chunking"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "portal"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "thesis"))
import ingest_metrics  # noqa: E402  (cache worktree copy first, same trick as snapshot.py)
import identity as pid  # noqa: E402
import expectations as E  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


DEFAULT_CFG = {
    "discount_rate": 0.10, "terminal_growth": 0.03, "years": 5,
    "sensitivity": {"discount_rate_delta": 0.01, "terminal_margin_delta": 0.03},
    "bisection": {"g_lo": -0.9, "g_hi": 5.0, "max_iter": 100, "tol_relative": 1e-8},
    "terminal_margin_by_family": {"software": 0.30, "semis": 0.35, "hardware": 0.12,
                                  "internet": 0.25, "default": 0.20},
    "fcf_margin_now_by_family": {"software": 0.30, "semis": 0.35, "hardware": 0.12,
                                 "internet": 0.25, "default": 0.20},
    "overrides": {},
    "sector_family_priority": ["semis", "software", "internet", "hardware"],
    "sector_keywords": {
        "semis": ["silicon", "semiconductor", "chip_design", "hbm", "foundry"],
        "software": ["ai_infrastructure_software", "inference_compute_economics", "software"],
        "internet": ["ad_market_strength", "hyperscaler_revenue_concentration"],
        "hardware": ["networking", "thermal_management_cooling", "handset_competition"],
    },
    "supported_growth": {
        "durability": {"stage_term_bound": 0.15, "stage_term_per_level": 0.05,
                       "credibility_term_bound": 0.10, "reads_term_bound": 0.10,
                       "multiplier_bounds": [0.5, 1.5]},
        "base_bounds": [-0.5, 2.0], "reads_min_dated": 3, "downside_haircut_pp": 5.0,
    },
    "peer": {"min_shared_themes": 2, "min_peers_for_z": 3},
    "history": {"min_days_for_z": 60},
    "valuation_extreme": {"gap_pp_threshold": 8, "peg_history_z_threshold": 2},
}


# ─────────────────────────── Layer 1: bisection ────────────────────────────

def test_bisection_reproduces_synthetic_ev_within_0_1_pct():
    # Sloped margin path (advisor guard: fcf_margin_now != terminal_margin so the
    # linear interpolation is genuinely exercised).
    margins = E._margin_path(0.15, 0.30, 5)
    check("margin path slopes from now to terminal", margins[0] > 0.15 and margins[-1] == 0.30, margins)
    g0 = 0.22
    ev_synth = E._pv_for_growth(g0, 1000.0, margins, 0.10, 0.03, 5)
    result = E.solve_implied_growth(ev_synth, 1000.0, 0.15, 0.30, 0.10, 0.03, 5, DEFAULT_CFG["bisection"])
    rel_err = abs(result["pv_at_growth"] - ev_synth) / ev_synth
    check("bisection reproduces synthetic EV within 0.1%", rel_err < 0.001, rel_err)
    check("solved growth close to the seed growth", abs(result["growth"] - g0) < 0.005, result["growth"])
    check("no guard flags on a clean solve", result["flags"] == [], result["flags"])


def test_bisection_out_of_bracket_flags_and_clips():
    margins = E._margin_path(0.15, 0.30, 5)
    huge_ev = E._pv_for_growth(4.9, 1000.0, margins, 0.10, 0.03, 5) * 10
    result = E.solve_implied_growth(huge_ev, 1000.0, 0.15, 0.30, 0.10, 0.03, 5,
                                    {"g_lo": -0.9, "g_hi": 5.0, "max_iter": 50, "tol_relative": 1e-6})
    check("EV above bracket clips to g_hi", result["growth"] == 5.0, result)
    check("flagged out of bracket (high)", "implied_growth_out_of_bracket_high" in result["flags"], result)


def test_margin_path_nonpositive_guard():
    result = E.solve_implied_growth(1000.0, 500.0, -0.05, 0.10, 0.10, 0.03, 5, DEFAULT_CFG["bisection"])
    check("nonpositive margin path -> growth None", result["growth"] is None)
    check("flagged margin_path_nonpositive", "margin_path_nonpositive" in result["flags"], result["flags"])


def test_invalid_gordon_denominator_guard():
    result = E.solve_implied_growth(1000.0, 500.0, 0.15, 0.20, 0.03, 0.05, 5, DEFAULT_CFG["bisection"])
    check("discount_rate <= terminal_growth -> growth None", result["growth"] is None)
    check("flagged invalid_gordon_denominator", "invalid_gordon_denominator" in result["flags"], result["flags"])


def test_sensitivity_monotonic():
    ig = E.implied_growth(ev=8000.0, fy0_sales=1000.0, fcf_margin_now=0.15, terminal_margin=0.30,
                          discount_rate=0.10, terminal_growth=0.03, years=5, cfg=DEFAULT_CFG)
    base = ig["implied_growth_5y"]
    s = ig["sensitivity"]
    check("higher discount rate needs MORE implied growth (increasing in dr)",
         s["dr_minus"] < base < s["dr_plus"], (s["dr_minus"], base, s["dr_plus"]))
    check("higher terminal margin needs LESS implied growth (decreasing in tm)",
         s["tm_plus"] < base < s["tm_minus"], (s["tm_plus"], base, s["tm_minus"]))
    check("implied_terminal_margin echoes the input, not solved", ig["implied_terminal_margin"] == 0.30)


# ─────────────────────────── sector family ──────────────────────────────────

_WORKTREE_ROOT = Path(__file__).resolve().parents[2]


def test_sector_family_nvda_avgo_cohr():
    # explicit worktree path (E.CONFIG_PATH defaults to REPO = the main checkout, same
    # "worktree copy is only visible here until merge" convention as theme_polarity.py's
    # POLARITY_PATH docstring) -- exercises the SHIPPED config/valuation.yaml.
    real_cfg = E.load_config(_WORKTREE_ROOT / "config" / "valuation.yaml")
    nvda_themes = ["ai_infrastructure_capex", "silicon_architecture_competition",
                  "networking_competitive_landscape", "sovereign_ai_deployments",
                  "china_export_controls", "inference_compute_economics", "ai_compute_topology"]
    avgo_themes = ["ai_infrastructure_capex", "silicon_architecture_competition",
                  "networking_competitive_landscape", "hyperscaler_revenue_concentration",
                  "inference_compute_economics", "ai_compute_topology"]
    cohr_themes = ["networking_competitive_landscape", "ai_infrastructure_capex",
                  "silicon_architecture_competition", "ai_compute_topology",
                  "thermal_management_cooling"]
    check("NVDA -> semis", E.sector_family(nvda_themes, real_cfg) == "semis",
         E.sector_family(nvda_themes, real_cfg))
    check("AVGO -> semis", E.sector_family(avgo_themes, real_cfg) == "semis",
         E.sector_family(avgo_themes, real_cfg))
    check("COHR -> hardware (networking + thermal_management outvote 1 silicon hit)",
         E.sector_family(cohr_themes, real_cfg) == "hardware", E.sector_family(cohr_themes, real_cfg))


def test_sector_family_no_themes_is_default():
    check("no matching themes -> default", E.sector_family([], DEFAULT_CFG) == "default")
    check("unmatched theme slugs -> default",
         E.sector_family(["some_unmapped_theme"], DEFAULT_CFG) == "default")


# ─────────────────────────── stage reader ────────────────────────────────────

def test_read_stage_tolerates_int_and_dict_and_theme_and_pair_gating():
    stages = {"pairs": {"themeA|AAA": 2, "themeB|BBB": {"stage": 3}, "themeC|CCC": 1},
             "gated": ["themeC", "themeB|BBB"]}
    check("bare int shape read", E.read_stage(stages, "themeA", "AAA") == 2)
    check("dict-with-stage-key shape read", E.read_stage(stages, "themeB", "BBB") is None,
         "themeB|BBB is pair-level gated")
    check("theme-level gate nulls every ticker under that theme",
         E.read_stage(stages, "themeC", "CCC") is None)
    check("missing pair -> None", E.read_stage(stages, "themeA", "ZZZ") is None)


def test_unobserved_stage_is_null_never_zero_or_one():
    stages = {"pairs": {"t|AAA": 0}, "gated": ["t"]}   # even a literal 0 in pairs is gated -> null
    v = E.read_stage(stages, "t", "AAA")
    check("gated pair returns None, not the raw 0", v is None, v)


# ─────────────────────────── stage-rank durability (ordinal, not linear) ─────
# fix round 0, item 1: stage_rank_term() now derives the ticker's themes from its OWN
# evidence pairs in stages.json (keys ending "|TICKER"), not watchlist.yaml's static
# tags -- signature dropped `themes`/`ticker_themes_all`.

def test_stage_rank_is_ordinal_not_linear():
    """Shifting every stage in the pool up by 1 (ticker AND peers) must leave the
    term unchanged -- it's a rank relative to peer-median, not an absolute stage
    number. A linear-on-raw-stage implementation would NOT be invariant to this
    shift."""
    stages_a = {"pairs": {"t1|AAA": 2, "t1|BBB": 3, "t1|CCC": 4}, "gated": []}
    stages_b = {"pairs": {"t1|AAA": 3, "t1|BBB": 4, "t1|CCC": 5}, "gated": []}  # +1 shift
    cfg = DEFAULT_CFG
    term_a, flags_a, detail_a = E.stage_rank_term("AAA", stages_a, cfg)
    term_b, flags_b, detail_b = E.stage_rank_term("AAA", stages_b, cfg)
    check("stage-rank term is shift-invariant (ordinal, not linear)",
         abs(term_a - term_b) < 1e-9, (term_a, term_b))
    check("earlier-stage ticker (2, peer median 3.5) gets a POSITIVE term (longer runway)",
         term_a > 0, term_a)
    check("theme discovered from AAA's own evidence pair (t1|AAA), not a passed-in list",
         detail_a["themes_used"] == ["t1"], detail_a)


def test_stage_rank_no_data_flags_and_omits():
    term, flags, detail = E.stage_rank_term("ZZZ", {"pairs": {}, "gated": []}, DEFAULT_CFG)
    check("no stage data -> term 0.0", term == 0.0, term)
    check("flagged no_stage_data", "no_stage_data" in flags, flags)


def test_stage_rank_uses_evidence_pairs_not_watchlist_tags():
    """The exact fix-round-0 scenario: a ticker's watchlist.yaml themes have NO pairs at
    all in stages.json, but the ticker DOES have pairs on a totally different theme
    (evidence-derived, not in its static tag list). The term must still compute from
    that evidence theme -- this is precisely what was producing no_stage_data everywhere
    before the fix."""
    stages = {"pairs": {"evidence_theme|AAA": 1, "evidence_theme|BBB": 3, "evidence_theme|CCC": 3},
             "gated": []}
    term, flags, detail = E.stage_rank_term("AAA", stages, DEFAULT_CFG)
    check("term computed from AAA's evidence pair even though it's not a watchlist tag",
         term != 0.0 and flags == [], (term, flags))
    check("themes_used shows the evidence theme", detail["themes_used"] == ["evidence_theme"], detail)


def test_stage_rank_combines_multiple_themes_by_median_not_mean():
    """Combine-across-themes uses the MEDIAN delta, not the mean: an outlier theme must
    not swing the whole term the way a mean would."""
    stages = {"pairs": {
        "t1|AAA": 2, "t1|BBB": 3,            # delta = 3 - 2 = 1
        "t2|AAA": 2, "t2|BBB": 3,            # delta = 1
        "t3|AAA": 1, "t3|BBB": 9,            # delta = 8 -- an outlier
    }, "gated": []}
    term, flags, detail = E.stage_rank_term("AAA", stages, DEFAULT_CFG)
    check("3 themes used", sorted(detail["themes_used"]) == ["t1", "t2", "t3"], detail)
    check("combined delta is the MEDIAN (1.0), not the mean (~3.33)",
         abs(detail["combined_stage_rank_delta"] - 1.0) < 1e-9, detail)


def test_stage_rank_gated_pair_and_theme_excluded_from_peer_set_too():
    """A gated peer must not count toward the peer median (amendment v1.1: unobserved
    excluded from BOTH the numerator and the peer set)."""
    stages = {"pairs": {"t1|AAA": 2, "t1|BBB": 3, "t1|CCC": 10}, "gated": ["t1|CCC"]}
    term, flags, detail = E.stage_rank_term("AAA", stages, DEFAULT_CFG)
    # peer set should be just {BBB: 3} (CCC's 10 excluded) -> delta = 3 - 2 = 1
    check("gated peer excluded from the peer median", detail["combined_stage_rank_delta"] == 1.0, detail)


# ─────────────────────────── credibility term ────────────────────────────────

class _FakeStore:
    def __init__(self, cred):
        self._cred = cred

    def credibility(self, ticker, metric="SALES"):
        return self._cred.get(ticker)


def test_credibility_term_neutral_flag_when_absent():
    term, flags, detail = E.credibility_term("NOPE", DEFAULT_CFG, store=_FakeStore({}))
    check("no credibility -> term 0.0 (neutral)", term == 0.0, term)
    check("flagged no_credibility", "no_credibility" in flags, flags)
    check("source recorded even when empty", detail.get("source") in ("pg", "file"), detail)


def test_credibility_term_positive_for_strong_track_record():
    store = _FakeStore({"GOOD": {"consensus_beat_rate": 0.9, "guide_hit_rate": 0.8}})
    term, flags, detail = E.credibility_term("GOOD", DEFAULT_CFG, store=store)
    check("strong track record -> positive term", term > 0, term)
    check("no flags on a clean read", flags == [], flags)
    check("source recorded", detail.get("source") in ("pg", "file"), detail)


# ─────────────────── read_credibility: env-honouring backend (fix round 0, item 2) ───

def test_read_credibility_honours_env_backend_no_live_db_in_tests():
    """No live DB is ever opened here: `store` is always injected, so
    store_b.get_metrics_store() is never reached regardless of CHUNK_STORE_BACKEND."""
    import os
    orig = os.environ.get("CHUNK_STORE_BACKEND")
    try:
        os.environ["CHUNK_STORE_BACKEND"] = "pg"
        cred, flags, source = E.read_credibility("GOOD", store=_FakeStore(
            {"GOOD": {"consensus_beat_rate": 0.9, "guide_hit_rate": 0.8}}))
        check("source reflects CHUNK_STORE_BACKEND=pg", source == "pg", source)
        check("cred returned", cred is not None)

        os.environ["CHUNK_STORE_BACKEND"] = "file"
        cred2, flags2, source2 = E.read_credibility("GOOD", store=_FakeStore({}))
        check("source reflects CHUNK_STORE_BACKEND=file", source2 == "file", source2)
        check("empty lookup still reports the real backend, not none",
             cred2 is None and source2 == "file", (cred2, source2))

        os.environ["CHUNK_STORE_BACKEND"] = "pg"
        check("unset default is 'file'",
             E.read_credibility("X", store=_FakeStore({}))[2] in ("pg",), "sanity")
    finally:
        if orig is None:
            os.environ.pop("CHUNK_STORE_BACKEND", None)
        else:
            os.environ["CHUNK_STORE_BACKEND"] = orig


def test_read_credibility_source_is_none_only_on_lookup_failure():
    class _BrokenStore:
        def credibility(self, ticker, metric="SALES"):
            raise RuntimeError("connection refused")
    cred, flags, source = E.read_credibility("X", store=_BrokenStore())
    check("lookup failure -> source 'none'", source == "none", source)
    check("flagged no_credibility", "no_credibility" in flags, flags)


# ─────────────────────────── reads-trend min-history gate ───────────────────

def _reads(ticker, axis, n, direction="up", magnitude=2):
    return [{"ticker": ticker, "axis": axis, "date": f"2026-01-{10+i:02d}",
            "direction": direction, "magnitude": magnitude} for i in range(n)]


def test_reads_term_min_history_gate():
    rows_short = _reads("T", "ai_positioning", 2)   # below the >=3 gate
    term, flags, detail = E.reads_term("T", rows_short, DEFAULT_CFG)
    check("< 3 dated reads on the only axis -> term 0.0", term == 0.0, term)
    check("flagged insufficient history", "insufficient history: reads trend" in flags, flags)

    rows_ok = _reads("T", "ai_positioning", 3, direction="up", magnitude=2)
    term2, flags2, detail2 = E.reads_term("T", rows_ok, DEFAULT_CFG)
    check(">= 3 dated reads -> term computed, no insufficient-history flag",
         term2 > 0 and flags2 == [], (term2, flags2))


def test_reads_term_averages_across_qualifying_axes_only():
    rows = _reads("T", "ai_positioning", 3, "up", 2) + _reads("T", "competitive_advantage.overall", 2, "down", 2)
    term, flags, detail = E.reads_term("T", rows, DEFAULT_CFG)
    check("only the qualifying axis (ai_positioning) is used",
         detail["axes_used"] == ["ai_positioning"], detail)


# ─────────────────────────── supported_growth ────────────────────────────────

def test_supported_growth_base_and_downside_bounds():
    entry = {"fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}   # 20% CAGR
    result = E.supported_growth("T", entry, DEFAULT_CFG, stages={"pairs": {}, "gated": []},
                                ticker_themes_all={"T": []}, reads_rows=[], thesis_fm=None,
                                downside_theme_slugs=set())
    check("near_term_cagr ~ 20%", abs(result["near_term_cagr"] - 0.20) < 1e-9, result["near_term_cagr"])
    check("base within configured bounds", -0.5 <= result["base"] <= 2.0, result["base"])
    check("no challenge -> downside == base", result["downside"] == result["base"], result)


def test_supported_growth_downside_haircut_when_challenged():
    entry = {"fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}
    thesis_fm = {"assumptions": [
        {"id": "a1", "status": "challenged", "themes": ["chip_design_competition"]},
        {"id": "a2", "status": "open", "themes": ["chip_design_competition"]},
    ]}
    result = E.supported_growth("T", entry, DEFAULT_CFG, stages={"pairs": {}, "gated": []},
                                ticker_themes_all={"T": []}, reads_rows=[], thesis_fm=thesis_fm,
                                downside_theme_slugs={"chip_design_competition"})
    check("challenged assumption id listed", result["challenged_assumption_ids"] == ["a1"], result)
    check("downside < base by the haircut", result["base"] - result["downside"] > 0, result)


def test_supported_growth_missing_sales_returns_none_base():
    result = E.supported_growth("T", {"fy1_sales": None, "fy3_sales": None}, DEFAULT_CFG,
                                stages={"pairs": {}, "gated": []}, ticker_themes_all={"T": []},
                                reads_rows=[], thesis_fm=None, downside_theme_slugs=set())
    check("missing sales -> base None", result["base"] is None)
    check("flagged", result["flags"] == ["missing fy1/fy3 sales for CAGR"], result["flags"])


# ─────────────────────────── gap sign ────────────────────────────────────────

def test_gap_sign():
    pos = E.compute_gap(0.30, 0.15, 0.10)
    neg = E.compute_gap(0.10, 0.25, 0.20)
    check("implied > supported -> positive gap_pp", pos["gap_pp"] > 0, pos)
    check("implied < supported -> negative gap_pp", neg["gap_pp"] < 0, neg)
    check("gap_pp is in PERCENTAGE POINTS (x100), not a bare fraction",
         abs(pos["gap_pp"] - 15.0) < 1e-6, pos["gap_pp"])
    check("gap_downside_pp computed against the downside base",
         abs(pos["gap_downside_pp"] - 20.0) < 1e-6, pos)


# ─────────────────────────── lenses ──────────────────────────────────────────

def test_pe_and_peg_guards():
    pe_bad, flags = E.pe_fy1(100.0, -1.0)
    check("negative EPS -> PE None + flag", pe_bad is None and flags, flags)
    pe_ok, flags2 = E.pe_fy1(100.0, 4.0)
    check("PE computed", pe_ok == 25.0)
    peg_bad, pflags = E.peg_like(25.0, -5.0)
    check("growth<=0 -> PEG None + flag", peg_bad is None and pflags, pflags)
    peg_ok, pflags2 = E.peg_like(25.0, 20.0)
    check("PEG computed", peg_ok == 1.25)


def test_zscore_history_insufficient_below_60_days_n_days_always_shown():
    series_short = [1.0, 2.0, 3.0]
    r = E.zscore_history(2.5, series_short, 60)
    check("n_days shown even when insufficient", r["n_days"] == 3, r)
    check("z is None below 60 points", r["z"] is None, r)
    check("flagged insufficient history", "insufficient history" in r["flags"], r)

    series_long = [float(i % 5) for i in range(60)]
    r2 = E.zscore_history(10.0, series_long, 60)
    check("z computed at exactly 60 points", r2["z"] is not None, r2)
    check("n_days == 60", r2["n_days"] == 60, r2)


def test_peer_lens_median_and_min_peers_for_z():
    r = E.peer_lens(10.0, [8.0, 9.0], 3)   # only 2 peers, min is 3
    check("median still shown with < min_peers_for_z", r["peer_median"] == 8.5, r)
    check("z gated below min_peers_for_z", r["peer_z"] is None, r)
    r2 = E.peer_lens(10.0, [8.0, 9.0, 11.0], 3)
    check("z computed at >= min_peers_for_z", r2["peer_z"] is not None, r2)


def test_theme_peers_min_shared_themes():
    ticker_themes = {"A": ["x", "y", "z"], "B": ["x", "y"], "C": ["x"], "D": ["q", "r"]}
    peers = E.theme_peers("A", ticker_themes, min_shared=2)
    check("2 shared themes -> peer", "B" in peers, peers)
    check("1 shared theme -> not a peer", "C" not in peers, peers)
    check("0 shared themes -> not a peer", "D" not in peers, peers)


def test_valuation_extreme_thresholds():
    check("gap just above 8pp -> extreme", E.is_valuation_extreme(8.01, None, DEFAULT_CFG) is True)
    check("gap exactly 8pp -> NOT extreme (strict >)", E.is_valuation_extreme(8.0, None, DEFAULT_CFG) is False)
    check("PEG-vs-history z just above 2 -> extreme", E.is_valuation_extreme(None, 2.01, DEFAULT_CFG) is True)
    check("PEG-vs-history z exactly 2 -> NOT extreme (strict >)",
         E.is_valuation_extreme(None, 2.0, DEFAULT_CFG) is False)
    check("neither extreme -> False", E.is_valuation_extreme(3.0, 0.5, DEFAULT_CFG) is False)
    check("both None -> False", E.is_valuation_extreme(None, None, DEFAULT_CFG) is False)


# ─────────────────── history cache (fix round 0, item 3) ────────────────────

def _write_dated(state_dir, d, rows_price, rows_cons):
    (state_dir / f"prices_{d}.jsonl").write_text("\n".join(json.dumps(r) for r in rows_price) + "\n")
    (state_dir / f"consensus_{d}.jsonl").write_text("\n".join(json.dumps(r) for r in rows_cons) + "\n")


def test_load_history_cache_excludes_as_of_and_is_shared_across_tickers():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        for d, price in (("2026-09-15", 10.0), ("2026-09-16", 11.0), ("2026-09-17", 12.0)):
            _write_dated(state_dir, d,
                        [{"ticker": "AAA", "date": d, "price": price, "mcap": price * 100, "quality": "ok"}],
                        [{"ticker": "AAA", "date": d, "metric": "SALES", "rel_period": 1,
                          "mean": 500.0, "count": 5, "up": 2, "down": 1, "quality": "ok"}])
        cache = E.load_history_cache(state_dir, exclude_date="2026-09-17")
        check("as_of excluded from the cache", "2026-09-17" not in cache, cache.keys())
        check("2 historical dates cached", sorted(cache.keys()) == ["2026-09-15", "2026-09-16"], cache.keys())
        # history_series() reads the SAME cache object for two different lenses/tickers --
        # no re-parsing, just dict lookups.
        prices = E.history_series("AAA", cache, lambda e: e.get("price"))
        check("history_series reads from the pre-built cache", sorted(prices) == [10.0, 11.0], prices)


def test_revision_breadth_uses_cache_not_filesystem():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        _write_dated(state_dir, "2026-08-20",
                    [{"ticker": "AAA", "date": "2026-08-20", "price": 10.0, "mcap": 1000.0, "quality": "ok"}],
                    [{"ticker": "AAA", "date": "2026-08-20", "metric": "SALES", "rel_period": 1,
                      "mean": 500.0, "count": 5, "up": 1, "down": 4, "quality": "ok"}])
        cache = E.load_history_cache(state_dir, exclude_date="2026-09-17")
        entry_now = {"up": {"fy1_sales": 5}, "down": {"fy1_sales": 1}}
        r = E.revision_breadth("AAA", entry_now, cache, "2026-09-17", 4)
        check("delta computed from the cache (no filesystem re-scan)",
             r["delta"] == (5 - 1) - (1 - 4), r)
        check("compared_to the cached date", r["compared_to"] == "2026-08-20", r)


def test_revision_breadth_na_when_cache_has_no_nearby_date():
    r = E.revision_breadth("AAA", {"up": {"fy1_sales": 5}, "down": {"fy1_sales": 1}}, {}, "2026-09-17", 4)
    check("empty cache -> n/a", r == {"delta": None, "note": "n/a"}, r)


# ─────────────────────────── build_card: skip reasons ───────────────────────

def test_build_card_not_in_snapshot():
    card = E.build_card("XYZ", None, DEFAULT_CFG, state_dir=Path("/tmp/nope"), as_of="2026-09-17",
                        stages={"pairs": {}, "gated": []}, ticker_themes_all={}, downside_theme_slugs=set(),
                        reads_rows=[])
    check("skipped True", card["skipped"] is True)
    check("reason: not in snapshot", card["reason"] == "not in snapshot", card)


def test_build_card_no_price_mcap_skip_reason():
    entry = {"price": None, "mcap": None, "fy1_sales": 100.0, "fy2_sales": 110.0, "fy3_sales": 120.0}
    card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path("/tmp/nope"), as_of="2026-09-17",
                        stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                        downside_theme_slugs=set(), reads_rows=[])
    check("skipped True", card["skipped"] is True)
    check("reason: no price/mcap", card["reason"] == "no price/mcap", card)


def test_build_card_missing_sales_generic_reason_when_no_raw_file():
    with tempfile.TemporaryDirectory() as td:
        entry = {"price": 100.0, "mcap": 5000.0, "fy1_sales": 100.0, "fy2_sales": None, "fy3_sales": 120.0}
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), reads_rows=[])
        check("skipped True", card["skipped"] is True)
        check("generic reason (no raw file present)", card["reason"] == "missing fy2_sales", card)


def test_build_card_quality_fail_rows_excluded_with_specific_reason():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        cons_rows = [{"ticker": "XYZ", "metric": "SALES", "rel_period": 2, "quality": "fail:count<1"}]
        (state_dir / "consensus_2026-09-17.jsonl").write_text(json.dumps(cons_rows[0]) + "\n")
        entry = {"price": 100.0, "mcap": 5000.0, "fy1_sales": 100.0, "fy2_sales": None, "fy3_sales": 120.0}
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=state_dir, as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), reads_rows=[])
        check("skipped True", card["skipped"] is True)
        check("specific quality-fail reason surfaced",
             card["reason"] == "quality fail: fail:count<1", card)


def test_build_card_full_card_no_net_debt_no_fundamentals_flags():
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0,
            "up": {"fy1_sales": 3}, "down": {"fy1_sales": 1}}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), reads_rows=[])
    check("not skipped", card["skipped"] is False, card)
    check("ev falls back to mcap", card["inputs"]["ev"] == 50000.0, card["inputs"])
    check("no_net_debt flagged", "no_net_debt" in card["flags"], card["flags"])
    check("margin_default flagged", "margin_default" in card["flags"], card["flags"])
    check("sector_family present", card["sector_family"] in ("software", "semis", "hardware", "internet", "default"))
    check("gap present", "gap_pp" in card["gap"])
    check("lenses ev_sales_fy1 computed", card["lenses"]["ev_sales_fy1"] == 50.0, card["lenses"])
    check("revision breadth n/a with no history", card["lenses"]["revision_breadth"]["4w"]["note"] == "n/a")
    check("credibility_source recorded on the card (top level)",
         card["credibility_source"] in ("pg", "file", "none"), card["credibility_source"])


def test_build_card_net_debt_from_fundamentals_changes_ev():
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0}
    fundamentals = {"XYZ": {"net_debt": 2000.0, "fcf_margin": 0.22}}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), reads_rows=[], fundamentals=fundamentals)
    check("EV = mcap + net_debt", card["inputs"]["ev"] == 52000.0, card["inputs"])
    check("no_net_debt NOT flagged", "no_net_debt" not in card["flags"], card["flags"])
    check("margin_default NOT flagged (fundamentals fcf_margin present)",
         "margin_default" not in card["flags"], card["flags"])
    check("fcf_margin_now from fundamentals", card["inputs"]["fcf_margin_now"] == 0.22, card["inputs"])


# ─────────────────────────── build_expectations / bundle shape ──────────────

def test_build_expectations_shape_and_universe_size():
    snapshot = {"as_of": "2026-09-17", "tickers": {
        "AAA": {"price": 10.0, "mcap": 1000.0, "fy1_sales": 100.0, "fy2_sales": 110.0,
               "fy3_sales": 121.0, "fy1_eps": 1.0},
        "BBB": {"price": None, "mcap": None, "fy1_sales": 50.0, "fy2_sales": 55.0, "fy3_sales": 60.0},
    }}
    with tempfile.TemporaryDirectory() as tdname:
        td = Path(tdname)
        (td / "config").mkdir()
        (td / "config" / "watchlist.yaml").write_text(
            "tier_1_bctk:\n  - ticker: AAA\n    themes: [x, y]\n"
            "tier_2_active_candidates:\n  - ticker: BBB\n    themes: [x, y]\n")
        (td / "notes").mkdir()
        state_dir = td / "state" / "valuation"
        orig_repo = pid.REPO
        pid.REPO = td
        try:
            result = E.build_expectations(snapshot, DEFAULT_CFG, state_dir=state_dir, as_of="2026-09-17",
                                          watchlist_path=td / "config" / "watchlist.yaml",
                                          notes_dir=td / "notes",
                                          reads_path=td / "state" / "thesis" / "reads.jsonl",
                                          polarity_path=td / "config" / "theme_polarity.yaml",
                                          stages_path=td / "state" / "topics" / "stages.json")
        finally:
            pid.REPO = orig_repo
    check("as_of carried through", result["as_of"] == "2026-09-17")
    check("AAA got a card", "AAA" in result["cards"], result["cards"].keys())
    check("BBB skipped (no price/mcap)", any(s["ticker"] == "BBB" for s in result["skipped"]), result["skipped"])
    latest = E.expectations_latest(result)
    check("expectations_latest.json shape has as_of/universe_size/skipped/tickers",
         set(("as_of", "universe_size", "skipped", "tickers")) <= set(latest.keys()), latest.keys())
    check("expectations_latest tickers keyed by ticker with full card",
         latest["tickers"]["AAA"]["ticker"] == "AAA", latest["tickers"]["AAA"])


def test_write_and_reread_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "expectations_latest.json"
        obj = {"as_of": "2026-09-17", "universe_size": 1, "skipped": [], "tickers": {"AAA": {"x": 1}}}
        E.write_json(obj, p)
        reread = json.loads(p.read_text())
        check("roundtrip identical", reread == obj)


def test_module_is_importable_as_a_script():
    import subprocess
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[0] / "expectations.py"),
                       "--help"], capture_output=True, text=True, timeout=30)
    check("expectations.py --help exits 0", r.returncode == 0, r.stderr[-300:])


if __name__ == "__main__":
    # Auto-discover every test_* function, alphabetically (fix round 0: manually listing
    # every name here was already drifting from the actual test set before this round
    # added 9 more; same auto-discovery convention as test_state_bundles.py).
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for _fn in _fns:
        _fn()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print(f"OK test_expectations ({len(_fns)} test functions)")
