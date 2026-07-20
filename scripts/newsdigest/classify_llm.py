"""
classify_llm — 3-pass LLM materiality/theme/macro classifier (v3 news-flow channel).

DIRECT CUTOVER replacement for filter.py's heuristic verdict. Instead of source-tier /
story-volume rules (which produced the SPOT/"spot" substring false-positive and other
tangential mis-tags), a batched `claude -p` call reads each clustered headline and
judges — as an analyst would — which of the 83 watchlist tickers the story is
SUBSTANTIVELY about (Pass A: materiality), which of the 61 watchlist themes it advances
(Pass B: themes), and which macro signals it carries (Pass C: macro_signals.yaml). The
three passes are NON-EXCLUSIVE: one story can hit all three.

Engine: `claude -p --output-format json` on subscription auth (ANTHROPIC_API_KEY stripped,
per cost-model), no tools. Batched ~BATCH_SIZE clusters per call → one structured-JSON
array back. A failed batch is NEVER silently dropped: the recovery ladder in
`_classify_recursive` retries transient errors with backoff, splits a timed-out /
total-miss batch in half and recurses, and recovers only the missing subset of a partial
response. A cluster that survives all of that still unclassified is returned in the
`unclassified` list (a PROCESSING FAILURE), which the caller treats as fail-loud (exit
non-zero) — NOT as a below-bar drop. This is the 2026-07-08 timeout-drop fix.

A cluster CLASSIFIED with materiality==[] AND themes==[] AND macro==[] is a legitimate DROP
(below bar). A cluster that lands in `unclassified` is a processing failure. The two must
never be conflated. Any cluster hitting >=1 pass is a SURVIVOR and flows to summarize.py.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field

# Batching. These calls are OUTPUT-token bound: each cluster costs one JSON object with a
# rationale sentence, so wall-time scales ~linearly with cluster count. Measured on
# 2026-07-08: 40 clusters ≈ 190s ≈ 63% of the 300s ceiling, so ordinary claude -p latency
# variance blew a batch past the timeout and (pre-fix) silently dropped all 40 of its
# clusters. 20 ≈ ~95s (~3x headroom); the split-on-timeout recovery below forgives the
# rare slow batch, so this is the safety margin, not a hard guarantee.
BATCH_SIZE = 20
MODEL = "claude-sonnet-4-6"      # matches the substack/inbox v3 extractors
CLAUDE_TIMEOUT_S = 300
MAX_TRANSIENT_RETRIES = 2        # rc!=0 / unparseable → retry SAME batch (with backoff)
RETRY_BACKOFF_S = 15             # base inter-retry sleep; grows per attempt (15s, 30s)
MAX_CLASSIFY_CALLS = 250         # runaway guard: hard cap on claude -p calls per run


# ───────────────────────────── result type ─────────────────────────────

@dataclass
class Classification:
    cluster_id: str
    materiality: list = field(default_factory=list)   # watchlist tickers the story is ABOUT
    themes: list = field(default_factory=list)        # 61-theme slugs advanced
    macro: list = field(default_factory=list)         # macro_signals.yaml categories
    confidence: str = "low"                           # 'high' | 'medium' | 'low'
    rationale: str = ""

    @property
    def is_survivor(self) -> bool:
        return bool(self.materiality or self.themes or self.macro)

    @property
    def lens_hits(self) -> list:
        hits = []
        if self.materiality:
            hits.append("company")
        if self.themes:
            hits.append("theme")
        if self.macro:
            hits.append("macro")
        return hits


# ───────────────────────────── prompt construction ─────────────────────────────

INSTRUCTIONS = """\
You are a precise buy-side research analyst triaging a morning news pool for a
technology-focused portfolio manager. You are given a numbered batch of news STORIES.
Each story is a CLUSTER of one or more near-duplicate headlines from different outlets
(plus, when available, a FactSet sentiment read). You see HEADLINES ONLY — no article
bodies.

For EACH story, run three independent, NON-EXCLUSIVE passes and return structured JSON:

