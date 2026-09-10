#!/usr/bin/env python3
import json, sys, tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import topic_map as tm


def _u(v):
    v = np.asarray(v, dtype=np.float32); return v / np.linalg.norm(v)


EXCH = [
    {"vector_id": "d1_q1", "ticker": "AAOI", "event_type": "earnings_call", "event_date": "2026-08-06",
     "period_key": "FY2026-Q2", "speaker_type": "analyst", "speaker_firm": "Raymond James",
     "text": "Can you talk about the new laser manufacturing capacity coming out of China and what it means for pricing?"},
    {"vector_id": "d1_a1", "ticker": "AAOI", "event_type": "earnings_call", "event_date": "2026-08-06",
     "period_key": "FY2026-Q2", "speaker_type": "corprep", "speaker_firm": None,
     "text": "We do see new laser suppliers emerging from China, although qualification cycles remain long for datacom."},
    {"vector_id": "d1_op", "ticker": "AAOI", "event_type": "earnings_call", "event_date": "2026-08-06",
     "period_key": "FY2026-Q2", "speaker_type": "operator", "speaker_firm": None, "text": "Next question."},
    {"vector_id": "d2_q1", "ticker": "LITE", "event_type": "conference", "event_date": "2026-06-09",
     "period_key": "CY2026-Q2", "speaker_type": "analyst", "speaker_firm": "Mizuho",
     "text": "How do you think about Chinese competitors in lasers over the next couple of years and the risk to share?"},
    {"vector_id": "d2_q2", "ticker": "LITE", "event_type": "conference", "event_date": "2026-06-09",
     "period_key": "CY2026-Q2", "speaker_type": "analyst", "speaker_firm": "Mizuho", "text": "Great, thanks. That's helpful."},
]


def test_units_from_exchanges_types_registers_and_skips_operator():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exchanges.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in EXCH) + "\n")
        units, skipped = tm.units_from_exchanges(p)
    assert [u.id for u in units] == ["d1_q1", "d1_a1", "d2_q1"] and skipped == 2   # operator turn + acknowledgement
    assert units[0].register == "question" and units[1].register == "evidence"
    assert units[0].firm == "Raymond James" and units[1].firm is None
    assert units[2].period_key == "CY2026-Q2"


def test_assign_returns_themes_at_or_above_threshold_best_first_capped():
    names = ["a", "b", "c", "d"]
    out = tm.assign(np.array([0.7, 0.9, 0.85, 0.3]), names, thr=0.6, top=2)
    assert out == [("b", 0.9), ("c", 0.85)]
    assert tm.assign(np.array([0.1, 0.2, 0.3, 0.4]), names, thr=0.6) == []


def test_cluster_candidates_greedy_leader_groups_by_cosine():
    V = np.vstack([_u([1, 0, 0]), _u([0.95, 0.05, 0]), _u([0, 1, 0]), _u([0.05, 0.95, 0]), _u([0, 0, 1])])
    cl = tm.cluster_candidates(V, min_sim=0.9)
    assert sorted(sorted(c) for c in cl) == [[0, 1], [2, 3], [4]]


def test_build_candidates_applies_company_and_bank_floors_and_labels():
    units = [tm.Unit("q1", "neocloud demand for gpus", "question", "NVDA", "earnings_call", "2026-05-28", "FY2027-Q1", "Bernstein", "exchange"),
             tm.Unit("q2", "neocloud demand is strong", "question", "CRWV", "conference", "2026-09-08", "CY2026-Q3", "Goldman", "exchange"),
             tm.Unit("q3", "neocloud customers renting gpus", "question", "NBIS", "conference", "2026-09-09", "CY2026-Q3", "Goldman", "exchange"),
             tm.Unit("a1", "we sell to neoclouds", "evidence", "NVDA", "earnings_call", "2026-05-28", "FY2027-Q1", None, "exchange"),
             tm.Unit("q4", "solar tariffs?", "question", "ENPH", "earnings_call", "2026-07-30", "FY2026-Q2", "JPM", "exchange")]
    texts = [u.text for u in units]
    df = tm.tp.doc_frequencies(texts)
    cands = tm.build_candidates([[0, 1, 2, 3], [4]], units, texts, df, len(texts), min_companies=3, min_banks=2)
    assert len(cands) == 1
    c = cands[0]
    assert c["id"] == "cand:q1" and c["n_companies"] == 3 and c["n_banks"] == 2 and c["n_exchanges"] == 4
    assert c["first_seen"] == "2026-05-28" and c["status"] == "pending" and "neocloud" in " ".join(c["ngrams"])
    assert sorted(c["members"]) == ["a1", "q1", "q2", "q3"] and len(c["examples"]) <= 3


