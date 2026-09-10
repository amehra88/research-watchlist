#!/usr/bin/env python3
"""Tests for scripts/topics/textprep.py — run directly."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import textprep as tp


def test_clean_text_strips_timestamps_and_pleasantries():
    raw = ("Yes. Good afternoon, gentlemen. Thanks for taking my question. Two question from me, please. "
           "First off, do you remain supply-constrained on datacom transceivers? Because (16:40) capacity "
           "comes online. Congrats on the quarter.")
    out = tp.clean_text(raw)
    assert "(16:40)" not in out
    assert "Good afternoon" not in out and "Thanks for taking" not in out and "Congrats" not in out
    assert "supply-constrained on datacom transceivers" in out
    # a long sentence that merely contains "thanks" is content, not a pleasantry
    keep = "Thanks, and on the second point, how should we think about neocloud demand versus hyperscaler demand into next year?"
    assert tp.clean_text(keep) == keep


def test_clean_text_drops_acknowledgement_only_turns():
    # measured 2026-09-10: 205/3,744 analyst turns are acknowledgements — they clustered as
    # "great; almost time; excellent; awesome" and "appreciate; eric; everyone" candidates
    for raw in ("Great, thanks Eric. That's helpful.", "Understood. Thank you.", "Perfect. Got it.",
                "Okay, makes sense. Appreciate it, everyone.", "Yeah.", "[Abrupt Start]"):
        assert tp.clean_text(raw) == "", raw


def test_tokens_and_ngrams_drop_stopwords_and_numbers():
    toks = tp.tokens("The neocloud demand is up 40% in the datacom segment, and the")
    assert "the" not in toks and "40" not in toks and "neocloud" in toks
    grams = tp.ngrams(["neocloud", "demand", "datacom", "segment"], n_max=2)
    assert "neocloud demand" in grams and "demand datacom" in grams and "neocloud" in grams


def test_label_ngrams_prefers_cluster_specific_phrases():
    corpus = ["hyperscaler capex is rising", "hyperscaler capex outlook", "gross margin guidance",
              "neocloud demand for gpus", "neocloud demand is strong", "neocloud customers renting gpus"]
    df = tp.doc_frequencies(corpus)
    cluster = corpus[3:]
    labels = tp.label_ngrams(cluster, df, n_docs=len(corpus), top=3)
    assert labels[0] in ("neocloud demand", "neocloud")
    assert "hyperscaler capex" not in labels


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for f in fns:
        try:
            f(); print(f"  ✓ {f.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1; print(f"  ✗ {f.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns)-bad}/{len(fns)} pass"); sys.exit(1 if bad else 0)
