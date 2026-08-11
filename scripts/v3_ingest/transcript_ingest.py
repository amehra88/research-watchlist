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
    python3 scripts/v3_ingest/transcript_ingest.py --window-months 1  # forward cron

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
cannot call it directly; the established repo pattern (newsdigest/factset_news.py,
cron_earnings_reviewer.py) is `claude -p` with the MCP tool allowed. Verbatim
fidelity matters more here than it does for news headlines, so:
  1. limit=50 responses are large enough that the harness spills the raw tool
     result to a file and hands the model the path. The model is asked to reply
     with ONLY that path; this script reads the JSON itself and the model never
     retypes a word (payload_source="file").
  2. Small responses stay inline, so the model echoes the raw JSON
     (payload_source="model_text"). Every chunk is then checked against the API's
     own textLength field; a single mismatch fails the whole page rather than
     admitting a paraphrase into the corpus.
If the harness stops spilling to files, path 2 still works — slower and costlier,
never silently lossy.

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
import os
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
MODEL = "claude-sonnet-4-6"                       # matches the other v3 wrappers
CLAUDE_TIMEOUT_S = 420

WINDOW_MONTHS = 9                                 # spec §3, operator's call
PAGE_LIMIT = 50                                   # FactSet max
MAX_PAGES = 3                                     # 150 chunks per (company, query)
MAX_QUERIES_PER_COMPANY = 6
DEFAULT_WORKERS = 3

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


def queries_for(entry: UniverseEntry, max_queries: int = MAX_QUERIES_PER_COMPANY) -> list:
    """Themes in operator-authored order, capped. A name with no assigned themes
    yields no queries — inventing one would contaminate the vocabulary."""
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
    def key(factset_id: str, query: str, offset: int) -> str:
        return f"{factset_id}|{query}|{offset}"

    def status(self, factset_id, query, offset) -> str | None:
        e = self.data["entries"].get(self.key(factset_id, query, offset))
        return e.get("status") if e else None

    def done(self, factset_id, query, offset) -> bool:
        s = self.status(factset_id, query, offset)
        return bool(s and (s == "ok" or s == "empty" or s.startswith("ok")))

    def record(self, factset_id, query, offset, status, n_chunks) -> None:
        with self._lock:
            self.data["entries"][self.key(factset_id, query, offset)] = {
                "status": status,
                "n_chunks": n_chunks,
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            }

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=1))
            tmp.replace(self.path)

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

def _claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def _fetch_prompt(factset_id, query, start, end, limit, offset) -> str:
    return (
        f"Call the {TOOL.split('__')[-1]} tool exactly once with these arguments, "
        "changing nothing:\n"
        f"  sources=['ALL_TRANSCRIPTS']\n"
        f"  ids=['{factset_id}']\n"
        f"  startDate='{start}'\n"
        f"  endDate='{end}'\n"
        f"  limit={limit}\n"
        f"  offset={offset}\n"
        f"  query='{query}'\n\n"
        "Do not modify the query text. Do not call any other tool. Do not summarise, "
        "analyse, review or read anything.\n\n"
        "THEN REPLY IN EXACTLY ONE OF TWO WAYS:\n"
        "1. If the tool result was too large and was saved to a file, reply with ONLY "
        "that absolute file path — no other words, and do not open the file.\n"
        "2. Otherwise reply with ONLY the tool's raw JSON response, copied character "
        "for character, with no code fences, no commentary and nothing omitted."
    )


def _extract_json_object(text: str):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def fetch_page(factset_id, query, start, end, offset, limit=PAGE_LIMIT,
               timeout=CLAUDE_TIMEOUT_S, raw_dir: Path | None = None):
    """-> (chunks, status, payload_source). Never raises; the caller records the status."""
    cmd = ["claude", "-p", _fetch_prompt(factset_id, query, start, end, limit, offset),
           "--output-format", "json", "--allowedTools", TOOL, "--model", MODEL]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              cwd=str(REPO_ROOT), env=_claude_env())
    except subprocess.TimeoutExpired:
        return [], "failed: timeout", None
    except Exception as e:                                   # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {e}", None

    if proc.returncode != 0:
        return [], f"failed: rc={proc.returncode} {(proc.stdout or proc.stderr or '')[:160]}", None
    try:
        env = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return [], "failed: unparseable claude envelope", None
    if env.get("is_error"):
        return [], f"failed: claude is_error {str(env.get('result'))[:160]}", None

    text = (env.get("result") or "").strip()
    payload, payload_source = None, None
    candidate = text.strip().strip("`").strip()
    if candidate.startswith("/") and "\n" not in candidate and len(candidate) < 500:
        try:
            payload = json.loads(Path(candidate).read_text())
            payload_source = "file"
        except (OSError, json.JSONDecodeError) as e:
            return [], f"failed: unreadable spill file ({type(e).__name__})", None
    if payload is None:
        payload = _extract_json_object(text)
        payload_source = "model_text"
    if payload is None:
        return [], "failed: no JSON in reply", None

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


