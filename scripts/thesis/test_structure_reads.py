"""Run directly: python3 scripts/thesis/test_structure_reads.py

`_run_claude` is stubbed throughout -- no real claude -p / network is touched. Every test
that reaches `process_notes` passes an explicit tmp `out_path` (never the module default,
which resolves against the MAIN CHECKOUT's REPO constant, not this worktree) and, where it
reads notes from disk, monkeypatches `structure_reads.NOTES` to a tempdir so nothing here
depends on -- or could corrupt -- the real vault.
"""
import hashlib, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from thesis import structure_reads as SRD  # noqa: E402
from thesis import thesis_io as tio        # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "structure_reads"
NOTE_A = (FIX / "note_a.md").read_text()
NOTE_B = (FIX / "note_b.md").read_text()


# ───────────────────────────── axis_texts (§-extraction) ─────────────────────────────

def test_axis_texts_full_layout_all_five_axes_in_score_keys_order():
    axes = SRD.axis_texts(NOTE_A)
    assert list(axes.keys()) == list(tio.SCORE_KEYS)
    assert "hyperscaler partnership" in axes["ai_positioning"]
    assert axes["competitive_advantage.innovation_rate"].startswith("**Innovation rate**")
    assert "fastest cadence" in axes["competitive_advantage.innovation_rate"]
    assert "Channel partner count" in axes["competitive_advantage.distribution"]
    assert axes["competitive_advantage.overall"].startswith("**Overall**")
    assert "EPS revisions are flat" in axes["potential_investor_interest.score"]


def test_axis_texts_conf_note_missing_section_6_yields_two_axes_only():
    axes = SRD.axis_texts(NOTE_B)
    assert set(axes.keys()) == {"ai_positioning", "potential_investor_interest.score"}
    assert "AI-adjacent supplier" in axes["ai_positioning"]
    assert "non-answer" in axes["potential_investor_interest.score"]


# ───────────────────────────── prompt construction ─────────────────────────────

def test_build_prompt_labels_every_item_with_note_id_and_axis():
    axes = SRD.axis_texts(NOTE_A)
    items = [("ZQTA/note_a.md", axis, text) for axis, text in axes.items()]
    prompt = SRD.build_prompt(items)
    for axis in axes:
        assert f"[note_id: ZQTA/note_a.md | axis: {axis}]" in prompt
    assert "OUTPUT: ONLY a JSON array" in prompt


# ───────────────────────────── _coerce_score ─────────────────────────────

def test_coerce_score_null_int_plus_minus_float_and_bad():
    assert SRD._coerce_score(None) == (None, True)
    assert SRD._coerce_score(4) == (4, True)
    assert SRD._coerce_score(4.0) == (4, True)
    assert SRD._coerce_score("4+") == (4, True)
    assert SRD._coerce_score("3-") == (3, True)
    assert SRD._coerce_score(6) == (None, False)
    assert SRD._coerce_score(0) == (None, False)
    assert SRD._coerce_score(True) == (None, False)          # bool is not a score
    assert SRD._coerce_score("not a number") == (None, False)
    assert SRD._coerce_score(4.5) == (None, False)            # non-integer float


# ───────────────────────────── _validate_row ─────────────────────────────

def _text_by_key():
    axes = SRD.axis_texts(NOTE_A)
    return {("ZQTA/note_a.md", axis): text for axis, text in axes.items()}


def test_validate_row_accepts_a_real_verbatim_quote():
    tbk = _text_by_key()
    quote = "the clearest proof point yet that our silicon wins AI workloads."
    assert quote in tbk[("ZQTA/note_a.md", "ai_positioning")]
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "hyperscaler partnership is real",
          "quote": quote}
    row, reason = SRD._validate_row(obj, tbk)
    assert reason == "ok" and row is not None
    assert row == {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
                   "direction": "up", "magnitude": 1,
                   "reason": "hyperscaler partnership is real", "quote": quote}


