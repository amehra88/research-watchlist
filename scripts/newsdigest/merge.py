"""
merge — Lever 1: two-stage event-merge that collapses fragments of ONE event that stage-1 clustering
left split. NO claude -p.

Stage-1 `cluster.cluster_items` (Jaccard 0.6 on raw headline tokens) fails on fragments because every
same-company headline shares the company name while each has enough distinct words to fall under 0.6.
This second pass fixes that by comparing NAME-STRIPPED CONTENT tokens:

  "Samsung Electronics Formalizes Robotics Division" → {robotics, division, formalizes}
  "Samsung Robotics Division Led by Hyundai Exec"    → {robotics, division, hyundai, exec}
  "Samsung Cuts Jobs in US"                          → {cuts, jobs, us}

Stripping the block company's own name makes robotics-fragments overlap strongly with each other and
NEAR-ZERO with the job-cuts story — so distinct events of the SAME company separate cleanly, which a
blunt global-threshold drop never could.

Design (drawn from measurement on the real 2026-07-21 pool):
  • block clusters by dominant queried item["ticker"] (free + reliable),
  • within a block, union-find merge (transitive) when content-signature Jaccard ≥ THRESHOLD,
  • THRESHOLD = 0.3 — collapses the real fragmentation (Samsung robotics ×12→1, NBIS/Nvidia stake
    ×11→1) with the ONLY over-merge being template-spam, which Lever 2 removes FIRST. So this MUST run
    AFTER pre_filter. Fall back to 0.4 if the post-filter over-merge gate (>5%) trips.
  • a merged cluster keeps ALL items → volume/tier go UP (stronger corroboration signal to the LLM).

Accepted limitation: blocking by queried ticker leaves a cross-ticker event (Nebius surfaced under both
NBIS and NVDA queries) as 2 clusters, not 1 — still a huge cut. Cross-block merge is a future refinement.
"""
from __future__ import annotations

import re
from collections import defaultdict

from .cluster import normalize_tokens

THRESHOLD = 0.3

# generic corp/sector/market tokens that carry no EVENT identity — stripped from the content signature
# alongside the block company's own name, so only the event words drive similarity.
_GENERIC = {
    "inc", "corp", "co", "ltd", "plc", "com", "holdings", "holding", "technology", "technologies",
    "platforms", "systems", "group", "software", "enterprise", "international", "global",
    "semiconductor", "semiconductors", "motors", "energy", "networks", "advanced", "micro",
    "devices", "electronics", "stock", "shares", "share", "price", "update", "coverage", "report",
    "reports", "analyst", "analysts", "says", "movement", "examined", "amid", "dynamics",
    "earnings", "company", "nasdaq", "nyse", "corporation",
}

# rank for picking the strongest FactSet sentiment across a merged group
_FA_RANK = {"Very Negative": 2, "Very Positive": 2, "Negative": 1, "Positive": 1, "Neutral": 0}


def _name_tokens(ticker_names: dict) -> dict:
    return {t: {w for w in re.split(r"[^a-z0-9]+", (nm or "").lower())
                if len(w) >= 3 and w not in _GENERIC}
            for t, nm in ticker_names.items()}


def content_signature(title: str, block_ticker: str, name_toks: dict) -> set:
    """Name-stripped content tokens for one headline within a ticker block."""
    strip = _GENERIC | name_toks.get(block_ticker, set())
    return {w for w in normalize_tokens(title) if w not in strip and len(w) >= 3}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / len(a | b) if inter else 0.0


def _dominant_ticker(cluster) -> str:
    cnt = defaultdict(int)
    for it in cluster.items:
        cnt[it.get("ticker", "?")] += 1
    return max(cnt, key=cnt.get)


def _absorb(primary, others):
    """Fold every `others` cluster's items+tokens into `primary` (kept as the merged cluster).
    Recomputes the strongest FactSet sentiment across the whole group."""
    for c in others:
        primary.items.extend(c.items)
        primary.tokens |= c.tokens
    best, best_r = getattr(primary, "_fa_sentiment", None), -1
    for it in primary.items:
        if it.get("_is_factset"):
            s = it.get("_fa_sentiment") or "Neutral"
            if _FA_RANK.get(s, 0) > best_r:
                best, best_r = s, _FA_RANK.get(s, 0)
    if best is not None:
        primary._fa_sentiment = best
    return primary


def merge_clusters(clusters, ticker_names: dict, threshold: float = THRESHOLD, logger=None):
    """Collapse event-fragments. Returns the merged cluster list (fewer clusters, same events).
    Run AFTER pre_filter.filter_clusters (filter-first keeps the merge safe at T=0.3)."""
    name_toks = _name_tokens(ticker_names)
    blocks = defaultdict(list)
    for c in clusters:
        blocks[_dominant_ticker(c)].append(c)

    out, n_groups, n_merged_in = [], 0, 0
    for tk, cs in blocks.items():
        sigs = [content_signature(c.headline, tk, name_toks) for c in cs]
        parent = list(range(len(cs)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                if _jaccard(sigs[i], sigs[j]) >= threshold:
                    parent[find(i)] = find(j)

        comp = defaultdict(list)
        for i in range(len(cs)):
            comp[find(i)].append(i)
        for members in comp.values():
            group = [cs[m] for m in members]
            if len(group) == 1:
                out.append(group[0])
            else:
                n_groups += 1
                n_merged_in += len(group)
                primary = max(group, key=lambda c: c.volume)   # best-corroborated becomes the merged base
                out.append(_absorb(primary, [c for c in group if c is not primary]))
    if logger:
        logger.info("event-merge: %d → %d clusters (%d group(s) absorbed %d fragments, T=%.2f)",
                    len(clusters), len(out), n_groups, n_merged_in, threshold)
    return out