def build_no_coverage(entries, unresolved, empty_names, window) -> dict:
    """Spec §4.1: names with no coverage are RECORDED, never dropped silently —
    and §11.5 requires every downstream figure to print its exclusions.

    Three distinct reasons, kept separate because they mean different things:
      no_factset_id  — we cannot even ask
      no_themes      — we can ask but have no operator-authored question to ask
                       (inventing one would contaminate the vocabulary, §11.2)
      no_results     — we asked and FactSet has nothing in the window
    """
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "window": {"start": window[0], "end": window[1]},
        "no_factset_id": unresolved,
        "no_themes": [{"ticker": e.ticker, "factset_id": e.factset_id,
                       "routes": e.reasons} for e in entries if not e.themes],
        "no_results": sorted(empty_names),
    }


def existing_vector_ids(path: Path) -> set:
    out = set()
    if not path.exists():
        return out
    with path.open() as fh:
        for line in fh:
            try:
                out.add(json.loads(line).get("vector_id"))
            except json.JSONDecodeError:
                continue
    return out


def window_bounds(months: int, today: dt.date | None = None):
    end = today or dt.date.today()
    y, m = end.year, end.month - months
    while m <= 0:
        m += 12
        y -= 1
    day = min(end.day, 28)
    return dt.date(y, m, day).isoformat(), end.isoformat()


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
    args = ap.parse_args(argv)

    watchlist = load_yaml(WATCHLIST_YAML)
    identity = load_yaml(IDENTITY_YAML)
    sc = load_yaml(SUPPLY_CHAIN_MANUAL)
    entries, unresolved = resolve_universe(watchlist, sc.get("edges") or [], identity)

    if args.ticker:
        wanted = set(args.ticker)
        entries = [e for e in entries if e.ticker in wanted]

    entries.sort(key=lambda e: e.ticker)
    start, end = window_bounds(args.window_months)

    log(f"window {start} -> {end}; universe {len(entries)} names, "
        f"{len(unresolved)} unresolved")
    for e in entries:
        log(f"  {e.ticker:<14} {e.factset_id:<12} themes={len(e.themes)} "
            f"[{'; '.join(e.reasons)}]" + ("  NO THEMES -> no queries" if not e.themes else ""))
    for u in unresolved:
        log(f"  UNRESOLVED {u['ticker']}: {u['reason']} (via {u['route']})")
    if args.print_universe:
        return 0

    plan = []
    for e in entries:
        for q in queries_for(e, args.max_queries):
            plan.append((e, q))
    log(f"planned: {len(plan)} (company, query) pairs x up to {args.max_pages} pages")

    if args.dry_run:
        for e, q in plan:
            log(f"  DRY {e.ticker} [{e.factset_id}] {q}")
        return 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(PROGRESS_PATH)
    seen_vectors = existing_vector_ids(EXCHANGES_PATH)
    log(f"exchanges.jsonl already holds {len(seen_vectors)} chunks")

    write_lock = threading.Lock()
    raw_dir = None if args.no_raw_cache else RAW_DIR
    stats = {"written": 0, "dupes": 0, "pages_ok": 0, "pages_empty": 0, "pages_failed": 0}
    queried, produced = set(), set()

    def work(item):
        entry, query = item
        queried.add(entry.ticker)
        for offset in page_offsets(args.limit, args.max_pages):
            if ledger.done(entry.factset_id, query, offset):
                continue
            chunks, status, source = fetch_page(entry.factset_id, query, start, end,
                                                offset, args.limit, raw_dir=raw_dir)
            if status == "ok":
                kept, status = accept_payload(chunks, source or "model_text")
            else:
                kept = []
            ledger.record(entry.factset_id, query, offset, status, len(kept))

            if status.startswith("failed"):
                stats["pages_failed"] += 1
                log(f"  {entry.ticker} offset={offset} {status}")
                return                     # do not page past an unknown
            if status == "empty":
                stats["pages_empty"] += 1
                return

            stats["pages_ok"] += 1
            produced.add(entry.ticker)
            rows = dedupe_rows([row_from_chunk(c, entry.ticker, query, source) for c in kept])
            with write_lock:
                fresh = [r for r in rows if r["vector_id"] not in seen_vectors]
                stats["dupes"] += len(rows) - len(fresh)
                if fresh:
                    with EXCHANGES_PATH.open("a") as fh:
                        for r in fresh:
                            fh.write(json.dumps(r) + "\n")
                    seen_vectors.update(r["vector_id"] for r in fresh)
                    stats["written"] += len(fresh)
                ledger.save()
            log(f"  {entry.ticker} offset={offset} kept={len(kept)} new={len(fresh)} "
                f"src={source}")
            if should_stop_paging(len(chunks), args.limit):
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

    no_cov = build_no_coverage(entries, unresolved, queried - produced, (start, end))
    NO_COVERAGE_PATH.write_text(json.dumps(no_cov, indent=1))
    log(f"no_coverage: {len(no_cov['no_factset_id'])} unmappable, "
        f"{len(no_cov['no_themes'])} themeless, {len(no_cov['no_results'])} no-results "
        f"-> {NO_COVERAGE_PATH}")
    log(f"done: {stats} ledger={ledger.counts()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
