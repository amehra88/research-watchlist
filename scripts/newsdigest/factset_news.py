"""
factset_news — quality / sentiment channel (spec §1b).

Calls FactSet ALL_NEWS via `claude -p` + the FactSet_UnstructuredContent MCP tool
(mirrors scripts/cron_earnings_reviewer.py's run_claude pattern), with a per-id
result cache (FACTSET_CACHE_HOURS) so the pre- and post-market runs in one window
don't double-call. De-dups chunk-level results into articles, keeping the strongest
sentiment per headline.

Article dict: {headline, sentiment, source, date, url}
Returns (articles, status):
  'ok' (fresh call) | 'cached' | 'empty' (call ok, no articles) | 'error' | 'disabled'
Failure never raises — the caller degrades to a Google-only digest (§10).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone

from . import FACTSET_CACHE_HOURS, FACTSET_TIMEOUT_SECONDS

_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_UnstructuredContent"

# strongest-sentiment ranking for de-dup (keep max |sentiment|)
_SENT_RANK = {
    "Very Negative": 2, "Very Positive": 2,
    "Negative": 1, "Positive": 1,
    "Neutral": 0, "": -1, None: -1,
}


def _prompt(name: str, factset_id: str, window_hours: int) -> str:
    return (
        f"Use the FactSet_UnstructuredContent tool to find the most important recent news "
        f"developments for {name} (FactSet id {factset_id}). "
        f"Query text: \"What are the most important recent news developments for this company?\". "
        f"Set sources=['ALL_NEWS'] and ids=['{factset_id}']. Restrict to the last {window_hours} hours. "
        f"Do NOT pass a sort argument.\n\n"
        "Return ONLY a JSON array (no prose, no markdown, no code fences) where each element is "
        '{\"headline\": str, \"sentiment\": one of '
        '\"Very Positive\"|\"Positive\"|\"Neutral\"|\"Negative\"|\"Very Negative\", '
        '\"source\": str, \"date\": ISO8601 str, \"url\": str}. '
        "De-duplicate repeated chunks of the same article into one element. "
        "Return [] if there is no qualifying news."
    )


def _extract_json_array(text: str):
    """Pull the first top-level JSON array out of claude's stdout."""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _dedup(raw_articles) -> list[dict]:
    by_headline: dict[str, dict] = {}
    for a in raw_articles:
        if not isinstance(a, dict):
            continue
        hl = (a.get("headline") or "").strip()
        if not hl:
            continue
        key = hl.lower()
        sent = a.get("sentiment") or "Neutral"
        cur = by_headline.get(key)
        if cur is None or _SENT_RANK.get(sent, 0) > _SENT_RANK.get(cur.get("sentiment"), 0):
            by_headline[key] = {
                "headline": hl,
                "sentiment": sent,
                "source": (a.get("source") or "").strip(),
                "date": (a.get("date") or "").strip(),
                "url": (a.get("url") or "").strip(),
            }
    return list(by_headline.values())


def _cache_path(cache_dir: str, factset_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", factset_id)
    return os.path.join(cache_dir, f"factset_{safe}.json")


def _read_cache(cache_dir: str, factset_id: str, now: datetime):
    path = _cache_path(cache_dir, factset_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as fh:
            blob = json.load(fh)
        fetched = datetime.fromisoformat(blob["fetched_ts"])
        if (now - fetched).total_seconds() <= FACTSET_CACHE_HOURS * 3600:
            return blob["articles"]
    except (OSError, KeyError, ValueError):
        return None
    return None


def _write_cache(cache_dir: str, factset_id: str, now: datetime, articles):
    os.makedirs(cache_dir, exist_ok=True)
    tmp = _cache_path(cache_dir, factset_id) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"fetched_ts": now.isoformat(), "articles": articles}, fh)
    os.replace(tmp, _cache_path(cache_dir, factset_id))


def fetch(name, factset_id, window_hours, now, cache_dir, repo_root,
          timeout=FACTSET_TIMEOUT_SECONDS):
    cached = _read_cache(cache_dir, factset_id, now)
    if cached is not None:
        return cached, "cached"

    cmd = ["claude", "-p", _prompt(name, factset_id, window_hours), "--allowedTools", _TOOL]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return [], "error: timeout"
    except Exception as e:  # noqa: BLE001
        return [], f"error: {type(e).__name__}: {e}"

    if result.returncode != 0:
        return [], f"error: rc={result.returncode}: {(result.stderr or '').strip()[:160]}"

    parsed = _extract_json_array(result.stdout or "")
    if parsed is None:
        return [], "error: unparseable"

    articles = _dedup(parsed)
    _write_cache(cache_dir, factset_id, now, articles)
    return articles, ("ok" if articles else "empty")
