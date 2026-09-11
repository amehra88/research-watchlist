# P4 diffusion — metrics, detectors, lifecycle staging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the P2/P3b topic map into the spec's answer — per-theme breadth counts with their denominators (§5), the disclosure-vs-question gap (§6.2), the asked-elsewhere detector over verified adjacency (§6.1), lifecycle stage + lag with an append-only first-seen detection log (§6.3), and the findings' "newly said" signal (R4/R5) — rendered as a weekly markdown report + email.

**Architecture:** Three new modules under `scripts/topics/`: `adjacency.py` (verified ticker graph), `lifecycle.py` (ported from branch `worktree-idea-surfacing-spec`, adapted to the live `topic_map.jsonl` row shape, staleness guard instead of the branch's extraction-progress guard), and `diffusion.py` (metrics, denominators, host-firm exclusion, newly-said, movers, report, CLI). Reads `state/topics/topic_map.jsonl` + `state/transcripts/exchanges.jsonl` (for host_hint / citations); writes `state/topics/diffusion.json`, `state/topics/detections.jsonl`, `notes/reports/theme-diffusion.md`. No LLM, no embedding, no vault writes, never edits `config/watchlist.yaml`.

**Tech Stack:** Python 3.12 stdlib + pyyaml. Direct-run tests (no pytest in this env). Email via `scripts/newsdigest/email_send.send` (Brevo; cron sources `/root/podcasts/.env`).

**Spec:** `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` §5, §6.1–6.3, §7.2 (report shape only; vault notes = P5), §10 (host-firm exclusion), §11.3/11.5/11.5c. Findings: `docs/superpowers/plans/2026-08-21-topic-space-findings.md` R4/R5. Operator decisions 2026-09-10: **P4 only** (no vault theme notes, no daily alert), **verified adjacency only** (manual supply-chain edges + `ingest_comparables.informs` + `tier_4_ecosystem.affects`; the 8,756 FactSet-extracted edges are NOT used).

## Global Constraints

- Metrics are per `(theme, cal_quarter)` — `cal_quarter` from the row (calendar; `period_key` is fiscal on ~53% and must never be the join key).
- Weighting: `n_banks` > `n_companies` > `n_exchanges` (spec §5). No velocity, slope, smoothing, or trend lines — ever. Prior-quarter figures printed alongside.
- Every printed figure carries its denominator (per event type, never merged) and the exclusions list (`state/transcripts/_no_coverage.json`).
- Host firm excluded from `n_banks` at its own conference (spec §10). Still counted in `n_companies` / `n_exchanges`.
- MD&A: a `(filer, theme, quarter)` counts as disclosing only with ≥ 2 mapped blocks; mdna counts are labelled lower-confidence (memory `mdna-evidence-p3b`).
- Only approved themes (rows with non-empty `themes`) enter metrics; candidate clusters never do.
- `detections.jsonl` is append-only, first-seen wins, and is refused when the map is stale (older than its inputs) or missing a source.
- Negative lags (question before evidence) are kept — they are the counter-evidence.
- `challenging_rate` (§5) is DROPPED: exchange rows carry no challenging flag and 99% of analyst turns are sentiment=Neutral. Say so in the report header.
- P3 foreign evidence does not exist: the China-laser gold test (§11.2) is computed from US evidence only; the report states it.
- Build hygiene: orphan scan first; pause auto_sync (backup crontab to `/root/backups/crontab.pre_build_<ts>.bak`, comment the `*/15 auto_sync` line); restore it LAST, after the final state commit.

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/topics/adjacency.py` | `build_adjacency(manual_edges, comparables, tier4)` → `{ticker: {neighbor: [route,...]}}`; `load_adjacency()` reads the three sources |
| `scripts/topics/lifecycle.py` | `build_index(rows)`, `stage()`, `lag_days()`, `open_lag_days()`, `summarize()`, `append_detections()`, `map_is_fresh()` |
| `scripts/topics/diffusion.py` | `load_rows`, `load_exchange_meta`, `is_host_firm`, `metrics`, `denominators`, `newly_said`, `movers`, `detector_asked_elsewhere`, `write_report`, CLI `--run [--email] [--as-of] [--no-log]` |
| `scripts/topics/test_adjacency.py`, `test_lifecycle.py`, `test_diffusion.py` | direct-run tests (same runner pattern as `test_topic_map.py`) |
| `state/topics/diffusion.json` | committed snapshot: metrics + stages + newly-said (small) |
| `state/topics/detections.jsonl` | committed, append-only |
| `notes/reports/theme-diffusion.md` | weekly report |

Row shape consumed (from `topic_map.jsonl`, 17,116 rows on 2026-09-10):
`{id, register: question|evidence, ticker, event_type, event_date, period_key, firm, source: exchange|mdna, cal_quarter, threshold, themes: [{theme, score}], best, candidate}`. For `source == "exchange"`, `id` is the `vector_id` in `exchanges.jsonl` (which carries `host_hint`, `speaker_name`, `speaker_firm`, `event_name`, `text`).

---

### Task 0: Build hygiene

- [x] **Step 1:** `pgrep -af "claude -p|ingest|topic_map|mdna|diffusion" | grep -v pgrep` → expect nothing.
- [x] **Step 2:** `ts=$(date +%Y%m%d_%H%M); crontab -l > /root/backups/crontab.pre_build_$ts.bak && crontab -l | sed 's#^\(\*/15 \* \* \* \* .*auto_sync.*\)$#\#PAUSED-P4 \1#' | crontab - && crontab -l | grep -n auto_sync` → the line shows `#PAUSED-P4`.

### Task 1: `adjacency.py` — the verified ticker graph

**Files:** Create `scripts/topics/adjacency.py`, `scripts/topics/test_adjacency.py`.

**Interfaces:**
- Produces `build_adjacency(manual_edges: list[dict], comparables: list[dict], tier4: list[dict]) -> dict[str, dict[str, list[str]]]` — undirected; routes are strings like `manual:competitor`, `comparable`, `tier4:innolight.cn`. `.pvt` targets and non-ticker names are skipped.
- Produces `load_adjacency(manual_path=MANUAL, watchlist_path=WATCHLIST) -> dict` (same shape).
- Produces `MANUAL = Path("/root/research/config/supply-chain-manual.yaml")`, `WATCHLIST = REPO / "config" / "watchlist.yaml"`.

- [x] **Step 1: Failing test**

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjacency as adj


def test_manual_edges_are_undirected_and_keep_kind():
    edges = [{"source": "NVDA", "target": "CBRS", "kind": ["competitor"], "provenance": "manual"},
             {"source": "CBRS", "target": "openai.pvt", "kind": ["customer"], "provenance": "manual"},
             {"source": "DDOG", "target": "Grafana", "kind": ["competitor"], "provenance": "manual"},
             {"source": "AMD", "target": "Intel Corporation", "kind": ["competitor"], "provenance": "extracted"}]
    g = adj.build_adjacency(edges, [], [])
    assert g["NVDA"]["CBRS"] == ["manual:competitor"]
    assert g["CBRS"]["NVDA"] == ["manual:competitor"]
    assert "openai.pvt" not in g.get("CBRS", {})          # privates never enter
    assert "Grafana" not in g.get("DDOG", {})              # bare names are not tickers
    assert "AMD" not in g                                  # extracted provenance is excluded by decision


def test_comparables_and_tier4_routes():
    comps = [{"ticker": "AAOI", "informs": ["COHR", "LITE"]}]
    t4 = [{"id": "innolight.cn", "affects": ["COHR", "LITE"]}]
    g = adj.build_adjacency([], comps, t4)
    assert g["AAOI"]["COHR"] == ["comparable"] and g["COHR"]["AAOI"] == ["comparable"]
    assert g["innolight.cn"]["COHR"] == ["tier4:innolight.cn"]
    assert g["COHR"]["innolight.cn"] == ["tier4:innolight.cn"]


def test_routes_accumulate_without_duplicates():
    edges = [{"source": "AAOI", "target": "COHR", "kind": ["competitor"], "provenance": "verified"}]
    comps = [{"ticker": "AAOI", "informs": ["COHR"]}]
    g = adj.build_adjacency(edges, comps, [])
    assert g["AAOI"]["COHR"] == ["manual:competitor", "comparable"]
    g2 = adj.build_adjacency(edges + edges, comps, [])
    assert g2["AAOI"]["COHR"] == ["manual:competitor", "comparable"]


def test_load_adjacency_reads_the_real_files():
    g = adj.load_adjacency()
    assert "COHR" in g["AAOI"], "AAOI informs COHR via ingest_comparables (spec §11.3 depends on this)"
    assert all(not n.endswith(".pvt") for d in g.values() for n in d)


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

- [x] **Step 2:** `python3 scripts/topics/test_adjacency.py` → fails with `ModuleNotFoundError: adjacency`.
- [x] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""Verified ticker adjacency for Detector 1 (spec §6.1).

Three operator-vetted sources, nothing extracted: supply-chain-manual.yaml edges (provenance
manual/verified), watchlist `ingest_comparables[].informs`, and `tier_4_ecosystem[].affects`.
The 8,756 FactSet-extracted edges are excluded by operator decision 2026-09-10 — they are
unaudited and name-keyed, and a false adjacency makes stage 2 fire on noise.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path("/root/research-watchlist")
MANUAL = Path("/root/research/config/supply-chain-manual.yaml")   # sibling repo, not symlinked
WATCHLIST = REPO / "config" / "watchlist.yaml"
TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.]*$|^[a-z_]+\.(cn|tw|in|us|kr)$")   # tickers, or tier_4 ids
MANUAL_PROVENANCE = {"manual", "verified"}


