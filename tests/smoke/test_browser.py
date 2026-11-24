"""The web figure in a browser: hover, legend toggles across panels, resize, offline (US2)."""

import re

import pytest

pytestmark = pytest.mark.smoke

# Whether each renderer of a group is visible, across every panel.
VISIBLE = "g => fbFigure.visible(g)"


def entry_point(page, group):
    """The centre of a legend entry's box, in page px."""
    return page.evaluate("""g => {
      const page = document.querySelector('.fb-page').getBoundingClientRect();
      const [l, t, r, b] = fbFigure.legend[g], k = fbFigure.k();
      return [page.x + (l + r) / 2 * k, page.y + (t + b) / 2 * k];
    }""", group)


def test_loads_offline_without_errors(open_page, server):
    page = open_page()
    hosts = {re.match(r"(\w+:)(//[^/]*)?", u).group(0) for u in page.requests}
    assert hosts <= {server, "data:"}, hosts
    assert not page.errors, page.errors
    assert page.evaluate("document.fonts.check('8px fb-text') && document.fonts.check('8px fb-math-it')")


def test_hover_shows_the_line_values(open_page):
    page = open_page(width=600)
    # The 2σ line at p_A = 1%: where it is on screen, from its own panel's view.
    x, y = page.evaluate("""() => {
      const v = [...Bokeh.index.roots].find(v => v.frame && v.model.renderers.length);
      const r = v.model.renderers.find(r => (r.glyph.tags || []).includes('fb:group:s2') && r.glyph.type === 'Line');
      const xs = r.data_source.data.x, ys = r.data_source.data.y, i = Math.floor(xs.length / 2);
      const box = v.el.getBoundingClientRect(), f = v.frame;
      return [box.x + f.x_scale.compute(xs[i]), box.y + f.y_scale.compute(ys[i])];  // the scales give canvas px
    }""")
    page.mouse.move(x - 15, y - 15)
    page.mouse.move(x, y, steps=8)
    tip = page.locator(".bk-tooltip-content").first  # Playwright's CSS reaches into shadow roots
    tip.wait_for(state="visible", timeout=5000)
    text = tip.inner_text()
    assert "2σ" in text and "p_A" in text and "N" in text, text


def test_a_legend_entry_toggles_its_group_in_every_panel_and_survives_resize(open_page):
    page = open_page("grid", width=600)
    assert page.evaluate(VISIBLE, "data") == [True] * 4
    page.mouse.click(*entry_point(page, "data"))
    page.wait_for_function(f"({VISIBLE})('data').every(v => !v)")
    assert page.evaluate(VISIBLE, "model") == [True] * 4
    assert page.evaluate("fbFigure.hidden()") == ["data"]
    before = page.evaluate("fbFigure.zoom()")
    page.set_viewport_size({"width": 400, "height": 900})
    page.wait_for_function(f"fbFigure.zoom() < {before} * 0.8")  # redrawn at the narrower width
    page.evaluate("fbFigure.redrawn()")
    assert page.evaluate(VISIBLE, "data") == [False] * 4
    page.mouse.click(*entry_point(page, "data"))
    page.wait_for_function(f"({VISIBLE})('data').every(v => v)")


def test_the_single_file_works_from_disk(open_page, built):
    page = open_page(url=(built / "bands.html").as_uri())
    assert not page.errors, page.errors
    assert {re.match(r"\w+:", u).group(0) for u in page.requests} <= {"file:", "data:"}
    assert page.evaluate("document.fonts.check('8px fb-text')")