def test_evidence_only_clusters_survive_the_gate_as_stage_one_candidates():
    # spec §6.3 stage 1 = evidence exists, zero analyst questions. A bank test would discard
    # exactly that signal (learning from the 2026-08 branch, "silence IS stage 1")
    ev = [tm.Unit(f"a{i}", f"we are ramping co-packaged optics with customer {i} this year", "evidence",
                  t, "earnings_call", "2026-05-0%d" % (i + 1), "FY2026-Q2", None, "exchange")
          for i, t in enumerate(["COHR", "LITE", "FN"])]
    qs = [tm.Unit(f"q{i}", f"how are you thinking about pricing this year for segment {i}", "question",
                  t, "earnings_call", "2026-05-0%d" % (i + 1), "FY2026-Q2", "OneBank", "exchange")
          for i, t in enumerate(["AMD", "ARM", "INTC"])]
    units = ev + qs
    texts = [u.text for u in units]; df = tm.tp.doc_frequencies(texts)
    cands = tm.build_candidates([[0, 1, 2], [3, 4, 5]], units, texts, df, len(texts), min_companies=3, min_banks=2)
    assert [c["register"] for c in cands] == ["evidence_only"]        # 3 companies, 0 banks -> kept
    assert cands[0]["n_banks"] == 0 and cands[0]["n_companies"] == 3  # the question cluster (1 bank) is not
    mixed = tm.build_candidates([[0, 1, 2, 3, 4, 5]], units, texts, df, len(texts), min_companies=3, min_banks=2)
    assert mixed == []                                                # has questions -> bank test applies


def test_calendar_quarter_from_event_date_on_every_row():
    assert tm.calendar_quarter("2026-09-08") == "CY2026-Q3" and tm.calendar_quarter("2026-01-31") == "CY2026-Q1"
    assert tm.calendar_quarter(None) is None
    names = ["a"]; A = np.vstack([_u([1, 0, 0, 0])])
    units = [tm.Unit("q1", "eight words are needed for a unit to count", "question", "X", "conference", "2026-06-09", "FY2027-Q1", "F", "exchange")]
    rows, _ = tm.map_units(units, FakeStore({"q1": _u([1, 0, 0, 0])}), names, A, thr=0.5)
    assert rows[0]["cal_quarter"] == "CY2026-Q2" and rows[0]["period_key"] == "FY2027-Q1"


def test_map_units_threshold_per_source():
    names = ["a"]; A = np.vstack([_u([1, 0, 0, 0])])
    v = _u([0.7, 0.714, 0, 0])                          # cosine ~0.70 to anchor a
    ex = tm.Unit("x1", "eight words are needed for a unit to count here", "question", "X", "conference", "2026-06-09", "CY2026-Q2", "F", "exchange")
    md = tm.Unit("m1", "eight words are needed for a unit to count here", "evidence", "X", "10-Q", "2026-06-09", "2026Q2", None, "mdna")
    store = FakeStore({"x1": v, "m1": v})
    rows, _ = tm.map_units([ex, md], store, names, A, thr={"exchange": 0.6, "mdna": 0.8, "default": 0.6})
    by = {r["id"]: r for r in rows}
    assert by["x1"]["themes"] and not by["m1"]["themes"]
    assert by["x1"]["threshold"] == 0.6 and by["m1"]["threshold"] == 0.8
    rows2, _ = tm.map_units([ex, md], store, names, A, thr=0.6)     # a float still works everywhere
    assert all(r["themes"] for r in rows2)


def test_reattach_decisions_survives_cluster_growth():
    # a rejected moderator cluster grows every week; containment of the decided members
    # (not Jaccard) is what keeps it rejected — Jaccard 3/10 would resurface it
    cands = [{"id": "cand:m1", "members": [f"m{i}" for i in range(1, 11)], "status": "pending", "name": None}]
    decisions = [{"id": "cand:m1", "members": ["m1", "m2", "m3"], "status": "rejected", "name": None, "ts": "t"}]
    assert tm.reattach_decisions(cands, decisions)[0]["status"] == "rejected"
    # but a decision whose members mostly left the cluster does not attach
    decisions = [{"id": "cand:x", "members": ["m1", "z2", "z3", "z4"], "status": "rejected", "name": None, "ts": "t"}]
    cands[0]["status"] = "pending"
    assert tm.reattach_decisions(cands, decisions)[0]["status"] == "pending"


def test_carry_suggestions_from_previous_candidates():
    prev = [{"id": "cand:q1", "members": ["q1", "q2", "q3"], "suggested_name": "neocloud_demand", "suggested_why": "w"}]
    cands = [{"id": "cand:q1", "members": ["q1", "q2", "q3", "q4", "q5"], "suggested_name": None},
             {"id": "cand:z1", "members": ["z1", "z2"], "suggested_name": None}]
    out = tm.carry_suggestions(cands, prev)
    assert out[0]["suggested_name"] == "neocloud_demand" and out[0]["suggested_why"] == "w"
    assert out[1]["suggested_name"] is None


