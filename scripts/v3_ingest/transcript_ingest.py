#!/usr/bin/env python3
"""
P1 of the idea-surfacing / sub-sector-timeliness design
(docs/superpowers/specs/2026-08-11-idea-surfacing-timeliness-design.md §4.1).

Retrieves verbatim, speaker-typed transcript exchanges (earnings calls AND
conferences) from FactSet ALL_TRANSCRIPTS for a resolved universe of companies
over a trailing 9-month window, and appends one row per chunk to
state/transcripts/exchanges.jsonl. This is the question-side substrate the whole
design turns on: analyst Q&A is unscripted, filings and news are IR-authored.

    python3 scripts/v3_ingest/transcript_ingest.py --print-universe
    python3 scripts/v3_ingest/transcript_ingest.py --ticker AAOI --max-queries 1 --dry-run
    python3 scripts/v3_ingest/transcript_ingest.py --ticker AAOI --max-queries 2
    python3 scripts/v3_ingest/transcript_ingest.py                    # full backfill
    python3 scripts/v3_ingest/transcript_ingest.py --conferences 8    # weekly forward cron
    python3 scripts/v3_ingest/transcript_ingest.py --start 2026-09-02 --end 2026-09-10 --query "..."

CONFERENCE MODE (2026-09-10). `--conferences DAYS` is the forward feed: trailing
window, one generic query per resolved name (themes not required), ledger entries
keyed `id|query|offset|start..end`. The window in the key is what makes a forward
run work at all — the 9-month backfill keyed on (id, query, offset) alone, so a
`--window-months 1` run found every offset-0 page already "ok" and fetched nothing.
Downstream, thesis/sources.conference_since reads the corprep rows straight from
exchanges.jsonl, so the daily matcher sees a conference the run after it lands.

WHAT WAS PROBED LIVE (2026-08-11) AND IS THEREFORE LOAD-BEARING HERE
  - Conference chunks carry financialYear but NO financialQuarter key at all.
    Period keys for conferences come from the event date (calendar quarter);
    naive dict access on financialQuarter KeyErrors on ~every conference chunk.
  - meta.pagination.total is the RETURNED count, not a corpus total (limit=50 ->
    total=50). The only honest stop condition is a short page.
  - storyDateTime is the publication moment, not the event: AAOI's 6-August call
    carries storyDateTime 2026-08-07. Event date comes from the headline only.
  - FactSet's own `themes` field is an ESG taxonomy misfiring on tech. Unused.

TRANSPORT. The FactSet MCP server is a claude.ai workspace connector, so Python
cannot call it directly; the call goes through `claude -p`. Since 2026-09-10 this
is the repo's mcp-lean transport (scripts/lib/claude_p.run_mcp, as factset_news /
factset_flows / insider_pull): a data-retrieval system prompt, `--tools ToolSearch`,
stream-json, and the page is read from the raw tool_result block (following a
spill-to-file if the harness made one) — ~22K tokens per call instead of ~100K, and
no word ever passes through the model (payload_source="tool_result"). Every chunk is
still checked against the API's own textLength; a failing chunk is dropped, the page
is not failed, because nothing was retyped. The legacy path (model echoes the JSON,
payload_source="model_text", all-or-nothing fidelity) is kept in accept_payload for
the rows already on disk and for the ledger's history.

FAILURE MARKING (the b1c351aa lesson). The ledger records ok / empty / failed as
three distinct states. `empty` means the API answered with nothing and the work
is done; `failed` means we do not know and the page will be retried. Conflating
them is what produced the 828-doc theme hole.

Writes only under state/ — no notes/ output, so the open chunker v3-awareness gap
is not on this path.

Env: claude -p is invoked with ANTHROPIC_API_KEY stripped so it stays on
subscription auth even when a cron has sourced podcasts/.env.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# ───────────────────────────── Configuration ─────────────────────────────

REPO_ROOT = Path("/root/research-watchlist")
sys.path.insert(0, str(REPO_ROOT / "scripts"))              # lib.claude_p, etfflows.factset_flows
from lib import claude_p                                     # noqa: E402  shared -p wrapper (mcp-lean)
from etfflows.factset_flows import _tool_result_blocks, _unwrap, resolve_payload  # noqa: E402
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
IDENTITY_YAML = REPO_ROOT / "config" / "ticker_identity.yaml"
# supply-chain lives in the sibling research repo, NOT under this repo's config/
# (watchlist.yaml is symlinked there; the supply-chain files are not).
SUPPLY_CHAIN_MANUAL = Path("/root/research/config/supply-chain-manual.yaml")

STATE_DIR = REPO_ROOT / "state" / "transcripts"
EXCHANGES_PATH = STATE_DIR / "exchanges.jsonl"
PROGRESS_PATH = STATE_DIR / "_progress.json"      # underscore: distinct from the
                                                  # {TICKER}.json earnings ledgers
NO_COVERAGE_PATH = STATE_DIR / "_no_coverage.json"
RAW_DIR = STATE_DIR / "raw"                       # gitignored payload cache

TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_UnstructuredContent"
MODEL = "claude-haiku-4-5-20251001"               # 2026-09-10: the model only places one tool call
                                                  # (arguments verified against the transcript, page read
                                                  # from the tool_result); Haiku A/B vs Sonnet on 3 names =
                                                  # identical vectorIds. Sonnet only for the legacy echo path.
CLAUDE_TIMEOUT_S = 420

WINDOW_MONTHS = 9                                 # spec §3, operator's call
PAGE_LIMIT = 50                                   # FactSet max
MAX_PAGES = 3                                     # 150 chunks per (company, query)
MAX_QUERIES_PER_COMPANY = 6
DEFAULT_WORKERS = 3

# Conference mode (2026-09-10): a trailing window, ONE generic query per resolved name
# (themes not required — a themeless name still presents at conferences), ledger keyed
# by the window so successive weekly runs never collide with the 9-month backfill's
# (id, query, offset) entries. Paging until a short page returns every chunk FactSet
# holds for the name in the window, so one query is complete, not a sample.
CONFERENCE_QUERY = "What did the executives say at the conference?"
CONFERENCE_WINDOW_DAYS = 8                        # weekly cron with one day of overlap

# Earnings mode (2026-09-11, P5b): the same calendar-driven per-event pull with
# eventTypes=['Earnings']. A call is ~52 chunks (median over 136 backfilled events,
# p75 64) and a page holds 50, and paging over ties leaves gaps — so two semantic
# queries per event, one page each: analyst Q&A first (the register topic_map keys on),
# prepared remarks second. vector_id dedup absorbs the overlap.
EARNINGS_QUERIES = ("What did analysts ask in the question and answer session?",
                    "What did management say in prepared remarks about results and guidance?")
EARNINGS_WINDOW_DAYS = 3                          # weekday cron with two days of overlap
ABORT = threading.Event()                         # set on ToolUnavailableError: stop all workers

# Calendar-driven conference mode (2026-09-10). Measured on AVGO (Goldman session + Q3 call
# in one 8-day window): pages at offset 0 and 50 of the same query overlapped on 22 of 50
# chunks — most chunks tie at the 0.01 similarity floor and FactSet orders ties arbitrarily
# per request, so paging over a whole-window corpus leaves gaps (30 of 44 documents were
# missing Q&A turns). ONE event over a 3-day window fits a single 50-chunk page, which is
# returned in full — so the feed asks the calendar where to look and pulls per event.
CAL_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_CalendarEvents"
CAL_SYMBOLS_PER_CALL = 50
EVENT_WINDOW_DAYS = 2                             # storyDateTime = publication, up to 2 days after the session

# tool contract: letters, digits and  space , % & / - ?
QUERY_CHARSET_RE = re.compile(r"[A-Za-z0-9 ,%&/\-?]+")
TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.]*$")
MANUAL_PROVENANCE = {"manual", "verified"}

# words that end the host-firm prefix of a conference name
_HOST_STOPWORDS = {
    "global", "technology", "tech", "annual", "conference", "summit", "forum",
    "investor", "investors", "day", "days", "healthcare", "aerospace", "defense",
    "industrials", "media", "communications", "growth", "best", "ideas", "and",
    "&", "energy", "consumer", "financial", "internet", "software", "semiconductor",
    "virtual", "fireside", "chat", "symposium", "capital", "markets",
    # sector acronyms that follow the host name in real headlines (measured on the
    # AAOI run: "Raymond James TMT and Consumer Conference" must yield "Raymond James",
    # not "Raymond James TMT", or the same host reads as two firms downstream)
    "tmt", "tme", "ai", "it", "emea", "apac", "us", "european", "asia", "asian",
    "institutional", "investors", "annualmeeting", "b2b", "iot",
}


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] transcript_ingest: {msg}", flush=True)


# ───────────────────────────── Universe ─────────────────────────────

@dataclass
class UniverseEntry:
    ticker: str                       # watchlist ticker or tier_4 id
    factset_id: str
    themes: list = field(default_factory=list)
    reasons: list = field(default_factory=list)


def _dedup_keep_order(items):
    seen, out = set(), []
    for i in items:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def resolve_factset_id(ticker: str, identity: dict) -> str | None:
    """Identity map wins; plain US tickers default to TICKER-US; anything with an
    exchange suffix and no mapping is unresolvable and must be recorded, not guessed."""
    mapped = (identity.get(ticker) or {}).get("factset_id")
    if mapped:
        return mapped
    if "." in ticker:
        return None
    return f"{ticker}-US"


def resolve_universe(watchlist: dict, sc_edges: list, identity: dict):
    """T1 + T2, plus manual/verified supply-chain adjacents of those names, plus
    ingest_comparables, plus tier_4_ecosystem. Returns (entries, unresolved).

    SPEC NOTE: §4.1 enumerates T1+T2, supply-chain adjacents and tier_4 but omits
    ingest_comparables. That omission contradicts the spec's own rationale (§3:
    "the most informative document on COHR/LITE China risk in 9 months was AAOI's
    call") and its acceptance criteria (§11.2 requires citing AAOI 2026-08-06),
    since AAOI reaches the universe by no other route. Comparables are included
    and printed with their reason.
    """
    tiers = {
        "tier_1": watchlist.get("tier_1_bctk") or [],
        "tier_2": watchlist.get("tier_2_active_candidates") or [],
    }
    themes_by_ticker: dict[str, list] = {}
    for block in ["tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist"]:
        for e in watchlist.get(block) or []:
            if e.get("ticker"):
                themes_by_ticker.setdefault(e["ticker"], list(e.get("themes") or []))

    entries: dict[str, UniverseEntry] = {}
    unresolved: list[dict] = []

    def add(ticker, reason, themes, factset_id=None):
        if ticker.endswith(".pvt"):          # privates never enter this pipeline
            return
        if ticker in entries:
            entries[ticker].reasons.append(reason)
            entries[ticker].themes = _dedup_keep_order(entries[ticker].themes + list(themes))
            return
        fsid = factset_id or resolve_factset_id(ticker, identity)
        if not fsid:
            unresolved.append({"ticker": ticker, "reason": "no factset_id mapping",
                               "route": reason})
            return
        entries[ticker] = UniverseEntry(ticker, fsid, _dedup_keep_order(list(themes)), [reason])

    for tier, rows in tiers.items():
        for e in rows:
            t = e.get("ticker")
            if t:
                add(t, tier, e.get("themes") or [])

    core = set(entries)                      # T1+T2 only — adjacency is measured from these

    for edge in sc_edges:
        if (edge.get("provenance") or "").lower() not in MANUAL_PROVENANCE:
            continue
        src, tgt = edge.get("source"), edge.get("target")
        for near, far in ((src, tgt), (tgt, src)):
            if near in core and far and TICKER_RE.match(str(far)):
                add(far, f"supply_chain_adjacent:{near}",
                    themes_by_ticker.get(far) or themes_by_ticker.get(near) or [])

    for c in watchlist.get("ingest_comparables") or []:
        t = c.get("ticker")
        if not t:
            continue
        inherited = []
        for informed in c.get("informs") or []:
            inherited += themes_by_ticker.get(informed) or []
        add(t, f"ingest_comparable:{','.join(c.get('informs') or [])}",
            themes_by_ticker.get(t) or inherited)

    for e in watchlist.get("tier_4_ecosystem") or []:
        eid, fsid = e.get("id"), e.get("factset_id")
        if not eid:
            continue
        if not fsid:
            unresolved.append({"ticker": eid, "reason": "no factset_id in tier_4 entry",
                               "route": "tier_4"})
            continue
        inherited = []
        for affected in e.get("affects") or []:
            inherited += themes_by_ticker.get(affected) or []
        add(eid, f"tier_4:{','.join(e.get('affects') or [])}", inherited, factset_id=fsid)

    return list(entries.values()), unresolved


# ───────────────────────────── Query generation ─────────────────────────────

def theme_to_query(theme: str) -> str:
    """Deterministic, LLM-free, one sentence per assigned theme.

    Deliberately mechanical: §11.2's gold test is only honest if the query set
    cannot be hand-tuned to make it pass. The tool's own contract also forbids
    topic expansion beyond what was literally asked.
    """
    phrase = re.sub(r"[^a-z0-9 ]", " ", theme.replace("_", " ").lower()).strip()
    phrase = re.sub(r"\s+", " ", phrase)
    return f"What are executives and analysts discussing about {phrase}?"


def queries_for(entry: UniverseEntry, max_queries: int = MAX_QUERIES_PER_COMPANY,
                override: list | None = None) -> list:
    """Themes in operator-authored order, capped. A name with no assigned themes
    yields no queries — inventing one would contaminate the vocabulary.
    `override` (conference mode / --query) replaces the theme queries for every name."""
    if override:
        return list(override)[:max_queries]
    return [theme_to_query(t) for t in entry.themes[:max_queries]]


# ───────────────────────────── Headline parsing ─────────────────────────────

_HEADLINE_RE = re.compile(
    r"^(?:(?P<prefix>[A-Z ]*TRANSCRIPT)\s*:\s*)?"
    r"(?P<company>.*?)\((?P<fsid>[A-Za-z0-9.]+-[A-Z]{2})\)\s*,\s*(?P<rest>.+)$"
)
_EVENT_DATE_RE = re.compile(r"(\d{1,2}-[A-Za-z]+-\d{4})")


def _parse_event_date(token: str) -> str | None:
    try:
        return dt.datetime.strptime(token, "%d-%B-%Y").date().isoformat()
    except ValueError:
        try:
            return dt.datetime.strptime(token, "%d-%b-%Y").date().isoformat()
        except ValueError:
            return None


def _host_hint(event_name: str) -> str | None:
    """Conference host firm, for §10's n_banks exclusion at its own conference.
    'Mizuho Global Technology Conference' -> 'Mizuho';
    'TD Cowen Aerospace & Defense Conference' -> 'TD Cowen'."""
    words = []
    for w in event_name.split():
        if w.lower().strip(".,") in _HOST_STOPWORDS:
            break
        words.append(w)
    return " ".join(words) or None


def parse_headline(headline: str) -> dict:
    """Event type, true event date and host firm — all of which exist ONLY here.
    An unrecognised shape returns Nones; it is never guessed from storyDateTime."""
    out = {"event_type": None, "event_date": None, "event_name": None,
           "host_hint": None, "corrected": False}
    m = _HEADLINE_RE.match(headline or "")
    if not m:
        return out
    out["corrected"] = bool(m.group("prefix") and "CORRECTED" in m.group("prefix"))
    rest = m.group("rest")
    dm = _EVENT_DATE_RE.search(rest)
    if dm:
        out["event_date"] = _parse_event_date(dm.group(1))
        event_name = rest[: dm.start()].strip().rstrip(",").strip()
    else:
        event_name = rest.strip()
    out["event_name"] = event_name or None
    if not event_name:
        return out
    if re.search(r"earnings\s+call", event_name, re.I):
        out["event_type"] = "earnings_call"
    else:
        out["event_type"] = "conference"
        out["host_hint"] = _host_hint(event_name)
    return out


def headline_family(headline: str) -> str:
    """Same event, corrected or not: 'CORRECTED TRANSCRIPT: X' and 'TRANSCRIPT: X'
    collapse to one key so a re-issued transcript cannot double-count a bank."""
    return re.sub(r"^[A-Z ]*TRANSCRIPT\s*:\s*", "", headline or "").strip().lower()


def calendar_quarter(date_iso: str) -> str:
    d = dt.date.fromisoformat(date_iso)
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


# ───────────────────────────── Row shaping ─────────────────────────────

def chunk_is_verbatim(chunk: dict) -> bool:
    """The API reports textLength for every chunk — a free integrity check on any
    payload that passed through a model."""
    text = chunk.get("content")
    if not isinstance(text, str) or not text:
        return False
    declared = chunk.get("textLength")
    if not isinstance(declared, int):
        return False
    return len(text) == declared


def accept_payload(chunks: list, payload_source: str):
    """(kept, status). A retyped payload is all-or-nothing: one bad chunk means the
    model summarised, so the page is failed and retried rather than half-trusted."""
    if not chunks:
        return [], "empty"
    good = [c for c in chunks if chunk_is_verbatim(c)]
    bad = len(chunks) - len(good)
    if payload_source == "model_text" and bad:
        return [], f"failed: fidelity ({bad} of {len(chunks)} chunks failed textLength)"
    if not good:
        return [], f"failed: fidelity ({bad} of {len(chunks)} chunks failed textLength)"
    if bad:
        log(f"  dropped {bad} chunk(s) failing the textLength check")
    return good, "ok"


def row_from_chunk(chunk: dict, ticker: str, query: str, payload_source: str) -> dict:
    parsed = parse_headline(chunk.get("headline", ""))
    fiscal_year = chunk.get("financialYear")
    fiscal_quarter = chunk.get("financialQuarter")          # ABSENT on conferences
    doc_num = chunk.get("docNum") or ""

    if parsed["event_type"] == "earnings_call" and fiscal_year and fiscal_quarter:
        period_key, period_basis = f"{fiscal_year}{fiscal_quarter}", "fiscal"
    elif parsed["event_date"]:
        period_key, period_basis = calendar_quarter(parsed["event_date"]), "calendar"
    elif fiscal_year and fiscal_quarter:
        period_key, period_basis = f"{fiscal_year}{fiscal_quarter}", "fiscal"
    else:
        period_key, period_basis = None, None

    ids = chunk.get("ids") or []
    return {
        "vector_id": chunk.get("vectorId"),
        "document_id": chunk.get("documentID"),
        "ticker": ticker,
        "factset_id": ids[0] if ids else None,
        "event_type": parsed["event_type"],
        "event_name": parsed["event_name"],
        "event_date": parsed["event_date"],
        "headline": chunk.get("headline"),
        "corrected": parsed["corrected"],
        "host_hint": parsed["host_hint"],
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "period_key": period_key,
        "period_basis": period_basis,
        "section": doc_num.split("_")[0] if doc_num else None,
        "doc_num": doc_num,
        # measured: some chunks carry speakerType "" — normalise to None so no
        # downstream count can treat the empty string as a fourth speaker class
        "speaker_type": chunk.get("speakerType") or None,
        "speaker_name": chunk.get("speakerName"),
        "speaker_title": chunk.get("speakerTitle"),
        "speaker_firm": chunk.get("speakerCompanyName"),
        "text": chunk.get("content"),
        "sentiment": chunk.get("sentiment"),
        "view_url": chunk.get("viewUrl"),
        "retrieved_by_query": query,
        "similarity": chunk.get("similarityScore"),
        "payload_source": payload_source,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }


def _exchange_key(row: dict):
    """Identify the same exchange across an original and a corrected transcript:
    vector ids differ (they embed the documentID) but the docNum + chunk index and
    the headline family do not."""
    vid = row.get("vector_id") or ""
    doc = row.get("document_id") or ""
    suffix = vid.replace(f"{doc}_{doc}_", "") if doc else vid
    return (headline_family(row.get("headline") or ""), suffix, row.get("speaker_name"))


def dedupe_rows(rows: list) -> list:
    by_vector: dict[str, dict] = {}
    for r in rows:
        by_vector.setdefault(r.get("vector_id"), r)

    by_exchange: dict[tuple, dict] = {}
    for r in by_vector.values():
        k = _exchange_key(r)
        cur = by_exchange.get(k)
        if cur is None or (r.get("corrected") and not cur.get("corrected")):
            by_exchange[k] = r
    return list(by_exchange.values())


# ───────────────────────────── Ledger ─────────────────────────────

class Ledger:
    """Three states per (factset_id, query, offset): ok / empty / failed.
    `empty` is answered-and-done; `failed` is unknown-and-retried."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.data = {"version": 1, "entries": {}}
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text())
                if isinstance(loaded, dict) and isinstance(loaded.get("entries"), dict):
                    self.data = loaded
            except (json.JSONDecodeError, OSError):
                log(f"WARNING: unreadable ledger at {self.path}; starting a fresh one")

    @staticmethod
    def key(factset_id: str, query: str, offset: int, window: tuple | None = None) -> str:
        """Legacy (windowless) key for the backfill; `|start..end` appended when the run
        has an explicit window, so a forward window never reads as already fetched."""
        k = f"{factset_id}|{query}|{offset}"
        return f"{k}|{window[0]}..{window[1]}" if window else k

    def status(self, factset_id, query, offset, window=None) -> str | None:
        e = self.data["entries"].get(self.key(factset_id, query, offset, window))
        return e.get("status") if e else None

    def done(self, factset_id, query, offset, window=None) -> bool:
        s = self.status(factset_id, query, offset, window)
        return bool(s and (s == "ok" or s == "empty" or s.startswith("ok")))

    def record(self, factset_id, query, offset, status, n_chunks,
               raw_returned=None, terminal=False, window=None) -> None:
        """`n_chunks` is what survived validation; `raw_returned` is what the API
        actually returned. Both are needed: the stop decision keys on the raw count,
        so without it a resumed run cannot tell a short page from a page where
        validation dropped chunks, and would re-fetch every terminated query."""
        with self._lock:
            self.data["entries"][self.key(factset_id, query, offset, window)] = {
                "status": status,
                "n_chunks": n_chunks,
                "raw_returned": raw_returned,
                "terminal": bool(terminal),
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            }

    def terminated(self, factset_id, query, offset, window=None) -> bool:
        """True when this page already ended the query's paging — so a resumed run
        skips the offsets beyond it instead of paying for them again."""
        e = self.data["entries"].get(self.key(factset_id, query, offset, window))
        return bool(e and e.get("terminal"))

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=1))
            tmp.replace(self.path)

    def coverage(self, factset_id: str) -> str:
        """Coverage as the LEDGER knows it, across every run — not as this run
        happened to behave. A resumed run makes no calls for names already done,
        so in-run activity would mislabel a fully covered name as uncovered.

        ok anywhere -> covered | else failed anywhere -> incomplete |
        else empty anywhere -> no_results | nothing recorded -> not_queried
        """
        prefix = f"{factset_id}|"
        seen = [e.get("status") or "" for k, e in self.data["entries"].items()
                if k.startswith(prefix)]
        if not seen:
            return "not_queried"
        if any(s.startswith("ok") for s in seen):
            return "covered"
        if any(s.startswith("failed") for s in seen):
            return "incomplete"
        return "no_results"

    def counts(self) -> dict:
        out: dict[str, int] = {}
        for e in self.data["entries"].values():
            head = (e.get("status") or "?").split(":")[0]
            out[head] = out.get(head, 0) + 1
        return out


