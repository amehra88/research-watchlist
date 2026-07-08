#!/usr/bin/env python3
"""
Path A v3 SEC filings channel.

Daily (07:00 ET) the droplet polls EDGAR for new filings from the T1+T2 watchlist
universe (config/watchlist.yaml tier_1_bctk + tier_2_active_candidates; NOT .pvt
privates, NOT tier_3), filters by form type and — for 8-Ks — by item-type signal
value, fetches full content plus key EX-99.* exhibits (esp. earnings press releases
for 8-K Item 2.02), extracts narrative item sections for periodic forms (skipping the
financial-statement boilerplate already covered via FactSet), writes
notes/sec/{date}-{TICKER}-{form}-{section}.md with multi-ticker frontmatter, and
ingests it into the pg corpus via the existing v3-aware chunker.

Form routing is automatic: EDGAR's submissions JSON returns only the forms a filer
actually files, so US filers yield 8-K/10-K/10-Q and ADRs yield 20-F/6-K with no
per-ticker classification. Korean tickers (000660.KS, 005930.KS) and .pvt privates
have no EDGAR coverage — flagged and skipped (DART integration deferred to Phase 2).

  cron: 0 11 * * * cd /root/research-watchlist && /root/bin/alert_on_failure.sh \\
        v3_sec python3 scripts/v3_ingest/sec_filings.py >> logs/v3_sec.log 2>&1

  python3 scripts/v3_ingest/sec_filings.py               # daily incremental (new filings)
  python3 scripts/v3_ingest/sec_filings.py --backfill    # apply backfill windows + per-form caps
  python3 scripts/v3_ingest/sec_filings.py --dry-run --ticker NVDA --form 8-K --limit 1
  python3 scripts/v3_ingest/sec_filings.py --skip-themes  # don't call claude -p (heuristic themes only)
  python3 scripts/v3_ingest/sec_filings.py --print-coverage  # CIK map + flagged tickers, then exit

Env: self-loads CHUNK_STORE_BACKEND from /root/podcasts/.env. Does NOT source
podcasts/.env wholesale (it holds ANTHROPIC_API_KEY, which would flip claude -p off
subscription auth); claude -p is additionally invoked with ANTHROPIC_API_KEY stripped.
embed.py + pgconn.py self-load GEMINI_API_KEY / DATABASE_URL.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

# ───────────────────────────── Configuration ─────────────────────────────

REPO_ROOT = Path("/root/research-watchlist")
NOTES_DIR = REPO_ROOT / "notes" / "sec"
STATE_DIR = REPO_ROOT / "state" / "v3_ingest"
WATERMARK_FILE = STATE_DIR / "sec_watermark.json"
CIK_CACHE_FILE = STATE_DIR / "sec_cik_map.json"
SEC_CONFIG = REPO_ROOT / "config" / "sec_subscriptions.yaml"
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
CHUNKING_DIR = REPO_ROOT / "scripts" / "chunking"
PODCASTS_ENV = Path("/root/podcasts/.env")

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}"
CIK_CACHE_TTL_DAYS = 7

MODEL = "claude-sonnet-4-6"
CLAUDE_TIMEOUT_S = 300
THEME_CONTENT_CAP = 16_000          # chars of filing body passed to the LLM tagger

sys.path.insert(0, str(CHUNKING_DIR))   # chunker / ingest / store / embed

_SESSION: requests.Session | None = None
_CFG: dict = {}


# ───────────────────────────── Logging ─────────────────────────────

def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] v3_sec: {msg}", flush=True)


# ───────────────────────────── Env / config ─────────────────────────────

def _read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith((f"{key}=", f"export {key}=")):
            return line.split("=", 1)[1].strip().strip("\"'")
    return None


def load_env() -> None:
    if not os.environ.get("CHUNK_STORE_BACKEND"):
        os.environ["CHUNK_STORE_BACKEND"] = _read_env_value(PODCASTS_ENV, "CHUNK_STORE_BACKEND") or "pg"


def load_config() -> dict:
    global _CFG
    _CFG = yaml.safe_load(SEC_CONFIG.read_text()) or {}
    return _CFG


def _claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def run_claude(prompt: str) -> tuple[str, float]:
    cmd = ["claude", "-p", prompt, "--output-format", "json",
           "--allowedTools", "", "--model", MODEL]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=CLAUDE_TIMEOUT_S, cwd=str(REPO_ROOT), env=_claude_env())
    if result.returncode != 0:
        # Auth/usage errors land on STDOUT (stderr is usually empty) — log both.
        raise RuntimeError(f"claude -p rc={result.returncode} "
                           f"stderr={result.stderr[:200]!r} stdout={result.stdout[:300]!r}")
    env = json.loads(result.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"claude -p is_error: {str(env.get('result'))[:200]}")
    return env.get("result", ""), float(env.get("total_cost_usd", 0.0) or 0.0)


# ───────────────────────────── HTTP (rate-limited) ─────────────────────────────

def session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update({"User-Agent": _CFG.get("user_agent", "research-watchlist contact@example.com")})
    return _SESSION

def _sleep() -> None:
    time.sleep(float(_CFG.get("rate_limit_sleep_s", 0.2)))

def http_get(url: str) -> requests.Response:
    """GET with the required EDGAR UA header + post-request rate-limit sleep."""
    r = session().get(url, timeout=60)
    _sleep()
    r.raise_for_status()
    return r


# ───────────────────────────── Watchlist universe ─────────────────────────────

def load_universe() -> list[str]:
    """T1 (tier_1_bctk) + T2 (tier_2_active_candidates) tickers from watchlist.yaml."""
    wl = yaml.safe_load(WATCHLIST_YAML.read_text()) or {}
    out: list[str] = []
    for key in ("tier_1_bctk", "tier_2_active_candidates"):
        for entry in (wl.get(key) or []):
            t = entry.get("ticker") if isinstance(entry, dict) else entry
            if t:
                out.append(str(t))
    # de-dup, preserve order
    seen: set[str] = set()
    return [t for t in out if not (t in seen or seen.add(t))]


def load_valid_themes() -> set[str]:
    block = (yaml.safe_load(WATCHLIST_YAML.read_text()) or {}).get("themes", {}) or {}
    out: set[str] = set()
    for cat in block.values():
        out.update(cat or [])
    return out


# ───────────────────────────── CIK mapping ─────────────────────────────

def build_cik_map(universe: list[str]) -> tuple[dict[str, int], list[str]]:
    """Return ({TICKER: cik}, [flagged_no_edgar]). Caches the full EDGAR
    ticker->CIK table to state for CIK_CACHE_TTL_DAYS to avoid refetching daily."""
    overrides = {k.upper(): int(v) for k, v in (_CFG.get("cik_overrides") or {}).items()}
    known_skip = set(_CFG.get("known_no_edgar") or [])

    table = _load_cik_table()
    cik_map: dict[str, int] = {}
    flagged: list[str] = []
    for tkr in universe:
        if tkr in known_skip:
            flagged.append(tkr)
            continue
        up = tkr.upper()
        if up in overrides:
            cik_map[tkr] = overrides[up]
        elif up in table:
            cik_map[tkr] = table[up]
        else:
            flagged.append(tkr)
    return cik_map, flagged


def _load_cik_table() -> dict[str, int]:
    """{TICKER_UPPER: cik} from EDGAR company_tickers.json (cached)."""
    if CIK_CACHE_FILE.exists():
        try:
            cached = json.loads(CIK_CACHE_FILE.read_text())
            age = dt.date.today().toordinal() - dt.date.fromisoformat(cached["fetched"]).toordinal()
            if age < CIK_CACHE_TTL_DAYS and cached.get("table"):
                return {k: int(v) for k, v in cached["table"].items()}
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            pass
    log("fetching EDGAR company_tickers.json …")
    data = http_get(COMPANY_TICKERS_URL).json()
    table = {str(row["ticker"]).upper(): int(row["cik_str"]) for row in data.values()}
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CIK_CACHE_FILE.write_text(json.dumps(
        {"fetched": dt.date.today().isoformat(), "table": table}, indent=0))
    return table


# ───────────────────────────── EDGAR filing discovery ─────────────────────────────

def _all_forms() -> set[str]:
    f = _CFG.get("forms", {})
    base = list(f.get("periodic", [])) + list(f.get("event", []))
    if f.get("include_amendments"):
        base = base + [b + "/A" for b in base]
    return set(base)

def _base_form(form: str) -> str:
    return form.split("/")[0]   # "10-K/A" -> "10-K"


def fetch_filings(ticker: str, cik: int) -> list[dict]:
    """All in-scope filings from the filer's submissions JSON (newest first)."""
    sub = http_get(SUBMISSIONS_URL.format(cik=cik)).json()
    rec = sub.get("filings", {}).get("recent", {})
    n = len(rec.get("accessionNumber", []))
    wanted = _all_forms()
    items_arr = rec.get("items", [""] * n)
    out = []
    for i in range(n):
        form = rec["form"][i]
        if form not in wanted:
            continue
        out.append({
            "ticker": ticker,
            "cik": cik,
            "accession": rec["accessionNumber"][i],
            "form": form,
            "base_form": _base_form(form),
            "filing_date": rec["filingDate"][i],
            "primary_doc": rec["primaryDocument"][i],
            "items": [s.strip() for s in (items_arr[i] or "").split(",") if s.strip()],
        })
    return out


