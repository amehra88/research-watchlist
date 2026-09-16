"""
Unit tests for scripts/portal/reports.py (RIS4 slice 2, Task 3).

Fixtures in fixtures/reports/ are hand-built two-day sets for every stream (ws,
is, podcasts, logs/etfflows(+table), logs/news_digest_*), plus thesis_state/
topics_ok/topics_degrade/transcripts_ok for the two alert ledgers. The ws day-1
fixture is a byte-for-byte copy of a real report_2026-09-15.txt (re-dated) so
the parser is tested against real Unicode (em dash, →, σ), not hand-typed
approximations of them. Tests run ONLY against these fixtures via explicit
`paths: Paths` overrides — reports.py's own zero-arg REPO-backed defaults are
never exercised here, EXCEPT the one documented case (thesis_alerts' join to
thesis_report.alert_events(), which has no override hook — see reports.py's
module docstring for why that is still fixture-safe).

No pytest in this env — run directly:
    python3 scripts/portal/test_reports.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reports as rp  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "reports"

BASE_PATHS = rp.Paths(
    ws_reports=FIXTURES / "ws",
    is_reports=FIXTURES / "is",
    podcasts_reports=FIXTURES / "podcasts",
    logs=FIXTURES / "logs",
    thesis_state=FIXTURES / "thesis_state",
    topics_state=FIXTURES / "topics_ok",
    transcripts_state=FIXTURES / "transcripts_ok",
    evidence_state=FIXTURES / "does_not_exist",
    streams=[
        ("ETF UPDATE", str((FIXTURES / "ws" / "report_{date}.txt"))),
        ("ETF FLOWS & CROWDING", str((FIXTURES / "logs" / "report_etfflows_{date}.txt"))),
        ("INSIDER ACTIVITY", str((FIXTURES / "is" / "report_{date}.txt"))),
        ("PODCAST DIGEST", str((FIXTURES / "podcasts" / "report_{date}.txt"))),
        ("ETF FLOW DETAIL", str((FIXTURES / "logs" / "report_etfflows_table_{date}.txt"))),
    ],
)

DEGRADE_PATHS = rp.Paths(
    ws_reports=FIXTURES / "ws", is_reports=FIXTURES / "is",
    podcasts_reports=FIXTURES / "podcasts", logs=FIXTURES / "logs",
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

def test_thesis_alerts_falls_back_to_id_when_not_in_live_alert_events():
    cards = rp.day_cards(DAY1, BASE_PATHS)
    ta = next((c for c in cards if c["kind"] == "thesis_alerts"), None)
    assert ta is not None, cards
    assert "FIXTURE_TICKER" in ta["text"]
    # This fixture id is invented and can never appear in the live repo's real
    # alert_events() output, so the join must fall back to the raw id text.
    assert "status:FIXTURE_TICKER:fake_assumption:confirmed:2026-01-05" in ta["text"]


def test_thesis_alerts_absent_on_a_day_with_no_rows():
    cards = rp.day_cards(DAY2, BASE_PATHS)
    assert not any(c["kind"] == "thesis_alerts" for c in cards)


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


# ───────────────────────── upcoming ─────────────────────────

def test_upcoming_returns_empty_list_without_calling_factset():
    assert rp.upcoming(14, BASE_PATHS) == []


# ───────────────────────── etf_trades parser ─────────────────────────

def test_etf_trades_parses_new_exits_added_trimmed():
    result = rp.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
    day = next(d for d in result["days"] if d["date"] == DAY1)
    etfs = {e["etf"]: e for e in day["etfs"]}

    assert len(etfs) == 15, sorted(etfs)

    jtek = etfs["JTEK"]
    assert [n["sym"] for n in jtek["new"]] == ["ADSK", "GENB"]
    assert jtek["new"][0] == {"sym": "ADSK", "name": "AUTODESK INC COMMON",
                               "weight": 0.25, "shares": 47525}
    assert len(jtek["added"]) == 4
    assert len(jtek["trimmed"]) == 2
    assert jtek["trimmed"][0] == {"sym": "ORCL", "name": "ORACLE CORP COMMON STOCK",
                                   "delta_pp": -0.83, "from_weight": 1.18, "to_weight": 0.32}

    tek = etfs["TEK"]
    assert len(tek["added"]) == 1 and len(tek["trimmed"]) == 1

    alai = etfs["ALAI"]
    assert len(alai["new"]) == 1 and len(alai["added"]) == 3 and len(alai["trimmed"]) == 24

    ais = etfs["AIS"]
    assert len(ais["new"]) == 1 and len(ais["exits"]) == 1
    assert ais["exits"][0] == {"sym": "688008", "name": "C1 Montage Technology Co Ltd",
                                "weight": 1.01, "shares": 351334}

    no_trade = etfs["SPRX"]
    assert no_trade == {"etf": "SPRX", "name": "SPEAR Alpha ETF",
                         "new": [], "exits": [], "added": [], "trimmed": []}


def test_etf_trades_by_ticker_inverted_index():
    result = rp.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
    assert result["by_ticker"]["ADSK"] == [{"date": DAY1, "etf": "JTEK", "action": "new"}]
    assert result["by_ticker"]["ORCL"] == [{"date": DAY1, "etf": "JTEK", "action": "trimmed"}]
    assert {"date": DAY1, "etf": "AIS", "action": "exit"} in result["by_ticker"]["688008"]


def test_etf_trades_tolerates_missing_day():
    result = rp.etf_trades(3, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 7))
    dates = {d["date"] for d in result["days"]}
    assert dates == {DAY1, DAY2}  # 2026-01-07 has no ws fixture -> skipped, not an error


def test_etf_trades_writes_file_when_out_dir_given():
    import tempfile
    import json
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        result = rp.etf_trades(1, out_dir=out, paths=BASE_PATHS,
                                today=__import__("datetime").date(2026, 1, 5))
        out_path = out / "data" / "etf_trades.json"
        assert out_path.exists()
        assert json.loads(out_path.read_text()) == result


def test_etf_trades_no_write_without_out_dir():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rp.etf_trades(1, paths=BASE_PATHS, today=__import__("datetime").date(2026, 1, 5))
        assert not (Path(td) / "data").exists()


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
