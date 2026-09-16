"""
Unit tests for scripts/portal/search_index.py (RIS4 slice 2, Task 5).

Two kinds of coverage: (1) unit tests against small in-test dicts for
tokenize()/build_index()/write_index()'s size fallback, and (2) one
integration test for build_units() that reuses TWO ALREADY-EXISTING fixture
trees rather than adding a new one (the brief says a fixtures/search/ dir is
optional) -- fixtures/vault/ (Task 1's tiny fake notes/ tree: NVDA
earnings/thesis/synthesis/_themes, GOOGL conference, themes/, reports/,
substacks/, podcasts/, flows/, openai.pvt/) supplies discover()+load_note()
coverage across sectioned/unsectioned/ticker/ticker-less notes, and
fixtures/state/notes/news/ (Task 4's 3-row news fixture) supplies
news_bundle() coverage -- these two roots are combined via build_units()'s
own pre-built `refs`/`news`/`ingest` override params, never by pointing two
modules at one merged tree.

No pytest in this env -- run directly:
    python3 scripts/portal/test_search_index.py
"""
import contextlib
import io
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search_index as si  # noqa: E402
import vault as vlt          # noqa: E402
import news_sec               # noqa: E402

VAULT_FIXTURES = Path(__file__).parent / "fixtures" / "vault"
STATE_FIXTURES = Path(__file__).parent / "fixtures" / "state"
TODAY = date(2026, 9, 15)


# ───────────────────────── tokenize() ─────────────────────────

def test_tokenize_golden_sentence():
    # "fast" deliberately mid-sentence (not sentence-final) so it is NOT the
    # word that picks up the trailing-period behavior pinned by the next test.
    text = "NVIDIA's GB200-NVL72 is a state-of-the-art rack, and it runs very fast today."
    toks = si.tokenize(text)
    # lowercased; "nvidia" (apostrophe splits the token, "s" is a single char
    # and never produced); hyphenated terms kept whole ("gb200-nvl72",
    # "state-of-the-art"); stopwords (is/a/and/it/very/of) dropped; no
    # stemming ("rack"/"runs"/"fast" stay as-is, not "rack(s)"/"run"/"fast").
    assert "nvidia" in toks
    assert "gb200-nvl72" in toks
    assert "state-of-the-art" in toks
    assert "rack" in toks
    assert "runs" in toks
    assert "fast" in toks
    for sw in ("is", "and", "it", "very", "of"):
        assert sw not in toks, toks


def test_tokenize_trailing_period_is_not_stripped():
    # brief-literal regex keeps a trailing "." inside the token char class --
    # "nvidia." at the end of a sentence indexes distinct from "nvidia". This
    # is pinned deliberately, not accidental: see the module docstring.
    toks = si.tokenize("Talking about Nvidia.")
    assert "nvidia." in toks
    assert "nvidia" not in toks


def test_tokenize_lowercases_tickers():
    assert si.tokenize("NVDA AVGO") == ["nvda", "avgo"]


def test_tokenize_single_char_tokens_are_dropped():
    # regex requires >= 2 chars; "a" and "I" never survive even before the
    # stoplist is consulted
    assert si.tokenize("a I") == []


def test_tokenize_empty_and_none_safe():
    assert si.tokenize("") == []
    assert si.tokenize(None) == []


def test_tokenize_keeps_duplicates():
    # dedup happens in build_index(), not tokenize()
    assert si.tokenize("gpu gpu gpu") == ["gpu", "gpu", "gpu"]


def test_stoplist_is_lowercase_and_matches_token_charclass():
    for w in si.STOPLIST:
        assert w == w.lower(), w
        assert si.TOKEN_RE.fullmatch(w) or len(w) < 2, w
    assert len(si.STOPLIST) == len(set(si.STOPLIST))
    assert 100 <= len(si.STOPLIST) <= 200


# ───────────────────────── build_index() ─────────────────────────

