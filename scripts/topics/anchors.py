#!/usr/bin/env python3
"""Theme anchors for topic mapping.

Each of the watchlist's themes becomes a centroid of the chunk embeddings pg already
holds under that label (chunks.themes × chunks.embedding; ~114K labelled vectors,
rarest theme ~290). Mapping new text to these centroids keeps continuity with every
existing assignment (spec §4.2 step 3). The cosine threshold is not chosen a priori
(spec §12): chunks are split 80/20 by a stable hash of chunk_id, centroids come from
the 80, and precision/recall are measured on the 20 across a sweep.

    python3 scripts/topics/anchors.py --build            # writes state/topics/anchors.npy + anchors_meta.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
import pgconn  # noqa: E402

STATE = REPO / "state" / "topics"
WATCHLIST = REPO / "config" / "watchlist.yaml"
THRESHOLDS = [round(x, 2) for x in np.arange(0.10, 0.62, 0.02)]   # centered cosines are small: 0.5 already maps <30%


def theme_names(watchlist: dict) -> list[str]:
    return [t for cat in (watchlist.get("themes") or {}).values() for t in (cat or [])]


def parse_vec(text: str) -> np.ndarray:
    return np.asarray(json.loads(text), dtype=np.float32)


def _norm(m: np.ndarray) -> np.ndarray:
    m = np.asarray(m, dtype=np.float32)
    n = np.linalg.norm(m, axis=-1, keepdims=True); n[n == 0] = 1.0
    return m / n


# pg partition: mod(abs(hashtext(chunk_id)), 5) = 0 is the held-out fifth (mod(), not %, so the
# same clause works with and without execute() parameters)
TRAIN_WHERE = "c.embedding IS NOT NULL AND mod(abs(hashtext(c.chunk_id)), 5) <> 0"
TEST_WHERE = "c.embedding IS NOT NULL AND mod(abs(hashtext(c.chunk_id)), 5) = 0"


def fetch_centroids(conn, names: list[str]) -> dict:
    """avg(vector) in-database — 62 vectors come back, not 90K."""
    cur = conn.cursor()
    cur.execute(f"SELECT t, avg(c.embedding)::text, count(*) FROM chunks c, unnest(c.themes) t "
                f"WHERE {TRAIN_WHERE} GROUP BY t")
    out = {}
    for t, vec, n in cur.fetchall():
        if t in names:
            out[t] = (parse_vec(vec), int(n))
    return out


DOC_GROUPS = {"earnings_transcript": "transcript", "conference_transcript": "transcript",
              "sec_filing": "sec_filing", "news": "news"}
# Measured 2026-09-10 per doc group (held-out, centered anchors): sec_filing prose maps to
# SOMETHING 97% of the time at the global 0.30 with P 0.22 — generic MD&A sits near every
# theme — while at 0.42 P is 0.39 with 83% still covered. Evidence COUNTS are the downstream
# product (§5/§6), so filings get a higher precision floor. Transcript-language chunks in pg
# are too few (72) to calibrate on their own -> exchanges keep the global threshold.
MIN_PRECISION_BY_GROUP = {"sec_filing": 0.35}
MIN_GROUP_TEST = 200                 # below this a group's sweep is reported but not used
SOURCE_GROUP = {"exchange": "transcript", "mdna": "sec_filing"}


def group_of(doc_type: str | None) -> str:
    return DOC_GROUPS.get(doc_type or "", "other")


def fetch_test(conn, names: list[str], per_theme: int = 30) -> list:
    """-> [(chunk_id, labels, vec, doc_type)]; per-theme sample so rare themes are represented."""
    cur = conn.cursor()
    cur.execute("SELECT setseed(0.42)")            # reproducible held-out sample across builds
    seen, out = set(), []
    for t in names:
        cur.execute(f"SELECT c.chunk_id, c.themes, c.embedding::text, c.doc_type FROM chunks c "
                    f"WHERE {TEST_WHERE} AND %s = ANY(c.themes) ORDER BY random() LIMIT %s",
                    (t, per_theme))
        for cid, themes, vec, doc_type in cur.fetchall():
            if cid in seen:
                continue
            seen.add(cid)
            out.append((cid, [x for x in themes if x in names], parse_vec(vec), doc_type))
    return out


def score_matrix(units: np.ndarray, anchors: np.ndarray, mean: np.ndarray | None = None) -> np.ndarray:
    """Cosine after removing the shared component. Uncentered, every chunk sits within
    cosine ~0.74 of EVERY theme centroid (measured 2026-09-10: P=0.07 across the sweep)
    because one corpus-wide direction dominates Gemini embeddings; subtracting the
    (weighted) centroid mean before normalising makes the anchors directional."""
    U = np.asarray(units, dtype=np.float32)
    A = np.asarray(anchors, dtype=np.float32)
    if mean is not None:
        U = U - mean
        A = A - mean
    return _norm(U) @ _norm(A).T


def calibrate(anchors: np.ndarray, names: list[str], test: list, thresholds=THRESHOLDS,
              mean: np.ndarray | None = None) -> list:
    if not test:
        return []
    S = score_matrix(np.vstack([t[2] for t in test]), anchors, mean=mean)
    rows = []
    for thr in thresholds:
        tp = fp = fn = 0; covered = 0
        for i, t in enumerate(test):
            labels = t[1]
            pred = {names[j] for j in np.where(S[i] >= thr)[0]}
            lab = set(labels)
            tp += len(pred & lab); fp += len(pred - lab); fn += len(lab - pred)
            covered += bool(pred)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        rows.append({"threshold": float(thr), "precision": round(p, 4), "recall": round(r, 4),
                     "f1": round(2 * p * r / (p + r), 4) if p + r else 0.0,
                     "coverage": round(covered / len(test), 4)})
    return rows


MIN_PRECISION = 0.3   # measured 2026-09-10: the held-out labels are the chunker's own LLM tags
                      # (noisy, ~1.7 per chunk); a P>=0.6 floor forced thr=0.50 with recall 0.08.
                      # Max-F1 is thr=0.30 (P 0.33 / R 0.39 / coverage 0.81, top-1 acc 0.59); a
                      # "false positive" there is usually a related theme the tagger omitted.


def calibrate_by_group(anchors, names, test, thresholds=THRESHOLDS, mean=None) -> dict:
    """The sweep per document group (4-tuples with doc_type); groups with no chunks are absent."""
    groups = {}
    for t in test:
        groups.setdefault(group_of(t[3] if len(t) > 3 else None), []).append(t)
    return {g: calibrate(anchors, names, sub, thresholds, mean=mean) for g, sub in groups.items()}


def thresholds_by_source(rows_by_group: dict, n_by_group: dict, global_thr: float) -> dict:
    """{'exchange': thr, 'mdna': thr, 'default': global}. A source takes its group's threshold
    only when the group had >= MIN_GROUP_TEST held-out chunks; otherwise the global one."""
    out = {"default": global_thr}
    for source, group in SOURCE_GROUP.items():
        rows = rows_by_group.get(group)
        if rows and n_by_group.get(group, 0) >= MIN_GROUP_TEST:
            out[source] = choose_threshold(rows, MIN_PRECISION_BY_GROUP.get(group, MIN_PRECISION))
        else:
            out[source] = global_thr
    return out


def choose_threshold(rows: list, min_precision: float = MIN_PRECISION) -> float:
    ok = [r for r in rows if r["precision"] >= min_precision]
    if ok:
        return max(ok, key=lambda r: (r["f1"], r["threshold"]))["threshold"]
    return max(rows, key=lambda r: (r["precision"], r["threshold"]))["threshold"]


def top1_accuracy(anchors, names, test, mean=None) -> float:
    if not test:
        return 0.0
    S = score_matrix(np.vstack([t[2] for t in test]), anchors, mean=mean)
    hits = sum(names[int(np.argmax(S[i]))] in t[1] for i, t in enumerate(test))
    return round(hits / len(test), 4)


def load_anchors(dir: Path = STATE):
    """-> (names, anchors[n,3072] float32 (raw centroids), mean[3072], meta). Score with
    score_matrix(units, anchors, mean=mean)."""
    meta = json.loads((dir / "anchors_meta.json").read_text())
    return (meta["names"], np.load(dir / "anchors.npy").astype(np.float32),
            np.load(dir / "mean.npy").astype(np.float32), meta)


def build(per_theme: int, min_precision: float, dir: Path = STATE) -> dict:
    names = theme_names(yaml.safe_load(WATCHLIST.read_text()))
    conn = pgconn.connect()
    cents = fetch_centroids(conn, names)
    missing = [t for t in names if t not in cents]
    names = [t for t in names if t in cents]
    C = np.vstack([cents[t][0] for t in names]).astype(np.float32)
    w = np.asarray([cents[t][1] for t in names], dtype=np.float32)
    mean = (C * w[:, None]).sum(axis=0) / w.sum()          # ≈ corpus mean (labels overlap; fine)
    test = fetch_test(conn, names, per_theme)
    rows = calibrate(C, names, test, mean=mean)
    thr = choose_threshold(rows, min_precision)
    by_group = calibrate_by_group(C, names, test, mean=mean)
    n_by_group = {}
    for t in test:
        n_by_group[group_of(t[3])] = n_by_group.get(group_of(t[3]), 0) + 1
    by_source = thresholds_by_source(by_group, n_by_group, thr)
    dir.mkdir(parents=True, exist_ok=True)
    np.save(dir / "anchors.npy", C)
    np.save(dir / "mean.npy", mean)
    A = C
    meta = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "model": "models/gemini-embedding-001", "task_type": "retrieval_document",
            "names": names, "n_train": {t: cents[t][1] for t in names},
            "themes_without_labels": missing, "n_test": len(test), "per_theme_test": per_theme,
            "min_precision": min_precision, "threshold": thr, "centered": True,
            "threshold_by_source": by_source, "n_test_by_group": n_by_group,
            "calibration_by_group": by_group,
            "top1_accuracy": top1_accuracy(C, names, test, mean=mean), "calibration": rows}
    (dir / "anchors_meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--per-theme", type=int, default=30)
    ap.add_argument("--min-precision", type=float, default=MIN_PRECISION)
    a = ap.parse_args(argv)
    if not a.build:
        ap.error("--build is the only action")
    meta = build(a.per_theme, a.min_precision)
    print(f"anchors: {len(meta['names'])} themes, {meta['n_test']} held-out chunks, "
          f"threshold={meta['threshold']} top1_acc={meta['top1_accuracy']} "
          f"(missing labels: {meta['themes_without_labels']})")
    for r in meta["calibration"]:
        print(f"  thr {r['threshold']:.2f}  P {r['precision']:.3f}  R {r['recall']:.3f}  "
              f"F1 {r['f1']:.3f}  cov {r['coverage']:.3f}")
    print(f"by source: {meta['threshold_by_source']} (held-out per group: {meta['n_test_by_group']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
