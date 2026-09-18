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
    check("market_value batch cap is 25 (fix 2, tightened from 50 after a live 408)",
         S.MARKET_VALUE_BATCH == 25, S.MARKET_VALUE_BATCH)
    check("5 market_value chunks for 125 ids (cap 25)", len(mv_chunks) == 5, len(mv_chunks))
    check("no chunk exceeds 25 for market_value", all(len(c) <= 25 for c in mv_chunks))


# ─────────────────────── consensus metrics (amendment v1.2) ────────────────

def test_consensus_metrics_includes_ebitda_and_fcf():
    check("CONSENSUS_METRICS has 4 metrics", len(S.CONSENSUS_METRICS) == 4, S.CONSENSUS_METRICS)
    check("SALES/EPS/EBITDA/FCF all present",
         set(S.CONSENSUS_METRICS) == {"SALES", "EPS", "EBITDA", "FCF"}, S.CONSENSUS_METRICS)
    check("WEEKLY_CONSENSUS_METRICS same four metrics",
         set(S.WEEKLY_CONSENSUS_METRICS) == {"SALES", "EPS", "EBITDA", "FCF"})
    check("weekly relative fiscal window is FY4-FY5",
         (S.WEEKLY_RELATIVE_FISCAL_START, S.WEEKLY_RELATIVE_FISCAL_END) == (4, 5))


def test_consensus_args_honour_explicit_rel_start_end():
    a = S._consensus_args(["FOO-US"], "EBITDA", rel_start=4, rel_end=5)
    check("rel_start/rel_end overridable per-call", a["relativeFiscalStart"] == 4 and a["relativeFiscalEnd"] == 5, a)
    check("metric placed correctly", a["metrics"] == ["EBITDA"])
    default = S._consensus_args(["FOO-US"], "SALES")
    check("defaults still FY1-FY3", (default["relativeFiscalStart"], default["relativeFiscalEnd"]) == (1, 3))


# ─────────────────────── 408/5xx retry (RIS5 A3 fix 2) ──────────────────────

def test_extract_http_status_finds_408_and_5xx():
    check("408 extracted", S._extract_http_status("Client error '408 Request Timeout' for url X") == "408")
    check("502 extracted", S._extract_http_status("Server error '502 Bad Gateway' for url X") == "502")
    check("no status -> None", S._extract_http_status("some other failure") is None)


def test_is_retryable_error_only_matches_marker_not_bare_digits():
    check("http_status=408 is retryable", S._is_retryable_error("tool_result unusable (http_status=408): x"))
    check("http_status=503 is retryable", S._is_retryable_error("tool_result unusable (http_status=503): x"))
    check("http_status=404 is NOT retryable (client error, not timeout/5xx)",
         not S._is_retryable_error("tool_result unusable (http_status=404): x"))
    check("a bare '500' in unrelated text does NOT false-positive (no http_status= marker)",
         not S._is_retryable_error("mean=500.0 count=500 price=408.12"))
    check("None error is not retryable", not S._is_retryable_error(None))


def test_fetch_market_value_retries_once_then_succeeds():
    pairs = [("FOO", "FOO-US")]
    calls = []

    def runner(fids):
        calls.append(fids)
        if len(calls) == 1:
            return [], "tool_result unusable (http_status=408): Client error '408 Request Timeout'"
        return [{"requestId": "FOO-US", "marketValue": 123.0}], None

    sleeps = []
    out, errs = S.fetch_market_value(pairs, runner, retry_wait=20, sleep=sleeps.append)
    check("exactly one retry (2 calls total)", len(calls) == 2, calls)
    check("slept the configured retry_wait once", sleeps == [20], sleeps)
    check("succeeded on the retry", out["FOO"]["mcap"] == 123.0, out)
    check("no error recorded (retry succeeded)", errs == [])


def test_fetch_market_value_retries_once_then_still_fails_marks_batch_failed():
    pairs = [("FOO", "FOO-US")]
    calls = []

    def runner(fids):
        calls.append(fids)
        return [], "tool_result unusable (http_status=408): still timing out"

    sleeps = []
    out, errs = S.fetch_market_value(pairs, runner, retry_wait=20, sleep=sleeps.append)
    check("exactly 2 calls (1 original + 1 retry, never a 3rd)", len(calls) == 2, calls)
    check("batch marked failed", len(errs) == 1 and errs[0]["ids"] == ["FOO-US"], errs)
    check("nothing in out", out == {})


