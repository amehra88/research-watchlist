"""No pytest in this env — run directly:  python3 scripts/thesis/test_thesis_io.py"""
import os, sys, tempfile, shutil
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio  # noqa: E402

def _fm():
    return {"doc_type": "thesis", "ticker": "TEST", "tier": "tier_1_bctk",
            "drafted": "2026-09-10", "reviewed_by_operator": False,
            "scores": {k: "4" for k in tio.SCORE_KEYS}, "proposed_scores": {},
            "assumptions": [{"id": "a1", "statement": "S", "derived_from": "ai_positioning: 4",
                             "themes": [], "challenged_by": ["x"], "confirmed_by": ["y"],
                             "status": "open", "status_source": "draft",
                             "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None},
                             "draft": True}]}

def test_roundtrip_preserves_body(tmp):
    tio.NOTES = tmp
    p = tio.save("TEST", _fm(), body="## Rationale\n\nhand-written\n")
    assert p.name == "_thesis.md" and p.parent.name == "TEST"
    fm2 = tio.load("TEST")
    assert fm2["assumptions"][0]["id"] == "a1"
    assert fm2["_body"].strip() == "## Rationale\n\nhand-written"
    fm2["assumptions"][0]["status"] = "confirmed"
    tio.save("TEST", fm2)            # body=None -> preserved
    assert "hand-written" in tio.load("TEST")["_body"]

def test_validate_catches_bad_status_and_dup_ids():
    fm = _fm(); fm["assumptions"].append(dict(fm["assumptions"][0]))
    fm["assumptions"][1]["status"] = "maybe"
    errs = tio.validate(fm)
    assert any("duplicate id" in e for e in errs) and any("status" in e for e in errs)

def test_pressure_rule_needs_two_sources():
    fm = _fm(); today = date(2026, 9, 10)
    rows = [{"assumption_id": "a1", "direction": "challenge", "strength": 3, "source": "news", "date": "2026-09-01"},
            {"assumption_id": "a1", "direction": "challenge", "strength": 2, "source": "news", "date": "2026-09-02"}]
    tio.recompute_pressure(fm, rows, today)
    assert fm["assumptions"][0]["status"] == "open"          # one source only
    rows.append({"assumption_id": "a1", "direction": "challenge", "strength": 1, "source": "sec_filing", "date": "2026-09-03"})
    tio.recompute_pressure(fm, rows, today)
    a = fm["assumptions"][0]
    assert a["status"] == "challenged" and a["status_source"] == "evidence"
    assert a["pressure"]["challenge"] == 6 and a["pressure"]["last_evidence"] == "2026-09-03"
    assert fm["_changes"][0]["assumption_id"] == "a1"

def test_operator_status_is_never_overridden():
    fm = _fm(); fm["assumptions"][0]["status_source"] = "operator"
    rows = [{"assumption_id": "a1", "direction": "challenge", "strength": 3, "source": "earnings_break", "date": "2026-09-01"}]
    tio.recompute_pressure(fm, rows, date(2026, 9, 10))
    assert fm["assumptions"][0]["status"] == "open"

def test_old_evidence_outside_window_ignored():
    fm = _fm()
    rows = [{"assumption_id": "a1", "direction": "confirm", "strength": 3, "source": "news", "date": "2026-01-01"}]
    tio.recompute_pressure(fm, rows, date(2026, 9, 10))
    assert fm["assumptions"][0]["pressure"]["confirm"] == 0

if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_roundtrip_preserves_body(tmp)
        test_validate_catches_bad_status_and_dup_ids()
        test_pressure_rule_needs_two_sources()
        test_operator_status_is_never_overridden()
        test_old_evidence_outside_window_ignored()
    finally:
        shutil.rmtree(tmp)
    print("OK test_thesis_io")