# ───────────────────────────── Paging ─────────────────────────────

def should_stop_paging(n_returned: int, limit: int) -> bool:
    """meta.pagination.total is the returned count, not a corpus total, so a short
    page is the only honest stop condition."""
    return n_returned < limit


def page_offsets(limit: int = PAGE_LIMIT, max_pages: int = MAX_PAGES) -> list:
    return [i * limit for i in range(max_pages)]


# ───────────────────────────── FactSet fetch ─────────────────────────────


def _fetch_prompt(factset_id, query, start, end, limit, offset) -> str:
    # mcp-lean: the model only places the call; the page is read from the tool_result.
    return (
        f"Call the {TOOL.split('__')[-1]} tool exactly once with exactly these arguments, "
        "changing nothing:\n"
        f"  sources=['ALL_TRANSCRIPTS']\n"
        f"  ids=['{factset_id}']\n"
        f"  startDate='{start}'\n"
        f"  endDate='{end}'\n"
        f"  limit={limit}\n"
        f"  offset={offset}\n"
        f"  query='{query}'\n\n"
        "Do not modify the query text. Do not call any other tool. Do not open any file. "
        "Then reply DONE."
    )



class CalendarError(RuntimeError):
    """The calendar pull failed — there is no plan to run, so the run stops loudly."""


