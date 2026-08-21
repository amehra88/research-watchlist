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
  • sell-side rating actions — "Maintained by Barclays — PT raised to $290", "New Buy Rating for X",
    and (since 2026-08-19, at operator instruction) bare up/downgrades and price-target moves too.
    Reiterations are always dropped; a rating CHANGE survives only when the headline gives a
    rationale other than valuation or the target change itself. See the category's own comment.
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


# ── sell-side rating actions ──────────────────────────────────────────────────────────────────
# OPERATOR DECISION 2026-08-19 — this REVERSES the earlier "up/downgrades are SPARED" rule above.
# Rationale (operator, verbatim): "the sell side is the last priority and only if this rationale
# for the upgrade or downgrade other than valuation or price target change". So:
#
#   • reiterations / maintains / assumed-or-resumed coverage  → ALWAYS dropped. Restating an
#     existing rating carries no new information by construction.
#   • upgrades / downgrades / initiations / price-target moves → dropped UNLESS the headline
#     states a rationale that is not valuation and not the target change itself. "Morgan Stanley
#     downgrades Baidu ... on advertising weakness" survives (fundamental reason); "Apple receives
#     rare analyst upgrade with price target raised to $400" does not (the PT *is* the story).
#
# Survivors are NOT promoted by surviving here — rank.py ranks rating actions LAST, so they only
# occupy a slot once every non-rating story has one. Failure direction is deliberate: an
# unrecognized rationale falls through to KEEP, so the cost of a regex miss is a low-ranked item,
# never a dropped material story.
_RATING_WORD = (r"(buy|sell|hold|neutral|overweight|underweight|outperform|underperform|"
                r"equal[\s-]?weight|market\s+perform|sector\s+perform|accumulate)")
# Broker/research-shop names are used ONLY as a CONTEXT signal, never alone — they must co-occur
# with a rating verb. That keeps "Bank of America opens a data center" out of this category.
_BROKER = (r"(goldman|morgan\s+stanley|j\.?p\.?\s*morgan|jpmorgan|barclays|citigroup|citi\b|ubs|"
           r"bernstein|jefferies|stifel|wedbush|baird|piper|raymond\s+james|bofa|"
           r"bank\s+of\s+america|deutsche\s+bank|mizuho|susquehanna|cantor|td\s+cowen|cowen|"
           r"evercore|truist|oppenheimer|keybanc|rosenblatt|melius|loop\s+capital|new\s*street|"
           r"redburn|hsbc|wells\s+fargo|zacks|argus|cfra|moffett|northland|craig[\s-]?hallum|"
           r"needham|btig|guggenheim|william\s+blair|canaccord|scotiabank|\brbc\b|"
           r"nomura|macquarie|daiwa|wolfe|da\s+davidson|citizens|morningstar|"
           r"\bbmo\b|cibc|phillip\s+securities)")

# (a) a rating RESTATEMENT — no new information, dropped unconditionally
_RATING_RESTATE = re.compile(
    r"\breiterat\w*|\bmaintain(s|ed|ing)?\b|\breaffirm\w*|\bassum\w+\s+coverage\b|"
    r"\bresum\w+\s+coverage\b|\bkeeps?\s+\w+\s+rating\b", re.I)
# (b) a rating CHANGE / initiation / price-target move — conditional on a non-valuation rationale
_RATING_CHANGE_VERB = re.compile(r"\b(upgrad|downgrad|initiat)\w*", re.I)
# Non-rating uses of the same words, ERASED from the headline before any rating test. "upgrade
# cycle" is a product cycle ("Why BofA Expects a $95B Beat and Multi-Quarter Upgrade Cycle" was the
# single false drop in the 2026-08 back-test); the rest are capex/infrastructure senses. A negative
# lookahead does NOT work here — \w* backtracks around it — so erase, then test.
_NON_RATING_SENSE = re.compile(
    r"\b(upgrade|upgrades|upgrading)\s+(cycle|cycles|path|program|programme|project|projects|"
    r"plan|plans|work|works)\b"
    r"|\b(infrastructure|network|fab|equipment|capacity|software|hardware|system|systems|grid|"
    r"platform|memory|plant|facility|site)\s+upgrade\w*\b", re.I)
