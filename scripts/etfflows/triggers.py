"""
triggers — decides what, if anything, is worth waking the operator for. Pure functions.

THE MULTIPLE-COMPARISONS PROBLEM IS THE WHOLE DESIGN. 28 trigger-eligible ETFs x 2 horizons
is ~56 tests every morning. At a nominal 2 sigma that is ~2 false alerts PER DAY from noise
alone, which trains the reader to skip the section within a fortnight. Three mechanisms keep
the budget near one alert per week:

  1. TIERING     — only the trigger tier may fire. Context names never alert on their own.
  2. THRESHOLDS  — 3 sigma standalone; 2 sigma only with independent corroboration.
  3. HYSTERESIS  — see below. This is the one that is easy to omit and expensive to omit.

WHY HYSTERESIS IS NOT OPTIONAL: a 63-day rolling sum on day t and day t+1 shares 62 of its
63 days, so consecutive z-scores are nearly identical by construction. Without a re-arm rule
a single crowding episode re-fires every morning for weeks, permanently occupying the daily
cap and crowding out genuinely new events. It also corrupts calibration — counting raw
alert-days over backfilled history reads enormously high and tempts you into over-tightening
the threshold, which then suppresses real episodes. CALIBRATE ON EPISODES, NOT ALERT-DAYS.

A (ticker, horizon) that has fired is DISARMED until its |z| falls back below RE_ARM_SIGMA,
and additionally cannot re-fire within ALERT_COOLDOWN_DAYS.

The alert cap truncates by severity, and truncation is ALWAYS reported (repo convention:
no silent caps).
"""
from __future__ import annotations

from typing import NamedTuple, Sequence

from . import (
    ALERT_COOLDOWN_DAYS,
    CORROBORATED_SIGMA,
    MAX_ALERTS_PER_DAY,
    RE_ARM_SIGMA,
    STANDALONE_SIGMA,
)


class Reading(NamedTuple):
    """One (ticker, horizon) measurement for one date."""
    ticker: str
    horizon: int
    z: float | None
    percentile: float | None
    flow_usd: float | None
    flow_bps: float | None
    divergence: str | None      # 'accumulation' | 'distribution' | ...
    tier: str                   # 'trigger' | 'context'
    synthetic: bool = False
    min_history_ok: bool = True
    degraded: bool = False
    degrade_reason: str = ""


class Alert(NamedTuple):
    ticker: str
    horizon: int
    z: float
    percentile: float | None
    direction: str              # 'inflow' | 'outflow'
    flow_usd: float | None
    flow_bps: float | None
    basis: str                  # 'standalone' | 'corroborated'
    corroboration: str          # '' when standalone
    severity: float             # |z|, the ranking key


def _eligible(r: Reading) -> bool:
    """Gate before any threshold is considered.

    Synthetic funds are excluded because swap/forward-backed creations do not mechanically
    buy the underlying — a flow z-score there does not mean what it means elsewhere.
    """
    return (
        r.tier == "trigger"
        and not r.synthetic
        and r.min_history_ok
        and not r.degraded
        and r.z is not None
    )


def _corroboration(r: Reading, by_ticker: dict[str, dict[int, Reading]]) -> str:
    """Independent second evidence for a 2-sigma reading.

    Two accepted forms:
      • the OTHER horizon is also elevated in the SAME direction — accumulated positioning
        and a fresh impulse agreeing,
      • a flow-vs-price divergence in the same direction — money moving against the tape,
        which is the reading that is hardest to explain as mechanical.

    Same-direction is required: a 63d inflow paired with a 5d outflow is the "crowded but
    stalling" quadrant, which is interesting but is NOT confirmation of the 5d reading.
    """
    assert r.z is not None
    sign = 1 if r.z > 0 else -1

    for h, other in by_ticker.get(r.ticker, {}).items():
        if h == r.horizon or other.z is None or other.degraded:
            continue
        if abs(other.z) >= CORROBORATED_SIGMA and (1 if other.z > 0 else -1) == sign:
            return f"{h}d also {abs(other.z):.1f}σ {'in' if sign > 0 else 'out'}"

    if sign > 0 and r.divergence == "accumulation":
        return "inflow against a falling tape"
    if sign < 0 and r.divergence == "distribution":
        return "outflow against a rising tape"
    return ""


