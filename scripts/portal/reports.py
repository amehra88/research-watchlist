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


def _thesis_alert_card(day: str, paths: Paths, events_cache: dict = None) -> dict | None:
    """events_cache is an optional {id: event} map from _thesis_events_for_window()
    (build_reports() passes one, computed once for the whole window). None (the
    day_cards()-standalone default) means compute it fresh for just this one day,
    same as before -- day_cards() stays usable on its own.
    """
    rows = [r for r in _read_jsonl(paths.thesis_state / "alerts_sent.jsonl")
            if str(r.get("ts", ""))[:10] == day]
    if not rows:
        return None

    if events_cache is not None:
        events_by_id = events_cache
    else:
        day_date = date.fromisoformat(day)
        events_by_id = {}
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
def day_cards(day: str, paths: Paths = None, thesis_events_cache: dict = None) -> list[dict]:
    """All cards for one ISO date: premarket/postmarket news-digest emails, the
    5-section Daily Digest, thesis alerts, and stage alerts. Any stream that has
    no content for `day` logs one line and is omitted — never an error.

    `thesis_events_cache` is passed straight through to _thesis_alert_card(); see
    _thesis_events_for_window() — build_reports() supplies one so alert_events()
    runs once per build, not once per qualifying day. None (the default) means
    day_cards() computes it on demand for just this one day, so it stays usable
    standalone.
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

    ta = _thesis_alert_card(day, paths, events_cache=thesis_events_cache)
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

    summaries = []
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        cards = day_cards(d, paths, thesis_events_cache=events_cache)
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
