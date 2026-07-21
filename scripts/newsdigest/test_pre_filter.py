"""
Precision test for the boilerplate-category pre-filter (Lever 2). The whole risk is the patterns
being too greedy — dropping a REAL material story. So this asserts, headline by headline:
  • every boilerplate example is caught (13F/holdings, template listicle, routine analyst stub, no-
    catalyst price stub), AND
  • every material example is SPARED — especially the corporate "Nvidia discloses 9.3% stake" which
    shares words ("discloses", "stake") with 13F spam but is a material equity-stake disclosure.

No pytest in this env — run directly:  python3 scripts/newsdigest/test_pre_filter.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from newsdigest import pre_filter  # noqa: E402


# ── must be DROPPED (genuine low-signal boilerplate) ──
BOILERPLATE = [
    # institutional 13F / ownership disclosures
    "SEB Asset Management AB Purchases Shares of 40,221 Taiwan Semiconductor Manufacturing",
    "Commerzbank Aktiengesellschaft FI Sells 130,947 Shares of Intel Corporation",
    "Earned Wealth Advisors LLC Sells 6,596 Shares of Intel Corporation",
    "Piar LLC Discloses Small Tesla Holding",
    "DUTCH ASSET Corp Increases Tesla Holdings",
    "Kornitzer Capital Management initiates position in NVIDIA (NVDA)",
    "OMC Financial Services sells NVIDIA (NVDA) shares",
    "Glenview Trust Co Reduces Analog Devices Holdings",
    "Jennison Associates discloses $30 million ADI holdings position",
    "Amova Asset Management Americas Inc. Has $105.78 Million Stock Position in Taiwan Semiconductor",
    "HORAN Wealth LLC Reports Increased Walmart Holding",
    "Swedish Pension Fund Adds Analog Devices Shares",
    "Independent Financial Group initiates small position in Analog Devices (ADI)",
    # template listicles (Zacks-style)
    "Is Genworth Financial (GNW) Stock Undervalued Right Now?",
    "What Makes Genworth Financial (GNW) a Strong Momentum Stock: Buy Now?",
    "AVTR vs. ICLR: Which Stock Should Value Investors Buy Now?",
    "Is Trending Stock Taiwan Semiconductor Manufacturing Company Ltd. (TSM) a Buy Now?",
    # routine analyst-rating stubs
    "DDOG Maintained by Barclays -- Price Target Raised to $290",
    "DDOG Maintains by Evercore ISI Group -- Price Target Raised to $280",
    "New Buy Rating for Microsoft (MSFT), the Technology Giant",
    # no-catalyst price stubs
    "Micron Stock Up; No Catalyst Named in Headlines",
    "Micron Technology stock movement examined amid semiconductor sector dynamics",
]

# ── must be SPARED (genuine material stories) ──
MATERIAL = [
    "Nvidia Takes 9.3% Equity Stake in Nebius Following $2B Cloud Commitment",
    "Nvidia Discloses 9.3% Ownership Stake in Nebius Group, Shares Rise",
    "Samsung Electronics Formalizes Robotics as a Key Strategic Growth Division",
    "TSMC Plans Wafer Price Increase of Up to 10% by 2027",
    "Tesla Q2 Earnings Miss Expectations Amid EV Market Challenges",
    "Micron Has Strong Q3 Earnings and Rising Guidance. Is It a Buy?",
    "Bank of America Issues Highly Bullish Micron Call, Citing ~83% Share Price Upside",
    "AMD Stock Rises; Move Likely Linked to Microsoft Azure Deal Announcement",
    "Apple Endorses Alibaba AI for China Apple Intelligence Deployment",
    "DDOG Downgraded by Jefferies, Shares Dip 2%",            # a downgrade that MOVED the stock — material
    "Intel Stock Rises Premarket on Reports of Planned Data Center Layoffs Ahead of Earnings",
    "Meta Platforms: Is This the Most Undervalued Stock in Big Tech?",  # thesis piece, not a Zacks "Right Now" template
    "TSMC vs. ASML: Which Is the Better AI Semiconductor Ecosystem Stock to Buy?",  # real thematic compare — 'which is the better', NOT 'which stock should'
]


class FakeC:
    def __init__(self, titles, is_factset=False):
        self.items = [{"title": t, "_is_factset": is_factset} for t in titles]


def test_boilerplate_all_caught():
    missed = [h for h in BOILERPLATE if not pre_filter.is_boilerplate(h)]
    assert not missed, f"boilerplate NOT caught ({len(missed)}):\n  " + "\n  ".join(missed)
    print(f"  ✓ all {len(BOILERPLATE)} boilerplate headlines caught")


def test_material_all_spared():
    wrong = [h for h in MATERIAL if pre_filter.is_boilerplate(h)]
    assert not wrong, f"MATERIAL wrongly flagged boilerplate ({len(wrong)}):\n  " + "\n  ".join(wrong)
    print(f"  ✓ all {len(MATERIAL)} material headlines spared (0 false drops)")


def test_cluster_dropped_only_if_all_boilerplate():
    # a cluster with ANY material headline survives
    mixed = FakeC([BOILERPLATE[0], MATERIAL[0]])
    assert pre_filter.keep_cluster(mixed), "cluster with a material headline must survive"
    allboiler = FakeC([BOILERPLATE[0], BOILERPLATE[1]])
    assert not pre_filter.keep_cluster(allboiler), "all-boilerplate cluster must drop"
    print("  ✓ cluster drops only when EVERY headline is boilerplate")


def test_factset_cluster_exempt():
    allboiler_fa = FakeC([BOILERPLATE[0], BOILERPLATE[1]], is_factset=True)
    assert pre_filter.keep_cluster(allboiler_fa), "FactSet cluster must be exempt even if all-boilerplate"
    print("  ✓ FactSet cluster exempt from the category filter")


if __name__ == "__main__":
    for fn in (test_boilerplate_all_caught, test_material_all_spared,
               test_cluster_dropped_only_if_all_boilerplate, test_factset_cluster_exempt):
        fn()
    print("\nALL PASS — category filter is precise (catches boilerplate, spares material).")
