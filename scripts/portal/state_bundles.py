"""State bundles + manifest: scripts/portal/state_bundles.py (RIS4 slice 2, Task 4).

Fourth module of the RIS4 portal builder. Reuses the public interfaces landed by
Tasks 1-3 (see their own docstrings, not re-read here): vault.py's discover/
load_note/resolve_wikilinks/signal_reads/ticker_bundle/ingest_bundles, identity.py's
load_universe/display_names/factset_ids, reports.py's build_reports/upcoming, and
the sibling modules scripts/portal/news_sec.py and scripts/portal/theme_ideas.py
(both split out of this module -- see their own docstrings for why; theme_ideas.py
was split in fix round 1, after review, and its docstring explains the resulting
two-way import between it and this module).

Seven public builders. Each returns a plain dict; build_state(out_dir, ctx) is the
only thing that writes them, per the Task 4 brief:
  - theme_ideas.themes_bundle()   -> data/themes.json
  - theme_ideas.ideas_bundle()    -> data/ideas.json
  - scores_bundle(ticker_bundles) -> data/scores.json
  - market_bundle()               -> data/market.json
  - news_sec.news_bundle(days)    -> data/news/<ISO-week>.json shards + news_index.json
  - news_sec.sec_bundle(days)     -> data/sec_30d.json
  - manifest(ctx)                 -> data/manifest.json (written LAST -- it hashes
                                      every file already under ctx.out_dir)

Every zero-arg-default path reads live data from REPO via the module-level
DEFAULT_PATHS (see the `Paths` dataclass below); every public function accepts an
explicit `paths: Paths` override so tests run only against fixtures under
scripts/portal/fixtures/state/. Read-only: this module never writes into notes/,
config/, or state/ -- build_state()'s only writes are under `<out_dir>/data/`.

Import style: this is the first portal module to import ANOTHER portal module
(vault, identity, reports, news_sec, theme_ideas) as a sibling rather than only
`from portal import REPO`. Both the package-relative style (`from portal import
state_bundles`) and the bare-module test-harness convention (`sys.path.insert(0,
dirname(__file__)); import state_bundles`) must resolve those sibling imports, so
this module inserts its OWN directory (scripts/portal/) onto sys.path in addition
to the usual scripts/-parent insert -- see the bootstrap below.

The §6.2 "gap" (theme_ideas.ideas_bundle()'s `gap:` stream): scripts/topics/
theme_notes.py:165 (render_section()) literally renders `f"**Gap (§6.2):**
{n_disclosing} disclosing / {n_companies} asked."` off the metrics-cell fields
diffusion.py:150-154 (metrics()) computes. A gap idea is a (theme, cal_quarter)
metrics cell where MORE companies disclosed than were ever asked
(`n_disclosing > n_companies`) -- a plain inequality, not an invented threshold
like `>= 3`. This is distinct from the `stage:` stream, which is diffusion.py's
OWN "evidence without question" concept (lifecycle.py:142, `stage()`: `if not
asked: return 1  # nobody has asked anywhere`) already persisted, once, in
detections.jsonl -- consuming stage1 again here for `gap:` would make two of the
six streams the same rows under different prefixes.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent             # scripts/portal
_here_parent = str(_here.parent)                     # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

_here_str = str(_here)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import identity        # noqa: E402
import news_sec         # noqa: E402
import reports as rp    # noqa: E402
import vault             # noqa: E402

sys.path.insert(0, str(REPO / "scripts"))
from thesis import thesis_report  # noqa: E402


def log(msg: str) -> None:
    print(f"[state_bundles] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Paths: every filesystem location this module touches, overridable for tests
# ---------------------------------------------------------------------------
@dataclass
class Paths:
    repo: Path = REPO
    notes: Path = None
    watchlist: Path = None
    topics_state: Path = None
    thesis_state: Path = None
    portal_state: Path = None
    docs: Path = None
    cron_log: Path = None
    etf_lookthrough: Path = None
    etf_flows: Path = None

    def __post_init__(self):
        self.notes = self.notes if self.notes is not None else (self.repo / "notes")
        self.watchlist = self.watchlist if self.watchlist is not None else (self.repo / "config" / "watchlist.yaml")
        self.topics_state = self.topics_state if self.topics_state is not None else (self.repo / "state" / "topics")
        self.thesis_state = self.thesis_state if self.thesis_state is not None else (self.repo / "state" / "thesis")
        self.portal_state = self.portal_state if self.portal_state is not None else (self.repo / "state" / "portal")
        self.docs = self.docs if self.docs is not None else (self.repo / "docs")
        self.cron_log = self.cron_log if self.cron_log is not None else Path("/root/logs/cron_runs.log")
        self.etf_lookthrough = (self.etf_lookthrough if self.etf_lookthrough is not None
                                 else (self.repo / "state" / "etf_lookthrough.json"))
        self.etf_flows = self.etf_flows if self.etf_flows is not None else (self.repo / "state" / "etf_flows.jsonl")


DEFAULT_PATHS = Paths()


@dataclass
class Ctx:
    """The contract build_portal.py (Task 6) constructs and passes to build_state()
    / manifest(). Every field is optional; build_state() fills in today/out_dir/
    ticker_bundles/universe itself when the caller leaves them unset, so `Ctx()` and
    `None` both work everywhere a ctx is accepted. Field names match Task 6's
    planned CLI flags 1:1 (--news-days/--sec-days/--reports-days) so an
    argparse.Namespace with those attributes is also a valid ctx (duck-typed via
    getattr, not isinstance).

    report_summaries: reports.build_reports()'s own return value, if the caller
        already has it (Task 6 calls build_reports() itself for the full history --
        passing its result here means manifest()'s own `today` slice doesn't re-run
        it). None -> manifest() calls build_reports(out_dir, days=1) itself, which
        is fixture-UNSAFE (reports.DEFAULT_PATHS, live REPO) unless ctx.out_dir is
        also None -- tests that set out_dir must always also set report_summaries
        (even to []) to stay fixture-isolated; this mirrors reports.py's own single
        documented live-only fallback (thesis_alerts -> alert_events()).
    ticker_bundles / universe / refs: pre-built vault.ticker_bundle() results
        (ALL universe tickers) + identity.load_universe() + vault.discover(),
        if the caller already built them this run (build_state() does). None ->
        manifest() builds its own via _load_context.
    themes / ideas: pre-built themes_bundle()/ideas_bundle() results, if the
        caller already built them this run (build_state() does, and passes its
        own `refs` into themes_bundle() too -- vault.discover() measured ~8.5s
        live, the single biggest avoidable cost of calling it more than once
        per build). None -> manifest() computes its own.
    out_dir: set by build_state() before calling manifest(ctx) LAST, so `files`
        can hash every file already written under it.
    report_paths: an optional reports.Paths instance (a DIFFERENT dataclass
        from this module's own Paths -- reports.py's own ws_reports/is_reports/
        etc.), threaded into reports.upcoming(). None -> reports.upcoming() uses
        its own reports.DEFAULT_PATHS (unchanged default behavior); this field
        just makes that plumbing explicit rather than an unconditional
        no-paths call, so a future caller/test can override it without an
        API change.
    """
    today: date = None
    news_days: int = 30
    sec_days: int = 30
    reports_days: int = 14
    report_summaries: list = None
    ticker_bundles: dict = None
    universe: list = None
    refs: list = None
    themes: dict = None
    ideas: dict = None
    out_dir: Path = None
    paths: Paths = None
    report_paths: object = None


# ---------------------------------------------------------------------------
# small IO helpers
# ---------------------------------------------------------------------------
def _read_json(path: Path, default):
    path = Path(path)
    if not path.exists():
        log(f"{path} missing -- using default")
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log(f"{path} unreadable ({exc}) -- using default")
        return default


def _read_jsonl(path: Path) -> list:
    path = Path(path)
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


def _write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha(repo: Path) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=5, check=True)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _known_sets(refs: list) -> tuple[set, set]:
    """Mirror of vault.py's own private `_known_sets` (leading underscore -- not
    exported, so duplicated here rather than importing a private name across
    modules, same convention etf_trades.py already established)."""
    tickers = {r.ticker for r in refs if r.ticker}
    themes = {Path(r.rel).stem for r in refs if r.kind == "theme"}
    return tickers, themes


def _load_context(paths: Paths) -> dict:
    """One shared pass: discover refs, load the universe + display names, and
    build a vault.ticker_bundle() for every universe ticker with meta=entry (so
    tier/themes/scores come from the fixture-controlled watchlist, never
    thesis_io's live-REPO default -- see vault.ticker_bundle's own docstring).
    Used both by build_state() (once, shared with manifest()) and by manifest()
    itself when called standalone with no ctx.ticker_bundles.
    """
    refs = vault.discover(paths.notes)
    universe = identity.load_universe(paths.watchlist, paths.notes)
    names = identity.display_names(paths.watchlist, notes_dir=paths.notes)
    known_tickers, known_themes = _known_sets(refs)
    bundles = {e["ticker"]: vault.ticker_bundle(e["ticker"], refs, names, known_tickers, known_themes, meta=e)
               for e in universe}
    return {"refs": refs, "universe": universe, "names": names, "bundles": bundles}


# themes_bundle/ideas_bundle moved to scripts/portal/theme_ideas.py in fix round 1
# (controller-authorized split, review 768e415d..4f613b35) -- imported here after
# Paths/DEFAULT_PATHS/_known_sets/_read_json/_read_jsonl are all defined, which is
# what makes the two-way import between this module and theme_ideas.py safe (see
# theme_ideas.py's own module docstring for the exact reasoning).
import theme_ideas  # noqa: E402


# ---------------------------------------------------------------------------
# scores_bundle
# ---------------------------------------------------------------------------
def _score_str(v) -> str | None:
    """watchlist.yaml carries two schema variants for ai_positioning/
    potential_investor_interest -- a bare scalar ('5', '4+') on some entries
    (AMZN/BE/GOOG/NVDA/MSFT, live-verified) and {score, notes} on the rest.
    competitive_advantage's three sub-fields are always bare scalars directly.
    Mirrors thesis_io._score_str's own "if isinstance(v, dict): v = v.get('score')"
    handling rather than assuming one shape.
    """
    if isinstance(v, dict):
        v = v.get("score")
    return None if v is None else str(v)


def scores_bundle(ticker_bundles: dict, as_of: str = None) -> dict:
    """data/scores.json, scoped to tiers 1-2 plus any ticker carrying a thesis
    (a bundle whose thesis.fm_without_body is non-empty). `ticker_bundles` is
    {ticker: vault.ticker_bundle(...)}; callers build it with
    meta=<identity.load_universe() entry> so "scores" carries the RAW nested
    watchlist shape (ai_positioning: {score,notes}, competitive_advantage:
    {innovation_rate,distribution,overall,notes}, potential_investor_interest:
    {score,notes} -- see config/watchlist.yaml) rather than thesis_io's flat
    dotted-key mirror. `current` always carries all three keys, `None` rather
    than omitted when the watchlist entry lacks a block.
    """
    as_of = as_of or date.today().isoformat()
    theses = {tk: b["thesis"]["fm_without_body"] for tk, b in ticker_bundles.items()
              if b.get("thesis", {}).get("fm_without_body")}
    proposals_by_ticker: dict[str, list] = {}
    try:
        for p in thesis_report.pending_proposals(theses):
            proposals_by_ticker.setdefault(p["ticker"], []).append(p)
    except Exception as exc:  # noqa: BLE001
        log(f"scores_bundle: pending_proposals() failed ({exc}); degrading to no proposals")

    out = {}
    for tk, b in ticker_bundles.items():
        has_thesis = tk in theses
        if b.get("tier") not in ("tier_1_bctk", "tier_2_active_candidates") and not has_thesis:
            continue
        raw = b.get("scores") or {}
        ca = raw.get("competitive_advantage") or {}
        if not isinstance(ca, dict):
            ca = {}
        current = {
            "ai_positioning": _score_str(raw.get("ai_positioning")),
            "competitive_advantage": {
                "innovation_rate": _score_str(ca.get("innovation_rate")),
                "distribution": _score_str(ca.get("distribution")), "overall": _score_str(ca.get("overall")),
            },
            "investor_interest": _score_str(raw.get("potential_investor_interest")),
        }
        fm = theses.get(tk, {})
        reads = []
        for note in b.get("notes") or []:                      # already newest-first (vault.ticker_bundle)
            if note.get("kind") not in ("earnings", "conference"):
                continue
            sig = vault.signal_reads(note)
            if sig is None:
                continue
            reads.append({"quarter": note.get("period"), "date": note.get("date"),
                          "note_id": note.get("id"), **sig})
        out[tk] = {"current": current, "proposed": fm.get("proposed_scores") or {},
                  "pending_proposals": proposals_by_ticker.get(tk, []), "reads": reads}
    return {"as_of": as_of, "tickers": out}


# ---------------------------------------------------------------------------
# market_bundle
# ---------------------------------------------------------------------------
def _latest_dated(dir_: Path, prefix: str, suffix: str) -> Path | None:
    """Glob-for-latest: the file whose FILENAME date (never mtime) is largest
    among `<prefix>_<YYYY-MM-DD>.<suffix>`. ranking_/insiders_/consensus_ land
    on different dates from each other in production, so each prefix is globbed
    and maxed independently -- never one shared "latest date" across all three.
    """
    dir_ = Path(dir_)
    best, best_date = None, ""
    if not dir_.is_dir():
        return None
    pat = re.compile(rf"^{re.escape(prefix)}_(\d{{4}}-\d{{2}}-\d{{2}})\.{re.escape(suffix)}$")
    for p in dir_.glob(f"{prefix}_*.{suffix}"):
        m = pat.match(p.name)
        if m and m.group(1) > best_date:
            best, best_date = p, m.group(1)
    return best


def market_bundle(paths: Paths = None, today: date = None) -> dict:
    """data/market.json: the latest ranking_*.json + insiders_*.jsonl (`_raw`
    dropped) + consensus_*.jsonl (glob-for-latest, each prefix independently),
    plus state/etf_lookthrough.json and the trailing 14 days of
    state/etf_flows.jsonl. Both ETF files are gitignored and may be absent in
    tests -- degraded to {}/[] with one log line each, never an error.
    etf_flows.jsonl runs ~10MB/63K lines back to 2023, so it's streamed
    line-by-line and filtered rather than json.load()ed whole.
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()

    ranking = {}
    rp_path = _latest_dated(paths.thesis_state, "ranking", "json")
    if rp_path:
        ranking = _read_json(rp_path, default={})
    else:
        log("market_bundle: no ranking_*.json found")

    insiders = []
    ip_path = _latest_dated(paths.thesis_state, "insiders", "jsonl")
    if ip_path:
        insiders = [{k: v for k, v in r.items() if k != "_raw"} for r in _read_jsonl(ip_path)]
    else:
        log("market_bundle: no insiders_*.jsonl found")

    consensus = []
    cp_path = _latest_dated(paths.thesis_state, "consensus", "jsonl")
    if cp_path:
        consensus = _read_jsonl(cp_path)
    else:
        log("market_bundle: no consensus_*.jsonl found")

    lookthrough = {}
    if paths.etf_lookthrough.exists():
        lookthrough = _read_json(paths.etf_lookthrough, default={})
    else:
        log("market_bundle: state/etf_lookthrough.json absent")

    flows = []
    if paths.etf_flows.exists():
        cutoff = (today - timedelta(days=14)).isoformat()
        with open(paths.etf_flows, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if str(r.get("date", "")) >= cutoff:
                    flows.append(r)
    else:
        log("market_bundle: state/etf_flows.jsonl absent")

    return {"ranking": ranking, "insiders": insiders, "consensus": consensus,
            "etf_lookthrough": lookthrough, "etf_flows_14d": flows}


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------
_CRON_RE = re.compile(r"^(\S+)\s+job=(\S+)\s+exit=(-?\d+)\s+cmd=(.*)$")


def _last_job_failures(cron_log: Path, today: date) -> list[dict]:
    cron_log = Path(cron_log)
    if not cron_log.exists():
        log(f"manifest: {cron_log} unreadable -- last_job_failures=[]")
        return []
    cutoff = today - timedelta(days=7)
    out = []
    try:
        with open(cron_log, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = _CRON_RE.match(line.rstrip("\n"))
                if not m or m.group(3) == "0":
                    continue
                ts = m.group(1)
                try:
                    ts_date = date.fromisoformat(ts[:10])
                except ValueError:
                    continue
                if ts_date < cutoff:
                    continue
                out.append({"ts": ts, "job": m.group(2), "exit": int(m.group(3)), "cmd": m.group(4)})
    except OSError as exc:
        log(f"manifest: {cron_log} unreadable ({exc}) -- last_job_failures=[]")
        return []
    return out


def _applied_ids(portal_state: Path) -> list:
    p = Path(portal_state) / "applied.json"
    if not p.exists():
        log("manifest: state/portal/applied.json absent (portal state not built yet) -- applied_ids=[]")
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log(f"manifest: applied.json unreadable ({exc}) -- applied_ids=[]")
        return []
    return data if isinstance(data, list) else (data.get("ids") or [])


def _search_news_mode(out_dir) -> str:
    """`news_mode` out of an ALREADY-WRITTEN data/search.json, for the Status
    screen -- so the app can name the search index's news window without
    fetching the 3MB index itself. The search-index stage runs before
    build_state() (see build_portal's orchestration order), so the file is on
    disk by the time manifest() runs; anything else (no out_dir, no file yet,
    unreadable, key absent) is None, never an error and never a guess.
    """
    if not out_dir:
        return None
    path = Path(out_dir) / "data" / "search.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("news_mode")
    except (OSError, ValueError):
        return None


def manifest(ctx: Ctx = None) -> dict:
    """data/manifest.json. Reuses ctx.ticker_bundles/ctx.universe when
    build_state() already built them this run; otherwise builds its own full
    pass (_load_context) so it stays independently callable/testable.

    `files` hashes every file already written under ctx.out_dir (Task 3's
    reports/etf_trades output too, not just this module's own) EXCEPT
    manifest.json itself -- build_state() calls this function LAST for exactly
    that reason, and Task 6's CLI must sequence reports.build_reports() /
    etf_trades.etf_trades() BEFORE calling build_state() for `files` to be
    complete. `ctx.out_dir=None` (the default for a standalone unit test)
    leaves today.cards/upcoming/files empty rather than touching the live tree.

    `vendor` degrades to {} -- scripts/portal/app/vendor/ is Task 7-8, doesn't
    exist yet; this never fabricates a hash for it.
    """
    ctx = ctx or Ctx()
    paths = ctx.paths or DEFAULT_PATHS
    today = ctx.today or date.today()

    if ctx.universe is not None and ctx.ticker_bundles is not None:
        universe, bundles, refs = ctx.universe, ctx.ticker_bundles, ctx.refs
    else:
        loaded = _load_context(paths)
        universe, bundles, refs = loaded["universe"], loaded["bundles"], loaded["refs"]

    names = identity.display_names(paths.watchlist, notes_dir=paths.notes)
    factset_map = identity.factset_ids([e["ticker"] for e in universe], paths.watchlist, paths.notes)

    theses = {tk: b["thesis"]["fm_without_body"] for tk, b in bundles.items()
              if b.get("thesis", {}).get("fm_without_body")}
    proposals_by_ticker: dict[str, list] = {}
    try:
        for p in thesis_report.pending_proposals(theses):
            proposals_by_ticker.setdefault(p["ticker"], []).append(p)
    except Exception as exc:  # noqa: BLE001
        log(f"manifest: pending_proposals() failed ({exc}); degrading")

    tickers_rows, tickers_without_notes = [], 0
    for e in universe:
        tk = e["ticker"]
        b = bundles.get(tk) or {}
        notes_list = b.get("notes") or []
        has_notes = bool(notes_list) or bool(b.get("thesis", {}).get("fm_without_body")) or bool(b.get("profile"))
        if not e.get("orphan_notes") and not has_notes:
            tickers_without_notes += 1
        fm = theses.get(tk, {})
        status_counts = dict(Counter(a.get("status") for a in (fm.get("assumptions") or [])))
        tickers_rows.append({
            "ticker": tk, "name": names.get(tk, tk), "tier": e.get("tier", "none"),
            "also_in": e.get("also_in") or [], "themes": e.get("themes") or [], "scores": e.get("scores") or {},
            "factset_id": factset_map.get(tk), "has_notes": has_notes, "n_notes": len(notes_list),
            "last_note": notes_list[0].get("date") if notes_list else None,
            "thesis_status_counts": status_counts, "pending_proposals": proposals_by_ticker.get(tk, []),
            "orphan_notes": bool(e.get("orphan_notes")),
        })

    tb = ctx.themes if ctx.themes is not None else theme_ideas.themes_bundle(paths, refs=refs)
    themes_rows = [{"slug": t["slug"], "stage": t["fm"].get("stage"), "status": t["fm"].get("status"),
                    "n_tickers": len(t["fm"].get("tickers") or []), "updated": t["fm"].get("updated")}
                   for t in tb["themes"]]
    themes_without_labels = sorted(t["slug"] for t in tb["themes"] if not t["in_vocab"])
    ib = ctx.ideas if ctx.ideas is not None else theme_ideas.ideas_bundle(paths)

    out_dir = ctx.out_dir
    if out_dir is not None:
        report_summaries = ctx.report_summaries
        if report_summaries is None:
            log("manifest: ctx.report_summaries unset -- calling reports.build_reports(days=1) "
                "with its own live-REPO default paths (fixture-unsafe; tests must pass "
                "report_summaries explicitly)")
            report_summaries = rp.build_reports(out_dir, days=1, today=today)
        today_iso = today.isoformat()
        today_cards = [s for s in report_summaries if s.get("date") == today_iso]
        upcoming = rp.upcoming(ctx.reports_days, paths=ctx.report_paths)
    else:
        log("manifest: ctx.out_dir unset -- today.cards/upcoming/files left empty")
        today_cards, upcoming = [], []

    try:
        stale_n = len(thesis_report.stale_assumptions(theses, today))
    except Exception as exc:  # noqa: BLE001
        log(f"manifest: stale_assumptions() failed ({exc}); degrading to 0")
        stale_n = 0

    files = {}
    if out_dir is not None and Path(out_dir).is_dir():
        for p in sorted(Path(out_dir).rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(out_dir).as_posix()
            if rel == "data/manifest.json":
                continue
            files[rel] = {"bytes": p.stat().st_size, "sha256": _sha256_file(p)}

    log("manifest: vendor manifest not built yet (scripts/portal/app/vendor/ is Task 7-8) -- vendor={}")

    return {
        "built_at": datetime.now(timezone.utc).isoformat(), "git_sha": _git_sha(paths.repo), "format": "json",
        "counts": {"tickers": len(tickers_rows), "themes": len(themes_rows),
                  "candidates_pending": len(tb["candidates"]), "ideas": len(ib["ideas"]),
                  "search_news_mode": _search_news_mode(ctx.out_dir)},
        "tickers": tickers_rows, "themes": themes_rows, "candidates_pending": len(tb["candidates"]),
        "today": {"cards": today_cards}, "upcoming": upcoming,
        "health": {"stale_assumptions": stale_n, "tickers_without_notes": tickers_without_notes,
                  "themes_without_labels": themes_without_labels, "last_job_failures": _last_job_failures(paths.cron_log, today)},
        "applied_ids": _applied_ids(paths.portal_state), "files": files, "vendor": {},
    }


# ---------------------------------------------------------------------------
# build_state: the single entry point Task 6's CLI calls
# ---------------------------------------------------------------------------
def build_state(out_dir: Path, ctx: Ctx = None) -> dict:
    """Writes every bundle under `<out_dir>/data/` and returns a small stats
    dict for the caller's own logging (this module prints no budget table --
    that's Task 6's budget.py). Order: themes -> ideas -> scores -> market ->
    news (shards + index) -> sec -> manifest LAST (see manifest()'s own
    docstring for why). Builds ticker_bundles + refs ONCE via _load_context and
    shares them (via ctx) with scores_bundle()/manifest() -- and caches its own
    themes_bundle()/ideas_bundle() results onto ctx too, so manifest() doesn't
    recompute either (vault.discover() alone measured ~8.5s live; without this
    sharing a full build called it 3x).
    """
    ctx = ctx or Ctx()
    paths = ctx.paths or DEFAULT_PATHS
    today = ctx.today or date.today()
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    loaded = _load_context(paths)
    ctx.universe, ctx.ticker_bundles, ctx.refs = loaded["universe"], loaded["bundles"], loaded["refs"]
    ctx.out_dir, ctx.today = out_dir, today

    tb_json = theme_ideas.themes_bundle(paths, refs=ctx.refs)
    ctx.themes = tb_json
    _write_json(data_dir / "themes.json", tb_json)

    ib_json = theme_ideas.ideas_bundle(paths)
    ctx.ideas = ib_json
    _write_json(data_dir / "ideas.json", ib_json)

    sb_json = scores_bundle(ctx.ticker_bundles)
    _write_json(data_dir / "scores.json", sb_json)

    mb_json = market_bundle(paths, today)
    _write_json(data_dir / "market.json", mb_json)
    # The Insiders tab needs ~12 rows and nothing else in market.json, which
    # runs to ~1MB (etf_flows_14d dominates). Same rows, own file, so a phone
    # does not pay for the rest; market.json is unchanged for every other
    # consumer. `as_of` is this build's date -- the rows themselves carry the
    # transaction dates. Written before manifest(), so `files` hashes it.
    _write_json(data_dir / "insiders.json",
                {"as_of": today.isoformat(), "rows": mb_json["insiders"]})

    news_paths = news_sec.Paths(notes=paths.notes)
    news = news_sec.news_bundle(ctx.news_days, news_paths, today)
    news_dir = data_dir / "news"
    for shard, payload in news["shards"].items():
        _write_json(news_dir / f"{shard}.json", payload)
    _write_json(data_dir / "news_index.json", news["index"])

    sec_json = news_sec.sec_bundle(ctx.sec_days, news_paths, today)
    _write_json(data_dir / "sec_30d.json", sec_json)

    mani = manifest(ctx)
    _write_json(data_dir / "manifest.json", mani)

    return {
        "themes": len(tb_json["themes"]), "candidates_pending": len(tb_json["candidates"]),
        "ideas": len(ib_json["ideas"]), "scores_tickers": len(sb_json["tickers"]),
        "news_shards": len(news["shards"]), "news_rows": sum(len(v["rows"]) for v in news["shards"].values()),
        "sec_rows": len(sec_json["rows"]), "manifest_tickers": len(mani["tickers"]),
    }
