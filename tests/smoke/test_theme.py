"""Light and dark (US5): greys follow the theme, data colours do not, and the layout stays.

Adapted from figpress-plotly tests/smoke/test_theme.py at f6d48b2.
"""

import pytest

pytestmark = pytest.mark.smoke

STATE = """() => { const v = [...Bokeh.index.roots].find(v => v.frame && v.model.renderers.length), p = v.model;
  const line = p.renderers.find(r => (r.glyph.tags || []).includes('fb:group:s2') && r.glyph.type === 'Line');
  return { ground: p.background_fill_color, axis: p.below[0].major_tick_line_color, outline: p.outline_line_color,
           line: line.glyph.line_color, body: getComputedStyle(document.body).backgroundColor,
           frame: [v.frame.bbox.left, v.frame.bbox.top, v.frame.bbox.width] }; }"""


def test_dark_when_asked(open_page, server):
    dark = open_page(url=f"{server}/bands/index.html?theme=dark", width=400)
    light = open_page(url=f"{server}/bands/index.html?theme=light", width=400)
    d, l = dark.evaluate(STATE), light.evaluate(STATE)
    assert d["ground"] == "rgb(11,14,20)" and d["axis"] == "rgb(229,233,240)" and d["outline"] == "rgb(229,233,240)"
    assert d["line"] == l["line"]  # the data's colour stays the paper's
    assert d["frame"] == l["frame"]  # and so does the layout
    assert d["body"] == "rgb(11, 14, 20)" and l["body"] == "rgb(255, 255, 255)"
    assert l["ground"] in ("white", "#ffffff") and l["axis"] in ("black", "#000000")


def test_follows_the_websites_toggle(open_page):
    page = open_page()
    ground = f"({STATE})().ground"
    page.evaluate("document.documentElement.dataset.theme = 'dark'")
    page.wait_for_function(f"{ground} === 'rgb(11,14,20)'")
    page.evaluate("document.documentElement.dataset.theme = 'light'")
    page.wait_for_function(f"['white', '#ffffff'].includes({ground})")


def test_follows_the_system_and_keeps_the_readers_choices(browser, server):
    page = browser.new_page(color_scheme="dark")
    page.goto(f"{server}/grid/index.html")
    page.wait_for_function("window.fbDrawn")
    page.evaluate("fbFigure.toggle('data')")
    page.emulate_media(color_scheme="light")
    page.wait_for_function("fbFigure.theme() === 'light'")
    page.evaluate("fbFigure.redrawn()")
    assert page.evaluate("fbFigure.visible('data')") == [False] * 4
    page.close()
