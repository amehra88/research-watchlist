#!/usr/bin/env python3
"""Tests for the P5b stage-transition alert (spec §7.3). Direct-run, no pytest:
    python3 scripts/topics/test_stage_alert.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_alert as sa  # noqa: E402


def _pair(theme, ticker, stage, fe=None, fq=None, banks=()):
    return {"theme": theme, "ticker": ticker, "stage": stage, "first_evidence_date": fe, "first_filing_date": fe,
            "first_question_date": fq, "lag_days": None, "n_evidence": 1 if fe else 0, "n_question": 1 if fq else 0,
            "banks": list(banks)}


def test_diff_emits_forward_moves_only_and_collapses_theme_level_kinds():
    prior = {"pairs": {"t|A": 1, "t|B": 1, "t|C": 1, "u|X": 4}, "gated": []}
    cur = {"pairs": {"t|A": 3, "t|B": 2, "t|C": 2, "t|D": 2, "u|X": 3, "v|Y": 3}, "gated": ["t"]}
    ev = sa.diff_events(prior, cur)
    assert [(e["kind"], e["theme"], e.get("ticker")) for e in ev] == [
        ("gate", "t", None), ("stage2", "t", None), ("stage3", "t", "A"), ("stage3", "v", "Y")], ev
    print("  ✓ forward moves + first gate crossing; regression u|X 4->3 and birth t|D at 2 are silent")


def test_stage4_is_one_line_per_theme():
    ev = sa.diff_events({"pairs": {"t|A": 3, "t|B": 3}, "gated": ["t"]},
                        {"pairs": {"t|A": 4, "t|B": 4}, "gated": ["t"]})
    assert [(e["kind"], e["theme"]) for e in ev] == [("stage4", "t")], ev
    assert sa.event_id(ev[0]) == "stage4:t"
    assert sa.event_id({"kind": "stage3", "theme": "t", "ticker": "A"}) == "stage3:t:A"
    print("  ✓ stage 4 collapses to one theme-level line; ids are stable")


def test_snapshot_stages_and_gate_from_diffusion_shape():
    snap = {"current_quarter": "CY2026-Q3",
            "pairs": [_pair("t", "A", 2, fe="2026-05-01"), _pair("t", "B", None)],
            "metrics": [{"theme": "t", "cal_quarter": "CY2026-Q3", "n_banks": 2, "n_companies": 3, "n_disclosing": 0},
                        {"theme": "t", "cal_quarter": "CY2026-Q2", "n_banks": 0, "n_companies": 0, "n_disclosing": 0},
                        {"theme": "u", "cal_quarter": "CY2026-Q3", "n_banks": 1, "n_companies": 1, "n_disclosing": 1},
                        {"theme": "w", "cal_quarter": "CY2026-Q2", "n_banks": 5, "n_companies": 9, "n_disclosing": 9}]}
    assert sa.snapshot_stages(snap) == {"t|A": 2}
    assert sa.gated_themes(snap) == ["t"]       # w cleared it last quarter, not now: gate is current-quarter only
    print("  ✓ snapshot -> stages map (None skipped) and current-quarter gated themes via theme_notes.clears_gate")


def test_render_stage2_line_matches_spec_shape():
    snap = {"as_of": "2026-09-11", "current_quarter": "CY2026-Q3", "metrics": [],
            "pairs": [_pair("chinese_optical_competition", "AAOI", 3, fe="2026-04-20", fq="2026-08-06", banks=["Raymond James"]),
                      _pair("chinese_optical_competition", "COHR", 2, fe="2026-04-20"),
                      _pair("chinese_optical_competition", "LITE", 2, fe="2026-05-02")]}
    rows = [{"id": "v1", "register": "question", "ticker": "AAOI", "event_date": "2026-08-06", "cal_quarter": "CY2026-Q3",
             "source": "exchange", "event_type": "earnings_call", "themes": [{"theme": "chinese_optical_competition", "score": 0.6}]},
            {"id": "v0", "register": "question", "ticker": "AAOI", "event_date": "2026-08-06", "cal_quarter": "CY2026-Q3",
             "source": "exchange", "event_type": "earnings_call", "themes": [{"theme": "chinese_optical_competition", "score": 0.4}]}]
    ex = {"v1": {"speaker_name": "Simon Leopold", "speaker_firm": "Raymond James", "event_name": "Q2 2026 Earnings Call"},
          "v0": {"speaker_name": "Someone Else", "speaker_firm": "Other", "event_name": "Q2 2026 Earnings Call"}}
    line = sa.render({"kind": "stage2", "theme": "chinese_optical_competition"}, snap, rows, ex, "2026-09-11")
    assert line.startswith("`chinese_optical_competition` moved to stage 2 — AAOI 2026-08-06 (Simon Leopold, Raymond James). "
                           "COHR, LITE still unasked. First evidence 2026-04-20, 144 days ago."), line
    l3 = sa.render({"kind": "stage3", "theme": "chinese_optical_competition", "ticker": "AAOI"}, snap, rows, ex, "2026-09-11")
    assert l3.startswith("`chinese_optical_competition` moved to stage 3 at AAOI — asked 2026-08-06 (Simon Leopold, Raymond James). "
                         "Asked at 1 of 3 covered names."), l3
    l4 = sa.render({"kind": "stage4", "theme": "chinese_optical_competition"}, snap, rows, ex, "2026-09-11")
    assert l4.startswith("`chinese_optical_competition` is now stage 4 (late): asked at 1 of 3 covered names."), l4
    snap["metrics"] = [{"theme": "chinese_optical_competition", "cal_quarter": "CY2026-Q3", "n_banks": 2, "n_companies": 3, "n_disclosing": 4}]
    lg = sa.render({"kind": "gate", "theme": "chinese_optical_competition"}, snap, rows, ex, "2026-09-11")
    assert lg == ("`chinese_optical_competition` crossed the breadth gate in CY2026-Q3: 2 banks / 3 companies asked, "
                  "4 disclosing → notes/themes/chinese_optical_competition.md"), lg
    print("  ✓ the four line shapes read like spec §7.3's example (highest-cosine citation wins)")


def test_run_seeds_silently_then_emails_once_and_absorbs_regressions():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        sa.DIFFUSION, sa.STAGES, sa.LEDGER = d / "diffusion.json", d / "stages.json", d / "alerts_sent.jsonl"
        sent = []
        sa.send = lambda subj, body: sent.append((subj, body))
        sa.load_sources = lambda: ([], {}, {})
        snap = {"as_of": "2026-09-10", "current_quarter": "CY2026-Q3", "metrics": [],
                "pairs": [_pair("t", "A", 1, fe="2026-05-01"), _pair("t", "B", 1, fe="2026-05-01"), _pair("u", "X", 4)]}
        sa.DIFFUSION.write_text(json.dumps(snap))
        assert sa.run(sa.parse(["--run", "--email"])) == 0 and sent == [] and sa.STAGES.exists()
        assert json.loads(sa.STAGES.read_text())["pairs"] == {"t|A": 1, "t|B": 1, "u|X": 4}
        assert sa.run(sa.parse(["--run", "--email"])) == 0 and sent == []              # not newer: no-op
        assert sa.run(sa.parse(["--run", "--email", "--force"])) == 0 and sent == []   # same content: no events
        snap["pairs"] = [_pair("t", "A", 3, fe="2026-05-01", fq="2026-09-11"), _pair("t", "B", 2, fe="2026-05-01"),
                         _pair("u", "X", 3)]
        snap["as_of"] = "2026-09-11"
        sa.DIFFUSION.write_text(json.dumps(snap))
        assert sa.run(sa.parse(["--run", "--email", "--force", "--as-of", "2026-09-11"])) == 0
        assert len(sent) == 1, sent
        subj, body = sent[0]
        assert subj == "Theme stage alert — 2026-09-11 (2 events)", subj
        assert "moved to stage 2" in body and "moved to stage 3 at A" in body and "`u`" not in body, body
        assert json.loads(sa.STAGES.read_text())["pairs"]["u|X"] == 3           # regression absorbed, not announced
        assert sa.run(sa.parse(["--run", "--email", "--force"])) == 0 and len(sent) == 1   # announced once
        ids = {json.loads(l)["id"] for l in sa.LEDGER.read_text().splitlines()}
        assert ids == {"stage2:t", "stage3:t:A"}, ids
    print("  ✓ seed is silent; transitions email once; regressions update state silently")


if __name__ == "__main__":
    test_diff_emits_forward_moves_only_and_collapses_theme_level_kinds()
    test_stage4_is_one_line_per_theme()
    test_snapshot_stages_and_gate_from_diffusion_shape()
    test_render_stage2_line_matches_spec_shape()
    test_run_seeds_silently_then_emails_once_and_absorbs_regressions()
    print("\nALL PASS")
