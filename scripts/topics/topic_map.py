#!/usr/bin/env python3
"""P2 topic_map — exchanges -> theme assignments | new-theme candidates (spec §4.2).

Both registers (question = analyst, evidence = corprep) go through the same function
against the same vocabulary so §6.2's two-count gap is computable. Assignment is cosine
to pg-derived theme centroids (anchors.py) at the calibrated threshold; units below it
are clustered (greedy leader) and clusters clearing a company-and-bank floor become
candidates the operator names or rejects. The system never writes watchlist.yaml.

    python3 scripts/topics/topic_map.py --run                      # map everything, refresh candidates + report
    python3 scripts/topics/topic_map.py --run --suggest-names      # + one Haiku call per surfaced candidate
    python3 scripts/topics/topic_map.py --accept cand:ID --name new_theme_slug
    python3 scripts/topics/topic_map.py --reject cand:ID
    python3 scripts/topics/topic_map.py --report [--email]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
import textprep as tp                       # noqa: E402
from anchors import load_anchors, score_matrix  # noqa: E402
from embed_store import EmbedStore          # noqa: E402

STATE = REPO / "state" / "topics"
EXCHANGES = REPO / "state" / "transcripts" / "exchanges.jsonl"
TOPIC_MAP = STATE / "topic_map.jsonl"
CANDIDATES = STATE / "candidates.json"
DECISIONS = STATE / "decisions.jsonl"
REPORT = REPO / "notes" / "reports" / "theme-candidates.md"

MIN_SIM = 0.65           # candidate clustering cosine on CENTERED vectors. Measured 2026-09-10 on
                         # 5,951 unmapped units: 0.45 -> 176 candidates (top cluster 210 units, "supply;
                         # capacity; demand"), 0.55 -> 113, 0.65 -> 27 (top size 19), 0.75 -> 2.
                         # One operator reviews this; 27 is a queue, 113 is not.
MIN_UNIT_WORDS = 8       # below this there is no topic (205/3,744 analyst turns were acknowledgements)
MIN_COMPANIES = 3
MIN_BANKS = 2
MAX_THEMES = 3
REGISTER = {"analyst": "question", "corprep": "evidence"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] topic_map: {msg}", flush=True)


@dataclass
class Unit:
    id: str
    text: str
    register: str
    ticker: str
    event_type: str
    event_date: str
    period_key: str
    firm: str | None
    source: str = "exchange"


def center(V: np.ndarray, mean: np.ndarray) -> np.ndarray:
    """Remove the shared component, then re-normalise — the same transform the anchors use.
    Uncentered, cosine 0.82 grouped 140 unrelated turns into one 'pricing; supply' cluster."""
    Vc = np.asarray(V, dtype=np.float32) - np.asarray(mean, dtype=np.float32)
    n = np.linalg.norm(Vc, axis=1, keepdims=True); n[n == 0] = 1.0
    return Vc / n


def units_from_exchanges(path: Path = EXCHANGES, min_words: int = MIN_UNIT_WORDS):
    units, skipped = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        reg = REGISTER.get(r.get("speaker_type"))
        if not reg or len(tp.clean_text(r.get("text") or "").split()) < min_words:
            skipped += 1                       # operator/untyped speaker, or no topic left after cleaning
            continue
        units.append(Unit(r["vector_id"], r["text"], reg, r.get("ticker"), r.get("event_type"),
                          r.get("event_date"), r.get("period_key"), r.get("speaker_firm") or None))
    return units, skipped


def assign(scores: np.ndarray, names: list, thr: float, top: int = MAX_THEMES) -> list:
    idx = [int(j) for j in np.argsort(-scores) if scores[j] >= thr][:top]
    return [(names[j], round(float(scores[j]), 4)) for j in idx]


def cluster_candidates(vectors: np.ndarray, min_sim: float) -> list:
    """Greedy leader clustering: each unit joins the first leader with cosine >= min_sim,
    else founds a cluster. Deterministic in input order (sort units by id first)."""
    leaders, members = [], []
    for i in range(len(vectors)):
        if leaders:
            sims = vectors[i] @ np.vstack([vectors[l] for l in leaders]).T
            j = int(np.argmax(sims))
            if sims[j] >= min_sim:
                members[j].append(i)
                continue
        leaders.append(i); members.append([i])
    return members


def build_candidates(clusters, units, texts, df, n_docs, min_companies=MIN_COMPANIES,
                     min_banks=MIN_BANKS) -> list:
    out = []
    for idxs in clusters:
        mem = [units[i] for i in idxs]
        companies = {u.ticker for u in mem if u.ticker}
        banks = {u.firm for u in mem if u.register == "question" and u.firm}
        if len(companies) < min_companies or len(banks) < min_banks:
            continue
        mem_sorted = sorted(mem, key=lambda u: (u.event_date or "9999", u.register != "question", u.id))  # questions lead
        ngr = tp.label_ngrams([texts[i] for i in idxs], df, n_docs)
        out.append({
            "id": f"cand:{mem_sorted[0].id}",
            "label": ngr[0] if ngr else mem_sorted[0].id,
            "ngrams": ngr,
            "n_exchanges": len(mem), "n_companies": len(companies), "n_banks": len(banks),
            "tickers": sorted(companies), "firms": sorted(banks),
            "first_seen": mem_sorted[0].event_date,
            "members": sorted(u.id for u in mem),
            "examples": [{"id": u.id, "ticker": u.ticker, "date": u.event_date, "firm": u.firm,
                          "text": tp.clean_text(u.text)[:280]} for u in mem_sorted[:3]],
            "status": "pending", "name": None, "suggested_name": None,
        })
    out.sort(key=lambda c: (-c["n_banks"], -c["n_companies"], -c["n_exchanges"], c["id"]))
    return out


def reattach_decisions(cands: list, decisions: list) -> list:
    for c in cands:
        best, best_j = None, 0.0
        m = set(c["members"])
        for d in decisions:
            dm = set(d.get("members") or [])
            j = len(m & dm) / len(m | dm) if m | dm else 0.0
            if j > best_j:
                best, best_j = d, j
        if best and best_j >= 0.5:
            c["status"], c["name"] = best["status"], best.get("name")
    return cands


def map_units(units, store, names, anchors, thr, min_sim=MIN_SIM, min_companies=MIN_COMPANIES,
              min_banks=MIN_BANKS, log_fn=None, mean=None):
    units = sorted(units, key=lambda u: u.id)
    texts = [tp.clean_text(u.text) or u.text for u in units]
    store.ensure([(u.id, t) for u, t in zip(units, texts)], log=log_fn)
    V = store.matrix([u.id for u in units])
    S = score_matrix(V, anchors, mean=mean)
    rows, unmapped = [], []
    for i, u in enumerate(units):
        themes = assign(S[i], names, thr)
        rows.append({**asdict(u), "themes": [{"theme": t, "score": s} for t, s in themes],
                     "best": round(float(S[i].max()), 4) if len(names) else None, "candidate": None})
        if not themes:
            unmapped.append(i)
    cands = []
    if unmapped:
        Vu = center(V[unmapped], mean) if mean is not None else V[unmapped]
        clusters = cluster_candidates(Vu, min_sim)
        clusters = [[unmapped[k] for k in cl] for cl in clusters]
        df = tp.doc_frequencies(texts)
        cands = build_candidates(clusters, units, texts, df, len(texts), min_companies, min_banks)
        member_to_cand = {m: c["id"] for c in cands for m in c["members"]}
        for r in rows:
            r["candidate"] = member_to_cand.get(r["id"])
    for r in rows:
        r.pop("text", None)                       # the text lives in exchanges.jsonl; keep the map slim
    return rows, cands


def record_decision(cand_id: str, status: str, name: str | None, cands_path: Path = CANDIDATES,
                    decisions_path: Path = DECISIONS) -> dict:
    cands = json.loads(cands_path.read_text()) if cands_path.exists() else []
    by = {c["id"]: c for c in cands}
    if cand_id not in by:
        raise KeyError(f"unknown candidate {cand_id}")
    c = by[cand_id]
    c["status"], c["name"] = status, name
    dec = {"id": cand_id, "members": list(c["members"]), "status": status, "name": name,
           "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    with decisions_path.open("a") as fh:
        fh.write(json.dumps(dec) + "\n")
    cands_path.write_text(json.dumps(cands, indent=1))
    return dec


def _slug(s: str) -> str:
    import re
    s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
    return s[:48]


def _default_runner(prompt: str) -> str:
    from lib import claude_p
    text, _, _ = claude_p.run(prompt, system_prompt="You name investment research themes. Reply in the exact two-line format requested.",
                              tools="", model="claude-haiku-4-5-20251001", timeout=120)
    return text


def suggest_names(cands: list, max_calls: int = 40, runner=None) -> list:
    runner = runner or _default_runner
    n = 0
    for c in cands:
        if c.get("status") != "pending" or c.get("suggested_name") or n >= max_calls:
            continue
        ex = "\n".join(f"- {e.get('text', '')[:240]}" for e in c.get("examples", [])[:3])
        prompt = ("Analysts on earnings calls and sell-side conferences raised the following topic, which does not "
                  "match any existing theme. Give it a short theme name (2-4 words, like 'neocloud demand' or "
                  "'china laser competition') and one line on why.\n"
                  f"Key phrases: {', '.join(c.get('ngrams', [])[:8])}\nExamples:\n{ex}\n\n"
                  "Reply exactly:\nNAME: <name>\nWHY: <one line>")
        try:
            text = runner(prompt)
        except Exception as e:  # noqa: BLE001
            log(f"  suggest_names {c['id']}: {type(e).__name__}: {str(e)[:120]}")
            continue
        n += 1
        for line in (text or "").splitlines():
            if line.upper().startswith("NAME:"):
                c["suggested_name"] = _slug(line.split(":", 1)[1])
            elif line.upper().startswith("WHY:"):
                c["suggested_why"] = line.split(":", 1)[1].strip()[:200]
    return cands


def write_report(rows: list, cands: list, meta: dict, skipped: int, path: Path = REPORT) -> str:
    def share(reg):
        r = [x for x in rows if x["register"] == reg]
        m = sum(1 for x in r if x["themes"])
        return f"{reg} register: {m}/{len(r)} mapped ({(m / len(r)):.0%})" if r else f"{reg} register: 0/0 mapped"
    cal = next((c for c in meta.get("calibration", []) if c["threshold"] == meta.get("threshold")), {})
    today = dt.date.today().isoformat()
    L = [f"## Theme candidates — {today}", "",
         f"Anchors: {len(meta.get('names', []))} themes; threshold {meta.get('threshold')} "
         f"(held-out P {cal.get('precision', '?')} / R {cal.get('recall', '?')} on {meta.get('n_test', '?')} labelled chunks).",
         f"Coverage: {share('question')}; {share('evidence')}; {skipped} rows skipped (operator/untyped speakers).",
         "A unit maps when its cosine to a theme centroid clears the threshold; the rest are clustered and only "
         f"clusters with >= {MIN_COMPANIES} companies and >= {MIN_BANKS} banks are listed. The system never edits "
         "`config/watchlist.yaml` — accept with `topic_map.py --accept <id> --name <slug>`, reject with `--reject <id>`.", ""]
    pending = [c for c in cands if c["status"] == "pending"]
    L.append(f"### Pending candidates ({len(pending)} of {len(cands)})")
    L.append("")
    L.append("| id | suggested | n_banks | n_companies | n_exch | first_seen | tickers | phrases |")
    L.append("|---|---|---|---|---|---|---|---|")
    for c in pending:
        L.append(f"| `{c['id']}` | {c.get('suggested_name') or ''} | {c['n_banks']} | {c['n_companies']} | {c['n_exchanges']} | "
                 f"{c['first_seen']} | {', '.join(c['tickers'][:8])} | {'; '.join(c['ngrams'][:5])} |")
    L.append("")
    for c in pending:
        L.append(f"#### `{c['id']}` — {c.get('suggested_name') or c['label']}")
        if c.get("suggested_why"):
            L.append(f"_{c['suggested_why']}_")
        L.append(f"Banks: {', '.join(c['firms'])}")
        for e in c["examples"]:
            L.append(f"- **{e['ticker']} {e['date']}** ({e.get('firm') or 'corprep'}): {e['text']}")
        L.append("")
    decided = [c for c in cands if c["status"] != "pending"]
    if decided:
        L.append("### Decided")
        for c in decided:
            L.append(f"- `{c['id']}` {c['status']}" + (f" as `{c['name']}`" if c.get("name") else ""))
        L.append("")
    text = "\n".join(L)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


def _load_decisions(path: Path = DECISIONS) -> list:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def run(args) -> int:
    names, A, mean, meta = load_anchors()
    thr = args.threshold if args.threshold is not None else meta["threshold"]
    units, skipped = units_from_exchanges(EXCHANGES)
    log(f"units {len(units)} ({sum(u.register == 'question' for u in units)} question / "
        f"{sum(u.register == 'evidence' for u in units)} evidence), {skipped} skipped; thr={thr} min_sim={args.min_sim}")
    store = EmbedStore(STATE)
    rows, cands = map_units(units, store, names, A, thr, args.min_sim, args.min_companies, args.min_banks,
                            log_fn=log, mean=mean)
    cands = reattach_decisions(cands, _load_decisions())
    if args.suggest_names:
        cands = suggest_names(cands)
    STATE.mkdir(parents=True, exist_ok=True)
    with TOPIC_MAP.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    CANDIDATES.write_text(json.dumps(cands, indent=1))
    text = write_report(rows, cands, meta, skipped)
    mapped = sum(1 for r in rows if r["themes"])
    log(f"mapped {mapped}/{len(rows)}; candidates {len(cands)} "
        f"({sum(c['status'] == 'pending' for c in cands)} pending) -> {REPORT}")
    if args.email:
        from newsdigest.email_send import send
        send(f"Theme candidates {dt.date.today().isoformat()}", text)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P2 topic_map (spec §4.2)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--suggest-names", action="store_true", help="one Haiku call per pending candidate (<=40)")
    ap.add_argument("--threshold", type=float, help="override the calibrated anchor threshold")
    ap.add_argument("--min-sim", type=float, default=MIN_SIM)
    ap.add_argument("--min-companies", type=int, default=MIN_COMPANIES)
    ap.add_argument("--min-banks", type=int, default=MIN_BANKS)
    ap.add_argument("--accept", metavar="ID"); ap.add_argument("--name")
    ap.add_argument("--reject", metavar="ID")
    ap.add_argument("--report", action="store_true", help="re-render the note from the saved state")
    ap.add_argument("--email", action="store_true")
    a = ap.parse_args(argv)
    if a.accept:
        if not a.name:
            ap.error("--accept needs --name <snake_case_slug>")
        d = record_decision(a.accept, "accepted", _slug(a.name)); print(json.dumps(d)); return 0
    if a.reject:
        d = record_decision(a.reject, "rejected", None); print(json.dumps(d)); return 0
    if a.report:
        rows = [json.loads(l) for l in TOPIC_MAP.read_text().splitlines() if l.strip()]
        cands = json.loads(CANDIDATES.read_text())
        _, _, _, meta = load_anchors()
        text = write_report(rows, cands, meta, skipped=0)
        if a.email:
            from newsdigest.email_send import send
            send(f"Theme candidates {dt.date.today().isoformat()}", text)
        print(text); return 0
    if a.run:
        return run(a)
    ap.error("one of --run / --accept / --reject / --report")


if __name__ == "__main__":
    sys.exit(main())
