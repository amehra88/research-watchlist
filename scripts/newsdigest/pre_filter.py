"""
pre_filter — Lever 2: cheap, high-precision BOILERPLATE-CATEGORY filter, run BETWEEN clustering and
the LLM classifier. NO claude -p.

Motivation (2026-07-21): the v3 news channel sends ~300 clusters/run to the batched `claude -p`
classifier, draining the shared subscription session limit before the morning reset (the 07-21
break — see [[news_classifier_quota_budget_open]]). An earlier attempt — a source-tier / cluster-
VOLUME gate — was measured and REJECTED: material breaking news is overwhelmingly a single low-tier
cluster, so any tier/volume drop hit 14-39% false-negatives. This filter instead drops well-defined
low-signal CATEGORIES (not source tiers), which is genuinely safe:

  • institutional 13F / ownership disclosures — "Swedish Pension Fund adds ADI shares" (ADI 5/5
    survivors were these), "Commerzbank Sells 130,947 Shares of Intel", "Kornitzer Capital initiates
    position in NVIDIA". CRITICAL: this must NOT catch a corporate equity-stake disclosure that shares
    the words ("Nvidia Discloses 9.3% Ownership Stake in Nebius") — the discriminator is a FUND entity
    / share-count / $-million, which corporate %-stakes lack.
  • template listicles — "Is X Undervalued Right Now", "Strong Momentum Stock" (Zacks farm).
  • routine analyst-rating stubs — "Maintained by Barclays — PT raised to $290", "New Buy Rating for
    X". Up/downgrades are SPARED (they can move the stock — material).
  • no-catalyst price stubs — "No Catalyst Named", "Stock Movement Examined".

A cluster is dropped ONLY if EVERY headline in it is boilerplate; FactSet clusters are exempt (curated
per-ticker + sentiment). This is NOT the retired substring filter.py (which decided HIGH/MEDIUM/DROP);
it only removes clearly-noise categories before the LLM, which stays the precision instrument.

Patterns live here as documented, high-precision regexes (the same in-module convention as filter.py).
Tune them, then re-run the offline drop-precision measurement (target ≥95% of drops genuine boilerplate).
"""
from __future__ import annotations

import re

# ── institutional 13F / ownership-disclosure signals ──────────────────────────────────────────
# A fund/advisor entity suffix. Deliberately EXCLUDES bare "Inc/Ltd/AG/Group/Bank" — those appear in
# COMPANY legal names (Broadcom Inc, Nebius Group) and would misfire on corporate stories.
_FUND = (r"(LLC|L\.?P\.?|Advisors?|Asset\s+(Management|Corp|Advisors)|Capital(\s+Management)?|"
         r"Wealth|Trust\s+Co|Kapital|Investment\s+Management|Bancorp|Associates|"
         r"Financial\s+(Group|Services)|Pension\s+Fund|Aktiengesellschaft|Sovereign\s+Wealth)")
_HOLD_ACTION = re.compile(
    r"\b(buys?|bought|sells?|sold|purchase[sd]?|acquir\w+|reduc\w+|increas\w+|trims?|trimmed|"
    r"boost\w+|adds?|added|initiat\w+|disclos\w+|invest\w+|raises?|raised|lowers?|lowered|"
    r"reports?|reported|holds?|has|have|owns?)\b", re.I)
_HOLD_OBJECT = re.compile(r"\b(shares?|position|holdings?|stake)\b", re.I)
_SHARECOUNT = re.compile(r"([\d,]{4,}\s*shares?|shares?\s+of\s+[\d,]{4,})", re.I)
_DOLLAR_POS = re.compile(r"\$[\d.]+\s*(million|billion)\b[\w\s.]{0,25}\b(position|stake|holdings?|shares?)", re.I)
_PORTFOLIO_ADJ = re.compile(r"\b(increases?|reduces?|boosts?|trims?|raises|lowers|cuts?)\b[\w\s.'()]{0,25}"
                            r"\b(holdings?|position|stake)\b", re.I)
_INITIATES_POS = re.compile(r"\binitiat\w+\b[\w\s.'()]{0,25}\bposition\b", re.I)
_DISCLOSES_HOLD = re.compile(r"\bdisclos\w+\b[\w\s.'()$]{0,25}\b(holdings?|position)\b", re.I)  # NB: not 'stake'
_PCT = re.compile(r"\d+(\.\d+)?\s*%")