def test_validate_row_accepts_null_score():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": None,
          "direction": "flat", "magnitude": 0, "reason": "no score stated",
          "quote": "Drift to"}
    row, reason = SRD._validate_row(obj, tbk)
    assert reason == "ok" and row["score"] is None


def test_validate_row_unknown_note_id_or_axis_key():
    tbk = _text_by_key()
    obj = {"note_id": "NOPE/x.md", "axis": "ai_positioning", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "r", "quote": "Drift"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "unknown_key"


def test_validate_row_bad_axis_not_in_score_keys():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "not_a_real_axis", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "r", "quote": "Drift"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "unknown_key"   # axis not in tbk's keys either -> caught here first


def test_validate_row_bad_axis_branch_when_key_present_but_axis_invalid():
    """Defense-in-depth: axis_texts() never produces a non-SCORE_KEYS axis, so in normal
    _call_batch use "unknown_key" always fires first for a hallucinated axis -- but
    _validate_row's own contract (any axis in tio.SCORE_KEYS) doesn't assume that, so this
    exercises the bad_axis branch directly against a hand-built text_by_key."""
    tbk = {("N1", "bogus_axis"): "some text"}
    obj = {"note_id": "N1", "axis": "bogus_axis", "score": 4, "direction": "up",
          "magnitude": 1, "reason": "r", "quote": "some"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "bad_axis"


def test_validate_row_bad_score_out_of_range():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 9,
          "direction": "up", "magnitude": 1, "reason": "r", "quote": "Drift to"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "bad_score"


def test_validate_row_bad_direction():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
          "direction": "sideways", "magnitude": 1, "reason": "r", "quote": "Drift to"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "bad_direction"


def test_validate_row_bad_magnitude_out_of_range_and_bool_trap():
    tbk = _text_by_key()
    base = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
           "direction": "up", "reason": "r", "quote": "Drift to"}
    row, reason = SRD._validate_row({**base, "magnitude": 3}, tbk)
    assert row is None and reason == "bad_magnitude"
    row, reason = SRD._validate_row({**base, "magnitude": True}, tbk)  # bool is not a magnitude
    assert row is None and reason == "bad_magnitude"


def test_validate_row_reason_too_long():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "x" * 161, "quote": "Drift to"}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "reason_too_long"


def test_validate_row_quote_too_long():
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "r", "quote": "x" * 241}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "quote_too_long"


def test_validate_row_quote_not_verbatim_hard_fail():
    """A quote that is neither present verbatim NOR present after stripping markdown/whitespace --
    the plain reject bucket."""
    tbk = _text_by_key()
    obj = {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
          "direction": "up", "magnitude": 1, "reason": "r",
          "quote": "We will crush the semicap oligopoly this year."}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "quote_not_verbatim"


def test_validate_row_quote_not_verbatim_but_loose_match_bucketed_separately():
    """A quote that's only present after stripping '**' bold markers and collapsing
    whitespace -- still rejected (the schema demands strict verbatim), but bucketed
    distinctly so a re-run can tell 'the model reformats markdown' from 'the model
    hallucinated a quote' without re-spending quota (see structure_reads docstring)."""
    tbk = _text_by_key()
    text = tbk[("ZQTA/note_a.md", "competitive_advantage.innovation_rate")]
    assert "**Innovation rate** (current: 3)" in text   # ground truth: the real text has "**"
    loose_quote = "Innovation rate (current: 3)"        # same string, markdown stripped
    assert loose_quote not in text                       # confirms this is NOT a verbatim hit
    obj = {"note_id": "ZQTA/note_a.md", "axis": "competitive_advantage.innovation_rate",
          "score": 3, "direction": "flat", "magnitude": 0, "reason": "r", "quote": loose_quote}
    row, reason = SRD._validate_row(obj, tbk)
    assert row is None and reason == "quote_not_verbatim_loose_match"


# ───────────────────────────── build_row / append_rows ─────────────────────────────

