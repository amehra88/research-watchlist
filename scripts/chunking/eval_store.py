#!/usr/bin/env python3
"""
Gold-eval through the REAL store (docs/chunking-strategy.md step 4 gate).

Runs the existing 32 gold cases through the production path —
retrieve.py -> get_store() -> FileStore vector search — and reports recall@k.
This proves the shipped pipeline (ingest -> store -> retrieve) reproduces the
documented embed_experiment.py numbers (vector-only 21/28/32; soft-boost
25/31/32), not just a notebook. It is the regression gate for step 4 and after.

Uses production_boosts=False so the ranking is exactly the proven soft-boost
spec (cosine + facet_lambda=0.05), apples-to-apples with the doc. Each note is
ticker-scoped (the hard ticker filter) so a combined store matches the
per-note-store experiment.

Run (needs the store populated for both gold notes — see ingest.py):
    python3 scripts/chunking/eval_store.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

from chunker import Chunk
from eval import check
from retrieve import retrieve
from store import FileStore

HERE = Path(__file__).resolve().parent
KS = (1, 3, 5)
DATASETS = [
    ("NVDA 1Q27", "NVDA", "eval_set.yaml"),
    ("GOOGL 1Q26", "GOOGL", "eval_set_googl.yaml"),
]


def _as_chunk(rec: dict) -> Chunk:
    return Chunk(**rec)  # store records carry exactly the Chunk fields


def run(label, ticker, eval_rel, store):
    cases = yaml.safe_load((HERE / eval_rel).read_text())["cases"]
    hits = {k: 0 for k in KS}
    misses = []
    for case in cases:
        ranked = retrieve(case["q"], k=max(KS), ticker=ticker, store=store,
                          production_boosts=False)
        passed_k = None
        for rank, h in enumerate(ranked, 1):
            if not check(case, _as_chunk(h.chunk)):
                passed_k = rank
                break
        for k in KS:
            if passed_k and passed_k <= k:
                hits[k] += 1
        if not passed_k or passed_k > 5:
            misses.append(case["q"])
    n = len(cases)
    line = "  ".join(f"@{k}={hits[k]:2d}/{n}" for k in KS)
    print(f"  {label:12s} {line}")
    for m in misses:
        print(f"      MISS: {m[:70]}")
    return hits, n


def main():
    store = FileStore()
    p, c = store.count()
    print(f"store: {p} parents + {c} children\n=== recall@k through retrieve.py -> FileStore ===")
    combined = {k: 0 for k in KS}
    total = 0
    for label, ticker, eval_rel in DATASETS:
        hits, n = run(label, ticker, eval_rel, store)
        total += n
        for k in KS:
            combined[k] += hits[k]
    print(f"  {'COMBINED':12s} " + "  ".join(f"@{k}={combined[k]:2d}/{total}" for k in KS))


if __name__ == "__main__":
    main()
