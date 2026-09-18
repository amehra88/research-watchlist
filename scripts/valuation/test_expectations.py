"""Tests for scripts/valuation/expectations.py (RIS5 A5). No claude -p, no live DB —
run directly:
    python3 scripts/valuation/test_expectations.py
"""
from __future__ import annotations

import json
import statistics
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


_ONE_SIXTH = 1.0 / 6

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
        "durability": {"stage_term_bound": _ONE_SIXTH, "stage_term_per_level": 0.05,
                       "credibility_term_bound": _ONE_SIXTH, "reads_term_bound": _ONE_SIXTH,
                       "durability_score_bounds": [-0.5, 0.5]},
        "base_bounds": [-0.5, 2.0], "reads_min_dated": 3, "downside_multiplier": 0.85,
    },
    "peer": {"min_shared_themes": 2, "min_peers_for_z": 3},
    "history": {"min_days_for_z": 60},
    "valuation_extreme": {"gap_pp_threshold": 8, "peg_history_z_threshold": 2},
    "long_duration": {"terminal_share_threshold": 0.90, "min_forward_years": 3},
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
    check("C7: renamed to pv_residual_check (not pv_at_growth)",
         "pv_residual_check" in ig and "pv_at_growth" not in ig, ig.keys())
    check("L2: terminal_share_of_ev present and in (0,1)",
         ig["terminal_share_of_ev"] is not None and 0.0 < ig["terminal_share_of_ev"] < 1.0,
         ig["terminal_share_of_ev"])


def test_terminal_share_of_ev_none_when_growth_none():
    r = E.terminal_share_of_ev(None, 1000.0, 0.15, 0.30, 0.10, 0.03, 5, 8000.0)
    check("None growth -> None terminal share", r is None, r)
    r2 = E.terminal_share_of_ev(0.2, 1000.0, 0.15, 0.30, 0.10, 0.03, 5, None)
    check("None ev -> None terminal share", r2 is None, r2)


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


def test_read_stage_honours_all_three_marker_lists():
    """RIS5 A5 fix round 1, C6: gated / stage4_not_assertable / unheard ALL gate to
    unobserved -- test each independently, theme-level AND pair-level."""
    base_pairs = {"t1|AAA": 2, "t2|AAA": 2, "t3|AAA": 2, "t1|BBB": 2, "t2|BBB": 2, "t3|BBB": 2}
    stages_gated = {"pairs": dict(base_pairs), "gated": ["t1"], "stage4_not_assertable": [], "unheard": []}
    check("gated (theme-level) -> unobserved", E.read_stage(stages_gated, "t1", "AAA") is None)
    stages_s4 = {"pairs": dict(base_pairs), "gated": [], "stage4_not_assertable": ["t2|AAA"], "unheard": []}
    check("stage4_not_assertable (pair-level) -> unobserved", E.read_stage(stages_s4, "t2", "AAA") is None)
    check("stage4_not_assertable does not gate the OTHER ticker's pair",
         E.read_stage(stages_s4, "t2", "BBB") == 2, E.read_stage(stages_s4, "t2", "BBB"))
    stages_unheard = {"pairs": dict(base_pairs), "gated": [], "stage4_not_assertable": [], "unheard": ["t3"]}
    check("unheard (theme-level) -> unobserved", E.read_stage(stages_unheard, "t3", "AAA") is None)
    check("unheard (theme-level) gates every ticker under that theme",
         E.read_stage(stages_unheard, "t3", "BBB") is None)


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


def test_stage_rank_peer_basis_label():
    stages = {"pairs": {"t1|AAA": 2, "t1|BBB": 3}, "gated": []}
    term, flags, detail = E.stage_rank_term("AAA", stages, DEFAULT_CFG)
    check("C5: peer_basis labelled evidence_pairs", detail.get("peer_basis") == "evidence_pairs", detail)


# ─────────────────────────── credibility term ────────────────────────────────

class _FakeStore:
    def __init__(self, cred):
        self._cred = cred

    def credibility(self, ticker, metric="SALES"):
        return self._cred.get(ticker)


def test_credibility_term_neutral_flag_when_absent():
    term, flags, detail = E.credibility_term("NOPE", DEFAULT_CFG, store=_FakeStore({}), cross_median=0.6)
    check("no credibility -> term 0.0 (neutral)", term == 0.0, term)
    check("flagged no_credibility", "no_credibility" in flags, flags)
    check("source recorded even when empty", detail.get("source") in ("pg", "file"), detail)


def test_credibility_term_uncentred_when_cross_median_unavailable():
    """RIS5 A5 fix round 1, F6: no `cross_median` (cross-section unavailable) -> term 0.0
    with flag `credibility_uncentred`, distinct from `no_credibility` (this ticker DOES
    have data, just nothing to centre it against)."""
    store = _FakeStore({"GOOD": {"consensus_beat_rate": 0.9, "guide_hit_rate": 0.8}})
    term, flags, detail = E.credibility_term("GOOD", DEFAULT_CFG, store=store, cross_median=None)
    check("cross_median unavailable -> term 0.0", term == 0.0, term)
    check("flagged credibility_uncentred (not no_credibility)",
         flags == ["credibility_uncentred"], flags)
    check("avg_rate still recorded even though uncentred",
         abs(detail.get("avg_rate") - 0.85) < 1e-9, detail)


def test_credibility_term_centred_on_cross_median_not_fixed_half():
    """F6: centred on the CROSS-SECTIONAL median, not a fixed 0.5 -- a ticker whose
    avg_rate sits BELOW a high cross-sectional median gets a NEGATIVE term even though
    0.7 would have been positive under the old fixed-0.5 centering."""
    store = _FakeStore({"OKAY": {"consensus_beat_rate": 0.7, "guide_hit_rate": 0.7}})
    term, flags, detail = E.credibility_term("OKAY", DEFAULT_CFG, store=store, cross_median=0.9)
    check("below a high cross-median -> negative term", term < 0, term)
    check("no flags on a clean centred read", flags == [], flags)
    check("cross_median recorded on the card detail", detail.get("cross_median") == 0.9, detail)

    term2, flags2, detail2 = E.credibility_term("OKAY", DEFAULT_CFG, store=store, cross_median=0.5)
    check("same avg_rate, LOWER cross-median -> positive term", term2 > 0, term2)


def test_credibility_term_credibility_as_of_from_date_range():
    cred = {"consensus_beat_rate": 0.9, "guide_hit_rate": 0.8, "date_range": ["2025-06-30", "2026-03-31"]}
    store = _FakeStore({"GOOD": cred})
    term, flags, detail = E.credibility_term("GOOD", DEFAULT_CFG, store=store, cross_median=0.6)
    check("credibility_as_of = max(date_range)", detail.get("credibility_as_of") == "2026-03-31", detail)