def test_build_row_id_and_shape():
    obj = {"axis": "ai_positioning", "score": 4, "direction": "up", "magnitude": 1,
          "reason": "r", "quote": "q"}
    row = SRD.build_row("ZQTA/20260101-1Q26.md", obj, "2026-01-01T00:00:00+00:00")
    assert row["ticker"] == "ZQTA"
    assert row["quarter"] == "1Q26"
    assert row["date"] == "2026-01-01"
    assert row["note_id"] == "ZQTA/20260101-1Q26.md"
    assert row["model"] == SRD.MODEL
    assert row["prompt_version"] == "v1"
    expected_id = hashlib.sha1(b"ZQTA/20260101-1Q26.md|ai_positioning|v1").hexdigest()
    assert row["id"] == expected_id


def test_append_rows_is_idempotent():
    tmp = Path(tempfile.mkdtemp()) / "reads.jsonl"
    obj = {"axis": "ai_positioning", "score": 4, "direction": "up", "magnitude": 1,
          "reason": "r", "quote": "q"}
    rows = [SRD.build_row("ZQTA/20260101-1Q26.md", obj, "ts1")]
    res1 = SRD.append_rows(tmp, rows)
    assert res1 == {"written": 1, "dupes": 0}
    res2 = SRD.append_rows(tmp, rows)
    assert res2 == {"written": 0, "dupes": 1}
    lines = [json.loads(l) for l in tmp.read_text().splitlines() if l.strip()]
    assert len(lines) == 1


# ───────────────────────────── _call_batch (stubbed claude -p) ─────────────────────────────

def _one_item():
    axes = SRD.axis_texts(NOTE_A)
    return [("ZQTA/note_a.md", "ai_positioning", axes["ai_positioning"])]


def test_call_batch_clean_run():
    items = _one_item()
    quote = "Drift to"
    assert quote in items[0][2]
    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        arr = [{"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
                "direction": "up", "magnitude": 1, "reason": "stub", "quote": quote}]
        return json.dumps(arr), 0.001
    orig = SRD._run_claude
    SRD._run_claude = stub
    try:
        rows, cost, reasons = SRD._call_batch(items)
    finally:
        SRD._run_claude = orig
    assert len(rows) == 1 and rows[0]["score"] == 4
    assert abs(cost - 0.001) < 1e-9
    assert reasons == {}


def test_call_batch_malformed_json_then_retry_succeeds():
    items = _one_item()
    quote = "Drift to"
    calls = []
    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        calls.append(1)
        if len(calls) == 1:
            return "not json at all", 0.0
        arr = [{"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
                "direction": "up", "magnitude": 1, "reason": "stub", "quote": quote}]
        return json.dumps(arr), 0.001
    orig, orig_sleep = SRD._run_claude, SRD.time.sleep
    SRD._run_claude = stub
    SRD.time.sleep = lambda *_a, **_k: None
    try:
        rows, cost, reasons = SRD._call_batch(items)
    finally:
        SRD._run_claude = orig
        SRD.time.sleep = orig_sleep
    assert len(calls) == 2, "must retry exactly once on malformed JSON"
    assert len(rows) == 1


def test_call_batch_malformed_both_attempts_batch_skipped():
    items = _one_item()
    calls = []
    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        calls.append(1)
        return "still not json", 0.0
    orig, orig_sleep = SRD._run_claude, SRD.time.sleep
    SRD._run_claude = stub
    SRD.time.sleep = lambda *_a, **_k: None
    logged = []
    try:
        rows, cost, reasons = SRD._call_batch(items, logger=logged.append)
    finally:
        SRD._run_claude = orig
        SRD.time.sleep = orig_sleep
    assert len(calls) == 2, "exactly 2 attempts (1 try + 1 retry), never more"
    assert rows == [] and reasons == {}
    assert any("skipped after" in l for l in logged)


