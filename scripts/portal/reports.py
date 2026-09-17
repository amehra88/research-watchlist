"""Today cards: scripts/portal/reports.py — RIS4 portal builder, Task 3.

Builds `build_reports(out_dir, days)`: one `data/reports/<date>.json` per day
that has at least one card, drawn from four streams — the 5-section Daily
Digest (ws/etfflows/is/podcasts/etfflows-table), the standalone news-digest
emails (premarket/postmarket), and the two alert ledgers (thesis, stage).
Returns manifest-ready card summaries for Task 4. Also builds `upcoming(days)`
(always `[]` today — see its docstring for why).

The ETF-trades parser (`etf_trades()`, ws-report text parsing, `by_ticker`
index) lives in the sibling module `scripts/portal/etf_trades.py` — split out
in fix round 1 (controller-directed, size/responsibility separation only; the
public interface and output shape are unchanged). Nothing in this repo imports
`etf_trades` from here, so there is no re-export shim.

Every zero-arg-default path here reads live data from REPO (see
scripts/portal/__init__.py) via the module-level `DEFAULT_PATHS`. Every public
function accepts an explicit `paths: Paths` override so tests run only against
fixtures under scripts/portal/fixtures/reports/ — see the `Paths` dataclass below.
Read-only: this module never writes into notes/, config/, or state/; its only
write is `<out_dir>/data/reports/<date>.json`, and only when an `out_dir` is
actually passed in.

One exception to "everything is overridable": the `thesis_alerts` card joins
state/thesis/alerts_sent.jsonl rows to human text via
`scripts.thesis.thesis_report.alert_events()`, which — like `thesis_io` in
vault.py — hardcodes its own STATE_DIR/NOTES against the live REPO and has no
path-override hook. Tests still stay fixture-safe: alert_events() recomputes
its events from live production state, so a fixture's deliberately-invented id
(e.g. "status:FIXTURE_TICKER:...") can never collide with it, which exercises
exactly the "fall back to id/ticker text" path the brief asks for.
build_reports() calls alert_events() once for the whole window (see
_thesis_events_for_window()) rather than once per qualifying day; day_cards()
still computes it fresh on demand when called standalone with no cache.

Slice 3 Task 1: the `thesis_alerts` card now groups today's alerts_sent.jsonl
rows into `items` (one per (ticker, assumption_id)) carrying the assumption's
own `statement` (from notes/{ticker}/_thesis.md, via vault.load_note — never
thesis_io.load, which has the same no-override-hook problem as
alert_events() above), a `from`/`to` status transition (id parse for `to`,
state/thesis/changes.jsonl for `from`), a `strength3_challenges` count, and up
to 3 evidence rows from `evidence.py`'s state/thesis/evidence_log.jsonl index
(paths.thesis_state, NOT paths.evidence_state — that field points at
state/evidence/claims.jsonl, a different, unrelated corpus). `note:...` rows
(earnings-note-landed events) are dropped from this card entirely (they still
appear in the Notes tab); `score:...` rows (watchlist.yaml score proposals)
get a minimal item with no evidence, since evidence_log.jsonl is keyed by
assumption id, not by score key. `text` stays a plain-string field (backward
compatible) but is now rendered from `items`, one paragraph per item — see
_render_thesis_item_text(). Both the evidence index and (like events_cache)
the alert_events() join are computed once per build window, not once per
qualifying day.

Slice 3 Task 2: the `stage_alerts` card now also carries `items` (one per
alerts_sent.jsonl row, in ledger order): `{id, kind, theme, ticker, stage,
line, exchange, trend, tier_names, theme_link}` — `line` is render()'s own
unchanged existing text (kept so `text` stays backward compatible: it is
always `line` first, with enrichment appended only when there is any, so a
fully-degraded row's `text` is byte-identical to the old plain-text card).
`exchange` (evidence.exchange_for) is the analyst question + management
answer render()'s own `_cite()` would point at, resolved via `_cite_target()`
(mirrors render()'s stage2/stage3 ticker/date picks exactly — gate/stage4
cite nothing, matching render() itself). `trend` (evidence.breadth_trend) and
`tier_names` (evidence.tier_names_on_theme, via `identity.load_universe()`)
are per-theme, so every kind gets them, not just stage2/stage3. All three are
gated on the SAME `snap is not None` check the existing line already used —
a load failure (any of diffusion.json/topic_map.jsonl/exchanges.jsonl
missing) degrades `exchange`/`trend` to `None` and `tier_names` to `{}` for
every row that day, one log line, never an error. `ex_by_doc`
(evidence.index_exchanges_by_document) and `universe` are each built once per
card, not once per event.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Bootstrap ONLY to make this package importable when this module is loaded as a bare
# `reports` module (the no-pytest test harness convention: sys.path.insert(0, dirname)
# + `import reports`, same as scripts/v3_ingest/test_transcript_ingest.py and
# scripts/portal/vault.py / identity.py). This uses __file__ solely to find our OWN
# sibling __init__.py.
_here_parent = str(Path(__file__).resolve().parent.parent)
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

# scripts/portal/ itself, for the bare sibling imports below (evidence.py,
# vault.py) -- same two-insert bootstrap as state_bundles.py's own (its
# module docstring explains why both inserts are needed).
_here_str = str(Path(__file__).resolve().parent)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import evidence  # noqa: E402
import identity  # noqa: E402
import vault  # noqa: E402

sys.path.insert(0, str(REPO / "scripts"))
from thesis import thesis_report  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "topics"))
import stage_alert  # noqa: E402


def log(msg: str) -> None:
    print(f"[reports] {msg}", flush=True)


# ---------------------------------------------------------------------------
# STREAMS: the five Daily Digest sections, in combine_and_send.py's own order
# ---------------------------------------------------------------------------
def _combine_and_send_streams() -> list[tuple[str, str]] | None:
    """[(title, path_template)] from /root/daily/combine_and_send.py:REPORTS, imported
    by file path (that module lives outside this repo and is never on sys.path).
    Importing it only runs module-level code (REPORTS + function defs); main() is
    behind `if __name__ == '__main__'`, so this never sends an email. None on any
    failure — the caller falls back to the literal paths from the brief.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            "_ris4_combine_and_send", "/root/daily/combine_and_send.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return [(title, path_template) for title, path_template, _required in mod.REPORTS]
    except Exception as exc:  # noqa: BLE001 — any import failure means "use the fallback"
        log(f"combine_and_send import failed ({exc}); using literal fallback STREAMS")
        return None


