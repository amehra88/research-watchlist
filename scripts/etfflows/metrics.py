"""
metrics — the arithmetic of the flow/crowding monitor. Pure functions, no I/O, no LLM.

Everything here is deliberately testable in isolation because the interesting failures are
statistical, not operational: a MAD of zero emitting +/-inf sigma, a z-score that is really
measuring AUM growth, an AUM denominator that already contains the flow it normalises.

TWO CONVENTIONS THAT ARE EASY TO GET WRONG AND EXPENSIVE TO GET WRONG:

1. The z-score is computed on the NORMALISED (bps-of-AUM) series, not on raw USD flow.
   Over a 3-year baseline a fund whose AUM tripled shows mechanically larger USD flows;
   z-scoring raw dollars would read that growth as an anomaly. Verified relevant: XLK's
   AUM moved 124.5B -> 115.4B over three months in 2026 alone.

2. The denominator is PRIOR-period AUM — AUM as of the START of the window, which does not
   already contain the flow being normalised. Using end-of-window AUM shrinks every large
   inflow's bps figure precisely when it matters most.

Verified against FactSet 2026-08-19 (XLK, July 2026): the sum of daily `fundFlows`
($1,414.2M) reconciles with delta-shares-outstanding (8,100,000) times an implied NAV of
$174.60 — i.e. FactSet's daily flows follow the ICI convention flow_t = dSO_t * NAV_{t-1}.
That is why roll_forward_aum below adds flow at NAV and why the reconciliation holds.

MISSING vs ZERO: FactSet returns `null` for a date whose flow is not yet available (T is
always null at a 05:30 fetch) and a genuine `0.0` for a real no-creation/redemption day
(2 of 23 July days for XLK). These MUST stay distinct — folding null into 0.0 silently
drags every rolling window toward zero and reads as "no flow" instead of "no data".
`None` means missing throughout this module.
"""
from __future__ import annotations

from typing import NamedTuple, Sequence

from . import (
    MAD_FLOOR_BPS,
    MAD_TO_SIGMA,
    MIN_BASELINE_OBS,
    MIN_WINDOW_COVERAGE,
)

Num = float | int | None


# ── basic robust statistics ───────────────────────────────────────────────────

def median(values: Sequence[float]) -> float:
    """Median of a non-empty sequence. Raises on empty — a silent 0.0 would poison a z-score."""
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def mad(values: Sequence[float], centre: float | None = None) -> float:
    """Median absolute deviation (RAW — not yet scaled to sigma units)."""
    if not values:
        raise ValueError("mad of empty sequence")
    c = median(values) if centre is None else centre
    return median([abs(v - c) for v in values])


class ZResult(NamedTuple):
    """z is None whenever we refuse to claim a sigma figure.

    `degraded=True` means the caller MUST NOT print a sigma label; report the percentile
    instead. This is the difference between "we don't know" and "zero", and rendering has
    to be able to tell them apart.
    """
    z: float | None
    percentile: float | None
    degraded: bool
    reason: str          # '' | 'mad_floor' | 'insufficient_baseline'
    centre: float | None
    scale: float | None  # MAD scaled to sigma units, after the floor is applied


def percentile_rank(x: float, baseline: Sequence[float]) -> float | None:
    """Empirical percentile of x within baseline, 0..100.

    Reported in preference to sigma because "99.4th percentile, largest since Nov-2025" is
    both more honest and more readable than "2.8 sigma" when the distribution is fat-tailed.
    Midpoint convention so ties don't systematically over- or under-state.
    """
    if not baseline:
        return None
    below = sum(1 for v in baseline if v < x)
    equal = sum(1 for v in baseline if v == x)
    return 100.0 * (below + 0.5 * equal) / len(baseline)


def robust_z(x: float, baseline: Sequence[float],
             mad_floor: float = MAD_FLOOR_BPS,
             min_obs: int = MIN_BASELINE_OBS) -> ZResult:
    """Robust z-score of x against baseline, in TRUE SIGMA UNITS.

    MAD is multiplied by MAD_TO_SIGMA (1.4826) so that thresholds expressed as "3 sigma"
    mean three Gaussian-equivalent standard deviations. Omitting that factor would make a
    nominal 3.0 threshold behave like ~2.0 and roughly quadruple the alert rate.

    Degrades rather than lying:
      - baseline too short          -> z=None, reason='insufficient_baseline'
      - MAD at/below the floor      -> z=None, reason='mad_floor'   (percentile still returned)
    """
    baseline = [v for v in baseline if v is not None]
    pct = percentile_rank(x, baseline) if baseline else None

    if len(baseline) < min_obs:
        return ZResult(None, pct, True, "insufficient_baseline", None, None)

    centre = median(baseline)
    scale = mad(baseline, centre) * MAD_TO_SIGMA

    if scale <= mad_floor:
        # Long runs of near-identical or zero flow. Emitting (x-centre)/~0 would produce a
        # meaningless +/-inf-ish sigma and eat the entire alert budget on the quietest funds.
        return ZResult(None, pct, True, "mad_floor", centre, scale)

    return ZResult((x - centre) / scale, pct, False, "", centre, scale)


# ── windows ───────────────────────────────────────────────────────────────────