def test_call_batch_session_limit_fast_aborts_no_retry():
    items = _one_item()
    calls = []
    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        calls.append(1)
        raise SRD.SessionLimitError("resets 8:30am")
    orig = SRD._run_claude
    SRD._run_claude = stub
    try:
        try:
            SRD._call_batch(items)
            assert False, "expected SessionLimitError to propagate"
        except SRD.SessionLimitError:
            pass
    finally:
        SRD._run_claude = orig
    assert len(calls) == 1, "a 429 must fast-abort after ONE call -- no retry, no split"


def test_call_batch_drops_invalid_row_and_row_with_quote_not_in_text():
    """The brief's required fixture: one stubbed model reply with a fully valid row, one
    row with a bad axis, and one row whose quote is not present verbatim in its section
    text -- exactly one row must survive, and both drops must be bucketed distinctly."""
    axes = SRD.axis_texts(NOTE_A)
    items = [("ZQTA/note_a.md", "ai_positioning", axes["ai_positioning"]),
             ("ZQTA/note_a.md", "potential_investor_interest.score",
              axes["potential_investor_interest.score"])]
    good_quote = "Drift to"
    assert good_quote in axes["ai_positioning"]
    bad_quote = "This sentence was never in the note at all."
    assert bad_quote not in axes["potential_investor_interest.score"]

    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        arr = [
            {"note_id": "ZQTA/note_a.md", "axis": "ai_positioning", "score": 4,
             "direction": "up", "magnitude": 1, "reason": "ok row", "quote": good_quote},
            {"note_id": "ZQTA/note_a.md", "axis": "not_a_real_axis", "score": 4,
             "direction": "up", "magnitude": 1, "reason": "bad axis row", "quote": good_quote},
            {"note_id": "ZQTA/note_a.md", "axis": "potential_investor_interest.score",
             "score": 2, "direction": "flat", "magnitude": 0, "reason": "bad quote row",
             "quote": bad_quote},
        ]
        return json.dumps(arr), 0.002
    orig = SRD._run_claude
    SRD._run_claude = stub
    try:
        rows, cost, reasons = SRD._call_batch(items)
    finally:
        SRD._run_claude = orig
    assert len(rows) == 1 and rows[0]["axis"] == "ai_positioning"
    assert reasons == {"unknown_key": 1, "quote_not_verbatim": 1}


# ───────────────────────────── process_notes (batching + write) ─────────────────────────────

def test_process_notes_dry_run_reports_batches_notes_items_no_writes():
    tmp_notes = Path(tempfile.mkdtemp())
    tdir = tmp_notes / "ZQTA"
    tdir.mkdir()
    pa = tdir / "20260101-1Q26.md"
    pa.write_text(NOTE_A, encoding="utf-8")
    pb = tdir / "20260201-conf-x.md"
    pb.write_text(NOTE_B, encoding="utf-8")
    orig_notes = SRD.NOTES
    SRD.NOTES = tmp_notes
    try:
        summary = SRD.process_notes([pa, pb], dry_run=True)
    finally:
        SRD.NOTES = orig_notes
    assert summary["batches"] == 1          # 2 notes <= BATCH_SIZE(5) -> one batch
    assert summary["notes"] == 2
    assert summary["items"] == 5 + 2         # note_a: 5 axes, note_b: 2 axes
    assert "written" not in summary          # dry run makes no claude -p calls / no writes
    note_ids = {nid for d in summary["detail"] for nid in d["note_ids"]}
    assert note_ids == {"ZQTA/20260101-1Q26.md", "ZQTA/20260201-conf-x.md"}


