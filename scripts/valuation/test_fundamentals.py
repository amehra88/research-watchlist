"""Tests for scripts/valuation/fundamentals.py (RIS5 A3). No claude -p is exercised.
    python3 scripts/valuation/test_fundamentals.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fundamentals as F  # noqa: E402

FAILURES = []


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
    test_main_refuses_without_confirmed_metrics()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_fundamentals")