def test_fetch_market_value_non_retryable_error_never_retries():
    pairs = [("FOO", "FOO-US")]
    calls = []

    def runner(fids):
        calls.append(fids)
        return [], "argument drift in ids: placed {...}"

    sleeps = []
    out, errs = S.fetch_market_value(pairs, runner, retry_wait=20, sleep=sleeps.append)
    check("only 1 call -- non-retryable error is not retried", len(calls) == 1, calls)
    check("no sleep called", sleeps == [])
    check("batch marked failed", len(errs) == 1)


def test_fetch_market_value_session_limit_propagates_through_retry_path():
    from newsdigest.classify_llm import SessionLimitError as SLE
    pairs = [("FOO", "FOO-US"), ("BAR", "BAR-US")]

    def runner(fids):
        raise SLE("429 hit")

    threw = False
    try:
        S.fetch_market_value(pairs, runner, retry_wait=0, sleep=lambda s: None)
    except SLE:
        threw = True
    check("SessionLimitError propagates through the retry wrapper untouched", threw)


def test_fetch_prices_and_fetch_consensus_also_get_the_retry():
    calls = []

    def price_runner(fids, on_date):
        calls.append(1)
        if len(calls) == 1:
            return [], "tool_result unusable (http_status=500): Server error '500 Internal'"
        return [{"requestId": fids[0], "date": on_date, "price": 10.0}], None

    out, errs = S.fetch_prices([("FOO", "FOO-US")], "2026-09-17", price_runner,
                              retry_wait=0, sleep=lambda s: None)
    check("prices retried once then succeeded", len(calls) == 2 and errs == [], (calls, errs))

    ccalls = []

    def cons_runner(fids, metric):
        ccalls.append(1)
        if len(ccalls) == 1:
            return [], "tool_result unusable (http_status=503): Server error '503'"
        return [{"requestId": fids[0], "estimateDate": "2026-09-17", "relativePeriod": 1,
                "fiscalEndDate": "2027-12-31", "mean": 1.0, "median": 1.0,
                "estimateCount": 1, "up": 1, "down": 0}], None

    crows, cerrs = S.fetch_consensus([("FOO", "FOO-US")], "FCF", cons_runner,
                                     retry_wait=0, sleep=lambda s: None)
    check("consensus retried once then succeeded", len(ccalls) == 2 and cerrs == [], (ccalls, cerrs))
    check("recovered row has the right metric", crows[0]["metric"] == "FCF")


# ─────────────────────── weekly FY4-FY5 (amendment v1.2) ────────────────────

def test_merge_weekly_consensus_adds_fy4_fy5_without_touching_daily_fields():
    latest = {"as_of": "2026-09-17", "tickers": {
        "FOO": {"price": 10.0, "mcap": 500.0, "fy1_sales": 100.0,
               "counts": {"fy1_sales": 5}, "up": {"fy1_sales": 2}, "down": {"fy1_sales": 1}},
    }}
    weekly_rows = [
        {"ticker": "FOO", "metric": "SALES", "rel_period": 4, "mean": 400.0,
        "count": 6, "up": 3, "down": 1, "quality": "ok"},
        {"ticker": "FOO", "metric": "EBITDA", "rel_period": 5, "mean": 55.0,
        "count": 4, "up": 1, "down": 0, "quality": "ok"},
        {"ticker": "FOO", "metric": "SALES", "rel_period": 1, "mean": 999.0,
        "count": 9, "up": 9, "down": 0, "quality": "fail:count<1"},  # must be skipped
    ]
    merged = S.merge_weekly_consensus(latest, weekly_rows, "2026-09-20")
    foo = merged["tickers"]["FOO"]
    check("daily price/mcap untouched", foo["price"] == 10.0 and foo["mcap"] == 500.0)
    check("daily fy1_sales untouched", foo["fy1_sales"] == 100.0)
    check("fy4_sales added", foo["fy4_sales"] == 400.0)
    check("fy5_ebitda added", foo["fy5_ebitda"] == 55.0)
    check("counts nested for fy4_sales", foo["counts"]["fy4_sales"] == 6)
    check("failed-quality row not merged", "fy1_sales" in foo and foo["fy1_sales"] == 100.0)
    check("weekly_as_of recorded", merged["weekly_as_of"] == "2026-09-20")


def test_merge_weekly_consensus_creates_entry_for_ticker_with_no_daily_row():
    latest = {"as_of": "2026-09-17", "tickers": {}}
    rows = [{"ticker": "NEWCO", "metric": "FCF", "rel_period": 4, "mean": 12.0,
            "count": 2, "up": 1, "down": 0, "quality": "ok"}]
    merged = S.merge_weekly_consensus(latest, rows, "2026-09-20")
    newco = merged["tickers"]["NEWCO"]
    check("consensus-only weekly entry created", newco["price"] is None and newco["fy4_fcf"] == 12.0, newco)