def _arg_norm(v):
    if isinstance(v, (list, tuple)):
        return sorted(str(x) for x in v)
    return str(v)


def argument_drift(placed: dict | None, expected: dict, optional=("sources",)) -> list:
    """Names of expected arguments the model did not place as given. Cosmetic differences
    (int vs str, list order/tuple) are not drift; an omitted key in `optional` is not."""
    if placed is None:
        return ["<no tool_use>"]
    bad = []
    for k, want in expected.items():
        if k not in placed:
            if k in optional:
                continue
            bad.append(k)
        elif _arg_norm(placed[k]) != _arg_norm(want):
            bad.append(k)
    return bad


def _page_args(factset_id, query, start, end, limit, offset) -> dict:
    return {"sources": ["ALL_TRANSCRIPTS"], "ids": [factset_id], "startDate": start,
            "endDate": end, "limit": limit, "offset": offset, "query": query}


def fetch_page(factset_id, query, start, end, offset, limit=PAGE_LIMIT,
               timeout=CLAUDE_TIMEOUT_S, raw_dir: Path | None = None, model: str | None = None):
    """-> (chunks, status, payload_source). Never raises; the caller records the status.

    mcp-lean transport (scripts/lib/claude_p.run_mcp, 2026-09-10; previously the full
    harness at ~100K tokens/call): the model's only job is to place the call, and the
    page is read from the raw tool_result in the stream-json transcript — no word passes
    through the model (payload_source="tool_result", so accept_payload drops a bad chunk
    instead of failing the page). A spilled tool_result is followed by resolve_payload.
    ToolUnavailableError means the connector is not loaded — identical for every name —
    so it sets ABORT and the other workers stop rather than paying for N more failures.
    """
    if ABORT.is_set():
        return [], "failed: aborted (tool unavailable earlier in this run)", None
    try:
        stdout = claude_p.run_mcp(_fetch_prompt(factset_id, query, start, end, limit, offset),
                                  mcp_tool=TOOL, model=model or MODEL, cwd=str(REPO_ROOT),
                                  timeout=timeout)
    except claude_p.ToolUnavailableError as e:
        ABORT.set()
        return [], f"failed: tool unavailable ({str(e)[:120]})", None
    except subprocess.TimeoutExpired:
        return [], "failed: timeout", None
    except Exception as e:                                   # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {str(e)[:160]}", None

    # The model is the only thing between us and the API. Whatever it placed is what
    # the page answers; a drifted argument is a different page under the same ledger key.
    placed = claude_p.tool_use_input(stdout, TOOL)
    drift = argument_drift(placed, _page_args(factset_id, query, start, end, limit, offset))
    if drift:
        shown = {k: (placed or {}).get(k) for k in drift}
        return [], f"failed: argument drift in {', '.join(drift)}: placed {shown!r}", None

    blocks = _tool_result_blocks(stdout)
    payload, payload_source = None, "tool_result"
    for text in reversed(blocks):
        # a spilled page (>~70KB, i.e. most full 50-chunk pages) comes back as the MCP
        # content-block wrapper [{"type":"text","text":"{...}"}]; _unwrap opens it
        cand = _unwrap(resolve_payload(text))
        if isinstance(cand, dict) and "data" in cand:
            payload = cand
            break
    if payload is None:
        tail = (blocks[-1] if blocks else stdout).strip()[-160:]
        return [], f"failed: no FactSet payload in tool_result: {tail!r}", None

    chunks = payload.get("data")
    if not isinstance(chunks, list):
        return [], "failed: payload has no data array", payload_source

    if raw_dir and chunks:
        raw_dir.mkdir(parents=True, exist_ok=True)
        # md5, not hash(): str hashing is salted per process, so hash() would write
        # a differently-named copy of the same page on every re-run
        qid = hashlib.md5(query.encode()).hexdigest()[:10]
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{factset_id}_{qid}_{offset}")
        (raw_dir / f"{safe}.json").write_text(json.dumps(payload))

    return chunks, "ok", payload_source