def _default_streams(ws_reports: Path, is_reports: Path, podcasts_reports: Path,
                      logs: Path) -> list[tuple[str, str]]:
    imported = _combine_and_send_streams()
    if imported is not None:
        return imported
    return [
        ("ETF UPDATE", str(ws_reports / "report_{date}.txt")),
        ("ETF FLOWS & CROWDING", str(logs / "report_etfflows_{date}.txt")),
        ("INSIDER ACTIVITY", str(is_reports / "report_{date}.txt")),
        ("PODCAST DIGEST", str(podcasts_reports / "report_{date}.txt")),
        ("ETF FLOW DETAIL", str(logs / "report_etfflows_table_{date}.txt")),
    ]


# ---------------------------------------------------------------------------
# Paths: every filesystem location this module touches, overridable for tests
# ---------------------------------------------------------------------------
@dataclass
class Paths:
    repo: Path = REPO
    ws_reports: Path = None
    is_reports: Path = None
    podcasts_reports: Path = None
    logs: Path = None
    notes: Path = None
    watchlist: Path = None
    thesis_state: Path = None
    topics_state: Path = None
    transcripts_state: Path = None
    evidence_state: Path = None
    streams: list = None

    def __post_init__(self):
        self.ws_reports = self.ws_reports or Path("/root/ws/data/reports")
        self.is_reports = self.is_reports or Path("/root/is/reports")
        self.podcasts_reports = self.podcasts_reports or Path("/root/podcasts/data/reports")
        self.logs = self.logs or (self.repo / "logs")
        self.notes = self.notes or (self.repo / "notes")
        self.watchlist = self.watchlist or (self.repo / "config" / "watchlist.yaml")
        self.thesis_state = self.thesis_state or (self.repo / "state" / "thesis")
        self.topics_state = self.topics_state or (self.repo / "state" / "topics")
        self.transcripts_state = self.transcripts_state or (self.repo / "state" / "transcripts")
        self.evidence_state = self.evidence_state or (self.repo / "state" / "evidence")
        if self.streams is None:
            self.streams = _default_streams(self.ws_reports, self.is_reports,
                                             self.podcasts_reports, self.logs)


DEFAULT_PATHS = Paths()
STREAMS = DEFAULT_PATHS.streams  # module-level export per the brief's literal interface


# ---------------------------------------------------------------------------
# jsonl helper
# ---------------------------------------------------------------------------
def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ---------------------------------------------------------------------------
# news_digest_files
# ---------------------------------------------------------------------------
_NEWS_DIGEST_RE = re.compile(r"^news_digest_(premarket|postmarket)_(\d{8})_(\d{6})\.txt$")


