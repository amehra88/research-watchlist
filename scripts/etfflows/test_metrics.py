"""
Tests for metrics.py.

These protect the invariants that a passing eyeball-check would NOT catch, because every
one of them fails silently and plausibly in production:

  • the MAD->sigma consistency factor (1.4826) is actually applied — without it a "3 sigma"
    threshold behaves like ~2 sigma and the alert budget is off by a large factor, while
    every other test still passes,
  • a constant/low-variance series degrades to percentile-only instead of emitting +/-inf,
  • missing (None) and genuine 0.0 stay distinct through rolling windows,
  • the AUM denominator is share-class, not fund-level (the VOO $1.70T vs $994B trap),
  • flow/AUM uses PRIOR-period AUM, so a large inflow is not normalised by AUM that already
    contains it.

No pytest in this env — run directly:  python3 scripts/etfflows/test_metrics.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import MAD_TO_SIGMA, MIN_BASELINE_OBS  # noqa: E402
from etfflows import metrics as m  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


# ── the scaling constant ──────────────────────────────────────────────────────

def test_mad_to_sigma_applied():
    """On a known-sigma sample the robust z must land near the Gaussian z, not ~1.48x it.

    A symmetric two-point distribution at +/-s has MAD = s exactly, so scaled MAD =
    1.4826*s. A point at centre + 1.4826*s must therefore read as exactly 1.0 sigma.
    If the factor were dropped it would read 1.4826 — this is the whole test.
    """
    s = 10.0
    baseline = [100.0 - s, 100.0 + s] * (MIN_BASELINE_OBS)  # median 100, MAD 10
    x = 100.0 + MAD_TO_SIGMA * s
    r = m.robust_z(x, baseline)
    check("MAD_TO_SIGMA applied (z==1.0 at 1 scaled MAD)",
          r.z is not None and abs(r.z - 1.0) < 1e-9, f"got z={r.z}")

    # And the un-scaled reading would have been materially different — guards against
    # someone "simplifying" the constant away and this test still passing by luck.
    check("scaling factor is material (>10% apart)",
          abs(MAD_TO_SIGMA - 1.0) > 0.10, f"MAD_TO_SIGMA={MAD_TO_SIGMA}")


def test_scale_is_reported_in_sigma_units():
    s = 4.0
    baseline = [50.0 - s, 50.0 + s] * MIN_BASELINE_OBS
    r = m.robust_z(50.0, baseline)
    check("ZResult.scale is MAD*1.4826",
          r.scale is not None and abs(r.scale - s * MAD_TO_SIGMA) < 1e-9,
          f"got scale={r.scale}")


# ── the MAD floor ─────────────────────────────────────────────────────────────

def test_constant_series_degrades():
    """The day-one failure mode: XLB/XLRE/PSI-style flat series -> +/-inf sigma."""
    baseline = [0.0] * MIN_BASELINE_OBS
    r = m.robust_z(500.0, baseline)
    check("constant series -> z is None", r.z is None, f"got z={r.z}")
    check("constant series -> degraded", r.degraded is True)
    check("constant series -> reason=mad_floor", r.reason == "mad_floor", f"got {r.reason!r}")
    check("constant series still reports a percentile", r.percentile is not None)
    check("no inf/nan leaks", r.z is None or (r.z == r.z and abs(r.z) != float("inf")))


def test_low_variance_below_floor_degrades():
    """MAD marginally above zero but below the floor must still degrade."""
    baseline = ([0.0, 0.01] * (MIN_BASELINE_OBS // 2 + 1))  # scaled MAD ~ 0.0074 bps
    r = m.robust_z(3.0, baseline)
    check("sub-floor MAD degrades", r.z is None and r.reason == "mad_floor",
          f"z={r.z} reason={r.reason!r} scale={r.scale}")


def test_healthy_series_does_not_degrade():
    baseline = [float(i % 40) - 20.0 for i in range(MIN_BASELINE_OBS * 2)]
    r = m.robust_z(60.0, baseline)
    check("healthy series yields a z", r.z is not None and not r.degraded,
          f"z={r.z} reason={r.reason!r}")


def test_short_baseline_refuses():
    """DRAM/LYTE case: enough window, nowhere near enough baseline."""
    r = m.robust_z(1.0, [0.5] * (MIN_BASELINE_OBS - 1))
    check("short baseline -> insufficient_baseline",
          r.z is None and r.reason == "insufficient_baseline", f"got {r.reason!r}")


# ── missing vs zero ───────────────────────────────────────────────────────────

def test_none_is_not_zero_in_windows():
    """A window of genuine zeros is 0.0; a window that is mostly missing is None.

    Folding None into 0.0 would make a data outage read as 'no flow'.
    """
    zeros = m.rolling_sums([0.0] * 5, 5)
    check("all-zero window sums to 0.0", zeros[-1] == 0.0, f"got {zeros[-1]}")

    mostly_missing = m.rolling_sums([None, None, None, None, 1.0], 5)
    check("mostly-missing window is None", mostly_missing[-1] is None,
          f"got {mostly_missing[-1]}")


def test_partial_coverage_boundary():
    # 4 of 5 present = 80% coverage -> valid at the default threshold.
    ok = m.rolling_sums([None, 1.0, 1.0, 1.0, 1.0], 5)
    check("80% coverage window is valid", ok[-1] == 4.0, f"got {ok[-1]}")
    # 3 of 5 = 60% -> invalid.
    bad = m.rolling_sums([None, None, 1.0, 1.0, 1.0], 5)
    check("60% coverage window is None", bad[-1] is None, f"got {bad[-1]}")


def test_rolling_sums_alignment():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    out = m.rolling_sums(vals, 3)
    check("first window-1 entries are None", out[0] is None and out[1] is None)
    check("right-aligned trailing sum", out[2] == 6.0 and out[4] == 12.0, f"got {out}")
    check("length preserved", len(out) == len(vals))


# ── AUM denominator ───────────────────────────────────────────────────────────

def test_voo_share_class_denominator():
    """Real figures pulled from FactSet 2026-08-19 (VOO, 2026-07-31).

    fundLevelAUM $1.6769T vs shareClassAUMReported $993.8B. Using fund-level understates
    every VOO flow/AUM reading by ~41%, which would quietly park VOO below every threshold.
    """
    fund_level = 1676909034357.62
    share_class = 993823499680.519
    flow = 1_000_000_000.0

    right = m.to_bps(flow, share_class)
    wrong = m.to_bps(flow, fund_level)
    check("share-class denominator gives ~10.06 bps", abs(right - 10.062) < 0.01, f"got {right}")
    check("fund-level would understate by >40%", (right - wrong) / right > 0.40,
          f"right={right} wrong={wrong}")


def test_prior_period_aum_denominator():
    """Normalising by post-flow AUM shrinks exactly the readings we care about."""
    aum_before = 100e9
    flow = 10e9
    before = m.to_bps(flow, aum_before)
    after = m.to_bps(flow, aum_before + flow)
    check("prior-period AUM gives 1000 bps", abs(before - 1000.0) < 1e-6, f"got {before}")
    check("post-flow AUM understates", after < before, f"before={before} after={after}")


def test_to_bps_guards():
    check("None flow -> None", m.to_bps(None, 1e9) is None)
    check("zero AUM -> None (no ZeroDivisionError)", m.to_bps(1.0, 0.0) is None)
    check("None AUM -> None", m.to_bps(1.0, None) is None)


# ── AUM roll-forward ──────────────────────────────────────────────────────────

def test_roll_forward_reanchors_on_month_end():
    dates = ["2026-06-30", "2026-07-01", "2026-07-02", "2026-07-31"]
    navs = [100.0, 100.0, 100.0, 100.0]
    flows = [0.0, 1e9, 1e9, 0.0]
    anchors = {"2026-06-30": 100e9, "2026-07-31": 123.0e9}
    out = m.roll_forward_aum(dates, navs, flows, anchors)
    check("anchor honoured at start", out[0] == 100e9, f"got {out[0]}")
    check("flow accumulates between anchors", abs(out[2] - 102e9) < 1e-6, f"got {out[2]}")
    check("re-anchors at month end (drift cannot accumulate)",
          out[3] == 123.0e9, f"got {out[3]}")


def test_step_aum_uses_window_start_not_end():
    """The denominator must predate the flow it normalises."""
    dates = ["2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03", "2026-07-04"]
    anchors = {"2026-06-30": 100e9}
    out = m.step_aum_series(dates, anchors, window=3)
    check("window ending 07-04 uses the 06-30 anchor (its start)", out[4] == 100e9,
          f"got {out[4]}")


def test_step_aum_picks_most_recent_prior_anchor():
    dates = ["2026-06-30", "2026-07-31", "2026-08-03"]
    anchors = {"2026-06-30": 100e9, "2026-07-31": 123e9}
    out = m.step_aum_series(dates, anchors, window=1)
    check("uses June anchor on 06-30", out[0] == 100e9, f"got {out[0]}")
    check("steps to July anchor on 07-31", out[1] == 123e9, f"got {out[1]}")
    check("holds July anchor into August", out[2] == 123e9, f"got {out[2]}")


def test_step_aum_before_any_anchor_is_none():
    out = m.step_aum_series(["2026-01-01"], {"2026-06-30": 100e9}, window=1)
    check("no prior anchor -> None, never back-filled", out[0] is None, f"got {out[0]}")
    check("empty anchors -> all None",
          m.step_aum_series(["2026-01-01"], {}, 1) == [None])


def test_roll_forward_applies_market_move():
    dates = ["2026-06-30", "2026-07-01"]
    navs = [100.0, 110.0]
    flows = [0.0, 0.0]
    out = m.roll_forward_aum(dates, navs, flows, {"2026-06-30": 100e9})
    check("10% NAV move moves AUM 10%", abs(out[1] - 110e9) / 110e9 < 1e-12, f"got {out[1]}")


def test_roll_forward_no_anchor_stays_none():
    out = m.roll_forward_aum(["2026-07-01"], [100.0], [1e9], {})
    check("no anchor -> None (never back-filled)", out[0] is None, f"got {out[0]}")


def test_roll_forward_matches_factset_reconciliation():
    """The live reconciliation from the module docstring, as a regression test.

    XLK July 2026: 650,361,794 -> 658,461,794 shares (+8.1M) and daily flows summing to
    $1,414.2M imply a NAV of $174.60. Rolling June's anchor forward by those flows at a flat
    NAV must land on the reported July anchor to within the market-move term we hold flat.
    """
    flows_sum = 1414166505.0  # sum of the 23 daily July prints
    june_anchor = 123912575433.976
    dates = ["2026-06-30", "2026-07-31x"]  # second date deliberately NOT an anchor
    out = m.roll_forward_aum(dates, [174.60, 174.60], [0.0, flows_sum],
                             {"2026-06-30": june_anchor})
    expected = june_anchor + flows_sum
    check("roll-forward adds flow at NAV (ICI convention)",
          abs(out[1] - expected) < 1e-6, f"got {out[1]} want {expected}")

    implied_nav = flows_sum / 8_100_000
    check("flows reconcile with dSO at a plausible NAV",
          170.0 < implied_nav < 180.0, f"implied NAV {implied_nav:.2f}")


# ── derived readings ──────────────────────────────────────────────────────────

def test_divergence_signs():
    check("inflow on down tape = accumulation", m.divergence(1.0, -0.01) == "accumulation")
    check("outflow on up tape = distribution", m.divergence(-1.0, 0.01) == "distribution")
    check("inflow on up tape = confirmation", m.divergence(1.0, 0.01) == "confirmation")
    check("outflow on down tape = capitulation", m.divergence(-1.0, -0.01) == "capitulation")
    check("missing input -> None", m.divergence(None, 0.01) is None)


def test_breadth_excludes_missing():
    """A data gap must not masquerade as an outflow."""
    pct, pos, n = m.breadth({"A": 1.0, "B": -1.0, "C": None, "D": 2.0})
    check("breadth ignores None in denominator", n == 3, f"got n={n}")
    check("breadth counts positives", pos == 2, f"got pos={pos}")
    check("breadth pct", abs(pct - 66.666) < 0.01, f"got {pct}")
    check("all-missing breadth -> None", m.breadth({"A": None})[0] is None)


def test_pair_spread():
    check("SPY 50bps vs siblings 10/10 -> 40", m.pair_spread(50.0, [10.0, 10.0]) == 40.0)
    check("siblings averaged not summed", m.pair_spread(50.0, [10.0, 10.0]) != 30.0)
    check("missing lead -> None", m.pair_spread(None, [1.0]) is None)
    check("no siblings -> None", m.pair_spread(1.0, [None]) is None)


def test_percentile_and_exceedance():
    baseline = [float(i) for i in range(100)]
    p = m.percentile_rank(99.0, baseline)
    check("top value ~99.5th pctile", p is not None and p > 99.0, f"got {p}")

    dates = ["d1", "d2", "d3", "d4"]
    vals = [10.0, 90.0, 5.0, 95.0]
    check("finds prior exceedance", m.most_recent_exceedance(dates, vals, 90.0) == "d2")
    check("no prior exceedance -> None",
          m.most_recent_exceedance(dates, vals, 1000.0) is None)
    check("negative direction is mirrored",
          m.most_recent_exceedance(["a", "b", "c"], [-50.0, 1.0, -1.0], -40.0) == "a")


def test_crowding_quadrant():
    check("high/high = sustained crowding",
          m.crowding_quadrant(2.0, 2.0) == "sustained crowding")
    check("63d high + 5d low = crowded but stalling",
          m.crowding_quadrant(-2.0, 2.0) == "crowded but stalling")
    check("low/high 5d = fresh rotation", m.crowding_quadrant(2.0, -2.0) == "fresh rotation")
    check("both low = neglected", m.crowding_quadrant(-2.0, -2.0) == "neglected")
    check("missing -> None", m.crowding_quadrant(None, 1.0) is None)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        print(f"\n{t.__name__}:")
        t()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {', '.join(FAILURES)}")
        return 1
    print(f"All checks passed ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