# ───────────────────────────── Run ─────────────────────────────

def load_yaml(path: Path):
    try:
        return yaml.safe_load(Path(path).read_text()) or {}
    except OSError as e:
        log(f"WARNING: could not read {path}: {e}")
        return {}


def build_no_coverage(entries, unresolved, empty_names, incomplete_names, window) -> dict:
    """Spec §4.1: names with no coverage are RECORDED, never dropped silently —
    and §11.5 requires every downstream figure to print its exclusions.

    Three distinct reasons, kept separate because they mean different things:
      no_factset_id  — we cannot even ask
      no_themes      — we can ask but have no operator-authored question to ask
                       (inventing one would contaminate the vocabulary, §11.2)
      no_results     — we asked and FactSet has nothing in the window
      incomplete     — we asked and the call failed, so coverage is UNKNOWN

    `incomplete` is separate from `no_results` for the same reason the ledger keeps
    `empty` separate from `failed`: a name whose pages all errored has not been
    shown to be uncovered, and reporting it as such would launder an outage into a
    finding — the b1c351aa lesson, one level up.
    """
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "window": {"start": window[0], "end": window[1]},
        "no_factset_id": unresolved,
        "no_themes": [{"ticker": e.ticker, "factset_id": e.factset_id,
                       "routes": e.reasons} for e in entries if not e.themes],
        "no_results": sorted(empty_names),
        "incomplete": sorted(incomplete_names),
    }


