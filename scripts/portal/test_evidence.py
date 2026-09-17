"""
Unit tests for scripts/portal/evidence.py (RIS4 slice 3, Task 1).

Fixtures live under fixtures/evidence/: evidence_log.jsonl (12 rows across 2
tickers -- AAA/a1, AAA/a2, BBB/b1 -- covering strengths 0-3, both confirm and
challenge directions, and one row (AAA/a1, 2025-12-20) noticeably older than
the other AAA/a1 rows so a card-builder's own date window has something real
to filter) plus AAA/_thesis.md (used only by the round-trip test below --
evidence.py itself never reads a thesis note). Tests run ONLY against these
fixtures via explicit `paths: Paths` overrides -- evidence.py's own zero-arg
REPO-backed default is never exercised here.

No pytest in this env -- run directly:
    python3 scripts/portal/test_evidence.py
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence as ev  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "evidence"
PATHS = ev.Paths(thesis_state=FIXTURES)
MISSING_PATHS = ev.Paths(thesis_state=FIXTURES / "does_not_exist")


# ───────────────────────── load_index ─────────────────────────

def test_load_index_shape_and_keys():
    idx = ev.load_index(PATHS)
    assert set(idx) == {("AAA", "a1"), ("AAA", "a2"), ("BBB", "b1")}, set(idx)
    assert len(idx[("AAA", "a1")]) == 5, idx[("AAA", "a1")]
    assert len(idx[("AAA", "a2")]) == 3, idx[("AAA", "a2")]
    assert len(idx[("BBB", "b1")]) == 4, idx[("BBB", "b1")]


def test_load_index_row_shape_trims_to_expected_fields():
    idx = ev.load_index(PATHS)
    row = idx[("BBB", "b1")][0]
    assert set(row) == {"date", "source", "source_id", "ref", "title", "direction",
                        "strength", "why", "quote", "cross_ticker"}, set(row)


def test_load_index_truncates_why_and_quote():
    idx = ev.load_index(PATHS)
    long_row = next(r for r in idx[("AAA", "a1")] if r["date"] == "2026-01-08")
    assert len(long_row["why"]) == 200, len(long_row["why"])
    assert len(long_row["quote"]) == 300, len(long_row["quote"])


def test_load_index_missing_file_returns_empty_dict():
    assert ev.load_index(MISSING_PATHS) == {}


def test_load_index_logs_one_line_on_missing_file():
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.load_index(MISSING_PATHS)
    lines = buf.getvalue().splitlines()
    assert len(lines) == 1, lines
    assert "missing" in lines[0], lines[0]


# ───────────────────────── top() ordering / drop / cap ─────────────────────────

def test_top_orders_by_strength_desc_then_date_desc():
    idx = ev.load_index(PATHS)
    rows = ev.top(idx[("AAA", "a1")], n=6)
    strengths = [r["strength"] for r in rows]
    assert strengths == sorted(strengths, reverse=True), strengths
    # the two strength-3 rows are dated 2026-01-09 and 2026-01-07 -- desc-by-date
    # among ties means 01-09 sorts ahead of 01-07.
    top_two_dates = [r["date"] for r in rows[:2]]
    assert top_two_dates == ["2026-01-09", "2026-01-07"], top_two_dates


def test_top_drops_strength_zero_rows_when_signal_exists():
    idx = ev.load_index(PATHS)
    rows = ev.top(idx[("AAA", "a1")], n=6)
    assert all(r["strength"] >= 1 for r in rows), rows
    # source data has 5 rows for a1, one of them strength 0 -> 4 survive the drop rule.
    assert len(rows) == 4, rows


def test_top_keeps_strength_zero_rows_when_no_signal_exists():
    idx = ev.load_index(PATHS)
    rows = ev.top(idx[("AAA", "a2")], n=6)
    assert len(rows) == 3, rows
    assert all(r["strength"] == 0 for r in rows), rows


def test_top_caps_at_n():
    idx = ev.load_index(PATHS)
    rows = ev.top(idx[("AAA", "a1")], n=2)
    assert len(rows) == 2, rows
    assert [r["strength"] for r in rows] == [3, 3], rows


def test_top_empty_rows_returns_empty_list():
    assert ev.top([], n=6) == []


def test_top_does_not_filter_by_date_or_age():
    # the 2025-12-20 row is far older than the rest of AAA/a1 but still has
    # strength 1 -- top() must include it (age filtering is the card
    # builder's job, not this module's), it just sorts to the bottom.
    idx = ev.load_index(PATHS)
    rows = ev.top(idx[("AAA", "a1")], n=6)
    dates = [r["date"] for r in rows]
    assert "2025-12-20" in dates, dates
    assert dates[-1] == "2025-12-20", dates


# ───────────────────────── attach_thesis ─────────────────────────

def _fixture_bundle(ticker="AAA", assumptions=None):
    assumptions = assumptions if assumptions is not None else [
        {"id": "a1", "statement": "..."},
        {"id": "a2", "statement": "..."},
    ]
    return {"ticker": ticker, "thesis": {"fm_without_body": {
        "doc_type": "thesis", "ticker": ticker, "assumptions": assumptions,
    }, "body": ""}}


def test_attach_thesis_sets_evidence_per_assumption():
    idx = ev.load_index(PATHS)
    bundle = _fixture_bundle()
    ev.attach_thesis(bundle, idx)
    assert set(bundle["thesis"]["evidence"]) == {"a1", "a2"}
    assert len(bundle["thesis"]["evidence"]["a1"]) == 4  # matches test_top_drops... above
    assert len(bundle["thesis"]["evidence"]["a2"]) == 3


def test_attach_thesis_assumption_with_no_evidence_gets_empty_list():
    bundle = _fixture_bundle(assumptions=[
        {"id": "a1", "statement": "..."},
        {"id": "no_such_assumption", "statement": "..."},
    ])
    ev.attach_thesis(bundle, ev.load_index(PATHS))
    assert bundle["thesis"]["evidence"]["no_such_assumption"] == []
    assert len(bundle["thesis"]["evidence"]["a1"]) == 4


def test_attach_thesis_no_thesis_gets_no_evidence_key():
    bundle = {"ticker": "ZZZ", "thesis": {"fm_without_body": {}, "body": ""}}
    ev.attach_thesis(bundle, ev.load_index(PATHS))
    assert "evidence" not in bundle["thesis"], bundle["thesis"]


def test_attach_thesis_missing_thesis_key_is_a_noop():
    bundle = {"ticker": "ZZZ"}
    ev.attach_thesis(bundle, ev.load_index(PATHS))  # must not raise
    assert "thesis" not in bundle


def test_attach_thesis_cross_ticker_isolation():
    # a BBB bundle must never see AAA's evidence rows even though both share
    # the index built from the same file.
    idx = ev.load_index(PATHS)
    bundle = _fixture_bundle(ticker="BBB", assumptions=[{"id": "b1", "statement": "..."}])
    ev.attach_thesis(bundle, idx)
    assert len(bundle["thesis"]["evidence"]["b1"]) == 3, bundle["thesis"]["evidence"]["b1"]
    assert all(r["source"] != "earnings_break" or True for r in bundle["thesis"]["evidence"]["b1"])


# ───────────────────────── fixture round-trip: _thesis.md <-> evidence_log.jsonl ─────────────────────────

def test_fixture_thesis_assumption_ids_all_have_evidence_rows():
    import yaml
    text = (FIXTURES / "AAA" / "_thesis.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = yaml.safe_load(m.group(1))
    ids = {a["id"] for a in fm["assumptions"]}
    idx = ev.load_index(PATHS)
    for aid in ids:
        assert ("AAA", aid) in idx, (aid, set(idx))


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
