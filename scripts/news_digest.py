#!/usr/bin/env python3
"""
news_digest — dual-source pre/post-market news digest entrypoint (spec §9).

  python3 scripts/news_digest.py --premarket          # build + email (cron mode, §8)
  python3 scripts/news_digest.py --premarket --dry-run # build + print to stdout, NO email, NO ledger write
  python3 scripts/news_digest.py --premarket --no-factset  # Google-only (skip the FactSet channel)

Per-ticker isolation: one ticker failing never aborts the run (§10). Degraded
coverage SENDS ANYWAY with a banner; only a both-channels-down run exits non-zero.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from newsdigest import (  # noqa: E402
    PREMARKET_WINDOW_HOURS, POSTMARKET_WINDOW_HOURS,
    FACTSET_CONCURRENCY, STALE_HOURS, LEDGER_PRUNE_HOURS,
)
from newsdigest.identity import load_identities          # noqa: E402
from newsdigest.sources import load_classifier           # noqa: E402
from newsdigest import google_rss, factset_news          # noqa: E402
from newsdigest import filter as nfilter                 # noqa: E402
from newsdigest.cluster import cluster_items, cluster_hash, normalize_tokens  # noqa: E402

LOG_PATH = os.path.join(REPO_ROOT, "logs", "news_digest.log")
LEDGER_PATH = os.path.join(REPO_ROOT, "state", "news_digest_seen.jsonl")
FACTSET_CACHE_DIR = os.path.join(REPO_ROOT, "state", "factset_cache")
FACTSET_CACHE_DRYRUN_DIR = os.path.join(REPO_ROOT, "state", "factset_cache_dryrun")  # v2: dry-run never touches prod cache

logger = logging.getLogger("news_digest")


# ─────────────────────────────── per-ticker work ────────────────────────────
def process_ticker(ident, window, now, classifier, use_factset, cache_dir, use_cache):
    out = {
        "ticker": ident.ticker, "g_status": None, "fa_status": "disabled",
        "verdicts": [], "factset_only": [], "error": None,
    }
    try:
        g_items, g_status = google_rss.fetch(ident.ticker, ident.google, window, now, classifier)
        out["g_status"] = g_status

        fa_articles, fa_status = [], "disabled"
        if use_factset:
            fa_articles, fa_status = factset_news.fetch(
                ident.name, ident.factset_id, window, now, cache_dir, REPO_ROOT,
                use_cache=use_cache,
            )
        out["fa_status"] = fa_status

        clusters = cluster_items(g_items, classifier)
        matched = set()
        verdicts = []
        for c in clusters:
            v = nfilter.classify(c, fa_articles, classifier, ident.name, ident.ticker)
            if v.factset_article:
                matched.add((v.factset_article.get("headline") or "").lower())
            if v.level in ("HIGH", "MEDIUM"):
                verdicts.append((c, v))
        out["verdicts"] = verdicts
        # FactSet-only stories (analyst desk picked up, not in Google) -> MEDIUM (§5a-medium)
        out["factset_only"] = [
            a for a in fa_articles if (a.get("headline") or "").lower() not in matched
        ]
    except Exception as e:  # noqa: BLE001 — per-ticker isolation (§10)
        out["error"] = f"{type(e).__name__}: {e}"
        logger.exception("ticker %s failed", ident.ticker)
    return out


# ─────────────────────────────── state ledger (§10) ─────────────────────────
def load_ledger(now):
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
                ts = datetime.fromisoformat(e["first_surfaced_ts"])
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
            if ts < cutoff:
                continue  # prune
            seen[e["cluster_hash"]] = {"first_surfaced_ts": ts, "tickers": e.get("tickers", [])}
    return seen


def rewrite_ledger(seen):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as fh:
        for h, v in seen.items():
            fh.write(json.dumps({
                "cluster_hash": h,
                "first_surfaced_ts": v["first_surfaced_ts"].isoformat(),
                "tickers": v["tickers"],
            }) + "\n")
    os.replace(tmp, LEDGER_PATH)


# ─────────────────────────────── rendering (§6) ─────────────────────────────
def _fmt_sources(sources, cap=5):
    s = sorted(sources)
    if len(s) <= cap:
        return ", ".join(s)
    return ", ".join(s[:cap]) + f" +{len(s) - cap} more"


def _vol_key(item):
    c, v = item
    return (c.volume, c.representative["published"])


def build_digest(results, mode, now_local, banners, suppressed=0):
    date_str = now_local.strftime("%Y-%m-%d")
    label = "Pre-market" if mode == "premarket" else "Post-market"
    subject = f"{label} news digest — {date_str}"

    high, medium = [], []         # (ticker, cluster, verdict)
    fa_high, fa_medium = [], []   # FactSet-only (ticker, article): v2 → HIGH unless templated boilerplate
    quiet, failures = [], []

    for r in results:
        t = r["ticker"]
        if r["error"]:
            failures.append(f"{t}: run error — {r['error']}")
        if (r["g_status"] or "").startswith("error"):
            failures.append(f"{t}: Google fetch failed — {r['g_status']}")
        if (r["fa_status"] or "").startswith("error"):
            failures.append(f"{t}: FactSet fetch failed — {r['fa_status']}")

        had = False
        for c, v in r["verdicts"]:
            had = True
            (high if v.level == "HIGH" else medium).append((t, c, v))
        for a in r["factset_only"]:
            had = True
            (fa_medium if nfilter.is_templated_preview(a.get("headline", "")) else fa_high).append((t, a))
        if not had and not r["error"]:
            quiet.append(t)

    high.sort(key=lambda x: _vol_key((x[1], x[2])), reverse=True)
    medium.sort(key=lambda x: _vol_key((x[1], x[2])), reverse=True)

    n_high_tickers = len({t for t, _, _ in high} | {t for t, _ in fa_high})
    lines = []
    lines.append(subject)
    lines.append("=" * len(subject))
    lines.append("")
    lines.append(
        f"{len(high) + len(fa_high)} high across {n_high_tickers} tickers · "
        f"{len(medium) + len(fa_medium)} medium · {len(quiet)} quiet"
    )
    for b in banners:
        lines.append(f"⚠ {b}")
    lines.append("")

    # ── HIGH ──
    lines.append("HIGH SIGNAL")
    lines.append("-" * 11)
    if not high:
        lines.append("(none)")
    for t, c, v in high:
        rep = c.representative
        fa = f" · {v.factset_status}" if v.factset_status else ""
        lines.append(f"{t} — {c.headline}")
        lines.append(f"    {c.volume} outlet{'s' if c.volume != 1 else ''} · {_fmt_sources(c.sources)}{fa} · [{v.reason}]")
        lines.append(f"    → {rep['link']}")
    for t, a in fa_high:
        sent = a.get("sentiment") or "Neutral"
        src = a.get("source") or "StreetAccount"
        lines.append(f"{t} — {a.get('headline','').strip()}")
        lines.append(f"    FactSet {src} · {sent} · [FactSet-only]")
        lines.append(f"    → {a.get('url','')}")
    lines.append("")

    # ── MEDIUM ──
    lines.append("MEDIUM SIGNAL")
    lines.append("-" * 13)
    if not medium and not fa_medium:
        lines.append("(none)")
    for t, c, v in medium:
        rep = c.representative
        fa = f" · {v.factset_status}" if v.factset_status else ""
        lines.append(f"{t} — {c.headline}  ({c.volume} outlet{'s' if c.volume != 1 else ''}{fa})  → {rep['link']}")
    for t, a in fa_medium:
        sent = a.get("sentiment") or "Neutral"
        url = a.get("url") or ""
        tail = f"  → {url}" if url else ""
        lines.append(f"{t} — {a.get('headline','').strip()}  (FactSet templated: {sent}){tail}")
    lines.append("")

    # ── QUIET ──
    if quiet:
        lines.append("QUIET")
        lines.append("-" * 5)
        lines.append(f"{', '.join(sorted(quiet))}  ({len(quiet)} tickers, no qualifying news)")
        lines.append("")

    # ── footer ──
    lines.append("·" * 60)
    lines.append(f"Sources: Google News RSS (breadth) + FactSet ALL_NEWS (quality/sentiment). Window: {('24h' if mode=='premarket' else '12h')}.")
    if suppressed:
        lines.append(f"Suppressed {suppressed} cluster(s) already surfaced within {STALE_HOURS}h (state ledger).")
    if failures:
        lines.append("Coverage notes (fetch failures — ticker omitted or partial):")
        for f in failures:
            lines.append(f"  - {f}")
    else:
        lines.append("Coverage: all tickers fetched cleanly.")

    return subject, "\n".join(lines)


# ─────────────────────────────── orchestration ──────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Dual-source pre/post-market news digest")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--premarket", action="store_true")
    g.add_argument("--postmarket", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print to stdout; no email, no ledger write")
    ap.add_argument("--no-factset", action="store_true", help="skip the FactSet channel (Google-only)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stderr)],
    )

    mode = "premarket" if args.premarket else "postmarket"
    window = PREMARKET_WINDOW_HOURS if args.premarket else POSTMARKET_WINDOW_HOURS
    use_factset = not args.no_factset
    # v2 cache policy: production cron ALWAYS fetches fresh (freshness > the old pre/post dedup);
    # dry-run uses a SEPARATE cache dir so testing never poisons the production cache.
    use_cache = args.dry_run
    cache_dir = FACTSET_CACHE_DRYRUN_DIR if args.dry_run else FACTSET_CACHE_DIR
    now = datetime.now(timezone.utc)
    now_local = datetime.now()

    identities = load_identities()
    classifier = load_classifier()
    logger.info("run start: mode=%s window=%dh tickers=%d factset=%s dry_run=%s",
                mode, window, len(identities), use_factset, args.dry_run)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=FACTSET_CONCURRENCY) as ex:
        futs = {ex.submit(process_ticker, ident, window, now, classifier,
                          use_factset, cache_dir, use_cache): tk
                for tk, ident in identities.items()}
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    # ── degraded-coverage detection (§10) ──
    g_ok = [r for r in results if r["g_status"] == "ok"]
    google_down = len(g_ok) == 0
    factset_down = use_factset and not any(
        (r["fa_status"] in ("ok", "cached", "empty")) for r in results
    )
    banners = []
    if not use_factset:
        banners.append("FactSet channel disabled (--no-factset): Google-only digest.")
    elif factset_down:
        banners.append("FactSet unavailable this run: Google-only digest.")
    if google_down and (not use_factset or factset_down):
        logger.error("both channels down — aborting")
        sys.exit(1)
    if google_down:
        banners.append("Google News unavailable this run: FactSet-only digest.")

    # ── state ledger: suppress clusters/articles surfaced within STALE_HOURS (§10) ──
    seen = load_ledger(now)
    stale_cutoff = now - timedelta(hours=STALE_HOURS)
    suppressed = 0
    for r in results:
        kept_v = []
        for c, v in r["verdicts"]:
            prev = seen.get(c.hash)
            if prev and prev["first_surfaced_ts"] >= stale_cutoff:
                suppressed += 1
                continue
            kept_v.append((c, v))
        r["verdicts"] = kept_v
        kept_fo = []
        for a in r["factset_only"]:
            h = cluster_hash(normalize_tokens(a.get("headline", "")))
            a["_hash"] = h
            prev = seen.get(h)
            if prev and prev["first_surfaced_ts"] >= stale_cutoff:
                suppressed += 1
                continue
            kept_fo.append(a)
        r["factset_only"] = kept_fo

    subject, body = build_digest(results, mode, now_local, banners, suppressed)

    # persist the rendered body (gitignored audit trail; also lets a non-dry-run / cron
    # run be inspected after the fact, since send-mode otherwise only emails it)
    artifact = os.path.join(REPO_ROOT, "logs",
                            f"news_digest_{mode}_{now_local.strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(artifact, "w") as fh:
            fh.write(body + "\n")
        logger.info("digest body saved: %s", artifact)
    except OSError as e:
        logger.warning("could not write digest artifact %s: %s", artifact, e)

    if not args.dry_run:
        for r in results:
            hashes = [c.hash for c, _ in r["verdicts"]] + [a["_hash"] for a in r["factset_only"]]
            for h in hashes:
                if h not in seen:
                    seen[h] = {"first_surfaced_ts": now, "tickers": [r["ticker"]]}
                elif r["ticker"] not in seen[h]["tickers"]:
                    seen[h]["tickers"].append(r["ticker"])
        rewrite_ledger(seen)

    logger.info("run done: subject=%r google_down=%s factset_down=%s suppressed=%d",
                subject, google_down, factset_down, suppressed)

    if args.dry_run:
        print(body)
    else:
        from newsdigest.email_send import send
        status = send(subject, body)
        logger.info("email sent (status %s)", status)


if __name__ == "__main__":
    main()
