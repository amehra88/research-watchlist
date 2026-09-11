#!/usr/bin/env python3
"""
Unit tests for lifecycle.py — spec §6.3 staging and the Tier 0 lag measurement, over the live
topic_map.jsonl row shape (themes: [{theme, score}], event_date on every row, firm on questions).

No pytest in this env — run directly:
    python3 scripts/topics/test_lifecycle.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lifecycle as lc  # noqa: E402


def _row(themes, ticker, register, rid, date, firm=None, source="exchange"):
    ts = themes if isinstance(themes, list) else ([themes] if themes else [])
    return {"id": rid, "register": register, "ticker": ticker, "event_date": date, "firm": firm,
            "source": source, "cal_quarter": "CY2026-Q2", "event_type": "earnings_call",
            "themes": [{"theme": t, "score": 0.5} for t in ts], "candidate": None}


def test_lag_is_question_minus_evidence_in_days():
    """The §6.3 clock. Positive means evidence led."""
    assert lc.lag_days("2026-04-20", "2026-06-09") == 50
    assert lc.lag_days("2026-06-09", "2026-04-20") == -50
    assert lc.lag_days(None, "2026-06-09") is None


def test_a_question_that_precedes_evidence_is_kept_as_a_negative_lag():
    """The falsification case, and the one a careless implementation drops.

    The system's whole premise is that evidence precedes questions. A pair
    where the analyst asked FIRST is the evidence against that premise, so
    filtering it out — or clamping it to zero — would rig the very measurement
    Tier 0 exists to perform."""
    rows = [_row("t1", "AAOI", "evidence", "e1", "2026-06-01"),
            _row("t1", "AAOI", "question", "q1", "2026-03-01")]
    pair = lc.build_index(rows)[("t1", "AAOI")]
    assert pair["first_evidence_date"] == "2026-06-01"
    assert pair["first_question_date"] == "2026-03-01"
    assert lc.lag_days(pair["first_evidence_date"], pair["first_question_date"]) == -92


def test_first_dates_take_the_earliest_of_each_register():
    rows = [_row("t1", "AAOI", "evidence", "e1", "2026-05-01"),
            _row("t1", "AAOI", "evidence", "e2", "2026-02-01"),
            _row("t1", "AAOI", "question", "q1", "2026-08-01"),
            _row("t1", "AAOI", "question", "q2", "2026-06-01")]
    p = lc.build_index(rows)[("t1", "AAOI")]
    assert p["first_evidence_date"] == "2026-02-01"
    assert p["first_question_date"] == "2026-06-01"


def test_a_row_with_two_themes_feeds_both_pairs():
    rows = [_row(["t1", "t2"], "AAOI", "question", "q1", "2026-06-01", firm="Mizuho")]
    idx = lc.build_index(rows)
    assert set(idx) == {("t1", "AAOI"), ("t2", "AAOI")}
    assert idx[("t1", "AAOI")]["banks"] == {"Mizuho"}


def test_first_evidence_date_comes_from_the_row_event_date_for_both_sources():
    rows = [_row("t1", "AAOI", "evidence", "c1", "2026-05-01", source="mdna"),
            _row("t1", "AAOI", "evidence", "e1", "2026-04-01", source="exchange")]
    p = lc.build_index(rows)[("t1", "AAOI")]
    assert p["first_evidence_date"] == "2026-04-01"
    assert p["evidence_sources"] == {"mdna", "exchange"}


def test_stage_1_is_evidence_with_no_question_anywhere():
    rows = [_row("t1", "AAOI", "evidence", "e1", "2026-05-01")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "AAOI") == 1


def test_stage_2_is_questions_at_another_name_but_not_this_one():
    rows = [_row("t1", "AAOI", "evidence", "e1", "2026-05-01"),
            _row("t1", "LITE", "evidence", "e2", "2026-05-01"),
            _row("t1", "LITE", "question", "q1", "2026-06-01")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "AAOI") == 2
    assert lc.stage(idx, "t1", "LITE") == 3


def test_stage_4_is_questions_on_most_covered_names():
    """'Late / priced'. Four names carry the topic and three are being asked
    about it, so it is no longer anyone's edge."""
    rows = []
    for tk in ("AAOI", "LITE", "COHR", "FN"):
        rows.append(_row("t1", tk, "evidence", f"e{tk}", "2026-05-01"))
    for tk in ("AAOI", "LITE", "COHR"):
        rows.append(_row("t1", tk, "question", f"q{tk}", "2026-06-01"))
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "AAOI") == 4


