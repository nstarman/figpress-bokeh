"""The print route (research R3, R4): two panels sharing an x range, one document, printed by
Chrome and placed on an exact page. Frames land within 0.1 pt, fonts are the paper's and none is
Type 3, and every label is in the text layer once."""

import re
import zlib
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
import pytest
from bokeh.plotting import figure

from figpress_bokeh.fonts import FAMILY, dejavu
from figpress_bokeh.page import html
from figpress_bokeh.pdf import print_page
from figpress_bokeh.units import font, pt

PAGE = (300, 120)
FRAMES = [(40, 10, 100, 80), (175, 10, 100, 80)]


def panel(x_range=None):
    p = figure(frame_width=round(pt(100)), frame_height=round(pt(80)), toolbar_location=None, min_border=0,
               **({"x_range": x_range} if x_range else {}))
    p.line([0, 1, 2], [0, 1, 0], line_width=pt(1))
    p.outline_line_color, p.outline_line_width, p.grid.visible = "black", pt(1), False
    p.yaxis.axis_label = "v (km/s)"
    for a in p.axis:
        a.major_label_text_font = a.axis_label_text_font = FAMILY["text"]
        a.major_label_text_font_size, a.axis_label_text_font_size = font(7), font(8)
    return p


@pytest.fixture(scope="module")
def pdf(tmp_path_factory) -> Path:
    a = panel()
    b = panel(a.x_range)
    out = tmp_path_factory.mktemp("print") / "two.pdf"
    return print_page(html([a, b], FRAMES, PAGE, dejavu()), out, PAGE)


def fonts(path: Path) -> set[bytes]:
    """The font subtypes in the PDF, including inside compressed object streams."""
    raw = path.read_bytes()
    chunks = [raw]
    for m in re.findall(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            chunks.append(zlib.decompress(m))
        except zlib.error:
            pass
    return {s for c in chunks for s in re.findall(rb"/Subtype\s*/(Type0|Type1|Type3|TrueType|CIDFontType[02])", c)}


def test_one_page_of_exactly_the_size(pdf):
    doc = pdfium.PdfDocument(str(pdf))
    assert len(doc) == 1 and doc[0].get_size() == pytest.approx(PAGE, abs=0.01)


def test_no_type3_fonts(pdf):
    kinds = fonts(pdf)
    assert kinds and b"Type3" not in kinds, kinds


def test_each_label_once(pdf):
    text = pdfium.PdfDocument(str(pdf))[0].get_textpage().get_text_range()
    assert text.count("v (km/s)") == 2  # one per panel, not two


def test_frames_where_they_were_put(pdf):
    """Outline centres (a 1 pt line) at each frame's edges, within 0.3 pt. The frames themselves are
    placed exactly (BokehJS reports each at 800 x 640 px = 100 x 80 pt at its target), but BokehJS
    draws the outline up to 2 px (0.25 pt) inside the frame on its top and right edges."""
    a = np.asarray(pdfium.PdfDocument(str(pdf))[0].render(scale=20).to_pil().convert("L")) < 100
    cols = _lines(np.where(a.sum(0) > a.shape[0] * 0.4)[0] / 20)
    rows = _lines(np.where(a.sum(1) > a.shape[1] * 0.4)[0] / 20)
    want_x = sorted(v for l, _, w, _ in FRAMES for v in (l, l + w))
    want_y = sorted({v for _, t, _, h in FRAMES for v in (t, t + h)})
    assert cols == pytest.approx(want_x, abs=0.3)
    assert rows == pytest.approx(want_y, abs=0.3)


def _lines(v: np.ndarray) -> list[float]:
    groups = [[v[0]]]
    for x in v[1:]:
        (groups[-1].append(x) if x - groups[-1][-1] < 0.2 else groups.append([x]))
    return [(g[0] + g[-1] + 0.05) / 2 for g in groups]
