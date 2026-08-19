"""
Integration test: store -> build -> render, on a synthetic 3-year history. No fetch, no LLM.

This is the test that would have caught the wiring mistakes unit tests cannot see:
  • the ledger is idempotent, and a later real value OVERWRITES an earlier null for the same
    (series, ticker, date) — today's flow arrives null at 05:30 and real the next morning,
  • the as-of date is derived from data that actually has values, not assumed to be T-1,
  • normalisation happens AFTER the window sum and against prior-period AUM,
  • a planted extreme actually reaches an alert, and a flat-flow ETF degrades instead of
    firing at infinity,
  • the whole report renders end to end.

Run:  python3 scripts/etfflows/test_build.py
"""
import math
import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import LONG_HORIZON, SHORT_HORIZON  # noqa: E402
from etfflows import build, render, store  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def trading_days(start: str, n: int) -> list[str]:
    d = date.fromisoformat(start)
    out = []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


UNIVERSE_YAML = """
meta: {version: 1, updated: "2026-08-19"}
pairs:
  - {name: "SPY vs IVV+VOO", lead: SPY, against: [IVV]}
tiers:
  trigger:
    baseline_years: 3
    sleeves:
      core_index: {label: Core, tickers: [SPY, IVV]}
      semis_software: {label: Semis, tickers: [SMH]}
      sectors: {label: Sectors, tickers: [XLRE]}
      factor: {label: Factor, tickers: [MTUM]}
  context:
    baseline_years: 1
    sleeves:
      synthetic_new: {label: Synthetic, tickers: [LYTE]}
overrides:
  LYTE: {synthetic: true, min_history_ok: false}
excluded: {}
"""


def seed(path, dates):
    """Build a plausible ledger.

    SMH gets a planted extreme on the final day; XLRE gets a perfectly flat flow history
    (the MAD-floor case); LYTE gets only a short tail (the no-baseline case).
    """
    aum = {"SPY": 600e9, "IVV": 500e9, "SMH": 20e9, "XLRE": 8e9, "MTUM": 25e9, "LYTE": 50e6}
    flows, prices, aums = [], [], []

    for t, base in aum.items():
        start_i = 0 if t != "LYTE" else len(dates) - 10
        for i, d in enumerate(dates):
            if i < start_i:
                continue
            if t == "XLRE":
                f = 1000.0                      # perfectly flat -> MAD floor must bind
            elif t == "SMH" and i == len(dates) - 1:
                f = base * 0.02                 # planted 200bp day: must alert
            else:
                f = base * 0.0002 * math.sin(i / 7.0)
            flows.append({"ticker": t, "date": d, "value": f})
            prices.append({"ticker": t, "date": d,
                           "value": 100.0 * (1.0 + 0.0004 * i)})
        # month-end AUM anchors
        for i, d in enumerate(dates):
            if i < start_i:
                continue
            nxt = dates[i + 1] if i + 1 < len(dates) else None
            if nxt is None or nxt[5:7] != d[5:7]:
                aums.append({"ticker": t, "date": d, "value": base,
                             "shares_outstanding": base / 100.0})

    store.append(path, flows, "flows")
    store.append(path, prices, "prices")
    store.append(path, aums, "aum")


