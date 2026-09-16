"""Today + ETF trades: scripts/portal/reports.py — RIS4 portal builder, Task 3.

Builds two things for the mobile-web portal:

  - `build_reports(out_dir, days)`: one `data/reports/<date>.json` per day that has
    at least one card, drawn from five streams — the Daily Digest sections
    (ws/etfflows/is/podcasts/etfflows-table), the standalone news-digest emails
    (premarket/postmarket), and the two alert ledgers (thesis, stage). Returns
    manifest-ready card summaries for Task 4.
  - `etf_trades(days)`: parses `/root/ws`'s daily ETF-holdings-change report text
    into structured new/exits/added/trimmed rows per ETF, plus an inverted
    `by_ticker` index, and (when given an `out_dir`) writes `data/etf_trades.json`.
  - `upcoming(days)`: always `[]` today — see its docstring for why.

Every zero-arg-default path here reads live data from REPO (see
scripts/portal/__init__.py) via the module-level `DEFAULT_PATHS`. Every public
function accepts an explicit `paths: Paths` override so tests run only against
fixtures under scripts/portal/fixtures/reports/ — see the `Paths` dataclass below.
Read-only: this module never writes into notes/, config/, or state/; its only
writes are `<out_dir>/data/reports/<date>.json` and `<out_dir>/data/etf_trades.json`,
and only when an `out_dir` is actually passed in.

One exception to "everything is overridable": the `thesis_alerts` card joins
state/thesis/alerts_sent.jsonl rows to human text via
`scripts.thesis.thesis_report.alert_events()`, which — like `thesis_io` in
vault.py — hardcodes its own STATE_DIR/NOTES against the live REPO and has no
path-override hook. Tests still stay fixture-safe: alert_events() recomputes
its events from live production state, so a fixture's deliberately-invented id
(e.g. "status:FIXTURE_TICKER:...") can never collide with it, which exercises
exactly the "fall back to id/ticker text" path the brief asks for.

ETF-trades data source note: /root/ws/data/etf_holdings.db's `holdings` table
only stores raw daily snapshots (date, etf_ticker, symbol, weight, shares) — the
same inputs report.py's own compare.py logic diffs to produce the change
report. There is no separate structured "what changed" file (JSON/CSV) per day;
the report text at data/reports/report_{date}.txt is the only per-day record of
that computation, so this module parses it (sanctioned fallback per the brief).
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

sys.path.insert(0, str(REPO / "scripts"))
from thesis import thesis_report  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "topics"))
import theme_notes  # noqa: E402
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
            continue
        text = p.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        if title == "INSIDER ACTIVITY" and len(text.encode("utf-8")) < 300:
            continue  # the "No conviction-level insider activity." stub
        sections.append({"title": title, "text": text})
    return sections


# ---------------------------------------------------------------------------
# thesis_alerts card
# ---------------------------------------------------------------------------
def _thesis_alert_card(day: str, paths: Paths) -> dict | None:
    rows = [r for r in _read_jsonl(paths.thesis_state / "alerts_sent.jsonl")
            if str(r.get("ts", ""))[:10] == day]
    if not rows:
        return None

    day_date = date.fromisoformat(day)
    events_by_id: dict = {}
    try:
        since_ts = datetime.combine(
            day_date - timedelta(days=thesis_report.ALERT_LOOKBACK_DAYS),
            datetime.min.time(), timezone.utc).isoformat()
        events_by_id = {e["id"]: e for e in thesis_report.alert_events(since_ts, day_date)}
    except Exception as exc:  # noqa: BLE001
        log(f"thesis_alerts {day}: alert_events() unavailable ({exc}); "
            f"falling back to id/ticker text for all rows")

    lines = []
    for r in rows:
        ticker = r.get("ticker", "?")
        ev = events_by_id.get(r.get("id"))
        text = ev["text"] if ev else r.get("id", "?")
        lines.append(f"- {ticker}: {text}")
    body = "\n".join(lines)
    return {"id": f"thesis_alerts:{day}", "kind": "thesis_alerts", "date": day,
            "title": f"Thesis alerts — {day}", "text": body,
            "bytes": len(body.encode("utf-8"))}


# ---------------------------------------------------------------------------
# stage_alerts card
# ---------------------------------------------------------------------------
def _stage_alert_render_inputs(paths: Paths):
    """(snap, topic_map_rows, exchanges) or (None, None, None) on any load failure —
    mirrors stage_alert.py's own main(), read-only (never calls run()/save_state(),
    which write state/topics/stages.json)."""
    try:
        snap = json.loads((paths.topics_state / "diffusion.json").read_text(encoding="utf-8"))
        claims_path = paths.evidence_state / "claims.jsonl"
        tm_rows, ex, _ = theme_notes.load_sources(
            topic_map=paths.topics_state / "topic_map.jsonl",
            exchanges=paths.transcripts_state / "exchanges.jsonl",
            claims=claims_path,
        )
        return snap, tm_rows, ex
    except Exception as exc:  # noqa: BLE001
        log(f"stage_alerts: render inputs unavailable ({exc}); "
            f"degrading to 'kind · theme · ticker' text")
        return None, None, None


def _stage_alert_card(day: str, paths: Paths) -> dict | None:
    rows = [r for r in _read_jsonl(paths.topics_state / "alerts_sent.jsonl")
            if r.get("as_of") == day]
    if not rows:
        return None

    snap, tm_rows, ex = _stage_alert_render_inputs(paths)
    lines = []
    for r in rows:
        kind, theme, ticker = r.get("kind", "?"), r.get("theme", "?"), r.get("ticker")
        text = None
        if snap is not None:
            try:
                e = {"kind": kind, "theme": theme, "ticker": ticker}
                text = stage_alert.render(e, snap, tm_rows, ex, day)
            except Exception as exc:  # noqa: BLE001
                log(f"stage_alerts {day}: render() failed for {kind}/{theme}/{ticker} "
                    f"({exc}); degrading this row")
        if text is None:
            text = f"{kind} · {theme}" + (f" · {ticker}" if ticker else "")
        lines.append(f"- {text}")
    body = "\n".join(lines)
    return {"id": f"stage_alerts:{day}", "kind": "stage_alerts", "date": day,
            "title": f"Stage alerts — {day}", "text": body,
            "bytes": len(body.encode("utf-8"))}


# ---------------------------------------------------------------------------
# day_cards
# ---------------------------------------------------------------------------
def day_cards(day: str, paths: Paths = None) -> list[dict]:
    """All cards for one ISO date: premarket/postmarket news-digest emails, the
    5-section Daily Digest, thesis alerts, and stage alerts. Any stream that has
    no content for `day` is silently omitted — never an error.
    """
    paths = paths or DEFAULT_PATHS
    cards = []

    files = news_digest_files(day, paths)
    for mode in ("premarket", "postmarket"):
        p = files.get(mode)
        if p is None:
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

    ta = _thesis_alert_card(day, paths)
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

    summaries = []
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        cards = day_cards(d, paths)
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


# ---------------------------------------------------------------------------
# etf_trades
# ---------------------------------------------------------------------------
_ETF_HEADER_RE = re.compile(r"^(?P<name>.+) \((?P<etf>[A-Z0-9]+)\)$")
_DASH_LINE_RE = re.compile(r"^-{5,}$")
_TABLE_DIVIDER_RE = re.compile(r"^-{5,}(\s+-{5,})+$")
_SECTION_RE = re.compile(
    r"^\s*(BOUGHT — NEW POSITIONS|SOLD — FULL EXIT|ADDED|TRIMMED) \(\d+\):\s*$")
_SECTION_KIND = {
    "BOUGHT — NEW POSITIONS": "new", "SOLD — FULL EXIT": "exits",
    "ADDED": "added", "TRIMMED": "trimmed",
}
_BOUGHT_ROW_RE = re.compile(
    r"^\s*\+\s+(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}(?P<weight>[\d.]+)%\s+"
    r"\((?P<shares>[\d,]+) shares\)\s*$")
_SOLD_ROW_RE = re.compile(
    r"^\s*-\s+(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}\(was (?P<weight>[\d.]+)%, "
    r"(?P<shares>[\d,]+) shares\)\s*$")
_TABLE_ROW_RE = re.compile(
    r"^\s*(?P<sym>\S+)\s+(?P<name>.+?)\s{2,}(?P<delta>[+-][\d.]+)pp\s+"
    r"(?P<frm>[\d.]+)% → (?P<to>[\d.]+)%\s*$")


def _is_etf_header(lines: list[str], i: int) -> re.Match | None:
    """An ETF block header is a "Name (TICKER)" line immediately followed by a
    dashed divider -- this two-line requirement is what keeps the parser from
    tripping on the report's other ALL-CAPS banner lines (data-quality alert,
    section titles), none of which are followed by a bare dash line."""
    if i + 1 >= len(lines):
        return None
    m = _ETF_HEADER_RE.match(lines[i].strip())
    if m and _DASH_LINE_RE.match(lines[i + 1].strip()):
        return m
    return None


def _parse_ws_report(text: str) -> list[dict]:
    """Parses the ws ETF-holdings daily-summary text into
    [{etf, name, new:[{sym,name,weight,shares}], exits:[{sym,name,weight,shares}],
      added:[{sym,name,delta_pp,from_weight,to_weight}],
      trimmed:[{sym,name,delta_pp,from_weight,to_weight}]}].

    added/trimmed use delta_pp/from_weight/to_weight rather than weight/shares --
    a deliberate deviation from the brief's abbreviated {sym,name,weight,shares}
    gloss (written for the `new` list specifically). The ADDED/TRIMMED table in
    the source report never carries a share count, only an active-weight delta
    and before/after weight, so there is nothing to put in a `shares` field for
    those two lists.
    """
    lines = text.splitlines()
    etfs: list[dict] = []
    i, n = 0, len(lines)
    while i < n:
        m = _is_etf_header(lines, i)
        if not m:
            i += 1
            continue
        rec = {"etf": m.group("etf"), "name": m.group("name").strip(),
               "new": [], "exits": [], "added": [], "trimmed": []}
        i += 2  # past the header + its dash divider
        section = None
        while i < n and not _is_etf_header(lines, i):
            line = lines[i]
            stripped = line.strip()
            sm = _SECTION_RE.match(line)
            if sm:
                section = _SECTION_KIND[sm.group(1)]
                i += 1
                continue
            if stripped.startswith("Symbol") or _TABLE_DIVIDER_RE.match(stripped):
                i += 1
                continue
            if section == "new":
                rm = _BOUGHT_ROW_RE.match(line)
                if rm:
                    rec["new"].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                        "weight": float(rm["weight"]),
                                        "shares": int(rm["shares"].replace(",", ""))})
            elif section == "exits":
                rm = _SOLD_ROW_RE.match(line)
                if rm:
                    rec["exits"].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                          "weight": float(rm["weight"]),
                                          "shares": int(rm["shares"].replace(",", ""))})
            elif section in ("added", "trimmed"):
                rm = _TABLE_ROW_RE.match(line)
                if rm:
                    rec[section].append({"sym": rm["sym"], "name": rm["name"].strip(),
                                          "delta_pp": float(rm["delta"]),
                                          "from_weight": float(rm["frm"]),
                                          "to_weight": float(rm["to"])})
            i += 1
        etfs.append(rec)
    return etfs


_ACTION_KEYS = ("new", "exits", "added", "trimmed")
_ACTION_LABEL = {"new": "new", "exits": "exit", "added": "added", "trimmed": "trimmed"}


def etf_trades(days: int = 14, out_dir: Path = None, paths: Paths = None,
               today: date = None) -> dict:
    """{as_of, days: [{date, etfs:[...]}, ...], by_ticker: {SYM: [{date, etf, action}]}}
    over the trailing `days` days (including today), parsed from
    /root/ws/data/reports/report_{date}.txt. Writes <out_dir>/data/etf_trades.json
    when `out_dir` is given; always returns the dict either way. Days with no
    report file (real gaps exist, e.g. weekends/holidays) are skipped with a log
    line, never an error.
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    days_out = []
    by_ticker: dict[str, list] = {}

    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        p = paths.ws_reports / f"report_{d}.txt"
        if not p.exists():
            log(f"etf_trades: no ws report for {d}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        etfs = _parse_ws_report(text)
        if not etfs:
            # A non-empty report file that yielded zero ETF blocks means the header
            # regex didn't match something in this run (e.g. a ticker with a dot/dash
            # the [A-Z0-9]+ pattern doesn't cover) -- silent-empty is exactly the
            # failure mode a nightly build can't otherwise see, so this is a WARN,
            # not a routine "no report today" skip.
            log(f"etf_trades: WARNING — {p} parsed to 0 ETF blocks "
                f"({len(text)} chars); header regex may be missing a symbol shape")
            continue
        days_out.append({"date": d, "etfs": etfs})
        for rec in etfs:
            for action_key in _ACTION_KEYS:
                for item in rec[action_key]:
                    by_ticker.setdefault(item["sym"], []).append(
                        {"date": d, "etf": rec["etf"], "action": _ACTION_LABEL[action_key]})

    result = {"as_of": today.isoformat(), "days": days_out, "by_ticker": by_ticker}
    if out_dir is not None:
        out_dir = Path(out_dir)
        (out_dir / "data").mkdir(parents=True, exist_ok=True)
        (out_dir / "data" / "etf_trades.json").write_text(
            json.dumps(result, indent=1), encoding="utf-8")
    return result
