# P5b stage-transition alert + daily earnings feed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Spec §7.3 — a daily, email-only, one-line-per-event alert when a theme changes lifecycle stage or first clears the §7.1 breadth gate — made meaningful by refreshing the question side daily (earnings-call transcripts the day after the call) instead of only on the Saturday conference pull. Plus the operator-approved weekend backfill of the 20 July earnings reviews (21 minus FICO, removed from the watchlist 2026-09-11) lost to the calendar-regex abort (commit 0f968170).

**Architecture:** `transcript_ingest.py` gains `--earnings DAYS`, a sibling of `--conferences DAYS` (same calendar-driven per-event pull, `eventTypes=['Earnings']`, two semantic queries per event because a call is ~52 chunks and one page holds 50). A weekday chain script runs, sequentially, earnings pull → `topic_map --run` → `diffusion --run` → new `scripts/topics/stage_alert.py`, which diffs the pairs in `state/topics/diffusion.json` against a stored `state/topics/stages.json`, dedups through `state/topics/alerts_sent.jsonl`, and emails the thin lines. First run seeds the baseline without emailing. `cron_earnings_reviewer.py` gains `--ticker` (repeatable) to bypass the calendar for the backfill, which runs as two one-shot self-removing weekend cron lines.

**Tech Stack:** Python 3.12 stdlib + pyyaml + numpy (existing); direct-run tests (no pytest on this box: `python3 scripts/topics/test_x.py`); email via `scripts/newsdigest/email_send.send`; FactSet via the mcp-lean `claude_p.run_mcp` transport already used by conference mode; crons in ET (the droplet crontab is ET; `/root/logs/cron_runs.log` is UTC).

**Spec:** `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` §5 (breadth), §6.3 (stages), §7.1 (gate, via `theme_notes.clears_gate`), §7.3 (this alert), §8 (P5b row). Prior plans: `2026-09-10-diffusion-p4.md` (snapshot `pairs` shape), `2026-09-10-theme-notes-p5.md` (gate + citation join).

## Global Constraints

- Stages come only from `diffusion.json["pairs"]` (`stage` ∈ {1,2,3,4} or None); never recompute stages here. No velocity, slope, smoothing (spec §5).
- Alert fires on **forward** stage moves and on a theme's **first** breadth-gate crossing (§7.3). Regressions (stage 4 → 3 when new covered names appear) update `stages.json` silently. A pair appearing for the first time counts as an event only at stage 3 (the holding was first asked); births at 1 are already `detections.jsonl`, births at 2/4 are silent.
- Stage-2 and stage-4 events are **theme-level** (one line per theme per day, since every carrier flips together when the first question lands); stage-3 events are **(theme, ticker)-level**.
- Announce once: ledger `state/topics/alerts_sent.jsonl`, ids `stage2:{theme}`, `stage3:{theme}:{ticker}`, `stage4:{theme}`, `gate:{theme}`. Same shape as `state/thesis/alerts_sent.jsonl` (`{"id","ts"}` + fields).
- First run (no `stages.json`) seeds and sends nothing. A run whose `diffusion.json` is not newer than `stages.json` is a no-op (exit 0, log "no new snapshot").
- Every printed figure carries its denominator: "asked at k of n covered names" (n = carriers of the theme in `pairs`).
- No LLM, no embedding in `stage_alert.py`. Zero `claude -p` in the weekday chain except the earnings pull (Haiku, mcp-lean).
- The earnings feed reuses the conference feed's contract verbatim: calendar per 50 symbols, `event_window` (+2 days, clamped to today), windowed ledger keys, `vector_id` dedup, `argument_drift` guard, abort on `ToolUnavailableError`.
- Backfill batches never overlap the 06:45/18:30 digest windows or the Saturday chain (09:00–12:45); if a run reports a session limit, the batch stops (remaining names logged `SKIPPED_SESSION_LIMIT`).
- Build hygiene: auto_sync is PAUSED (backup `/root/backups/crontab.pre_build_20260911_143237.bak`); restore it LAST, after the final commit.

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/v3_ingest/transcript_ingest.py` | add `EARNINGS_QUERIES`, `--earnings DAYS`; `_calendar_prompt(..., event_types)`, `fetch_calendar(..., event_types)`, `plan_from_events(..., event_type, queries)`; main wiring |
| `scripts/v3_ingest/test_transcript_ingest.py` | tests for the earnings plan/prompt |
| `scripts/cron_earnings_reviewer.py` | `--ticker` (repeatable) bypasses the calendar; batch stops on a session-limit marker |
| `scripts/test_cron_earnings_reviewer.py` | tests for both |
| `scripts/topics/stage_alert.py` | `load_prior`, `diff_events`, `gate_events`, `render`, `run`, CLI `--run [--email] [--dry-run] [--as-of]` |
| `scripts/topics/test_stage_alert.py` | direct-run tests |
| `scripts/topics/daily_chain.sh` | weekday sequential chain with per-step `alert_on_failure.sh` |
| `state/topics/stages.json` | committed: `{"as_of", "pairs": {"theme|ticker": stage}, "gated": [theme...]}` |
| `state/topics/alerts_sent.jsonl` | committed, append-only ledger |
| `docs/architecture.md` (status table) + `docs/cost-model.md` | one line each |

`diffusion.json["pairs"]` row (consumed): `{theme, ticker, stage, first_evidence_date, first_filing_date, first_question_date, lag_days, n_evidence, n_question, banks}`. `diffusion.json["metrics"]` row: `{theme, cal_quarter, n_banks, n_companies, n_disclosing, ...}`. Citations: `theme_notes.load_sources()` → `(rows, ex, cl)`; a question row `r` has `r["id"]` = `vector_id` in `ex`, whose record carries `speaker_name`, `speaker_firm`, `event_name`.

---

### Task 0: Build hygiene

- [x] **Step 1:** `pgrep -af "claude -p|ingest|topic_map|diffusion" | grep -v pgrep` → nothing.
- [x] **Step 2:** crontab backed up to `/root/backups/crontab.pre_build_20260911_143237.bak`; `*/15 auto_sync` line shows `#PAUSED_BUILD`.

