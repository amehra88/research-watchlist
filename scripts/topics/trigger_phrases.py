#!/usr/bin/env python3
"""Trigger-phrase screen over InsiderScore transcript bodies (plan 2026-09-15, step 3).

Why InsiderScore and not our own FactSet corpus: `search_filings` with
formtypes=["TSCRIPT"] indexes COMPLETE transcripts, market-wide, sentence by
sentence, with speaker, firm, and `basetype` separating prepared remarks from
Q&A. Our FactSet corpus holds ~57% of each call (now rising with PR #7), and a
phrase absent from half a call is not a phrase the company didn't say. Running a
phrase screen over a partial corpus is the "absence read as evidence" bug this
repo fixed three times on 2026-09-15.

The unit of signal is NOT the phrase. Measured live: about a third of
"step function" hits negate it ("it's not a new step function"). A hit is
scored only when it is
  (i)   in the operator-owned phrase list (config/trigger_phrases.yaml),
  (ii)  actually present in the returned sentence — the vendor's boolean matches
        at DOCUMENT level, so rows arrive whose snippet holds only one term,
  (iii) not negated within a local window,
  (iv)  tagged by who said it — management CLAIMING an inflection is a different
        signal from an analyst ASKING about one, and
  (v)   flagged NEW only under the newly_said predicate: the filer was observed in
        each of the prior two quarters and never said it. An unobserved baseline
        is unknown, never new.

Standalone by design. Its state lives in its own files and nothing here feeds
the §5 diffusion counts or the lifecycle stages. Announce-once via an
append-only ledger, the same idiom as stage_alert.py.

This is a timeliness tool: it surfaces language for the operator to research.
It is not a return predictor and must not be framed as one — the literature is
consistent that short-horizon prediction from call language does not survive.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CODE_ROOT = HERE.parent.parent                       # the tree this code lives in
sys.path.insert(0, str(HERE.parent))                  # lib.claude_p, etfflows.factset_flows
from lib import claude_p                                                        # noqa: E402
from etfflows.factset_flows import _tool_result_blocks, _unwrap, resolve_payload  # noqa: E402

REPO_ROOT = Path("/root/research-watchlist")          # shared DATA root (state/, notes/)
PHRASES_PATH = CODE_ROOT / "config" / "trigger_phrases.yaml"   # ships with the code
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
STATE = REPO_ROOT / "state" / "topics"
LEDGER = STATE / "trigger_hits.jsonl"
REPORT = REPO_ROOT / "notes" / "reports" / "trigger-hits.md"

TOOL = "mcp__claude_ai_InsiderScore__search_filings"
MODEL = "claude-haiku-4-5-20251001"                   # the model only places the call
TIMEOUT_S = 180
NEG_WINDOW_WORDS = 10                                 # measured: 8 needed, 15 too wide
NOVELTY_BASELINE = 2                                  # quarters, per diffusion.newly_said

_NEG_WORD = re.compile(r"^(not|never|no|without|hardly|nor|\w+n't)$", re.I)
_ROLE_RE = re.compile(
    r"\b(chief|officer|president|founder|director|chairman|chairwoman|executive|vice|"
    r"treasurer|controller|head of|general counsel|investor relations|ceo|cfo|coo|cto)\b", re.I)
_FIRM_PARENS_RE = re.compile(r"\(([^)]+)\)")
_MARK_RE = re.compile(r"\*\*")
_WS_RE = re.compile(r"\s+")


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] trigger_phrases: {msg}", flush=True)


# ───────────────────────── the phrase file (operator-owned) ─────────────────────────

def load_phrases(path: Path = PHRASES_PATH) -> dict:
    """Read and validate. There is deliberately no writer in this module."""
    cfg = yaml.safe_load(Path(path).read_text()) or {}
    groups = cfg.get("groups") or {}
    if not isinstance(groups, dict) or not groups:
        raise ValueError(f"{path}: 'groups' must be a non-empty mapping")
    for g, items in groups.items():
        if not isinstance(items, list):
            raise ValueError(f"{path}: group {g!r} must be a list")
        for it in items:
            if not isinstance(it, dict) or not it.get("phrase") \
                    or not isinstance(it.get("weight"), int) or it["weight"] <= 0:
                raise ValueError(f"{path}: group {g!r} item {it!r} needs phrase + positive int weight")
    for k in ("mcap_floor", "lookback_days"):
        if not isinstance(cfg.get(k), int) or cfg[k] <= 0:
            raise ValueError(f"{path}: {k} must be a positive int")
    cfg.setdefault("max_hits_per_phrase", 40)
    return cfg


def watchlist_tickers(path: Path = WATCHLIST_YAML) -> set:
    w = yaml.safe_load(Path(path).read_text()) or {}
    out = set()
    for tier in ("tier_1_bctk", "tier_2_active_candidates", "tier_3_watchlist"):
        for e in (w.get(tier) or []):
            if e.get("ticker"):
                out.add(e["ticker"])
    return out


# ───────────────────────── parsing the vendor result ─────────────────────────

def parse_search_csv(text: str) -> list:
    """search_filings returns a 'URL To Search: ...' preamble, a blank line, then
    CRLF CSV headed `ticker,mcap,...`. 'No Results Found' has no header."""
    if not text:
        return []
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("ticker,")), None)
    if start is None:
        return []
    body = "\n".join(lines[start:])
    rows = []
    for r in csv.DictReader(io.StringIO(body)):
        rows.append({k.strip(): (v or "").strip() for k, v in r.items() if k})
    return rows


# ───────────────────────── the gates ─────────────────────────

def _norm(s: str) -> str:
    return _WS_RE.sub(" ", _MARK_RE.sub("", s or "")).strip().lower()


def _phrase_re(phrase: str) -> re.Pattern:
    words = [re.escape(w) for w in _norm(phrase).split(" ")]
    return re.compile(r"(?<![\w-])" + r"\s+".join(words) + r"(?![\w-])")


def snippet_contains(snippet: str, phrase: str) -> bool:
    """Whole-phrase, case-insensitive, highlight markers stripped. THE post-filter."""
    return bool(_phrase_re(phrase).search(_norm(snippet)))


def is_negated(snippet: str, phrase: str) -> bool:
    """A negation cue within NEG_WINDOW_WORDS before the phrase, clipped at the
    last sentence break. Local on purpose: a 'not' about something else twelve
    words earlier must not poison the phrase."""
    text = _norm(snippet)
    m = _phrase_re(phrase).search(text)
    if not m:
        return False
    before = text[:m.start()]
    before = re.split(r"[.;?!]", before)[-1]             # clip at sentence break
    words = before.split()[-NEG_WINDOW_WORDS:]
    if any(_NEG_WORD.match(w) for w in words):
        return True
    return "rather than" in " ".join(words)


def speaker_role(row: dict) -> str:
    """management | analyst | unknown, from basetype and the title field.
    Management rows carry a role ("Chief Executive Officer, CRWD"); analyst rows
    carry a firm in parentheses ("(Morgan Stanley & Co Ltd)") and no role."""
    if (row.get("basetype") or "").lower() == "presentation":
        return "management"
    title = row.get("title") or ""
    if _ROLE_RE.search(title):
        return "management"
    if _FIRM_PARENS_RE.search(title):
        return "analyst"
    return "unknown"


def hit_id(row: dict, phrase: str) -> str:
    return f"{row.get('ticker')}|{row.get('iacc')}|{row.get('chunkid')}|{phrase}"


def _cal_quarter(date: str) -> str:
    d = dt.date.fromisoformat(str(date)[:10])
    return f"CY{d.year}-Q{(d.month - 1) // 3 + 1}"


def score_row(row: dict, phrase: str, weight: int, group: str) -> dict | None:
    """Every gate, in order. None = the phrase is not in this sentence (post-filter).
    A negated hit is RETURNED with weight 0 so the report can show what was
    excluded and why — silently dropping it would hide a third of the matches."""
    snippet = row.get("snippet") or ""
    if not snippet_contains(snippet, phrase):
        return None
    negated = is_negated(snippet, phrase)
    date = str(row.get("datefiled") or "")[:10]
    return {
        "id": hit_id(row, phrase),
        "ticker": row.get("ticker"), "iacc": row.get("iacc"), "chunkid": row.get("chunkid"),
        "sectionid": row.get("sectionid"), "basetype": row.get("basetype"),
        "date": date, "cal_quarter": _cal_quarter(date) if date else None,
        "mcap": row.get("mcap"), "sector": row.get("sector"),
        "phrase": phrase, "group": group,
        "weight": 0 if negated else weight, "negated": negated,
        "role": speaker_role(row), "speaker": row.get("title"),
        "quote": _MARK_RE.sub("", snippet).strip(), "link": row.get("link"),
    }


# ───────────────────────── novelty: the newly_said predicate ─────────────────────────

def _prior_quarters(cq: str, n: int) -> list:
    y, q = int(cq[2:6]), int(cq[-1])
    out = []
    for _ in range(n):
        q -= 1
        if q == 0:
            q, y = 4, y - 1
        out.append(f"CY{y}-Q{q}")
    return out[::-1]


def is_novel(ticker: str, phrase: str, cal_quarter: str, history: list,
             baseline: int = NOVELTY_BASELINE) -> bool:
    """New for this filer iff it was OBSERVED (any hit) in each of the prior
    `baseline` quarters and none of those hits carried this phrase. An
    unobserved baseline is unknown — never counted as new."""
    if not cal_quarter:
        return False
    prior = _prior_quarters(cal_quarter, baseline)
    mine = [h for h in history if h.get("ticker") == ticker]
    observed = {h.get("cal_quarter") for h in mine}
    if any(p not in observed for p in prior):
        return False
    return not any(h.get("phrase") == phrase and h.get("cal_quarter") in prior for h in mine)


# ───────────────────────── announce-once ledger ─────────────────────────

def load_ledger(path: Path = LEDGER) -> list:
    out = []
    if not Path(path).exists():
        return out
    for line in Path(path).read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def append_hits(path: Path, hits: list, as_of: str) -> int:
    """Append hits whose id has never been recorded. First-seen wins."""
    seen = {h.get("id") for h in load_ledger(path)}
    new = [h for h in hits if h and h.get("id") not in seen]
    if not new:
        return 0
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    with Path(path).open("a") as fh:
        for h in new:
            fh.write(json.dumps(dict(h, as_of=as_of, ts=ts), sort_keys=True) + "\n")
    return len(new)


def split_by_watchlist(hits: list, watchlist: set):
    watch = [h for h in hits if h.get("ticker") in watchlist]
    other = [h for h in hits if h.get("ticker") not in watchlist]
    return watch, other


# ───────────────────────── the MCP call ─────────────────────────

def build_query(phrases: list) -> str:
    return " OR ".join(f'"{p}"' for p in phrases)


def _prompt(phrase: str, begin: str, end: str, mcap_low: int, limit: int) -> str:
    return (
        f"Call the {TOOL.split('__')[-1]} tool exactly once with exactly these arguments, "
        "changing nothing:\n"
        f"  search_phrase='{build_query([phrase])}'\n"
        f"  formtypes=['TSCRIPT']\n"
        f"  begin_date='{begin}'\n"
        f"  end_date='{end}'\n"
        f"  mcap_low={mcap_low}\n"
        f"  limit={limit}\n\n"
        "Do not modify the search phrase. Do not call any other tool. Then reply DONE."
    )


def fetch_phrase(phrase: str, begin: str, end: str, mcap_low: int, limit: int,
                 model: str = MODEL, timeout: int = TIMEOUT_S) -> list:
    """-> parsed CSV rows for one phrase. The model places the call; the CSV is
    read from the tool_result, never from the reply (mcp-lean)."""
    stdout = claude_p.run_mcp(_prompt(phrase, begin, end, mcap_low, limit),
                              mcp_tool=TOOL, model=model, cwd=str(REPO_ROOT), timeout=timeout)
    for text in reversed(_tool_result_blocks(stdout)):
        obj = _unwrap(resolve_payload(text))
        if isinstance(obj, dict) and isinstance(obj.get("result"), str):
            return parse_search_csv(obj["result"])
        if isinstance(obj, str):
            return parse_search_csv(obj)
    return []


# ───────────────────────── report ─────────────────────────

def _table(hits: list) -> list:
    L = ["| ticker | phrase | group | who | new? | quote | link |", "|---|---|---|---|---|---|---|"]
    for h in hits:
        q = h["quote"].replace("|", "\\|")
        q = q if len(q) <= 220 else q[:217] + "…"
        L.append(f"| {h['ticker']} | `{h['phrase']}` | {h['group']} | {h['role']} | "
                 f"{'**new**' if h.get('novel') else ''} | {q} | [{h['date']}]({h['link']}) |")
    return L


def render(watch: list, other: list, negated: list, as_of: str, cfg: dict, window: tuple) -> str:
    L = [f"## Trigger phrases — {as_of}", "",
         f"Window {window[0]}..{window[1]}, mcap >= ${cfg['mcap_floor']/1e9:.0f}B, "
         f"{sum(len(v) for v in cfg['groups'].values())} phrases in "
         f"{len(cfg['groups'])} groups. Source: InsiderScore `search_filings` over transcript "
         "bodies (complete index). Each row is a verbatim sentence with a deep link.", "",
         "Scored only when the phrase is in the sentence, not negated, and attributed. "
         "**new** = the filer was observed in each of the prior two quarters and never said it. "
         "This surfaces language to research; it is not a return predictor.", ""]
    L.append(f"### Watchlist names ({len(watch)})")
    L += _table(sorted(watch, key=lambda h: (-h['weight'], h['ticker']))) if watch else ["_none_"]
    L.append("")
    L.append(f"### Names you do not own ({len(other)}) — §6.4 novel-name discovery")
    L += _table(sorted(other, key=lambda h: (-h['weight'], h['ticker']))) if other else ["_none_"]
    L.append("")
    L.append(f"### Excluded as negated ({len(negated)}) — shown so the filter is auditable")
    if negated:
        for h in negated:
            L.append(f"- {h['ticker']} `{h['phrase']}` ({h['role']}): {h['quote'][:160]}")
    else:
        L.append("_none_")
    L.append("")
    return "\n".join(L)


# ───────────────────────── run ─────────────────────────

def run(args) -> int:
    cfg = load_phrases(PHRASES_PATH)
    days = args.days or cfg["lookback_days"]
    end = dt.date.fromisoformat(args.as_of)
    begin = end - dt.timedelta(days=days)
    window = (begin.isoformat(), end.isoformat())
    items = [(g, it["phrase"], it["weight"]) for g, its in cfg["groups"].items() for it in its]
    log(f"window {window[0]}..{window[1]}; {len(items)} phrases; mcap >= {cfg['mcap_floor']}")
    if args.dry_run:
        for g, p, w in items:
            log(f"  DRY {g:<9} w={w} {build_query([p])}")
        return 0

    history = load_ledger(LEDGER)
    seen = {h.get("id") for h in history}
    fresh, negated, n_rows, n_filtered = [], [], 0, 0
    for g, phrase, weight in items:
        try:
            rows = fetch_phrase(phrase, window[0], window[1], cfg["mcap_floor"],
                                cfg["max_hits_per_phrase"], model=args.model)
        except claude_p.ToolUnavailableError as e:
            log(f"ABORT: {e}")
            return 1
        except Exception as e:                                    # noqa: BLE001
            log(f"  {phrase!r}: failed {type(e).__name__}: {str(e)[:120]}")
            continue
        n_rows += len(rows)
        for r in rows:
            h = score_row(r, phrase, weight, g)
            if h is None:
                n_filtered += 1
                continue
            if h["id"] in seen:
                continue
            seen.add(h["id"])
            h["novel"] = is_novel(h["ticker"], phrase, h["cal_quarter"], history)
            (negated if h["negated"] else fresh).append(h)
        log(f"  {g:<9} {phrase!r}: {len(rows)} rows")
    log(f"{n_rows} rows returned; {n_filtered} rejected by the snippet post-filter; "
        f"{len(fresh)} scored hits, {len(negated)} negated, all new to the ledger")

    watch, other = split_by_watchlist(fresh, watchlist_tickers())
    text = render(watch, other, negated, args.as_of, cfg, window)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(text)
    log(f"report -> {REPORT} ({len(watch)} watchlist, {len(other)} other)")
    n = append_hits(LEDGER, fresh + negated, args.as_of)
    log(f"{n} hits appended -> {LEDGER}")
    if args.email and (watch or other):
        from newsdigest.email_send import send                    # noqa: PLC0415
        send(f"Trigger phrases {args.as_of} ({len(watch)} watchlist / {len(other)} other)", text)
        log("emailed")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Trigger-phrase screen over transcript bodies")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the phrase plan; call nothing")
    ap.add_argument("--days", type=int, help="override lookback_days from the phrase file")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--email", action="store_true")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args(argv)
    if not (args.run or args.dry_run):
        ap.print_help()
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
