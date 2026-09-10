# P3b MD&A evidence (port + integrate) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the US evidence side (10-Q Item 2 / 10-K Item 7 MD&A prose, windowed, dated by `filed_date`) into `state/evidence/claims.jsonl` and feed it through P2 `topic_map` as evidence-register units, so §6.2's disclosure count and §6.3's `first_evidence_date` clock exist.

**Architecture:** Port `evidence_store.py` and `mdna_evidence.py` (+ their tests) from the unmerged branch `worktree-idea-surfacing-spec` into `scripts/topics/` unchanged except for imports, then fix the one spec violation (diff only within a form type), add the branch's housekeeping filter at unit construction, and teach `topic_map.units_from_claims()` to emit `Unit(register="evidence", source="mdna")` rows. The diff is a filter, not the signal (branch finding: ~75% of MD&A prose is rewritten each quarter) — topic-level novelty stays in P4.

**Tech Stack:** Python 3.12 stdlib (difflib), yaml; reuses P2's EmbedStore/anchors. No LLM calls.

**Spec:** `docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md` §4.3 (claim record, `first_evidence_date`), §4.4 (MD&A, form-type trap), §4.2 (same mapping function for both registers). Findings: `docs/superpowers/plans/2026-08-21-topic-space-findings.md` R1 (housekeeping filter).

## Global Constraints

- Every claim carries `first_evidence_date` (= `filed_date`); `make_claim` raises without it.
- Never diff across form types (10-Q↔10-Q, 10-K↔10-K only) — spec §4.4 trap.
- Claims are leads, not facts: `verified` is False on write.
- Housekeeping prose (accounting/financing/legal) never becomes a unit — it appears in every filer and sails through the 3-company gate.
- `state/evidence/claims.jsonl` is regenerable from `notes/sec/` → gitignored; `topic_map.jsonl` rows that point at claims are committed as today.
- auto_sync paused for the build (backup `/root/backups/crontab.pre_build_20260910_*.bak`); restore LAST.

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/topics/evidence_store.py` | claim record (`make_claim`, `claim_id`, `calendar_quarter`, `join_period_key`, `append_claims`) — ported verbatim |
| `scripts/topics/mdna_evidence.py` | notes/sec → MD&A section → QoQ added blocks (within form type) → claims; CLI `--dry-run/--ticker/--window-months` — ported + form-type fix |
| `scripts/topics/topic_map.py` | + `HOUSEKEEPING_CUES`, `is_housekeeping()`, `units_from_claims()`; `run()` reads both sources; report shows per-source coverage |
| `scripts/topics/test_evidence_store.py`, `test_mdna_evidence.py`, `test_topic_map.py` | direct-run tests |
| `state/evidence/claims.jsonl` | gitignored output |

---

### Task 1: Port `evidence_store` and `mdna_evidence` with their tests

- [x] **Step 1: Port** — `for f in evidence_store mdna_evidence test_evidence_store test_mdna_evidence; do git show worktree-idea-surfacing-spec:scripts/v3_ingest/$f.py > scripts/topics/$f.py; done`. In `mdna_evidence.py` the import is already same-directory (`sys.path.insert(0, dirname(__file__))`), so no change; confirm tests import by same-dir path.
- [x] **Step 2: Run** — `python3 scripts/topics/test_evidence_store.py` → 9/9; `python3 scripts/topics/test_mdna_evidence.py` → 11/11.
- [x] **Step 3: gitignore** — append `state/evidence/` (regenerable; ~10 MB, rewritten by every full run).
- [x] **Step 4: Commit** — `git add scripts/topics/{evidence_store,mdna_evidence,test_evidence_store,test_mdna_evidence}.py .gitignore && git commit -m "topics: port evidence_store + mdna_evidence (P3b) from worktree-idea-surfacing-spec"`

### Task 2: Diff only within a form type (spec §4.4 trap)

- [x] **Step 1: Failing test** (append to `test_mdna_evidence.py`):

```python
def test_claims_for_ticker_never_diffs_across_form_types():
    # spec §4.4: AMD's 10-K MD&A is ~174k chars vs its 10-Q at ~30k; a sequential diff reports
    # the whole 10-K as "new" every year. 10-Q diffs against the previous 10-Q, 10-K against 10-K.
    q1 = {"ticker": "X", "filed_date": "2026-02-01", "form_type": "10-Q", "document_id": "q1",
          "mdna": "Quarterly paragraph one that is long enough to pass the minimum word count filter for a block of prose here."}
    k  = {"ticker": "X", "filed_date": "2026-03-01", "form_type": "10-K", "document_id": "k",
          "mdna": "Annual paragraph that is entirely different and also long enough to pass the minimum word count filter for a block."}
    q2 = {"ticker": "X", "filed_date": "2026-05-01", "form_type": "10-Q", "document_id": "q2",
          "mdna": q1["mdna"] + "\nA second quarterly paragraph that is new this quarter and long enough to pass the minimum word count filter."}
    claims = me.claims_for_ticker([q1, k, q2])
    docs = [c["document_id"] for c in claims]
    assert docs == ["q2"], docs                      # the 10-K has no prior 10-K -> emits nothing
    assert claims[0]["text"].startswith("A second quarterly paragraph")
    assert claims[0]["form_type"] == "10-Q"