def test_open_lag_is_measured_to_today_for_stage_1():
    """§6.3: 'that duration, not merely the stage label, is what gets
    reported.' An unanswered topic gets more interesting the longer it sits."""
    rows = [_row("t1", "AAOI", "evidence", "e1", "2026-05-01")]
    idx = lc.build_index(rows)
    assert lc.open_lag_days(idx[("t1", "AAOI")], as_of="2026-08-22") == 113


def test_rows_with_no_theme_are_ignored():
    """Below-threshold rows are candidates, not topics. Counting them here
    would put un-named clusters into the lag distribution."""
    rows = [_row(None, "AAOI", "evidence", "e1", "2026-05-01"),
            _row("t1", "AAOI", "evidence", "e2", "2026-05-01")]
    idx = lc.build_index(rows)
    assert list(idx) == [("t1", "AAOI")]


def test_summarize_reports_the_distribution_not_just_a_mean():
    lags = [-10, 0, 5, 30, 60, 90, 120, 200]
    s = lc.summarize(lags)
    assert s["n"] == 8
    assert s["median"] == 45
    assert s["p25"] == 5 and s["p75"] == 120
    assert s["n_negative"] == 1
    assert s["share_evidence_led"] == 75.0    # strictly positive: 6 of 8


def test_detection_log_is_append_only_and_first_seen_wins():
    """The point of the log: in three years the question is 'when did the
    system FIRST say this', and a value that moves on every re-run cannot
    answer it. Re-running must not restamp an existing detection."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "detections.jsonl"
        lc.append_detections(p, [{"theme": "t1", "ticker": "AAOI",
                                  "first_evidence_date": "2026-05-01",
                                  "stage": 1}], as_of="2026-08-01")
        lc.append_detections(p, [{"theme": "t1", "ticker": "AAOI",
                                  "first_evidence_date": "2026-05-01",
                                  "stage": 1}], as_of="2026-09-01")
        recs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        assert len(recs) == 1, "a re-run must not duplicate a detection"
        assert recs[0]["detected_on"] == "2026-08-01", \
            "detected_on must keep the FIRST date, not the latest run's"


def test_detection_log_records_a_later_distinct_pair():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "detections.jsonl"
        lc.append_detections(p, [{"theme": "t1", "ticker": "AAOI",
                                  "first_evidence_date": "2026-05-01",
                                  "stage": 1}], as_of="2026-08-01")
        lc.append_detections(p, [{"theme": "t1", "ticker": "LITE",
                                  "first_evidence_date": "2026-06-01",
                                  "stage": 1}], as_of="2026-09-01")
        recs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        assert len(recs) == 2
        assert recs[1]["detected_on"] == "2026-09-01"


def test_a_detection_records_the_coverage_it_was_computed_at():
    """A stage-1 claim made on a partial map is a different claim from one made
    on a finished map, and detected_on is permanent. The log has to carry
    enough to tell them apart years later."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "detections.jsonl"
        lc.append_detections(p, [{"theme": "t1", "ticker": "AAOI",
                                  "first_evidence_date": "2026-05-01",
                                  "stage": 1}],
                             as_of="2026-08-22", coverage_pct=42.5)
        rec = json.loads(p.read_text().splitlines()[0])
        assert rec["coverage_pct"] == 42.5


def test_map_is_fresh_rejects_a_map_older_than_its_inputs():
    with tempfile.TemporaryDirectory() as d:
        m, x = Path(d) / "map.jsonl", Path(d) / "exchanges.jsonl"
        m.write_text("{}\n"); time.sleep(0.02); x.write_text("{}\n")
        ok, why = lc.map_is_fresh(m, [x]); assert not ok and "older" in why
        time.sleep(0.02); os.utime(m, None)
        assert lc.map_is_fresh(m, [x])[0]
        assert not lc.map_is_fresh(Path(d) / "missing.jsonl", [x])[0]


# ───────────────────────── runner ─────────────────────────

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
