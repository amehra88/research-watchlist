"""
etfflows — ETF flow & crowding monitor for the 07:00 combined digest.

Spec: docs/specs/2026-08-19-etf-flow-crowding-monitor.md (approved 2026-08-19).

FRAMING, NOT DECORATION: this is a POSITIONING / CROWDING monitor, explicitly NOT a
directional signal. Flow-induced demand mean-reverts over multi-week horizons
(Ben-David/Franzoni/Moussawi; Brown/Davies/Ringgenberg), so "inflows = bullish" is likely
backwards at exactly the horizons reported here. Any language added to render.py must
respect that; the validation gate exists to confirm the sign before we claim otherwise.

Tunable constants live here (repo convention, mirrors scripts/newsdigest/__init__.py).
"""

# ── Horizons (spec: "Horizons: 5d and 63d") ───────────────────────────────────
# Three overlapping windows read the same impulse three times and inflate apparent
# confirmation (21d CONTAINS 5d). Two, chosen to be near-independent:
SHORT_HORIZON = 5        # trading days — the operator's "trailing 7 days"
LONG_HORIZON = 63        # ~1 quarter — crowding is accumulated positioning, not an impulse
HORIZONS = (SHORT_HORIZON, LONG_HORIZON)

# 1d is computed but NEVER a headline — kept only as an event flag.
EVENT_FLAG_HORIZON = 1

# ── Robust z-score ────────────────────────────────────────────────────────────
# median/MAD, not mean/sigma: daily flows have fat tails and a Gaussian z over-fires.
#
# MAD_TO_SIGMA is the consistency factor that makes MAD a drop-in estimator for the
# standard deviation of a normal distribution. WITHOUT IT a "3 sigma" threshold is really
# ~2 sigma in Gaussian-equivalent terms and the alert budget is off by a large factor.
# It is applied in metrics.robust_z; thresholds below are therefore in true sigma units.
MAD_TO_SIGMA = 1.4826

# MAD floor. Several ETFs (XLB, XLRE, PSI, XSD, PDP and most of the context tier) have long
# runs of near-identical or zero daily flow. A trailing MAD of ~0 makes every reading +/-inf
# sigma and destroys the alert budget. When the floor binds we fall back to EMPIRICAL
# PERCENTILE ONLY and suppress the sigma label rather than emitting a fake number.
# Units are bps of AUM because the z-score is computed on the normalised (bps) series --
# a fund whose AUM tripled over the baseline would otherwise show mechanically larger
# USD flows and read as anomalous when nothing changed.
MAD_FLOOR_BPS = 0.5

# Minimum baseline observations before any z-score is emitted at all.
MIN_BASELINE_OBS = 120

# Fraction of a rolling window that must be non-missing for the window to be valid.
MIN_WINDOW_COVERAGE = 0.8

# ── Trigger thresholds — PROVISIONAL until calibrated ─────────────────────────
# Starting values, NOT fixed. Calibration runs on backfilled history and is ALLOWED to
# move them; materially more than ~1 alert/week means these move. That is the expected
# outcome, not a failure. DO NOT WIRE THE EMAIL UNTIL CALIBRATION HAS RUN.
STANDALONE_SIGMA = 3.0   # fires on its own
CORROBORATED_SIGMA = 2.0 # fires only with corroboration (other horizon elevated, or divergence)
MAX_ALERTS_PER_DAY = 6   # ranked by severity; truncation is REPORTED, never silent

# GATE CHOICE. When True, a reading qualifies on its EMPIRICAL PERCENTILE rather than on a
# robust-z threshold, and the corroboration tier is bypassed entirely.
#
# Why this exists: daily ETF flows are so fat-tailed that MAD-scaled sigma is not comparable
# across funds or interpretable on its own — a real -7σ print is unremarkable. Calibration on
# backfilled history also showed the two-tier design was not doing what it looked like:
# essentially all corroborated alerts qualified via flow-vs-price divergence, which is close
# to a coin flip, so the effective threshold was the LOWER number almost all the time and the
# standalone value barely mattered. A percentile gate says the same thing for every fund
# ("top X% of this ETF's own history for this horizon") and is self-calibrating.
USE_PERCENTILE_GATE = True

