#!/usr/bin/env python3
"""P5b stage-transition alert (spec §7.3) — email only, deliberately thin, one line per event.

Reads the pairs in state/topics/diffusion.json (P4's per-(theme, ticker) stage snapshot), diffs
them against the stored state/topics/stages.json, and emails one line per:
  gate    — a theme clears the §7.1 breadth gate (theme_notes.clears_gate) for the first time
  stage2  — a theme's first analyst question anywhere (every carrier flips 1->2 together: one line)
  stage3  — a holding is asked for the first time (per theme, ticker)
  stage4  — a theme is now asked on most covered calls (one line per theme)
Forward moves only. Regressions (4->3 when new covered names appear) update the stored
stage silently. Births at stage 1 are already detections.jsonl; births at 2/4 are silent.

First run seeds stages.json and sends nothing. Announce-once through
state/topics/alerts_sent.jsonl (same shape as state/thesis/alerts_sent.jsonl). No LLM, no
embedding. Plan: docs/superpowers/plans/2026-09-11-stage-alert-p5b.md.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from theme_notes import clears_gate, load_sources  # noqa: E402

try:
    from newsdigest.email_send import send  # noqa: E402
except ImportError:  # pragma: no cover — tests patch sa.send
    send = None

REPO = Path("/root/research-watchlist")
STATE = REPO / "state" / "topics"
DIFFUSION = STATE / "diffusion.json"
STAGES = STATE / "stages.json"
LEDGER = STATE / "alerts_sent.jsonl"
THEMES_DIR = REPO / "notes" / "themes"
KIND_ORDER = {"gate": 0, "stage2": 1, "stage3": 2, "stage4": 3}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] stage_alert: {msg}", flush=True)


def pair_key(theme: str, ticker: str) -> str:
    return f"{theme}|{ticker}"


def _split(key: str) -> tuple:
    theme, ticker = key.split("|", 1)
    return theme, ticker


# ───────────────────────── snapshot -> comparable state ─────────────────────────

def snapshot_stages(snap: dict) -> dict:
    """{'theme|ticker': stage} from diffusion.json pairs; a pair with no stage is not a pair."""
    return {pair_key(p["theme"], p["ticker"]): p["stage"] for p in snap.get("pairs", []) if p.get("stage")}


def gated_themes(snap: dict) -> list:
    """Themes whose CURRENT-quarter cell clears the §7.1 gate. Current-quarter only: a theme
    that cleared it last quarter and no longer does is not 'crossing' anything now."""
    cq = snap.get("current_quarter")
    by_theme: dict = {}
    for m in snap.get("metrics", []):
        if m.get("cal_quarter") == cq:
            by_theme.setdefault(m["theme"], []).append(m)
    return sorted(t for t, cells in by_theme.items() if clears_gate(cells))


# ───────────────────────── the diff ─────────────────────────

def diff_events(prior: dict, cur: dict) -> list:
    """Events between two {'pairs': {key: stage}, 'gated': [theme]} states. Sorted by
    (theme, kind, ticker) so a theme's gate/stage lines sit together in the email."""
    pp, cp = prior.get("pairs", {}), cur.get("pairs", {})
    events, seen = [], set()

    def add(kind, theme, ticker=None):
        k = (kind, theme, ticker)
        if k in seen:
            return
        seen.add(k)
        e = {"kind": kind, "theme": theme}
        if ticker:
            e["ticker"] = ticker
        events.append(e)

    for key, st in cp.items():
        theme, ticker = _split(key)
        was = pp.get(key)
        if was is None:
            if st == 3:
                add("stage3", theme, ticker)       # born already asked at the holding
            continue
        if st <= was:
            continue                               # regression or no move: absorbed silently
        if st == 2:
            add("stage2", theme)
        elif st == 3:
            add("stage3", theme, ticker)
        elif st == 4:
            add("stage4", theme)
    prior_gated = set(prior.get("gated", []))
    for t in cur.get("gated", []):
        if t not in prior_gated:
            add("gate", t)
    events.sort(key=lambda e: (e["theme"], KIND_ORDER[e["kind"]], e.get("ticker") or ""))
    return events


def event_id(e: dict) -> str:
    return f"{e['kind']}:{e['theme']}" + (f":{e['ticker']}" if e.get("ticker") else "")
