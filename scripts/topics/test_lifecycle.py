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


def test_first_filing_date_is_mdna_only_so_same_call_answers_do_not_zero_the_lag():
    """A corprep answer carries the date of the question that prompted it; measuring the lag
    from it would report 0 for every answered question. The clock runs from filings."""
    rows = [_row("t1", "AAOI", "question", "q1", "2026-06-09", firm="Mizuho"),
            _row("t1", "AAOI", "evidence", "a1", "2026-06-09", source="exchange"),
            _row("t1", "AAOI", "evidence", "c1", "2026-04-20", source="mdna")]
    p = lc.build_index(rows)[("t1", "AAOI")]
    assert p["first_evidence_date"] == "2026-04-20" and p["first_filing_date"] == "2026-04-20"
    assert lc.lag_days(p["first_filing_date"], p["first_question_date"]) == 50
    q = lc.build_index(rows[:2])[("t1", "AAOI")]
    assert q["first_filing_date"] is None and q["first_evidence_date"] == "2026-06-09"


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


# ───────── stages 1 and 2 assert a silence (2026-09-15) ─────────
#
# Stage 1 ("nobody has asked anywhere") and stage 2 ("asked elsewhere, not
# here") are both negative claims. They are only observations if we pulled the
# company's calls. Measured on the live map: 61 of 631 pairs asserted a silence
# that was never observed — 4 at stage 1 and 57 at stage 2, on tickers with no
# call rows at all. GOOGL/antitrust_action sat at stage 1, the strongest signal
# the system emits, for a company we have never once queried.

def test_stage_1_is_withheld_when_the_company_was_never_heard():
    """`called` is the set of tickers whose calls we actually pulled. A ticker
    outside it cannot be said to have stayed silent."""
    rows = [_m("t1", "GOOGL"), _m("t1", "GOOGL", "2026-06-01")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "GOOGL", assigned={}, called={"AAOI"}) is None
    # ...and it IS stage 1 once we have heard the company
    assert lc.stage(idx, "t1", "GOOGL", assigned={}, called={"GOOGL"}) == 1


def test_stage_2_is_withheld_when_the_company_was_never_heard():
    """'Asked at another name, not here' is the same negative claim about
    THIS company, so it needs the same observation."""
    rows = [_q("t1", "AAOI"), _m("t1", "WMT")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "WMT", assigned={}, called={"AAOI"}) is None
    assert lc.stage(idx, "t1", "WMT", assigned={}, called={"AAOI", "WMT"}) == 2


def test_stages_3_and_4_never_need_the_guard():
    """They rest on a POSITIVE observation — this company was asked — so being
    heard is implied. Withholding them would discard real evidence."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    # `called` deliberately omits the asked tickers; stage 3/4 must survive
    assert lc.stage(idx, "t1", "A", assigned={}, called=set()) in (3, 4)


def test_the_guard_is_off_when_no_coverage_information_is_supplied():
    """Back-compat: callers that pass neither assigned nor called get the old
    behaviour, so the pre-existing stage tests still mean what they meant."""
    rows = [_m("t1", "GOOGL"), _m("t1", "GOOGL", "2026-06-01")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "GOOGL") == 1


# ───────────── stage-4 denominator (2026-09-15) ─────────────
#
# `covered` used to be "tickers where a (theme, ticker) pair exists", and a
# pair only exists where the theme was DETECTED. For any theme the evidence
# side never matches, covered == asked and "asked at > half of covered" cannot
# fail. Measured: 24 of 40 stage-4 themes had zero MD&A evidence anywhere and
# 28 of 40 sat at a ratio of exactly 1.00, which is how 408 of 631 pairs came
# to read "late / priced".

def _q(theme, ticker, date="2026-06-01"):
    return {"unit_id": f"q-{theme}-{ticker}", "register": "question", "ticker": ticker,
            "themes": [{"theme": theme}], "event_date": date, "firm": "Wolfe"}


def _m(theme, ticker, date="2026-05-01"):
    return {"unit_id": f"m-{theme}-{ticker}", "register": "evidence", "source": "mdna",
            "ticker": ticker, "themes": [{"theme": theme}], "event_date": date}


def test_theme_assignments_reads_every_tier():
    w = {"tier_1_bctk": [{"ticker": "COHR", "themes": ["t1", "t2"]}],
         "tier_3_watchlist": [{"ticker": "LITE", "themes": ["t1"]}],
         "tier_4_ecosystem": [{"id": "innolight.cn", "themes": ["t1"]}]}
    a = lc.theme_assignments(w)
    assert a["t1"] == {"COHR", "LITE", "innolight.cn"}
    assert a["t2"] == {"COHR"}


def test_stage_without_relevance_info_keeps_the_old_denominator():
    """Back-compat. Callers that pass nothing get exactly today's behaviour, so
    the change is opt-in at the call site and the old tests still mean what
    they meant."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    assert lc.stage(idx, "t1", "A") == 4


