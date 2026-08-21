"""
Tests for fear_greed.py — offline. The live endpoint is exercised by --selftest, not here.

What these protect:
  • a CNN outage degrades to the cached value WITH its age, and never raises into the digest,
  • a missing/garbled payload is an error rather than a confident fake 0.0 reading,
  • the header block that turns a 418 into a 200 is still present.

No pytest in this env — run directly:  python3 scripts/etfflows/test_fear_greed.py
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import FEAR_GREED_MAX_AGE_HOURS  # noqa: E402
from etfflows import fear_greed as fg  # noqa: E402

FAILURES = []
NOW = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)

# The real payload shape, captured live 2026-08-19.
LIVE = {"fear_and_greed": {
    "score": 56.3428571428571, "rating": "greed",
    "timestamp": "2026-08-19T21:42:49+00:00", "previous_close": 54.4,
    "previous_1_week": 62.9428571428571, "previous_1_month": 37.2285714285714,
    "previous_1_year": 59.88571428571429}}


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def test_parses_live_shape():
    r = fg.parse(LIVE, now=NOW)
    check("score parsed", abs(r.score - 56.34) < 0.01, f"got {r.score}")
    check("rating parsed", r.rating == "greed", f"got {r.rating}")
    check("1w history parsed", abs(r.week_ago - 62.94) < 0.01, f"got {r.week_ago}")
    check("1m history parsed", abs(r.month_ago - 37.23) < 0.01, f"got {r.month_ago}")


def test_missing_block_raises():
    for bad in ({}, {"fear_and_greed": None}, {"fear_and_greed": {"score": None}}):
        try:
            fg.parse(bad, now=NOW)
            check("missing block raises rather than faking a reading", False, f"for {bad}")
            return
        except ValueError:
            pass
    check("missing block raises rather than faking a reading", True)


def test_get_degrades_to_cache_on_failure():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fg.json")
        # seed a good cache one hour old
        seeded = fg.parse(LIVE, now=NOW - timedelta(hours=1))
        fg.save_cache(path, seeded)

        def boom():
            raise RuntimeError("HTTP 418")

        r, status = fg.get(path, fetcher=boom, now=NOW)
        check("failure does not raise", True)
        check("serves the cached value", r is not None and abs(r.score - 56.34) < 0.01)
        check("status is 'cached'", status == "cached", f"got {status}")


def test_get_marks_stale_cache():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fg.json")
        old = fg.parse(LIVE, now=NOW - timedelta(hours=FEAR_GREED_MAX_AGE_HOURS + 5))
        fg.save_cache(path, old)

        def boom():
            raise RuntimeError("down")

        r, status = fg.get(path, fetcher=boom, now=NOW)
        check("very old cache is flagged stale", status == "stale", f"got {status}")
        line = fg.render_line(r, status, now=NOW)
        check("stale line says CACHED and gives an age", "CACHED" in line and "h old" in line,
              f"got {line!r}")


def test_get_with_no_cache_returns_none():
    with tempfile.TemporaryDirectory() as d:
        def boom():
            raise RuntimeError("down")
        r, status = fg.get(os.path.join(d, "missing.json"), fetcher=boom, now=NOW)
        check("no fetch + no cache -> ('none')", r is None and status == "none",
              f"got {r}, {status}")
        check("line degrades to an explicit 'unavailable'",
              "unavailable" in fg.render_line(r, status), fg.render_line(r, status))


def test_live_fetch_writes_cache():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fg.json")
        r, status = fg.get(path, fetcher=lambda: LIVE, now=NOW)
        check("status is live", status == "live", f"got {status}")
        check("cache file written", os.path.exists(path))
        check("cache round-trips", fg.load_cache(path).score == r.score)


def test_corrupt_cache_is_survivable():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fg.json")
        with open(path, "w") as fh:
            fh.write("{not json")
        check("corrupt cache loads as None", fg.load_cache(path) is None)

        def boom():
            raise RuntimeError("down")
        r, status = fg.get(path, fetcher=boom, now=NOW)
        check("corrupt cache + failed fetch does not raise", status == "none", f"got {status}")


def test_render_line_shape():
    r = fg.parse(LIVE, now=NOW)
    line = fg.render_line(r, "live", now=NOW)
    print("\n" + line)
    check("header is labelled market risk", line.startswith("MARKET RISK"), f"got {line!r}")
    check("fear & greed score present", "Fear & Greed" in line and "56" in line)
    check("1w delta shown as a signed change", "1w -7" in line, f"got {line!r}")
    check("1m delta shown as a signed change", "1m +19" in line, f"got {line!r}")


# ── VIX ───────────────────────────────────────────────────────────────────────

def test_vix_parsed_from_the_same_payload():
    """VIX rides along in the CNN response, so it costs no extra fetch."""
    payload = dict(LIVE)
    payload["market_volatility_vix"] = {"data": [
        {"x": 1, "y": 20.0}, {"x": 2, "y": 18.0}, {"x": 3, "y": 14.89}]}
    r = fg.parse(payload, now=NOW)
    check("level is the LATEST point", r.vix_level == 14.89, f"got {r.vix_level}")
    check("percentile computed against its own history",
          r.vix_percentile is not None and r.vix_percentile < 50, f"got {r.vix_percentile}")
    check("history length recorded", r.vix_history_days == 3)


def test_vix_bands_are_absolute_levels():
    """A percentile alone is not enough: 'high for this calm year' != 'high'."""
    for level, want in ((9.5, "very low"), (14.9, "low"), (18.0, "normal"),
                        (22.0, "elevated"), (27.0, "high"), (45.0, "stress")):
        if fg.vix_band(level) != want:
            check(f"VIX {level} reads '{want}'", False, f"got {fg.vix_band(level)}")
            return
    check("VIX bands map levels to plain words", True)
    check("unknown level is 'unknown'", fg.vix_band(None) == "unknown")


def test_vix_line_carries_both_kinds_of_context():
    payload = dict(LIVE)
    payload["market_volatility_vix"] = {"data": [{"x": i, "y": 20.0} for i in range(50)]
                                        + [{"x": 99, "y": 14.89}]}
    line = fg.render_line(fg.parse(payload, now=NOW), "live", now=NOW)
    check("absolute level shown", "14.9" in line, f"got:\n{line}")
    check("band word shown", "low" in line, f"got:\n{line}")
    check("percentile-vs-own-history shown", "pctile of the past year" in line, f"got:\n{line}")
    check("scale legend shown so no number needs memorising",
          "under 12 very low" in line and "over 30 stress" in line, f"got:\n{line}")


def test_missing_vix_block_degrades():
    """No VIX must not take down the header."""
    r = fg.parse(LIVE, now=NOW)          # LIVE has no market_volatility_vix
    check("absent VIX parses as None", r.vix_level is None)
    line = fg.render_line(r, "live", now=NOW)
    check("header still renders without VIX", "Fear & Greed" in line)
    check("no VIX row is emitted", "VIX" not in line, f"got:\n{line}")


def test_old_cache_without_vix_still_loads():
    """Cache files written before VIX existed must not break on load."""
    import json as _json
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fg.json")
        old = fg.parse(LIVE, now=NOW).as_dict()
        for k in ("vix_level", "vix_percentile", "vix_history_days"):
            old.pop(k, None)
        with open(path, "w") as fh:
            _json.dump(old, fh)
        r = fg.load_cache(path)
        check("pre-VIX cache loads", r is not None and r.vix_level is None, f"got {r}")


def test_headers_still_include_the_418_workaround():
    """These exact headers are what make the droplet's request succeed."""
    for h in ("Referer", "Origin", "sec-fetch-site"):
        if h not in fg._HEADERS:
            check(f"header {h} present", False)
            return
    check("418-workaround headers present (Referer/Origin/sec-fetch-site)", True)
    check("Referer points at the fear-and-greed page",
          "fear-and-greed" in fg._HEADERS["Referer"])


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