---

### Task 1: `transcript_ingest.py --earnings DAYS`

**Files:**
- Modify: `scripts/v3_ingest/transcript_ingest.py` (constants ~L108-125, `_calendar_prompt` ~L765, `fetch_calendar` ~L779, `plan_from_events` ~L806, `main` ~L832-915)
- Test: `scripts/v3_ingest/test_transcript_ingest.py`

**Interfaces:**
- Produces `EARNINGS_QUERIES: tuple[str, str]`, `EARNINGS_WINDOW_DAYS = 3`.
- Produces `_calendar_prompt(symbols, start, end, event_types=("Conference",)) -> str`.
- Produces `fetch_calendar(entries, start, end, timeout=..., model=None, event_types=("Conference",)) -> list`.
- Produces `plan_from_events(entries, events, today=None, event_type="Conference", queries=(CONFERENCE_QUERY,)) -> list[(entry, query, (start, end))]` — one item per (name, event day, query).
- CLI: `--earnings DAYS` mutually exclusive with `--conferences`; both refuse `--start/--end`.

- [ ] **Step 1: Failing tests** — append to `scripts/v3_ingest/test_transcript_ingest.py` (follow its `_entry`/fixture helpers; if none, build an entry with `ti.Entry(ticker="NVDA", factset_id="NVDA-US", themes=[], reasons=[])` — check the dataclass name with `grep -n "class .*Entry" scripts/v3_ingest/transcript_ingest.py` first):

```python
def test_earnings_plan_makes_two_query_pulls_per_event():
    e = _entry("NVDA", "NVDA-US")
    events = [{"eventType": "Earnings", "requestId": "NVDA-US", "eventDateTime": "2026-08-27T20:00:00Z"},
              {"eventType": "Conference", "requestId": "NVDA-US", "eventDateTime": "2026-08-28T15:00:00Z"}]
    plan = ti.plan_from_events([e], events, today=dt.date(2026, 9, 11),
                               event_type="Earnings", queries=ti.EARNINGS_QUERIES)
    assert [(p[0].ticker, p[1], p[2]) for p in plan] == [
        ("NVDA", ti.EARNINGS_QUERIES[0], ("2026-08-27", "2026-08-29")),
        ("NVDA", ti.EARNINGS_QUERIES[1], ("2026-08-27", "2026-08-29"))]
    print("  ✓ earnings mode plans two queries per call and ignores conferences")


def test_calendar_prompt_carries_the_event_type():
    p = ti._calendar_prompt(["NVDA-US"], "2026-09-08", "2026-09-11", event_types=("Earnings",))
    assert "eventTypes=['Earnings']" in p and "Conference" not in p
    assert "eventTypes=['Conference']" in ti._calendar_prompt(["NVDA-US"], "2026-09-08", "2026-09-11")
    print("  ✓ calendar prompt pins the event type; default stays Conference")


def test_earnings_queries_are_tool_legal_and_distinct():
    assert len(set(ti.EARNINGS_QUERIES)) == 2
    for q in ti.EARNINGS_QUERIES:
        assert ti.QUERY_CHARSET_RE.fullmatch(q), q
    print("  ✓ two distinct earnings queries, tool-legal charset")
```
Register the three in the file's `__main__` runner list.

- [ ] **Step 2: Run** `python3 scripts/v3_ingest/test_transcript_ingest.py` → expect `TypeError: plan_from_events() got an unexpected keyword argument 'event_type'` (or `AttributeError: EARNINGS_QUERIES`).