def test_credibility_cross_median_and_cache():
    store = _FakeStore({
        "A": {"consensus_beat_rate": 1.0, "guide_hit_rate": 1.0},
        "B": {"consensus_beat_rate": 0.5, "guide_hit_rate": 0.5},
        "C": {"consensus_beat_rate": 0.0, "guide_hit_rate": 0.0},
    })
    cache = E.build_credibility_cache(["A", "B", "C", "D"], store=store)
    check("cache has an entry for every ticker asked, including a miss", set(cache) == {"A", "B", "C", "D"})
    median = E.credibility_cross_median(cache)
    check("cross median is the middle avg_rate (0.5)", median == 0.5, median)


def test_credibility_cross_median_none_when_cross_section_unavailable():
    store = _FakeStore({})
    cache = E.build_credibility_cache(["A", "B"], store=store)
    check("no ticker has data -> cross median None", E.credibility_cross_median(cache) is None)


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


def test_reads_latest_date():
    rows = _reads("T", "ai_positioning", 3) + [{"ticker": "T", "axis": "x", "date": "2026-05-01",
                                                "direction": "up", "magnitude": 1}]
    check("reads_latest_date is the max dated row for this ticker",
         E.reads_latest_date("T", rows) == "2026-05-01", E.reads_latest_date("T", rows))
    check("no rows for ticker -> None", E.reads_latest_date("ZZZ", rows) is None)


# ─────────────────────────── fade_growth_path (F3) ───────────────────────────

def test_fade_growth_path_neutral_durability_fades_halfway():
    fade = E.fade_growth_path(cagr=0.30, terminal_growth=0.03, durability_score=0.0)
    check("neutral durability -> persistence 0.5", fade["persistence"] == 0.5, fade)
    check("g_fade is the midpoint between cagr and terminal_growth",
         abs(fade["g_fade"] - (0.03 + (0.30 - 0.03) * 0.5)) < 1e-12, fade)
    check("base (5y CAGR of the 2-stage path) sits strictly between g_fade and cagr",
         fade["g_fade"] < fade["base"] < 0.30, fade)


def test_fade_growth_path_positive_durability_persists_more():
    fade_pos = E.fade_growth_path(cagr=0.30, terminal_growth=0.03, durability_score=0.5)
    check("durability_score at its max (+0.5) -> persistence 1.0 -> g_fade == cagr (no fade)",
         abs(fade_pos["persistence"] - 1.0) < 1e-12 and abs(fade_pos["g_fade"] - 0.30) < 1e-12, fade_pos)
    fade_neg = E.fade_growth_path(cagr=0.30, terminal_growth=0.03, durability_score=-0.5)
    check("durability_score at its min (-0.5) -> persistence 0.0 -> g_fade == terminal_growth (full fade)",
         abs(fade_neg["persistence"]) < 1e-12 and abs(fade_neg["g_fade"] - 0.03) < 1e-12, fade_neg)
    check("more durability -> higher base", fade_pos["base"] > fade_neg["base"], (fade_pos, fade_neg))


# ─────────────────────────── supported_growth (F3 fade + F5 + C1) ───────────

