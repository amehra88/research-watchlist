"""Run directly: python3 scripts/thesis/test_score_reads.py"""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import score_reads as SR  # noqa: E402
from thesis import match_evidence as M  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "score_reads"


def test_full_layout_every_axis_and_verb():
    text = (FIX / "full_layout.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "hold", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "drift", "value": "4+"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "3"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "5"},
    ]


def test_propose_initial_score_verb_form():
    text = (FIX / "propose_initial_score.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "propose", "value": "2"},
        {"axis": "potential_investor_interest.score", "verb": "propose", "value": "2"},
    ]


def test_bold_colon_article_tolerance():
    text = (FIX / "bold_colon_article.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "drift", "value": "4+"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "hold", "value": "4"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "4"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4-"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "3+"},
    ]


def test_idiom_populate_a_initialize_initiate_establish_initial_score_of():
    text = (FIX / "idiom_populate_a.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "populate", "value": "3+"},
        {"axis": "competitive_advantage.distribution", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.overall", "verb": "populate", "value": "4-"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "4+"},
    ]


def test_idiom_populate_b_proposal_forms_and_reaffirm():
    text = (FIX / "idiom_populate_b.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "populate", "value": "3"},
        {"axis": "competitive_advantage.distribution", "verb": "populate", "value": "5"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4"},   # "propose initial" (no "score") -> existing PROPOSE verb
        {"axis": "potential_investor_interest.score", "verb": "hold", "value": "4"},  # "reaffirm" -> HOLD
    ]


def test_idiom_revise_updown_and_quoted_backticked_values():
    text = (FIX / "idiom_revise_and_quotes.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "revise", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "revise", "value": "4+"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "3+"},
        {"axis": "competitive_advantage.overall", "verb": "revise", "value": "3"},
        {"axis": "potential_investor_interest.score", "verb": "drift", "value": "4+"},
    ]


def test_idiom_revise_from_prior_quoted_value_skips_the_earlier_quote():
    text = (FIX / "idiom_revise_from_prior.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "revise", "value": "4"}]


def test_line_anchored_hedge_in_reasoning_never_wins_over_true_recommendation():
    """RIS5 A1 fix round 2 regression: notes/CSCO/20260513-2Q26.md's real §5 recommendation
    is "Initialize at "4-"" (populate), but its Reasoning bullet hedges "would revise to
    "4"" -- a whole-block search finds that hedge first and gets it wrong. Matching must be
    anchored to the line that starts with "Recommendation"."""
    text = (FIX / "csco_hedge_line_not_matched.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "populate", "value": "4-"}]


def test_line_anchored_recap_before_true_recommendation_never_wins():
    """RIS5 A1 fix round 2 regression: notes/CSCO/20260514-3Q26.md's "Current score" bullet
    recaps last quarter's "Initialize at 4-" before the real (later) "Revise upward ... to
    "4"" recommendation line -- a whole-block search finds the recap's idiom first and gets
    it wrong. Matching must be anchored to the line that starts with "Recommendation"."""
    text = (FIX / "csco_recap_line_not_matched.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "revise", "value": "4"}]


def test_no_recs_note_yields_no_rows():
    text = (FIX / "no_recs.md").read_text()
    assert SR.parse_recs(text) == []


def test_parse_note_id_earnings_and_conf():
    assert SR.parse_note_id("COHR/20260904-2Q27.md") == ("COHR", "2Q27", "2026-09-04")
    assert SR.parse_note_id("COHR/20260904-conf-analyst-day.md") == ("COHR", None, "2026-09-04")


def test_build_rows_shape_and_applied():
    text = (FIX / "full_layout.md").read_text()
    rows = SR.build_rows("AMAT/20260515-2Q26.md", text, {"ai_positioning": "3"}, "2026-09-16T00:00:00+00:00")
    assert len(rows) == 5
    r0 = rows[0]
    assert r0["ticker"] == "AMAT" and r0["quarter"] == "2Q26" and r0["date"] == "2026-05-15"
    assert r0["note_id"] == "AMAT/20260515-2Q26.md" and r0["axis"] == "ai_positioning"
    assert r0["verb"] == "hold" and r0["value"] == "4" and r0["applied"] == "3"
    # axis with no watchlist entry -> applied is null, not a KeyError
    assert rows[1]["applied"] is None
    ids = {r["id"] for r in rows}
    assert len(ids) == 5   # one id per (note_id, axis)


def test_append_rows_is_idempotent():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-09-16T00:00:00+00:00")
    first = SR.append_rows(tmp, rows)
    assert first == {"written": 5, "dupes": 0}
    second = SR.append_rows(tmp, rows)
    assert second == {"written": 0, "dupes": 5}
    lines = [json.loads(l) for l in tmp.read_text().splitlines() if l.strip()]
    assert len(lines) == 5


def test_append_rows_replace_mode_updates_changed_and_preserves_ts_on_unchanged():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows_v1 = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-01-01T00:00:00+00:00")
    first = SR.append_rows(tmp, rows_v1, replace=True)
    assert first == {"written": 5, "replaced": 0, "unchanged": 0, "changes": []}

    # same content, different ts -> compared on (verb, value, applied) only: nothing changes,
    # and the ORIGINAL ts is kept on disk (not overwritten by the re-run's ts)
    rows_same = [dict(r, ts="2026-02-02T00:00:00+00:00") for r in rows_v1]
    second = SR.append_rows(tmp, rows_same, replace=True)
    assert second["written"] == 0 and second["replaced"] == 0 and second["unchanged"] == 5 and second["changes"] == []
    stored = [json.loads(l) for l in tmp.read_text().splitlines()]
    assert all(r["ts"] == "2026-01-01T00:00:00+00:00" for r in stored)

    # change one row's value -> replaced, with the NEW ts; the other four stay untouched
    rows_v2 = [dict(r) for r in rows_v1]
    rows_v2[0] = dict(rows_v2[0], value="5", ts="2026-03-03T00:00:00+00:00")
    third = SR.append_rows(tmp, rows_v2, replace=True)
    assert third["written"] == 0 and third["replaced"] == 1 and third["unchanged"] == 4
    assert third["changes"] == [{"id": rows_v1[0]["id"],
                                  "old": {"verb": "hold", "value": "4", "applied": None},
                                  "new": {"verb": "hold", "value": "5", "applied": None}}]
    stored2 = {r["id"]: r for r in (json.loads(l) for l in tmp.read_text().splitlines())}
    assert stored2[rows_v1[0]["id"]]["value"] == "5" and stored2[rows_v1[0]["id"]]["ts"] == "2026-03-03T00:00:00+00:00"
    assert stored2[rows_v1[1]["id"]]["ts"] == "2026-01-01T00:00:00+00:00"


def test_append_rows_default_mode_unchanged_by_replace_kwarg_existing():
    """The pre-existing dupe-skip default (replace=False) must be untouched: same shape,
    same counts, for the live-ingest call site (match_evidence.lift_score_recs)."""
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-09-16T00:00:00+00:00")
    assert SR.append_rows(tmp, rows) == {"written": 5, "dupes": 0}
    assert SR.append_rows(tmp, rows) == {"written": 0, "dupes": 5}


def test_iter_note_paths_finds_amat():
    paths = SR.iter_note_paths("AMAT")
    names = {p.name for p in paths}
    assert "20260515-2Q26.md" in names


def test_lift_score_recs_unchanged_semantics_no_note_id():
    """No note_id/applied given -> pure text parse, no filesystem side effect, same dict
    shape lift_score_recs has always returned: only proposal-worthy verbs, hold/populate excluded."""
    note = (FIX / "full_layout.md").read_text()
    out = M.lift_score_recs(note)
    assert out == {
        "competitive_advantage.innovation_rate": "4+",
        "competitive_advantage.distribution": "3",
        "competitive_advantage.overall": "4",
    }
    assert "ai_positioning" not in out                       # hold at 4 -> reaffirm, no proposal
    assert "potential_investor_interest.score" not in out    # Populate as 5 -> reaffirm, no proposal


def test_lift_score_recs_records_every_verb_when_note_id_given():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    note = (FIX / "full_layout.md").read_text()
    out = M.lift_score_recs(note, note_id="AMAT/20260515-2Q26.md", applied={}, out_path=tmp)
    assert out == {
        "competitive_advantage.innovation_rate": "4+",
        "competitive_advantage.distribution": "3",
        "competitive_advantage.overall": "4",
    }
    lines = [json.loads(l) for l in tmp.read_text().splitlines() if l.strip()]
    verbs = sorted(r["verb"] for r in lines)
    assert verbs == ["drift", "hold", "populate", "propose", "revise"]   # all six-verb reads recorded, not just proposals


if __name__ == "__main__":
    test_full_layout_every_axis_and_verb(); test_propose_initial_score_verb_form()
    test_bold_colon_article_tolerance()
    test_idiom_populate_a_initialize_initiate_establish_initial_score_of()
    test_idiom_populate_b_proposal_forms_and_reaffirm()
    test_idiom_revise_updown_and_quoted_backticked_values()
    test_idiom_revise_from_prior_quoted_value_skips_the_earlier_quote()
    test_line_anchored_hedge_in_reasoning_never_wins_over_true_recommendation()
    test_line_anchored_recap_before_true_recommendation_never_wins()
    test_no_recs_note_yields_no_rows()
    test_parse_note_id_earnings_and_conf(); test_build_rows_shape_and_applied()
    test_append_rows_is_idempotent(); test_iter_note_paths_finds_amat()
    test_append_rows_replace_mode_updates_changed_and_preserves_ts_on_unchanged()
    test_append_rows_default_mode_unchanged_by_replace_kwarg_existing()
    test_lift_score_recs_unchanged_semantics_no_note_id()
    test_lift_score_recs_records_every_verb_when_note_id_given()
    print("OK test_score_reads")
