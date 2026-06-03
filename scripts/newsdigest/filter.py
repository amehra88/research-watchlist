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


# Calendar-driven StreetAccount boilerplate — published on a schedule, not on an event.
# Per operator (signal-not-volume): these do NOT earn HIGH even though SA published them.
# CALIBRATION NOTE: weekly "StreetAccount Macro Update" items are deliberately NOT matched here —
# they aggregate curated cross-name weekend headlines (real signal) and stay HIGH-eligible. Revisit
# after ~1 week of digest output if macro updates start dominating HIGH.
_TEMPLATED_PREVIEW_RE = re.compile(
    r"consensus metrics preview"      # "StreetAccount Consensus Metrics Preview - <co> Q# Earnings"
    r"|earnings preview"              # "<co> F#Q## Earnings Preview"
    r"|streetaccount\b.*\bsummary",   # "StreetAccount M&A Summary: Week of 25-May"
    re.IGNORECASE,
)


def is_templated_preview(headline: str) -> bool:
    """True for scheduled SA boilerplate (previews / weekly summaries) -> cap at MEDIUM."""
    return bool(_TEMPLATED_PREVIEW_RE.search(headline or ""))


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
    """v2 (channel inversion): FactSet StreetAccount is the institutional-signal channel;
    Google volume no longer earns HIGH on its own. This function governs Google clusters and
    Google↔FactSet matches; FactSet-ONLY items are routed to HIGH in news_digest.build_digest."""
    sources = cluster.sources
    volume = cluster.volume
    tt_items = [it for it in cluster.items if classifier.classify(it["source"]) == "top_tier"]
    tt_relevant = bool(tt_items) and any(
        _headline_mentions(it["title"], name, ticker) for it in tt_items
    )

    fa = _match_factset(cluster, factset_articles) if factset_articles else None
    fa_sent = (fa or {}).get("sentiment")
    fa_status = f"FactSet: {fa_sent or 'Neutral'}" if fa is not None else None

    # ── HIGH ──────────────────────────────────────────────────────────────────
    if fa is not None:                                                  # in both FactSet + Google
        if is_templated_preview(fa.get("headline", "")) or is_templated_preview(cluster.headline):
            return Verdict("MEDIUM", "FactSet templated preview", fa_status, fa)
        return Verdict("HIGH", "in both FactSet + Google", fa_status, fa)
    if tt_relevant:                                                     # top-tier single + relevance gate
        tt = sorted({classifier.canonical(it["source"]) for it in tt_items})
        return Verdict("HIGH", f"top-tier source ({', '.join(tt)})", fa_status, None)
    # v2: story_volume NO LONGER promotes to HIGH — institutional bar lives in the FactSet channel.

    # ── MEDIUM ────────────────────────────────────────────────────────────────
    if tt_items:                                                        # top-tier, headline didn't name the ticker
        tt = sorted({classifier.canonical(it["source"]) for it in tt_items})
        return Verdict("MEDIUM", f"top-tier ({', '.join(tt)}), no headline match", fa_status, None)
    if volume >= HIGH_VOLUME:                                           # >=4 allowlisted Google, not in FactSet
        return Verdict("MEDIUM", f"story_volume {volume}", fa_status, None)
    if any(classifier.is_medium_single(s) for s in sources) and \
            _headline_mentions(cluster.headline, name, ticker):         # relevance-gated medium-single
        ms = sorted(s for s in sources if classifier.is_medium_single(s))
        return Verdict("MEDIUM", f"single {', '.join(ms)} item", fa_status, None)

    # ── DROP ──────────────────────────────────────────────────────────────────
    return Verdict("DROP", f"single-source / below bar (volume {volume})", fa_status, None)
