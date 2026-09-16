"""Themes + ideas bundles: scripts/portal/theme_ideas.py (RIS4 slice 2, Task 4,
fix round 1 -- split authorized by controller ruling on review).

Split out of state_bundles.py alongside news_sec.py: themes_bundle()/
ideas_bundle() plus the state/topics/candidates.json <-> decisions.jsonl
reconciliation they share are the other natural seam (diffusion- and
candidates-derived, as opposed to state_bundles.py's ticker/market/manifest
orchestration). state_bundles.py imports themes_bundle/ideas_bundle from here
for use in manifest()/build_state(); nothing in this module imports FROM
state_bundles except the shared low-level pieces below.

Import order note (this and state_bundles.py import each other): this only
works because state_bundles.py defines Paths/DEFAULT_PATHS/_known_sets/
_read_json/_read_jsonl BEFORE its own `import theme_ideas` line, and this
module's use of `state_bundles`'s later-defined names (there are none) never
happens. Whichever of the two test harnesses imports first, the shared names
this module pulls via `from state_bundles import ...` are already bound on the
partially-initialized state_bundles module by the time this line runs -- a
standard, safe pattern for two modules that need each other's names as long as
neither needs the OTHER's late-defined names at import time (both modules only
call each other's functions from inside function bodies, never at module-level
evaluation).

Import as `from portal import theme_ideas` or the bare-module test-harness
convention `import theme_ideas` (scripts/portal/ must already be on sys.path --
see the bootstrap below, same as state_bundles.py's own).

Every zero-arg-default path reads live data from REPO via the module-level
DEFAULT_PATHS (imported from state_bundles.py, not duplicated); both public
functions accept an explicit `paths` override so tests run only against
fixtures under scripts/portal/fixtures/state/. Read-only.

The §6.2 "gap" and the stage1-vs-gap distinction are documented in
state_bundles.py's own module docstring (not repeated here) -- see
scripts/topics/theme_notes.py:165 and scripts/topics/lifecycle.py:142.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent             # scripts/portal
_here_parent = str(_here.parent)                     # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

_here_str = str(_here)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import identity  # noqa: E402
import vault      # noqa: E402
from state_bundles import DEFAULT_PATHS, Paths, _known_sets, _read_json, _read_jsonl  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "topics"))
import theme_notes  # noqa: E402


def log(msg: str) -> None:
    print(f"[theme_ideas] {msg}", flush=True)


def _affects_map(watchlist_path: Path) -> dict:
    try:
        return theme_notes.affects_map(watchlist_path)
    except Exception as exc:  # noqa: BLE001 -- any failure degrades
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
    returned whole, sorted by the matching decisions.jsonl row's `ts`
    (fallback: the candidate's own `first_seen`, when the decision came in via
    an inline status with no decisions.jsonl row at all) descending -- most
    recent decision first. The caller caps at "last 50" by slicing the FRONT of
    this already-descending list, not an arbitrary file-order tail.
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

    def _decided_sort_key(c: dict) -> str:
        dec = latest_decision.get(c.get("id"))
        ts = dec.get("ts") if dec else None
        return str(ts or c.get("first_seen") or "")

    decided.sort(key=_decided_sort_key, reverse=True)
    return pending, decided


# ---------------------------------------------------------------------------
# themes_bundle
# ---------------------------------------------------------------------------
_THEME_FM_KEYS = ("theme", "status", "stage", "tickers", "affects", "first_question_date", "lag_days", "updated")


def themes_bundle(paths: Paths = None, refs: list = None) -> dict:
    """data/themes.json.

    `refs` is an optional pre-computed vault.discover() result (build_state()
    and manifest() both already have one and pass it through -- vault.discover()
    reads and title-regexes every note under notes/, ~8.5s measured live, so
    recomputing it per caller was the single biggest avoidable cost in a full
    build_state() run). None -> computed fresh, so this stays independently
    callable/testable with just `paths`.

    themes: every written notes/themes/*.md (in_vocab=True; fm trimmed to
    _THEME_FM_KEYS, body wikilink-resolved, stages_by_ticker recomputed live via
    theme_notes.theme_state() off diffusion.json's "pairs" -- notes don't carry
    per-ticker stage in their own frontmatter) UNION every theme in
    state/topics/stages.json's "gated" list (scripts/topics/stage_alert.py's own
    current-quarter §7.1 gate, already computed daily -- not re-derived here)
    that has NO note yet (in_vocab=False, same theme_state() call, body="").

    candidates/decided: state/topics/candidates.json reconciled against
    decisions.jsonl (see _reconcile_candidates). "decided" is the 50 MOST
    RECENT decisions (already sorted ts/first_seen descending by
    _reconcile_candidates -- this just takes the front 50, not a file-order
    tail).

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
        "themes": themes, "candidates": pending, "decided": decided[:50],
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
    stage, screen, novel. See state_bundles.py's module docstring for the exact
    §6.2 gap citation and the stage1-vs-gap distinction.

    Ids are stable across runs by construction: candidate/gap ids come straight
    from source-file keys (candidates.json's own id / metrics' theme+quarter);
    stage ids are synthesized ONLY from append-only detections.jsonl fields
    (theme|ticker|detected_on, ticker guarded to "" when absent so the id never
    literally renders the string "None") -- never from a recomputed field like
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

    # 3. gap:<theme>|<quarter> -- §6.2 (see state_bundles.py module docstring);
    # no invented threshold, restricted to current + previous quarter (matches
    # the themes bundle's own diffusion trim).
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

    # 4. stage:<detection id> -- ticker guarded to "" (see docstring)
    for d in _read_jsonl(paths.topics_state / "detections.jsonl"):
        theme, ticker, detected_on = d.get("theme"), d.get("ticker"), d.get("detected_on")
        ideas.append({
            "id": f"stage:{theme}|{ticker or ''}|{detected_on}", "stream": "stage",
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
