"""
summarize — structured summarizer for v3 news-flow survivors.

Runs ONLY on survivors (clusters that hit >=1 classifier pass). Batched `claude -p`
(subscription auth, no tools) turns each story's cluster of HEADLINES (+ FactSet
sentiment + the classifier's tags) into a PM-ready item:
  {headline, bullets[3-5], lens_tags, why_it_matters}

CRITICAL CONSTRAINT — headline-only sourcing. No source in this channel (Google RSS,
IR, FactSet ALL_NEWS) exposes an article BODY. The summarizer therefore synthesizes
STRICTLY from the multiple headlines in the cluster plus the FactSet sentiment label.
The prompt forbids inventing figures, quotes, dates, or specifics not present in the
headlines. When the headlines under-determine a detail, the bullet stays at the level
the headlines support (or says the detail is unconfirmed) — never fabricated.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

from .classify_llm import _run_claude, _extract_json_array, SessionLimitError, MODEL  # reuse the claude -p wrapper

BATCH_SIZE = 20                    # survivors are far fewer than the raw pool
MACRO_LABEL = "MACRO / no single ticker"


@dataclass
class Summary:
    cluster_id: str
    headline: str = ""
    bullets: list = field(default_factory=list)
    lens_tags: list = field(default_factory=list)      # human-readable lens labels
    why_it_matters: str = ""


INSTRUCTIONS = """\
You are a buy-side analyst writing the morning brief for a technology-focused portfolio
manager. For each SURVIVOR STORY below you are given: its cluster of HEADLINES (from one
or more outlets), an optional FactSet sentiment read, and the tags an upstream classifier
already assigned (tickers / themes / macro signals). Write a tight, PM-ready summary.

ABSOLUTE CONSTRAINT — you have HEADLINES ONLY, never article bodies. Synthesize strictly
from the headlines given (plus the FactSet sentiment). DO NOT invent or assume any
specific figure, percentage, price, dollar amount, date, quote, or named detail that is
not explicitly present in the headlines. If the headlines only support a general claim,
keep the bullet general. If outlets' headlines conflict or a detail is unconfirmed, say
so plainly ("outlets differ on…", "figure not specified in coverage"). A fabricated
detail is a serious error; a general-but-true bullet is correct.

