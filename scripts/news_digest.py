#!/usr/bin/env python3
"""
news_digest — v3 news-flow / IR channel (merged-pool, 3-pass LLM classifier).

Evolution of the Phase-C dual-source digest: the heuristic source-tier/story-volume
filter (filter.py) is REPLACED by a batched `claude -p` classifier (classify_llm.py) that
judges materiality over the full 83-ticker T1+T2 universe, themes over the 61-theme master
list, and macro signals over config/macro_signals.yaml — then a batched summarizer
(summarize.py) writes PM-ready items from the HEADLINES (no article bodies exist in any
source). Survivors land in BOTH the morning brief AND the pg corpus (notes/news/).

Pipeline (was ticker-first; now merged-pool):
  pull Google RSS across 87 identities + FactSet ALL_NEWS  → one pool
    → dedup items by sha256(source+title) vs the state ledger (STALE_HOURS)
    → cluster near-duplicate headlines (Jaccard, reused)
    → LLM classify clusters (materiality / themes / macro)   [Pass A/B/C, batched]
    → RANK survivors and select the top DIGEST_LIMIT          [rank.py, batched]
    → summarize the SELECTED stories only                     [batched]
    → route into Company / Themes / Macro sections (rank order preserved)
    → render brief + (live) file notes/news/{date}-{slug}.md → chunk into pg
       (selected → full notes; below-the-cut survivors → headline-only notes, same corpus)

Modes:
  --premarket / --postmarket   full digest, EMAIL, writes ledger + files pg (standalone, as before)
  --brief                      overnight run for the 03:00 combined brief: writes
                               report_news_{date}.txt + files pg, NO email, and reads the
                               ledger READ-ONLY (never writes it) so it can't starve the
                               standalone emails' dedup.
  --dry-run                    print to stdout; no email, no ledger write, no pg filing.
  --no-factset                 Google-only (skip the FactSet channel).

DELIVERY (operator, 2026-08-21): this digest is a STANDALONE EMAIL. It used to ALSO appear as the
NEWS FLOW section of the 07:00 Daily Digest, which delivered the same stories twice each morning;
combine_and_send.py dropped that section and run_daily.sh no longer waits for report_news_{date}.txt
(still written, as a gitignored audit artifact). On weekends run_daily.sh invokes --premarket, since
the 06:45 cron is Mon-Fri and the weekend run IS the standalone email.

Story cap (operator, 2026-08-19; tightened to 20 on 2026-08-21): at most rank.DIGEST_LIMIT stories, max
rank.MAX_PER_TICKER per ticker, with sell-side rating actions ranked last and admitted only when
they state a non-valuation rationale. Selection sits BEFORE the summarizer, so it cuts the largest
cost line (~$3.2/run over ~260 items) rather than merely shortening the email. Everything that
misses the cut is still classified and still filed to notes/news + pg, headline-only.

Engine: `claude -p` on subscription auth (ANTHROPIC_API_KEY stripped), per the cost model;
rides the daily auth canary. Per-source/per-batch isolation: one feed or one classifier
batch failing never aborts the run (degraded coverage SENDS ANYWAY with a banner).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from newsdigest import (  # noqa: E402
    PREMARKET_WINDOW_HOURS, POSTMARKET_WINDOW_HOURS,
    FACTSET_CONCURRENCY, STALE_HOURS, LEDGER_PRUNE_HOURS,   # FACTSET_CONCURRENCY now caps the
    #                                        Google RSS fan-out only; FactSet is a batched pass.
)
from newsdigest.identity import load_identities          # noqa: E402
from newsdigest.sources import load_classifier           # noqa: E402
from newsdigest import google_rss, factset_news          # noqa: E402
from newsdigest.cluster import cluster_items             # noqa: E402
from newsdigest import classify_llm, summarize           # noqa: E402
from newsdigest import pre_filter, merge, verdict_cache  # noqa: E402  (pre-LLM volume reduction: Levers 1-3)
from newsdigest import rank                             # noqa: E402  (editorial top-N selection)

LOG_PATH = os.path.join(REPO_ROOT, "logs", "news_digest.log")
LEDGER_PATH = os.path.join(REPO_ROOT, "state", "news_digest_seen.jsonl")
NOTES_NEWS_DIR = os.path.join(REPO_ROOT, "notes", "news")
WATCHLIST_YAML = os.path.join(REPO_ROOT, "config", "watchlist.yaml")
MACRO_YAML = os.path.join(REPO_ROOT, "config", "macro_signals.yaml")
CHUNKING_DIR = os.path.join(REPO_ROOT, "scripts", "chunking")

# Cost / rate-limit guardrail: cap clusters sent to the classifier per run. Excess (lowest
# volume/oldest) is dropped with a logged banner — never silently. Tune if volume grows.
MAX_CLUSTERS = 300

logger = logging.getLogger("news_digest")


# ─────────────────────────── vocab / universe helpers ───────────────────────────

def load_universe_ticker_names(identities) -> dict:
    """{TICKER: name} for the 83-ticker T1+T2 materiality universe (∩ identities).

    A000660 (redundant Korean SK Hynix alt-id, no identity) is excluded — SK Hynix is
    covered by 000660.KS. This set is BOTH the classifier's name-hint block and its
    materiality allow-list."""
    wl = yaml.safe_load(open(WATCHLIST_YAML)) or {}
    universe = set()
    for block in ("tier_1_bctk", "tier_2_active_candidates"):
        for x in (wl.get(block) or []):
            t = x.get("ticker") if isinstance(x, dict) else x
            if t:
                universe.add(t)
    return {t: identities[t].name for t in universe if t in identities}


def load_ticker_tiers() -> dict:
    """{TICKER: watchlist block name} — the tier signal rank.py ranks on (T1 > T2 > not held)."""
    wl = yaml.safe_load(open(WATCHLIST_YAML)) or {}
    tiers = {}
    for block in ("tier_1_bctk", "tier_2_active_candidates"):
        for x in (wl.get(block) or []):
            t = x.get("ticker") if isinstance(x, dict) else x
            if t and t not in tiers:          # first block wins: a cross-tier dup stays T1
                tiers[t] = block
    return tiers


def load_valid_themes() -> set:
    block = (yaml.safe_load(open(WATCHLIST_YAML)) or {}).get("themes", {}) or {}
    out = set()
    for cat in block.values():
        out.update(cat or [])
    return out


def load_macro_cfg() -> dict:
    return yaml.safe_load(open(MACRO_YAML)) or {}


# ─────────────────────────────── sourcing (Phase 1) ─────────────────────────────

def _parse_iso(s, fallback):
    try:
        dt = datetime.fromisoformat((s or "").replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return fallback


def _fa_to_item(d: dict, now, classifier) -> dict:
    """A batched FactSet document → ONE pool item (same shape as a Google item).

    Emitted once per documentID, not once per ticker that names it. The old per-ticker pull
    fetched a story like "Apple partnered with Alibaba" separately under AAPL and again under
    GOOGL, putting two copies of the same story into the pool. The tool hands back the full id
    list per document, so the primary ticker carries the item and `_fa_tickers` records every
    watchlist name it mentions.

    NB `_fa_tickers` is RECORDED BUT NOT YET CONSUMED. Everything downstream (clustering,
    classify, the ledger, the digest sections) still reads the scalar `ticker`, so a story
    naming four holdings surfaces once under its primary. That satisfies "no duplicate
    stories"; richer per-ticker routing would need the ledger and sections to read the list."""
    src = (d.get("source") or "StreetAccount").strip()
    tickers = d.get("tickers") or []
    return {
        "ticker": tickers[0] if tickers else "",
        "title": (d.get("headline") or "").strip(),
        "source": f"FactSet/{src}",
        "link": (d.get("url") or "").strip(),
        "published": _parse_iso(d.get("date"), now),
        "tier": "unknown",
        "_is_factset": True,
        "_fa_sentiment": d.get("sentiment") or "Neutral",
        "_fa_tickers": tickers,
        "_fa_doc_id": d.get("documentID") or "",
    }


