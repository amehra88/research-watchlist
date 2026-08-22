#!/usr/bin/env python3
"""CNINFO channel — annual/interim reports for non-EDGAR Chinese companies.

The tier_4_ecosystem names (Innolight, Eoptolink, Accelink, HG Genuine) file nothing
with EDGAR, so until now everything the corpus knew about them was secondhand: what US
filers and news said ABOUT them. This ingests their PRIMARY disclosure.

WHY THIS EXISTS ALONGSIDE StreetAccount. FactSet StreetAccount already gives these names'
results against consensus, in English — but only at headline depth ("Reports Q3: Revenue
CNY10.22B"). It cannot tell you WHY. The proven contrast (docs/foreign-filings-sourcing.md):
a single MD&A slice of Innolight's FY2025 annual report yielded capacity +34% YoY to 28.06M
units, revenue +64% with gross margin EXPANDING 34.65%->42.61%, and a 1.6T dual EML +
silicon-photonics platform. None of that is in StreetAccount. Use both.

NO TRANSLATION STEP. CNINFO PDFs are text-based (pypdf, no OCR — 208,079 chars from a
229-page report). claude -p reads Chinese directly and emits English, carrying the Chinese
source phrase through for audit.

ARCHITECTURE. Writes a normal note per filing and ingests it through the existing v3 path,
so these documents become retrievable corpus members rather than a side table. entities.py
then runs over their chunks unchanged. Notes land in notes/foreign/ with `tickers` set to
the registry `affects` list, so a query scoped to COHR surfaces Innolight's own disclosure.

  python3 scripts/v3_ingest/cninfo_filings.py --dry-run
  python3 scripts/v3_ingest/cninfo_filings.py --id innolight.cn --limit 1
  python3 scripts/v3_ingest/cninfo_filings.py

Progress is checkpointed per filing; an interrupted run resumes without re-spending.
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import time
from pathlib import Path

import requests
import yaml

REPO_ROOT = Path("/root/research-watchlist")
NOTES_DIR = REPO_ROOT / "notes" / "foreign"
STATE = REPO_ROOT / "state" / "v3_ingest" / "cninfo.json"
WATCHLIST = REPO_ROOT / "config" / "watchlist.yaml"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "chunking"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v3_ingest"))

from sec_filings import (is_auth_failure, is_fatal_run_failure, log,  # noqa: E402
                         run_claude)

SEARCH_URL = "http://www.cninfo.com.cn/new/information/topSearch/query"
QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
STATIC_BASE = "http://static.cninfo.com.cn/"
UA = "Mozilla/5.0 (research-watchlist; contact ashimmehra@gmail.com)"
SLEEP_S = 1.0                       # CNINFO publishes no rate cap — be conservative
SLICE_CHARS = 12_000                # per claude -p call; the measured $0.15 unit
MAX_SLICES = 3                      # cap cost per filing
FATAL_STREAK = 3                    # abort on a STREAK, not one blip (see entities.py)

# Annual + interim + quarterlies. Shenzhen/Shanghai share these category codes.
CATEGORIES = {
    "annual":  "category_ndbg_szsh",
    "interim": "category_bndbg_szsh",
    "q3":      "category_sjdbg_szsh",
}

# Sections worth paying to read. Everything else in a 229-page report is boilerplate,
# financial statements (better obtained from FactSet) or governance.
SECTION_CUES = ["管理层讨论与分析", "产能", "光模块", "研发", "主营业务", "行业格局", "竞争"]

PROMPT = """Below is an excerpt from {name}'s {form} filed in Chinese with the Shenzhen/Shanghai
exchange. This company is a {relation} to {affects}.

Extract, IN ENGLISH, ONLY what the text actually states. Do not infer or add outside
knowledge. Prefer specific figures (capacity, volumes, revenue, margin, product specs,
customers) over general statements.

Return JSON only, no prose or code fences:
{{"claims": [{{"topic": "...", "claim": "one sentence in English",
"chinese_source": "the phrase it came from", "figures": ["..."],
"confidence": "high|medium|low"}}]}}

CRITICAL: never use a double-quote character inside a string value. Chinese source text
often contains quotation marks (e.g. "订单生产") — replace them with the full-width
brackets 「」 instead. An unescaped inner quote makes the whole response unparseable.

If the excerpt is boilerplate with nothing substantive, return {{"claims": []}}.

