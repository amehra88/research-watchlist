"""
Tests for lookthrough.py (Phase 2). Offline — transports are faked.

What these protect:
  • weight_pct is a PERCENT and must be divided by 100. A missing divide overstates every
    implied-demand figure by 100x and is invisible in a spot check,
  • ADV is DOLLAR volume (volume x price). Mixing share volume with a dollar demand figure
    would make a $900 stock look ~30x more liquid than a $30 one,
  • 'NVDA-US' -> 'NVDA', but genuinely hyphenated tickers (BF-B) survive,
  • synthetic ETFs are never decomposed — swap-backed creations buy no underlying shares,
  • the BCTK intersection is by normalised ticker, so a region suffix cannot cause a silent miss.

Run:  python3 scripts/etfflows/test_lookthrough.py
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from etfflows import lookthrough as lt  # noqa: E402
from etfflows import triggers as tg  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILURES.append(name)


# Real FactSet fund_holdings rows for SMH, pulled 2026-08-19 (as-of 2026-07-31).
SMH_ROWS = [
    {"requestId": "SMH", "date": "2026-07-31", "securityTicker": "NVDA-US",
     "securityName": "NVIDIA CORP  COM", "weightClose": 21.3781180682395},
    {"requestId": "SMH", "date": "2026-07-31", "securityTicker": "TSM-US",
     "securityName": "TAIWAN SEMICONDUCTOR MFG CO LTD  ADR", "weightClose": 9.57007240200994},
    {"requestId": "SMH", "date": "2026-07-31", "securityTicker": "AVGO-US",
     "securityName": "BROADCOM INC COM", "weightClose": 6.60204236059147},
    {"requestId": "SMH", "date": "2026-07-31", "securityTicker": "MU-US",
     "securityName": "MICRON TECHNOLOGY INC  COM", "weightClose": 4.92381749665686},
    {"requestId": "SMH", "date": "2026-07-31", "securityTicker": "DUST-US",
     "securityName": "TINY POSITION", "weightClose": 0.01},
]


class FakeUniverse:
    def __init__(self, synthetic=()):
        self._syn = set(synthetic)

    def synthetic(self, t):
        return t in self._syn


def alert(ticker, flow_usd, horizon=63, z=3.4):
    return tg.Alert(ticker=ticker, horizon=horizon, z=z, percentile=99.4,
                    direction="inflow" if flow_usd > 0 else "outflow",
                    flow_usd=flow_usd, flow_bps=88.3, basis="standalone",
                    corroboration="", severity=abs(z))


# ── ticker normalisation ──────────────────────────────────────────────────────

def test_region_suffix_stripped():
    check("NVDA-US -> NVDA", lt.normalize_ticker("NVDA-US") == "NVDA")
    check("ASML-US -> ASML", lt.normalize_ticker("ASML-US") == "ASML")
    check("bare ticker untouched", lt.normalize_ticker("NVDA") == "NVDA")


def test_hyphenated_tickers_survive():
    """Only a trailing TWO-letter region code comes off."""
    check("BF-B survives", lt.normalize_ticker("BF-B") == "BF-B", lt.normalize_ticker("BF-B"))
    check("BRK-B survives", lt.normalize_ticker("BRK-B") == "BRK-B")


# ── parsing ───────────────────────────────────────────────────────────────────

def test_parse_holdings_shape():
    parsed = lt.parse_holdings(SMH_ROWS)
    check("keyed by ETF", list(parsed) == ["SMH"], f"got {list(parsed)}")
    check("as-of date captured", parsed["SMH"]["as_of"] == "2026-07-31")
    check("tickers normalised",
          parsed["SMH"]["holdings"][0]["ticker"] == "NVDA")
    check("sorted by weight descending",
          [h["ticker"] for h in parsed["SMH"]["holdings"]][:3] == ["NVDA", "TSM", "AVGO"])


def test_compute_adv_is_dollar_volume():
    rows = [{"requestId": "NVDA-US", "volume": 100e6, "price": 220.0},
            {"requestId": "NVDA-US", "volume": 100e6, "price": 220.0}]
    adv = lt.compute_adv(rows)
    check("ADV is volume x price", abs(adv["NVDA"] - 22e9) < 1, f"got {adv}")
    check("ADV is NOT share volume", adv["NVDA"] != 100e6)


def test_compute_adv_skips_nulls():
    rows = [{"requestId": "MU-US", "volume": None, "price": 900.0},
            {"requestId": "MU-US", "volume": 30e6, "price": 900.0}]
    adv = lt.compute_adv(rows)
    check("null rows excluded from the mean", abs(adv["MU"] - 27e9) < 1, f"got {adv}")


# ── the arithmetic ────────────────────────────────────────────────────────────

def test_weight_is_a_percent():
    """THE 100x bug. SMH's 21.378% of a $4.12B inflow is $881M, not $88.1B."""
    parsed = lt.parse_holdings(SMH_ROWS)
    d = lt.implied_demand(4.12e9, parsed["SMH"]["holdings"])
    nvda = next(x for x in d if x.ticker == "NVDA")
    check("21.378% of $4.12B is ~$881M", abs(nvda.implied_usd - 880_778_463) < 1e6,
          f"got ${nvda.implied_usd/1e6:.1f}M")
    check("not 100x larger", nvda.implied_usd < 1e10, f"got {nvda.implied_usd}")


