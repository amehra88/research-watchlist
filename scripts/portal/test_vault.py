"""
Unit tests for scripts/portal/vault.py (RIS4 slice 2, Task 1).

Fixtures in fixtures/vault/ are a tiny fake notes/ tree, trimmed from real vault
frontmatter shapes (see task-1-report.md for provenance). Tests run ONLY against
these fixtures, never the live vault at /root/research-watchlist/notes — except
for one explicitly-flagged live-data-coupled assertion in
test_ticker_bundle_nvda_smoke (tier_of() reads the live watchlist by design).

No pytest in this env — run directly:
    python3 scripts/portal/test_vault.py
"""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault as v  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "vault"


# ───────────────────────── classify() ─────────────────────────

def test_classify_earnings_ticker():
    kind, ticker, d, period = v.classify("NVDA/20260512-4Q26.md")
    assert kind == "earnings" and ticker == "NVDA" and d == "2026-05-12" and period == "4Q26"


def test_classify_earnings_pvt_id():
    kind, ticker, d, period = v.classify("simaai.pvt/20260601-1Q27.md")
    assert kind == "earnings" and ticker == "simaai.pvt" and d == "2026-06-01" and period == "1Q27"


def test_classify_earnings_foreign_ticker():
    kind, ticker, d, period = v.classify("000660.KS/20260101-1Q26.md")
    assert kind == "earnings" and ticker == "000660.KS" and period == "1Q26"


def test_classify_conference():
    kind, ticker, d, period = v.classify("GOOGL/20260303-conf-morgan-stanley-tmt.md")
    assert (kind, ticker, d, period) == ("conference", "GOOGL", "2026-03-03", None)


def test_classify_synthesis():
    kind, ticker, d, period = v.classify("NVDA/synthesis-20260602-run8.md")
    assert (kind, ticker, d, period) == ("synthesis", "NVDA", "2026-06-02", None)


def test_classify_news_note():
    kind, ticker, d, period = v.classify("COHR/20260602-news-optical-halo-record-high.md")
    assert (kind, ticker, d, period) == ("news_note", "COHR", "2026-06-02", None)


def test_classify_thesis():
    assert v.classify("NVDA/_thesis.md") == ("thesis", "NVDA", None, None)


def test_classify_theme_index():
    assert v.classify("NVDA/_themes.md") == ("theme_index", "NVDA", None, None)


def test_classify_profile_non_pvt():
    assert v.classify("SPCX/_profile.md") == ("profile", "SPCX", None, None)


def test_classify_pvt_profile():
    assert v.classify("openai.pvt/_profile.md") == ("pvt_profile", "openai.pvt", None, None)


def test_classify_theme():
    assert v.classify("themes/ai_inference_margin_compression.md") == ("theme", None, None, None)


def test_classify_report():
    assert v.classify("reports/thesis-delta-20260914.md") == ("report", None, None, None)


def test_classify_substack():
    assert v.classify("substacks/2026-06-24-x.md") == ("substack", None, None, None)


def test_classify_podcast():
    assert v.classify("podcasts/2026-06-08-hObRMv6q.md") == ("podcast", None, None, None)


def test_classify_flow():
    assert v.classify("flows/20260915-flows.md") == ("flow", None, None, None)


def test_classify_foreign():
    assert v.classify("foreign/2023-08-24-eoptolink-cn-2023.md") == ("foreign", None, None, None)


def test_classify_sector():
    assert v.classify("sector/20260512-ai-inference-accelerators-smoke.md") == ("sector", None, None, None)


def test_classify_other_salvages_ticker():
    assert v.classify("NVDA/random-notes.md") == ("other", "NVDA", None, None)


def test_classify_other_no_ticker():
    assert v.classify("m2a-earnings-reviewer-gap-analysis.md") == ("other", None, None, None)


# ───────────────────────── discover() ─────────────────────────

def test_discover_excludes_inbox_and_returns_11_refs():
    refs = v.discover(FIXTURES)
    assert len(refs) == 11
    assert not any(r.rel.startswith("inbox/") for r in refs)
    kinds = {r.kind for r in refs}
    assert kinds == {"earnings", "thesis", "theme_index", "conference", "synthesis",
                     "theme", "report", "substack", "podcast", "flow", "pvt_profile"}


def test_discover_on_empty_dir_is_empty():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        assert v.discover(Path(d)) == []


# ───────────────────────── load_note() frontmatter synthesis ─────────────────────────

def test_load_note_synthesizes_fm_for_frontmatterless_earnings_note():
    refs = v.discover(FIXTURES)
    ref = next(r for r in refs if r.rel == "NVDA/20260512-4Q26.md")
    note = v.load_note(ref)
    assert note["fm"] == {"ticker": "NVDA", "date": "2026-05-12", "period": "4Q26"}
    assert note["title"].startswith("NVDA —")
    assert note["provenance"] == "machine"


