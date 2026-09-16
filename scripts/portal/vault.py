"""Vault walker: discovers, classifies and loads notes/ for the RIS4 portal builder.

Every function here reads live data from REPO (see scripts/portal/__init__.py) —
never from a worktree checkout. Reuses scripts/thesis/sources.py (_fm_and_body,
_iso_from_name) and scripts/thesis/thesis_io.py (tier_of, watchlist_entry,
watchlist_scores, load) rather than re-parsing frontmatter or re-reading the
watchlist. Read-only: never writes into notes/, config/, or state/.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

# Resolve scripts/ onto sys.path so `from portal import REPO` and `from thesis import
# ...` both work regardless of whether this module is imported as `portal.vault` or as
# a bare `vault` module (the test harness's no-pytest convention imports it bare, the
# same way scripts/v3_ingest/test_transcript_ingest.py imports transcript_ingest).
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from portal import REPO  # noqa: E402
from thesis import sources, thesis_io  # noqa: E402

EXCLUDED_TOP = {"inbox", "news", "sec"}

_EARNINGS_RE = re.compile(r"^([A-Z0-9.\-]+|[a-z]+\.pvt)/(\d{8})-([1-4]Q\d{2})\.md$")
_CONF_RE = re.compile(r"/(\d{8})-conf-")
_SYNTH_RE = re.compile(r"/synthesis-(\d{8})")
_NEWS_NOTE_RE = re.compile(r"/(\d{8})-news-")
_TICKER_DIR_RE = re.compile(r"^([A-Z0-9.\-]+|[a-z]+\.pvt)$")
_TITLE_RE = re.compile(r"^# (.+)$", re.M)
_SECTION_RE = re.compile(r"^## (.*)$", re.M)
_LEAD_NUM_RE = re.compile(r"^(\d+)\.")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

_TOP_DIR_KIND = {
    "themes": "theme", "reports": "report", "substacks": "substack",
    "podcasts": "podcast", "flows": "flow", "foreign": "foreign", "sector": "sector",
}

_SIGNAL_KEYS = {"5": "ai_positioning", "6": "competitive_advantage", "7": "investor_interest"}

# ingest_bundles bucket name -> (NoteRef.kind, window override in days, else use `days`)
_BUCKETS = {
    "substacks": ("substack", None), "podcasts": ("podcast", None),
    "foreign": ("foreign", None), "flows": ("flow", 14),
    "sector": ("sector", None), "pvt": ("pvt_profile", None),
}


@dataclass
class NoteRef:
    path: Path
    rel: str
    ticker: str | None
    kind: str
    date: str | None
    period: str | None
    title: str
    size: int


def classify(rel: str) -> tuple[str, str | None, str | None, str | None]:
    """(kind, ticker, iso_date, period) from a notes/-relative path, no filesystem access."""
    top = rel.split("/", 1)[0]

    m = _EARNINGS_RE.match(rel)
    if m:
        ticker, d, period = m.groups()
        return "earnings", ticker, sources._iso_from_name(d), period

    m = _CONF_RE.search(rel)
    if m:
        return "conference", top, sources._iso_from_name(m.group(1)), None

    m = _SYNTH_RE.search(rel)
    if m:
        return "synthesis", top, sources._iso_from_name(m.group(1)), None

    m = _NEWS_NOTE_RE.search(rel)
    if m:
        return "news_note", top, sources._iso_from_name(m.group(1)), None

    if rel.endswith("/_thesis.md"):
        return "thesis", top, None, None
    if rel.endswith("/_themes.md"):
        return "theme_index", top, None, None
    if rel.endswith("/_profile.md"):
        return ("pvt_profile" if top.endswith(".pvt") else "profile"), top, None, None

    if top in _TOP_DIR_KIND:
        return _TOP_DIR_KIND[top], None, None, None

    if "/" in rel and _TICKER_DIR_RE.match(top):
        return "other", top, None, None
    return "other", None, None, None


def discover(notes_dir: Path = REPO / "notes") -> list[NoteRef]:
    """Walk notes_dir, classify every .md file, skip inbox/ news/ sec/."""
    out = []
    for p in sorted(notes_dir.rglob("*.md")):
        rel = p.relative_to(notes_dir).as_posix()
        if rel.split("/", 1)[0] in EXCLUDED_TOP:
            continue
        kind, ticker, d, period = classify(rel)
        text = p.read_text(encoding="utf-8", errors="replace")
        m = _TITLE_RE.search(text)
        title = m.group(1).strip() if m else p.stem
        out.append(NoteRef(p, rel, ticker, kind, d, period, title, p.stat().st_size))
    return out


def _split_sections(body: str) -> list[dict]:
    heads = list(_SECTION_RE.finditer(body))
    out = []
    for i, m in enumerate(heads):
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out.append({"h": m.group(1).strip(), "text": body[start:end].strip()})
    return out


def _synth_fm(ref: NoteRef) -> dict:
    d = {"ticker": ref.ticker, "date": ref.date, "period": ref.period}
    return {k: v for k, v in d.items() if v is not None}


def _provenance(fm: dict) -> str:
    if fm.get("reviewed_by_operator") is True or fm.get("status_source") == "operator":
        return "operator_reviewed"
    if fm.get("summarized") is False:
        return "headline_only"
    return "machine"


def load_note(ref: NoteRef) -> dict:
    fm, body = sources._fm_and_body(ref.path)
    if not fm:
        fm = _synth_fm(ref)
    return {
        "id": ref.rel,
        "rel": ref.rel,
        "ticker": ref.ticker,
        "kind": ref.kind,
        "date": ref.date,
        "period": ref.period,
        "title": ref.title,
        "fm": fm,
        "body": body,
        "sections": _split_sections(body),
        "provenance": _provenance(fm),
    }


def resolve_wikilinks(text: str, known_tickers: set, known_themes: set) -> str:
    def repl(m: re.Match) -> str:
        target, alias = m.group(1), m.group(2)
        label = alias if alias is not None else target.rsplit("/", 1)[-1]
        if target.endswith("/_thesis"):
            t = target[: -len("/_thesis")]
            return f"[{label}](#/ticker/{t}/thesis)" if t in known_tickers else label
        if target.startswith("themes/"):
            slug = target.split("/", 1)[1]
            return f"[{label}](#/theme/{slug})" if slug in known_themes else label
        return f"[{label}](#/ticker/{target})" if target in known_tickers else label

    return _WIKILINK_RE.sub(repl, text)


def signal_reads(note: dict) -> dict | None:
    if note["kind"] not in ("earnings", "conference"):
        return None
    picks = {}
    for sec in note["sections"]:
        m = _LEAD_NUM_RE.match(sec["h"])
        if m and m.group(1) in _SIGNAL_KEYS:
            picks[_SIGNAL_KEYS[m.group(1)]] = sec["text"].strip()[:600]
    if not picks:
        return None
    return {k: picks.get(k) for k in ("ai_positioning", "competitive_advantage", "investor_interest")}


def ticker_bundle(ticker: str, refs: list[NoteRef], names: dict,
                   known_tickers: set, known_themes: set) -> dict:
    tier = thesis_io.tier_of(ticker) or "none"
    _, entry = thesis_io.watchlist_entry(ticker)
    themes = entry.get("themes") or []
    scores = thesis_io.watchlist_scores(ticker)
    name = names.get(ticker) or ticker

    tfm = thesis_io.load(ticker)
    if tfm:
        body = tfm.get("_body", "")
        fm_without_body = {k: v for k, v in tfm.items() if k != "_body"}
    else:
        body, fm_without_body = "", {}
    thesis = {"fm_without_body": fm_without_body, "body": body}

    ti_ref = next((r for r in refs if r.ticker == ticker and r.kind == "theme_index"), None)
    theme_index_body = sources._fm_and_body(ti_ref.path)[1] if ti_ref else ""

    profile_ref = next((r for r in refs if r.ticker == ticker
                        and r.kind in ("profile", "pvt_profile")), None)
    profile = load_note(profile_ref) if profile_ref else None

    excluded_kinds = ("thesis", "theme_index", "profile", "pvt_profile")
    note_refs = [r for r in refs if r.ticker == ticker and r.kind not in excluded_kinds]
    notes = sorted((load_note(r) for r in note_refs), key=lambda n: n["date"] or "", reverse=True)

    return {
        "ticker": ticker, "name": name, "tier": tier, "themes": themes, "scores": scores,
        "thesis": thesis, "theme_index_body": theme_index_body, "notes": notes,
        "profile": profile,
    }


def _known_sets(refs: list[NoteRef]) -> tuple[set, set]:
    tickers = {r.ticker for r in refs if r.ticker}
    themes = {Path(r.rel).stem for r in refs if r.kind == "theme"}
    return tickers, themes


def _bucket_date(ref: NoteRef, fm: dict) -> str | None:
    if ref.kind == "substack":
        return fm.get("source_date")
    if ref.kind == "podcast":
        return fm.get("published_date")
    if ref.kind == "foreign":
        return fm.get("filed_date")
    if ref.kind in ("flow", "sector"):
        stem = Path(ref.rel).name[:8]
        return sources._iso_from_name(stem) if stem.isdigit() else None
    return None  # pvt_profile: standing doc, not time-windowed


def _bucket_source(ref: NoteRef, fm: dict) -> str:
    if ref.kind == "substack":
        return fm.get("publication") or "substack"
    if ref.kind == "podcast":
        return fm.get("podcast_name") or "podcast"
    if ref.kind == "foreign":
        return fm.get("company") or "foreign"
    if ref.kind == "pvt_profile":
        return ref.ticker or "pvt"
    return ref.kind


def ingest_bundles(refs: list[NoteRef], days: int = 30, today: date | None = None) -> dict:
    """dict[bucket_name, {items: [...]}] for substacks/podcasts/foreign/flows(14d)/sector/pvt.

    `today` is an additive, optional override (default None -> date.today()) so the
    window filter can be tested deterministically against static fixture dates without
    changing the documented default behaviour for any caller that omits it.
    """
    today = today or date.today()
    known_tickers, known_themes = _known_sets(refs)
    out = {}
    for name, (kind, window_override) in _BUCKETS.items():
        window = window_override if window_override is not None else days
        cutoff = (today - timedelta(days=window)).isoformat()
        items = []
        for ref in refs:
            if ref.kind != kind:
                continue
            note = load_note(ref)
            d = _bucket_date(ref, note["fm"])
            if d is not None and d < cutoff:
                continue
            tickers = note["fm"].get("tickers") or (
                [ref.ticker] if kind == "pvt_profile" and ref.ticker else [])
            items.append({
                "id": note["id"], "date": d, "title": note["title"], "tickers": tickers,
                "themes": note["fm"].get("themes") or [],
                "source": _bucket_source(ref, note["fm"]),
                "body": resolve_wikilinks(note["body"], known_tickers, known_themes),
            })
        items.sort(key=lambda it: it["date"] or "", reverse=True)
        out[name] = {"items": items}
    return out