def existing_keys(path: Path):
    """(vector_ids, exchange_keys) already on disk.

    Both are needed. vector_id catches the same chunk arriving twice — which it
    does, since pages overlap. The exchange key catches the SAME exchange arriving
    under a different documentID (an original and a corrected transcript), whose
    vector_ids differ by construction. Measured on the 990-row ramp corpus: zero
    collisions and no headline family split across documentIDs, so this guard is
    latent today — FactSet appears to retire the original. It is kept because the
    failure it prevents (a bank counted twice in n_banks) is silent and lands in
    P4's headline numbers."""
    vectors, exchanges = set(), {}
    if not path.exists():
        return vectors, exchanges
    with path.open() as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            vectors.add(row.get("vector_id"))
            exchanges[_exchange_key(row)] = bool(row.get("corrected"))
    return vectors, exchanges


def window_bounds(months: int, today: dt.date | None = None):
    end = today or dt.date.today()
    y, m = end.year, end.month - months
    while m <= 0:
        m += 12
        y -= 1
    day = min(end.day, 28)
    return dt.date(y, m, day).isoformat(), end.isoformat()


def conference_window(days: int, today: dt.date | None = None):
    """Trailing window for the forward (conference) cron: [today - days, today]."""
    end = today or dt.date.today()
    return (end - dt.timedelta(days=days)).isoformat(), end.isoformat()