def fetch_one(ident, window, now, classifier):
    """Pull Google RSS for one identity. Returns (items, g_status).

    FactSet is no longer fetched here — it is pulled once for the whole universe by
    fetch_factset_batch below. Google RSS stays per-identity because its RSS endpoint takes
    one query at a time."""
    items, g_status = [], None
    try:
        g_items, g_status = google_rss.fetch(ident.ticker, ident.google, window, now, classifier)
        items.extend(g_items)
    except Exception as e:  # noqa: BLE001 — per-source isolation
        g_status = f"error: {type(e).__name__}: {e}"
    return items, g_status


def fetch_factset_batch(idents, window, now, classifier):
    """Pull FactSet for the WHOLE universe in a handful of calls. Returns (items, failed).

    Replaces one `claude -p` per ticker (~87 sessions/run, ~800 calls and ~8M billed tokens a
    day — 93% of all news-pipeline spend) with one session per 30-ticker chunk. The `ids`
    argument accepts up to 100 identifiers and post-filters a single shared similarity search,
    so this is lossless: a ticker queried alone returns exactly the documentIDs it gets inside
    a batch (verified live 2026-08-14 on AAPL/INTC over a 24h window)."""
    runner = factset_news.make_runner(now, REPO_ROOT)
    docs, failed = factset_news.fetch_batch(idents, window, runner)
    items = [it for it in (_fa_to_item(d, now, classifier) for d in docs)
             if it["title"] and it["ticker"]]
    return items, failed


