"""
cluster — story de-duplication (spec §4).

Headline normalization + token-overlap (Jaccard >= JACCARD_THRESHOLD), stdlib only.
Normalize: lowercase, strip trailing " - {source}" (done upstream), strip punctuation,
strip share-price / number tokens, drop stopwords. A cluster's strength is its set of
unique sources; the representative item is the one from the highest-tier source.
"""
from __future__ import annotations

import hashlib
import re

from . import JACCARD_THRESHOLD

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "at", "by",
    "from", "as", "is", "are", "was", "were", "be", "been", "it", "its", "this", "that",
    "after", "over", "amid", "vs", "into", "up", "down", "but", "than", "out", "new",
    "says", "say", "said", "report", "reports", "stock", "stocks", "shares", "inc",
    "corp", "co", "ltd", "plc", "update", "amp",
}
# tokens that are purely a number / price / percentage / money-with-suffix
_NUMERIC = re.compile(r"^[+\-($]*\$?\d[\d,.%()kmbt+\-]*$")


def normalize_tokens(title: str) -> set[str]:
    t = title.lower()
    t = re.sub(r"[^a-z0-9$%.+\-() ]", " ", t)
    tokens = set()
    for raw in t.split():
        tok = raw.strip(".-()")
        if not tok or len(tok) <= 1:
            continue
        if _NUMERIC.match(raw) or _NUMERIC.match(tok):
            continue
        if tok in _STOPWORDS:
            continue
        tokens.add(tok)
    return tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if not inter:
        return 0.0
    return inter / len(a | b)


def cluster_hash(tokens: set[str]) -> str:
    return hashlib.sha1(" ".join(sorted(tokens)).encode()).hexdigest()[:16]


class Cluster:
    def __init__(self, item, tokens, classifier):
        self.items = [item]
        self.tokens = set(tokens)
        self._classifier = classifier

    def matches(self, tokens: set[str]) -> bool:
        return _jaccard(self.tokens, tokens) >= JACCARD_THRESHOLD

    def add(self, item, tokens):
        self.items.append(item)
        # union keeps the cluster anchor stable enough for near-verbatim syndication
        self.tokens |= tokens

    @property
    def sources(self) -> set[str]:
        return {it["source"] for it in self.items if it["source"]}

    @property
    def volume(self) -> int:
        # unique sources (denylisted items never reach here) = story_volume (§5)
        return len(self.sources)

    @property
    def representative(self):
        # highest-tier source, tiebreak newest
        return max(self.items, key=lambda it: (self._classifier.rank(it["source"]), it["published"]))

    @property
    def headline(self) -> str:
        return self.representative["title"]

    @property
    def hash(self) -> str:
        return cluster_hash(self.tokens)


def cluster_items(items, classifier) -> list[Cluster]:
    """Greedy single-pass clustering. Items should be one ticker's articles."""
    clusters: list[Cluster] = []
    # process newest first so representatives trend recent on ties
    for item in sorted(items, key=lambda a: a["published"], reverse=True):
        toks = normalize_tokens(item["title"])
        if not toks:
            continue
        placed = False
        for c in clusters:
            if c.matches(toks):
                c.add(item, toks)
                placed = True
                break
        if not placed:
            clusters.append(Cluster(item, toks, classifier))
    return clusters