- [ ] **Step 3: Implement**

Constants (next to `CONFERENCE_QUERY`):
```python
# Earnings mode (2026-09-11, P5b): the same calendar-driven per-event pull with
# eventTypes=['Earnings']. A call is ~52 chunks (median over 136 backfilled events,
# p75 64) and a page holds 50, and paging over ties leaves gaps — so two semantic
# queries per event, one page each: analyst Q&A first (the register topic_map keys on),
# prepared remarks second. vector_id dedup absorbs the overlap.
EARNINGS_QUERIES = ("What did analysts ask in the question and answer session?",
                    "What did management say in prepared remarks about results and guidance?")
EARNINGS_WINDOW_DAYS = 3                          # weekday cron with two days of overlap
```

`_calendar_prompt`: add `event_types=("Conference",)` and render `f"  eventTypes={list(event_types)!r}\n"`.

`fetch_calendar`: add `event_types=("Conference",)`, pass through to `_calendar_prompt`.

`plan_from_events`: add `event_type="Conference", queries=(CONFERENCE_QUERY,)`; replace the `!= "Conference"` test with `!= event_type`; after `seen.add(...)`, `for q in queries: plan.append((entry, q, w))`.

`main`: add
```python
ap.add_argument("--earnings", type=int, metavar="DAYS",
                help="calendar-driven earnings-call feed over a trailing window (weekday cron)")
```
validation: `if args.earnings and args.conferences: ap.error("--earnings and --conferences are separate feeds")`; extend the `--start` refusal to `(args.conferences or args.earnings)`. Window: `if args.conferences or args.earnings: start, end = conference_window(args.conferences or args.earnings); window, override = (start, end), (args.query or list(CONFERENCE_QUERY if ...))` — write it as:
```python
    feed = "Conference" if args.conferences else ("Earnings" if args.earnings else None)
    feed_queries = (args.query or ([CONFERENCE_QUERY] if feed == "Conference" else list(EARNINGS_QUERIES))) if feed else None
    if feed:
        start, end = conference_window(args.conferences or args.earnings)
        window, override = (start, end), feed_queries
```
Planning block: `if feed and not args.scan:` → `fetch_calendar(entries, start, end, model=args.model, event_types=(feed,))`, `plan_from_events(entries, events, event_type=feed, queries=tuple(feed_queries))`, and the log line counts `ev.get("eventType") == feed`. Default `--max-pages` stays; the per-event window with `limit=50` returns one page per query (short page → terminal).

- [ ] **Step 4: Run** the test file → all ✓ (existing conference tests unchanged).

- [ ] **Step 5: Live validation on one known call** (3 Haiku calls). NVDA reported 2026-08-27; its call is already in `exchanges.jsonl` from the backfill.
```bash
python3 - <<'EOF'
import json
ids=set(); n=0
for l in open('state/transcripts/exchanges.jsonl'):
    r=json.loads(l)
    if r['ticker']=='NVDA' and r.get('event_date')=='2026-08-27': ids.add(r['vector_id'])
print('before', len(ids))
EOF
cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && python3 scripts/v3_ingest/transcript_ingest.py --earnings 16 --ticker NVDA --dry-run
python3 scripts/v3_ingest/transcript_ingest.py --earnings 16 --ticker NVDA 2>&1 | tail -8
```
Expected: dry run lists exactly two `DRY NVDA [NVDA-US] 2026-08-27..2026-08-29` lines; the live run logs `calendar: N events (1 Earnings)`, two `kept=` lines, `written=0` or small (dedup), and `no_coverage` unchanged. Then count how many of the run's returned vector_ids (from `state/transcripts/raw/` cache for the two windowed keys, or the `kept=` totals) were already in the backfill set — record the coverage % in the commit message. If coverage of the backfill's analyst chunks is < 80%, add a third query `"What were the questions about demand, pricing, capacity and competition?"` and re-measure.

- [ ] **Step 6: Commit**
```bash
git add scripts/v3_ingest/transcript_ingest.py scripts/v3_ingest/test_transcript_ingest.py
git commit -m "transcript_ingest: --earnings DAYS daily feed (calendar-driven, two queries per call)"
```

---

### Task 2: `cron_earnings_reviewer.py --ticker` + session-limit stop

**Files:**
- Modify: `scripts/cron_earnings_reviewer.py` (`main()` ~L296-350; add argparse)
- Test: `scripts/test_cron_earnings_reviewer.py`

**Interfaces:**
- Produces `main(argv=None) -> int` with `--ticker T` (repeatable). With `--ticker`, the calendar is not queried; names not on the watchlist are logged `NOT_ON_WATCHLIST` and skipped.
- Produces `is_session_limit(marker: str) -> bool` — True when a `STATUS: error` marker's detail contains `429` or `session limit` or `usage limit` (case-insensitive).
- Batch behaviour: on the first session-limit marker, the remaining tickers are logged `SKIPPED_SESSION_LIMIT {ticker}` and the run exits 1.

