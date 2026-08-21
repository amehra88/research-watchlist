"""
render — plain-text output for the 07:00 combined digest. Zero LLM calls, pure formatting.

LAYOUT IS AN OPERATOR DECISION, not a suggestion:
    Fear & Greed one-liner  ->  Block A (metrics, FACTS ONLY)  ->  Block B (analysis)
    ... and the full table at the very END of the email, after NEWS FLOW.

That last requirement is why this module emits TWO files. combine_and_send.py assembles
sections in list order, so the only way to put the table last is to register it as its own
trailing section:

    ('ETF FLOWS & CROWDING', '.../report_etfflows_{date}.txt')        <- after ETF UPDATE
    ...
    ('ETF FLOW DETAIL',      '.../report_etfflows_table_{date}.txt')  <- last entry

BLOCK A / BLOCK B SEPARATION IS THE OTHER OPERATOR DECISION. Block A states what the flows
WERE; Block B says what it might mean. They are never interleaved — the operator asked for
metrics that stand on their own, with interpretation clearly downstream of them.

LANGUAGE DISCIPLINE: this is a positioning monitor, not a forecast. Flow-induced demand
mean-reverts over multi-week horizons, so Block B describes CROWDING STATE and never
predicts direction. Until the validation gate confirms the sign, nothing here may say a
flow implies a future return.
"""
from __future__ import annotations

from typing import Sequence

from . import LONG_HORIZON, SHORT_HORIZON

WIDTH = 86


# ── formatting primitives ─────────────────────────────────────────────────────

def usd(v: float | None) -> str:
    """Compact signed USD. '-' for missing, which must not read as zero."""
    if v is None:
        return "-"
    sign = "-" if v < 0 else "+"
    a = abs(v)
    for cutoff, suffix, div in ((1e12, "T", 1e12), (1e9, "B", 1e9), (1e6, "M", 1e6)):
        if a >= cutoff:
            return f"{sign}${a / div:,.1f}{suffix}"
    return f"{sign}${a:,.0f}"


def bps(v: float | None) -> str:
    return "-" if v is None else f"{v:+.1f}"


def sigma(z: float | None, degraded: bool = False) -> str:
    """Sigma label, or an explicit refusal.

    'n/a' when the MAD floor bound or the baseline was too short — printing a number there
    would be inventing precision the data does not support.
    """
    if degraded or z is None:
        return "n/a"
    return f"{z:+.1f}σ"


def pct(p: float | None) -> str:
    if p is None:
        return "-"
    return f"{p:.1f}"


def _rule(ch: str = "─") -> str:
    return ch * WIDTH


# ── Block A: facts ────────────────────────────────────────────────────────────

def block_a(report: dict) -> str:
    """Metrics only. No interpretation, no adjectives that imply a direction."""
    out: list[str] = []
    as_of = report.get("as_of") or "unknown"

    out.append("ETF FLOWS & CROWDING")
    # The spec requires the as-of date be PRINTED, never assumed to be T-1: at a 05:30 fetch
    # the newest available flow date genuinely varies.
    out.append(f"Flows as of {as_of}  (FactSet, net creations/redemptions, T+1)")
    out.append(_rule())

    alerts = report.get("alerts") or []
    if alerts:
        out.append(f"ALERTS ({len(alerts)}):")
        for a in alerts:
            corro = f" — {a.corroboration}" if getattr(a, "corroboration", "") else ""
            out.append(
                f"  {a.ticker:<5} {a.horizon:>2}d  {a.direction:<7} "
                f"{usd(a.flow_usd):>10}  {bps(a.flow_bps):>7}bp  "
                f"{sigma(a.z):>6}  {pct(a.percentile):>5}pctile  [{a.basis}]{corro}"
            )
        suppressed = report.get("suppressed", 0)
        if suppressed:
            # Repo convention: no silent caps.
            out.append(f"  ... {suppressed} further alert(s) suppressed by the daily cap.")
    else:
        out.append("ALERTS: none — no trigger-tier ETF cleared the threshold.")

    out.append("")

    br = report.get("breadth") or {}
    for h in (SHORT_HORIZON, LONG_HORIZON):
        b = br.get(h)
        if b and b.get("pct") is not None:
            out.append(f"Breadth {h:>2}d: {b['pct']:.0f}% of trigger tier with net inflow "
                       f"({b['positive']}/{b['measured']} measured)")

    pairs = report.get("pairs") or []
    if pairs:
        out.append("")
        out.append("Sibling spreads (trading vehicle vs allocation):")
        for p in pairs:
            out.append(f"  {p['name']:<18} {SHORT_HORIZON}d {bps(p.get('short')):>7}bp   "
                       f"{LONG_HORIZON}d {bps(p.get('long')):>7}bp")

    factor = report.get("factor_rotation") or []
    if factor:
        out.append("")
        out.append(f"Factor complex ({LONG_HORIZON}d, bps of AUM):")
        out.append("  " + "   ".join(f"{f['ticker']} {bps(f['bps'])}" for f in factor))

    warnings = report.get("warnings") or []
    if warnings:
        out.append("")
        for w in warnings:
            out.append(f"  ! {w}")

    return "\n".join(out)


