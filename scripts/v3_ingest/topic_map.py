#!/usr/bin/env python3
"""Shared topic vocabulary over both registers (spec §4.2).

ONE VOCABULARY, TWO REGISTERS. Analyst exchanges (exchanges.jsonl) are the
question side; MD&A diffs and foreign claims (claims.jsonl) are the evidence
side. Both map into the SAME topic namespace — otherwise §6.2's two-count
comparison has no way to know that a disclosure and a question concern the same
topic, and the gap metric is simply not computable.

THEMES ARE ANCHORS, NOT BOXES. The config/watchlist.yaml slugs seed the space
and preserve continuity with the existing labelled history. A phrase that lands
near one inherits it; a phrase that lands far from all of them becomes a
new-theme CANDIDATE. That is how the vocabulary grows.

THE OPERATOR OWNS THE VOCABULARY. Candidates are written to a review file. This
module NEVER writes to config/watchlist.yaml — the same rule that governs tier
promotion.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evidence_store as es  # noqa: E402

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

REPO_ROOT = Path("/root/research-watchlist")
WATCHLIST_YAML = REPO_ROOT / "config" / "watchlist.yaml"
EXCHANGES_PATH = REPO_ROOT / "state" / "transcripts" / "exchanges.jsonl"
CLAIMS_PATH = REPO_ROOT / "state" / "evidence" / "claims.jsonl"

MODEL = "claude-sonnet-4-6"                # matches the other v3 wrappers
CLAUDE_TIMEOUT_S = 120
MIN_UNIT_WORDS = 8                         # below this there is no topic

# Cosine on gemini-embedding-001. Calibrated in Task 6 against the real
# corpus; this is the starting point, not a tuned value.
SIM_THRESHOLD = 0.72

# Findings 2026-08-21 R2. The whole best-cosine distribution is ~0.08 wide, so
# "nearest anchor" is often a coin flip: convertible-note prose landed on
# ai_generated_content at 0.689. When the top two anchors are this close the
# winner carries no information, and letting it inherit silently inflates that
# theme's cross-sectional count — the §5 metric with no visible symptom.
MIN_MARGIN = 0.02


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] topic_map: {msg}", flush=True)


def load_themes(watchlist_path: Path = WATCHLIST_YAML) -> list:
    """Every slug across every theme group, sorted. The count is whatever the
    file says today — it has already changed once and will change again."""
    data = yaml.safe_load(watchlist_path.read_text()) or {}
    slugs = set()
    for group in (data.get("themes") or {}).values():
        for slug in group or []:
            slugs.add(str(slug))
    return sorted(slugs)


def anchor_text(slug: str) -> str:
    """A slug is not a sentence. Embedding `china_ai_infrastructure_demand`
    raw wastes the model's language prior; the spaced phrase does not."""
    return slug.replace("_", " ")


def cosine(a: list, b: list) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def clears_gates(best: float, second, threshold: float = SIM_THRESHOLD,
                 min_margin: float = MIN_MARGIN) -> bool:
    """Both gates in one place. `assign` and `score_phrases` must decide
    identically — one is the readable reference, the other is the batched form
    the real run uses, and a divergence between them would be invisible."""
    if best < threshold:
        return False
    # a single anchor has no runner-up, so there is no coin flip to lose
    if second is not None and (best - second) < min_margin:
        return False
    return True


def assign(phrase_vecs: list, anchor_vecs: list, anchors: list,
           threshold: float = SIM_THRESHOLD,
           min_margin: float = MIN_MARGIN) -> list:
    """-> [(theme_or_None, similarity)] aligned to phrase_vecs.

    Two gates, and the second is not in the original spec. A phrase inherits a
    theme only when it clears `threshold` AND beats the runner-up by
    `min_margin`. Without the margin, prose that belongs to no theme still
    lands on whichever anchor happens to be a hair closer — see MIN_MARGIN.

    The similarity is reported even on a miss: a phrase that scored 0.71
    against an existing theme is a different kind of candidate from one that
    scored 0.2, and the operator review in §4.2 needs to see which."""
    out = []
    for pv in phrase_vecs:
        scored = sorted(((cosine(pv, av), a)
                         for av, a in zip(anchor_vecs, anchors)), reverse=True)
        best_s, best_a = scored[0]
        second = scored[1][0] if len(scored) > 1 else None
        ok = clears_gates(best_s, second, threshold, min_margin)
        out.append((best_a if ok else None, best_s))
    return out