- [ ] **Step 1: Failing tests**
```python
def test_ticker_flag_bypasses_calendar_and_filters_watchlist():
    calls = []
    cer.query_calendar = lambda wl: (_ for _ in ()).throw(AssertionError("calendar must not be queried"))
    cer.run_earnings_reviewer = lambda t, started: (calls.append(t) or f"STATUS: new-note-written ticker={t}")
    cer.load_watchlist_tickers = lambda: ["AAPL", "MSFT"]
    rc = cer.main(["--ticker", "AAPL", "--ticker", "ZZZZ", "--ticker", "MSFT"])
    assert rc == 0 and calls == ["AAPL", "MSFT"], (rc, calls)
    print("  ✓ --ticker skips the calendar and drops non-watchlist names")


def test_session_limit_stops_the_batch():
    calls = []
    def fake(t, started):
        calls.append(t)
        return ("STATUS: error reason=invocation-failed detail=rc=1 stderr='claude -p session limit reached (429)'"
                if t == "AAPL" else f"STATUS: new-note-written ticker={t}")
    cer.run_earnings_reviewer = fake
    cer.load_watchlist_tickers = lambda: ["AAPL", "MSFT", "META"]
    rc = cer.main(["--ticker", "AAPL", "--ticker", "MSFT", "--ticker", "META"])
    assert rc == 1 and calls == ["AAPL"], (rc, calls)
    assert cer.is_session_limit("STATUS: error reason=x detail=Usage limit reached") is True
    assert cer.is_session_limit("STATUS: error reason=no-marker-emitted detail=...") is False
    print("  ✓ a 429/session-limit marker stops the batch instead of burning 15 min per name")
```
Save/restore the patched functions in the runner (`orig = (cer.query_calendar, cer.run_earnings_reviewer, cer.load_watchlist_tickers)` … `finally:` restore).

- [ ] **Step 2: Run** → `TypeError: main() takes 0 positional arguments`.

- [ ] **Step 3: Implement** — in `main(argv=None)`: `import argparse`; `ap.add_argument("--ticker", action="append")`; after loading the watchlist:
```python
    if args.ticker:
        reported = [t.upper() for t in args.ticker]
        log_write(f"  --ticker given: {reported} (calendar skipped)")
    else:
        ... existing calendar block ...
```
then the existing intersect logic (log the dropped ones as `NOT_ON_WATCHLIST`). In the loop:
```python
        if marker.startswith("STATUS: error"):
            error_count += 1
            if is_session_limit(marker):
                rest = to_process[to_process.index(ticker) + 1:]
                for r in rest: log_write(f"  SKIPPED_SESSION_LIMIT {r}")
                break
```
and
```python
SESSION_LIMIT_RE = re.compile(r"429|session limit|usage limit", re.I)
def is_session_limit(marker: str) -> bool:
    return marker.startswith("STATUS: error") and bool(SESSION_LIMIT_RE.search(marker))
```
`if __name__ == "__main__": sys.exit(main())` unchanged (argv=None → sys.argv).

- [ ] **Step 4: Run** the test file → all ✓ (9 prior + 2).

- [ ] **Step 5: Commit** `git commit -m "earnings_reviewer: --ticker backfill entry point; stop the batch on a session limit"`.

---

### Task 3: `stage_alert.py` — diff, gate, seed (pure functions)

**Files:**
- Create: `scripts/topics/stage_alert.py`, `scripts/topics/test_stage_alert.py`

**Interfaces:**
- `STATE = REPO/"state"/"topics"`, `STAGES = STATE/"stages.json"`, `LEDGER = STATE/"alerts_sent.jsonl"`, `DIFFUSION = STATE/"diffusion.json"`.
- `pair_key(theme, ticker) -> str` = `f"{theme}|{ticker}"`.
- `snapshot_stages(snap) -> dict[str, int]` — from `snap["pairs"]`, skipping `stage is None`.
- `gated_themes(snap) -> list[str]` — themes whose current-quarter metric cells clear `theme_notes.clears_gate` (import `clears_gate` from `theme_notes`; cells = `[m for m in snap["metrics"] if m["theme"] == theme]`).
- `diff_events(prior: dict, cur: dict) -> list[dict]` — prior/cur are `{"pairs": {...}, "gated": [...]}`. Returns events sorted by (theme, kind, ticker):
  - `{"kind": "stage2", "theme"}` when any pair of the theme moved to 2 from 1 (theme-level, once).
  - `{"kind": "stage3", "theme", "ticker"}` when a pair moved to 3 from 1 or 2, **or** is new at 3.
  - `{"kind": "stage4", "theme"}` when any pair of the theme moved to 4 from < 4 (theme-level).
  - `{"kind": "gate", "theme"}` for themes in `cur["gated"]` not in `prior["gated"]`.
  - Regressions and births at 1/2/4 produce nothing.
