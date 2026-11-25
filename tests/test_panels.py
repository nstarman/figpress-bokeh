import pytest
from bokeh.models import Range1d
from bokeh.plotting import figure

import figpress_bokeh as fb
from figpress_bokeh.panels import grid_frames


def build(fn, page=(200, 100)):
    return fb.figure(page=page, frame=(0, 0, *page), fonts=fb.dejavu())(fn).build()


def test_grid_frames_fill_the_margins():
    f = grid_frames((200, 100), 2, 2, (20, 5, 10, 15), (10, 6))
    assert f == [(20, 5, 80, 37), (110, 5, 80, 37), (20, 48, 80, 37), (110, 48, 80, 37)]


def test_a_grid_of_panels_is_built():
    def fn(target):
        return fb.panels([[figure(), figure()], [figure(), figure()]], margins=(20, 5, 10, 15), gaps=(10, 6))
    b = build(fn)
    assert len(b.plots) == 5 and b.frames[:4] == grid_frames((200, 100), 2, 2, (20, 5, 10, 15), (10, 6))
    assert b.frames[4] == (0, 0, 200, 100)  # the page layer
    assert b.plots[1].frame_width == round(80 * 8) and b.plots[2].frame_height == round(37 * 8)


def test_explicit_frames():
    def fn(target):
        return fb.panels([figure(), figure()], [(10, 10, 50, 50), (100, 10, 80, 60)])
    assert build(fn).frames[:2] == [(10, 10, 50, 50), (100, 10, 80, 60)]


def test_overlapping_or_off_page_panels_are_named():
    with pytest.raises(ValueError, match="panels 0 and 1 overlap"):
        build(lambda t: fb.panels([figure(), figure()], [(10, 10, 50, 50), (50, 10, 50, 50)]))
    with pytest.raises(ValueError, match="panel 1 .* leaves the page"):
        build(lambda t: fb.panels([figure(), figure()], [(10, 10, 50, 50), (160, 10, 50, 50)]))


def test_grid_or_frames_not_both():
    with pytest.raises(ValueError, match="grid of plots"):
        build(lambda t: fb.panels([figure(), figure()]))


def test_shared_axes_share_one_range():
    def fn(target):
        a, b, c, d = (figure() for _ in range(4))
        a.x_range = Range1d(0, 5)
        p = fb.panels([[a, b], [c, d]], margins=(20, 5, 10, 15), share_x="col", share_y="row")
        assert a.x_range is c.x_range and b.x_range is d.x_range and a.x_range is not b.x_range
        assert a.y_range is b.y_range and c.y_range is d.y_range
        assert isinstance(a.x_range, Range1d) and (a.x_range.start, a.x_range.end) == (0, 5)
        ctx = fb.context()
        assert [ctx.outer[id(q)] for q in p] == [{"x": False, "y": True}, {"x": False, "y": False},
                                                   {"x": True, "y": True}, {"x": True, "y": False}]
        return p
    build(fn)


def test_shared_axes_with_different_ranges_fail():
    def fn(target):
        a, b = figure(x_range=Range1d(0, 5)), figure(x_range=Range1d(0, 6))
        return fb.panels([[a, b]], margins=(20, 5, 10, 15), share_x="all")
    with pytest.raises(ValueError, match="different ranges"):
        build(fn)


def test_panel_labels_in_order():
    def fn(target):
        return fb.panels([[figure(), figure()]], margins=(20, 5, 10, 15), labels="(a)")
    texts = [lab.text for lab in build(fn).plots[-1].center]
    assert texts == ["(a)", "(b)"]


def test_inner_panels_get_no_tick_labels_or_titles():
    def fn(target):
        a, b = figure(x_range=Range1d(0, 1), y_range=Range1d(0, 1)), figure(x_range=Range1d(0, 1), y_range=Range1d(0, 1))
        p = fb.panels([[a, b]], margins=(20, 5, 10, 15), share_y="row")
        for q in p:
            fb.ticklabels(q, "y", [0, 0.5, 1])
            fb.axis_label(q, "y", "Value")
        return p
    texts = [lab.text for lab in build(fn).plots[-1].center]
    assert texts == ["0", "0.5", "1", "Value"]
