"""Run directly: python3 scripts/thesis/test_thesis_report.py  (hermetic: tmp state + notes)"""
import json, shutil, sys, tempfile
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio                 # noqa: E402
from thesis import thesis_report as R               # noqa: E402

TODAY = date(2026, 9, 14)


def _fm(t, extra=None):
    fm = {"doc_type": "thesis", "ticker": t, "tier": "tier_1_bctk", "drafted": "2026-09-10", "reviewed_by_operator": False,
          "scores": {"ai_positioning": "4", "potential_investor_interest.score": "4"}, "proposed_scores": {},
          "assumptions": [{"id": "a1", "statement": "S1", "derived_from": "ai_positioning: 4", "themes": ["ai_infrastructure_capex"],
                           "challenged_by": ["x"], "confirmed_by": ["y"], "status": "open", "status_source": "draft",
                           "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None}, "draft": True}]}
    fm.update(extra or {}); return fm


def setup(tmp):
    R.STATE_DIR = tmp / "state"; R.NOTES = tio.NOTES = tmp / "notes"; R.REPORTS_DIR = tmp / "notes" / "reports"
    R.STATE_DIR.mkdir(parents=True)
    tio.save("AAA", _fm("AAA", {"proposed_scores": {"ai_positioning": {"value": "4+", "since": "2026-09-11", "source": "notes/AAA/20260911-2Q27.md"}}}), "## Rationale\n")
    tio.save("BBB", _fm("BBB"), "## Rationale\n")
    tio.save("CCC", _fm("CCC", {"drafted": "2026-01-01"}), "## Rationale\n")
    ev = [{"ts": "2026-09-11T10:00:00+00:00", "ticker": "AAA", "source": "news", "source_id": "n1", "ref": "u1", "date": "2026-09-11", "title": "t",
           "assumption_id": "a1", "direction": "challenge", "strength": 3, "why": "w", "quote": "", "cross_ticker": False},
          {"ts": "2026-09-12T10:00:00+00:00", "ticker": "AAA", "source": "sec_filing", "source_id": "s1", "ref": "u2", "date": "2026-09-12", "title": "t",
           "assumption_id": "a1", "direction": "challenge", "strength": 2, "why": "w2", "quote": "", "cross_ticker": False},
          {"ts": "2026-09-12T10:00:00+00:00", "ticker": "BBB", "source": "news", "source_id": "n2", "ref": "u3", "date": "2026-09-12", "title": "t",
           "assumption_id": None, "direction": "neutral", "strength": 0, "why": "", "quote": "", "cross_ticker": False}]
    chg = [{"ts": "2026-09-12T10:00:01+00:00", "ticker": "AAA", "kind": "status", "assumption_id": "a1", "from": "open", "to": "challenged", "evidence_ids": ["n1", "s1"]},
           {"ts": "2026-09-11T10:00:01+00:00", "ticker": "AAA", "kind": "proposed_score", "key": "ai_positioning", "value": "4+", "source": "notes/AAA/20260911-2Q27.md"}]
    (R.STATE_DIR / "evidence_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in ev))
    (R.STATE_DIR / "changes.jsonl").write_text("".join(json.dumps(r) + "\n" for r in chg))
    R.send = lambda subject, body: 200
    R.storeb_context = lambda t: ["Store B stubbed"]
    R.coverage = lambda theses, ev, since, until: {"evidence_by_source": {"news": 2}, "matched": 2, "no_thesis": [], "reviewer": {}, "storeb_as_of": "stub"}


def test_score_num():
    assert R.score_num("4+") == 4.25 and R.score_num("4-") == 3.75 and R.score_num("4") == 4.0 and R.score_num("x") is None


def test_movers_ranking_is_deterministic_and_signed():
    ctx = R.build_context("weekly", TODAY, "2026-09-08", "2026-09-14")
    m = ctx["movers"]
    assert m[0]["ticker"] == "AAA" and m[0]["delta"] == -3 + 2 - 5   # status -3, score up +2, pressure -5 (capped)
    assert "a1 open→challenged" in m[0]["why"]
    assert [x["ticker"] for x in ctx["all"]] == [x["ticker"] for x in R.rank_movers(ctx["theses"], ctx["evidence"], R._read_jsonl(R.STATE_DIR / "changes.jsonl"), "2026-09-08", "2026-09-14")]
    assert ctx["quiet"] == ["CCC"] and "BBB" in [x["ticker"] for x in m]   # BBB had evidence (neutral) → listed, not quiet
    assert ctx["ranking"][0]["rank_score_proposed"] == 4.125             # (4.25 + 4) / 2 for AAA


def test_render_leads_with_h2_and_wikilinks():
    ctx = R.build_context("weekly", TODAY, "2026-09-08", "2026-09-14")
    md, txt = R.render(ctx, wiki=True), R.render(ctx, wiki=False)
    assert md.startswith("## Thesis delta") and "[[AAA]]" in md and "[[AAA/_thesis]]" in md
    assert "[[" not in txt and "notes/AAA/_thesis.md" in txt
    assert "## 4. Pending score proposals" in txt and "apply_scores.py --accept AAA" in txt
    assert "## 5. Drafts needing your eye" in txt and "AAA a1" in txt      # draft:true + first hit this period
    assert "CCC a1" in txt and "d)" in txt                                   # stale (drafted 2026-01-01, no evidence)
    assert "## 3. Themes" in txt and "ai_infrastructure_capex" in txt


def test_weekly_writes_note_ranking_questions_ledger():
    R.run_report("weekly", TODAY, None, dry_run=False)
    assert (R.REPORTS_DIR / "thesis-delta-20260914.md").exists()
    rk = json.loads((R.STATE_DIR / "ranking_2026-09-14.json").read_text())
    assert rk["ranking"][0]["ticker"] == "AAA"
    qs = R._read_jsonl(R.STATE_DIR / "questions.jsonl")
    assert {q["id"] for q in qs} >= {"draft:AAA:a1", "score:AAA:ai_positioning", "stale:CCC:a1"}
    sent = R._read_jsonl(R.STATE_DIR / "reports_sent.jsonl")
    assert sent[-1]["kind"] == "weekly" and sent[-1]["date"] == "2026-09-14"
    R.run_report("weekly", TODAY, None, dry_run=False)                       # idempotent questions
    assert len(R._read_jsonl(R.STATE_DIR / "questions.jsonl")) == len(qs)


def test_alerts_fire_once():
    calls = []
    R.send = lambda s, b: calls.append((s, b)) or 200
    ev = R.alert_events("2026-09-01T00:00:00+00:00", TODAY)
    ids = {e["id"] for e in ev}
    assert any(i.startswith("status:AAA:a1:challenged") for i in ids) and any(i.startswith("score:AAA:ai_positioning") for i in ids) and any(i.startswith("chal3:AAA:n1") for i in ids)
    R.ALERT_LOOKBACK_DAYS = 10_000                                           # fixture rows are older than 3 days
    assert R.run_alerts(TODAY, dry_run=False) == 0 and len(calls) == 1 and "Thesis alert" in calls[0][0]
    assert R.run_alerts(TODAY, dry_run=False) == 0 and len(calls) == 1     # ledger blocks the repeat


def test_quarterly_due_rule(tmp):
    theses = R.load_theses()
    R.quarterly_t1 = lambda: ["AAA", "BBB", "CCC"]
    for t, d in (("AAA", "20260801"), ("BBB", "20260805")):
        (R.NOTES / t / f"{d}-2Q27.md").write_text("## 1.\n")
    assert R.quarterly_due(date(2026, 8, 25), theses) is True               # 2/3 reported, newest 20d old, none sent
    assert R.quarterly_due(date(2026, 8, 10), theses) is False              # newest only 5d old
    R._append(R.STATE_DIR / "reports_sent.jsonl", [{"kind": "quarterly", "date": "2026-08-20"}])
    assert R.quarterly_due(date(2026, 8, 25), theses) is False              # sent 5d ago


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        setup(tmp)
        test_score_num(); test_movers_ranking_is_deterministic_and_signed(); test_render_leads_with_h2_and_wikilinks()
        test_weekly_writes_note_ranking_questions_ledger(); test_alerts_fire_once(); test_quarterly_due_rule(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_thesis_report")