```

- [x] **Step 2: Run** → fails (`k` emitted, or `form_type` KeyError).
- [x] **Step 3: Implement** in `claims_for_ticker`: group `notes` by `form_type` family (`10-K`/`10-K/A` → "10-K"; `10-Q`/`10-Q/A` → "10-Q"; else the raw form), diff within each group in `filed_date` order, and pass `form_type` through `make_claim(..., form_type=...)`. In `evidence_store.make_claim` add an optional `form_type=None` field (append to `CLAIM_FIELDS` and the record); update `test_make_claim_has_exactly_the_declared_fields` accordingly.
- [x] **Step 4: Run** both suites green. **Step 5: Live** — `python3 scripts/topics/mdna_evidence.py --dry-run | tail -3` (expect fewer than the 9,607 of the cross-type diff; record the number), then `python3 scripts/topics/mdna_evidence.py` → `state/evidence/claims.jsonl`; re-run → `written: 0` (idempotent).
- [x] **Step 6: Commit** — `"topics: mdna diff only within a form type (spec §4.4); form_type on claims"`

### Task 3: Claims become evidence units in `topic_map`

- [x] **Step 1: Failing tests** (append to `test_topic_map.py`):

```python
def test_units_from_claims_drops_housekeeping_and_short_blocks():
    claims = [
        {"claim_id": "c1", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Demand for our datacom transceivers continued to exceed our capacity as hyperscale customers accelerated deployments of AI clusters."},
        {"claim_id": "c2", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Our 4.00% convertible senior notes due 2031 carry an aggregate principal amount that remains outstanding as of quarter end."},
        {"claim_id": "c3", "ticker": "COHR", "first_evidence_date": "2026-05-06", "period_key": "2026Q2", "form_type": "10-Q",
         "text": "Too short to count."},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "claims.jsonl"; p.write_text("\n".join(json.dumps(c) for c in claims) + "\n")
        units, skipped = tm.units_from_claims(p)
    assert [u.id for u in units] == ["c1"] and skipped == 2
    u = units[0]
    assert u.register == "evidence" and u.source == "mdna" and u.firm is None
    assert u.event_date == "2026-05-06" and u.period_key == "2026Q2" and u.event_type == "10-Q"


def test_is_housekeeping_keeps_capex_prose():
    assert tm.is_housekeeping("we recorded an impairment charge related to goodwill")
    assert not tm.is_housekeeping("cash paid for property and equipment was $7.7 billion, reflecting data center capacity additions")
```

- [x] **Step 2: Run** → `AttributeError: units_from_claims`.
- [x] **Step 3: Implement** in `topic_map.py`: paste the branch's `HOUSEKEEPING_CUES` + `is_housekeeping` (from `git show worktree-idea-surfacing-spec:scripts/v3_ingest/topic_map.py`, lines 134–160) and

```python
CLAIMS = REPO / "state" / "evidence" / "claims.jsonl"

def units_from_claims(path: Path = CLAIMS, min_words: int = MIN_UNIT_WORDS):
    """Evidence-register units from mdna_evidence's claims. Housekeeping prose is dropped
    here (findings R1): it appears in every filer, so the 3-company gate cannot filter it."""
    units, skipped = [], 0
    if not path.exists():
        return units, skipped
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = (r.get("text") or "").strip()
        if len(text.split()) < min_words or is_housekeeping(text):
            skipped += 1
            continue
        units.append(Unit(r["claim_id"], text, "evidence", r.get("ticker"), r.get("form_type") or "mdna",
                          r.get("first_evidence_date"), r.get("period_key"), None, source=r.get("source") or "mdna"))
    return units, skipped
```

  In `run()`: `units, skipped = units_from_exchanges(EXCHANGES)`; then `cu, cs = units_from_claims(); units += cu; skipped += cs` unless `--no-claims`; log counts per source. In `write_report`, add a coverage line per `source` (exchange vs mdna) next to the per-register line. Add `--no-claims` to argparse.
- [x] **Step 4: Run** all topic suites green.
- [ ] **Step 5: Live** — `topic_map.py --run` (embeds the new MD&A units once, ~5 min), then inspect: mapped share for `source=mdna`, candidate count and how many are MD&A-only. If MD&A-generic clusters flood the queue (>~20 evidence-only MD&A clusters of boilerplate), raise the evidence-only floor for `source=mdna`-only clusters to 4 companies and record the measurement; do NOT reintroduce a bank test. Then `--run --suggest-names`.
- [ ] **Step 6: Commit** — code + `state/topics/{topic_map.jsonl,candidates.json}` + `notes/reports/theme-candidates.md`: `"topics: MD&A claims as evidence units (housekeeping filter, source on rows) + live map"`

### Task 4: Cron, docs, memory, restore

- [x] **Step 1: Cron** — daily after SEC ingest (11:00, minutes): `30 12 * * * cd /root/research-watchlist && /root/bin/alert_on_failure.sh mdna_evidence python3 scripts/topics/mdna_evidence.py >> logs/mdna_evidence.log 2>&1` (no env needed: no API). Backup crontab first; verify count; `scripts/snapshot_crontab.sh`.
- [x] **Step 2: Docs** — ARCHITECTURE §4 (mdna_evidence row; topic_map now maps both sources), §8 idea-surfacing status "P1+P2+P3b built"; cost-model (P3b = 0 LLM calls; embeddings ~+7K units once); spec status header.
- [ ] **Step 3: Memory** — `mdna_evidence_p3b.md` + MEMORY.md line; update `resume_here.md` (next = P4 diffusion/lifecycle from the branch's `lifecycle.py`).
- [ ] **Step 4: Restore auto_sync** (uncomment `# PAUSED-BUILD-P3B`), verify 0 PAUSED, snapshot, commit, push.

## Deviations found in execution (2026-09-10)

- The shared `state/evidence/claims.jsonl` already held the branch's Aug-22 rows (no `form_type`); moved to
  `/root/backups/topics_branch_artifacts_20260822/` and regenerated: 8,459 claims / 209 filings / 73 filers
  (cross-type diff would have been 9,607).
- First combined map: MD&A mapped 88% at the global 0.30 but spot checks were misfilings (the branch's
  finding, reproduced on centered anchors). Fix: `anchors.py` calibrates per document group and writes
  `threshold_by_source` {exchange 0.30, mdna 0.40; sec_filing precision floor 0.35}; `map_units` takes a
  float or a per-source dict and rows carry `threshold`. Plus expense-line / cash-flow / dividend /
  tax-legislation housekeeping cues (the 12 MD&A-only candidate clusters were all of that kind).

## Self-review

- Spec coverage: §4.3 record shape + `first_evidence_date` (Task 1), §4.4 window + form-type trap (Task 2), §4.2 same mapping function for both registers (Task 3), R1 housekeeping (Task 3). P3 foreign evidence (CNINFO/StreetAccount) is NOT in this plan. §4.4's "newly said" framing is deliberately not claimed (branch measurement) — P4.
- Names used consistently: `units_from_claims`, `is_housekeeping`, `HOUSEKEEPING_CUES`, `Unit.source`, `make_claim(form_type=)`.