def rolling_sums(values: Sequence[Num], window: int,
                 min_coverage: float = MIN_WINDOW_COVERAGE) -> list[float | None]:
    """Trailing-window sums, aligned to the RIGHT edge (index i covers values[i-window+1..i]).

    A window is None unless at least `min_coverage` of its slots are non-missing. Missing
    slots are skipped, not zero-filled — see the MISSING vs ZERO note in the module docstring.
    Returns a list the same length as `values`; the first window-1 entries are None.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    out: list[float | None] = []
    need = max(1, int(round(window * min_coverage)))
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
            continue
        chunk = values[i - window + 1: i + 1]
        present = [v for v in chunk if v is not None]
        out.append(float(sum(present)) if len(present) >= need else None)
    return out


def most_recent_exceedance(dates: Sequence[str], values: Sequence[Num],
                           x: float, exclude_last: int = 1) -> str | None:
    """Most recent date (excluding the last `exclude_last` points) whose value was at least
    as extreme as x, in the same direction. Powers "largest since Nov-2025".

    Returns None when x is the most extreme in the series — the caller should then say
    "largest on record" scoped to the baseline length, not invent a date.
    """
    end = len(values) - exclude_last
    for i in range(end - 1, -1, -1):
        v = values[i]
        if v is None:
            continue
        if (x >= 0 and v >= x) or (x < 0 and v <= x):
            return dates[i]
    return None


# ── normalisation ─────────────────────────────────────────────────────────────

def to_bps(flow_usd: float | None, aum_usd: float | None) -> float | None:
    """Flow as basis points of AUM. `aum_usd` MUST be prior-period AUM (start of window)."""
    if flow_usd is None or not aum_usd:
        return None
    return 1e4 * flow_usd / aum_usd


def roll_forward_aum(dates: Sequence[str], navs: Sequence[Num], flows: Sequence[Num],
                     month_end_aum: dict[str, float]) -> list[float | None]:
    """Daily AUM series, anchored on reported month-end AUM and rolled forward between anchors.

    FactSet exposes AUM at month-end only (`frequency` accepts MTD/M/CQTD/CQ/CYTD/CY — there
    is no daily option), but flow/AUM needs a daily denominator. Between anchors:

        AUM_t = AUM_{t-1} * (1 + NAV return_t) + flow_t

    We RE-ANCHOR at every month-end rather than compounding across the whole series, so
    drift cannot accumulate beyond a single month.

    IMPORTANT: pass `shareClassAUMReported`, never `fundLevelAUM`. Verified 2026-08-19 —
    VOO reports fundLevelAUM $1.70T against shareClassAUMReported $994B, so fund-level would
    understate every VOO flow/AUM figure by ~41%.

    Dates with no anchor at or before them stay None rather than being back-filled.
    """
    out: list[float | None] = []
    running: float | None = None
    prev_nav: float | None = None

    for i, d in enumerate(dates):
        nav = navs[i] if i < len(navs) else None
        flow = flows[i] if i < len(flows) else None

        if d in month_end_aum:                     # hard anchor wins outright
            running = float(month_end_aum[d])
        elif running is not None:
            if prev_nav and nav:
                running *= (nav / prev_nav)        # market move
            if flow is not None:
                running += flow                    # creations/redemptions at NAV (ICI convention)

        out.append(running)
        if nav is not None:
            prev_nav = nav
    return out


# ── derived readings ──────────────────────────────────────────────────────────

def window_return(navs: Sequence[Num], window: int) -> float | None:
    """Simple NAV return over the trailing window, right-aligned on the last point."""
    if len(navs) < window + 1:
        return None
    end = navs[-1]
    start = navs[-(window + 1)]
    if end is None or not start:
        return None
    return (end / start) - 1.0


def divergence(flow: float | None, ret: float | None) -> str | None:
    """Sign of flow against sign of the same-window return.

    The two mixed cases are the informative ones: money arriving into a falling tape is
    accumulation; money leaving a rising tape is distribution. Same-sign readings are
    just trend-following and are labelled as such.
    """
    if flow is None or ret is None:
        return None
    if flow > 0 and ret < 0:
        return "accumulation"      # inflow on a down tape
    if flow < 0 and ret > 0:
        return "distribution"      # outflow on an up tape
    if flow > 0 and ret > 0:
        return "confirmation"
    if flow < 0 and ret < 0:
        return "capitulation"
    return "flat"


def breadth(flows_by_ticker: dict[str, float | None]) -> tuple[float | None, int, int]:
    """Share of names with positive flow -> (pct or None, positive_count, measured_count).

    A risk-appetite gauge over the trigger tier. Names with a missing reading are excluded
    from BOTH numerator and denominator so a data gap cannot masquerade as an outflow.
    """
    measured = [v for v in flows_by_ticker.values() if v is not None]
    if not measured:
        return None, 0, 0
    pos = sum(1 for v in measured if v > 0)
    return 100.0 * pos / len(measured), pos, len(measured)


def pair_spread(lead_bps: float | None,
                against_bps: Sequence[float | None]) -> float | None:
    """Lead-minus-siblings spread in bps.

    SPY absorbs hedging and trading demand that IVV/VOO do not; a wide positive spread is a
    trading-vehicle event, while the two moving together is a genuine allocation shift.
    Siblings are averaged (not summed) so the spread stays in comparable bps units.
    """
    if lead_bps is None:
        return None
    present = [v for v in against_bps if v is not None]
    if not present:
        return None
    return lead_bps - (sum(present) / len(present))


def crowding_quadrant(short_z: float | None, long_z: float | None,
                      hi: float = 1.0, lo: float = -1.0) -> str | None:
    """The 5d x 63d 2x2 that IS the crowding measure.

    63d high + 5d high -> sustained crowding, the most reversal-prone cell.
    63d high + 5d low  -> crowded but stalling: accumulated position, buying has stopped.
    """
    if short_z is None or long_z is None:
        return None
    if long_z >= hi and short_z >= hi:
        return "sustained crowding"
    if long_z >= hi and short_z <= lo:
        return "crowded but stalling"
    if long_z <= lo and short_z >= hi:
        return "fresh rotation"
    if long_z <= lo and short_z <= lo:
        return "neglected"
    return "neutral"
