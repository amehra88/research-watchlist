#!/usr/bin/env python3
"""P4 diffusion (spec §5, §6.1–6.3, findings R4/R5): breadth counts per (theme, calendar quarter)
with their denominators, the disclosure-vs-question gap, asked-elsewhere over verified adjacency,
lifecycle stage + lag, and "newly said". Reads the P2/P3b topic map; writes a snapshot, the
append-only detection log, and a weekly report. No LLM, no embedding, no vault writes.

Prohibited by design (§5): velocity, slope, smoothing, trend lines. Counts per quarter only, with
the prior quarter printed alongside.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import adjacency as adjmod   # noqa: E402
import lifecycle as lc       # noqa: E402

REPO = Path("/root/research-watchlist")
STATE = REPO / "state" / "topics"
TOPIC_MAP = STATE / "topic_map.jsonl"
DIFFUSION = STATE / "diffusion.json"
DETECTIONS = STATE / "detections.jsonl"
EXCHANGES = REPO / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS = REPO / "state" / "evidence" / "claims.jsonl"
NO_COVERAGE = REPO / "state" / "transcripts" / "_no_coverage.json"
REPORT = REPO / "notes" / "reports" / "theme-diffusion.md"

MDNA_MIN_BLOCKS = 2        # memory mdna-evidence-p3b: one mapped MD&A block is ~half wrong at thr 0.40
NEWLY_SAID_BASELINE = 2    # findings R5: absent from the filer's two prior quarters
_FIRM_ALIASES = {"bankofamerica": "bofa", "jpmorgansecurities": "jpmorgan", "jpmorgan": "jpmorgan"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] diffusion: {msg}", flush=True)


def load_rows(path: Path = TOPIC_MAP) -> list:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_exchange_meta(path: Path = EXCHANGES) -> dict:
    """vector_id -> the exchange fields the report needs (host_hint for §10, text for citations)."""
    meta = {}
    if not path.exists():
        return meta
    for l in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        if r.get("vector_id"):
            meta[r["vector_id"]] = {k: r.get(k) for k in
                                    ("host_hint", "speaker_name", "speaker_firm", "event_name", "event_type", "text")}
    return meta


def firm_key(s) -> str:
    k = re.sub(r"[^a-z]", "", (s or "").lower())
    for a, b in _FIRM_ALIASES.items():
        if k.startswith(a):
            return b
    return k


def is_host_firm(firm, host_hint) -> bool:
    """Spec §10: the host bank asks nearly every question at its own conference. Matched on
    normalised prefixes ('Goldman Sachs Communacopia +' vs 'Goldman Sachs & Co. LLC')."""
    f, h = firm_key(firm), firm_key(host_hint)
    if len(f) < 4 or len(h) < 4:
        return False
    lcp = 0
    for a, b in zip(f, h):
        if a != b:
            break
        lcp += 1
    return lcp >= min(6, len(f), len(h))   # 'citi' (4) matches whole; longer names need 6 shared chars


def _themes(r) -> list:
    return [t["theme"] if isinstance(t, dict) else t for t in (r.get("themes") or []) if t]


def apply_mdna_block_rule(rows, min_blocks: int = MDNA_MIN_BLOCKS) -> list:
    """Drop a theme from an MD&A row unless that filer has >= min_blocks blocks mapped to it in
    the same quarter. One block at thr 0.40 is ~half wrong (GLW derivatives -> foundry_capacity);
    two independent blocks from one filing rarely agree by accident. Exchange rows are untouched.
    Returns new row dicts; the input is not mutated."""
    n = collections.Counter()
    for r in rows:
        if r.get("source") == "mdna":
            for t in _themes(r):
                n[(t, r.get("cal_quarter"), r.get("ticker"))] += 1
    out = []
    for r in rows:
        if r.get("source") != "mdna":
            out.append(r)
            continue
        keep = [t for t in (r.get("themes") or [])
                if n[((t["theme"] if isinstance(t, dict) else t), r.get("cal_quarter"), r.get("ticker"))] >= min_blocks]
        out.append({**r, "themes": keep})
    return out


def metrics(rows, meta, mdna_min_blocks: int = MDNA_MIN_BLOCKS) -> dict:
    """{(theme, cal_quarter): counts}. Weighting for any ranking: n_banks > n_companies > n_exchanges."""
    acc: dict = {}
    mdna_blocks = collections.Counter()      # (theme, cq, ticker) -> mapped MD&A blocks
    first_seen: dict = {}
    for r in rows:
        cq = r.get("cal_quarter")
        if not cq:
            continue
        for theme in _themes(r):
            key = (theme, cq)
            first_seen[theme] = min(first_seen.get(theme, cq), cq)
            m = acc.setdefault(key, {"banks": set(), "n_host_excluded": 0, "companies": set(), "n_exchanges": 0,
                                     "disclosing": set(), "corprep": set()})
            if r.get("register") == "question":
                m["n_exchanges"] += 1
                m["companies"].add(r["ticker"])
                firm = r.get("firm")
                if firm:
                    host = (meta.get(r["id"]) or {}).get("host_hint") if r.get("event_type") == "conference" else None
                    if host and is_host_firm(firm, host):
                        m["n_host_excluded"] += 1
                    else:
                        m["banks"].add(firm)
            elif r.get("register") == "evidence":
                if r.get("source") == "mdna":
                    mdna_blocks[(theme, cq, r["ticker"])] += 1
                else:
                    m["corprep"].add(r["ticker"])
    for (theme, cq, ticker), n in mdna_blocks.items():
        if n >= mdna_min_blocks:
            acc[(theme, cq)]["disclosing"].add(ticker)
    out = {}
    for (theme, cq), m in acc.items():
        out[(theme, cq)] = {
            "n_banks": len(m["banks"]), "banks": sorted(m["banks"]), "n_host_excluded": m["n_host_excluded"],
            "n_companies": len(m["companies"]), "companies": sorted(m["companies"]),
            "n_exchanges": m["n_exchanges"],
            "n_disclosing": len(m["disclosing"]), "disclosing": sorted(m["disclosing"]),
            "n_corprep_companies": len(m["corprep"]),
            "first_seen_quarter": first_seen[theme]}
    return out


def denominators(rows) -> dict:
    """Companies with ANY row (mapped or not) per quarter, per event type — never merged (§4.1)."""
    cov: dict = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        cq = r.get("cal_quarter")
        if not cq or not r.get("ticker"):
            continue
        if r.get("source") == "mdna":
            cov[cq]["mdna_filers"].add(r["ticker"])
        elif r.get("event_type") in ("earnings_call", "conference"):
            cov[cq][r["event_type"]].add(r["ticker"])
    return {cq: {k: len(cov[cq][k]) for k in ("earnings_call", "conference", "mdna_filers")} for cq in sorted(cov)}
