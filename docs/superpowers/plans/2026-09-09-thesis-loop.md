# Thesis Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every channel (earnings, news, filings, presentations, competition, podcasts, Substacks, insiders, consensus) one write target, a per-name thesis file, and one integrated output: a weekly thesis-delta report with a ranked movers list, thin daily alerts, and a weekly operator chat.

**Architecture:** `notes/{TICKER}/_thesis.md` holds machine-drafted, operator-correctable assumptions. A daily matcher turns new evidence into confirm/challenge pressure and proposed score moves. The earnings reviewer becomes assumption-aware. A report script renders weekly/daily/quarterly outputs and a questions list; a `thesis-chat` skill answers questions interactively.

**Tech Stack:** Python 3 stdlib + PyYAML + psycopg2 (pg `chunk_store`), `scripts/lib/claude_p.py` for `claude -p` (Sonnet, lean flags; `run_mcp` for FactSet/InsiderScore), Brevo via `scripts/newsdigest/email_send.py`. Tests are plain scripts run with `python3 path/test_x.py` (no pytest here).

**Spec:** `/root/.claude/plans/i-want-to-think-temporal-parasol.md` (copied to `docs/superpowers/specs/2026-09-09-thesis-loop-design.md` in Task 12).

## Global Constraints

- `config/watchlist.yaml` is NEVER machine-written. Scores, tiers, vocabulary are operator-only.
- `auto_sync` cron is PAUSED for this build (backup `/root/backups/crontab.pre_build_20260909_101534.bak`). Restore in Task 12; commit per task meanwhile.
- All `claude -p` calls go through `scripts/lib/claude_p.run` / `run_mcp` with a `system_prompt` (lean mode) and `model="claude-sonnet-4-6"` unless stated. Abort a batch on the first 429/auth failure (`precheck`), never grind.
- Every batch job is resumable via a ledger under `state/thesis/` and idempotent on re-run.
- pg access only via `scripts/chunking/pgconn.connect()`. Never `SELECT *` from `guidance_with_track_record` (fans out ~30k rows/ticker).
- `.pvt` ids and the `A000660` alias never enter the loop (`ingest_metrics.universe()` already drops them).
- Ranking uses machine-proposed scores, labelled, with applied scores shown beside them (operator decision 2026-09-09).
- Before launching any batch: scan for orphaned `claude` sessions / running ingest jobs (`ps -eo pid,etime,cmd | grep -E "claude -p|ingest|entities"`), never kill your own tree.
- Commit messages end with the attribution block from the session (Co-Authored-By + Claude-Session lines).

## File Structure

| File | Responsibility |
|---|---|
| `scripts/thesis/__init__.py` | package marker; `REPO`, `STATE_DIR = REPO/state/thesis`, `universe()` re-export |
| `scripts/thesis/thesis_io.py` | `_thesis.md` schema constants, load/save (frontmatter round-trip, atomic), validation, score mirror, pressure/status math |
| `scripts/thesis/sources.py` | evidence collectors, one function per source, each returning `list[Evidence]` since a watermark |
| `scripts/thesis/draft_thesis.py` | CLI: draft `_thesis.md` for T1+T2 (three modes), import COHR/LITE from the draft doc |
| `scripts/thesis/match_evidence.py` | CLI (daily cron): collect → match via `claude -p` → append `evidence_log.jsonl` → update frontmatter |
| `scripts/thesis/thesis_report.py` | CLI: `--weekly`, `--alerts`, `--quarterly`, `--dry-run`; renders email + `notes/reports/`, writes `ranking_{date}.json`, maintains `questions.jsonl` |
| `scripts/thesis/apply_scores.py` | CLI: print/apply the exact watchlist YAML diff for accepted proposals (operator-invoked only) |
| `scripts/thesis/insider_pull.py` | weekly InsiderScore pull via `run_mcp`, 10b5-1 excluded → `state/thesis/insiders_{date}.jsonl` |
| `scripts/thesis/test_*.py` | one test script per module, plain asserts |
| `.claude/skills/thesis-chat/SKILL.md` | interactive weekly chat: walks open questions, records answers, applies edits via `thesis_io` |
| `.claude/agents/earnings-reviewer.md` (+ canonical copy) | Step 3 glob fix, `_thesis.md` read, new §4b |
| `scripts/cron_earnings_reviewer.py` | pre-stage writes `state/thesis/context/{TICKER}.md`; prompt mentions it |
| `scripts/chunking/ingest_metrics.py` | `--pull` stage via `run_mcp`; consensus snapshot |
| `scripts/v3_ingest/sec_filings.py` | PDF EX-99 exhibits for 8-K 2.02/7.01/8.01 |
| `scripts/chunking/store.py` | `thesis` doc_type weight |
| `scripts/check.py` | thesis file validation |

---

### Task 1: `thesis_io.py` — the thesis object

**Files:**
- Create: `scripts/thesis/__init__.py`, `scripts/thesis/thesis_io.py`
- Test: `scripts/thesis/test_thesis_io.py`

**Interfaces:**
- Produces:
  - `STATUSES = ("open","confirmed","challenged","retired")`, `SCORE_KEYS = ("ai_positioning","competitive_advantage.innovation_rate","competitive_advantage.distribution","competitive_advantage.overall","potential_investor_interest.score")`
  - `thesis_path(ticker) -> Path` (`notes/{T}/_thesis.md`)
  - `load(ticker) -> dict | None` (frontmatter dict + `"_body": str`)
  - `save(ticker, fm: dict, body: str | None = None) -> Path` (atomic; body preserved when None)
  - `validate(fm) -> list[str]` (errors)
  - `watchlist_scores(ticker) -> dict[str, str]` (mirror of the five keys, both schema variants)
  - `recompute_pressure(fm, log_rows, today, window_days=90) -> dict` (mutates + returns fm; applies the status-proposal rule; returns list of changes in `fm["_changes"]`)
  - `universe() -> list[str]` re-exported from `scripts/chunking/ingest_metrics.universe`

- [ ] **Step 1: Write the failing test**

```python
# scripts/thesis/test_thesis_io.py
"""No pytest in this env — run directly:  python3 scripts/thesis/test_thesis_io.py"""
import os, sys, tempfile, shutil
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio  # noqa: E402

def _fm():
    return {"doc_type": "thesis", "ticker": "TEST", "tier": "tier_1_bctk",
            "drafted": "2026-09-10", "reviewed_by_operator": False,
            "scores": {k: "4" for k in tio.SCORE_KEYS}, "proposed_scores": {},
            "assumptions": [{"id": "a1", "statement": "S", "derived_from": "ai_positioning: 4",
                             "themes": [], "challenged_by": ["x"], "confirmed_by": ["y"],
                             "status": "open", "status_source": "draft",
                             "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None},
                             "draft": True}]}

def test_roundtrip_preserves_body(tmp):
    tio.NOTES = tmp
    p = tio.save("TEST", _fm(), body="## Rationale\n\nhand-written\n")
    assert p.name == "_thesis.md" and p.parent.name == "TEST"
    fm2 = tio.load("TEST")
    assert fm2["assumptions"][0]["id"] == "a1"
    assert fm2["_body"].strip() == "## Rationale\n\nhand-written"
    fm2["assumptions"][0]["status"] = "confirmed"
    tio.save("TEST", fm2)            # body=None -> preserved
    assert "hand-written" in tio.load("TEST")["_body"]

def test_validate_catches_bad_status_and_dup_ids():
    fm = _fm(); fm["assumptions"].append(dict(fm["assumptions"][0]))
    fm["assumptions"][1]["status"] = "maybe"
    errs = tio.validate(fm)
    assert any("duplicate id" in e for e in errs) and any("status" in e for e in errs)

def test_pressure_rule_needs_two_sources():
    fm = _fm(); today = date(2026, 9, 10)
    rows = [{"assumption_id": "a1", "direction": "challenge", "strength": 3, "source": "news", "date": "2026-09-01"},
            {"assumption_id": "a1", "direction": "challenge", "strength": 2, "source": "news", "date": "2026-09-02"}]
    tio.recompute_pressure(fm, rows, today)
    assert fm["assumptions"][0]["status"] == "open"          # one source only
    rows.append({"assumption_id": "a1", "direction": "challenge", "strength": 1, "source": "sec_filing", "date": "2026-09-03"})
    tio.recompute_pressure(fm, rows, today)
    a = fm["assumptions"][0]
    assert a["status"] == "challenged" and a["status_source"] == "evidence"
    assert a["pressure"]["challenge"] == 6 and a["pressure"]["last_evidence"] == "2026-09-03"
    assert fm["_changes"][0]["assumption_id"] == "a1"

def test_operator_status_is_never_overridden():
    fm = _fm(); fm["assumptions"][0]["status_source"] = "operator"
    rows = [{"assumption_id": "a1", "direction": "challenge", "strength": 3, "source": "earnings_break", "date": "2026-09-01"}]
    tio.recompute_pressure(fm, rows, date(2026, 9, 10))
    assert fm["assumptions"][0]["status"] == "open"

def test_old_evidence_outside_window_ignored():
    fm = _fm()
    rows = [{"assumption_id": "a1", "direction": "confirm", "strength": 3, "source": "news", "date": "2026-01-01"}]
    tio.recompute_pressure(fm, rows, date(2026, 9, 10))
    assert fm["assumptions"][0]["pressure"]["confirm"] == 0

if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_roundtrip_preserves_body(tmp)
        test_validate_catches_bad_status_and_dup_ids()
        test_pressure_rule_needs_two_sources()
        test_operator_status_is_never_overridden()
        test_old_evidence_outside_window_ignored()
    finally:
        shutil.rmtree(tmp)
    print("OK test_thesis_io")
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd /root/research-watchlist && python3 scripts/thesis/test_thesis_io.py`
Expected: `ModuleNotFoundError: No module named 'thesis'`

- [ ] **Step 3: Implement**

```python
# scripts/thesis/__init__.py
"""Thesis loop: per-ticker `_thesis.md` objects, evidence matching, reporting."""
from pathlib import Path
REPO = Path("/root/research-watchlist")
STATE_DIR = REPO / "state" / "thesis"
```

```python
# scripts/thesis/thesis_io.py
"""Read/write/validate notes/{TICKER}/_thesis.md and the pressure/status math.

Frontmatter is the machine-read state; the body is human prose and is preserved
byte-for-byte on every save. No existing helper rewrites YAML-only, so this is the
one place that does it (regex from chunker._parse_frontmatter; atomic write pattern
from backfill_frontmatter._write_note_atomic).
"""
from __future__ import annotations
import os, re, sys, tempfile
from datetime import date, timedelta
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
NOTES = REPO / "notes"
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
from ingest_metrics import universe  # noqa: E402,F401  (T1+T2, drops A000660)

STATUSES = ("open", "confirmed", "challenged", "retired")
STATUS_SOURCES = ("draft", "evidence", "operator")
SCORE_KEYS = ("ai_positioning", "competitive_advantage.innovation_rate",
              "competitive_advantage.distribution", "competitive_advantage.overall",
              "potential_investor_interest.score")
SOURCE_WEIGHT = {"podcast_summary": 0.5, "substack_post": 0.5}   # commentary, not disclosure
CHALLENGE_THRESHOLD = 4       # strength-sum within window
MIN_SOURCES = 2               # distinct sources within window
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def thesis_path(ticker: str) -> Path:
    return NOTES / ticker / "_thesis.md"


def load(ticker: str) -> dict | None:
    p = thesis_path(ticker)
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ValueError(f"{p}: no frontmatter")
    fm = yaml.safe_load(m.group(1)) or {}
    fm["_body"] = text[m.end():]
    return fm


def save(ticker: str, fm: dict, body: str | None = None) -> Path:
    p = thesis_path(ticker)
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = {k: v for k, v in fm.items() if not k.startswith("_")}
    if body is None:
        body = (load(ticker) or {}).get("_body", "") if p.exists() else ""
    errs = validate(fm)
    if errs:
        raise ValueError(f"{p}: " + "; ".join(errs))
    content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".md", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return p


def validate(fm: dict) -> list[str]:
    errs = []
    if fm.get("doc_type") != "thesis":
        errs.append("doc_type must be 'thesis'")
    if not fm.get("ticker"):
        errs.append("ticker missing")
    seen = set()
    for a in fm.get("assumptions") or []:
        aid = a.get("id")
        if not aid or not re.match(r"^[a-z0-9_]+$", aid):
            errs.append(f"bad id {aid!r}")
        if aid in seen:
            errs.append(f"duplicate id {aid}")
        seen.add(aid)
        if a.get("status") not in STATUSES:
            errs.append(f"{aid}: status {a.get('status')!r} not in {STATUSES}")
        if a.get("status_source") not in STATUS_SOURCES:
            errs.append(f"{aid}: status_source invalid")
        if not a.get("statement"):
            errs.append(f"{aid}: statement missing")
        if not a.get("challenged_by"):
            errs.append(f"{aid}: challenged_by empty")
    for k in fm.get("scores") or {}:
        if k not in SCORE_KEYS:
            errs.append(f"unknown score key {k}")
    return errs


def _score_str(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("score")
    return None if v is None else str(v)


def watchlist_scores(ticker: str, watchlist: dict | None = None) -> dict[str, str]:
    """Mirror of the five score keys from watchlist.yaml (both schema variants)."""
    w = watchlist or yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    for tier in ("tier_1_bctk", "tier_2_active_candidates"):
        for e in w.get(tier) or []:
            if isinstance(e, dict) and e.get("ticker") == ticker:
                ca = e.get("competitive_advantage") or {}
                out = {
                    "ai_positioning": _score_str(e.get("ai_positioning")),
                    "competitive_advantage.innovation_rate": _score_str(ca.get("innovation_rate")),
                    "competitive_advantage.distribution": _score_str(ca.get("distribution")),
                    "competitive_advantage.overall": _score_str(ca.get("overall")),
                    "potential_investor_interest.score": _score_str(e.get("potential_investor_interest")),
                }
                return {k: v for k, v in out.items() if v is not None}
    return {}


def tier_of(ticker: str, watchlist: dict | None = None) -> str | None:
    w = watchlist or yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    for tier in ("tier_1_bctk", "tier_2_active_candidates"):
        for e in w.get(tier) or []:
            if isinstance(e, dict) and e.get("ticker") == ticker:
                return tier
    return None


def recompute_pressure(fm: dict, log_rows: list[dict], today: date, window_days: int = 90) -> dict:
    """Recompute per-assumption pressure from evidence rows and propose status moves.

    Rule: `challenged` when challenge strength-sum >= CHALLENGE_THRESHOLD from >= MIN_SOURCES
    distinct sources within the window, OR any row with source 'earnings_break'; `confirmed`
    symmetrically ('earnings_confirm'). Never touches an assumption whose status_source is
    'operator' or whose status is 'retired'. Records changes in fm['_changes'].
    """
    cutoff = today - timedelta(days=window_days)
    by_id: dict[str, list[dict]] = {}
    for r in log_rows:
        if not r.get("assumption_id"):
            continue
        try:
            d = date.fromisoformat(str(r.get("date"))[:10])
        except ValueError:
            continue
        if d >= cutoff:
            by_id.setdefault(r["assumption_id"], []).append(dict(r, _d=d))
    changes = []
    for a in fm.get("assumptions") or []:
        rows = by_id.get(a["id"], [])
        conf = sum(r["strength"] * SOURCE_WEIGHT.get(r["source"], 1.0) for r in rows if r["direction"] == "confirm")
        chal = sum(r["strength"] * SOURCE_WEIGHT.get(r["source"], 1.0) for r in rows if r["direction"] == "challenge")
        a["pressure"] = {"confirm": conf, "challenge": chal, "window_days": window_days,
                         "last_evidence": max((r["_d"] for r in rows), default=None) and max(r["_d"] for r in rows).isoformat()}
        if a.get("status_source") == "operator" or a.get("status") == "retired":
            continue
        chal_src = {r["source"] for r in rows if r["direction"] == "challenge"}
        conf_src = {r["source"] for r in rows if r["direction"] == "confirm"}
        new = a["status"]
        if "earnings_break" in chal_src or (chal >= CHALLENGE_THRESHOLD and len(chal_src) >= MIN_SOURCES and chal > conf):
            new = "challenged"
        elif "earnings_confirm" in conf_src or (conf >= CHALLENGE_THRESHOLD and len(conf_src) >= MIN_SOURCES and conf > chal):
            new = "confirmed"
        if new != a["status"]:
            changes.append({"assumption_id": a["id"], "from": a["status"], "to": new,
                            "evidence_ids": [r.get("source_id") for r in rows]})
            a["status"] = new
            a["status_source"] = "evidence"
    fm["_changes"] = changes
    return fm
```

- [ ] **Step 4: Run tests**

Run: `python3 scripts/thesis/test_thesis_io.py`
Expected: `OK test_thesis_io`

- [ ] **Step 5: Commit**

```bash
git add scripts/thesis/__init__.py scripts/thesis/thesis_io.py scripts/thesis/test_thesis_io.py
git commit -m "thesis: _thesis.md object — frontmatter round-trip, validation, pressure/status rule"
```

---

### Task 2: `draft_thesis.py` — draft assumptions for every T1+T2 name

**Files:**
- Create: `scripts/thesis/draft_thesis.py`
- Test: `scripts/thesis/test_draft_thesis.py`
- Modify: `scripts/chunking/store.py:56` (`_DOC_TYPE_WEIGHTS` add `"thesis": 1.00`)

**Interfaces:**
- Consumes: `thesis_io.save/load/watchlist_scores/tier_of/universe`; `claude_p.run`; `pgconn.connect` (MD&A for thin mode); `docs/thesis-assumptions-draft.md` for COHR/LITE.
- Produces: `notes/{T}/_thesis.md` per ticker; `state/thesis/_draft_progress.json` ledger `{ticker: {"status": "ok|failed|skipped", "mode": ..., "ts": ...}}`; functions `gather_inputs(ticker) -> dict(mode, scores, scoring_notes, earnings_notes[], mdna, news[])`, `build_prompt(inputs) -> str`, `parse_assumptions(text) -> list[dict]`, `import_draft_doc() -> dict[ticker, list[assumption]]`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/thesis/test_draft_thesis.py
"""Run directly: python3 scripts/thesis/test_draft_thesis.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import draft_thesis as dt  # noqa: E402

def test_mode_selection():
    assert dt.pick_mode(scores={"ai_positioning": "4"}, earnings_notes=["x"]) == "scores"
    assert dt.pick_mode(scores={}, earnings_notes=["x"]) == "notes"
    assert dt.pick_mode(scores={}, earnings_notes=[]) == "thin"

def test_parse_assumptions_rejects_overreads():
    good = json.dumps({"assumptions": [{"id": "ramp_continues", "statement": "The 800G ramp continues to pull volume.",
        "derived_from": "ai_positioning: 4", "themes": ["ai_infrastructure_capex"],
        "challenged_by": ["capex digestion"], "confirmed_by": ["1.6T design wins"]}]})
    out = dt.parse_assumptions(good)
    assert out[0]["status"] == "open" and out[0]["draft"] is True and out[0]["status_source"] == "draft"
    bad = json.dumps({"assumptions": [{"id": "x", "statement": "Supply remains tight, supporting share.",
        "derived_from": "d", "themes": [], "challenged_by": ["a"], "confirmed_by": []}]})
    try:
        dt.parse_assumptions(bad); assert False, "should reject 'remains'"
    except dt.OverreadError:
        pass

def test_import_draft_doc_has_cohr_and_lite():
    d = dt.import_draft_doc()
    assert "COHR" in d and "LITE" in d
    ids = {a["id"] for a in d["COHR"]}
    assert "chinese_laser_capability" in ids and "datacom_ramp_continues" in ids
    assert all(a["challenged_by"] for t in d.values() for a in t)

def test_prompt_contains_guardrails():
    p = dt.build_prompt({"ticker": "T", "mode": "scores", "scores": {"ai_positioning": "4"},
                         "scoring_notes": "n", "score_notes": {}, "themes": ["t"], "earnings_notes": [], "mdna": "", "news": []})
    for w in ("watch-item stays a watch-item", "durable", "remains", "offsetting", "JSON"):
        assert w in p

if __name__ == "__main__":
    test_mode_selection(); test_parse_assumptions_rejects_overreads()
    test_import_draft_doc_has_cohr_and_lite(); test_prompt_contains_guardrails()
    print("OK test_draft_thesis")
```

- [ ] **Step 2: Run to verify it fails** — `python3 scripts/thesis/test_draft_thesis.py` → `ImportError`/`AttributeError`.

- [ ] **Step 3: Implement**

```python
# scripts/thesis/draft_thesis.py
#!/usr/bin/env python3
"""Draft notes/{TICKER}/_thesis.md for T1+T2 names (three input modes).

    python3 scripts/thesis/draft_thesis.py --all                 # every T1+T2 ticker lacking a file
    python3 scripts/thesis/draft_thesis.py --ticker COHR --dry-run
    python3 scripts/thesis/draft_thesis.py --ticker X --force    # regenerate, keep draft:false assumptions
    python3 scripts/thesis/draft_thesis.py --missing-only        # weekly cron form