# ───────────────────── input units, both registers ─────────────────────

# Findings 2026-08-21 R1. Accounting, financing and legal housekeeping is a
# large share of MD&A prose, is never a thesis topic, and — because every filer
# writes it — sails straight through MIN_CANDIDATE_COMPANIES. It has to be
# dropped BEFORE a claude -p call is spent on it. Cues are multi-word and
# deliberately specific: bare "revenue" or "capital expenditures" must survive,
# since capex prose scored 0.805 against ai_infrastructure_capex.
HOUSEKEEPING_CUES = (
    "forward-looking statements", "safe harbor",
    "critical accounting", "accounting policies", "accounting pronouncement",
    "recently issued accounting", "revenue is recognized",
    "revenue recognition", "effective tax rate", "uncertain tax positions",
    "unrecognized tax benefits", "valuation allowance", "deferred tax",
    "pension", "postretirement", "actuarial",
    "convertible senior notes", "senior notes", "credit agreement",
    "credit facility", "borrowing capacity", "revolving", "indenture",
    "aggregate principal amount", "lease payments", "operating lease",
    "right-of-use", "contractual obligations", "off-balance sheet",
    "share-based compensation", "stock-based compensation",
    "goodwill", "impairment charge", "intangible assets",
    "marketable securities", "debt securities", "fair value measurement",
    "prospectus", "selling stockholder", "registration statement",
    "shelf registration", "corporate website", "available free of charge",
    "incorporated by reference", "foreign exchange gain",
    "foreign currency translation", "repurchase program", "treasury stock",
    "dividends declared",
)


def is_housekeeping(text: str) -> bool:
    """True when this block is accounting/financing/legal mechanics."""
    low = " ".join(text.lower().split())
    return any(cue in low for cue in HOUSEKEEPING_CUES)


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue                       # torn line must not abort the run


def iter_question_units(path: Path = EXCHANGES_PATH):
    """Analyst speech only. corprep speech is the company describing itself,
    which is evidence and reaches us through claims.jsonl instead.

    period_key is DERIVED, never read: 53.1% of the corpus carries a fiscal
    label that would misalign it against the calendar-keyed evidence side.
    See evidence_store.join_period_key."""
    for r in _iter_jsonl(path):
        if r.get("speaker_type") != "analyst":
            continue
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        try:
            pk = es.join_period_key(period_key=r.get("period_key"),
                                    period_basis=r.get("period_basis"),
                                    event_date=r.get("event_date"))
        except ValueError:
            continue                       # undatable row cannot be compared
        yield {
            "unit_id": r["vector_id"],
            "register": "question",
            "ticker": r.get("ticker"),
            "period_key": pk,
            "first_evidence_date": None,
            "speaker_firm": r.get("speaker_firm"),
            "text": text,
        }


def iter_evidence_units(path: Path = CLAIMS_PATH):
    """Claims are already calendar-keyed by evidence_store, so period_key is
    read as-is here. Housekeeping prose is dropped before it can cost a call."""
    for r in _iter_jsonl(path):
        text = (r.get("text") or "").strip()
        if len(text.split()) < MIN_UNIT_WORDS:
            continue
        if is_housekeeping(text):
            continue
        yield {
            "unit_id": r["claim_id"],
            "register": "evidence",
            "ticker": r.get("ticker"),
            "period_key": r.get("period_key"),
            "first_evidence_date": r.get("first_evidence_date"),
            "speaker_firm": None,
            "text": text,
        }


