#!/usr/bin/env python3
"""Shared topic vocabulary over both registers (spec §4.2).

ONE VOCABULARY, TWO REGISTERS. Analyst exchanges (exchanges.jsonl) are the
question side; MD&A diffs and foreign claims (claims.jsonl) are the evidence
side. Both map into the SAME topic namespace — otherwise §6.2's two-count
comparison has no way to know that a disclosure and a question concern the same
topic, and the gap metric is simply not computable.

THEMES ARE ANCHORS, NOT BOXES. The config/watchlist.yaml slugs seed the space
and preserve continuity with the existing labelled history. A phrase that lands
near one inherits it; a phrase that lands far from all of them becomes a
new-theme CANDIDATE. That is how the vocabulary grows.

THE OPERATOR OWNS THE VOCABULARY. Candidates are written to a review file. This
module NEVER writes to config/watchlist.yaml — the same rule that governs tier
promotion.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_store as es  # noqa: E402

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

REPO_ROOT = Path("/root/research-watchlist")
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
EXCHANGES_PATH = REPO_ROOT / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS_PATH = REPO_ROOT / "state" / "evidence" / "claims.jsonl"

MODEL = "claude-sonnet-4-6"                # matches the other v3 wrappers
CLAUDE_TIMEOUT_S = 120
MIN_UNIT_WORDS = 8                         # below this there is no topic

# Cosine on gemini-embedding-001. Calibrated in Task 6 against the real
# corpus; this is the starting point, not a tuned value.
SIM_THRESHOLD = 0.72

# Findings 2026-08-21 R2. The whole best-cosine distribution is ~0.08 wide, so
# "nearest anchor" is often a coin flip: convertible-note prose landed on
# ai_generated_content at 0.689. When the top two anchors are this close the
# winner carries no information, and letting it inherit silently inflates that
# theme's cross-sectional count — the §5 metric with no visible symptom.
MIN_MARGIN = 0.02


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] topic_map: {msg}", flush=True)


def load_themes(watchlist_path: Path = WATCHLIST_YAML) -> list:
    """Every slug across every theme group, sorted. The count is whatever the
    file says today — it has already changed once and will change again."""
    data = yaml.safe_load(watchlist_path.read_text()) or {}
    slugs = set()
    for group in (data.get("themes") or {}).values():
        for slug in group or []:
            slugs.add(str(slug))
    return sorted(slugs)


def anchor_text(slug: str) -> str:
    """A slug is not a sentence. Embedding `china_ai_infrastructure_demand`
    raw wastes the model's language prior; the spaced phrase does not."""
    return slug.replace("_", " ")


def cosine(a: list, b: list) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def assign(phrase_vecs: list, anchor_vecs: list, anchors: list,
           threshold: float = SIM_THRESHOLD,
           min_margin: float = MIN_MARGIN) -> list:
    """-> [(theme_or_None, similarity)] aligned to phrase_vecs.

    Two gates, and the second is not in the original spec. A phrase inherits a
    theme only when it clears `threshold` AND beats the runner-up by
    `min_margin`. Without the margin, prose that belongs to no theme still
    lands on whichever anchor happens to be a hair closer — see MIN_MARGIN.

    The similarity is reported even on a miss: a phrase that scored 0.71
    against an existing theme is a different kind of candidate from one that
    scored 0.2, and the operator review in §4.2 needs to see which."""
    out = []
    for pv in phrase_vecs:
        scored = sorted(((cosine(pv, av), a)
                         for av, a in zip(anchor_vecs, anchors)), reverse=True)
        best_s, best_a = scored[0]
        clears = best_s >= threshold
        # a single anchor has no runner-up, so there is no coin flip to lose
        if clears and len(scored) > 1 and (best_s - scored[1][0]) < min_margin:
            clears = False
        out.append((best_a if clears else None, best_s))
    return out


# ───────────────────── input units, both registers ─────────────────────

# Findings 2026-08-21 R1. Accounting, financing and legal housekeeping is a
# large share of MD&A prose, is never a thesis topic, and — because every filer
# writes it — sails straight through MIN_CANDIDATE_COMPANIES. It has to be
# dropped BEFORE a claude -p call is spent on it. Cues are multi-word and
# deliberately specific: bare "revenue" or "capital expenditures" must survive,
# since capex prose scored 0.805 against ai_infrastructure_capex.
HOUSEKEEPING_CUES = (
    "forward-looking statements", "safe harbor",
    "critical accounting", "accounting policies", "accounting pronouncement",
    "recently issued accounting", "revenue is recognized",
    "revenue recognition", "effective tax rate", "uncertain tax positions",
    "unrecognized tax benefits", "valuation allowance", "deferred tax",
    "pension", "postretirement", "actuarial",
    "convertible senior notes", "senior notes", "credit agreement",
    "credit facility", "borrowing capacity", "revolving", "indenture",
    "aggregate principal amount", "lease payments", "operating lease",
    "right-of-use", "contractual obligations", "off-balance sheet",
    "share-based compensation", "stock-based compensation",
    "goodwill", "impairment charge", "intangible assets",
    "marketable securities", "debt securities", "fair value measurement",
    "prospectus", "selling stockholder", "registration statement",
    "shelf registration", "corporate website", "available free of charge",
    "incorporated by reference", "foreign exchange gain",
    "foreign currency translation", "repurchase program", "treasury stock",
    "dividends declared",
)