PASS A — materiality (company): Which watchlist TICKERS is this story SUBSTANTIVELY
  about? Substantive = the story concerns that company's business, products, strategy,
  financials, guidance, competitive position, capital allocation, legal/regulatory
  standing, or a named counterparty/supply-chain link that moves it. Use the EXACT
  watchlist symbol. Rules:
    • A ticker earns materiality ONLY on a real reference to THAT COMPANY — never on a
      common English word, a place, or an unrelated entity that happens to collide with
      the symbol. (e.g. "gold spot price" or "on the spot" is NOT SPOT/Spotify; "core
      inflation" is NOT any ticker; "Arm wrestling" is NOT ARM Holdings.) Use the company
      NAME hints below to disambiguate.
    • A story can be material to several tickers (e.g. an NVDA–TSM supply headline → both).
    • A pure market-wrap that merely lists many names ("Nasdaq ends higher, led by...")
      is NOT material to those names — leave materiality empty unless the story is
      genuinely about a specific company.

PASS B — themes: Which THEME slugs (from the fixed list below) does the story
  substantively advance? Only slugs from the list. Empty if none genuinely fit.

PASS C — macro: Which MACRO-SIGNAL categories (from the fixed list below) does the story
  carry? These are top-down economic/market signals (Fed, inflation, jobs, growth,
  geopolitics, commodities/energy, cross-asset). A story with NO watchlist company can
  still be a valuable macro signal (e.g. a CPI print, an OPEC cut, a power-price spike).
  Only categories from the list. Empty if none genuinely fit.

confidence: your overall confidence that this story is worth a PM's attention as tagged —
  "high" (clearly material/thematic/macro, unambiguous), "medium" (relevant but
  secondary or partly ambiguous), or "low" (borderline; tagged but thin). When a symbol
  match is ambiguous, prefer LEAVING IT OUT and lowering confidence over a false tag.

rationale: ONE short line (<=140 chars) explaining the tags. No prose beyond this.

A story with materiality, themes, AND macro all empty is fine — return it with all three
empty; it will be dropped. Do not force a tag to avoid an empty result.

OUTPUT: ONLY a JSON array (no prose, no markdown, no code fences), one object per input
story, each:
{"cluster_id": str, "materiality": [str], "themes": [str], "macro": [str],
 "confidence": "high"|"medium"|"low", "rationale": str}
Return exactly one object per input story, echoing its cluster_id.
"""


def _ticker_hint_block(ticker_names: dict) -> str:
    """`SYM — Name` lines for the 83-ticker universe (disambiguation is the SPOT-bug fix)."""
    lines = [f"  {t} — {ticker_names.get(t) or t}" for t in sorted(ticker_names)]
    return "WATCHLIST TICKERS (Pass A — use EXACT symbol; NAME disambiguates):\n" + "\n".join(lines)


def _theme_block(valid_themes) -> str:
    return "THEME SLUGS (Pass B — only these):\n  " + ", ".join(sorted(valid_themes))


def _macro_block(macro_cfg: dict) -> str:
    lines = ["MACRO SIGNAL CATEGORIES (Pass C — only these):"]
    for cat in macro_cfg.get("categories", []):
        desc = " ".join((cat.get("description") or "").split())
        lines.append(f"  {cat['name']}: {desc}")
    return "\n".join(lines)


def _story_block(batch) -> str:
    """Render the batch of clusters as a numbered story list."""
    out = ["STORIES:"]
    for c in batch:
        rep = c.representative
        headlines = sorted({it["title"] for it in c.items})
        srcs = ", ".join(sorted(c.sources)) or "unknown"
        fa = getattr(c, "_fa_sentiment", None)
        fa_line = f" | FactSet sentiment: {fa}" if fa else ""
        out.append(f"\n[cluster_id: {c.hash}] ({c.volume} outlet{'s' if c.volume != 1 else ''}: {srcs}){fa_line}")
        for h in headlines:
            out.append(f"  - {h}")
    return "\n".join(out)


def build_classifier_prompt(batch, macro_cfg: dict, ticker_names: dict, valid_themes) -> str:
    """The exact prompt sent to claude -p for one batch. Pure function (surfaced at Checkpoint A)."""
    return (
        INSTRUCTIONS
        + "\n" + _ticker_hint_block(ticker_names)
        + "\n\n" + _theme_block(valid_themes)
        + "\n\n" + _macro_block(macro_cfg)
        + "\n\n" + _story_block(batch)
        + "\n"
    )


# ───────────────────────────── claude -p ─────────────────────────────

_SESSION_LIMIT_RE = re.compile(r"session limit|usage limit", re.I)


class SessionLimitError(RuntimeError):
    """claude -p returned a 429 session/usage-limit result — NON-RETRYABLE and NON-SPLITTABLE.

    A 429 means the shared subscription quota is exhausted, not that this batch was too big or
    too slow. Retrying or splitting only fires MORE calls against the same drained quota — the
    2026-07-20 pathology where a session-limit batch split recursively and stormed 07:52→08:35
    ET before the wrapper SIGKILLed it. So this is caught distinctly from TimeoutExpired: the
    run aborts fast, every remaining cluster is UNCLASSIFIED (fail-loud), and alerting fires."""
    def __init__(self, reset_hint: str = ""):
        self.reset_hint = reset_hint
        super().__init__("claude -p session limit reached (429)"
                         + (f" — {reset_hint}" if reset_hint else ""))


def _detect_session_limit(stdout: str):
    """If claude -p stdout carries a 429 session-limit result, return the reset hint (may be
    ''); otherwise None. Handles both the parsed-JSON envelope (api_error_status==429 /
    is_error+'session limit') and a raw-text fallback when stdout is truncated/unparseable."""
    if not stdout:
        return None
    body = None
    try:
        env = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        env = None
    if isinstance(env, dict):
        body = str(env.get("result") or "")
        is_429 = env.get("api_error_status") == 429 or (env.get("is_error") and _SESSION_LIMIT_RE.search(body))
    else:
        body = stdout
        is_429 = ('"api_error_status":429' in stdout or '"api_error_status": 429' in stdout
                  or _SESSION_LIMIT_RE.search(stdout))
    if not is_429:
        return None
    m = re.search(r"resets[^\"'.}]*", body or "")
    return (m.group(0).strip() if m else "")


def _claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def _run_claude(prompt: str, repo_root: str, timeout: int = CLAUDE_TIMEOUT_S) -> tuple[str, float]:
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--allowedTools", "", "--model", MODEL]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout, cwd=str(repo_root), env=_claude_env())
    # Session-limit 429 is checked FIRST — it can arrive with rc!=0 OR as an is_error envelope,
    # and must map to the non-retryable SessionLimitError rather than a generic transient error.
    hint = _detect_session_limit(result.stdout)
    if hint is not None:
        raise SessionLimitError(hint)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p rc={result.returncode} "
                           f"stderr={result.stderr[:200]!r} stdout={result.stdout[:300]!r}")
    env = json.loads(result.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"claude -p is_error: {str(env.get('result'))[:200]}")
    return env.get("result", ""), float(env.get("total_cost_usd", 0.0) or 0.0)


def _extract_json_array(text: str):
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _validate(obj, valid_tickers, valid_themes, valid_macro) -> Classification:
    """Sanitize one model object: drop any tag outside the fixed vocabularies."""
    cid = str(obj.get("cluster_id") or "")
    mat = [t for t in (obj.get("materiality") or []) if t in valid_tickers]
    thm = [t for t in (obj.get("themes") or []) if t in valid_themes]
    mac = [m for m in (obj.get("macro") or []) if m in valid_macro]
    conf = str(obj.get("confidence") or "low").lower()
    if conf not in ("high", "medium", "low"):
        conf = "low"
    return Classification(cluster_id=cid, materiality=mat, themes=thm, macro=mac,
                          confidence=conf, rationale=str(obj.get("rationale") or "")[:200])


# ───────────────────────────── public API ─────────────────────────────

@dataclass
class _Ctx:
    """Invariant state threaded through the recursive classifier (one instance per run)."""
    macro_cfg: dict
    ticker_names: dict
    valid_themes: set
    valid_tickers: set
    valid_macro: set
    repo_root: str
    timeout: int
    logger: object = None
    cost: float = 0.0      # accumulated claude -p cost (mutated in place)
    calls: int = 0         # total claude -p calls this run (runaway guard)


def _classify_recursive(batch, ctx: _Ctx, depth: int = 0) -> dict:
    """Classify one batch, GUARANTEEING progress. Returns {cluster_id: Classification} for
    every cluster it could classify; clusters absent from the return are unclassified and
    are reconciled (→ fail-loud) by classify_clusters. Recovery ladder — NO batch is ever
    silently dropped:
      • transient error (rc!=0 / unparseable) → retry SAME batch with backoff (≤MAX_TRANSIENT_RETRIES)
      • timeout OR total-miss (empty result)  → split the batch in half and recurse (less
        output per call ⇒ faster; also isolates a poison cluster)
      • partial response (model omits some)   → re-classify ONLY the missing subset
      • single cluster still failing           → give up, logged LOUD (caller marks UNCLASSIFIED)
    A cluster classified with all-empty passes is a legitimate below-bar DROP; a cluster
    that lands in `unclassified` is a PROCESSING FAILURE. The two must never be conflated."""
    if not batch:
        return {}

    parsed = None
    for attempt in range(MAX_TRANSIENT_RETRIES + 1):
        if ctx.calls >= MAX_CLASSIFY_CALLS:
            ctx.logger and ctx.logger.error(
                "CLASSIFY-CAP: hit MAX_CLASSIFY_CALLS=%d; leaving %d cluster(s) unclassified",
                MAX_CLASSIFY_CALLS, len(batch))
            return {}
        try:
            ctx.calls += 1
            prompt = build_classifier_prompt(batch, ctx.macro_cfg, ctx.ticker_names, ctx.valid_themes)
            text, cost = _run_claude(prompt, ctx.repo_root, ctx.timeout)
            ctx.cost += cost
            parsed = _extract_json_array(text)
            if parsed is None:
                raise ValueError(f"unparseable response: {text[:160]!r}")
            break
        except SessionLimitError:
            # 429 quota exhaustion is NON-RETRYABLE and NON-SPLITTABLE: retry/split would only
            # fire more doomed calls against the drained quota. Propagate to classify_clusters,
            # which aborts the run fast and marks the remainder UNCLASSIFIED (fail-loud).
            raise
        except subprocess.TimeoutExpired:
            # Splitting halves the output length and near-certainly clears the timeout —
            # strictly better than burning another full CLAUDE_TIMEOUT_S on the same size.
            ctx.logger and ctx.logger.warning(
                "classify timeout (n=%d, depth=%d) → split", len(batch), depth)
            parsed = None
            break
        except Exception as e:  # noqa: BLE001 — transient (rc!=0 / unparseable): retry, then split
            parsed = None
            if attempt < MAX_TRANSIENT_RETRIES:
                sleep_s = RETRY_BACKOFF_S * (attempt + 1)
                ctx.logger and ctx.logger.warning(
                    "classify transient error (n=%d, depth=%d, attempt %d/%d): %s: %s — retry in %ds",
                    len(batch), depth, attempt + 1, MAX_TRANSIENT_RETRIES, type(e).__name__, e, sleep_s)
                time.sleep(sleep_s)
            else:
                ctx.logger and ctx.logger.warning(
                    "classify transient error (n=%d, depth=%d) exhausted retries: %s: %s → split",
                    len(batch), depth, type(e).__name__, e)

    verdicts: dict[str, Classification] = {}
    if parsed is not None:
        for obj in parsed:
            if isinstance(obj, dict):
                c = _validate(obj, ctx.valid_tickers, ctx.valid_themes, ctx.valid_macro)
                if c.cluster_id:
                    verdicts[c.cluster_id] = c

    missing = [c for c in batch if c.hash not in verdicts]
    if not missing:
        return verdicts

    if len(missing) == len(batch):
        # total miss (timeout / unparseable / empty array). Split to make progress.
        if len(batch) == 1:
            ctx.logger and ctx.logger.error(
                "CLASSIFY-FAIL: cluster %s unclassifiable after retries+splits (depth=%d)",
                batch[0].hash, depth)
            return {}
        mid = len(batch) // 2
        ctx.logger and ctx.logger.warning(
            "classify total-miss (n=%d, depth=%d) → split %d/%d",
            len(batch), depth, mid, len(batch) - mid)
        verdicts.update(_classify_recursive(batch[:mid], ctx, depth + 1))
        verdicts.update(_classify_recursive(batch[mid:], ctx, depth + 1))
        return verdicts

    # partial response: recover ONLY the missing clusters (strictly smaller ⇒ terminates)
    ctx.logger and ctx.logger.warning(
        "classify partial (%d/%d missing, depth=%d) → recover subset",
        len(missing), len(batch), depth)
    verdicts.update(_classify_recursive(missing, ctx, depth + 1))
    return verdicts


def classify_clusters(clusters, macro_cfg, ticker_names, valid_themes, repo_root,
                      batch_size: int = BATCH_SIZE, timeout: int = CLAUDE_TIMEOUT_S,
                      logger=None) -> tuple[dict, float, list]:
    """Classify all clusters. Returns ({cluster_id: Classification}, total_cost_usd, unclassified).

    `unclassified` is the list of cluster hashes that could NOT be classified — a PROCESSING
    FAILURE distinct from a below-bar DROP. Two ways in: (1) retries+splits exhausted for a
    genuine timeout/transient error; (2) a session-limit 429 aborted the run fast (quota gone,
    no point retrying). Either way the caller must fail loud so the run never silently
    under-reports the news pool (the 2026-07-08 timeout-drop / 2026-07-20 session-limit defects)."""
    ctx = _Ctx(
        macro_cfg=macro_cfg,
        ticker_names=ticker_names,
        valid_themes=set(valid_themes),
        valid_tickers=set(ticker_names),
        valid_macro={c["name"] for c in macro_cfg.get("categories", [])},
        repo_root=str(repo_root),
        timeout=timeout,
        logger=logger,
    )
    out: dict[str, Classification] = {}
    try:
        for i in range(0, len(clusters), batch_size):
            out.update(_classify_recursive(clusters[i:i + batch_size], ctx))
    except SessionLimitError as e:
        # Fast-abort: quota is exhausted, so stop calling claude -p entirely. Everything
        # classified before the 429 is kept; the remainder falls through to `unclassified`.
        ctx.logger and ctx.logger.error(
            "CLASSIFIER ABORTED (session limit 429, %d call(s)): %s — %d/%d classified before "
            "abort; remainder UNCLASSIFIED (no retry/split). Quota %s",
            ctx.calls, e, len(out), len(clusters),
            (f"resets — {e.reset_hint}" if e.reset_hint else "reset time unknown"))

    unclassified = [c.hash for c in clusters if c.hash not in out]
    if unclassified:
        shown = ", ".join(unclassified[:20]) + (" …" if len(unclassified) > 20 else "")
        ctx.logger and ctx.logger.error(
            "CLASSIFIER INCOMPLETE: %d/%d cluster(s) unclassified after retries+splits: %s",
            len(unclassified), len(clusters), shown)
    return out, ctx.cost, unclassified


# ───────────────────────────── prompt render (Checkpoint A) ─────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Render the classifier prompt against a sample batch")
    ap.add_argument("--render-prompt", action="store_true")
    args = ap.parse_args()

    if args.render_prompt:
        import sys
        import yaml
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
        from newsdigest.sources import load_classifier
        from newsdigest.cluster import cluster_items

        REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        macro_cfg = yaml.safe_load(open(os.path.join(REPO, "config", "macro_signals.yaml")))
        themes_block = (yaml.safe_load(open(os.path.join(REPO, "config", "watchlist.yaml"))) or {}).get("themes", {})
        valid_themes = set()
        for cat in themes_block.values():
            valid_themes.update(cat or [])
        # a tiny 5-name hint map + a realistic sample batch incl. the SPOT trap and a macro-only story
        ticker_names = {"SPOT": "Spotify", "NVDA": "NVIDIA", "TSM": "Taiwan Semiconductor (TSMC)",
                        "ARM": "Arm Holdings", "AMD": "Advanced Micro Devices"}
        classifier = load_classifier()
        sample = [
            {"ticker": "GOLD", "title": "Gold spot price hits record as investors seek haven", "source": "Reuters", "link": "", "published": __import__("datetime").datetime.now(__import__("datetime").timezone.utc), "tier": "top_tier"},
            {"ticker": "NVDA", "title": "Nvidia and TSMC deepen partnership on 2nm AI chips", "source": "Bloomberg", "link": "", "published": __import__("datetime").datetime.now(__import__("datetime").timezone.utc), "tier": "top_tier"},
            {"ticker": "NVDA", "title": "TSMC to prioritize Nvidia orders on advanced node", "source": "DigiTimes", "link": "", "published": __import__("datetime").datetime.now(__import__("datetime").timezone.utc), "tier": "allowlist"},
            {"ticker": "MACRO", "title": "US core PCE inflation cools to 2.6%, boosting rate-cut bets", "source": "CNBC", "link": "", "published": __import__("datetime").datetime.now(__import__("datetime").timezone.utc), "tier": "top_tier"},
        ]
        clusters = cluster_items(sample, classifier)
        print(build_classifier_prompt(clusters, macro_cfg, ticker_names, valid_themes))
