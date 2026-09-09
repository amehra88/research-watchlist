#!/usr/bin/env python3
"""Weekly InsiderScore pull for T1+T2: open-market Buy/Sell, 10b5-1 EXCLUDED (the load-bearing split
from the COHR/LITE analysis — pre-planned sales say nothing about conviction).

    python3 scripts/thesis/insider_pull.py [--days 7] [--ticker COHR,LITE] [--dry-run]

Writes state/thesis/insiders_{YYYY-MM-DD}.jsonl (normalized rows + _raw) and, when >= 2 distinct
insiders trade the same direction in one name, a strength-1 evidence row (source 'insider') on that
name's investor-interest assumptions. One claude -p (mcp-lean) per 25 tickers; a claude failure
aborts the run (never grinds). Re-running the same day overwrites the file and adds no new evidence
(source_id is keyed on the week end).
"""
from __future__ import annotations
import argparse, csv, io, json, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts"))
from lib import claude_p                                                              # noqa: E402
from etfflows.factset_flows import _SPILL_RE, _tool_result_blocks, resolve_payload, rows_of  # noqa: E402
from thesis import STATE_DIR, thesis_io as tio                                        # noqa: E402

TOOL = "mcp__claude_ai_InsiderScore__get_insider_transactions"
MODEL = "claude-sonnet-4-6"
CHUNK = 25
MIN_INSIDERS = 2


def prompt(tickers: list[str], begin: str, end: str) -> str:
    return (f"Call the InsiderScore get_insider_transactions tool EXACTLY ONCE with these arguments:\n"
            f"  tickerlist: {json.dumps(list(tickers))}\n"
            f"  txntypes: [\"Buy\", \"Sell\"]\n"
            f"  tenb5: 'E'\n"
            f"  use_disclosure_date: true\n"
            f"  begin_date: '{begin}'\n"
            f"  end_date: '{end}'\n"
            f"  limit: 1000\n"
            "Do NOT call the tool more than once. Do NOT paginate. Do NOT retry with different arguments.\n\n"
            "Then reply with the single word DONE. Do NOT summarise, quote, reformat or repeat any of the data — "
            "it is read directly from the tool output, not from your reply.")


def _pick(r: dict, *names, default=None):
    low = {str(k).lower().replace("_", "").replace(" ", ""): v for k, v in r.items()}
    for n in names:
        v = low.get(n.lower().replace("_", "").replace(" ", ""))
        if v not in (None, ""):
            return v
    return default


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def normalize(r: dict) -> dict:
    tt = str(_pick(r, "txntype", "transactiontype", "txn_type", "type", "transaction", default="")).strip()
    tt = "Buy" if tt.lower().startswith(("b", "p")) else "Sell" if tt.lower().startswith("s") else tt
    return {"ticker": str(_pick(r, "ticker", "symbol", default="")).upper(),
            "insider": str(_pick(r, "insider", "insidername", "name", "rptname", "reportingname", "owner", "reportingowner", default="")),
            "position": str(_pick(r, "position", "title", "role", "relationship", "officertitle", default="")),
            "txn_type": tt, "shares": _num(_pick(r, "shares", "qty", "quantity", "sharestraded")),
            "value": _num(_pick(r, "value", "amount", "dollarvalue", "txnvalue")),
            "date": str(_pick(r, "date", "transactiondate", "txndate", "disclosuredate", "filingdate", default=""))[:10],
            "notable": _pick(r, "notable", "notableevents", "events", "unusual", default=""), "_raw": r}


def _block_text(text: str) -> str:
    m = _SPILL_RE.search(text or "")
    if m:
        try:
            return Path(m.group(1)).read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    return text or ""


def parse_rows(stdout: str) -> list[dict]:
    """tool_result → rows. JSON shapes via rows_of; CSV (InsiderScore tools also return CSV) via DictReader."""
    for text in reversed(_tool_result_blocks(stdout)):
        rows = rows_of(resolve_payload(text))
        if rows is not None:
            return [r for r in rows if isinstance(r, dict)]
        body = _block_text(text).strip()
        head = body.splitlines()[0] if body else ""
        if "," in head and any(w in head.lower() for w in ("ticker", "symbol")):
            try:
                out = list(csv.DictReader(io.StringIO(body)))
                if out:
                    return out
            except csv.Error:
                pass
    return []


