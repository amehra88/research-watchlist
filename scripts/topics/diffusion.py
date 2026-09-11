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
STAGE_EVIDENCE_SOURCES = ("mdna",)   # §6.3: the evidence clock is filings. Corprep speech (thr 0.30, P~0.31) drove
                                     # 3 of the 5 first spot-checked stage-2 pairs wrong; it stays a reported count
NEWLY_SAID_BASELINE = 2    # findings R5: absent from the filer's two prior quarters
_FIRM_ALIASES = {"bankofamerica": "bofa", "jpmorgansecurities": "jpmorgan", "jpmorgan": "jpmorgan"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] diffusion: {msg}", flush=True)


def load_rows(path: Path = TOPIC_MAP) -> list:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_exchange_meta(path: Path = EXCHANGES) -> dict:
    """vector_id -> the exchange fields the report needs (host_hint for §10, text for citations)."""
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
    """Spec §10: the host bank asks nearly every question at its own conference. Matched on
    normalised prefixes ('Goldman Sachs Communacopia +' vs 'Goldman Sachs & Co. LLC')."""
    f, h = firm_key(firm), firm_key(host_hint)
    if len(f) < 4 or len(h) < 4:
        return False
    lcp = 0
    for a, b in zip(f, h):
        if a != b:
            break
        lcp += 1
    return lcp >= min(6, len(f), len(h))   # 'citi' (4) matches whole; longer names need 6 shared chars


def _themes(r) -> list:
    return [t["theme"] if isinstance(t, dict) else t for t in (r.get("themes") or []) if t]


def apply_mdna_block_rule(rows, min_blocks: int = MDNA_MIN_BLOCKS) -> list:
    """Drop a theme from an MD&A row unless that filer has >= min_blocks blocks mapped to it in
    the same quarter. One block at thr 0.40 is ~half wrong (GLW derivatives -> foundry_capacity);
    two independent blocks from one filing rarely agree by accident. Exchange rows are untouched.
    Returns new row dicts; the input is not mutated."""
    n = collections.Counter()
    for r in rows:
        if r.get("source") == "mdna":
            for t in _themes(r):
                n[(t, r.get("cal_quarter"), r.get("ticker"))] += 1
    out = []
    for r in rows:
        if r.get("source") != "mdna":
            out.append(r)
            continue
        keep = [t for t in (r.get("themes") or [])
                if n[((t["theme"] if isinstance(t, dict) else t), r.get("cal_quarter"), r.get("ticker"))] >= min_blocks]
        out.append({**r, "themes": keep})
    return out


def metrics(rows, meta, mdna_min_blocks: int = MDNA_MIN_BLOCKS) -> dict:
    """{(theme, cal_quarter): counts}. Weighting for any ranking: n_banks > n_companies > n_exchanges."""
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


def denominators(rows) -> dict:
    """Companies with ANY row (mapped or not) per quarter, per event type — never merged (§4.1)."""
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


def quarters_in(rows) -> list:
    return sorted({r["cal_quarter"] for r in rows if r.get("cal_quarter")})


def newly_said(rows, baseline: int = NEWLY_SAID_BASELINE, mdna_min_blocks: int = MDNA_MIN_BLOCKS) -> list:
    """Findings R4/R5: (filer, theme) is newly said in quarter q when the filer has rows of that
    source in each of the `baseline` prior quarters and none of them carry the theme. Recurring
    boilerplate can never register — that is the point. A filer with no rows in a baseline
    quarter is skipped (unknown), never counted as new."""
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
    """Two quarters compared, nothing fitted. Sorted on n_banks delta, then n_companies (§5 weighting)."""
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
                    "first_evidence_date": p["first_evidence_date"], "first_filing_date": p["first_filing_date"],
                    "evidence_sources": sorted(p["evidence_sources"]),
                    "open_lag_days": lc.open_lag_days(p, as_of)})
    out.sort(key=lambda e: (not e["adjacent_asked"], -(e["open_lag_days"] or 0), e["theme"], e["ticker"]))
    return out


def _quarter_of(date_iso: str) -> str:
    y, m = int(date_iso[:4]), int(date_iso[5:7])
    return f"CY{y}-Q{(m - 1) // 3 + 1}"


def _date_span(rows, pred) -> tuple:
    ds = sorted(str(r.get("event_date") or "")[:10] for r in rows if pred(r) and r.get("event_date"))
    return (ds[0], ds[-1]) if ds else (None, None)