For each story produce:
  • headline — a single clean, neutral headline for the story (dedupe/normalize the
    cluster's headlines into one; strip outlet name and clickbait). <=140 chars.
  • bullets — 3 to 5 terse bullets capturing what the headlines collectively convey:
    what happened, who/what is involved, and any directional read the headlines +
    FactSet sentiment support. No fabricated specifics (see constraint).
  • lens_tags — the lenses this story hit, as short readable labels, e.g.
    "Company: NVDA, TSM", "Theme: ai_infrastructure_capex", "Macro: commodity". Build
    these from the classifier tags provided with the story.
  • why_it_matters — 1-2 sentences, PM-framed: why a tech PM should care (thesis
    implication, second-order read, or risk). Grounded in the headlines; no fabrication.

OUTPUT: ONLY a JSON array (no prose, no markdown, no code fences), one object per input
story, each:
{"cluster_id": str, "headline": str, "bullets": [str], "lens_tags": [str],
 "why_it_matters": str}
Return exactly one object per input story, echoing its cluster_id.
"""


def _lens_hint(cls) -> str:
    parts = []
    if cls.materiality:
        parts.append("Company: " + ", ".join(cls.materiality))
    if cls.themes:
        parts.append("Theme: " + ", ".join(cls.themes))
    if cls.macro:
        parts.append("Macro: " + ", ".join(cls.macro))
    return " | ".join(parts) or "(uncategorized)"


def _story_block(survivors) -> str:
    """survivors: list of (cluster, Classification)."""
    out = ["SURVIVOR STORIES:"]
    for c, cls in survivors:
        headlines = sorted({it["title"] for it in c.items})
        srcs = ", ".join(sorted(c.sources)) or "unknown"
        fa = getattr(c, "_fa_sentiment", None)
        fa_line = f" | FactSet sentiment: {fa}" if fa else ""
        out.append(f"\n[cluster_id: {c.hash}] ({c.volume} outlet{'s' if c.volume != 1 else ''}: {srcs}){fa_line}")
        out.append(f"  classifier tags → {_lens_hint(cls)}"
                   + (f"  (confidence: {cls.confidence})" if getattr(cls, 'confidence', None) else ""))
        if cls.rationale:
            out.append(f"  classifier rationale → {cls.rationale}")
        for h in headlines:
            out.append(f"  - {h}")
    return "\n".join(out)


def build_summarizer_prompt(survivors) -> str:
    """Exact prompt sent to claude -p (surfaced at Checkpoint A)."""
    return INSTRUCTIONS + "\n" + _story_block(survivors) + "\n"


def _validate(obj) -> Summary:
    bullets = [str(b).strip() for b in (obj.get("bullets") or []) if str(b).strip()][:5]
    lens = [str(x).strip() for x in (obj.get("lens_tags") or []) if str(x).strip()]
    return Summary(
        cluster_id=str(obj.get("cluster_id") or ""),
        headline=str(obj.get("headline") or "").strip(),
        bullets=bullets,
        lens_tags=lens,
        why_it_matters=str(obj.get("why_it_matters") or "").strip(),
    )


def summarize_survivors(survivors, repo_root, batch_size: int = BATCH_SIZE,
                        logger=None) -> tuple[dict, float, list]:
    """survivors: list of (cluster, Classification). Returns
    ({cluster_id: Summary}, cost, unsummarized_hashes).

    `unsummarized` is the list of survivor cluster hashes with no summary — a PROCESSING
    FAILURE the caller must fail loud on (never a silent drop from the digest). Two ways in:
      • a genuine per-batch error (timeout / unparseable) leaves THAT batch's items
        unsummarized but the run CONTINUES — per-batch isolation, so other batches still
        summarize;
      • a session-limit 429 ABORTS the run fast (NON-RETRYABLE): every remaining batch is
        left unsummarized. Retrying/continuing only fires more doomed calls at the drained
        quota — the 2026-07-21 pathology where the summarizer plowed all ~13 batches into a
        429 wall (07:46→07:48) instead of stopping. Mirrors classify_llm.classify_clusters'
        429 fast-abort + fail-loud contract exactly."""
    out: dict[str, Summary] = {}
    total_cost = 0.0
    for i in range(0, len(survivors), batch_size):
        batch = survivors[i:i + batch_size]
        prompt = build_summarizer_prompt(batch)
        try:
            text, cost = _run_claude(prompt, repo_root)
            total_cost += cost
            parsed = _extract_json_array(text)
            if parsed is None:
                raise ValueError(f"unparseable response: {text[:160]!r}")
            for obj in parsed:
                if isinstance(obj, dict):
                    s = _validate(obj)
                    if s.cluster_id:
                        out[s.cluster_id] = s
        except SessionLimitError as e:
            # 429 quota exhaustion is NON-RETRYABLE and NON-CONTINUABLE: stop calling claude -p
            # entirely. Everything summarized before the 429 is kept; the remainder falls through
            # to `unsummarized` (fail-loud). Distinct from a generic per-batch failure below.
            if logger:
                logger.error(
                    "SUMMARIZER ABORTED (session limit 429): %s — %d/%d survivor(s) summarized "
                    "before abort; remainder UNSUMMARIZED (no retry). Quota %s",
                    e, len(out), len(survivors),
                    f"resets — {e.reset_hint}" if e.reset_hint else "reset time unknown")
            break
        except Exception as e:  # noqa: BLE001 — per-batch isolation for genuine (non-429) failures
            if logger:
                logger.warning("summarizer batch %d-%d failed: %s: %s",
                               i, i + len(batch), type(e).__name__, e)
    unsummarized = [c.hash for c, _cls in survivors if c.hash not in out]
    return out, total_cost, unsummarized


# ───────────────────────────── prompt render (Checkpoint A) ─────────────────────────────

if __name__ == "__main__":
    import argparse
    import datetime as _dt
    ap = argparse.ArgumentParser(description="Render the summarizer prompt against a sample")
    ap.add_argument("--render-prompt", action="store_true")
    args = ap.parse_args()
    if args.render_prompt:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
        from newsdigest.sources import load_classifier
        from newsdigest.cluster import cluster_items
        from newsdigest.classify_llm import Classification

        now = _dt.datetime.now(_dt.timezone.utc)
        classifier = load_classifier()
        sample = [
            {"ticker": "NVDA", "title": "Nvidia and TSMC deepen partnership on 2nm AI chips", "source": "Bloomberg", "link": "", "published": now, "tier": "top_tier"},
            {"ticker": "NVDA", "title": "TSMC to prioritize Nvidia orders on advanced node", "source": "DigiTimes", "link": "", "published": now, "tier": "allowlist"},
        ]
        c = cluster_items(sample, classifier)[0]
        c._fa_sentiment = "Positive"
        cls = Classification(cluster_id=c.hash, materiality=["NVDA", "TSM"],
                             themes=["ai_infrastructure_capex", "foundry_capacity"], macro=[],
                             confidence="high", rationale="NVDA-TSMC 2nm supply deepening; AI capex + foundry")
        macro_sample = [
            {"ticker": "MACRO", "title": "US core PCE inflation cools to 2.6%, boosting rate-cut bets", "source": "CNBC", "link": "", "published": now, "tier": "top_tier"},
        ]
        mc = cluster_items(macro_sample, classifier)[0]
        mcls = Classification(cluster_id=mc.hash, materiality=[], themes=[], macro=["inflation", "fed_policy"],
                              confidence="high", rationale="core PCE cooler → cuts back on table")
        print(build_summarizer_prompt([(c, cls), (mc, mcls)]))