def is_housekeeping(text: str) -> bool:
    """True when this block is accounting/financing/legal mechanics."""
    low = " ".join(text.lower().split())
    return any(cue in low for cue in HOUSEKEEPING_CUES)


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue                       # torn line must not abort the run


def iter_question_units(path: Path = EXCHANGES_PATH):
    """Analyst speech only. corprep speech is the company describing itself,
    which is evidence and reaches us through claims.jsonl instead.

    period_key is DERIVED, never read: 53.1% of the corpus carries a fiscal
    label that would misalign it against the calendar-keyed evidence side.
    See evidence_store.join_period_key."""
    for r in _iter_jsonl(path):
        if r.get("speaker_type") != "analyst":
            continue
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        try:
            pk = es.join_period_key(period_key=r.get("period_key"),
                                    period_basis=r.get("period_basis"),
                                    event_date=r.get("event_date"))
        except ValueError:
            continue                       # undatable row cannot be compared
        yield {
            "unit_id": r["vector_id"],
            "register": "question",
            "ticker": r.get("ticker"),
            "period_key": pk,
            "first_evidence_date": None,
            "speaker_firm": r.get("speaker_firm"),
            "text": text,
        }


def iter_evidence_units(path: Path = CLAIMS_PATH):
    """Claims are already calendar-keyed by evidence_store, so period_key is
    read as-is here. Housekeeping prose is dropped before it can cost a call."""
    for r in _iter_jsonl(path):
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        if is_housekeeping(text):
            continue
        yield {
            "unit_id": r["claim_id"],
            "register": "evidence",
            "ticker": r.get("ticker"),
            "period_key": r.get("period_key"),
            "first_evidence_date": r.get("first_evidence_date"),
            "speaker_firm": None,
            "text": text,
        }


# ───────────────────────── phrase extraction ─────────────────────────

def extract_prompt(text: str) -> str:
    return (
        "Read the passage below from an earnings call or a company filing.\n"
        "List the distinct SUBJECT TOPICS it concerns — what it is about, not "
        "what it claims.\n\n"
        "Rules:\n"
        "- 2 to 5 words per topic, lowercase, no punctuation.\n"
        "- Name the subject matter, not the sentiment or direction. "
        "'chinese transceiver competition', not 'worry about china'.\n"
        "- At most 4 topics. Fewer is better. Return [] if it is small talk, "
        "an operator handoff, or pleasantries.\n"
        "- Do not name the company or the speaker.\n\n"
        "Reply with ONLY a JSON array of strings. No prose, no code fence.\n\n"
        "PASSAGE:\n" + text[:4000]
    )


def is_limit_cliff(envelope: dict) -> bool:
    """The 2026-08-11 signature: an error that returned instantly, took one
    turn and cost nothing. That is the usage limiter, not a bad prompt, and
    retrying into it just burns wall-clock. 267 pages died this way."""
    return bool(envelope.get("is_error")) \
        and envelope.get("duration_api_ms") == 0 \
        and envelope.get("num_turns") == 1 \
        and not envelope.get("total_cost_usd")


def parse_phrases(envelope: dict):
    """-> (phrases, status) where status is ok | empty | failed: <why>."""
    if envelope.get("is_error"):
        return [], f"failed: claude is_error {str(envelope.get('result'))[:120]}"
    raw = envelope.get("result") or ""
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return [], "failed: no JSON array in reply"
    try:
        items = json.loads(m.group(0))
    except ValueError as e:
        return [], f"failed: unparseable array ({e})"
    if not isinstance(items, list):
        return [], "failed: reply was not an array"
    phrases = [" ".join(str(x).lower().split()) for x in items
               if str(x).strip()]
    return (phrases, "ok") if phrases else ([], "empty")


def _claude_env() -> dict:
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)     # force subscription auth
    return env


def extract_phrases(text: str):
    """-> (phrases, status). Never raises; the caller records the status."""
    cmd = ["claude", "-p", extract_prompt(text),
           "--model", MODEL, "--output-format", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CLAUDE_TIMEOUT_S, env=_claude_env())
    except subprocess.TimeoutExpired:
        return [], "failed: timeout"
    except Exception as e:                            # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {e}"
    try:
        env = json.loads(proc.stdout)
    except ValueError:
        return [], f"failed: rc={proc.returncode} unparseable envelope"
    if is_limit_cliff(env):
        return [], "failed: usage-limit cliff"
    return parse_phrases(env)
