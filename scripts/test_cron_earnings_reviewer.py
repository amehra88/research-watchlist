#!/usr/bin/env python3
"""Tests for the earnings-reviewer cron wrapper's calendar query.

Context (2026-09-07): the channel silently produced nothing on 08-30, 09-06 and
09-07. Every one of those runs failed with rc=124 — the calendar query exceeded
its 180s timeout, so `query_calendar` returned None, which aborts the whole run
before a single ticker is processed.

Measured latency on a day with NO reporting tickers: 62s, 95s, 100s, 118s —
already up to 65% of the old 180s budget for the cheapest possible case. The
query gets strictly more expensive as tickers actually report (more MCP calls),
which is why the timeouts cluster on active days. The ceiling had no margin.

These tests pin the two properties that fix it: a timeout with real headroom, and
one retry so a single slow call cannot zero out the day's run.

  python3 scripts/test_cron_earnings_reviewer.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cron_earnings_reviewer as cer  # noqa: E402

cer.log_write = lambda *a, **k: None  # silence log writes during tests


def _patch(fake):
    cer.run_claude = fake


def test_timeout_has_headroom():
    assert cer.CALENDAR_TIMEOUT_S >= 480, (
        f"calendar timeout {cer.CALENDAR_TIMEOUT_S}s must clear the observed 118s "
        f"empty-day worst case by a wide margin — a busy day costs strictly more")
    print(f"  ✓ calendar timeout {cer.CALENDAR_TIMEOUT_S}s has headroom over 118s observed")


def test_retries_once_after_timeout():
    calls = []

    def fake(prompt, timeout_seconds=None, model=None):
        calls.append(timeout_seconds)
        if len(calls) == 1:
            return 124, "", "TIMEOUT after 600s: "
        return 0, '["NVDA", "AMD"]', ""

    _patch(fake)
    got = cer.query_calendar(["NVDA", "AMD"])
    assert got == ["NVDA", "AMD"], got
    assert len(calls) == 2, f"expected exactly one retry, got {len(calls)} calls"
    print("  ✓ a single slow calendar call retries instead of zeroing the run")


def test_empty_result_is_not_a_failure():
    calls = []

    def fake(prompt, timeout_seconds=None, model=None):
        calls.append(1)
        return 0, "[]", ""

    _patch(fake)
    got = cer.query_calendar(["NVDA"])
    assert got == [], got
    assert len(calls) == 1, "an empty calendar is a VALID answer; must not retry"
    print("  ✓ empty calendar (no earnings that day) is accepted, not retried")


def test_persistent_failure_still_aborts():
    calls = []

    def fake(prompt, timeout_seconds=None, model=None):
        calls.append(1)
        return 124, "", "TIMEOUT after 600s: "

    _patch(fake)
    got = cer.query_calendar(["NVDA"])
    assert got is None, got
    assert len(calls) == 2, f"should attempt exactly twice then give up, got {len(calls)}"
    print("  ✓ persistent failure still aborts — retry adds resilience, not blindness")


def test_write_context_without_thesis():
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    cer.CONTEXT_DIR = tmp
    p = cer.write_context("ZZZZ")            # no _thesis.md, no metrics rows
    text = p.read_text()
    assert "No thesis file" in text and "ZZZZ" in text
    assert "Guidance track record" in text
    print("  ✓ context pre-stage handles a T3 name with no thesis file")


def test_write_context_with_thesis_carries_assumptions():
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    cer.CONTEXT_DIR = tmp
    if not (cer.REPO_ROOT / "notes" / "COHR" / "_thesis.md").exists():
        print("  - COHR _thesis.md absent; skipped"); return
    text = cer.write_context("COHR").read_text()
    assert "chinese_laser_capability" in text and "```yaml" in text
    print("  ✓ context pre-stage carries the thesis frontmatter")


def test_prompt_mentions_context():
    assert "state/thesis/context/NVDA.md" in cer.build_prompt("NVDA")
    print("  ✓ dispatch prompt points the agent at its context file")


def test_non_us_symbols_do_not_abort_the_run():
    """2026-07-29/31 and 09-10: one dotted or digit-bearing symbol (UMG.AS, 2308.TW,
    000660.KS) made the whole array unparseable, so AAPL/AMZN/KLAC/NXPI... were never
    reviewed. The watchlist filter downstream is what drops foreign names, not the regex."""
    _patch(lambda prompt, timeout_seconds=None, model=None:
           (0, '["SONY", "AAPL", "MPWR", "UMG.AS", "2308.TW", "000660.KS"]\n', ""))
    got = cer.query_calendar(["AAPL", "MPWR"])
    assert got == ["SONY", "AAPL", "MPWR", "UMG.AS", "2308.TW", "000660.KS"], got
    print("  ✓ dotted / digit-bearing symbols no longer abort the calendar parse")


def test_array_inside_prose_still_parses():
    """2026-07-30: the cheap model prefixed the array with its reasoning."""
    _patch(lambda prompt, timeout_seconds=None, model=None:
           (0, 'Filtering into the window (excluding SK hynix, 000660.KS):\n\n["MSFT", "META", "BRK.B"]', ""))
    got = cer.query_calendar(["MSFT", "META"])
    assert got == ["MSFT", "META", "BRK.B"], got
    print("  ✓ a prose-wrapped array is still found")


if __name__ == "__main__":
    orig = cer.run_claude
    try:
        test_write_context_without_thesis()
        test_write_context_with_thesis_carries_assumptions()
        test_prompt_mentions_context()
        test_timeout_has_headroom()
        test_retries_once_after_timeout()
        test_empty_result_is_not_a_failure()
        test_persistent_failure_still_aborts()
        test_non_us_symbols_do_not_abort_the_run()
        test_array_inside_prose_still_parses()
    finally:
        cer.run_claude = orig
    print("\nALL PASS — calendar query has headroom and survives one slow call.")
