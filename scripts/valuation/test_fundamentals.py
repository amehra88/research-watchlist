"""Tests for scripts/valuation/fundamentals.py (RIS5 A3). No claude -p is exercised.
    python3 scripts/valuation/test_fundamentals.py
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
import ingest_metrics  # noqa: E402  (worktree copy first, same trick as snapshot.py)
import fundamentals as F  # noqa: E402
import valuation.snapshot as vs  # noqa: E402  (fundamentals.py's build_universe/pid live here)

FAILURES = []

_WATCHLIST_YAML = """
tier_1_bctk:
  - ticker: FOO
    themes: []
tier_2_active_candidates:
  - ticker: BAR
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


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def test_discover_metrics_prompt_shape():
    p = F.discover_metrics_prompt(["net debt", "gross margin"])
    check("prompt names the tool once", "FactSet_Metrics tool EXACTLY ONCE" in p)
    check("queries embedded", '"net debt"' in p and '"gross margin"' in p)
    check("data_products fundamentals only", '"fundamentals"' in p)


def test_fundamentals_prompt_requires_audit_null():
    p = F._fundamentals_prompt(["AAPL-US"], ["FF_NET_DEBT"], "QTR")
    check("audit explicitly null", "audit: null" in p)
    check("periodicity embedded", "periodicity: 'QTR'" in p)
    check("metrics embedded", '"FF_NET_DEBT"' in p)


def test_fundamentals_args_periodicity_default():
    a = F._fundamentals_args(["AAPL-US"], ["FF_NET_DEBT"], "QTR")
    check("audit key present and None", "audit" in a and a["audit"] is None, a)
    check("data_type fundamentals", a["data_type"] == "fundamentals")


def test_normalize_fundamentals_rows_missing_value_fails_quality():
    raw = [
        {"requestId": "AAPL-US", "metric": "FF_NET_DEBT", "value": -500.0,
        "fiscalPeriodEnd": "2026-06-30", "currency": "USD"},
        {"requestId": "AAPL-US", "metric": "FF_GROSS_MARGIN", "value": None,
        "fiscalPeriodEnd": "2026-06-30", "currency": "USD"},
    ]
    fid_to_tk = {"AAPL-US": "AAPL"}
    code_to_label = {"FF_NET_DEBT": "net_debt", "FF_GROSS_MARGIN": "gross_margin"}
    rows = F.normalize_fundamentals_rows(raw, fid_to_tk, code_to_label, "QTR")
    check("2 rows produced", len(rows) == 2)
    ok_row = next(r for r in rows if r["metric"] == "net_debt")
    fail_row = next(r for r in rows if r["metric"] == "gross_margin")
    check("value passes through with label", ok_row["value"] == -500.0 and ok_row["quality"] == "ok", ok_row)
    check("missing value -> fail:missing", fail_row["quality"] == "fail:missing", fail_row)


def test_periodicity_is_ltm_and_sales_is_pulled():
    """RIS5 A3 fix 4 (coordinator review): the understated-FCF-margin incident was
    QTR fcf vs ANN sales -- fixed by pulling both at LTM in the same call."""
    check("default periodicity is LTM, not QTR", F.FUNDAMENTALS_PERIODICITY == "LTM", F.FUNDAMENTALS_PERIODICITY)
    check("sales is in FUNDAMENTALS_METRICS", F.FUNDAMENTALS_METRICS.get("sales") == "FF_SALES", F.FUNDAMENTALS_METRICS)
    check("fcf is in FUNDAMENTALS_METRICS", F.FUNDAMENTALS_METRICS.get("fcf") == "FF_FREE_CF", F.FUNDAMENTALS_METRICS)


def test_balance_sheet_and_flow_metrics_use_different_periodicities():
    """RIS5 A3 fix 4 round 2: a live full-universe LTM attempt against net_debt/
    total_debt/cash returned 0/178 ok for all three (balance-sheet items have no
    trailing-12-month figure) -- they must stay on QTR while the flow metrics move to
    LTM. This is a hard split, not a preference: mixing them into one LTM call is the
    exact regression this test guards against."""
    check("net_debt/total_debt/cash are balance-sheet metrics",
         set(F.BALANCE_SHEET_METRICS) == {"net_debt", "total_debt", "cash"}, F.BALANCE_SHEET_METRICS)
    check("gross_margin/operating_margin/fcf/sales are flow metrics",
         set(F.FLOW_METRICS) == {"gross_margin", "operating_margin", "fcf", "sales"}, F.FLOW_METRICS)
    check("balance-sheet periodicity is QTR (unchanged)", F.BALANCE_SHEET_PERIODICITY == "QTR")
    check("flow periodicity is LTM (fix 4)", F.FLOW_PERIODICITY == "LTM")
    check("no metric label appears in both groups",
         not (set(F.BALANCE_SHEET_METRICS) & set(F.FLOW_METRICS)))
    check("FUNDAMENTALS_METRICS is the union of both groups",
         F.FUNDAMENTALS_METRICS == {**F.BALANCE_SHEET_METRICS, **F.FLOW_METRICS}, F.FUNDAMENTALS_METRICS)