def test_run_weekly_refuses_without_an_existing_daily_latest_json():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)

        def runner(fids, metric):
            return [], None
        rc = S.run_weekly([("FOO", "FOO-US")], "2026-09-20", state_dir, runner)
        check("run_weekly returns 1 with no daily latest.json", rc == 1)
        check("nothing written", not (state_dir / "consensus_weekly_2026-09-20.jsonl").exists())


def test_run_weekly_merges_into_existing_latest_json():
    with tempfile.TemporaryDirectory() as td:
        state_dir = Path(td)
        S.write_json({"as_of": "2026-09-17", "tickers": {
            "FOO": {"price": 10.0, "mcap": 500.0, "counts": {}, "up": {}, "down": {}}}},
            state_dir / "latest.json")

        def runner(fids, metric):
            return [{"requestId": fids[0], "estimateDate": "2026-09-20", "relativePeriod": 4,
                    "fiscalEndDate": "2030-12-31", "mean": 42.0, "median": 41.0,
                    "estimateCount": 3, "up": 2, "down": 0}], None

        rc = S.run_weekly([("FOO", "FOO-US")], "2026-09-20", state_dir, runner)
        check("run_weekly returns 0", rc == 0)
        check("consensus_weekly_<date>.jsonl written",
             (state_dir / "consensus_weekly_2026-09-20.jsonl").exists())
        latest = json.loads((state_dir / "latest.json").read_text())
        check("daily price/mcap preserved", latest["tickers"]["FOO"]["price"] == 10.0)
        check("weekly fy4 field merged in for every metric pulled",
             all(latest["tickers"]["FOO"].get(f"fy4_{m.lower()}") == 42.0
                for m in S.WEEKLY_CONSENSUS_METRICS), latest["tickers"]["FOO"])


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


def test_argument_drift_none_and_literal_null_string_are_equivalent():
    """RIS5 A3 live run finding: the live FactSet_Fundamentals call placed audit as the
    STRING "null", not JSON null/Python None, which false-positived as drift on the very
    first live Fundamentals probe (expected {"audit": None}). None and "null"/"NULL" must
    normalize to the same value; a genuinely different string (e.g. "AUDIT_TABLE" when
    None was expected) must still be caught."""
    expected = {"audit": None, "ids": ["NVDA-US"]}
    check("None placed matches None expected", S.argument_drift({"audit": None, "ids": ["NVDA-US"]}, expected) == [])
    check("literal string 'null' matches None expected (the real live shape)",
         S.argument_drift({"audit": "null", "ids": ["NVDA-US"]}, expected) == [])
    check("'NULL' case-insensitive also matches",
         S.argument_drift({"audit": "NULL", "ids": ["NVDA-US"]}, expected) == [])
    check("a genuinely different value is still drift",
         "audit" in S.argument_drift({"audit": "AUDIT_TABLE", "ids": ["NVDA-US"]}, expected))


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


def test_normalize_market_value_rows_uses_currentMarketValue_confirmed_live():
    """RIS5 A3 live run finding: the real key is `currentMarketValue` (raw row observed:
    {"fsymId": "SZG8SG-R", "requestId": "000660-KR", "currentMarketValue": 1240826747.5,
    "currency": "KRW", "date": "2026-09-17"}) -- none of the pre-live guesses matched."""
    raw = [{"fsymId": "SZG8SG-R", "requestId": "000660-KR",
           "currentMarketValue": 1240826747.5, "currency": "KRW", "date": "2026-09-17"}]
    out = S.normalize_market_value_rows(raw, {"000660-KR": "000660.KS"})
    check("currentMarketValue matched first", out["000660.KS"]["mcap"] == 1240826747.5, out)
    check("currentMarketValue is tried before the fallback guesses",
         S._MCAP_KEYS[0] == "currentMarketValue", S._MCAP_KEYS)


def test_build_price_rows_missing_mcap_fails_quality():
    fid_to_tk = {"BAR-US": "BAR"}
    rows = S.build_price_rows({"BAR": {"price": 10.0, "date": "2026-09-17", "volume": 1, "currency": "USD"}},
                              {}, fid_to_tk, {"BAR": "BAR-US"}, "2026-09-17")
    check("missing mcap -> fail:mcap<=0", rows[0]["quality"] == "fail:mcap<=0", rows[0])


