"""
filter — HIGH / MEDIUM / DROP classification (spec §5, v1.5).

Per Google cluster, compute story_volume and FactSet corroboration, then assign a
level with a human-readable reason. FactSet articles for the same ticker are matched
to clusters by headline token-overlap (FACTSET_MATCH_JACCARD).
"""
from __future__ import annotations

import re

from . import HIGH_VOLUME, MEDIUM_VOLUME, FACTSET_MATCH_JACCARD, SIGNAL_SENTIMENTS
from .cluster import normalize_tokens

# generic / corporate-suffix / geographic name tokens that don't establish relevance on their own
_NAME_STOP = {
    "inc", "corp", "co", "ltd", "plc", "the", "com", "holdings", "holding", "technology",
    "technologies", "platforms", "systems", "group", "software", "enterprise", "international",
    "global", "semiconductor", "semiconductors", "motors", "energy", "networks", "advanced",
    "micro", "devices", "taiwan", "korea", "korean", "infrastructure", "solutions", "power",
}


def _headline_mentions(headline: str, name: str, ticker: str) -> bool:
    """Relevance gate (fix 3): is this headline actually about the ticker?

    True if the full company name, a distinctive name token (len>=4, non-generic),
    or the bare ticker symbol appears in the headline. Filters tangential mentions
    (e.g. a 'Wall St ends higher' market-wrap that merely lists MSFT)."""
    h = (headline or "").lower()
    if name and name.lower() in h:
        return True
    for tok in re.split(r"[^a-z0-9]+", (name or "").lower()):
        if len(tok) >= 4 and tok not in _NAME_STOP and re.search(rf"\b{re.escape(tok)}\b", h):
            return True
    t = (ticker or "").lower()
    if t and "." not in t and re.search(rf"\b{re.escape(t)}\b", h):
        return True
    return False


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


def classify(cluster, factset_articles, classifier, name="", ticker="") -> Verdict:
    sources = cluster.sources
    volume = cluster.volume
    tt_items = [it for it in cluster.items if classifier.classify(it["source"]) == "top_tier"]

    fa = _match_factset(cluster, factset_articles) if factset_articles else None
    fa_sent = (fa or {}).get("sentiment")
    fa_status = None
    if fa is not None:
        fa_status = f"FactSet: {fa_sent or 'Neutral'}"

    # ── HIGH (§5: any of a–d) ────────────────────────────────────────────────
    if fa is not None:
        return Verdict("HIGH", "in both FactSet + Google", fa_status, fa)            # §5a
    # §5d top-tier-single override, gated on the top-tier item actually being about
    # this ticker (fix 3) — a tangential market-wrap mention no longer qualifies.
    if tt_items and any(_headline_mentions(it["title"], name, ticker) for it in tt_items):
        tt = sorted({classifier.canonical(it["source"]) for it in tt_items})
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
