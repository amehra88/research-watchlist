"""News + SEC 30-day shards for the RIS4 portal builder: scripts/portal/news_sec.py
(RIS4 slice 2, Task 4).

Split out of state_bundles.py from the start (controller-directed, per the Task 4
brief's size note: "if it passes ~600 lines, split the news/sec shard writer out") --
seven builders plus a Paths dataclass in one file was always going to clear that.
Nothing imports these from state_bundles.py's own namespace; call as
`from portal import news_sec` (package-relative) or the bare-module test-harness
convention `import news_sec` (works once scripts/portal/ is on sys.path -- see the
bootstrap below, identical in spirit to vault.py/identity.py/reports.py's own).

`news_bundle()` shards notes/news/*.md into ISO-week files (Mon-Sun) plus a
per-ticker index; `sec_bundle()` reads notes/sec/*.md frontmatter ONLY -- SEC note
bodies average 36 KB and are never loaded (see `_head_fm`). Both windows are
`[today - days, today]`, filtered on the filename's leading YYYY-MM-DD before any
YAML parse -- same technique as scripts/thesis/sources.py's news_since()/
earnings_notes_since() (filenames start with the note's own date). Every file in
the window is read exactly ONCE (a single glob + a single frontmatter/body parse
per file); there is no second pass. Read-only: never writes into notes/, config/,
or state/. The only writes to `<out_dir>/data/news/*.json` and
`<out_dir>/data/sec_30d.json` happen in state_bundles.build_state(), not here --
these functions only return dicts, per the Task 4 brief's "each returns a dict;
build_state(out_dir, ctx) writes them".
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import yaml

try:
    from yaml import CSafeLoader as _YamlLoader     # libyaml (measured live: ~10x
except ImportError:                                 # faster than pure-Python SafeLoader --
    from yaml import SafeLoader as _YamlLoader       # 76s -> 7s over 12.5K news notes, the
                                                      # dominant cost in a 30-day news_bundle()
                                                      # run) -- falls back if libyaml isn't
                                                      # built into this interpreter's pyyaml.

_here = Path(__file__).resolve().parent            # scripts/portal
_here_parent = str(_here.parent)                    # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402


def log(msg: str) -> None:
    print(f"[news_sec] {msg}", flush=True)


@dataclass
class Paths:
    notes: Path = None

    def __post_init__(self):
        self.notes = self.notes if self.notes is not None else (REPO / "notes")


DEFAULT_PATHS = Paths()

# Mirrors scripts/thesis/sources.py's own private `_FM_RE` -- this module is
# self-contained (etf_trades.py precedent) rather than importing a leading-
# underscore name across modules.
_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
_HEAD_BYTES = 4096   # SEC frontmatter measured ~500B live; 4096 gives ample margin
                      # without reading the body (avg 36 KB) into memory.
_HEADLINE_RE = re.compile(r"^## (.+)$", re.M)


def _fm_and_body(path: Path) -> tuple[dict, str]:
    t = path.read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(t)
    if not m:
        return {}, t
    try:
        return (yaml.load(m.group(1), Loader=_YamlLoader) or {}), t[m.end():]
    except yaml.YAMLError:
        return {}, t


def _head_fm(path: Path, n: int = _HEAD_BYTES) -> dict:
    """Frontmatter-only parse: reads only the first `n` bytes of `path`, never the
    body. Falls back to a full read only if the closing '---' fence isn't inside
    the head window (never observed live; frontmatter runs ~500B), so a very rare
    long-frontmatter file still parses correctly rather than silently dropping.
    """
    with open(path, "rb") as f:
        head = f.read(n)
    text = head.decode("utf-8", errors="replace")
    m = _FM_RE.match(text)
    if m:
        try:
            return yaml.load(m.group(1), Loader=_YamlLoader) or {}
        except yaml.YAMLError:
            return {}
    if text.startswith("---\n"):
        # frontmatter longer than the head window -- fall back to a full parse
        fm, _ = _fm_and_body(path)
        return fm
    return {}


# ---------------------------------------------------------------------------
# sec_bundle
# ---------------------------------------------------------------------------
def sec_bundle(days: int = 30, paths: Paths = None, today: date = None) -> dict:
    """{rows:[{ticker, form_type, items, filed_date, filing_url, press_release_url,
    themes}]} for every notes/sec/*.md filed within the trailing `days` days
    (inclusive of `today`). Frontmatter-only per file (see `_head_fm`). Windowed
    on the filename's leading YYYY-MM-DD, which is the filing date for every SEC
    note observed; `filed_date` from frontmatter is still preferred in the row
    itself when present, filename date is only the fallback/window key.
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    cutoff = (today - timedelta(days=days)).isoformat()
    sec_dir = paths.notes / "sec"
    if not sec_dir.is_dir():
        log(f"sec_bundle: {sec_dir} missing -- returning 0 rows")
        return {"rows": []}

    rows, n_seen = [], 0
    for p in sorted(sec_dir.glob("*.md")):
        name = p.name
        if name[:10] < cutoff:
            continue
        n_seen += 1
        fm = _head_fm(p)
        if not fm:
            continue
        rows.append({
            "ticker": fm.get("ticker"), "form_type": fm.get("form_type"),
            "items": fm.get("items") or [], "filed_date": fm.get("filed_date") or name[:10],
            "filing_url": fm.get("filing_url"), "press_release_url": fm.get("press_release_url"),
            "themes": fm.get("themes") or [],
        })
    log(f"sec_bundle: {n_seen} filings in the last {days}d, {len(rows)} rows")
    return {"rows": rows}


# ---------------------------------------------------------------------------
# news_bundle
# ---------------------------------------------------------------------------
def _headline(body: str) -> str | None:
    m = _HEADLINE_RE.search(body)
    return m.group(1).strip() if m else None


def _iso_week_shard(iso_date: str) -> str:
    y, mo, d = (int(x) for x in iso_date[:10].split("-"))
    iy, iw, _ = date(y, mo, d).isocalendar()
    return f"{iy}-W{iw:02d}"


def news_bundle(days: int = 30, paths: Paths = None, today: date = None) -> dict:
    """{shards: {"<iso_year>-W<iso_week>": {"rows": [...]}}, index: {ticker:
    [[shard, idx], ...]}} for notes/news/*.md within the trailing `days` days.
    Sharded by ISO week (Monday-Sunday) of the row's own date (`published_date`
    frontmatter if present, else the filename's leading YYYY-MM-DD). One glob +
    one frontmatter/body parse per in-window file -- no second pass, no per-
    ticker re-scan (unlike scripts/thesis/sources.py's news_since(), which
    prefilters per ticker because it's called once per ticker; here every
    in-window file is wanted regardless of ticker, so a raw byte prefilter would
    just be extra work for the same read).

    `headline` = the body's first `## ` line (not `cluster_headlines[0]` --
    the brief is explicit these can differ for a re-clustered story).
    `url` = `source_urls[0]` if present, else None (a handful of low-confidence
    notes carry no source_urls -- see fixture 2026-09-09-headline-three).
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    cutoff = (today - timedelta(days=days)).isoformat()
    news_dir = paths.notes / "news"
    if not news_dir.is_dir():
        log(f"news_bundle: {news_dir} missing -- returning 0 rows")
        return {"shards": {}, "index": {}}

    shards: dict[str, list[dict]] = {}
    index: dict[str, list[list]] = {}
    n_seen = 0
    for p in sorted(news_dir.glob("*.md")):
        name = p.name
        if name[:10] < cutoff:
            continue
        n_seen += 1
        fm, body = _fm_and_body(p)
        if not fm:
            continue
        row_date = fm.get("published_date") or name[:10]
        try:
            shard = _iso_week_shard(row_date)
        except (ValueError, TypeError) as exc:
            log(f"news_bundle: {name}: malformed published_date {row_date!r} ({exc}) -- skipping row")
            continue
        urls = fm.get("source_urls") or []
        row = {
            "id": f"news/{name}", "date": row_date, "tickers": fm.get("tickers") or [],
            "themes": fm.get("themes") or [], "macro_signals": fm.get("macro_signals") or [],
            "confidence": fm.get("confidence"), "summarized": fm.get("summarized"),
            "headline": _headline(body), "rationale": fm.get("rationale"),
            "url": urls[0] if urls else None,
        }
        bucket = shards.setdefault(shard, [])
        idx = len(bucket)
        bucket.append(row)
        for tk in row["tickers"]:
            index.setdefault(tk, []).append([shard, idx])

    log(f"news_bundle: {n_seen} notes in the last {days}d, {len(shards)} ISO-week shards, "
        f"{sum(len(v) for v in shards.values())} rows")
    return {"shards": {k: {"rows": v} for k, v in shards.items()}, "index": index}