def test_days_of_adv():
    parsed = lt.parse_holdings(SMH_ROWS)
    adv = {"NVDA": 22e9, "MU": 32e9}
    d = lt.implied_demand(4.12e9, parsed["SMH"]["holdings"], adv=adv)
    nvda = next(x for x in d if x.ticker == "NVDA")
    check("days of ADV computed", abs(nvda.days_of_adv - 0.0400) < 0.001,
          f"got {nvda.days_of_adv}")
    print(f"       a 3σ $4.12B SMH inflow = {nvda.days_of_adv:.2f} days of NVDA ADV")
    avgo = next(x for x in d if x.ticker == "AVGO")
    check("missing ADV -> None, not 0", avgo.days_of_adv is None and avgo.adv_usd is None)


def test_outflow_direction_preserved():
    parsed = lt.parse_holdings(SMH_ROWS)
    d = lt.implied_demand(-4.12e9, parsed["SMH"]["holdings"], adv={"NVDA": 22e9})
    nvda = next(x for x in d if x.ticker == "NVDA")
    check("an outflow implies negative demand", nvda.implied_usd < 0)
    check("days of ADV carries the sign", nvda.days_of_adv < 0)


def test_dust_positions_filtered():
    parsed = lt.parse_holdings(SMH_ROWS)
    d = lt.implied_demand(4.12e9, parsed["SMH"]["holdings"])
    check("sub-0.5% dust dropped", all(x.ticker != "DUST" for x in d),
          f"got {[x.ticker for x in d]}")


def test_ranked_by_absolute_size():
    parsed = lt.parse_holdings(SMH_ROWS)
    d = lt.implied_demand(4.12e9, parsed["SMH"]["holdings"])
    sizes = [abs(x.implied_usd) for x in d]
    check("ranked by |implied demand|", sizes == sorted(sizes, reverse=True), f"got {sizes}")


def test_max_names_cap():
    holdings = [{"ticker": f"T{i}", "name": "", "weight_pct": 1.0} for i in range(40)]
    d = lt.implied_demand(1e9, holdings, max_names=5)
    check("constituent list capped", len(d) == 5, f"got {len(d)}")


# ── portfolio intersection ────────────────────────────────────────────────────

def test_portfolio_intersection():
    parsed = lt.parse_holdings(SMH_ROWS)
    portfolio = {"NVDA": 6.58, "MU": 3.10}
    d = lt.implied_demand(4.12e9, parsed["SMH"]["holdings"], portfolio=portfolio)
    held = {x.ticker for x in d if x.in_portfolio}
    check("held names flagged", held == {"NVDA", "MU"}, f"got {held}")
    nvda = next(x for x in d if x.ticker == "NVDA")
    check("portfolio weight carried", nvda.portfolio_weight == 6.58)
    tsm = next(x for x in d if x.ticker == "TSM")
    check("unheld names not flagged", tsm.in_portfolio is False)


