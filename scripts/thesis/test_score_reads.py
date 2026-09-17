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
    test_bold_colon_article_tolerance(); test_no_recs_note_yields_no_rows()
    test_parse_note_id_earnings_and_conf(); test_build_rows_shape_and_applied()
    test_append_rows_is_idempotent(); test_iter_note_paths_finds_amat()
    test_lift_score_recs_unchanged_semantics_no_note_id()
    test_lift_score_recs_records_every_verb_when_note_id_given()
    print("OK test_score_reads")
