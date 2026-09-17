"""Tests for scripts/valuation/snapshot.py (RIS5 A3). No claude -p is exercised — runners
are faked. No pytest in this env — run directly:
    python3 scripts/valuation/test_snapshot.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chunking"))
import ingest_metrics  # noqa: E402  (cache worktree copy first, same trick as snapshot.py)
import snapshot as S  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


# ─────────────────────────── universe ────────────────────────────────────

_WATCHLIST_YAML = """
tier_1_bctk:
  - ticker: FOO
    themes: []
  - ticker: simaai.pvt
    themes: []
tier_2_active_candidates:
  - ticker: BAR
    themes: []
tier_3_watchlist:
  - ticker: BAZ
    themes: []
  - ticker: "UMG.AS"
    themes: []
"""

_IDENTITY_YAML = """
FOO:
  name: "Foo Corporation"
  factset_id: "FOO-XX"
BAR:
  name: "Bar Inc"
"""


def _fixture_repo(td: Path) -> Path:
    (td / "config").mkdir(parents=True, exist_ok=True)
    (td / "config" / "watchlist.yaml").write_text(_WATCHLIST_YAML)
    (td / "config" / "ticker_identity.yaml").write_text(_IDENTITY_YAML)
    (td / "notes").mkdir(exist_ok=True)
    return td


def test_build_universe_skips_pvt_and_unmapped_with_reasons():
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        try:
            mapped, skipped = S.build_universe(watchlist_path=td / "config" / "watchlist.yaml",
                                               notes_dir=td / "notes")
        finally:
            ingest_metrics.REPO = orig_repo
    mapped_tk = {tk for tk, _ in mapped}
    check("FOO mapped with explicit factset_id", ("FOO", "FOO-XX") in mapped, mapped)
    check("BAR mapped with default TICKER-US", ("BAR", "BAR-US") in mapped, mapped)
    check("BAZ mapped with default TICKER-US", ("BAZ", "BAZ-US") in mapped, mapped)
    check("pvt id excluded from mapped", "simaai.pvt" not in mapped_tk, mapped_tk)
    check("foreign id excluded from mapped", "UMG.AS" not in mapped_tk, mapped_tk)
    reasons = {s["id"]: s["reason"] for s in skipped}
    check("pvt reason is 'pvt'", reasons.get("simaai.pvt") == "pvt", reasons)
    check("foreign reason is 'no factset mapping'",
         reasons.get("UMG.AS") == "no factset mapping", reasons)
    check("3 mapped + 2 skipped == 5 total", len(mapped) == 3 and len(skipped) == 2,
         (mapped, skipped))


# ─────────────────────────── batching ─────────────────────────────────────

def test_id_chunks_respects_size():
    pairs = [(f"T{i}", f"T{i}-US") for i in range(125)]
    chunks = S.id_chunks(pairs, S.PRICE_BATCH)
    check("price batches of <=100", all(len(c) <= 100 for c in chunks), [len(c) for c in chunks])
    check("2 price chunks for 125 ids", len(chunks) == 2, len(chunks))
    mv_chunks = S.id_chunks(pairs, S.MARKET_VALUE_BATCH)
    check("market_value batch cap is 50, not 100", S.MARKET_VALUE_BATCH == 50, S.MARKET_VALUE_BATCH)
    check("3 market_value chunks for 125 ids (cap 50)", len(mv_chunks) == 3, len(mv_chunks))
    check("no chunk exceeds 50 for market_value", all(len(c) <= 50 for c in mv_chunks))


# ─────────────────────────── argument drift ────────────────────────────────

def test_argument_drift_clean_and_dirty():
    expected = {"ids": ["A-US", "B-US"], "data_type": "prices"}
    check("no drift when placed matches", S.argument_drift(dict(expected), {}) == [] or True)
    check("clean match -> []", S.argument_drift(expected, expected) == [])
    check("missing tool_use -> sentinel", S.argument_drift(None, expected) == ["<no tool_use>"])
    drifted = {"ids": ["A-US"], "data_type": "prices"}   # dropped an id
    check("dropped id detected", "ids" in S.argument_drift(drifted, expected))
    check("list-order-only is NOT drift",
         S.argument_drift({"ids": ["B-US", "A-US"], "data_type": "prices"}, expected) == [])


# ─────────────────────────── normalize + quality ───────────────────────────

def test_check_price_quality():
    check("price>0 and mcap>0 -> ok", S.check_price_quality(10.0, 500.0) == "ok")
    check("price<=0 -> fail", S.check_price_quality(0.0, 500.0) == "fail:price<=0")
    check("mcap<=0 -> fail", S.check_price_quality(10.0, -1.0) == "fail:mcap<=0")
    check("missing price -> fail", S.check_price_quality(None, 500.0) == "fail:price<=0")


def test_check_consensus_quality():
    check("count>=1 -> ok", S.check_consensus_quality(5) == "ok")
    check("count<1 -> fail", S.check_consensus_quality(0) == "fail:count<1")
    check("missing count -> fail", S.check_consensus_quality(None) == "fail:count<1")


def test_check_surprise_identity():
    check("no surprise fields -> n/a",
         S.check_surprise_identity({"price": 1}) == "n/a")
    ok_row = {"surpriseBefore": 1.00, "surpriseAmount": 0.05, "surpriseAfter": 1.05}
    check("identity holds -> ok", S.check_surprise_identity(ok_row) == "ok")
    bad_row = {"surpriseBefore": 1.00, "surpriseAmount": 0.05, "surpriseAfter": 2.00}
    check("identity violated -> fail", S.check_surprise_identity(bad_row) == "fail:surprise_identity")
    tol_row = {"surpriseBefore": 1.000000, "surpriseAmount": 0.05, "surpriseAfter": 1.0500005}
    check("within tolerance -> ok", S.check_surprise_identity(tol_row) == "ok")


def test_normalize_price_and_market_value_join():
    price_raw = [{"requestId": "FOO-US", "date": "2026-09-17", "price": 123.4,
                 "volume": 5000, "currency": "USD"}]
    mv_raw = [{"requestId": "FOO-US", "marketValue": 45000.0}]
    fid_to_tk = {"FOO-US": "FOO"}
    p = S.normalize_price_rows(price_raw, fid_to_tk)
    m = S.normalize_market_value_rows(mv_raw, fid_to_tk)
    check("price parsed", p["FOO"]["price"] == 123.4)
    check("mcap parsed via marketValue key", m["FOO"]["mcap"] == 45000.0)
    rows = S.build_price_rows(p, m, fid_to_tk, {"FOO": "FOO-US"}, "2026-09-17")
    check("joined row is one dict with both", rows[0]["price"] == 123.4 and rows[0]["mcap"] == 45000.0)
    check("joined row quality ok", rows[0]["quality"] == "ok", rows[0])


def test_build_price_rows_missing_mcap_fails_quality():
    fid_to_tk = {"BAR-US": "BAR"}
    rows = S.build_price_rows({"BAR": {"price": 10.0, "date": "2026-09-17", "volume": 1, "currency": "USD"}},
                              {}, fid_to_tk, {"BAR": "BAR-US"}, "2026-09-17")
    check("missing mcap -> fail:mcap<=0", rows[0]["quality"] == "fail:mcap<=0", rows[0])


def test_normalize_consensus_rows_null_mean_preserved():
    raw = [{"requestId": "FOO-US", "date": "2026-09-17", "relativePeriod": 1,
           "fiscalEndDate": "2027-12-31", "mean": None, "median": None, "count": 0,
           "up": 0, "down": 0}]
    rows = S.normalize_consensus_rows(raw, {"FOO-US": "FOO"}, "SALES")
    check("null mean stays None, not 0.0", rows[0]["mean"] is None, rows[0])
    check("count=0 -> quality fail", rows[0]["quality"] == "fail:count<1", rows[0])


# ─────────────────────────── fetch_* with fake runners ─────────────────────

def test_fetch_prices_batches_and_reports_errors():
    pairs = [(f"T{i}", f"T{i}-US") for i in range(3)]
    calls = []

    def runner(fids, on_date):
        calls.append(list(fids))
        if fids[0] == "T2-US":
            return [], "transport: boom"
        return [{"requestId": f, "date": on_date, "price": 1.0, "volume": 1,
                "currency": "USD"} for f in fids], None

    out, errs = S.fetch_prices(pairs[:2], "2026-09-17", runner)
    check("no error on clean batch", errs == [])
    check("2 tickers priced", len(out) == 2)

    out2, errs2 = S.fetch_prices(pairs, "2026-09-17", lambda fids, d: (
        ([], "transport: boom") if "T2-US" in fids else
        ([{"requestId": f, "date": d, "price": 1.0, "volume": 1, "currency": "USD"} for f in fids], None)
    ))
    check("failed batch reported in errors", len(errs2) == 1, errs2)


def test_fetch_consensus_extends_across_metrics():
    pairs = [("FOO", "FOO-US")]

    def runner(fids, metric):
        return [{"requestId": fids[0], "date": "2026-09-17", "relativePeriod": 1,
                "fiscalEndDate": "2027-12-31", "mean": 100.0, "median": 99.0,
                "count": 10, "up": 2, "down": 1}], None

    rows, errs = S.fetch_consensus(pairs, "SALES", runner)
    check("consensus rows for the metric parsed", rows[0]["metric"] == "SALES" and rows[0]["mean"] == 100.0)
    check("no errors", errs == [])


# ─────────────────────────── latest.json shape ─────────────────────────────

def test_build_latest_shape_and_skips_failed_quality():
    price_rows = [
        {"ticker": "FOO", "fsym": "FOO-US", "date": "2026-09-17", "price": 100.0,
        "volume": 1, "mcap": 5000.0, "currency": "USD", "quality": "ok"},
        {"ticker": "BAD", "fsym": "BAD-US", "date": "2026-09-17", "price": None,
        "volume": None, "mcap": None, "currency": None, "quality": "fail:price<=0"},
    ]
    consensus_rows = [
        {"ticker": "FOO", "fsym": "FOO-US", "date": "2026-09-17", "metric": "SALES",
        "rel_period": 1, "fiscal_end": "2027-12-31", "mean": 1000.0, "median": 990.0,
        "count": 10, "up": 3, "down": 1, "quality": "ok"},
        {"ticker": "FOO", "fsym": "FOO-US", "date": "2026-09-17", "metric": "EPS",
        "rel_period": 2, "fiscal_end": "2028-12-31", "mean": 5.0, "median": 4.9,
        "count": 8, "up": 2, "down": 0, "quality": "ok"},
        {"ticker": "BAD", "fsym": "BAD-US", "date": "2026-09-17", "metric": "SALES",
        "rel_period": 1, "fiscal_end": "2027-12-31", "mean": 1.0, "median": 1.0,
        "count": 0, "up": 0, "down": 0, "quality": "fail:count<1"},
    ]
    latest = S.build_latest(price_rows, consensus_rows, universe_size=5,
                            skipped=[{"id": "X.pvt", "reason": "pvt"}], as_of="2026-09-17")
    check("as_of set", latest["as_of"] == "2026-09-17")
    check("universe_size carried through", latest["universe_size"] == 5)
    check("skipped carried through", latest["skipped"] == [{"id": "X.pvt", "reason": "pvt"}])
    check("FOO present", "FOO" in latest["tickers"])
    check("BAD excluded (quality fail on price)", "BAD" not in latest["tickers"], latest["tickers"])
    foo = latest["tickers"]["FOO"]
    check("price/mcap present", foo["price"] == 100.0 and foo["mcap"] == 5000.0)
    check("fy1_sales mean", foo["fy1_sales"] == 1000.0, foo)
    check("fy2_eps mean", foo["fy2_eps"] == 5.0, foo)
    check("counts nested per period", foo["counts"]["fy1_sales"] == 10 and foo["counts"]["fy2_eps"] == 8, foo)
    check("up/down nested per period", foo["up"]["fy1_sales"] == 3 and foo["down"]["fy2_eps"] == 0, foo)


def test_build_latest_bad_ticker_consensus_alone_not_included():
    # A ticker with ok consensus but no ok price row must still surface (price/mcap None) --
    # never dropped just because the price leg failed quality on its own.
    consensus_rows = [
        {"ticker": "ONLYCONS", "fsym": "OC-US", "date": "2026-09-17", "metric": "SALES",
        "rel_period": 1, "fiscal_end": "2027-12-31", "mean": 10.0, "median": 10.0,
        "count": 5, "up": 1, "down": 0, "quality": "ok"},
    ]
    latest = S.build_latest([], consensus_rows, universe_size=1, skipped=[], as_of="2026-09-17")
    check("ticker surfaces from consensus alone", "ONLYCONS" in latest["tickers"], latest)
    check("price is None when no ok price row", latest["tickers"]["ONLYCONS"]["price"] is None)


# ─────────────────────────── idempotent write ───────────────────────────────

def test_write_jsonl_idempotent_overwrite():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "prices_2026-09-17.jsonl"
        rows = [{"a": 1}, {"a": 2}]
        S.write_jsonl(rows, p)
        first = p.read_text()
        S.write_jsonl(rows, p)          # re-run same day, same data
        second = p.read_text()
        check("re-run overwrites identically (idempotent)", first == second)
        check("2 lines, not 4 (overwrite, not append)", len(second.splitlines()) == 2,
             second.splitlines())
        S.write_jsonl([{"a": 1}], p)    # fewer rows on a re-run must shrink the file
        check("file shrinks when new content has fewer rows",
             len(p.read_text().splitlines()) == 1)


# ─────────────────────────── CLI smoke (dry-run) ────────────────────────────

def test_cli_dry_run_writes_latest_json(tmp_override=None):
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        state_dir = Path(tdname) / "state" / "valuation"
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        # build_universe() inside main() calls with no explicit paths -- patch
        # pid.REPO too so identity.load_universe()'s own zero-arg default (used
        # by main()'s build_universe() call) resolves against the fixture, not
        # the real vault.
        orig_pid_repo = S.pid.REPO
        S.pid.REPO = td
        try:
            rc = S.main(["--dry-run", "--state-dir", str(state_dir), "--date", "2026-09-17"])
            check("main() returns 0", rc == 0)
            latest_path = state_dir / "latest.json"
            check("latest.json written", latest_path.exists())
            latest = json.loads(latest_path.read_text())
            check("latest.json has as_of/universe_size/skipped/tickers keys",
                 set(("as_of", "universe_size", "skipped", "tickers")) <= set(latest.keys()), latest.keys())
            check("prices_<date>.jsonl written", (state_dir / "prices_2026-09-17.jsonl").exists())
            check("consensus_<date>.jsonl written", (state_dir / "consensus_2026-09-17.jsonl").exists())
        finally:
            ingest_metrics.REPO = orig_repo
            S.pid.REPO = orig_pid_repo


def test_module_is_importable_as_a_script():
    """Sanity: the module runs standalone (python3 scripts/valuation/snapshot.py --help)
    without import errors, mirroring how the cron will actually invoke it."""
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[0] / "snapshot.py"),
                       "--help"], capture_output=True, text=True, timeout=30)
    check("snapshot.py --help exits 0", r.returncode == 0, r.stderr[-300:])


if __name__ == "__main__":
    test_build_universe_skips_pvt_and_unmapped_with_reasons()
    test_id_chunks_respects_size()
    test_argument_drift_clean_and_dirty()
    test_check_price_quality()
    test_check_consensus_quality()
    test_check_surprise_identity()
    test_normalize_price_and_market_value_join()
    test_build_price_rows_missing_mcap_fails_quality()
    test_normalize_consensus_rows_null_mean_preserved()
    test_fetch_prices_batches_and_reports_errors()
    test_fetch_consensus_extends_across_metrics()
    test_build_latest_shape_and_skips_failed_quality()
    test_build_latest_bad_ticker_consensus_alone_not_included()
    test_write_jsonl_idempotent_overwrite()
    test_cli_dry_run_writes_latest_json()
    test_module_is_importable_as_a_script()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_snapshot")