def news_digest_files(day: str, paths: Paths = None) -> dict:
    """{mode: Path} for the news-digest email artifacts on `day` (ISO YYYY-MM-DD).
    Per (date, mode) keeps the LARGEST file among possibly-several runs (a later
    stub re-run must not shadow the real, larger, earlier one). 'brief'-mode files
    (an older naming convention) are excluded by construction — the filename regex
    only matches premarket/postmarket.
    """
    paths = paths or DEFAULT_PATHS
    yyyymmdd = day.replace("-", "")
    best: dict[str, Path] = {}
    if not paths.logs.is_dir():
        return best
    for p in paths.logs.glob(f"news_digest_*_{yyyymmdd}_*.txt"):
        m = _NEWS_DIGEST_RE.match(p.name)
        if not m:
            continue
        mode = m.group(1)
        cur = best.get(mode)
        if cur is None or p.stat().st_size > cur.stat().st_size:
            best[mode] = p
    return best


# ---------------------------------------------------------------------------
# digest sections (the 5 Daily Digest streams)
# ---------------------------------------------------------------------------
def _digest_sections(day: str, paths: Paths) -> list[dict]:
    sections = []
    for title, template in paths.streams:
        p = Path(template.format(date=day))
        if not p.exists():
            log(f"reports: {day} digest/{title} missing")
            continue
        text = p.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            log(f"reports: {day} digest/{title} empty")
            continue
        if title == "INSIDER ACTIVITY" and len(text.encode("utf-8")) < 300:
            # the "No conviction-level insider activity." stub
            log(f"reports: {day} digest/{title} stub dropped ({len(text.encode('utf-8'))} B)")
            continue
        sections.append({"title": title, "text": text})
    return sections


# ---------------------------------------------------------------------------
# thesis_alerts card
# ---------------------------------------------------------------------------
def _thesis_events_for_window(today: date, days: int) -> dict:
    """One thesis_report.alert_events() call covering the whole
    [today - (days-1) .. today] build window (plus alert_events' own
    ALERT_LOOKBACK_DAYS margin), for build_reports() to compute ONCE and pass to
    every day_cards() call instead of once per qualifying day -- each call
    re-globs notes/*/[0-9]*-[1-4]Q[0-9][0-9].md and re-reads changes.jsonl/
    evidence_log.jsonl in full. {} (not an error) when alert_events() itself is
    unavailable; every row then falls back to its raw id text, same as the
    per-day on-demand path below.
    """
    earliest = today - timedelta(days=max(days - 1, 0))
    try:
        since_ts = datetime.combine(
            earliest - timedelta(days=thesis_report.ALERT_LOOKBACK_DAYS),
            datetime.min.time(), timezone.utc).isoformat()
        return {e["id"]: e for e in thesis_report.alert_events(since_ts, today)}
    except Exception as exc:  # noqa: BLE001
        log(f"thesis_alerts: alert_events() unavailable for the {days}-day window "
            f"({exc}); falling back to id/ticker text for all rows")
        return {}


def _events_by_id_for_day(day: str, paths: Paths) -> dict:
    """{id: event} for just this one day -- the day_cards()-standalone path
    (no events_cache supplied). Refactored out of _thesis_alert_card so both
    this and _thesis_events_for_window() share the exact same
    since_ts/alert_events() call shape.
    """
    day_date = date.fromisoformat(day)
    try:
        since_ts = datetime.combine(
            day_date - timedelta(days=thesis_report.ALERT_LOOKBACK_DAYS),
            datetime.min.time(), timezone.utc).isoformat()
        return {e["id"]: e for e in thesis_report.alert_events(since_ts, day_date)}
    except Exception as exc:  # noqa: BLE001
        log(f"thesis_alerts {day}: alert_events() unavailable ({exc}); "
            f"falling back to id/ticker text for all rows")
        return {}


# alerts_sent.jsonl id formats, all built by thesis_report.alert_events()'s own
# f-strings -- parsed structurally here (never via arrow-parsing the human
# `text`) so grouping/`to` still work even when a fixture id can never match a
# live alert_events() event (see the module docstring's fixture-isolation note).
#   status:{ticker}:{assumption_id}:{to}:{date}
#   chal3:{ticker}:{source_id}:{assumption_id}   (source_id itself may contain
#                                                  colons -- assumption_id never
#                                                  does, so it's always the LAST
#                                                  colon-separated segment)
#   score:{ticker}:{key}:{value}                 (key is a watchlist.yaml score
#                                                  key, e.g. ai_positioning --
#                                                  NOT a thesis assumption id)
#   note:{ticker}:{filename}                     (dropped entirely, see below)
def _parse_alert_id(id_: str) -> dict:
    parts = id_.split(":")
    kind = parts[0] if parts else "?"
    ticker = parts[1] if len(parts) > 1 else "?"
    aid = to = None
    if kind == "status" and len(parts) >= 5:
        aid, to = parts[2], parts[3]
    elif kind == "chal3" and len(parts) >= 3:
        aid = parts[-1]
    elif kind == "score" and len(parts) >= 3:
        aid = parts[2]
    return {"kind": kind, "ticker": ticker, "assumption_id": aid, "to": to}