def event_window(event_datetime: str, today: dt.date | None = None):
    """[event day, min(event day + EVENT_WINDOW_DAYS, today)]: storyDateTime is the
    publication moment (CRWV's 8-Sep session carried 9-Sep 09:26), so the window trails
    the session — but never past today: FactSet rejects a future endDate outright
    ("Invalid date/dateTime ... not in the future", measured 2026-09-10 on NOW). A
    clamped window has its own ledger key, so next week's unclamped window is re-pulled
    and the late-published turns land then (vectorId dedup absorbs the overlap)."""
    today = today or dt.date.today()
    day = dt.date.fromisoformat(event_datetime[:10])
    end = min(day + dt.timedelta(days=EVENT_WINDOW_DAYS), today)
    return day.isoformat(), end.isoformat()


def _calendar_prompt(symbols: list, start: str, end: str, event_types=("Conference",)) -> str:
    end_excl = (dt.date.fromisoformat(end) + dt.timedelta(days=1)).isoformat()
    return (
        f"Call the {CAL_TOOL.split('__')[-1]} tool exactly once with exactly these arguments, "
        "changing nothing:\n"
        f"  symbols={symbols!r}\n"
        "  universeType='Tickers'\n"
        f"  eventTypes={list(event_types)!r}\n"
        f"  startDateTime='{start}T00:00:00Z'\n"
        f"  endDateTime='{end_excl}T00:00:00Z'\n\n"
        "Do not call any other tool. Do not open any file. Then reply DONE."
    )


