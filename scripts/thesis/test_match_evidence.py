"""Run directly: python3 scripts/thesis/test_match_evidence.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import match_evidence as M  # noqa: E402
from thesis.sources import Evidence  # noqa: E402

EV = [Evidence("news", "notes/news/a.md", "COHR", "2026-09-02", "Innolight adds 1.6T capacity", "text a", "u1"),
      Evidence("sec_filing", "pg:d1:8-K body", "COHR", "2026-09-03", "8-K body", "text b", "pg d1")]

def test_parse_verdicts_maps_by_index_and_validates():
    txt = json.dumps({"verdicts": [
        {"i": 0, "assumption_id": "supply_was_tight_at_scoring", "direction": "challenge", "strength": 2, "why": "w", "quote": "q"},
        {"i": 1, "assumption_id": None, "direction": "neutral", "strength": 0, "why": "", "quote": ""},
        {"i": 7, "assumption_id": "x", "direction": "confirm", "strength": 9, "why": "", "quote": ""}]})
    out = M.parse_verdicts(txt, EV, valid_ids={"supply_was_tight_at_scoring"})
    assert len(out) == 2 and out[0]["source_id"] == "notes/news/a.md" and out[0]["strength"] == 2
    assert out[1]["assumption_id"] is None

def test_lift_score_recs():
    note = """## 5. AI positioning signal
- **Current score:** 4
- **Recommendation:** drift to 4+
## 6. Competitive advantage signal
- **Innovation rate** (current: 4)
  - Recommendation: hold
- **Distribution** (current: 3)
  - Recommendation: revise to 4
- **Overall** (current: 4)
  - Recommendation: hold
## 7. Potential investor interest signal
- **Recommendation:** under review
"""
    r = M.lift_score_recs(note)
    assert r == {"ai_positioning": "4+", "competitive_advantage.distribution": "4"}

def test_earnings_break_becomes_strength3_row():
    note = "## 4b. Assumption read\n- supply_was_tight_at_scoring: Challenge — lead times normalised (Q&A)\n- datacom_ramp_continues: Confirm — 1.6T ramping (prepared remarks)\n- other: Silent\n"
    rows = M.rows_from_4b(note, Evidence("earnings_note", "notes/COHR/x.md", "COHR", "2026-09-04", "x", note, "notes/COHR/x.md"),
                          valid_ids={"supply_was_tight_at_scoring", "datacom_ramp_continues", "other"})
    assert {r["source"] for r in rows} == {"earnings_break", "earnings_confirm"} and all(r["strength"] == 3 for r in rows)

def test_prompt_lists_every_assumption_and_item():
    fm = {"ticker": "COHR", "assumptions": [{"id": "a1", "statement": "S1", "challenged_by": ["c"], "confirmed_by": ["k"]}]}
    p = M.build_prompt(fm, EV)
    assert "a1" in p and "[0]" in p and "[1]" in p and "JSON" in p

def test_batches_respect_cap_and_keep_order():
    big = [Evidence("news", f"n{i}", "T", f"2026-09-0{i+1}", "t", "x" * 5000, "r") for i in range(5)]
    bs = M.batches(big, char_cap=12_000)
    assert [len(b) for b in bs] == [2, 2, 1] and bs[0][0].source_id == "n0"

if __name__ == "__main__":
    test_parse_verdicts_maps_by_index_and_validates(); test_lift_score_recs()
    test_earnings_break_becomes_strength3_row(); test_prompt_lists_every_assumption_and_item()
    test_batches_respect_cap_and_keep_order()
    print("OK test_match_evidence")