def test_reattach_decisions_by_member_overlap():
    cands = [{"id": "cand:q1", "members": ["q1", "q2", "q3", "a1"], "status": "pending", "name": None},
             {"id": "cand:q9", "members": ["q9"], "status": "pending", "name": None}]
    decisions = [{"id": "cand:q0", "members": ["q1", "q2", "q3"], "status": "accepted", "name": "neocloud_demand", "ts": "t"},
                 {"id": "cand:zz", "members": ["z1", "z2"], "status": "rejected", "name": None, "ts": "t"}]
    out = tm.reattach_decisions(cands, decisions)
    assert out[0]["status"] == "accepted" and out[0]["name"] == "neocloud_demand"
    assert out[1]["status"] == "pending"


class FakeStore:
    def __init__(self, vecs): self.v = vecs; self.ids = list(vecs)
    def ensure(self, items, **kw): return 0
    def matrix(self, ids): return np.vstack([self.v[i] for i in ids])


def test_cluster_candidates_uses_centered_vectors_when_a_mean_is_given():
    # two units that look alike only through the shared component must NOT cluster
    common = np.array([10.0, 10.0, 0.0, 0.0], dtype=np.float32)
    raw = np.vstack([common + [1, 0, 0, 0], common + [0, 1, 0, 0]])
    V = np.vstack([_u(r) for r in raw])
    assert tm.cluster_candidates(V, 0.9) == [[0, 1]]                                  # uncentered: same cluster
    assert tm.cluster_candidates(tm.center(raw, raw.mean(axis=0)), 0.9) == [[0], [1]]   # mean on the raw scale


def test_map_units_assigns_mapped_and_clusters_the_rest_deterministically():
    names = ["china_laser_competition", "pc_demand"]
    A = np.vstack([_u([1, 0, 0, 0]), _u([0, 1, 0, 0])])
    units = [tm.Unit("q1", "lasers from china", "question", "AAOI", "earnings_call", "2026-08-06", "FY2026-Q2", "RJ", "exchange"),
             tm.Unit("q2", "neoclouds", "question", "NVDA", "earnings_call", "2026-05-28", "FY2027-Q1", "Bernstein", "exchange"),
             tm.Unit("q3", "neoclouds again", "question", "CRWV", "conference", "2026-09-08", "CY2026-Q3", "GS", "exchange")]
    store = FakeStore({"q1": _u([0.95, 0.05, 0, 0]), "q2": _u([0, 0, 1, 0]), "q3": _u([0, 0, 0.98, 0.02])})
    rows, cands = tm.map_units(units, store, names, A, thr=0.8, min_sim=0.9, min_companies=2, min_banks=2)
    assert rows[0]["themes"] == [{"theme": "china_laser_competition", "score": round(float(0.95 / np.linalg.norm([0.95, 0.05])), 4)}]
    assert rows[1]["themes"] == [] and rows[1]["candidate"] == "cand:q2" and rows[2]["candidate"] == "cand:q2"
    assert cands[0]["n_companies"] == 2 and cands[0]["n_banks"] == 2
    rows2, cands2 = tm.map_units(units, store, names, A, thr=0.8, min_sim=0.9, min_companies=2, min_banks=2)
    assert rows2 == rows and cands2 == cands                    # idempotent


def test_record_decision_appends_with_members_and_updates_candidates():
    with tempfile.TemporaryDirectory() as d:
        cp, dp = Path(d) / "candidates.json", Path(d) / "decisions.jsonl"
        cp.write_text(json.dumps([{"id": "cand:q1", "members": ["q1", "q2"], "status": "pending", "name": None}]))
        dec = tm.record_decision("cand:q1", "accepted", "neocloud_demand", cp, dp)
        assert dec["members"] == ["q1", "q2"] and dec["name"] == "neocloud_demand"
        assert json.loads(cp.read_text())[0]["status"] == "accepted"
        assert json.loads(dp.read_text().splitlines()[0])["id"] == "cand:q1"
        try:
            tm.record_decision("cand:nope", "rejected", None, cp, dp); assert False
        except KeyError:
            pass


def test_suggest_names_only_for_pending_and_parses_slug():
    cands = [{"id": "cand:q1", "status": "pending", "ngrams": ["neocloud demand"], "examples": [{"text": "x"}], "suggested_name": None, "name": None},
             {"id": "cand:q2", "status": "rejected", "ngrams": ["y"], "examples": [], "suggested_name": None, "name": None}]
    calls = []
    def runner(prompt):
        calls.append(prompt); return "NAME: Neocloud GPU Demand\nWHY: analysts ask about neocloud capacity"
    out = tm.suggest_names(cands, runner=runner)
    assert len(calls) == 1 and out[0]["suggested_name"] == "neocloud_gpu_demand" and out[1]["suggested_name"] is None