def clusters(rows: list[dict]) -> dict[str, dict]:
    acc: dict[str, dict] = {}
    for r in rows:
        c = acc.setdefault(r["ticker"], {"buyers": set(), "sellers": set(), "buy_value": 0.0, "sell_value": 0.0})
        if r["txn_type"] == "Buy":
            c["buyers"].add(r["insider"]); c["buy_value"] += r["value"] or 0.0
        elif r["txn_type"] == "Sell":
            c["sellers"].add(r["insider"]); c["sell_value"] += r["value"] or 0.0
    return {t: {"buyers": sorted(c["buyers"]), "sellers": sorted(c["sellers"]), "buy_value": c["buy_value"], "sell_value": c["sell_value"]}
            for t, c in sorted(acc.items())}


def investor_assumptions(fm: dict) -> list[str]:
    return [a["id"] for a in fm.get("assumptions") or [] if a.get("status") != "retired"
            and ("potential_investor_interest" in str(a.get("derived_from", "")) or "investor" in a["id"])]


def evidence_rows(cl: dict[str, dict], theses: dict[str, dict], week_end: str) -> list[dict]:
    rows = []
    for t, c in sorted(cl.items()):
        fm = theses.get(t)
        if not fm:
            continue
        nb, ns = len(c["buyers"]), len(c["sellers"])
        if nb >= MIN_INSIDERS and ns < MIN_INSIDERS:
            direction, why = "confirm", f"{nb} insiders bought open-market (ex-10b5-1) ${c['buy_value'] / 1e6:.1f}M in the week to {week_end}"
        elif ns >= MIN_INSIDERS and nb < MIN_INSIDERS:
            direction, why = "challenge", f"{ns} insiders sold open-market (ex-10b5-1) ${c['sell_value'] / 1e6:.1f}M in the week to {week_end}"
        else:
            continue
        for aid in investor_assumptions(fm):
            rows.append({"source": "insider", "source_id": f"insider:{t}:{week_end}", "ref": "InsiderScore get_insider_transactions (tenb5=E)",
                         "date": week_end, "title": "insider cluster", "assumption_id": aid, "direction": direction, "strength": 1,
                         "why": why, "quote": "", "cross_ticker": False, "ticker": t})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7); ap.add_argument("--ticker"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    today = date.today()
    begin, end = (today - timedelta(days=a.days)).isoformat(), today.isoformat()
    tickers = a.ticker.split(",") if a.ticker else [t for t in tio.universe() if t.isalpha()]   # US listings only
    rows: list[dict] = []
    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i + CHUNK]
        try:
            stdout = claude_p.run_mcp(prompt(chunk, begin, end), mcp_tool=TOOL, model=MODEL, cwd=str(REPO), timeout=600)
        except RuntimeError as e:
            print(f"ABORT chunk {chunk[0]}..{chunk[-1]}: {e}"); return 1
        got = [normalize(r) for r in parse_rows(stdout)]
        print(f"chunk {chunk[0]}..{chunk[-1]}: {len(got)} rows", flush=True)
        rows += got
    rows = [r for r in rows if r["ticker"] in set(tickers) and r["txn_type"] in ("Buy", "Sell")]
    cl = clusters(rows)
    theses = {t: fm for t in tickers if (fm := tio.load(t))}
    ev = evidence_rows(cl, theses, end)
    if a.dry_run:
        print(json.dumps({"rows": len(rows), "clusters": {t: c for t, c in cl.items() if len(c["buyers"]) + len(c["sellers"]) >= MIN_INSIDERS},
                          "evidence": ev}, indent=1, default=str))
        return 0
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    out = STATE_DIR / f"insiders_{end}.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows), encoding="utf-8")
    from thesis.match_evidence import CHANGES, LOG, _append, _read_log
    log = _read_log()
    existing = {f"{r['ticker']}|{r['source_id']}|{r.get('assumption_id')}" for r in log}
    ts = datetime.now(timezone.utc).isoformat()
    new = [dict(r, ts=ts) for r in ev if f"{r['ticker']}|{r['source_id']}|{r['assumption_id']}" not in existing]
    _append(LOG, new)
    log += new
    for t in sorted({r["ticker"] for r in new}):
        fm = theses[t]
        tio.recompute_pressure(fm, [r for r in log if r["ticker"] == t], today)
        if fm["_changes"]:
            _append(CHANGES, [dict(c, ts=ts, ticker=t, kind="status") for c in fm["_changes"]])
        tio.save(t, fm)
    print(f"DONE rows={len(rows)} file={out.name} clusters={sum(1 for c in cl.values() if len(c['buyers']) + len(c['sellers']) >= MIN_INSIDERS)} "
          f"evidence_rows={len(new)} tickers_updated={len({r['ticker'] for r in new})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
