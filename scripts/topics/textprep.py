#!/usr/bin/env python3
"""Text preparation for topic mapping: strip what carries no topic (timestamps,
pleasantries), tokenise, and label a cluster of texts with its most specific n-grams.
Pure functions — no I/O, no models."""
from __future__ import annotations

import math
import re
from collections import Counter

TIMESTAMP_RE = re.compile(r"\(\d{1,2}:\d{2}(?::\d{2})?\)")
SENT_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")
PLEASANTRY_RE = re.compile(
    r"\b(thank(s| you)|congrat\w*|good (morning|afternoon|evening)|taking my question|"
    r"great quarter|nice quarter|appreciate (it|the)|hi\b|hey\b|hello\b|two questions?|"
    r"couple of questions|follow[- ]up)\b", re.I)
PLEASANTRY_MAX_WORDS = 12

STOPWORDS = set("""a about above after again against all also am an and any are as at be because been
before being below between both but by can could did do does doing down during each few for from
further had has have having he her here hers him his how i if in into is it its itself just kind know
like little lot maybe me more most my no nor not now of off on once only or other our out over own
same she should so some such than that the their them then there these they thing things think this
those through to too under until up us very was we were what when where which while who whom why will
with would you your yours yourself yourselves guys sort obviously basically really actually right okay
ok yeah yes well one two three first second next last year years quarter quarters going get got give
say said see look looking want wanted question questions thanks thank talk talked bit maybe much
many still even way back around across along per versus vs may might must shall let us""".split())

WORD_RE = re.compile(r"[a-z][a-z0-9\-]+")


def clean_text(text: str) -> str:
    text = TIMESTAMP_RE.sub("", text or "")
    keep = []
    for s in SENT_SPLIT_RE.split(text.strip()):
        s = s.strip()
        if not s:
            continue
        if PLEASANTRY_RE.search(s) and len(s.split()) <= PLEASANTRY_MAX_WORDS:
            continue
        keep.append(s)
    return re.sub(r"\s{2,}", " ", " ".join(keep)).strip()


def tokens(text: str) -> list[str]:
    return [w for w in WORD_RE.findall((text or "").lower())
            if w not in STOPWORDS and len(w) > 2 and not w.replace("-", "").isdigit()]


def ngrams(toks: list[str], n_max: int = 3) -> list[str]:
    out = []
    for n in range(1, n_max + 1):
        out += [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return out


def doc_frequencies(texts: list[str]) -> dict:
    df: Counter = Counter()
    for t in texts:
        df.update(set(ngrams(tokens(t))))
    return dict(df)


def label_ngrams(texts: list[str], df: dict, n_docs: int, top: int = 8) -> list[str]:
    """Cluster term frequency × inverse corpus document frequency, longest n-gram wins ties.
    Only phrases present in ≥2 cluster texts (or all of them when the cluster is tiny)."""
    tf: Counter = Counter()
    for t in texts:
        tf.update(set(ngrams(tokens(t))))
    floor = 2 if len(texts) >= 3 else 1
    scored = []
    for g, c in tf.items():
        if c < floor:
            continue
        idf = math.log((n_docs + 1) / (df.get(g, 0) + 1)) + 1.0
        scored.append((c * idf * (1.0 + 0.15 * g.count(" ")), g))
    scored.sort(key=lambda x: (-x[0], x[1]))
    out, seen = [], set()
    for _, g in scored:
        if any(g in s or s in g for s in seen):     # skip sub/super-phrases already listed
            continue
        seen.add(g); out.append(g)
        if len(out) == top:
            break
    return out