# CALIBRATED 2026-08-21 against 3 years of real FactSet history: 20 trigger-tier ETFs,
# 653 evaluable days, replayed through the shipped triggers.evaluate().
#
#   pctile   episodes   per week    5d   63d
#    99.00        239       1.83   155    84
#    99.50        169       1.29   103    66     <- chosen
#    99.80        140       1.07    79    61
#    99.90        134       1.03    74    60
#
# WHY 99.5 AND NOT THE ROW CLOSEST TO 1.0/WEEK: the baseline is ~600 observations, so the
# finest percentile the data can actually resolve is ~1/600 = 0.17%. A 99.8 or 99.9 gate is
# finer than that — it pins the threshold to a single observation and is noise, not
# precision. 99.5 is the top ~3 of 600, which the data supports.
#
# The curve is also nearly flat above 99.5 (169 -> 134 episodes across a 0.4pp move), because
# the binding constraint is hysteresis, not the threshold: once a ticker fires it is locked
# out until it re-arms. Chasing the last 0.3/week by tightening the gate buys almost nothing
# and costs resolution.
#
# EXPECT ~2/WEEK IN PRODUCTION: this was measured on 20 trigger names and the tier now holds
# 32, so scale by ~1.6. RE-RUN calibrate.py once the remaining 12 are backfilled.
#
# The percentile gate also keeps BOTH horizons alive (103 x 5d, 66 x 63d). The sigma gate did
# not — at its best setting it fired 119 x 5d against 9 x 63d, which would have made a
# "crowding monitor" into a short-term flow monitor, since accumulated 63d positioning is the
# half that actually measures crowding.
GATE_PERCENTILE = 99.5

# Alert hysteresis. A 63d rolling sum on day t and t+1 shares 62 of 63 days, so z-scores are
# near-identical day over day and one crowding episode would re-fire for weeks, permanently
# occupying the daily cap. Once a (ticker, horizon) fires it will not fire again until it has
# first fallen back below RE_ARM_SIGMA. Calibration counts EPISODES, not alert-days.
RE_ARM_SIGMA = 1.5
RE_ARM_PERCENTILE = 90.0   # percentile-gate equivalent: re-arm once back inside 10th-90th
ALERT_COOLDOWN_DAYS = 5

# ── FactSet transport (mirrors scripts/newsdigest/factset_news.py) ────────────
FACTSET_CHUNK_SIZE = 10      # tool hard limit: max 10 ids per request
FACTSET_RESULT_LIMIT = 500   # tool hard limit; rows = ids x days, so this caps the date span
FACTSET_TIMEOUT_SECONDS = 180

# ── Fear & Greed ──────────────────────────────────────────────────────────────
# 418s from this droplet without the Referer/origin header set — see fear_greed.py.
FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
FEAR_GREED_MAX_AGE_HOURS = 48  # older than this -> print with an age note, never fail the digest

__all__ = [
    "SHORT_HORIZON", "LONG_HORIZON", "HORIZONS", "EVENT_FLAG_HORIZON",
    "MAD_TO_SIGMA", "MAD_FLOOR_BPS", "MIN_BASELINE_OBS", "MIN_WINDOW_COVERAGE",
    "STANDALONE_SIGMA", "CORROBORATED_SIGMA", "MAX_ALERTS_PER_DAY",
    "RE_ARM_SIGMA", "RE_ARM_PERCENTILE", "ALERT_COOLDOWN_DAYS",
    "USE_PERCENTILE_GATE", "GATE_PERCENTILE",
    "FACTSET_CHUNK_SIZE", "FACTSET_RESULT_LIMIT", "FACTSET_TIMEOUT_SECONDS",
    "FEAR_GREED_URL", "FEAR_GREED_MAX_AGE_HOURS",
]