def test_a_theme_only_ever_detected_where_it_was_asked_cannot_reach_stage_4():
    """The bug. Three tickers asked, nothing else known about the theme — so
    there is no company where it was relevant and NOT asked, and 'asked at most
    covered names' is unfalsifiable. Stage 3 is the honest ceiling."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    called = {"A", "B", "C", "D", "E"}
    assert lc.stage(idx, "t1", "A", assigned={}, called=called) == 3
    assert lc.stage4_assertable(idx, "t1", assigned={}, called=called) is False


def test_operator_assignment_supplies_the_missing_denominator():
    """Assigned to five covered names, asked at three of them -> a real 3/5
    majority, and stage 4 becomes assertable and true."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    assigned = {"t1": {"A", "B", "C", "D", "E"}}
    called = {"A", "B", "C", "D", "E"}
    assert lc.stage4_assertable(idx, "t1", assigned=assigned, called=called) is True
    assert lc.stage(idx, "t1", "A", assigned=assigned, called=called) == 4


def test_assignment_that_is_broad_enough_keeps_a_theme_at_stage_3():
    """Asked at 3 of 9 relevant covered names is not 'late / priced'."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    assigned = {"t1": set("ABCDEFGHI")}
    assert lc.stage(idx, "t1", "A", assigned=assigned, called=set("ABCDEFGHI")) == 3


def test_relevant_names_whose_calls_we_never_heard_do_not_count():
    """A theme must not be held back from stage 4 because WE failed to ingest a
    company's call — that is the same censoring trap as the Tier-0 lag. Only
    companies we actually heard can be counted as having stayed silent."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    assigned = {"t1": set("ABCDEFGHI")}
    # we only ever heard A..E; F..I are assigned but unheard
    assert lc.stage(idx, "t1", "A", assigned=assigned, called=set("ABCDE")) == 4


def test_evidence_only_names_count_toward_relevance():
    """A company that DISCLOSED the theme but was never asked about it is the
    most informative kind of denominator entry — it is the §6.2 gap itself."""
    rows = ([_q("t1", tk) for tk in ("A", "B", "C")]
            + [_m("t1", tk) for tk in ("D", "E", "F", "G")])
    idx = lc.build_index(rows)
    called = set("ABCDEFG")
    assert lc.stage4_assertable(idx, "t1", assigned={}, called=called) is True
    # 4 companies disclosed it and were never asked, so 3 of 7 is not a majority
    assert lc.stage(idx, "t1", "A", assigned={}, called=called) == 3
    assert lc.stage4_universe(idx, "t1", assigned={}, called=called) == set("ABCDEFG")


def test_asked_is_always_inside_the_universe():
    """If a ticker could be in `asked` but not in the denominator, the ratio
    exceeds 1.0 and stage 4 goes automatic again — the same bug wearing a
    different denominator."""
    rows = [_q("t1", tk) for tk in ("A", "B", "C")]
    idx = lc.build_index(rows)
    u = lc.stage4_universe(idx, "t1", assigned={}, called=set())   # nothing 'called'
    asked = {tk for (th, tk), p in idx.items() if th == "t1" and p["first_question_date"]}
    assert asked <= u, (asked, u)


# ────────────── Tier-0 identification guard (2026-09-15) ──────────────
#
# Measured on the live map: the raw lag says evidence led 34.2% of the time
# (median -1d). Drop only the negative lags whose question predates observable
# MD&A and it becomes 86.2% (median +174d). Apply the guard in both directions
# and nothing survives. A number that swings 34% -> 86% -> n=0 on which
# defensible correction you pick is not a measurement, and these tests pin the
# rule that says so.

def _pair(theme="t1", ticker="AAOI", filing=None, question=None):
    return {"theme": theme, "ticker": ticker, "first_filing_date": filing,
            "first_question_date": question}


def test_coverage_starts_takes_the_earliest_date_per_register():
    rows = [
        {"ticker": "AAOI", "register": "question", "event_date": "2026-03-01",
         "themes": [{"theme": "t1"}]},
        {"ticker": "AAOI", "register": "question", "event_date": "2026-01-05",
         "themes": [{"theme": "t1"}]},
        {"ticker": "AAOI", "register": "evidence", "source": "mdna",
         "event_date": "2026-05-01", "themes": [{"theme": "t1"}]},
        {"ticker": "AAOI", "register": "evidence", "source": "exchange",
         "event_date": "2025-01-01", "themes": [{"theme": "t1"}]},
    ]
    s = lc.coverage_starts(rows)["AAOI"]
    assert s["question"] == "2026-01-05"
    # corprep/exchange rows are NOT MD&A and must not move the filing start
    assert s["mdna"] == "2026-05-01", s


def test_a_negative_lag_is_unidentified_when_mdna_was_not_yet_observed():
    """The dangerous direction. 'The analyst asked before the company wrote
    it' requires that no earlier filing said it — untestable if MD&A was not
    being ingested yet. CRWD's MD&A starts 93 days after its call coverage, and
    those names produce the entire negative tail."""
    starts = {"AAOI": {"question": "2025-11-01", "mdna": "2026-05-01"}}
    p = _pair(filing="2026-05-07", question="2025-12-09")    # lag -149
    assert lc.lag_is_identified(p, starts, buf=30) is False