def keep_8k(items: list[str]) -> bool:
    """Keep when the item set intersects `signal`. `noise` suppresses ONLY when it is
    the filing's sole items (so earnings '2.02,9.01' survives via 2.02)."""
    cfg = _CFG.get("eight_k_items", {})
    signal = set(cfg.get("signal", []))
    noise = set(cfg.get("noise", []))
    its = set(items)
    if its & signal:
        return True
    if its and its <= noise:
        return False
    # No recognized items (e.g. blank) or only-unknown items: keep conservatively
    # so we never silently drop a materially-tagged 8-K we don't recognize.
    return bool(its) is False or bool(its - noise)


def select_filings(filings: list[dict], *, backfill: bool, processed: set[str],
                   today: dt.date) -> list[dict]:
    """Apply form/item/date/watermark filters and (optionally) per-form backfill caps."""
    bf = _CFG.get("backfill", {})
    event_forms = set(_CFG.get("forms", {}).get("event", []))
    event_cut = today - dt.timedelta(days=int(bf.get("event_days", 30)))
    periodic_cut = today - dt.timedelta(days=int(bf.get("periodic_days", 365)))
    caps = {k: int(v) for k, v in (bf.get("max_per_form", {}) or {}).items()}

    kept: list[dict] = []
    for f in filings:
        if f["accession"] in processed:
            continue
        bf_form = f["base_form"]
        # 8-K item-signal filter
        if bf_form == "8-K" and not keep_8k(f["items"]):
            continue
        # date window
        try:
            fdate = dt.date.fromisoformat(f["filing_date"])
        except ValueError:
            continue
        cut = event_cut if bf_form in event_forms else periodic_cut
        if backfill and fdate < cut:
            continue
        kept.append(f)

    # per-form caps (most-recent-N). Applied in both modes; harmless in daily mode
    # where new-filing counts never approach the caps.
    kept.sort(key=lambda f: f["filing_date"], reverse=True)
    if caps:
        seen: dict[str, int] = {}
        capped = []
        for f in kept:
            bform = f["base_form"]
            cap = caps.get(bform)              # uncapped forms (cap is None) always pass
            if cap is not None and seen.get(bform, 0) >= cap:
                continue
            seen[bform] = seen.get(bform, 0) + 1
            capped.append(f)
        kept = capped
    return kept


