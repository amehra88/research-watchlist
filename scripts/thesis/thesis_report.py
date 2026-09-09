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


def _rel(p: Path) -> str:
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


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
    rows = [{"kind": k, "date": today.isoformat(), "since": since, "path": _rel(note), "questions_added": nq, "ts": ts}
            for k in ([kind] + (["weekly"] if kind == "quarterly" else []))]
    _append(STATE_DIR / "reports_sent.jsonl", rows)
    print(f"sent '{subject}'; note {_rel(note)}; movers {len(ctx['movers'])}; +{nq} questions")
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
            ev.append({"id": f"note:{p.parent.name}:{p.name}", "ticker": p.parent.name, "text": f"earnings note landed: {_rel(p)}"})
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