# ───────────────────────── phrase extraction ─────────────────────────

def extract_prompt(text: str) -> str:
    return (
        "Read the passage below from an earnings call or a company filing.\n"
        "List the distinct SUBJECT TOPICS it concerns — what it is about, not "
        "what it claims.\n\n"
        "Rules:\n"
        "- 2 to 5 words per topic, lowercase, no punctuation.\n"
        "- Name the subject matter, not the sentiment or direction. "
        "'chinese transceiver competition', not 'worry about china'.\n"
        "- At most 4 topics. Fewer is better. Return [] if it is small talk, "
        "an operator handoff, or pleasantries.\n"
        "- Do not name the company or the speaker.\n\n"
        "Reply with ONLY a JSON array of strings. No prose, no code fence.\n\n"
        "PASSAGE:\n" + text[:4000]
    )


def is_limit_cliff(envelope: dict) -> bool:
    """The 2026-08-11 signature: an error that returned instantly, took one
    turn and cost nothing. That is the usage limiter, not a bad prompt, and
    retrying into it just burns wall-clock. 267 pages died this way."""
    return bool(envelope.get("is_error")) \
        and envelope.get("duration_api_ms") == 0 \
        and envelope.get("num_turns") == 1 \
        and not envelope.get("total_cost_usd")


def parse_phrases(envelope: dict):
    """-> (phrases, status) where status is ok | empty | failed: <why>."""
    if envelope.get("is_error"):
        return [], f"failed: claude is_error {str(envelope.get('result'))[:120]}"
    raw = envelope.get("result") or ""
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return [], "failed: no JSON array in reply"
    try:
        items = json.loads(m.group(0))
    except ValueError as e:
        return [], f"failed: unparseable array ({e})"
    if not isinstance(items, list):
        return [], "failed: reply was not an array"
    phrases = [" ".join(str(x).lower().split()) for x in items
               if str(x).strip()]
    return (phrases, "ok") if phrases else ([], "empty")


def _claude_env() -> dict:
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)     # force subscription auth
    return env


def extract_phrases(text: str):
    """-> (phrases, status). Never raises; the caller records the status."""
    cmd = ["claude", "-p", extract_prompt(text),
           "--model", MODEL, "--output-format", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CLAUDE_TIMEOUT_S, env=_claude_env())
    except subprocess.TimeoutExpired:
        return [], "failed: timeout"
    except Exception as e:                            # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {e}"
    try:
        env = json.loads(proc.stdout)
    except ValueError:
        return [], f"failed: rc={proc.returncode} unparseable envelope"
    if is_limit_cliff(env):
        return [], "failed: usage-limit cliff"
    return parse_phrases(env)


# ───────────────────── new-theme candidate clustering ─────────────────────

MIN_CANDIDATE_COMPANIES = 3
MIN_CANDIDATE_BANKS = 2


def cluster_candidates(rows: list, vecs: dict, threshold: float = 0.80) -> list:
    """Greedy single-pass clustering of below-threshold phrases.

    Greedy, not k-means: the number of emergent topics is unknown by
    construction, and a centroid method needs that number up front. The cost
    is order-sensitivity, which is acceptable because the operator reads the
    clusters before anything is named.

    Reports n_banks / n_companies / n_exchanges separately — the §5 weighting
    is meaningless if they are collapsed into one count.
    """
    clusters = []
    for row in rows:
        v = vecs.get(row["phrase"])
        if v is None:
            continue
        placed = False
        for c in clusters:
            if cosine(v, c["_centroid"]) >= threshold:
                c["unit_ids"].append(row["unit_id"])
                c["phrases"].add(row["phrase"])
                c["_companies"].add(row.get("ticker"))
                if row.get("speaker_firm"):
                    c["_banks"].add(row["speaker_firm"])
                c["_registers"].add(row.get("register"))
                placed = True
                break
        if not placed:
            clusters.append({
                "_centroid": v,
                "unit_ids": [row["unit_id"]],
                "phrases": {row["phrase"]},
                "_companies": {row.get("ticker")},
                "_banks": ({row["speaker_firm"]}
                           if row.get("speaker_firm") else set()),
                "_registers": {row.get("register")},
            })

    out = []
    for c in clusters:
        out.append({
            "label_suggestion": sorted(c["phrases"])[0],
            "phrases": sorted(c["phrases"]),
            "unit_ids": c["unit_ids"],
            "registers": sorted(x for x in c["_registers"] if x),
            "n_exchanges": len(c["unit_ids"]),
            "n_companies": len({x for x in c["_companies"] if x}),
            "n_banks": len(c["_banks"]),
        })
    out.sort(key=lambda c: (c["n_banks"], c["n_companies"]), reverse=True)
    return out