def _changes_from_index(paths: Paths) -> dict:
    """{(ticker, assumption_id, to): from} from changes.jsonl's own 'status'-kind
    rows -- the only place a status change's `from` value lives structurally
    (alerts_sent.jsonl's id only carries `to`, and the human `text` embeds
    `from` only as prose). File is small and append-only chronological, so a
    later write for the same key naturally overwrites an earlier one, which is
    what we want (the LATEST from->to transition for that key).
    """
    idx: dict = {}
    for c in _read_jsonl(paths.thesis_state / "changes.jsonl"):
        if c.get("kind") != "status":
            continue
        idx[(c.get("ticker"), c.get("assumption_id"), c.get("to"))] = c.get("from")
    return idx


def _load_thesis_fm(ticker: str, paths: Paths) -> dict | None:
    """Loads notes/{ticker}/_thesis.md via vault.load_note (never
    thesis_io.load -- thesis_io hardcodes the live REPO with no path-override
    hook, same reason vault.py itself avoids it for the thesis body/fm). A
    single-file load, not a full vault.discover() (~8.5s per
    state_bundles.py's own docstring) -- this only runs for tickers that
    actually appear in today's alerts_sent.jsonl rows.
    """
    p = paths.notes / ticker / "_thesis.md"
    if not p.exists():
        return None
    try:
        ref = vault.NoteRef(p, f"{ticker}/_thesis.md", ticker, "thesis", None, None, p.stem, p.stat().st_size)
        return vault.load_note(ref)["fm"]
    except Exception as exc:  # noqa: BLE001
        log(f"thesis_alerts: could not load {p} for a statement lookup ({exc})")
        return None


def _statement_lookup(ticker: str, aid: str, bundles_by_ticker: dict | None, paths: Paths) -> str:
    """The assumption's own `statement` from its ticker's _thesis.md frontmatter,
    preferring an in-memory bundle from THIS SAME build if the caller has one
    (build_portal.py's own stage order runs reports before tickers/ingest, so
    that branch is not exercised by the live path today -- see this module's
    own docstring section on why it stays available for a future re-order or
    for tests that construct bundles directly). Falls back to `aid` itself
    when no thesis, no matching assumption id, or a load failure.
    """
    fm = None
    if bundles_by_ticker and ticker in bundles_by_ticker:
        fm = (bundles_by_ticker[ticker].get("thesis") or {}).get("fm_without_body")
    if not fm:
        fm = _load_thesis_fm(ticker, paths)
    for a in (fm or {}).get("assumptions") or []:
        if a.get("id") == aid:
            return a.get("statement") or aid
    return aid


def _within_days(d: str | None, anchor_day: str, window: int) -> bool:
    if not d:
        return False
    try:
        return abs((date.fromisoformat(anchor_day) - date.fromisoformat(str(d)[:10])).days) <= window
    except ValueError:
        return False


def _render_thesis_item_text(item: dict) -> str:
    text = f"{item['ticker']} — {item['statement']}"
    if item["to"]:
        trans = f"{item['from']}→{item['to']}" if item["from"] else f"→{item['to']}"
        text += f" — {trans}"
    if item["evidence"]:
        e0 = item["evidence"][0]
        text += f" ({len(item['evidence'])} evidence)"
        # earnings_break/earnings_confirm rows carry an empty quote (the
        # transcript exchange isn't quoted verbatim in evidence_log.jsonl) --
        # fall back to `why` (always populated) rather than render a dangling
        # `: ""`, which reads as broken enrichment, not "no evidence".
        snippet = e0.get("quote") or e0.get("why") or ""
        if snippet:
            text += f" · {e0.get('date')} {e0.get('source')}: \"{snippet[:160]}\""
    return text