def test_process_notes_full_run_writes_rows_and_is_idempotent_on_rerun():
    tmp_notes = Path(tempfile.mkdtemp())
    tdir = tmp_notes / "ZQTA"
    tdir.mkdir()
    note_path = tdir / "20260101-1Q26.md"
    note_path.write_text(NOTE_A, encoding="utf-8")
    note_id = "ZQTA/20260101-1Q26.md"
    axes = SRD.axis_texts(NOTE_A)   # ground truth text per axis (independent of NOTES patch)
    out = Path(tempfile.mkdtemp()) / "reads.jsonl"

    calls = []
    def stub(prompt, timeout=SRD.CLAUDE_TIMEOUT_S):
        calls.append(1)
        arr = [{"note_id": note_id, "axis": axis, "score": 4, "direction": "flat",
                "magnitude": 0, "reason": "stub", "quote": text[:20]}
               for axis, text in axes.items()]
        return json.dumps(arr), 0.002
    orig_run, orig_notes = SRD._run_claude, SRD.NOTES
    SRD._run_claude = stub
    SRD.NOTES = tmp_notes
    try:
        summary1 = SRD.process_notes([note_path], out_path=out)
        summary2 = SRD.process_notes([note_path], out_path=out)   # rerun: must be all dupes
    finally:
        SRD._run_claude = orig_run
        SRD.NOTES = orig_notes

    assert len(calls) == 2, "one claude -p call per process_notes() invocation (1 note <= batch size)"
    assert summary1["written"] == 5 and summary1["dupes"] == 0 and summary1["dropped"] == 0
    assert summary2["written"] == 0 and summary2["dupes"] == 5
    lines = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    assert len(lines) == 5
    assert {l["axis"] for l in lines} == set(tio.SCORE_KEYS)
    assert all(l["note_id"] == note_id for l in lines)


# ───────────────────────────── CLI guards (--rebuild) ─────────────────────────────

def test_rebuild_requires_explicit_out_or_yes():
    try:
        SRD.main(["--backfill", "--rebuild"])
        assert False, "expected SystemExit (missing --out/--yes guard)"
    except SystemExit as e:
        assert e.code == 2


def test_rebuild_refuses_ticker_filter():
    tmp = Path(tempfile.mkdtemp()) / "reads.jsonl"
    try:
        SRD.main(["--backfill", "--rebuild", "--out", str(tmp), "--ticker", "AMAT"])
        assert False, "expected SystemExit (--rebuild + --ticker guard)"
    except SystemExit as e:
        assert e.code == 2


if __name__ == "__main__":
    test_axis_texts_full_layout_all_five_axes_in_score_keys_order()
    test_axis_texts_conf_note_missing_section_6_yields_two_axes_only()
    test_build_prompt_labels_every_item_with_note_id_and_axis()
    test_coerce_score_null_int_plus_minus_float_and_bad()
    test_validate_row_accepts_a_real_verbatim_quote()
    test_validate_row_accepts_null_score()
    test_validate_row_unknown_note_id_or_axis_key()
    test_validate_row_bad_axis_not_in_score_keys()
    test_validate_row_bad_axis_branch_when_key_present_but_axis_invalid()
    test_validate_row_bad_score_out_of_range()
    test_validate_row_bad_direction()
    test_validate_row_bad_magnitude_out_of_range_and_bool_trap()
    test_validate_row_reason_too_long()
    test_validate_row_quote_too_long()
    test_validate_row_quote_not_verbatim_hard_fail()
    test_validate_row_quote_not_verbatim_but_loose_match_bucketed_separately()
    test_build_row_id_and_shape()
    test_append_rows_is_idempotent()
    test_call_batch_clean_run()
    test_call_batch_malformed_json_then_retry_succeeds()
    test_call_batch_malformed_both_attempts_batch_skipped()
    test_call_batch_session_limit_fast_aborts_no_retry()
    test_call_batch_drops_invalid_row_and_row_with_quote_not_in_text()
    test_process_notes_dry_run_reports_batches_notes_items_no_writes()
    test_process_notes_full_run_writes_rows_and_is_idempotent_on_rerun()
    test_rebuild_requires_explicit_out_or_yes()
    test_rebuild_refuses_ticker_filter()
    print("OK test_structure_reads")
