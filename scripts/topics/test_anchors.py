#!/usr/bin/env python3
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchors as an


def test_theme_names_flattens_categories_in_order():
    wl = {"themes": {"demand": ["pc_demand", "ad_market_strength"], "supply": ["foundry_capacity"]}}
    assert an.theme_names(wl) == ["pc_demand", "ad_market_strength", "foundry_capacity"]


def test_parse_vec_reads_pgvector_text():
    v = an.parse_vec("[0.5,-1,2.25]")
    assert v.dtype == np.float32 and v.tolist() == [0.5, -1.0, 2.25]


def _unit(v):
    v = np.asarray(v, dtype=np.float32); return v / np.linalg.norm(v)


def test_calibrate_and_choose_threshold_on_separable_synthetic_data():
    names = ["a", "b"]
    A = np.vstack([_unit([1, 0, 0]), _unit([0, 1, 0])])
    test = [("c1", ["a"], _unit([0.9, 0.1, 0])), ("c2", ["b"], _unit([0.1, 0.9, 0])),
            ("c3", ["a", "b"], _unit([0.7, 0.7, 0])), ("c4", ["a"], _unit([0, 0, 1]))]  # c4: unmappable
    rows = an.calibrate(A, names, test, thresholds=[0.5, 0.9, 0.99])
    by = {r["threshold"]: r for r in rows}
    assert by[0.5]["recall"] > by[0.99]["recall"] and by[0.99]["precision"] >= by[0.5]["precision"]
    assert by[0.5]["coverage"] == 0.75                      # c4 assigned nothing at any threshold
    thr = an.choose_threshold(rows, min_precision=0.6)
    assert thr in (0.5, 0.9)                                # highest-F1 row with precision >= 0.6


def test_centering_removes_the_shared_component():
    # measured 2026-09-10: raw centroids of 62 themes all sit within cosine 0.74 of every chunk
    # (P=0.07 at every threshold <= 0.74) — one shared component dominates. Subtracting the
    # centroid mean before normalising is what makes the anchors directional.
    common = np.array([10, 10, 0, 0], dtype=np.float32)
    A_raw = np.vstack([common + [1, 0, 0, 0], common + [0, 1, 0, 0]])
    u = (common + [0.9, 0, 0, 0])[None]
    assert an.score_matrix(u, A_raw).min() > 0.99            # indistinguishable uncentered
    S = an.score_matrix(u, A_raw, mean=A_raw.mean(axis=0))
    assert S[0, 0] > 0.9 and S[0, 1] < 0.0


def test_group_of_doc_type_and_per_group_thresholds():
    assert an.group_of("earnings_transcript") == "transcript" and an.group_of("conference_transcript") == "transcript"
    assert an.group_of("sec_filing") == "sec_filing" and an.group_of("news") == "news" and an.group_of("podcast_summary") == "other"
    names = ["a", "b"]
    A = np.vstack([_unit([1, 0, 0]), _unit([0, 1, 0])])
    test = [("c1", ["a"], _unit([0.9, 0.1, 0]), "sec_filing"), ("c2", ["b"], _unit([0.1, 0.9, 0]), "sec_filing"),
            ("c3", ["a"], _unit([0.95, 0.05, 0]), "news"), ("c4", ["a"], _unit([0, 0, 1]), "earnings_transcript")]
    by = an.calibrate_by_group(A, names, test, thresholds=[0.5, 0.9])
    assert set(by) == {"sec_filing", "news", "transcript"} and by["sec_filing"][0]["coverage"] == 1.0
    # 4-tuples (with doc_type) and 3-tuples both calibrate
    assert an.calibrate(A, names, [x[:3] for x in test], thresholds=[0.5])[0]["coverage"] == 0.75
    thr = an.thresholds_by_source({"sec_filing": [{"threshold": 0.3, "precision": 0.22, "recall": 0.4, "f1": 0.29, "coverage": 0.97},
                                                  {"threshold": 0.42, "precision": 0.39, "recall": 0.22, "f1": 0.28, "coverage": 0.83}],
                                   "transcript": [{"threshold": 0.3, "precision": 0.9, "recall": 0.9, "f1": 0.9, "coverage": 0.9}]},
                                  n_by_group={"sec_filing": 829, "transcript": 72}, global_thr=0.30)
    assert thr["mdna"] == 0.42                        # sec_filing floor 0.35 -> the precise row wins
    assert thr["exchange"] == 0.30                    # 72 transcript chunks < MIN_GROUP_TEST -> global


def test_choose_threshold_falls_back_to_most_precise_when_floor_unmet():
    rows = [{"threshold": 0.5, "precision": 0.3, "recall": 0.9, "f1": 0.45, "coverage": 1.0},
            {"threshold": 0.8, "precision": 0.5, "recall": 0.2, "f1": 0.29, "coverage": 0.3}]
    assert an.choose_threshold(rows, min_precision=0.6) == 0.8


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for f in fns:
        try:
            f(); print(f"  ✓ {f.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1; print(f"  ✗ {f.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns)-bad}/{len(fns)} pass"); sys.exit(1 if bad else 0)