_PT_VERB = (r"(rais\w+|cuts?|lower\w+|boost\w+|increas\w+|decreas\w+|reduc\w+|sets?|trim\w+|"
            r"hikes?|slash\w+|up(s|ped|ping)?|lift\w+|bump\w+|jumps?|drops?|climbs?|slides?|"
            r"moves?|reset\w*)")
_PT_ACTION = re.compile(
    r"\b(price\s+)?target(s)?\b[\w\s'()$.,%-]{0,25}?\b" + _PT_VERB + r"\b"
    r"|\b" + _PT_VERB + r"\b[\w\s'()$.,%-]{0,25}?\b(price\s+)?target(s)?\b"
    r"|\bprice\s+target(s)?\b[\w\s'()$.,%-]{0,20}?\bto\s*\$"
    r"|\bnew\s+" + _RATING_WORD + r"\s+rating\s+for\b", re.I)
# NB the broker group MUST be word-bounded: unanchored, "ubs" matches inside "h(ubs)" and turned
# "Vietnam plans infrastructure upgrades around Samsung manufacturing hubs" into a rating action.
_ANALYST_CTX = re.compile(r"\banalysts?\b|\brating\b|\bcoverage\b|\bprice\s+target\b|"
                          r"\bwall\s+street\b|\bsell[\s-]side\b|\b(?:" + _BROKER + r")\b", re.I)

# rationale connectors — the tail after the LAST one is the stated reason
_RATIONALE = re.compile(r"\b(on|after|following|amid|citing|cites|due\s+to|because\s+of|over|as)\b",
                        re.I)
# a reason built ONLY from these tokens is a valuation / price-target reason, i.e. not a reason
_VALUATION_VOCAB = {
    "valuation", "valuations", "price", "prices", "target", "targets", "pt", "upside", "downside",
    "fair", "value", "multiple", "multiples", "rich", "cheap", "expensive", "stretched", "risk",
    "reward", "limited", "share", "shares", "stock", "stocks", "run", "rally", "selloff", "gains",
    "gain", "decline", "declines", "drop", "move", "moves", "premium", "discount", "concerns",
    "concern", "worries", "level", "levels", "outperformance", "underperformance", "weakness",
    "strength", "high", "low", "highs", "lows", "recent", "current", "further", "more", "less",
    "increase", "increases", "decrease", "decreases", "rise", "rises", "hike", "hikes", "boost",
    "cut", "cuts", "street", "consensus", "estimate", "estimates", "sentiment", "optimism",
    "bullish", "bearish", "conviction", "accelerates", "why", "here",
}
_STOP_TAIL = {"the", "a", "an", "of", "in", "to", "its", "their", "his", "her", "and", "or",
              "for", "with", "at", "by", "from", "s", "it", "that", "this", "new", "com",
              "investing", "benzinga", "reuters", "barron", "zen", "tipranks", "seeking", "alpha"}


def _rationale_tail(h: str) -> str:
    """Text after the LAST rationale connector — the stated reason, if any."""
    last = None
    for m in _RATIONALE.finditer(h):
        last = m
    return h[last.end():].strip() if last else ""


_TAIL_FURNITURE = None          # built lazily from _BROKER + the rating vocabulary


def _strip_furniture(tail: str) -> str:
    """Remove broker names, rating verbs and rating words from a reason clause. What is left is
    the ACTUAL stated reason, which is what the valuation test should judge."""
    global _TAIL_FURNITURE
    if _TAIL_FURNITURE is None:
        _TAIL_FURNITURE = re.compile(
            r"\b(?:" + _BROKER + r")\b|\b(?:" + _RATING_WORD + r")\b|"
            r"\b(upgrad|downgrad|initiat|reiterat|maintain|rat(e|es|ed|ing)|analysts?|coverage|"
            r"point\w*|see\w*|say\w*|call\w*|flag\w*|cit\w*|note\w*|which|that|its|firm|"
            r"indicat\w*|impl\w*|suggest\w*|opinion\w*|reset\w*|draw\w*|lofty)\w*\b",
            re.I)
    return _TAIL_FURNITURE.sub(" ", tail)


