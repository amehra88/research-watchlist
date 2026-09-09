"""Run directly: python3 scripts/thesis/test_draft_thesis.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import draft_thesis as dt  # noqa: E402

def test_mode_selection():
    assert dt.pick_mode(scores={"ai_positioning": "4"}, earnings_notes=["x"]) == "scores"
    assert dt.pick_mode(scores={}, earnings_notes=["x"]) == "notes"
    assert dt.pick_mode(scores={}, earnings_notes=[]) == "thin"

def test_parse_assumptions_rejects_overreads():
    good = json.dumps({"assumptions": [{"id": "ramp_continues", "statement": "The 800G ramp continues to pull volume.",
        "derived_from": "ai_positioning: 4", "themes": ["ai_infrastructure_capex"],
        "challenged_by": ["capex digestion"], "confirmed_by": ["1.6T design wins"]}]})
    out = dt.parse_assumptions(good)
    assert out[0]["status"] == "open" and out[0]["draft"] is True and out[0]["status_source"] == "draft"
    bad = json.dumps({"assumptions": [{"id": "x", "statement": "Supply remains tight, supporting share.",
        "derived_from": "d", "themes": [], "challenged_by": ["a"], "confirmed_by": []}]})
    try:
        dt.parse_assumptions(bad); assert False, "should reject 'remains'"
    except dt.OverreadError:
        pass

def test_import_draft_doc_has_cohr_and_lite():
    d = dt.import_draft_doc()
    assert "COHR" in d and "LITE" in d
    ids = {a["id"] for a in d["COHR"]}
    assert "chinese_laser_capability" in ids and "datacom_ramp_continues" in ids
    assert all(a["challenged_by"] for t in d.values() for a in t)
    # the doc repeats `chinese_laser_capability` under COHR — must import as ONE assumption
    assert [a["id"] for a in d["COHR"]].count("chinese_laser_capability") == 1
    assert all(a["statement"] for t in d.values() for a in t)
    ps = next(a for a in d["COHR"] if a["id"] == "policy_shelter")
    assert ps["status"] == "retired"

def test_prompt_contains_guardrails():
    p = dt.build_prompt({"ticker": "T", "mode": "scores", "scores": {"ai_positioning": "4"},
                         "scoring_notes": "n", "score_notes": {}, "themes": ["t"], "earnings_notes": [], "mdna": "", "news": []})
    for w in ("watch-item stays a watch-item", "durable", "remains", "offsetting", "JSON"):
        assert w in p

if __name__ == "__main__":
    test_mode_selection(); test_parse_assumptions_rejects_overreads()
    test_import_draft_doc_has_cohr_and_lite(); test_prompt_contains_guardrails()
    print("OK test_draft_thesis")