def test_supported_growth_base_and_downside_bounds():
    entry = {"fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}   # 20% CAGR
    result = E.supported_growth("T", entry, DEFAULT_CFG, stages={"pairs": {}, "gated": []},
                                ticker_themes_all={"T": []}, reads_rows=[], thesis_fm=None,
                                downside_theme_slugs=set())
    check("near_term_cagr ~ 20%", abs(result["near_term_cagr"] - 0.20) < 1e-9, result["near_term_cagr"])
    check("base within configured bounds", -0.5 <= result["base"] <= 2.0, result["base"])
    check("g_fade/persistence/durability_score present (fade model, no durability_multiplier)",
         "g_fade" in result and "persistence" in result and "durability_score" in result
         and "durability_multiplier" not in result, result)
    check("no challenge -> downside == base", result["downside"] == result["base"], result)


def test_supported_growth_downside_is_relative_085_when_challenged():
    """F5: downside = base * 0.85 (relative), not an absolute pp subtraction."""
    entry = {"fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}
    thesis_fm = {"assumptions": [
        {"id": "a1", "status": "challenged", "themes": ["chip_design_competition"]},
        {"id": "a2", "status": "open", "themes": ["chip_design_competition"]},
    ]}
    result = E.supported_growth("T", entry, DEFAULT_CFG, stages={"pairs": {}, "gated": []},
                                ticker_themes_all={"T": []}, reads_rows=[], thesis_fm=thesis_fm,
                                downside_theme_slugs={"chip_design_competition"})
    check("challenged assumption id listed", result["challenged_assumption_ids"] == ["a1"], result)
    expected = result["base"] * 0.85
    check("downside == base * 0.85 exactly", abs(result["downside"] - expected) < 1e-9,
         (result["downside"], expected))


def test_supported_growth_missing_sales_returns_none_base():
    result = E.supported_growth("T", {"fy1_sales": None, "fy3_sales": None}, DEFAULT_CFG,
                                stages={"pairs": {}, "gated": []}, ticker_themes_all={"T": []},
                                reads_rows=[], thesis_fm=None, downside_theme_slugs=set())
    check("missing sales -> base None", result["base"] is None)
    check("flagged", result["flags"] == ["missing fy1/fy3 sales for CAGR"], result["flags"])


def test_supported_growth_polarity_unavailable_nulls_challenged_and_downside():
    """RIS5 A5 fix round 1, C1: polarity_unavailable=True must NEVER read as "no
    assumption challenged" -- challenged_assumption_ids and downside come back None,
    with the flag on the card, even though a REAL challenged assumption exists (we just
    can't tell because the polarity config is unreadable)."""
    entry = {"fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}
    thesis_fm = {"assumptions": [{"id": "a1", "status": "challenged", "themes": ["chip_design_competition"]}]}
    result = E.supported_growth("T", entry, DEFAULT_CFG, stages={"pairs": {}, "gated": []},
                                ticker_themes_all={"T": []}, reads_rows=[], thesis_fm=thesis_fm,
                                downside_theme_slugs=set(), polarity_unavailable=True)
    check("challenged_assumption_ids is None, not []", result["challenged_assumption_ids"] is None, result)
    check("downside is None, not a value", result["downside"] is None, result)
    check("flagged polarity_unavailable", "polarity_unavailable" in result["flags"], result["flags"])
    check("base is still computed (only downside/challenged are affected)",
         result["base"] is not None, result)


# ─────────────────────────── C1: theme_polarity availability ────────────────

def test_load_downside_theme_slugs_missing_file_flags_unavailable():
    slugs, unavailable = E.load_downside_theme_slugs(Path("/tmp/does-not-exist-polarity.yaml"),
                                                      Path("/tmp/does-not-exist-watchlist.yaml"))
    check("missing polarity file -> slugs empty, unavailable True", slugs == set() and unavailable is True,
         (slugs, unavailable))


def test_load_downside_theme_slugs_success():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        wl = tdp / "watchlist.yaml"
        wl.write_text("themes:\n  semis: [chip_design_competition, ai_infrastructure_capex]\n")
        pol = tdp / "theme_polarity.yaml"
        pol.write_text("chip_design_competition: 0\nai_infrastructure_capex: 1\n"
                       "competition_slugs: [chip_design_competition]\n")
        slugs, unavailable = E.load_downside_theme_slugs(pol, wl)
        check("competition_slugs picked up, unavailable False",
             slugs == {"chip_design_competition"} and unavailable is False, (slugs, unavailable))


# ─────────────────────────── gap sign + gap ranges (F1) ──────────────────────

def test_gap_sign():
    pos = E.compute_gap(0.30, 0.15, 0.10)
    neg = E.compute_gap(0.10, 0.25, 0.20)
    check("implied > supported -> positive gap_pp", pos["gap_pp"] > 0, pos)
    check("implied < supported -> negative gap_pp", neg["gap_pp"] < 0, neg)
    check("gap_pp is in PERCENTAGE POINTS (x100), not a bare fraction",
         abs(pos["gap_pp"] - 15.0) < 1e-6, pos["gap_pp"])
    check("gap_downside_pp computed against the downside base",
         abs(pos["gap_downside_pp"] - 20.0) < 1e-6, pos)


def test_compute_gap_ranges_min_max_of_four_resolves():
    sensitivity = {"dr_plus": 0.35, "dr_minus": 0.25, "tm_plus": 0.28, "tm_minus": 0.32}
    gap_range, gap_downside_range = E.compute_gap_ranges(sensitivity, supported_base=0.20, supported_downside=0.15)
    check("gap_range = [min, max] of the 4 re-solves vs base",
         gap_range == [round((0.25 - 0.20) * 100, 4), round((0.35 - 0.20) * 100, 4)], gap_range)
    check("gap_downside_range against downside",
         gap_downside_range == [round((0.25 - 0.15) * 100, 4), round((0.35 - 0.15) * 100, 4)],
         gap_downside_range)


def test_compute_gap_ranges_none_when_supported_none():
    gap_range, gap_downside_range = E.compute_gap_ranges({"dr_plus": 0.3}, None, None)
    check("both ranges None when supported base/downside are None",
         gap_range is None and gap_downside_range is None, (gap_range, gap_downside_range))


def test_compute_gap_ranges_excludes_failed_resolves():
    sensitivity = {"dr_plus": 0.35, "dr_minus": None, "tm_plus": 0.28, "tm_minus": None}
    gap_range, _ = E.compute_gap_ranges(sensitivity, supported_base=0.20, supported_downside=None)
    check("None re-solves excluded from min/max, not treated as 0",
         gap_range == [round((0.28 - 0.20) * 100, 4), round((0.35 - 0.20) * 100, 4)], gap_range)


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
    check("C7: field is peer_score, not peer_z", "peer_score" in r and "peer_z" not in r, r)
    check("score gated below min_peers_for_z", r["peer_score"] is None, r)
    r2 = E.peer_lens(10.0, [8.0, 9.0, 11.0], 3)
    check("score computed at >= min_peers_for_z", r2["peer_score"] is not None, r2)


def test_peer_lens_median_mad_robust_to_outlier():
    """C7: median/MAD is robust to one wild outlier peer the way mean/stdev is not."""
    normal_peers = [10.0, 10.5, 9.5, 10.2]
    r_normal = E.peer_lens(11.0, normal_peers, 3)
    outlier_peers = [10.0, 10.5, 9.5, 500.0]   # one wildly mispriced peer
    r_outlier = E.peer_lens(11.0, outlier_peers, 3)
    check("median barely moves with one outlier peer",
         abs(r_normal["peer_median"] - r_outlier["peer_median"]) < 1.0,
         (r_normal["peer_median"], r_outlier["peer_median"]))
    check("peer_score stays informative (not crushed near 0) despite the outlier",
         r_outlier["peer_score"] is not None and abs(r_outlier["peer_score"]) > 0.1, r_outlier)


def test_theme_peers_min_shared_themes():
    ticker_themes = {"A": ["x", "y", "z"], "B": ["x", "y"], "C": ["x"], "D": ["q", "r"]}
    peers = E.theme_peers("A", ticker_themes, min_shared=2)
    check("2 shared themes -> peer", "B" in peers, peers)
    check("1 shared theme -> not a peer", "C" not in peers, peers)
    check("0 shared themes -> not a peer", "D" not in peers, peers)


def test_valuation_extreme_thresholds():
    """RIS5 A5 fix round 1, F1: signature is (gap_range, lens_history_z, flags, cfg) ->
    (extreme, reason); the gap branch needs min(gap_range) > 8 AND no margin_default/
    no_net_debt flag."""
    check("min(gap_range) just above 8pp, no vetoing flags -> extreme",
         E.is_valuation_extreme([8.01, 20.0], None, [], DEFAULT_CFG) == (True, None))
    check("min(gap_range) exactly 8pp -> NOT extreme (strict >)",
         E.is_valuation_extreme([8.0, 20.0], None, [], DEFAULT_CFG) == (False, None))
    check("lens_history_z just above 2 -> extreme",
         E.is_valuation_extreme(None, 2.01, [], DEFAULT_CFG) == (True, None))
    check("lens_history_z exactly 2 -> NOT extreme (strict >)",
         E.is_valuation_extreme(None, 2.0, [], DEFAULT_CFG) == (False, None))
    check("neither extreme -> False, no reason", E.is_valuation_extreme([3.0, 5.0], 0.5, [], DEFAULT_CFG) == (False, None))
    check("both None -> False, no reason", E.is_valuation_extreme(None, None, [], DEFAULT_CFG) == (False, None))


def test_valuation_extreme_gap_branch_vetoed_by_margin_default_or_no_net_debt():
    """F1's binding ruling: even a huge min(gap_range) must NOT fire the gap branch when
    the card carries margin_default or no_net_debt (the reverse-DCF ran on a
    sector-default assumption, not real fundamentals). Fix round 2, item 2: when the
    veto is what blocked the flag, a reason string is returned so "not extreme" can be
    told apart from "unverifiable"."""
    extreme, reason = E.is_valuation_extreme([50.0, 80.0], None, ["margin_default"], DEFAULT_CFG)
    check("margin_default vetoes the gap branch", extreme is False, extreme)
    check("reason names the vetoing flag", reason == "vetoed: margin_default", reason)

    extreme2, reason2 = E.is_valuation_extreme([50.0, 80.0], None, ["no_net_debt"], DEFAULT_CFG)
    check("no_net_debt vetoes the gap branch", extreme2 is False, extreme2)
    check("reason names the vetoing flag", reason2 == "vetoed: no_net_debt", reason2)

    extreme3, reason3 = E.is_valuation_extreme([50.0, 80.0], None, ["margin_default", "no_net_debt"], DEFAULT_CFG)
    check("both veto flags named in order", reason3 == "vetoed: margin_default, no_net_debt", reason3)

    extreme4, reason4 = E.is_valuation_extreme([50.0, 80.0], None, [], DEFAULT_CFG)
    check("neither flag present -> gap branch fires, no reason needed", extreme4 is True and reason4 is None,
         (extreme4, reason4))

    extreme5, reason5 = E.is_valuation_extreme([50.0, 80.0], 3.0, ["margin_default", "no_net_debt"], DEFAULT_CFG)
    check("z-branch still fires independently even with the veto flags present -- genuinely "
         "extreme, no veto framing needed", extreme5 is True and reason5 is None, (extreme5, reason5))


def test_valuation_extreme_no_reason_when_gap_would_not_have_fired_anyway():
    """The veto reason is ONLY set when the veto is what actually blocked the flag -- a
    small gap_range with veto flags present should not manufacture a spurious reason."""
    extreme, reason = E.is_valuation_extreme([2.0, 5.0], None, ["margin_default"], DEFAULT_CFG)
    check("not extreme, no reason (gap wouldn't have fired regardless of the veto)",
         extreme is False and reason is None, (extreme, reason))


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
        check("C4: raw up_now/down_now/up_then/down_then all present",
             (r["up_now"], r["down_now"], r["up_then"], r["down_then"]) == (5, 1, 1, 4), r)


def test_revision_breadth_na_when_cache_has_no_nearby_date():
    r = E.revision_breadth("AAA", {"up": {"fy1_sales": 5}, "down": {"fy1_sales": 1}}, {}, "2026-09-17", 4)
    check("empty cache -> n/a, but raw up_now/down_now still shown",
         r == {"delta": None, "note": "n/a", "up_now": 5, "down_now": 1, "up_then": None, "down_then": None}, r)


# ─────────────────────────── amendment v1.2: multiple ladder (L1) ───────────

def test_ev_multiple_fwd_averages_fy1_fy2_excludes_nonpositive():
    check("averages FY1+FY2", E.ev_multiple_fwd(1000.0, 100.0, 200.0) == 1000.0 / 150.0)
    check("FY1 only when FY2 missing", E.ev_multiple_fwd(1000.0, 100.0, None) == 10.0)
    check("negative/zero values excluded", E.ev_multiple_fwd(1000.0, 100.0, -50.0) == 10.0)
    check("None when nothing usable", E.ev_multiple_fwd(1000.0, None, -5.0) is None)
    check("None when ev is None", E.ev_multiple_fwd(None, 100.0, 200.0) is None)


def test_select_primary_lens_waterfall():
    peg_entry = {"fy1_eps": 2.0, "fy3_eps": 3.0, "fy1_sales": 100.0, "fy3_sales": 130.0}
    check("positive, growing EPS -> peg", E.select_primary_lens(peg_entry) == "peg")

    ebitda_entry = {"fy1_eps": -1.0, "fy3_eps": -0.5, "fy1_ebitda": 50.0, "fy3_ebitda": 80.0,
                    "fy1_sales": 100.0, "fy3_sales": 130.0}
    check("EPS<=0, EBITDA growing -> ev_ebitda_to_growth",
         E.select_primary_lens(ebitda_entry) == "ev_ebitda_to_growth")

    fcf_entry = {"fy1_eps": -1.0, "fy3_eps": -0.5, "fy1_fcf": 20.0, "fy3_fcf": 35.0,
                "fy1_sales": 100.0, "fy3_sales": 130.0}
    check("EPS<=0, no EBITDA, FCF growing -> ev_fcf_to_growth",
         E.select_primary_lens(fcf_entry) == "ev_fcf_to_growth")

    fcf_even_when_eps_positive = {"fy1_eps": 2.0, "fy3_eps": 1.5,   # EPS positive but SHRINKING
                                  "fy1_fcf": 20.0, "fy3_fcf": 35.0,
                                  "fy1_sales": 100.0, "fy3_sales": 130.0}
    check("(c) has no EPS-sign gate -- fires even when EPS is positive but growth<=0",
         E.select_primary_lens(fcf_even_when_eps_positive) == "ev_fcf_to_growth")

    sales_only = {"fy1_eps": -1.0, "fy3_eps": -2.0, "fy1_sales": 100.0, "fy3_sales": 130.0}
    check("nothing else eligible -> ev_sales_to_growth (last resort)",
         E.select_primary_lens(sales_only) == "ev_sales_to_growth")

    nothing = {"fy1_eps": -1.0, "fy3_eps": -2.0, "fy1_sales": 100.0, "fy3_sales": 80.0}
    check("even sales shrinking -> None (no valid lens)", E.select_primary_lens(nothing) is None)


def test_build_ladder_rung_shapes_and_flags():
    entry = {"price": 50.0, "fy1_eps": 2.0, "fy3_eps": 3.0, "fy1_sales": 1000.0, "fy3_sales": 1300.0}
    ladder = E.build_ladder(entry, ev=5000.0, ticker="T", ticker_themes_all={"T": []},
                            all_entries={}, fundamentals={}, history_cache={}, peers=[],
                            min_days=60, min_peers_for_z=3)
    check("all 4 rungs present", set(ladder) == set(E.RUNG_NAMES), ladder.keys())
    check("peg rung has a raw multiple and adjusted value", ladder["peg"]["adjusted"] is not None, ladder["peg"])
    check("ev_ebitda_to_growth rung is null with a reason (no EBITDA data)",
         ladder["ev_ebitda_to_growth"]["raw_multiple"] is None
         and "ev_ebitda_to_growth_unavailable" in ladder["ev_ebitda_to_growth"]["flags"],
         ladder["ev_ebitda_to_growth"])
    check("each rung's peers dict carries peer_basis watchlist_themes",
         ladder["peg"]["peers"]["peer_basis"] == "watchlist_themes", ladder["peg"]["peers"])


def test_build_ladder_rung_null_with_reason_when_growth_nonpositive():
    entry = {"price": 50.0, "fy1_eps": 2.0, "fy3_eps": 1.0,   # positive EPS but SHRINKING
            "fy1_sales": 1000.0, "fy3_sales": 900.0}
    ladder = E.build_ladder(entry, ev=5000.0, ticker="T", ticker_themes_all={"T": []},
                            all_entries={}, fundamentals={}, history_cache={}, peers=[],
                            min_days=60, min_peers_for_z=3)
    check("peg raw multiple present but adjusted is None (growth<=0)",
         ladder["peg"]["raw_multiple"] is not None and ladder["peg"]["adjusted"] is None, ladder["peg"])
    check("flagged growth<=0 or missing", "growth<=0 or missing" in ladder["peg"]["flags"], ladder["peg"])


# ─────────────────────────── amendment v1.2: horizon + long_duration (L2/L3) ─

def test_forward_years_available():
    check("3 years", E.forward_years_available({"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3}) == 3)
    check("2 years (fy3 missing)", E.forward_years_available({"fy1_sales": 1, "fy2_sales": 2}) == 2)
    check("1 year", E.forward_years_available({"fy1_sales": 1}) == 1)


def test_horizon_info_never_extends_without_count_ge_3():
    entry_no_fy4 = {"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3}
    h = E.horizon_info(entry_no_fy4)
    check("no fy4 data -> years_used stays [1,2,3]", h["years_used"] == [1, 2, 3], h)
    check("not extended", h["extended"] is False, h)

    entry_low_count = {"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3, "fy4_sales": 4,
                       "counts": {"fy4_sales": 2}}   # count < 3
    h2 = E.horizon_info(entry_low_count)
    check("fy4 present but count<3 -> NOT extended", h2["years_used"] == [1, 2, 3], h2)

    entry_extended = {"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3, "fy4_sales": 4,
                      "counts": {"fy4_sales": 3}}
    h3 = E.horizon_info(entry_extended)
    check("fy4 present with count>=3 -> extended to year 4", h3["years_used"] == [1, 2, 3, 4], h3)
    check("never extends to fy5 without fy4 first",
         E.horizon_info({"fy1_sales": 1, "fy2_sales": 2, "fy3_sales": 3, "fy5_sales": 5,
                        "counts": {"fy5_sales": 10}})["years_used"] == [1, 2, 3])


def test_determine_long_duration_each_trigger_independently():
    """Fix round 2: threshold recalibrated to 0.90 (was 0.75); the forward-years check is
    now `lens_forward_years` (the SELECTED lens's own denominator, e.g. EPS years for
    peg), reason string renamed `lens_forward_years<min`."""
    check("terminal_share > threshold (0.90)", E.determine_long_duration(0.95, 3, "peg", DEFAULT_CFG) ==
         (True, ["terminal_share_of_ev>threshold"]))
    check("terminal_share of 0.80 no longer trips it (recalibration)",
         E.determine_long_duration(0.80, 3, "peg", DEFAULT_CFG) == (False, []))
    check("lens_forward_years < min", E.determine_long_duration(0.5, 2, "peg", DEFAULT_CFG) ==
         (True, ["lens_forward_years<min"]))
    check("primary lens is last resort", E.determine_long_duration(0.5, 3, "ev_sales_to_growth", DEFAULT_CFG) ==
         (True, ["primary_lens_last_resort"]))
    check("none fire -> not long_duration", E.determine_long_duration(0.5, 3, "peg", DEFAULT_CFG) == (False, []))
    is_ld, reasons = E.determine_long_duration(0.95, 2, "ev_sales_to_growth", DEFAULT_CFG)
    check("all three fire together, all reasons listed", is_ld is True and len(reasons) == 3, reasons)


def test_forward_years_available_for_lens_uses_selected_lens_denominator():
    """Fix round 2, item 1: the long_duration gate reads forward years off the SELECTED
    lens's own denominator, not always sales -- 3 years of sales but only 1 year of EPS
    (for a peg-primary card) must read as 1, not 3."""
    entry = {"fy1_sales": 100.0, "fy2_sales": 110.0, "fy3_sales": 121.0,
            "fy1_eps": 2.0, "fy2_eps": None, "fy3_eps": None,
            "fy1_ebitda": 10.0, "fy2_ebitda": 11.0, "fy3_ebitda": 12.0}
    check("peg primary -> reads EPS years (1), not sales years (3)",
         E.forward_years_available_for_lens(entry, "peg") == 1,
         E.forward_years_available_for_lens(entry, "peg"))
    check("ev_ebitda_to_growth primary -> reads EBITDA years (3)",
         E.forward_years_available_for_lens(entry, "ev_ebitda_to_growth") == 3,
         E.forward_years_available_for_lens(entry, "ev_ebitda_to_growth"))
    check("ev_sales_to_growth primary -> reads sales years (3)",
         E.forward_years_available_for_lens(entry, "ev_sales_to_growth") == 3,
         E.forward_years_available_for_lens(entry, "ev_sales_to_growth"))
    check("no valid lens (None) -> falls back to sales years",
         E.forward_years_available_for_lens(entry, None) == 3,
         E.forward_years_available_for_lens(entry, None))


def test_duration_note_formats_percent_and_year():
    check("formats percent and year", E.duration_note(0.82, 5) == "82% of EV rests beyond year 5",
         E.duration_note(0.82, 5))
    check("rounds to nearest percent", E.duration_note(0.8249, 5) == "82% of EV rests beyond year 5")
    check("None terminal_share -> None note", E.duration_note(None) is None)


# ─────────────────────────── F7: priced-in component ─────────────────────────

def test_load_gap_history_excludes_as_of_and_nulls():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        (state_dir / "expectations_2026-09-15.jsonl").write_text(
            json.dumps({"ticker": "AAA", "gap": {"gap_pp": 5.0}}) + "\n" +
            json.dumps({"ticker": "BBB", "gap": {"gap_pp": None}}) + "\n")
        (state_dir / "expectations_2026-09-17.jsonl").write_text(
            json.dumps({"ticker": "AAA", "gap": {"gap_pp": 999.0}}) + "\n")   # today, excluded
        hist = E.load_gap_history(state_dir, exclude_date="2026-09-17")
        check("today excluded", "2026-09-17" not in hist, hist)
        check("AAA's gap_pp carried, BBB's null gap_pp excluded",
             hist["2026-09-15"] == {"AAA": 5.0}, hist)


def test_compute_gap_z_cross_section_includes_self():
    """F7 + coordinator review: cross-sectional z includes the ticker's own value in the
    mean/stdev (the standard cross-sectional-z reading), not a leave-one-out peer z."""
    gap_today = {"AAA": 10.0, "BBB": 20.0, "CCC": 30.0}
    z, basis, n = E.compute_gap_z("AAA", 10.0, gap_today, {}, min_days=60)
    check("basis is cross_section (no own-history)", basis == "cross_section", basis)
    check("n reflects the full cross-section including self", n == 3, n)
    mean, stdev = statistics.mean(gap_today.values()), statistics.pstdev(gap_today.values())
    check("z computed against the full cross-section", abs(z - (10.0 - mean) / stdev) < 1e-9, z)


def test_compute_gap_z_switches_to_own_history_at_60_points():
    own_series = {f"2026-{i:02d}-01": {"AAA": 5.0} for i in range(1, 61)}   # 60 points, exactly at the gate
    gap_today = {"AAA": 5.0, "BBB": 999.0}
    z, basis, n = E.compute_gap_z("AAA", 5.0, gap_today, own_series, min_days=60)
    check("switches to own_history at exactly 60 points", basis == "own_history", basis)
    check("n_days from the own-history series", n == 60, n)


def test_combine_priced_in_clips_and_lists_available():
    piv, avail = E.combine_priced_in(gap_z=5.0, lens_history_z=None, lens_peer_score=1.0)
    check("mean of available, clipped to [-3,3]", piv == 3.0, piv)
    check("available lists only the non-null inputs", avail == ["gap_z", "lens_peer_score"], avail)

    piv2, avail2 = E.combine_priced_in(None, None, None)
    check("nothing available -> None, empty list", piv2 is None and avail2 == [], (piv2, avail2))


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


def test_build_card_mcap_null_skip_reason_is_specific():
    """RIS5 A5 live run: A3's real build_latest() seats `price` even when `mcap` fails its
    OWN quality check (currency mismatch / fail:mcap<=0) -- price-present-mcap-null must
    get a SPECIFIC skip reason (`no_mcap`), distinct from the "no price at all" case
    above, per the coordinator's explicit instruction (these 16 real tickers return once
    FX conversion lands)."""
    entry = {"price": 68.5, "mcap": None, "price_currency": "USD", "mcap_currency": None,
            "fy1_sales": 100.0, "fy2_sales": 110.0, "fy3_sales": 120.0}
    card = E.build_card("ADR_LIKE", entry, DEFAULT_CFG, state_dir=Path("/tmp/nope-no-mcap"), as_of="2026-09-17",
                        stages={"pairs": {}, "gated": []}, ticker_themes_all={"ADR_LIKE": []},
                        downside_theme_slugs=set())
    check("skipped True", card["skipped"] is True, card)
    check("reason: no_mcap (specific, not the generic no price/mcap)", card["reason"] == "no_mcap", card)


def test_build_card_missing_fy1_sales_still_skips():
    entry = {"price": 100.0, "mcap": 5000.0, "fy1_sales": None, "fy2_sales": 110.0, "fy3_sales": 120.0}
    card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path("/tmp/nope-missing-fy1"), as_of="2026-09-17",
                        stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                        downside_theme_slugs=set())
    check("fy1_sales missing -> still skipped (it anchors Layer 1)", card["skipped"] is True, card)
    check("reason: missing fy1_sales", card["reason"] == "missing fy1_sales", card)


def test_build_card_missing_fy2_or_fy3_sales_is_long_duration_not_skipped():
    """RIS5 A5 fix round 1, L3: only fy1_sales is mandatory now -- a ticker missing
    fy2/fy3 sales gets a long_duration card (SPCX-like), not a skip."""
    with tempfile.TemporaryDirectory() as td:
        entry = {"price": 100.0, "mcap": 5000.0, "fy1_sales": 100.0, "fy2_sales": 110.0, "fy3_sales": None,
                "fy1_eps": 2.0, "fy3_eps": 3.0}
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
        check("NOT skipped", card["skipped"] is False, card)
        check("flagged missing_fy3_sales", any(f.startswith("missing_fy3_sales") for f in card["flags"]), card["flags"])
        check("long_duration True (only 2 forward years)", card["long_duration"] is True, card)
        check("reason includes lens_forward_years<min",
             "lens_forward_years<min" in card["long_duration_reasons"], card)
        check("supported/gap/valuation_extreme/valuation_extreme_reason/priced_in all null",
             card["layer2_supported"] is None and card["gap"] is None and card["valuation_extreme"] is None
             and card["valuation_extreme_reason"] is None and card["priced_in"] is None, card)
        check("layer1_priced/lenses/inputs still shown (only priced fields)",
             card["layer1_priced"] is not None and card["lenses"] is not None, card)


def test_build_card_quality_fail_reason_surfaced_as_flag_not_skip():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        cons_rows = [{"ticker": "XYZ", "metric": "SALES", "rel_period": 2, "quality": "fail:count<1"}]
        (state_dir / "consensus_2026-09-17.jsonl").write_text(json.dumps(cons_rows[0]) + "\n")
        entry = {"price": 100.0, "mcap": 5000.0, "fy1_sales": 100.0, "fy2_sales": None, "fy3_sales": 120.0}
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=state_dir, as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
        check("NOT skipped (only fy1_sales is mandatory)", card["skipped"] is False, card)
        check("specific quality-fail reason surfaced as a flag",
             "missing_fy2_sales:fail:count<1" in card["flags"], card["flags"])


def test_build_card_margin_path_nonpositive_skips_no_partial_card():
    """C3: margin_path_nonpositive SKIPS the whole ticker -- no partial card."""
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    cfg["fcf_margin_now_by_family"]["default"] = -0.05   # nonpositive fcf_margin_now
    cfg["terminal_margin_by_family"]["default"] = -0.05
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, cfg, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
    check("skipped True", card["skipped"] is True, card)
    check("reason: margin_path_nonpositive", card["reason"] == "margin_path_nonpositive", card)
    check("no partial card fields leaked", set(card.keys()) == {"ticker", "skipped", "reason"}, card)


def test_build_card_full_card_no_net_debt_no_fundamentals_flags():
    # mcap chosen so terminal_share_of_ev stays well under 0.90 under the flat default
    # margin path (see the dedicated long_duration tests below for the mechanism); fy2_eps
    # included so the primary lens (peg) clears the lens_forward_years>=3 gate too --
    # this is meant to be an ORDINARY card, not a long_duration one.
    entry = {"price": 100.0, "mcap": 2500.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0, "fy2_eps": 5.0, "fy3_eps": 6.0,
            "up": {"fy1_sales": 3, "fy1_eps": 2}, "down": {"fy1_sales": 1, "fy1_eps": 0}}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
    check("not skipped", card["skipped"] is False, card)
    check("ev falls back to mcap", card["inputs"]["ev"] == 2500.0, card["inputs"])
    check("no_net_debt flagged", "no_net_debt" in card["flags"], card["flags"])
    check("margin_default flagged", "margin_default" in card["flags"], card["flags"])
    check("breadth_semantics_unverified always flagged (C4)",
         "breadth_semantics_unverified" in card["flags"], card["flags"])
    check("sector_family present", card["sector_family"] in ("software", "semis", "hardware", "internet", "default"))
    check("NOT long_duration", card["long_duration"] is False, card)
    check("gap present", "gap_pp" in card["gap"])
    check("gap_range present (F1)", "gap_range" in card["gap"], card["gap"])
    check("valuation_extreme_reason key present (fix round 2, item 2)",
         "valuation_extreme_reason" in card, card)
    check("duration_note present (fix round 2, item 1)", card["duration_note"] is not None, card)
    check("lenses ev_sales_fy1 computed", card["lenses"]["ev_sales_fy1"] == 2.5, card["lenses"])
    check("revision breadth is now split by fy1_sales/fy1_eps (C4)",
         set(card["lenses"]["revision_breadth"]) == {"fy1_sales", "fy1_eps"}, card["lenses"]["revision_breadth"])
    check("revision breadth n/a with no history", card["lenses"]["revision_breadth"]["fy1_sales"]["4w"]["note"] == "n/a")
    check("raw counts present even when n/a",
         card["lenses"]["revision_breadth"]["fy1_sales"]["4w"]["up_now"] == 3, card["lenses"]["revision_breadth"])
    check("credibility_source recorded on the card (top level)",
         card["credibility_source"] in ("pg", "file", "none"), card["credibility_source"])
    check("primary_lens is peg (positive EPS, positive EPS CAGR)", card["primary_lens"] == "peg", card)
    check("ladder present with all 4 rungs", set(card["lenses"]["ladder"]) == {"primary"} | set(E.RUNG_NAMES),
         card["lenses"]["ladder"].keys())
    check("provenance block present (C5)",
         set(("snapshot_as_of", "stages_as_of", "reads_latest_date", "credibility_as_of"))
         <= set(card["provenance"].keys()), card["provenance"])
    check("horizon block present (L2)", card["horizon"]["years_used"] == [1, 2, 3], card["horizon"])


def test_build_card_net_debt_from_fundamentals_changes_ev():
    # "fcf" (a raw dollar figure), NOT "fcf_margin" -- the real fundamentals_<date>.jsonl
    # shape confirmed live 2026-09-17 (RIS5 A5 live run); see derive_fcf_margin().
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0}
    fundamentals = {"XYZ": {"net_debt": 2000.0, "fcf": 220.0}}   # 220/1000 = 0.22 margin
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), fundamentals=fundamentals)
    check("EV = mcap + net_debt", card["inputs"]["ev"] == 52000.0, card["inputs"])
    check("no_net_debt NOT flagged", "no_net_debt" not in card["flags"], card["flags"])
    check("margin_default NOT flagged (real fcf present, derived instead)",
         "margin_default" not in card["flags"], card["flags"])
    check("flagged fcf_margin_derived", "fcf_margin_derived" in card["flags"], card["flags"])
    check("fcf_margin_now derived as fcf / fy1_sales",
         abs(card["inputs"]["fcf_margin_now"] - 0.22) < 1e-9, card["inputs"])


def test_build_card_negative_net_debt_reduces_ev():
    """F4: net_debt may be NEGATIVE (net cash) -- EV = mcap + net_debt handles that by
    plain addition, reducing EV below mcap."""
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0}
    fundamentals = {"XYZ": {"net_debt": -8000.0, "fcf": 220.0}}   # net CASH position
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set(), fundamentals=fundamentals)
    check("EV = mcap + (negative) net_debt < mcap", card["inputs"]["ev"] == 42000.0, card["inputs"])
    check("no_net_debt NOT flagged (fundamentals present, sign irrelevant)",
         "no_net_debt" not in card["flags"], card["flags"])


# ─────────────────────── derive_fcf_margin (RIS5 A5 live run) ───────────────

def test_derive_fcf_margin_computed_from_real_fcf_key():
    entry = {"fy1_sales": 1000.0}
    margin, flags = E.derive_fcf_margin({"fcf": 350.0}, entry, now_default=0.20)
    check("margin = fcf / fy1_sales", abs(margin - 0.35) < 1e-9, margin)
    check("flagged fcf_margin_derived, not margin_default", flags == ["fcf_margin_derived"], flags)


def test_derive_fcf_margin_negative_fcf_gives_negative_margin():
    """COHR-shaped real case: FF_FREE_CF can be negative (a quarter with negative free
    cash flow) -- the derived margin is genuinely negative, still flagged derived (not
    silently floored or discarded)."""
    entry = {"fy1_sales": 10608.17}
    margin, flags = E.derive_fcf_margin({"fcf": -486.225}, entry, now_default=0.12)
    check("negative fcf -> negative derived margin", margin < 0, margin)
    check("still flagged fcf_margin_derived (not silently defaulted)",
         flags == ["fcf_margin_derived"], flags)


def test_derive_fcf_margin_falls_back_when_fcf_missing():
    margin, flags = E.derive_fcf_margin({}, {"fy1_sales": 1000.0}, now_default=0.20)
    check("no fcf row -> falls back to now_default", margin == 0.20, margin)
    check("flagged margin_default", flags == ["margin_default"], flags)


def test_derive_fcf_margin_falls_back_when_fy1_sales_missing_or_nonpositive():
    margin1, flags1 = E.derive_fcf_margin({"fcf": 100.0}, {"fy1_sales": None}, now_default=0.20)
    check("fy1_sales None -> falls back", margin1 == 0.20 and flags1 == ["margin_default"], (margin1, flags1))
    margin2, flags2 = E.derive_fcf_margin({"fcf": 100.0}, {"fy1_sales": 0.0}, now_default=0.20)
    check("fy1_sales == 0 -> falls back (can't divide)", margin2 == 0.20 and flags2 == ["margin_default"],
         (margin2, flags2))
    margin3, flags3 = E.derive_fcf_margin({"fcf": 100.0}, {"fy1_sales": -50.0}, now_default=0.20)
    check("fy1_sales negative -> falls back (nonsensical denominator)",
         margin3 == 0.20 and flags3 == ["margin_default"], (margin3, flags3))


def test_build_card_real_shaped_fundamentals_cohr_like_negative_margin_skips():
    """Sanity check on the live-run mechanism, hand-crafted: a COHR-shaped negative
    derived FCF margin can push the margin PATH negative in year 1 (linear interpolation
    from a negative fcf_margin_now toward a small positive terminal_margin) -- C3 then
    SKIPS the ticker (margin_path_nonpositive), same guard as any other nonpositive
    margin path. This is a real, surfaced consequence of live data, not a code bug --
    see the A5 report's Live run section."""
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    cfg["terminal_margin_by_family"]["default"] = 0.12
    entry = {"price": 296.0, "mcap": 56777.6, "fy1_sales": 10608.17, "fy2_sales": 14583.9,
            "fy3_sales": 19071.8, "fy1_eps": 9.44, "fy3_eps": 18.55}
    fundamentals = {"COHR_LIKE": {"net_debt": 1532.82, "fcf": -486.225}}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("COHR_LIKE", entry, cfg, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"COHR_LIKE": []},
                            downside_theme_slugs=set(), fundamentals=fundamentals)
    check("skipped due to the negative derived margin pushing the path nonpositive",
         card["skipped"] is True and card["reason"] == "margin_path_nonpositive", card)


