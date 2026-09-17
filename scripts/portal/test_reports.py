"""
Unit tests for scripts/portal/reports.py (RIS4 slice 2, Task 3).

Fixtures in fixtures/reports/ are hand-built day sets for every stream (is,
podcasts, logs/etfflows(+table), logs/news_digest_*, and the "ETF UPDATE"
digest section text, which now points at fixtures/etf_trades/ws/ -- reports.py
only treats that file as opaque digest text, it doesn't parse it; the parser
itself and its own fixtures moved to etf_trades.py / test_etf_trades.py in fix
round 1), plus thesis_state/topics_ok/topics_degrade/transcripts_ok for the two
alert ledgers. Tests run ONLY against these fixtures via explicit `paths: Paths`
overrides — reports.py's own zero-arg REPO-backed defaults are never exercised
here, EXCEPT the one documented case (thesis_alerts' join to
thesis_report.alert_events(), which has no override hook — see reports.py's
module docstring for why that is still fixture-safe).

No pytest in this env — run directly:
    python3 scripts/portal/test_reports.py
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reports as rp  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "reports"
ETF_FIXTURES = Path(__file__).parent / "fixtures" / "etf_trades"
# Same fixture watchlist STAGE_PATHS uses (see its own comment below). Defined
# here, ahead of BASE_PATHS/DEGRADE_PATHS, so every Paths override in this
# file passes an explicit `watchlist=` -- Paths.__post_init__ defaults an
# unset one to the LIVE `config/watchlist.yaml`, and no test here should be
# able to reach that.
STAGE_FIXTURES = Path(__file__).parent / "fixtures" / "stage"
FIXTURE_WATCHLIST = STAGE_FIXTURES / "watchlist.yaml"

BASE_PATHS = rp.Paths(
    is_reports=FIXTURES / "is",
    podcasts_reports=FIXTURES / "podcasts",
    logs=FIXTURES / "logs",
    notes=FIXTURES / "notes",
    watchlist=FIXTURE_WATCHLIST,
    thesis_state=FIXTURES / "thesis_state",
    topics_state=FIXTURES / "topics_ok",
    transcripts_state=FIXTURES / "transcripts_ok",
    evidence_state=FIXTURES / "does_not_exist",
    streams=[
        ("ETF UPDATE", str((ETF_FIXTURES / "ws" / "report_{date}.txt"))),
        ("ETF FLOWS & CROWDING", str((FIXTURES / "logs" / "report_etfflows_{date}.txt"))),
        ("INSIDER ACTIVITY", str((FIXTURES / "is" / "report_{date}.txt"))),
        ("PODCAST DIGEST", str((FIXTURES / "podcasts" / "report_{date}.txt"))),
        ("ETF FLOW DETAIL", str((FIXTURES / "logs" / "report_etfflows_table_{date}.txt"))),
    ],
)

DEGRADE_PATHS = rp.Paths(
    is_reports=FIXTURES / "is",
    podcasts_reports=FIXTURES / "podcasts", logs=FIXTURES / "logs",
    notes=FIXTURES / "notes",
    watchlist=FIXTURE_WATCHLIST,
    thesis_state=FIXTURES / "thesis_state",
    topics_state=FIXTURES / "topics_degrade",
    transcripts_state=FIXTURES / "does_not_exist",
    evidence_state=FIXTURES / "does_not_exist",
    streams=BASE_PATHS.streams,
)

DAY1, DAY2 = "2026-01-05", "2026-01-06"


# ───────────────────────── news_digest_files ─────────────────────────

def test_news_digest_dedupe_keeps_the_largest():
    files = rp.news_digest_files(DAY1, BASE_PATHS)
    assert files["premarket"].name == "news_digest_premarket_20260105_064500.txt", files
    assert files["premarket"].stat().st_size > 500, files["premarket"].stat().st_size


def test_news_digest_ignores_brief_mode_files():
    files = rp.news_digest_files(DAY1, BASE_PATHS)
    assert all("brief" not in p.name for p in files.values())


def test_news_digest_single_file_per_mode_on_day2():
    files = rp.news_digest_files(DAY2, BASE_PATHS)
    assert set(files) == {"premarket", "postmarket"}


# ───────────────────────── digest sections / IS stub ─────────────────────────

def test_digest_drops_is_stub_under_300_bytes():
    cards = rp.day_cards(DAY2, BASE_PATHS)
    digest = next(c for c in cards if c["kind"] == "digest")
    titles = [s["title"] for s in digest["sections"]]
    assert "INSIDER ACTIVITY" not in titles, titles


def test_digest_keeps_is_section_when_over_300_bytes():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    digest = next(c for c in cards if c["kind"] == "digest")
    titles = [s["title"] for s in digest["sections"]]
    assert "INSIDER ACTIVITY" in titles, titles


def test_digest_tolerates_a_missing_stream():
    # day2 fixtures have no podcasts/report_2026-01-06.txt -- a real, documented gap.
    cards = rp.day_cards(DAY2, BASE_PATHS)
    digest = next(c for c in cards if c["kind"] == "digest")
    titles = [s["title"] for s in digest["sections"]]
    assert "PODCAST DIGEST" not in titles, titles
    assert "ETF UPDATE" in titles, titles


def test_digest_text_banners_each_section_title():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    digest = next(c for c in cards if c["kind"] == "digest")
    assert "INSIDER ACTIVITY\n" in digest["text"], digest["text"][:200]


# ───────────────────────── gap logging: exactly one line per omission ─────────────────────────

def test_digest_logs_one_line_for_a_missing_stream():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rp.day_cards(DAY2, BASE_PATHS)
    lines = [ln for ln in buf.getvalue().splitlines() if "PODCAST DIGEST" in ln]
    assert lines == [f"[reports] reports: {DAY2} digest/PODCAST DIGEST missing"], buf.getvalue()


def test_digest_logs_one_line_for_the_is_stub_drop():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rp.day_cards(DAY2, BASE_PATHS)
    lines = [ln for ln in buf.getvalue().splitlines() if "INSIDER ACTIVITY" in ln]
    assert lines == [f"[reports] reports: {DAY2} digest/INSIDER ACTIVITY stub dropped (157 B)"], buf.getvalue()


def test_digest_logs_one_line_for_an_empty_stream():
    # fixtures/reports/logs/report_etfflows_2026-01-08.txt is a real 0-byte file;
    # every other stream for that day is also absent, so this isolates the "empty"
    # branch (distinct from "missing" and from the IS-stub "dropped" branch).
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rp.day_cards("2026-01-08", BASE_PATHS)
    lines = [ln for ln in buf.getvalue().splitlines() if "ETF FLOWS & CROWDING" in ln]
    assert lines == ["[reports] reports: 2026-01-08 digest/ETF FLOWS & CROWDING empty"], buf.getvalue()


def test_premarket_and_postmarket_each_log_one_absent_line():
    # 2026-01-07 has no logs/news_digest_* fixtures at all -> both modes absent.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rp.day_cards("2026-01-07", BASE_PATHS)
    out = buf.getvalue().splitlines()
    assert out.count("[reports] reports: 2026-01-07 premarket absent") == 1, out
    assert out.count("[reports] reports: 2026-01-07 postmarket absent") == 1, out


# ───────────────────────── day with no sources ─────────────────────────

def test_no_sources_day_yields_no_cards():
    assert rp.day_cards("2026-01-09", BASE_PATHS) == []


def test_build_reports_skips_the_no_source_day():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        summaries = rp.build_reports(out, 1, BASE_PATHS, today=__import__("datetime").date(2026, 1, 9))
        assert summaries == []
        assert not (out / "data" / "reports" / "2026-01-09.json").exists()
        # mkdir is lazy: a caller can tell "no reports in range" (no dir at all)
        # apart from "ran but everything landed under it".
        assert not (out / "data").exists()


# ───────────────────────── build_reports writes + summarizes ─────────────────────────

def test_build_reports_writes_a_file_and_returns_summaries():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        today = __import__("datetime").date(2026, 1, 5)
        summaries = rp.build_reports(out, 1, BASE_PATHS, today=today)
        out_path = out / "data" / "reports" / "2026-01-05.json"
        assert out_path.exists()
        import json
        data = json.loads(out_path.read_text())
        assert data["date"] == "2026-01-05"
        assert len(data["cards"]) == len(summaries)
        for s in summaries:
            assert set(s) == {"id", "kind", "date", "title", "bytes", "file"}
            assert s["file"] == "data/reports/2026-01-05.json"


# ───────────────────────── thesis_alerts: fallback join ─────────────────────────

def test_thesis_alerts_falls_back_to_assumption_id_when_not_in_live_alert_events():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next((c for c in cards if c["kind"] == "thesis_alerts"), None)
    assert ta is not None, cards
    assert "FIXTURE_TICKER" in ta["text"]
    item = next(i for i in ta["items"] if i["ticker"] == "FIXTURE_TICKER")
    # This fixture id/ticker/assumption is invented and can never appear in the
    # live repo's real alert_events() output or its notes/ tree, so both the
    # `from` join and the statement lookup must fall back cleanly: `statement`
    # falls back to the assumption id itself (no notes/FIXTURE_TICKER/_thesis.md
    # exists), and `from` stays None (no matching changes.jsonl row).
    assert item["assumption_id"] == "fake_assumption", item
    assert item["statement"] == "fake_assumption", item
    assert item["to"] == "confirmed" and item["from"] is None, item
    assert item["evidence"] == [] and item["strength3_challenges"] == 0, item
    assert "fake_assumption" in ta["text"] and "confirmed" in ta["text"]


# ───────────────────────── thesis_alerts: items (slice 3 Task 1) ─────────────────────────

def test_thesis_alert_card_groups_rows_into_one_item_with_statement_and_evidence():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    grouped = [i for i in ta["items"]
               if i["ticker"] == "GROUPED" and i["assumption_id"] == "grp_assumption_a"]
    assert len(grouped) == 1, grouped
    item = grouped[0]
    assert item["assumption_id"] == "grp_assumption_a"
    # statement comes from the fixture notes/GROUPED/_thesis.md frontmatter,
    # not a fallback to the raw id.
    assert item["statement"] == \
        "GROUPED depends on segment X demand remaining healthy through the year."
    assert item["from"] == "open" and item["to"] == "challenged", item
    # evidence_log.jsonl has 2 challenge/strength-3 rows for this assumption
    # (a 3rd confirm/strength-1 row is >7 days before the 2026-01-05 card date,
    # and a 4th strength-0 row is dropped by evidence.top()'s own drop rule).
    assert item["strength3_challenges"] == 2, item
    assert len(item["evidence"]) == 2, item["evidence"]
    assert [e["date"] for e in item["evidence"]] == ["2026-01-04", "2026-01-03"], item["evidence"]
    # both surviving evidence rows share the same notes/ ref -> note_links dedupes to 1.
    assert item["note_links"] == ["notes/GROUPED/20260104-1Q26.md"], item["note_links"]
    text = next(t for t in ta["text"].split("\n\n") if t.startswith("GROUPED"))
    assert "GROUPED — GROUPED depends on segment X" in text, text
    assert "open→challenged" in text, text
    assert "(2 evidence)" in text, text


def test_thesis_alert_card_drops_note_kind_rows():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    assert not any(i["assumption_id"] == "20260104-1Q26.md" for i in ta["items"])
    assert "earnings note landed" not in ta["text"]
    assert "note:GROUPED" not in ta["text"]


def test_thesis_alert_card_only_note_rows_returns_none():
    cards = rp.day_cards("2026-01-10", BASE_PATHS)
    assert not any(c["kind"] == "thesis_alerts" for c in cards), cards


def test_thesis_alert_card_score_row_gets_a_minimal_item():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    score_items = [i for i in ta["items"] if i["assumption_id"] == "ai_positioning"]
    assert len(score_items) == 1, ta["items"]
    item = score_items[0]
    assert item["ticker"] == "GROUPED"
    assert item["evidence"] == [] and item["note_links"] == [] and item["strength3_challenges"] == 0
    assert item["from"] is None and item["to"] is None


def test_thesis_alert_card_falls_back_to_why_when_quote_is_empty():
    # earnings_break/earnings_confirm rows carry an empty quote in production
    # (see the live FPS/AAPL rows found during the Task 1 live rebuild) --
    # rendering `: ""` reads as broken enrichment, so the text must fall back
    # to the always-populated `why` field instead of a dangling empty string.
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    item = next(i for i in ta["items"] if i["ticker"] == "QUOTELESS")
    assert item["evidence"][0]["quote"] == ""
    text = next(t for t in ta["text"].split("\n\n") if t.startswith("QUOTELESS"))
    assert '""' not in text, text
    assert "This is the why text used when the quote field is empty" in text, text


def test_thesis_alert_card_evidence_is_windowed_before_capped():
    # WINDOWCAP/window_cap_assumption carries three challenge/strength-3 rows
    # dated 2025-11-01..03 (all well outside the 7-day window around the
    # 2026-01-05 card day) plus one weaker confirm/strength-1 row dated
    # 2026-01-04 (inside the window). evidence.top()'s cap is 3: capping
    # BEFORE filtering to the window fills all three slots with the old
    # strong rows and drops the only in-window row entirely. Filtering to the
    # window FIRST, then capping, is the only order that can ever show it.
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    item = next(i for i in ta["items"] if i["ticker"] == "WINDOWCAP")
    assert [e["date"] for e in item["evidence"]] == ["2026-01-04"], item["evidence"]
    assert item["evidence"][0]["quote"] == "Recent weak confirming detail", item["evidence"]
    text = next(t for t in ta["text"].split("\n\n") if t.startswith("WINDOWCAP"))
    assert "Recent weak confirming detail" in text, text


def test_thesis_alert_card_without_evidence_still_renders():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    noev = next(i for i in ta["items"] if i["ticker"] == "NOEV")
    assert noev["statement"] == "NOEV placeholder assumption with no matched evidence yet."
    assert noev["evidence"] == [] and noev["strength3_challenges"] == 0
    assert noev["from"] == "open" and noev["to"] == "confirmed"
    assert ta["text"], "card text must stay non-empty even with an evidence-free item"
    text = next(t for t in ta["text"].split("\n\n") if t.startswith("NOEV"))
    assert "evidence)" not in text, text


def test_thesis_alerts_absent_on_a_day_with_no_rows():
    cards = rp.day_cards(DAY2, BASE_PATHS)
    assert not any(c["kind"] == "thesis_alerts" for c in cards)


def test_thesis_alerts_absent_when_ledger_file_missing():
    p = rp.Paths(
        is_reports=FIXTURES / "is", podcasts_reports=FIXTURES / "podcasts",
        logs=FIXTURES / "logs", notes=FIXTURES / "notes", watchlist=FIXTURE_WATCHLIST,
        thesis_state=FIXTURES / "does_not_exist",
        topics_state=FIXTURES / "topics_ok", transcripts_state=FIXTURES / "transcripts_ok",
        evidence_state=FIXTURES / "does_not_exist", streams=BASE_PATHS.streams,
    )
    cards = rp.day_cards(DAY1, p)
    assert not any(c["kind"] == "thesis_alerts" for c in cards)


def test_build_reports_calls_evidence_load_index_once_for_the_whole_window():
    # Same reasoning as the alert_events cache just below -- evidence.load_index()
    # re-reads the whole evidence_log.jsonl, so it must run once per build, not
    # once per qualifying day (thesis_state/alerts_sent.jsonl qualifies on both
    # 2026-01-05 and 2026-01-04).
    import datetime as dt
    import tempfile

    calls = []
    orig = rp.evidence.load_index

    def counting(*a, **kw):
        calls.append(a)
        return orig(*a, **kw)

    rp.evidence.load_index = counting
    try:
        with tempfile.TemporaryDirectory() as td:
            rp.build_reports(Path(td), 2, BASE_PATHS, today=dt.date(2026, 1, 5))
    finally:
        rp.evidence.load_index = orig

    assert len(calls) == 1, calls


def test_build_reports_calls_alert_events_once_for_the_whole_window():
    # thesis_state/alerts_sent.jsonl has qualifying rows on BOTH 2026-01-05 and
    # 2026-01-04 -- without the fix round 1 cache this would be 2 alert_events()
    # calls (one per qualifying day); with it, exactly 1 for the whole build.
    import datetime as dt
    import json
    import tempfile

    calls = []
    orig = rp.thesis_report.alert_events

    def counting(*a, **kw):
        calls.append(a)
        return orig(*a, **kw)

    rp.thesis_report.alert_events = counting
    try:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            rp.build_reports(out, 2, BASE_PATHS, today=dt.date(2026, 1, 5))
            d1 = json.loads((out / "data" / "reports" / "2026-01-05.json").read_text())
            d0 = json.loads((out / "data" / "reports" / "2026-01-04.json").read_text())
    finally:
        rp.thesis_report.alert_events = orig

    assert len(calls) == 1, calls
    ta1 = next(c for c in d1["cards"] if c["kind"] == "thesis_alerts")
    ta0 = next(c for c in d0["cards"] if c["kind"] == "thesis_alerts")
    assert "FIXTURE_TICKER" in ta1["text"] and "FIXTURE_TICKER3" not in ta1["text"]
    assert "FIXTURE_TICKER3" in ta0["text"]


def test_day_cards_standalone_still_computes_on_demand_without_a_cache():
    # No thesis_events_cache passed -> day_cards() must still work on its own.
    cards = rp.day_cards("2026-01-04", BASE_PATHS)
    ta = next(c for c in cards if c["kind"] == "thesis_alerts")
    assert "FIXTURE_TICKER3" in ta["text"], ta["text"]


# ───────────────────────── stage_alerts: render() success + degrade ─────────────────────────

def test_stage_alerts_renders_via_stage_alert_when_inputs_load():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    sa = next((c for c in cards if c["kind"] == "stage_alerts"), None)
    assert sa is not None, cards
    assert "fixture_theme" in sa["text"] and "breadth gate" in sa["text"], sa["text"]


def test_stage_alerts_degrades_when_state_files_absent():
    cards = rp.day_cards(DAY2, DEGRADE_PATHS)
    sa = next((c for c in cards if c["kind"] == "stage_alerts"), None)
    assert sa is not None, cards
    assert sa["text"] == "- stage3 · fixture_theme_missing · ZZZ", sa["text"]


def test_stage_alerts_absent_on_a_day_with_no_rows():
    cards = rp.day_cards(DAY2, BASE_PATHS)
    assert not any(c["kind"] == "stage_alerts" for c in cards)


# ───────────────────────── stage_alerts: Task 2 enrichment ─────────────────────────
# fixtures/stage/ (shared with test_evidence.py): diffusion.json pairs FTHM (tier_1,
# stage 3, first_question_date 2026-01-10) and OTHR (tier_2) on fixture_theme_enriched
# across two cal_quarters; exchanges.jsonl carries FTHM's cited question + 2 management
# rows in docA-t plus 3 noise rows (different ticker) in docB-t; watchlist.yaml gives
# FTHM tier_1, OTHR tier_2, ZZZZ tier_3 (unpaired, must never appear); alerts_sent.jsonl
# has a gate row (no ticker -- exercises trend/tier_names on a kind with no citation)
# and the FTHM stage3 row (exercises exchange too); notes/themes/ has a matching note
# so theme_link resolves to a real path.
DAY_STAGE = "2026-01-10"
# STAGE_FIXTURES/FIXTURE_WATCHLIST are defined once, near BASE_PATHS above.
STAGE_PATHS = rp.Paths(
    is_reports=FIXTURES / "is", podcasts_reports=FIXTURES / "podcasts", logs=FIXTURES / "logs",
    notes=STAGE_FIXTURES / "notes", watchlist=FIXTURE_WATCHLIST,
    thesis_state=FIXTURES / "does_not_exist",
    topics_state=STAGE_FIXTURES, transcripts_state=STAGE_FIXTURES,
    evidence_state=FIXTURES / "does_not_exist", streams=BASE_PATHS.streams,
)


def test_stage_alerts_items_shape_and_backward_compatible_text():
    cards = rp.day_cards(DAY_STAGE, STAGE_PATHS)
    sa = next((c for c in cards if c["kind"] == "stage_alerts"), None)
    assert sa is not None, cards
    assert len(sa["items"]) == 2, sa["items"]
    gate = next(i for i in sa["items"] if i["kind"] == "gate")
    stage3 = next(i for i in sa["items"] if i["kind"] == "stage3")
    # text always STARTS with the item's own `line` -- the pre-enrichment text --
    # with any enrichment appended after it on the same line (see
    # _render_stage_item_text), never on its own line.
    assert sa["text"].splitlines()[0].startswith(f"- {gate['line']}"), sa["text"]
    assert stage3["line"] in sa["text"], sa["text"]


def test_stage_alerts_stage3_item_carries_exchange():
    cards = rp.day_cards(DAY_STAGE, STAGE_PATHS)
    sa = next(c for c in cards if c["kind"] == "stage_alerts")
    stage3 = next(i for i in sa["items"] if i["kind"] == "stage3")
    assert stage3["id"] == "stage3:fixture_theme_enriched:FTHM", stage3
    assert stage3["stage"] == 3
    exch = stage3["exchange"]
    assert exch is not None, stage3
    assert exch["speaker_name"] == "Jane Analyst"
    assert exch["speaker_firm"] == "Fixture Capital LLC"
    assert "pipeline breakdown" in exch["answer"]
    assert "noise" not in exch["answer"].lower()


def test_stage_alerts_trend_and_tier_names_populate_even_without_a_ticker():
    # 'gate' events have no single cited ticker (exchange stays None), but trend and
    # tier_names are per-theme -- they must still populate.
    cards = rp.day_cards(DAY_STAGE, STAGE_PATHS)
    sa = next(c for c in cards if c["kind"] == "stage_alerts")
    gate = next(i for i in sa["items"] if i["kind"] == "gate")
    assert gate["exchange"] is None, gate
    assert gate["trend"] == {
        "current_quarter": "CY2026-Q1", "n_banks": 3, "n_companies": 4, "n_disclosing": 2,
        "prev_quarter": "CY2025-Q4", "prev_n_banks": 1, "prev_n_companies": 2,
    }, gate["trend"]
    assert gate["tier_names"] == {"tier_1": ["FTHM"], "tier_2": ["OTHR"]}, gate["tier_names"]


def test_stage_alerts_theme_link_resolves_when_note_exists():
    cards = rp.day_cards(DAY_STAGE, STAGE_PATHS)
    sa = next(c for c in cards if c["kind"] == "stage_alerts")
    stage3 = next(i for i in sa["items"] if i["kind"] == "stage3")
    assert stage3["theme_link"] == "notes/themes/fixture_theme_enriched.md", stage3


def test_stage_alerts_text_includes_qa_breadth_and_tier_segments():
    cards = rp.day_cards(DAY_STAGE, STAGE_PATHS)
    sa = next(c for c in cards if c["kind"] == "stage_alerts")
    assert 'Q: "Can you quantify' in sa["text"], sa["text"]
    assert '— A: "Sure' in sa["text"], sa["text"]
    assert "breadth 3 banks / 4 cos (prev 1/2)" in sa["text"], sa["text"]
    assert "tier 1/2 on theme: FTHM, OTHR" in sa["text"], sa["text"]


def test_stage_alerts_degrade_still_nulls_exchange_trend_and_empties_tier_names():
    # the pre-existing degrade fixture (topics_degrade/does_not_exist) -- diffusion.json
    # and topic_map.jsonl are both missing, so snap is None and every enrichment field
    # must be null/empty, matching the byte-identical fallback text this test already
    # asserted on before Task 2.
    cards = rp.day_cards(DAY2, DEGRADE_PATHS)
    sa = next(c for c in cards if c["kind"] == "stage_alerts")
    item = sa["items"][0]
    assert item["exchange"] is None and item["trend"] is None and item["tier_names"] == {}, item
    assert item["line"] == "stage3 · fixture_theme_missing · ZZZ" == sa["text"][2:], item


def test_stage_alerts_needed_tickers_is_scoped_not_the_whole_universe():
    # fix round 1 (reviewer-required): the ticker set built BEFORE loading
    # exchanges.jsonl must be exactly the tickers today's events could cite --
    # FTHM (the stage3 row's own ticker) and nothing else (no OTHR/ZZZZ, even
    # though both appear in diffusion.json's pairs / watchlist.yaml's universe).
    rows = [r for r in rp._read_jsonl(STAGE_FIXTURES / "alerts_sent.jsonl") if r["as_of"] == DAY_STAGE]
    snap = json.loads((STAGE_FIXTURES / "diffusion.json").read_text())
    assert rp._needed_tickers(rows, snap) == {"FTHM"}


def test_stage_alerts_render_inputs_ex_excludes_the_noise_ticker():
    rows = [r for r in rp._read_jsonl(STAGE_FIXTURES / "alerts_sent.jsonl") if r["as_of"] == DAY_STAGE]
    _, _, ex = rp._stage_alert_render_inputs(STAGE_PATHS, rows)
    assert ex is not None
    assert all(r["ticker"] == "FTHM" for r in ex.values()), ex
    assert not any(r["ticker"] == "ZZZZ" for r in ex.values()), "noise ticker must not be retained"


def test_stage_alerts_text_omits_dash_a_segment_when_no_answer():
    text = rp._render_stage_item_text(
        "the line", {"question": "a question with no answer", "answer": None}, None, None)
    assert text == 'the line Q: "a question with no answer"', text
    assert "— A:" not in text, text


# ───────────────────────── upcoming ─────────────────────────

def test_upcoming_returns_empty_list_without_calling_factset():
    assert rp.upcoming(14, BASE_PATHS) == []


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
