"""Run directly: python3 scripts/thesis/test_answer.py"""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio   # noqa: E402
from thesis import answer as AN       # noqa: E402


def _fm():
    return {"doc_type": "thesis", "ticker": "TST", "tier": "tier_1_bctk", "drafted": "2026-09-10", "reviewed_by_operator": False,
            "scores": {"ai_positioning": "4"}, "proposed_scores": {"ai_positioning": {"value": "4+", "since": "2026-09-11", "source": "s"}},
            "assumptions": [{"id": "a1", "statement": "S", "derived_from": "d", "themes": [], "challenged_by": ["x"], "confirmed_by": [],
                             "status": "challenged", "status_source": "evidence", "pressure": {"confirm": 0, "challenge": 5, "window_days": 90, "last_evidence": None}, "draft": True}]}


def test_actions(tmp):
    tio.NOTES = tmp / "notes"; AN.QUESTIONS = tmp / "questions.jsonl"
    tio.save("TST", _fm(), "## R\n")
    qs = [{"id": "draft:TST:a1", "kind": "draft_review", "ticker": "TST", "assumption_id": "a1", "text": "?", "asked_at": "t", "answered_at": None, "answer": None},
          {"id": "score:TST:ai_positioning", "kind": "score_proposal", "ticker": "TST", "key": "ai_positioning", "value": "4+", "text": "?", "asked_at": "t", "answered_at": None, "answer": None}]
    AN.QUESTIONS.write_text("".join(json.dumps(q) + "\n" for q in qs))
    assert AN.main(["--id", "draft:TST:a1", "--action", "keep"]) == 0
    a = tio.load("TST")["assumptions"][0]
    assert a["status"] == "challenged" and a["status_source"] == "operator" and a["draft"] is False   # keep = status unchanged, now operator-owned
    assert tio.load("TST")["reviewed_by_operator"] is True
    assert AN.load_questions()[0]["answered_at"] and AN.load_questions()[0]["answer"]["action"] == "keep"
    AN.QUESTIONS.write_text("".join(json.dumps(q) + "\n" for q in qs))
    assert AN.main(["--id", "draft:TST:a1", "--action", "edit", "--text", "New statement"]) == 0
    assert tio.load("TST")["assumptions"][0]["statement"] == "New statement"
    assert AN.main(["--id", "draft:TST:a1", "--action", "retire"]) == 0 and tio.load("TST")["assumptions"][0]["status"] == "retired"
    assert AN.main(["--id", "score:TST:ai_positioning", "--action", "reject"]) == 0 and tio.load("TST")["proposed_scores"] == {}
    assert AN.main(["--id", "nope", "--action", "keep"]) == 1


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_actions(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_answer")