# ── Block B: analysis ─────────────────────────────────────────────────────────

def block_b(report: dict) -> str:
    """Interpretation, kept structurally separate from Block A per the operator's request.

    Describes POSITIONING STATE. It must not tell the reader what happens next.
    """
    out: list[str] = ["", "CROWDING READ", _rule()]

    quadrants = report.get("quadrants") or {}
    alerts = report.get("alerts") or []

    if not alerts and not quadrants:
        out.append("Nothing at extreme positioning today. No crowded vehicle to decompose.")
        return "\n".join(out)

    labelled = {
        "sustained crowding": [],
        "crowded but stalling": [],
        "fresh rotation": [],
        "neglected": [],
    }
    for ticker, q in sorted(quadrants.items()):
        if q in labelled:
            labelled[q].append(ticker)

    if labelled["sustained crowding"]:
        out.append(f"Sustained crowding ({LONG_HORIZON}d and {SHORT_HORIZON}d both elevated): "
                   + ", ".join(labelled["sustained crowding"]))
        out.append("  Accumulated positioning with money still arriving — the most")
        out.append("  reversal-prone cell in the 2x2.")
    if labelled["crowded but stalling"]:
        out.append(f"Crowded but stalling ({LONG_HORIZON}d high, {SHORT_HORIZON}d soft): "
                   + ", ".join(labelled["crowded but stalling"]))
        out.append("  The position is on but the buying has stopped. Distribution risk.")
    if labelled["fresh rotation"]:
        out.append(f"Fresh rotation ({SHORT_HORIZON}d high, {LONG_HORIZON}d not yet): "
                   + ", ".join(labelled["fresh rotation"]))
    if labelled["neglected"]:
        out.append("Neglected (both horizons soft): " + ", ".join(labelled["neglected"]))

    # Deduped by ticker: an ETF can appear in `alerts` more than once, and repeating the same
    # divergence sentence per alert reads as two separate findings about one move.
    for ticker in sorted({a.ticker for a in alerts}):
        div = (report.get("divergence") or {}).get(ticker)
        if div == "accumulation":
            out.append(f"  {ticker}: inflow against a falling tape — accumulation, not chase.")
        elif div == "distribution":
            out.append(f"  {ticker}: outflow against a rising tape — distribution into strength.")

    out.append("")
    out += _lookthrough_lines(report.get("lookthrough") or [],
                              report.get("lookthrough_note", ""))
    out.append("")
    out.append("Read as POSITIONING, not direction: ETF flow is largely non-fundamental")
    out.append("demand and mean-reverts over multi-week horizons. Thresholds are provisional")
    out.append("pending calibration against backfilled history.")
    return "\n".join(out)


def _days(d: float | None) -> str:
    """Days of ADV. '?' when the name's liquidity is unknown — never silently 0.

    Sub-0.01 magnitudes print as '<0.01d' rather than '+0.00d'. Real mega-cap decompositions
    land there constantly (a 3σ $4.1B SMH inflow is 0.04 days of NVDA volume), and '-0.00d'
    reads as an exact zero when the true statement is "far too small to matter" — which is
    itself the finding, and deserves to be legible rather than look like a rounding artifact.
    """
    if d is None:
        return "?"
    if d != 0 and abs(d) < 0.01:
        return f"<0.01d" if d > 0 else f">-0.01d"
    return f"{d:+.2f}d"


