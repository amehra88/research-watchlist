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
    → summarize survivors (>=1 pass hit)                     [batched]
    → route into Company / Themes / Macro sections
    → render brief + (live) file notes/news/{date}-{slug}.md → chunk into pg

Modes:
  --premarket / --postmarket   full digest, EMAIL, writes ledger + files pg (standalone, as before)
  --brief                      overnight run for the 03:00 combined brief: writes
                               report_news_{date}.txt + files pg, NO email, and reads the
                               ledger READ-ONLY (never writes it) so it can't starve the
                               standalone emails' dedup.
  --dry-run                    print to stdout; no email, no ledger write, no pg filing.
  --no-factset                 Google-only (skip the FactSet channel).

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
    FACTSET_CONCURRENCY, STALE_HOURS, LEDGER_PRUNE_HOURS,
)
from newsdigest.identity import load_identities          # noqa: E402
from newsdigest.sources import load_classifier           # noqa: E402
from newsdigest import google_rss, factset_news          # noqa: E402
from newsdigest.cluster import cluster_items             # noqa: E402
from newsdigest import classify_llm, summarize           # noqa: E402

LOG_PATH = os.path.join(REPO_ROOT, "logs", "news_digest.log")
LEDGER_PATH = os.path.join(REPO_ROOT, "state", "news_digest_seen.jsonl")
FACTSET_CACHE_DIR = os.path.join(REPO_ROOT, "state", "factset_cache")
FACTSET_CACHE_DRYRUN_DIR = os.path.join(REPO_ROOT, "state", "factset_cache_dryrun")
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


def _fa_to_item(a: dict, ident, now, classifier) -> dict:
    """A FactSet article → a pool item dict (same shape as a Google item), sentiment attached."""
    src = (a.get("source") or "StreetAccount").strip()
    return {
        "ticker": ident.ticker,
        "title": (a.get("headline") or "").strip(),
        "source": f"FactSet/{src}",
        "link": (a.get("url") or "").strip(),
        "published": _parse_iso(a.get("date"), now),
        "tier": "unknown",
        "_is_factset": True,
        "_fa_sentiment": a.get("sentiment") or "Neutral",
    }


def fetch_one(ident, window, now, classifier, use_factset, cache_dir, use_cache):
    """Pull Google RSS (+ FactSet) for one identity. Returns (items, g_status, fa_status)."""
    items, g_status, fa_status = [], None, "disabled"
    try:
        g_items, g_status = google_rss.fetch(ident.ticker, ident.google, window, now, classifier)
        items.extend(g_items)
    except Exception as e:  # noqa: BLE001 — per-source isolation
        g_status = f"error: {type(e).__name__}: {e}"
    if use_factset:
        try:
            fa_articles, fa_status = factset_news.fetch(
                ident.name, ident.factset_id, window, now, cache_dir, REPO_ROOT, use_cache=use_cache)
            for a in fa_articles:
                it = _fa_to_item(a, ident, now, classifier)
                if it["title"]:
                    items.append(it)
        except Exception as e:  # noqa: BLE001
            fa_status = f"error: {type(e).__name__}: {e}"
    return items, g_status, fa_status


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

_CONF_RANK = {"high": 3, "medium": 2, "low": 1}


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
    """survivors: list of (cluster, Classification, Summary). Route each to ONE section by
    the highest-priority pass it hits: Company > Themes > Macro. Returns 3 sorted lists."""
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
    keyf = lambda t: (_CONF_RANK.get(t[1].confidence, 0), t[0].volume)
    company.sort(key=keyf, reverse=True)
    themes.sort(key=keyf, reverse=True)
    macro.sort(key=keyf, reverse=True)
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