- `event_id(ev) -> str`: `stage2:{theme}`, `stage3:{theme}:{ticker}`, `stage4:{theme}`, `gate:{theme}`.

- [ ] **Step 1: Failing tests** (`scripts/topics/test_stage_alert.py`, direct-run, same style as `test_diffusion.py`):
```python
#!/usr/bin/env python3
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_alert as sa


def _pair(theme, ticker, stage, fe=None, fq=None, banks=()):
    return {"theme": theme, "ticker": ticker, "stage": stage, "first_evidence_date": fe, "first_filing_date": fe,
            "first_question_date": fq, "lag_days": None, "n_evidence": 1 if fe else 0, "n_question": 1 if fq else 0,
            "banks": list(banks)}


def test_diff_emits_forward_moves_only_and_collapses_theme_level_kinds():
    prior = {"pairs": {"t|A": 1, "t|B": 1, "t|C": 1, "u|X": 4}, "gated": []}
    cur = {"pairs": {"t|A": 3, "t|B": 2, "t|C": 2, "t|D": 2, "u|X": 3, "v|Y": 3}, "gated": ["t"]}
    ev = sa.diff_events(prior, cur)
    assert [(e["kind"], e["theme"], e.get("ticker")) for e in ev] == [
        ("gate", "t", None), ("stage2", "t", None), ("stage3", "t", "A"), ("stage3", "v", "Y")], ev
    print("  ✓ forward moves + first gate crossing; regression u|X 4->3 and birth t|D at 2 are silent")


def test_stage4_is_one_line_per_theme():
    ev = sa.diff_events({"pairs": {"t|A": 3, "t|B": 3}, "gated": ["t"]}, {"pairs": {"t|A": 4, "t|B": 4}, "gated": ["t"]})
    assert [(e["kind"], e["theme"]) for e in ev] == [("stage4", "t")]
    assert sa.event_id(ev[0]) == "stage4:t"
    print("  ✓ stage 4 collapses to one theme-level line")


def test_snapshot_stages_and_gate_from_diffusion_shape():
    snap = {"current_quarter": "CY2026-Q3",
            "pairs": [_pair("t", "A", 2, fe="2026-05-01"), _pair("t", "B", None)],
            "metrics": [{"theme": "t", "cal_quarter": "CY2026-Q3", "n_banks": 2, "n_companies": 3, "n_disclosing": 0},
                        {"theme": "u", "cal_quarter": "CY2026-Q3", "n_banks": 1, "n_companies": 1, "n_disclosing": 1}]}
    assert sa.snapshot_stages(snap) == {"t|A": 2}
    assert sa.gated_themes(snap) == ["t"]
    print("  ✓ snapshot -> stages map (None skipped) and gated themes via theme_notes.clears_gate")


if __name__ == "__main__":
    test_diff_emits_forward_moves_only_and_collapses_theme_level_kinds()
    test_stage4_is_one_line_per_theme()
    test_snapshot_stages_and_gate_from_diffusion_shape()
    print("\nALL PASS")
```

- [ ] **Step 2: Run** `python3 scripts/topics/test_stage_alert.py` → `ModuleNotFoundError: stage_alert`.

- [ ] **Step 3: Implement** `scripts/topics/stage_alert.py` (module docstring: spec §7.3, the four kinds, seed rule, ledger):
```python
#!/usr/bin/env python3
"""P5b stage-transition alert (spec §7.3). See docs/superpowers/plans/2026-09-11-stage-alert-p5b.md."""
import argparse, datetime as dt, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from theme_notes import clears_gate, load_sources   # noqa: E402

REPO = Path("/root/research-watchlist")
STATE = REPO / "state" / "topics"
DIFFUSION, STAGES, LEDGER = STATE / "diffusion.json", STATE / "stages.json", STATE / "alerts_sent.jsonl"
KIND_ORDER = {"gate": 0, "stage2": 1, "stage3": 2, "stage4": 3}


def log(msg): print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] stage_alert: {msg}", flush=True)
def pair_key(theme, ticker): return f"{theme}|{ticker}"
def _split(k): return k.split("|", 1)


def snapshot_stages(snap) -> dict:
    return {pair_key(p["theme"], p["ticker"]): p["stage"] for p in snap["pairs"] if p.get("stage")}


def gated_themes(snap) -> list:
    cq = snap.get("current_quarter")
    by_theme = {}
    for m in snap.get("metrics", []):
        if m["cal_quarter"] == cq:
            by_theme.setdefault(m["theme"], []).append(m)
    return sorted(t for t, cells in by_theme.items() if clears_gate(cells))


def diff_events(prior, cur) -> list:
    pp, cp = prior.get("pairs", {}), cur.get("pairs", {})
    ev, seen = [], set()
    def add(kind, theme, ticker=None):
        key = (kind, theme, ticker)
        if key not in seen:
            seen.add(key); ev.append({"kind": kind, "theme": theme, **({"ticker": ticker} if ticker else {})})
    for k, st in cp.items():
        theme, ticker = _split(k)
        was = pp.get(k)
        if was is None:
            if st == 3: add("stage3", theme, ticker)
            continue
        if st <= was: continue
        if st == 2: add("stage2", theme)
        elif st == 3: add("stage3", theme, ticker)
        elif st == 4: add("stage4", theme)
    for t in cur.get("gated", []):
        if t not in set(prior.get("gated", [])): add("gate", t)
    ev.sort(key=lambda e: (e["theme"], KIND_ORDER[e["kind"]], e.get("ticker") or ""))
    return ev


def event_id(e) -> str:
    return f"{e['kind']}:{e['theme']}" + (f":{e['ticker']}" if e.get("ticker") else "")
```
(`run`/`render`/CLI come in Task 4; leave a `if __name__ == "__main__": sys.exit(main())` only once `main` exists.)