def _is_node(s) -> bool:
    return bool(s) and not str(s).endswith(".pvt") and bool(TICKER_RE.match(str(s)))


def _link(g: dict, a: str, b: str, route: str) -> None:
    for x, y in ((a, b), (b, a)):
        routes = g.setdefault(x, {}).setdefault(y, [])
        if route not in routes:
            routes.append(route)


def build_adjacency(manual_edges: list, comparables: list, tier4: list) -> dict:
    g: dict = {}
    for e in manual_edges or []:
        if (e.get("provenance") or "").lower() not in MANUAL_PROVENANCE:
            continue
        s, t = e.get("source"), e.get("target")
        if _is_node(s) and _is_node(t):
            for kind in (e.get("kind") or ["related"]):
                _link(g, s, t, f"manual:{kind}")
    for c in comparables or []:
        t = c.get("ticker")
        for h in (c.get("informs") or []):
            if _is_node(t) and _is_node(h):
                _link(g, t, h, "comparable")
    for e in tier4 or []:
        cid = e.get("id")
        for h in (e.get("affects") or []):
            if _is_node(cid) and _is_node(h):
                _link(g, cid, h, f"tier4:{cid}")
    return g


def load_adjacency(manual_path: Path = MANUAL, watchlist_path: Path = WATCHLIST) -> dict:
    edges = (yaml.safe_load(manual_path.read_text()) or {}).get("edges") or [] if manual_path.exists() else []
    wl = yaml.safe_load(watchlist_path.read_text()) or {}
    return build_adjacency(edges, wl.get("ingest_comparables") or [], wl.get("tier_4_ecosystem") or [])
```

- [x] **Step 4:** `python3 scripts/topics/test_adjacency.py` → 4/4.
- [x] **Step 5:** `git add scripts/topics/adjacency.py scripts/topics/test_adjacency.py && git commit -m "topics: verified ticker adjacency for Detector 1 (manual edges + comparables + tier_4 affects)"`

### Task 2: `lifecycle.py` — port and adapt to the live row shape

**Files:** Create `scripts/topics/lifecycle.py`, `scripts/topics/test_lifecycle.py` (start from `git show worktree-idea-surfacing-spec:scripts/v3_ingest/{lifecycle,test_lifecycle}.py`).

**Interfaces:**
- Produces `build_index(rows) -> dict[(theme, ticker) -> pair]` where `pair = {theme, ticker, first_evidence_date, first_question_date, n_evidence, n_question, banks: set, evidence_sources: set}`. Each row contributes once per theme in `row["themes"]`. `register == "evidence"` rows advance `first_evidence_date` from `row["event_date"]` (mdna rows' event_date IS `first_evidence_date`; corprep exchange rows count too — spec §6.2 lists corprep speech as evidence). `register == "question"` rows advance `first_question_date` and add `firm` to `banks`.
- Produces `stage(idx, theme, ticker) -> int|None` (unchanged semantics: 1 nobody asked anywhere; 2 asked elsewhere not here; 3 asked here; 4 asked here and at ≥ `STAGE4_MIN_TICKERS` names and > half of the names carrying the theme).
- Produces `lag_days`, `open_lag_days`, `summarize`, `append_detections(path, entries, as_of, coverage_pct=None) -> int` (unchanged).
- Produces `map_is_fresh(map_path, inputs: list[Path]) -> tuple[bool, str]` — False if the map is missing, or older (mtime) than any existing input.

- [x] **Step 1: Port** — `for f in lifecycle test_lifecycle; do git show worktree-idea-surfacing-spec:scripts/v3_ingest/$f.py > scripts/topics/$f.py; done`. Then rewrite the tests' `_row` helper and the index tests to the live shape:

```python
def _row(themes, ticker, register, rid, date, firm=None, source="exchange"):
    return {"id": rid, "register": register, "ticker": ticker, "event_date": date, "firm": firm,
            "source": source, "cal_quarter": "CY2026-Q2", "event_type": "earnings_call",
            "themes": [{"theme": t, "score": 0.5} for t in (themes if isinstance(themes, list) else [themes] if themes else [])],
            "candidate": None}
