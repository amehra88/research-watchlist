"""
Unit tests for scripts/portal/theme_ideas.py (RIS4 slice 2, Task 4, fix round 1).

Moved out of test_state_bundles.py when theme_ideas.py was split out of
state_bundles.py (controller-authorized, review 768e415d..4f613b35) --
themes_bundle()/ideas_bundle() and their fixtures under fixtures/state/ are
unchanged by the split; only the module under test changed.

Fixtures live under fixtures/state/ (topics/, notes/, docs/, state_portal/,
watchlist.yaml) -- see test_state_bundles.py's own docstring for the full
fixture-tree description (both test files share the same fixtures/state/
directory). Every test pins `today` implicitly via the fixture data itself
(diffusion.json's as_of, stages.json's as_of) rather than a `today` parameter
-- themes_bundle()/ideas_bundle() don't take one.

No pytest in this env -- run directly:
    python3 scripts/portal/test_theme_ideas.py
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme_ideas as ti  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "state"

BASE_PATHS = ti.Paths(
    notes=FIXTURES / "notes",
    watchlist=FIXTURES / "watchlist.yaml",
    topics_state=FIXTURES / "topics",
    thesis_state=FIXTURES / "thesis",
    portal_state=FIXTURES / "state_portal",
    docs=FIXTURES / "docs",
    cron_log=FIXTURES / "cron_runs_fixture.txt",
    etf_lookthrough=FIXTURES / "does_not_exist_lookthrough.json",
    etf_flows=FIXTURES / "does_not_exist_flows.jsonl",
)

NO_PORTAL_STATE = ti.Paths(
    notes=FIXTURES / "notes", watchlist=FIXTURES / "watchlist.yaml", topics_state=FIXTURES / "topics",
    thesis_state=FIXTURES / "thesis", portal_state=FIXTURES / "does_not_exist_portal",
    docs=FIXTURES / "docs", cron_log=FIXTURES / "cron_runs_fixture.txt",
    etf_lookthrough=FIXTURES / "does_not_exist_lookthrough.json",
    etf_flows=FIXTURES / "does_not_exist_flows.jsonl",
)


# ───────────────────────── themes_bundle ─────────────────────────

def test_themes_bundle_written_note_is_in_vocab():
    tb = ti.themes_bundle(BASE_PATHS)
    by_slug = {t["slug"]: t for t in tb["themes"]}
    assert set(by_slug) == {"fixture_theme_a", "fixture_theme_b", "fixture_theme_gate_only"}
    a = by_slug["fixture_theme_a"]
    assert a["in_vocab"] is True
    assert a["fm"]["theme"] == "fixture_theme_a" and a["fm"]["status"] == "approved"
    assert set(a["fm"]) == set(ti._THEME_FM_KEYS)
    assert "[[FIX/_thesis" not in a["body"] or "#/ticker/FIX" in a["body"], a["body"]


def test_themes_bundle_gate_only_theme_is_not_in_vocab():
    tb = ti.themes_bundle(BASE_PATHS)
    by_slug = {t["slug"]: t for t in tb["themes"]}
    g = by_slug["fixture_theme_gate_only"]
    assert g["in_vocab"] is False
    assert g["body"] == ""
    assert g["fm"]["stage"] == 1
    assert g["fm"]["tickers"] == ["FIX"]
    assert g["fm"]["updated"] == "2026-09-15"           # diffusion.as_of, no real note
    assert g["stages_by_ticker"] == {"FIX": 1}


def test_themes_bundle_diffusion_is_trimmed():
    tb = ti.themes_bundle(BASE_PATHS)
    d = tb["diffusion"]
    assert set(d) == {"as_of", "current_quarter", "metrics", "movers", "stage_counts", "lag_summary"}
    assert d["current_quarter"] == "CY2026-Q2"
    assert len(d["metrics"]) == 4        # both fixture quarters kept (Q1 + Q2)


def test_themes_bundle_candidates_pending_and_decided():
    tb = ti.themes_bundle(BASE_PATHS)
    pending_ids = {c["id"] for c in tb["candidates"]}
    assert pending_ids == {"cand:pend1", "cand:pend2"}
    p1 = next(c for c in tb["candidates"] if c["id"] == "cand:pend1")
    assert len(p1["ngrams"]) == 8         # capped, fixture has 9
    assert {c["id"] for c in tb["decided"]} == {"cand:dec1", "cand:dec2", "cand:dec3"}
    dec1 = next(c for c in tb["decided"] if c["id"] == "cand:dec1")
    assert dec1["name"] == "decided_theme_name"   # backfilled from decisions.jsonl


def test_themes_bundle_decided_is_sorted_most_recent_first_not_file_order():
    # Fixture file order in candidates.json is [..., dec1, dec3, dec2] -- ts
    # 09-10, 09-14, 08-01(fallback first_seen, no decisions.jsonl row) -- so a
    # naive "keep file order" or "reverse file order" slice would both get this
    # wrong. Correct is ts/first_seen descending: dec3 (09-14) > dec1 (09-10) >
    # dec2 (08-01 fallback, decided via an inline status with no decisions.jsonl
    # row at all).
    tb = ti.themes_bundle(BASE_PATHS)
    ids_in_order = [c["id"] for c in tb["decided"]]
    assert ids_in_order == ["cand:dec3", "cand:dec1", "cand:dec2"], ids_in_order
    dec2 = next(c for c in tb["decided"] if c["id"] == "cand:dec2")
    assert dec2["name"] == "decided_two_inline_name"   # inline status/name, no decisions.jsonl row


def test_themes_bundle_decided_caps_at_50_keeping_the_most_recent():
    """Cap is exercised against a synthetic 55-decided-candidate fixture built
    in a tmp dir (not the shared BASE_PATHS tree, to avoid bloating it) -- all
    decided via inline status with distinct, deterministically ordered
    first_seen dates so "most recent 50" has one unambiguous answer.
    """
    tmp = Path(tempfile.mkdtemp(prefix="ris4_theme_ideas_cap_test_"))
    try:
        topics = tmp / "topics"
        topics.mkdir(parents=True)
        cands = []
        for i in range(55):
            cands.append({
                "id": f"cand:cap{i:02d}", "label": f"cap {i}", "ngrams": ["x"],
                "n_exchanges": 1, "n_companies": 1, "n_banks": 1, "tickers": [],
                "first_seen": f"2026-01-{i + 1:02d}" if i < 31 else f"2026-02-{i - 30:02d}",
                "members": [], "status": "accepted", "name": f"cap_theme_{i}",
            })
        import json
        (topics / "candidates.json").write_text(json.dumps(cands), encoding="utf-8")
        (topics / "decisions.jsonl").write_text("", encoding="utf-8")
        paths = ti.Paths(
            notes=FIXTURES / "notes", watchlist=FIXTURES / "watchlist.yaml", topics_state=topics,
            thesis_state=FIXTURES / "thesis", portal_state=FIXTURES / "state_portal",
            docs=FIXTURES / "docs", cron_log=FIXTURES / "cron_runs_fixture.txt",
            etf_lookthrough=FIXTURES / "does_not_exist_lookthrough.json",
            etf_flows=FIXTURES / "does_not_exist_flows.jsonl",
        )
        tb = ti.themes_bundle(paths)
        assert len(tb["decided"]) == 50
        # the 5 OLDEST (cap00..cap04, first_seen 2026-01-01..05) must be dropped;
        # the most recent (cap54, first_seen 2026-02-24) must be first.
        ids = {c["id"] for c in tb["decided"]}
        assert "cand:cap00" not in ids and "cand:cap04" not in ids
        assert tb["decided"][0]["id"] == "cand:cap54"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_themes_bundle_degrades_when_diffusion_and_stages_are_missing():
    missing_state = ti.Paths(
        notes=FIXTURES / "notes", watchlist=FIXTURES / "watchlist.yaml",
        topics_state=FIXTURES / "does_not_exist_topics", thesis_state=FIXTURES / "thesis",
        portal_state=FIXTURES / "state_portal", docs=FIXTURES / "docs", cron_log=FIXTURES / "cron_runs_fixture.txt",
        etf_lookthrough=FIXTURES / "does_not_exist_lookthrough.json",
        etf_flows=FIXTURES / "does_not_exist_flows.jsonl",
    )
    tb = ti.themes_bundle(missing_state)
    # written notes still surface (they're on disk regardless of diffusion.json);
    # stages_by_ticker degrades to {} rather than raising.
    assert {t["slug"] for t in tb["themes"]} == {"fixture_theme_a", "fixture_theme_b"}
    assert all(t["stages_by_ticker"] == {} for t in tb["themes"])
    assert tb["candidates"] == [] and tb["decided"] == [] and tb["stage_events"] == []
    ib = ti.ideas_bundle(missing_state)
    # candidate/newly_said/gap/stage all source off diffusion.json/candidates.json
    # (all missing here) -- only screen: (docs/ai-screen-report-*.md, untouched by
    # this override) still produces ideas.
    assert {i["stream"] for i in ib["ideas"]} == {"screen"}


def test_themes_bundle_stage_events_is_a_tail():
    tb = ti.themes_bundle(BASE_PATHS)
    assert len(tb["stage_events"]) == 2
    assert tb["stage_events"][0]["theme"] == "fixture_theme_gate_only"


# ───────────────────────── ideas_bundle ─────────────────────────

def test_ideas_bundle_candidate_stream_honors_dismissal():
    ib = ti.ideas_bundle(BASE_PATHS)
    ids = [i["id"] for i in ib["ideas"] if i["stream"] == "candidate"]
    assert ids == ["candidate:cand:pend2"]     # pend1 dismissed via state_portal/ideas_decisions.jsonl


def test_ideas_bundle_candidate_stream_without_dismissal_file():
    ib = ti.ideas_bundle(NO_PORTAL_STATE)
    ids = {i["id"] for i in ib["ideas"] if i["stream"] == "candidate"}
    assert ids == {"candidate:cand:pend1", "candidate:cand:pend2"}


def test_ideas_bundle_newly_said_is_current_quarter_only():
    ib = ti.ideas_bundle(BASE_PATHS)
    newly = [i for i in ib["ideas"] if i["stream"] == "newly_said"]
    assert len(newly) == 1
    assert newly[0]["id"] == "newly_said:fixture_theme_a|FIX|CY2026-Q2"
    assert newly[0]["score"] == 3              # n_banks off the (theme, cq) metrics cell


def test_ideas_bundle_gap_stream_uses_disclosing_vs_asked():
    ib = ti.ideas_bundle(BASE_PATHS)
    gaps = {i["id"]: i for i in ib["ideas"] if i["stream"] == "gap"}
    assert set(gaps) == {"gap:fixture_theme_b|CY2026-Q2", "gap:fixture_theme_gate_only|CY2026-Q2"}
    assert gaps["gap:fixture_theme_b|CY2026-Q2"]["score"] == 4       # 4 disclosing / 0 asked
    assert gaps["gap:fixture_theme_gate_only|CY2026-Q2"]["score"] == 1
    # fixture_theme_a never qualifies (1 disclosing <= n_companies in both quarters)
    assert not any(i["theme"] == "fixture_theme_a" for i in gaps.values())


def test_ideas_bundle_stage_stream_ids_are_stable_and_not_recomputed():
    ib1 = ti.ideas_bundle(BASE_PATHS)
    ib2 = ti.ideas_bundle(BASE_PATHS)
    ids1 = sorted(i["id"] for i in ib1["ideas"] if i["stream"] == "stage")
    ids2 = sorted(i["id"] for i in ib2["ideas"] if i["stream"] == "stage")
    assert ids1 == ids2 == [
        "stage:fixture_theme_a|ORPHAN|2026-09-05",
        "stage:fixture_theme_gate_only|FIX|2026-09-01",
    ]


def test_ideas_bundle_screen_stream_skips_tracked_rows():
    ib = ti.ideas_bundle(BASE_PATHS)
    screens = {i["id"]: i for i in ib["ideas"] if i["stream"] == "screen"}
    assert set(screens) == {"screen:NOTR", "screen:ANO"}   # FIX is *tracked*, excluded
    assert screens["screen:NOTR"]["score"] == 3


def test_ideas_bundle_novel_stream_degrades_to_empty_when_absent():
    ib = ti.ideas_bundle(BASE_PATHS)
    assert [i for i in ib["ideas"] if i["stream"] == "novel"] == []


def test_ideas_bundle_all_ids_unique():
    ib = ti.ideas_bundle(BASE_PATHS)
    ids = [i["id"] for i in ib["ideas"]]
    assert len(ids) == len(set(ids)), ids


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