# ─────────────────────────── dedup + ledger (Phase 1b) ──────────────────────────

def item_hash(source: str, title: str) -> str:
    """sha256(source + title) — the dedup key (spec: headline-based; no body available)."""
    return hashlib.sha256(f"{(source or '').strip()}\n{(title or '').strip()}".encode()).hexdigest()[:16]


def load_ledger(now):
    """{hash: {first_surfaced_ts, tickers}} pruned to LEDGER_PRUNE_HOURS. Reads the extended
    item-hash schema (`h`) AND legacy cluster-hash entries (`cluster_hash`) — same file."""
    seen = {}
    if not os.path.exists(LEDGER_PATH):
        return seen
    cutoff = now - timedelta(hours=LEDGER_PRUNE_HOURS)
    with open(LEDGER_PATH) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                h = e.get("h") or e.get("cluster_hash")
                ts = datetime.fromisoformat(e["first_surfaced_ts"])
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
            if not h or ts < cutoff:
                continue
            seen[h] = {"first_surfaced_ts": ts, "tickers": e.get("tickers", [])}
    return seen


def rewrite_ledger(seen):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as fh:
        for h, v in seen.items():
            fh.write(json.dumps({
                "h": h,
                "first_surfaced_ts": v["first_surfaced_ts"].isoformat(),
                "tickers": v["tickers"],
            }) + "\n")
    os.replace(tmp, LEDGER_PATH)


def dedup_pool(pool, seen, now):
    """Drop items whose sha256(source+title) was surfaced within STALE_HOURS. Returns
    (kept_items, suppressed_count). Each kept item is annotated with its `_h`."""
    stale_cutoff = now - timedelta(hours=STALE_HOURS)
    kept, suppressed = [], 0
    for it in pool:
        h = item_hash(it["source"], it["title"])
        it["_h"] = h
        prev = seen.get(h)
        if prev and prev["first_surfaced_ts"] >= stale_cutoff:
            suppressed += 1
            continue
        kept.append(it)
    return kept, suppressed


# ─────────────────────────────── clustering (Phase 1c) ──────────────────────────

def cluster_pool(items, classifier):
    """Global near-duplicate clustering over the merged pool; attach strongest FactSet
    sentiment to each cluster that contains a FactSet item."""
    clusters = cluster_items(items, classifier)
    rank = {"Very Negative": 2, "Very Positive": 2, "Negative": 1, "Positive": 1, "Neutral": 0}
    for c in clusters:
        best, best_r = None, -1
        for it in c.items:
            if it.get("_is_factset"):
                s = it.get("_fa_sentiment") or "Neutral"
                if rank.get(s, 0) > best_r:
                    best, best_r = s, rank.get(s, 0)
        if best is not None:
            c._fa_sentiment = best
    return clusters


# ─────────────────────────── routing + rendering (Phase 4) ──────────────────────

def _cluster_urls(cluster, cap=4):
    urls = []
    for it in sorted(cluster.items, key=lambda x: x["published"], reverse=True):
        u = (it.get("link") or "").strip()
        if u and u not in urls:
            urls.append(u)
        if len(urls) >= cap:
            break
    return urls


def route(survivors):
    """survivors: list of (cluster, Classification, Summary), ALREADY IN RANK ORDER. Route each to
    ONE section by the highest-priority pass it hits: Company > Themes > Macro.

    Order is PRESERVED, not recomputed. This used to sort each section by (confidence, volume) —
    which as of the 2026-08-19 selection pass would silently discard the editorial ranking and
    restore the ordering that put four near-duplicate SK Hynix clusters in the top six slots.
    Both signals are measured dead ends anyway (106 of 262 items were conf=high; only 4 of those
    had volume >= 3). rank.py owns ordering now; route only bins."""
    # Priority for a no-ticker story: Macro > Themes. A macro print (CPI/PCE/Fed) often also
    # carries an incidental theme tag (e.g. fed_policy_tech); it belongs in Macro, where the
    # PM looks for top-down signal — not buried in Themes.
    company, themes, macro = [], [], []
    for c, cls, summ in survivors:
        if cls.materiality:
            company.append((c, cls, summ))
        elif cls.macro:
            macro.append((c, cls, summ))
        elif cls.themes:
            themes.append((c, cls, summ))
    return company, themes, macro