def _lookthrough_lines(results, note: str = "") -> list[str]:
    """Phase 2 decomposition, rendered only for ETFs that actually alerted.

    Sized in DAYS OF ADV rather than dollars: "$881M of implied NVDA demand" is unreadable
    without knowing that it is 0.04 of a day's volume, i.e. nothing. The whole point of the
    unit is to stop a large dollar figure from implying a large effect.
    """
    if not results:
        # "not available" and "nothing to decompose" are different facts. Reporting the
        # second when the first is true would claim we looked and found nothing worth saying.
        return [f"Constituent look-through: {note or 'no alerting ETF was eligible for '
                                                    'decomposition.'}"]

    out: list[str] = ["WHAT THE CROWDED VEHICLE IS BUYING"]
    for r in results:
        flow = usd(r.get("flow_usd"))
        out.append(f"  {r['etf']} {r['horizon']}d {r.get('direction', '')} {flow} "
                   f"(weights as of {r.get('weights_as_of') or 'unknown'}):")
        if r.get("reconstitution_warning"):
            # A rebalance reshuffles which names are held and reads exactly like a flow event.
            out.append("    ! near a semi-annual reconstitution — some of this is rebalance, "
                       "not demand")

        for d in (r.get("demands") or [])[:6]:
            mark = " *HELD*" if d.in_portfolio else ""
            out.append(f"    {d.ticker:<6} {d.weight_pct:>5.1f}%  "
                       f"{usd(d.implied_usd):>9}  {_days(d.days_of_adv):>7} ADV{mark}")

        held = r.get("held") or []
        if held:
            names = ", ".join(f"{d.ticker} ({_days(d.days_of_adv)} ADV)" for d in held)
            out.append(f"    In the book: {names}")
        else:
            out.append("    In the book: none of the top names are BCTK holdings.")
    out.append("")
    out.append("  Days of ADV = implied demand / the name's own dollar volume. Weights are")
    out.append("  month-end and drift after a sharp move; synthetic ETFs are never decomposed")
    out.append("  because swap-backed creations buy no underlying shares.")
    return out


# ── the full table (trailing section) ─────────────────────────────────────────

def full_table(report: dict) -> str:
    """Every tracked ETF. Its own file so it can sit at the END of the email."""
    rows: Sequence[dict] = report.get("rows") or []
    out = ["ETF FLOW DETAIL — full universe",
           f"Flows as of {report.get('as_of') or 'unknown'}",
           _rule()]
    hdr = (f"{'ETF':<6}{'tier':<9}{SHORT_HORIZON}d flow    "
           f"{SHORT_HORIZON}d bp   {SHORT_HORIZON}d z   "
           f"{LONG_HORIZON}d flow   {LONG_HORIZON}d bp  {LONG_HORIZON}d z  quadrant")
    out.append(hdr)
    out.append(_rule("·"))

    if not rows:
        out.append("(no rows — fetch produced no usable data)")
        return "\n".join(out)

    for r in rows:
        out.append(
            f"{r.get('ticker', '?'):<6}"
            f"{r.get('tier', '')[:8]:<9}"
            f"{usd(r.get('flow_short_usd')):>10}  "
            f"{bps(r.get('bps_short')):>7}  "
            f"{sigma(r.get('z_short'), r.get('degraded_short', False)):>6}  "
            f"{usd(r.get('flow_long_usd')):>10}  "
            f"{bps(r.get('bps_long')):>7}  "
            f"{sigma(r.get('z_long'), r.get('degraded_long', False)):>6}  "
            f"{r.get('quadrant') or '-'}"
        )

    notes = report.get("table_notes") or []
    if notes:
        out.append("")
        for n in notes:
            out.append(f"  ! {n}")
    out.append("")
    out.append("n/a in a z column = the robust baseline could not support a sigma figure")
    out.append("(flat flow history or too little data), not a reading of zero.")
    return "\n".join(out)


def render_main(report: dict) -> str:
    """The section inserted after ETF UPDATE: Fear & Greed -> Block A -> Block B."""
    fg_line = report.get("fear_greed_line") or ""
    parts = [fg_line, ""] if fg_line else []
    parts.append(block_a(report))
    parts.append(block_b(report))
    return "\n".join(parts).rstrip() + "\n"


def render_table(report: dict) -> str:
    return full_table(report).rstrip() + "\n"


def render_note(report: dict) -> str:
    """Markdown mirror for notes/flows/{date}-flows.md.

    MUST lead with '##', not '#': the pg chunker keys off `##` headings and a note that
    opens with a single hash indexes to zero chunks (see memory chunker-v3-awareness-gap).
    """
    as_of = report.get("as_of") or "unknown"
    body = [f"## ETF flows & crowding — {as_of}", ""]
    if report.get("fear_greed_line"):
        body += [report["fear_greed_line"], ""]
    body += ["```", block_a(report), block_b(report), "```", "",
             "## Full universe", "", "```", full_table(report), "```", ""]
    return "\n".join(body)