def test_load_note_keeps_real_frontmatter_when_present():
    refs = v.discover(FIXTURES)
    ref = next(r for r in refs if r.rel == "NVDA/_thesis.md")
    note = v.load_note(ref)
    assert note["fm"]["doc_type"] == "thesis"
    assert note["fm"]["ticker"] == "NVDA"
    assert note["provenance"] == "machine"    # reviewed_by_operator: false


# ───────────────────────── sections / signal_reads ─────────────────────────

def test_sections_splits_the_10_step_skeleton():
    refs = v.discover(FIXTURES)
    ref = next(r for r in refs if r.rel == "NVDA/20260512-4Q26.md")
    note = v.load_note(ref)
    heads = [s["h"] for s in note["sections"]]
    assert heads == [f"{i}. " + t for i, t in enumerate([
        "Headline read", "Actuals vs. consensus", "Forward guidance",
        "Thesis read by theme", "AI positioning signal", "Competitive advantage signal",
        "Potential investor interest signal", "Management Q&A flags",
        "Vocabulary candidates", "Sourcing"], start=1)]
    # embedded '---' inside the body (between §1 and §2) must not be mistaken for
    # frontmatter and must not disturb section splitting
    assert note["fm"] == {"ticker": "NVDA", "date": "2026-05-12", "period": "4Q26"}


def test_signal_reads_picks_5_6_7_with_600_char_cap():
    refs = v.discover(FIXTURES)
    ref = next(r for r in refs if r.rel == "NVDA/20260512-4Q26.md")
    note = v.load_note(ref)
    sig = v.signal_reads(note)
    assert sig is not None
    sec5 = next(s for s in note["sections"] if s["h"].startswith("5."))
    full = sec5["text"].strip()
    assert len(full) > 600                       # fixture paragraph is deliberately long
    assert sig["ai_positioning"] == full[:600]
    assert len(sig["ai_positioning"]) == 600
    assert sig["competitive_advantage"] and sig["competitive_advantage"].startswith("- **Innovation rate**")
    assert sig["investor_interest"] and "Hold at 4" in sig["investor_interest"]


def test_signal_reads_none_when_no_5_6_7_sections():
    note = {"kind": "conference", "sections": [{"h": "1. Headline read", "text": "x"}]}
    assert v.signal_reads(note) is None


def test_signal_reads_none_for_non_earnings_conference_kind():
    note = {"kind": "theme", "sections": [{"h": "5. AI positioning signal", "text": "x"}]}
    assert v.signal_reads(note) is None


# ───────────────────────── resolve_wikilinks() ─────────────────────────

KNOWN_T = {"NVDA"}
KNOWN_TH = {"silicon_architecture_competition"}


def test_wikilink_bare_ticker():
    assert v.resolve_wikilinks("[[NVDA]]", KNOWN_T, KNOWN_TH) == "[NVDA](#/ticker/NVDA)"


def test_wikilink_thesis_aliased():
    got = v.resolve_wikilinks("[[NVDA/_thesis|NVDA]]", KNOWN_T, KNOWN_TH)
    assert got == "[NVDA](#/ticker/NVDA/thesis)"


def test_wikilink_thesis_unaliased_labels_last_segment():
    got = v.resolve_wikilinks("[[NVDA/_thesis]]", KNOWN_T, KNOWN_TH)
    assert got == "[_thesis](#/ticker/NVDA/thesis)"


def test_wikilink_theme_aliased():
    got = v.resolve_wikilinks(
        "[[themes/silicon_architecture_competition|silicon_architecture_competition]]",
        KNOWN_T, KNOWN_TH)
    assert got == "[silicon_architecture_competition](#/theme/silicon_architecture_competition)"


def test_wikilink_unknown_target_degrades_to_plain_text():
    assert v.resolve_wikilinks("[[ZZZZ]]", KNOWN_T, KNOWN_TH) == "ZZZZ"


def test_wikilink_unknown_theme_degrades_to_plain_text():
    got = v.resolve_wikilinks("[[themes/nonexistent_theme|nonexistent_theme]]", KNOWN_T, KNOWN_TH)
    assert got == "nonexistent_theme"


# ───────────────────────── provenance ─────────────────────────

def test_provenance_operator_reviewed_via_flag():
    assert v._provenance({"reviewed_by_operator": True}) == "operator_reviewed"


def test_provenance_operator_reviewed_via_status_source():
    assert v._provenance({"status_source": "operator"}) == "operator_reviewed"