def _render_item(c, cls, summ, lines):
    head = (summ.headline or c.headline).strip()
    tag = ", ".join(cls.materiality) if cls.materiality else (
        ", ".join(cls.themes) if cls.themes else ", ".join(cls.macro) or "—")
    lines.append(f"{tag} — {head}")
    for b in summ.bullets:
        lines.append(f"    • {b}")
    if summ.why_it_matters:
        lines.append(f"    why: {summ.why_it_matters}")
    lens = " ".join(f"[{x}]" for x in (summ.lens_tags or cls.lens_hits))
    fa = f" · FactSet {getattr(c, '_fa_sentiment', '')}" if getattr(c, "_fa_sentiment", None) else ""
    srcs = ", ".join(sorted(c.sources)[:5])
    lines.append(f"    {lens} · {c.volume} outlet{'s' if c.volume != 1 else ''}: {srcs}{fa} · conf={cls.confidence}")
    urls = _cluster_urls(c)
    if urls:
        lines.append(f"    → {urls[0]}")


def render_sections(company, themes, macro, mode, now_local, banners, suppressed, failures,
                    dropped_cap, n_survivors=None, n_filed=0, filed=True):
    date_str = now_local.strftime("%Y-%m-%d")
    n = len(company) + len(themes) + len(macro)
    # No silent caps (same convention as dropped_cap): if selection trimmed the pool, SAY SO in the
    # header, not only in the footer — the count is the first thing the operator reads.
    head = f"{n} stories · {len(company)} company · {len(themes)} thematic · {len(macro)} macro"
    if n_survivors and n_survivors > n:
        head = f"top {n} of {n_survivors} · {len(company)} company · {len(themes)} thematic · {len(macro)} macro"
    lines = [
        f"NEWS FLOW — {date_str} ({mode})",
        "=" * 40,
        head,
    ]
    for b in banners:
        lines.append(f"⚠ {b}")
    lines.append("")

    for title, bucket in (("COMPANY", company), ("THEMES", themes), ("MACRO", macro)):
        lines.append(title)
        lines.append("-" * len(title))
        if not bucket:
            lines.append("(none)")
        for c, cls, summ in bucket:
            _render_item(c, cls, summ, lines)
            lines.append("")
        if bucket:
            lines.pop()  # trailing blank
        lines.append("")

    lines.append("·" * 60)
    lines.append("Sources: Google News RSS (breadth) + FactSet ALL_NEWS (quality/sentiment). "
                 "Classifier: claude -p 3-pass (materiality/themes/macro).")
    if suppressed:
        lines.append(f"Deduped {suppressed} item(s) already surfaced within {STALE_HOURS}h (state ledger).")
    if n_survivors and n_survivors > n:
        lines.append(
            f"Showing the top {n} of {n_survivors} stories that passed materiality triage "
            f"(editorial rank: tier → estimate-changing → novelty → cross-read; sell-side last; "
            f"max {rank.MAX_PER_TICKER} per ticker). "
            + (f"The other {n_survivors - n} are filed to notes/news + pg (headline, tickers, "
               f"themes, sources — not summarized) and are searchable there."
               if (filed and n_filed) else "The remainder is not filed this run."))
    if dropped_cap:
        lines.append(f"NOTE: {dropped_cap} lowest-volume cluster(s) dropped by the MAX_CLUSTERS={MAX_CLUSTERS} cap.")
    if failures:
        lines.append(f"Coverage notes ({len(failures)} fetch failure(s)):")
        for f in failures[:20]:
            lines.append(f"  - {f}")
        if len(failures) > 20:
            lines.append(f"  … +{len(failures) - 20} more")
    else:
        lines.append("Coverage: all sources fetched cleanly.")
    return "\n".join(lines)


# ─────────────────────────── filing to notes/news + pg (Phase 4) ─────────────────

def _slug(s, maxlen=60):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s[:maxlen].strip("-")) or "story"


