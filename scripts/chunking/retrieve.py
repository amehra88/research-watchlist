#!/usr/bin/env python3
"""
Retriever — Store A (docs/chunking-strategy.md step 4).

query  ->  embed (retrieval_query)  ->  Store.search (vector + soft facet boost)
       ->  auto-merge each child hit to its parent section (§3a)

This is the function any consumer (agents, the gold eval, future tools) calls.
The ranking is the PROVEN spec from §11b-c — cosine + soft facet boost, never a
hard facet gate — plus the §7 production boosts (operator-opinion + recency),
which are ON here but OFF in the gold-eval harness so that eval stays an
apples-to-apples reproduction of the documented numbers.

Usage:
    python3 scripts/chunking/retrieve.py "How large is Google Cloud's backlog?"
    python3 scripts/chunking/retrieve.py "NVDA data center margin" --ticker NVDA -k 5
"""
from __future__ import annotations

import argparse
import re

from embed import embed_one
from store import get_store, Hit

# Production §7 ranking weights. Untuned-but-reasonable; tune on a multi-note
# corpus (the gold eval pins the facet_lambda=0.05 baseline that these extend).
OPERATOR_BOOST = 0.03      # §7: operator's own synthesis should dominate raw transcript
RECENCY_LAMBDA = 0.02      # §7: a stale margin comment shouldn't tie a current one
FACET_LAMBDA = 0.05        # the proven soft-boost weight (embed_experiment.py)

# Same facet-cue inference the chunker/eval use (hybrid retrieval, query side).
from chunker import _FACET_CUES  # noqa: E402


def query_facets(question: str) -> set:
    low = question.lower()
    return {f for f, pat in _FACET_CUES.items() if re.search(pat, low, re.I)}


def retrieve(question: str, k: int = 5, *, ticker: str = None, since: str = None,
             store=None, production_boosts: bool = True) -> list[Hit]:
    """Return top-k child Hits, each auto-merged to its parent section.

    production_boosts=False reproduces the bare proven retriever (facet soft
    boost only) — used by the gold eval. True adds the §7 operator + recency
    boosts for real use.
    """
    store = store or get_store()
    qvec = embed_one(question, "retrieval_query")
    hits = store.search(
        qvec, k, query_facets=query_facets(question), ticker=ticker, since=since,
        facet_lambda=FACET_LAMBDA,
        operator_boost=OPERATOR_BOOST if production_boosts else 0.0,
        recency_lambda=RECENCY_LAMBDA if production_boosts else 0.0,
    )
    for h in hits:  # auto-merge: hand back the parent section for context (§3a)
        h.parent = store.get_parent(h.chunk["chunk_id"])
    return hits


def main():
    ap = argparse.ArgumentParser(description="Query Store A.")
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--ticker", help="hard-scope to a ticker")
    ap.add_argument("--since", help="hard-scope to event_date >= YYYY-MM-DD")
    args = ap.parse_args()

    hits = retrieve(args.query, args.k, ticker=args.ticker, since=args.since)
    if not hits:
        print("(no hits — is the store populated? run ingest.py --all)")
        return
    for rank, h in enumerate(hits, 1):
        c = h.chunk
        ans = (f"  →{c['answered_by']}/{c.get('answerer_role')}"
               f"({c.get('answer_directness') or '?'})" if c.get("answered_by") else "")
        print(f"\n[{rank}] {h.score:.3f}  {c['chunk_id']}{ans}")
        print(f"     {c.get('ticker')} | {c.get('section')} | "
              f"facets={c.get('facets')} [{c.get('claim_source')}/{c.get('time_orientation')}]")
        print(f"     {c['text'][:200].strip()}…")
        if h.parent:
            print(f"     ⤷ parent {h.parent['chunk_id']} ({len(h.parent['text'])} chars context)")


if __name__ == "__main__":
    main()