def test_bctk_holdings_from_sqlite():
    with tempfile.TemporaryDirectory() as d:
        db = os.path.join(d, "etf_holdings.db")
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE holdings (date TEXT, etf_ticker TEXT, symbol TEXT, "
                    "name TEXT, weight REAL, shares INTEGER, market_value REAL)")
        con.executemany("INSERT INTO holdings VALUES (?,?,?,?,?,?,?)", [
            ("2026-08-19", "BCTK", "NVDA", "NVIDIA", 6.58, 70495, 0.0),
            ("2026-08-19", "BCTK", "TSM", "TSMC", 7.67, 43650, 0.0),
            ("2026-08-18", "BCTK", "NVDA", "NVIDIA", 6.00, 70000, 0.0),  # older date
            ("2026-08-19", "JTEK", "AAPL", "Apple", 5.00, 100, 0.0),     # other fund
        ])
        con.commit()
        con.close()

        h = lt.bctk_holdings(db)
        check("only the latest date is used", h.get("NVDA") == 6.58, f"got {h}")
        check("only the requested fund", "AAPL" not in h, f"got {h}")
        check("both latest rows present", set(h) == {"NVDA", "TSM"}, f"got {set(h)}")


def test_missing_db_is_survivable():
    check("missing db -> empty dict, no raise",
          lt.bctk_holdings("/nonexistent/path/x.db") == {})


# ── orchestration ─────────────────────────────────────────────────────────────

def test_synthetic_etfs_never_decomposed():
    """Swap-backed creations buy no underlying — decomposing them invents demand."""
    uni = FakeUniverse(synthetic={"DRAM"})
    check("synthetic excluded from the work list",
          lt.etfs_to_decompose([alert("DRAM", 1e9), alert("SMH", 1e9)], uni) == ["SMH"])
    res = lt.analyse([alert("DRAM", 1e9)], uni,
                     {"DRAM": {"as_of": "2026-07-31", "holdings": [
                         {"ticker": "MU", "name": "", "weight_pct": 10.0}]}},
                     {}, {})
    check("synthetic produces no decomposition", res == [], f"got {res}")


def test_duplicate_etf_decomposed_once():
    """An ETF alerting on both horizons should cost one holdings call, not two."""
    uni = FakeUniverse()
    work = lt.etfs_to_decompose([alert("SMH", 1e9, horizon=5), alert("SMH", 2e9, horizon=63)], uni)
    check("one entry per ETF", work == ["SMH"], f"got {work}")


def test_analyse_end_to_end():
    uni = FakeUniverse()
    parsed = lt.parse_holdings(SMH_ROWS)
    res = lt.analyse([alert("SMH", 4.12e9)], uni, parsed,
                     {"NVDA": 22e9, "MU": 32e9}, {"NVDA": 6.58})
    check("one result", len(res) == 1)
    r = res[0]
    check("weights as-of surfaced", r["weights_as_of"] == "2026-07-31")
    check("held names extracted", [d.ticker for d in r["held"]] == ["NVDA"],
          f"got {[d.ticker for d in r['held']]}")
    check("no spurious reconstitution warning", r["reconstitution_warning"] is False)


def test_mtum_reconstitution_warning():
    check("MTUM in May flagged", lt.needs_reconstitution_warning("MTUM", "2026-05-31"))
    check("MTUM in November flagged", lt.needs_reconstitution_warning("MTUM", "2026-11-30"))
    check("MTUM in August not flagged",
          not lt.needs_reconstitution_warning("MTUM", "2026-08-31"))
    check("other ETFs never flagged",
          not lt.needs_reconstitution_warning("SMH", "2026-05-31"))


def test_missing_holdings_is_skipped_not_fatal():
    res = lt.analyse([alert("SMH", 1e9)], FakeUniverse(), {}, {}, {})
    check("no holdings -> skipped quietly, no raise", res == [])


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
