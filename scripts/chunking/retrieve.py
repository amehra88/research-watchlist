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
import logging
import re

from embed import embed_one
from store import get_store, Hit
from store_b import get_metrics_store  # mirrors store.get_store() pattern

log = logging.getLogger(__name__)

# Lazy, cached Store B handle — built on first guidance-chunk enrichment so a
# retrieval over non-guidance content never pays the metrics-store connect cost.
_metrics_store = None


def _get_metrics_store():
    global _metrics_store
    if _metrics_store is None:
        _metrics_store = get_metrics_store()
    return _metrics_store

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
             themes: list = None, store=None, production_boosts: bool = False) -> list[Hit]:
    """Return top-k child Hits, each auto-merged to its parent section.

    Default is the VERIFIED config: facet soft boost only (the §11c retriever
    measured at 25/31/32). production_boosts=True additionally applies the §7
    operator-opinion + recency boosts — design-intended but UNTUNED and
    UNMEASURED on a full corpus (they demonstrably reorder results), so they
    are OFF by default until tuned + re-evaluated on the embedded corpus. Keep
    default == measured config; do not flip until §7 weights are measured.

    themes: HARD scoping filter (like ticker/since) — keep only chunks carrying
    ANY of these theme tags. None/[] = no theme filter (behavior unchanged). The
    v3 ingest channels (inbox_processor, substacks) pass their LLM-extracted
    themes here so a query surfaces same-theme chunks across tickers.
    """
    store = store or get_store()
    qvec = embed_one(question, "retrieval_query")
    hits = store.search(
        qvec, k, query_facets=query_facets(question), ticker=ticker, since=since,
        themes=themes,
        facet_lambda=FACET_LAMBDA,
        operator_boost=OPERATOR_BOOST if production_boosts else 0.0,
        recency_lambda=RECENCY_LAMBDA if production_boosts else 0.0,
    )
    for h in hits:  # auto-merge: hand back the parent section for context (§3a)
        h.parent = store.get_parent(h.chunk["chunk_id"])

        # A<->B JOIN: forward-guidance chunks carry their management's quant
        # track record + credibility (store_b.join_guidance_chunk). Additive
        # post-processing — never affects ranking. Returns None gracefully when
        # Store B has no data for the ticker (most tickers today; see
        # store-b-coverage-expansion).
        chunk = h.chunk
        facets = chunk.get("facets") or []
        if "guidance" in facets and chunk.get("time_orientation") == "forward":
            try:
                enrichment = _get_metrics_store().join_guidance_chunk(chunk)
                if enrichment:
                    # `or None`: an empty track record (ticker not in Store B)
                    # is absence, not a result — keep the None contract uniform.
                    h.track_record = enrichment.get("track_record") or None
                    h.credibility = enrichment.get("credibility")
            except Exception as e:  # noqa: BLE001 — enrichment must not break retrieval
                log.warning("guidance enrichment failed for %s: %s",
                            chunk.get("chunk_id"), e)
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
        print(f"     {c.get('tickers')} | {c.get('section')} | "
              f"facets={c.get('facets')} [{c.get('claim_source')}/{c.get('time_orientation')}]")
        print(f"     {c['text'][:200].strip()}…")
        if h.parent:
            print(f"     ⤷ parent {h.parent['chunk_id']} ({len(h.parent['text'])} chars context)")


if __name__ == "__main__":
    main()
