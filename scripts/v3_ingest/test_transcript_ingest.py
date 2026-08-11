"""
Unit tests for transcript_ingest (spec §4.1).

Fixtures in fixtures/ are REAL FactSet_UnstructuredContent responses captured
2026-08-11 — one earnings call (financialQuarter present) and one conference
(financialQuarter absent). The conference fixture is the regression guard for the
KeyError trap the spec calls out.

No pytest in this env — run directly:
    python3 scripts/v3_ingest/test_transcript_ingest.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcript_ingest as ti  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    return json.loads((FIXTURES / name).read_text())["data"]


EARNINGS = _load("factset_transcripts_aaoi_2q26.json")
CONFERENCE = _load("factset_transcripts_lite_conference.json")


# ───────────────────────── query generation ─────────────────────────

def test_theme_to_query_is_a_natural_language_sentence():
    q = ti.theme_to_query("ai_infrastructure_capex")
    assert q.endswith("?")
    assert "_" not in q
    assert "ai infrastructure capex" in q


def test_theme_to_query_charset_is_tool_legal():
    # tool contract: letters, digits and  space , % & / - ?  only
    for theme in ["china_export_controls", "hbm_competitive_landscape", "400g_optics"]:
        assert ti.QUERY_CHARSET_RE.fullmatch(ti.theme_to_query(theme)), theme


def test_queries_for_entry_is_deterministic_and_capped():
    entry = ti.UniverseEntry("COHR", "COHR-US", ["a_one", "b_two", "c_three"], ["tier_1"])
    first = ti.queries_for(entry, max_queries=2)
    assert first == ti.queries_for(entry, max_queries=2)
    assert len(first) == 2
    assert "a one" in first[0]


def test_queries_for_entry_without_themes_yields_nothing():
    # a name with no assigned themes must not silently fall back to a hand-written
    # query — that is the §11.2 gold-test contamination the spec forbids
    entry = ti.UniverseEntry("XYZ", "XYZ-US", [], ["tier_4"])
    assert ti.queries_for(entry, max_queries=6) == []


# ───────────────────────── headline parsing ─────────────────────────

def test_parse_headline_earnings_call():
    p = ti.parse_headline(EARNINGS[0]["headline"])
    assert p["event_type"] == "earnings_call"
    assert p["event_date"] == "2026-08-06"          # NOT storyDateTime's 08-07
    assert p["corrected"] is True
    assert p["host_hint"] is None


def test_parse_headline_conference_gives_host_hint():
    p = ti.parse_headline(CONFERENCE[0]["headline"])
    assert p["event_type"] == "conference"
    assert p["event_date"] == "2026-06-09"
    assert p["host_hint"] == "Mizuho"               # §10 host-firm exclusion input


def test_host_hint_keeps_multiword_firms():
    p = ti.parse_headline(
        "CORRECTED TRANSCRIPT: Some Co, Inc.(XYZ-US), TD Cowen Aerospace & Defense "
        "Conference, 3-March-2026 9:00 AM ET")
    assert p["host_hint"] == "TD Cowen"


def test_host_hint_strips_trailing_sector_acronyms():
    # measured on the live AAOI run: "Raymond James TMT and Consumer Conference"
    # and "Raymond James & Associates Institutional Investors Conference" are the
    # same host and must not resolve to two different firms
    a = ti.parse_headline("CORRECTED TRANSCRIPT: Applied Optoelectronics, Inc.(AAOI-US), "
                          "Raymond James TMT and Consumer Conference, 9-December-2025 1:00 PM ET")
    b = ti.parse_headline("CORRECTED TRANSCRIPT: Applied Optoelectronics, Inc.(AAOI-US), "
                          "Raymond James & Associates Institutional Investors Conference, "
                          "3-March-2026 1:00 PM ET")
    assert a["host_hint"] == "Raymond James"
    assert b["host_hint"] == "Raymond James"


def test_empty_speaker_type_normalises_to_none():
    # measured: 16 of 200 live chunks carried speakerType ""
    chunk = dict(EARNINGS[0], speakerType="")
    assert ti.row_from_chunk(chunk, "AAOI", "q", "file")["speaker_type"] is None


def test_event_date_is_not_the_story_timestamp():
    # storyDateTime is the publication moment (08-07); the call was held 08-06
    row = ti.row_from_chunk(EARNINGS[0], "AAOI", "q", "file")
    assert row["event_date"] == "2026-08-06"
    assert EARNINGS[0]["storyDateTime"].startswith("2026-08-07")


def test_parse_headline_unrecognised_shape_is_flagged_not_guessed():
    p = ti.parse_headline("SOMETHING ENTIRELY DIFFERENT")
    assert p["event_type"] is None
    assert p["event_date"] is None


# ───────────────────────── period keys ─────────────────────────

def test_period_key_earnings_uses_fiscal_quarter():
    row = ti.row_from_chunk(EARNINGS[0], "AAOI", "q", "file")
    assert row["period_key"] == "2026Q2"
    assert row["period_basis"] == "fiscal"
    assert row["fiscal_quarter"] == "Q2"


def test_period_key_conference_falls_back_to_calendar_quarter():
    # the KeyError trap: these chunks have NO financialQuarter at all
    assert "financialQuarter" not in CONFERENCE[0]
    row = ti.row_from_chunk(CONFERENCE[0], "LITE", "q", "file")
    assert row["period_key"] == "2026Q2"            # 9-June-2026 -> calendar Q2
    assert row["period_basis"] == "calendar"
    assert row["fiscal_quarter"] is None


def test_calendar_quarter_boundaries():
    for date, expected in [("2026-01-05", "2026Q1"), ("2026-03-31", "2026Q1"),
                           ("2026-04-01", "2026Q2"), ("2026-08-06", "2026Q3"),
                           ("2025-12-31", "2025Q4")]:
        assert ti.calendar_quarter(date) == expected, date


# ───────────────────────── row shape ─────────────────────────

def test_row_carries_the_spec_fields_plus_headline():
    row = ti.row_from_chunk(EARNINGS[1], "AAOI", "some query", "file")
    for key in ["vector_id", "document_id", "ticker", "factset_id", "event_type",
                "event_date", "fiscal_year", "fiscal_quarter", "section",
                "speaker_type", "speaker_name", "speaker_firm", "text",
                "retrieved_by_query", "similarity", "headline", "payload_source"]:
        assert key in row, key
    assert row["section"] == "qna"
    assert row["speaker_type"] == "analyst"
    assert row["speaker_firm"] == "Wolfe Research LLC"
    assert row["text"] == EARNINGS[1]["content"]    # verbatim, never rewritten


def test_section_split_md_vs_qna():
    assert ti.row_from_chunk(EARNINGS[0], "AAOI", "q", "file")["section"] == "md"
    assert ti.row_from_chunk(EARNINGS[1], "AAOI", "q", "file")["section"] == "qna"


# ───────────────────────── fidelity check ─────────────────────────

def test_every_fixture_chunk_passes_the_textlength_check():
    for chunk in EARNINGS + CONFERENCE:
        assert ti.chunk_is_verbatim(chunk), chunk["vectorId"]


def test_truncated_text_fails_the_textlength_check():
    bad = dict(EARNINGS[0])
    bad["content"] = bad["content"][:50] + " ..."
    assert not ti.chunk_is_verbatim(bad)


def test_model_retyped_payload_with_a_bad_chunk_is_a_failure_not_a_silent_drop():
    bad = dict(EARNINGS[0], content="summarised away")
    kept, status = ti.accept_payload([bad], "model_text")
    assert kept == []
    assert status.startswith("failed")


def test_file_payload_mismatch_is_dropped_per_chunk_but_run_continues():
    bad = dict(EARNINGS[0], content="truncated")
    kept, status = ti.accept_payload([bad, EARNINGS[1]], "file")
    assert [c["vectorId"] for c in kept] == [EARNINGS[1]["vectorId"]]
    assert status == "ok"


def test_no_results_is_empty_not_failed():
    kept, status = ti.accept_payload([], "file")
    assert kept == [] and status == "empty"


# ───────────────────────── dedup ─────────────────────────

def test_dedup_on_vector_id():
    rows = [ti.row_from_chunk(c, "AAOI", "q1", "file") for c in EARNINGS]
    rows += [ti.row_from_chunk(EARNINGS[0], "AAOI", "q2", "file")]
    assert len(ti.dedupe_rows(rows)) == 3


def test_corrected_transcript_wins_over_original_for_the_same_exchange():
    orig = dict(EARNINGS[1],
                vectorId="3510329-t_3510329-t_qna_4_0",
                documentID="3510329-t",
                headline=EARNINGS[1]["headline"].replace("CORRECTED TRANSCRIPT: ",
                                                         "TRANSCRIPT: "))
    rows = [ti.row_from_chunk(orig, "AAOI", "q", "file"),
            ti.row_from_chunk(EARNINGS[1], "AAOI", "q", "file")]
    kept = ti.dedupe_rows(rows)
    assert len(kept) == 1
    assert kept[0]["document_id"] == "3510330-t"    # the corrected one


def test_dedup_keeps_distinct_exchanges():
    rows = [ti.row_from_chunk(c, "AAOI", "q", "file") for c in EARNINGS]
    assert len(ti.dedupe_rows(rows)) == 3


# ───────────────────────── universe ─────────────────────────

WATCHLIST = {
    "tier_1_bctk": [{"ticker": "COHR", "themes": ["optical_interconnect"]}],
    "tier_2_active_candidates": [{"ticker": "LITE", "themes": ["optical_interconnect"]}],
    "tier_3_watchlist": [{"ticker": "AAOI", "themes": ["datacenter_optics"]},
                         {"ticker": "AAON", "themes": ["thermal_management_cooling"]}],
    "ingest_comparables": [{"ticker": "FN", "informs": ["COHR", "LITE"]}],
    "tier_4_ecosystem": [{"id": "innolight.cn", "factset_id": "300308-CN",
                          "affects": ["COHR", "LITE"]}],
}
SC_EDGES = [
    {"source": "COHR", "target": "MRVL", "provenance": "manual"},
    {"source": "COHR", "target": "NOISE", "provenance": "factset"},      # ignored
    {"source": "LITE", "target": "openai.pvt", "provenance": "manual"},  # never enters
]
IDENTITY = {"COHR": {"factset_id": "COHR-US"}}


def test_universe_covers_t1_t2_adjacents_comparables_and_tier4():
    entries, _ = ti.resolve_universe(WATCHLIST, SC_EDGES, IDENTITY)
    got = {e.ticker for e in entries}
    assert {"COHR", "LITE", "MRVL", "FN", "innolight.cn"} <= got


def test_universe_excludes_factset_provenance_edges_and_pvt_ids():
    entries, _ = ti.resolve_universe(WATCHLIST, SC_EDGES, IDENTITY)
    got = {e.ticker for e in entries}
    assert "NOISE" not in got
    assert not any(t.endswith(".pvt") for t in got)


def test_universe_excludes_plain_tier_3():
    # AAON is T3 and nothing else — it must not be pulled in
    entries, _ = ti.resolve_universe(WATCHLIST, SC_EDGES, IDENTITY)
    assert "AAON" not in {e.ticker for e in entries}


def test_comparable_inherits_themes_from_the_names_it_informs():
    entries, _ = ti.resolve_universe(WATCHLIST, SC_EDGES, IDENTITY)
    fn = next(e for e in entries if e.ticker == "FN")
    assert fn.themes == ["optical_interconnect"]
    assert "ingest_comparable" in " ".join(fn.reasons)


def test_tier4_inherits_themes_from_affects_and_keeps_its_factset_id():
    entries, _ = ti.resolve_universe(WATCHLIST, SC_EDGES, IDENTITY)
    inno = next(e for e in entries if e.ticker == "innolight.cn")
    assert inno.factset_id == "300308-CN"
    assert inno.themes == ["optical_interconnect"]


def test_aaoi_enters_via_comparables_when_present():
    wl = dict(WATCHLIST, ingest_comparables=[{"ticker": "AAOI", "informs": ["COHR"]}])
    entries, _ = ti.resolve_universe(wl, SC_EDGES, IDENTITY)
    assert "AAOI" in {e.ticker for e in entries}    # §11.2 gold test needs AAOI


def test_factset_id_defaults_to_us_suffix_and_unmappable_names_are_recorded():
    wl = dict(WATCHLIST, tier_1_bctk=WATCHLIST["tier_1_bctk"] + [
        {"ticker": "005930.KS", "themes": ["x"]}])
    entries, unresolved = ti.resolve_universe(wl, SC_EDGES, IDENTITY)
    assert next(e for e in entries if e.ticker == "LITE").factset_id == "LITE-US"
    assert any(u["ticker"] == "005930.KS" for u in unresolved)
    assert "005930.KS" not in {e.ticker for e in entries}


def test_real_config_resolves_a_universe_with_aaoi_and_no_pvt():
    """Guards against config drift — runs against the actual repo config."""
    wl = ti.load_yaml(ti.WATCHLIST_YAML)
    sc = ti.load_yaml(ti.SUPPLY_CHAIN_MANUAL)
    identity = ti.load_yaml(ti.IDENTITY_YAML)
    entries, unresolved = ti.resolve_universe(wl, sc.get("edges") or [], identity)
    tickers = {e.ticker for e in entries}
    assert len(entries) > 40, len(entries)
    assert "AAOI" in tickers                         # §11.2
    assert not any(t.endswith(".pvt") for t in tickers)
    assert all(e.factset_id for e in entries)
    print(f"    (real config: {len(entries)} names, {len(unresolved)} unresolved)")


# ───────────────────────── ledger ─────────────────────────

def test_ledger_distinguishes_empty_from_failed():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "_progress.json"
        led = ti.Ledger(p)
        led.record("AAOI-US", "q", 0, "empty", 0)
        led.record("LITE-US", "q", 0, "failed: timeout", 0)
        led.save()

        reloaded = ti.Ledger(p)
        assert reloaded.status("AAOI-US", "q", 0) == "empty"
        assert reloaded.status("LITE-US", "q", 0).startswith("failed")
        assert reloaded.done("AAOI-US", "q", 0) is True     # empty = answered, skip
        assert reloaded.done("LITE-US", "q", 0) is False    # failed = retry


def test_ledger_never_treats_a_missing_key_as_done():
    with tempfile.TemporaryDirectory() as d:
        led = ti.Ledger(Path(d) / "_progress.json")
        assert led.done("NEW-US", "q", 0) is False


def test_ledger_survives_a_corrupt_file():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "_progress.json"
        p.write_text("{not json")
        led = ti.Ledger(p)
        assert led.done("X-US", "q", 0) is False


# ───────────────────────── paging / window ─────────────────────────

def test_short_page_terminates_paging():
    # meta.total is the returned count, not a corpus total (probed 2026-08-11),
    # so a page shorter than the limit is the only honest stop condition
    assert ti.should_stop_paging(n_returned=12, limit=50) is True
    assert ti.should_stop_paging(n_returned=50, limit=50) is False


def test_paging_stops_at_the_page_cap():
    assert ti.page_offsets(limit=50, max_pages=3) == [0, 50, 100]


def test_window_bounds_walks_back_whole_months():
    import datetime as dt
    assert ti.window_bounds(9, dt.date(2026, 8, 11)) == ("2025-11-11", "2026-08-11")
    assert ti.window_bounds(9, dt.date(2026, 3, 31)) == ("2025-06-28", "2026-03-31")
    assert ti.window_bounds(1, dt.date(2026, 1, 15)) == ("2025-12-15", "2026-01-15")


# ───────────────────────── runner ─────────────────────────

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