- [ ] **Step 4: Run** tests → ALL PASS.
- [ ] **Step 5: Commit** `git add scripts/topics/stage_alert.py scripts/topics/test_stage_alert.py && git commit -m "topics: stage_alert diff/gate/seed primitives (P5b)"`.

---

### Task 4: `stage_alert.py` — rendering, citations, ledger, CLI, seed run

**Files:**
- Modify: `scripts/topics/stage_alert.py`; `scripts/topics/test_stage_alert.py`

**Interfaces:**
- `first_question_cite(theme, ticker, date, rows, ex) -> dict|None` — among topic_map rows with `register=="question"`, that ticker, `event_date==date`, carrying the theme, pick the highest-score one; return `{"speaker","firm","event"}` from `ex[row["id"]]` (fallbacks "analyst"/"?"/event_type).
- `render(e, snap, rows, ex, as_of) -> str` — one line, no markdown headers:
  - stage2: ``"`{theme}` moved to stage 2 — {asker} {date} ({speaker}, {firm}). {unasked} still unasked. First evidence {fe}, {N} days ago."`` where asker = the theme's pair with the earliest `first_question_date`; unasked = tickers of the theme's pairs with `first_question_date` None (join ", ", or "no other carrier"); fe = min first_evidence_date over the theme's pairs; if fe is None the sentence is "No filing evidence yet."
  - stage3: ``"`{theme}` moved to stage 3 at {ticker} — asked {date} ({speaker}, {firm}). Asked at {k} of {n} covered names."``
  - stage4: ``"`{theme}` is now stage 4 (late): asked at {k} of {n} covered names."``
  - gate: ``"`{theme}` crossed the breadth gate in {cq}: {n_banks} banks / {n_companies} companies asked, {n_disclosing} disclosing → notes/themes/{theme}.md"``
  - every line ends with `" → notes/themes/{theme}.md"` if that file exists (gate line already carries it).
- `load_prior(path=STAGES) -> dict|None`; `save_state(path, as_of, pairs, gated)`.
- `sent_ids(path=LEDGER) -> set`; `append_ledger(path, events, ts)`.
- `run(args) -> int`: no snapshot → log + 2; `prior is None` → seed, log `seeded {n} pairs, {g} gated themes; no email`, 0; snapshot mtime ≤ stages mtime and not `--force` → log "no new snapshot", 0; else events = diff − ledger; render; `--dry-run` prints; else email `Theme stage alert — {as_of} ({k} event(s))` only when k > 0; append ledger; save state (always, so regressions are absorbed).