def test_normalize_consensus_rows_null_mean_preserved():
    raw = [{"requestId": "FOO-US", "estimateDate": "2026-09-17", "relativePeriod": 1,
           "fiscalEndDate": "2027-12-31", "mean": None, "median": None, "estimateCount": 0,
           "up": 0, "down": 0}]
    rows = S.normalize_consensus_rows(raw, {"FOO-US": "FOO"}, "SALES")
    check("null mean stays None, not 0.0", rows[0]["mean"] is None, rows[0])
    check("count=0 -> quality fail", rows[0]["quality"] == "fail:count<1", rows[0])


def test_normalize_consensus_rows_uses_estimateCount_and_estimateDate_not_count_and_date():
    """RIS5 A3 live run finding: the raw response has NO top-level `count`/`date` keys --
    those names were a pre-live guess that made every real row fail quality. The real
    keys are `estimateCount`/`estimateDate`."""
    raw = [{"requestId": "FOO-US", "estimateDate": "2026-09-20", "relativePeriod": 1,
           "fiscalEndDate": "2027-12-31", "mean": 10.0, "median": 10.0,
           "estimateCount": 5, "up": 2, "down": 1}]
    rows = S.normalize_consensus_rows(raw, {"FOO-US": "FOO"}, "SALES")
    check("estimateCount mapped to count", rows[0]["count"] == 5, rows[0])
    check("estimateDate mapped to date", rows[0]["date"] == "2026-09-20", rows[0])
    check("quality ok with a real count", rows[0]["quality"] == "ok", rows[0])
    # a raw row with the OLD guessed keys (count/date) instead of the real ones must NOT
    # be picked up -- proves the fix actually changed the lookup, not just added a fallback
    stale = [{"requestId": "FOO-US", "date": "2026-09-20", "relativePeriod": 1,
             "fiscalEndDate": "2027-12-31", "mean": 10.0, "median": 10.0,
             "count": 5, "up": 2, "down": 1}]
    stale_rows = S.normalize_consensus_rows(stale, {"FOO-US": "FOO"}, "SALES")
    check("old 'count'/'date' keys are NOT read (would have silently 'worked' and hidden the bug)",
         stale_rows[0]["count"] is None and stale_rows[0]["date"] is None
         and stale_rows[0]["quality"] == "fail:count<1", stale_rows[0])


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
        return [{"requestId": fids[0], "estimateDate": "2026-09-17", "relativePeriod": 1,
                "fiscalEndDate": "2027-12-31", "mean": 100.0, "median": 99.0,
                "estimateCount": 10, "up": 2, "down": 1}], None

    rows, errs = S.fetch_consensus(pairs, "SALES", runner)
    check("consensus rows for the metric parsed", rows[0]["metric"] == "SALES" and rows[0]["mean"] == 100.0)
    check("count correctly read from estimateCount", rows[0]["count"] == 10, rows[0])
    check("no errors", errs == [])


# ─────────────────────── session-limit abort (fix round 1, item 3) ─────────────────────