def promotable(cluster: dict) -> bool:
    """Breadth gate before a cluster reaches the operator.

    Evidence-only clusters are exempt from the bank test: an analyst has by
    definition not asked about them yet, and that silence IS stage 1 of §6.3 —
    the earliest and most valuable state the system can report."""
    if cluster.get("registers") == ["evidence"]:
        return cluster.get("n_companies", 0) >= MIN_CANDIDATE_COMPANIES
    return (cluster.get("n_companies", 0) >= MIN_CANDIDATE_COMPANIES
            and cluster.get("n_banks", 0) >= MIN_CANDIDATE_BANKS)


# ───────────────────────── ledger, rows, CLI ─────────────────────────

import argparse  # noqa: E402  (appended with the Task 6 code)
import concurrent.futures as cf  # noqa: E402
import itertools  # noqa: E402
import threading  # noqa: E402

STATE_DIR = REPO_ROOT / "state" / "topics"
TOPICS_PATH = STATE_DIR / "topics.jsonl"
CANDIDATES_PATH = STATE_DIR / "_candidates.json"
PROGRESS_PATH = STATE_DIR / "_progress.json"
PAIRS_PATH = STATE_DIR / "_pairs.jsonl"
EMBED_CACHE_PATH = STATE_DIR / "_phrase_vectors.json"

# Code is imported from THIS tree, not from REPO_ROOT. REPO_ROOT is the shared
# data root (state/, config/) and stays pinned to the main checkout, but a
# worktree must run its own scripts — pointing this at REPO_ROOT silently
# imported the main checkout's embed.py and ran the un-fixed version.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chunking"))

#: phrases per embedding request.
EMBED_BATCH = 100


