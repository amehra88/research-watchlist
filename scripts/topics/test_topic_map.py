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
     "period_key": "FY2026-Q2", "speaker_type": "analyst", "speaker_firm": "Raymond James", "text": "Chinese laser competition?"},
    {"vector_id": "d1_a1", "ticker": "AAOI", "event_type": "earnings_call", "event_date": "2026-08-06",
     "period_key": "FY2026-Q2", "speaker_type": "corprep", "speaker_firm": None, "text": "We see new lasers from China."},
    {"vector_id": "d1_op", "ticker": "AAOI", "event_type": "earnings_call", "event_date": "2026-08-06",
     "period_key": "FY2026-Q2", "speaker_type": "operator", "speaker_firm": None, "text": "Next question."},
    {"vector_id": "d2_q1", "ticker": "LITE", "event_type": "conference", "event_date": "2026-06-09",
     "period_key": "CY2026-Q2", "speaker_type": "analyst", "speaker_firm": "Mizuho", "text": "Chinese competitors in lasers?"},
]


def test_units_from_exchanges_types_registers_and_skips_operator():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exchanges.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in EXCH) + "\n")
        units, skipped = tm.units_from_exchanges(p)
    assert [u.id for u in units] == ["d1_q1", "d1_a1", "d2_q1"] and skipped == 1
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


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for f in fns:
        try:
            f(); print(f"  ✓ {f.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1; print(f"  ✗ {f.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns)-bad}/{len(fns)} pass"); sys.exit(1 if bad else 0)