def _thesis_alert_card(day: str, paths: Paths, events_cache: dict = None,
                        evidence_index: dict = None, bundles_by_ticker: dict = None) -> dict | None:
    """events_cache/evidence_index are optional caches from
    _thesis_events_for_window()/build_reports() (computed once for the whole
    build window); None (the day_cards()-standalone default) means compute
    them fresh for just this one day/build, same convention as
    events_cache always had. bundles_by_ticker is additive (see
    _statement_lookup's own docstring for why it's currently always None on
    the live path).

    Builds `items` grouped by (ticker, assumption_id) from today's
    alerts_sent.jsonl rows, one item per group, and `text` = one paragraph per
    item (see _render_thesis_item_text). 'note:...' rows (earnings-note-landed
    events) are dropped entirely here -- they still show up in the Notes tab,
    just never in this card. 'score:...' rows (watchlist.yaml score
    proposals, not thesis assumptions) get a minimal item of their own: no
    evidence/note_links (evidence_log.jsonl is keyed by assumption id, not by
    score key), `statement` falls back to the live alert_events() text for
    that row, else the raw id.
    """
    rows = [r for r in _read_jsonl(paths.thesis_state / "alerts_sent.jsonl")
            if str(r.get("ts", ""))[:10] == day]
    if not rows:
        return None

    events_by_id = events_cache if events_cache is not None else _events_by_id_for_day(day, paths)
    ev_index = evidence_index if evidence_index is not None else evidence.load_index(
        evidence.Paths(thesis_state=paths.thesis_state))
    changes_idx = _changes_from_index(paths)

    groups: dict[tuple, dict] = {}
    for r in rows:
        rid = r.get("id", "")
        parsed = _parse_alert_id(rid)
        if parsed["kind"] == "note":
            continue  # DROP earnings-note-landed lines -- see docstring above
        ticker = r.get("ticker") or parsed["ticker"]
        aid = parsed["assumption_id"] or rid
        key = (ticker, aid)
        g = groups.setdefault(key, {"ticker": ticker, "assumption_id": aid,
                                     "from": None, "to": None,
                                     "is_score": parsed["kind"] == "score", "score_row_id": None})
        if parsed["kind"] == "score":
            g["score_row_id"] = g["score_row_id"] or rid
        else:
            g["is_score"] = False  # a real status/chal3 row always wins the classification
        if parsed["kind"] == "status":
            g["to"] = parsed["to"]
            g["from"] = changes_idx.get((ticker, aid, parsed["to"]))

    if not groups:
        return None  # every row on this day was a dropped 'note' kind

    items, texts = [], []
    for (ticker, aid), g in groups.items():
        if g["is_score"]:
            ev = events_by_id.get(g["score_row_id"])
            statement = ev["text"] if ev else g["score_row_id"]
            evid_rows, ev_top, strength3, note_links = [], [], 0, []
        else:
            statement = _statement_lookup(ticker, aid, bundles_by_ticker, paths)
            evid_rows = ev_index.get((ticker, aid), [])
            # Window THEN cap: evidence.top() ranks strength-desc/date-desc with
            # no age filter by design (see its own docstring), so filtering the
            # window after capping at 3 can drop a real in-window row entirely
            # when three older, stronger rows fill all three slots first.
            windowed = [r for r in evid_rows if _within_days(r.get("date"), day, 7)]
            ev_top = evidence.top(windowed, 3)
            strength3 = sum(1 for r in evid_rows
                             if r.get("direction") == "challenge" and r.get("strength") == 3)
            note_links = sorted({r["ref"] for r in evid_rows if str(r.get("ref") or "").startswith("notes/")})
        item = {"ticker": ticker, "assumption_id": aid, "statement": statement,
                "from": g["from"], "to": g["to"], "strength3_challenges": strength3,
                "evidence": ev_top, "note_links": note_links}
        items.append(item)
        texts.append(_render_thesis_item_text(item))

    body = "\n\n".join(texts)
    return {"id": f"thesis_alerts:{day}", "kind": "thesis_alerts", "date": day,
            "title": f"Thesis alerts — {day}", "text": body,
            "bytes": len(body.encode("utf-8")), "items": items}


# ---------------------------------------------------------------------------
# stage_alerts card
# ---------------------------------------------------------------------------
def _needed_tickers(rows: list, snap: dict) -> set:
    """Every ticker today's stage-alert `rows` could possibly cite -- the row's own
    `ticker` (stage3) plus, for stage2 (whose ledger row carries no ticker at all),
    the SAME theme-wide "first asked" ticker `_cite_target` resolves (identical call,
    so the tickers this loads for are always exactly the tickers render()/
    exchange_for() will actually look up -- never a mismatch, never a silent miss).
    gate/stage4 contribute nothing (`_cite_target` returns None for them, matching
    render() itself never citing them)."""
    needed = set()
    for r in rows:
        ticker = r.get("ticker")
        if ticker:
            needed.add(ticker)
        target = _cite_target(r.get("kind", "?"), r.get("theme", "?"), ticker, snap)
        if target:
            needed.add(target[1])
    return needed


