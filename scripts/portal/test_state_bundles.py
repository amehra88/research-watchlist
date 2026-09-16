"""
Unit tests for scripts/portal/state_bundles.py + scripts/portal/news_sec.py
(RIS4 slice 2, Task 4).

themes_bundle()/ideas_bundle() tests moved to test_theme_ideas.py in fix round 1
when theme_ideas.py was split out of state_bundles.py (controller-authorized,
review 768e415d..4f613b35) -- both test files share the same fixtures/state/
directory.

Fixtures live under fixtures/state/ (topics/, thesis/, notes/, docs/,
state_portal/, watchlist.yaml, ticker_identity.yaml, cron_runs_fixture.txt --
named .txt not .log because *.log is globally gitignored in this repo).
Every test pins `today` to 2026-09-16 for deterministic windowing (news/sec
30-day cutoffs, market_bundle's 14-day ETF-flows window, manifest's 7-day
cron-failure window and 180-day staleness window).

No pytest in this env -- run directly:
    python3 scripts/portal/test_state_bundles.py
"""
import contextlib
import io
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identity            # noqa: E402
import news_sec            # noqa: E402
import state_bundles as sb  # noqa: E402
import vault                # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "state"
TODAY = date(2026, 9, 16)

BASE_PATHS = sb.Paths(
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


def _build_ticker_bundles(paths: sb.Paths) -> dict:
    """Same composition build_state() does, using only PUBLIC vault/identity
    functions -- exercises the real integration path rather than a private
    helper."""
    refs = vault.discover(paths.notes)
    universe = identity.load_universe(paths.watchlist, paths.notes)
    names = identity.display_names(paths.watchlist, notes_dir=paths.notes)
    known_tickers = {r.ticker for r in refs if r.ticker}
    known_themes = {Path(r.rel).stem for r in refs if r.kind == "theme"}
    return {e["ticker"]: vault.ticker_bundle(e["ticker"], refs, names, known_tickers, known_themes, meta=e)
            for e in universe}


# ───────────────────────── scores_bundle ─────────────────────────

def test_scores_bundle_reads_are_newest_first():
    bundles = _build_ticker_bundles(BASE_PATHS)
    sbnd = sb.scores_bundle(bundles, as_of="2026-09-16")
    fix = sbnd["tickers"]["FIX"]
    dates = [r["date"] for r in fix["reads"]]
    assert dates == ["2026-09-01", "2026-03-01"], dates
    assert fix["reads"][0]["note_id"] == "FIX/20260901-3Q26.md"


def test_scores_bundle_current_shape_and_proposed():
    bundles = _build_ticker_bundles(BASE_PATHS)
    sbnd = sb.scores_bundle(bundles)
    fix = sbnd["tickers"]["FIX"]
    assert fix["current"] == {
        "ai_positioning": "4",
        "competitive_advantage": {"innovation_rate": "4", "distribution": "3", "overall": "4"},
        "investor_interest": "3",
    }
    assert "ai_positioning" in fix["proposed"]
    assert any(p["key"] == "ai_positioning" for p in fix["pending_proposals"])


def test_scores_bundle_handles_bare_scalar_score_variant():
    # config/watchlist.yaml carries two schema variants for ai_positioning /
    # potential_investor_interest -- a bare scalar on some live entries
    # (AMZN/BE/GOOG/NVDA/MSFT) and {score, notes} on the rest. BARESTR fixture
    # exercises the bare-scalar path (caught live during the Task 4 live check).
    bundles = _build_ticker_bundles(BASE_PATHS)
    sbnd = sb.scores_bundle(bundles)
    bare = sbnd["tickers"]["BARESTR"]
    assert bare["current"]["ai_positioning"] == "4+"
    assert bare["current"]["investor_interest"] == "3-"
    assert bare["current"]["competitive_advantage"]["overall"] == "3"


def test_scores_bundle_scope_is_t1_t2_plus_thesis():
    bundles = _build_ticker_bundles(BASE_PATHS)
    sbnd = sb.scores_bundle(bundles)
    # AAA is tier_2 (in scope even with no thesis/notes); BBB is tier_3 with no
    # thesis (out of scope); ORPHAN has no tier and no thesis (out of scope).
    assert "AAA" in sbnd["tickers"]
    assert "BBB" not in sbnd["tickers"]
    assert "ORPHAN" not in sbnd["tickers"]


# ───────────────────────── market_bundle ─────────────────────────

def test_market_bundle_glob_for_latest_picks_newest_ranking():
    mb = sb.market_bundle(BASE_PATHS, today=TODAY)
    assert mb["ranking"]["date"] == "2026-09-14"    # not the older 2026-09-10 fixture


def test_market_bundle_drops_raw_from_insiders():
    mb = sb.market_bundle(BASE_PATHS, today=TODAY)
    assert len(mb["insiders"]) == 1
    assert "_raw" not in mb["insiders"][0]
    assert mb["insiders"][0]["insider"] == "Jane Doe"   # the newer (09-13) file, not 09-06


def test_market_bundle_degrades_when_etf_files_absent():
    mb = sb.market_bundle(BASE_PATHS, today=TODAY)
    assert mb["etf_lookthrough"] == {}
    assert mb["etf_flows_14d"] == []


# ───────────────────────── manifest ─────────────────────────

def test_manifest_ticker_rows_include_orphan():
    mani = sb.manifest(sb.Ctx(today=TODAY, paths=BASE_PATHS))
    by_ticker = {t["ticker"]: t for t in mani["tickers"]}
    assert "ORPHAN" in by_ticker
    o = by_ticker["ORPHAN"]
    assert o["orphan_notes"] is True
    assert o["tier"] == "none"
    assert o["has_notes"] is True and o["n_notes"] >= 1


def test_manifest_health_and_applied_ids():
    mani = sb.manifest(sb.Ctx(today=TODAY, paths=BASE_PATHS))
    h = mani["health"]
    assert h["stale_assumptions"] >= 1     # FIX's fixture_assumption, last_evidence 2026-01-05
    assert "fixture_theme_gate_only" in h["themes_without_labels"]
    assert "fixture_theme_a" not in h["themes_without_labels"]
    assert len(h["last_job_failures"]) == 1
    assert h["last_job_failures"][0]["job"] == "fixture_fail"
    assert mani["applied_ids"] == ["gap:fixture_theme_b|CY2026-Q2"]


def test_manifest_without_out_dir_leaves_today_and_files_empty():
    mani = sb.manifest(sb.Ctx(today=TODAY, paths=BASE_PATHS))
    assert mani["today"]["cards"] == []
    assert mani["upcoming"] == []
    assert mani["files"] == {}
    # vendor is independent of out_dir/files -- it reads the package's own
    # checked-in scripts/portal/app/vendor/, present in this worktree (see
    # test_vendor_manifest_* below for the isolated-tmp-dir cases).
    assert "markdown-it" in mani["vendor"], mani["vendor"]


# ───────────────────────── _vendor_manifest ─────────────────────────

def test_vendor_manifest_reads_versions_txt_and_hashes_the_real_file():
    import shutil
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="ris4_vendor_test_"))
    try:
        content = b"/* pretend markdown-it build */"
        (td / "fake-lib.min.js").write_bytes(content)
        (td / "VERSIONS.txt").write_text(
            "Vendored third-party assets for the RIS4 portal app.\n"
            "Copied verbatim into <out>/vendor/.\n\n"
            "fake-lib 9.9.9  (UMD build, global `fakeLib`, MIT)\n"
            "  file    fake-lib.min.js\n"
            "  bytes   32\n"
            "  sha256  0000000000000000000000000000000000000000000000000000000000000000\n"
            "  source  https://example.com/fake-lib.min.js\n"
            "  pulled  2026-09-16\n"
        )
        vendor = sb._vendor_manifest(td)
        assert list(vendor) == ["fake-lib"], vendor
        assert vendor["fake-lib"]["version"] == "9.9.9"
        # hashed directly off disk, not trusted from the (deliberately wrong)
        # sha256 recorded in VERSIONS.txt above.
        assert vendor["fake-lib"]["sha256"] == sb._sha256_file(td / "fake-lib.min.js")
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_vendor_manifest_missing_dir_returns_empty():
    assert sb._vendor_manifest(Path("/nonexistent/vendor/dir")) == {}