def test_end_to_end():
    dates = trading_days("2023-01-02", 800)
    as_of_expected = dates[-1]

    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "etf_flows.jsonl")
        uni_path = os.path.join(d, "etf_universe.yaml")
        with open(uni_path, "w") as fh:
            fh.write(UNIVERSE_YAML)

        seed(ledger, dates)
        state = store.load(ledger)
        uni = build.load_universe(uni_path)

        check("universe flattens tiers",
              set(uni.tickers) == {"SPY", "IVV", "SMH", "XLRE", "MTUM", "LYTE"},
              f"got {uni.tickers}")
        check("LYTE is context + synthetic + no-history",
              uni.tier["LYTE"] == "context" and uni.synthetic("LYTE")
              and not uni.min_history_ok("LYTE"))

        as_of = store.latest_date(state, "flows")
        check("as-of derived from data with values", as_of == as_of_expected,
              f"got {as_of} want {as_of_expected}")

        report, new_trigger_state = build.build_report(
            state, uni, as_of, {}, "FEAR & GREED: 56 (greed)  |  1w -7  |  1m +19")

        # the planted extreme
        alert_tickers = [a.ticker for a in report["alerts"]]
        check("planted 200bp SMH day produces an alert", "SMH" in alert_tickers,
              f"alerts={[(a.ticker, a.horizon, round(a.z, 2)) for a in report['alerts']]}")

        # the flat-flow ETF
        xlre = next(r for r in report["rows"] if r["ticker"] == "XLRE")
        check("flat-flow ETF degrades instead of firing at infinity",
              xlre["degraded_short"] and xlre["z_short"] is None, f"got {xlre}")
        check("flat-flow ETF is not in the alert list", "XLRE" not in alert_tickers)

        # the no-baseline ETF
        check("insufficient-history ETF never alerts", "LYTE" not in alert_tickers)
        check("insufficient-history ETF is warned about",
              any("LYTE" in w for w in report["warnings"]), f"got {report['warnings']}")

        # structure
        check("every universe ticker with data has a row",
              {r["ticker"] for r in report["rows"]} >= {"SPY", "IVV", "SMH", "XLRE", "MTUM"},
              f"got {[r['ticker'] for r in report['rows']]}")
        check("trigger-tier rows sort first",
              report["rows"][0]["tier"] == "trigger")
        check("breadth measured over trigger tier only",
              report["breadth"][LONG_HORIZON]["measured"] <= 5,
              f"got {report['breadth'][LONG_HORIZON]}")
        check("pair spread computed", report["pairs"][0]["short"] is not None)
        check("factor rotation computed",
              any(f["ticker"] == "MTUM" for f in report["factor_rotation"]))

        # trigger state persisted for hysteresis
        check("trigger state returned for persistence", isinstance(new_trigger_state, dict)
              and any(k.startswith("SMH") for k in new_trigger_state),
              f"got {list(new_trigger_state)[:4]}")

        # renders
        main = render.render_main(report)
        table = render.render_table(report)
        check("main section renders", "ETF FLOWS & CROWDING" in main and len(main) > 200)
        check("table renders every row", all(t in table for t in ("SPY", "SMH", "XLRE")))
        check("note opens with ##", render.render_note(report).lstrip().startswith("## "))

        print("\n" + "=" * 86)
        print(main)
        print("=" * 86)


def test_ledger_is_idempotent_and_last_write_wins():
    """Today's flow arrives null at 05:30 and real the next morning. The number must win."""
    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "s.jsonl")
        store.append(ledger, [{"ticker": "XLK", "date": "2026-08-19", "value": None}], "flows")
        store.append(ledger, [{"ticker": "XLK", "date": "2026-08-19", "value": 42.0}], "flows")
        state = store.load(ledger)
        dates, values = store.series_for(state, "flows", "XLK")
        check("one row per (series,ticker,date)", dates == ["2026-08-19"], f"got {dates}")
        check("later real value overwrites the earlier null", values == [42.0], f"got {values}")


def test_latest_date_skips_null_only_days():
    """The 05:30 case: today exists as a row but has no value anywhere yet."""
    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "s.jsonl")
        store.append(ledger, [{"ticker": "XLK", "date": "2026-08-18", "value": 1.0},
                              {"ticker": "XLK", "date": "2026-08-19", "value": None}], "flows")
        state = store.load(ledger)
        check("as-of skips a null-only day", store.latest_date(state, "flows") == "2026-08-18",
              f"got {store.latest_date(state, 'flows')}")


def test_corrupt_line_is_survivable():
    with tempfile.TemporaryDirectory() as d:
        ledger = os.path.join(d, "s.jsonl")
        store.append(ledger, [{"ticker": "XLK", "date": "2026-08-18", "value": 1.0}], "flows")
        with open(ledger, "a") as fh:
            fh.write("{torn line\n")
        state = store.load(ledger)
        check("a torn trailing line does not lose history",
              store.series_for(state, "flows", "XLK")[1] == [1.0])


def test_missing_ticker_does_not_crash_build():
    with tempfile.TemporaryDirectory() as d:
        uni_path = os.path.join(d, "u.yaml")
        with open(uni_path, "w") as fh:
            fh.write(UNIVERSE_YAML)
        uni = build.load_universe(uni_path)
        report, _ = build.build_report({"flows": {}, "prices": {}, "aum": {}},
                                       uni, "2026-08-18", {})
        check("empty state builds an empty report rather than raising",
              report["rows"] == [] and report["alerts"] == [])
        check("every missing ticker is warned about", len(report["warnings"]) >= 6,
              f"got {report['warnings']}")
        check("empty report still renders", "ETF FLOWS" in render.render_main(report))


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        print(f"\n{fn.__name__}:")
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
        return 1
    print(f"All checks passed ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
