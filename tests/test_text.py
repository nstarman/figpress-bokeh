import pytest
from bokeh.models import Range1d
from bokeh.plotting import figure

from figpress_bokeh import dejavu
from figpress_bokeh.figure import Figure, context
from figpress_bokeh.text import SCRIPT, SUB, SUP, _vmetrics, layout, runs, text, width
from figpress_bokeh.units import pt


# The parser is figpress-plotly's (copied); these are its tests.
def test_runs_follow_mathtext():
    assert runs(r"Rate $\lambda_{\rm C}$") == [("Rate ", "text", None), ("λ", "math_italic", None),
                                                ("C", "math_upright", "sub")]
    assert runs(r"$x^2 - 1$") == [("x", "math_italic", None), ("2", "math_upright", "sup"),
                                  (" − 1", "math_upright", None)]


def test_a_script_on_the_text_before():
    assert runs(r"km s$^{-1}$") == [("km s", "text", None), ("−1", "math_upright", "sup")]


def test_unsupported_and_malformed_math_are_named():
    with pytest.raises(ValueError, match=r"\\frac"):
        runs(r"$\frac{1}{2}$")
    with pytest.raises(ValueError, match="nested"):
        runs(r"$x^{y^2}$")
    with pytest.raises(ValueError, match="braces"):
        runs(r"$x^{2$")


def test_layout_places_runs_by_the_font():
    f = dejavu()
    pieces, w = layout(r"Rate $\lambda_{\rm C}$", 10, f)
    rate, lam, c = pieces
    assert rate.dx == 0 and lam.dx == pytest.approx(f.width("Rate ", "text", 10))
    assert c.dx == pytest.approx(lam.dx + f.width("λ", "math_italic", 10))
    assert (c.size, c.dy) == (pytest.approx(10 * SCRIPT), pytest.approx(-SUB * 10))
    assert w == pytest.approx(c.dx + f.width("C", "math_upright", 7))


def test_sup_and_sub_on_one_base_are_stacked():
    (p, sup, sub), w = layout(r"$p^{\rm sim}_{\rm A}$", 7, dejavu())
    assert sup.dx == sub.dx > p.dx and sup.dy == pytest.approx(SUP * 7) and sub.dy == pytest.approx(-SUB * 7)
    assert w == pytest.approx(sup.dx + dejavu().width("sim", "math_upright", 7 * SCRIPT))


def build(fn):
    return Figure(fn, page=(100, 50), frame=(10, 5, 80, 40), fonts=dejavu()).build("pdf")


def test_text_goes_on_the_page_layer_at_page_points():
    def fn(target):
        p = figure()
        text("Hi", 10, 25, 8)
        return p
    layer = build(fn).plots[-1]
    (label,) = layer.center
    a, d = _vmetrics(dejavu().text)  # BokehJS's SVG baseline is (a - d)/2 em low: text() raises it
    assert (label.x, label.y, label.text, label.x_offset) == (10, 25, "Hi", 0)
    assert label.y_offset == pytest.approx(pt((a - d) / 2 * 8))
    assert label.text_font == "fb-text" and label.text_font_size == "64px" and label.text_baseline == "alphabetic"


def test_text_at_a_data_point_and_aligned():
    def fn(target):
        p = figure(x_range=Range1d(0, 1), y_range=Range1d(1, 10), y_axis_type="log")
        assert context().to_page(p, 0.5, 10 ** 0.5) == pytest.approx((50, 25))
        text("Hi", 0.5, 10 ** 0.5, 8, panel=p, ha="right", dx=-2)
        assert width("Hi", 8) == pytest.approx(dejavu().width("Hi", "text", 8))
        return p
    (label,) = build(fn).plots[-1].center
    assert (label.x, label.y) == pytest.approx((48, 25)) and label.x_offset == pytest.approx(-pt(dejavu().width("Hi", "text", 8)))


def test_turned_text_runs_along_its_baseline():
    def fn(target):
        p = figure()
        text("$v_c$", 5, 30, 10, angle=90)
        return p
    v, c = build(fn).plots[-1].center
    w = dejavu().width("v", "math_italic", 10)
    a, d = _vmetrics(dejavu().math_upright)
    above = -SUB * 10 + (a - d) / 2 * 7  # the subscript's drop and the baseline correction
    # along the baseline is up the page; above the baseline is to the left
    assert c.x_offset == pytest.approx(pt(-above)) and c.y_offset == pytest.approx(pt(w))


def test_leading_spaces_become_offset():
    def fn(target):
        p = figure()
        text("a $b$ c", 0, 10, 10)
        return p
    a, b, c = build(fn).plots[-1].center
    f = dejavu()
    assert c.text == "c" and c.x_offset == pytest.approx(pt(f.width("a ", "text", 10) + f.width("b", "math_italic", 10)
                                                              + f.width(" ", "text", 10)))