def test_build_card_ebitda_fcf_unavailable_flag_and_no_profit_lens():
    """L1: EPS<=0 with no EBITDA/FCF data at all -> ladder falls to (d) EV/Sales-to-growth
    -> flagged both no_profit_lens (last resort) and ebitda_fcf_unavailable (A3 hasn't
    added those fields yet)."""
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": -1.0, "fy3_eps": -0.5}   # unprofitable, no EBITDA/FCF
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
    check("primary_lens falls to ev_sales_to_growth", card["primary_lens"] == "ev_sales_to_growth", card)
    check("flagged no_profit_lens", "no_profit_lens" in card["flags"], card["flags"])
    check("flagged ebitda_fcf_unavailable", "ebitda_fcf_unavailable" in card["flags"], card["flags"])


def test_build_card_ebitda_selected_when_eps_negative_and_ebitda_growing():
    entry = {"price": 100.0, "mcap": 50000.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0, "fy3_sales": 1440.0,
            "fy1_eps": -1.0, "fy3_eps": -0.5,
            "fy1_ebitda": 200.0, "fy2_ebitda": 260.0, "fy3_ebitda": 320.0}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
    check("primary_lens is ev_ebitda_to_growth", card["primary_lens"] == "ev_ebitda_to_growth", card)
    check("no_profit_lens NOT flagged", "no_profit_lens" not in card["flags"], card["flags"])
    check("ebitda_fcf_unavailable NOT flagged (EBITDA present)",
         "ebitda_fcf_unavailable" not in card["flags"], card["flags"])
    rung = card["lenses"]["ladder"]["ev_ebitda_to_growth"]
    check("EV/EBITDA rung has a raw multiple and adjusted value",
         rung["raw_multiple"] is not None and rung["adjusted"] is not None, rung)


