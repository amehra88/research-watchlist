# P5 theme notes — per-theme living notes in the vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write spec §7.1's durable artifact — `notes/themes/{theme}.md`, one file per threshold-clearing theme, §7.1 frontmatter, one dated section per calendar quarter with counts, gap, stage/lag and verbatim citations — plus a per-ticker `notes/{TICKER}/_themes.md` index so wikilinks run both ways; append-only and idempotent per closed quarter, with a replace-in-place "in progress" section for the open quarter (operator decision 2026-09-10).

**Architecture:** `diffusion.build_snapshot()` gains a `pairs` list (per (theme, ticker) stage + dates) so `scripts/topics/theme_notes.py` reads `state/topics/diffusion.json` as its single source of truth, joins citations by row id to `exchanges.jsonl` / `claims.jsonl` via `topic_map.jsonl`, and writes the vault files. Cron Saturday 12:30 after diffusion (12:00). No LLM, no embedding; the system never edits `config/watchlist.yaml` or `_thesis.md`.

**Tech Stack:** Python 3.12 stdlib + pyyaml. Direct-run tests.

**Spec:** `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` §7.1, §10 (machine-appended notes risk), §11.6b. Operator decisions 2026-09-10: HYBRID open quarter (closed quarters appended once and never rewritten; the open quarter's section is labelled "in progress — as of <date>", replaced in place each run, frozen at quarter end + 14 days); ticker-side list = `notes/{TICKER}/_themes.md` (machine-owned, rewritten each run), never `_thesis.md`.

## Global Constraints

- A note is created only for a theme clearing the breadth gate in some quarter: (`n_banks >= 2 and n_companies >= 3`) or `n_disclosing >= 3` (P4 metrics; the MD&A clause is what lets stage-1 themes get a note). Measured 2026-09-10: 36 of 61 themes.
- Frontmatter (state) is rewritten every run; closed-quarter body sections are appended once and never rewritten; the open-quarter section is replaced in place. Re-running the same day changes nothing in a closed section (§11.6b).
- Quarter closed ⇔ `as_of >= quarter_end + 14 days` (grace for late transcript retrieval).
- `doc_type: theme_state` on every theme note, `doc_type: theme_index` on every `_themes.md`, so `ingest --all` (which rglobs `notes/**`) can tell them from source evidence.
- Wikilinks are path-suffix form: theme → ticker `[[COHR/_thesis|COHR]]`; ticker → theme `[[themes/<theme>|<theme>]]`.
- Citations are verbatim from the source rows: analyst questions carry speaker, firm, event date, event name; MD&A excerpts carry form type and filed date. Max 3 questions + 2 MD&A excerpts per quarter section, highest cosine first, distinct tickers preferred.
- `status: approved` (every anchored theme is an operator-named watchlist theme; candidate clusters have no metrics and get no note).
- Theme stage = earliest stage among the `affects` holdings that carry the theme; if no affected holding carries it, earliest stage among all its tickers.
- Build hygiene: auto_sync paused (`/root/backups/crontab.pre_build_20260910_2041.bak`, line tagged `#PAUSED-P5`); restore LAST.

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/topics/diffusion.py` | + `pairs` in `build_snapshot()` |
| `scripts/topics/theme_notes.py` | `quarter_end`, `is_closed`, `clears_gate`, `theme_state`, `citations_for`, `render_frontmatter`, `render_section`, `upsert_note`, `write_ticker_index`, CLI `--run [--as-of] [--dry-run]` |
| `scripts/topics/test_theme_notes.py` | direct-run tests |
| `notes/themes/{theme}.md`, `notes/{TICKER}/_themes.md` | vault outputs (committed by auto_sync) |

Snapshot fields consumed: `metrics[]` (theme, cal_quarter, n_banks, banks, n_companies, companies, n_exchanges, n_disclosing, disclosing, n_corprep_companies), `denominators{cq: {earnings_call, conference, mdna_filers}}`, `quarters`, `current_quarter`, `pairs[]` (new).

---

### Task 1: `pairs` in the diffusion snapshot

**Files:** Modify `scripts/topics/diffusion.py` (`build_snapshot`), `scripts/topics/test_diffusion.py`.

**Interfaces:** Produces `snap["pairs"]: list[{theme, ticker, stage, first_evidence_date, first_filing_date, first_question_date, lag_days, n_evidence, n_question, banks: [..]}]` sorted by (theme, ticker). `lag_days = lc.lag_days(first_filing_date, first_question_date)` (may be negative or None).

- [ ] **Step 1: Failing test** (append to `test_diffusion.py`)

```python
def test_snapshot_pairs_carry_stage_and_dates_per_theme_ticker():
    rows = [_r("c1", "evidence", "COHR", "2026-04-20", "CY2026-Q2", ["t1"], source="mdna"),
            _r("c2", "evidence", "COHR", "2026-04-20", "CY2026-Q2", ["t1"], source="mdna"),
            _r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"], firm="Raymond James")]
    snap = df.build_snapshot(rows, {}, {}, as_of="2026-09-10", no_coverage={})
    pairs = {(p["theme"], p["ticker"]): p for p in snap["pairs"]}
    assert pairs[("t1", "COHR")]["stage"] == 2 and pairs[("t1", "COHR")]["lag_days"] is None
    assert pairs[("t1", "AAOI")]["stage"] == 3 and pairs[("t1", "AAOI")]["banks"] == ["Raymond James"]
    assert pairs[("t1", "COHR")]["first_filing_date"] == "2026-04-20"
```

- [ ] **Step 2:** `python3 scripts/topics/test_diffusion.py` → 1 failure (`KeyError: 'pairs'`).
- [ ] **Step 3: Implement** — in `build_snapshot`, after the stage loop:

```python
    pairs = []
    for (theme, ticker), p in sorted(idx.items()):
        pairs.append({"theme": theme, "ticker": ticker, "stage": lc.stage(idx, theme, ticker),
                      "first_evidence_date": p["first_evidence_date"], "first_filing_date": p["first_filing_date"],
                      "first_question_date": p["first_question_date"],
                      "lag_days": lc.lag_days(p["first_filing_date"], p["first_question_date"]),
                      "n_evidence": p["n_evidence"], "n_question": p["n_question"], "banks": sorted(p["banks"])})
```
and add `"pairs": pairs` to the returned dict.

- [ ] **Step 4:** tests 14/14. Re-run `python3 scripts/topics/diffusion.py --run` (0 new detections) so `diffusion.json` carries `pairs`.
- [ ] **Step 5:** `git add scripts/topics/diffusion.py scripts/topics/test_diffusion.py state/topics/diffusion.json && git commit -m "topics: diffusion snapshot carries per-(theme, ticker) pairs for the theme-note writer"`

### Task 2: `theme_notes.py` — state, gate, rendering, idempotent upsert

**Files:** Create `scripts/topics/theme_notes.py`, `scripts/topics/test_theme_notes.py`.

**Interfaces:**
- `quarter_end(cq: str) -> dt.date`; `is_closed(cq, as_of: str, grace_days=GRACE_DAYS) -> bool`.
- `clears_gate(cells: list[dict]) -> bool` (cells = this theme's metrics rows).
- `theme_state(theme, snap, affects_map: dict[str, list[str]]) -> dict` → `{theme, status, stage, tickers, affects, first_evidence_date, first_question_date, lag_days, stages_by_ticker}`. `affects_map` = T1 ticker → its watchlist `themes` list.
- `citations_for(theme, cq, rows, ex_meta, claims, max_q=3, max_m=2) -> dict{questions: [...], mdna: [...]}`.
- `render_frontmatter(state, as_of) -> str`; `render_section(theme, cq, snap, cites, as_of, closed: bool) -> str` — heading `## CY2026-Q2` when closed, `## CY2026-Q3 — in progress (as of 2026-09-10)` when open.
- `upsert_note(path, fm_text, sections: list[(cq, text, closed)]) -> dict{created, appended: [cq], replaced: [cq], unchanged: [cq]}`.
- `write_ticker_index(ticker, entries, path) -> bool`.
- Constants: `THEMES_DIR = REPO/"notes"/"themes"`, `GRACE_DAYS = 14`, `SECTION_RE = re.compile(r"^## (CY\d{4}-Q[1-4])(?P<open> — in progress.*)?$", re.M)`.

- [ ] **Step 1: Failing tests**

```python
#!/usr/bin/env python3
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme_notes as tn


def _cell(theme, cq, banks=0, companies=0, disclosing=0, corprep=0):
    return {"theme": theme, "cal_quarter": cq, "n_banks": banks, "banks": [f"B{i}" for i in range(banks)],
            "n_companies": companies, "companies": [f"C{i}" for i in range(companies)], "n_exchanges": banks + companies,
            "n_disclosing": disclosing, "disclosing": [f"D{i}" for i in range(disclosing)], "n_corprep_companies": corprep,
            "first_seen_quarter": cq}


def _pair(theme, ticker, stage, fe=None, ff=None, fq=None, lag=None):
    return {"theme": theme, "ticker": ticker, "stage": stage, "first_evidence_date": fe, "first_filing_date": ff,
            "first_question_date": fq, "lag_days": lag, "n_evidence": 1, "n_question": 1 if fq else 0, "banks": []}


SNAP = {"as_of": "2026-09-10", "quarters": ["CY2026-Q1", "CY2026-Q2", "CY2026-Q3"], "current_quarter": "CY2026-Q3",
        "denominators": {"CY2026-Q1": {"earnings_call": 40, "conference": 20, "mdna_filers": 60},
                         "CY2026-Q2": {"earnings_call": 43, "conference": 23, "mdna_filers": 69},
                         "CY2026-Q3": {"earnings_call": 45, "conference": 29, "mdna_filers": 67}},
        "no_coverage": {"no_results": ["ADI"], "incomplete": ["innolight.cn"], "no_factset_id": []},
        "metrics": [_cell("t1", "CY2026-Q2", banks=1, companies=1, disclosing=3), _cell("t1", "CY2026-Q3", banks=3, companies=4),
                    _cell("t2", "CY2026-Q3", banks=1, companies=2)],
        "pairs": [_pair("t1", "COHR", 2, fe="2026-04-20", ff="2026-04-20"), _pair("t1", "AAOI", 3, fq="2026-08-06"),
                  _pair("t1", "LITE", 2, fe="2026-05-01", ff="2026-05-01"), _pair("t2", "NVDA", 3, fq="2026-08-01")]}


def test_quarter_closes_fourteen_days_after_its_end():
    assert tn.quarter_end("CY2026-Q2").isoformat() == "2026-06-30"
    assert tn.is_closed("CY2026-Q2", "2026-07-14") and not tn.is_closed("CY2026-Q2", "2026-07-13")
    assert not tn.is_closed("CY2026-Q3", "2026-09-10")


def test_gate_needs_breadth_on_either_register():
    assert tn.clears_gate([_cell("t", "q", banks=2, companies=3)])
    assert tn.clears_gate([_cell("t", "q", disclosing=3)])
    assert not tn.clears_gate([_cell("t", "q", banks=2, companies=2), _cell("t", "q2", disclosing=2)])


def test_theme_state_takes_the_earliest_stage_among_affected_holdings():
    st = tn.theme_state("t1", SNAP, {"COHR": ["t1"], "LITE": ["t1"], "NVDA": ["t2"]})
    assert st["stage"] == 2 and st["affects"] == ["COHR", "LITE"] and st["tickers"] == ["AAOI", "COHR", "LITE"]
    assert st["first_evidence_date"] == "2026-04-20" and st["first_question_date"] == "2026-08-06"
    assert st["lag_days"] == 108 and st["status"] == "approved"
    st2 = tn.theme_state("t2", SNAP, {})            # no affected holding: fall back to all tickers
    assert st2["stage"] == 3 and st2["affects"] == []


def test_frontmatter_matches_spec_7_1():
    st = tn.theme_state("t1", SNAP, {"COHR": ["t1"]})
    fm = tn.render_frontmatter(st, "2026-09-10")
    import yaml
    d = yaml.safe_load(fm.strip("-\n"))
    assert d["doc_type"] == "theme_state" and d["theme"] == "t1" and d["stage"] == 2
    assert d["tickers"] == ["AAOI", "COHR", "LITE"] and d["affects"] == ["COHR"]
    assert d["first_evidence_date"] == "2026-04-20" and d["lag_days"] == 108 and d["updated"] == "2026-09-10"


def test_section_prints_counts_denominators_gap_and_citations():
    cites = {"questions": [{"ticker": "AAOI", "date": "2026-08-06", "speaker": "Simon Leopold", "firm": "Raymond James",
                            "event": "Q2 2026 Earnings Call", "text": "What's it like competitively?"}],
             "mdna": [{"ticker": "COHR", "date": "2026-04-20", "form": "10-Q", "text": "Capacity additions in China..."}]}
    s = tn.render_section("t1", "CY2026-Q3", SNAP, cites, "2026-09-10", closed=False)
    assert s.startswith("## CY2026-Q3 — in progress (as of 2026-09-10)")
    assert "3 banks" in s and "4 of 45 earnings-call" in s and "29 conference" in s
    assert "[[COHR/_thesis|COHR]]" in s and "Simon Leopold" in s and "Raymond James" in s and "10-Q" in s
    c = tn.render_section("t1", "CY2026-Q2", SNAP, {"questions": [], "mdna": []}, "2026-09-10", closed=True)
    assert c.startswith("## CY2026-Q2\n") and "3 disclosing" in c and "0 asked" in c


def test_upsert_appends_closed_once_replaces_open_and_rewrites_frontmatter():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t1.md"
        fm1 = "---\ndoc_type: theme_state\nstage: 2\n---\n"
        r = tn.upsert_note(p, fm1, [("CY2026-Q2", "## CY2026-Q2\nclosed v1\n", True),
                                    ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-10)\nopen v1\n", False)])
        assert r["created"] and r["appended"] == ["CY2026-Q2", "CY2026-Q3"]
        # re-run same day: nothing changes in the closed section, open section replaced with identical text
        r = tn.upsert_note(p, fm1, [("CY2026-Q2", "## CY2026-Q2\nclosed v2 MUST NOT LAND\n", True),
                                    ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-10)\nopen v1\n", False)])
        t = p.read_text()
        assert r["unchanged"] == ["CY2026-Q2", "CY2026-Q3"] and "closed v1" in t and "MUST NOT LAND" not in t
        # next week: frontmatter rewritten, open section replaced, closed untouched
        r = tn.upsert_note(p, "---\ndoc_type: theme_state\nstage: 3\n---\n",
                           [("CY2026-Q2", "## CY2026-Q2\nclosed v3\n", True),
                            ("CY2026-Q3", "## CY2026-Q3 — in progress (as of 2026-09-17)\nopen v2\n", False)])
        t = p.read_text()
        assert r["replaced"] == ["CY2026-Q3"] and "stage: 3" in t and "closed v1" in t and "open v2" in t and "open v1" not in t
        assert t.count("## CY2026-Q3") == 1 and t.count("## CY2026-Q2") == 1
        # quarter closes: the open section is replaced by the frozen one, then never again
        r = tn.upsert_note(p, fm1, [("CY2026-Q3", "## CY2026-Q3\nfrozen\n", True)])
        t = p.read_text()
        assert r["replaced"] == ["CY2026-Q3"] and "frozen" in t and "in progress" not in t
        r = tn.upsert_note(p, fm1, [("CY2026-Q3", "## CY2026-Q3\nfrozen AGAIN\n", True)])
        assert r["unchanged"] == ["CY2026-Q3"] and "AGAIN" not in p.read_text()


def test_ticker_index_links_to_theme_notes_and_is_rewritten():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "_themes.md"
        assert tn.write_ticker_index("COHR", [{"theme": "t1", "stage": 2, "lag_days": None, "open_lag_days": 143}], p)
        t = p.read_text()
        assert "doc_type: theme_index" in t and "[[themes/t1|t1]]" in t and "stage 2" in t
        assert not tn.write_ticker_index("COHR", [{"theme": "t1", "stage": 2, "lag_days": None, "open_lag_days": 143}], p)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1; print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass"); sys.exit(1 if failed else 0)
```

- [ ] **Step 2:** run → `ModuleNotFoundError`.
- [ ] **Step 3: Implement `theme_notes.py`** (full module; the CLI `run()` is Task 3):

```python
#!/usr/bin/env python3
"""P5 theme notes (spec §7.1): one living note per threshold-clearing theme in the operator's
vault, plus a per-ticker index so wikilinks run both ways.

Machine-appended files inside notes/ — a first for this repo (spec §10). Rules that make that
safe: frontmatter is STATE and is rewritten every run; closed-quarter sections are HISTORY and
are appended once and never rewritten; the open quarter's section is labelled "in progress"
and replaced in place until the quarter closes (quarter end + 14 days). Re-running the same
day changes nothing. The system never edits config/watchlist.yaml or notes/{T}/_thesis.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lifecycle as lc  # noqa: E402

REPO = Path("/root/research-watchlist")
STATE = REPO / "state" / "topics"
DIFFUSION = STATE / "diffusion.json"
TOPIC_MAP = STATE / "topic_map.jsonl"
EXCHANGES = REPO / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS = REPO / "state" / "evidence" / "claims.jsonl"
WATCHLIST = REPO / "config" / "watchlist.yaml"
NOTES = REPO / "notes"
THEMES_DIR = NOTES / "themes"

GRACE_DAYS = 14
MIN_BANKS, MIN_COMPANIES, MIN_DISCLOSING = 2, 3, 3
MAX_Q, MAX_M = 3, 2
SECTION_RE = re.compile(r"^## (CY\d{4}-Q[1-4])(?P<open> — in progress.*)?$", re.M)
FM_RE = re.compile(r"\A---\n.*?\n---\n", re.S)


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] theme_notes: {msg}", flush=True)


# ───────────────────────── quarters and gate ─────────────────────────

def quarter_end(cq: str) -> dt.date:
    y, q = int(cq[2:6]), int(cq[-1])
    m = q * 3
    nxt = dt.date(y + (m == 12), (m % 12) + 1, 1)
    return nxt - dt.timedelta(days=1)


def is_closed(cq: str, as_of: str, grace_days: int = GRACE_DAYS) -> bool:
    return dt.date.fromisoformat(as_of) >= quarter_end(cq) + dt.timedelta(days=grace_days)


def clears_gate(cells: list) -> bool:
    return any((c["n_banks"] >= MIN_BANKS and c["n_companies"] >= MIN_COMPANIES) or c["n_disclosing"] >= MIN_DISCLOSING
               for c in cells)


# ───────────────────────── state ─────────────────────────

def theme_state(theme: str, snap: dict, affects_map: dict) -> dict:
    pairs = [p for p in snap["pairs"] if p["theme"] == theme]
    tickers = sorted({p["ticker"] for p in pairs})
    affects = sorted(t for t, ths in affects_map.items() if theme in ths)
    carrying = [p for p in pairs if p["ticker"] in affects] or pairs
    stages = [p["stage"] for p in carrying if p["stage"]]
    fe = min((p["first_evidence_date"] for p in pairs if p["first_evidence_date"]), default=None)
    ff = min((p["first_filing_date"] for p in pairs if p["first_filing_date"]), default=None)
    fq = min((p["first_question_date"] for p in pairs if p["first_question_date"]), default=None)
    return {"theme": theme, "status": "approved", "stage": min(stages) if stages else None,
            "tickers": tickers, "affects": affects, "first_evidence_date": fe, "first_question_date": fq,
            "lag_days": lc.lag_days(ff, fq), "stages_by_ticker": {p["ticker"]: p["stage"] for p in pairs}}


def render_frontmatter(st: dict, as_of: str) -> str:
    d = {"doc_type": "theme_state", "theme": st["theme"], "status": st["status"], "stage": st["stage"],
         "tickers": st["tickers"], "affects": st["affects"], "first_evidence_date": st["first_evidence_date"],
         "first_question_date": st["first_question_date"], "lag_days": st["lag_days"], "updated": as_of,
         "written_by": "scripts/topics/theme_notes.py"}
    return "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) + "---\n"


# ───────────────────────── citations ─────────────────────────

def load_sources(topic_map=TOPIC_MAP, exchanges=EXCHANGES, claims=CLAIMS):
    rows = [json.loads(l) for l in topic_map.read_text(encoding="utf-8").splitlines() if l.strip()]
    ex, cl = {}, {}
    for l in exchanges.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        if r.get("vector_id"):
            ex[r["vector_id"]] = r
    if claims.exists():
        for l in claims.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            cl[r["claim_id"]] = r
    return rows, ex, cl


def _score(r, theme):
    return max((t["score"] for t in r.get("themes") or [] if t.get("theme") == theme), default=0.0)


def citations_for(theme, cq, rows, ex, cl, max_q=MAX_Q, max_m=MAX_M) -> dict:
    """Highest-cosine rows first, one per ticker before a second from any ticker."""
    def pick(cands, n):
        cands.sort(key=lambda r: -_score(r, theme))
        out, seen = [], set()
        for r in cands:
            if r["ticker"] not in seen:
                out.append(r); seen.add(r["ticker"])
            if len(out) == n:
                return out
        for r in cands:
            if r not in out:
                out.append(r)
            if len(out) == n:
                break
        return out
    qs = [r for r in rows if r["cal_quarter"] == cq and r["register"] == "question" and _score(r, theme) > 0 and r["id"] in ex]
    ms = [r for r in rows if r["cal_quarter"] == cq and r["source"] == "mdna" and _score(r, theme) > 0 and r["id"] in cl]
    questions = [{"ticker": r["ticker"], "date": r["event_date"], "speaker": ex[r["id"]].get("speaker_name") or "analyst",
                  "firm": ex[r["id"]].get("speaker_firm") or "?", "event": ex[r["id"]].get("event_name") or r["event_type"],
                  "text": (ex[r["id"]].get("text") or "").strip()} for r in pick(qs, max_q)]
    mdna = [{"ticker": r["ticker"], "date": r["event_date"], "form": r["event_type"],
             "text": (cl[r["id"]].get("text") or "").strip()} for r in pick(ms, max_m)]
    return {"questions": questions, "mdna": mdna}


# ───────────────────────── rendering ─────────────────────────

def _tick(t: str) -> str:
    return f"[[{t}/_thesis|{t}]]"


def _clip(s: str, n: int = 600) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"


def render_section(theme, cq, snap, cites, as_of, closed: bool) -> str:
    cell = next((c for c in snap["metrics"] if c["theme"] == theme and c["cal_quarter"] == cq), None) or {
        "n_banks": 0, "banks": [], "n_companies": 0, "companies": [], "n_exchanges": 0, "n_disclosing": 0,
        "disclosing": [], "n_corprep_companies": 0}
    den = snap["denominators"].get(cq, {})
    head = f"## {cq}" if closed else f"## {cq} — in progress (as of {as_of})"
    L = [head, ""]
    L.append(f"**Asked:** {cell['n_banks']} banks, {cell['n_companies']} of {den.get('earnings_call', 0)} earnings-call / "
             f"{den.get('conference', 0)} conference companies covered, {cell['n_exchanges']} exchanges"
             + (f" — {', '.join(_tick(t) for t in cell['companies'])}" if cell["companies"] else "") + ".")
    L.append(f"**Disclosed (MD&A):** {cell['n_disclosing']} of {den.get('mdna_filers', 0)} filers"
             + (f" — {', '.join(_tick(t) for t in cell['disclosing'])}" if cell["disclosing"] else "")
             + f"; corprep speech at {cell['n_corprep_companies']} companies.")
    L.append(f"**Gap (§6.2):** {cell['n_disclosing']} disclosing / {cell['n_companies']} asked.")
    if cell["banks"]:
        L.append(f"**Banks:** {', '.join(cell['banks'])}.")
    nc = snap.get("no_coverage") or {}
    excl = (nc.get("no_results") or []) + (nc.get("incomplete") or [])
    if excl:
        L.append(f"_Not covered this quarter: {', '.join(excl[:12])}{' …' if len(excl) > 12 else ''}._")
    L.append("")
    if cites.get("questions"):
        L.append("**Analyst questions (verbatim):**")
        for q in cites["questions"]:
            L.append(f"- {_tick(q['ticker'])} {q['date']} — {q['speaker']} ({q['firm']}), {q['event']}: “{_clip(q['text'])}”")
        L.append("")
    if cites.get("mdna"):
        L.append("**MD&A (added this quarter, lower-confidence mapping):**")
        for m in cites["mdna"]:
            L.append(f"- {_tick(m['ticker'])} {m['form']} filed {m['date']}: “{_clip(m['text'])}”")
        L.append("")
    return "\n".join(L) + "\n"


# ───────────────────────── idempotent upsert ─────────────────────────

def _split_sections(body: str) -> tuple:
    """-> (preamble, [(cq, text, open?)]) in file order."""
    ms = list(SECTION_RE.finditer(body))
    if not ms:
        return body, []
    pre = body[:ms[0].start()]
    secs = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(body)
        secs.append((m.group(1), body[m.start():end], bool(m.group("open"))))
    return pre, secs


def upsert_note(path: Path, fm_text: str, sections: list) -> dict:
    """sections = [(cq, text, closed)]. Closed sections are appended once (an existing closed
    section for that quarter is never touched); an open section replaces an existing open
    section for the same quarter; a closed section replaces an existing OPEN one (freeze)."""
    path = Path(path)
    res = {"created": not path.exists(), "appended": [], "replaced": [], "unchanged": []}
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    body = FM_RE.sub("", old, count=1)
    pre, secs = _split_sections(body)
    have = {cq: (text, is_open) for cq, text, is_open in secs}
    order = [cq for cq, _, _ in secs]
    for cq, text, closed in sections:
        if cq not in have:
            have[cq] = (text, not closed); order.append(cq); res["appended"].append(cq)
        else:
            cur_text, cur_open = have[cq]
            if not cur_open:
                res["unchanged"].append(cq)                    # frozen history
            elif cur_text == text:
                res["unchanged"].append(cq)
            else:
                have[cq] = (text, not closed); res["replaced"].append(cq)
    order.sort()                                                # chronological
    new = fm_text + pre + "".join(have[cq][0] for cq in order)
    if new != old:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
    return res


def write_ticker_index(ticker: str, entries: list, path: Path) -> bool:
    """notes/{T}/_themes.md — machine-owned, rewritten; -> True if the file changed."""
    entries = sorted(entries, key=lambda e: (e["stage"] or 9, e["theme"]))
    L = ["---", "doc_type: theme_index", f"ticker: {ticker}", "written_by: scripts/topics/theme_notes.py", "---", "",
         f"# {ticker} — themes", "", "Themes where this name has been asked or has disclosed (spec §7.1). Machine-written; "
         "edit the theme notes' operator sections, not this index.", ""]
    for e in entries:
        lag = (f"lag {e['lag_days']}d" if e.get("lag_days") is not None
               else (f"open {e['open_lag_days']}d" if e.get("open_lag_days") is not None else ""))
        L.append(f"- [[themes/{e['theme']}|{e['theme']}]] — stage {e['stage']}{(' · ' + lag) if lag else ''}")
    new = "\n".join(L) + "\n"
    path = Path(path)
    if path.exists() and path.read_text(encoding="utf-8") == new:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new, encoding="utf-8")
    return True
```

- [ ] **Step 4:** `python3 scripts/topics/test_theme_notes.py` → 7/7.
- [ ] **Step 5:** `git add scripts/topics/theme_notes.py scripts/topics/test_theme_notes.py && git commit -m "topics: theme_notes — §7.1 state/gate/rendering and the idempotent closed/open-quarter upsert"`

### Task 3: CLI, real run, §11.6b verification

**Files:** Modify `scripts/topics/theme_notes.py` (append `affects_map`, `run`, `main`).

- [ ] **Step 1: Implement**

```python
def affects_map(watchlist_path: Path = WATCHLIST) -> dict:
    wl = yaml.safe_load(watchlist_path.read_text()) or {}
    return {e["ticker"]: list(e.get("themes") or []) for e in (wl.get("tier_1_bctk") or []) if e.get("ticker")}


def run(args) -> int:
    snap = json.loads(DIFFUSION.read_text())
    if "pairs" not in snap:
        log("diffusion.json has no pairs — re-run diffusion.py --run"); return 2
    as_of = args.as_of
    rows, ex, cl = load_sources()
    amap = affects_map()
    themes = sorted({c["theme"] for c in snap["metrics"]})
    gated = [t for t in themes if clears_gate([c for c in snap["metrics"] if c["theme"] == t])]
    log(f"{len(themes)} themes with metrics, {len(gated)} clear the gate (banks>={MIN_BANKS}&companies>={MIN_COMPANIES} "
        f"or disclosing>={MIN_DISCLOSING}); quarters {snap['quarters']}")
    by_ticker: dict = {}
    n_created = n_changed = 0
    for theme in gated:
        st = theme_state(theme, snap, amap)
        secs = []
        for cq in snap["quarters"]:
            if not any(c["theme"] == theme and c["cal_quarter"] == cq for c in snap["metrics"]):
                continue
            closed = is_closed(cq, as_of)
            secs.append((cq, render_section(theme, cq, snap, citations_for(theme, cq, rows, ex, cl), as_of, closed), closed))
        path = THEMES_DIR / f"{theme}.md"
        if args.dry_run:
            log(f"  would write {path.name}: stage {st['stage']}, {len(secs)} sections, tickers {len(st['tickers'])}")
        else:
            r = upsert_note(path, render_frontmatter(st, as_of), secs)
            n_created += r["created"]; n_changed += bool(r["appended"] or r["replaced"])
            if r["appended"] or r["replaced"]:
                log(f"  {path.name}: +{r['appended']} ~{r['replaced']}")
        for p in snap["pairs"]:
            if p["theme"] == theme:
                open_lag = lc.open_lag_days(p, as_of)
                by_ticker.setdefault(p["ticker"], []).append({"theme": theme, "stage": p["stage"], "lag_days": p["lag_days"],
                                                             "open_lag_days": open_lag})
    n_idx = 0
    if not args.dry_run:
        for ticker, entries in by_ticker.items():
            if (NOTES / ticker).is_dir():                       # only names that already have a vault folder
                n_idx += write_ticker_index(ticker, entries, NOTES / ticker / "_themes.md")
    log(f"theme notes: {len(gated)} gated, {n_created} created, {n_changed} changed; ticker indexes changed: {n_idx}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P5 theme notes (spec §7.1)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.run:
        return run(a)
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Dry run** — `python3 scripts/topics/theme_notes.py --run --dry-run` → 36 gated (matches the measurement), no files written (`ls notes/themes` → missing).
- [ ] **Step 3: Real run** — `python3 scripts/topics/theme_notes.py --run`; then verify §11.6b:
  - `ls notes/themes | wc -l` = number gated; every file's frontmatter parses (`python3 -c` loop with yaml) and has the §7.1 keys;
  - links both ways: a theme note names `[[COHR/_thesis|COHR]]` and `notes/COHR/_themes.md` names `[[themes/<theme>|…]]`;
  - `md5sum notes/themes/*.md > /tmp/a; python3 scripts/topics/theme_notes.py --run; md5sum notes/themes/*.md > /tmp/b; diff /tmp/a /tmp/b` → empty (re-run appends nothing);
  - read one note end to end (e.g. `hyperscaler_revenue_concentration.md`) and judge the citations.
- [ ] **Step 4: Commit** — `git add scripts/topics/theme_notes.py notes/themes notes/*/_themes.md && git commit -m "topics: P5 theme notes live — <n> theme notes + <m> ticker indexes (first run)"`

### Task 4: cron, docs, memory, restore auto_sync

- [ ] **Step 1: Cron** — `(crontab -l; echo '30 12 * * 6 cd /root/research-watchlist && /root/bin/alert_on_failure.sh theme_notes python3 scripts/topics/theme_notes.py --run >> logs/theme_notes.log 2>&1') | crontab -`; verify.
- [ ] **Step 2: Spec status** — `P4 built 2026-09-10 (...)` → append `; P5 theme notes built 2026-09-10 (plan docs/superpowers/plans/2026-09-10-theme-notes-p5.md; hybrid open quarter, _themes.md ticker index)` and change `P3/P5/P5b open` → `P3/P5b (alert) and the §7.2 quarterly digest open`.
- [ ] **Step 3: ARCHITECTURE.md §8** — in the P4 sentence's "Open:" list replace `P5 vault theme notes` with `P5 theme notes built 2026-09-10 (scripts/topics/theme_notes.py, cron Sat 12:30, notes/themes/*.md + notes/{T}/_themes.md; closed quarters append-only, open quarter replaced in place)`.
- [ ] **Step 4:** `crontab -l > config/crontab.snapshot; git add docs ARCHITECTURE.md config/crontab.snapshot; git commit -m "docs+cron: P5 theme notes live (Sat 12:30)"; git push origin main`.
- [ ] **Step 5: Memory** — `/root/.claude/projects/-root/memory/theme_notes_p5.md` + MEMORY.md line + resume_here.md (next = P5b alert or P3).
- [ ] **Step 6: Restore auto_sync LAST** — `crontab -l | sed 's#^\#PAUSED-P5 ##' | crontab -`; verify; orphan scan.

---

## Self-review

- **Spec coverage:** §7.1 frontmatter keys → `render_frontmatter`; one dated section per quarter with §5 counts, §6.2 gap, §6.3 stage/lag, verbatim citations with speaker/firm/date → `render_section` + `citations_for`; wikilinks both ways → `_tick()` + `write_ticker_index`; creation gate → `clears_gate`; append-only + idempotent per quarter → `upsert_note` (§11.6b test in Task 3 step 3); `status: candidate` case → not applicable (only anchored operator themes have metrics), stated in constraints; §10 risk (Auto-sync commits within 15 min, iPad pull-only) → unchanged behaviour, noted in module docstring.
- **Placeholders:** none.
- **Type consistency:** `snap["pairs"]` fields (Task 1) match `theme_state`/`run` consumers; `upsert_note` sections tuple `(cq, text, closed)` matches `run`; `write_ticker_index` entries carry `theme, stage, lag_days, open_lag_days` as built in `run`.