def test_provenance_headline_only():
    assert v._provenance({"summarized": False}) == "headline_only"


def test_provenance_default_machine():
    assert v._provenance({}) == "machine"
    assert v._provenance({"reviewed_by_operator": False, "summarized": True}) == "machine"


# ───────────────────────── ingest_bundles() ─────────────────────────

def test_ingest_bundles_substack_window_filter():
    refs = v.discover(FIXTURES)
    within = v.ingest_bundles(refs, days=30, today=date(2026, 6, 30))    # 6 days later
    assert len(within["substacks"]["items"]) == 1
    outside = v.ingest_bundles(refs, days=30, today=date(2026, 9, 1))    # 69 days later
    assert len(outside["substacks"]["items"]) == 0


def test_ingest_bundles_flows_window_is_14_days_not_the_default():
    refs = v.discover(FIXTURES)
    within = v.ingest_bundles(refs, days=30, today=date(2026, 9, 20))    # 5 days later
    assert len(within["flows"]["items"]) == 1
    outside = v.ingest_bundles(refs, days=30, today=date(2026, 10, 15))  # 30 days later
    assert len(outside["flows"]["items"]) == 0


def test_ingest_bundles_pvt_bucket_is_unwindowed():
    refs = v.discover(FIXTURES)
    for today in (date(2026, 6, 30), date(2026, 12, 31)):
        out = v.ingest_bundles(refs, days=30, today=today)
        assert len(out["pvt"]["items"]) == 1
        item = out["pvt"]["items"][0]
        assert item["date"] is None
        assert item["tickers"] == ["openai.pvt"]
        assert item["title"].startswith("OpenAI")


def test_ingest_bundles_podcast_item_shape_and_wikilinks_resolved():
    refs = v.discover(FIXTURES)
    out = v.ingest_bundles(refs, days=3650, today=date(2026, 6, 8))
    items = out["podcasts"]["items"]
    assert len(items) == 1
    item = items[0]
    assert item["tickers"] == ["GOOGL"]
    assert "themes" in item and "model_commoditization" in item["themes"]
    assert item["source"] == "All-In"
    assert item["date"] == "2026-06-08"


def test_ingest_bundles_default_today_does_not_error():
    # exercises the today=None -> date.today() default path
    refs = v.discover(FIXTURES)
    out = v.ingest_bundles(refs)
    assert set(out.keys()) == {"substacks", "podcasts", "foreign", "flows", "sector", "pvt"}


# ───────────────────────── ticker_bundle() ─────────────────────────

def test_ticker_bundle_nvda_smoke():
    refs = v.discover(FIXTURES)
    b = v.ticker_bundle("NVDA", refs, {"NVDA": "NVIDIA"}, {"NVDA"},
                        {"ai_inference_margin_compression"})
    assert b["ticker"] == "NVDA" and b["name"] == "NVIDIA"
    # live-data-coupled: tier_of() reads the real watchlist.yaml, not the fixture tree
    assert b["tier"] in ("tier_1_bctk", "none")
    assert b["thesis"]["body"].strip() != ""
    assert b["thesis"]["fm_without_body"]["doc_type"] == "thesis"
    assert "ai_inference_margin_compression" in b["theme_index_body"]
    # thesis, theme_index AND profile are excluded from notes (profile: none exists
    # for NVDA in the fixtures anyway, but the exclusion list itself is asserted below
    # via the openai.pvt case)
    assert [n["id"] for n in b["notes"]] == [
        "NVDA/synthesis-20260602-run8.md",     # 2026-06-02, sorts first (date desc)
        "NVDA/20260512-4Q26.md",               # 2026-05-12
    ]
    assert b["profile"] is None


def test_ticker_bundle_unknown_ticker_falls_back_to_tier_none():
    refs = v.discover(FIXTURES)
    b = v.ticker_bundle("ZZZZ", refs, {}, {"NVDA"}, set())
    assert b["tier"] == "none"
    assert b["notes"] == []
    assert b["thesis"] == {"fm_without_body": {}, "body": ""}
    assert b["theme_index_body"] == ""
    assert b["profile"] is None


def test_ticker_bundle_pvt_profile_excluded_from_notes():
    refs = v.discover(FIXTURES)
    b = v.ticker_bundle("openai.pvt", refs, {}, {"openai.pvt", "NVDA"}, set())
    assert b["tier"] == "none"
    assert b["profile"] is not None
    assert b["profile"]["title"].startswith("OpenAI")
    # thesis, theme_index AND profile are excluded from notes (coordinator ruling)
    assert b["notes"] == []


if __name__ == "__main__":
    fns = [v_ for k, v_ in sorted(globals().items())
           if k.startswith("test_") and callable(v_)]
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
