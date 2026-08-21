"""
Tests for triggers.py.

What these protect — every one is a way the section quietly becomes unreadable:

  • hysteresis: a 63d episode must fire ONCE, not every morning for three weeks (consecutive
    63d windows share 62 of 63 days, so raw z-scores barely move),
  • the alert cap never silently eats an alert — capped candidates stay armed for tomorrow,
    and the suppressed count is returned,
  • context-tier, synthetic and degraded readings can never fire,
  • 2 sigma requires SAME-DIRECTION corroboration; the "crowded but stalling" pattern
    (63d in, 5d out) is NOT corroboration.

No pytest in this env — run directly:  python3 scripts/etfflows/test_triggers.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import ALERT_COOLDOWN_DAYS, MAX_ALERTS_PER_DAY  # noqa: E402
from etfflows import triggers as t  # noqa: E402

FAILURES = []

# Most tests here exercise the SIGMA gate and the gate-independent machinery (eligibility,
# hysteresis, the cap, per-ticker collapse). The shipped default is the percentile gate, so
# the mode is pinned explicitly rather than inherited — a test that silently follows the
# default would change meaning the next time the default moves.
t.USE_PERCENTILE_GATE = False


class pctile_gate:
    """Context manager: run a block under the percentile gate, then restore."""

    def __init__(self, gate=99.5):
        self.gate = gate

    def __enter__(self):
        self.saved = (t.USE_PERCENTILE_GATE, t.GATE_PERCENTILE)
        t.USE_PERCENTILE_GATE, t.GATE_PERCENTILE = True, self.gate

    def __exit__(self, *exc):
        t.USE_PERCENTILE_GATE, t.GATE_PERCENTILE = self.saved
        return False


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def R(ticker, horizon, z, **kw):
    """Reading with sensible trigger-tier defaults."""
    base = dict(ticker=ticker, horizon=horizon, z=z, percentile=99.0,
                flow_usd=1e9, flow_bps=25.0, divergence=None, tier="trigger",
                synthetic=False, min_history_ok=True, degraded=False, degrade_reason="")
    base.update(kw)
    return t.Reading(**base)


# ── thresholds ────────────────────────────────────────────────────────────────

def test_standalone_fires_at_3sigma():
    alerts, _, _ = t.evaluate([R("XLK", 63, 3.4)], {}, "2026-08-19")
    check("3.4 sigma fires standalone", len(alerts) == 1 and alerts[0].basis == "standalone",
          f"got {alerts}")
    check("direction is inflow for +z", alerts and alerts[0].direction == "inflow")


def test_below_2sigma_never_fires():
    alerts, _, _ = t.evaluate([R("XLK", 63, 1.9)], {}, "2026-08-19")
    check("1.9 sigma is silent", alerts == [], f"got {alerts}")


def test_2sigma_alone_does_not_fire():
    alerts, _, _ = t.evaluate([R("XLK", 63, 2.4)], {}, "2026-08-19")
    check("2.4 sigma with no corroboration is silent", alerts == [], f"got {alerts}")


def test_2sigma_with_other_horizon_fires():
    readings = [R("XLK", 5, 2.4), R("XLK", 63, 2.6)]
    alerts, _, _ = t.evaluate(readings, {}, "2026-08-19")
    check("2 sigma corroborated by the other horizon fires", len(alerts) == 1, f"got {alerts}")
    check("the more severe horizon is the one reported",
          alerts[0].horizon == 63, f"got {alerts[0].horizon}")
    check("basis recorded as corroborated", alerts[0].basis == "corroborated")
    check("corroboration text is populated", bool(alerts[0].corroboration))


def test_one_alert_per_ticker():
    """The 5d window sits INSIDE the 63d window, so both horizons describe one episode.

    Live 2026-08-19: MTUM fired at 5d (-2.8σ) and 63d (-2.0σ), each citing the other as
    corroboration. Reporting it twice double-counts, and the mutual corroboration lets a
    single move clear the 2σ bar when neither horizon would clear 3σ alone.
    """
    readings = [R("MTUM", 5, -2.8), R("MTUM", 63, -2.0)]
    alerts, state, _ = t.evaluate(readings, {}, "2026-08-19")
    check("one episode -> one alert", len(alerts) == 1, f"got {[a.horizon for a in alerts]}")
    check("keeps the most severe horizon", alerts[0].horizon == 5, f"got {alerts[0].horizon}")
    check("BOTH horizons disarm (same episode)",
          state["MTUM:5"]["armed"] is False and state["MTUM:63"]["armed"] is False,
          f"got {state['MTUM:5']}, {state['MTUM:63']}")


def test_distinct_tickers_still_both_report():
    readings = [R("SMH", 63, 3.4), R("MTUM", 5, -3.1)]
    alerts, _, _ = t.evaluate(readings, {}, "2026-08-19")
    check("collapsing is per-ticker, not global",
          {a.ticker for a in alerts} == {"SMH", "MTUM"}, f"got {alerts}")


def test_opposite_direction_is_not_corroboration():
    """63d inflow + 5d outflow is 'crowded but stalling' — interesting, but not confirmation."""
    readings = [R("XLK", 5, -2.4), R("XLK", 63, 2.6)]
    alerts, _, _ = t.evaluate(readings, {}, "2026-08-19")
    check("opposite-direction horizons do not corroborate", alerts == [], f"got {alerts}")


def test_divergence_corroborates():
    a1, _, _ = t.evaluate([R("SMH", 5, 2.3, divergence="accumulation")], {}, "2026-08-19")
    check("inflow + accumulation corroborates", len(a1) == 1, f"got {a1}")

    a2, _, _ = t.evaluate([R("SMH", 5, -2.3, divergence="distribution")], {}, "2026-08-19")
    check("outflow + distribution corroborates", len(a2) == 1, f"got {a2}")

    a3, _, _ = t.evaluate([R("SMH", 5, 2.3, divergence="confirmation")], {}, "2026-08-19")
    check("trend-following divergence does NOT corroborate", a3 == [], f"got {a3}")


# ── eligibility gates ─────────────────────────────────────────────────────────

def test_context_tier_never_fires():
    alerts, _, _ = t.evaluate([R("VGT", 63, 9.0, tier="context")], {}, "2026-08-19")
    check("context tier cannot alert even at 9 sigma", alerts == [], f"got {alerts}")


def test_synthetic_never_fires():
    alerts, _, _ = t.evaluate([R("DRAM", 63, 9.0, synthetic=True)], {}, "2026-08-19")
    check("synthetic fund cannot alert", alerts == [], f"got {alerts}")


def test_degraded_never_fires():
    alerts, _, _ = t.evaluate(
        [R("XLRE", 63, None, degraded=True, degrade_reason="mad_floor")], {}, "2026-08-19")
    check("MAD-floor degraded reading cannot alert", alerts == [], f"got {alerts}")


def test_insufficient_history_never_fires():
    alerts, _, _ = t.evaluate([R("LYTE", 5, 5.0, min_history_ok=False)], {}, "2026-08-19")
    check("insufficient history cannot alert", alerts == [], f"got {alerts}")


# ── hysteresis: the expensive one ─────────────────────────────────────────────

def test_episode_fires_once_not_every_day():
    """THE headline test. A 63d episode decays slowly; without hysteresis this fires ~20x."""
    state = {}
    fired_days = []
    # A realistic slow decay: consecutive 63d windows share 62 of 63 days.
    path = [3.5, 3.45, 3.4, 3.38, 3.3, 3.25, 3.2, 3.1, 3.05, 3.0,
            2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0]
    for i, z in enumerate(path):
        day = f"2026-08-{i + 1:02d}"
        alerts, state, _ = t.evaluate([R("XLK", 63, z)], state, day)
        if alerts:
            fired_days.append(day)
    check("slow-decaying episode fires exactly once", len(fired_days) == 1,
          f"fired on {fired_days}")
    check("it fires on the first day", fired_days == ["2026-08-01"], f"got {fired_days}")


def test_rearm_after_calming_allows_a_second_episode():
    state = {}
    fired = []
    # spike, fall well below the re-arm band, spike again
    path = [("2026-08-01", 3.5), ("2026-08-02", 0.2), ("2026-08-03", 0.1),
            ("2026-09-01", 3.6)]
    for day, z in path:
        alerts, state, _ = t.evaluate([R("XLK", 63, z)], state, day)
        if alerts:
            fired.append(day)
    check("a genuinely new episode fires again", fired == ["2026-08-01", "2026-09-01"],
          f"got {fired}")


def test_cooldown_blocks_immediate_refire():
    """Even a full re-arm cannot bypass the cooldown window."""
    state = {}
    alerts, state, _ = t.evaluate([R("XLK", 5, 3.5)], state, "2026-08-01")
    check("first fire lands", len(alerts) == 1)
    # drop below re-arm (so armed flips True) then spike the very next day
    _, state, _ = t.evaluate([R("XLK", 5, 0.0)], state, "2026-08-02")
    alerts, state, _ = t.evaluate([R("XLK", 5, 4.0)], state, "2026-08-03")
    check(f"cooldown ({ALERT_COOLDOWN_DAYS}d) blocks a 2-day-later refire", alerts == [],
          f"got {alerts}")


def test_state_is_keyed_per_horizon():
    """State stays per-(ticker, horizon) even though reporting collapses per ticker.

    The horizons re-arm independently — a 5d impulse can calm while 63d positioning stays
    elevated — so the bookkeeping must stay separate even when the OUTPUT is collapsed.
    """
    state = {}
    alerts, state, _ = t.evaluate([R("XLK", 5, 3.5), R("XLK", 63, 3.5)], state, "2026-08-01")
    check("one alert reported for the ticker", len(alerts) == 1, f"got {alerts}")
    keys = sorted(k for k in state if k.startswith("XLK"))
    check("state is still keyed per (ticker, horizon)", keys == ["XLK:5", "XLK:63"], f"got {keys}")


def test_unknown_ticker_starts_armed():
    alerts, _, _ = t.evaluate([R("NEWETF", 5, 3.2)], {}, "2026-08-19")
    check("a ticker absent from state can fire immediately", len(alerts) == 1)


# ── the cap ───────────────────────────────────────────────────────────────────

def test_cap_truncates_by_severity_and_reports():
    readings = [R(f"ET{i}", 63, 3.0 + i * 0.1) for i in range(MAX_ALERTS_PER_DAY + 3)]
    alerts, _, suppressed = t.evaluate(readings, {}, "2026-08-19")
    check("cap is enforced", len(alerts) == MAX_ALERTS_PER_DAY, f"got {len(alerts)}")
    check("truncation is reported, never silent", suppressed == 3, f"got {suppressed}")
    check("ranked by severity descending",
          [a.severity for a in alerts] == sorted([a.severity for a in alerts], reverse=True))


def test_capped_candidates_stay_armed_for_tomorrow():
    """A capped alert must not be consumed — it should surface the next day."""
    readings = [R(f"ET{i}", 63, 3.0 + i * 0.1) for i in range(MAX_ALERTS_PER_DAY + 1)]
    alerts, state, suppressed = t.evaluate(readings, {}, "2026-08-19")
    dropped = "ET0"  # lowest severity
    check("lowest-severity name was the one dropped",
          dropped not in [a.ticker for a in alerts] and suppressed == 1)
    check("dropped candidate remains armed", state[f"{dropped}:63"]["armed"] is True,
          f"got {state.get(f'{dropped}:63')}")
    check("dropped candidate has no last_fired stamp",
          state[f"{dropped}:63"]["last_fired"] is None)


def test_ordering_is_deterministic():
    readings = [R("BBB", 63, 3.0), R("AAA", 63, 3.0), R("CCC", 63, 3.0)]
    a1, _, _ = t.evaluate(readings, {}, "2026-08-19")
    a2, _, _ = t.evaluate(list(reversed(readings)), {}, "2026-08-19")
    check("equal-severity output is stable run to run",
          [a.ticker for a in a1] == [a.ticker for a in a2] == ["AAA", "BBB", "CCC"],
          f"{[a.ticker for a in a1]} vs {[a.ticker for a in a2]}")


def test_state_is_not_mutated_in_place():
    state = {}
    t.evaluate([R("XLK", 63, 3.5)], state, "2026-08-19")
    check("caller's state dict is left untouched", state == {}, f"got {state}")


# ── the percentile gate (the shipped default) ─────────────────────────────────

def test_percentile_gate_fires_in_the_tail():
    with pctile_gate(99.5):
        alerts, _, _ = t.evaluate([R("SMH", 63, 4.2, percentile=99.7)], {}, "2026-08-19")
        check("99.7th pctile clears a 99.5 gate", len(alerts) == 1, f"got {alerts}")
        alerts, _, _ = t.evaluate([R("SMH", 63, 4.2, percentile=99.2)], {}, "2026-08-19")
        check("99.2nd pctile does not", alerts == [], f"got {alerts}")


def test_percentile_gate_is_two_sided():
    """An extreme OUTFLOW sits at the bottom of the distribution, not the top."""
    with pctile_gate(99.5):
        alerts, _, _ = t.evaluate([R("MTUM", 5, -4.0, percentile=0.2)], {}, "2026-08-19")
        check("0.2nd pctile fires as an outflow", len(alerts) == 1, f"got {alerts}")
        check("direction taken from the sign", alerts[0].direction == "outflow")
        alerts, _, _ = t.evaluate([R("MTUM", 5, -1.0, percentile=40.0)], {}, "2026-08-19")
        check("mid-distribution is silent", alerts == [], f"got {alerts}")


def test_percentile_gate_ignores_sigma_magnitude():
    """The whole point: a big MAD-scaled sigma is NOT rare when the tails are heavy.

    A -7σ print was observed in real backfilled data. Under the sigma gate that fires
    trivially; under the percentile gate it fires only if it is genuinely in the tail of
    that fund's own history.
    """
    with pctile_gate(99.5):
        alerts, _, _ = t.evaluate([R("SMH", 5, -7.2, percentile=1.0)], {}, "2026-08-19")
        check("-7.2σ at the 1st pctile does NOT fire", alerts == [], f"got {alerts}")


def test_percentile_gate_bypasses_corroboration():
    """No two-tier logic under the percentile gate — everything is 'standalone'."""
    with pctile_gate(99.5):
        alerts, _, _ = t.evaluate(
            [R("XLK", 5, 2.1, percentile=99.9, divergence="accumulation")], {}, "2026-08-19")
        check("qualifies on percentile alone", len(alerts) == 1, f"got {alerts}")
        check("basis is standalone", alerts[0].basis == "standalone")
        check("no corroboration text", alerts[0].corroboration == "")


def test_percentile_gate_rearms_on_percentile():
    """Re-arm must use the same statistic as the gate, or a name re-arms while still extreme."""
    with pctile_gate(99.5):
        state = {}
        alerts, state, _ = t.evaluate([R("XLK", 5, 4.0, percentile=99.9)], state, "2026-08-01")
        check("fires once", len(alerts) == 1)
        # still extreme on percentile -> must NOT re-arm
        _, state, _ = t.evaluate([R("XLK", 5, 4.0, percentile=99.8)], state, "2026-08-02")
        check("stays disarmed while still in the tail", state["XLK:5"]["armed"] is False,
              f"got {state['XLK:5']}")
        # back to mid-distribution -> re-arms
        _, state, _ = t.evaluate([R("XLK", 5, 0.1, percentile=55.0)], state, "2026-08-03")
        check("re-arms once back inside the band", state["XLK:5"]["armed"] is True,
              f"got {state['XLK:5']}")


def test_percentile_gate_still_respects_eligibility():
    with pctile_gate(99.5):
        for label, z, kw in (("context tier", 5.0, {"tier": "context"}),
                             ("synthetic", 5.0, {"synthetic": True}),
                             ("no history", 5.0, {"min_history_ok": False}),
                             ("degraded", None, {"degraded": True})):
            alerts, _, _ = t.evaluate([R("X", 63, z, percentile=99.99, **kw)], {},
                                      "2026-08-19")
            check(f"{label} cannot fire under the percentile gate", alerts == [],
                  f"got {alerts}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        print(f"\n{fn.__name__}:")
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
        return 1
    print(f"All checks passed ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
