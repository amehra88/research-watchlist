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


# ───────────────────────── citations + rendering ─────────────────────────

def _theme_pairs(snap: dict, theme: str) -> list:
    return [p for p in snap.get("pairs", []) if p["theme"] == theme and p.get("stage")]


def _score(r: dict, theme: str) -> float:
    return max((t.get("score", 0.0) for t in r.get("themes") or [] if t.get("theme") == theme), default=0.0)


def first_question_cite(theme: str, ticker: str, date: str, rows: list, ex: dict) -> dict | None:
    """The highest-cosine analyst row for (theme, ticker) on `date`, joined to its exchange
    record for the speaker and firm — the same join theme_notes.citations_for uses."""
    cands = [r for r in rows if r.get("register") == "question" and r.get("ticker") == ticker
             and str(r.get("event_date") or "")[:10] == date and _score(r, theme) > 0 and r.get("id") in ex]
    if not cands:
        return None
    r = max(cands, key=lambda r: _score(r, theme))
    e = ex[r["id"]]
    return {"speaker": e.get("speaker_name") or "analyst", "firm": e.get("speaker_firm") or "?",
            "event": e.get("event_name") or r.get("event_type") or "?"}


def _days_ago(as_of: str, date: str | None) -> int | None:
    if not date:
        return None
    return (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(date[:10])).days


def _cite(theme, ticker, date, rows, ex) -> str:
    c = first_question_cite(theme, ticker, date, rows, ex)
    return f" ({c['speaker']}, {c['firm']})" if c else ""


def _note_link(theme: str) -> str:
    return f" → notes/themes/{theme}.md" if (THEMES_DIR / f"{theme}.md").exists() else ""


def render(e: dict, snap: dict, rows: list, ex: dict, as_of: str) -> str:
    theme = e["theme"]
    pairs = _theme_pairs(snap, theme)
    asked = [p for p in pairs if p.get("first_question_date")]
    n, k = len(pairs), len(asked)
    kind = e["kind"]
    if kind == "gate":
        cq = snap.get("current_quarter")
        cell = next((m for m in snap.get("metrics", []) if m["theme"] == theme and m.get("cal_quarter") == cq), {})
        return (f"`{theme}` crossed the breadth gate in {cq}: {cell.get('n_banks', 0)} banks / "
                f"{cell.get('n_companies', 0)} companies asked, {cell.get('n_disclosing', 0)} disclosing"
                f" → notes/themes/{theme}.md")
    if kind == "stage2":
        first = min(asked, key=lambda p: p["first_question_date"]) if asked else None
        unasked = sorted(p["ticker"] for p in pairs if not p.get("first_question_date"))
        fe = min((p["first_evidence_date"] for p in pairs if p.get("first_evidence_date")), default=None)
        head = f"`{theme}` moved to stage 2"
        if first:
            head += (f" — {first['ticker']} {first['first_question_date']}"
                     f"{_cite(theme, first['ticker'], first['first_question_date'], rows, ex)}.")
        else:
            head += "."
        still = f" {', '.join(unasked)} still unasked." if unasked else " No other carrier."
        ev = (f" First evidence {fe}, {_days_ago(as_of, fe)} days ago." if fe else " No filing evidence yet.")
        return head + still + ev + _note_link(theme)
    if kind == "stage3":
        ticker = e["ticker"]
        p = next((p for p in pairs if p["ticker"] == ticker), {})
        fq = p.get("first_question_date")
        when = f" — asked {fq}{_cite(theme, ticker, fq, rows, ex)}." if fq else "."
        return (f"`{theme}` moved to stage 3 at {ticker}{when} Asked at {k} of {n} covered names."
                + _note_link(theme))
    if kind == "stage4":
        return f"`{theme}` is now stage 4 (late): asked at {k} of {n} covered names." + _note_link(theme)
    raise ValueError(f"unknown event kind {kind!r}")


# ───────────────────────── state + ledger ─────────────────────────

def load_prior(path: Path = None) -> dict | None:
    path = path or STAGES
    if not Path(path).exists():
        return None
    return json.loads(Path(path).read_text())


def save_state(path: Path, as_of: str, pairs: dict, gated: list) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps({"as_of": as_of, "pairs": dict(sorted(pairs.items())), "gated": sorted(gated)},
                                     indent=1))


def sent_ids(path: Path = None) -> set:
    path = path or LEDGER
    out = set()
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if line.strip():
                try:
                    out.add(json.loads(line)["id"])
                except (ValueError, KeyError):
                    continue
    return out


def append_ledger(path: Path, events: list, ts: str, as_of: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a") as fh:
        for e in events:
            rec = {"id": event_id(e), "kind": e["kind"], "theme": e["theme"], "ticker": e.get("ticker"),
                   "ts": ts, "as_of": as_of}
            fh.write(json.dumps(rec, sort_keys=True) + "\n")


# ───────────────────────── run ─────────────────────────

def parse(argv=None):
    ap = argparse.ArgumentParser(description="P5b stage-transition alert (spec §7.3)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--email", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the lines; no email, no ledger, no state write")
    ap.add_argument("--force", action="store_true", help="compare even if diffusion.json is not newer than stages.json")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    return ap.parse_args(argv)


def run(args) -> int:
    if not DIFFUSION.exists():
        log(f"REFUSING: {DIFFUSION} missing — run diffusion.py --run first")
        return 2
    snap = json.loads(DIFFUSION.read_text())
    cur = {"pairs": snapshot_stages(snap), "gated": gated_themes(snap)}
    prior = load_prior(STAGES)
    if prior is None:
        save_state(STAGES, args.as_of, cur["pairs"], cur["gated"])
        log(f"seeded {len(cur['pairs'])} pairs, {len(cur['gated'])} gated themes -> {STAGES}; no email on a seed")
        return 0
    if not args.force and DIFFUSION.stat().st_mtime <= STAGES.stat().st_mtime:
        log(f"no new snapshot ({DIFFUSION.name} is not newer than {STAGES.name}); nothing to compare")
        return 0
    events = diff_events(prior, cur)
    already = sent_ids(LEDGER)
    fresh = [e for e in events if event_id(e) not in already]
    log(f"{len(cur['pairs'])} pairs vs prior {len(prior.get('pairs', {}))}: {len(events)} event(s), "
        f"{len(fresh)} not yet announced")
    if fresh:
        rows, ex, _ = load_sources()
        lines = [render(e, snap, rows, ex, args.as_of) for e in fresh]
    else:
        lines = []
    if args.dry_run:
        for ln in lines:
            print(ln)
        return 0
    if lines:
        subject = f"Theme stage alert — {args.as_of} ({len(lines)} event{'s' if len(lines) != 1 else ''})"
        body = "\n".join(f"- {ln}" for ln in lines) + "\n"
        if args.email:
            if send is None:
                raise RuntimeError("newsdigest.email_send unavailable; cannot --email")
            send(subject, body)
            log(f"emailed {len(lines)} line(s)")
        else:
            print(subject); print(body)
        append_ledger(LEDGER, fresh, dt.datetime.now(dt.timezone.utc).isoformat(), args.as_of)
    save_state(STAGES, args.as_of, cur["pairs"], cur["gated"])
    return 0


def main(argv=None) -> int:
    args = parse(argv)
    if not args.run:
        parse(["--help"])
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
