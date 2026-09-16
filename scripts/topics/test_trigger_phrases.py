#!/usr/bin/env python3
"""Tests for the trigger-phrase screen over InsiderScore transcript bodies.

No pytest in this env — run directly:
    python3 scripts/topics/test_trigger_phrases.py

Everything here is offline. The MCP call is the one thing not exercised; the
CSV shape below is copied verbatim from a live search_filings result.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trigger_phrases as tp  # noqa: E402

# Verbatim shape of a live result: a "URL To Search" preamble, a blank line,
# then CSV with CRLF rows. Note the RIVN row — the vendor's boolean matched
# "demand" at document level and the snippet does NOT contain the phrase.
LIVE_CSV = (
    'URL To Search: https://www.infilings.com/search.php?stype=all&bodytext="inflection point"\n'
    "\n"
    "ticker,mcap,sector,iacc,basetype,formtype,datefiled,chunkid,sectionid,title,snippet,link\r\n"
    'CRWD,241013783110,Technology,43734507,qanda,TSCRIPT,2026-09-10T00:00:00Z,n-95,830015950,'
    '"George Kurtz (Co-President, Chief Executive Officer, Director, CRWD) - 11",'
    '"I think the **inflection point** for security is going to be a lot sooner and a lot steeper than what we saw with the cloud.",'
    'https://www.infilings.com/v/43734507/?jump=n-95#n-95\r\n'
    'DGX,26256718610,Healthcare,43742489,qanda,TSCRIPT,2026-09-14T00:00:00Z,n-138,830233648,'
    'Erin Wright (Morgan Stanley & Co Ltd) - 22,'
    '"Are you seeing that sort of hit some sort of **inflection point** with pressure across health systems?",'
    'https://www.infilings.com/v/43742489/?jump=n-138#n-138\r\n'
    'RIVN,22963069592,Consumer Discretionary,43746583,qanda,TSCRIPT,2026-09-15T00:00:00Z,n-52,830363480,'
    '"Robert Scaringe (Chairman of the Board of Directors, Chief Executive Officer, Founder, RIVN) - 5",'
    '"Yeah, so if we think about getting to much higher volumes, there is the **demand** side and there is the production side.",'
    'https://www.infilings.com/v/43746583/?jump=n-52#n-52\r\n'
    'CYTK,10072246634,Healthcare,43739669,qanda,TSCRIPT,2026-09-14T00:00:00Z,n-103,830168507,'
    '"Andrew Callos (Executive Vice President, Chief Commercial Officer, CYTK) - 7",'
    '"I would not expect any major hockey stick **inflection point**. I think we are going to see continuous growth.",'
    'https://www.infilings.com/v/43739669/?jump=n-103#n-103\r\n'
    'GILD,181541834244,Healthcare,43745146,presentation,TSCRIPT,2026-09-15T00:00:00Z,n-9,830314998,'
    '"Daniel O\'Day, Chairman of the Board, Chief Executive Officer - 2",'
    '"We, I think, are at another **inflection point** in value.",'
    'https://www.infilings.com/v/43745146/?jump=n-9#n-9\r\n'
)


def _rows():
    return tp.parse_search_csv(LIVE_CSV)


# ───────────────────────── parsing the vendor result ─────────────────────────

def test_parse_strips_the_preamble_and_reads_crlf_csv():
    rows = _rows()
    assert [r["ticker"] for r in rows] == ["CRWD", "DGX", "RIVN", "CYTK", "GILD"]
    assert rows[0]["basetype"] == "qanda" and rows[4]["basetype"] == "presentation"
    assert rows[0]["link"].endswith("#n-95")
    assert set(rows[0]) >= {"ticker", "iacc", "basetype", "datefiled", "chunkid", "title",
                            "snippet", "link", "mcap"}


def test_parse_tolerates_no_results():
    assert tp.parse_search_csv("URL To Search: ...\nNo Results Found\n") == []
    assert tp.parse_search_csv("") == []


# ───────────────────────── the post-filter (mandatory) ─────────────────────────

def test_document_level_match_without_the_phrase_in_the_snippet_is_rejected():
    """The vendor's boolean is document-level. RIVN came back for
    "inflection point" AND (growth OR demand) with a snippet containing only
    "demand". Scoring it would be silent precision collapse."""
    rows = {r["ticker"]: r for r in _rows()}
    assert tp.snippet_contains(rows["CRWD"]["snippet"], "inflection point") is True
    assert tp.snippet_contains(rows["RIVN"]["snippet"], "inflection point") is False


def test_highlight_markers_do_not_break_matching():
    assert tp.snippet_contains("a **step function** change", "step function")
    assert tp.snippet_contains("a **step** function change", "step function")
    assert tp.snippet_contains("Step Function up", "step function")     # case-insensitive


def test_partial_word_does_not_match():
    assert tp.snippet_contains("inflecting hard", "inflection point") is False
    assert tp.snippet_contains("the backlog grew", "log") is False     # whole-phrase only


# ───────────────────────── negation ─────────────────────────

def test_negated_uses_are_detected():
    """Measured: about a third of "step function" hits negate it. Bare
    matching would score "it's not a step function" as bullish."""
    neg = ["It's not a new step function.",
           "I don't think it's going to be a step function change next quarter.",
           "It is not one step function, it's a gradual impact.",
           "I would not expect any major hockey stick inflection point.",
           "We haven't seen an inflection point yet.",
           "rather than a step function, a gradual ramp"]
    for s in neg:
        assert tp.is_negated(s, "step function" if "step" in s else "inflection point") is True, s


def test_affirmative_uses_are_not_flagged_as_negated():
    pos = ["this is a structural change and an inflection in our results and a step function change",
           "We're at step function growth, right?",
           "We, I think, are at another inflection point in value.",
           "I think the inflection point for security is going to be a lot sooner."]
    for s in pos:
        assert tp.is_negated(s, "step function" if "step" in s else "inflection point") is False, s


def test_negation_window_is_local_not_sentence_wide():
    """A 'not' twelve words earlier about something else must not poison the phrase."""
    s = "We did not raise prices this year, and the data center business is at an inflection point."
    assert tp.is_negated(s, "inflection point") is False


# ───────────────────────── who said it ─────────────────────────

def test_speaker_role_from_title_and_basetype():
    rows = {r["ticker"]: r for r in _rows()}
    assert tp.speaker_role(rows["CRWD"]) == "management"      # CEO in title
    assert tp.speaker_role(rows["DGX"]) == "analyst"          # firm in parens, no role
    assert tp.speaker_role(rows["GILD"]) == "management"      # presentation basetype
    assert tp.speaker_role({"basetype": "qanda", "title": "Operator"}) == "unknown"


# ───────────────────────── scoring a row ─────────────────────────

def test_score_row_applies_every_gate_in_order():
    rows = {r["ticker"]: r for r in _rows()}
    ok = tp.score_row(rows["CRWD"], "inflection point", 4, group="upside")
    assert ok and ok["role"] == "management" and ok["weight"] == 4 and ok["negated"] is False
    assert ok["quote"].startswith("I think the inflection point")        # markers stripped
    assert tp.score_row(rows["RIVN"], "inflection point", 4, group="upside") is None   # post-filter
    neg = tp.score_row(rows["CYTK"], "inflection point", 4, group="upside")
    assert neg is not None and neg["negated"] is True and neg["weight"] == 0
    ask = tp.score_row(rows["DGX"], "inflection point", 4, group="upside")
    assert ask["role"] == "analyst"


# ───────────────────────── announce-once ─────────────────────────

def test_hit_id_is_stable_and_specific_to_the_sentence():
    r = _rows()[0]
    a = tp.hit_id(r, "inflection point")
    assert a == tp.hit_id(r, "inflection point")
    assert a != tp.hit_id(r, "step function")
    assert "CRWD" in a and "43734507" in a and "n-95" in a


def test_ledger_suppresses_a_hit_seen_on_a_previous_run():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "trigger_hits.jsonl"
        hits = [tp.score_row(_rows()[0], "inflection point", 4, group="upside")]
        assert tp.append_hits(p, hits, as_of="2026-09-16") == 1
        assert tp.append_hits(p, hits, as_of="2026-09-17") == 0     # same sentence: silent
        recs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        assert len(recs) == 1 and recs[0]["as_of"] == "2026-09-16"


# ───────────────────────── novelty: the newly_said predicate ─────────────────────────

def test_novel_only_with_two_observed_prior_quarters_and_no_prior_use():
    """Mirror of diffusion.newly_said: a filer is 'new' on a phrase only if we
    observed it in each of the prior two quarters and it never said the phrase.
    An unobserved baseline is UNKNOWN, never counted as new — the same guard
    that runs through every detector in this repo."""
    hist = [
        {"ticker": "CRWD", "phrase": "digestion", "cal_quarter": "CY2026-Q1"},
        {"ticker": "CRWD", "phrase": "digestion", "cal_quarter": "CY2026-Q2"},
        {"ticker": "GILD", "phrase": "inflection point", "cal_quarter": "CY2026-Q2"},
    ]
    # CRWD observed Q1 and Q2, never said "inflection point" -> new in Q3
    assert tp.is_novel("CRWD", "inflection point", "CY2026-Q3", hist) is True
    # GILD said it in Q2 -> not new
    assert tp.is_novel("GILD", "inflection point", "CY2026-Q3", hist) is False
    # DGX never observed at all -> unknown, NOT new
    assert tp.is_novel("DGX", "inflection point", "CY2026-Q3", hist) is False
    # CRWD observed in only ONE prior quarter -> unknown
    one = [h for h in hist if not (h["ticker"] == "CRWD" and h["cal_quarter"] == "CY2026-Q1")]
    assert tp.is_novel("CRWD", "inflection point", "CY2026-Q3", one) is False


# ───────────────────────── the universe split ─────────────────────────

def test_watchlist_hits_and_market_hits_are_separated_and_never_blurred():
    hits = [{"ticker": t} for t in ("CRWD", "DGX", "GILD", "RIVN")]
    watch, other = tp.split_by_watchlist(hits, watchlist={"CRWD", "GILD"})
    assert [h["ticker"] for h in watch] == ["CRWD", "GILD"]
    assert [h["ticker"] for h in other] == ["DGX", "RIVN"]
    assert not ({h["ticker"] for h in watch} & {h["ticker"] for h in other})


# ───────────────────────── the phrase file is operator-owned ─────────────────────────

def test_phrase_file_loads_groups_with_weights_and_is_never_written():
    cfg = tp.load_phrases(tp.PHRASES_PATH)
    assert set(cfg["groups"]) >= {"upside", "downside", "regime"}
    for g, items in cfg["groups"].items():
        for it in items:
            assert it["phrase"] and isinstance(it["weight"], int) and it["weight"] > 0, (g, it)
    assert cfg["mcap_floor"] > 0 and cfg["lookback_days"] > 0
    assert not any(n.startswith(("save_", "write_")) and "phrase" in n for n in dir(tp)), \
        "the system never writes the phrase file"


def test_build_query_quotes_and_ors_phrases():
    q = tp.build_query(["inflection point", "step function"])
    assert q == '"inflection point" OR "step function"'


# ───────────────────────── runner ─────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} pass")
    sys.exit(1 if failed else 0)