Drafting rule (the COHR/LITE lesson, docs/thesis-assumptions-draft.md): claim only what the
operator's score/notes imply. Eight of eleven hand drafts had to be corrected for hardening a
watch-item or observation into a forward assertion. The prompt forbids it and parse_assumptions
rejects the tell-tale words.
"""
from __future__ import annotations
import argparse, glob, json, re, sys
from datetime import date, datetime, timezone
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
from lib import claude_p                        # noqa: E402
from thesis import thesis_io as tio             # noqa: E402
from thesis import STATE_DIR                    # noqa: E402

MODEL = "claude-sonnet-4-6"
LEDGER = STATE_DIR / "_draft_progress.json"
DRAFT_DOC = REPO / "docs" / "thesis-assumptions-draft.md"
OVERREAD_RE = re.compile(r"\b(remains?|durable|offset(?:s|ting)?|contained|stable|on track|continues to come down)\b", re.I)
SYSTEM = ("You are a buy-side research analyst decomposing a PM's scoring notes into testable thesis "
          "assumptions. Output JSON only.")


class OverreadError(ValueError):
    pass


def pick_mode(scores: dict, earnings_notes: list) -> str:
    if scores:
        return "scores"
    return "notes" if earnings_notes else "thin"


def _watchlist_entry(ticker: str, w: dict) -> dict:
    for tier in ("tier_1_bctk", "tier_2_active_candidates"):
        for e in w.get(tier) or []:
            if isinstance(e, dict) and e.get("ticker") == ticker:
                return e
    return {}


def _latest_notes(ticker: str, n: int = 2) -> list[tuple[str, str]]:
    paths = sorted(glob.glob(str(REPO / "notes" / ticker / "[0-9]*-[1-4]Q[0-9][0-9].md")))[-n:]
    return [(Path(p).relative_to(REPO).as_posix(), Path(p).read_text(encoding="utf-8")[:9000]) for p in paths]


def _mdna(ticker: str) -> str:
    from pgconn import connect
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""SELECT text FROM chunks WHERE kind='parent' AND doc_type='sec_filing'
                       AND %s = ANY(tickers) AND section ILIKE 'Item %%Management%%'
                       ORDER BY event_date DESC NULLS LAST LIMIT 1""", (ticker,))
        row = cur.fetchone()
    return (row[0] if row else "")[:8000]


def _recent_news(ticker: str, days: int = 30, cap: int = 8) -> list[str]:
    from thesis.sources import news_since   # Task 3
    cutoff = date.fromordinal(date.today().toordinal() - days)
    return [e.text[:600] for e in news_since(ticker, cutoff)][:cap]


def gather_inputs(ticker: str, w: dict | None = None) -> dict:
    w = w or yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    e = _watchlist_entry(ticker, w)
    scores = tio.watchlist_scores(ticker, w)
    notes = _latest_notes(ticker)
    mode = pick_mode(scores, notes)
    score_notes = {}
    for k in ("ai_positioning", "competitive_advantage", "potential_investor_interest"):
        v = e.get(k)
        if isinstance(v, dict) and v.get("notes"):
            score_notes[k] = v["notes"]
    return {"ticker": ticker, "mode": mode, "tier": tio.tier_of(ticker, w), "scores": scores,
            "score_notes": score_notes, "scoring_notes": e.get("scoring_notes") or e.get("notes") or "",
            "themes": e.get("themes") or [], "earnings_notes": notes,
            "mdna": _mdna(ticker) if mode != "scores" else "",
            "news": _recent_news(ticker) if mode == "thin" else []}


def build_prompt(i: dict) -> str:
    n_max = 3 if i["mode"] == "thin" else 6
    parts = [f"TICKER: {i['ticker']}   MODE: {i['mode']}   THEMES: {', '.join(i['themes'])}",
             "SCORES (1-5, + / - = trajectory): " + json.dumps(i["scores"]),
             "SCORE NOTES:\n" + json.dumps(i["score_notes"], indent=1)[:6000],
             "SCORING NOTES:\n" + i["scoring_notes"][:3000]]
    for path, text in i["earnings_notes"]:
        parts.append(f"EARNINGS NOTE {path}:\n{text}")
    if i["mdna"]:
        parts.append("LATEST MD&A (excerpt):\n" + i["mdna"])
    for n in i["news"]:
        parts.append("RECENT NEWS: " + n)
    rules = f"""
RULES — non-negotiable:
- Write 3 to {n_max} assumptions the PM's own notes actually imply. Each is a statement that evidence could refute.
- Claim ONLY what the score itself implies. A watch-item stays a watch-item (an assumption that it does not worsen), never a claim that it is improving.
- NEVER add words the notes do not state: "durable", "remains", "offsetting", "contained", "stable", "on track". Do not invent a causal mechanism.
- Point-in-time observations ("supply tight amid ...") become "conditions at scoring still hold", not forward assertions.
- challenged_by / confirmed_by must be OBSERVABLE events (a filing, a design win, a customer qualifying a second source), not opinions.
- themes: pick only from the ticker's THEMES list above.
- id: snake_case, <= 40 chars, unique.
Output JSON only: {{"assumptions": [{{"id": "...", "statement": "...", "derived_from": "<score key>: <value> — <quoted phrase>",
 "themes": [...], "challenged_by": ["..."], "confirmed_by": ["..."]}}]}}"""
    return "\n\n".join(parts) + "\n" + rules