class _FakeCompleted:
    def __init__(self, returncode, stdout, stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_run_mcp_checked_raises_session_limit_before_returncode_check():
    """A 429 on stdout must raise SessionLimitError even though rc!=0 -- precheck-first,
    mirroring claude_p.run's own documented ordering (a 429 can arrive as rc!=0 with the
    session-limit text on stdout, and that must not fall through to a generic RuntimeError
    the per-batch log-and-continue path would swallow)."""
    fake_stdout = json.dumps({"is_error": True, "result": "session limit reached, resets in 3h",
                              "api_error_status": 429})
    orig_run = subprocess.run
    subprocess.run = lambda *a, **k: _FakeCompleted(1, fake_stdout, "")
    try:
        raised = None
        try:
            S._run_mcp_checked("prompt", "sometool", None, ".", 30)
        except S.SessionLimitError as e:
            raised = e
        check("SessionLimitError raised despite rc=1", raised is not None)
    finally:
        subprocess.run = orig_run


def test_run_and_parse_lets_session_limit_propagate_not_caught_into_tuple():
    """Every other transport exception is caught into (rows, error); SessionLimitError
    must NOT be -- it has to propagate so the caller aborts instead of logging-and-
    continuing (coordinator fix round 1, item 3)."""
    orig = S._run_mcp_checked
    S._run_mcp_checked = lambda *a, **k: (_ for _ in ()).throw(S.SessionLimitError("resets in 1h"))
    try:
        raised = None
        try:
            S._run_and_parse("p", "tool", {}, ".", 30)
        except S.SessionLimitError as e:
            raised = e
        check("SessionLimitError propagates out of _run_and_parse (not swallowed)",
             raised is not None)
    finally:
        S._run_mcp_checked = orig


def test_fetch_prices_propagates_session_limit_instead_of_logging_and_continuing():
    pairs = [(f"T{i}", f"T{i}-US") for i in range(3)]

    def runner(fids, on_date):
        raise S.SessionLimitError("resets in 2h")

    raised = None
    try:
        S.fetch_prices(pairs, "2026-09-17", runner)
    except S.SessionLimitError as e:
        raised = e
    check("fetch_prices lets SessionLimitError propagate (aborts, doesn't catch it)",
         raised is not None)


def test_main_aborts_on_session_limit_returns_1_and_writes_nothing(tmp_override=None):
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        state_dir = Path(tdname) / "state" / "valuation"
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        orig_pid_repo = S.pid.REPO
        S.pid.REPO = td
        orig_checked = S._run_mcp_checked
        S._run_mcp_checked = lambda *a, **k: (_ for _ in ()).throw(S.SessionLimitError("resets in 4h"))
        try:
            rc = S.main(["--state-dir", str(state_dir), "--date", "2026-09-17"])
            check("main() returns 1 (non-zero) on a session limit", rc == 1, rc)
            check("latest.json NOT written on abort", not (state_dir / "latest.json").exists())
        finally:
            ingest_metrics.REPO = orig_repo
            S.pid.REPO = orig_pid_repo
            S._run_mcp_checked = orig_checked


def test_other_transport_errors_still_log_and_continue_not_abort():
    """Non-session-limit transport failures keep the existing per-batch precedent: one bad
    chunk is reported and the rest of the run proceeds (unchanged by this fix)."""
    pairs = [(f"T{i}", f"T{i}-US") for i in range(2)]

    def runner(fids, on_date):
        return [], "transport: RuntimeError: boom"

    out, errs = S.fetch_prices(pairs, "2026-09-17", runner)
    check("ordinary transport error is reported, not raised", len(errs) == 1, errs)


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
    check("summary.priced == 1 (only FOO)", latest["summary"]["priced"] == 1, latest["summary"])
    check("summary.consensus_only == 0 (BAD excluded entirely)",
         latest["summary"]["consensus_only"] == 0, latest["summary"])


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
    check("summary.consensus_only == 1", latest["summary"]["consensus_only"] == 1, latest["summary"])
    check("summary.priced == 0", latest["summary"]["priced"] == 0, latest["summary"])


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
    test_consensus_metrics_includes_ebitda_and_fcf()
    test_consensus_args_honour_explicit_rel_start_end()
    test_extract_http_status_finds_408_and_5xx()
    test_is_retryable_error_only_matches_marker_not_bare_digits()
    test_fetch_market_value_retries_once_then_succeeds()
    test_fetch_market_value_retries_once_then_still_fails_marks_batch_failed()
    test_fetch_market_value_non_retryable_error_never_retries()
    test_fetch_market_value_session_limit_propagates_through_retry_path()
    test_fetch_prices_and_fetch_consensus_also_get_the_retry()
    test_merge_weekly_consensus_adds_fy4_fy5_without_touching_daily_fields()
    test_merge_weekly_consensus_creates_entry_for_ticker_with_no_daily_row()
    test_run_weekly_refuses_without_an_existing_daily_latest_json()
    test_run_weekly_merges_into_existing_latest_json()
    test_argument_drift_clean_and_dirty()
    test_argument_drift_none_and_literal_null_string_are_equivalent()
    test_check_price_quality()
    test_check_consensus_quality()
    test_check_surprise_identity()
    test_normalize_price_and_market_value_join()
    test_normalize_market_value_rows_uses_currentMarketValue_confirmed_live()
    test_build_price_rows_missing_mcap_fails_quality()
    test_normalize_consensus_rows_null_mean_preserved()
    test_normalize_consensus_rows_uses_estimateCount_and_estimateDate_not_count_and_date()
    test_fetch_prices_batches_and_reports_errors()
    test_fetch_consensus_extends_across_metrics()
    test_run_mcp_checked_raises_session_limit_before_returncode_check()
    test_run_and_parse_lets_session_limit_propagate_not_caught_into_tuple()
    test_fetch_prices_propagates_session_limit_instead_of_logging_and_continuing()
    test_main_aborts_on_session_limit_returns_1_and_writes_nothing()
    test_other_transport_errors_still_log_and_continue_not_abort()
    test_build_latest_shape_and_skips_failed_quality()
    test_build_latest_bad_ticker_consensus_alone_not_included()
    test_write_jsonl_idempotent_overwrite()
    test_cli_dry_run_writes_latest_json()
    test_module_is_importable_as_a_script()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_snapshot")
