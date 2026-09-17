"""Run directly: python3 scripts/thesis/test_score_reads.py"""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import score_reads as SR  # noqa: E402
from thesis import match_evidence as M  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "score_reads"


def test_full_layout_every_axis_and_verb():
    text = (FIX / "full_layout.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "hold", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "drift", "value": "4+"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "3"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "5"},
    ]


def test_propose_initial_score_verb_form():
    text = (FIX / "propose_initial_score.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "propose", "value": "2"},
        {"axis": "potential_investor_interest.score", "verb": "propose", "value": "2"},
    ]


def test_bold_colon_article_tolerance():
    text = (FIX / "bold_colon_article.md").read_text()
    recs = SR.parse_recs(text)
    assert recs == [
        {"axis": "ai_positioning", "verb": "drift", "value": "4+"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "hold", "value": "4"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "4"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4-"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "3+"},
    ]


def test_idiom_populate_a_initialize_initiate_establish_initial_score_of():
    text = (FIX / "idiom_populate_a.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "populate", "value": "3+"},
        {"axis": "competitive_advantage.distribution", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.overall", "verb": "populate", "value": "4-"},
        {"axis": "potential_investor_interest.score", "verb": "populate", "value": "4+"},
    ]


def test_idiom_populate_b_proposal_forms_and_reaffirm():
    text = (FIX / "idiom_populate_b.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "populate", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "populate", "value": "3"},
        {"axis": "competitive_advantage.distribution", "verb": "populate", "value": "5"},
        {"axis": "competitive_advantage.overall", "verb": "propose", "value": "4"},   # "propose initial" (no "score") -> existing PROPOSE verb
        {"axis": "potential_investor_interest.score", "verb": "hold", "value": "4"},  # "reaffirm" -> HOLD
    ]


def test_idiom_revise_updown_and_quoted_backticked_values():
    text = (FIX / "idiom_revise_and_quotes.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "revise", "value": "4"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "revise", "value": "4+"},
        {"axis": "competitive_advantage.distribution", "verb": "revise", "value": "3+"},
        {"axis": "competitive_advantage.overall", "verb": "revise", "value": "3"},
        {"axis": "potential_investor_interest.score", "verb": "drift", "value": "4+"},
    ]


def test_idiom_revise_from_prior_quoted_value_skips_the_earlier_quote():
    text = (FIX / "idiom_revise_from_prior.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "revise", "value": "4"}]


def test_idiom_hold_prior_recommendation_of_n_and_unicode_minus_normalized():
    """RIS5 A1 fix round 3: NBIS/20260813-2Q26.md (x2) and HSAI/20260818-2Q26.md phrase a
    genuine HOLD as "hold [at] the (prior|previous|<N>Q<YY>) (recommendation|score) of N" --
    too much text between the verb and the value for VERB_RE's connector, and not covered
    by any fix-round-1 idiom. HSAI's note also uses the Unicode minus (U+2212) for "4−",
    which must normalize to ASCII "-" like every other value in the corpus."""
    text = (FIX / "idiom_hold_prior_recommendation.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "ai_positioning", "verb": "hold", "value": "5"},
        {"axis": "competitive_advantage.innovation_rate", "verb": "hold", "value": "4+"},
        {"axis": "competitive_advantage.distribution", "verb": "hold", "value": "3"},
        {"axis": "competitive_advantage.overall", "verb": "hold", "value": "4-"},
        {"axis": "potential_investor_interest.score", "verb": "hold", "value": "4-"},   # U+2212 -> ASCII "-"
    ]


def test_line_anchored_hedge_in_reasoning_never_wins_over_true_recommendation():
    """RIS5 A1 fix round 2 regression: notes/CSCO/20260513-2Q26.md's real §5 recommendation
    is "Initialize at "4-"" (populate), but its Reasoning bullet hedges "would revise to
    "4"" -- a whole-block search finds that hedge first and gets it wrong. Matching must be
    anchored to the line that starts with "Recommendation"."""
    text = (FIX / "csco_hedge_line_not_matched.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "populate", "value": "4-"}]


def test_line_anchored_recap_before_true_recommendation_never_wins():
    """RIS5 A1 fix round 2 regression: notes/CSCO/20260514-3Q26.md's "Current score" bullet
    recaps last quarter's "Initialize at 4-" before the real (later) "Revise upward ... to
    "4"" recommendation line -- a whole-block search finds the recap's idiom first and gets
    it wrong. Matching must be anchored to the line that starts with "Recommendation"."""
    text = (FIX / "csco_recap_line_not_matched.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "revise", "value": "4"}]


def test_no_recs_note_yields_no_rows():
    text = (FIX / "no_recs.md").read_text()
    assert SR.parse_recs(text) == []


# RIS5 A2 fix round 1: section identification by heading TITLE first, numeric position
# only as a fallback for a BLANK title -- never for a heading with a real, non-matching
# title. Fixtures below reproduce the real headings (titles verbatim, bodies shortened)
# of the three non-canonical conference notes the A2 20-note agreement check found:
# MRVL/20260602-conf-computex-murphy.md, GOOGL/20260422-conf-cloud-next.md, and
# NVDA/20260601-conf-gtc-taipei.md -- none of which use the canonical
# AI-positioning/competitive-advantage/investor-interest section titles anywhere, so all
# three axes must now map to NOTHING (previously score_reads and structure_reads both
# misread these notes' "## 5."/"## 6."/"## 7." headings by number alone).

def test_noncanonical_mrvl_computex_maps_to_nothing():
    """Real headings: '## 5. Market reaction', '## 6. Cross-ticker signal extraction
    (for synthesis cross-reading)', '## 7. Operator-relevant observations' -- none match
    any axis title pattern, so no section/row for this note at all."""
    text = (FIX / "noncanonical_mrvl_computex.md").read_text()
    assert SR._sections(text) == {}
    assert SR.parse_recs(text) == []


def test_noncanonical_googl_cloudnext_maps_to_nothing():
    """Real headings: '## 5. Quantified guidance and TAM claims', '## 6. Strategic
    positioning statements', '## 7. Cross-ticker implications' -- none match."""
    text = (FIX / "noncanonical_googl_cloudnext.md").read_text()
    assert SR._sections(text) == {}
    assert SR.parse_recs(text) == []


def test_noncanonical_nvda_taipei_maps_to_nothing():
    """Real headings: '## 5. Operator-relevant observations', '## 6. Sourcing &
    coverage gaps' -- neither matches; in particular the informal "(anchor 5/5/5)"
    shorthand inside §5's body must NOT be read as an ai_positioning score just because
    it sits at position 5 -- the section itself must not exist."""
    text = (FIX / "noncanonical_nvda_taipei.md").read_text()
    assert SR._sections(text) == {}
    assert SR.parse_recs(text) == []


def test_title_found_at_nonstandard_heading_number():
    """Positive case: a 'Competitive advantage signal' heading at position 8 (not 6) is
    still found and scored correctly -- title identification is number-independent."""
    text = (FIX / "title_at_nonstandard_number.md").read_text()
    assert SR.parse_recs(text) == [
        {"axis": "competitive_advantage.innovation_rate", "verb": "hold", "value": "3"},
        {"axis": "competitive_advantage.distribution", "verb": "hold", "value": "3"},
        {"axis": "competitive_advantage.overall", "verb": "hold", "value": "3"},
    ]


def test_blank_title_heading_falls_back_to_numeric_position():
    """A bare '## 5.' with no title text at all still resolves via the numeric fallback
    (the ONLY case the fallback applies to)."""
    text = (FIX / "blank_title_fallback.md").read_text()
    assert SR.parse_recs(text) == [{"axis": "ai_positioning", "verb": "hold", "value": "4"}]


def test_parse_note_id_earnings_and_conf():
    assert SR.parse_note_id("COHR/20260904-2Q27.md") == ("COHR", "2Q27", "2026-09-04")
    assert SR.parse_note_id("COHR/20260904-conf-analyst-day.md") == ("COHR", None, "2026-09-04")


def test_build_rows_shape_and_applied():
    text = (FIX / "full_layout.md").read_text()
    rows = SR.build_rows("AMAT/20260515-2Q26.md", text, {"ai_positioning": "3"}, "2026-09-16T00:00:00+00:00")
    assert len(rows) == 5
    r0 = rows[0]
    assert r0["ticker"] == "AMAT" and r0["quarter"] == "2Q26" and r0["date"] == "2026-05-15"
    assert r0["note_id"] == "AMAT/20260515-2Q26.md" and r0["axis"] == "ai_positioning"
    assert r0["verb"] == "hold" and r0["value"] == "4" and r0["applied"] == "3"
    # axis with no watchlist entry -> applied is null, not a KeyError
    assert rows[1]["applied"] is None
    ids = {r["id"] for r in rows}
    assert len(ids) == 5   # one id per (note_id, axis)


def test_append_rows_is_idempotent():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-09-16T00:00:00+00:00")
    first = SR.append_rows(tmp, rows)
    assert first == {"written": 5, "dupes": 0}
    second = SR.append_rows(tmp, rows)
    assert second == {"written": 0, "dupes": 5}
    lines = [json.loads(l) for l in tmp.read_text().splitlines() if l.strip()]
    assert len(lines) == 5


def test_append_rows_replace_mode_updates_changed_and_preserves_ts_on_unchanged():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows_v1 = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-01-01T00:00:00+00:00")
    first = SR.append_rows(tmp, rows_v1, replace=True)
    assert first == {"written": 5, "replaced": 0, "unchanged": 0, "changes": []}

    # same content, different ts -> compared on (verb, value, applied) only: nothing changes,
    # and the ORIGINAL ts is kept on disk (not overwritten by the re-run's ts)
    rows_same = [dict(r, ts="2026-02-02T00:00:00+00:00") for r in rows_v1]
    second = SR.append_rows(tmp, rows_same, replace=True)
    assert second["written"] == 0 and second["replaced"] == 0 and second["unchanged"] == 5 and second["changes"] == []
    stored = [json.loads(l) for l in tmp.read_text().splitlines()]
    assert all(r["ts"] == "2026-01-01T00:00:00+00:00" for r in stored)

    # change one row's value -> replaced, with the NEW ts; the other four stay untouched
    rows_v2 = [dict(r) for r in rows_v1]
    rows_v2[0] = dict(rows_v2[0], value="5", ts="2026-03-03T00:00:00+00:00")
    third = SR.append_rows(tmp, rows_v2, replace=True)
    assert third["written"] == 0 and third["replaced"] == 1 and third["unchanged"] == 4
    assert third["changes"] == [{"id": rows_v1[0]["id"],
                                  "old": {"verb": "hold", "value": "4", "applied": None},
                                  "new": {"verb": "hold", "value": "5", "applied": None}}]
    stored2 = {r["id"]: r for r in (json.loads(l) for l in tmp.read_text().splitlines())}
    assert stored2[rows_v1[0]["id"]]["value"] == "5" and stored2[rows_v1[0]["id"]]["ts"] == "2026-03-03T00:00:00+00:00"
    assert stored2[rows_v1[1]["id"]]["ts"] == "2026-01-01T00:00:00+00:00"


def test_append_rows_default_mode_unchanged_by_replace_kwarg_existing():
    """The pre-existing dupe-skip default (replace=False) must be untouched: same shape,
    same counts, for the live-ingest call site (match_evidence.lift_score_recs)."""
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    rows = SR.build_rows("AMAT/20260515-2Q26.md", (FIX / "full_layout.md").read_text(), {}, "2026-09-16T00:00:00+00:00")
    assert SR.append_rows(tmp, rows) == {"written": 5, "dupes": 0}
    assert SR.append_rows(tmp, rows) == {"written": 0, "dupes": 5}


def test_rebuild_requires_explicit_out_or_yes():
    try:
        SR.main(["--backfill", "--rebuild"])
        assert False, "expected SystemExit (missing --out/--yes guard)"
    except SystemExit as e:
        assert e.code == 2


def test_rebuild_refuses_ticker_filter():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    try:
        SR.main(["--backfill", "--rebuild", "--out", str(tmp), "--ticker", "AMAT"])
        assert False, "expected SystemExit (--rebuild + --ticker guard)"
    except SystemExit as e:
        assert e.code == 2


def test_rebuild_wipes_stale_rows_and_writes_fresh():
    """RIS5 A1 fix round 3: --rebuild must not carry forward a row the current parser no
    longer produces (a stale decoy value sitting in a tracked file)."""
    fake_notes = Path(tempfile.mkdtemp()) / "notes"
    (fake_notes / "ZZZZ").mkdir(parents=True)
    (fake_notes / "ZZZZ" / "20260101-1Q26.md").write_text((FIX / "full_layout.md").read_text())
    out = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    # a stale row that no longer matches anything the current parser would produce
    stale_id = SR.hashlib.sha1("ZZZZ/does-not-exist.md|ai_positioning".encode()).hexdigest()
    out.write_text(json.dumps({"id": stale_id, "ticker": "ZZZZ", "quarter": None, "date": "2020-01-01",
                                "note_id": "ZZZZ/does-not-exist.md", "axis": "ai_positioning", "verb": "drift",
                                "value": "5", "applied": None, "ts": "2020-01-01T00:00:00+00:00"}) + "\n")
    orig_notes = SR.NOTES
    SR.NOTES = fake_notes
    try:
        rc = SR.main(["--backfill", "--rebuild", "--out", str(out)])
        assert rc == 0
    finally:
        SR.NOTES = orig_notes
    rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    ids = {r["id"] for r in rows}
    assert stale_id not in ids                       # the stale row is gone, not carried forward
    assert len(rows) == 5                             # exactly this run's 5 full_layout.md rows
    assert {r["note_id"] for r in rows} == {"ZZZZ/20260101-1Q26.md"}


def test_iter_note_paths_finds_amat():
    paths = SR.iter_note_paths("AMAT")
    names = {p.name for p in paths}
    assert "20260515-2Q26.md" in names


def test_lift_score_recs_unchanged_semantics_no_note_id():
    """No note_id/applied given -> pure text parse, no filesystem side effect, same dict
    shape lift_score_recs has always returned: only proposal-worthy verbs, hold/populate excluded."""
    note = (FIX / "full_layout.md").read_text()
    out = M.lift_score_recs(note)
    assert out == {
        "competitive_advantage.innovation_rate": "4+",
        "competitive_advantage.distribution": "3",
        "competitive_advantage.overall": "4",
    }
    assert "ai_positioning" not in out                       # hold at 4 -> reaffirm, no proposal
    assert "potential_investor_interest.score" not in out    # Populate as 5 -> reaffirm, no proposal


def test_lift_score_recs_records_every_verb_when_note_id_given():
    tmp = Path(tempfile.mkdtemp()) / "score_reads.jsonl"
    note = (FIX / "full_layout.md").read_text()
    out = M.lift_score_recs(note, note_id="AMAT/20260515-2Q26.md", applied={}, out_path=tmp)
    assert out == {
        "competitive_advantage.innovation_rate": "4+",
        "competitive_advantage.distribution": "3",
        "competitive_advantage.overall": "4",
    }
    lines = [json.loads(l) for l in tmp.read_text().splitlines() if l.strip()]
    verbs = sorted(r["verb"] for r in lines)
    assert verbs == ["drift", "hold", "populate", "propose", "revise"]   # all six-verb reads recorded, not just proposals


if __name__ == "__main__":
    test_full_layout_every_axis_and_verb(); test_propose_initial_score_verb_form()
    test_bold_colon_article_tolerance()
    test_idiom_populate_a_initialize_initiate_establish_initial_score_of()
    test_idiom_populate_b_proposal_forms_and_reaffirm()
    test_idiom_revise_updown_and_quoted_backticked_values()
    test_idiom_revise_from_prior_quoted_value_skips_the_earlier_quote()
    test_idiom_hold_prior_recommendation_of_n_and_unicode_minus_normalized()
    test_line_anchored_hedge_in_reasoning_never_wins_over_true_recommendation()
    test_line_anchored_recap_before_true_recommendation_never_wins()
    test_no_recs_note_yields_no_rows()
    test_noncanonical_mrvl_computex_maps_to_nothing()
    test_noncanonical_googl_cloudnext_maps_to_nothing()
    test_noncanonical_nvda_taipei_maps_to_nothing()
    test_title_found_at_nonstandard_heading_number()
    test_blank_title_heading_falls_back_to_numeric_position()
    test_parse_note_id_earnings_and_conf(); test_build_rows_shape_and_applied()
    test_append_rows_is_idempotent(); test_iter_note_paths_finds_amat()
    test_rebuild_requires_explicit_out_or_yes()
    test_rebuild_refuses_ticker_filter()
    test_rebuild_wipes_stale_rows_and_writes_fresh()
    test_append_rows_replace_mode_updates_changed_and_preserves_ts_on_unchanged()
    test_append_rows_default_mode_unchanged_by_replace_kwarg_existing()
    test_lift_score_recs_unchanged_semantics_no_note_id()
    test_lift_score_recs_records_every_verb_when_note_id_given()
    print("OK test_score_reads")
