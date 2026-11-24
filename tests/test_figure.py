import pytest
from bokeh.models import Label
from bokeh.plotting import figure

import figpress_bokeh as fb


def test_the_decorator_gives_a_figure():
    @fb.figure(page=(100, 50), frame=(10, 5, 80, 40), fonts=fb.dejavu())
    def f(target):
        return figure()
    assert isinstance(f, fb.Figure) and f.name == "f" and callable(f.write_pdf)
    b = f.build("pdf")
    panel, layer = b.plots
    assert b.frames == [(10, 5, 80, 40), (0.0, 0.0, 100, 50)]
    assert (panel.frame_width, panel.frame_height, panel.toolbar_location, panel.toolbar.logo) == (640, 320, None, None)
    assert layer.name == "fb-page-layer"


def test_frame_from_the_style_margins():
    @fb.figure(page=(100, 50), style=fb.Style(fb.dejavu(), margins=(20, 5, 5, 15)))
    def f(target):
        return figure()
    assert f.frame == (20, 5, 75, 30)


def test_fonts_are_required_and_frames_checked():
    with pytest.raises(ValueError, match="fonts"):
        fb.figure(page=(100, 50), frame=(10, 5, 80, 40))(lambda t: figure())
    with pytest.raises(ValueError, match="inside the page"):
        fb.figure(page=(100, 50), frame=(30, 5, 80, 40), fonts=fb.dejavu())(lambda t: figure())


def test_build_must_return_a_plot():
    f = fb.figure(page=(100, 50), frame=(10, 5, 80, 40), fonts=fb.dejavu())(lambda t: "nope")
    with pytest.raises(TypeError, match="not str"):
        f.build()


def test_text_outlines_are_refused():
    def fn(target):
        p = figure()
        p.add_layout(Label(x=0, y=0, text="x", text_outline_color="red"))
        return p
    with pytest.raises(ValueError, match="text_outline_color"):
        fb.figure(page=(100, 50), frame=(10, 5, 80, 40), fonts=fb.dejavu())(fn).build()


def test_the_figures_own_settings_win_over_the_style():
    from figpress_bokeh.page import document

    @fb.figure(page=(100, 50), style=fb.Style(fb.dejavu(), size=8))
    def f(target):
        p = figure()
        p.xaxis.major_label_text_font_size = "10px"
        return p
    b = f.build()
    docs, _ = document(b.plots, b.theme)  # the theme is applied while the document is serialized
    root = next(iter(docs.values()))["roots"][0]["attributes"]
    y, x = (a["attributes"].get("major_label_text_font_size") for a in root["left"] + root["below"])
    assert (x, y) == ("10px", "64px")