def build_snapshot(rows, meta, graph, as_of: str, no_coverage: dict | None) -> dict:
    rows = apply_mdna_block_rule(rows)          # single-block MD&A themes never reach a stage or a count
    qs = quarters_in(rows)
    cur = qs[-1] if qs else None
    prev = qs[-2] if len(qs) > 1 else None
    m = metrics(rows, meta)
    idx = lc.build_index([r for r in rows if r.get("register") == "question"
                          or (r.get("register") == "evidence" and r.get("source") in STAGE_EVIDENCE_SOURCES)])
    lags = [lc.lag_days(p["first_filing_date"], p["first_question_date"]) for p in idx.values()
            if p["first_filing_date"] and p["first_question_date"]]
    stage_counts = collections.Counter()
    stage1 = []
    for (theme, ticker), p in idx.items():
        st = lc.stage(idx, theme, ticker)
        stage_counts[st] += 1
        if st == 1 and p["first_evidence_date"]:
            stage1.append({"theme": theme, "ticker": ticker, "stage": 1, "first_evidence_date": p["first_evidence_date"],
                           "first_filing_date": p["first_filing_date"], "n_evidence": p["n_evidence"],
                           "evidence_sources": sorted(p["evidence_sources"]), "open_lag_days": lc.open_lag_days(p, as_of)})
    stage1.sort(key=lambda e: (-(e["open_lag_days"] or 0), e["theme"], e["ticker"]))
    pairs = []
    for (theme, ticker), p in sorted(idx.items()):
        pairs.append({"theme": theme, "ticker": ticker, "stage": lc.stage(idx, theme, ticker),
                      "first_evidence_date": p["first_evidence_date"], "first_filing_date": p["first_filing_date"],
                      "first_question_date": p["first_question_date"],
                      "lag_days": lc.lag_days(p["first_filing_date"], p["first_question_date"]),
                      "n_evidence": p["n_evidence"], "n_question": p["n_question"], "banks": sorted(p["banks"])})
    nc = no_coverage or {}
    excl = {"no_results": sorted(nc.get("no_results") or []), "incomplete": sorted(nc.get("incomplete") or []),
            "no_factset_id": sorted(x.get("ticker") for x in (nc.get("no_factset_id") or []) if x.get("ticker"))}
    q_span = _date_span(rows, lambda r: r.get("register") == "question")
    f_span = _date_span(rows, lambda r: r.get("source") == "mdna")
    notes = ["challenging_rate (spec §5) is not computed: exchange rows carry no challenging flag and 99% of "
             "analyst turns are sentiment=Neutral.",
             "P3 foreign evidence is not built: stages and lags use US MD&A evidence only; Chinese filers "
             "appear only in the exclusions list. Corprep transcript speech is reported as a count "
             "(n_corprep_companies) but does not set a stage: at its 0.30 threshold it mis-paired 3 of 5 "
             "spot-checked stage-2 rows.",
             f"MD&A counts need >= {MDNA_MIN_BLOCKS} mapped blocks per filer-quarter and are lower-confidence "
             "than transcript counts (mdna precision ~0.4 at its threshold).",
             f"The Tier-0 lag runs from MD&A filing dates only (corprep answers share the question's date). Both "
             f"windows are truncated — questions {q_span[0]}..{q_span[1]}, filings {f_span[0]}..{f_span[1]} — so a "
             "question dated before the first filing in the window can only look question-first (left-censoring); "
             "negative lags near the window start are not evidence against the premise.",
             "No trend lines by design: three or four observations per theme support a comparison, not a slope."]
    return {"as_of": as_of, "quarters": qs, "current_quarter": cur, "in_progress": bool(cur) and _quarter_of(as_of) == cur,
            "denominators": denominators(rows), "no_coverage": excl,
            "metrics": [dict(theme=t, cal_quarter=q, **v) for (t, q), v in sorted(m.items())],
            "movers": movers(m, cur, prev) if cur and prev else [],
            "stage_counts": {str(k): v for k, v in sorted(stage_counts.items()) if k},
            "lag_summary": lc.summarize(lags), "stage1": stage1,
            "stage2": detector_asked_elsewhere(idx, graph, as_of), "newly_said": newly_said(rows), "pairs": pairs,
            "notes": notes}


def write_report(snap: dict, path: Path = REPORT) -> str:
    d, cur = snap["denominators"], snap["current_quarter"]
    prev = snap["quarters"][-2] if len(snap["quarters"]) > 1 else None
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
    L.append("### Lifecycle (spec §6.3) — Tier-0 lag = first analyst question minus first MD&A filing, days")
    if s.get("n"):
        L.append(f"n={s['n']} (theme, company) pairs with both a filing and a question: min {s['min']}, p25 {s['p25']}, "
                 f"median {s['median']}, p75 {s['p75']}, max {s['max']}; evidence led in {s['share_evidence_led']}% "
                 f"({s['n_negative']} negative = question came first, {s['n_zero']} same-day). See the censoring note above.")
    L.append("Stage counts (theme, company): " + ", ".join(f"stage {k}: {v}" for k, v in snap["stage_counts"].items()))
    L.append("")
    L.append(f"### Stage 2 — asked at another name, not here ({len(snap['stage2'])}; verified-adjacent askers first)")
    L.append("| theme | company | adjacent asked (route, first question) | other askers | first evidence | open days | evidence |")
    L.append("|---|---|---|---|---|---|---|")
    for e in snap["stage2"][:60]:
        adj = "; ".join(f"{a['ticker']} ({','.join(a['routes'])}, {a['first_question_date']})" for a in e["adjacent_asked"]) or "—"
        others = ", ".join(e["other_asked"][:6]) + (f" +{len(e['other_asked']) - 6}" if len(e["other_asked"]) > 6 else "")
        L.append(f"| {e['theme']} | {e['ticker']} | {adj} | {others} | {e['first_evidence_date']} | "
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
        f"newly_said {len(snap['newly_said'])}, lag {snap['lag_summary']}")
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
        log("emailed")
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
