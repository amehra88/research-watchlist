"""
factset_news — quality / sentiment channel (spec §1b), batched.

Pulls FactSet ALL_NEWS through the FactSet_UnstructuredContent MCP tool via `claude -p`
(the only route to that server). The tool's `ids` argument accepts up to 100 identifiers and
post-filters a single shared similarity search, so the whole universe is covered in a handful
of calls instead of one per ticker — verified lossless 2026-08-14: AAPL queried alone returned
exactly the documentIDs it got inside a 10-ticker batch, and INTC returned 0 either way.

Python owns chunking and the saturation split; the model is a verbatim transport that must not
summarise, re-rank or paginate.

Doc dict: {documentID, headline, sentiment, source, date, url, tickers[]}
fetch_batch returns (docs, failed_tickers) and never raises — the caller degrades to
Google-only (§10). Each document is emitted ONCE, attributed to every watchlist ticker it
names, so a story mentioning two holdings no longer enters the pool twice.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta

from . import FACTSET_CHUNK_SIZE, FACTSET_RESULT_LIMIT, FACTSET_TIMEOUT_SECONDS
from .classify_llm import _claude_env, MODEL  # reuse the claude -p auth/model convention

_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_UnstructuredContent"

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


def _batch_prompt(ids, start_date, end_date, limit) -> str:
    """Ask for the tool's own result elements verbatim. The model is a transport, not an
    analyst: it must not summarise, rank or reword, and it must not decide pagination —
    Python owns chunking and the saturation split."""
    return (
        "Call the FactSet_UnstructuredContent tool EXACTLY ONCE with these arguments:\n"
        '  query: "What are the most important recent news developments for this company?"\n'
        "  sources: ['ALL_NEWS']\n"
        f"  ids: {json.dumps(ids)}\n"
        f"  startDate: '{start_date}'\n"
        f"  endDate: '{end_date}'\n"
        f"  limit: {limit}\n"
        "Do NOT pass a sort argument. Do NOT call the tool more than once. Do NOT paginate.\n\n"
        "Then return ONLY a JSON array (no prose, no markdown, no code fences) of the tool's "
        "result elements, each as "
        '{"documentID": str, "headline": str, "sentiment": str, "source": str, '
        '"storyDateTime": ISO8601 str, "viewUrl": str, "ids": [str]}. '
        "Copy every value VERBATIM from the tool response — do not summarise, reword, filter, "
        "re-rank or invent. Include every element the tool returned. "
        "Return [] if the tool returned no results."
    )


def make_runner(now: datetime, repo_root, timeout=FACTSET_TIMEOUT_SECONDS):
    """Build the production runner: one `claude -p` per id-chunk.

    This is where the 93% saving lives. The old path spent ~30k tokens of system prompt plus
    FactSet MCP tool schemas per TICKER to carry a ~500-token payload; one session now covers
    30 tickers, so the wrapper is amortised ~30x."""
    def run(ids, window_hours, limit):
        # WINDOW IS DATE-GRANULAR AND ROUNDS UP. The tool takes startDate/endDate, not hours,
        # so a 24h window at a 07:00 run asks for 08-13..08-14 — everything from 08-13T00:00,
        # i.e. ~31h, not 24h. This is deliberate: over-fetching is the safe direction (the
        # state ledger dedups repeats across runs, so the cost of an extra story is nil),
        # whereas filtering on `storyDateTime` would risk dropping real stories — the field
        # carries no timezone, so a wrong tz assumption silently loses news. Do NOT "tighten"
        # this to an exact hour window without first establishing what tz storyDateTime is in.
        start = (now - timedelta(hours=window_hours)).date().isoformat()
        end = now.date().isoformat()
        # --model pinned and ANTHROPIC_API_KEY stripped, same convention as the per-ticker path.
        cmd = ["claude", "-p", _batch_prompt(ids, start, end, limit),
               "--allowedTools", _TOOL, "--model", MODEL]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(repo_root),
            env=_claude_env(),
        )
        if result.returncode != 0:
            raise RuntimeError(f"rc={result.returncode}: {(result.stderr or '').strip()[:160]}")
        parsed = _extract_json_array(result.stdout or "")
        if parsed is None:
            # Unparseable is a FAILURE, not an empty result. Returning [] here would silently
            # drop a whole chunk and read as "no news" — the 2026-08-11 silent-degradation trap.
            raise ValueError(f"unparseable: {(result.stdout or '').strip()[:160]}")
        return [d for d in parsed if isinstance(d, dict)], "ok"
    return run


def _chunks(seq, size):
    return [seq[i : i + size] for i in range(0, len(seq), size)]


def _normalize(d: dict, id_to_ticker: dict) -> dict | None:
    """One FactSet result element → a doc dict, attributed to every watchlist ticker it names.

    The tool returns the full id list per document, so attribution comes from the data instead
    of from which per-ticker query happened to surface it. A document naming no watchlist ticker
    is dropped — it reached us only as a side-effect of another company's id filter."""
    tickers = sorted({id_to_ticker[i] for i in (d.get("ids") or []) if i in id_to_ticker})
    if not tickers:
        return None
    return {
        "documentID": d.get("documentID") or "",
        "headline": (d.get("headline") or "").strip(),
        "sentiment": d.get("sentiment") or "Neutral",
        "source": (d.get("source") or "SA").strip(),
        "date": (d.get("storyDateTime") or "").strip(),
        "url": (d.get("viewUrl") or "").strip(),
        "tickers": tickers,
    }


def fetch_batch(idents, window_hours, runner, chunk_size=FACTSET_CHUNK_SIZE,
                limit=FACTSET_RESULT_LIMIT):
    """Pull FactSet news for a whole universe in a handful of calls instead of one per ticker.

    `ids` accepts up to 100 identifiers and acts as a post-filter on one shared similarity
    search, so batching is lossless (verified live: a ticker queried alone returns exactly the
    documentIDs it gets inside a batch). Python owns the chunking; the model is never asked to
    paginate, which is the part LLMs do unreliably.

    Returns (docs, failed_tickers). Never raises — the caller degrades to Google-only."""
    id_to_ticker = {i.factset_id: i.ticker for i in idents}
    by_doc: dict[str, dict] = {}
    failed: set[str] = set()

    def collect(raw):
        for d in raw:
            norm = _normalize(d, id_to_ticker)
            if norm is None:
                continue
            # Dedup by documentID: the same story reaches us once per chunk that names it, and
            # a chunk can repeat it. Emit once, unioning the tickers it was attributed to.
            cur = by_doc.get(norm["documentID"])
            if cur is None:
                by_doc[norm["documentID"]] = norm
            else:
                cur["tickers"] = sorted(set(cur["tickers"]) | set(norm["tickers"]))

    def run(chunk):
        try:
            raw, _status = runner(chunk, window_hours, limit)
        except Exception:  # noqa: BLE001 — one bad chunk must not lose the other chunks
            if len(chunk) == 1:
                failed.update(id_to_ticker[i] for i in chunk if i in id_to_ticker)
            else:
                # Widened blast radius is the cost of batching: fall back to per-ticker for
                # THIS chunk only, so a connector hiccup loses one ticker, not thirty.
                for one in chunk:
                    run([one])
            return
        # A chunk returning exactly `limit` docs may have been truncated. Split and re-query
        # rather than silently dropping the tail. A single id can't be split further.
        if len(raw) >= limit and len(chunk) > 1:
            half = len(chunk) // 2
            run(chunk[:half])
            run(chunk[half:])
            return
        collect(raw)

    for chunk in _chunks([i.factset_id for i in idents], chunk_size):
        run(chunk)
    return list(by_doc.values()), failed