def _stage_alert_render_inputs(paths: Paths, rows: list):
    """(snap, topic_map_rows, exchanges) or (None, None, None) on any load failure —
    mirrors stage_alert.py's own main(), read-only (never calls run()/save_state(),
    which write state/topics/stages.json).

    Fix round 1 (reviewer-required): `exchanges` is no longer the WHOLE file loaded
    via `theme_notes.load_sources()` -- it is streamed once via
    `evidence.load_exchanges_by_ticker()`, scoped to `_needed_tickers(rows, snap)`
    (computed from TODAY's `rows`, before the exchanges.jsonl read happens at all).
    This same filtered `ex` is handed to BOTH `stage_alert.render()` (in
    `_stage_alert_card`, below) and `evidence.exchange_for()` -- render() only ever
    cites the one ticker `_cite_target` already resolved for an event, so scoping to
    that same set can never drop a citation render() itself would have made."""
    try:
        snap = json.loads((paths.topics_state / "diffusion.json").read_text(encoding="utf-8"))
        tm_rows = evidence.load_topic_map_rows(paths.topics_state / "topic_map.jsonl")
        needed = _needed_tickers(rows, snap)
        ex = evidence.load_exchanges_by_ticker(needed, paths.transcripts_state / "exchanges.jsonl")
        return snap, tm_rows, ex
    except Exception as exc:  # noqa: BLE001
        log(f"stage_alerts: render inputs unavailable ({exc}); "
            f"degrading to 'kind · theme · ticker' text")
        return None, None, None


_STAGE_NUM = {"stage2": 2, "stage3": 3, "stage4": 4}  # gate has no single stage number
_TIER_TEXT_CAP = 8


def _cite_target(kind: str, theme: str, ticker: str | None, snap: dict) -> tuple | None:
    """(theme, ticker, date) for the SAME analyst exchange stage_alert.render()'s own
    `_cite()` calls would resolve for this event -- deliberately calls stage_alert's
    "private" `_theme_pairs()` (leading underscore) rather than reimplementing its
    filter, so a future change to what counts as an "asked" pair can never silently
    drift between render()'s own line and this card's exchange/trend enrichment.
    gate/stage4 events cite no single ticker -- render() itself never calls `_cite`
    for those kinds either, so this returns None for them by construction (the `if`
    chain below simply has no branch for them)."""
    pairs = stage_alert._theme_pairs(snap, theme)  # noqa: SLF001 -- see docstring
    if kind == "stage3" and ticker:
        p = next((p for p in pairs if p["ticker"] == ticker), None)
        fq = p.get("first_question_date") if p else None
        return (theme, ticker, fq) if fq else None
    if kind == "stage2":
        asked = [p for p in pairs if p.get("first_question_date")]
        if not asked:
            return None
        first = min(asked, key=lambda p: p["first_question_date"])
        return (theme, first["ticker"], first["first_question_date"])
    return None


def _render_stage_item_text(line: str, exch: dict | None, trend: dict | None,
                             tier_names: dict | None) -> str:
    """`line` (render()'s own existing text) stays first and unchanged -- backward
    compatible with every consumer of the old plain-text card. Each enrichment
    segment is appended only when it has something to say, so a row with no
    exchange/trend/tier_names data (a gap, or a gate/stage4 kind with no citation)
    renders IDENTICAL to the pre-enrichment text -- see
    test_stage_alerts_degrades_when_state_files_absent."""
    parts = [line]
    if exch and (exch.get("question") or exch.get("answer")):
        q = (exch.get("question") or "")[:200]
        qa = f'Q: "{q}"'
        if exch.get("answer"):
            qa += f' — A: "{exch["answer"][:200]}"'
        parts.append(qa)
    if trend:
        prev_b = trend.get("prev_n_banks")
        prev_c = trend.get("prev_n_companies")
        parts.append(f"breadth {trend.get('n_banks', 0)} banks / {trend.get('n_companies', 0)} cos "
                      f"(prev {prev_b if prev_b is not None else '-'}/"
                      f"{prev_c if prev_c is not None else '-'})")
    names = ((tier_names.get("tier_1") or []) + (tier_names.get("tier_2") or [])) if tier_names else []
    if names:
        shown = ", ".join(names[:_TIER_TEXT_CAP])
        suffix = f" (+{len(names) - _TIER_TEXT_CAP} more)" if len(names) > _TIER_TEXT_CAP else ""
        parts.append(f"tier 1/2 on theme: {shown}{suffix}")
    return " ".join(parts)


