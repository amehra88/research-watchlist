"""State bundles + manifest: scripts/portal/state_bundles.py (RIS4 slice 2, Task 4).

Fourth module of the RIS4 portal builder. Reuses the public interfaces landed by
Tasks 1-3 (see their own docstrings, not re-read here): vault.py's discover/
load_note/resolve_wikilinks/signal_reads/ticker_bundle/ingest_bundles, identity.py's
load_universe/display_names/factset_ids, reports.py's build_reports/upcoming, and
the sibling module scripts/portal/news_sec.py (split out from here from the start --
see its own docstring for why).

Seven public builders. Each returns a plain dict; build_state(out_dir, ctx) is the
only thing that writes them, per the Task 4 brief:
  - themes_bundle()               -> data/themes.json
  - ideas_bundle()                -> data/ideas.json
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
(vault, identity, reports, news_sec) as a sibling rather than only `from portal
import REPO`. Both the package-relative style (`from portal import state_bundles`)
and the bare-module test-harness convention (`sys.path.insert(0, dirname(__file__));
import state_bundles`) must resolve those sibling imports, so this module inserts
its OWN directory (scripts/portal/) onto sys.path in addition to the usual
scripts/-parent insert -- see the bootstrap below.

The §6.2 "gap" (ideas_bundle's `gap:` stream): scripts/topics/theme_notes.py:165
(render_section()) literally renders `f"**Gap (§6.2):** {n_disclosing} disclosing /
{n_companies} asked."` off the metrics-cell fields diffusion.py:150-154 (metrics())
computes. A gap idea is a (theme, cal_quarter) metrics cell where MORE companies
disclosed than were ever asked (`n_disclosing > n_companies`) -- a plain
inequality, not an invented threshold like `>= 3`. This is distinct from the
`stage:` stream, which is diffusion.py's OWN "evidence without question" concept
(lifecycle.py:142, `stage()`: `if not asked: return 1  # nobody has asked
anywhere`) already persisted, once, in detections.jsonl -- consuming stage1 again
here for `gap:` would make two of the six streams the same rows under different
prefixes.
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

sys.path.insert(0, str(REPO / "scripts" / "topics"))
import theme_notes  # noqa: E402


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


def _affects_map(watchlist_path: Path) -> dict:
    try:
        return theme_notes.affects_map(watchlist_path)
    except (OSError, Exception) as exc:  # noqa: BLE001 -- any failure degrades
        log(f"affects_map({watchlist_path}) failed ({exc}); degrading to {{}}")
        return {}


def _theme_state_safe(theme: str, snap: dict, amap: dict) -> dict | None:
    if "pairs" not in snap:
        return None
    try:
        return theme_notes.theme_state(theme, snap, amap)
    except Exception as exc:  # noqa: BLE001
        log(f"theme_state({theme}) failed ({exc}); degrading")
        return None


# ---------------------------------------------------------------------------
# candidates.json <-> decisions.jsonl reconciliation (shared by themes_bundle
# and ideas_bundle)
# ---------------------------------------------------------------------------
def _reconcile_candidates(topics_state: Path) -> tuple[list, list]:
    """(pending, decided) from state/topics/candidates.json. An inline "status"
    key on the candidate entry wins (production candidates.json already carries
    one on every row -- see the task brief's "Facts to save discovery"); when
    absent, the LATEST (max ts) matching row in decisions.jsonl supplies it.
    Anything still unresolved is pending. Pending entries are trimmed to the
    brief's literal field list (ngrams capped at 8); decided entries are
    returned whole (the caller caps at "last 50").
    """
    cands = _read_json(topics_state / "candidates.json", default=[])
    decisions = _read_jsonl(topics_state / "decisions.jsonl")
    latest_decision: dict[str, dict] = {}
    for d in decisions:
        cid = d.get("id")
        if not cid:
            continue
        cur = latest_decision.get(cid)
        if cur is None or str(d.get("ts", "")) >= str(cur.get("ts", "")):
            latest_decision[cid] = d

    pending, decided = [], []
    for c in cands:
        status = c.get("status")
        dec = latest_decision.get(c.get("id"))
        if status is None and dec is not None:
            status = dec.get("status")
            c = {**c, "name": c.get("name") or dec.get("name")}
        if status in ("accepted", "rejected"):
            decided.append({**c, "status": status})
        else:
            pending.append({
                "id": c.get("id"), "label": c.get("label"), "suggested_name": c.get("suggested_name"),
                "ngrams": (c.get("ngrams") or [])[:8], "n_exchanges": c.get("n_exchanges"),
                "n_companies": c.get("n_companies"), "n_banks": c.get("n_banks"),
                "tickers": c.get("tickers") or [], "first_seen": c.get("first_seen"),
            })
    return pending, decided


# ---------------------------------------------------------------------------
# themes_bundle
# ---------------------------------------------------------------------------
_THEME_FM_KEYS = ("theme", "status", "stage", "tickers", "affects", "first_question_date", "lag_days", "updated")


def themes_bundle(paths: Paths = None, refs: list = None) -> dict:
    """data/themes.json.

    `refs` is an optional pre-computed vault.discover() result (build_state()
    and manifest() both already have one via _load_context and pass it through
    -- vault.discover() reads and title-regexes every note under notes/, ~8.5s
    measured live, so recomputing it per caller was the single biggest avoidable
    cost in a full build_state() run). None -> computed fresh, so this stays
    independently callable/testable with just `paths`.

    themes: every written notes/themes/*.md (in_vocab=True; fm trimmed to
    _THEME_FM_KEYS, body wikilink-resolved, stages_by_ticker recomputed live via
    theme_notes.theme_state() off diffusion.json's "pairs" -- notes don't carry
    per-ticker stage in their own frontmatter) UNION every theme in
    state/topics/stages.json's "gated" list (scripts/topics/stage_alert.py's own
    current-quarter §7.1 gate, already computed daily -- not re-derived here)
    that has NO note yet (in_vocab=False, same theme_state() call, body="").

    candidates/decided: state/topics/candidates.json reconciled against
    decisions.jsonl (see _reconcile_candidates).

    diffusion: diffusion.json trimmed to {as_of, current_quarter, metrics
    (current + previous quarter only), movers, stage_counts, lag_summary} per
    the brief's size note (drops "pairs"/"newly_said" -- ideas_bundle carries
    the newly_said rows; nothing here needs raw pairs).

    stage_events: last 60 rows of detections.jsonl (append-only, already
    chronological -- a tail, no re-sort).
    """
    paths = paths or DEFAULT_PATHS
    snap = _read_json(paths.topics_state / "diffusion.json", default={})
    if not snap:
        log("themes_bundle: diffusion.json missing/empty -- diffusion/stages_by_ticker will be empty")

    refs = refs if refs is not None else vault.discover(paths.notes)
    known_tickers, known_themes = _known_sets(refs)
    amap = _affects_map(paths.watchlist)

    theme_refs = {Path(r.rel).stem: r for r in refs if r.kind == "theme"}
    themes = []
    for slug, ref in sorted(theme_refs.items()):
        note = vault.load_note(ref)
        st = _theme_state_safe(slug, snap, amap) or {}
        themes.append({
            "slug": slug, "fm": {k: note["fm"].get(k) for k in _THEME_FM_KEYS},
            "stages_by_ticker": st.get("stages_by_ticker", {}),
            "body": vault.resolve_wikilinks(note["body"], known_tickers, known_themes),
            "in_vocab": True,
        })

    stages = _read_json(paths.topics_state / "stages.json", default={})
    for slug in stages.get("gated") or []:
        if slug in theme_refs:
            continue
        st = _theme_state_safe(slug, snap, amap)
        if st is None:
            log(f"themes_bundle: gated theme {slug!r} has no note and theme_state() degraded -- skipping")
            continue
        fm = {k: st.get(k) for k in _THEME_FM_KEYS}
        fm["updated"] = snap.get("as_of")
        themes.append({"slug": slug, "fm": fm, "stages_by_ticker": st.get("stages_by_ticker", {}),
                       "body": "", "in_vocab": False})
    themes.sort(key=lambda t: t["slug"])

    pending, decided = _reconcile_candidates(paths.topics_state)

    cq = snap.get("current_quarter")
    quarters = snap.get("quarters") or []
    prev_q = quarters[-2] if len(quarters) > 1 and quarters[-1] == cq else None
    keep_qs = {q for q in (cq, prev_q) if q}
    trimmed_metrics = [m for m in (snap.get("metrics") or []) if m.get("cal_quarter") in keep_qs]

    return {
        "themes": themes, "candidates": pending, "decided": decided[-50:],
        "diffusion": {
            "as_of": snap.get("as_of"), "current_quarter": cq, "metrics": trimmed_metrics,
            "movers": snap.get("movers") or [], "stage_counts": snap.get("stage_counts") or {},
            "lag_summary": snap.get("lag_summary") or {},
        },
        "stage_events": _read_jsonl(paths.topics_state / "detections.jsonl")[-60:],
    }


# ---------------------------------------------------------------------------
# ideas_bundle
# ---------------------------------------------------------------------------
_SCREEN_REPORT_RE = re.compile(r"^ai-screen-report-(\d{8})\.md$")
_SCREEN_ROW_RE = re.compile(r"^\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")


def _latest_screen_report(docs_dir: Path) -> Path | None:
    best, best_date = None, ""
    if not Path(docs_dir).is_dir():
        return None
    for p in Path(docs_dir).glob("ai-screen-report-*.md"):
        m = _SCREEN_REPORT_RE.match(p.name)
        if m and m.group(1) > best_date:
            best, best_date = p, m.group(1)
    return best


def _latest_screen_rows(docs_dir: Path) -> list[dict]:
    """[{ticker, n, screens, tracked, report_date}] from the newest
    docs/ai-screen-report-*.md's "## Cross-signal" GFM table (brief: `| # |
    Ticker | Name | Screens cleared | |`, tracked rows end `*tracked*`).
    """
    p = _latest_screen_report(docs_dir)
    if p is None:
        log("ideas_bundle: no docs/ai-screen-report-*.md found -- screen: stream empty")
        return []
    date_s = _SCREEN_REPORT_RE.match(p.name).group(1)
    report_date = f"{date_s[:4]}-{date_s[4:6]}-{date_s[6:]}"
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## Cross-signal.*$", text, re.M)
    if not m:
        log(f"ideas_bundle: {p.name} has no Cross-signal section -- screen: stream empty")
        return []
    body = text[m.end():]
    nxt = re.search(r"\n## ", body)
    body = body[:nxt.start()] if nxt else body

    rows = []
    for line in body.splitlines():
        rm = _SCREEN_ROW_RE.match(line)
        if not rm:
            continue
        n_s, ticker, _name, screens, tail = rm.groups()
        if not n_s.isdigit():
            continue   # header ("#") or the |---|---| divider row
        rows.append({"ticker": ticker, "n": int(n_s), "screens": screens,
                     "tracked": "*tracked*" in tail, "report_date": report_date})
    return rows


def _novel_names(topics_state: Path) -> list[dict]:
    p = Path(topics_state) / "novel_names.json"
    if not p.exists():
        log("ideas_bundle: state/topics/novel_names.json absent -- novel: stream empty")
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log(f"ideas_bundle: novel_names.json unreadable ({exc}) -- novel: stream empty")
        return []
    return data if isinstance(data, list) else (data.get("names") or [])


def _dismissed_ideas(portal_state: Path) -> set:
    p = Path(portal_state) / "ideas_decisions.jsonl"
    if not p.exists():
        return set()
    return {r["id"] for r in _read_jsonl(p) if r.get("id")}


def ideas_bundle(paths: Paths = None) -> dict:
    """data/ideas.json = {as_of, ideas:[...]}. Six streams, in this priority
    order (each internally sorted by score desc): candidate, newly_said, gap,
    stage, screen, novel. See the module docstring for the exact §6.2 gap
    citation and the stage1-vs-gap distinction.

    Ids are stable across runs by construction: candidate/gap ids come straight
    from source-file keys (candidates.json's own id / metrics' theme+quarter);
    stage ids are synthesized ONLY from append-only detections.jsonl fields
    (theme|ticker|detected_on) -- never from a recomputed field like
    open_lag_days, which changes every day and would silently un-dismiss a
    detection the operator already dismissed.

    Dismissals: any id present in state/portal/ideas_decisions.jsonl
    ({id, status}) is dropped, regardless of its status value -- the ledger
    doesn't exist in production yet; absence is not an error.
    """
    paths = paths or DEFAULT_PATHS
    snap = _read_json(paths.topics_state / "diffusion.json", default={})
    as_of = snap.get("as_of")
    cq = snap.get("current_quarter")
    pending, _decided = _reconcile_candidates(paths.topics_state)
    universe = identity.load_universe(paths.watchlist, paths.notes)
    tier_of = {e["ticker"]: e["tier"] for e in universe}
    t1_t2 = ("tier_1_bctk", "tier_2_active_candidates")

    ideas = []

    # 1. candidate:<id>
    for c in pending:
        ideas.append({
            "id": f"candidate:{c['id']}", "stream": "candidate",
            "title": c.get("suggested_name") or c.get("label") or c["id"],
            "detail": (f"{c.get('n_exchanges', 0)} exchanges / {c.get('n_companies', 0)} companies / "
                       f"{c.get('n_banks', 0)} banks"),
            "tickers": c.get("tickers") or [], "theme": None,
            "score": c.get("n_banks") or 0, "first_seen": c.get("first_seen"), "links": {},
        })

    # 2. newly_said:<theme>|<ticker>|<quarter> -- current quarter only; score =
    # n_banks via a join to the (theme, cal_quarter) metrics cell (newly_said
    # rows don't carry n_banks themselves).
    metrics_idx = {(m["theme"], m["cal_quarter"]): m for m in (snap.get("metrics") or [])}
    for row in snap.get("newly_said") or []:
        if row.get("cal_quarter") != cq:
            continue
        theme, ticker = row["theme"], row["ticker"]
        n_banks = metrics_idx.get((theme, cq), {}).get("n_banks", 0)
        ideas.append({
            "id": f"newly_said:{theme}|{ticker}|{cq}", "stream": "newly_said",
            "title": f"{ticker} newly said {theme}",
            "detail": (f"{row.get('source')}/{row.get('register')}, {row.get('n_rows', 0)} row(s) this "
                       f"quarter; absent {row.get('baseline_quarters') or []}"),
            "tickers": [ticker], "theme": theme, "score": n_banks, "first_seen": as_of,
            "links": {"ticker": ticker, "theme": theme},
        })

    # 3. gap:<theme>|<quarter> -- §6.2 (see module docstring); no invented
    # threshold, restricted to current + previous quarter (matches the themes
    # bundle's own diffusion trim).
    quarters = snap.get("quarters") or []
    prev_q = quarters[-2] if len(quarters) > 1 and quarters[-1] == cq else None
    for m in snap.get("metrics") or []:
        if m.get("cal_quarter") not in (cq, prev_q):
            continue
        n_disc, n_asked = m.get("n_disclosing", 0), m.get("n_companies", 0)
        if n_disc <= n_asked:
            continue
        ideas.append({
            "id": f"gap:{m['theme']}|{m['cal_quarter']}", "stream": "gap",
            "title": f"{m['theme']} — disclosed, not asked ({m['cal_quarter']})",
            "detail": f"{n_disc} disclosing / {n_asked} asked",
            "tickers": m.get("disclosing") or [], "theme": m["theme"],
            "score": n_disc - n_asked, "first_seen": as_of, "links": {"theme": m["theme"]},
        })

    # 4. stage:<detection id>
    for d in _read_jsonl(paths.topics_state / "detections.jsonl"):
        theme, ticker, detected_on = d.get("theme"), d.get("ticker"), d.get("detected_on")
        ideas.append({
            "id": f"stage:{theme}|{ticker}|{detected_on}", "stream": "stage",
            "title": f"{ticker} — {theme}: evidence, nobody's asked",
            "detail": (f"open {d.get('open_lag_days')}d since {d.get('first_evidence_date')} "
                       f"({', '.join(d.get('evidence_sources') or [])})"),
            "tickers": [ticker] if ticker else [], "theme": theme,
            "score": d.get("open_lag_days") or 0, "first_seen": detected_on,
            "links": ({"ticker": ticker, "theme": theme} if ticker else {"theme": theme}),
        })

    # 5. screen:<ticker> -- *tracked* rows excluded (already in the watchlist)
    for row in _latest_screen_rows(paths.docs):
        if row["tracked"]:
            continue
        ideas.append({
            "id": f"screen:{row['ticker']}", "stream": "screen",
            "title": f"{row['ticker']} clears {row['n']} AI screens", "detail": row["screens"],
            "tickers": [row["ticker"]], "theme": None, "score": row["n"],
            "first_seen": row["report_date"], "links": {"ticker": row["ticker"]},
        })

    # 6. novel:<name>
    for n in _novel_names(paths.topics_state):
        ideas.append({
            "id": f"novel:{n['name']}", "stream": "novel", "title": n["name"],
            "detail": n.get("why") or "", "tickers": n.get("tickers") or [],
            "theme": n.get("theme"), "score": n.get("score", 0),
            "first_seen": n.get("first_seen"), "links": {},
        })

    dismissed = _dismissed_ideas(paths.portal_state)
    ideas = [i for i in ideas if i["id"] not in dismissed]

    order = {"candidate": 0, "newly_said": 1, "gap": 2, "stage": 3, "screen": 4, "novel": 5}

    def _sort_key(i: dict):
        tier_rank = 0
        if i["stream"] == "newly_said":
            tk = i["tickers"][0] if i["tickers"] else None
            tier_rank = 0 if tier_of.get(tk) in t1_t2 else 1
        return (order[i["stream"]], tier_rank, -i["score"])

    ideas.sort(key=_sort_key)
    return {"as_of": as_of, "ideas": ideas}


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

    tb = ctx.themes if ctx.themes is not None else themes_bundle(paths, refs=refs)
    themes_rows = [{"slug": t["slug"], "stage": t["fm"].get("stage"), "status": t["fm"].get("status"),
                    "n_tickers": len(t["fm"].get("tickers") or []), "updated": t["fm"].get("updated")}
                   for t in tb["themes"]]
    themes_without_labels = sorted(t["slug"] for t in tb["themes"] if not t["in_vocab"])
    ib = ctx.ideas if ctx.ideas is not None else ideas_bundle(paths)

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
        upcoming = rp.upcoming(ctx.reports_days)
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
                  "candidates_pending": len(tb["candidates"]), "ideas": len(ib["ideas"])},
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

    tb_json = themes_bundle(paths, refs=ctx.refs)
    ctx.themes = tb_json
    _write_json(data_dir / "themes.json", tb_json)

    ib_json = ideas_bundle(paths)
    ctx.ideas = ib_json
    _write_json(data_dir / "ideas.json", ib_json)

    sb_json = scores_bundle(ctx.ticker_bundles)
    _write_json(data_dir / "scores.json", sb_json)

    mb_json = market_bundle(paths, today)
    _write_json(data_dir / "market.json", mb_json)

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