def test_a_positive_lag_is_unidentified_when_questions_were_not_yet_observed():
    """The mirror case, and the reason the guard cannot be one-sided. If the
    call register started late, an earlier question may exist unseen and the
    true order could be the other way round."""
    starts = {"AAOI": {"question": "2026-05-01", "mdna": "2025-11-01"}}
    p = _pair(filing="2026-05-07", question="2026-09-01")    # lag +117
    assert lc.lag_is_identified(p, starts, buf=30) is False


def test_a_pair_observed_on_both_sides_well_before_either_event_is_identified():
    starts = {"AAOI": {"question": "2025-11-01", "mdna": "2025-11-01"}}
    p = _pair(filing="2026-03-01", question="2026-06-01")
    assert lc.lag_is_identified(p, starts, buf=30) is True


def test_a_same_day_pair_must_clear_BOTH_guards():
    """lag == 0 is neither positive nor negative, so a branch written as
    if/elif skips it entirely. Measured consequence: the only four pairs that
    survived a 30-day guard were all same-day call/filing coincidences sitting
    on a coverage boundary (FPS, DASH, ZS, HPE) — artifacts that looked like
    the sample."""
    starts = {"AAOI": {"question": "2025-11-01", "mdna": "2026-05-14"}}
    p = _pair(filing="2026-05-14", question="2026-05-14")
    assert lc.lag_is_identified(p, starts, buf=30) is False


def test_identified_lags_reports_why_pairs_were_dropped():
    """The dropped counts ARE the diagnostic. Collapsing them into one number
    hides which direction the censoring runs in."""
    starts = {"A": {"question": "2025-11-01", "mdna": "2026-05-01"},
              "B": {"question": "2025-11-01", "mdna": "2025-11-01"}}
    idx = {
        ("t1", "A"): _pair("t1", "A", "2026-05-07", "2025-12-09"),   # neg, unid
        ("t1", "B"): _pair("t1", "B", "2026-03-01", "2026-06-01"),   # +92, kept
    }
    out = lc.identified_lags(idx, starts, buf=30)
    assert out["lags"] == [92], out
    assert out["dropped_neg"] == 1 and out["dropped_pos"] == 0, out
    assert out["buffer_days"] == 30


def test_a_same_reporting_event_pair_has_no_timing_content():
    """Filings land a median +1 day after the call (p25 0, p75 2, measured).
    So a pair whose two events are a day apart is one disclosure event, not a
    company reacting to an analyst. AMBA/automotive_semiconductor_demand was
    exactly this — filed 2026-09-04, asked 2026-09-03 — and it was half the
    identified sample until it got its own bucket."""
    starts = {"A": {"question": "2025-11-01", "mdna": "2025-11-01"}}
    idx = {("t1", "A"): _pair("t1", "A", "2026-09-04", "2026-09-03")}
    out = lc.identified_lags(idx, starts, buf=30)
    assert out["lags"] == [], out
    assert out["dropped_same_event"] == 1, out
    # it is NOT a censoring drop — conflating the two would make the
    # directional diagnostic lie
    assert out["dropped_neg"] == 0 and out["dropped_pos"] == 0, out


def test_every_pair_lands_in_exactly_one_bucket():
    """The accounting invariant. Four buckets now, and the `lag == 0` hole was
    born of a branch that matched none of them. If a future edit drops a pair
    into no bucket, or into two, this fails."""
    starts = {"A": {"question": "2025-11-01", "mdna": "2026-05-01"},
              "B": {"question": "2025-11-01", "mdna": "2025-11-01"},
              "C": {"question": "2026-09-01", "mdna": "2025-11-01"}}
    idx = {
        ("t1", "A"): _pair("t1", "A", "2026-05-07", "2025-12-09"),   # neg, censored
        ("t1", "B"): _pair("t1", "B", "2026-03-01", "2026-06-01"),   # +92, kept
        ("t2", "B"): _pair("t2", "B", "2026-09-04", "2026-09-03"),   # same event
        ("t1", "C"): _pair("t1", "C", "2026-02-01", "2026-09-20"),   # pos, censored
        ("t3", "B"): _pair("t3", "B", "2026-03-01", None),           # not a pair
    }
    out = lc.identified_lags(idx, starts, buf=30)
    n_with_both = sum(1 for p in idx.values()
                      if p["first_filing_date"] and p["first_question_date"])
    total = (len(out["lags"]) + out["dropped_pos"] + out["dropped_neg"]
             + out["dropped_same_event"])
    assert total == n_with_both == 4, (total, n_with_both, out)


def test_identified_lags_ignores_pairs_missing_a_side():
    starts = {"A": {"question": "2025-11-01", "mdna": "2025-11-01"}}
    idx = {("t1", "A"): _pair("t1", "A", "2026-03-01", None)}
    out = lc.identified_lags(idx, starts, buf=30)
    assert out["lags"] == [] and out["dropped_pos"] == 0 and out["dropped_neg"] == 0


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