```

Replace every `lc.build_index(rows, {...})` with `lc.build_index(rows)` and put the question dates on the rows. Delete `test_coverage_reads_attempted_and_total_from_the_ledger` (no `_progress.json` on this path). Add:

```python
def test_a_row_with_two_themes_feeds_both_pairs():
    rows = [_row(["t1", "t2"], "AAOI", "question", "q1", "2026-06-01", firm="Mizuho")]
    idx = lc.build_index(rows)
    assert set(idx) == {("t1", "AAOI"), ("t2", "AAOI")}
    assert idx[("t1", "AAOI")]["banks"] == {"Mizuho"}


def test_first_evidence_date_comes_from_the_row_event_date_for_both_sources():
    rows = [_row("t1", "AAOI", "evidence", "c1", "2026-05-01", source="mdna"),
            _row("t1", "AAOI", "evidence", "e1", "2026-04-01", source="exchange")]
    p = lc.build_index(rows)[("t1", "AAOI")]
    assert p["first_evidence_date"] == "2026-04-01"
    assert p["evidence_sources"] == {"mdna", "exchange"}


def test_map_is_fresh_rejects_a_map_older_than_its_inputs():
    import os, time
    with tempfile.TemporaryDirectory() as d:
        m, x = Path(d) / "map.jsonl", Path(d) / "exchanges.jsonl"
        m.write_text("{}\n"); time.sleep(0.01); x.write_text("{}\n")
        ok, why = lc.map_is_fresh(m, [x]); assert not ok and "older" in why
        os.utime(m, None)
        assert lc.map_is_fresh(m, [x])[0]
        assert not lc.map_is_fresh(Path(d) / "missing.jsonl", [x])[0]
```

- [x] **Step 2:** `python3 scripts/topics/test_lifecycle.py` → the index/stage tests fail (`build_index` still expects `theme`/`unit_id`/`qdates`).
- [x] **Step 3: Adapt `lifecycle.py`** — replace `build_index`, drop `question_dates`/`coverage`/`PROGRESS_PATH`, add `map_is_fresh`, fix paths (`TOPICS_PATH = REPO/"state"/"topics"/"topic_map.jsonl"`, `DETECTIONS_PATH = .../detections.jsonl`); keep the module docstring (it is the Tier-0 rationale) and `main()` but have `main()` call `map_is_fresh(TOPICS_PATH, [EXCHANGES_PATH, CLAIMS_PATH])` in place of the `_progress.json` refusal.

```python
def build_index(rows) -> dict:
    """-> {(theme, ticker): pair}. Rows without themes are candidates, not topics: skipped."""
    idx: dict = {}
    for r in rows:
        ticker, date = r.get("ticker"), str(r.get("event_date") or "")[:10]
        if not ticker or not date:
            continue
        for t in (r.get("themes") or []):
            theme = t.get("theme") if isinstance(t, dict) else t
            if not theme:
                continue
            p = idx.setdefault((theme, ticker), {
                "theme": theme, "ticker": ticker, "first_evidence_date": None, "first_question_date": None,
                "n_evidence": 0, "n_question": 0, "banks": set(), "evidence_sources": set()})
            if r.get("register") == "evidence":
                p["n_evidence"] += 1
                p["evidence_sources"].add(r.get("source") or "exchange")
                if p["first_evidence_date"] is None or date < p["first_evidence_date"]:
                    p["first_evidence_date"] = date
            elif r.get("register") == "question":
                p["n_question"] += 1
                if r.get("firm"):
                    p["banks"].add(r["firm"])
                if p["first_question_date"] is None or date < p["first_question_date"]:
                    p["first_question_date"] = date
    return idx


def map_is_fresh(map_path: Path, inputs: list) -> tuple:
    map_path = Path(map_path)
    if not map_path.exists():
        return False, f"{map_path} missing — run topic_map.py --run first"
    mt = map_path.stat().st_mtime
    for p in inputs:
        p = Path(p)
        if p.exists() and p.stat().st_mtime > mt:
            return False, f"{map_path.name} is older than {p.name} — re-run topic_map.py before logging detections"
    return True, "fresh"
```

- [x] **Step 4:** `python3 scripts/topics/test_lifecycle.py` → all pass (expect 13).
- [x] **Step 5:** `git add scripts/topics/lifecycle.py scripts/topics/test_lifecycle.py && git commit -m "topics: port lifecycle (Tier-0 lag, §6.3 staging, append-only detections) onto topic_map rows"`

### Task 3: `diffusion.py` — metrics, denominators, host-firm exclusion

**Files:** Create `scripts/topics/diffusion.py`, `scripts/topics/test_diffusion.py`.

**Interfaces:**
- Produces `load_rows(path=TOPIC_MAP) -> list[dict]`; `load_exchange_meta(path=EXCHANGES) -> dict[vector_id -> {host_hint, speaker_name, speaker_firm, event_name, event_type, text}]`.
- Produces `firm_key(s) -> str` (lowercase alnum, aliases `bankofamerica→bofa`, `jpmorgansecurities→jpmorgan`); `is_host_firm(firm, host_hint) -> bool` (host key is a prefix of the firm key, or vice versa, min 4 chars).
- Produces `metrics(rows, meta, mdna_min_blocks=MDNA_MIN_BLOCKS) -> dict[(theme, cq) -> m]` with `m = {n_banks, banks: sorted list, n_host_excluded, n_companies, companies, n_exchanges, n_disclosing, disclosing, n_corprep_companies, first_seen_quarter}`.
- Produces `denominators(rows, no_coverage=None) -> dict[cq -> {earnings_call: n, conference: n, mdna_filers: n}]` over ALL exchange/mdna rows regardless of mapping, plus `no_coverage` lists passed through.
- Constants: `MDNA_MIN_BLOCKS = 2`, `STATE = REPO/"state"/"topics"`, `TOPIC_MAP`, `EXCHANGES`, `CLAIMS`, `NO_COVERAGE = REPO/"state"/"transcripts"/"_no_coverage.json"`, `DIFFUSION = STATE/"diffusion.json"`, `REPORT = REPO/"notes"/"reports"/"theme-diffusion.md"`.

- [x] **Step 1: Failing tests**

```python
#!/usr/bin/env python3
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import diffusion as df


