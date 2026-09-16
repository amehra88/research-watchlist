"""Search index: scripts/portal/search_index.py (RIS4 slice 2, Task 5).

Fifth module of the RIS4 portal builder. Builds `data/search.json`, a single
client-side inverted index the mobile-web app (Task 8's "More -> Search")
loads once and queries entirely in the browser -- no server-side search.

Reuses Task 1's vault.py (discover/load_note), Task 4's news_sec.py
(news_bundle) and vault.py's own ingest_bundles() rather than re-reading
notes/. Read-only: never writes into notes/, config/, or state/ -- the only
write is `<out_dir>/data/search.json`.

Import as `from portal import search_index` or the bare-module test-harness
convention `import search_index` (scripts/portal/ must already be on
sys.path -- see the bootstrap below, same as state_bundles.py/news_sec.py's
own two-insert convention: scripts/ parent so `from portal import REPO`
resolves, and scripts/portal/ itself so `import vault` / `import news_sec`
resolve as bare sibling modules).

--------------------------------------------------------------------------
TOKENIZER SPEC -- app.js (Task 8) mirrors this EXACTLY. Read this before
touching TOKEN_RE, tokenize(), or STOPLIST; any drift here silently breaks
query-vs-index matching in the browser.
--------------------------------------------------------------------------
1. Lowercase the whole input string first (`text.lower()`). CAVEAT: Python
   `str.lower()` and JS `String.prototype.toLowerCase()` agree on ASCII
   (the overwhelming case here -- tickers, note prose) but can diverge on a
   handful of Unicode edge cases (e.g. Turkish dotless i, German ß
   case-folding); not handled here, flagged for awareness rather than fixed
   since the corpus is ASCII-dominant.
2. Extract tokens with the regex `[a-z0-9][a-z0-9.\\-]+` (TOKEN_RE below),
   applied with a global "find all matches" scan (`re.findall` / JS
   `String.matchAll`) over the lowercased text -- NOT split-on-whitespace.
   A token is 2+ chars, starts with a letter or digit, and may otherwise
   contain letters, digits, `.` and `-`. Consequences worth naming because
   they are easy to get wrong when re-implementing in JS:
     - single-character tokens ("a", "i") can never occur (`+` requires the
       tail to have >= 1 more char after the leading class).
     - punctuation other than `.`/`-` (apostrophes, commas, parens, colons,
       Markdown `**`/`|`/`#`) is never token-internal -- it always splits
       tokens, so "NVIDIA's" tokenizes to ["nvidia", "s"] (both kept unless
       in STOPLIST; "s" is not).
     - a trailing `.` or `-` is NOT stripped. "Nvidia." at the end of a
       sentence indexes as the token "nvidia." (distinct from "nvidia").
       This is the literal brief regex, shipped as specified rather than
       "fixed" -- do not add trimming without updating this docstring AND
       app.js together.
     - "gb200-nvl72" and "state-of-the-art" survive as single tokens
       (hyphens are token-internal).
3. Drop every token that is an exact (post-lowercase) member of STOPLIST.
4. No stemming, no plural-folding, no synonym expansion.
5. Duplicates are NOT removed by tokenize() itself -- `tokenize("gpu gpu")`
   returns `["gpu", "gpu"]`. Dedup (one docIdx per token per doc) happens
   one layer up, in build_index().

STOPLIST is emitted verbatim into `data/search.json` under the `"stoplist"`
key specifically so app.js LOADS it at runtime instead of maintaining its
own hardcoded copy that could drift -- see build_index()'s docstring.
--------------------------------------------------------------------------

Doc record shape (per the Task 5 brief, verbatim):
    {id, t, k, tk, th, d, f, s, sn}
  id  -- stable unit id: "<note-id>#<section-idx>" for a note section
         (note-id = vault NoteRef.rel, already stable per vault.py's own
         docstring), the news row's own "news/<file>.md" id for a news row,
         or the ingest item's own note id for an ingest item. Unique by
         construction across all three unit sources (disjoint id
         namespaces: ticker-dir/top-dir relpaths vs "news/*.md" vs
         substack/podcast/etc relpaths never collide).
  t   -- title: the section heading (or the note's own title when the
         heading is blank), the news row's headline, or the ingest item's
         title.
  k   -- content kind. For a note section, `note["kind"]` verbatim (e.g.
         "earnings", "conference", "synthesis", "thesis", "theme_index",
         "profile", "theme", "report", "other" -- see vault.classify()).
         For a news row, the literal string "news". For an ingest item,
         `ref.kind` verbatim (e.g. "substack", "podcast", "flow",
         "foreign", "sector", "pvt_profile" -- matches vault.NoteRef.kind,
         NOT the plural ingest_bundles() bucket name).
  tk  -- SCHEMA NOTE (deviation from the brief's singular "tk"): always a
         list[str], never a bare string. A note section carries `[ticker]`
         or `[]`; a news row carries `row["tickers"]` (already a list --
         news rows are routinely multi-ticker, and collapsing that to one
         string would silently drop tickers from the index). Flagged
         explicitly for Task 6/7/8: app.js must treat `tk` as an array
         everywhere (`doc.tk.includes(T)`, not `doc.tk === T`).
  th  -- list[str] of themes (fm.get("themes") or the row's own "themes").
  d   -- ISO date string, or None when the underlying note/item has none
         (e.g. a thesis note, or an unwindowed pvt_profile item).
  f   -- the data file the app should open to render this doc, one of:
           "data/tickers/<TICKER>.json"  -- ticker-carrying note sections
           "data/themes.json"            -- theme (kind="theme") sections;
                                             themes_bundle() (Task 4) embeds
                                             every notes/themes/*.md body,
                                             wikilink-resolved, so this is
                                             a real, already-built target
           "data/news/<shard>.json"      -- news rows (ISO-week shard,
                                             matches news_sec.news_bundle())
           "data/ingest/<bucket>.json"   -- ingest items, bucket = the
                                             plural key from
                                             vault.ingest_bundles() (
                                             "substacks"/"podcasts"/
                                             "foreign"/"flows"/"sector"/
                                             "pvt") -- Task 6 is expected to
                                             write exactly these six files
           None                           -- SCHEMA NOTE (deviation): a
                                             ticker-less, non-theme note
                                             (kind="report", or kind="other"
                                             with no ticker -- e.g.
                                             notes/reports/*.md) has no
                                             individual route in the Task
                                             7/8 briefs. Rather than drop
                                             this content from the index
                                             (a silent search miss for text
                                             that genuinely exists in the
                                             vault), it is still indexed
                                             with f=None; the app renders
                                             the snippet as a non-tappable
                                             row. Flagged for the
                                             controller to overrule.
  s   -- section index within the note (note sections), row index within
         the news shard (news rows -- matches news_sec's own [shard, idx]
         index pairs), or item index within the ingest bucket's `items`
         list (ingest items).
  sn  -- a <=120-char snippet (SNIPPET_LEN), whitespace-collapsed. FIX ROUND
         1: for a news doc, `sn` degrades to `""` once write_index()'s
         fallback ladder reaches "no_snippet" or later (see NEWS_MODES) --
         the app falls back to displaying `t` (the headline) when `sn` is
         empty. Note-section and ingest-item docs never have `sn` cleared.

build_index()'s internal unit shape adds one field beyond the doc record,
"text" (the searchable body tokenize() runs over) -- build_index() strips
it before emitting `docs`, so it never reaches search.json. News units
additionally carry "_headline_text" (headline only, no rationale), used by
write_index()'s "headline_only"/"7d" fallback stages; also stripped.

`data/search.json`'s top-level shape is `{docs, terms, stoplist, news_mode}`
-- `news_mode` (fix round 1) is one of NEWS_MODES, the fallback stage
write_index() actually used for this build; Task 8's Status screen reads it
to show the operator when news search has been degraded.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

_here = Path(__file__).resolve().parent             # scripts/portal
_here_parent = str(_here.parent)                     # scripts/
if _here_parent not in sys.path:
    sys.path.insert(0, _here_parent)
from portal import REPO  # noqa: E402

_here_str = str(_here)
if _here_str not in sys.path:
    sys.path.insert(0, _here_str)
import news_sec  # noqa: E402
import vault      # noqa: E402


def log(msg: str) -> None:
    print(f"[search_index] {msg}", flush=True)


# ---------------------------------------------------------------------------
# tokenizer -- see the module docstring's TOKENIZER SPEC section
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.\-]+")

# ~150 common English function words, lowercase, deduplicated. Entries that
# could never be produced by TOKEN_RE (none here -- single-char words like
# "a"/"i" were deliberately left OUT rather than kept as dead weight) are
# not present. Emitted verbatim into data/search.json's "stoplist" key.
STOPLIST = [
    "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by",
    "can", "could",
    "did", "do", "does", "doing", "down", "during",
    "each",
    "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how",
    "if", "in", "into", "is", "it", "its", "itself",
    "just",
    "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now",
    "of", "off", "on", "once", "only", "or", "other", "our", "ours",
    "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up",
    "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with",
    "you", "your", "yours", "yourself", "yourselves",
    "also", "across", "among", "amid", "around", "behind", "beside",
    "beyond", "cannot", "despite", "either", "etc", "might", "must",
    "neither", "next", "onto", "per", "perhaps", "rather", "shall", "since",
    "still", "thus", "toward", "upon", "via", "whence", "whereas",
    "wherever", "whether", "whose", "yet",
]
_STOP_SET = frozenset(STOPLIST)


def tokenize(text: str) -> list[str]:
    """[a-z0-9][a-z0-9.\\-]+ over text.lower(), STOPLIST removed, no
    stemming, duplicates retained. See the module docstring's TOKENIZER SPEC
    -- app.js mirrors these rules exactly.
    """
    if not text:
        return []
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in _STOP_SET]


# ---------------------------------------------------------------------------
# build_index / write_index
# ---------------------------------------------------------------------------
_DOC_KEYS = ("id", "t", "k", "tk", "th", "d", "f", "s", "sn")


def build_index(units: list[dict]) -> dict:
    """{docs:[{id,t,k,tk,th,d,f,s,sn}], terms:{token:[docIdx,...]}}.

    `units` are the unit dicts build_units() (or a caller/test) assembles --
    each doc record's fields (_DOC_KEYS) plus "text", the string tokenize()
    runs over. docIdx is the unit's position in `units` (== its position in
    the returned `docs` list); appending in input order and only ever
    growing `terms[token]` keeps every docIdx list ascending and, within a
    single doc, unique (a token repeated in one doc's text is only appended
    once, checked via "last entry == this docIdx" rather than a full
    membership test). Callers control the order units are handed in --
    build_units() enumerates notes/news/ingest in a fixed, glob-sorted /
    dict-insertion-ordered sequence (see its own docstring), so `docs` is
    byte-stable across rebuilds when the underlying inputs haven't changed.
    `terms` keys are sorted so the output doesn't depend on token-discovery
    order (which does vary run-to-run with dict iteration only in the
    pathological case of hash randomization across separate processes --
    sorting removes that as a variable entirely, at zero cost since the
    terms dict is written once, not looked up by insertion order).
    """
    docs = []
    terms: dict[str, list[int]] = {}
    for idx, u in enumerate(units):
        docs.append({k: u[k] for k in _DOC_KEYS})
        for tok in tokenize(u.get("text") or ""):
            lst = terms.setdefault(tok, [])
            if not lst or lst[-1] != idx:
                lst.append(idx)
    return {"docs": docs, "terms": {tok: terms[tok] for tok in sorted(terms)}}


MAX_BYTES = 3 * 1024 * 1024   # 3 MB -- the brief's size-fallback threshold

# Ordered, CUMULATIVE degradation ladder (fix round 1, controller-directed:
# news must stay searchable in production as long as possible, so cheap
# per-doc field cuts come before window/row cuts). Each stage includes
# every earlier stage's cut:
#   "full"          -- units as given (the documented default upstream
#                       window is the last 14 days of news, per
#                       build_units()); no cuts.
#   "no_snippet"    -- news docs' `sn` cleared to "" (app falls back to
#                       `t`, the headline).
#   "headline_only" -- ALSO: news docs are tokenized headline-only (the
#                       `rationale` text stops contributing terms).
#   "7d"            -- ALSO: the news window narrows from 14 to 7 days.
#   "none"          -- every news unit is dropped.
# Non-news units (note sections, ingest items) are never touched at any
# stage. write_index() stops at the first stage whose serialized payload
# fits under max_bytes and records it in the payload as "news_mode".
NEWS_MODES = ("full", "no_snippet", "headline_only", "7d", "none")


def _apply_news_mode(units: list[dict], mode: str, today: date) -> list[dict]:
    """One step of the NEWS_MODES ladder applied to `units`. Non-news units
    (k != "news") always pass through unchanged, at every mode. A missing/
    None `d` on a "7d" pass is treated as out-of-window (dropped
    defensively -- an undated news row should never occur upstream, but
    this must not crash on one).
    """
    if mode == "full":
        return units
    cutoff = (today - timedelta(days=7)).isoformat() if mode == "7d" else None
    out = []
    for u in units:
        if u["k"] != "news":
            out.append(u)
            continue
        if mode == "none":
            continue
        if mode == "7d":
            d = u.get("d")
            if d is None or d < cutoff:
                continue
        u2 = dict(u)
        u2["sn"] = ""                                    # no_snippet and every stage after it
        if mode in ("headline_only", "7d"):
            u2["text"] = u.get("_headline_text", u["text"])
        out.append(u2)
    return out


def write_index(out_dir, units: list[dict], today: date = None, max_bytes: int = MAX_BYTES) -> dict:
    """Writes `<out_dir>/data/search.json` and returns {path, bytes, docs,
    terms, news_mode} for the caller's own logging.

    Size fallback (fix round 1 -- each transition logged): walk NEWS_MODES
    in order, stopping at the first stage whose serialized payload
    (including "stoplist" and "news_mode") fits under `max_bytes`. See
    NEWS_MODES' own comment for what each stage cuts. Non-news units are
    never dropped or altered at any stage -- only news is size-elastic, per
    the brief. The stage actually used is written into the payload as
    `news_mode` (Task 8's Status screen reads it) and returned in the stats
    dict. If the corpus is still oversized at "none" (every news unit
    already dropped), the "none" build is written anyway (logged), since
    there is nothing left this function is allowed to cut.
    """
    today = today or date.today()
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "search.json"

    idx, blob, mode = {}, b"", NEWS_MODES[0]
    for i, mode in enumerate(NEWS_MODES):
        filtered = _apply_news_mode(units, mode, today)
        idx = build_index(filtered)
        idx["stoplist"] = STOPLIST
        idx["news_mode"] = mode
        blob = json.dumps(idx, separators=(",", ":")).encode("utf-8")
        over = len(blob) > max_bytes
        if not over:
            if mode != "full":
                log(f"search.json {len(blob)} bytes <= {max_bytes} at news_mode={mode}")
            break
        if mode == NEWS_MODES[-1]:
            log(f"search.json still {len(blob)} bytes > {max_bytes} at news_mode={mode} -- writing anyway")
            break
        nxt = NEWS_MODES[i + 1]
        log(f"search.json {len(blob)} bytes > {max_bytes} at news_mode={mode} -- dropping to news_mode={nxt}")

    path.write_bytes(blob)
    return {"path": str(path), "bytes": len(blob), "docs": len(idx["docs"]),
            "terms": len(idx["terms"]), "news_mode": mode}


# ---------------------------------------------------------------------------
# build_units -- convenience assembly Task 6 may call instead of building
# `units` itself. Duck-typed, not tied to state_bundles.Ctx: pass whichever
# of `refs`/`news`/`ingest` the caller already has (build_state() builds a
# vault.discover() refs list and a news_sec.news_bundle() once each --
# vault.discover() alone measured ~8.5s live per news_sec.py/state_bundles.py's
# own docstrings, so re-running it here for a caller that already has one
# would be the same avoidable cost those modules call out).
# ---------------------------------------------------------------------------
@dataclass
class Paths:
    notes: Path = None

    def __post_init__(self):
        self.notes = self.notes if self.notes is not None else (REPO / "notes")


DEFAULT_PATHS = Paths()

NEWS_DAYS = 14          # brief: "news rows from the last 14 days"
INGEST_DAYS = 30        # matches ingest_bundles()'s own default; flows still
                         # gets its 14d override internally (vault.py's _BUCKETS)
SNIPPET_LEN = 120

# note kinds vault.ingest_bundles() already turns into ingest items -- skipped
# in the note-section pass below so nothing is indexed twice. Keys match
# vault.NoteRef.kind, NOT the plural ingest_bundles() bucket names.
_INGEST_KINDS = {"substack", "podcast", "foreign", "flow", "sector", "pvt_profile"}

# Mirror of vault.py's own private `_BUCKETS` (bucket name -> NoteRef.kind
# half only -- the window-override half isn't needed here). Duplicated
# rather than importing a private name across modules, same convention
# state_bundles.py's own `_known_sets` comment already established.
_INGEST_BUCKET_KIND = {
    "substacks": "substack", "podcasts": "podcast", "foreign": "foreign",
    "flows": "flow", "sector": "sector", "pvt": "pvt_profile",
}


def _snippet(text: str, n: int = SNIPPET_LEN) -> str:
    return " ".join((text or "").split())[:n]


def _note_section_units(refs: list) -> list[dict]:
    units = []
    for ref in refs:
        if ref.kind in _INGEST_KINDS:
            continue
        note = vault.load_note(ref)
        ticker = note["ticker"]
        if ticker:
            f = f"data/tickers/{ticker}.json"
        elif note["kind"] == "theme":
            f = "data/themes.json"
        else:
            f = None   # see module docstring's doc-record "f" schema note
        themes = note["fm"].get("themes") or []
        for i, sec in enumerate(note["sections"]):
            units.append({
                "id": f"{note['id']}#{i}", "t": sec["h"] or note["title"],
                "k": note["kind"], "tk": [ticker] if ticker else [], "th": themes,
                "d": note["date"], "f": f, "s": i, "sn": _snippet(sec["text"]),
                "text": f"{sec['h']}\n{sec['text']}",
            })
    return units


def _news_units(news: dict, days: int, today: date) -> list[dict]:
    cutoff = (today - timedelta(days=days)).isoformat()
    units = []
    for shard, payload in news.get("shards", {}).items():
        for idx, row in enumerate(payload.get("rows", [])):
            d = row.get("date")
            if d is not None and d < cutoff:
                continue
            headline = row.get("headline") or ""
            units.append({
                "id": row["id"], "t": headline, "k": "news",
                "tk": row.get("tickers") or [], "th": row.get("themes") or [],
                "d": d, "f": f"data/news/{shard}.json", "s": idx,
                "sn": _snippet(row.get("rationale") or headline),
                "text": f"{headline}\n{row.get('rationale') or ''}",
                "_headline_text": headline,   # fix round 1: NEWS_MODES "headline_only"/"7d"
            })
    return units


def _ingest_units(ingest: dict) -> list[dict]:
    units = []
    for bucket, payload in ingest.items():
        for idx, item in enumerate(payload.get("items", [])):
            body = item.get("body") or ""
            units.append({
                "id": item["id"], "t": item.get("title") or "",
                "k": _INGEST_BUCKET_KIND.get(bucket, bucket),
                "tk": item.get("tickers") or [], "th": item.get("themes") or [],
                "d": item.get("date"), "f": f"data/ingest/{bucket}.json", "s": idx,
                "sn": _snippet(item.get("title") or body),
                "text": f"{item.get('title') or ''}\n{body[:600]}",
            })
    return units


def build_units(paths: Paths = None, refs: list = None, news: dict = None,
                 ingest: dict = None, today: date = None,
                 news_days: int = NEWS_DAYS, ingest_days: int = INGEST_DAYS) -> list[dict]:
    """Every searchable unit: note sections (every discovered note whose
    kind isn't one of the six ingest_bundles() kinds) + news rows (last
    `news_days` days) + ingest items (all six ingest_bundles() buckets).
    Order is fixed -- notes (vault.discover()'s own sorted-glob order, one
    entry per section in note order) then news (shard-sorted, row order
    within each shard) then ingest (vault.ingest_bundles()'s own fixed
    bucket order, item order within each bucket, already date-sorted) --
    so the same inputs always produce the same `units` list, which is what
    makes build_index()'s `docs` byte-stable across rebuilds.

    `paths`/`refs`/`news`/`ingest`/`today` are all optional, additive
    overrides: pass pre-built `refs` (vault.discover()) and/or `news`
    (news_sec.news_bundle(), any window >= news_days -- rows outside the
    trailing `news_days` are filtered out here regardless of the window the
    bundle itself was built with) and/or `ingest` (vault.ingest_bundles())
    when the caller already has them this run; None -> computed fresh
    against `paths` (default: live REPO/notes).
    """
    paths = paths or DEFAULT_PATHS
    today = today or date.today()
    refs = refs if refs is not None else vault.discover(paths.notes)
    news = news if news is not None else news_sec.news_bundle(
        news_days, news_sec.Paths(notes=paths.notes), today)
    ingest = ingest if ingest is not None else vault.ingest_bundles(refs, ingest_days, today)

    return _note_section_units(refs) + _news_units(news, news_days, today) + _ingest_units(ingest)