def test_build_card_long_duration_huge_terminal_share_tsla_like():
    """L3 (fix round 2, recalibrated to 0.90): a TSLA-like fixture needs a genuinely
    extreme multiple to trip 0.90 -- a flat margin path structurally caps terminal_share
    well below 0.90 for any realistic multiple (verified: even a 300-400x EV/sales,
    ~150-200% implied growth barely clears it), which is the whole point of the
    recalibration (ordinary high-growth names should NOT trip this any more). Verified
    via the actual mechanism (terminal_share_of_ev), not hardcoded."""
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    cfg["fcf_margin_now_by_family"]["default"] = 0.35
    cfg["terminal_margin_by_family"]["default"] = 0.35   # flat path (like the real config's defaults)
    # fy2_eps included so the ONLY trigger firing is terminal_share_of_ev (not also
    # lens_forward_years<min) -- isolates the mechanism this test is about.
    entry = {"price": 300.0, "mcap": 200_000_000.0, "fy1_sales": 100000.0, "fy2_sales": 130000.0,
            "fy3_sales": 175000.0, "fy1_eps": 3.0, "fy2_eps": 4.2, "fy3_eps": 5.5}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("TSLA_LIKE", entry, cfg, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"TSLA_LIKE": []},
                            downside_theme_slugs=set())
    check("long_duration reason is ONLY terminal_share (isolated mechanism)",
         card["long_duration_reasons"] == ["terminal_share_of_ev>threshold"], card["long_duration_reasons"])
    check("terminal_share_of_ev > 0.90 (the mechanical trigger, recalibrated)",
         card["layer1_priced"]["terminal_share_of_ev"] > 0.90, card["layer1_priced"]["terminal_share_of_ev"])
    check("card is long_duration", card["long_duration"] is True, card)
    check("reason includes terminal_share_of_ev>threshold",
         "terminal_share_of_ev>threshold" in card["long_duration_reasons"], card)
    check("supported/gap/valuation_extreme/valuation_extreme_reason/priced_in nulled",
         card["layer2_supported"] is None and card["gap"] is None and card["valuation_extreme"] is None
         and card["valuation_extreme_reason"] is None and card["priced_in"] is None, card)
    check("layer1_priced (what is priced) still shown", card["layer1_priced"]["implied_growth_5y"] is not None, card)
    check("duration_note present and plain-English", card["duration_note"] is not None
         and "% of EV rests beyond year" in card["duration_note"], card["duration_note"])