EXCERPT:
{text}
"""


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s


def load_registry() -> list[dict]:
    wl = yaml.safe_load(WATCHLIST.read_text()) or {}
    out = []
    for e in (wl.get("tier_4_ecosystem") or []):
        listing = str(e.get("listing") or "")
        if re.search(r"\b(\d{6})\.(SZ|SH)\b", listing):
            out.append(e)
    return out


def stock_code(entry: dict) -> str | None:
    m = re.search(r"\b(\d{6})\.(SZ|SH)\b", str(entry.get("listing") or ""))
    return m.group(1) if m else None


def resolve_org_id(s: requests.Session, code: str) -> tuple[str, str] | None:
    """CNINFO needs 'code,orgId' — code alone silently returns zero announcements."""
    r = s.post(SEARCH_URL, data={"keyWord": code, "maxNum": 5}, timeout=25)
    time.sleep(SLEEP_S)
    for row in (r.json() or []):
        if row.get("code") == code:
            return row.get("orgId"), row.get("zwjc") or ""
    return None


def list_filings(s: requests.Session, code: str, org_id: str, category: str,
                 since: str) -> list[dict]:
    r = s.post(QUERY_URL, data={
        "stock": f"{code},{org_id}", "tabName": "fulltext", "pageSize": 30, "pageNum": 1,
        "column": "szse", "category": category,
        "seDate": f"{since}~{dt.date.today().isoformat()}",
    }, timeout=30)
    time.sleep(SLEEP_S)
    out = []
    for a in (r.json().get("announcements") or []):
        title = a.get("announcementTitle") or ""
        if "摘要" in title:            # skip the summary edition, we want the full report
            continue
        ts = a.get("announcementTime")
        out.append({
            "title": title,
            "url": STATIC_BASE + (a.get("adjunctUrl") or ""),
            "date": dt.datetime.fromtimestamp(ts / 1000).date().isoformat() if ts else None,
        })
    return out


def pdf_text(s: requests.Session, url: str) -> str:
    import pypdf
    r = s.get(url, timeout=120)
    time.sleep(SLEEP_S)
    reader = pypdf.PdfReader(io.BytesIO(r.content))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def pick_slices(text: str) -> list[str]:
    """The paid-for sections only. A 229-page report is mostly boilerplate and
    financial statements — the latter are cleaner from FactSet than from a PDF."""
    pages = text.split("\n")
    joined = "\n".join(pages)
    starts = []
    for cue in SECTION_CUES:
        i = joined.find(cue)
        if i > 0:
            starts.append(i)
    if not starts:
        return [joined[:SLICE_CHARS]]
    starts = sorted(set(starts))
    out, used = [], []
    for i in starts:
        if any(abs(i - u) < SLICE_CHARS for u in used):
            continue          # overlapping window already covered
        out.append(joined[i:i + SLICE_CHARS])
        used.append(i)
        if len(out) >= MAX_SLICES:
            break
    return out


def build_note(entry: dict, filing: dict, claims: list[dict], org_name: str) -> str:
    fm = {
        "doc_type": "foreign_filing",
        "source": "cninfo",
        "ecosystem_id": entry["id"],
        "company": entry.get("name"),
        "company_zh": org_name,
        "relation": entry.get("relation"),
        # `tickers` is what retrieval scopes on: a COHR-scoped query must surface a
        # competitor's own disclosure, so the affected tickers go here.
        "tickers": list(entry.get("affects") or []),
        "affects": list(entry.get("affects") or []),
        "themes": [],
        "filing_title": filing["title"],
        "filing_url": filing["url"],
        "filed_date": filing["date"],
        "listing": entry.get("listing"),
        "factset_id": entry.get("factset_id"),
        "language_note": "filed in Chinese; claims extracted to English with source phrases",
        "ingestion_date": dt.date.today().isoformat(),
        "extraction_source": "v3 CNINFO channel (cninfo_filings.py); claude-extracted claims",
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    body = [f"# {entry.get('name')} — {filing['title']} (filed {filing['date']})", ""]
    body.append(f"Primary disclosure from {entry.get('listing')}. This company is a "
                f"{entry.get('relation')} to {', '.join(entry.get('affects') or [])} and files "
                f"nothing with EDGAR, so this is the only primary source available for it.")
    body.append("")
    body.append("## Extracted claims")
    body.append("")
    for c in claims:
        figs = ", ".join(c.get("figures") or [])
        body.append(f"### {c.get('topic','(untitled)')}")
        body.append("")
        body.append(c.get("claim", ""))
        if figs:
            body.append("")
            body.append(f"Figures: {figs}")
        if c.get("chinese_source"):
            body.append("")
            body.append(f"> Source (Chinese): {c['chinese_source']}")
        body.append("")
        body.append(f"Confidence: {c.get('confidence','?')}")
        body.append("")
    return f"---\n{front}---\n\n" + "\n".join(body) + "\n"


def parse_claims(out: str) -> list[dict]:
    """Tolerant JSON extraction.

    Chinese source text routinely contains quotation marks, and the model emits them as
    ASCII double quotes INSIDE string values, which breaks the whole payload. The prompt
    asks for 「」 instead; this repairs the cases where it does not comply, so one bad
    quote does not throw away a $0.20 call."""
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return []
    frag = m.group(0)
    try:
        return json.loads(frag).get("claims") or []
    except json.JSONDecodeError:
        pass
    # Repair: within each "key": "value" pair, escape stray inner double quotes. Matches a
    # value that runs to the next `",\n` or `"\n}` boundary, so inner quotes are captured.
    def _fix(mm: re.Match) -> str:
        key, val = mm.group(1), mm.group(2)
        return f'"{key}": "' + val.replace('"', "'") + '"'
    repaired = re.sub(r'"(topic|claim|chinese_source|confidence)":\s*"(.*?)"(?=\s*[,}\]])',
                      _fix, frag, flags=re.S)
    try:
        return json.loads(repaired).get("claims") or []
    except json.JSONDecodeError:
        # Last resort: salvage individual well-formed claim objects.
        out_claims = []
        for om in re.finditer(r'\{[^{}]*"claim"[^{}]*\}', repaired, re.S):
            try:
                out_claims.append(json.loads(om.group(0)))
            except json.JSONDecodeError:
                continue
        return out_claims


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"done": {}, "cost": 0.0}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="CNINFO filings channel (tier_4_ecosystem)")
    ap.add_argument("--id", help="limit to one ecosystem id, e.g. innolight.cn")
    ap.add_argument("--since", default="2024-01-01")
    ap.add_argument("--limit", type=int, help="max filings per company")
    ap.add_argument("--dry-run", action="store_true",
                    help="list + extract + print; no note write, no ingest, no checkpoint")
    args = ap.parse_args()

    st = load_state()
    done = st["done"]
    s = session()
    entries = [e for e in load_registry() if not args.id or e["id"] == args.id]
    log(f"CNINFO START companies={len(entries)} since={args.since} dry_run={args.dry_run}")

    written = failed = 0
    consecutive_fatal = 0
    cost = 0.0
    for entry in entries:
        code = stock_code(entry)
        resolved = resolve_org_id(s, code) if code else None
        if not resolved:
            log(f"  {entry['id']}: could not resolve orgId for code {code}")
            failed += 1
            continue
        org_id, org_name = resolved
        filings: list[dict] = []
        for cat in CATEGORIES.values():
            try:
                filings += list_filings(s, code, org_id, cat, args.since)
            except Exception as e:  # noqa: BLE001
                log(f"  {entry['id']}: list failed for {cat}: {type(e).__name__}: {e}")
        filings.sort(key=lambda f: f["date"] or "", reverse=True)
        if args.limit:
            filings = filings[:args.limit]
        log(f"  {entry['id']} ({org_name}, code {code}): {len(filings)} filing(s)")

        for f in filings:
            key = f["url"]
            if key in done and not args.dry_run:
                continue
            fcost = 0.0
            try:
                text = pdf_text(s, f["url"])
                slices = pick_slices(text)
                claims: list[dict] = []
                for sl in slices:
                    prompt = PROMPT.format(name=entry.get("name"), form=f["title"],
                                           relation=entry.get("relation"),
                                           affects=", ".join(entry.get("affects") or []),
                                           text=sl)
                    out, c = run_claude(prompt)
                    fcost += c
                    claims += parse_claims(out)
                cost += fcost
            except Exception as e:  # noqa: BLE001
                failed += 1
                log(f"    FAILED {f['title'][:40]}: {type(e).__name__}: {e}")
                if is_auth_failure(e):
                    log("  auth failure — aborting immediately; an expired token is not "
                        "transient and a retry cannot fix it. Run `claude /login` on "
                        "the droplet, then re-run to resume from the checkpoint.")
                    return 1
                if is_fatal_run_failure(e):
                    consecutive_fatal += 1
                    if consecutive_fatal >= FATAL_STREAK:
                        log(f"    {consecutive_fatal} consecutive fatal failures (usage "
                            f"limit) — aborting; re-run later to resume from the "
                            f"checkpoint")
                        return 1
                    log(f"    fatal-looking failure {consecutive_fatal}/{FATAL_STREAK} — "
                        f"continuing in case it is transient")
                else:
                    consecutive_fatal = 0
                continue

            if args.dry_run:
                log(f"    [dry-run] {f['date']} {f['title'][:44]} -> {len(claims)} claims "
                    f"({len(text):,} chars, {len(slices)} slice(s))")
                for c in claims[:4]:
                    log(f"        {c.get('topic','')}: {str(c.get('claim',''))[:110]}")
                continue

            note = build_note(entry, f, claims, org_name)
            NOTES_DIR.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r"[^a-z0-9]+", "-", f["title"].lower())[:40].strip("-") or "filing"
            path = NOTES_DIR / f"{f['date']}-{entry['id'].replace('.', '-')}-{slug}.md"
            path.write_text(note)
            try:
                from ingest import ingest
                ingest([path])
                log(f"    WROTE+INGESTED {path.name} ({len(claims)} claims)")
            except Exception as e:  # noqa: BLE001
                log(f"    WROTE {path.name} but INGEST_DEFERRED: {type(e).__name__}: {e}")
            written += 1
            consecutive_fatal = 0
            done[key] = {"note": path.name, "claims": len(claims),
                         "at": dt.datetime.now().isoformat(timespec="seconds")}
            st["cost"] = st.get("cost", 0.0) + fcost
            save_state(st)

    log(f"CNINFO DONE written={written} failed={failed} cost=${cost:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