def _is_holdings(h: str) -> bool:
    fund = re.search(_FUND, h, re.I)
    if fund and _HOLD_ACTION.search(h) and _HOLD_OBJECT.search(h):
        return True                                   # (a) fund + action + object
    if _SHARECOUNT.search(h) and _HOLD_ACTION.search(h):
        return True                                   # (b) explicit share-count filing
    if _PORTFOLIO_ADJ.search(h) and not _PCT.search(h):
        return True                                   # (c) portfolio-adjust verb + holdings, not a %-stake
    if _INITIATES_POS.search(h):
        return True                                   # (d) "initiates position in X"
    if _DISCLOSES_HOLD.search(h):
        return True                                   # (e) "discloses holding/position" (excludes 'stake')
    if _DOLLAR_POS.search(h):
        return True                                   # (f) "$X million stock position"
    return False


# ── routine analyst-rating stubs (spare up/downgrades — they can be material) ──────────────────
_ANALYST = re.compile(
    r"\bmaintain(s|ed)?\s+by\b"
    r"|\bnew\s+(buy|sell|hold|neutral|overweight|underweight)\s+rating\s+for\b"
    r"|\bprice\s+target\s+(raised|cut|lowered|boosted|increased|decreased|reduced|set)\s+to\s*\$"
    r"|\breiterat\w+\b[\w\s]{0,25}\brating\b", re.I)
_ANALYST_SPARE = re.compile(r"\b(upgrad|downgrad)\w*", re.I)


def _is_analyst_stub(h: str) -> bool:
    return bool(_ANALYST.search(h)) and not _ANALYST_SPARE.search(h)


# ── Zacks-style template listicles ────────────────────────────────────────────────────────────
_LISTICLE = re.compile(
    r"\bundervalued\s+right\s+now\b|\bstrong\s+momentum\s+stock\b|\bmomentum\s+stock\b"
    r"|\ba\s+strong\s+(buy|sell)\b|\bzacks\s+rank\b|\bmotley\s+fool\s+stock\s+advisor\b"
    # Zacks screener templates (caught here so they're FILTERED, not over-merged by the event-merge):
    r"|\bwhich\s+stock\s+should\b|\bvalue\s+investors\s+buy\b|\btrending\s+stock\b"
    r"|\bshould\s+value\s+investors\b", re.I)


def _is_listicle(h: str) -> bool:
    return bool(_LISTICLE.search(h))


# ── no-catalyst price stubs ───────────────────────────────────────────────────────────────────
_PRICE_STUB = re.compile(
    r"\bno\s+(specific\s+)?catalyst\s+(named|specified|in\b|identified|cited|disclosed)"
    r"|\bstock\s+movement\b[\w\s]{0,20}\b(examined|explainer|draws|coverage)\b"
    r"|\bbenchmarked\s+against\b[\w\s]{0,25}\bpeers\b"
    r"|\bheadline\s+too\s+truncated\b|\btoo\s+truncated\s+to\b", re.I)


def _is_price_stub(h: str) -> bool:
    return bool(_PRICE_STUB.search(h))


_CATEGORIES = (
    ("institutional_holdings", _is_holdings),
    ("analyst_stub", _is_analyst_stub),
    ("template_listicle", _is_listicle),
    ("price_stub", _is_price_stub),
)


def boilerplate_category(headline: str):
    """Return the boilerplate category name for a headline, or None if it is not boilerplate."""
    h = headline or ""
    for name, fn in _CATEGORIES:
        if fn(h):
            return name
    return None


def is_boilerplate(headline: str) -> bool:
    return boilerplate_category(headline) is not None


def keep_cluster(cluster) -> bool:
    """Keep unless EVERY headline is boilerplate. FactSet clusters are always kept (exempt)."""
    items = getattr(cluster, "items", [])
    if any(it.get("_is_factset") for it in items):
        return True
    heads = [it.get("title", "") for it in items if it.get("title")]
    if not heads:
        return True
    return not all(is_boilerplate(h) for h in heads)


def filter_clusters(clusters, logger=None) -> tuple[list, dict]:
    """Split into (kept, dropped_category_counts). A dropped cluster is tagged by the category of its
    (first) boilerplate headline. Logs a per-category breakdown."""
    kept, reasons = [], {}
    for c in clusters:
        if keep_cluster(c):
            kept.append(c)
            continue
        cat = next((boilerplate_category(it.get("title", "")) for it in c.items
                    if boilerplate_category(it.get("title", ""))), "boilerplate")
        reasons[cat] = reasons.get(cat, 0) + 1
    if logger:
        brk = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])) or "none"
        logger.info("pre-filter (category): %d → %d clusters (dropped %d boilerplate before LLM; %s)",
                    len(clusters), len(kept), sum(reasons.values()), brk)
    return kept, reasons