def _is_valuation_only(tail: str) -> bool:
    """True when every content word in the reason is valuation / price-target vocabulary.

    Subset test, not keyword search: "recent share price gains" is valuation-only, while
    "ad revenue decline" is not (revenue survives the vocabulary), so it is kept."""
    toks = [w for w in re.split(r"[^a-z0-9]+", _strip_furniture(tail).lower())
            if w and w not in _STOP_TAIL and not w.isdigit()]
    if not toks:
        return True                                    # a connector with no reason is no reason
    return all(t in _VALUATION_VOCAB for t in toks)


def _is_analyst_stub(h: str) -> bool:
    h = _NON_RATING_SENSE.sub(" ", h)
    ctx = bool(_ANALYST_CTX.search(h))
    if _RATING_RESTATE.search(h) and ctx:
        return True                                    # (a) restatement — always noise
    is_change = bool(_PT_ACTION.search(h)) or (bool(_RATING_CHANGE_VERB.search(h)) and ctx)
    if not is_change:
        return False
    tail = _rationale_tail(h)                          # (b) change: keep only for a real reason
    if not tail:
        return True
    return _is_valuation_only(tail)


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
    r"|\bheadline\s+too\s+truncated\b|\btoo\s+truncated\s+to\b"
    # MarketWatch daily-move template: "X Inc. stock outperforms competitors on strong trading day",
    # "X stock rises Monday, outperforms market" — a price print with no event behind it.
    r"|\bstock\s+(out|under)performs?\b"
    r"|\bstock\s+(rises?|falls?|climbs?|slides?|drops?|gains?|declines?)\s+"
    r"(monday|tuesday|wednesday|thursday|friday)\b", re.I)


def _is_price_stub(h: str) -> bool:
    return bool(_PRICE_STUB.search(h))


_CATEGORIES = (
    ("institutional_holdings", _is_holdings),
    ("analyst_stub", _is_analyst_stub),        # NB: NOT FactSet-exempt — see _NO_FACTSET_EXEMPTION
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


# Categories the FactSet exemption does NOT cover. StreetAccount carries a high volume of routine
# rating actions, so exempting every FactSet cluster (as the original blanket rule did) let the
# sell-side noise the operator asked to remove straight back in through the second channel. The
# exemption still holds for every other category — FactSet's 13F/listicle/price-stub rate is
# negligible and its curation is worth trusting there.
_NO_FACTSET_EXEMPTION = {"analyst_stub"}


def cluster_category(cluster):
    """The boilerplate category labelling a cluster whose headlines are ALL boilerplate, or None
    if any headline is a real story. Mixed-category all-boilerplate clusters take the dominant
    category (they still drop — only the reason label is approximate)."""
    heads = [it.get("title", "") for it in getattr(cluster, "items", []) if it.get("title")]
    if not heads:
        return None
    cats = [boilerplate_category(h) for h in heads]
    if any(c is None for c in cats):
        return None                                    # a real story in the cluster — keep it
    return max(set(cats), key=cats.count)              # all boilerplate; label by the dominant one


def keep_cluster(cluster) -> bool:
    """Keep unless EVERY headline is boilerplate of ONE category. FactSet clusters are exempt for
    every category except those in _NO_FACTSET_EXEMPTION."""
    cat = cluster_category(cluster)
    if cat is None:
        return True
    if cat in _NO_FACTSET_EXEMPTION:
        return False                                   # rating actions drop from BOTH channels
    # all-boilerplate in an exempt category: kept ONLY because FactSet curated it
    return any(it.get("_is_factset") for it in getattr(cluster, "items", []))


def filter_clusters(clusters, logger=None) -> tuple[list, dict]:
    """Split into (kept, dropped_category_counts). A dropped cluster is tagged by the category of its
    (first) boilerplate headline. Logs a per-category breakdown."""
    kept, reasons = [], {}
    for c in clusters:
        if keep_cluster(c):
            kept.append(c)
            continue
        cat = cluster_category(c) or "boilerplate"
        reasons[cat] = reasons.get(cat, 0) + 1
    if logger:
        brk = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])) or "none"
        logger.info("pre-filter (category): %d → %d clusters (dropped %d boilerplate before LLM; %s)",
                    len(clusters), len(kept), sum(reasons.values()), brk)
    return kept, reasons
