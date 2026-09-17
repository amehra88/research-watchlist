#!/usr/bin/env python3
"""Daily: match new evidence against each ticker's assumptions; update _thesis.md pressure.

    python3 scripts/thesis/match_evidence.py                       # all T1+T2 since watermarks (cron)
    python3 scripts/thesis/match_evidence.py --ticker COHR,LITE --since 2026-08-01 --dry-run
    python3 scripts/thesis/match_evidence.py --max-tickers 20      # bound a catch-up run
    python3 scripts/thesis/match_evidence.py --ticker COHR --since 2026-08-01 --max-batches 40   # backfill

One claude -p per batch of new evidence (CHAR_CAP chars); tickers with nothing new cost nothing.
Evidence already in the log (any verdict, including neutral) is never re-sent. A 429 or auth
failure aborts the run (precheck) — never grind. The watermark advances only past what was sent,
and never regresses.
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
from thesis import STATE_DIR, extract_json, save_failed_reply, thesis_io as tio   # noqa: E402
from thesis import score_reads                              # noqa: E402
from thesis.sources import Evidence, collect_all           # noqa: E402

MODEL = "claude-sonnet-4-6"
LOG = STATE_DIR / "evidence_log.jsonl"
CHANGES = STATE_DIR / "changes.jsonl"
WATERMARKS = STATE_DIR / "watermarks.json"
CHAR_CAP = 12_000
DEFAULT_MAX_BATCHES = 3
DEFAULT_LOOKBACK_DAYS = 3
SYSTEM = "You are a buy-side analyst testing thesis assumptions against new evidence. Output JSON only."


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
    for i, e in enumerate(evidence):
        lines.append(f"[{i}] {e.source} {e.date} {e.title}{' (cross-ticker)' if e.cross_ticker else ''}\n{e.text}\n")
    lines.append("""