def _stage_alert_card(day: str, paths: Paths) -> dict | None:
    rows = [r for r in _read_jsonl(paths.topics_state / "alerts_sent.jsonl")
            if r.get("as_of") == day]
    if not rows:
        return None

    snap, tm_rows, ex = _stage_alert_render_inputs(paths, rows)
    ex_by_doc = evidence.index_exchanges_by_document(ex) if ex is not None else None
    universe = None
    if snap is not None:
        try:
            universe = identity.load_universe(paths.watchlist, paths.notes)
        except Exception as exc:  # noqa: BLE001
            log(f"stage_alerts {day}: load_universe() unavailable ({exc}); tier_names will be {{}}")
    else:
        # one line for the whole card, not once per row -- every row degrades the
        # same way when there is no snapshot at all.
        log(f"stage_alerts {day}: no diffusion snapshot for any of today's "
            f"{len(rows)} row(s); exchange/trend null, tier_names {{}} for all")

    items, lines = [], []
    for r in rows:
        kind, theme, ticker = r.get("kind", "?"), r.get("theme", "?"), r.get("ticker")
        line = None
        if snap is not None:
            try:
                e = {"kind": kind, "theme": theme, "ticker": ticker}
                line = stage_alert.render(e, snap, tm_rows, ex, day)
            except Exception as exc:  # noqa: BLE001
                log(f"stage_alerts {day}: render() failed for {kind}/{theme}/{ticker} "
                    f"({exc}); degrading this row")
        if line is None:
            line = f"{kind} · {theme}" + (f" · {ticker}" if ticker else "")

        exch, trend, tier_names = None, None, {}
        if snap is not None:
            target = _cite_target(kind, theme, ticker, snap)
            if target:
                try:
                    exch = evidence.exchange_for({"theme": target[0], "ticker": target[1], "date": target[2]},
                                                  tm_rows, ex, ex_by_doc)
                except Exception as exc:  # noqa: BLE001
                    log(f"stage_alerts {day}: exchange_for() failed for {kind}/{theme}/{ticker} "
                        f"({exc}); exchange=null")
            try:
                trend = evidence.breadth_trend(theme, snap)
            except Exception as exc:  # noqa: BLE001
                log(f"stage_alerts {day}: breadth_trend() failed for {theme} ({exc}); trend=null")
            if universe is not None:
                try:
                    tier_names = evidence.tier_names_on_theme(theme, snap, universe)
                except Exception as exc:  # noqa: BLE001
                    log(f"stage_alerts {day}: tier_names_on_theme() failed for {theme} "
                        f"({exc}); tier_names={{}}")

        theme_link = f"notes/themes/{theme}.md" if (paths.notes / "themes" / f"{theme}.md").exists() else None
        item = {"id": r.get("id"), "kind": kind, "theme": theme, "ticker": ticker,
                "stage": _STAGE_NUM.get(kind), "line": line, "exchange": exch, "trend": trend,
                "tier_names": tier_names, "theme_link": theme_link}
        items.append(item)
        lines.append(f"- {_render_stage_item_text(line, exch, trend, tier_names)}")

    body = "\n".join(lines)
    return {"id": f"stage_alerts:{day}", "kind": "stage_alerts", "date": day,
            "title": f"Stage alerts — {day}", "text": body,
            "bytes": len(body.encode("utf-8")), "items": items}


