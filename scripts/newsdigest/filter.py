"""
filter — HIGH / MEDIUM / DROP classification (spec §5, v1.5).

Per Google cluster, compute story_volume and FactSet corroboration, then assign a
level with a human-readable reason. FactSet articles for the same ticker are matched
to clusters by headline token-overlap (FACTSET_MATCH_JACCARD).
"""
from __future__ import annotations

from . import HIGH_VOLUME, MEDIUM_VOLUME, FACTSET_MATCH_JACCARD, SIGNAL_SENTIMENTS
from .cluster import normalize_tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / len(a | b) if inter else 0.0


def _match_factset(cluster, factset_articles):
    """Return the best-matching FactSet article for a cluster, or None."""
    ctoks = cluster.tokens
    best, best_score = None, 0.0
    for fa in factset_articles:
        score = _jaccard(ctoks, normalize_tokens(fa.get("headline", "")))
        if score > best_score:
            best, best_score = fa, score
    if best is not None and best_score >= FACTSET_MATCH_JACCARD:
        return best
    return None


class Verdict:
    __slots__ = ("level", "reason", "factset_status", "factset_article")

    def __init__(self, level, reason, factset_status=None, factset_article=None):
        self.level = level                  # 'HIGH' | 'MEDIUM' | 'DROP'
        self.reason = reason
        self.factset_status = factset_status  # short label for the digest line
        self.factset_article = factset_article


def classify(cluster, factset_articles, classifier) -> Verdict:
    sources = cluster.sources
    volume = cluster.volume
    top_tier_present = any(classifier.classify(s) == "top_tier" for s in sources)

    fa = _match_factset(cluster, factset_articles) if factset_articles else None
    fa_sent = (fa or {}).get("sentiment")
    fa_status = None
    if fa is not None:
        fa_status = f"FactSet: {fa_sent or 'Neutral'}"

    # ── HIGH (§5: any of a–d) ────────────────────────────────────────────────
    if fa is not None:
        return Verdict("HIGH", "in both FactSet + Google", fa_status, fa)            # §5a
    if top_tier_present:
        tt = sorted(s for s in sources if classifier.classify(s) == "top_tier")
        return Verdict("HIGH", f"top-tier source ({', '.join(tt)})", fa_status, None)  # §5d
    if volume >= HIGH_VOLUME:
        return Verdict("HIGH", f"story_volume {volume}", fa_status, None)             # §5b
    # §5c sentiment can only apply on a matched FactSet article, handled by §5a above.

    # ── MEDIUM (§5: any of a–c, and not HIGH) ────────────────────────────────
    if volume >= MEDIUM_VOLUME:
        return Verdict("MEDIUM", f"story_volume {volume}", fa_status, None)           # §5b
    if any(classifier.is_medium_single(s) for s in sources):
        ms = sorted(s for s in sources if classifier.is_medium_single(s))
        return Verdict("MEDIUM", f"single {', '.join(ms)} item", fa_status, None)     # §5c

    # ── DROP ─────────────────────────────────────────────────────────────────
    return Verdict("DROP", f"volume {volume}, no corroboration", fa_status, None)