def test_vendor_manifest_skips_entry_whose_file_is_missing():
    import shutil
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="ris4_vendor_test_"))
    try:
        (td / "VERSIONS.txt").write_text(
            "some-lib 1.0.0  (MIT)\n"
            "  file    some-lib.min.js\n"
        )
        assert sb._vendor_manifest(td) == {}
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ───────────────────────── news_sec._iso_week_shard ─────────────────────────

def test_iso_week_shard_accepts_a_real_date_object():
    # An unquoted `published_date: 2026-09-10` in frontmatter YAML parses as a
    # real datetime.date, not a str -- _iso_week_shard() must handle that
    # (str() first) rather than TypeError on a perfectly valid date and have
    # the news_bundle() malformed-date guard silently swallow a good row.
    assert news_sec._iso_week_shard(date(2026, 9, 10)) == "2026-W37"
    assert news_sec._iso_week_shard("2026-09-10") == "2026-W37"


# ───────────────────────── news_sec.news_bundle ─────────────────────────

def test_news_bundle_shards_by_iso_week_and_indexes_tickers():
    nb = news_sec.news_bundle(30, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    assert set(nb["shards"]) == {"2026-W36", "2026-W37"}
    assert len(nb["shards"]["2026-W36"]["rows"]) == 1
    assert len(nb["shards"]["2026-W37"]["rows"]) == 2
    assert "FIX" in nb["index"] and "ORPHAN" in nb["index"]
    shard, idx = nb["index"]["FIX"][0]
    row = nb["shards"][shard]["rows"][idx]
    assert row["tickers"] == ["FIX"] or "FIX" in row["tickers"]


def test_news_bundle_row_shape_headline_and_url():
    nb = news_sec.news_bundle(30, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    row = nb["shards"]["2026-W36"]["rows"][0]
    assert row["headline"] == "Fixture Headline One"
    assert row["url"] == "https://news.example.com/one"
    # third fixture note has no source_urls -> url must be None, not an error
    week37 = nb["shards"]["2026-W37"]["rows"]
    no_url_row = next(r for r in week37 if r["url"] is None)
    assert no_url_row["headline"] == "Fixture Headline Three"


def test_news_bundle_respects_window():
    nb = news_sec.news_bundle(5, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    total = sum(len(v["rows"]) for v in nb["shards"].values())
    assert total == 0       # all 3 fixture notes are > 5 days before 2026-09-16


def test_news_bundle_skips_row_with_malformed_published_date():
    # fixtures/state/notes/news/2026-09-10-bad-date-dddddddd.md carries
    # published_date: not-a-real-date -- _iso_week_shard() can't parse that
    # into a (year, month, day) int triple. The row must be skipped (logged),
    # never abort the whole build; the 3 good fixture rows are unaffected.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        nb = news_sec.news_bundle(30, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    total = sum(len(v["rows"]) for v in nb["shards"].values())
    assert total == 3, nb["shards"]     # the bad-date row contributes nothing
    all_headlines = [r["headline"] for shard in nb["shards"].values() for r in shard["rows"]]
    assert "Fixture Headline Four" not in all_headlines
    assert "bad-date-dddddddd.md" in buf.getvalue()


# ───────────────────────── news_sec.sec_bundle ─────────────────────────

def test_sec_bundle_is_frontmatter_only():
    secb = news_sec.sec_bundle(30, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    assert len(secb["rows"]) == 1
    row = secb["rows"][0]
    assert row == {
        "ticker": "FIX", "form_type": "8-K", "items": ["1"], "filed_date": "2026-09-01",
        "filing_url": "https://www.sec.gov/Archives/fixture-8k.htm",
        "press_release_url": "", "themes": ["fixture_theme_a"],
    }


def test_sec_bundle_respects_window():
    secb = news_sec.sec_bundle(5, news_sec.Paths(notes=BASE_PATHS.notes), today=TODAY)
    assert secb["rows"] == []


# ───────────────────────── build_state (integration) ─────────────────────────

def test_build_state_writes_every_bundle():
    import json
    import shutil
    import tempfile
    tmp_out_dir = Path(tempfile.mkdtemp(prefix="ris4_state_bundles_test_"))
    try:
        stats = sb.build_state(tmp_out_dir, sb.Ctx(today=TODAY, paths=BASE_PATHS, report_summaries=[]))
        data = tmp_out_dir / "data"
        for name in ("themes.json", "ideas.json", "scores.json", "market.json",
                     "news_index.json", "sec_30d.json", "manifest.json"):
            assert (data / name).exists(), name
        assert (data / "news" / "2026-W36.json").exists()
        assert stats["themes"] == 3
        assert stats["sec_rows"] == 1
        mani = json.loads((data / "manifest.json").read_text())
        assert "data/themes.json" in mani["files"]
        assert "data/manifest.json" not in mani["files"]
    finally:
        shutil.rmtree(tmp_out_dir, ignore_errors=True)


def test_build_state_writes_insiders_json_with_the_market_rows():
    """fix round 1 (Task 8 r1): the Insiders tab reads its own small file
    instead of the ~1MB market.json. Same rows, both files written."""
    import json
    import shutil
    import tempfile
    tmp_out_dir = Path(tempfile.mkdtemp(prefix="ris4_state_bundles_test_"))
    try:
        sb.build_state(tmp_out_dir, sb.Ctx(today=TODAY, paths=BASE_PATHS, report_summaries=[]))
        data = tmp_out_dir / "data"
        assert (data / "insiders.json").exists(), "data/insiders.json not written"
        ins = json.loads((data / "insiders.json").read_text())
        mkt = json.loads((data / "market.json").read_text())
        assert ins["rows"] == mkt["insiders"], "insiders.json rows must be market.json's insiders verbatim"
        assert ins["as_of"] == TODAY.isoformat()
        assert "insiders" in mkt, "market.json must keep its own insiders key for other consumers"
        mani = json.loads((data / "manifest.json").read_text())
        assert "data/insiders.json" in mani["files"], "the manifest must hash the new file"
    finally:
        shutil.rmtree(tmp_out_dir, ignore_errors=True)


def test_manifest_counts_carry_search_news_mode_from_the_written_index():
    """fix round 1 (Task 8 r1): Status shows the search index's news window
    without fetching the 3MB index. Read from data/search.json if the
    search-index stage already wrote it, None otherwise -- never a guess."""
    import json
    import shutil
    import tempfile
    tmp_out_dir = Path(tempfile.mkdtemp(prefix="ris4_state_bundles_test_"))
    try:
        (tmp_out_dir / "data").mkdir(parents=True)
        # no search.json yet -> None, not an error
        ctx = sb.Ctx(today=TODAY, paths=BASE_PATHS, report_summaries=[], out_dir=tmp_out_dir)
        assert sb.manifest(ctx)["counts"]["search_news_mode"] is None

        (tmp_out_dir / "data" / "search.json").write_text(
            json.dumps({"docs": [], "terms": {}, "stoplist": [], "news_mode": "7d"}))
        ctx2 = sb.Ctx(today=TODAY, paths=BASE_PATHS, report_summaries=[], out_dir=tmp_out_dir)
        assert sb.manifest(ctx2)["counts"]["search_news_mode"] == "7d"

        (tmp_out_dir / "data" / "search.json").write_text("{ not json")
        ctx3 = sb.Ctx(today=TODAY, paths=BASE_PATHS, report_summaries=[], out_dir=tmp_out_dir)
        assert sb.manifest(ctx3)["counts"]["search_news_mode"] is None
    finally:
        shutil.rmtree(tmp_out_dir, ignore_errors=True)


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