# ───────────────────────────── Filing content fetch ─────────────────────────────

def _acc_nodash(accession: str) -> str:
    return accession.replace("-", "")

def filing_base_url(cik: int, accession: str) -> str:
    return ARCHIVE_BASE.format(cik=cik, acc=_acc_nodash(accession))


def fetch_exhibit_map(cik: int, accession: str) -> dict[str, str]:
    """{EX_TYPE: filename} from the filing's -index.html documents table — the
    authoritative exhibit-type map (filenames like q1fy27pr.htm don't pattern-match)."""
    from bs4 import BeautifulSoup
    url = f"{filing_base_url(cik, accession)}/{accession}-index.html"
    html = http_get(url).text
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, str] = {}
    for tbl in soup.find_all("table"):
        hdr = [th.get_text(strip=True) for th in tbl.find_all("th")]
        if "Type" not in hdr or "Document" not in hdr:
            continue
        ti, di = hdr.index("Type"), hdr.index("Document")
        for tr in tbl.find_all("tr")[1:]:
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if len(tds) <= max(ti, di):
                continue
            etype = tds[ti].strip()
            doc = tds[di].split()[0] if tds[di].split() else ""   # strip " iXBRL" suffix
            if etype and doc and etype not in out:
                out[etype] = doc
    return out