def test_default_runner_uses_the_lean_wrapper_contract():
    # 2026-09-10 first names pass: every call failed with "pass exactly one of system_prompt=
    # (lean), tools= (mcp), ..." because tools="" was passed alongside system_prompt
    from lib import claude_p
    seen = {}
    def fake_run(prompt, **kw):
        seen.update(kw); return ("NAME: x\nWHY: y", 0.0, {})
    orig = claude_p.run; claude_p.run = fake_run
    try:
        assert tm._default_runner("p").startswith("NAME:")
    finally:
        claude_p.run = orig
    assert seen.get("system_prompt") and "tools" not in seen and "mcp_tool" not in seen
    assert seen.get("model") == "claude-haiku-4-5-20251001"


def test_write_report_leads_with_h2_and_prints_denominators():
    rows = [{"id": "q1", "register": "question", "themes": [{"theme": "a", "score": 0.9}], "candidate": None, "ticker": "X", "period_key": "FY2026-Q2", "firm": "F"},
            {"id": "q2", "register": "question", "themes": [], "candidate": "cand:q2", "ticker": "Y", "period_key": "FY2026-Q2", "firm": "G"},
            {"id": "a1", "register": "evidence", "themes": [], "candidate": None, "ticker": "X", "period_key": "FY2026-Q2", "firm": None}]
    cands = [{"id": "cand:q2", "label": "neocloud", "ngrams": ["neocloud"], "n_exchanges": 1, "n_companies": 1, "n_banks": 1,
              "tickers": ["Y"], "firms": ["G"], "first_seen": "2026-05-28", "members": ["q2"], "status": "pending", "name": None,
              "suggested_name": "neocloud_demand", "examples": [{"id": "q2", "ticker": "Y", "date": "2026-05-28", "firm": "G", "text": "neoclouds?"}]}]
    meta = {"threshold": 0.72, "names": ["a"], "n_test": 100, "calibration": [{"threshold": 0.72, "precision": 0.7, "recall": 0.5, "f1": 0.58, "coverage": 0.8}]}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "r.md"
        text = tm.write_report(rows, cands, meta, skipped=7, path=p)
    assert text.startswith("## ") and "question register: 1/2 mapped" in text and "evidence register: 0/1 mapped" in text
    assert "7 rows skipped" in text and "cand:q2" in text and "neocloud_demand" in text and "0.72" in text



def test_units_from_claims_drops_housekeeping_and_short_blocks():
    claims = [
        {"claim_id": "c1", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Demand for our datacom transceivers continued to exceed our capacity as hyperscale customers accelerated deployments of AI clusters."},
        {"claim_id": "c2", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Our 4.00% convertible senior notes due 2031 carry an aggregate principal amount that remains outstanding as of quarter end."},
        {"claim_id": "c3", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Too short to count."},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"; p.write_text("\n".join(json.dumps(c) for c in claims) + "\n")
        units, skipped = tm.units_from_claims(p)
        assert tm.units_from_claims(Path(d) / "missing.jsonl") == ([], 0)
    assert [u.id for u in units] == ["c1"] and skipped == 2
    u = units[0]
    assert u.register == "evidence" and u.source == "mdna" and u.firm is None
    assert u.event_date == "2026-05-06" and u.period_key == "2026Q2" and u.event_type == "10-Q"


def test_is_housekeeping_catches_expense_line_and_cash_flow_commentary():
    # first combined map 2026-09-10: 12 MD&A-only candidate clusters were all of this kind
    for txt in ("Research and development expenses increased $12.4 million for the six months ended June 30",
                "General and administrative expenses increased primarily due to personnel costs",
                "Sales and marketing expenses increased due to events and headcount",
                "Net cash used in investing activities was $310 million for the nine months",
                "We declared a quarterly cash dividend of $0.20 per share to stockholders of record on August 15",
                "The One Big Beautiful Bill Act (OBBBA) was enacted in July with provisions affecting bonus depreciation",
                "Depreciation expense increased due to capital expenditures placed in service"):
        assert tm.is_housekeeping(txt), txt


def test_is_housekeeping_keeps_capex_prose():
    assert tm.is_housekeeping("we recorded an impairment charge related to goodwill")
    assert not tm.is_housekeeping("cash paid for property and equipment was $7.7 billion, reflecting data center capacity additions")

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for f in fns:
        try:
            f(); print(f"  ✓ {f.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1; print(f"  ✗ {f.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns)-bad}/{len(fns)} pass"); sys.exit(1 if bad else 0)