def _r(rid, reg, ticker, date, cq, themes, firm=None, source="exchange", event_type="earnings_call"):
    return {"id": rid, "register": reg, "ticker": ticker, "event_date": date, "cal_quarter": cq, "firm": firm,
            "source": source, "event_type": event_type, "period_key": "x", "threshold": 0.3, "best": 0.5,
            "themes": [{"theme": t, "score": 0.5} for t in themes], "candidate": None}


def test_host_firm_matching_handles_real_headline_forms():
    assert df.is_host_firm("Goldman Sachs & Co. LLC", "Goldman Sachs Communacopia +")
    assert df.is_host_firm("Citigroup Global Markets, Inc.", "Citi")
    assert df.is_host_firm("BofA Securities, Inc.", "Bank of America")
    assert df.is_host_firm("JPMorgan Securities LLC", "JP Morgan")
    assert not df.is_host_firm("Mizuho Securities USA LLC", "Goldman Sachs")
    assert not df.is_host_firm(None, "Citi") and not df.is_host_firm("Citi", None)


def test_metrics_count_banks_companies_exchanges_and_exclude_host_from_banks():
    rows = [_r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"], firm="Raymond James & Associates, Inc."),
            _r("q2", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], firm="Goldman Sachs & Co. LLC", event_type="conference"),
            _r("q3", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], firm="Mizuho Securities USA LLC", event_type="conference"),
            _r("q4", "question", "LITE", "2026-08-12", "CY2026-Q3", ["t2"], firm="Mizuho Securities USA LLC")]
    meta = {"q2": {"host_hint": "Goldman Sachs Communacopia +"}, "q3": {"host_hint": "Goldman Sachs Communacopia +"}}
    m = df.metrics(rows, meta)
    t1 = m[("t1", "CY2026-Q3")]
    assert t1["n_exchanges"] == 3 and t1["n_companies"] == 2
    assert t1["n_banks"] == 2 and t1["n_host_excluded"] == 1     # Goldman at its own conference is out
    assert t1["companies"] == ["AAOI", "LITE"]
    assert m[("t2", "CY2026-Q3")]["n_banks"] == 1


