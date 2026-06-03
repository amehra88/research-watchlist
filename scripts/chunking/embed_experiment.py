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
MODEL = "models/gemini-embedding-001"
KS = (1, 3, 5)
# (label, note, eval set, keyword-baseline recall@1 from eval.py). Step 3b adds
# the GOOGL note to test generalization beyond the note the chunker/eval were
# co-developed on.
DATASETS = [
    ("NVDA 1Q27", "notes/NVDA/20260521-1Q27.md", "eval_set.yaml", 11),
    ("GOOGL 1Q26", "notes/GOOGL/20260429-1Q26.md", "eval_set_googl.yaml", 6),
]


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


# facet-boost weight (added to cosine sim per fraction of query facets the
# chunk carries). The HARD pre-filter wins +2 @1 but COSTS recall@5: IDF drops
# the common `revenue` facet from a chunk that does discuss revenue growth, so a
# `revenue`-only query hard-filters out a chunk vector ranks in the top-5. A
# soft boost keeps that recall while retaining the @1 gain — facets belong as a
# ranking signal, not a gate (see docs §11b).
LAMBDA = 0.05
MODES = (("vector only", "none"),
         ("vector + facet pre-filter (hard)", "filter"),
         ("vector + facet boost (soft)", "boost"))


def run_dataset(label, note_rel, eval_rel, kw_base, genai):
    """Embed one note + its gold set; return {mode: {k: hits}} and n."""
    chunks = [c for c in chunk_note(HERE.parents[1] / note_rel) if c.kind == "child"]
    cases = yaml.safe_load((HERE / eval_rel).read_text())["cases"]
    n = len(cases)

    cache_path = Path(f"/tmp/embed_exp_cache_{Path(note_rel).stem}.json")
    key = f"{MODEL}|{len(chunks)}|{n}"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if cache.get("key") != key:
        print(f"[{label}] embedding {len(chunks)} chunks + {n} queries via {MODEL} …",
              file=sys.stderr)
        cache = {
            "key": key,
            "doc": _embed([c.text for c in chunks], "retrieval_document", genai),
            "qry": _embed([c["q"] for c in cases], "retrieval_query", genai),
        }
        cache_path.write_text(json.dumps(cache))
    D = np.array(cache["doc"]); Q = np.array(cache["qry"])
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    Q /= np.linalg.norm(Q, axis=1, keepdims=True)

    facet_top = [{f.split(".")[0] for f in c.facets} for c in chunks]

    def topk_indices(qi, mode):
        sims = D @ Q[qi]
        qf = _query_facets(cases[qi]["q"])
        if mode == "boost" and qf:
            boost = np.array([len(qf & facet_top[i]) / len(qf)
                              for i in range(len(chunks))])
            return list(np.argsort(-(sims + LAMBDA * boost))[:max(KS)])
        order = np.argsort(-sims)
        if mode == "filter" and qf:
            cand = [i for i in order if facet_top[i] & qf]
            if cand:
                return cand[:max(KS)]
        return list(order[:max(KS)])

    def recall_at(mode):
        hits = {k: 0 for k in KS}
        per = []
        for qi, case in enumerate(cases):
            idx = topk_indices(qi, mode)
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

    print(f"\n=== recall@k on {n} gold cases ({label}) ===")
    print(f"  keyword baseline (eval.py)         recall@1 = {kw_base}/{n}")
    out = {}
    for mlabel, mode in MODES:
        hits, per = recall_at(mode)
        out[mode] = hits
        line = "  ".join(f"recall@{k} = {hits[k]:2d}/{n}" for k in KS)
        print(f"  {mlabel:34s} {line}")
        if mode == "boost":
            print(f"\n  per-case ({label}, vector + facet boost):")
            for case, pk, idx in per:
                mark = f"@{pk}" if pk else "MISS"
                print(f"    [{mark:>4}] {case['q'][:60]}")
                if not pk:
                    top = chunks[idx[0]]
                    print(f"            top1={top.chunk_id} facets={top.facets}")
    return out, n


def main():
    _load_key()
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    combined = {mode: {k: 0 for k in KS} for _, mode in MODES}
    total_n = 0
    for label, note_rel, eval_rel, kw_base in DATASETS:
        out, n = run_dataset(label, note_rel, eval_rel, kw_base, genai)
        total_n += n
        for _, mode in MODES:
            for k in KS:
                combined[mode][k] += out[mode][k]

    print(f"\n=== COMBINED across {len(DATASETS)} notes ({total_n} cases) ===")
    for mlabel, mode in MODES:
        line = "  ".join(f"recall@{k} = {combined[mode][k]:2d}/{total_n}" for k in KS)
        print(f"  {mlabel:34s} {line}")


if __name__ == "__main__":
    main()
