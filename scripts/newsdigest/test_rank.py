"""
Tests for the editorial selection pass (rank.py).

The LLM call is not exercised here — what is tested is everything that must hold REGARDLESS of
what the model returns, because those are the guarantees the operator actually asked for:
  • the digest is capped at `limit`,
  • one ticker cannot eat the digest (the 2026-08-19 SK Hynix case: 26 of 262 items, one event),
  • sell-side rating actions sort LAST in the deterministic order,
  • a ranking failure degrades to that order and REPORTS it — never a silent drop.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_rank.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import rank  # noqa: E402
from newsdigest.classify_llm import Classification  # noqa: E402

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
TIERS = {"NVDA": "tier_1_bctk", "MU": "tier_1_bctk", "000660.KS": "tier_2_active_candidates",
         "DASH": "tier_2_active_candidates", "GNW": "tier_3_watch"}


class FakeC:
    """Minimal stand-in for cluster.Cluster (only what rank.py touches)."""
    def __init__(self, cid, titles, age_min=0, volume=1):
        self.hash = cid
        self._volume = volume
        self.items = [{"title": t, "published": NOW - timedelta(minutes=age_min)} for t in titles]

    @property
    def volume(self):
        return self._volume


def mk(cid, ticker, titles, conf="high", age=0, macro=None, themes=None, volume=1):
    cls = Classification(cluster_id=cid, materiality=[ticker] if ticker else [],
                         macro=macro or [], themes=themes or [], confidence=conf)
    return FakeC(cid, titles, age_min=age, volume=volume), cls


def test_cap_is_enforced():
    survivors = [mk(f"c{i}", f"T{i}", [f"Company {i} announces new fab"]) for i in range(50)]
    picked, _capped = rank._apply_caps(survivors, limit=30, max_per_ticker=2)
    assert len(picked) == 30, f"expected exactly 30, got {len(picked)}"
    print("  ✓ selection is capped at the limit")


def test_one_ticker_cannot_eat_the_digest():
    """The real 2026-08-19 failure: 26 SK Hynix items, all one buyback, sorted to the top."""
    hynix = [mk(f"h{i}", "000660.KS", [f"SK Hynix buyback story variant {i}"]) for i in range(26)]
    others = [mk(f"o{i}", f"T{i}", [f"Other company {i} raises guidance"]) for i in range(10)]
    picked, capped = rank._apply_caps(hynix + others, limit=30, max_per_ticker=2)
    n_hynix = sum(1 for _c, cls in picked if cls.materiality == ["000660.KS"])
    assert n_hynix == 2, f"SK Hynix took {n_hynix} slots, expected 2"
    # the cap is HARD: 24 over-cap SK Hynix clusters are DROPPED, not used to pad the digest
    assert len(picked) == 12 and capped == 24, (len(picked), capped)
    print("  ✓ per-ticker cap is hard (26 SK Hynix clusters → 2 slots, 24 dropped, no padding)")


def test_macro_and_theme_are_not_ticker_capped():
    macro = [mk(f"m{i}", None, [f"US CPI print detail {i}"], macro=["inflation"]) for i in range(5)]
    picked, _capped = rank._apply_caps(macro, limit=30, max_per_ticker=2)
    assert len(picked) == 5, "macro stories must not be squeezed by the per-ticker cap"
    print("  ✓ macro/theme buckets are exempt from the per-ticker cap")


def test_sell_side_sorts_last():
    real = mk("real", "NVDA", ["Nvidia raises data center capacity guidance for FY27"])
    rating = mk("rating", "NVDA", ["Morgan Stanley upgrades Nvidia on datacenter demand checks"])
    ordered = rank.deterministic_order([rating, real], TIERS)
    assert ordered[0][0].hash == "real", "a business story must outrank a rating action"
    assert ordered[-1][0].hash == "rating"
    print("  ✓ sell-side rating actions sort last in the deterministic order")


def test_tier_then_confidence_ordering():
    t1_low = mk("a", "NVDA", ["Nvidia signs supply agreement"], conf="low")
    t2_high = mk("b", "DASH", ["DoorDash announces buyback"], conf="high")
    t1_high = mk("c", "MU", ["Micron lifts HBM output"], conf="high")
    ordered = rank.deterministic_order([t2_high, t1_low, t1_high], TIERS)
    assert [p[0].hash for p in ordered] == ["c", "a", "b"], [p[0].hash for p in ordered]
    print("  ✓ deterministic order is tier → confidence → recency")


def test_no_llm_call_when_under_limit():
    survivors = [mk(f"c{i}", f"T{i}", [f"Story {i}"]) for i in range(12)]
    picked, cost, note, ranked = rank.select_top(survivors, repo_root=".", limit=30, tier_map=TIERS)
    assert len(picked) == 12 and cost == 0.0 and note is None and ranked
    print("  ✓ under the limit, selection is free (no claude -p call at all)")


def test_ranking_failure_falls_back_and_reports():
    """A broken ranking call must degrade visibly, never silently drop the digest."""
    survivors = [mk(f"c{i}", "NVDA" if i % 2 else "MU", [f"Story {i}"]) for i in range(40)]
    orig = rank._rank_once
    rank._rank_once = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("claude -p rc=1"))
    try:
        picked, cost, note, ranked = rank.select_top(survivors, repo_root=".", limit=30, tier_map=TIERS)
    finally:
        rank._rank_once = orig
    assert note and "deterministic" in note, f"failure must be reported, got {note!r}"
    assert not ranked, "a true fallback must report ranked=False so the caller alerts"
    assert len(picked) == 4, f"2 tickers x max 2 = 4 (hard cap holds in fallback too), got {len(picked)}"
    assert cost == 0.0
    print("  ✓ ranking failure → deterministic fallback + a banner the caller must render")


def test_session_limit_falls_back_with_reset_hint():
    from newsdigest.classify_llm import SessionLimitError
    survivors = [mk(f"c{i}", f"T{i}", [f"Story {i}"]) for i in range(40)]
    orig = rank._rank_once
    rank._rank_once = lambda *a, **k: (_ for _ in ()).throw(SessionLimitError("resets at 3pm"))
    try:
        picked, _cost, note, ranked = rank.select_top(survivors, repo_root=".", limit=30, tier_map=TIERS)
    finally:
        rank._rank_once = orig
    assert "session limit" in note and "resets at 3pm" in note, note
    assert len(picked) == 30, "40 distinct tickers, so the cap does not bind here"
    print("  ✓ 429 session limit → fallback, reset hint surfaced in the banner")


def test_pooled_timeout_shards_instead_of_giving_up():
    """The 2026-08-19 postmarket regression: a pooled timeout dropped straight to deterministic
    order. A timeout means the prompt was too big for ONE call, not that ranking is impossible."""
    import subprocess
    survivors = [mk(f"c{i}", f"T{i}", [f"Story {i}"]) for i in range(250)]
    calls = {"n": 0}
    orig = rank._rank_once

    def flaky(pool, tier_map, limit, repo_root, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:                       # the pooled attempt times out
            raise subprocess.TimeoutExpired("claude", 900)
        return [rank.Selection(c.hash, "sharded") for c, _ in pool[:limit]], 0.05

    rank._rank_once = flaky
    try:
        picked, cost, note, ranked = rank.select_top(survivors, repo_root=".", limit=30, tier_map=TIERS)
    finally:
        rank._rank_once = orig
    assert calls["n"] > 1, "a pooled timeout must trigger the sharded retry, not give up"
    assert len(picked) == 30, f"sharded recovery must still fill the digest, got {len(picked)}"
    assert note and "timed out" in note, f"recovery must be reported, got {note!r}"
    assert "deterministic" not in note, "sharded recovery is NOT the deterministic fallback"
    assert ranked, "sharded recovery DID rank — it must not trip the fail-loud alert"
    assert cost > 0, "sharded calls cost money; cost must be reported"
    print(f"  ✓ pooled timeout → sharded retry ({calls['n']} calls), digest filled, recovery reported")


def test_rank_timeout_is_longer_than_classify():
    from newsdigest.classify_llm import CLAUDE_TIMEOUT_S
    assert rank.RANK_TIMEOUT_S > CLAUDE_TIMEOUT_S, (
        "the pooled rank call is one big call replacing 13-15 summarizer calls; it must not "
        "inherit a per-classify-batch timeout")
    print(f"  ✓ rank timeout {rank.RANK_TIMEOUT_S}s > classify {CLAUDE_TIMEOUT_S}s")


def test_prompt_carries_the_ranking_rules():
    survivors = [mk("c1", "NVDA", ["Nvidia raises guidance"])]
    p = rank.build_rank_prompt(survivors, TIERS, 30)
    for must in ("SELL-SIDE RANKS LAST", "NOVELTY", "T1-BCTK", "cluster_id: c1", "best 30"):
        assert must in p, f"prompt missing {must!r}"
    print("  ✓ prompt carries the ranking rules, tier labels and cluster ids")


if __name__ == "__main__":
    for fn in (test_cap_is_enforced, test_one_ticker_cannot_eat_the_digest,
               test_macro_and_theme_are_not_ticker_capped, test_sell_side_sorts_last,
               test_tier_then_confidence_ordering, test_no_llm_call_when_under_limit,
               test_ranking_failure_falls_back_and_reports,
               test_session_limit_falls_back_with_reset_hint,
               test_pooled_timeout_shards_instead_of_giving_up,
               test_rank_timeout_is_longer_than_classify,
               test_prompt_carries_the_ranking_rules):
        fn()
    print("\nALL PASS — selection is capped, per-ticker bounded, sell-side last, fail-visible.")