def test_mdna_disclosing_needs_two_mapped_blocks_per_filer_quarter():
    rows = [_r("c1", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("c2", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("c3", "evidence", "LITE", "2026-05-02", "CY2026-Q2", ["t1"], source="mdna", event_type="10-Q"),
            _r("e1", "evidence", "FN", "2026-05-03", "CY2026-Q2", ["t1"])]
    t1 = df.metrics(rows, {})[("t1", "CY2026-Q2")]
    assert t1["disclosing"] == ["COHR"] and t1["n_disclosing"] == 1   # LITE has one block: not counted
    assert t1["n_corprep_companies"] == 1                              # FN corprep speech is evidence, separately
    assert t1["n_companies"] == 0 and t1["n_banks"] == 0


def test_first_seen_quarter_is_the_earliest_quarter_with_any_row():
    rows = [_r("q1", "question", "AAOI", "2026-02-01", "CY2026-Q1", ["t1"], firm="X"),
            _r("c1", "evidence", "COHR", "2025-11-01", "CY2025-Q4", ["t1"], source="mdna"),
            _r("c2", "evidence", "COHR", "2025-11-01", "CY2025-Q4", ["t1"], source="mdna")]
    m = df.metrics(rows, {})
    assert m[("t1", "CY2026-Q1")]["first_seen_quarter"] == "CY2025-Q4"


def test_denominators_count_covered_companies_per_quarter_and_event_type_over_all_rows():
    rows = [_r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", []),                       # unmapped still covered
            _r("e1", "evidence", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"]),
            _r("q2", "question", "LITE", "2026-08-10", "CY2026-Q3", ["t1"], event_type="conference"),
            _r("c1", "evidence", "COHR", "2026-08-01", "CY2026-Q3", [], source="mdna", event_type="10-Q")]
    d = df.denominators(rows)
    assert d["CY2026-Q3"] == {"earnings_call": 1, "conference": 1, "mdna_filers": 1}


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

- [x] **Step 2:** `python3 scripts/topics/test_diffusion.py` → `ModuleNotFoundError`.
- [x] **Step 3: Implement**

```python
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
    f, h = firm_key(firm), firm_key(host_hint)
    if len(f) < 4 or len(h) < 4:
        return False
    return f.startswith(h) or h.startswith(f)


def _themes(r) -> list:
    return [t["theme"] if isinstance(t, dict) else t for t in (r.get("themes") or []) if t]


def metrics(rows, meta, mdna_min_blocks: int = MDNA_MIN_BLOCKS) -> dict:
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


def denominators(rows, no_coverage: dict | None = None) -> dict:
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
```

- [x] **Step 4:** `python3 scripts/topics/test_diffusion.py` → 5/5.
- [x] **Step 5:** `git add scripts/topics/diffusion.py scripts/topics/test_diffusion.py && git commit -m "topics: diffusion metrics per (theme, quarter) with denominators, host-firm exclusion, 2-block MD&A rule"`

### Task 4: newly-said, movers, asked-elsewhere detector

**Files:** Modify `scripts/topics/diffusion.py`, `scripts/topics/test_diffusion.py`.

**Interfaces:**
- Produces `quarters_in(rows) -> list[str]` sorted distinct `cal_quarter`s.
- Produces `newly_said(rows, baseline=NEWLY_SAID_BASELINE) -> list[dict]` — one entry per `(ticker, theme, cq, source)` where the ticker has rows of that source in each of the `baseline` prior quarters (otherwise the baseline is unknown and the pair is skipped) and none of those rows carry the theme; for `source == "mdna"` the current quarter must also clear `MDNA_MIN_BLOCKS`. Entry: `{ticker, theme, cal_quarter, source, register, n_rows, baseline_quarters: [..]}`.
- Produces `movers(m: dict, cq: str, prev: str) -> list[dict]` sorted by `(-delta_banks, -delta_companies)`: `{theme, n_banks, prev_banks, delta_banks, n_companies, prev_companies, delta_companies, n_disclosing, prev_disclosing}` for every theme present in either quarter.
- Produces `detector_asked_elsewhere(idx, graph) -> list[dict]` — for every `(theme, ticker)` pair with `stage == 2`: `{theme, ticker, stage: 2, adjacent_asked: [{ticker, routes, first_question_date}], other_asked: [tickers], first_evidence_date, open_lag_days}`. `adjacent_asked` is the asked names that are graph-neighbours of `ticker`; sorted so pairs with non-empty `adjacent_asked` come first.

- [x] **Step 1: Failing tests** (append to `test_diffusion.py`)

```python
def test_newly_said_requires_a_full_baseline_and_absence_in_it():
    rows = [_r("a1", "evidence", "COHR", "2025-11-01", "CY2025-Q4", ["other"]),
            _r("a2", "evidence", "COHR", "2026-02-01", "CY2026-Q1", ["other"]),
            _r("a3", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"]),          # new: absent Q4, Q1
            _r("b1", "evidence", "LITE", "2026-02-01", "CY2026-Q1", ["other"]),
            _r("b2", "evidence", "LITE", "2026-05-01", "CY2026-Q2", ["t1"]),          # only 1 prior quarter: unknown
            _r("c1", "evidence", "FN", "2025-11-01", "CY2025-Q4", ["t1"]),
            _r("c2", "evidence", "FN", "2026-02-01", "CY2026-Q1", ["other"]),
            _r("c3", "evidence", "FN", "2026-05-01", "CY2026-Q2", ["t1"])]           # said in Q4: not new
    out = df.newly_said(rows)
    assert [(e["ticker"], e["theme"], e["cal_quarter"]) for e in out] == [("COHR", "t1", "CY2026-Q2")]
    assert out[0]["baseline_quarters"] == ["CY2025-Q4", "CY2026-Q1"]


def test_newly_said_mdna_needs_two_blocks_in_the_current_quarter():
    base = [_r(f"m{q}", "evidence", "COHR", d, q, ["other"], source="mdna")
            for q, d in (("CY2025-Q4", "2025-11-01"), ("CY2026-Q1", "2026-02-01"))]
    one = base + [_r("x1", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna")]
    assert df.newly_said(one) == []
    two = one + [_r("x2", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna")]
    assert [e["theme"] for e in df.newly_said(two)] == ["t1"]


def test_movers_compare_two_quarters_and_sort_on_banks_then_companies():
    m = {("t1", "Q1"): {"n_banks": 1, "n_companies": 1, "n_disclosing": 0},
         ("t1", "Q2"): {"n_banks": 4, "n_companies": 3, "n_disclosing": 2},
         ("t2", "Q2"): {"n_banks": 2, "n_companies": 5, "n_disclosing": 0},
         ("t3", "Q1"): {"n_banks": 3, "n_companies": 3, "n_disclosing": 0}}
    out = df.movers(m, "Q2", "Q1")
    assert [(e["theme"], e["delta_banks"]) for e in out] == [("t1", 3), ("t2", 2), ("t3", -3)]
    assert out[0]["prev_companies"] == 1 and out[1]["prev_banks"] == 0


def test_asked_elsewhere_separates_adjacent_from_other_askers():
    rows = [_r("c1", "evidence", "COHR", "2026-04-20", "CY2026-Q2", ["t1"], source="mdna"),
            _r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"], firm="Raymond James"),
            _r("q2", "question", "NVDA", "2026-08-07", "CY2026-Q3", ["t1"], firm="Citi")]
    idx = lc.build_index(rows)
    graph = {"COHR": {"AAOI": ["comparable"]}, "AAOI": {"COHR": ["comparable"]}}
    out = df.detector_asked_elsewhere(idx, graph, as_of="2026-09-10")
    assert len(out) == 1 and out[0]["ticker"] == "COHR" and out[0]["stage"] == 2
    assert out[0]["adjacent_asked"] == [{"ticker": "AAOI", "routes": ["comparable"], "first_question_date": "2026-08-06"}]
    assert out[0]["other_asked"] == ["NVDA"]
    assert out[0]["open_lag_days"] == (dt.date(2026, 9, 10) - dt.date(2026, 4, 20)).days
```

Add `import datetime as dt` and `import lifecycle as lc` at the top of the test file.

- [x] **Step 2:** run → 4 new failures (`AttributeError`).
- [x] **Step 3: Implement** (append to `diffusion.py`)

```python
def quarters_in(rows) -> list:
    return sorted({r["cal_quarter"] for r in rows if r.get("cal_quarter")})


def newly_said(rows, baseline: int = NEWLY_SAID_BASELINE, mdna_min_blocks: int = MDNA_MIN_BLOCKS) -> list:
    """Findings R4/R5: (filer, theme) is newly said in quarter q when the filer has rows of that
    source in each of the `baseline` prior quarters and none of them carry the theme. Recurring
    boilerplate can never register — that is the point."""
    qs = quarters_in(rows)
    seen: dict = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))  # (ticker,source)->cq->theme->n
    present: dict = collections.defaultdict(set)                                                # (ticker,source)->{cq}
    register_of = {}
    for r in rows:
        k, cq = (r.get("ticker"), r.get("source") or "exchange"), r.get("cal_quarter")
        if not k[0] or not cq:
            continue
        present[k].add(cq)
        register_of[(k, cq)] = r.get("register")
        for t in _themes(r):
            seen[k][cq][t] += 1
    out = []
    for k, by_q in seen.items():
        ticker, source = k
        for cq, counter in by_q.items():
            i = qs.index(cq)
            if i < baseline:
                continue
            prior = qs[i - baseline:i]
            if any(p not in present[k] for p in prior):
                continue                       # baseline unknown: the filer has no rows there
            for theme, n in counter.items():
                if source == "mdna" and n < mdna_min_blocks:
                    continue
                if any(theme in by_q.get(p, {}) for p in prior):
                    continue
                out.append({"ticker": ticker, "theme": theme, "cal_quarter": cq, "source": source,
                            "register": register_of.get((k, cq)), "n_rows": n, "baseline_quarters": prior})
    out.sort(key=lambda e: (e["cal_quarter"], e["ticker"], e["theme"], e["source"]))
    return out


def movers(m: dict, cq: str, prev: str) -> list:
    themes = {t for (t, q) in m if q in (cq, prev)}
    z = {"n_banks": 0, "n_companies": 0, "n_disclosing": 0}
    out = []
    for t in themes:
        a, b = m.get((t, cq), z), m.get((t, prev), z)
        out.append({"theme": t, "n_banks": a["n_banks"], "prev_banks": b["n_banks"],
                    "delta_banks": a["n_banks"] - b["n_banks"],
                    "n_companies": a["n_companies"], "prev_companies": b["n_companies"],
                    "delta_companies": a["n_companies"] - b["n_companies"],
                    "n_disclosing": a["n_disclosing"], "prev_disclosing": b["n_disclosing"]})
    out.sort(key=lambda e: (-e["delta_banks"], -e["delta_companies"], e["theme"]))
    return out


def detector_asked_elsewhere(idx: dict, graph: dict, as_of: str) -> list:
    """§6.1 over §6.3 stage 2: evidence here, questions elsewhere. Adjacent askers (verified
    graph) are what the spec calls stage 2; askers with no verified link are listed separately
    so the operator sees both and the stage never depends on an unaudited edge."""
    asked_by_theme: dict = collections.defaultdict(dict)
    for (theme, ticker), p in idx.items():
        if p["first_question_date"]:
            asked_by_theme[theme][ticker] = p["first_question_date"]
    out = []
    for (theme, ticker), p in idx.items():
        if lc.stage(idx, theme, ticker) != 2:
            continue
        nbrs = graph.get(ticker, {})
        adjacent = [{"ticker": t, "routes": nbrs[t], "first_question_date": d}
                    for t, d in sorted(asked_by_theme[theme].items()) if t in nbrs]
        other = [t for t in sorted(asked_by_theme[theme]) if t not in nbrs]
        out.append({"theme": theme, "ticker": ticker, "stage": 2, "adjacent_asked": adjacent, "other_asked": other,
                    "first_evidence_date": p["first_evidence_date"],
                    "evidence_sources": sorted(p["evidence_sources"]),
                    "open_lag_days": lc.open_lag_days(p, as_of)})
    out.sort(key=lambda e: (not e["adjacent_asked"], -(e["open_lag_days"] or 0), e["theme"], e["ticker"]))
    return out
```

- [x] **Step 4:** `python3 scripts/topics/test_diffusion.py` → 9/9.
- [x] **Step 5:** `git add scripts/topics/diffusion.py scripts/topics/test_diffusion.py && git commit -m "topics: newly-said (2-quarter baseline), movers, asked-elsewhere detector over verified adjacency"`

### Task 5: report, snapshot, detection log, CLI — run on the real map

**Files:** Modify `scripts/topics/diffusion.py`; `.gitignore` unchanged (`diffusion.json` and `detections.jsonl` are committed).

**Interfaces:**
- Produces `write_report(snapshot: dict, path=REPORT) -> str` and `build_snapshot(rows, meta, graph, as_of, no_coverage) -> dict` with keys `{as_of, quarters, current_quarter, in_progress: bool, denominators, no_coverage, metrics: [{theme, cal_quarter, ...m}], movers, stage_counts, lag_summary, stage1: [...], stage2: [...], newly_said, notes: [str]}`.
- CLI: `diffusion.py --run [--as-of YYYY-MM-DD] [--email] [--no-log] [--force-log]`.

- [x] **Step 1: Failing test** (append)

```python
def test_report_prints_denominators_exclusions_and_the_dropped_metric_note():
    rows = [_r("q1", "question", "AAOI", "2026-08-06", "CY2026-Q3", ["t1"], firm="Raymond James"),
            _r("c1", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna"),
            _r("c2", "evidence", "COHR", "2026-05-01", "CY2026-Q2", ["t1"], source="mdna")]
    nc = {"no_results": ["ADI"], "incomplete": ["innolight.cn"], "no_factset_id": [{"ticker": "base_power.us"}]}
    snap = df.build_snapshot(rows, {}, {"COHR": {"AAOI": ["comparable"]}, "AAOI": {"COHR": ["comparable"]}},
                             as_of="2026-09-10", no_coverage=nc)
    with tempfile.TemporaryDirectory() as d:
        text = df.write_report(snap, Path(d) / "r.md")
    assert "innolight.cn" in text and "ADI" in text and "base_power.us" in text     # exclusions named
    assert "earnings_call" in text and "conference" in text                        # denominators per event type
    assert "challenging_rate" in text                                                # the dropped metric is declared
    assert "stage 2" in text.lower() and "COHR" in text and "AAOI" in text
    assert snap["current_quarter"] == "CY2026-Q3" and snap["in_progress"] is True
```

- [x] **Step 2:** run → fails (`build_snapshot` missing).
- [x] **Step 3: Implement** (append)

```python
def _quarter_of(date_iso: str) -> str:
    y, m = int(date_iso[:4]), int(date_iso[5:7])
    return f"CY{y}-Q{(m - 1) // 3 + 1}"


def build_snapshot(rows, meta, graph, as_of: str, no_coverage: dict | None) -> dict:
    qs = quarters_in(rows)
    cur = qs[-1] if qs else None
    prev = qs[-2] if len(qs) > 1 else None
    m = metrics(rows, meta)
    idx = lc.build_index(rows)
    both = [lc.lag_days(p["first_evidence_date"], p["first_question_date"]) for p in idx.values()
            if p["first_evidence_date"] and p["first_question_date"]]
    stage_counts = collections.Counter()
    stage1 = []
    for (theme, ticker), p in idx.items():
        st = lc.stage(idx, theme, ticker)
        stage_counts[st] += 1
        if st == 1 and p["first_evidence_date"]:
            stage1.append({"theme": theme, "ticker": ticker, "stage": 1, "first_evidence_date": p["first_evidence_date"],
                           "n_evidence": p["n_evidence"], "evidence_sources": sorted(p["evidence_sources"]),
                           "open_lag_days": lc.open_lag_days(p, as_of)})
    stage1.sort(key=lambda e: (-(e["open_lag_days"] or 0), e["theme"], e["ticker"]))
    nc = no_coverage or {}
    excl = {"no_results": sorted(nc.get("no_results") or []), "incomplete": sorted(nc.get("incomplete") or []),
            "no_factset_id": sorted(x.get("ticker") for x in (nc.get("no_factset_id") or []) if x.get("ticker"))}
    notes = ["challenging_rate (spec §5) is not computed: exchange rows carry no challenging flag and 99% of "
             "analyst turns are sentiment=Neutral.",
             "P3 foreign evidence is not built: stages and lags use US evidence only (MD&A + corprep speech); "
             "Chinese filers appear only in the exclusions list.",
             f"MD&A counts need >= {MDNA_MIN_BLOCKS} mapped blocks per filer-quarter and are lower-confidence "
             "than transcript counts (mdna precision ~0.4 at its threshold).",
             "No trend lines by design: three or four observations per theme support a comparison, not a slope."]
    return {"as_of": as_of, "quarters": qs, "current_quarter": cur, "in_progress": bool(cur) and _quarter_of(as_of) == cur,
            "denominators": denominators(rows), "no_coverage": excl,
            "metrics": [dict(theme=t, cal_quarter=q, **v) for (t, q), v in sorted(m.items())],
            "movers": movers(m, cur, prev) if cur and prev else [],
            "stage_counts": {str(k): v for k, v in sorted(stage_counts.items()) if k},
            "lag_summary": lc.summarize(both), "stage1": stage1,
            "stage2": detector_asked_elsewhere(idx, graph, as_of), "newly_said": newly_said(rows), "notes": notes}


def write_report(snap: dict, path: Path = REPORT) -> str:
    d, cur, prev = snap["denominators"], snap["current_quarter"], (snap["quarters"][-2] if len(snap["quarters"]) > 1 else None)
    L = [f"## Theme diffusion — {snap['as_of']}", ""]
    L.append(f"Current quarter **{cur}**{' (in progress — counts are partial)' if snap['in_progress'] else ''}; "
             f"prior {prev or 'n/a'}. Quarters covered: {', '.join(snap['quarters'])}.")
    L.append("")
    L.append("### Coverage (read first)")
    L.append("| quarter | earnings_call companies | conference companies | MD&A filers |")
    L.append("|---|---|---|---|")
    for q in snap["quarters"]:
        x = d.get(q, {})
        L.append(f"| {q} | {x.get('earnings_call', 0)} | {x.get('conference', 0)} | {x.get('mdna_filers', 0)} |")
    nc = snap["no_coverage"]
    L.append(f"\nNo transcript coverage — no results: {', '.join(nc['no_results']) or 'none'}; "
             f"incomplete/unknown: {', '.join(nc['incomplete']) or 'none'}; "
             f"unmappable: {', '.join(nc['no_factset_id']) or 'none'}. "
             "FactSet retrieval is topically scoped (theme-derived queries), not whole-call export.")
    L.append("")
    for n in snap["notes"]:
        L.append(f"- {n}")
    L.append("")
    if snap["movers"]:
        L.append(f"### Movers — {cur} vs {prev} (n_banks first, then n_companies; host banks excluded at their own conferences)")
        L.append("| theme | banks | prev | Δ | companies asked | prev | disclosing (MD&A) | prev |")
        L.append("|---|---|---|---|---|---|---|---|")
        for e in snap["movers"][:40]:
            L.append(f"| {e['theme']} | {e['n_banks']} | {e['prev_banks']} | {e['delta_banks']:+d} | {e['n_companies']} | "
                     f"{e['prev_companies']} | {e['n_disclosing']} | {e['prev_disclosing']} |")
        L.append("")
    s = snap["lag_summary"]
    L.append("### Lifecycle (spec §6.3) — Tier-0 lag = first analyst question minus first evidence, days")
    if s.get("n"):
        L.append(f"n={s['n']} (theme, company) pairs with both registers: min {s['min']}, p25 {s['p25']}, median {s['median']}, "
                 f"p75 {s['p75']}, max {s['max']}; evidence led in {s['share_evidence_led']}% "
                 f"({s['n_negative']} negative = question came first, {s['n_zero']} same-day).")
    L.append("Stage counts: " + ", ".join(f"stage {k}: {v}" for k, v in snap["stage_counts"].items()))
    L.append("")
    L.append(f"### Stage 2 — asked at another name, not here ({len(snap['stage2'])}; verified-adjacent askers first)")
    L.append("| theme | company | adjacent asked (route, first question) | other askers | first evidence | open days | evidence |")
    L.append("|---|---|---|---|---|---|---|")
    for e in snap["stage2"][:60]:
        adj = "; ".join(f"{a['ticker']} ({','.join(a['routes'])}, {a['first_question_date']})" for a in e["adjacent_asked"]) or "—"
        L.append(f"| {e['theme']} | {e['ticker']} | {adj} | {', '.join(e['other_asked'][:6])} | {e['first_evidence_date']} | "
                 f"{e['open_lag_days']} | {','.join(e['evidence_sources'])} |")
    L.append("")
    L.append(f"### Stage 1 — evidence, nobody asked anywhere ({len(snap['stage1'])})")
    L.append("| theme | company | first evidence | open days | n_evidence | sources |")
    L.append("|---|---|---|---|---|---|")
    for e in snap["stage1"][:60]:
        L.append(f"| {e['theme']} | {e['ticker']} | {e['first_evidence_date']} | {e['open_lag_days']} | {e['n_evidence']} | "
                 f"{','.join(e['evidence_sources'])} |")
    L.append("")
    ns = [e for e in snap["newly_said"] if e["cal_quarter"] == cur]
    L.append(f"### Newly said in {cur} ({len(ns)}) — absent from the same filer's two prior quarters (findings R4/R5)")
    L.append("| company | theme | register | source | rows |")
    L.append("|---|---|---|---|---|")
    for e in ns[:80]:
        L.append(f"| {e['ticker']} | {e['theme']} | {e['register']} | {e['source']} | {e['n_rows']} |")
    L.append("")
    text = "\n".join(L)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


def run(args) -> int:
    ok, why = lc.map_is_fresh(TOPIC_MAP, [EXCHANGES, CLAIMS])
    if not ok and not args.force_log:
        log(f"REFUSING: {why}")
        return 2
    rows = load_rows()
    meta = load_exchange_meta()
    graph = adjmod.load_adjacency()
    nc = json.loads(NO_COVERAGE.read_text()) if NO_COVERAGE.exists() else {}
    snap = build_snapshot(rows, meta, graph, args.as_of, nc)
    log(f"{len(rows)} rows, {len(snap['metrics'])} (theme, quarter) cells, quarters {snap['quarters']}, "
        f"stages {snap['stage_counts']}, stage2 {len(snap['stage2'])}, stage1 {len(snap['stage1'])}, "
        f"newly_said {len(snap['newly_said'])}")
    STATE.mkdir(parents=True, exist_ok=True)
    DIFFUSION.write_text(json.dumps(snap, indent=1, default=list))
    text = write_report(snap)
    log(f"report -> {REPORT}")
    if not args.no_log:
        n = lc.append_detections(DETECTIONS, snap["stage1"], args.as_of)
        log(f"{n} new stage-1 detections appended -> {DETECTIONS} (first-seen dates never restamped)")
    if args.email:
        from newsdigest.email_send import send
        send(f"Theme diffusion {args.as_of}", text)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P4 diffusion (spec §5/§6)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--email", action="store_true")
    ap.add_argument("--no-log", action="store_true", help="do not append stage-1 detections")
    ap.add_argument("--force-log", action="store_true", help="proceed even if the map is older than its inputs")
    a = ap.parse_args(argv)
    if a.run:
        return run(a)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4:** `python3 scripts/topics/test_diffusion.py` → 10/10.
- [x] **Step 5: Real run, no log first** — `python3 scripts/topics/diffusion.py --run --no-log` → exit 0; read `notes/reports/theme-diffusion.md`. Record in the plan the counts: cells, stage counts, lag summary, stage2 count, stage1 count, newly_said count, host exclusions total (`python3 -c "import json;s=json.load(open('state/topics/diffusion.json'));print(sum(m['n_host_excluded'] for m in s['metrics']))"`).
- [x] **Step 6: Gold checks (§11.3 / §11.5c)** — `python3 - <<'EOF'` : load `diffusion.json`; (a) print the stage-2 entries whose `ticker` is COHR or LITE and whose `adjacent_asked` includes AAOI — expected ≥ 1 (Detector 1 fires on COHR/LITE via the AAOI comparable route); if none, print which themes AAOI's 2026-08-06 Raymond James rows mapped to (`topic_map.jsonl` rows with ticker AAOI, event_date 2026-08-06, register question) and record the recall gap honestly — do NOT add a query or theme to make it pass; (b) print at least one stage-1/stage-2 entry with `"mdna"` in `evidence_sources` (§11.5c: the MD&A path contributes). Paste both results into the plan under this step.
- [x] **Step 7: Spot-check 5 stage-2 rows** by joining ids back to `exchanges.jsonl` (question text) and `claims.jsonl` (evidence text) — record ok/wrong per row. If ≥ 3 of 5 are wrong, stop and reassess the mdna 2-block rule before logging anything.
- [x] **Step 8: Log run** — `python3 scripts/topics/diffusion.py --run` → detections appended (N); re-run → `0 new stage-1 detections`.
- [x] **Step 9: Commit** — `git add scripts/topics/diffusion.py scripts/topics/test_diffusion.py state/topics/diffusion.json state/topics/detections.jsonl notes/reports/theme-diffusion.md && git commit -m "topics: P4 diffusion report + snapshot + append-only stage-1 detections (first real run: <N cells>, stage2 <n>, stage1 <n>)"`

**Recorded on the first real run (2026-09-10, as_of 2026-09-10):** 17,116 rows → 223 (theme, quarter) cells over CY2025-Q4..CY2026-Q3 (Q3 in progress). Host-firm exclusions: 897 conference analyst turns. **Deviation adopted at Step 7:** the first spot check (stages driven by any evidence) had all 5 top adjacent-backed stage-2 pairs sourced from corprep transcript speech and 3 of 5 wrongly paired, so `STAGE_EVIDENCE_SOURCES = ("mdna",)` — stages and the Tier-0 lag run from MD&A evidence only (spec §6.3 says the clock is claims); corprep speech stays a reported count (`n_corprep_companies`). After that: stages {1: 13, 2: 155, 3: 55, 4: 372}; adjacent-backed stage 2 = 1 (NVDA `hyperscaler_revenue_concentration`: 10-K customer-concentration prose 2026-02-25 → CBRS/MRVL questions; pairing judged sound); newly_said 124; Tier-0 lag n=53, min −184, p25 −77, median −4, p75 174, max 272, evidence-led 39.6% (31 negative) — left-censored (questions from 2025-11-11, filings from 2025-12-10), stated in the report. Gold (a) §11.3: with corprep evidence Detector 1 fired on COHR (`thermal_management_cooling`) and LITE (`hyperscaler_revenue_concentration`) via AAOI but both pairings were wrong on inspection; with MD&A evidence it does not fire for COHR/LITE — the AAOI 2026-08-06 Raymond James turn is unmapped and the LITE/Mizuho 2026-06-09 turns map to `networking_competitive_landscape` (stage 3/4 there). `laser_architecture_competition` has no anchor yet (no labelled chunks). **Recall gap recorded, not papered over.** Gold (b) §11.5c: 168 of 490 stage-1/2 entries carried MD&A evidence before the deviation; after it every stage-1/2 entry is MD&A-sourced by construction. Known leak: AMBA's 2026-09-04 10-Q Item 2 embeds a risk-factor summary (192 blocks; 64 mapped to `software_seat_pricing_pressure`) — isolated (only note with ≥10 risk-flavoured blocks), left labelled; generic-finance themes (`software_seat_pricing_pressure` 26 disclosing, `capex_vs_opex_shift` 20) remain misfiling-dominated at mdna thr 0.40 and are flagged lower-confidence in the report.

### Task 6: cron, docs, memory, restore auto_sync

**Files:** crontab; `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` (status line); `ARCHITECTURE.md` §8 bullet; `config/crontab.snapshot` (auto by daily snapshot, but commit now); memory files.

- [ ] **Step 1: Cron** — after the Saturday 11:00 topic_map: `(crontab -l; echo '0 12 * * 6 cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh diffusion python3 scripts/topics/diffusion.py --run --email >> logs/diffusion.log 2>&1') | crontab -`; verify with `crontab -l | grep diffusion`. Email test once by hand: `set -a; . /root/podcasts/.env; set +a; python3 scripts/topics/diffusion.py --run --email --no-log` → HTTP 201 in the log.
- [ ] **Step 2: Spec status line** — change `P3/P4/P5 open` to `P4 built 2026-09-10 (plan docs/superpowers/plans/2026-09-10-diffusion-p4.md; challenging_rate dropped, verified adjacency only, no vault notes); P3/P5/P5b open`.
- [ ] **Step 3: ARCHITECTURE.md §8** — in the idea-surfacing bullet append: `**P4 diffusion built 2026-09-10** (scripts/topics/{adjacency,lifecycle,diffusion}.py, cron Sat 12:00, report notes/reports/theme-diffusion.md, append-only state/topics/detections.jsonl). Open: P3 foreign evidence (China-laser gold test needs it), P5 vault theme notes, P5b daily transition alert.`
- [ ] **Step 4: Commit docs** — `crontab -l > config/crontab.snapshot; git add docs/ ARCHITECTURE.md config/crontab.snapshot && git commit -m "docs+cron: P4 diffusion live (Sat 12:00), spec/architecture status"` then `git push origin main`.
- [ ] **Step 5: Memory** — write `/root/.claude/projects/-root/memory/diffusion_p4.md` (numbers from Task 5 steps 5–7, gold-check outcome, what P5 needs), update `resume_here.md` (P4 done; next = P5 theme notes or P3 foreign evidence — operator's call), add MEMORY.md line.
- [ ] **Step 6: Restore auto_sync LAST** — `crontab -l | sed 's#^\#PAUSED-P4 ##' | crontab - && crontab -l | grep -n auto_sync` → uncommented. Then `pgrep -af "claude -p|diffusion|topic_map" | grep -v pgrep` → nothing.

---

## Self-review

- **Spec coverage:** §5 counts + denominators + weighting → Task 3/5; `challenging_rate` → dropped, declared (constraints, report notes); §6.1 → Task 1 + Task 4 `detector_asked_elsewhere`; §6.2 gap → `n_disclosing` vs `n_companies` in metrics/movers; §6.3 stage/lag/open lag → Task 2 + snapshot; §6.4 novel names → out of P4 scope (needs `entities.py` residual; note in ARCHITECTURE as open); §7.2 sections 1–3 → report; 4 (candidates) stays in `theme-candidates.md`; 5–6 → not built (6 impossible without the flag); §10 host exclusion → Task 3; §11.3/11.5/11.5c → Task 5 steps 6–7; findings R4/R5 → Task 4.
- **Placeholders:** none; every step has code or an exact command.
- **Type consistency:** `build_index` pairs carry `evidence_sources` (set) used by `detector_asked_elsewhere` and `build_snapshot`; `metrics` keys `(theme, cq)` consumed by `movers`; `open_lag_days(pair, as_of)` signature matches the branch.