def parse_assumptions(text: str) -> list[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0) if m else text)
    out = []
    for a in data["assumptions"]:
        if OVERREAD_RE.search(a["statement"]):
            raise OverreadError(f"{a['id']}: over-read wording in statement: {a['statement']!r}")
        out.append({"id": a["id"], "statement": a["statement"].strip(), "derived_from": a.get("derived_from", ""),
                    "themes": list(a.get("themes") or []), "challenged_by": list(a.get("challenged_by") or []),
                    "confirmed_by": list(a.get("confirmed_by") or []), "status": "open", "status_source": "draft",
                    "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None}, "draft": True})
    return out


def import_draft_doc() -> dict[str, list[dict]]:
    """COHR/LITE assumptions from docs/thesis-assumptions-draft.md (### `id` sections)."""
    text = DRAFT_DOC.read_text(encoding="utf-8")
    out: dict[str, list[dict]] = {}
    ticker = None
    for block in re.split(r"\n(?=#{2,3} )", text):
        h = block.split("\n", 1)[0]
        if h.startswith("## ") and re.match(r"## ([A-Z]{2,5}) ", h):
            ticker = re.match(r"## ([A-Z]{2,5}) ", h).group(1); continue
        m = re.match(r"### `([a-z0-9_]+)`", h)
        if not (m and ticker):
            continue
        aid = m.group(1)
        st = re.search(r"\*\*Statement:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)", block, re.S)
        ch = re.search(r"\*\*Challenged by:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)", block, re.S)
        cf = re.search(r"\*\*Confirmed by:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)", block, re.S)
        df = re.search(r"\*\*Derived from:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)", block, re.S)
        split = lambda s: [x.strip(" .") for x in re.split(r";", s.replace("\n", " ")) if x.strip()]
        entry = {"id": aid, "statement": re.sub(r"\s+", " ", st.group(1)).strip() if st else "",
                 "derived_from": re.sub(r"\s+", " ", df.group(1)).strip() if df else "operator",
                 "themes": [], "challenged_by": split(ch.group(1)) if ch else ["operator to specify"],
                 "confirmed_by": split(cf.group(1)) if cf else [], "status": "open", "status_source": "operator",
                 "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None}, "draft": False}
        if "policy_shelter" in aid:
            entry["status"] = "retired"; entry["statement"] = entry["statement"] or "Policy shelter is a watch item, not an assumption (operator 2026-08-21)."
        if aid == "chinese_laser_capability" and ticker == "LITE":
            entry["statement"] = entry["statement"] or "Shared with COHR: Chinese vendors have not yet closed the high-end laser gap (see COHR)."
        out.setdefault(ticker, []).append(entry)
    return out


def draft_one(ticker: str, w: dict, force: bool = False, dry_run: bool = False) -> str:
    existing = tio.load(ticker)
    if existing and not force:
        return "skipped-exists"
    if existing and existing.get("reviewed_by_operator"):
        return "skipped-reviewed"
    i = gather_inputs(ticker, w)
    imported = import_draft_doc().get(ticker)
    if imported:
        assumptions, mode = imported, "imported"
    else:
        text, cost, _ = claude_p.run(build_prompt(i), system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=300)
        assumptions, mode = parse_assumptions(text), i["mode"]
    if existing and force:   # keep operator-touched assumptions
        keep = [a for a in existing["assumptions"] if not a.get("draft")]
        ids = {a["id"] for a in keep}
        assumptions = keep + [a for a in assumptions if a["id"] not in ids]
    fm = {"doc_type": "thesis", "ticker": ticker, "tier": i["tier"], "drafted": date.today().isoformat(),
          "draft_mode": mode, "thin_inputs": mode == "thin",
          "drafted_from": [f"config/watchlist.yaml#{ticker}"] + [p for p, _ in i["earnings_notes"]],
          "reviewed_by_operator": False, "scores": i["scores"],
          "proposed_scores": (existing or {}).get("proposed_scores", {}), "assumptions": assumptions}
    body = (existing or {}).get("_body") or (f"## Rationale\n\nDrafted {fm['drafted']} in mode `{mode}` from the sources in "
            f"`drafted_from`. Edit statements freely; set `draft: false` on any assumption you have reviewed.\n")
    if dry_run:
        print(yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)); return "dry-run"
    tio.save(ticker, fm, body)
    return f"written:{mode}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", action="append")
    ap.add_argument("--all", action="store_true"); ap.add_argument("--missing-only", action="store_true")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    w = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    tickers = a.ticker or [t for t in tio.universe() if not t.endswith(".pvt")]
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    for t in tickers:
        if a.missing_only and tio.thesis_path(t).exists():
            continue
        try:
            r = draft_one(t, w, force=a.force, dry_run=a.dry_run)
            ledger[t] = {"status": "ok", "result": r, "ts": datetime.now(timezone.utc).isoformat()}
            print(f"{t}: {r}")
        except OverreadError as e:
            ledger[t] = {"status": "failed", "error": str(e)[:200]}; print(f"{t}: OVERREAD {e}")
        except RuntimeError as e:   # claude -p failure: fail loud, stop the batch
            ledger[t] = {"status": "failed", "error": str(e)[:200]}
            LEDGER.write_text(json.dumps(ledger, indent=1)); print(f"{t}: ABORT {e}"); return 1
        if not a.dry_run:
            LEDGER.write_text(json.dumps(ledger, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Also in `scripts/chunking/store.py` `_DOC_TYPE_WEIGHTS`: add `"thesis": 1.00,` with the comment `# operator thesis object — neutral weight`.

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_draft_thesis.py` → `OK test_draft_thesis` (Task 3's `sources.news_since` is only imported lazily in thin mode, so tests pass before Task 3 exists).

- [ ] **Step 5: Gold check + one real draft**

Run: `python3 scripts/thesis/draft_thesis.py --ticker COHR --dry-run` → uses the imported doc; confirm `chinese_laser_capability` has `status_source: operator`, `draft: false`.
Run: `python3 scripts/thesis/draft_thesis.py --ticker MRVL --dry-run` → mode `scores`, 3-6 assumptions, no OverreadError; read the statements against the MRVL scoring notes and reject anything the notes do not say.

- [ ] **Step 6: Commit** — `git add scripts/thesis/draft_thesis.py scripts/thesis/test_draft_thesis.py scripts/chunking/store.py && git commit -m "thesis: drafter (scores/notes/thin modes) + COHR/LITE import from the assumptions draft"`

- [ ] **Step 7: Batch run (after Task 3 lands, so thin mode works)** — orphan scan first, then `python3 scripts/thesis/draft_thesis.py --all 2>&1 | tee logs/draft_thesis.log`. Expected ≈90 files, ledger all `ok`. Spot-read NVDA, ANET, CBRS, INTC (mode notes), DPC (mode thin). Commit `notes/*/_thesis.md` + `state/thesis/_draft_progress.json` as "thesis: initial drafts for T1+T2".

---

### Task 3: `sources.py` — evidence collectors

**Files:**
- Create: `scripts/thesis/sources.py`
- Test: `scripts/thesis/test_sources.py`

**Interfaces:**
- Produces: `@dataclass Evidence(source: str, source_id: str, ticker: str, date: str, title: str, text: str, ref: str, cross_ticker: bool = False)` and collectors, each `(ticker, since: date) -> list[Evidence]`:
  `earnings_notes_since`, `news_since`, `sec_since`, `entity_claims_since`, `commentary_since` (substack+podcast), `conference_since` (conf notes + `state/transcripts/exchanges.jsonl` corprep conference rows), `operator_notes_since`; plus `collect_all(ticker, since) -> list[Evidence]` (concatenated, sorted by date, deduped on `source_id`). `source` values: `earnings_note | news | sec_filing | entity_claim | substack_post | podcast_summary | conference | operator_note`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/thesis/test_sources.py
"""Run directly: python3 scripts/thesis/test_sources.py  (uses real notes/ + pg read-only)"""
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import sources as S  # noqa: E402

def test_news_filter_from_disk():
    ev = S.news_since("NVDA", date(2026, 9, 1))
    assert ev and all(e.source == "news" and e.ticker == "NVDA" for e in ev)
    assert all(e.date >= "2026-09-01" for e in ev)
    assert all(e.source_id.startswith("notes/news/") for e in ev)

def test_earnings_notes_glob_matches_real_names():
    ev = S.earnings_notes_since("AMBA", date(2026, 8, 1))
    assert any(e.source_id.endswith("2Q27.md") for e in ev)
    assert "## 4." in ev[-1].text          # thesis-read section carried through

def test_entity_claims_use_subject_or_affects():
    ev = S.entity_claims_since("COHR", date(2026, 8, 1))
    assert any("Accelink" in e.title or "Innolight" in e.title for e in ev)
    assert all(e.source == "entity_claim" for e in ev)

def test_collect_all_dedups_and_sorts():
    ev = S.collect_all("COHR", date(2026, 8, 1))
    ids = [e.source_id for e in ev]
    assert len(ids) == len(set(ids)) and ids == [e.source_id for e in sorted(ev, key=lambda e: e.date)]

if __name__ == "__main__":
    test_news_filter_from_disk(); test_earnings_notes_glob_matches_real_names()
    test_entity_claims_use_subject_or_affects(); test_collect_all_dedups_and_sorts()
    print("OK test_sources")
```

- [ ] **Step 2: Run to verify it fails** — `ImportError`.

- [ ] **Step 3: Implement**

```python
# scripts/thesis/sources.py
"""Evidence collectors: one function per channel, all returning Evidence since a date.

News comes from DISK (notes/news/{YYYY-MM-DD}-*.md) because the frontmatter filter
(summarized / confidence) is not expressible against pg. Everything else comes from pg
parent chunks or existing state files. Read-only everywhere.
"""
from __future__ import annotations
import glob, json, re, sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TEXT_CAP = 3500


@dataclass
class Evidence:
    source: str
    source_id: str
    ticker: str
    date: str          # ISO
    title: str
    text: str
    ref: str           # path or url for the report citation
    cross_ticker: bool = False


def _fm_and_body(path: Path) -> tuple[dict, str]:
    t = path.read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(t)
    if not m:
        return {}, t
    try:
        return (yaml.safe_load(m.group(1)) or {}), t[m.end():]
    except yaml.YAMLError:
        return {}, t


def _pg():
    from pgconn import connect
    return connect()


def earnings_notes_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / ticker / "[0-9]*-[1-4]Q[0-9][0-9].md"))):
        d = Path(p).name[:8]
        iso = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        if iso < since.isoformat():
            continue
        fm, body = _fm_and_body(Path(p))
        keep = re.findall(r"(## (?:1|3|4|4b|5|6|7)\..*?)(?=\n## |\Z)", body, re.S)
        out.append(Evidence("earnings_note", Path(p).relative_to(REPO).as_posix(), ticker, iso,
                            Path(p).stem, "\n".join(keep)[:12000], Path(p).relative_to(REPO).as_posix()))
    return out


def news_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / "news" / "*.md"))):
        name = Path(p).name
        if name[:10] < since.isoformat():
            continue
        fm, body = _fm_and_body(Path(p))
        if ticker not in (fm.get("tickers") or []):
            continue
        if not (fm.get("summarized", True) or fm.get("confidence") == "high"):
            continue
        title = (fm.get("cluster_headlines") or [name])[0]
        out.append(Evidence("news", f"notes/news/{name}", ticker, name[:10], title,
                            (fm.get("rationale", "") + "\n" + body)[:TEXT_CAP], (fm.get("source_urls") or [name])[0]))
    return out


def sec_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT doc_id, section, event_date, text FROM chunks
           WHERE kind='parent' AND doc_type='sec_filing' AND %s = ANY(tickers) AND event_date > %s
             AND (section LIKE 'Exhibit EX-99%%' OR section ILIKE 'Item %%Management%%' OR section LIKE '%%body')
           ORDER BY event_date"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, since))
        return [Evidence("sec_filing", f"pg:{r[0]}:{r[1]}", ticker, r[2].isoformat(), r[1], r[3][:TEXT_CAP], f"pg chunks doc_id={r[0]}")
                for r in cur.fetchall()]


def entity_claims_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT chunk_id, entity, claim, stance, confidence, event_date, extracted_at, subject, affects, doc_type
           FROM entity_mentions WHERE (subject = %s OR %s = ANY(affects)) AND extracted_at > %s ORDER BY extracted_at"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, ticker, since))
        rows = cur.fetchall()
    out = []
    for r in rows:
        d = (r[5] or r[6].date()).isoformat()
        out.append(Evidence("entity_claim", f"pg:em:{r[0]}:{r[1]}", ticker, d, f"{r[1]} ({r[3]}, {r[4]})",
                            f"{r[1]}: {r[2]}", f"pg entity_mentions chunk_id={r[0]}", cross_ticker=(r[7] != ticker)))
    return out


def commentary_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT doc_id, doc_type, section, event_date, text FROM chunks
           WHERE kind='parent' AND doc_type IN ('substack_post','podcast_summary') AND %s = ANY(tickers) AND event_date > %s
           ORDER BY event_date"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, since))
        return [Evidence(r[1], f"pg:{r[0]}:{r[2]}", ticker, r[3].isoformat(), r[2], r[4][:TEXT_CAP], f"pg doc_id={r[0]}") for r in cur.fetchall()]


def conference_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / ticker / "*-conf-*.md"))):
        d = Path(p).name[:8]; iso = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        if iso < since.isoformat():
            continue
        fm, body = _fm_and_body(Path(p))
        keep = re.findall(r"(## (?:2|3)\..*?)(?=\n## |\Z)", body, re.S)
        out.append(Evidence("conference", Path(p).relative_to(REPO).as_posix(), ticker, iso, Path(p).stem, "\n".join(keep)[:8000], Path(p).relative_to(REPO).as_posix()))
    ex = REPO / "state" / "transcripts" / "exchanges.jsonl"
    if ex.exists():
        for line in ex.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ticker") != ticker or r.get("event_type") != "conference" or r.get("speaker_type") != "corprep":
                continue
            if (r.get("event_date") or "") <= since.isoformat():
                continue
            out.append(Evidence("conference", f"exch:{r['vector_id']}", ticker, r["event_date"], r.get("event_name") or "conference",
                                r.get("text", "")[:TEXT_CAP], f"FactSet transcript {r.get('document_id')}"))
    return out


def operator_notes_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / "inbox" / "*.summary.md"))):
        fm, body = _fm_and_body(Path(p))
        d = str(fm.get("ingestion_date") or fm.get("event_date") or "")[:10]
        if ticker not in (fm.get("tickers") or []) or d <= since.isoformat():
            continue
        out.append(Evidence("operator_note", Path(p).relative_to(REPO).as_posix(), ticker, d, Path(p).stem, body[:8000], Path(p).relative_to(REPO).as_posix()))
    return out


COLLECTORS = (earnings_notes_since, news_since, sec_since, entity_claims_since, commentary_since, conference_since, operator_notes_since)


def collect_all(ticker: str, since: date) -> list[Evidence]:
    seen, out = set(), []
    for fn in COLLECTORS:
        for e in fn(ticker, since):
            if e.source_id in seen:
                continue
            seen.add(e.source_id); out.append(e)
    return sorted(out, key=lambda e: e.date)
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_sources.py` → `OK test_sources`. If the entity test fails, check `SELECT count(*) FROM entity_mentions WHERE subject='COHR' OR 'COHR' = ANY(affects)` before touching code.

- [ ] **Step 5: Commit** — `git add scripts/thesis/sources.py scripts/thesis/test_sources.py && git commit -m "thesis: evidence collectors for all channels (disk news, pg filings/claims/commentary, conferences, inbox)"`

---

### Task 4: `match_evidence.py` — the daily matcher

**Files:**
- Create: `scripts/thesis/match_evidence.py`
- Test: `scripts/thesis/test_match_evidence.py`

**Interfaces:**
- Consumes: `sources.collect_all`, `thesis_io.load/save/recompute_pressure/watchlist_scores`, `claude_p.run`, `classify_llm._detect_session_limit`.
- Produces: `state/thesis/evidence_log.jsonl` rows `{ts, ticker, source, source_id, ref, date, assumption_id|null, direction, strength, why, quote, cross_ticker}`; `state/thesis/watermarks.json` `{ticker: ISO date}`; `state/thesis/changes.jsonl` (status and proposed-score changes, `{ts, ticker, kind: "status"|"proposed_score", ...}`); functions `build_prompt(fm, evidence) -> str`, `parse_verdicts(text, evidence) -> list[dict]`, `lift_score_recs(evidence_note_text) -> dict[score_key, value]`, `run_ticker(ticker, since, today, dry_run) -> dict(stats)`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/thesis/test_match_evidence.py
"""Run directly: python3 scripts/thesis/test_match_evidence.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import match_evidence as M  # noqa: E402
from thesis.sources import Evidence  # noqa: E402

EV = [Evidence("news", "notes/news/a.md", "COHR", "2026-09-02", "Innolight adds 1.6T capacity", "text a", "u1"),
      Evidence("sec_filing", "pg:d1:8-K body", "COHR", "2026-09-03", "8-K body", "text b", "pg d1")]

def test_parse_verdicts_maps_by_index_and_validates():
    txt = json.dumps({"verdicts": [
        {"i": 0, "assumption_id": "supply_was_tight_at_scoring", "direction": "challenge", "strength": 2, "why": "w", "quote": "q"},
        {"i": 1, "assumption_id": None, "direction": "neutral", "strength": 0, "why": "", "quote": ""},
        {"i": 7, "assumption_id": "x", "direction": "confirm", "strength": 9, "why": "", "quote": ""}]})
    out = M.parse_verdicts(txt, EV, valid_ids={"supply_was_tight_at_scoring"})
    assert len(out) == 2 and out[0]["source_id"] == "notes/news/a.md" and out[0]["strength"] == 2
    assert out[1]["assumption_id"] is None

def test_lift_score_recs():
    note = """## 5. AI positioning signal
- **Current score:** 4
- **Recommendation:** drift to 4+
## 6. Competitive advantage signal
- **Innovation rate** (current: 4)
  - Recommendation: hold
- **Distribution** (current: 3)
  - Recommendation: revise to 4
- **Overall** (current: 4)
  - Recommendation: hold
## 7. Potential investor interest signal
- **Recommendation:** under review
"""
    r = M.lift_score_recs(note)
    assert r == {"ai_positioning": "4+", "competitive_advantage.distribution": "4"}

def test_earnings_break_becomes_strength3_row():
    note = "## 4b. Assumption read\n- supply_was_tight_at_scoring: Challenge — lead times normalised (Q&A)\n- datacom_ramp_continues: Confirm — 1.6T ramping (prepared remarks)\n- other: Silent\n"
    rows = M.rows_from_4b(note, Evidence("earnings_note", "notes/COHR/x.md", "COHR", "2026-09-04", "x", note, "notes/COHR/x.md"),
                          valid_ids={"supply_was_tight_at_scoring", "datacom_ramp_continues", "other"})
    assert {r["source"] for r in rows} == {"earnings_break", "earnings_confirm"} and all(r["strength"] == 3 for r in rows)

def test_prompt_lists_every_assumption_and_item():
    fm = {"ticker": "COHR", "assumptions": [{"id": "a1", "statement": "S1", "challenged_by": ["c"], "confirmed_by": ["k"]}]}
    p = M.build_prompt(fm, EV)
    assert "a1" in p and "[0]" in p and "[1]" in p and "JSON" in p

if __name__ == "__main__":
    test_parse_verdicts_maps_by_index_and_validates(); test_lift_score_recs()
    test_earnings_break_becomes_strength3_row(); test_prompt_lists_every_assumption_and_item()
    print("OK test_match_evidence")
```

- [ ] **Step 2: Run to verify it fails** — `ImportError`.

- [ ] **Step 3: Implement**

```python
# scripts/thesis/match_evidence.py
#!/usr/bin/env python3
"""Daily: match new evidence against each ticker's assumptions; update _thesis.md pressure.

    python3 scripts/thesis/match_evidence.py                       # all T1+T2 since watermarks (cron)
    python3 scripts/thesis/match_evidence.py --ticker COHR,LITE --since 2026-08-01 --dry-run
    python3 scripts/thesis/match_evidence.py --max-tickers 20      # bound a catch-up run

One claude -p per ticker with new evidence; tickers with nothing new cost nothing. A 429 or
auth failure aborts the run (precheck) — never grind. Watermark advances only past what was sent.
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from lib import claude_p                                   # noqa: E402
from newsdigest.classify_llm import _detect_session_limit, SessionLimitError  # noqa: E402
from thesis import STATE_DIR, thesis_io as tio             # noqa: E402
from thesis.sources import Evidence, collect_all           # noqa: E402

MODEL = "claude-sonnet-4-6"
LOG = STATE_DIR / "evidence_log.jsonl"
CHANGES = STATE_DIR / "changes.jsonl"
WATERMARKS = STATE_DIR / "watermarks.json"
CHAR_CAP = 12_000
DEFAULT_LOOKBACK_DAYS = 3
SYSTEM = "You are a buy-side analyst testing thesis assumptions against new evidence. Output JSON only."
_REC_RE = re.compile(r"(?:drift to|revise to)\s+([1-5][+-]?)", re.I)


def _precheck(stdout: str):
    hint = _detect_session_limit(stdout)
    if hint is not None:
        raise SessionLimitError(hint)


def build_prompt(fm: dict, evidence: list[Evidence]) -> str:
    lines = [f"TICKER: {fm['ticker']}", "ASSUMPTIONS (id — statement — what would challenge it — what would confirm it):"]
    for a in fm["assumptions"]:
        if a.get("status") == "retired":
            continue
        lines.append(f"- {a['id']} — {a['statement']} — CHALLENGED BY: {'; '.join(a.get('challenged_by') or [])} — CONFIRMED BY: {'; '.join(a.get('confirmed_by') or [])}")
    lines.append("\nEVIDENCE ITEMS (index, source, date, title, text):")
    used = 0
    for i, e in enumerate(evidence):
        block = f"[{i}] {e.source} {e.date} {e.title}{' (cross-ticker)' if e.cross_ticker else ''}\n{e.text}\n"
        lines.append(block); used += len(block)
    lines.append("""
For EVERY index above return one verdict. Match to an assumption ONLY when the item bears on that assumption's
challenged_by or confirmed_by conditions; otherwise assumption_id null and direction neutral. strength: 1 = weak/indirect,
2 = clear but single-source or secondary, 3 = primary disclosure that directly meets a stated condition. quote <= 200 chars, verbatim.
Output JSON only: {"verdicts": [{"i": 0, "assumption_id": "..."|null, "direction": "confirm"|"challenge"|"neutral", "strength": 0-3, "why": "...", "quote": "..."}]}""")
    return "\n".join(lines)


def parse_verdicts(text: str, evidence: list[Evidence], valid_ids: set[str]) -> list[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0) if m else text)
    out = []
    for v in data.get("verdicts", []):
        i = v.get("i")
        if not isinstance(i, int) or i < 0 or i >= len(evidence):
            continue
        aid = v.get("assumption_id")
        if aid not in valid_ids:
            aid = None
        direction = v.get("direction") if v.get("direction") in ("confirm", "challenge", "neutral") else "neutral"
        strength = min(3, max(0, int(v.get("strength") or 0)))
        if aid is None:
            direction, strength = "neutral", 0
        e = evidence[i]
        out.append({"source": e.source, "source_id": e.source_id, "ref": e.ref, "date": e.date, "title": e.title,
                    "assumption_id": aid, "direction": direction, "strength": strength,
                    "why": (v.get("why") or "")[:300], "quote": (v.get("quote") or "")[:200], "cross_ticker": e.cross_ticker})
    return out


def lift_score_recs(note_text: str) -> dict[str, str]:
    """Explicit 'drift to X' / 'revise to X' recommendations in an earnings note, by score key."""
    out = {}
    sec = {}
    for m in re.finditer(r"## (5|6|7)\..*?(?=\n## |\Z)", note_text, re.S):
        sec[m.group(1)] = m.group(0)
    if "5" in sec and (r := _REC_RE.search(sec["5"])):
        out["ai_positioning"] = r.group(1)
    if "6" in sec:
        for label, key in (("Innovation rate", "competitive_advantage.innovation_rate"), ("Distribution", "competitive_advantage.distribution"), ("Overall", "competitive_advantage.overall")):
            blk = re.search(rf"\*\*{label}\*\*.*?(?=\n- \*\*|\Z)", sec["6"], re.S)
            if blk and (r := _REC_RE.search(blk.group(0))):
                out[key] = r.group(1)
    if "7" in sec and (r := _REC_RE.search(sec["7"])):
        out["potential_investor_interest.score"] = r.group(1)
    return out


def rows_from_4b(note_text: str, e: Evidence, valid_ids: set[str]) -> list[dict]:
    """§4b 'Assumption read' lines become strength-3 rows with source earnings_break/earnings_confirm."""
    sec = re.search(r"## 4b\..*?(?=\n## |\Z)", note_text, re.S)
    if not sec:
        return []
    rows = []
    for m in re.finditer(r"^- ([a-z0-9_]+):\s*(Confirm|Challenge|Silent)\b\s*[—-]?\s*(.*)$", sec.group(0), re.M):
        aid, verdict, why = m.groups()
        if aid not in valid_ids or verdict == "Silent":
            continue
        rows.append({"source": "earnings_break" if verdict == "Challenge" else "earnings_confirm", "source_id": e.source_id + f"#4b:{aid}",
                     "ref": e.ref, "date": e.date, "title": e.title, "assumption_id": aid,
                     "direction": "challenge" if verdict == "Challenge" else "confirm", "strength": 3, "why": why[:300], "quote": "", "cross_ticker": False})
    return rows


def _existing_ids() -> set[str]:
    if not LOG.exists():
        return set()
    return {f"{json.loads(l)['ticker']}|{json.loads(l)['source_id']}|{json.loads(l).get('assumption_id')}" for l in LOG.read_text().splitlines() if l.strip()}


def _append(path: Path, rows: list[dict]):
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _log_rows_for(ticker: str) -> list[dict]:
    if not LOG.exists():
        return []
    return [r for r in (json.loads(l) for l in LOG.read_text().splitlines() if l.strip()) if r["ticker"] == ticker]


def run_ticker(ticker: str, since: date, today: date, dry_run: bool = False, watchlist: dict | None = None) -> dict:
    fm = tio.load(ticker)
    if not fm:
        return {"ticker": ticker, "skipped": "no-thesis"}
    evidence = collect_all(ticker, since)
    stats = {"ticker": ticker, "evidence": len(evidence), "rows": 0, "changes": 0}
    if not evidence:
        return stats
    valid = {a["id"] for a in fm["assumptions"] if a.get("status") != "retired"}
    rows, sent, used = [], [], 0
    for e in evidence:
        if e.source == "earnings_note":
            rows += rows_from_4b(e.text, e, valid)
            recs = lift_score_recs(e.text)
            for k, v in recs.items():
                if fm.get("scores", {}).get(k) != v and (fm.setdefault("proposed_scores", {}).get(k) or {}).get("value") != v:
                    fm["proposed_scores"][k] = {"value": v, "since": e.date, "source": e.source_id}
                    _append_change = {"ts": datetime.now(timezone.utc).isoformat(), "ticker": ticker, "kind": "proposed_score", "key": k, "value": v, "source": e.source_id}
                    if not dry_run:
                        _append(CHANGES, [_append_change])
                    stats["changes"] += 1
        if used + len(e.text) > CHAR_CAP:
            break
        sent.append(e); used += len(e.text)
    if sent:
        text, cost, _ = claude_p.run(build_prompt(fm, sent), system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=300, precheck=_precheck)
        try:
            rows += parse_verdicts(text, sent, valid)
        except (json.JSONDecodeError, KeyError):
            text, cost, _ = claude_p.run(build_prompt(fm, sent) + "\nReturn ONLY the JSON object.", system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=300, precheck=_precheck)
            rows += parse_verdicts(text, sent, valid)
    existing = _existing_ids()
    ts = datetime.now(timezone.utc).isoformat()
    new_rows = [dict(r, ts=ts, ticker=ticker) for r in rows if f"{ticker}|{r['source_id']}|{r.get('assumption_id')}" not in existing]
    stats["rows"] = len(new_rows)
    # score mirror: operator edits to the watchlist clear matching proposals
    live = tio.watchlist_scores(ticker, watchlist)
    if live != fm.get("scores"):
        fm["scores"] = live
        for k in list(fm.get("proposed_scores", {})):
            if live.get(k) == fm["proposed_scores"][k]["value"]:
                del fm["proposed_scores"][k]
    tio.recompute_pressure(fm, _log_rows_for(ticker) + new_rows, today)
    stats["changes"] += len(fm["_changes"])
    if dry_run:
        print(json.dumps({"ticker": ticker, "new_rows": new_rows, "changes": fm["_changes"], "proposed": fm.get("proposed_scores")}, indent=1, ensure_ascii=False))
        return stats
    _append(LOG, new_rows)
    if fm["_changes"]:
        _append(CHANGES, [dict(c, ts=ts, ticker=ticker, kind="status") for c in fm["_changes"]])
    tio.save(ticker, fm)
    last_sent = max((e.date for e in sent), default=None) if sent else max(e.date for e in evidence)
    wm = json.loads(WATERMARKS.read_text()) if WATERMARKS.exists() else {}
    wm[ticker] = last_sent
    WATERMARKS.write_text(json.dumps(wm, indent=1, sort_keys=True))
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker"); ap.add_argument("--since"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-tickers", type=int, default=0)
    a = ap.parse_args(argv)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today()
    wm = json.loads(WATERMARKS.read_text()) if WATERMARKS.exists() else {}
    w = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    tickers = a.ticker.split(",") if a.ticker else [t for t in tio.universe() if not t.endswith(".pvt")]
    if a.max_tickers:
        tickers = tickers[:a.max_tickers]
    totals = {"tickers": 0, "evidence": 0, "rows": 0, "changes": 0}
    for t in tickers:
        since = date.fromisoformat(a.since) if a.since else date.fromisoformat(wm.get(t, (today - timedelta(days=DEFAULT_LOOKBACK_DAYS)).isoformat()))
        try:
            s = run_ticker(t, since, today, dry_run=a.dry_run, watchlist=w)
        except SessionLimitError as e:
            print(f"ABORT session limit at {t}: {e}"); return 2
        except RuntimeError as e:
            print(f"ABORT {t}: {e}"); return 1
        print(f"{t}: {s}")
        for k in totals:
            totals[k] += s.get(k, 0) if k != "tickers" else 1
    print("DONE", json.dumps(totals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_match_evidence.py` → `OK test_match_evidence`.

- [ ] **Step 5: Backfill test on the gold names** — `python3 scripts/thesis/match_evidence.py --ticker COHR,LITE,AAOI --since 2026-08-01 --dry-run`. Expected: Accelink EML claims → `chinese_laser_capability` challenge; COHR demand language → `datacom_ramp_continues` confirm; nothing flips to `challenged` on one source. Then run without `--dry-run`; re-run → `rows: 0` for all three (idempotent).

- [ ] **Step 6: Commit** — `git add scripts/thesis/match_evidence.py scripts/thesis/test_match_evidence.py state/thesis/ && git commit -m "thesis: daily evidence matcher (claude -p verdicts, pressure/status, score proposals, watermarks)"`

---

### Task 5: Thesis-aware earnings reviewer

**Files:**
- Modify: `plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md` (canonical; `.claude/agents/earnings-reviewer.md` is a symlink — verify with `ls -l`), Steps 3, 5, Output structure
- Modify: `scripts/cron_earnings_reviewer.py:218-235` (`run_earnings_reviewer`)
- Test: `scripts/test_cron_earnings_reviewer.py` (extend)

**Interfaces:**
- Produces: `write_context(ticker) -> Path` in `cron_earnings_reviewer.py` writing `state/thesis/context/{TICKER}.md`; note section `## 4b. Assumption read` with lines `- {id}: Confirm|Challenge|Silent — evidence (location)`.

- [ ] **Step 1: Failing test** (append to `scripts/test_cron_earnings_reviewer.py`, following its existing style):

```python
def test_write_context_without_thesis(tmp_path):
    import cron_earnings_reviewer as C
    C.CONTEXT_DIR = tmp_path
    p = C.write_context("ZZZZ")            # no _thesis.md, no metrics rows
    t = p.read_text()
    assert "No thesis file" in t and "ZZZZ" in t

def test_prompt_mentions_context():
    import cron_earnings_reviewer as C
    assert "state/thesis/context/NVDA.md" in C.build_prompt("NVDA")
```

- [ ] **Step 2: Run** — `python3 scripts/test_cron_earnings_reviewer.py` → AttributeError.

- [ ] **Step 3: Implement in `cron_earnings_reviewer.py`**

```python
CONTEXT_DIR = REPO_ROOT / "state" / "thesis" / "context"

def build_prompt(ticker: str) -> str:
    return (f"Use the earnings-reviewer agent to review {ticker}'s latest earnings call. "
            f"Before Step 4, Read state/thesis/context/{ticker}.md if it exists — it carries the open thesis "
            f"assumptions and the guidance track record for Section 4b and Section 8.")

def write_context(ticker: str) -> Path:
    """Pre-stage: the agent has no Bash/DB, so the wrapper hands it thesis + Store B facts as a file."""
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# Context for {ticker} (generated {datetime.now(timezone.utc).isoformat(timespec='seconds')})", ""]
    th = REPO_ROOT / "notes" / ticker / "_thesis.md"
    if th.exists():
        lines += ["## Open thesis assumptions (from notes/{0}/_thesis.md)".format(ticker), th.read_text(encoding="utf-8").split("---\n", 2)[1], ""]
    else:
        lines += ["## Thesis", f"No thesis file for {ticker} (not a T1/T2 name or not yet drafted). Section 4b reads 'no thesis file'.", ""]
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
        from pgconn import connect
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""SELECT metric, period, guidance_mid, consensus_at_guide, actual, consensus_at_print, beat_vs_guidance, beat_vs_guidance_pct
                           FROM metrics WHERE ticker=%s AND (actual IS NOT NULL OR guidance_mid IS NOT NULL) ORDER BY fiscal_end DESC NULLS LAST LIMIT 12""", (ticker,))
            rows = cur.fetchall()
            cur.execute("SELECT metric, score FROM metrics_credibility WHERE ticker=%s", (ticker,))
            cred = cur.fetchall()
        lines += ["## Guidance track record (Store B, last 12 rows)", "| metric | period | guide mid | cons@guide | actual | cons@print | vs guide | % |", "|---|---|---|---|---|---|---|---|"]
        lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |" for r in rows]
        lines += ["", "## Credibility scores"] + [f"- {m}: {json.dumps(s)}" for m, s in cred]
    except Exception as e:  # noqa: BLE001 — context is best-effort; the review must not fail on pg
        lines += ["## Guidance track record", f"unavailable: {type(e).__name__}: {e}"]
    p = CONTEXT_DIR / f"{ticker}.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
```
In `run_earnings_reviewer`: call `write_context(ticker)` first (wrapped in try/except that logs `CONTEXT_FAILED` and continues), and replace the literal prompt with `build_prompt(ticker)`.

- [ ] **Step 4: Agent prompt edits** (canonical file):
  - Step 3: replace the glob sentence with: *Use Glob to list `notes/{TICKER}/????????-[1-4]Q??.md` (earnings notes are named `{YYYYMMDD}-{1QYY}.md`). Sort; read the two most recent. Also Read `notes/{TICKER}/_thesis.md` if it exists and `state/thesis/context/{TICKER}.md` if it exists.*
  - Step 5: add *For each assumption in `_thesis.md` (skip `retired`), classify Confirm / Challenge / Silent with evidence and transcript location. When the context file carries a guidance track record, Section 8 must state whether this quarter's guide fits the recorded pattern (hit rate, sandbag index).*
  - Output structure: insert after §4:
    ```
    ## 4b. Assumption read

    [One line per assumption id from _thesis.md, exactly: `- {id}: Confirm|Challenge|Silent — evidence (location)`. If no thesis file: "No thesis file for {TICKER}."]
    ```
  - §10 Sourcing: add `- **Thesis context read:** {path or none}`.
  - Confirm `.claude/agents/earnings-reviewer.md` still resolves to the canonical file; if it is a copy not a symlink, copy the edited file over it.

- [ ] **Step 5: Run tests + one real dispatch** — `python3 scripts/test_cron_earnings_reviewer.py`; then replay: `cp state/transcripts/AMBA.json /tmp/AMBA.json.bak && python3 - <<'PY'\nimport json;p='state/transcripts/AMBA.json';d=json.load(open(p));d['last_iacc']='replay';json.dump(d,open(p,'w'))\nPY` and `python3 -c "import sys;sys.path.insert(0,'scripts');import cron_earnings_reviewer as C;from datetime import datetime,timezone;print(C.run_earnings_reviewer('AMBA', datetime.now(timezone.utc)))"`. Expected: STATUS new-note-written; the new note has §4b with every AMBA assumption id, §10 cites the context file, and Step 3 found the prior AMBA note without a dispatch override. Restore the state file if the replay must not count.

- [ ] **Step 6: Commit** — `git add plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md scripts/cron_earnings_reviewer.py scripts/test_cron_earnings_reviewer.py && git commit -m "earnings-reviewer: thesis-aware (4b assumption read), prior-note glob fix, Store B context pre-stage"`

---

## Tasks 6–12 (written 2026-09-09 afternoon; the morning write stopped after Task 5)

Interface facts these tasks rely on (verified 2026-09-09):
- `scripts/newsdigest/email_send.send(subject: str, body: str, to_address=TO_ADDRESS) -> int` — **plain text only**, recipient is a module constant, needs `SMTP_USER`/`SMTP_PASSWORD` from `/root/podcasts/.env`.
- `scripts/lib/claude_p.run_mcp(prompt, *, mcp_tool, system_prompt=MCP_SYSTEM_PROMPT, model=None, cwd=None, timeout=300) -> str` (raw stream-json stdout; raises `RuntimeError` / `ToolUnavailableError`). Parse with `scripts/etfflows/factset_flows._tool_result_blocks / resolve_payload / rows_of` (spill-to-file handled by `resolve_payload`; `_SPILL_RE` is importable).
- `scripts/check.py` is straight-line module code: `err(msg)` accumulates, `sys.exit(1)` at the end; no warning tier (use `print("WARN ...")`).
- Any note written under `notes/` must lead with `##`, never `#`, or the chunker indexes zero chunks (`scripts/etfflows/render.py:398`).
- InsiderScore `get_insider_transactions` args: `tickerlist`, `txntypes` (Buy/Sell/…), `tenb5` ('E' = exclude 10b5-1), `use_disclosure_date`, `begin_date`, `end_date`, `limit`. Return shape undocumented (JSON or CSV) — parser handles both.
- FactSet `FactSet_EstimatesConsensus` args: `ids` (≤3000), `estimate_type` in {guidance, surprise, …}, `metrics` (max 1), `periodicity` 'QTR', `startDate`/`endDate` (both required for PIT history), `frequency` 'AM', `relativeFiscalStart/End` (guidance), `statistic` (surprise). Existing raw rows: `requestId` = `TICKER-US` from `id_maps`.
- `ingest_metrics.build(tickers, metrics, fid_to_tk, offsets) -> (records, cred)`; records are dicts keyed by `store_b._COLS` (`ticker, period, metric, fiscal_end, guidance_date, guidance_low, guidance_mid, guidance_high, consensus_at_guide, guide_vs_consensus_pct, actual, consensus_at_print, beat_vs_consensus_pct, surprise_date, beat_vs_guidance, beat_vs_guidance_pct, source, as_of`).
- `sec_filings.fetch_ex99(cik, accession)` skips every non-HTML exhibit at the `re.search(r"\.html?$", doc)` line; `process_filing` passes `filing["items"]` (list of item codes like `"2.02"`) to `_item_slug` and `keep_8k`.
- Files in this section are written with a `# FILE: <path>` first line so they can be materialized verbatim.

### Task 6: `thesis_report.py` — weekly delta report, alerts, quarterly edition, ranking, questions

**Files:**
- Create: `scripts/thesis/thesis_report.py`, `notes/reports/` (created on first write)
- Test: `scripts/thesis/test_thesis_report.py`

**Interfaces:**
- Consumes: `thesis_io.load/universe/SCORE_KEYS`, `state/thesis/{evidence_log,changes}.jsonl` (row shapes from Task 4), `state/thesis/consensus_*.jsonl` (Task 8), `state/thesis/insiders_*.jsonl` (Task 7), `email_send.send`.
- Produces: `notes/reports/thesis-delta-{YYYYMMDD}[-quarterly].md`, `state/thesis/ranking_{date}.json` (`{date, since, kind, ranking: [{ticker, tier, delta, why, rank_score_proposed, applied, proposed, n_assumptions, status_counts}]}`), `state/thesis/reports_sent.jsonl` (`{kind, date, since, path, questions_added, ts}`), `state/thesis/alerts_sent.jsonl` (`{id, ticker, ts}`), `state/thesis/questions.jsonl` (`{id, kind: draft_review|stale|score_proposal, ticker, assumption_id?, key?, value?, text, asked_at, answered_at, answer}` — consumed by Task 11), and functions `score_num`, `ticker_delta`, `rank_movers`, `ranking_rows`, `themes_rollup`, `pending_proposals`, `drafts_needing_eye`, `stale_assumptions`, `alert_events`, `quarterly_due`, `render(ctx, wiki)`, `run_report`, `run_alerts`.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/thesis/test_thesis_report.py
"""Run directly: python3 scripts/thesis/test_thesis_report.py  (hermetic: tmp state + notes)"""
import json, shutil, sys, tempfile
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio                 # noqa: E402
from thesis import thesis_report as R               # noqa: E402

TODAY = date(2026, 9, 14)


def _fm(t, extra=None):
    fm = {"doc_type": "thesis", "ticker": t, "tier": "tier_1_bctk", "drafted": "2026-09-10", "reviewed_by_operator": False,
          "scores": {"ai_positioning": "4", "potential_investor_interest.score": "4"}, "proposed_scores": {},
          "assumptions": [{"id": "a1", "statement": "S1", "derived_from": "ai_positioning: 4", "themes": ["ai_infrastructure_capex"],
                           "challenged_by": ["x"], "confirmed_by": ["y"], "status": "open", "status_source": "draft",
                           "pressure": {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None}, "draft": True}]}
    fm.update(extra or {}); return fm


def setup(tmp):
    R.STATE_DIR = tmp / "state"; R.NOTES = tio.NOTES = tmp / "notes"; R.REPORTS_DIR = tmp / "notes" / "reports"
    R.STATE_DIR.mkdir(parents=True)
    tio.save("AAA", _fm("AAA", {"proposed_scores": {"ai_positioning": {"value": "4+", "since": "2026-09-11", "source": "notes/AAA/20260911-2Q27.md"}}}), "## Rationale\n")
    tio.save("BBB", _fm("BBB"), "## Rationale\n")
    tio.save("CCC", _fm("CCC", {"drafted": "2026-01-01"}), "## Rationale\n")
    ev = [{"ts": "2026-09-11T10:00:00+00:00", "ticker": "AAA", "source": "news", "source_id": "n1", "ref": "u1", "date": "2026-09-11", "title": "t",
           "assumption_id": "a1", "direction": "challenge", "strength": 3, "why": "w", "quote": "", "cross_ticker": False},
          {"ts": "2026-09-12T10:00:00+00:00", "ticker": "AAA", "source": "sec_filing", "source_id": "s1", "ref": "u2", "date": "2026-09-12", "title": "t",
           "assumption_id": "a1", "direction": "challenge", "strength": 2, "why": "w2", "quote": "", "cross_ticker": False},
          {"ts": "2026-09-12T10:00:00+00:00", "ticker": "BBB", "source": "news", "source_id": "n2", "ref": "u3", "date": "2026-09-12", "title": "t",
           "assumption_id": None, "direction": "neutral", "strength": 0, "why": "", "quote": "", "cross_ticker": False}]
    chg = [{"ts": "2026-09-12T10:00:01+00:00", "ticker": "AAA", "kind": "status", "assumption_id": "a1", "from": "open", "to": "challenged", "evidence_ids": ["n1", "s1"]},
           {"ts": "2026-09-11T10:00:01+00:00", "ticker": "AAA", "kind": "proposed_score", "key": "ai_positioning", "value": "4+", "source": "notes/AAA/20260911-2Q27.md"}]
    (R.STATE_DIR / "evidence_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in ev))
    (R.STATE_DIR / "changes.jsonl").write_text("".join(json.dumps(r) + "\n" for r in chg))
    R.send = lambda subject, body: 200
    R.storeb_context = lambda t: ["Store B stubbed"]
    R.coverage = lambda theses, ev, since, until: {"evidence_by_source": {"news": 2}, "matched": 2, "no_thesis": [], "reviewer": {}, "storeb_as_of": "stub"}


def test_score_num():
    assert R.score_num("4+") == 4.25 and R.score_num("4-") == 3.75 and R.score_num("4") == 4.0 and R.score_num("x") is None


def test_movers_ranking_is_deterministic_and_signed():
    ctx = R.build_context("weekly", TODAY, "2026-09-08", "2026-09-14")
    m = ctx["movers"]
    assert m[0]["ticker"] == "AAA" and m[0]["delta"] == -3 + 2 - 5   # status -3, score up +2, pressure -5 (capped)
    assert "a1 open→challenged" in m[0]["why"]
    assert [x["ticker"] for x in ctx["all"]] == [x["ticker"] for x in R.rank_movers(ctx["theses"], ctx["evidence"], R._read_jsonl(R.STATE_DIR / "changes.jsonl"), "2026-09-08", "2026-09-14")]
    assert ctx["quiet"] == ["CCC"] and "BBB" in [x["ticker"] for x in m]   # BBB had evidence (neutral) → listed, not quiet
    assert ctx["ranking"][0]["rank_score_proposed"] == 4.125             # (4.25 + 4) / 2 for AAA


def test_render_leads_with_h2_and_wikilinks():
    ctx = R.build_context("weekly", TODAY, "2026-09-08", "2026-09-14")
    md, txt = R.render(ctx, wiki=True), R.render(ctx, wiki=False)
    assert md.startswith("## Thesis delta") and "[[AAA]]" in md and "[[AAA/_thesis]]" in md
    assert "[[" not in txt and "notes/AAA/_thesis.md" in txt
    assert "## 4. Pending score proposals" in txt and "apply_scores.py --accept AAA" in txt
    assert "## 5. Drafts needing your eye" in txt and "AAA a1" in txt      # draft:true + first hit this period
    assert "CCC a1" in txt and "d)" in txt                                   # stale (drafted 2026-01-01, no evidence)
    assert "## 3. Themes" in txt and "ai_infrastructure_capex" in txt


def test_weekly_writes_note_ranking_questions_ledger():
    R.run_report("weekly", TODAY, None, dry_run=False)
    assert (R.REPORTS_DIR / "thesis-delta-20260914.md").exists()
    rk = json.loads((R.STATE_DIR / "ranking_2026-09-14.json").read_text())
    assert rk["ranking"][0]["ticker"] == "AAA"
    qs = R._read_jsonl(R.STATE_DIR / "questions.jsonl")
    assert {q["id"] for q in qs} >= {"draft:AAA:a1", "score:AAA:ai_positioning", "stale:CCC:a1"}
    sent = R._read_jsonl(R.STATE_DIR / "reports_sent.jsonl")
    assert sent[-1]["kind"] == "weekly" and sent[-1]["date"] == "2026-09-14"
    R.run_report("weekly", TODAY, None, dry_run=False)                       # idempotent questions
    assert len(R._read_jsonl(R.STATE_DIR / "questions.jsonl")) == len(qs)


def test_alerts_fire_once():
    calls = []
    R.send = lambda s, b: calls.append((s, b)) or 200
    ev = R.alert_events("2026-09-01T00:00:00+00:00", TODAY)
    ids = {e["id"] for e in ev}
    assert any(i.startswith("status:AAA:a1:challenged") for i in ids) and any(i.startswith("score:AAA:ai_positioning") for i in ids) and any(i.startswith("chal3:AAA:n1") for i in ids)
    R.ALERT_LOOKBACK_DAYS = 10_000                                           # fixture rows are older than 3 days
    assert R.run_alerts(TODAY, dry_run=False) == 0 and len(calls) == 1 and "Thesis alert" in calls[0][0]
    assert R.run_alerts(TODAY, dry_run=False) == 0 and len(calls) == 1     # ledger blocks the repeat


def test_quarterly_due_rule(tmp):
    theses = R.load_theses()
    R.quarterly_t1 = lambda: ["AAA", "BBB", "CCC"]
    for t, d in (("AAA", "20260801"), ("BBB", "20260805")):
        (R.NOTES / t / f"{d}-2Q27.md").write_text("## 1.\n")
    assert R.quarterly_due(date(2026, 8, 25), theses) is True               # 2/3 reported, newest 20d old, none sent
    assert R.quarterly_due(date(2026, 8, 10), theses) is False              # newest only 5d old
    R._append(R.STATE_DIR / "reports_sent.jsonl", [{"kind": "quarterly", "date": "2026-08-20"}])
    assert R.quarterly_due(date(2026, 8, 25), theses) is False              # sent 5d ago


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        setup(tmp)
        test_score_num(); test_movers_ranking_is_deterministic_and_signed(); test_render_leads_with_h2_and_wikilinks()
        test_weekly_writes_note_ranking_questions_ledger(); test_alerts_fire_once(); test_quarterly_due_rule(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_thesis_report")
```

- [ ] **Step 2: Run to verify it fails** — `python3 scripts/thesis/test_thesis_report.py` → `ImportError: cannot import name 'thesis_report'`.

- [ ] **Step 3: Implement**

```python
# FILE: scripts/thesis/thesis_report.py
#!/usr/bin/env python3
"""Thesis-delta report: weekly email + vault note, thin daily alerts, quarterly edition, ranking json.

    python3 scripts/thesis/thesis_report.py --weekly [--auto-quarterly] [--since 2026-09-01] [--dry-run]
    python3 scripts/thesis/thesis_report.py --alerts [--dry-run]
    python3 scripts/thesis/thesis_report.py --quarterly [--dry-run]

Deterministic — no LLM call. Inputs: notes/*/_thesis.md, state/thesis/{evidence_log,changes}.jsonl,
Store B (pg metrics; best-effort), state/thesis/consensus_*.jsonl (Store B weekly snapshots),
state/thesis/insiders_*.jsonl, state/etf_lookthrough.json + state/etf_flows.jsonl, notes/news
macro_signals. Outputs: notes/reports/thesis-delta-{YYYYMMDD}[-quarterly].md (leads with '##' so the
chunker indexes it; wikilinks for Obsidian), state/thesis/ranking_{date}.json, reports_sent.jsonl,
alerts_sent.jsonl (an event is announced once), questions.jsonl (for the thesis-chat skill), and a
plain-text Brevo email. Ranking uses machine-proposed scores, labelled, beside applied scores
(operator decision 2026-09-09).
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from thesis import STATE_DIR as _STATE_DIR, thesis_io as tio   # noqa: E402

STATE_DIR = _STATE_DIR
NOTES = REPO / "notes"
REPORTS_DIR = REPO / "notes" / "reports"
W_STATUS, W_SCORE, PRESSURE_CAP = 3.0, 2.0, 5.0
STALE_DAYS = 180
ALERT_LOOKBACK_DAYS = 3
MOVERS_LISTED, MOVERS_DETAILED = 25, 15
QUARTERLY_T1_SHARE, QUARTERLY_SETTLE_DAYS, QUARTERLY_MIN_GAP_DAYS = 0.6, 14, 60


def send(subject: str, body: str) -> int:          # indirection so tests stub delivery
    from newsdigest.email_send import send as _send
    return _send(subject, body)


def _read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _append(p: Path, rows: list[dict]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def load_theses() -> dict[str, dict]:
    out = {}
    for p in sorted(NOTES.glob("*/_thesis.md")):
        fm = tio.load(p.parent.name)
        if fm:
            out[p.parent.name] = fm
    return out


def score_num(v) -> float | None:
    m = re.match(r"^\s*([1-5])\s*([+-])?\s*$", str(v)) if v is not None else None
    if not m:
        return None
    return float(m.group(1)) + (0.25 if m.group(2) == "+" else -0.25 if m.group(2) == "-" else 0.0)


def in_period(d, since: str, until: str) -> bool:
    return bool(d) and since <= str(d)[:10] <= until


# ───────────────────────────── §1 movers / ranking ─────────────────────────────
def ticker_delta(ticker: str, fm: dict, ev_rows: list[dict], chg_rows: list[dict]) -> dict:
    """Thesis delta for one name over period rows: status ±3, score proposal ±2 per axis, net pressure ±1/strength capped ±5."""
    status = [c for c in chg_rows if c.get("kind") == "status"]
    scores = [c for c in chg_rows if c.get("kind") == "proposed_score"]
    applied = fm.get("scores") or {}
    d = 0.0
    for c in status:
        d += W_STATUS if c["to"] == "confirmed" else -W_STATUS if c["to"] == "challenged" else 0.0
    for c in scores:
        cur, new = score_num(applied.get(c["key"])), score_num(c["value"])
        if cur is not None and new is not None:
            d += W_SCORE if new > cur else -W_SCORE if new < cur else 0.0
    conf = sum(r.get("strength", 0) for r in ev_rows if r.get("direction") == "confirm")
    chal = sum(r.get("strength", 0) for r in ev_rows if r.get("direction") == "challenge")
    d += max(-PRESSURE_CAP, min(PRESSURE_CAP, float(conf - chal)))
    why = [f"{c['assumption_id']} {c['from']}→{c['to']}" for c in status]
    why += [f"{c['key'].split('.')[-1]} proposed {c['value']} (applied {applied.get(c['key'])})" for c in scores]
    if conf or chal:
        why.append(f"pressure +{conf}/−{chal}")
    return {"ticker": ticker, "delta": round(d, 2), "status_changes": status, "score_moves": scores,
            "pressure": {"confirm": conf, "challenge": chal},
            "evidence_by_source": dict(Counter(r["source"] for r in ev_rows)), "why": "; ".join(why) or "quiet"}


def rank_movers(theses: dict, ev_rows: list[dict], chg_rows: list[dict], since: str, until: str) -> list[dict]:
    ev_by, chg_by = defaultdict(list), defaultdict(list)
    for r in ev_rows:
        if in_period(r.get("date"), since, until):
            ev_by[r["ticker"]].append(r)
    for c in chg_rows:
        if in_period(c.get("ts"), since, until):
            chg_by[c["ticker"]].append(c)
    rows = [ticker_delta(t, fm, ev_by.get(t, []), chg_by.get(t, [])) for t, fm in theses.items()]
    return sorted(rows, key=lambda r: (-abs(r["delta"]), -r["delta"], r["ticker"]))


def ranking_rows(theses: dict, movers: list[dict]) -> list[dict]:
    """Ranking view: machine-proposed scores (labelled) beside applied ones."""
    by = {m["ticker"]: m for m in movers}
    out = []
    for t, fm in theses.items():
        applied = fm.get("scores") or {}
        proposed = {k: v.get("value") for k, v in (fm.get("proposed_scores") or {}).items()}
        nums = [score_num(proposed.get(k, applied.get(k))) for k in tio.SCORE_KEYS]
        nums = [n for n in nums if n is not None]
        out.append({"ticker": t, "tier": fm.get("tier"), "delta": by[t]["delta"], "why": by[t]["why"],
                    "rank_score_proposed": round(sum(nums) / len(nums), 3) if nums else None,
                    "applied": applied, "proposed": proposed, "n_assumptions": len(fm.get("assumptions") or []),
                    "status_counts": dict(Counter(a.get("status") for a in fm.get("assumptions") or []))})
    return sorted(out, key=lambda r: (-abs(r["delta"]), -r["delta"], r["ticker"]))


# ───────────────────────────── §3–§7 rollups ─────────────────────────────
def themes_rollup(theses: dict, ev_rows: list[dict], since: str, until: str) -> list[dict]:
    idx = {(t, a["id"]): a.get("themes") or [] for t, fm in theses.items() for a in fm.get("assumptions") or []}
    agg: dict[str, dict] = defaultdict(lambda: {"confirm": 0, "challenge": 0, "tickers": Counter()})
    for r in ev_rows:
        if not (in_period(r.get("date"), since, until) and r.get("assumption_id") and r.get("direction") in ("confirm", "challenge")):
            continue
        for th in idx.get((r["ticker"], r["assumption_id"]), []):
            agg[th][r["direction"]] += 1
            agg[th]["tickers"][r["ticker"]] += 1
    out = [{"theme": th, "confirm": v["confirm"], "challenge": v["challenge"], "top": [t for t, _ in v["tickers"].most_common(3)]}
           for th, v in agg.items() if v["confirm"] + v["challenge"] >= 2]
    return sorted(out, key=lambda x: (-(x["confirm"] + x["challenge"]), x["theme"]))


def pending_proposals(theses: dict) -> list[dict]:
    out = []
    for t, fm in theses.items():
        for k, v in (fm.get("proposed_scores") or {}).items():
            out.append({"ticker": t, "key": k, "value": v.get("value"), "applied": (fm.get("scores") or {}).get(k),
                        "since": v.get("since"), "source": v.get("source")})
    return sorted(out, key=lambda r: (r["ticker"], r["key"]))


def drafts_needing_eye(theses: dict, ev_rows: list[dict], since: str, until: str) -> list[dict]:
    """Assumptions still draft:true whose FIRST matched evidence landed in this period (review where it matters)."""
    first: dict[tuple, dict] = {}
    for r in sorted(ev_rows, key=lambda r: str(r.get("date"))):
        if r.get("assumption_id"):
            first.setdefault((r["ticker"], r["assumption_id"]), r)
    out = []
    for t, fm in theses.items():
        for a in fm.get("assumptions") or []:
            r = first.get((t, a["id"]))
            if a.get("draft") and r and in_period(r["date"], since, until):
                out.append({"ticker": t, "assumption_id": a["id"], "statement": a.get("statement", ""), "thin": bool(fm.get("thin_inputs")),
                            "first_hit": f"{r['source']} {r['date']} {r['direction']}/{r['strength']}: {(r.get('why') or '')[:120]}"})
    return sorted(out, key=lambda x: (not x["thin"], x["ticker"], x["assumption_id"]))


def stale_assumptions(theses: dict, today: date, days: int = STALE_DAYS) -> list[dict]:
    out = []
    for t, fm in theses.items():
        for a in fm.get("assumptions") or []:
            if a.get("status") == "retired":
                continue
            anchor = (a.get("pressure") or {}).get("last_evidence") or fm.get("drafted")
            try:
                age = (today - date.fromisoformat(str(anchor)[:10])).days
            except (TypeError, ValueError):
                continue
            if age >= days:
                out.append({"ticker": t, "assumption_id": a["id"], "days": age})
    return sorted(out, key=lambda x: (-x["days"], x["ticker"], x["assumption_id"]))


def storeb_context(ticker: str) -> list[str]:
    """Latest guidance vs consensus per metric (pg, best-effort) + drift between the last two consensus snapshots."""
    lines = []
    try:
        sys.path.insert(0, str(REPO / "scripts" / "chunking"))
        from pgconn import connect
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""SELECT DISTINCT ON (metric) metric, period, guidance_mid, consensus_at_guide, actual, beat_vs_guidance_pct, as_of
                           FROM metrics WHERE ticker=%s AND guidance_mid IS NOT NULL ORDER BY metric, fiscal_end DESC NULLS LAST""", (ticker,))
            for m, per, gm, cg, act, bvg, asof in cur.fetchall():
                tail = f", actual {act} ({bvg:+.1f}% vs guide)" if act is not None and bvg is not None else ""
                lines.append(f"{m} {per}: guide {gm} vs cons@guide {cg}{tail} [as_of {asof}]")
            cur.execute("SELECT metric, score FROM metrics_credibility WHERE ticker=%s ORDER BY metric", (ticker,))
            for m, sc in cur.fetchall():
                lines.append(f"credibility {m}: {json.dumps(sc, default=str)[:160]}")
    except Exception as e:  # noqa: BLE001 — the report must render without pg
        lines.append(f"Store B unavailable: {type(e).__name__}")
    snaps = sorted(STATE_DIR.glob("consensus_*.jsonl"))[-2:]
    if len(snaps) == 2:
        def _cons(r):
            return r.get("consensus_at_print") if r.get("consensus_at_print") is not None else r.get("consensus_at_guide")
        cur_ = {r["metric"]: r for r in _read_jsonl(snaps[1]) if r.get("ticker") == ticker}
        prev = {r["metric"]: r for r in _read_jsonl(snaps[0]) if r.get("ticker") == ticker}
        for m, r in sorted(cur_.items()):
            p = prev.get(m)
            if p and r.get("period") == p.get("period") and _cons(r) is not None and _cons(p) not in (None, 0):
                lines.append(f"consensus drift {m} {r['period']}: {(_cons(r) - _cons(p)) / abs(_cons(p)) * 100:+.1f}% since {snaps[0].stem.split('_')[-1]}")
    return lines


def flows_line(ticker: str) -> str | None:
    try:
        holdings = json.loads((REPO / "state" / "etf_lookthrough.json").read_text()).get("holdings") or []
    except (OSError, json.JSONDecodeError):
        return None
    w = None
    for h in holdings:
        if h.get("requestId") == "BCTK" and re.sub(r"-[A-Z]{2}$", "", str(h.get("securityTicker") or "")) == ticker:
            w = h.get("weightClose") if h.get("weightClose") is not None else h.get("weight")
    if w is None:
        return None
    rows = sorted((r for r in _read_jsonl(REPO / "state" / "etf_flows.jsonl") if r.get("ticker") == "BCTK" and r.get("series") == "flows"), key=lambda r: r["date"])[-5:]
    net = sum(r.get("value") or 0 for r in rows)
    return f"BCTK weight {float(w):.1f}%; BCTK 5d net flow {net / 1e6:+.0f}M"


def insiders_line(ticker: str) -> str | None:
    files = sorted(STATE_DIR.glob("insiders_*.jsonl"))
    rows = [r for r in _read_jsonl(files[-1]) if r.get("ticker") == ticker] if files else []
    if not rows:
        return None
    buys = {r.get("insider") for r in rows if r.get("txn_type") == "Buy"}
    sells = {r.get("insider") for r in rows if r.get("txn_type") == "Sell"}
    bv = sum(r.get("value") or 0 for r in rows if r.get("txn_type") == "Buy")
    sv = sum(r.get("value") or 0 for r in rows if r.get("txn_type") == "Sell")
    return (f"insiders open-market ex-10b5-1 (week to {files[-1].stem.split('_')[-1]}): "
            f"{len(buys)} buyer(s) ${bv / 1e6:.1f}M / {len(sells)} seller(s) ${sv / 1e6:.1f}M")


def macro_lines(since: str, until: str, top: int = 6) -> list[str]:
    c: Counter = Counter()
    for p in NOTES.glob("news/*.md"):
        if not (since <= p.name[:10] <= until):
            continue
        m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8", errors="replace"), re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        for s in fm.get("macro_signals") or []:
            c[str(s)] += 1
    return [f"{s}: {n} stories" for s, n in c.most_common(top)]


def coverage(theses: dict, ev_rows: list[dict], since: str, until: str) -> dict:
    period = [r for r in ev_rows if in_period(r.get("date"), since, until)]
    universe = [t for t in tio.universe() if not t.endswith(".pvt")]
    rev: Counter = Counter()
    log = REPO / "logs" / "cron-earnings-reviewer.log"
    if log.exists():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"(\d{4}-\d{2}-\d{2})", line[:40])
            s = re.search(r"STATUS:\s*([\w-]+)", line)
            if m and s and since <= m.group(1) <= until:
                rev[s.group(1)] += 1
    asof = None
    try:
        sys.path.insert(0, str(REPO / "scripts" / "chunking"))
        from pgconn import connect
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT max(as_of) FROM metrics")
            asof = cur.fetchone()[0]
    except Exception:  # noqa: BLE001
        pass
    return {"evidence_by_source": dict(Counter(r["source"] for r in period)), "matched": sum(1 for r in period if r.get("assumption_id")),
            "no_thesis": [t for t in universe if t not in theses], "reviewer": dict(rev), "storeb_as_of": str(asof) if asof else "unknown"}


# ───────────────────────────── periods / quarterly rule ─────────────────────────────
def last_sent(kind: str) -> str | None:
    rows = [r for r in _read_jsonl(STATE_DIR / "reports_sent.jsonl") if r.get("kind") == kind]
    return rows[-1]["date"] if rows else None


def period_for(kind: str, today: date, since_arg: str | None) -> tuple[str, str]:
    if since_arg:
        return since_arg, today.isoformat()
    return (last_sent(kind) or (today - timedelta(days={"weekly": 7, "quarterly": 91}[kind])).isoformat()), today.isoformat()


def quarterly_t1() -> list[str]:
    w = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    return [e["ticker"] for e in w.get("tier_1_bctk") or [] if isinstance(e, dict) and e.get("ticker") and not str(e["ticker"]).endswith(".pvt")]


def quarterly_due(today: date, theses: dict) -> bool:
    """~2 weeks after the bulk of T1 reported: >=60% of T1 have an earnings note in the last 60 days, the newest is
    >=14 days old, and no quarterly edition went out in the last 60 days. Calendar-free and deterministic."""
    t1 = quarterly_t1()
    dates = []
    for t in t1:
        ns = sorted(NOTES.glob(f"{t}/[0-9]*-[1-4]Q[0-9][0-9].md"))
        if ns:
            d = ns[-1].name[:8]
            dates.append(date(int(d[:4]), int(d[4:6]), int(d[6:8])))
    recent = [d for d in dates if 0 <= (today - d).days <= 60]
    if not t1 or len(recent) / len(t1) < QUARTERLY_T1_SHARE or (today - max(recent)).days < QUARTERLY_SETTLE_DAYS:
        return False
    prev = last_sent("quarterly")
    return not prev or (today - date.fromisoformat(prev)).days >= QUARTERLY_MIN_GAP_DAYS


# ───────────────────────────── build + render ─────────────────────────────
def build_context(kind: str, today: date, since: str, until: str) -> dict:
    theses = load_theses()
    ev = _read_jsonl(STATE_DIR / "evidence_log.jsonl")
    chg = _read_jsonl(STATE_DIR / "changes.jsonl")
    movers = rank_movers(theses, ev, chg, since, until)
    return {"kind": kind, "date": today.isoformat(), "since": since, "until": until, "theses": theses, "evidence": ev, "all": movers,
            "movers": [m for m in movers if m["delta"] != 0 or m["evidence_by_source"]],
            "quiet": [m["ticker"] for m in movers if m["delta"] == 0 and not m["evidence_by_source"]],
            "ranking": ranking_rows(theses, movers), "themes": themes_rollup(theses, ev, since, until),
            "proposals": pending_proposals(theses), "drafts": drafts_needing_eye(theses, ev, since, until),
            "stale": stale_assumptions(theses, today), "coverage": coverage(theses, ev, since, until), "macro": macro_lines(since, until)}


def detail_for(ctx: dict, m: dict, max_cites: int = 2) -> list[str]:
    t = m["ticker"]
    fm = ctx["theses"][t]
    amap = {a["id"]: a for a in fm.get("assumptions") or []}
    rows = [r for r in ctx["evidence"] if r.get("ticker") == t and r.get("assumption_id") and in_period(r.get("date"), ctx["since"], ctx["until"])]
    lines = []
    changed = sorted({c["assumption_id"] for c in m["status_changes"]})
    for aid in changed:
        a = amap.get(aid)
        if not a:
            continue
        lines.append(f"- {aid} → {a.get('status')}: {a.get('statement', '')[:200]}")
        for r in sorted((r for r in rows if r["assumption_id"] == aid), key=lambda r: (-r["strength"], r["date"]))[:max_cites]:
            lines.append(f"    · {r['date']} {r['source']} ({r['direction']}/{r['strength']}): {(r.get('why') or '')[:140]} [{(r.get('ref') or '')[:80]}]")
    if not changed:
        for r in sorted(rows, key=lambda r: (-r["strength"], r["date"]))[:max_cites]:
            lines.append(f"- {r['assumption_id']} {r['direction']}/{r['strength']} {r['date']} {r['source']}: {(r.get('why') or '')[:140]} [{(r.get('ref') or '')[:80]}]")
    applied, prop = fm.get("scores") or {}, fm.get("proposed_scores") or {}
    if prop:
        lines.append("- scores, proposed vs applied: " + ", ".join(f"{k.split('.')[-1]} {v.get('value')} vs {applied.get(k)}" for k, v in sorted(prop.items())))
    lines += [f"- {l}" for l in storeb_context(t)]
    for fn in (flows_line, insiders_line):
        l = fn(t)
        if l:
            lines.append(f"- {l}")
    return lines


def render(ctx: dict, wiki: bool = False) -> str:
    L = (lambda t: f"[[{t}]]") if wiki else (lambda t: t)
    TH = (lambda t: f"[[{t}/_thesis]]") if wiki else (lambda t: f"notes/{t}/_thesis.md")
    title = "State of theses" if ctx["kind"] == "quarterly" else "Thesis delta"
    out = [f"## {title} — {ctx['date']} (period {ctx['since']} → {ctx['until']})", ""]
    out += ["## 1. Movers (ranked by thesis delta; scores are machine-proposed unless marked applied)", ""]
    if not ctx["movers"]:
        out.append("Quiet period: no status changes, score proposals, or matched evidence.")
    for m in ctx["movers"][:MOVERS_LISTED]:
        arrow = "▲" if m["delta"] > 0 else "▼" if m["delta"] < 0 else "•"
        src = ", ".join(f"{k} {v}" for k, v in sorted(m["evidence_by_source"].items()))
        out.append(f"- {arrow} {L(m['ticker'])} {m['delta']:+.1f} — {m['why']}" + (f" [{src}]" if src else ""))
    out += ["", "## 2. Per-name detail", ""]
    names = ctx["all"] if ctx["kind"] == "quarterly" else ctx["movers"][:MOVERS_DETAILED]
    for m in names:
        out.append(f"### {L(m['ticker'])} ({m['delta']:+.1f}) — {TH(m['ticker'])}")
        out += detail_for(ctx, m) or ["- no matched evidence this period"]
        out.append("")
    out += ["## 3. Themes (≥2 matched items this period)", ""]
    out += [f"- {t['theme']}: confirm {t['confirm']} / challenge {t['challenge']} — {', '.join(L(x) for x in t['top'])}" for t in ctx["themes"]] or ["none"]
    out += ["", "## 4. Pending score proposals (watchlist.yaml is operator-edited only)", ""]
    out += [f"- {L(p['ticker'])} {p['key']}: proposed {p['value']} vs applied {p['applied']} (since {p['since']}; {p['source']})" for p in ctx["proposals"]] or ["none"]
    if ctx["proposals"]:
        out.append("Apply: python3 scripts/thesis/apply_scores.py --accept " + ",".join(sorted({p["ticker"] for p in ctx["proposals"]})) + " [--key K] [--write]")
    out += ["", "## 5. Drafts needing your eye (first evidence hit this period)", ""]
    out += [f"- {L(d['ticker'])} {d['assumption_id']}{' (thin inputs)' if d['thin'] else ''}: {d['statement'][:160]} — first hit: {d['first_hit']}" for d in ctx["drafts"]] or ["none"]
    if ctx["stale"]:
        out += ["", f"Stale (no evidence for ≥{STALE_DAYS}d; retire or keep?):"] + [f"- {L(s['ticker'])} {s['assumption_id']} ({s['days']}d)" for s in ctx["stale"][:20]]
    out += ["", "## 6. Quiet names", "", ", ".join(L(t) for t in ctx["quiet"]) or "none"]
    c = ctx["coverage"]
    out += ["", "## 7. Coverage & health", "",
            "- evidence by source: " + (", ".join(f"{k} {v}" for k, v in sorted(c["evidence_by_source"].items())) or "none") + f"; matched to an assumption: {c['matched']}",
            "- macro: " + ("; ".join(ctx["macro"]) or "none"),
            f"- tickers without _thesis.md: {', '.join(c['no_thesis']) or 'none'}",
            "- earnings reviewer outcomes: " + (", ".join(f"{k} {v}" for k, v in sorted(c["reviewer"].items())) or "none logged"),
            f"- Store B as_of: {c['storeb_as_of']}"]
    return "\n".join(out) + "\n"


def update_questions(ctx: dict) -> int:
    p = STATE_DIR / "questions.jsonl"
    existing = {r["id"] for r in _read_jsonl(p)}
    ts = datetime.now(timezone.utc).isoformat()
    new = []
    for d in ctx["drafts"]:
        new.append({"id": f"draft:{d['ticker']}:{d['assumption_id']}", "kind": "draft_review", "ticker": d["ticker"], "assumption_id": d["assumption_id"],
                    "text": f"Draft assumption '{d['assumption_id']}' got its first evidence ({d['first_hit'][:100]}). Keep, edit, or retire?"})
    for s in ctx["stale"]:
        new.append({"id": f"stale:{s['ticker']}:{s['assumption_id']}", "kind": "stale", "ticker": s["ticker"], "assumption_id": s["assumption_id"],
                    "text": f"'{s['assumption_id']}' has had no evidence for {s['days']} days. Retire or keep?"})
    for pr in ctx["proposals"]:
        new.append({"id": f"score:{pr['ticker']}:{pr['key']}", "kind": "score_proposal", "ticker": pr["ticker"], "key": pr["key"], "value": pr["value"],
                    "text": f"Accept proposed {pr['key']} = {pr['value']} (applied {pr['applied']}; source {pr['source']})?"})
    rows = [dict(r, asked_at=ts, answered_at=None, answer=None) for r in new if r["id"] not in existing]
    _append(p, rows)
    return len(rows)


def run_report(kind: str, today: date, since_arg: str | None, dry_run: bool) -> int:
    since, until = period_for(kind, today, since_arg)
    ctx = build_context(kind, today, since, until)
    text, md = render(ctx, wiki=False), render(ctx, wiki=True)
    subject = f"{'State of theses' if kind == 'quarterly' else 'Thesis delta'} — {today.isoformat()}"
    if dry_run:
        print(subject); print(text)
        return 0
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    note = REPORTS_DIR / f"thesis-delta-{today.strftime('%Y%m%d')}{'-quarterly' if kind == 'quarterly' else ''}.md"
    note.write_text(md, encoding="utf-8")
    (STATE_DIR / f"ranking_{today.isoformat()}.json").write_text(json.dumps({"date": today.isoformat(), "since": since, "kind": kind, "ranking": ctx["ranking"]}, indent=1, default=str))
    nq = update_questions(ctx)
    send(subject, text)
    ts = datetime.now(timezone.utc).isoformat()
    rows = [{"kind": k, "date": today.isoformat(), "since": since, "path": note.relative_to(REPO).as_posix(), "questions_added": nq, "ts": ts}
            for k in ([kind] + (["weekly"] if kind == "quarterly" else []))]
    _append(STATE_DIR / "reports_sent.jsonl", rows)
    print(f"sent '{subject}'; note {note.relative_to(REPO)}; movers {len(ctx['movers'])}; +{nq} questions")
    return 0


# ───────────────────────────── alerts ─────────────────────────────
def alert_events(since_ts: str, today: date) -> list[dict]:
    ev = []
    for c in _read_jsonl(STATE_DIR / "changes.jsonl"):
        if c.get("ts", "") <= since_ts:
            continue
        if c.get("kind") == "status":
            ev.append({"id": f"status:{c['ticker']}:{c['assumption_id']}:{c['to']}:{c['ts'][:10]}", "ticker": c["ticker"],
                       "text": f"{c['assumption_id']} {c['from']}→{c['to']} ({len(c.get('evidence_ids') or [])} evidence ids)"})
        elif c.get("kind") == "proposed_score":
            ev.append({"id": f"score:{c['ticker']}:{c['key']}:{c['value']}", "ticker": c["ticker"], "text": f"score proposal {c['key']} → {c['value']} ({c.get('source')})"})
    for r in _read_jsonl(STATE_DIR / "evidence_log.jsonl"):
        if r.get("ts", "") > since_ts and r.get("direction") == "challenge" and r.get("strength") == 3 and r.get("assumption_id"):
            ev.append({"id": f"chal3:{r['ticker']}:{r['source_id']}:{r['assumption_id']}", "ticker": r["ticker"],
                       "text": f"strength-3 challenge to {r['assumption_id']} from {r['source']} {r['date']}: {(r.get('why') or '')[:120]} [{(r.get('ref') or '')[:80]}]"})
    cutoff = datetime.fromisoformat(since_ts).timestamp()
    for p in NOTES.glob("*/[0-9]*-[1-4]Q[0-9][0-9].md"):
        if p.stat().st_mtime > cutoff:
            ev.append({"id": f"note:{p.parent.name}:{p.name}", "ticker": p.parent.name, "text": f"earnings note landed: {p.relative_to(REPO).as_posix()}"})
    return sorted(ev, key=lambda e: (e["ticker"], e["id"]))


def run_alerts(today: date, dry_run: bool) -> int:
    ledger = STATE_DIR / "alerts_sent.jsonl"
    sent = {r["id"] for r in _read_jsonl(ledger)}
    since_ts = (datetime.now(timezone.utc) - timedelta(days=ALERT_LOOKBACK_DAYS)).isoformat()
    events = [e for e in alert_events(since_ts, today) if e["id"] not in sent]
    if not events:
        print("no new thesis events")
        return 0
    body = "\n".join(f"- {e['ticker']}: {e['text']} — notes/{e['ticker']}/_thesis.md" for e in events) + "\n"
    subject = f"Thesis alert — {today.isoformat()} ({len(events)} event{'s' if len(events) != 1 else ''})"
    if dry_run:
        print(subject); print(body)
        return 0
    send(subject, body)
    ts = datetime.now(timezone.utc).isoformat()
    _append(ledger, [{"id": e["id"], "ticker": e["ticker"], "ts": ts} for e in events])
    print(f"sent {len(events)} alert line(s)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--weekly", action="store_true"); g.add_argument("--alerts", action="store_true"); g.add_argument("--quarterly", action="store_true")
    ap.add_argument("--auto-quarterly", action="store_true", help="with --weekly: send the quarterly edition instead when due")
    ap.add_argument("--since"); ap.add_argument("--today"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if a.alerts:
        return run_alerts(today, a.dry_run)
    kind = "quarterly" if a.quarterly or (a.auto_quarterly and quarterly_due(today, load_theses())) else "weekly"
    return run_report(kind, today, a.since, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_thesis_report.py` → `OK test_thesis_report`.
- [ ] **Step 5: Real dry-run** — `python3 scripts/thesis/thesis_report.py --weekly --since 2026-08-01 --dry-run` on the backfilled COHR/LITE/AAOI log: COHR/LITE in §1, §2 shows citations with dates/sources, §7 counts by source; run twice, `diff` of the two outputs is empty. Then `--alerts --dry-run` lists the backfill's status changes.
- [ ] **Step 6: Commit** — `git add scripts/thesis/thesis_report.py scripts/thesis/test_thesis_report.py && git commit -m "thesis: weekly delta report + alerts + quarterly edition + ranking json + questions ledger"`


---

### Task 7: `insider_pull.py` — weekly InsiderScore counterweight

**Files:**
- Create: `scripts/thesis/insider_pull.py`
- Test: `scripts/thesis/test_insider_pull.py`

**Interfaces:**
- Consumes: `claude_p.run_mcp`, `factset_flows._tool_result_blocks/resolve_payload/rows_of/_SPILL_RE`, `thesis_io.load/save/recompute_pressure/universe`, `match_evidence.LOG/CHANGES/_append/_read_log`.
- Produces: `state/thesis/insiders_{YYYY-MM-DD}.jsonl` rows `{ticker, insider, position, txn_type: Buy|Sell, shares, value, date, notable, _raw}` (read by `thesis_report.insiders_line`); evidence rows with `source: "insider"`, `source_id: "insider:{T}:{week_end}"`, strength 1 on investor-interest assumptions when ≥2 distinct insiders trade the same direction; functions `prompt`, `parse_rows`, `normalize`, `clusters`, `investor_assumptions`, `evidence_rows`.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/thesis/test_insider_pull.py
"""Run directly: python3 scripts/thesis/test_insider_pull.py  (no network)"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import insider_pull as I  # noqa: E402


def _transcript(payload: str) -> str:
    return "\n".join([json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": I.TOOL, "input": {}}]}}),
                      json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": payload}]}})])


def test_prompt_excludes_10b5_1():
    p = I.prompt(["COHR", "LITE"], "2026-09-01", "2026-09-08")
    assert "tenb5: 'E'" in p and '"COHR"' in p and "use_disclosure_date: true" in p and "EXACTLY ONCE" in p


def test_parse_rows_json_and_csv():
    rows = [{"ticker": "COHR", "insider": "A", "txntype": "Buy", "shares": 100, "value": 5000, "date": "2026-09-02"}]
    assert I.parse_rows(_transcript(json.dumps({"data": rows})))[0]["ticker"] == "COHR"
    assert I.parse_rows(_transcript(json.dumps(rows)))[0]["insider"] == "A"
    csv_text = "ticker,insider_name,transaction_type,shares,value,transaction_date\nLITE,B,Sell,10,\"1,000\",2026-09-03\n"
    out = I.parse_rows(_transcript(csv_text))
    assert out and out[0]["ticker"] == "LITE"


def test_normalize_key_variants():
    n = I.normalize({"Ticker": "lite", "Insider Name": "B", "Transaction Type": "Sale", "Shares": "10", "Value": "$1,000", "Transaction Date": "2026-09-03T00:00:00", "Position": "CFO"})
    assert n["ticker"] == "LITE" and n["insider"] == "B" and n["txn_type"] == "Sell" and n["value"] == 1000.0 and n["date"] == "2026-09-03" and n["position"] == "CFO"


def test_clusters_and_evidence_direction():
    rows = [I.normalize(r) for r in [
        {"ticker": "COHR", "insider": "A", "txntype": "Buy", "value": 100}, {"ticker": "COHR", "insider": "B", "txntype": "Buy", "value": 200},
        {"ticker": "LITE", "insider": "C", "txntype": "Sell", "value": 50}, {"ticker": "LITE", "insider": "C", "txntype": "Sell", "value": 50}]]
    cl = I.clusters(rows)
    assert cl["COHR"]["buyers"] == ["A", "B"] and cl["COHR"]["buy_value"] == 300 and cl["LITE"]["sellers"] == ["C"]
    theses = {"COHR": {"assumptions": [{"id": "leverage_is_a_watch_item", "derived_from": "potential_investor_interest.score: 4", "status": "open"},
                                       {"id": "datacom_ramp_continues", "derived_from": "ai_positioning: 4", "status": "open"}]},
              "LITE": {"assumptions": [{"id": "x_investor", "derived_from": "potential_investor_interest.score: 3", "status": "open"}]}}
    ev = I.evidence_rows(cl, theses, "2026-09-08")
    assert len(ev) == 1 and ev[0]["ticker"] == "COHR" and ev[0]["assumption_id"] == "leverage_is_a_watch_item"
    assert ev[0]["direction"] == "confirm" and ev[0]["strength"] == 1 and ev[0]["source"] == "insider"   # LITE: one seller only → nothing


if __name__ == "__main__":
    test_prompt_excludes_10b5_1(); test_parse_rows_json_and_csv(); test_normalize_key_variants(); test_clusters_and_evidence_direction()
    print("OK test_insider_pull")
```

- [ ] **Step 2: Run to verify it fails** — `ImportError`.

- [ ] **Step 3: Implement**

```python
# FILE: scripts/thesis/insider_pull.py
#!/usr/bin/env python3
"""Weekly InsiderScore pull for T1+T2: open-market Buy/Sell, 10b5-1 EXCLUDED (the load-bearing split
from the COHR/LITE analysis — pre-planned sales say nothing about conviction).

    python3 scripts/thesis/insider_pull.py [--days 7] [--ticker COHR,LITE] [--dry-run]

Writes state/thesis/insiders_{YYYY-MM-DD}.jsonl (normalized rows + _raw) and, when >= 2 distinct
insiders trade the same direction in one name, a strength-1 evidence row (source 'insider') on that
name's investor-interest assumptions. One claude -p (mcp-lean) per 25 tickers; a claude failure
aborts the run (never grinds). Re-running the same day overwrites the file and adds no new evidence
(source_id is keyed on the week end).
"""
from __future__ import annotations
import argparse, csv, io, json, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from lib import claude_p                                                              # noqa: E402
from etfflows.factset_flows import _SPILL_RE, _tool_result_blocks, resolve_payload, rows_of  # noqa: E402
from thesis import STATE_DIR, thesis_io as tio                                        # noqa: E402

TOOL = "mcp__claude_ai_InsiderScore__get_insider_transactions"
MODEL = "claude-sonnet-4-6"
CHUNK = 25
MIN_INSIDERS = 2


def prompt(tickers: list[str], begin: str, end: str) -> str:
    return (f"Call the InsiderScore get_insider_transactions tool EXACTLY ONCE with these arguments:\n"
            f"  tickerlist: {json.dumps(list(tickers))}\n"
            f"  txntypes: [\"Buy\", \"Sell\"]\n"
            f"  tenb5: 'E'\n"
            f"  use_disclosure_date: true\n"
            f"  begin_date: '{begin}'\n"
            f"  end_date: '{end}'\n"
            f"  limit: 1000\n"
            "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different arguments.\n\n"
            "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat any of the data — "
            "it is read directly from the tool output, not from your reply.")


def _pick(r: dict, *names, default=None):
    low = {str(k).lower().replace("_", "").replace(" ", ""): v for k, v in r.items()}
    for n in names:
        v = low.get(n.lower().replace("_", "").replace(" ", ""))
        if v not in (None, ""):
            return v
    return default


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def normalize(r: dict) -> dict:
    tt = str(_pick(r, "txntype", "transactiontype", "txn_type", "type", "transaction", default="")).strip()
    tt = "Buy" if tt.lower().startswith(("b", "p")) else "Sell" if tt.lower().startswith("s") else tt
    return {"ticker": str(_pick(r, "ticker", "symbol", default="")).upper(),
            "insider": str(_pick(r, "insider", "insidername", "name", "rptname", "reportingname", "owner", "reportingowner", default="")),
            "position": str(_pick(r, "position", "title", "role", "relationship", "officertitle", default="")),
            "txn_type": tt, "shares": _num(_pick(r, "shares", "qty", "quantity", "sharestraded")),
            "value": _num(_pick(r, "value", "amount", "dollarvalue", "txnvalue")),
            "date": str(_pick(r, "date", "transactiondate", "txndate", "disclosuredate", "filingdate", default=""))[:10],
            "notable": _pick(r, "notable", "notableevents", "events", "unusual", default=""), "_raw": r}


def _block_text(text: str) -> str:
    m = _SPILL_RE.search(text or "")
    if m:
        try:
            return Path(m.group(1)).read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return text or ""


def parse_rows(stdout: str) -> list[dict]:
    """tool_result → rows. JSON shapes via rows_of; CSV (InsiderScore tools also return CSV) via DictReader."""
    for text in reversed(_tool_result_blocks(stdout)):
        rows = rows_of(resolve_payload(text))
        if rows is not None:
            return [r for r in rows if isinstance(r, dict)]
        body = _block_text(text).strip()
        head = body.splitlines()[0] if body else ""
        if "," in head and any(w in head.lower() for w in ("ticker", "symbol")):
            try:
                out = list(csv.DictReader(io.StringIO(body)))
                if out:
                    return out
            except csv.Error:
                pass
    return []


def clusters(rows: list[dict]) -> dict[str, dict]:
    acc: dict[str, dict] = {}
    for r in rows:
        c = acc.setdefault(r["ticker"], {"buyers": set(), "sellers": set(), "buy_value": 0.0, "sell_value": 0.0})
        if r["txn_type"] == "Buy":
            c["buyers"].add(r["insider"]); c["buy_value"] += r["value"] or 0.0
        elif r["txn_type"] == "Sell":
            c["sellers"].add(r["insider"]); c["sell_value"] += r["value"] or 0.0
    return {t: {"buyers": sorted(c["buyers"]), "sellers": sorted(c["sellers"]), "buy_value": c["buy_value"], "sell_value": c["sell_value"]}
            for t, c in sorted(acc.items())}


def investor_assumptions(fm: dict) -> list[str]:
    return [a["id"] for a in fm.get("assumptions") or [] if a.get("status") != "retired"
            and ("potential_investor_interest" in str(a.get("derived_from", "")) or "investor" in a["id"])]


def evidence_rows(cl: dict[str, dict], theses: dict[str, dict], week_end: str) -> list[dict]:
    rows = []
    for t, c in sorted(cl.items()):
        fm = theses.get(t)
        if not fm:
            continue
        nb, ns = len(c["buyers"]), len(c["sellers"])
        if nb >= MIN_INSIDERS and ns < MIN_INSIDERS:
            direction, why = "confirm", f"{nb} insiders bought open-market (ex-10b5-1) ${c['buy_value'] / 1e6:.1f}M in the week to {week_end}"
        elif ns >= MIN_INSIDERS and nb < MIN_INSIDERS:
            direction, why = "challenge", f"{ns} insiders sold open-market (ex-10b5-1) ${c['sell_value'] / 1e6:.1f}M in the week to {week_end}"
        else:
            continue
        for aid in investor_assumptions(fm):
            rows.append({"source": "insider", "source_id": f"insider:{t}:{week_end}", "ref": "InsiderScore get_insider_transactions (tenb5=E)",
                         "date": week_end, "title": "insider cluster", "assumption_id": aid, "direction": direction, "strength": 1,
                         "why": why, "quote": "", "cross_ticker": False, "ticker": t})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7); ap.add_argument("--ticker"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    today = date.today()
    begin, end = (today - timedelta(days=a.days)).isoformat(), today.isoformat()
    tickers = a.ticker.split(",") if a.ticker else [t for t in tio.universe() if t.isalpha()]   # US listings only
    rows: list[dict] = []
    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i + CHUNK]
        try:
            stdout = claude_p.run_mcp(prompt(chunk, begin, end), mcp_tool=TOOL, model=MODEL, cwd=str(REPO), timeout=600)
        except RuntimeError as e:
            print(f"ABORT chunk {chunk[0]}..{chunk[-1]}: {e}"); return 1
        got = [normalize(r) for r in parse_rows(stdout)]
        print(f"chunk {chunk[0]}..{chunk[-1]}: {len(got)} rows", flush=True)
        rows += got
    rows = [r for r in rows if r["ticker"] in set(tickers) and r["txn_type"] in ("Buy", "Sell")]
    cl = clusters(rows)
    theses = {t: fm for t in tickers if (fm := tio.load(t))}
    ev = evidence_rows(cl, theses, end)
    if a.dry_run:
        print(json.dumps({"rows": len(rows), "clusters": {t: c for t, c in cl.items() if len(c["buyers"]) + len(c["sellers"]) >= MIN_INSIDERS},
                          "evidence": ev}, indent=1, default=str))
        return 0
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    out = STATE_DIR / f"insiders_{end}.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows), encoding="utf-8")
    from thesis.match_evidence import CHANGES, LOG, _append, _read_log
    log = _read_log()
    existing = {f"{r['ticker']}|{r['source_id']}|{r.get('assumption_id')}" for r in log}
    ts = datetime.now(timezone.utc).isoformat()
    new = [dict(r, ts=ts) for r in ev if f"{r['ticker']}|{r['source_id']}|{r['assumption_id']}" not in existing]
    _append(LOG, new)
    log += new
    for t in sorted({r["ticker"] for r in new}):
        fm = theses[t]
        tio.recompute_pressure(fm, [r for r in log if r["ticker"] == t], today)
        if fm["_changes"]:
            _append(CHANGES, [dict(c, ts=ts, ticker=t, kind="status") for c in fm["_changes"]])
        tio.save(t, fm)
    print(f"DONE rows={len(rows)} file={out.name} clusters={sum(1 for c in cl.values() if len(c['buyers']) + len(c['sellers']) >= MIN_INSIDERS)} "
          f"evidence_rows={len(new)} tickers_updated={len({r['ticker'] for r in new})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_insider_pull.py` → `OK test_insider_pull`.
- [ ] **Step 5: One real dry-run** — `set -a && . /root/podcasts/.env && set +a && python3 scripts/thesis/insider_pull.py --ticker COHR,LITE,NVDA,AMD,AVGO --days 14 --dry-run` (one MCP call). Inspect `_raw` keys in the output; if `normalize` missed the real key names, add them to `_pick(...)` lists and re-run the unit test. Confirm no row carries a 10b5-1 marker.
- [ ] **Step 6: Commit** — `git add scripts/thesis/insider_pull.py scripts/thesis/test_insider_pull.py && git commit -m "thesis: weekly InsiderScore pull (open-market, ex-10b5-1) → insiders_{date}.jsonl + strength-1 investor-interest evidence"`

---

### Task 8: Store B weekly refresh — `ingest_metrics.py --pull / --cron`

**Files:**
- Modify: `scripts/chunking/ingest_metrics.py` (constants after `KINDS`, new functions before `main`, `main` gains `--pull/--cron/--snapshot`)
- Test: `scripts/chunking/test_ingest_metrics_pull.py`

**Interfaces:**
- Consumes: `claude_p.run_mcp`, `factset_flows._tool_result_blocks/resolve_payload/rows_of`, existing `id_maps/build/get_metrics_store`.
- Produces: refreshed `state/chunk_store/factset_raw/{METRIC}_{kind}.json` (`{"data": rows}`; previous copy at `.prev.json`), `state/thesis/consensus_{date}.jsonl` rows `{ticker, metric, period, fiscal_end, guidance_mid, consensus_at_guide, consensus_at_print, actual, as_of}` (read by `thesis_report.storeb_context`); functions `pull_prompt(ids, metric, kind, start, end)`, `mcp_runner(ids, metric, kind, start, end) -> list[dict]`, `pull_all(tickers, metrics, *, kinds, runner, start, end, log) -> dict[str, int]`, `consensus_snapshot(records, path) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/chunking/test_ingest_metrics_pull.py
"""Run directly: python3 scripts/chunking/test_ingest_metrics_pull.py  (no network; RAW redirected)"""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_metrics as IM  # noqa: E402


def test_pull_prompt_shapes():
    g = IM.pull_prompt(["NVDA-US", "AMD-US"], "SALES", "guidance", "2020-01-01", "2026-09-14")
    assert "FactSet_EstimatesConsensus" in g and "estimate_type: 'guidance'" in g and "relativeFiscalStart: 1" in g
    assert "periodicity: 'QTR'" in g and "frequency: 'AM'" in g and '"NVDA-US"' in g and "metrics: [\"SALES\"]" in g
    s = IM.pull_prompt(["NVDA-US"], "EPS", "surprise", "2020-01-01", "2026-09-14")
    assert "estimate_type: 'surprise'" in s and "statistic: 'MEAN'" in s and "relativeFiscalStart" not in s


def test_pull_all_writes_union_and_keeps_prev(tmp):
    IM.RAW = tmp
    (tmp / "SALES_guidance.json").write_text(json.dumps({"data": [{"requestId": "OLD-US"}]}))
    calls = []
    def runner(ids, metric, kind, start, end):
        calls.append((tuple(ids), metric, kind))
        return [{"requestId": i, "metric": metric, "kind": kind} for i in ids]
    IM.IDS_PER_CALL = 2
    counts = IM.pull_all(["NVDA", "AMD", "AVGO"], ["SALES"], kinds=("guidance",), runner=runner, end="2026-09-14")
    assert counts == {"SALES_guidance": 3} and len(calls) == 2 and calls[0][0] == ("NVDA-US", "AMD-US")
    assert [r["requestId"] for r in json.loads((tmp / "SALES_guidance.json").read_text())["data"]] == ["NVDA-US", "AMD-US", "AVGO-US"]
    assert json.loads((tmp / "SALES_guidance.prev.json").read_text())["data"][0]["requestId"] == "OLD-US"


def test_pull_all_failure_leaves_file_untouched(tmp):
    IM.RAW = tmp
    (tmp / "EPS_surprise.json").write_text(json.dumps({"data": [{"requestId": "KEEP-US"}]}))
    def runner(ids, metric, kind, start, end):
        raise RuntimeError("claude -p rc=1")
    try:
        IM.pull_all(["NVDA"], ["EPS"], kinds=("surprise",), runner=runner); assert False
    except RuntimeError:
        pass
    assert json.loads((tmp / "EPS_surprise.json").read_text())["data"][0]["requestId"] == "KEEP-US"


def test_consensus_snapshot_latest_period(tmp):
    recs = [{"ticker": "NVDA", "metric": "SALES", "period": "1Q27", "fiscal_end": "2026-04-30", "guidance_mid": 1, "consensus_at_guide": 2, "consensus_at_print": 3, "actual": 4, "as_of": "2026-09-14"},
            {"ticker": "NVDA", "metric": "SALES", "period": "2Q27", "fiscal_end": "2026-07-31", "guidance_mid": 5, "consensus_at_guide": 6, "consensus_at_print": None, "actual": None, "as_of": "2026-09-14"}]
    p = tmp / "consensus_2026-09-14.jsonl"
    assert IM.consensus_snapshot(recs, p) == 1
    row = json.loads(p.read_text().splitlines()[0])
    assert row["period"] == "2Q27" and row["guidance_mid"] == 5 and row["consensus_at_print"] is None


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_pull_prompt_shapes(); test_pull_all_writes_union_and_keeps_prev(tmp); test_pull_all_failure_leaves_file_untouched(tmp); test_consensus_snapshot_latest_period(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_ingest_metrics_pull")
```

- [ ] **Step 2: Run to verify it fails** — `AttributeError: module 'ingest_metrics' has no attribute 'pull_prompt'`.

- [ ] **Step 3: Implement** — insert after `KINDS = ("guidance", "surprise")`:

```python
# --- weekly FactSet pull (thesis loop P5) -----------------------------------
PULL_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_EstimatesConsensus"
PULL_MODEL = "claude-sonnet-4-6"
PULL_START = "2020-01-01"        # full history every week: build() is unchanged and needs the whole series
IDS_PER_CALL = 10                # keeps each response under the MCP size cap (spill handled anyway)
SNAPSHOT_DIR = REPO / "state" / "thesis"
```

and before `def main():`:

```python
def pull_prompt(ids, metric: str, kind: str, start: str, end: str) -> str:
    """One EstimatesConsensus call. guidance needs relativeFiscalStart (every stored row has
    relativePeriod=1); surprise needs startDate/endDate + statistic. periodicity QTR + frequency AM
    per the module docstring (AQ silently drops off-calendar quarters)."""
    args = [f"  ids: {json.dumps(list(ids))}", f"  estimate_type: '{kind}'", f"  metrics: [\"{metric}\"]",
            "  periodicity: 'QTR'", f"  startDate: '{start}'", f"  endDate: '{end}'", "  frequency: 'AM'"]
    args += ["  relativeFiscalStart: 1", "  relativeFiscalEnd: 1"] if kind == "guidance" else ["  statistic: 'MEAN'"]
    return ("Call the FactSet_EstimatesConsensus tool EXACTLY ONCE with these arguments:\n" + "\n".join(args) + "\n"
            "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different arguments.\n\n"
            "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat any of the data — "
            "it is read directly from the tool output, not from your reply.")


def mcp_runner(ids, metric: str, kind: str, start: str, end: str) -> list[dict]:
    sys.path.insert(0, str(REPO / "scripts"))
    from lib import claude_p
    from etfflows.factset_flows import _tool_result_blocks, resolve_payload, rows_of
    stdout = claude_p.run_mcp(pull_prompt(ids, metric, kind, start, end), mcp_tool=PULL_TOOL, model=PULL_MODEL,
                              cwd=str(REPO), timeout=600)
    for text in reversed(_tool_result_blocks(stdout)):
        rows = rows_of(resolve_payload(text))
        if rows is not None:
            return [r for r in rows if isinstance(r, dict)]
    raise ValueError(f"tool_result unusable for {metric}/{kind} {ids[0]}..: {stdout.strip()[-200:]}")


def pull_all(tickers, metrics, *, kinds=KINDS, runner=mcp_runner, start: str = PULL_START,
             end: str | None = None, log=print) -> dict[str, int]:
    """Refresh RAW/{metric}_{kind}.json for the given tickers. A file is replaced only after every
    id-chunk for it succeeded (previous copy kept as .prev.json); any failure raises and leaves the
    old file in place, so a half-pull can never feed build()."""
    end = end or date.today().isoformat()
    tk_to_fid, _ = id_maps(tickers)
    ids = [tk_to_fid[t] for t in tickers]
    RAW.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for metric in metrics:
        for kind in kinds:
            rows: list[dict] = []
            for i in range(0, len(ids), IDS_PER_CALL):
                chunk = ids[i:i + IDS_PER_CALL]
                got = runner(chunk, metric, kind, start, end)
                log(f"  {metric}/{kind} {chunk[0]}..{chunk[-1]}: {len(got)} rows")
                rows += got
            p = RAW / f"{metric}_{kind}.json"
            if p.exists():
                p.replace(p.with_suffix(".prev.json"))
            tmp = p.with_suffix(".tmp")
            tmp.write_text(json.dumps({"data": rows}))
            tmp.replace(p)
            counts[f"{metric}_{kind}"] = len(rows)
    return counts


def consensus_snapshot(records: list[dict], path: Path) -> int:
    """Latest fiscal period per (ticker, metric) → jsonl; the thesis report diffs consecutive
    snapshots for consensus drift (consensus_at_print, else consensus_at_guide)."""
    latest: dict[tuple, dict] = {}
    for r in records:
        k = (r["ticker"], r["metric"])
        if r.get("fiscal_end") and (k not in latest or str(r["fiscal_end"]) > str(latest[k]["fiscal_end"])):
            latest[k] = r
    keys = ("ticker", "metric", "period", "fiscal_end", "guidance_mid", "consensus_at_guide", "consensus_at_print", "actual", "as_of")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for k in sorted(latest):
            f.write(json.dumps({x: latest[k].get(x) for x in keys}, default=str) + "\n")
    return len(latest)
```

In `main()`: add `ap.add_argument("--pull", action="store_true", help="refresh factset_raw via FactSet MCP, then build+report (no write unless --cron)")`, `ap.add_argument("--cron", action="store_true", help="weekly: pull + build + write pg + consensus snapshot")`, `ap.add_argument("--snapshot", action="store_true", help="also write state/thesis/consensus_{date}.jsonl")`. After `metrics = ...`: `if args.pull or args.cron: counts = pull_all(tickers, metrics); print("pulled:", json.dumps(counts))`. Change the dry-run guard to `if args.dry_run or (args.pull and not args.cron):` (a plain `--pull` never writes pg). After the store write: `if args.cron or args.snapshot: n = consensus_snapshot(records, SNAPSHOT_DIR / f"consensus_{date.today().isoformat()}.jsonl"); print(f"consensus snapshot: {n} rows")`.

- [ ] **Step 4: Run tests** — `python3 scripts/chunking/test_ingest_metrics_pull.py` → `OK test_ingest_metrics_pull`.
- [ ] **Step 5: Bounded real pull** — `set -a && . /root/podcasts/.env && set +a && python3 scripts/chunking/ingest_metrics.py --pull --tickers NVDA,AVGO,COHR --metrics SALES 2>&1 | tail -30` (2 MCP calls). Expect the coverage guard `✓` (AVGO's FY22Q2/FY23Q3 present), `SALES_guidance.json` rows for the 3 ids only — **then restore the full file**: `mv state/chunk_store/factset_raw/SALES_guidance.prev.json state/chunk_store/factset_raw/SALES_guidance.json` (same for surprise), because a partial-universe pull replaces the whole file. The full weekly `--cron` runs all 89 names (54 calls) and is left to the Sunday 08:00 cron; verify Monday with `SELECT max(as_of), count(*) FROM metrics`.
- [ ] **Step 6: Commit** — `git add scripts/chunking/ingest_metrics.py scripts/chunking/test_ingest_metrics_pull.py && git commit -m "store-b: weekly FactSet pull via run_mcp (--pull/--cron) + consensus snapshots for drift"`

---

### Task 9: PDF EX-99 exhibits in the SEC channel (decks, investor days, ADR 6-K reports)

**Files:**
- Modify: `scripts/v3_ingest/sec_filings.py` (`fetch_ex99`, `process_filing` call site, `main` gains `--accession`)
- Test: `scripts/v3_ingest/test_sec_pdf_exhibits.py`

**Finding that changes the design (2026-09-09 survey of 530 EDGAR exhibit indexes):** every PDF EX-99 observed sits on a **6-K** (GDS, BIDU, HSAI, BABA, NTES), which carries no item codes; zero were on 8-Ks. So the gate is form-based: 6-K always, 8-K when `{"2.02","7.01","8.01"} & set(items)`. Extraction must stream pages with an early break (the GDS 6-K EX-99.2 is 374 pages / 1.3M chars; join-then-slice would blow the 165 MB envelope).

**Interfaces:**
- Produces: `pdf_to_text(data: bytes, max_pages=60, max_chars=120_000) -> str`; `fetch_ex99(cik, accession, *, form: str = "8-K", items: list[str] | None = None)`; section header `## Exhibit EX-99.N (slides)`; CLI `--accession 0001104659-26-105234` (with `--ticker`) re-processes one known filing even if already in the watermark.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/v3_ingest/test_sec_pdf_exhibits.py
"""Run directly: python3 scripts/v3_ingest/test_sec_pdf_exhibits.py  (no network: exhibit map + http stubbed)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sec_filings as S  # noqa: E402

def _pdf(text: str = "Investor Day 2026 capacity plan") -> bytes:
    """Minimal one-page PDF with a real xref table (pypdf refuses files without startxref)."""
    stream = f"BT /F1 14 Tf 20 150 Td ({text}) Tj ET".encode()
    objs = [b"<</Type/Catalog/Pages 2 0 R>>", b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 300]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
            b"<</Length " + str(len(stream)).encode() + b">>stream\n" + stream + b"\nendstream",
            b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>"]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<</Size {len(objs) + 1}/Root 1 0 R>>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


PDF = _pdf()


class _Resp:
    def __init__(self, content=b"", text=""):
        self.content, self.text = content, text


def _stub(exmap):
    S.fetch_exhibit_map = lambda cik, acc: exmap
    S.http_get = lambda url: _Resp(content=PDF, text="<html><body><p>press release text here</p></body></html>")


def test_pdf_to_text_extracts_and_caps():
    t = S.pdf_to_text(PDF)
    assert "Investor Day 2026" in t
    assert S.pdf_to_text(PDF, max_chars=8) == "Investor"


def test_8k_pdf_only_on_presentation_items():
    _stub({"8-K": "a.htm", "EX-99.1": "deck.pdf"})
    assert S.fetch_ex99(1, "0000000000-26-000001", form="8-K", items=["7.01", "9.01"])[0][0] == "EX-99.1 (slides)"
    assert S.fetch_ex99(1, "0000000000-26-000001", form="8-K", items=["5.02"]) == []


def test_6k_pdf_always_and_html_untouched():
    _stub({"6-K": "a.htm", "EX-99.1": "pr.htm", "EX-99.2": "report.pdf"})
    out = S.fetch_ex99(1, "0000000000-26-000002", form="6-K", items=[])
    assert [o[0] for o in out] == ["EX-99.1", "EX-99.2 (slides)"] and "press release" in out[0][2] and "Investor Day" in out[1][2]


if __name__ == "__main__":
    test_pdf_to_text_extracts_and_caps(); test_8k_pdf_only_on_presentation_items(); test_6k_pdf_always_and_html_untouched()
    print("OK test_sec_pdf_exhibits")
```

- [ ] **Step 2: Run to verify it fails** — `AttributeError: module 'sec_filings' has no attribute 'pdf_to_text'`.

- [ ] **Step 3: Implement** — replace `fetch_ex99` with:

```python
PDF_EXHIBIT_ITEMS = {"2.02", "7.01", "8.01"}   # 8-K items that carry decks (earnings, Reg FD, other events)
PDF_MAX_PAGES = 60
PDF_MAX_CHARS = 120_000


def pdf_to_text(data: bytes, max_pages: int = PDF_MAX_PAGES, max_chars: int = PDF_MAX_CHARS) -> str:
    """Deck/report text, streamed page by page with an early break on BOTH caps (a 374-page ADR annual
    report must not be joined then sliced inside the 165 MB ingest envelope)."""
    import io
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(data))
    parts, used = [], 0
    for i, page in enumerate(reader.pages):
        if i >= max_pages or used >= max_chars:
            break
        try:
            t = (page.extract_text() or "").strip()
        except Exception:  # noqa: BLE001 — one bad page must not sink the deck
            t = ""
        if t:
            parts.append(t)
            used += len(t) + 2
    return "\n\n".join(parts)[:max_chars]


def fetch_ex99(cik: int, accession: str, *, form: str = "8-K", items: list[str] | None = None) -> list[tuple[str, str, str]]:
    """All EX-99.* exhibits as [(ex_type, url, markdown)]. HTML always. PDF on every 6-K (ADR issuers
    furnish reports/decks as PDF and 6-K has no item codes) and on 8-K items 2.02/7.01/8.01; a PDF
    exhibit is labelled '(slides)' so its section header is distinguishable downstream."""
    exmap = fetch_exhibit_map(cik, accession)
    base = filing_base_url(cik, accession)
    want_pdf = form == "6-K" or bool(PDF_EXHIBIT_ITEMS & set(items or []))
    out = []
    for etype in sorted(exmap):
        if not re.match(r"(?i)EX-99", etype):
            continue
        doc = exmap[etype]
        is_html = bool(re.search(r"\.html?$", doc, re.I))
        is_pdf = bool(re.search(r"\.pdf$", doc, re.I))
        if not is_html and not (is_pdf and want_pdf):
            continue     # images, and PDFs outside the presentation gate
        url = f"{base}/{doc}"
        try:
            if is_html:
                md, label = html_to_markdown(http_get(url).text), etype
            else:
                md, label = pdf_to_text(http_get(url).content), f"{etype} (slides)"
        except Exception as e:  # noqa: BLE001
            log(f"    EX fetch failed {etype} {doc}: {type(e).__name__}: {e}")
            continue
        if md.strip():
            out.append((label, url, md))
    return out
```

In `process_filing`, change the call to `fetch_ex99(cik, filing["accession"], form=base_form, items=filing.get("items"))`. In `main()`: add `ap.add_argument("--accession", help="re-process this one accession for --ticker even if already in the watermark (testing/backfill)")`; in the per-ticker loop, right after `sel = select_filings(...)`: `if args.accession: sel = [f for f in filings if f["accession"] == args.accession]` (bypasses the processed-set skip; `filings` is the full fetched list).

- [ ] **Step 4: Run tests** — `python3 scripts/v3_ingest/test_sec_pdf_exhibits.py` → `OK test_sec_pdf_exhibits`; also `python3 scripts/v3_ingest/test_sec_filings.py` if present (regression).
- [ ] **Step 5: Real re-fetch** — `cd /root/research-watchlist && /usr/bin/time -v python3 scripts/v3_ingest/sec_filings.py --ticker GDS --accession 0001104659-26-105234 --skip-themes 2>&1 | grep -E "EX-99|Maximum resident|DONE|FAILED"`. Expect the GDS 2026-09-04 6-K note to gain `## Exhibit EX-99.1 (slides)`, chunk count > 0 in pg for that doc, and `Maximum resident set size` under 200 MB. (`--skip-themes` avoids a claude -p call while the drafter/matcher batches may still be running.)
- [ ] **Step 6: Commit** — `git add scripts/v3_ingest/sec_filings.py scripts/v3_ingest/test_sec_pdf_exhibits.py && git commit -m "sec: ingest PDF EX-99 exhibits (6-K always, 8-K 2.02/7.01/8.01) streamed under the memory envelope; --accession re-fetch"`


---

### Task 10: `apply_scores.py` + `check.py` thesis validation

**Files:**
- Create: `scripts/thesis/apply_scores.py`
- Modify: `scripts/check.py` (new `# --- 6. thesis files ---` block before `# --- report ---`)
- Test: `scripts/thesis/test_apply_scores.py`

**Interfaces:**
- Consumes: `thesis_io.load/save/watchlist_scores`, `notes/*/_thesis.md` `proposed_scores`.
- Produces: `proposals(tickers=None) -> list[{ticker, key, value, applied, since, source}]`, `patch_text(text, ticker, key, value) -> str` (raises `PatchError`), `apply(accept, key, write) -> int`. `check.py` reports `thesis: notes/X/_thesis.md: <error>` and prints `WARN thesis: N T1/T2 ticker(s) without _thesis.md`.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/thesis/test_apply_scores.py
"""Run directly: python3 scripts/thesis/test_apply_scores.py"""
import sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import apply_scores as A  # noqa: E402

SAMPLE = """tier_1_bctk:
  - ticker: COHR
    themes: [a, b]
    ai_positioning:
      score: "4"
      notes: "n"
    competitive_advantage:
      innovation_rate: "4"
      distribution: "4"   # comment
      overall: "4"
    potential_investor_interest:
      score: "4"
      notes: "n"
  - ticker: ZZZ
    ai_positioning: "3"
    competitive_advantage:
      innovation_rate: "3"
    potential_investor_interest: "2"
tier_3_watchlist:
  - ticker: COHR
    themes: [a]
"""


def test_patch_nested_and_inline_forms():
    t = A.patch_text(SAMPLE, "COHR", "potential_investor_interest.score", "4+")
    t = A.patch_text(t, "COHR", "competitive_advantage.distribution", "5")
    t = A.patch_text(t, "ZZZ", "ai_positioning", "3+")
    d = yaml.safe_load(t)
    assert d["tier_1_bctk"][0]["potential_investor_interest"]["score"] == "4+"
    assert d["tier_1_bctk"][0]["competitive_advantage"]["distribution"] == "5" and "# comment" in t
    assert d["tier_1_bctk"][1]["ai_positioning"] == "3+"
    assert d["tier_3_watchlist"][0] == {"ticker": "COHR", "themes": ["a"]}          # T3 block untouched
    assert t.count("\n") == SAMPLE.count("\n")                                     # formatting preserved


def test_patch_errors():
    for args in (("NOPE", "ai_positioning", "4"), ("ZZZ", "competitive_advantage.overall", "4")):
        try:
            A.patch_text(SAMPLE, *args); assert False, args
        except A.PatchError:
            pass


if __name__ == "__main__":
    test_patch_nested_and_inline_forms(); test_patch_errors()
    print("OK test_apply_scores")
```

- [ ] **Step 2: Run to verify it fails** — `ImportError`.

- [ ] **Step 3: Implement**

```python
# FILE: scripts/thesis/apply_scores.py
#!/usr/bin/env python3
"""Operator-invoked: print/apply the exact watchlist.yaml diff for accepted score proposals.

    python3 scripts/thesis/apply_scores.py --list
    python3 scripts/thesis/apply_scores.py --accept COHR,LITE                    # unified diff only
    python3 scripts/thesis/apply_scores.py --accept COHR --key ai_positioning --write

config/watchlist.yaml is never machine-written on a schedule. This script runs only when the
operator runs it: it edits the score lines in place (text patch — comments and formatting survive),
re-parses the result as YAML before writing, writes atomically through the symlink to the real
file, then mirrors the new scores into notes/{T}/_thesis.md and clears the accepted proposals.
"""
from __future__ import annotations
import argparse, difflib, os, re, sys, tempfile
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from thesis import thesis_io as tio   # noqa: E402

WATCHLIST = REPO / "config" / "watchlist.yaml"
_KEY_PATH = {"ai_positioning": ("ai_positioning", "score"),
             "competitive_advantage.innovation_rate": ("competitive_advantage", "innovation_rate"),
             "competitive_advantage.distribution": ("competitive_advantage", "distribution"),
             "competitive_advantage.overall": ("competitive_advantage", "overall"),
             "potential_investor_interest.score": ("potential_investor_interest", "score")}
_VAL = r'(["\']?)([1-5][+-]?)(["\']?)'


class PatchError(ValueError):
    pass


def proposals(tickers=None) -> list[dict]:
    out = []
    for p in sorted((REPO / "notes").glob("*/_thesis.md")):
        t = p.parent.name
        if tickers and t not in tickers:
            continue
        fm = tio.load(t) or {}
        for k, v in (fm.get("proposed_scores") or {}).items():
            out.append({"ticker": t, "key": k, "value": str(v.get("value")), "applied": (fm.get("scores") or {}).get(k),
                        "since": v.get("since"), "source": v.get("source")})
    return out


def _indent(l: str) -> int:
    return len(l) - len(l.lstrip())


def _block_span(lines: list[str], ticker: str) -> tuple[int, int]:
    """First '- ticker: T' entry (T1 precedes T2 precedes T3 in the file — the same block watchlist_scores reads)."""
    start = next((i for i, l in enumerate(lines) if re.match(rf"^\s*-\s*ticker:\s*{re.escape(ticker)}\s*$", l)), None)
    if start is None:
        raise PatchError(f"{ticker}: no '- ticker: {ticker}' line in watchlist")
    ind = _indent(lines[start])
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip() and _indent(lines[j]) <= ind and not lines[j].lstrip().startswith("#"):
            end = j
            break
    return start, end


def patch_text(text: str, ticker: str, key: str, value: str) -> str:
    """Replace one score inside the ticker's block. Handles both schema variants:
    nested (`ai_positioning:` / `  score: "4"`) and inline (`ai_positioning: "4"`)."""
    if key not in _KEY_PATH:
        raise PatchError(f"unknown score key {key}")
    parent, leaf = _KEY_PATH[key]
    lines = text.split("\n")
    start, end = _block_span(lines, ticker)
    blk = lines[start:end]
    if leaf == "score":                                     # inline form
        for i, l in enumerate(blk):
            m = re.match(rf"^(\s*{parent}:\s*){_VAL}\s*$", l)
            if m:
                blk[i] = f'{m.group(1)}"{value}"'
                return "\n".join(lines[:start] + blk + lines[end:])
    pi = next((i for i, l in enumerate(blk) if re.match(rf"^\s*{parent}:\s*$", l)), None)
    if pi is None:
        raise PatchError(f"{ticker}: no '{parent}:' block")
    pind = _indent(blk[pi])
    for i in range(pi + 1, len(blk)):
        l = blk[i]
        if l.strip() and _indent(l) <= pind:
            break
        m = re.match(rf"^(\s*{leaf}:\s*){_VAL}(\s*(?:#.*)?)$", l)
        if m:
            blk[i] = f'{m.group(1)}"{value}"{m.group(5)}'
            return "\n".join(lines[:start] + blk + lines[end:])
    raise PatchError(f"{ticker}: no '{leaf}:' line under '{parent}:'")


def apply(accept: list[str], key: str | None, write: bool) -> int:
    props = [p for p in proposals(set(accept)) if not key or p["key"] == key]
    if not props:
        print("nothing to apply")
        return 0
    target = WATCHLIST.resolve()
    old = target.read_text(encoding="utf-8")
    new = old
    for p in props:
        new = patch_text(new, p["ticker"], p["key"], p["value"])
    yaml.safe_load(new)                                     # must still parse before anything is written
    print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(target), tofile=str(target) + " (proposed)")) or "(no textual change)")
    if not write:
        print(f"\n{len(props)} change(s) NOT written (add --write)")
        return 0
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".watchlist-", suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, target)
    for p in props:
        fm = tio.load(p["ticker"])
        fm.setdefault("scores", {})[p["key"]] = p["value"]
        (fm.get("proposed_scores") or {}).pop(p["key"], None)
        tio.save(p["ticker"], fm)
        live = tio.watchlist_scores(p["ticker"]).get(p["key"])
        print(f"{p['ticker']} {p['key']}: watchlist now {live!r}" + ("" if live == p["value"] else "  <-- MISMATCH, inspect"))
    print(f"wrote {len(props)} change(s) to {target}; proposals cleared in _thesis.md")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true"); ap.add_argument("--accept", help="comma list of tickers")
    ap.add_argument("--key", help="restrict to one score key"); ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.accept:
        return apply(a.accept.split(","), a.key, a.write)
    for p in proposals():
        print(f"{p['ticker']:<8} {p['key']:<42} proposed {p['value']:<3} applied {p['applied']!s:<4} since {p['since']}  ({p['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`scripts/check.py` — insert before `# --- report ---`:

```python
# --- 6. thesis files (notes/*/_thesis.md) -----------------------------------
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from thesis import thesis_io as _tio
    for th in sorted((ROOT / "notes").glob("*/_thesis.md")):
        checked += 1
        try:
            _fm = _tio.load(th.parent.name) or {}
        except Exception as e:  # noqa: BLE001
            err(f"thesis: {rel(th)}: unreadable ({type(e).__name__}: {e})")
            continue
        for e in _tio.validate(_fm):
            err(f"thesis: {rel(th)}: {e}")
        if _fm.get("ticker") != th.parent.name:
            err(f"thesis: {rel(th)}: ticker {_fm.get('ticker')!r} != directory {th.parent.name}")
    _missing = [t for t in _tio.universe() if not t.endswith(".pvt") and not (ROOT / "notes" / t / "_thesis.md").exists()]
    if _missing:
        print(f"WARN thesis: {len(_missing)} T1/T2 ticker(s) without _thesis.md: {', '.join(_missing)}")
except ImportError as e:
    print(f"WARN thesis: validation skipped ({e})")
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_apply_scores.py` → OK; `python3 scripts/check.py` → `OK — N file(s) checked` (with the WARN line while the drafter is still filling in).
- [ ] **Step 5: Real diff, no write** — `python3 scripts/thesis/apply_scores.py --list` then `--accept <first ticker listed>` and read the unified diff: exactly one score line changes inside that ticker's T1/T2 block. Do NOT `--write` (operator's call).
- [ ] **Step 6: Commit** — `git add scripts/thesis/apply_scores.py scripts/thesis/test_apply_scores.py scripts/check.py && git commit -m "thesis: apply_scores (operator-invoked watchlist patch) + check.py thesis validation"`

---

### Task 11: `thesis-chat` skill + `answer.py`

**Files:**
- Create: `scripts/thesis/answer.py`, `.claude/skills/thesis-chat/SKILL.md`
- Test: `scripts/thesis/test_answer.py`

**Interfaces:**
- Consumes: `state/thesis/questions.jsonl` (Task 6 shape), `thesis_io.load/save`.
- Produces: `answer.py --list [--ticker T]`, `answer.py --id QID --action keep|retire|confirm|challenge|edit [--text ...]` (assumption questions) or `--action accept|reject` (score questions); `apply_answer(q, action, text) -> str`. Every operator action sets `status_source: operator`, `draft: false`, `reviewed_by_operator: true`.

- [ ] **Step 1: Write the failing test**

```python
# FILE: scripts/thesis/test_answer.py
"""Run directly: python3 scripts/thesis/test_answer.py"""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import thesis_io as tio   # noqa: E402
from thesis import answer as AN       # noqa: E402


def _fm():
    return {"doc_type": "thesis", "ticker": "TST", "tier": "tier_1_bctk", "drafted": "2026-09-10", "reviewed_by_operator": False,
            "scores": {"ai_positioning": "4"}, "proposed_scores": {"ai_positioning": {"value": "4+", "since": "2026-09-11", "source": "s"}},
            "assumptions": [{"id": "a1", "statement": "S", "derived_from": "d", "themes": [], "challenged_by": ["x"], "confirmed_by": [],
                             "status": "challenged", "status_source": "evidence", "pressure": {"confirm": 0, "challenge": 5, "window_days": 90, "last_evidence": None}, "draft": True}]}


def test_actions(tmp):
    tio.NOTES = tmp / "notes"; AN.QUESTIONS = tmp / "questions.jsonl"
    tio.save("TST", _fm(), "## R\n")
    qs = [{"id": "draft:TST:a1", "kind": "draft_review", "ticker": "TST", "assumption_id": "a1", "text": "?", "asked_at": "t", "answered_at": None, "answer": None},
          {"id": "score:TST:ai_positioning", "kind": "score_proposal", "ticker": "TST", "key": "ai_positioning", "value": "4+", "text": "?", "asked_at": "t", "answered_at": None, "answer": None}]
    AN.QUESTIONS.write_text("".join(json.dumps(q) + "\n" for q in qs))
    assert AN.main(["--id", "draft:TST:a1", "--action", "keep"]) == 0
    a = tio.load("TST")["assumptions"][0]
    assert a["status"] == "challenged" and a["status_source"] == "operator" and a["draft"] is False   # keep = status unchanged, now operator-owned
    assert tio.load("TST")["reviewed_by_operator"] is True
    assert AN.load_questions()[0]["answered_at"] and AN.load_questions()[0]["answer"]["action"] == "keep"
    AN.QUESTIONS.write_text("".join(json.dumps(q) + "\n" for q in qs))
    assert AN.main(["--id", "draft:TST:a1", "--action", "edit", "--text", "New statement"]) == 0
    assert tio.load("TST")["assumptions"][0]["statement"] == "New statement"
    assert AN.main(["--id", "draft:TST:a1", "--action", "retire"]) == 0 and tio.load("TST")["assumptions"][0]["status"] == "retired"
    assert AN.main(["--id", "score:TST:ai_positioning", "--action", "reject"]) == 0 and tio.load("TST")["proposed_scores"] == {}
    assert AN.main(["--id", "nope", "--action", "keep"]) == 1


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    try:
        test_actions(tmp)
    finally:
        shutil.rmtree(tmp)
    print("OK test_answer")
```

- [ ] **Step 2: Run to verify it fails** — `ImportError`.

- [ ] **Step 3: Implement**

```python
# FILE: scripts/thesis/answer.py
#!/usr/bin/env python3
"""Record operator answers from state/thesis/questions.jsonl into notes/{T}/_thesis.md.

    python3 scripts/thesis/answer.py --list [--ticker COHR]
    python3 scripts/thesis/answer.py --id draft:COHR:datacom_ramp_continues --action keep|retire|confirm|challenge|edit [--text "..."]
    python3 scripts/thesis/answer.py --id score:COHR:ai_positioning --action accept|reject

Assumption actions set status_source: operator, draft: false and reviewed_by_operator: true on the
file ('keep' leaves the status as it stands; 'edit' replaces the statement). 'accept' on a score
question only prints the apply_scores command — the watchlist is written by apply_scores --write.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from thesis import STATE_DIR, thesis_io as tio   # noqa: E402

QUESTIONS = STATE_DIR / "questions.jsonl"
STATUS_FOR = {"retire": "retired", "confirm": "confirmed", "challenge": "challenged"}
ASSUMPTION_ACTIONS = ("keep", "edit", *STATUS_FOR)


def load_questions() -> list[dict]:
    if not QUESTIONS.exists():
        return []
    return [json.loads(l) for l in QUESTIONS.read_text(encoding="utf-8").splitlines() if l.strip()]


def save_questions(rows: list[dict]):
    tmp = QUESTIONS.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    tmp.replace(QUESTIONS)


def apply_answer(q: dict, action: str, text: str | None = None) -> str:
    fm = tio.load(q["ticker"])
    if not fm:
        raise ValueError(f"no thesis file for {q['ticker']}")
    if q["kind"] == "score_proposal":
        if action == "accept":
            return f"run: python3 scripts/thesis/apply_scores.py --accept {q['ticker']} --key {q['key']} --write"
        if action == "reject":
            (fm.get("proposed_scores") or {}).pop(q["key"], None)
            tio.save(q["ticker"], fm)
            return f"{q['ticker']} {q['key']}: proposal dropped"
        raise ValueError("score questions take --action accept|reject")
    if action not in ASSUMPTION_ACTIONS:
        raise ValueError(f"--action must be one of {ASSUMPTION_ACTIONS}")
    a = next((x for x in fm.get("assumptions") or [] if x["id"] == q["assumption_id"]), None)
    if not a:
        raise ValueError(f"{q['ticker']}: assumption {q['assumption_id']} not found")
    if action == "edit":
        if not text:
            raise ValueError("edit needs --text")
        a["statement"] = text.strip()
    elif action in STATUS_FOR:
        a["status"] = STATUS_FOR[action]
    a["status_source"] = "operator"
    a["draft"] = False
    fm["reviewed_by_operator"] = True
    tio.save(q["ticker"], fm)
    return f"{q['ticker']}/{a['id']}: {action} → status {a['status']} (operator)"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true"); ap.add_argument("--ticker"); ap.add_argument("--id"); ap.add_argument("--action"); ap.add_argument("--text")
    a = ap.parse_args(argv)
    rows = load_questions()
    if a.list or not a.id:
        for q in rows:
            if q.get("answered_at") or (a.ticker and q["ticker"] != a.ticker):
                continue
            print(f"{q['id']}\n    {q['text']}")
        return 0
    q = next((x for x in rows if x["id"] == a.id), None)
    if not q:
        print(f"unknown question id {a.id}"); return 1
    if not a.action:
        print("--action required"); return 1
    try:
        msg = apply_answer(q, a.action, a.text)
    except ValueError as e:
        print(f"ERROR {e}"); return 1
    q["answered_at"] = datetime.now(timezone.utc).isoformat()
    q["answer"] = {"action": a.action, "text": a.text}
    save_questions(rows)
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```markdown
# FILE: .claude/skills/thesis-chat/SKILL.md
---
name: thesis-chat
description: Weekly operator chat over the thesis loop — walks the open questions in state/thesis/questions.jsonl (drafts that got their first evidence, stale assumptions, pending score proposals), shows the evidence behind each, records the operator's decision via scripts/thesis/answer.py, and answers ad-hoc questions about any ticker's thesis from notes/{T}/_thesis.md + state/thesis/evidence_log.jsonl. Use when the operator says "thesis chat", "walk me through the thesis questions", "what changed on COHR's thesis", or after reading a Thesis delta email.
---

# Thesis chat

You are the operator's weekly thesis review partner. Everything you show comes from files; every
decision you record goes through `scripts/thesis/answer.py` (never edit `_thesis.md` by hand here,
and never touch `config/watchlist.yaml` — score changes go through `apply_scores.py --write`, which
only the operator triggers).

## Opening

1. `python3 scripts/thesis/answer.py --list` — the open questions, grouped by ticker.
2. Read the latest `notes/reports/thesis-delta-*.md` (most recent file) for context; mention the
   top three movers in one line each.
3. Ask which ticker to start with, or walk in file order if the operator says "go".

## Per question

- **draft_review** (`draft:{T}:{id}`): show the assumption statement, `derived_from`, `challenged_by`
  / `confirmed_by`, and the evidence rows for that assumption id from `state/thesis/evidence_log.jsonl`
  (filter `ticker`, `assumption_id`; show date, source, direction/strength, why, ref; newest first,
  at most 6). Offer: keep as written / edit the statement / retire / mark confirmed / mark challenged.
  Record with `--action keep|edit|retire|confirm|challenge` (`--text` for edit).
- **stale** (`stale:{T}:{id}`): show the statement and days since last evidence. Offer retire / keep.
- **score_proposal** (`score:{T}:{key}`): show proposed vs applied, the source note path, and the
  note's section 5/6/7 lines that carry the recommendation. Offer accept / reject. `accept` prints
  the `apply_scores.py` command; run it WITHOUT `--write` first, show the diff, and run `--write`
  only when the operator confirms in this conversation.

After each answer, echo the `answer.py` output line so the operator sees exactly what changed.

## Ad-hoc questions

"What is the thesis on X?" → read `notes/X/_thesis.md` (frontmatter + body) and summarize the
assumptions with their status, pressure and last evidence date. "What changed on X since <date>?" →
filter `state/thesis/changes.jsonl` and `evidence_log.jsonl` by ticker and date. "Why is X ranked
there?" → `state/thesis/ranking_{latest}.json` row for X (delta, why, proposed vs applied scores).

## Closing

Print the count answered / remaining. Remind the operator that `reviewed_by_operator: true` files
are never re-drafted by `draft_thesis.py --missing-only`, and that `--force` preserves anything
with `draft: false`.
```

- [ ] **Step 4: Run tests** — `python3 scripts/thesis/test_answer.py` → `OK test_answer`; `python3 scripts/check.py` still OK (skills dir is outside its scope; confirm no new error).
- [ ] **Step 5: Commit** — `git add scripts/thesis/answer.py scripts/thesis/test_answer.py .claude/skills/thesis-chat/SKILL.md && git commit -m "thesis: answer.py + thesis-chat skill (operator decisions recorded through thesis_io, never by hand)"`

---

### Task 12: Crons, docs, memory, restore `auto_sync`

**Files:**
- Modify: live crontab (via `crontab -l | ... | crontab -`), `config/crontab.snapshot` (regenerated by `scripts/snapshot_crontab.sh`), `ARCHITECTURE.md` §4/§5/§8, `docs/cost-model.md` §2, `docs/superpowers/specs/2026-09-09-thesis-loop-design.md` (already copied), memory notes under `/root/.claude/projects/-root/memory/`.

- [ ] **Step 1: Finish the in-flight verifications from Tasks 2/4/5** — drafter ledger all `ok` (re-run `draft_thesis.py --ticker AAOI --ticker 000660.KS` for the two failures; the SK Hynix over-read may need one more attempt), matcher backfill idempotent (`match_evidence.py --ticker COHR,LITE,AAOI --since 2026-08-01` → `rows: 0`), one AMBA replay of the reviewer (Task 5 Step 5). Commit `notes/*/_thesis.md` + `state/thesis/` as "thesis: initial drafts for T1+T2 + gold backfill".

- [ ] **Step 2: Install crons** (ET box; env sourced where Brevo or claude -p is needed; Sunday jobs spaced so no two claude -p batches overlap):

```
# thesis loop (2026-09-09)
0 15 * * *   cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh thesis_match python3 scripts/thesis/match_evidence.py >> logs/thesis_match.log 2>&1
20 6 * * *   cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh thesis_alerts_am python3 scripts/thesis/thesis_report.py --alerts >> logs/thesis_report.log 2>&1
45 15 * * *  cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh thesis_alerts_pm python3 scripts/thesis/thesis_report.py --alerts >> logs/thesis_report.log 2>&1
15 6 * * 1   cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh thesis_weekly python3 scripts/thesis/thesis_report.py --weekly --auto-quarterly >> logs/thesis_report.log 2>&1
0 7 * * 0    cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh thesis_draft python3 scripts/thesis/draft_thesis.py --missing-only >> logs/draft_thesis.log 2>&1
0 8 * * 0    cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh store_b_weekly python3 scripts/chunking/ingest_metrics.py --cron >> logs/store_b_weekly.log 2>&1
30 9 * * 0   cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh insider_pull python3 scripts/thesis/insider_pull.py >> logs/insider_pull.log 2>&1
```

The design's `0 9 * * 0 transcript_ingest --conferences --since-last` is NOT installed: `scripts/v3_ingest/transcript_ingest.py` has no such flags (its CLI is `--ticker/--window-months/--max-queries/...`) and belongs to the parked idea-surfacing extraction. Record as an open item in memory. Install with `crontab -l > /root/backups/crontab.pre_thesis_crons_<ts>.bak && (crontab -l; cat <lines>) | crontab -`, verify with `crontab -l | grep -c thesis_`, then `scripts/snapshot_crontab.sh`.

- [ ] **Step 3: Docs** — `ARCHITECTURE.md`: §4 add the seven cron rows; §5 add `thesis-chat` skill + the reviewer's §4b/context pre-stage; §8 close "no thesis object" and open "transcript conference feed unscheduled". `docs/cost-model.md` §2: "thesis matcher ≈ up to 90 Sonnet lean calls/day (most tickers skip), weekly report 0 calls, drafter one-off ≈ 90 + weekly `--missing-only` ≈ 0-3, Store B weekly 54 MCP calls, insider pull 4 MCP calls/week". Commit "docs: thesis loop (architecture, cost model)".

- [ ] **Step 4: Restore `auto_sync`** — `crontab -l | sed 's/^# PAUSED-BUILD-THESIS //' | crontab -`; verify `crontab -l | grep auto_sync` shows the live line; `diff <(crontab -l) /root/backups/crontab.pre_build_20260909_101534.bak` shows ONLY the seven thesis additions. Run `python3 scripts/auto_sync.py` once by hand and confirm `git status` clean and `git log origin/main -1` matches HEAD.

- [ ] **Step 5: Memory** — write `thesis_loop_complete.md` (what shipped, commit subjects, crons, the 6-K PDF finding, the transcript-conference open item, the AMBA replay outcome) and add its MEMORY.md line; update `build_workflow_pause_autosync_default.md` if anything about the pause/restore procedure changed.

## Self-review (Tasks 6–12 against the design)

- §4 report sections 1–7: Task 6 (`render`) — all seven, in order; ranking json + reports_sent + alerts_sent + notes/reports: Task 6. Quarterly edition: Task 6 `quarterly_due` (calendar-free rule replaces the InsiderScore `future_earnings_dates` trigger — deterministic and free; noted). Questions list for the chat: Task 6 `update_questions` → Task 11.
- §2b Insider transactions: Task 7. ETF flows context line + macro line: Task 6 `flows_line` / `macro_lines`. Store B weekly + consensus snapshots: Task 8. PDF exhibits: Task 9 (gate corrected to form-based). `apply_scores.py` + `check.py`: Task 10. `thesis-chat`: Task 11. Crons/docs/restore/memory: Task 12.
- Not built, recorded as open: conference-transcript weekly feed (no script CLI for it); ETF per-name "days of ADV" (only BCTK weight + 5d flow in v1).
- Type consistency: evidence row fields (`source, source_id, ref, date, title, assumption_id, direction, strength, why, quote, cross_ticker, ts, ticker`) used identically in Tasks 4/6/7; `changes.jsonl` kinds `status|proposed_score` in Tasks 4/6/7; questions ids `draft:|stale:|score:` in Tasks 6/11; `insiders_{date}.jsonl` fields `ticker, insider, txn_type, value` in Tasks 6/7; consensus snapshot keys in Tasks 6/8.