def test_compute_fcf_margin_rows_uses_the_same_ticker_same_period_sales():
    """The core fix 4 property: fcf_margin must come from THIS ticker's fcf and sales
    rows, matched on (ticker, fiscal_end) -- never a different ticker's or a
    different-period sales figure."""
    rows = [
        {"ticker": "NVDA", "fsym": "NVDA-US", "date": "2026-09-17", "metric": "fcf",
        "value": 72000.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
        {"ticker": "NVDA", "fsym": "NVDA-US", "date": "2026-09-17", "metric": "sales",
        "value": 200000.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
        # a decoy: a DIFFERENT ticker's sales must never leak into NVDA's margin
        {"ticker": "AVGO", "fsym": "AVGO-US", "date": "2026-09-17", "metric": "sales",
        "value": 999999.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
    ]
    out = F.compute_fcf_margin_rows(rows)
    nvda = next(r for r in out if r["ticker"] == "NVDA")
    check("fcf_margin = fcf/sales*100 using NVDA's OWN sales row",
         abs(nvda["value"] - 36.0) < 1e-9, nvda)
    check("metric labeled fcf_margin", nvda["metric"] == "fcf_margin")
    check("quality ok", nvda["quality"] == "ok", nvda)
    check("fiscal_end carried through", nvda["fiscal_end"] == "2026-07-31", nvda)
    check("only ONE fcf_margin row per ticker with both legs", len(out) == 1, out)


def test_compute_fcf_margin_rows_period_mismatch_fails_not_silently_wrong():
    """RIS5 A3 fix 4's whole point: a quarter-vs-annual (or any fiscal_end) mismatch
    must be CAUGHT, not silently divided -- this is what produced the ~4x understated
    margins in the first place."""
    rows = [
        {"ticker": "AVGO", "fsym": "AVGO-US", "date": "2026-09-17", "metric": "fcf",
        "value": 10562.0, "periodicity": "QTR", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
        {"ticker": "AVGO", "fsym": "AVGO-US", "date": "2026-09-17", "metric": "sales",
        "value": 59419.0, "periodicity": "ANN", "fiscal_end": "2025-10-31",
        "currency": "USD", "quality": "ok"},
    ]
    out = F.compute_fcf_margin_rows(rows)
    check("one row produced", len(out) == 1, out)
    check("period mismatch caught, not silently computed",
         out[0]["quality"] == "fail:period_mismatch", out[0])
    check("value is None on a period mismatch, never a wrong number", out[0]["value"] is None, out[0])


def test_compute_fcf_margin_rows_missing_leg_produces_no_row():
    rows = [
        {"ticker": "SOLO", "fsym": "SOLO-US", "date": "2026-09-17", "metric": "fcf",
        "value": 100.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
    ]
    out = F.compute_fcf_margin_rows(rows)
    check("no fcf_margin row when sales never came back for this ticker", out == [], out)


def test_compute_fcf_margin_rows_nonpositive_sales_fails():
    rows = [
        {"ticker": "ZERO", "fsym": "ZERO-US", "date": "2026-09-17", "metric": "fcf",
        "value": 100.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
        {"ticker": "ZERO", "fsym": "ZERO-US", "date": "2026-09-17", "metric": "sales",
        "value": 0.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
    ]
    out = F.compute_fcf_margin_rows(rows)
    check("sales<=0 fails cleanly", out[0]["quality"] == "fail:sales<=0", out[0])


def test_compute_fcf_margin_rows_propagates_missing_quality_from_either_leg():
    rows = [
        {"ticker": "BAD", "fsym": "BAD-US", "date": "2026-09-17", "metric": "fcf",
        "value": None, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "fail:missing"},
        {"ticker": "BAD", "fsym": "BAD-US", "date": "2026-09-17", "metric": "sales",
        "value": 100.0, "periodicity": "LTM", "fiscal_end": "2026-07-31",
        "currency": "USD", "quality": "ok"},
    ]
    out = F.compute_fcf_margin_rows(rows)
    check("a fail:missing leg propagates -- never derives a margin from a missing fcf",
         out[0]["quality"] == "fail:missing", out[0])


def test_normalize_fundamentals_rows_uses_fiscalEndDate_not_fiscalPeriodEnd():
    """RIS5 A3 fix 4: found while testing compute_fcf_margin_rows' period-match logic --
    the real raw field is `fiscalEndDate` (confirmed live), not the guessed
    `fiscalPeriodEnd`, which doesn't exist on any real row. Before this fix, fiscal_end
    was silently None on every fundamentals row ever written."""
    raw = [{"requestId": "NVDA-US", "metric": "FF_FREE_CF", "value": 120230.0,
           "fiscalEndDate": "2026-07-31", "reportDate": "2026-07-26", "currency": "USD"}]
    rows = F.normalize_fundamentals_rows(raw, {"NVDA-US": "NVDA"}, {"FF_FREE_CF": "fcf"}, "LTM")
    check("fiscal_end reads fiscalEndDate", rows[0]["fiscal_end"] == "2026-07-31", rows[0])
    check("date reads reportDate", rows[0]["date"] == "2026-07-26", rows[0])

    # old guessed key alone (no fiscalEndDate) -- fallback still resolves, just from a
    # field that doesn't actually exist on real rows; proves the fallback chain, not a
    # claim that FactSet ever sends fiscalPeriodEnd.
    raw_fallback = [{"requestId": "NVDA-US", "metric": "FF_FREE_CF", "value": 1.0,
                    "fiscalPeriodEnd": "2026-01-01", "currency": "USD"}]
    rows2 = F.normalize_fundamentals_rows(raw_fallback, {"NVDA-US": "NVDA"}, {"FF_FREE_CF": "fcf"}, "LTM")
    check("falls back to fiscalPeriodEnd if fiscalEndDate is absent", rows2[0]["fiscal_end"] == "2026-01-01", rows2[0])


def test_compute_fcf_margin_rows_catches_a_real_period_mismatch_with_real_field_names():
    """End-to-end fix 4 regression: real raw-row shapes (fiscalEndDate, not the old
    guessed key) through normalize_fundamentals_rows -> compute_fcf_margin_rows must
    catch a genuine period disagreement, not silently pass on a None==None fluke."""
    raw = [
        {"requestId": "AVGO-US", "metric": "FF_FREE_CF", "value": 10562.0,
        "fiscalEndDate": "2026-07-31", "reportDate": "2026-07-26", "currency": "USD"},
        {"requestId": "AVGO-US", "metric": "FF_SALES", "value": 89104.0,
        "fiscalEndDate": "2025-10-31", "reportDate": "2025-11-01", "currency": "USD"},
    ]
    code_to_label = {"FF_FREE_CF": "fcf", "FF_SALES": "sales"}
    norm = F.normalize_fundamentals_rows(raw, {"AVGO-US": "AVGO"}, code_to_label, "LTM")
    margins = F.compute_fcf_margin_rows(norm)
    check("real fiscal_end values differ and ARE caught (not None==None)",
         margins[0]["quality"] == "fail:period_mismatch", margins[0])


# ─────────────────────── fetch_fundamentals_group (RIS5 A3 fix 5) ──────────────────

def test_fetch_fundamentals_group_batches_and_normalizes():
    pairs = [(f"T{i}", f"T{i}-US") for i in range(3)]

    def runner(fids, codes, periodicity):
        return [{"requestId": f, "metric": "FF_NET_DEBT", "value": 10.0,
                "fiscalEndDate": "2026-07-31", "reportDate": "2026-07-26",
                "currency": "USD"} for f in fids], None

    rows, errs = F.fetch_fundamentals_group(pairs, ["FF_NET_DEBT"], {"FF_NET_DEBT": "net_debt"},
                                            "QTR", runner)
    check("3 rows, one per ticker", len(rows) == 3, rows)
    check("labeled net_debt", all(r["metric"] == "net_debt" for r in rows), rows)
    check("no errors", errs == [])


def test_fetch_fundamentals_group_retries_408_once_then_succeeds():
    calls = []

    def runner(fids, codes, periodicity):
        calls.append(1)
        if len(calls) == 1:
            return [], "tool_result unusable (http_status=408): Client error '408 Request Timeout'"
        return [{"requestId": fids[0], "metric": "FF_SALES", "value": 5.0,
                "fiscalEndDate": "2026-07-31", "currency": "USD"}], None

    sleeps = []
    rows, errs = F.fetch_fundamentals_group([("FOO", "FOO-US")], ["FF_SALES"], {"FF_SALES": "sales"},
                                            "LTM", runner, retry_wait=20, sleep=sleeps.append)
    check("exactly one retry (2 calls total)", len(calls) == 2, calls)
    check("slept once", sleeps == [20], sleeps)
    check("succeeded on retry", len(rows) == 1 and rows[0]["value"] == 5.0, rows)
    check("no error recorded", errs == [])


def test_fetch_fundamentals_group_non_retryable_error_marks_batch_failed():
    def runner(fids, codes, periodicity):
        return [], "argument drift in ids: placed {...}"

    rows, errs = F.fetch_fundamentals_group([("FOO", "FOO-US")], ["FF_SALES"], {"FF_SALES": "sales"},
                                            "LTM", runner, retry_wait=0, sleep=lambda s: None)
    check("batch marked failed, no retry for non-retryable error", len(errs) == 1, errs)
    check("no rows", rows == [])


def test_fetch_fundamentals_group_session_limit_propagates():
    def runner(fids, codes, periodicity):
        raise vs.SessionLimitError("429 hit")

    threw = False
    try:
        F.fetch_fundamentals_group([("FOO", "FOO-US")], ["FF_SALES"], {"FF_SALES": "sales"},
                                   "LTM", runner, retry_wait=0, sleep=lambda s: None)
    except vs.SessionLimitError:
        threw = True
    check("SessionLimitError propagates uncaught", threw)


# ─────────────────────── main() CLI orchestration (RIS5 A3 fix 5) ──────────────────

def test_dry_run_prints_plan_and_never_calls_the_runner():
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        orig_pid_repo = vs.pid.REPO
        vs.pid.REPO = td

        def boom():
            raise AssertionError("dry-run must never build a real runner")
        orig_make_runner = F.make_fundamentals_runner
        F.make_fundamentals_runner = boom
        try:
            rc = F.main(["--dry-run", "--date", "2026-09-17"])
            check("dry-run returns 0", rc == 0, rc)
        finally:
            ingest_metrics.REPO = orig_repo
            vs.pid.REPO = orig_pid_repo
            F.make_fundamentals_runner = orig_make_runner


def _fake_fundamentals_runner_factory():
    """One row per (id, code) -- enough for normalize_fundamentals_rows +
    compute_fcf_margin_rows to produce a real, non-trivial fundamentals file."""
    def make_runner():
        def run(fids, codes, periodicity):
            rows = []
            for fid in fids:
                for code in codes:
                    value = 200.0 if code == "FF_SALES" else 40.0
                    rows.append({"requestId": fid, "metric": code, "value": value,
                                "fiscalEndDate": "2026-07-31", "reportDate": "2026-07-26",
                                "currency": "USD"})
            return rows, None
        return run
    return make_runner


def test_main_full_pull_writes_both_groups_plus_derived_margin_idempotently():
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        state_dir = Path(tdname) / "state" / "valuation"
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        orig_pid_repo = vs.pid.REPO
        vs.pid.REPO = td
        orig_make_runner = F.make_fundamentals_runner
        F.make_fundamentals_runner = _fake_fundamentals_runner_factory()
        try:
            rc = F.main(["--state-dir", str(state_dir), "--date", "2026-09-17"])
            check("main() returns 0", rc == 0, rc)
            out_path = state_dir / "fundamentals_2026-09-17.jsonl"
            check("output file written", out_path.exists())
            rows = [json.loads(l) for l in out_path.read_text().splitlines()]
            metrics_seen = {r["metric"] for r in rows}
            check("balance-sheet metrics present",
                 {"net_debt", "total_debt", "cash"} <= metrics_seen, metrics_seen)
            check("flow metrics present",
                 {"gross_margin", "operating_margin", "fcf", "sales"} <= metrics_seen, metrics_seen)
            check("derived fcf_margin present", "fcf_margin" in metrics_seen, metrics_seen)
            margin_rows = [r for r in rows if r["metric"] == "fcf_margin"]
            check("fcf_margin = 40/200*100 = 20.0 for each ticker",
                 all(abs(r["value"] - 20.0) < 1e-9 for r in margin_rows), margin_rows)
            check("periodicities correct",
                 all(r["periodicity"] == "QTR" for r in rows if r["metric"] in ("net_debt", "total_debt", "cash"))
                 and all(r["periodicity"] == "LTM" for r in rows if r["metric"] in ("gross_margin", "fcf", "sales")))

            first_text = out_path.read_text()
            rc2 = F.main(["--state-dir", str(state_dir), "--date", "2026-09-17"])
            second_text = out_path.read_text()
            check("re-run returns 0", rc2 == 0)
            check("idempotent re-run produces byte-identical output", first_text == second_text)
        finally:
            ingest_metrics.REPO = orig_repo
            vs.pid.REPO = orig_pid_repo
            F.make_fundamentals_runner = orig_make_runner


def test_main_out_flag_overrides_state_dir_naming():
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        out_file = Path(tdname) / "custom" / "wherever.jsonl"
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        orig_pid_repo = vs.pid.REPO
        vs.pid.REPO = td
        orig_make_runner = F.make_fundamentals_runner
        F.make_fundamentals_runner = _fake_fundamentals_runner_factory()
        try:
            rc = F.main(["--out", str(out_file), "--date", "2026-09-17"])
            check("main() returns 0", rc == 0, rc)
            check("--out path used verbatim, not state-dir/date naming", out_file.exists())
        finally:
            ingest_metrics.REPO = orig_repo
            vs.pid.REPO = orig_pid_repo
            F.make_fundamentals_runner = orig_make_runner


def test_main_aborts_on_session_limit_writes_nothing():
    with tempfile.TemporaryDirectory() as tdname:
        td = _fixture_repo(Path(tdname))
        state_dir = Path(tdname) / "state" / "valuation"
        orig_repo = ingest_metrics.REPO
        ingest_metrics.REPO = td
        orig_pid_repo = vs.pid.REPO
        vs.pid.REPO = td

        def make_runner():
            def run(fids, codes, periodicity):
                raise vs.SessionLimitError("resets in 4h")
            return run
        orig_make_runner = F.make_fundamentals_runner
        F.make_fundamentals_runner = make_runner
        try:
            rc = F.main(["--state-dir", str(state_dir), "--date", "2026-09-17"])
            check("main() returns 1 on session limit", rc == 1, rc)
            check("nothing written", not (state_dir / "fundamentals_2026-09-17.jsonl").exists())
        finally:
            ingest_metrics.REPO = orig_repo
            vs.pid.REPO = orig_pid_repo
            F.make_fundamentals_runner = orig_make_runner


def test_module_is_importable_as_a_script():
    """Sanity: the module runs standalone (python3 scripts/valuation/fundamentals.py
    --help) without import errors, mirroring how the cron will actually invoke it."""
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[0] / "fundamentals.py"),
                       "--help"], capture_output=True, text=True, timeout=30)
    check("fundamentals.py --help exits 0", r.returncode == 0, r.stderr[-300:])


def test_main_refuses_without_confirmed_metrics():
    orig = dict(F.FUNDAMENTALS_METRICS)
    F.FUNDAMENTALS_METRICS.clear()
    try:
        rc = F.main([])
    finally:
        F.FUNDAMENTALS_METRICS.update(orig)
    check("main() exits 1 when no metrics confirmed (never guesses FF_ codes)", rc == 1, rc)


if __name__ == "__main__":
    test_discover_metrics_prompt_shape()
    test_fundamentals_prompt_requires_audit_null()
    test_fundamentals_args_periodicity_default()
    test_normalize_fundamentals_rows_missing_value_fails_quality()
    test_periodicity_is_ltm_and_sales_is_pulled()
    test_balance_sheet_and_flow_metrics_use_different_periodicities()
    test_compute_fcf_margin_rows_uses_the_same_ticker_same_period_sales()
    test_compute_fcf_margin_rows_period_mismatch_fails_not_silently_wrong()
    test_compute_fcf_margin_rows_missing_leg_produces_no_row()
    test_compute_fcf_margin_rows_nonpositive_sales_fails()
    test_compute_fcf_margin_rows_propagates_missing_quality_from_either_leg()
    test_normalize_fundamentals_rows_uses_fiscalEndDate_not_fiscalPeriodEnd()
    test_compute_fcf_margin_rows_catches_a_real_period_mismatch_with_real_field_names()
    test_fetch_fundamentals_group_batches_and_normalizes()
    test_fetch_fundamentals_group_retries_408_once_then_succeeds()
    test_fetch_fundamentals_group_non_retryable_error_marks_batch_failed()
    test_fetch_fundamentals_group_session_limit_propagates()
    test_dry_run_prints_plan_and_never_calls_the_runner()
    test_main_full_pull_writes_both_groups_plus_derived_margin_idempotently()
    test_main_out_flag_overrides_state_dir_naming()
    test_main_aborts_on_session_limit_writes_nothing()
    test_module_is_importable_as_a_script()
    test_main_refuses_without_confirmed_metrics()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_fundamentals")
