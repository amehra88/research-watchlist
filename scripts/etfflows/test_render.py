"""
Tests for render.py, driven by a hand-written fixture (no fetch, no LLM).

What these protect:
  • 'n/a' vs '-' vs a number stay distinguishable — a degraded z must never print as 0.0,
  • Block A carries no interpretation and Block B carries no prediction (the operator asked
    for facts and analysis to be visibly separate, and the framing is positioning-not-signal),
  • the as-of date is always printed rather than assumed to be T-1,
  • cap suppression is always disclosed,
  • the markdown note opens with '##' (a '#' first heading indexes to zero chunks in pg).

Run:  python3 scripts/etfflows/test_render.py   (also prints a full sample report)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import render as rd  # noqa: E402
from etfflows import triggers as tg  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


def sample_report():
    alerts = [
        tg.Alert(ticker="SMH", horizon=63, z=3.4, percentile=99.4, direction="inflow",
                 flow_usd=4.12e9, flow_bps=88.3, basis="standalone", corroboration="",
                 severity=3.4),
        tg.Alert(ticker="MTUM", horizon=5, z=-2.3, percentile=1.2, direction="outflow",
                 flow_usd=-812e6, flow_bps=-41.0, basis="corroborated",
                 corroboration="outflow against a rising tape", severity=2.3),
    ]
    return {
        "as_of": "2026-08-18",
        "fear_greed_line": "FEAR & GREED: 56 (greed)  |  1w -7  |  1m +19",
        "alerts": alerts,
        "suppressed": 2,
        "breadth": {5: {"pct": 61.5, "positive": 16, "measured": 26},
                    63: {"pct": 73.1, "positive": 19, "measured": 26}},
        "pairs": [{"name": "SPY vs IVV+VOO", "short": 41.2, "long": -18.7},
                  {"name": "QQQ vs QQQM", "short": -6.4, "long": 12.0}],
        "factor_rotation": [{"ticker": "MTUM", "bps": 120.4}, {"ticker": "QUAL", "bps": -8.1},
                            {"ticker": "VLUE", "bps": -30.2}, {"ticker": "USMV", "bps": 4.4}],
        "quadrants": {"SMH": "sustained crowding", "MTUM": "crowded but stalling",
                      "XLE": "neglected", "IGV": "fresh rotation"},
        "divergence": {"MTUM": "distribution", "SMH": "confirmation"},
        "warnings": ["LYTE: insufficient history (inception 2026-08-06) — raw flow only"],
        "rows": [
            {"ticker": "SMH", "tier": "trigger", "flow_short_usd": 1.1e9, "bps_short": 23.4,
             "z_short": 1.9, "flow_long_usd": 4.12e9, "bps_long": 88.3, "z_long": 3.4,
             "quadrant": "sustained crowding"},
            {"ticker": "XLRE", "tier": "trigger", "flow_short_usd": 0.0, "bps_short": 0.0,
             "z_short": None, "degraded_short": True, "flow_long_usd": -12e6,
             "bps_long": -1.1, "z_long": None, "degraded_long": True, "quadrant": None},
            {"ticker": "LYTE", "tier": "context", "flow_short_usd": 41e6, "bps_short": None,
             "z_short": None, "degraded_short": True, "flow_long_usd": None,
             "bps_long": None, "z_long": None, "degraded_long": True, "quadrant": None},
        ],
        "table_notes": ["DRAM and LYTE are synthetically backed — excluded from z-scores."],
    }


# ── formatting primitives ─────────────────────────────────────────────────────

def test_missing_and_degraded_are_distinguishable():
    check("missing USD renders '-'", rd.usd(None) == "-")
    check("missing bps renders '-'", rd.bps(None) == "-")
    check("degraded z renders 'n/a', never 0.0", rd.sigma(None, degraded=True) == "n/a")
    check("real zero flow renders as +$0", rd.usd(0.0) == "+$0", f"got {rd.usd(0.0)}")
    check("a real z still renders", rd.sigma(3.4) == "+3.4σ", f"got {rd.sigma(3.4)}")


def test_usd_scaling():
    check("billions", rd.usd(4.12e9) == "+$4.1B", f"got {rd.usd(4.12e9)}")
    check("negative millions", rd.usd(-812e6) == "-$812.0M", f"got {rd.usd(-812e6)}")
    check("trillions", rd.usd(1.7e12) == "+$1.7T", f"got {rd.usd(1.7e12)}")


# ── Block A ───────────────────────────────────────────────────────────────────

def test_block_a_prints_as_of_date():
    a = rd.block_a(sample_report())
    check("as-of date is printed, not assumed", "Flows as of 2026-08-18" in a)


def test_block_a_discloses_suppression():
    a = rd.block_a(sample_report())
    check("cap suppression is disclosed", "2 further alert(s) suppressed" in a,
          "silent cap!")


def test_block_a_has_no_interpretation():
    """Block A is facts. Interpretive vocabulary belongs in Block B."""
    a = rd.block_a(sample_report()).lower()
    for word in ("crowded", "reversal-prone", "distribution risk", "read as positioning"):
        if word in a:
            check("Block A carries no interpretation", False, f"found {word!r}")
            return
    check("Block A carries no interpretation", True)


def test_block_a_no_alerts_says_so():
    r = sample_report()
    r["alerts"], r["suppressed"] = [], 0
    check("empty alert list is stated explicitly",
          "UNUSUAL FLOWS: none today" in rd.block_a(r))


def test_block_a_shows_breadth_and_pairs():
    a = rd.block_a(sample_report())
    check("risk appetite rendered", "Risk appetite (63d): 73%" in a, f"missing in:\n{a}")
    check("sibling spread rendered", "SPY vs IVV+VOO" in a)
    check("factor block rendered", "FACTOR FLOWS" in a and "MTUM" in a)


# ── readability (the whole point of the redesign) ─────────────────────────────

def test_flows_are_expressed_as_percent_of_fund():
    """'-797.1bp' is jargon; '-8.0% of the fund' is the same number without a decoder ring."""
    check("bps converts to percent of fund", rd.pct_aum(-797.1) == "-8.0%",
          rd.pct_aum(-797.1))
    check("positive keeps its sign", rd.pct_aum(463.9) == "+4.6%", rd.pct_aum(463.9))
    check("missing stays '-'", rd.pct_aum(None) == "-")

    a = rd.block_a(sample_report())
    check("Block A speaks in % of fund", "% of the fund" in a, f"missing in:\n{a}")


def test_rarity_is_plain_english():
    """MTUM printed -2.0σ at the 0.0th percentile — the sigma actively understates it."""
    check("0th percentile is 'most extreme on record'",
          rd.rarity(0.0) == "most extreme on record", rd.rarity(0.0))
    check("99.99th is also most extreme", rd.rarity(99.99) == "most extreme on record")
    check("top half-percent", rd.rarity(99.6) == "top 0.5% of its history", rd.rarity(99.6))
    check("ordinary readings just state the percentile",
          rd.rarity(60.0) == "60th percentile", rd.rarity(60.0))
    check("missing percentile says nothing", rd.rarity(None) == "")


def test_alert_verb_carries_the_sign_not_the_number():
    """'lost +$1.9B' reads as a contradiction."""
    check("magnitude is unsigned", rd.usd_mag(-1.9e9) == "$1.9B", rd.usd_mag(-1.9e9))
    check("inflow magnitude too", rd.usd_mag(4.12e9) == "$4.1B", rd.usd_mag(4.12e9))
    a = rd.block_a(sample_report())
    check("no 'lost +$' contradiction in output", "lost +$" not in a, f"in:\n{a}")


def test_sector_block_is_a_ranked_rotation_map():
    r = sample_report()
    r["sector_rotation"] = [
        {"ticker": "XLE", "short_bps": 250.0, "bps": 900.0},
        {"ticker": "XLK", "short_bps": -40.0, "bps": -5.0},
        {"ticker": "XLRE", "short_bps": -170.0, "bps": -600.0},
    ]
    a = rd.block_a(r)
    check("sector block present", "SECTOR FLOWS" in a)
    check("tickers get plain names", "XLE Energy" in a and "XLK Tech" in a, f"in:\n{a}")
    check("both horizons shown", "past week" in a and "past quarter" in a)
    check("money-in ranks above money-out",
          a.index("XLE Energy") < a.index("XLRE Real Estate"), f"in:\n{a}")
    check("values as % of fund", "+9.0%" in a and "-6.0%" in a, f"in:\n{a}")


def test_competitor_block_leads_and_names_our_fund():
    """The only place the digest says whether OUR fund is gaining or losing assets."""
    r = sample_report()
    r["competitor_rotation"] = [
        {"ticker": "BCTK", "short_bps": -50.0, "bps": 3010.0},
        {"ticker": "JTEK", "short_bps": 60.0, "bps": 1460.0},
        {"ticker": "BAI", "short_bps": 190.0, "bps": -380.0},
    ]
    r["sector_rotation"] = [{"ticker": "XLE", "short_bps": 10.0, "bps": 900.0}]
    a = rd.block_a(r)
    check("competitor block present", "FUND FLOWS — us vs competitors" in a, f"in:\n{a}")
    check("our fund is labelled as ours", "BCTK ours" in a, f"in:\n{a}")
    check("competitors are named, not just tickers", "JTEK JPMorgan Tech" in a)
    check("it leads the three rotation blocks",
          a.index("FUND FLOWS") < a.index("SECTOR FLOWS") < a.index("FACTOR FLOWS"),
          "competitor block should come first")
    check("percent-of-fund used", "+30.1%" in a and "-3.8%" in a, f"in:\n{a}")


def test_rotation_block_omitted_when_empty():
    r = sample_report()
    r["sector_rotation"] = [{"ticker": "XLE", "short_bps": None, "bps": None}]
    check("all-missing sector block is omitted, not printed empty",
          "SECTOR FLOWS" not in rd.block_a(r))


def test_block_a_surfaces_warnings():
    check("warnings surfaced", "insufficient history" in rd.block_a(sample_report()))


# ── Block B ───────────────────────────────────────────────────────────────────

def test_block_b_is_separate_and_labelled():
    b = rd.block_b(sample_report())
    check("Block B has its own header", "CROWDING READ" in b)
    check("quadrant names are used", "Sustained crowding" in b and "Crowded but stalling" in b)


def test_block_b_makes_no_prediction():
    """Until the validation gate confirms the sign, no directional claim may appear."""
    b = rd.block_b(sample_report()).lower()
    banned = ["will rise", "will fall", "expect a", "buy ", "sell ", "target price",
              "should outperform", "predicts"]
    found = [w for w in banned if w in b]
    check("Block B contains no directional prediction", not found, f"found {found}")
    check("positioning framing is stated", "positioning, not direction" in b)


def test_block_b_renders_lookthrough():
    from etfflows.lookthrough import Demand
    r = sample_report()
    r["lookthrough"] = [{
        "etf": "SMH", "horizon": 63, "flow_usd": 4.12e9, "direction": "inflow",
        "weights_as_of": "2026-07-31", "reconstitution_warning": False,
        "demands": [
            Demand("NVDA", "NVIDIA", 21.4, 880.8e6, 22e9, 0.040, True, 6.58),
            Demand("TSM", "TSMC", 9.6, 394.4e6, 8e9, 0.049, True, 7.67),
            Demand("AVGO", "Broadcom", 6.6, 272.0e6, None, None, False, None),
        ],
        "held": [Demand("NVDA", "NVIDIA", 21.4, 880.8e6, 22e9, 0.040, True, 6.58)],
    }]
    b = rd.block_b(r)
    check("decomposition header present", "WHAT THE CROWDED VEHICLE IS BUYING" in b)
    check("days of ADV shown, not just dollars", "ADV" in b and "+0.04d" in b, f"got:\n{b}")
    check("held names marked", "*HELD*" in b)
    check("weights as-of surfaced", "2026-07-31" in b)
    check("unknown ADV shows '?', not 0", "?" in b)
    print("\n" + b)


def test_tiny_days_of_adv_do_not_read_as_zero():
    """Mega-cap decompositions land here constantly; '-0.00d' looks like an exact zero."""
    check("tiny positive shows <0.01d", rd._days(0.004) == "<0.01d", rd._days(0.004))
    check("tiny negative shows >-0.01d", rd._days(-0.004) == ">-0.01d", rd._days(-0.004))
    check("a real zero still shows +0.00d", rd._days(0.0) == "+0.00d", rd._days(0.0))
    check("normal magnitudes unchanged", rd._days(0.04) == "+0.04d", rd._days(0.04))
    check("unknown liquidity is '?', never 0", rd._days(None) == "?")


def test_block_b_lookthrough_absent_is_explicit():
    r = sample_report()
    r["lookthrough"] = []
    check("no decomposition says so plainly",
          "no alerting ETF was eligible" in rd.block_b(r))


def test_reconstitution_warning_rendered():
    from etfflows.lookthrough import Demand
    r = sample_report()
    r["lookthrough"] = [{
        "etf": "MTUM", "horizon": 63, "flow_usd": 1e9, "direction": "inflow",
        "weights_as_of": "2026-05-31", "reconstitution_warning": True,
        "demands": [Demand("AVGO", "Broadcom", 5.0, 50e6, 10e9, 0.005, False, None)],
        "held": [],
    }]
    check("rebalance caveat surfaced", "rebalance" in rd.block_b(r))


def test_block_b_quiet_day():
    r = sample_report()
    r["alerts"], r["quadrants"] = [], {}
    check("quiet day says so plainly", "Nothing at extreme positioning" in rd.block_b(r))


# ── full table ────────────────────────────────────────────────────────────────

def test_table_renders_all_rows():
    t = rd.full_table(sample_report())
    for tk in ("SMH", "XLRE", "LYTE"):
        if tk not in t:
            check("all rows rendered", False, f"{tk} missing")
            return
    check("all rows rendered", True)


def test_table_explains_na():
    t = rd.full_table(sample_report())
    check("n/a is explained as 'not zero'", "not a reading of zero" in t)
    check("degraded rows show n/a", "n/a" in t)


def test_table_notes_surfaced():
    check("table notes surfaced", "synthetically backed" in rd.full_table(sample_report()))


def test_empty_table_is_explicit():
    t = rd.full_table({"as_of": "2026-08-18", "rows": []})
    check("empty table says why", "no rows" in t)


# ── assembly ──────────────────────────────────────────────────────────────────

def test_render_main_order():
    m = rd.render_main(sample_report())
    i_fg = m.index("FEAR & GREED")
    i_a = m.index("ETF FLOWS & CROWDING")
    i_b = m.index("CROWDING READ")
    check("Fear & Greed sits above Block A", i_fg < i_a)
    check("Block B follows Block A", i_a < i_b)
    check("full table is NOT in the main section (it goes last in the email)",
          "ETF FLOW DETAIL" not in m)


def test_note_uses_h2_heading():
    """A '#' first heading indexes to ZERO chunks in pg — see chunker-v3-awareness-gap."""
    note = rd.render_note(sample_report())
    first = note.lstrip().splitlines()[0]
    check("note opens with '##'", first.startswith("## ") and not first.startswith("# "),
          f"got {first!r}")


def test_sample_output_is_printable():
    print("\n" + "=" * 86)
    print(rd.render_main(sample_report()))
    print("=" * 86)
    print(rd.render_table(sample_report()))
    print("=" * 86)
    check("sample rendered without error", True)


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
