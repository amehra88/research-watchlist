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
    test_main_refuses_without_confirmed_metrics()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("OK test_fundamentals")