def _unit(id_, text, **kw):
    base = {"id": id_, "t": "T", "k": "note", "tk": [], "th": [], "d": "2026-09-01",
            "f": "data/tickers/X.json", "s": 0, "sn": "snippet", "text": text}
    base.update(kw)
    return base


def test_build_index_doc_record_shape():
    idx = si.build_index([_unit("a#0", "hello world")])
    assert len(idx["docs"]) == 1
    doc = idx["docs"][0]
    assert set(doc.keys()) == {"id", "t", "k", "tk", "th", "d", "f", "s", "sn"}
    assert "text" not in doc
    assert doc["id"] == "a#0"


def test_build_index_maps_tokens_to_doc_indexes():
    idx = si.build_index([_unit("a#0", "gpu demand"), _unit("b#0", "gpu supply")])
    assert idx["terms"]["gpu"] == [0, 1]
    assert idx["terms"]["demand"] == [0]
    assert idx["terms"]["supply"] == [1]


def test_build_index_docidx_ascending_and_unique_within_a_doc():
    # "gpu" appears twice in the same doc's text -- must appear once in the list
    idx = si.build_index([_unit("a#0", "gpu gpu chips"), _unit("b#0", "gpu")])
    assert idx["terms"]["gpu"] == [0, 1]


def test_build_index_drops_stopwords_from_terms():
    idx = si.build_index([_unit("a#0", "the gpu is fast")])
    assert "the" not in idx["terms"]
    assert "is" not in idx["terms"]
    assert "gpu" in idx["terms"] and "fast" in idx["terms"]


def test_build_index_empty_units():
    idx = si.build_index([])
    assert idx == {"docs": [], "terms": {}}


# ───────────────────────── write_index() size fallback ─────────────────────────

def _news_unit(id_, d):
    return _unit(id_, "gpu " * 50, k="news", d=d, f="data/news/x.json")


