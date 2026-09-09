"""Evidence collectors: one function per channel, all returning Evidence since a date.

News comes from DISK (notes/news/{YYYY-MM-DD}-*.md) because the frontmatter filter
(summarized / confidence) is not expressible against pg. Everything else comes from pg
parent chunks or existing state files. Read-only everywhere.
"""
from __future__ import annotations
import glob, json, re, sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import yaml

REPO = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO / "scripts" / "chunking"))
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TEXT_CAP = 3500


@dataclass
class Evidence:
    source: str
    source_id: str
    ticker: str
    date: str          # ISO
    title: str
    text: str
    ref: str           # path or url for the report citation
    cross_ticker: bool = False


def _fm_and_body(path: Path) -> tuple[dict, str]:
    t = path.read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(t)
    if not m:
        return {}, t
    try:
        return (yaml.safe_load(m.group(1)) or {}), t[m.end():]
    except yaml.YAMLError:
        return {}, t


def _pg():
    from pgconn import connect
    return connect()


def _iso_from_name(name: str) -> str:
    """'20260904-2Q27.md' -> '2026-09-04'."""
    d = name[:8]
    return f"{d[:4]}-{d[4:6]}-{d[6:]}"


def earnings_notes_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / ticker / "[0-9]*-[1-4]Q[0-9][0-9].md"))):
        iso = _iso_from_name(Path(p).name)
        if iso < since.isoformat():
            continue
        fm, body = _fm_and_body(Path(p))
        keep = re.findall(r"(## (?:1|3|4|4b|5|6|7)\..*?)(?=\n## |\Z)", body, re.S)
        rel = Path(p).relative_to(REPO).as_posix()
        out.append(Evidence("earnings_note", rel, ticker, iso, Path(p).stem, "\n".join(keep)[:12000], rel))
    return out


_NEWS_CACHE: dict[str, tuple[dict, str]] = {}   # filename -> (frontmatter, body); notes/news files are immutable once written


def _news_note(p: Path) -> tuple[dict, str] | None:
    """Parse one news note once per process; None when the note has no frontmatter."""
    name = p.name
    if name not in _NEWS_CACHE:
        _NEWS_CACHE[name] = _fm_and_body(p)
    return _NEWS_CACHE[name]


def news_since(ticker: str, since: date) -> list[Evidence]:
    """Materially-tagged news for the ticker, from disk (18k+ notes: prefilter on a raw
    substring before the YAML parse, and cache parses across tickers in one run)."""
    out = []
    needle = f"- {ticker}\n".encode()
    for p in sorted(glob.glob(str(REPO / "notes" / "news" / "*.md"))):
        name = Path(p).name
        if name[:10] < since.isoformat():
            continue
        if name not in _NEWS_CACHE:
            with open(p, "rb") as f:
                head = f.read(4096)
            if needle not in head:
                continue
        fm, body = _news_note(Path(p))
        if ticker not in (fm.get("tickers") or []):
            continue
        if not (fm.get("summarized", True) or fm.get("confidence") == "high"):
            continue
        title = (fm.get("cluster_headlines") or [name])[0]
        out.append(Evidence("news", f"notes/news/{name}", ticker, name[:10], str(title),
                            (str(fm.get("rationale") or "") + "\n" + body)[:TEXT_CAP], str((fm.get("source_urls") or [name])[0])))
    return out


def sec_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT doc_id, section, event_date, text FROM chunks
           WHERE kind='parent' AND doc_type='sec_filing' AND %s = ANY(tickers) AND event_date > %s
             AND (section LIKE 'Exhibit EX-99%%' OR section ILIKE 'Item %%Management%%' OR section LIKE '%%body')
           ORDER BY event_date"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, since))
        return [Evidence("sec_filing", f"pg:{r[0]}:{r[1]}", ticker, r[2].isoformat(), r[1], (r[3] or "")[:TEXT_CAP], f"pg chunks doc_id={r[0]}")
                for r in cur.fetchall()]


def entity_claims_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT chunk_id, entity, claim, stance, confidence, event_date, extracted_at, subject, affects, doc_type
           FROM entity_mentions WHERE (subject = %s OR %s = ANY(affects)) AND extracted_at > %s ORDER BY extracted_at"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, ticker, since))
        rows = cur.fetchall()
    out = []
    for r in rows:
        d = (r[5] or r[6].date()).isoformat()
        out.append(Evidence("entity_claim", f"pg:em:{r[0]}:{r[1]}", ticker, d, f"{r[1]} ({r[3]}, {r[4]})",
                            f"{r[1]}: {r[2]}", f"pg entity_mentions chunk_id={r[0]}", cross_ticker=(r[7] != ticker)))
    return out


def commentary_since(ticker: str, since: date) -> list[Evidence]:
    q = """SELECT doc_id, doc_type, section, event_date, text FROM chunks
           WHERE kind='parent' AND doc_type IN ('substack_post','podcast_summary') AND %s = ANY(tickers) AND event_date > %s
           ORDER BY event_date"""
    with _pg() as conn, conn.cursor() as cur:
        cur.execute(q, (ticker, since))
        return [Evidence(r[1], f"pg:{r[0]}:{r[2]}", ticker, r[3].isoformat(), r[2] or r[1], (r[4] or "")[:TEXT_CAP], f"pg doc_id={r[0]}")
                for r in cur.fetchall()]


def conference_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / ticker / "[0-9]*-conf-*.md"))):
        iso = _iso_from_name(Path(p).name)
        if iso < since.isoformat():
            continue
        fm, body = _fm_and_body(Path(p))
        keep = re.findall(r"(## (?:2|3|4)\..*?)(?=\n## |\Z)", body, re.S)
        rel = Path(p).relative_to(REPO).as_posix()
        out.append(Evidence("conference", rel, ticker, iso, Path(p).stem, "\n".join(keep)[:8000], rel))
    ex = REPO / "state" / "transcripts" / "exchanges.jsonl"
    if ex.exists():
        for line in ex.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ticker") != ticker or r.get("event_type") != "conference" or r.get("speaker_type") != "corprep":
                continue
            if (r.get("event_date") or "") <= since.isoformat():
                continue
            out.append(Evidence("conference", f"exch:{r.get('vector_id') or r.get('id')}", ticker, r["event_date"],
                                r.get("event_name") or "conference", (r.get("text") or "")[:TEXT_CAP],
                                f"FactSet transcript {r.get('document_id')}"))
    return out


def operator_notes_since(ticker: str, since: date) -> list[Evidence]:
    out = []
    for p in sorted(glob.glob(str(REPO / "notes" / "inbox" / "*.summary.md"))):
        fm, body = _fm_and_body(Path(p))
        d = str(fm.get("processed_at") or fm.get("ingestion_date") or fm.get("event_date") or "")[:10]
        if ticker not in (fm.get("tickers") or []) or d <= since.isoformat():
            continue
        rel = Path(p).relative_to(REPO).as_posix()
        out.append(Evidence("operator_note", rel, ticker, d, Path(p).stem, body[:8000], rel))
    return out


COLLECTORS = (earnings_notes_since, news_since, sec_since, entity_claims_since, commentary_since, conference_since, operator_notes_since)


def collect_all(ticker: str, since: date) -> list[Evidence]:
    seen, out = set(), []
    for fn in COLLECTORS:
        for e in fn(ticker, since):
            if e.source_id in seen:
                continue
            seen.add(e.source_id); out.append(e)
    return sorted(out, key=lambda e: e.date)
