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


def test_ticker_flag_bypasses_calendar_and_filters_watchlist():
    calls = []
    def boom(wl):
        raise AssertionError("calendar must not be queried with --ticker")
    cer.query_calendar = boom
    cer.run_earnings_reviewer = lambda t, started: (calls.append(t) or f"STATUS: new-note-written ticker={t}")
    cer.load_watchlist_tickers = lambda: ["AAPL", "MSFT"]
    rc = cer.main(["--ticker", "AAPL", "--ticker", "ZZZZ", "--ticker", "msft"])
    assert rc == 0 and calls == ["AAPL", "MSFT"], (rc, calls)
    print("  ✓ --ticker skips the calendar, uppercases, and drops non-watchlist names")


def test_structure_new_note_noop_without_path():
    """No path= in the marker (a test stub, or the artifact-inspection fallback without
    one) -- must be a silent no-op, never touching thesis.structure_reads."""
    cer.structure_new_note("STATUS: new-note-written ticker=AAPL")   # no path= -> no-op
    cer.structure_new_note("STATUS: no-new-transcript ticker=AAPL")  # wrong marker -> no-op
    print("  ✓ structure_new_note no-ops when the marker carries no path=")


def test_structure_new_note_invokes_process_notes_and_never_raises():
    """RIS5 A2 hook wiring: a 'new-note-written ... path=...' marker calls
    thesis.structure_reads.process_notes([REPO_ROOT/path]) exactly once. A raised
    exception (simulating a claude -p 429) must be caught and logged, never propagated --
    the reviewer loop must never block on this."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from thesis import structure_reads
    calls = []
    orig = structure_reads.process_notes
    structure_reads.process_notes = lambda paths, **kw: (calls.append(paths) or {"written": 1, "dupes": 0, "dropped": 0})
    try:
        cer.structure_new_note("STATUS: new-note-written ticker=AAPL period=1Q26 iacc=1 path=notes/AAPL/20260101-1Q26.md")
        assert len(calls) == 1
        assert calls[0] == [cer.REPO_ROOT / "notes/AAPL/20260101-1Q26.md"]

        structure_reads.process_notes = lambda paths, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
        cer.structure_new_note("STATUS: new-note-written ticker=MSFT period=1Q26 iacc=1 path=notes/MSFT/x.md")  # must not raise
    finally:
        structure_reads.process_notes = orig
    print("  ✓ structure_new_note invokes process_notes once and swallows its exceptions")


def test_structure_reads_budget_skips_remaining_notes_once_exceeded():
    """RIS5 Part A pre-merge fix 7: a total wall-clock budget across notes in one run, so
    the 02:30 job cannot run into the 04:47 valuation-snapshot slot. A fake clock that
    jumps past STRUCTURE_READS_BUDGET_S on the second call must make every subsequent
    structure_new_note() call in the SAME run a no-op (process_notes never invoked again),
    logged once -- not re-checked/re-logged on every later note."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from thesis import structure_reads
    calls = []
    logged = []
    orig_pn = structure_reads.process_notes
    orig_clock = cer._clock
    orig_log = cer.log_write
    structure_reads.process_notes = lambda paths, **kw: (calls.append(paths) or {"written": 1, "dupes": 0, "dropped": 0})
    cer.log_write = lambda line: logged.append(line)
    # 1st call starts the clock at t=0 (deadline = 1800s later); 2nd call reports
    # t=1801 -- past budget -- so it, and every later call this run, must be skipped.
    ticks = iter([0.0, 1801.0])
    cer._clock = lambda: next(ticks)
    cer.reset_structure_reads_budget()
    try:
        cer.structure_new_note("STATUS: new-note-written ticker=AAPL path=notes/AAPL/a.md")
        cer.structure_new_note("STATUS: new-note-written ticker=MSFT path=notes/MSFT/b.md")
        cer.structure_new_note("STATUS: new-note-written ticker=META path=notes/META/c.md")
        assert len(calls) == 1, calls  # only the first, in-budget call went through
        assert cer._structure_reads_budget_exceeded is True
        assert sum("STRUCTURE_READS_BUDGET_EXCEEDED" in l for l in logged) == 1, logged
    finally:
        structure_reads.process_notes = orig_pn
        cer._clock = orig_clock
        cer.log_write = orig_log
        cer.reset_structure_reads_budget()
    print("  ✓ structure_reads budget exceeded mid-run skips remaining notes, logged once")


def test_session_limit_stops_the_batch():
    calls = []
    def fake(t, started):
        calls.append(t)
        return ("STATUS: error reason=invocation-failed detail=rc=1 stderr='claude -p session limit reached (429)'"
                if t == "AAPL" else f"STATUS: new-note-written ticker={t}")
    cer.run_earnings_reviewer = fake
    cer.load_watchlist_tickers = lambda: ["AAPL", "MSFT", "META"]
    rc = cer.main(["--ticker", "AAPL", "--ticker", "MSFT", "--ticker", "META"])
    assert rc == 1 and calls == ["AAPL"], (rc, calls)
    assert cer.is_session_limit("STATUS: error reason=x detail=Usage limit reached") is True
    assert cer.is_session_limit("STATUS: error reason=no-marker-emitted detail=...") is False
    assert cer.is_session_limit("STATUS: new-note-written ticker=X period=429") is False
    print("  ✓ a 429/session-limit marker stops the batch instead of burning 15 min per name")


if __name__ == "__main__":
    orig = cer.run_claude
    orig_main = (cer.query_calendar, cer.run_earnings_reviewer, cer.load_watchlist_tickers)
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
        test_ticker_flag_bypasses_calendar_and_filters_watchlist()
        test_structure_new_note_noop_without_path()
        test_structure_new_note_invokes_process_notes_and_never_raises()
        test_structure_reads_budget_skips_remaining_notes_once_exceeded()
        test_session_limit_stops_the_batch()
    finally:
        cer.run_claude = orig
        cer.query_calendar, cer.run_earnings_reviewer, cer.load_watchlist_tickers = orig_main
    print("\nALL PASS — calendar query has headroom and survives one slow call.")