def fetch_calendar(entries: list, start: str, end: str, timeout=CLAUDE_TIMEOUT_S,
                   model: str | None = None, event_types=("Conference",)) -> list:
    """Conference events for every resolved name in [start, end], CAL_SYMBOLS_PER_CALL
    symbols per MCP call. Raises CalendarError on any failure: without the calendar
    there is no plan, and a silent empty plan would read as a quiet week."""
    symbols = [e.factset_id for e in entries]
    events = []
    for i in range(0, len(symbols), CAL_SYMBOLS_PER_CALL):
        chunk = symbols[i:i + CAL_SYMBOLS_PER_CALL]
        try:
            stdout = claude_p.run_mcp(_calendar_prompt(chunk, start, end, event_types), mcp_tool=CAL_TOOL,
                                      model=model or MODEL, cwd=str(REPO_ROOT), timeout=timeout)
        except (claude_p.ToolUnavailableError, RuntimeError, subprocess.TimeoutExpired) as e:
            raise CalendarError(f"calendar pull {chunk[0]}..{chunk[-1]}: "
                                f"{type(e).__name__}: {str(e)[:200]}") from e
        payload = None
        for text in reversed(_tool_result_blocks(stdout)):
            cand = _unwrap(resolve_payload(text))
            if isinstance(cand, dict) and isinstance(cand.get("data"), list):
                payload = cand
                break
        if payload is None:
            raise CalendarError(f"calendar pull {chunk[0]}..{chunk[-1]}: no data array in "
                                f"tool_result: {stdout.strip()[-200:]!r}")
        events.extend(payload["data"])
    return events