class Ledger:
    """Three states per unit: ok / empty / failed. `empty` is
    answered-and-done, `failed` is unknown-and-retried.

    That distinction is the whole point. A usage-limit cliff is `failed`, so a
    later run re-attempts the unit; routing it to `empty` would mark thousands
    of units answered after the first cliff and silently build the topic map
    from a fraction of the corpus."""

    def __init__(self, path: Path):
        self.path = path
        self.data = {"version": 1, "entries": {}}
        if path.exists():
            try:
                loaded = json.loads(path.read_text())
                if isinstance(loaded, dict):
                    self.data = loaded
            except ValueError:
                pass          # a kill mid-save must not strand the whole pass
        self.data.setdefault("version", 1)
        self.data.setdefault("entries", {})

    def status(self, unit_id: str):
        e = self.data["entries"].get(unit_id)
        return e.get("status") if e else None

    def done(self, unit_id: str) -> bool:
        s = self.status(unit_id)
        return s in ("ok", "empty")

    def record(self, unit_id: str, status: str, n_phrases: int) -> None:
        self.data["entries"][unit_id] = {
            "status": status,
            "n_phrases": n_phrases,
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        }

    def counts(self) -> dict:
        c = {}
        for e in self.data["entries"].values():
            k = str(e.get("status", "?")).split(":")[0]
            c[k] = c.get(k, 0) + 1
        return c

    def save(self) -> None:
        """Atomic, for the same reason the embedding cache is: this file is
        what makes 8,677 units resumable, and a truncated one loses the run."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(f"{self.path.name}.tmp{os.getpid()}")
        try:
            tmp.write_text(json.dumps(self.data, indent=1))
            os.replace(tmp, self.path)
        finally:
            if tmp.exists():
                tmp.unlink()


def topic_row(unit: dict, phrase: str, theme, similarity: float) -> dict:
    return {
        "unit_id": unit["unit_id"],
        "register": unit["register"],
        "ticker": unit.get("ticker"),
        "period_key": unit.get("period_key"),
        "speaker_firm": unit.get("speaker_firm"),
        "first_evidence_date": unit.get("first_evidence_date"),
        "phrase": phrase,
        "theme": theme,
        "similarity": round(float(similarity), 4),
    }


# ── extracted (unit, phrase) pairs: the durable, threshold-free record ──
#
# topics.jsonl carries an ASSIGNMENT, which depends on the threshold. Storing
# only that would mean a threshold change could never be applied to units
# already extracted — and re-extracting is the one genuinely expensive step.
# So the pairs are persisted separately and every run re-assigns all of them.

def append_pairs(path: Path, pairs: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for unit, phrase in pairs:
            fh.write(json.dumps({"unit": unit, "phrase": phrase}) + "\n")


def load_pairs(path: Path) -> list:
    if not path.exists():
        return []
    out, seen = [], set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue          # tolerate a torn final line from a kill
        key = (r["unit"].get("unit_id"), r["phrase"])
        if key in seen:
            continue
        seen.add(key)
        out.append((r["unit"], r["phrase"]))
    return out


def score_phrases(phrases: list, anchor_vecs: list, anchors: list, *, emb,
                  threshold: float = SIM_THRESHOLD,
                  min_margin: float = MIN_MARGIN,
                  batch_size: int = EMBED_BATCH,
                  keep_vectors: bool = True):
    """-> (scores, vecs)

    scores: phrase -> {"theme", "best", "second"}
    vecs:   phrase -> list[float], ONLY for phrases that inherited nothing

    Batched and streamed on purpose. Holding a vector for every distinct
    phrase is what the spec's one-shot `dict(zip(uniq, embed(uniq)))` does,
    and at ~15k phrases that is ~1.5GB as Python floats plus a ~640MB JSON
    cache — on a host with ~1GB free. Measured, not guessed; it is the same
    shape as the exit-137 the probe took.

    So each batch is scored against the anchors as float32 and then dropped.
    Only below-threshold vectors are retained, because only those go on to
    clustering, and they are a minority.
    """
    import numpy as np                                  # noqa: PLC0415

    A = np.asarray(anchor_vecs, dtype=np.float32)
    A /= np.clip(np.linalg.norm(A, axis=1, keepdims=True), 1e-12, None)

    scores, vecs = {}, {}
    uniq = sorted(set(phrases))
    for i in range(0, len(uniq), batch_size):
        batch = uniq[i:i + batch_size]
        # use_cache=False, and this is the whole point of the function.
        # embed() keeps a cached vector resident in _CACHES for the life of
        # the process and re-serialises the dict on every flush, so caching
        # here would quietly rebuild the very structure the batching exists to
        # avoid: measured at 41.5 KB/vector, 15k phrases is a 638MB file and
        # ~1.5GB parsed, against ~500MB free. Re-embedding costs ~15 min at
        # the measured 58 ms/phrase. That is the trade, and it is not close.
        raw = emb.embed(batch, "retrieval_document", use_cache=False,
                        batch_size=batch_size)
        V = np.asarray(raw, dtype=np.float32)
        V /= np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-12, None)
        sims = V @ A.T                                  # (batch, n_anchors)
        for j, phrase in enumerate(batch):
            row = sims[j]
            order = np.argsort(row)[::-1]
            best = float(row[order[0]])
            second = float(row[order[1]]) if len(order) > 1 else None
            ok = clears_gates(best, second, threshold, min_margin)
            scores[phrase] = {
                "theme": anchors[int(order[0])] if ok else None,
                "best": best,
                "second": second,
            }
            if not ok and keep_vectors:
                vecs[phrase] = raw[j]
        del V, sims, raw
    return scores, vecs


def inherit_curve(scores: dict, lo: float = 0.60, hi: float = 0.86,
                  step: float = 0.02, min_margin: float = MIN_MARGIN) -> list:
    """Inherit rate as a function of threshold.

    Reported instead of auto-calibrated. Findings 2026-08-21: corpus coverage
    is 43 of 68 tickers and skews optical/networking, so a threshold fitted to
    it now would be fitted to that skew. The curve is the honest artefact —
    it lets the value be chosen later, against better coverage, without
    re-extracting anything."""
    out = []
    n = len(scores) or 1
    t = lo
    while t <= hi + 1e-9:
        k = sum(1 for s in scores.values()
                if clears_gates(s["best"], s["second"], t, min_margin))
        out.append((round(t, 3), k, round(100.0 * k / n, 1)))
        t += step
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P2 topic map (spec §4.2)")
    ap.add_argument("--threshold", type=float, default=SIM_THRESHOLD)
    ap.add_argument("--cluster-threshold", type=float, default=0.80)
    ap.add_argument("--limit", type=int, help="stop after N units (calibration)")
    ap.add_argument("--register", choices=["question", "evidence"],
                    action="append")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-extract", action="store_true",
                    help="re-assign already-extracted pairs; spend no LLM calls")
    ap.add_argument("--workers", type=int, default=4,
                    help="concurrent claude -p calls (extraction is I/O-bound)")
    args = ap.parse_args(argv)

    import embed as emb                                # noqa: PLC0415

    themes = load_themes()
    log(f"{len(themes)} theme anchors from config/watchlist.yaml")

    want = set(args.register or ["question", "evidence"])
    q_units = list(iter_question_units()) if "question" in want else []
    e_units = list(iter_evidence_units()) if "evidence" in want else []

    # Interleave the two registers rather than running one then the other.
    # A usage cliff can stop this pass at any point, and concatenated order
    # means an early stop yields questions only — with no evidence side there
    # is no §6.2 gap to compute and no stage 1 at all, which is the single most
    # valuable thing the run produces. Interleaved, a partial run is a smaller
    # version of the whole answer instead of half of one.
    units = [u for pair in itertools.zip_longest(q_units, e_units)
             for u in pair if u is not None]
    log(f"{len(units)} input units ({sorted(want)}: "
        f"{len(q_units)} question, {len(e_units)} evidence, interleaved)")

    ledger = Ledger(PROGRESS_PATH)
    # Recorded so a reader can tell a partial map from a complete one. Without
    # it the ledger says how many units were attempted but not how many exist,
    # and a half-extracted map looks exactly like a finished one.
    ledger.data["n_units"] = len(units)
    todo = [u for u in units if not ledger.done(u["unit_id"])]
    log(f"{len(todo)} units need phrase extraction "
        f"({len(units) - len(todo)} already done)")
    if args.limit:
        todo = todo[:args.limit]
        log(f"--limit {args.limit}: extracting {len(todo)}")
    if args.no_extract:
        todo = []
        log("--no-extract: re-assigning stored pairs only")

    if args.dry_run:
        for u in todo[:20]:
            log(f"  DRY {u['register']} {u['ticker']} {u['text'][:100]}")
        return 0

    # Extraction is one `claude -p` subprocess per unit and is entirely
    # I/O-bound: measured at ~8.9s/unit, which is ~21.5h for 8,717 units
    # serially. Workers cut that proportionally. A cliff stops the whole pass —
    # once the limiter is on, every in-flight call fails the same way, and
    # retrying into it only burns wall-clock.
    cliff, new_pairs, done_n = False, [], 0
    lock = threading.Lock()
    pending = list(todo)
    while pending and not cliff:
        wave, pending = pending[:args.workers * 4], pending[args.workers * 4:]
        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(extract_phrases, u["text"]): u for u in wave}
            for fut in cf.as_completed(futs):
                u = futs[fut]
                try:
                    phrases, status = fut.result()
                except Exception as e:                  # noqa: BLE001
                    phrases, status = [], f"failed: {type(e).__name__}: {e}"
                with lock:
                    done_n += 1
                    ledger.record(u["unit_id"], status, len(phrases))
                    if status == "failed: usage-limit cliff":
                        cliff = True
                        continue
                    meta = {k: v for k, v in u.items() if k != "text"}
                    for p in phrases:
                        new_pairs.append((meta, p))
        ledger.save()
        if new_pairs:
            append_pairs(PAIRS_PATH, new_pairs)
            new_pairs = []
        log(f"  {done_n}/{len(todo)} units, ledger {ledger.counts()}")
    if cliff:
        log(f"USAGE-LIMIT CLIFF after {done_n} units — stopping. Re-run later; "
            f"the ledger resumes without re-spending.")
    ledger.save()
    if new_pairs:
        append_pairs(PAIRS_PATH, new_pairs)
    log(f"ledger now {ledger.counts()}" + (" (stopped early)" if cliff else ""))

    pairs = load_pairs(PAIRS_PATH)
    log(f"{len(pairs)} (unit, phrase) pairs on record")
    if not pairs:
        log("nothing to map")
        return 1 if cliff else 0

    emb.load_key()
    anchor_vecs = emb.embed([anchor_text(t) for t in themes],
                            "retrieval_document", cache_path=EMBED_CACHE_PATH)

    scores, vecs = score_phrases([p for _, p in pairs], anchor_vecs, themes,
                                 emb=emb, threshold=args.threshold)
    log(f"scored {len(scores)} distinct phrases")

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    rows, unmapped = [], []
    for unit, p in pairs:
        s = scores[p]
        rows.append(topic_row(unit, p, s["theme"], s["best"]))
        if s["theme"] is None:
            unmapped.append({"unit_id": unit["unit_id"], "phrase": p,
                             "ticker": unit.get("ticker"),
                             "speaker_firm": unit.get("speaker_firm"),
                             "register": unit["register"]})

    tmp = TOPICS_PATH.with_name(TOPICS_PATH.name + f".tmp{os.getpid()}")
    with tmp.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.replace(tmp, TOPICS_PATH)
    log(f"wrote {len(rows)} topic rows -> {TOPICS_PATH} "
        f"({len(rows) - len(unmapped)} inherited a theme, "
        f"{len(unmapped)} below threshold)")

    log(f"inherit rate vs threshold (margin {MIN_MARGIN}):")
    for t, k, pct in inherit_curve(scores):
        mark = "  <- current" if abs(t - args.threshold) < 1e-9 else ""
        log(f"    {t:.2f}  {k:>6}/{len(scores)}  {pct:>5.1f}%{mark}")

    clusters = cluster_candidates(unmapped, vecs,
                                  threshold=args.cluster_threshold)
    ready = [c for c in clusters if promotable(c)]
    CANDIDATES_PATH.write_text(json.dumps({
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "threshold": args.threshold,
        "gate": {"min_companies": MIN_CANDIDATE_COMPANIES,
                 "min_banks": MIN_CANDIDATE_BANKS},
        "note": "Proposals only. The operator names or rejects each one; "
                "nothing here is written to config/watchlist.yaml.",
        "promotable": ready,
        "below_gate": len(clusters) - len(ready),
    }, indent=1))
    log(f"{len(ready)} candidate themes past the gate "
        f"({len(clusters) - len(ready)} below) -> {CANDIDATES_PATH}")
    return 1 if cliff else 0


if __name__ == "__main__":
    sys.exit(main())
