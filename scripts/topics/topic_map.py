#!/usr/bin/env python3
"""P2 topic_map — exchanges -> theme assignments | new-theme candidates (spec §4.2).

Both registers (question = analyst, evidence = corprep) go through the same function
against the same vocabulary so §6.2's two-count gap is computable. Assignment is cosine
to pg-derived theme centroids (anchors.py) at the calibrated threshold; units below it
are clustered (greedy leader) and clusters clearing a company-and-bank floor become
candidates the operator names or rejects. The system never writes watchlist.yaml.

    python3 scripts/topics/topic_map.py --run                      # map everything, refresh candidates + report
    python3 scripts/topics/topic_map.py --run --suggest-names      # + one Haiku call per surfaced candidate
    python3 scripts/topics/topic_map.py --accept cand:ID --name new_theme_slug
    python3 scripts/topics/topic_map.py --reject cand:ID
    python3 scripts/topics/topic_map.py --report [--email]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
import textprep as tp                       # noqa: E402
from anchors import load_anchors, score_matrix  # noqa: E402
from embed_store import EmbedStore          # noqa: E402

STATE = REPO / "state" / "topics"
EXCHANGES = REPO / "state" / "transcripts" / "exchanges.jsonl"
TOPIC_MAP = STATE / "topic_map.jsonl"
CANDIDATES = STATE / "candidates.json"
DECISIONS = STATE / "decisions.jsonl"
REPORT = REPO / "notes" / "reports" / "theme-candidates.md"

MIN_SIM = 0.82           # candidate clustering cosine; empirical, see the run log in the plan
MIN_COMPANIES = 3
MIN_BANKS = 2
MAX_THEMES = 3
REGISTER = {"analyst": "question", "corprep": "evidence"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] topic_map: {msg}", flush=True)


@dataclass
class Unit:
    id: str
    text: str
    register: str
    ticker: str
    event_type: str
    event_date: str
    period_key: str
    firm: str | None
    source: str = "exchange"


def units_from_exchanges(path: Path = EXCHANGES):
    units, skipped = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        reg = REGISTER.get(r.get("speaker_type"))
        if not reg or not (r.get("text") or "").strip():
            skipped += 1
            continue
        units.append(Unit(r["vector_id"], r["text"], reg, r.get("ticker"), r.get("event_type"),
                          r.get("event_date"), r.get("period_key"), r.get("speaker_firm") or None))
    return units, skipped


def assign(scores: np.ndarray, names: list, thr: float, top: int = MAX_THEMES) -> list:
    idx = [int(j) for j in np.argsort(-scores) if scores[j] >= thr][:top]
    return [(names[j], round(float(scores[j]), 4)) for j in idx]


def cluster_candidates(vectors: np.ndarray, min_sim: float) -> list:
    """Greedy leader clustering: each unit joins the first leader with cosine >= min_sim,
    else founds a cluster. Deterministic in input order (sort units by id first)."""
    leaders, members = [], []
    for i in range(len(vectors)):
        if leaders:
            sims = vectors[i] @ np.vstack([vectors[l] for l in leaders]).T
            j = int(np.argmax(sims))
            if sims[j] >= min_sim:
                members[j].append(i)
                continue
        leaders.append(i); members.append([i])
    return members


def build_candidates(clusters, units, texts, df, n_docs, min_companies=MIN_COMPANIES,
                     min_banks=MIN_BANKS) -> list:
    out = []
    for idxs in clusters:
        mem = [units[i] for i in idxs]
        companies = {u.ticker for u in mem if u.ticker}
        banks = {u.firm for u in mem if u.register == "question" and u.firm}
        if len(companies) < min_companies or len(banks) < min_banks:
            continue
        mem_sorted = sorted(mem, key=lambda u: (u.event_date or "9999", u.register != "question", u.id))  # questions lead
        ngr = tp.label_ngrams([texts[i] for i in idxs], df, n_docs)
        out.append({
            "id": f"cand:{mem_sorted[0].id}",
            "label": ngr[0] if ngr else mem_sorted[0].id,
            "ngrams": ngr,
            "n_exchanges": len(mem), "n_companies": len(companies), "n_banks": len(banks),
            "tickers": sorted(companies), "firms": sorted(banks),
            "first_seen": mem_sorted[0].event_date,
            "members": sorted(u.id for u in mem),
            "examples": [{"id": u.id, "ticker": u.ticker, "date": u.event_date, "firm": u.firm,
                          "text": tp.clean_text(u.text)[:280]} for u in mem_sorted[:3]],
            "status": "pending", "name": None, "suggested_name": None,
        })
    out.sort(key=lambda c: (-c["n_banks"], -c["n_companies"], -c["n_exchanges"], c["id"]))
    return out


def reattach_decisions(cands: list, decisions: list) -> list:
    for c in cands:
        best, best_j = None, 0.0
        m = set(c["members"])
        for d in decisions:
            dm = set(d.get("members") or [])
            j = len(m & dm) / len(m | dm) if m | dm else 0.0
            if j > best_j:
                best, best_j = d, j
        if best and best_j >= 0.5:
            c["status"], c["name"] = best["status"], best.get("name")
    return cands


def map_units(units, store, names, anchors, thr, min_sim=MIN_SIM, min_companies=MIN_COMPANIES,
              min_banks=MIN_BANKS, log_fn=None, mean=None):
    units = sorted(units, key=lambda u: u.id)
    texts = [tp.clean_text(u.text) or u.text for u in units]
    store.ensure([(u.id, t) for u, t in zip(units, texts)], log=log_fn)
    V = store.matrix([u.id for u in units])
    S = score_matrix(V, anchors, mean=mean)
    rows, unmapped = [], []
    for i, u in enumerate(units):
        themes = assign(S[i], names, thr)
        rows.append({**asdict(u), "themes": [{"theme": t, "score": s} for t, s in themes],
                     "best": round(float(S[i].max()), 4) if len(names) else None, "candidate": None})
        if not themes:
            unmapped.append(i)
    cands = []
    if unmapped:
        clusters = cluster_candidates(V[unmapped], min_sim)
        clusters = [[unmapped[k] for k in cl] for cl in clusters]
        df = tp.doc_frequencies(texts)
        cands = build_candidates(clusters, units, texts, df, len(texts), min_companies, min_banks)
        member_to_cand = {m: c["id"] for c in cands for m in c["members"]}
        for r in rows:
            r["candidate"] = member_to_cand.get(r["id"])
    for r in rows:
        r.pop("text", None)                       # the text lives in exchanges.jsonl; keep the map slim
    return rows, cands


def main(argv=None) -> int:
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main())