def build_news_note(c, cls, summ, date_str) -> str:
    tickers = list(cls.materiality)
    fm = {
        "doc_type": "news",
        "source": "news",
        "tickers": tickers,
        "themes": list(cls.themes),
        "macro_signals": list(cls.macro),
        "lens_tags": list(summ.lens_tags or cls.lens_hits),
        "confidence": cls.confidence,
        "rationale": cls.rationale,
        "source_urls": _cluster_urls(c, cap=8),
        "cluster_headlines": sorted({it["title"] for it in c.items}),
        "factset_sentiment": getattr(c, "_fa_sentiment", None) or "",
        "published_date": max(c.items, key=lambda x: x["published"])["published"].date().isoformat(),
        "ingestion_date": date_str,
        "extraction_source": "v3 news-flow channel (news_digest.py), claude -p 3-pass classifier + summarizer",
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    # Use ## (not #) so the v3 chunker's section detector (## / ### / **bold** cascade)
    # segments the note into a parent + children — a single # H1 yields ZERO sections
    # and therefore zero chunks (note would land un-retrievable in pg).
    headline = (summ.headline or c.headline).strip()
    body = [f"## {headline}", ""]
    if summ.why_it_matters:
        body += [summ.why_it_matters, ""]
    for b in summ.bullets:
        body.append(f"- {b}")
    return f"---\n{front}---\n\n" + "\n".join(body) + "\n"


def build_headline_note(c, cls, date_str) -> str:
    """A note for a survivor that was NOT selected for the digest (2026-08-19 top-N cap).

    It carries everything the classifier already produced — tickers, themes, macro signals,
    every cluster headline, source URLs — but no LLM-written bullets, because the summarizer no
    longer runs on it. That keeps the pg corpus at full recall for ~$0 while the emailed digest
    stays at the operator's story limit. `summarized: false` marks the difference so a later
    consumer can tell a headline note from a full one."""
    fm = {
        "doc_type": "news",
        "source": "news",
        "tickers": list(cls.materiality),
        "themes": list(cls.themes),
        "macro_signals": list(cls.macro),
        "lens_tags": list(cls.lens_hits),
        "confidence": cls.confidence,
        "rationale": cls.rationale,
        "summarized": False,
        "source_urls": _cluster_urls(c, cap=8),
        "cluster_headlines": sorted({it["title"] for it in c.items}),
        "factset_sentiment": getattr(c, "_fa_sentiment", None) or "",
        "published_date": max(c.items, key=lambda x: x["published"])["published"].date().isoformat(),
        "ingestion_date": date_str,
        "extraction_source": "v3 news-flow channel (news_digest.py), classified but below the "
                             "digest cut — headline-only note, not summarized",
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    # ## (not #) for the same reason as build_news_note: a lone H1 yields zero chunks in pg.
    body = [f"## {c.headline.strip()}", ""]
    if cls.rationale:
        body += [cls.rationale, ""]
    for h in sorted({it["title"] for it in c.items}):
        body.append(f"- {h}")
    return f"---\n{front}---\n\n" + "\n".join(body) + "\n"


def note_path(c, date_str):
    """Deterministic per story per day (date + slug + short cluster-hash) → re-filing overwrites
    the same file, so multiple runs in a day don't create duplicate notes/pg chunks.

    The slug comes from the CLUSTER headline, never the summarizer's rewritten one. Since the
    2026-08-19 story cap a cluster can be filed as a full note in one run (it made the top 30) and
    a headline-only note in another (it didn't) — and the brief re-sources what premarket already
    saw. Slugging from the summary would give those two runs two different filenames for the SAME
    cluster hash, i.e. two files and two pg documents for one story, breaking exactly the
    idempotence this function exists to provide."""
    return os.path.join(NOTES_NEWS_DIR, f"{date_str}-{_slug(c.headline)}-{c.hash[:8]}.md")


def file_notes(summarized, unsummarized, date_str):
    """Write + ingest one note per survivor. Returns (n_written, n_ingested, n_headline_only).

    `summarized` are (cluster, Classification, Summary) — the digest's selected stories, filed in
    full. `unsummarized` are (cluster, Classification) that ranked below the cut: filed as
    headline-only notes so the pg corpus keeps full recall even though the summarizer skipped
    them. Isolated per note — one failure never aborts filing."""
    sys.path.insert(0, CHUNKING_DIR)
    os.makedirs(NOTES_NEWS_DIR, exist_ok=True)
    if not os.environ.get("CHUNK_STORE_BACKEND"):
        os.environ["CHUNK_STORE_BACKEND"] = "pg"
    from ingest import ingest  # noqa: E402
    from pathlib import Path
    written = ingested = headline_only = 0
    jobs = ([(c, cls, summ, False) for c, cls, summ in summarized]
            + [(c, cls, None, True) for c, cls in unsummarized])
    for c, cls, summ, is_headline in jobs:
        try:
            p = note_path(c, date_str)
            with open(p, "w") as fh:
                fh.write(build_headline_note(c, cls, date_str) if is_headline
                         else build_news_note(c, cls, summ, date_str))
            written += 1
            headline_only += int(is_headline)
            ingest([Path(p)])
            ingested += 1
        except Exception as e:  # noqa: BLE001 — one note must not abort filing
            logger.warning("filing failed for cluster %s: %s: %s", c.hash, type(e).__name__, e)
    return written, ingested, headline_only


# ─────────────────────────────── orchestration ──────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="v3 news-flow / IR channel (merged-pool 3-pass)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--premarket", action="store_true")
    g.add_argument("--postmarket", action="store_true")
    g.add_argument("--brief", action="store_true", help="overnight run for the combined 03:00 brief "
                   "(writes report_news artifact + files pg; NO email; ledger read-only)")
    ap.add_argument("--dry-run", action="store_true", help="print to stdout; no email/ledger/pg")
    ap.add_argument("--no-factset", action="store_true", help="Google-only (skip FactSet)")
    ap.add_argument("--max-tickers", type=int, default=0, help="cap identities sourced (testing)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stderr)])

    mode = "premarket" if args.premarket else "postmarket" if args.postmarket else "brief"
    window = POSTMARKET_WINDOW_HOURS if args.postmarket else PREMARKET_WINDOW_HOURS
    use_factset = not args.no_factset
    now = datetime.now(timezone.utc)
    now_local = datetime.now()
    date_str = now_local.strftime("%Y-%m-%d")

    identities = load_identities()
    classifier = load_classifier()
    ticker_names = load_universe_ticker_names(identities)
    ticker_tiers = load_ticker_tiers()
    valid_themes = load_valid_themes()
    macro_cfg = load_macro_cfg()
    src_ids = list(identities.items())
    if args.max_tickers:
        src_ids = src_ids[:args.max_tickers]
    logger.info("run start: mode=%s window=%dh identities=%d universe=%d factset=%s dry_run=%s",
                mode, window, len(src_ids), len(ticker_names), use_factset, args.dry_run)

    # ── Phase 1: merged sourcing ──
    pool, failures = [], []
    g_ok = fa_ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=FACTSET_CONCURRENCY) as ex:
        futs = {ex.submit(fetch_one, ident, window, now, classifier): tk
                for tk, ident in src_ids}
        for fut in concurrent.futures.as_completed(futs):
            tk = futs[fut]
            items, g_status = fut.result()
            pool.extend(items)
            if g_status == "ok":
                g_ok += 1
            elif g_status and g_status.startswith("error"):
                failures.append(f"{tk}: Google — {g_status}")

    # FactSet: one batched pass for the whole universe (was one claude -p per ticker).
    fa_items = []
    if use_factset:
        idents = [ident for _tk, ident in src_ids]
        fa_items, fa_failed = fetch_factset_batch(idents, window, now, classifier)
        pool.extend(fa_items)
        fa_ok = len(idents) - len(fa_failed)
        for tk in sorted(fa_failed):
            failures.append(f"{tk}: FactSet — error: chunk and per-ticker retry both failed")
    logger.info("sourced pool=%d items (google_ok=%d factset_ok=%d factset_docs=%d)",
                len(pool), g_ok, fa_ok, len(fa_items))

    google_down = g_ok == 0
    factset_down = use_factset and fa_ok == 0
    banners = []
    if not use_factset:
        banners.append("FactSet channel disabled (--no-factset): Google-only.")
    elif factset_down:
        banners.append("FactSet unavailable this run: Google-only digest.")
    if google_down:
        banners.append("Google News unavailable this run.")
    if google_down and (not use_factset or factset_down):
        logger.error("both channels down — aborting")
        sys.exit(1)

    # ── Phase 1b: dedup vs ledger ──
    seen = load_ledger(now)
    kept, suppressed = dedup_pool(pool, seen, now)
    logger.info("dedup: kept=%d suppressed=%d", len(kept), suppressed)

    # ── Phase 1c: cluster ──
    clusters = cluster_pool(kept, classifier)
    n_clustered = len(clusters)

    # ── Phase 1d: pre-LLM volume reduction (NO claude -p) — filter-first, then merge ──
    # Lever 2: drop boilerplate CATEGORIES (13F/analyst-stub/listicle/price-stub); FactSet exempt.
    clusters, filt_reasons = pre_filter.filter_clusters(clusters, logger=logger)
    n_filtered = len(clusters)
    # Lever 1: collapse event-fragments (name-stripped content-signature, T=0.3). MUST be after the
    # filter — filter-first removes the template-spam that would otherwise over-merge.
    clusters = merge.merge_clusters(clusters, ticker_names, logger=logger)
    n_merged = len(clusters)

    # MAX_CLUSTERS is now a high safety BACKSTOP (the levers do the real cleanup). It drops the
    # lowest-volume excess; merged real-events sort UP (higher volume), boilerplate is already gone,
    # so the surviving top-N is higher-signal than before. Kept at 300 (lowering re-introduces the
    # material-single-source FN the tier/volume gate died on — see the quota-budget memory).
    dropped_cap = 0
    if len(clusters) > MAX_CLUSTERS:
        clusters.sort(key=lambda c: (c.volume, c.representative["published"]), reverse=True)
        dropped_cap = len(clusters) - MAX_CLUSTERS
        clusters = clusters[:MAX_CLUSTERS]
        logger.warning("cluster cap: kept %d, dropped %d (MAX_CLUSTERS=%d)",
                       MAX_CLUSTERS, dropped_cap, MAX_CLUSTERS)
    logger.info("clustered %d → filtered %d (−%d boilerplate) → merged %d → %d to classify",
                n_clustered, n_filtered, n_clustered - n_filtered, n_merged, len(clusters))

    # ── Phase 2: LLM classify (with the Lever 3 verdict cache) ──
    # Self-populating per-day content-hash cache: within a run window, the brief/postmarket reuse the
    # verdicts premarket already produced instead of re-calling claude -p on the same clusters. A hash
    # hit is safe (same tokens = same story); a miss just classifies. dry-run does not use the cache.
    cache = None
    if not args.dry_run:
        vc_path = os.path.join(REPO_ROOT, "state", f"news_verdict_cache_{date_str}.json")
        vtag = verdict_cache.build_version_tag(ticker_names, valid_themes, macro_cfg)
        cache = verdict_cache.VerdictCache(vc_path, vtag)
    classifications, c_cost, unclassified = classify_llm.classify_clusters(
        clusters, macro_cfg, ticker_names, valid_themes, REPO_ROOT,
        logger=logger, cache=cache, now=now)
    survivors_cc = [(c, classifications[c.hash]) for c in clusters
                    if c.hash in classifications and classifications[c.hash].is_survivor]
    logger.info("classified: %d verdicts, %d survivors, %d unclassified (cost=$%.4f)",
                len(classifications), len(survivors_cc), len(unclassified), c_cost)

    # ── Phase 2b: editorial selection (operator cap, 2026-08-19) ──
    # Placed BEFORE summarize deliberately: the summarizer used to run over every survivor
    # (~260 items, ~$3.2/run) and is now the single largest saving in the pipeline. It also
    # applies the max-N-per-ticker rule that stops one event (SK Hynix's buyback: 26 of 262
    # items on 2026-08-19) from occupying the whole brief.
    selected, r_cost, rank_note, ranked_ok = rank.select_top(
        survivors_cc, REPO_ROOT, limit=rank.DIGEST_LIMIT, tier_map=ticker_tiers, logger=logger)
    if rank_note:
        banners.append(rank_note)
    selected_cc = [(c, cls) for c, cls, _reason in selected]
    sel_hashes = {c.hash for c, _cls in selected_cc}
    below_cut = [(c, cls) for c, cls in survivors_cc if c.hash not in sel_hashes]
    logger.info("selection: %d survivors → %d for the digest, %d below the cut (cost=$%.4f)",
                len(survivors_cc), len(selected_cc), len(below_cut), r_cost)

    # ── Phase 3: summarize the SELECTED stories only ──
    summaries, s_cost, unsummarized = summarize.summarize_survivors(
        selected_cc, REPO_ROOT, logger=logger)
    survivors = [(c, cls, summaries[c.hash]) for c, cls in selected_cc if c.hash in summaries]
    logger.info("summarized: %d items (%d unsummarized, cost=$%.4f)",
                len(survivors), len(unsummarized), s_cost)
    if unsummarized:
        banners.append(f"{len(unsummarized)} selected stor{'y' if len(unsummarized) == 1 else 'ies'} "
                       f"not summarized (claude -p quota/error) — omitted from digest, see log")

    # ── Phase 4: route + render ──
    company, themes, macro = route(survivors)
    section = render_sections(company, themes, macro, mode, now_local, banners,
                              suppressed, failures, dropped_cap,
                              n_survivors=len(survivors_cc), n_filed=len(below_cut),
                              filed=not args.dry_run)

    # persist a log artifact (gitignored audit trail)
    artifact = os.path.join(REPO_ROOT, "logs",
                            f"news_digest_{mode}_{now_local.strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(artifact, "w") as fh:
            fh.write(section + "\n")
        logger.info("digest body saved: %s", artifact)
    except OSError as e:
        logger.warning("could not write artifact: %s", e)

    # ── Phase 4b: file notes/news + pg (live only) ──
    if not args.dry_run and (survivors or below_cut):
        written, ingested, headline_only = file_notes(survivors, below_cut, date_str)
        logger.info("filed notes/news: %d written (%d full, %d headline-only), %d ingested to pg",
                    written, written - headline_only, headline_only, ingested)

    # ── report_news artifact for the combined brief (all live modes; brief is the one that
    #    matters, but refreshing in every mode keeps combine_and_send's date lookup satisfied) ──
    if not args.dry_run:
        report_news = os.path.join(REPO_ROOT, "logs", f"report_news_{date_str}.txt")
        try:
            with open(report_news, "w") as fh:
                fh.write(section + "\n")
            logger.info("report_news written: %s", report_news)
        except OSError as e:
            logger.warning("could not write report_news: %s", e)

    # ── ledger write: premarket/postmarket only (brief is read-only; dry-run never writes) ──
    if not args.dry_run and mode in ("premarket", "postmarket"):
        for it in kept:
            h = it["_h"]
            if h not in seen:
                seen[h] = {"first_surfaced_ts": now, "tickers": [it["ticker"]]}
            elif it["ticker"] not in seen[h]["tickers"]:
                seen[h]["tickers"].append(it["ticker"])
        rewrite_ledger(seen)
        logger.info("ledger updated: %d entries", len(seen))

    logger.info("run done: mode=%s stories=%d/%d survivors unclassified=%d google_down=%s "
                "factset_down=%s suppressed=%d cost=$%.4f (classify=$%.4f rank=$%.4f "
                "summarize=$%.4f)", mode, len(survivors), len(survivors_cc), len(unclassified),
                google_down, factset_down, suppressed, c_cost + r_cost + s_cost,
                c_cost, r_cost, s_cost)

    # ── delivery ──
    if args.dry_run:
        print(section)
    elif mode in ("premarket", "postmarket"):
        label = "Pre-market" if mode == "premarket" else "Post-market"
        subject = f"{label} news digest — {date_str}"
        from newsdigest.email_send import send
        status = send(subject, section)
        logger.info("email sent (status %s)", status)
    else:  # brief — no email; report_news already written
        logger.info("brief mode: no email; report_news is the deliverable")

    # ── fail loud on unclassified OR unsummarized clusters ───────────────────────────
    # Filing/reporting/delivery above already ran, so partial results are saved. But a cluster
    # that was classified-material yet left unclassified (claude -p down at classify) OR
    # unsummarized (claude -p down at summarize — the 2026-07-21 session-limit 429) is a
    # PROCESSING FAILURE, NOT a below-bar drop — exit non-zero so alert_on_failure.sh fires.
    # Guardrail against silent under-reporting (2026-07-08 classify drop / 2026-07-21 summarize
    # drop). NOTE: this only alerts if the invocation is wrapped by alert_on_failure.sh (see
    # run_daily.sh); a bare `... --brief || true` would swallow it.
    # A FAILED ranking joins this set as of the 2026-08-19 story cap — but only a true fallback
    # (`ranked_ok` False), not a sharded recovery, which still produced real editorial ranking and
    # only warrants the banner. Before the cap, ordering was
    # cosmetic — every survivor was rendered anyway, so a bad sort cost nothing. Now the ranking
    # DECIDES which 30 of ~260 the operator ever sees, so falling back to the deterministic order
    # is a degraded product, not a degraded nicety. In --brief mode there is no email at all, so
    # the banner alone would be near-invisible; the non-zero exit is what reaches the operator.
    if unclassified or unsummarized or not ranked_ok:
        logger.error("run INCOMPLETE: %d unclassified + %d unsummarized cluster(s)%s (processing "
                     "failure, not below-bar drops) — exiting non-zero to trigger alerting",
                     len(unclassified), len(unsummarized),
                     "" if ranked_ok else "; ranking degraded to deterministic order")
        sys.exit(1)


if __name__ == "__main__":
    main()
