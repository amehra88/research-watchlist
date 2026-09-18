"""
Unit tests for scripts/portal/theme_share.py (RIS5 Part A, Task 4 -- bear-side paths;
fix round 1 adds per-cell `n` / per-ticker `rows` denominators and the null-vs-zero
delta distinction).

No pytest in this env -- run directly:
    python3 scripts/portal/test_theme_share.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme_share as TS  # noqa: E402


def _row(ticker, cq, themes, register="evidence", **extra):
    return {"ticker": ticker, "cal_quarter": cq, "register": register,
            "themes": [{"theme": t, "score": 0.5} for t in themes], **extra}


def test_share_is_ticker_rows_over_theme_rows_same_quarter():
    rows = [
        _row("AAA", "CY2026-Q1", ["hbm_competitive_landscape"]),
        _row("AAA", "CY2026-Q1", ["hbm_competitive_landscape"]),
        _row("BBB", "CY2026-Q1", ["hbm_competitive_landscape"]),
    ]
    out = TS.compute_theme_share(rows)
    cell = out["hbm_competitive_landscape"]["CY2026-Q1"]
    assert cell["n"] == 3   # fix round 1: total rows for the theme that quarter
    tickers = cell["tickers"]
    assert tickers["AAA"]["share"] == round(2 / 3, 6) and tickers["BBB"]["share"] == round(1 / 3, 6)
    assert tickers["AAA"]["rows"] == 2 and tickers["BBB"]["rows"] == 1   # fix round 1: per-ticker row count
    assert tickers["AAA"]["delta"] is None and tickers["BBB"]["delta"] is None   # first (only) quarter for this theme


def test_multi_theme_row_counts_once_per_theme_not_split():
    rows = [
        _row("AAA", "CY2026-Q1", ["hbm_competitive_landscape", "ai_infrastructure_capex"]),
        _row("BBB", "CY2026-Q1", ["hbm_competitive_landscape"]),
        _row("CCC", "CY2026-Q1", ["ai_infrastructure_capex"]),
    ]
    out = TS.compute_theme_share(rows)
    # AAA's row contributes a FULL 1 to each of its two themes, not 0.5 to each -- so each
    # theme's own `n` is 2 (AAA + one other), not 1.5.
    hbm = out["hbm_competitive_landscape"]["CY2026-Q1"]
    capex = out["ai_infrastructure_capex"]["CY2026-Q1"]
    assert hbm["n"] == 2 and capex["n"] == 2
    assert hbm["tickers"]["AAA"]["share"] == 0.5 and hbm["tickers"]["BBB"]["share"] == 0.5
    assert capex["tickers"]["AAA"]["share"] == 0.5 and capex["tickers"]["CCC"]["share"] == 0.5
    assert hbm["tickers"]["AAA"]["rows"] == 1 and capex["tickers"]["AAA"]["rows"] == 1


def test_delta_vs_prior_quarter_ticker_absent_but_theme_present_gets_zero_baseline():
    # fix round 1: a ticker absent from an EXISTING prior quarter (the theme had rows, just
    # not from this ticker) still gets a real numeric delta against a 0.0 baseline -- only a
    # prior quarter with ZERO rows for the theme (theme absent) gets null (see the next test).
    rows = [
        _row("AAA", "CY2025-Q4", ["hbm_competitive_landscape"]),
        _row("AAA", "CY2026-Q1", ["hbm_competitive_landscape"]),
        _row("BBB", "CY2026-Q1", ["hbm_competitive_landscape"]),   # new entrant this quarter
    ]
    out = TS.compute_theme_share(rows)
    q1, q4 = out["hbm_competitive_landscape"]["CY2026-Q1"]["tickers"], out["hbm_competitive_landscape"]["CY2025-Q4"]["tickers"]
    assert q4["AAA"]["share"] == 1.0 and q4["AAA"]["delta"] is None    # CY2025-Q4 is the global first quarter -> null
    # AAA: 1.0 (Q4, sole ticker) -> 0.5 (Q1, split with BBB) => delta -0.5
    assert q1["AAA"]["share"] == 0.5 and q1["AAA"]["delta"] == -0.5
    # BBB had 0 rows for this theme in the (EXISTING, nonzero-total) prior quarter -> real
    # numeric delta vs 0.0, not null -- the theme existed, only this ticker was absent from it.
    assert q1["BBB"]["share"] == 0.5 and q1["BBB"]["delta"] == 0.5


def test_delta_is_null_when_theme_has_zero_rows_in_the_prior_quarter():
    """fix round 1: when the theme itself has NO rows at all in the (existing) global prior
    quarter -- as opposed to just this ticker being absent from a quarter where the theme DID
    have rows -- delta must be null, not a 0-based numeric value. A theme with a gap (present
    in Q4 and Q2 but not Q1) compares Q2 against the GLOBAL prior quarter Q1, where it had
    zero rows -> null, not silently skipped back to Q4 (which would make its delta window
    span two quarters while every other theme's spans one)."""
    rows = [
        _row("AAA", "CY2025-Q4", ["gap_theme"]),
        _row("ZZZ", "CY2026-Q1", ["other_theme"]),          # makes CY2026-Q1 a real global quarter
        _row("AAA", "CY2026-Q2", ["gap_theme"]),
    ]
    out = TS.compute_theme_share(rows)
    q2 = out["gap_theme"]["CY2026-Q2"]["tickers"]
    assert "CY2026-Q1" not in out["gap_theme"]     # gap_theme really has no rows in Q1
    assert q2["AAA"]["share"] == 1.0 and q2["AAA"]["delta"] is None   # theme absent in the global prior quarter -> null, not 1.0


def test_register_agnostic_question_and_evidence_both_count():
    rows = [
        _row("AAA", "CY2026-Q1", ["ai_regulation"], register="question", source="exchange"),
        _row("AAA", "CY2026-Q1", ["ai_regulation"], register="evidence", source="mdna"),
    ]
    out = TS.compute_theme_share(rows)
    cell = out["ai_regulation"]["CY2026-Q1"]
    assert cell["n"] == 2 and cell["tickers"]["AAA"]["share"] == 1.0 and cell["tickers"]["AAA"]["rows"] == 2


def test_rows_missing_ticker_or_quarter_are_skipped():
    rows = [_row("AAA", None, ["x"]), {"ticker": None, "cal_quarter": "CY2026-Q1", "themes": [{"theme": "x"}]},
            _row("BBB", "CY2026-Q1", ["x"])]
    out = TS.compute_theme_share(rows)
    assert out["x"]["CY2026-Q1"] == {"n": 1, "tickers": {"BBB": {"share": 1.0, "delta": None, "rows": 1}}}


def test_write_and_read_topic_map_jsonl(tmp_path=None):
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tm = tmp / "topic_map.jsonl"
        tm.write_text("\n".join(json.dumps(r) for r in [
            _row("AAA", "CY2026-Q1", ["hbm_competitive_landscape"]),
            _row("BBB", "CY2026-Q1", ["hbm_competitive_landscape"]),
        ]) + "\n", encoding="utf-8")
        out_file = tmp / "state" / "topics" / "theme_share.json"
        result = TS.theme_share(tm, out_path=out_file)
        assert out_file.exists()
        on_disk = json.loads(out_file.read_text())
        assert on_disk == result
        cell = on_disk["hbm_competitive_landscape"]["CY2026-Q1"]
        assert cell["n"] == 2 and cell["tickers"]["AAA"]["share"] == 0.5


def test_no_write_without_out_path():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tm = tmp / "topic_map.jsonl"
        tm.write_text(json.dumps(_row("AAA", "CY2026-Q1", ["x"])) + "\n", encoding="utf-8")
        cwd = os.getcwd()
        os.chdir(td)
        try:
            TS.theme_share(tm)   # no out_path
            assert list(Path(td).iterdir()) == [tm]   # only the input file we wrote ourselves exists
        finally:
            os.chdir(cwd)


def test_missing_topic_map_file_returns_empty_not_error():
    assert TS.theme_share(Path("/nonexistent/topic_map.jsonl")) == {}


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