def fetch_ex99(cik: int, accession: str) -> list[tuple[str, str, str]]:
    """All EX-99.* exhibits as [(ex_type, url, markdown)] (press releases / commentary)."""
    exmap = fetch_exhibit_map(cik, accession)
    base = filing_base_url(cik, accession)
    out = []
    for etype in sorted(exmap):
        if not re.match(r"(?i)EX-99", etype):
            continue
        doc = exmap[etype]
        if not re.search(r"\.html?$", doc, re.I):     # skip image/pdf exhibits
            continue
        url = f"{base}/{doc}"
        try:
            md = html_to_markdown(http_get(url).text)
        except Exception as e:  # noqa: BLE001
            log(f"    EX fetch failed {etype} {doc}: {type(e).__name__}: {e}")
            continue
        if md.strip():
            out.append((etype, url, md))
    return out


# ───────────────────────────── HTML -> markdown + section extraction ─────────────

BLOCK_TAGS = ["div", "p", "tr", "li", "section", "article", "table", "ul", "ol",
              "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "blockquote"]


def html_to_markdown(html: str) -> str:
    """SEC iXBRL -> clean line-per-block text. SEC puts paragraph text directly inside
    <div>/<span> (no <p>), so we mark block boundaries with newlines and flatten;
    ix:header and display:none XBRL fact blocks are dropped."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html or "", "html.parser")
    for t in soup(["script", "style", "head", "img", "svg", "noscript", "ix:header"]):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        t.decompose()
    for t in soup.find_all(BLOCK_TAGS):
        t.insert_before("\n")
        t.insert_after("\n")
    text = soup.get_text(separator=" ")
    lines = []
    for ln in text.split("\n"):
        ln = re.sub(r"[ \t ]+", " ", ln).strip()
        if ln:
            lines.append(ln)
    return "\n".join(lines)


ITEM_RE = re.compile(r"^\s*(?:#+\s*)?item\s+(\d{1,2})\s*([a-z])?\b", re.I)


def _item_headers(lines: list[str]) -> list[tuple[int, str]]:
    out = []
    for i, ln in enumerate(lines):
        stripped = ln.strip().lstrip("#").strip()
        m = ITEM_RE.match(ln)
        if m and len(stripped) <= 160:
            out.append((i, m.group(1) + (m.group(2) or "").upper()))
    return out


def extract_item(md: str, target: str) -> str | None:
    """Body markdown for item `target` (e.g. '7','1A','2'), choosing the occurrence
    with the longest span — TOC entries are short, the real section is long."""
    target = target.upper()
    lines = md.split("\n")
    hdrs = _item_headers(lines)
    if not hdrs:
        return None
    best, best_len = None, 0
    for idx, (line_i, key) in enumerate(hdrs):
        if key != target:
            continue
        end_i = hdrs[idx + 1][0] if idx + 1 < len(hdrs) else len(lines)
        body = "\n".join(lines[line_i:end_i]).strip()
        if len(body) > best_len:
            best, best_len = body, len(body)
    return best


def extract_sections(md: str, base_form: str) -> tuple[list[str], list[str], list[str]]:
    """Return (section_markdowns, found_item_keys, missing_item_keys) for a periodic form."""
    targets = _CFG.get("sections", {}).get(base_form, {})
    cap = int(_CFG.get("max_section_chars", 200_000))
    bodies, found, missing = [], [], []
    for item_key, label in targets.items():
        sec = extract_item(md, item_key)
        if sec:
            if len(sec) > cap:
                sec = sec[:cap] + f"\n\n…[section truncated at {cap} chars]…"
            bodies.append(f"## Item {item_key}. {label}\n\n{sec}")
            found.append(item_key)
        else:
            missing.append(item_key)
    return bodies, found, missing


# ───────────────────────────── Note assembly ─────────────────────────────

def slugify(s: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s[:maxlen].strip("-")) or "x"

def _item_slug(items: list[str]) -> str:
    return "-".join(it.replace(".", "_") for it in items) or "body"

def form_slug(form: str) -> str:
    return form.replace("/", "-").replace(" ", "")   # 10-K/A -> 10-K-A


def extract_themes(body_md: str, ticker: str, valid_themes: set[str]) -> tuple[list[str], float]:
    prompt = (
        "You are a precise financial-research tagging assistant. From the SEC FILING "
        f"excerpt below (filer: {ticker}), extract the THEME TAGS substantively present, "
        "using ONLY the provided vocabulary. A theme is present only if the filing "
        "materially discusses it — exclude incidental mentions.\n\n"
        "Output ONLY a JSON object, no prose / markdown / code fences:\n"
        '{"themes": ["..."]}\n\n'
        "THEME TAGS (only these are valid):\n" + ", ".join(sorted(valid_themes)) +
        "\n\nSEC FILING EXCERPT:\n" + body_md[:THEME_CONTENT_CAP] + "\n")
    text, cost = run_claude(prompt)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object in theme response: {text[:160]!r}")
    obj = json.loads(m.group(0))
    themes = [t for t in (obj.get("themes") or []) if t in valid_themes]
    return themes, cost


def build_note(*, ticker: str, filing: dict, items: list[str], filing_url: str,
               press_release_url: str | None, themes: list[str], body_md: str) -> str:
    fm = {
        "doc_type": "sec_filing",
        "source": "sec_edgar",
        "ticker": ticker,
        "accession_number": filing["accession"],
        "form_type": filing["form"],
        "items": items,
        "filed_date": filing["filing_date"],
        "filing_url": filing_url,
        "press_release_url": press_release_url or "",
        "tickers": [ticker],
        "themes": themes,
        "ingestion_date": dt.date.today().isoformat(),
        "extraction_source": "v3 SEC filings pipeline (sec_filings.py); EDGAR; claude-extracted themes",
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    title = f"# {ticker} {filing['form']} — filed {filing['filing_date']}\n\n"
    return f"---\n{front}---\n\n{title}{body_md}\n"


def note_path(ticker: str, filing: dict, section_tag: str) -> Path:
    return NOTES_DIR / f"{filing['filing_date']}-{ticker}-{form_slug(filing['form'])}-{slugify(section_tag, 40)}.md"


def ingest_note(path: Path) -> None:
    from ingest import ingest
    ingest([path])


# ───────────────────────────── Per-filing processing ─────────────────────────────

def process_filing(filing: dict, *, dry_run: bool, skip_themes: bool,
                   valid_themes: set[str]) -> tuple[str, float]:
    """Returns (status, cost). Raises on hard failure (caller isolates per-filing).
    status in {'ok', 'empty'} — 'empty' = nothing extractable (skipped, not written)."""
    ticker, cik, base_form = filing["ticker"], filing["cik"], filing["base_form"]
    base = filing_base_url(cik, filing["accession"])
    primary_url = f"{base}/{filing['primary_doc']}"
    primary_md = html_to_markdown(http_get(primary_url).text)

    press_release_url = None
    items_meta: list[str] = []
    sections: list[str] = []

    if base_form in ("8-K", "6-K"):
        # body (cover) + appended EX-99.* exhibits (press release is the real content)
        parts = []
        if primary_md.strip():
            parts.append(f"## {filing['form']} body\n\n{primary_md}")
        for etype, url, md in fetch_ex99(cik, filing["accession"]):
            parts.append(f"## Exhibit {etype}\n\n{md}")
            if press_release_url is None and re.match(r"(?i)EX-99\.?1?$", etype):
                press_release_url = url
        sections = parts
        items_meta = filing["items"] or [base_form]
        section_tag = _item_slug(filing["items"]) if base_form == "8-K" else "body"
    else:
        # periodic form: extract narrative item sections only
        bodies, found, missing = extract_sections(primary_md, base_form)
        sections = bodies
        items_meta = found
        section_tag = "-".join(found) if found else "none"
        if missing:
            log(f"    {ticker} {filing['form']} {filing['accession']}: missing items {missing} (found {found})")

    body_md = "\n\n".join(s for s in sections if s.strip()).strip()
    if len(body_md) < 60:
        return "empty", 0.0   # nothing substantive extracted — skip, do NOT dump raw doc

    themes, cost = ([], 0.0)
    if not skip_themes:
        try:
            themes, cost = extract_themes(body_md, ticker, valid_themes)
        except Exception as e:  # noqa: BLE001 — themes are optional; chunker adds heuristic themes
            log(f"    {ticker} theme extraction failed (continuing): {type(e).__name__}: {e}")

    note = build_note(ticker=ticker, filing=filing, items=items_meta,
                      filing_url=f"{base}/{filing['primary_doc']}",
                      press_release_url=press_release_url, themes=themes, body_md=body_md)
    path = note_path(ticker, filing, section_tag)

    if dry_run:
        log(f"  [dry-run] {path.name} ({len(body_md)} body chars, items={items_meta}, "
            f"themes={themes}, pr={'yes' if press_release_url else 'no'})")
        print("\n----- DRY-RUN NOTE (" + path.name + ") -----\n"
              + note[:2000] + ("\n…[truncated]…\n" if len(note) > 2000 else "\n")
              + "----- END -----\n", flush=True)
        return "ok", cost

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(note)
    try:
        ingest_note(path)
        log(f"  WROTE+INGESTED {path.name} (items={items_meta}, themes={themes})")
    except Exception as e:  # noqa: BLE001 — note persisted; reingest later via ingest.py --note
        log(f"  WROTE {path.name} but INGEST_DEFERRED: {type(e).__name__}: {e}")
    return "ok", cost


# ───────────────────────────── Watermark ─────────────────────────────

def load_watermark() -> dict:
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"tickers": {}, "runs": 0}


def flush_watermark(wm: dict) -> None:
    """Atomically write the watermark to disk (no counter bump)."""
    wm["last_run_at"] = dt.datetime.now().isoformat(timespec="seconds")
    WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = WATERMARK_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(wm, indent=2) + "\n")
    tmp.replace(WATERMARK_FILE)


def save_watermark(wm: dict) -> None:
    wm["runs"] = wm.get("runs", 0) + 1
    flush_watermark(wm)


# ───────────────────────────── Main ─────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Path A v3 SEC filings channel")
    ap.add_argument("--backfill", action="store_true",
                    help="apply backfill date windows + per-form caps (first/bulk load)")
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch + parse + print; no write, no ingest, no watermark")
    ap.add_argument("--skip-themes", action="store_true",
                    help="do not call claude -p (rely on chunker heuristic themes)")
    ap.add_argument("--ticker", help="restrict to one ticker (testing)")
    ap.add_argument("--form", help="restrict to one base form e.g. 8-K (testing)")
    ap.add_argument("--limit", type=int, help="cap total filings processed (testing)")
    ap.add_argument("--print-coverage", action="store_true",
                    help="print CIK map + flagged tickers, then exit")
    args = ap.parse_args()

    load_env()
    load_config()
    universe = load_universe()
    if args.ticker:
        universe = [t for t in universe if t == args.ticker] or [args.ticker]
    cik_map, flagged = build_cik_map(universe)
    valid_themes = load_valid_themes()
    today = dt.date.today()

    if args.print_coverage:
        log(f"universe={len(universe)}  mapped={len(cik_map)}  flagged={len(flagged)}")
        for t in universe:
            print(f"  {t:12} CIK={cik_map.get(t, '— NO EDGAR (skip)')}")
        print(f"\nFLAGGED (no EDGAR coverage, skipped): {flagged}")
        return 0

    wm = load_watermark()
    mode = "BACKFILL" if args.backfill else "INCREMENTAL"
    if args.dry_run:
        mode += "/DRY-RUN"
    log(f"START mode={mode} backend={os.environ.get('CHUNK_STORE_BACKEND')} "
        f"universe={len(universe)} mapped={len(cik_map)} flagged={len(flagged)}")
    if flagged:
        log(f"INFO flagged tickers without EDGAR coverage (skipped): {flagged}")

    total = processed = empty = failed = 0
    form_counts: dict[str, int] = {}
    total_cost = 0.0
    stop = False

    for ticker in universe:
        if stop:
            break
        cik = cik_map.get(ticker)
        if cik is None:
            continue
        tw = wm.setdefault("tickers", {}).setdefault(ticker, {"processed": []})
        is_first = not tw.get("processed")
        processed_set = set(tw.get("processed", []))
        try:
            filings = fetch_filings(ticker, cik)
        except Exception as e:  # noqa: BLE001 — per-ticker isolation
            failed += 1
            log(f"FETCH FAILED {ticker} (cik={cik}): {type(e).__name__}: {e}")
            continue
        # backfill windows apply on first sight of a ticker OR when --backfill is passed.
        # dry-run is a testing mode -> skip the date window so specific historical
        # filings are reachable via --ticker/--form/--limit.
        sel = select_filings(filings, backfill=(args.backfill or is_first) and not args.dry_run,
                             processed=processed_set, today=today)
        if args.form:
            sel = [f for f in sel if f["base_form"] == args.form]
        if not sel:
            continue
        log(f"{ticker}: {len(sel)} new filing(s) "
            f"({', '.join(sorted({f['form'] for f in sel}))})")

        for filing in sel:
            if args.limit and total >= args.limit:
                stop = True
                break
            total += 1
            try:
                status, cost = process_filing(filing, dry_run=args.dry_run,
                                              skip_themes=args.skip_themes, valid_themes=valid_themes)
                total_cost += cost
                if status == "ok":
                    processed += 1
                    form_counts[filing["form"]] = form_counts.get(filing["form"], 0) + 1
                    if not args.dry_run:
                        tw["processed"] = (tw.get("processed", []) + [filing["accession"]])[-300:]
                elif status == "empty":
                    empty += 1
                    log(f"  EMPTY (skipped, no extractable content): {ticker} {filing['form']} "
                        f"{filing['accession']}")
            except Exception as e:  # noqa: BLE001 — per-filing isolation
                failed += 1
                log(f"  FAILED {ticker} {filing['form']} {filing['accession']}: "
                    f"{type(e).__name__}: {e}")

    if not args.dry_run:
        save_watermark(wm)
    log(f"DONE mode={mode} processed={processed} empty={empty} failed={failed} "
        f"by_form={form_counts} cost=${total_cost:.4f}")
    # Systematic-parse-failure signal: a periodic form whose every filing came back empty.
    return 0


if __name__ == "__main__":
    sys.exit(main())