- [ ] **Step 1: Failing tests** (append; use `tempfile.TemporaryDirectory` and monkeypatch `sa.DIFFUSION/STAGES/LEDGER`; patch `sa.send = lambda subj, body: sent.append((subj, body))` and `sa.load_sources = lambda: (rows, ex, {})`):
```python
def test_render_stage2_line_matches_spec_shape():
    snap = {"as_of": "2026-09-11", "current_quarter": "CY2026-Q3", "metrics": [],
            "pairs": [_pair("chinese_optical_competition", "AAOI", 3, fe="2026-04-20", fq="2026-08-06", banks=["Raymond James"]),
                      _pair("chinese_optical_competition", "COHR", 2, fe="2026-04-20"),
                      _pair("chinese_optical_competition", "LITE", 2, fe="2026-05-02")]}
    rows = [{"id": "v1", "register": "question", "ticker": "AAOI", "event_date": "2026-08-06", "cal_quarter": "CY2026-Q3",
             "source": "exchange", "event_type": "earnings_call", "themes": [{"theme": "chinese_optical_competition", "score": 0.6}]}]
    ex = {"v1": {"speaker_name": "Simon Leopold", "speaker_firm": "Raymond James", "event_name": "Q2 2026 Earnings Call"}}
    line = sa.render({"kind": "stage2", "theme": "chinese_optical_competition"}, snap, rows, ex, "2026-09-11")
    assert line.startswith("`chinese_optical_competition` moved to stage 2 — AAOI 2026-08-06 (Simon Leopold, Raymond James). "
                           "COHR, LITE still unasked. First evidence 2026-04-20, 144 days ago"), line
    print("  ✓ stage-2 line reads like spec §7.3's example")


def test_run_seeds_silently_then_emails_once_and_absorbs_regressions():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d); sa.DIFFUSION, sa.STAGES, sa.LEDGER = d / "diffusion.json", d / "stages.json", d / "alerts_sent.jsonl"
        sent = []; sa.send = lambda s, b: sent.append((s, b)); sa.load_sources = lambda: ([], {}, {})
        snap = {"as_of": "2026-09-10", "current_quarter": "CY2026-Q3", "metrics": [],
                "pairs": [_pair("t", "A", 1, fe="2026-05-01"), _pair("t", "B", 1, fe="2026-05-01"), _pair("u", "X", 4)]}
        sa.DIFFUSION.write_text(json.dumps(snap))
        assert sa.run(sa.parse(["--run", "--email"])) == 0 and sent == [] and sa.STAGES.exists()
        # nothing new: same snapshot again (force past the mtime guard)
        assert sa.run(sa.parse(["--run", "--email", "--force"])) == 0 and sent == []
        snap["pairs"] = [_pair("t", "A", 3, fe="2026-05-01", fq="2026-09-11"), _pair("t", "B", 2, fe="2026-05-01"), _pair("u", "X", 3)]
        snap["as_of"] = "2026-09-11"; sa.DIFFUSION.write_text(json.dumps(snap))
        assert sa.run(sa.parse(["--run", "--email", "--force"])) == 0
        assert len(sent) == 1 and "stage 2" in sent[0][1] and "stage 3 at A" in sent[0][1] and "u" not in sent[0][0]
        assert json.loads(sa.STAGES.read_text())["pairs"]["u|X"] == 3            # regression absorbed, not announced
        assert sa.run(sa.parse(["--run", "--email", "--force"])) == 0 and len(sent) == 1   # ledger: announced once
        ids = {json.loads(l)["id"] for l in sa.LEDGER.read_text().splitlines()}
        assert ids == {"stage2:t", "stage3:t:A"}, ids
    print("  ✓ seed is silent; transitions email once; regressions update state silently")
```

- [ ] **Step 2: Run** → `AttributeError: module 'stage_alert' has no attribute 'render'`.

- [ ] **Step 3: Implement** the interfaces above. Notes: `parse(argv)` is the argparse wrapper (`--run`, `--email`, `--dry-run`, `--force`, `--as-of` default today) so tests can build args; `from newsdigest.email_send import send` at module top guarded by `try/except ImportError: send = None` — `run` raises a clear error if `--email` and `send is None`. Days-ago = `(date(as_of) - date(fe)).days`. Covered n = number of the theme's pairs; k = pairs with `first_question_date`. Ledger record: `{"id", "kind", "theme", "ticker", "ts", "as_of"}`.

- [ ] **Step 4: Run** the test file → ALL PASS.

- [ ] **Step 5: First real run = seed** (auto_sync is paused, so this is safe to commit deliberately):
```bash
cd /root/research-watchlist && python3 scripts/topics/stage_alert.py --run
python3 -c "import json;d=json.load(open('state/topics/stages.json'));print(len(d['pairs']), d['gated'][:5], len(d['gated']))"
```
Expected: `seeded 595 pairs, 36 gated themes; no email` (36 = the P5 note count; if it differs, explain why in the commit — the gate here is current-quarter-only, P5 is any-quarter, so ≤ 36 is expected; say which).
Then `python3 scripts/topics/stage_alert.py --run --dry-run --force` → "no events".

- [ ] **Step 6: Commit** `git add scripts/topics/stage_alert.py scripts/topics/test_stage_alert.py state/topics/stages.json && git commit -m "topics: stage_alert — §7.3 daily stage-transition alert, seeded"`.

---

### Task 5: Weekday chain, crons, backfill one-shots, docs, restore

**Files:**
- Create: `scripts/topics/daily_chain.sh`
- Modify: crontab (via `crontab -l | … | crontab -`), `docs/architecture.md` (status table row), `docs/cost-model.md` (one line), memory files.

