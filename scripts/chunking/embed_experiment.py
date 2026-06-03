#!/usr/bin/env python3
"""
Embedding recall@k experiment (advisor next-step #1 — gates the pgvector build).

Question: do real embeddings + a facet pre-filter recover the gold cases the
keyword baseline misses? We already proved the correct chunk EXISTS for every
miss; this checks whether vector retrieval actually finds it.

Throwaway-grade but kept as the A/B harness for the real retriever. Reuses the
chunker and the gold check() from eval.py — only the retrieval mechanism changes.

Embeddings: Gemini gemini-embedding-001 (the only embedding access available;
key sourced from /root/podcasts/.env per the enrich_sidecars convention — the
shell/.bashrc GEMINI_API_KEY is expired).

Run:  python3 scripts/chunking/embed_experiment.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import yaml

from chunker import chunk_note
from eval import check, _query_facets  # reuse gold-check + query-facet inference

HERE = Path(__file__).resolve().parent
NOTE = HERE.parents[1] / "notes/NVDA/20260521-1Q27.md"
MODEL = "models/gemini-embedding-001"
CACHE = Path("/tmp/embed_exp_cache.json")
KS = (1, 3, 5)


def _load_key() -> None:
    """Prefer /root/podcasts/.env (known-valid) over the expired shell key."""
    envf = Path("/root/podcasts/.env")
    if envf.exists():
        for line in envf.read_text().splitlines():
            line = line.strip()
            if line.startswith(("GEMINI_API_KEY=", "export GEMINI_API_KEY=")):
                os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("no GEMINI_API_KEY available")


def _embed(texts: list[str], task_type: str, genai) -> list[list[float]]:
    out = []
    for t in texts:
        for attempt in range(3):
            try:
                r = genai.embed_content(model=MODEL, content=t, task_type=task_type)
                out.append(r["embedding"])
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    raise
                time.sleep(1.5 * (attempt + 1))
    return out


def main():
    _load_key()
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    chunks = [c for c in chunk_note(NOTE) if c.kind == "child"]
    cases = yaml.safe_load((HERE / "eval_set.yaml").read_text())["cases"]

    # --- embed (cache to avoid repeat API calls on rerun) ---
    key = f"{MODEL}|{len(chunks)}|{len(cases)}"
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    if cache.get("key") != key:
        print(f"embedding {len(chunks)} chunks + {len(cases)} queries via {MODEL} …",
              file=sys.stderr)
        cache = {
            "key": key,
            "doc": _embed([c.text for c in chunks], "retrieval_document", genai),
            "qry": _embed([c["q"] for c in cases], "retrieval_query", genai),
        }
        CACHE.write_text(json.dumps(cache))
    D = np.array(cache["doc"]); Q = np.array(cache["qry"])
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    Q /= np.linalg.norm(Q, axis=1, keepdims=True)

    facet_top = [{f.split(".")[0] for f in c.facets} for c in chunks]

    def topk_indices(qi, prefilter):
        sims = D @ Q[qi]
        order = np.argsort(-sims)
        if prefilter:
            qf = _query_facets(cases[qi]["q"])
            if qf:
                cand = [i for i in order if facet_top[i] & qf]
                if cand:
                    return cand[:max(KS)]
        return list(order[:max(KS)])

    def recall_at(prefilter):
        hits = {k: 0 for k in KS}
        per = []
        for qi, case in enumerate(cases):
            idx = topk_indices(qi, prefilter)
            passed_k = None
            for rank, i in enumerate(idx, 1):
                if not check(case, chunks[i]):
                    passed_k = rank
                    break
            per.append((case, passed_k, idx))
            for k in KS:
                if passed_k and passed_k <= k:
                    hits[k] += 1
        return hits, per

    n = len(cases)
    print(f"\n=== recall@k on {n} gold cases (NVDA 1Q27) ===")
    print(f"  keyword baseline (eval.py)      recall@1 = 8/{n}")
    for label, pf in (("vector only", False), ("vector + facet pre-filter", True)):
        hits, per = recall_at(pf)
        line = "  ".join(f"recall@{k} = {hits[k]:2d}/{n}" for k in KS)
        print(f"  {label:30s} {line}")
        if pf:  # show per-case detail for the recommended variant
            print("\n  per-case (vector + facet pre-filter):")
            for case, pk, idx in per:
                mark = f"@{pk}" if pk else "MISS"
                print(f"    [{mark:>4}] {case['q'][:62]}")
                if not pk:
                    top = chunks[idx[0]]
                    print(f"            top1={top.chunk_id} facets={top.facets}")


if __name__ == "__main__":
    main()
