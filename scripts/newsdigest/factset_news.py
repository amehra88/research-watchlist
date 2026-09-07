"""
factset_news — quality / sentiment channel (spec §1b), batched.

Pulls FactSet ALL_NEWS through the FactSet_UnstructuredContent MCP tool via `claude -p`
(the only route to that server). The tool's `ids` argument accepts up to 100 identifiers and
post-filters a single shared similarity search, so the whole universe is covered in a handful
of calls instead of one per ticker — verified lossless 2026-08-14: AAPL queried alone returned
exactly the documentIDs it got inside a 10-ticker batch, and INTC returned 0 either way.

Python owns chunking and the saturation split. THE MODEL MAKES THE CALL; WE READ THE TOOL'S
OWN OUTPUT. It used to be asked to echo the rows back as a JSON array, which (a) paid ~600
output tokens per call to transcribe data Python could read directly, and (b) put a model
between the tool and the parser, where it could reword, drop or invent a row with no error.
The transcript is now read with `--output-format stream-json` and the raw tool_result payload
is parsed, the pattern etfflows/factset_flows.py established on 2026-08-19 (500 rows: echo =
590s and truncated; raw = 18s and byte-exact). The raw payload carries every field the prompt
used to ask for, so _normalize is unchanged.

That also makes the harness-stripping flags SAFE here. `--setting-sources ""` alone leaves the
FactSet MCP server loaded (probed 2026-09-07: real rows came back); adding `--strict-mcp-config`
removes it, and the model then hunts with ToolSearch and answers without data. Reading the raw
tool_result turns that silent failure into a hard one: no FactSet tool_use in the transcript
means the tool never ran, and that raises rather than reading as "no news".

Measured per session (3 ids, 3 API turns: ToolSearch -> tool call -> DONE), 2026-09-07:

    default harness + JSON echo (production until 2026-09-07)   ~100,000 prompt tokens
    --system-prompt + --setting-sources ""                         59,654
    + --tools ToolSearch                                           21,953   <- shipped
    + --tools ""            (no ToolSearch: every connector's schemas load eagerly)   76,377
    + --tools <FactSet tool name>                       (same eager load)             76,374
    + --strict-mcp-config   (connector unloaded, tool never runs -> ToolUnavailableError)

`--tools ToolSearch` keeps only the discovery tool: the built-in tool schemas go, and the
connector tools stay deferred until the single ToolSearch fetch. The 10-ticker/4-day A/B
returned the identical 12 documentIDs under every flag set that ran the tool, so the choice is
purely cost. test_factset_tool_result.py pins this argv.

Doc dict: {documentID, headline, sentiment, source, date, url, tickers[]}
fetch_batch returns (docs, failed_tickers) and never raises — the caller degrades to
Google-only (§10). Each document is emitted ONCE, attributed to every watchlist ticker it
names, so a story mentioning two holdings no longer enters the pool twice.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from . import FACTSET_CHUNK_SIZE, FACTSET_RESULT_LIMIT, FACTSET_TIMEOUT_SECONDS
from .classify_llm import _claude_env, MODEL  # reuse the claude -p auth/model convention

# The stream-json transcript readers live in etfflows.factset_flows (lookthrough.py already
# imports them from there). One definition, covered by etfflows/test_factset_flows.py, rather
# than a third copy that could drift from the two spill formats those tests pin down.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from etfflows.factset_flows import _tool_result_blocks, resolve_payload, rows_of  # noqa: E402

_TOOL = "mcp__claude_ai_FactSet_AI-Ready_Data__FactSet_UnstructuredContent"

# Lean system prompt. The default Claude Code preamble (~28K tokens) is replaced, but
# `--strict-mcp-config` is deliberately NOT passed — that is the flag that drops the MCP server.
SYSTEM_PROMPT = (
    "You are a data-retrieval backend. Call the tool you are told to call, exactly once, with "
    "exactly the arguments given, then reply DONE. Do not summarise or restate the tool output."
)


class ToolUnavailableError(RuntimeError):
    """The FactSet tool was never invoked — the transcript has no tool_use naming it.

    This is the failure a mis-set flag produces (e.g. `--strict-mcp-config` unloading the MCP
    server): the model cannot see the tool, so it answers without data. It is NOT a chunk with
    no news and NOT a transient error — retrying per ticker would fail 30 more times the same
    way. fetch_batch treats it as non-splittable and fails the whole chunk at once.
    """

def _factset_tool_ran(stdout: str) -> bool:
    """True iff the transcript contains a tool_use block naming the FactSet tool.

    Presence of SOME tool_result is not enough: when the FactSet server is missing the model
    reaches for ToolSearch instead, and ToolSearch's "No matching deferred tools found" is a
    perfectly well-formed tool_result. The invocation itself is what has to be checked.
    """
    for line in (stdout or "").splitlines():
        try:
            ev = json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" \
                    and str(block.get("name", "")).endswith("FactSet_UnstructuredContent"):
                return True
    return False


def _is_news_payload(rows) -> bool:
    """A FactSet news result is a list whose rows all carry a documentID; [] is a real empty."""
    return isinstance(rows, list) and all(
        isinstance(r, dict) and "documentID" in r for r in rows)


def _batch_prompt(ids, start_date, end_date, limit) -> str:
    """Ask the model to make ONE call and stop. It is not asked to echo anything back —
    Python reads the tool's own output from the transcript — so it cannot summarise, rank,
    reword or paginate. Python owns chunking and the saturation split."""
    return (
        "Call the FactSet_UnstructuredContent tool EXACTLY ONCE with these arguments:\n"
        '  query: "What are the most important recent news developments for this company?"\n'
        "  sources: ['ALL_NEWS']\n"
        f"  ids: {json.dumps(ids)}\n"
        f"  startDate: '{start_date}'\n"
        f"  endDate: '{end_date}'\n"
        f"  limit: {limit}\n"
        "Do NOT pass a sort argument. Do NOT call the tool more than once. Do NOT paginate.\n"
        "After the tool returns, reply with exactly: DONE"
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
        # `--verbose` is what makes stream-json carry the tool_use/tool_result blocks.
        # `--tools ToolSearch` (NOT "" and NOT the FactSet tool name — both load every
        # connector schema eagerly at ~76K) is the 60K -> 22K step; see the module docstring.
        cmd = ["claude", "-p", _batch_prompt(ids, start, end, limit),
               "--allowedTools", _TOOL, "--model", MODEL,
               "--system-prompt", SYSTEM_PROMPT, "--setting-sources", "",
               "--tools", "ToolSearch",
               "--output-format", "stream-json", "--verbose"]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(repo_root),
            env=_claude_env(),
        )
        if result.returncode != 0:
            raise RuntimeError(f"rc={result.returncode}: {(result.stderr or '').strip()[:160]}")
        stdout = result.stdout or ""
        if not _factset_tool_ran(stdout):
            raise ToolUnavailableError(
                "no FactSet tool_use in transcript — the tool was never called: "
                f"{stdout.strip()[-200:]}")
        for text in reversed(_tool_result_blocks(stdout)):
            rows = rows_of(resolve_payload(text))
            if _is_news_payload(rows):
                return rows, "ok"
        # The tool ran but nothing in the transcript parses as its result. A FAILURE, not an
        # empty chunk — returning [] here would read as "no news" (the 2026-08-11 trap).
        raise ValueError(f"tool_result unusable: {stdout.strip()[-200:]}")
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
        except ToolUnavailableError:
            # The tool is not loaded at all. Splitting to per-ticker would fire one doomed
            # call per id (30 for a full chunk) and fail identically — fail the chunk as one.
            failed.update(id_to_ticker[i] for i in chunk if i in id_to_ticker)
            return
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