# ---------------------------------------------------------------------------
# day_cards
# ---------------------------------------------------------------------------
def day_cards(day: str, paths: Paths = None, thesis_events_cache: dict = None,
              thesis_evidence_index: dict = None, thesis_bundles_by_ticker: dict = None) -> list[dict]:
    """All cards for one ISO date: premarket/postmarket news-digest emails, the
    5-section Daily Digest, thesis alerts, and stage alerts. Any stream that has
    no content for `day` logs one line and is omitted — never an error.

    `thesis_events_cache` is passed straight through to _thesis_alert_card(); see
    _thesis_events_for_window() — build_reports() supplies one so alert_events()
    runs once per build, not once per qualifying day. None (the default) means
    day_cards() computes it on demand for just this one day, so it stays usable
    standalone. `thesis_evidence_index` is the same idea for
    evidence.load_index() (2,685 rows -- also a once-per-build cost, not a
    once-per-day one). `thesis_bundles_by_ticker` is passed straight through to
    _statement_lookup() — see its own docstring for why it's always None today.
    """
    paths = paths or DEFAULT_PATHS
    cards = []

    files = news_digest_files(day, paths)
    for mode in ("premarket", "postmarket"):
        p = files.get(mode)
        if p is None:
            log(f"reports: {day} {mode} absent")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        first_line = text.splitlines()[0].strip() if text.strip() else ""
        title = first_line or f"News digest — {mode} — {day}"
        cards.append({"id": f"{mode}:{day}", "kind": mode, "date": day, "title": title,
                      "text": text, "bytes": len(text.encode("utf-8"))})

    sections = _digest_sections(day, paths)
    if sections:
        # Banner each section's own title into the blob (matching the live email's
        # own "#### TITLE ####" banners) so a `text`-only consumer (e.g. the Reports
        # archive screen) doesn't show five unlabeled sections run together --
        # `sections` still carries the titles separately for a richer renderer.
        text = "\n\n".join(f"{s['title']}\n{s['text']}" for s in sections)
        cards.append({"id": f"digest:{day}", "kind": "digest", "date": day,
                      "title": f"Daily Digest — {day}", "text": text,
                      "bytes": len(text.encode("utf-8")), "sections": sections})

    ta = _thesis_alert_card(day, paths, events_cache=thesis_events_cache,
                             evidence_index=thesis_evidence_index,
                             bundles_by_ticker=thesis_bundles_by_ticker)
    if ta:
        cards.append(ta)

    sa = _stage_alert_card(day, paths)
    if sa:
        cards.append(sa)

    return cards


# ---------------------------------------------------------------------------
# build_reports
# ---------------------------------------------------------------------------
def build_reports(out_dir: Path, days: int = 14, paths: Paths = None,
                   today: date = None) -> list[dict]:
    """Writes <out_dir>/data/reports/<date>.json = {date, cards} for each of the
    trailing `days` days (including today) that has >= 1 card; returns manifest
    summaries {id, kind, date, title, bytes, file} (file relative to out_dir) for
    every card written, across all dates, newest-date first.
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    out_dir = Path(out_dir)
    reports_dir = out_dir / "data" / "reports"
    events_cache = _thesis_events_for_window(today, days)
    # loaded once for the whole build window, same reasoning as events_cache
    # just above -- day_cards() would otherwise re-read 2,685 evidence rows
    # once per qualifying day.
    evidence_index = evidence.load_index(evidence.Paths(thesis_state=paths.thesis_state))

    summaries = []
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        cards = day_cards(d, paths, thesis_events_cache=events_cache,
                           thesis_evidence_index=evidence_index)
        if not cards:
            log(f"build_reports: no cards for {d}")
            continue
        # mkdir lazily -- a caller must be able to tell "no reports in range" (no
        # dir at all) apart from "ran but everything landed under it".
        reports_dir.mkdir(parents=True, exist_ok=True)
        out_path = reports_dir / f"{d}.json"
        out_path.write_text(json.dumps({"date": d, "cards": cards}, indent=1), encoding="utf-8")
        rel = str(out_path.relative_to(out_dir))
        for c in cards:
            summaries.append({"id": c["id"], "kind": c["kind"], "date": c["date"],
                               "title": c["title"], "bytes": c["bytes"], "file": rel})
    return summaries


# ---------------------------------------------------------------------------
# upcoming
# ---------------------------------------------------------------------------
def upcoming(days: int = 14, paths: Paths = None) -> list[dict]:
    """Forward-looking earnings/conference calendar for the portal's 'Upcoming' rail.

    scripts/v3_ingest/transcript_ingest.py fetches the FactSet calendar live, on
    demand, inside fetch_calendar() -- it is never persisted anywhere. Everything
    written under state/transcripts/ was inspected for a forward-looking date and
    has none: per-ticker <TICKER>.json carries only last_iacc/last_period/
    last_processed_at/last_note_path (backward-looking); _progress.json is an
    LLM-query dedup ledger; _no_coverage.json is a diagnostic snapshot of routing
    gaps as of its generated_at. So there is no calendar cache to read, and per
    the brief this module must never call FactSet itself to manufacture one.
    `days`/`paths` are accepted for interface symmetry with the other builders,
    so a future calendar-cache writer can be wired in here without an API change.
    """
    paths = paths or DEFAULT_PATHS
    log("upcoming: no calendar cache under state/transcripts/ "
        "(transcript_ingest.py fetches the FactSet calendar live and never "
        "persists it) -- returning []")
    return []
