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


if __name__ == "__main__":
    test_diff_emits_forward_moves_only_and_collapses_theme_level_kinds()
    test_stage4_is_one_line_per_theme()
    test_snapshot_stages_and_gate_from_diffusion_shape()
    print("\nALL PASS")
