"""
rank — editorial selection of the DIGEST_LIMIT stories that actually reach the operator.

Motivation (operator, 2026-08-19): "the news updates have too many stories". Measured on the
2026-08-19 premarket run: 262 items across 76 tickers — but SK Hynix alone accounted for 26 of
them (one buyback, told 26 ways), Samsung 21, NVDA 17. So the digest was not 262 stories; it was
~50-70 events with a syndication multiplier on top.

This module runs BETWEEN classify and summarize and picks the top N. Placing it there is what
makes it a COST REDUCTION rather than a cosmetic one: the summarizer used to run over every
survivor (~260 items, ~$3.2/run); it now runs over N (~$0.4). The ranking call itself is one
cheap pass over headlines only.

Why an LLM pass and not a sort. The two deterministic signals available are both dead ends here:
  • `confidence` is 3-level and 106 of 262 items were 'high' — no discrimination inside the bucket;
  • `volume` is worse than useless — only 4 high-confidence items had volume >= 3, and pre_filter's
    own docstring records that a source-tier/volume gate was MEASURED AND REJECTED at 14-39% false
    negatives, because material breaking news is typically a single low-volume cluster. A top-30
    sort on volume is that rejected gate at ~9x the aggression.
So selection is delegated to one batched `claude -p` call with the ranking rules written into the
prompt (auditable), and the deterministic sort survives only as the FALLBACK when that call fails.

Hard constraints applied AFTER the model ranks, in code, so they cannot be argued away:
  • MAX_PER_TICKER slots per ticker — the SK Hynix guard;
  • sell-side rating actions rank last (they only take a slot no real story wanted);
  • the selection is exactly `limit` items when that many survivors exist (backfill on shortfall).

Failure contract: a failed ranking call NEVER drops the digest. It falls back to the deterministic
order and the caller renders a ⚠ banner — degraded, visible, never silent.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from . import pre_filter
from .classify_llm import _run_claude, _extract_json_array, SessionLimitError

DIGEST_LIMIT = 30        # operator decision 2026-08-19 (was uncapped, ~260/run)
MAX_PER_TICKER = 2       # one event per name, plus one genuinely separate second story
# Survivors per ranking call in the SHARDED fallback. The normal path is one pooled call with the
# WHOLE pool in view, which is what lets the model collapse "same event, told five ways" across
# tickers — a run-off round loses exactly the global view rule 3 (NOVELTY) depends on. Sharding is
# therefore a recovery step, not the design.
SHARD_SIZE = 100

# Rank gets its OWN timeout, well above classify's 300s. Measured 2026-08-19 on the first live
# production run: one pooled call over 283 survivors (~19k prompt tokens, ~1k output) exceeded 300s
# and fell back to deterministic order. That is a big single call by design — it replaces the 13-15
# summarizer calls the cap removed — so it is budgeted like one, not like a classify batch.
RANK_TIMEOUT_S = 900

_CONF_RANK = {"high": 3, "medium": 2, "low": 1}
_TIER_RANK = {"tier_1_bctk": 3, "tier_2_active_candidates": 2}

MACRO_KEY = "__macro__"
THEME_KEY = "__theme__"


@dataclass
class Selection:
    cluster_id: str
    reason: str = ""


INSTRUCTIONS = """\
You are the editor of a morning news brief for a technology-focused buy-side portfolio manager.
Below is every story that passed materiality triage today. There are far too many to send. Select
and RANK the best {limit}.

You are choosing what a busy PM reads before the open. Rank by DECISION VALUE — would this change
how the PM thinks about a position today?

RANKING RULES, in priority order:
1. TIER. A story about a Tier-1 (BCTK holding) name outranks Tier-2, which outranks a name the
   fund does not hold. Macro prints that move the whole tape rank with Tier-1.
2. ESTIMATE-CHANGING over commentary. Guidance, capacity/capex decisions, pricing actions, design
   wins, customer wins/losses, M&A, capital returns, regulatory or legal action, supply
   constraints, management change — these move numbers. Previews, opinion, "what to watch",
   valuation musings, and price-action-with-no-cause do not.
3. NOVELTY. The FIRST disclosure of an event outranks a confirmation, a wire pickup, a regional
   re-report, or a "shares rose on yesterday's news" follow-on. If several stories describe the
   SAME underlying event, pick the single most complete one and DROP THE REST — do not spend two
   slots on one event.