def render_sections(company, themes, macro, mode, now_local, banners, suppressed, failures, dropped_cap):
    date_str = now_local.strftime("%Y-%m-%d")
    n = len(company) + len(themes) + len(macro)
    lines = [
        f"NEWS FLOW — {date_str} ({mode})",
        "=" * 40,
        f"{n} stories · {len(company)} company · {len(themes)} thematic · {len(macro)} macro",
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


def note_path(c, summ, date_str):
    # deterministic per story per day (date + slug + short cluster-hash) → re-filing overwrites
    # the same file, so multiple runs in a day don't create duplicate notes/pg chunks.
    return os.path.join(NOTES_NEWS_DIR, f"{date_str}-{_slug(summ.headline or c.headline)}-{c.hash[:8]}.md")


def file_notes(survivors, date_str):
    """Write + ingest a note per survivor. Returns (n_written, n_ingested). Isolated per note."""
    sys.path.insert(0, CHUNKING_DIR)
    os.makedirs(NOTES_NEWS_DIR, exist_ok=True)
    if not os.environ.get("CHUNK_STORE_BACKEND"):
        os.environ["CHUNK_STORE_BACKEND"] = "pg"
    from ingest import ingest  # noqa: E402
    from pathlib import Path
    written = ingested = 0
    for c, cls, summ in survivors:
        try:
            p = note_path(c, summ, date_str)
            with open(p, "w") as fh:
                fh.write(build_news_note(c, cls, summ, date_str))
            written += 1
            ingest([Path(p)])
            ingested += 1
        except Exception as e:  # noqa: BLE001 — one note must not abort filing
            logger.warning("filing failed for cluster %s: %s: %s", c.hash, type(e).__name__, e)
    return written, ingested


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
    use_cache = args.dry_run
    cache_dir = FACTSET_CACHE_DRYRUN_DIR if args.dry_run else FACTSET_CACHE_DIR
    now = datetime.now(timezone.utc)
    now_local = datetime.now()
    date_str = now_local.strftime("%Y-%m-%d")

    identities = load_identities()
    classifier = load_classifier()
    ticker_names = load_universe_ticker_names(identities)
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
        futs = {ex.submit(fetch_one, ident, window, now, classifier, use_factset, cache_dir, use_cache): tk
                for tk, ident in src_ids}
        for fut in concurrent.futures.as_completed(futs):
            tk = futs[fut]
            items, g_status, fa_status = fut.result()
            pool.extend(items)
            if g_status == "ok":
                g_ok += 1
            elif g_status and g_status.startswith("error"):
                failures.append(f"{tk}: Google — {g_status}")
            if fa_status in ("ok", "cached", "empty"):
                fa_ok += 1
            elif fa_status and fa_status.startswith("error"):
                failures.append(f"{tk}: FactSet — {fa_status}")
    logger.info("sourced pool=%d items (google_ok=%d factset_ok=%d)", len(pool), g_ok, fa_ok)

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
    dropped_cap = 0
    if len(clusters) > MAX_CLUSTERS:
        clusters.sort(key=lambda c: (c.volume, c.representative["published"]), reverse=True)
        dropped_cap = len(clusters) - MAX_CLUSTERS
        clusters = clusters[:MAX_CLUSTERS]
        logger.warning("cluster cap: kept %d, dropped %d (MAX_CLUSTERS=%d)",
                       MAX_CLUSTERS, dropped_cap, MAX_CLUSTERS)
    logger.info("clustered: %d clusters", len(clusters))

    # ── Phase 2: LLM classify ──
    classifications, c_cost, unclassified = classify_llm.classify_clusters(
        clusters, macro_cfg, ticker_names, valid_themes, REPO_ROOT, logger=logger)
    survivors_cc = [(c, classifications[c.hash]) for c in clusters
                    if c.hash in classifications and classifications[c.hash].is_survivor]
    logger.info("classified: %d verdicts, %d survivors, %d unclassified (cost=$%.4f)",
                len(classifications), len(survivors_cc), len(unclassified), c_cost)

    # ── Phase 3: summarize survivors ──
    summaries, s_cost, unsummarized = summarize.summarize_survivors(
        survivors_cc, REPO_ROOT, logger=logger)
    survivors = [(c, cls, summaries[c.hash]) for c, cls in survivors_cc if c.hash in summaries]
    logger.info("summarized: %d items (%d unsummarized, cost=$%.4f)",
                len(survivors), len(unsummarized), s_cost)
    if unsummarized:
        banners.append(f"{len(unsummarized)} classified stor{'y' if len(unsummarized) == 1 else 'ies'} "
                       f"not summarized (claude -p quota/error) — omitted from digest, see log")

    # ── Phase 4: route + render ──
    company, themes, macro = route(survivors)
    section = render_sections(company, themes, macro, mode, now_local, banners,
                              suppressed, failures, dropped_cap)

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
    if not args.dry_run and survivors:
        written, ingested = file_notes(survivors, date_str)
        logger.info("filed notes/news: %d written, %d ingested to pg", written, ingested)

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

    logger.info("run done: mode=%s stories=%d unclassified=%d google_down=%s factset_down=%s "
                "suppressed=%d cost=$%.4f", mode, len(survivors), len(unclassified),
                google_down, factset_down, suppressed, c_cost + s_cost)

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
    if unclassified or unsummarized:
        logger.error("run INCOMPLETE: %d unclassified + %d unsummarized cluster(s) (processing "
                     "failure, not below-bar drops) — exiting non-zero to trigger alerting",
                     len(unclassified), len(unsummarized))
        sys.exit(1)


if __name__ == "__main__":
    main()