def test_write_index_no_fallback_needed(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        units = [_unit("a#0", "small doc")]
        stats = si.write_index(td, units, today=TODAY)
        out = Path(td) / "data" / "search.json"
        assert out.exists()
        payload = json.loads(out.read_text())
        assert "stoplist" in payload and payload["stoplist"] == si.STOPLIST
        assert stats["docs"] == 1
        assert stats["bytes"] == out.stat().st_size


def test_write_index_no_snippet_stage_holds_all_news_rows():
    # corpus A: heavy `sn` (100 chars * 8 news docs), light/shared `text` --
    # the "no_snippet" stage alone (clear sn, keep every row + full text)
    # is enough to clear a threshold the "full" stage misses.
    import tempfile
    other = [_unit("note/x#0", "chips")]
    news = [_unit(f"news/{i}#0", "gpu demand", k="news", d="2026-09-14",
                   f="data/news/x.json", sn="x" * 100, _headline_text="gpu demand")
            for i in range(8)]
    units = other + news
    with tempfile.TemporaryDirectory() as td:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            stats = si.write_index(td, units, today=TODAY, max_bytes=2500)
        logged = buf.getvalue()
        assert "news_mode=full" in logged and "news_mode=no_snippet" in logged
        assert stats["news_mode"] == "no_snippet"
        out = Path(td) / "data" / "search.json"
        payload = json.loads(out.read_text())
        assert payload["news_mode"] == "no_snippet"
        news_docs = [d for d in payload["docs"] if d["k"] == "news"]
        assert len(news_docs) == 8                    # every news row survived
        assert all(d["sn"] == "" for d in news_docs)   # sn cleared, per the brief
        assert "demand" in payload["terms"]            # rationale text still tokenized


def test_write_index_headline_only_stage_holds_all_news_rows():
    # corpus B: light `sn` (no_snippet barely shrinks it) but a large,
    # high-cardinality `text`/rationale -- only "headline_only" (stop
    # tokenizing rationale) clears the threshold; the row itself survives.
    import tempfile
    other = [_unit("note/x#0", "chips")]
    news = [_unit(f"news/{i}#0", " ".join(f"uniqueterm{i}_{j}" for j in range(40)),
                   k="news", d="2026-09-14", f="data/news/x.json", sn="s",
                   _headline_text="gpu")
            for i in range(8)]
    units = other + news
    with tempfile.TemporaryDirectory() as td:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            stats = si.write_index(td, units, today=TODAY, max_bytes=2500)
        logged = buf.getvalue()
        assert "news_mode=no_snippet" in logged and "news_mode=headline_only" in logged
        assert stats["news_mode"] == "headline_only"
        out = Path(td) / "data" / "search.json"
        payload = json.loads(out.read_text())
        assert payload["news_mode"] == "headline_only"
        news_docs = [d for d in payload["docs"] if d["k"] == "news"]
        assert len(news_docs) == 8                     # every news row survived
        assert "gpu" in payload["terms"]                # headline still tokenized
        assert "uniqueterm0_0" not in payload["terms"]  # rationale no longer indexed


def test_write_index_size_fallback_drops_news_progressively():
    import tempfile
    old_units = [_news_unit("news/old#0", "2026-08-01")]   # 45 days before TODAY
    recent_units = [_news_unit("news/new#0", "2026-09-14")]  # 1 day before TODAY
    other = [_unit("note/x#0", "chips" * 5)]
    units = other + old_units + recent_units
    with tempfile.TemporaryDirectory() as td:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            # threshold below every earlier stage's size (forces field cuts
            # AND the window cut) but above the "none" size (so "none" --
            # dropping the still-fresh recent row too -- is never reached)
            stats = si.write_index(td, units, today=TODAY, max_bytes=1500)
        logged = buf.getvalue()
        assert "search.json" in logged and "news_mode" in logged  # each step logged
        assert stats["news_mode"] == "7d"
        out = Path(td) / "data" / "search.json"
        payload = json.loads(out.read_text())
        assert payload["news_mode"] == "7d"
        ids = {d["id"] for d in payload["docs"]}
        assert "note/x#0" in ids
        assert "news/old#0" not in ids   # older than 7d, dropped
        assert "news/new#0" in ids        # within 7d, kept
        assert stats["bytes"] <= out.stat().st_size


def test_write_index_size_fallback_drops_all_news_when_still_oversize():
    import tempfile
    many_news = [_news_unit(f"news/{i}#0", "2026-09-14") for i in range(20)]
    other = [_unit("note/x#0", "chips")]
    units = other + many_news
    with tempfile.TemporaryDirectory() as td:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            stats = si.write_index(td, units, today=TODAY, max_bytes=200)
        assert stats["news_mode"] == "none"
        out = Path(td) / "data" / "search.json"
        payload = json.loads(out.read_text())
        assert payload["news_mode"] == "none"
        ids = {d["id"] for d in payload["docs"]}
        assert ids == {"note/x#0"}   # every news/* unit dropped, even the recent ones


def test_write_index_synthetic_oversize_corpus_with_lowered_threshold():
    import tempfile
    units = [_unit(f"a/{i}#0", "gpu " * 200) for i in range(50)]
    with tempfile.TemporaryDirectory() as td:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            stats = si.write_index(td, units, today=TODAY, max_bytes=500)
        assert "writing anyway" in buf.getvalue()
        assert stats["docs"] == 50   # non-news units are never dropped, only news
        assert stats["news_mode"] == "none"  # no news in this corpus -- ladder runs to the end regardless


# ───────────────────────── build_units() integration ─────────────────────────

def test_build_units_note_sections_and_ingest_and_news():
    refs = vlt.discover(VAULT_FIXTURES)
    news = news_sec.news_bundle(14, news_sec.Paths(notes=STATE_FIXTURES / "notes"), TODAY)
    ingest = vlt.ingest_bundles(refs, days=3650, today=TODAY)
    units = si.build_units(refs=refs, news=news, ingest=ingest, today=TODAY)

    by_id = {u["id"]: u for u in units}

    # NVDA earnings note: 10 "## " sections, ticker set -> data/tickers/NVDA.json
    nvda_sections = [u for u in units if u["id"].startswith("NVDA/20260512-4Q26.md#")]
    assert len(nvda_sections) == 10
    assert all(u["f"] == "data/tickers/NVDA.json" and u["tk"] == ["NVDA"] for u in nvda_sections)

    # NVDA _thesis.md has no "## " headers -> zero section units
    assert not any(u["id"].startswith("NVDA/_thesis.md#") for u in units)

    # theme note (no ticker) routes to data/themes.json
    theme_units = [u for u in units
                   if u["id"].startswith("themes/ai_inference_margin_compression.md#")]
    assert len(theme_units) == 1
    assert theme_units[0]["f"] == "data/themes.json"
    assert theme_units[0]["tk"] == []

    # report note (no ticker, not a theme) -> f is None (no standalone route,
    # documented schema deviation), but still indexed
    report_units = [u for u in units if u["id"].startswith("reports/thesis-delta-20260914.md#")]
    assert len(report_units) == 2
    assert all(u["f"] is None for u in report_units)

    # substack/podcast/flows/pvt come from ingest_bundles, not the section pass
    substack = next(u for u in units if u["k"] == "substack")
    assert substack["f"] == "data/ingest/substacks.json"
    podcast = next(u for u in units if u["k"] == "podcast")
    assert podcast["f"] == "data/ingest/podcasts.json"
    assert podcast["tk"] == ["GOOGL"]
    assert "model_commoditization" in podcast["th"]
    pvt = next(u for u in units if u["k"] == "pvt_profile")
    assert pvt["tk"] == ["openai.pvt"]

    # news rows: 3 fixture notes, all within the 14d window as of TODAY
    news_units = [u for u in units if u["k"] == "news"]
    assert len(news_units) == 3
    assert all(u["f"].startswith("data/news/") for u in news_units)

    # doc ids are unique
    assert len(by_id) == len(units)


def test_note_section_units_route_pvt_ids_to_the_pvt_bundle_path():
    """fix round 1 (Task 8 r1): a `.pvt` id's bundle is data/pvt/<slug>.json
    (the builder strips the suffix for the file name) -- emitting
    data/tickers/openai.pvt.json pointed the app at a file that never exists.
    The fixture vault's only .pvt note is a _profile.md, which is an INGEST
    kind and so never reaches the section pass, hence a tiny temp tree here.
    """
    import shutil
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="ris4_search_pvt_"))
    try:
        (td / "openai.pvt").mkdir()
        (td / "openai.pvt" / "20260601-conf-test-summit.md").write_text(
            '---\ndoc_type: "conference_transcript"\nprimary_ticker: "openai.pvt"\n'
            'event_date: "2026-06-01"\n---\n\n## Headline read\n\nCompute is the constraint.\n',
            encoding="utf-8")
        units = si._note_section_units(vlt.discover(td))
        assert len(units) == 1, units
        assert units[0]["tk"] == ["openai.pvt"]
        assert units[0]["f"] == "data/pvt/openai.json", units[0]["f"]
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_build_units_is_deterministic():
    refs = vlt.discover(VAULT_FIXTURES)
    news = news_sec.news_bundle(14, news_sec.Paths(notes=STATE_FIXTURES / "notes"), TODAY)
    ingest = vlt.ingest_bundles(refs, days=3650, today=TODAY)
    u1 = si.build_units(refs=refs, news=news, ingest=ingest, today=TODAY)
    u2 = si.build_units(refs=refs, news=news, ingest=ingest, today=TODAY)
    assert [u["id"] for u in u1] == [u["id"] for u in u2]


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
