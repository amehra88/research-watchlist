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
_EMPTY_PRESSURE = {"confirm": 0, "challenge": 0, "window_days": 90, "last_evidence": None}


class OverreadError(ValueError):
    pass


def pick_mode(scores: dict, earnings_notes: list) -> str:
    if scores:
        return "scores"
    return "notes" if earnings_notes else "thin"


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
    tier, e = tio.watchlist_entry(ticker, w)
    scores = tio.watchlist_scores(ticker, w)
    notes = _latest_notes(ticker)
    mode = pick_mode(scores, notes)
    score_notes = {}
    for k in ("ai_positioning", "competitive_advantage", "potential_investor_interest"):
        v = e.get(k)
        if isinstance(v, dict) and v.get("notes"):
            score_notes[k] = v["notes"]
        if isinstance(v, dict):   # nested notes under competitive_advantage sub-keys
            for sk, sv in v.items():
                if isinstance(sv, dict) and sv.get("notes"):
                    score_notes[f"{k}.{sk}"] = sv["notes"]
    return {"ticker": ticker, "mode": mode, "tier": tier, "scores": scores,
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
                    "pressure": dict(_EMPTY_PRESSURE), "draft": True})
    return out


def _field(block: str, label: str) -> str:
    m = re.search(rf"\*\*{label}:\*\*\s*(.+?)(?=\n\*\*|\n\n|\Z)", block, re.S)
    if not m:
        return ""
    v = re.sub(r"\*\((?:CORRECTED|revised|operator)[^)]*\)\*", "", m.group(1))   # drop the doc's audit annotations
    return re.sub(r"\s+", " ", v).strip()


def _split(s: str) -> list[str]:
    return [x.strip(" .") for x in re.split(r";", s.replace("\n", " ")) if x.strip(" .")]


def import_draft_doc() -> dict[str, list[dict]]:
    """COHR/LITE assumptions from docs/thesis-assumptions-draft.md (### `id` sections).

    The doc repeats an id when the operator revisited it (COHR `chinese_laser_capability`
    appears twice); later sections only FILL fields the first left empty, so each id
    imports once.
    """
    text = DRAFT_DOC.read_text(encoding="utf-8")
    out: dict[str, dict[str, dict]] = {}
    ticker = None
    for block in re.split(r"\n(?=#{2,3} )", text):
        h = block.split("\n", 1)[0]
        tm = re.match(r"## ([A-Z]{2,5}) ", h)
        if tm:
            ticker = tm.group(1); continue
        m = re.match(r"### `([a-z0-9_]+)`", h)
        if not (m and ticker):
            continue
        aid = m.group(1)
        entry = {"id": aid, "statement": _field(block, "Statement"),
                 "derived_from": _field(block, "Derived from") or "operator",
                 "themes": [], "challenged_by": _split(_field(block, "Challenged by")),
                 "confirmed_by": _split(_field(block, "Confirmed by")), "status": "open", "status_source": "operator",
                 "pressure": dict(_EMPTY_PRESSURE), "draft": False}
        if "policy_shelter" in aid:
            entry["status"] = "retired"
            entry["statement"] = entry["statement"] or "Policy shelter is a watch item, not an assumption (operator 2026-08-21)."
            entry["challenged_by"] = entry["challenged_by"] or _split(_field(block, "Would become relevant if")) or ["operator to specify"]
        if aid == "chinese_laser_capability" and ticker == "LITE":
            entry["statement"] = entry["statement"] or "Shared with COHR: Chinese vendors have not yet closed the high-end laser gap (see COHR)."
        entry["challenged_by"] = entry["challenged_by"] or ["operator to specify"]
        per = out.setdefault(ticker, {})
        if aid in per:
            for k, v in entry.items():
                if v and not per[aid].get(k):
                    per[aid][k] = v
        else:
            per[aid] = entry
    return {t: list(d.values()) for t, d in out.items()}


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
        text, cost, _ = claude_p.run(build_prompt(i), system_prompt=SYSTEM, model=MODEL, cwd=str(REPO), timeout=600)
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
        except (OverreadError, json.JSONDecodeError, KeyError, ValueError) as e:
            ledger[t] = {"status": "failed", "error": f"{type(e).__name__}: {str(e)[:200]}"}; print(f"{t}: FAILED {type(e).__name__}: {e}")
        except RuntimeError as e:   # claude -p failure: fail loud, stop the batch
            ledger[t] = {"status": "failed", "error": str(e)[:200]}
            LEDGER.write_text(json.dumps(ledger, indent=1)); print(f"{t}: ABORT {e}"); return 1
        if not a.dry_run:
            LEDGER.write_text(json.dumps(ledger, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
