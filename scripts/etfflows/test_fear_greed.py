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
    print(f"       {line}")
    check("line leads with the score and rating", line.startswith("FEAR & GREED: 56 (greed)"),
          f"got {line!r}")
    check("1w delta shown as a signed change", "1w -7" in line, f"got {line!r}")
    check("1m delta shown as a signed change", "1m +19" in line, f"got {line!r}")
    check("single line", "\n" not in line)


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
