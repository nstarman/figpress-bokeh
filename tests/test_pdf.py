"""A one-panel figure's PDF (US1): the exact page, only the paper's fonts and none Type 3, no
screen controls, every label once, and a clear message without Chrome."""

import re

import pypdfium2 as pdfium
import pytest
from bokeh.models import Range1d
from bokeh.plotting import figure

import figpress_bokeh as fb
from figpress_bokeh import pdf as pdf_module
from test_print import fonts

STYLE = fb.Style(fb.dejavu(), size=7, label=8)


@fb.figure(page=(200, 150), frame=(40, 8, 150, 110), style=STYLE)
def rotation(target):
    p = figure(x_range=Range1d(0, 20), y_range=Range1d(0, 300))
    p.line([0, 5, 10, 20], [0, 200, 230, 240])
    p.xaxis.axis_label = "Radius (kpc)"
    fb.text(r"$v_{\rm c}$ (km s$^{-1}$)", 12, 63, 8, ha="center", angle=90)
    fb.text("Model", 15, 230, 7, panel=p, va="bottom", dy=-2)
    return p


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    return rotation.write_pdf(tmp_path_factory.mktemp("pdf") / "rotation.pdf")


def test_page_is_exact(out):
    doc = pdfium.PdfDocument(str(out))
    assert len(doc) == 1 and doc[0].get_size() == pytest.approx((200, 150), abs=0.01)


def test_only_the_papers_fonts_and_no_type3(out):
    kinds = fonts(out)
    assert kinds and b"Type3" not in kinds
    names = set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([\w-]+)", out.read_bytes()))
    assert names and names <= {b"DejaVuSerif", b"DejaVuSans", b"DejaVuSans-Oblique", b"DejaVuSerif-Bold"}, names


def test_each_label_once_and_no_screen_controls(out):
    text = pdfium.PdfDocument(str(out))[0].get_textpage().get_text_range()
    for label in ("Radius (kpc)", "Model", "(km s"):
        assert text.count(label) == 1, (label, text)
    assert "Bokeh" not in text


def test_mathematics_is_set_in_the_math_fonts(out):
    names = set(re.findall(rb"/BaseFont\s*/[A-Z]{6}\+([\w-]+)", out.read_bytes()))
    assert {b"DejaVuSans-Oblique", b"DejaVuSans", b"DejaVuSerif"} <= names  # v italic; c and -1 upright; text


def test_no_chrome_says_what_to_install(monkeypatch, tmp_path):
    monkeypatch.setattr("choreographer.browsers.chromium.Chromium.find_browser", staticmethod(lambda **kw: None))
    with pytest.raises(RuntimeError, match="install"):
        pdf_module.chrome()


def test_prints_in_parallel_take_turns(tmp_path):
    """Two processes printing at once share Chrome's profile safely (a showyourwork build runs figure
    scripts in parallel)."""
    import subprocess
    import sys
    from pathlib import Path

    code = ("import sys; sys.path.insert(0, 'tests'); from test_pdf import rotation; "
            "rotation.write_pdf(sys.argv[1])")
    root = Path(__file__).resolve().parents[1]
    procs = [subprocess.Popen([sys.executable, "-c", code, str(tmp_path / f"{k}.pdf")], cwd=root) for k in range(2)]
    assert [p.wait(timeout=180) for p in procs] == [0, 0]
    assert all(pdfium.PdfDocument(str(tmp_path / f"{k}.pdf"))[0].get_size() == pytest.approx((200, 150)) for k in range(2))
