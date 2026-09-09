"""Run directly: python3 scripts/v3_ingest/test_sec_pdf_exhibits.py  (no network: exhibit map + http stubbed)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sec_filings as S  # noqa: E402

def _pdf(text: str = "Investor Day 2026 capacity plan") -> bytes:
    """Minimal one-page PDF with a real xref table (pypdf refuses files without startxref)."""
    stream = f"BT /F1 14 Tf 20 150 Td ({text}) Tj ET".encode()
    objs = [b"<</Type/Catalog/Pages 2 0 R>>", b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 300]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
            b"<</Length " + str(len(stream)).encode() + b">>stream\n" + stream + b"\nendstream",
            b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>"]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<</Size {len(objs) + 1}/Root 1 0 R>>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


PDF = _pdf()


class _Resp:
    def __init__(self, content=b"", text=""):
        self.content, self.text = content, text


def _stub(exmap):
    S.fetch_exhibit_map = lambda cik, acc: exmap
    S.http_get = lambda url: _Resp(content=PDF, text="<html><body><p>press release text here</p></body></html>")


def test_pdf_to_text_extracts_and_caps():
    t = S.pdf_to_text(PDF)
    assert "Investor Day 2026" in t
    assert S.pdf_to_text(PDF, max_chars=8) == "Investor"


def test_8k_pdf_only_on_presentation_items():
    _stub({"8-K": "a.htm", "EX-99.1": "deck.pdf"})
    assert S.fetch_ex99(1, "0000000000-26-000001", form="8-K", items=["7.01", "9.01"])[0][0] == "EX-99.1 (slides)"
    assert S.fetch_ex99(1, "0000000000-26-000001", form="8-K", items=["5.02"]) == []


def test_6k_pdf_always_and_html_untouched():
    _stub({"6-K": "a.htm", "EX-99.1": "pr.htm", "EX-99.2": "report.pdf"})
    out = S.fetch_ex99(1, "0000000000-26-000002", form="6-K", items=[])
    assert [o[0] for o in out] == ["EX-99.1", "EX-99.2 (slides)"] and "press release" in out[0][2] and "Investor Day" in out[1][2]


if __name__ == "__main__":
    test_pdf_to_text_extracts_and_caps(); test_8k_pdf_only_on_presentation_items(); test_6k_pdf_always_and_html_untouched()
    print("OK test_sec_pdf_exhibits")