For EVERY index above return one verdict. Match to an assumption ONLY when the item bears on that assumption's
challenged_by or confirmed_by conditions; otherwise assumption_id null and direction neutral. strength: 1 = weak/indirect,
2 = clear but single-source or secondary, 3 = primary disclosure that directly meets a stated condition. quote <= 200 chars, verbatim.
Output JSON only: {"verdicts": [{"i": 0, "assumption_id": "..."|null, "direction": "confirm"|"challenge"|"neutral", "strength": 0-3, "why": "...", "quote": "..."}]}""")
    return "\n".join(lines)


def parse_verdicts(text: str, evidence: list[Evidence], valid_ids: set[str]) -> list[dict]:
    data = extract_json(text)
    out = []
    for v in data.get("verdicts", []):
        i = v.get("i")
        if not isinstance(i, int) or i < 0 or i >= len(evidence):
            continue
        aid = v.get("assumption_id")
        if aid not in valid_ids:
            aid = None
        direction = v.get("direction") if v.get("direction") in ("confirm", "challenge", "neutral") else "neutral"
        try:
            strength = min(3, max(0, int(v.get("strength") or 0)))
        except (TypeError, ValueError):
            strength = 0
        if aid is None or direction == "neutral":
            aid, direction, strength = None, "neutral", 0
        e = evidence[i]
        out.append({"source": e.source, "source_id": e.source_id, "ref": e.ref, "date": e.date, "title": e.title,
                    "assumption_id": aid, "direction": direction, "strength": strength,
                    "why": (v.get("why") or "")[:300], "quote": (v.get("quote") or "")[:200], "cross_ticker": e.cross_ticker})
    return out


def lift_score_recs(note_text: str, note_id: str | None = None, applied: dict | None = None,
                     out_path: Path | None = None) -> dict[str, str]:
    """Explicit score-recommendation lines (all six verb forms) in an earnings/conference note, by score key.

    Returns axis -> value only for proposal-worthy verbs (drift/revise/propose); hold/populate are
    reaffirmations and never appear in the returned dict -- this is the semantics run_ticker's
    proposed_scores logic has always relied on, unchanged.

    When note_id is given (a live ingest, not a dry run), every parsed recommendation -- all six
    verbs, not just the proposal-worthy three -- is additionally recorded as a row in
    state/thesis/score_reads.jsonl via score_reads.parse_recs/build_rows/append_rows, so
    reaffirmations ('hold at', 'Populate as') leave a record too.
    """
    recs = score_reads.parse_recs(note_text)
    out = {r["axis"]: r["value"] for r in recs if r["verb"] in ("drift", "revise", "propose")}
    if note_id is not None:
        ts = datetime.now(timezone.utc).isoformat()
        rows = score_reads.build_rows(note_id, note_text, applied, ts)
        score_reads.append_rows(out_path or score_reads.SCORE_READS, rows)
    return out


def score_rec_text(e: Evidence) -> str | None:
    """Full note text to hand to lift_score_recs, or None if `e` carries no §5/§6/§7.

    earnings_note Evidence.text already keeps §5/6/7 (collectors.earnings_notes_since's
    section allowlist includes them) -- use it as-is, no extra disk read. conference
    Evidence.text is stripped to §2-4 (the evidence-matching prompt only needs the
    Q&A/guidance sections), so §5/6/7 is never in it; for a file-backed conference note
    (source_id is a real notes/<T>/...-conf-*.md path, not a pg-derived "exch:..." id)
    read the file fresh to recover them. The evidence-matching text (e.text) itself is
    untouched either way.
    """
    if e.source == "earnings_note":
        return e.text
    if e.source == "conference" and e.source_id.startswith("notes/") and e.source_id.endswith(".md"):
        try:
            return (REPO / e.source_id).read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"WARN score_rec_text: could not read {e.source_id}: {exc}", file=sys.stderr)
            return None
    return None


def rows_from_4b(note_text: str, e: Evidence, valid_ids: set[str]) -> list[dict]:
    """§4b 'Assumption read' lines become strength-3 rows with source earnings_break/earnings_confirm."""
    sec = re.search(r"## 4b\..*?(?=\n## |\Z)", note_text, re.S)
    if not sec:
        return []
    rows = []
    for m in re.finditer(r"^- `?([a-z0-9_]+)`?:\s*\**(Confirm|Challenge|Silent)\**\b\s*[—-]?\s*(.*)$", sec.group(0), re.M):
        aid, verdict, why = m.groups()
        if aid not in valid_ids or verdict == "Silent":
            continue
        rows.append({"source": "earnings_break" if verdict == "Challenge" else "earnings_confirm", "source_id": e.source_id + f"#4b:{aid}",
                     "ref": e.ref, "date": e.date, "title": e.title, "assumption_id": aid,
                     "direction": "challenge" if verdict == "Challenge" else "confirm", "strength": 3, "why": why[:300], "quote": "", "cross_ticker": False})
    return rows


def batches(evidence: list[Evidence], char_cap: int = CHAR_CAP) -> list[list[Evidence]]:
    """Split in order into prompt-sized batches; an oversized single item gets its own batch."""
    out, cur, used = [], [], 0
    for e in evidence:
        n = len(e.text) + len(e.title) + 40
        if cur and used + n > char_cap:
            out.append(cur); cur, used = [], 0
        cur.append(e); used += n
    if cur:
        out.append(cur)
    return out


def _read_log() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def _append(path: Path, rows: list[dict]):
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _ask(fm: dict, sent: list[Evidence], valid: set[str]) -> list[dict]:
    prompt = build_prompt(fm, sent)
    text, cost, _ = claude_p.run(prompt, system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=600, precheck=_precheck)
    try:
        return parse_verdicts(text, sent, valid)
    except (json.JSONDecodeError, KeyError, AttributeError):
        save_failed_reply(f"{fm['ticker']}-match-1", text)
        text, cost, _ = claude_p.run(prompt + "\nReturn ONLY the JSON object.", system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=600, precheck=_precheck)
        try:
            return parse_verdicts(text, sent, valid)
        except (json.JSONDecodeError, KeyError, AttributeError):
            save_failed_reply(f"{fm['ticker']}-match-2", text)
            raise


def run_ticker(ticker: str, since: date, today: date, dry_run: bool = False, watchlist: dict | None = None,
               max_batches: int = DEFAULT_MAX_BATCHES) -> dict:
    fm = tio.load(ticker)
    if not fm:
        return {"ticker": ticker, "skipped": "no-thesis"}
    log = _read_log()
    mine = [r for r in log if r["ticker"] == ticker]
    seen_src = {r["source_id"].split("#4b:")[0] for r in mine}
    evidence = [e for e in collect_all(ticker, since) if e.source_id not in seen_src]
    stats = {"ticker": ticker, "evidence": len(evidence), "sent": 0, "batches": 0, "rows": 0, "changes": 0}
    if not evidence:
        return stats
    valid = {a["id"] for a in fm["assumptions"] if a.get("status") != "retired"}
    ts = datetime.now(timezone.utc).isoformat()
    rows, change_rows = [], []
    # earnings notes: §4b verdicts are lifted without an LLM call; earnings + conference
    # notes both get their explicit score recommendations (§5/§6/§7) lifted the same way
    for e in evidence:
        if e.source == "earnings_note":
            rows += rows_from_4b(e.text, e, valid)
        rec_text = score_rec_text(e)
        if rec_text is None:
            continue
        # score_reads.jsonl is a real filesystem write: skip it on --dry-run like every other side effect below
        note_id = e.source_id[len("notes/"):] if e.source_id.startswith("notes/") else e.source_id
        rec_kwargs = {} if dry_run else {"note_id": note_id, "applied": fm.get("scores", {})}
        for k, v in lift_score_recs(rec_text, **rec_kwargs).items():
            cur = (fm.setdefault("proposed_scores", {}) or {}).get(k) or {}
            if fm.get("scores", {}).get(k) != v and cur.get("value") != v:
                fm["proposed_scores"][k] = {"value": v, "since": e.date, "source": e.source_id}
                change_rows.append({"ts": ts, "ticker": ticker, "kind": "proposed_score", "key": k, "value": v, "source": e.source_id})
    all_batches = batches(evidence)
    to_send = all_batches[:max_batches]
    sent = [e for b in to_send for e in b]
    for n, b in enumerate(to_send, 1):
        print(f"  {ticker} batch {n}/{len(all_batches)}: {len(b)} items ({sum(len(e.text) for e in b)} chars)", flush=True)
        rows += _ask(fm, b, valid)
        stats["batches"] += 1
    stats["sent"] = len(sent)
    existing = {f"{r['source_id']}|{r.get('assumption_id')}" for r in mine}
    new_rows, seen_new = [], set()
    for r in rows:
        k = f"{r['source_id']}|{r.get('assumption_id')}"
        if k in existing or k in seen_new:
            continue
        seen_new.add(k); new_rows.append(dict(r, ts=ts, ticker=ticker))
    stats["rows"] = len(new_rows)
    # score mirror: operator edits to the watchlist clear matching proposals
    live = tio.watchlist_scores(ticker, watchlist)
    if live != fm.get("scores"):
        fm["scores"] = live
        for k in list(fm.get("proposed_scores") or {}):
            if live.get(k) == fm["proposed_scores"][k]["value"]:
                del fm["proposed_scores"][k]
    tio.recompute_pressure(fm, mine + new_rows, today)
    change_rows += [dict(c, ts=ts, ticker=ticker, kind="status") for c in fm["_changes"]]
    stats["changes"] = len(change_rows)
    caught_up = len(to_send) == len(all_batches)
    stats["caught_up"] = caught_up
    if dry_run:
        print(json.dumps({"ticker": ticker, "new_rows": new_rows, "changes": change_rows, "proposed": fm.get("proposed_scores"),
                          "caught_up": caught_up}, indent=1, ensure_ascii=False))
        return stats
    _append(LOG, new_rows)
    if change_rows:
        _append(CHANGES, change_rows)
    tio.save(ticker, fm)
    wm = json.loads(WATERMARKS.read_text()) if WATERMARKS.exists() else {}
    new_wm = today.isoformat() if caught_up else max(e.date for e in sent)
    wm[ticker] = max(wm.get(ticker, ""), min(new_wm, today.isoformat()))
    WATERMARKS.write_text(json.dumps(wm, indent=1, sort_keys=True))
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker"); ap.add_argument("--since"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-tickers", type=int, default=0)
    ap.add_argument("--max-batches", type=int, default=DEFAULT_MAX_BATCHES, help="claude -p calls per ticker per run")
    a = ap.parse_args(argv)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today()
    wm = json.loads(WATERMARKS.read_text()) if WATERMARKS.exists() else {}
    w = yaml.safe_load((REPO / "config" / "watchlist.yaml").read_text())
    tickers = a.ticker.split(",") if a.ticker else [t for t in tio.universe() if not t.endswith(".pvt")]
    if a.max_tickers:
        tickers = tickers[:a.max_tickers]
    totals = {"tickers": 0, "evidence": 0, "sent": 0, "batches": 0, "rows": 0, "changes": 0}
    for t in tickers:
        since = date.fromisoformat(a.since) if a.since else date.fromisoformat(wm.get(t, (today - timedelta(days=DEFAULT_LOOKBACK_DAYS)).isoformat()))
        try:
            s = run_ticker(t, since, today, dry_run=a.dry_run, watchlist=w, max_batches=a.max_batches)
        except SessionLimitError as e:
            print(f"ABORT session limit at {t}: {e}"); return 2
        except RuntimeError as e:
            print(f"ABORT {t}: {e}"); return 1
        print(f"{t}: {s}", flush=True)
        for k in totals:
            totals[k] += s.get(k, 0) if k != "tickers" else 1
    print("DONE", json.dumps(totals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