4. CROSS-READ. A story with a read-through to another holding in the universe (a supplier's
   capacity decision, a customer's capex) outranks an equally-sized story that stops at one name.
5. SELL-SIDE RANKS LAST. An analyst upgrade, downgrade, initiation, or price-target change is the
   LOWEST priority category. Include one ONLY if slots remain after every genuine business story,
   and ONLY when the headline states a rationale that is not valuation and not the target change
   itself (a demand check, a channel datapoint, a fundamental thesis change). Never include a
   rating story whose only content is the rating or the target.

Do not pad. If fewer than {limit} stories genuinely deserve a slot, return fewer.

OUTPUT: ONLY a JSON array (no prose, no markdown, no code fences), best first:
[{{"cluster_id": str, "reason": str}}]
`reason` is at most 12 words, saying why it earned its rank. Echo cluster_id exactly.
"""


def _bucket(cls) -> str:
    """The per-ticker cap applies to COMPANY stories only; macro/theme share their own buckets."""
    if cls.materiality:
        # sorted(), not [0]: the classifier's ticker ORDER is not stable, so one event tagged
        # [NVDA, MU] here and [MU, NVDA] there would land in two buckets and escape the cap.
        return sorted(cls.materiality)[0]
    if cls.macro:
        return MACRO_KEY
    return THEME_KEY


def _tier_of(cls, tier_map: dict) -> int:
    return max((_TIER_RANK.get(tier_map.get(t, ""), 0) for t in cls.materiality), default=0)


def _is_rating_story(c) -> bool:
    """True when EVERY headline in the cluster is a sell-side rating action. Such clusters reach
    rank only because they carried a non-valuation rationale past pre_filter — they are eligible,
    but they sort last."""
    heads = [it.get("title", "") for it in c.items if it.get("title")]
    return bool(heads) and all(_rating_ish(h) for h in heads)


def _rating_ish(h: str) -> bool:
    """A rating action that pre_filter SPARED (it had a real rationale). Same detectors, without
    the rationale test — here we only need to know it is sell-side, not whether to drop it."""
    h = pre_filter._NON_RATING_SENSE.sub(" ", h)
    if not pre_filter._ANALYST_CTX.search(h):
        return False
    return bool(pre_filter._RATING_CHANGE_VERB.search(h) or pre_filter._PT_ACTION.search(h)
                or pre_filter._RATING_RESTATE.search(h))


def deterministic_order(survivors, tier_map: dict) -> list:
    """The FALLBACK ordering — also the tie-break the model's output is backfilled from.
    Sell-side last, then tier, then confidence, then recency."""
    def key(t):
        c, cls = t
        newest = max(it["published"] for it in c.items)
        return (0 if _is_rating_story(c) else 1, _tier_of(cls, tier_map),
                _CONF_RANK.get(cls.confidence, 0), newest)
    return sorted(survivors, key=key, reverse=True)


def _story_line(c, cls, tier_map: dict) -> str:
    tiers = {1: "T3/other", 2: "T2", 3: "T1-BCTK"}
    who = ", ".join(cls.materiality) if cls.materiality else (
        "MACRO: " + ", ".join(cls.macro) if cls.macro else "THEME: " + ", ".join(cls.themes))
    tier = tiers.get(_tier_of(cls, tier_map), "not held")
    heads = sorted({it["title"] for it in c.items})
    line = (f"[cluster_id: {c.hash}] {who} ({tier}, conf={cls.confidence}, "
            f"{c.volume} outlet{'s' if c.volume != 1 else ''})")
    if cls.rationale:
        line += f"\n    why-material: {cls.rationale[:120]}"
    for h in heads[:3]:                       # 3 headlines is enough to judge; keeps the prompt lean
        line += f"\n    - {h}"
    if len(heads) > 3:
        line += f"\n    - (+{len(heads) - 3} more headlines on the same story)"
    return line


def build_rank_prompt(survivors, tier_map: dict, limit: int) -> str:
    """Exact prompt sent to claude -p (rendered by --render-prompt for review)."""
    body = "\n".join(_story_line(c, cls, tier_map) for c, cls in survivors)
    return INSTRUCTIONS.format(limit=limit) + "\nCANDIDATE STORIES:\n" + body + "\n"


def _rank_once(survivors, tier_map, limit, repo_root,
               timeout: int = RANK_TIMEOUT_S) -> tuple[list, float]:
    """One ranking call. Returns (ordered [Selection], cost). Raises on failure."""
    text, cost = _run_claude(build_rank_prompt(survivors, tier_map, limit), repo_root, timeout)
    parsed = _extract_json_array(text)
    if parsed is None:
        raise ValueError(f"unparseable ranking response: {text[:160]!r}")
    valid = {c.hash for c, _ in survivors}
    out, seen = [], set()
    for obj in parsed:
        if not isinstance(obj, dict):
            continue
        cid = str(obj.get("cluster_id") or "")
        if cid in valid and cid not in seen:        # ignore hallucinated / duplicated ids
            seen.add(cid)
            out.append(Selection(cid, str(obj.get("reason") or "").strip()[:120]))
    if not out:
        raise ValueError("ranking returned no usable cluster_ids")
    return out, cost


def _apply_caps(ordered_pairs, limit: int, max_per_ticker: int) -> tuple[list, int]:
    """Enforce MAX_PER_TICKER over an already-ranked list. Returns (picked, n_capped).

    The cap is HARD — over-cap items are dropped, never backfilled. `limit` is a CEILING, not a
    quota: a quiet day yields a short digest, which is the point. An earlier version relaxed the
    cap to reach `limit` and refilled the digest with 18 further SK Hynix buyback re-tellings —
    i.e. it reproduced the exact complaint this module exists to fix."""
    picked, counts, n_capped = [], {}, 0
    for c, cls in ordered_pairs:
        if len(picked) >= limit:
            break
        b = _bucket(cls)
        if b not in (MACRO_KEY, THEME_KEY) and counts.get(b, 0) >= max_per_ticker:
            n_capped += 1
            continue
        counts[b] = counts.get(b, 0) + 1
        picked.append((c, cls))
    return picked, n_capped


def select_top(survivors, repo_root, limit: int = DIGEST_LIMIT, tier_map=None,
               max_per_ticker: int = MAX_PER_TICKER, logger=None):
    """survivors: list of (cluster, Classification). Returns (selected, cost, note).

    `selected` is a ranked list of (cluster, Classification, reason) capped at `limit`.
    `note` is None on a clean run, else a human-readable banner the caller MUST surface.
    `ranked` is False ONLY when no LLM ranking happened at all and the deterministic order was
    used. The distinction matters for alerting: a SHARDED recovery still produced a real editorial
    ranking (weaker cross-story dedup, but sound), whereas the deterministic order is the measured-
    and-rejected volume proxy standing in for editorial judgement — that one is worth waking
    someone for, the other is not."""
    tier_map = tier_map or {}
    if len(survivors) <= limit:
        # Nothing to choose — everything fits. Not a degradation, so ranked=True.
        ordered = deterministic_order(survivors, tier_map)
        return [(c, cls, "") for c, cls in ordered], 0.0, None, True

    by_id = {c.hash: (c, cls) for c, cls in survivors}
    cost, note, ranked = 0.0, None, True

    def _sharded(pool):
        """Recovery path: each shard nominates its top `limit`, then a run-off ranks the nominees
        head-to-head. Bounded prompts, but it loses the cross-shard view that lets the model see
        one event told five ways — hence recovery only, never the first choice."""
        c_total, finalists = 0.0, []
        shards = [pool[i:i + SHARD_SIZE] for i in range(0, len(pool), SHARD_SIZE)]
        for i, shard in enumerate(shards):
            s_sel, s_cost = _rank_once(shard, tier_map, limit, repo_root)
            c_total += s_cost
            finalists += [by_id[x.cluster_id] for x in s_sel[:limit]]
            if logger:
                logger.info("rank shard %d/%d: %d candidates → %d nominees",
                            i + 1, len(shards), len(shard), min(len(s_sel), limit))
        f_sel, f_cost = _rank_once(finalists, tier_map, limit, repo_root)
        return f_sel, c_total + f_cost

    try:
        try:
            sels, cost = _rank_once(survivors, tier_map, limit, repo_root)
        except subprocess.TimeoutExpired:
            # A pooled timeout means the prompt was too big for one call, NOT that ranking is
            # impossible — so shard and retry rather than dropping to the deterministic order.
            # Same ladder as _classify_recursive: timeout → split → recurse. Going straight to
            # the fallback here is what produced a deterministically-ordered digest on the first
            # live run (2026-08-19 postmarket, 283 survivors, 300s timeout).
            if logger:
                logger.warning("pooled rank timed out at %ds over %d survivors — retrying sharded "
                               "(%d/shard)", RANK_TIMEOUT_S, len(survivors), SHARD_SIZE)
            sels, cost = _sharded(survivors)
            note = (f"story ranking timed out on the full pool ({len(survivors)} stories); "
                    f"recovered via sharded ranking — selection is sound but cross-story dedup "
                    f"is weaker than usual")
        reasons = {x.cluster_id: x.reason for x in sels}
        ordered_pairs = [by_id[x.cluster_id] for x in sels]
        chosen = {x.cluster_id for x in sels}
        ordered_pairs += [p for p in deterministic_order(survivors, tier_map)
                          if p[0].hash not in chosen]
    except SessionLimitError as e:
        note = (f"story ranking unavailable (claude -p session limit) — fell back to "
                f"deterministic order{'; ' + e.reset_hint if e.reset_hint else ''}")
        if logger:
            logger.error("rank ABORTED (429): %s — deterministic fallback", e)
        ordered_pairs, reasons, ranked = deterministic_order(survivors, tier_map), {}, False
    except Exception as e:  # noqa: BLE001 — ranking must never take the digest down
        note = f"story ranking failed ({type(e).__name__}) — fell back to deterministic order"
        if logger:
            logger.warning("rank failed: %s: %s — deterministic fallback", type(e).__name__, e)
        ordered_pairs, reasons, ranked = deterministic_order(survivors, tier_map), {}, False

    picked, n_capped = _apply_caps(ordered_pairs, limit, max_per_ticker)
    if logger:
        for i, (c, cls) in enumerate(picked, 1):
            who = ", ".join(cls.materiality) or ",".join(cls.macro or cls.themes) or "-"
            logger.info("  rank %2d. %-14s %-58s | %s", i, who[:14], c.headline[:58],
                        reasons.get(c.hash, "(deterministic)"))
        logger.info("rank: %d survivors → %d selected (limit=%d; %d dropped by the max-%d/ticker "
                    "cap)%s", len(survivors), len(picked), limit, n_capped, max_per_ticker,
                    "" if ranked else " [FALLBACK]")
    return [(c, cls, reasons.get(c.hash, "")) for c, cls in picked], cost, note, ranked