def plan_from_events(entries: list, events: list, today: dt.date | None = None,
                     event_type: str = "Conference", queries: tuple = (CONFERENCE_QUERY,)) -> list:
    """(entry, query, (start, end)) per (name, event day) x query, matched on the
    event's requestId (our factset_id; `identifier` may be the primary listing, e.g.
    TSM-US -> 2330-TW). Two sessions on one day are one pull. An event dated after
    today is deferred: the next trailing-window run sees it."""
    today = today or dt.date.today()
    by_id = {e.factset_id: e for e in entries}
    seen, plan = set(), []
    for ev in events:
        if not isinstance(ev, dict) or ev.get("eventType") != event_type:
            continue
        entry = by_id.get(ev.get("requestId")) or by_id.get(ev.get("identifier"))
        when = ev.get("eventDateTime") or ""
        if entry is None or len(when) < 10:
            continue
        w = event_window(when, today)
        if w[0] > w[1]:
            continue                                   # not happened yet
        if (entry.ticker, w) in seen:
            continue
        seen.add((entry.ticker, w))
        for q in queries:
            plan.append((entry, q, w))
    plan.sort(key=lambda t: (t[0].ticker, t[2], queries.index(t[1]) if t[1] in queries else 0))
    return plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P1 transcript ingest (spec §4.1)")
    ap.add_argument("--ticker", action="append", help="restrict to these tickers (repeatable)")
    ap.add_argument("--window-months", type=int, default=WINDOW_MONTHS)
    ap.add_argument("--max-queries", type=int, default=MAX_QUERIES_PER_COMPANY)
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES)
    ap.add_argument("--limit", type=int, default=PAGE_LIMIT)
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    ap.add_argument("--print-universe", action="store_true", help="resolve, print, exit")
    ap.add_argument("--dry-run", action="store_true", help="print planned calls, call nothing")
    ap.add_argument("--retry-failed", action="store_true", default=True)
    ap.add_argument("--no-raw-cache", action="store_true")
    ap.add_argument("--start", help="explicit window start YYYY-MM-DD (with --end); "
                                    "ledger entries are scoped to the window")
    ap.add_argument("--end", help="explicit window end YYYY-MM-DD (with --start)")
    ap.add_argument("--earnings", type=int, metavar="DAYS",
                    help="calendar-driven earnings-call feed over a trailing window (weekday cron, P5b)")
    ap.add_argument("--conferences", type=int, metavar="DAYS",
                    help="forward mode: trailing DAYS window, one generic query per resolved "
                         f"name, themes not required (weekly cron: {CONFERENCE_WINDOW_DAYS}). "
                         "Calendar-driven: one pull per (name, conference day) from "
                         "CalendarEvents, each over a 3-day window that fits one page")
    ap.add_argument("--scan", action="store_true",
                    help="with --conferences: page the whole trailing window per name instead "
                         "of asking the calendar (the 2026-09-10 first run; leaves gaps)")
    ap.add_argument("--model", default=MODEL,
                    help=f"claude -p model for the MCP calls (default {MODEL}); the model only "
                         "places the call and its arguments are verified against the transcript")
    ap.add_argument("--query", action="append",
                    help="replace the theme queries with this sentence (repeatable)")
    args = ap.parse_args(argv)
    if bool(args.start) != bool(args.end):
        ap.error("--start and --end go together")
    if args.conferences and args.earnings:
        ap.error("--earnings and --conferences are separate feeds; run one at a time")
    if (args.conferences or args.earnings) and args.start:
        ap.error("--conferences/--earnings set their own window; drop --start/--end")
    feed = "Conference" if args.conferences else ("Earnings" if args.earnings else None)
    feed_queries = None
    if feed:
        feed_queries = list(args.query) if args.query else (
            [CONFERENCE_QUERY] if feed == "Conference" else list(EARNINGS_QUERIES))

    watchlist = load_yaml(WATCHLIST_YAML)
    identity = load_yaml(IDENTITY_YAML)
    sc = load_yaml(SUPPLY_CHAIN_MANUAL)
    entries, unresolved = resolve_universe(watchlist, sc.get("edges") or [], identity)

    if args.ticker:
        wanted = set(args.ticker)
        entries = [e for e in entries if e.ticker in wanted]

    entries.sort(key=lambda e: e.ticker)
    if feed:
        start, end = conference_window(args.conferences or args.earnings)
        window, override = (start, end), feed_queries
    elif args.start:
        start, end = args.start, args.end
        window, override = (start, end), args.query
    else:
        start, end = window_bounds(args.window_months)
        window, override = None, args.query           # legacy ledger keys: the backfill

    log(f"window {start} -> {end}{' (ledger-scoped)' if window else ''}; universe "
        f"{len(entries)} names, {len(unresolved)} unresolved"
        + (f"; query override: {override}" if override else ""))
    for e in entries:
        log(f"  {e.ticker:<14} {e.factset_id:<12} themes={len(e.themes)} "
            f"[{'; '.join(e.reasons)}]"
            + ("  NO THEMES -> no queries" if not e.themes and not override else ""))
    for u in unresolved:
        log(f"  UNRESOLVED {u['ticker']}: {u['reason']} (via {u['route']})")
    if args.print_universe:
        return 0

    # plan items: (entry, query, (start, end), ledger window-key or None)
    if feed and not args.scan:
        try:
            events = fetch_calendar(entries, start, end, model=args.model, event_types=(feed,))
        except CalendarError as e:
            log(f"ABORT: {e}")
            return 1
        plan = [(e, q, w, w) for e, q, w in
                plan_from_events(entries, events, event_type=feed, queries=tuple(feed_queries))]
        n_typed = sum(1 for ev in events if isinstance(ev, dict) and ev.get("eventType") == feed)
        log(f"calendar: {len(events)} events ({n_typed} {feed}) for {len(entries)} names "
            f"-> {len(plan)} (name, day, query) pulls")
    else:
        plan = [(e, q, (start, end), window) for e in entries
                for q in queries_for(e, args.max_queries, override=override)]
    log(f"planned: {len(plan)} (company, query, window) items x up to {args.max_pages} pages")

    if args.dry_run:
        for e, q, (s0, e0), _ in plan:
            log(f"  DRY {e.ticker} [{e.factset_id}] {s0}..{e0} {q}")
        return 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(PROGRESS_PATH)
    seen_vectors, seen_exchanges = existing_keys(EXCHANGES_PATH)
    log(f"exchanges.jsonl already holds {len(seen_vectors)} chunks "
        f"({len(seen_exchanges)} distinct exchanges)")

    write_lock = threading.Lock()
    raw_dir = None if args.no_raw_cache else RAW_DIR
    stats = {"written": 0, "dupes": 0, "superseded": 0,
             "pages_ok": 0, "pages_empty": 0, "pages_failed": 0}
    queried, produced, failed_names = set(), set(), set()

    def work(item):
        entry, query, (w_start, w_end), wkey = item
        queried.add(entry.ticker)
        for offset in page_offsets(args.limit, args.max_pages):
            if ABORT.is_set():
                return                     # connector unavailable: same for every name
            if ledger.done(entry.factset_id, query, offset, window=wkey):
                if ledger.terminated(entry.factset_id, query, offset, window=wkey):
                    return                 # this query already ran out of results
                continue
            chunks, status, source = fetch_page(entry.factset_id, query, w_start, w_end,
                                                offset, args.limit, raw_dir=raw_dir,
                                                model=args.model)
            if status == "ok":
                kept, status = accept_payload(chunks, source or "model_text")
            else:
                kept = []
            terminal = not status.startswith("failed") and should_stop_paging(
                len(chunks), args.limit)
            ledger.record(entry.factset_id, query, offset, status, len(kept),
                          raw_returned=len(chunks), terminal=terminal, window=wkey)

            if status.startswith("failed"):
                stats["pages_failed"] += 1
                failed_names.add(entry.ticker)
                log(f"  {entry.ticker} offset={offset} {status}")
                return                     # do not page past an unknown
            if status == "empty":
                stats["pages_empty"] += 1
                return

            stats["pages_ok"] += 1
            produced.add(entry.ticker)
            rows = dedupe_rows([row_from_chunk(c, entry.ticker, query, source) for c in kept])
            with write_lock:
                fresh = []
                for r in rows:
                    if r["vector_id"] in seen_vectors:
                        stats["dupes"] += 1
                        continue
                    ekey = _exchange_key(r)
                    if ekey in seen_exchanges:
                        # same exchange, different documentID — an original/corrected
                        # pair. Never counted twice; flagged when the stored copy is
                        # the uncorrected one, which would warrant a rebuild.
                        stats["dupes"] += 1
                        if r.get("corrected") and not seen_exchanges[ekey]:
                            stats["superseded"] += 1
                            log(f"  NOTE {entry.ticker}: corrected copy of an already-"
                                f"stored uncorrected exchange ({r['vector_id']})")
                        continue
                    fresh.append(r)
                    seen_vectors.add(r["vector_id"])
                    seen_exchanges[ekey] = bool(r.get("corrected"))
                if fresh:
                    with EXCHANGES_PATH.open("a") as fh:
                        for r in fresh:
                            fh.write(json.dumps(r) + "\n")
                    stats["written"] += len(fresh)
                ledger.save()
            log(f"  {entry.ticker} offset={offset} kept={len(kept)} new={len(fresh)} "
                f"src={source}")
            if terminal:
                return

    try:
        if args.workers > 1:
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                list(pool.map(work, plan))
        else:
            for item in plan:
                work(item)
    finally:
        ledger.save()

    # Ledger-derived, not run-derived: a resumed run makes no calls for names it
    # already covered, and those must not read as uncovered. A name that only ever
    # errored is UNKNOWN coverage, not "no results".
    no_results = {e.ticker for e in entries
                  if ledger.coverage(e.factset_id) == "no_results"}
    incomplete = {e.ticker for e in entries
                  if ledger.coverage(e.factset_id) == "incomplete"}
    no_cov = build_no_coverage(entries, unresolved, no_results, incomplete, (start, end))
    NO_COVERAGE_PATH.write_text(json.dumps(no_cov, indent=1))
    log(f"no_coverage: {len(no_cov['no_factset_id'])} unmappable, "
        f"{len(no_cov['no_themes'])} themeless, {len(no_cov['no_results'])} no-results, "
        f"{len(no_cov['incomplete'])} incomplete -> {NO_COVERAGE_PATH}")
    log(f"done: {stats} ledger={ledger.counts()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
