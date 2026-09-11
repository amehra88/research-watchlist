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


# ───────────────────────── CLI ─────────────────────────

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