- [ ] **Step 1: Chain script**
```bash
#!/bin/bash
# P5b weekday chain (2026-09-11): sequential so diffusion never sees a map older than its inputs.
# mdna_evidence runs at 12:30 on its own line; this starts at 12:45.
set -u
cd /root/research-watchlist || exit 1
set -a; . /root/podcasts/.env; set +a
A=/root/bin/alert_on_failure.sh
$A transcript_earnings python3 scripts/v3_ingest/transcript_ingest.py --earnings 3 >> logs/transcript_ingest_earnings.log 2>&1
$A topic_map_daily     python3 scripts/topics/topic_map.py --run                    >> logs/topic_map.log 2>&1
$A diffusion_daily     python3 scripts/topics/diffusion.py --run                    >> logs/diffusion.log 2>&1
$A stage_alert         python3 scripts/topics/stage_alert.py --run --email          >> logs/stage_alert.log 2>&1
```
`chmod +x`. Each step pages on failure but the chain continues (a failed earnings pull must not block an MD&A-driven alert; diffusion's own staleness guard refuses if the map is stale).

- [ ] **Step 2: Time the daily topic_map** once by hand before scheduling: `time python3 scripts/topics/topic_map.py --run` (no `--suggest-names`, no `--email`; all units cached → expect well under 5 min; log the number). Then `python3 scripts/topics/diffusion.py --run` and `python3 scripts/topics/stage_alert.py --run --dry-run` → "no events" (same day as the seed).

- [ ] **Step 3: Crons** (ET). Append under the topic block:
```
45 12 * * 1-5 /root/research-watchlist/scripts/topics/daily_chain.sh
45 12 * * 6 cd /root/research-watchlist && set -a && . /root/podcasts/.env && set +a && /root/bin/alert_on_failure.sh stage_alert python3 scripts/topics/stage_alert.py --run --email >> logs/stage_alert.log 2>&1
```
Backfill one-shots (self-removing; marker is a shell no-op inside the command):
```
0 14 12 9 * : ONESHOT_BACKFILL_1; cd /root/research-watchlist && /root/bin/alert_on_failure.sh earnings_backfill_1 python3 scripts/cron_earnings_reviewer.py --ticker BE --ticker CLS --ticker GLW --ticker KLAC --ticker NXPI --ticker SWKS --ticker UMC --ticker WELL --ticker MSFT --ticker META --ticker QCOM; crontab -l | grep -v ONESHOT_BACKFILL_1 | crontab -
0 13 13 9 * : ONESHOT_BACKFILL_2; cd /root/research-watchlist && /root/bin/alert_on_failure.sh earnings_backfill_2 python3 scripts/cron_earnings_reviewer.py --ticker ARM --ticker LRCX --ticker AAPL --ticker AMZN --ticker MPWR --ticker PWR --ticker RDDT --ticker SOLS --ticker SONY; crontab -l | grep -v ONESHOT_BACKFILL_2 | crontab -
```
Sat 2026-09-12 14:00 (after the chain, before nothing) and Sun 2026-09-13 13:00 (after nport 12:07; thesis_draft/store_b/insider are 07:00–09:30). `crontab -l | grep -c ONESHOT_BACKFILL` → 2.

- [ ] **Step 4: Docs** — `docs/architecture.md`: add the P5b row (daily chain, files, cron) next to the P4/P5 rows; `docs/cost-model.md`: "+ weekday earnings pull: 2–3 Haiku calendar calls + 2 Haiku pulls per reporting name (mcp-lean, ~23K tok each); zero LLM elsewhere in the chain". Spec §8 table: mark P5b delivered (one word, date).

- [ ] **Step 5: Commit + push + restore**
```bash
git add scripts/topics/daily_chain.sh docs/architecture.md docs/cost-model.md docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md docs/superpowers/plans/2026-09-11-stage-alert-p5b.md
git commit -m "docs+cron: P5b stage alert live (weekday chain 12:45, Sat 12:45), July earnings backfill one-shots"
git push origin main
crontab -l | sed 's#^\#PAUSED_BUILD \(.*\)$#\1#' | crontab - && crontab -l | grep -n auto_sync
```
Then update memory: `resume_here.md` (P5b LIVE, first weekday run Mon 09-14 12:45, backfill one-shots Sat/Sun, what to verify), new `stage_alert_p5b.md`, index line.

---

## Self-review

- **Spec coverage:** §7.3 fires on stage change → Task 3/4 (forward moves; theme-level for 2/4, ticker-level for 3 — a deliberate thinning, stated). First breadth-threshold crossing → `gate` kind. Daily check, emit only on change → chain + mtime guard. Ledger dedup → `alerts_sent.jsonl`. Denominators → "k of n covered names". "Most daily checks find nothing" → no email when k = 0.
- **Placeholders:** none; every step has code or an exact command.
- **Types:** `diff_events` consumes `{"pairs": {key: int}, "gated": [str]}` everywhere; `render(e, snap, rows, ex, as_of)` matches its test; `parse(argv)` is defined in Task 4 and used only there; `plan_from_events(..., event_type, queries)` signature identical in Task 1 test and implementation.