def _days_between(a: str, b: str) -> int:
    """Calendar days between ISO dates. Cooldown is intentionally in calendar days, not
    trading days — it only needs to be approximately right and this avoids needing a
    market calendar in a pure module."""
    from datetime import date
    ya, ma, da = (int(x) for x in a.split("-"))
    yb, mb, db = (int(x) for x in b.split("-"))
    return abs((date(yb, mb, db) - date(ya, ma, da)).days)


def evaluate(readings: Sequence[Reading], state: dict, as_of: str,
             max_alerts: int = MAX_ALERTS_PER_DAY) -> tuple[list[Alert], dict, int]:
    """Return (alerts, new_state, suppressed_by_cap).

    `state` maps "TICKER:HORIZON" -> {"armed": bool, "last_fired": "YYYY-MM-DD"}. It is
    returned rather than mutated so the caller owns persistence and this stays testable.
    A key absent from state is treated as ARMED — a new ticker can fire immediately.
    """
    new_state = {k: dict(v) for k, v in state.items()}
    by_ticker: dict[str, dict[int, Reading]] = {}
    for r in readings:
        by_ticker.setdefault(r.ticker, {})[r.horizon] = r

    candidates: list[Alert] = []

    for r in readings:
        key = f"{r.ticker}:{r.horizon}"
        st = new_state.setdefault(key, {"armed": True, "last_fired": None})

        if not _eligible(r):
            continue
        assert r.z is not None
        mag = abs(r.z)

        # Re-arm first, so a name that has calmed down can fire again on its next episode.
        if not st["armed"] and mag < RE_ARM_SIGMA:
            st["armed"] = True

        if not st["armed"]:
            continue
        if st["last_fired"] and _days_between(st["last_fired"], as_of) < ALERT_COOLDOWN_DAYS:
            continue

        basis, corro = "", ""
        if mag >= STANDALONE_SIGMA:
            basis = "standalone"
        elif mag >= CORROBORATED_SIGMA:
            corro = _corroboration(r, by_ticker)
            if corro:
                basis = "corroborated"

        if not basis:
            continue

        candidates.append(Alert(
            ticker=r.ticker, horizon=r.horizon, z=r.z, percentile=r.percentile,
            direction="inflow" if r.z > 0 else "outflow",
            flow_usd=r.flow_usd, flow_bps=r.flow_bps,
            basis=basis, corroboration=corro, severity=mag,
        ))

    # Rank by severity, then deterministically so equal-severity output is stable run to run.
    candidates.sort(key=lambda a: (-a.severity, a.ticker, a.horizon))
    fired, suppressed = candidates[:max_alerts], max(0, len(candidates) - max_alerts)

    # Only alerts that actually FIRED disarm. A candidate dropped by the cap stays armed so
    # it can surface tomorrow rather than being silently consumed.
    for a in fired:
        st = new_state[f"{a.ticker}:{a.horizon}"]
        st["armed"] = False
        st["last_fired"] = as_of

    return fired, new_state, suppressed


def count_episodes(alerts_by_date: dict[str, Sequence[Alert]]) -> dict[str, int]:
    """Calibration helper: episodes per (ticker, horizon), not alert-days.

    With hysteresis in place these are already the same number — which is the point. This
    exists so verification step 5 measures the thing the threshold should be tuned against.
    """
    out: dict[str, int] = {}
    for _, alerts in sorted(alerts_by_date.items()):
        for a in alerts:
            out[f"{a.ticker}:{a.horizon}"] = out.get(f"{a.ticker}:{a.horizon}", 0) + 1
    return out