def test_duration_note_shown_even_when_not_long_duration():
    """Fix round 2, item 1: duration_note is printed on EVERY card, not just
    long_duration ones, so a reader sees the terminal-value share without the mark."""
    entry = {"price": 100.0, "mcap": 2500.0, "fy1_sales": 1000.0, "fy2_sales": 1200.0,
            "fy3_sales": 1440.0, "fy1_eps": 4.0, "fy2_eps": 5.0, "fy3_eps": 6.0}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("XYZ", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"XYZ": []},
                            downside_theme_slugs=set())
    check("not long_duration", card["long_duration"] is False, card)
    check("duration_note still present", card["duration_note"] is not None, card)


def test_build_card_long_duration_two_forward_years_spcx_like():
    """L3: a SPCX-like fixture -- only 2 forward years of consensus (fy3 missing)."""
    entry = {"price": 50.0, "mcap": 20000.0, "fy1_sales": 5000.0, "fy2_sales": 8000.0, "fy3_sales": None,
            "fy1_eps": 0.5, "fy3_eps": None}
    with tempfile.TemporaryDirectory() as td:
        card = E.build_card("SPCX_LIKE", entry, DEFAULT_CFG, state_dir=Path(td), as_of="2026-09-17",
                            stages={"pairs": {}, "gated": []}, ticker_themes_all={"SPCX_LIKE": []},
                            downside_theme_slugs=set())
    check("NOT skipped (fy1_sales present)", card["skipped"] is False, card)
    check("only 2 forward years available", card["horizon"]["years_available"] == 2, card["horizon"])
    check("card is long_duration", card["long_duration"] is True, card)
    check("reason includes lens_forward_years<min",
         "lens_forward_years<min" in card["long_duration_reasons"], card)
    check("layer1_priced still shown (implied growth is computable off fy1_sales alone)",
         card["layer1_priced"]["implied_growth_5y"] is not None, card)


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
    check("priced_in attached (F7, second pass)", "priced_in" in result["cards"]["AAA"], result["cards"]["AAA"])
    check("layer1_priced has no pv_residual_check leaking through the write path (C7)",
         "pv_residual_check" not in result["cards"]["AAA"]["layer1_priced"], result["cards"]["AAA"]["layer1_priced"])


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
