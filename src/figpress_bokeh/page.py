"""The HTML page that draws a figure: the same page is printed for the PDF and shown on the web.

All panels are one Bokeh document with one root per panel, so they can share ranges; each root is
embedded in its own absolutely placed element, which the page moves after layout so that the
panel's frame sits exactly where the figure puts it (research R3).
"""

import json
from html import escape as html_escape
from pathlib import Path

from bokeh.embed.util import OutputDocumentFor, standalone_docs_json_and_render_items
from bokeh.models import Plot
from bokeh.resources import Resources

from . import __version__
from .fonts import Fonts, b64


def bokehjs() -> str:
    """BokehJS (the core bundle only) from the installed bokeh, as inline script tags."""
    return Resources(mode="inline", components=["bokeh"]).render_js()


def document(plots: list[Plot], theme=None) -> tuple[dict, list[dict]]:
    """The plots as one Bokeh document (with the paper's `theme`, if any): its JSON and one render
    item per panel, rooted at `fb-panel-<k>`."""
    with OutputDocumentFor(plots, apply_theme=theme, always_new=True):
        docs, items = standalone_docs_json_and_render_items(plots)
    ids = [p.id for p in plots]
    out = []
    for item in items:
        j = item.to_json()
        j.pop("elementid", None)
        j["roots"] = {mid: f"fb-panel-{ids.index(mid)}" for mid in j["roots"]}
        out.append(j)
    return docs, out


RUNTIME = Path(__file__).parent / "js" / "index.js"


def spec(built, fonts: dict[str, str]) -> dict:
    """What the runtime draws (figure.json): the document, its panels' roots and frames (drawing px),
    the page (pt), px per pt, the fonts' URLs by family, and the legend entries' boxes (pt)."""
    for p in built.plots:
        p.output_backend = "svg" if built.target == "pdf" else "canvas"
    docs, items = document(built.plots, built.theme)
    k = built.k
    return {"version": __version__, "name": built.name, "page": list(built.page), "k": k, "docs": docs,
            "items": items, "ids": [p.id for p in built.plots], "frames": [[l * k, t * k] for l, t, _, _ in built.frames],
            "fonts": fonts, "legend": {g: list(b) for g, b in built.entries.items()}}


def inline_fonts(fonts: Fonts) -> dict[str, str]:
    return {fam: f"data:font/ttf;base64,{b64(path)}" for fam, path in fonts.files().items()}


def standalone(built, title: str | None = None, print_: bool = False) -> str:
    """The figure as one self-contained HTML page: BokehJS, the runtime, the figure and its fonts."""
    s = json.dumps(spec(built, inline_fonts(built.fonts))).replace("</", "<\\/")
    w, h = (v * built.k for v in built.page)
    size = f"@page{{size:{w:g}px {h:g}px;margin:0}}" if print_ else ""
    boot = (f'<script type="module">\n{RUNTIME.read_text(encoding="utf-8")}\n'
            f'window.fbFigure = await mount(document.getElementById("figure"), {s}, {{print: {str(print_).lower()}}});\n'
            "</script>")
    return PAGE.format(title=html_escape(title or built.name), version=__version__, style=size, bokeh=bokehjs(), boot=boot)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="figpress-bokeh-version" content="{version}">
<link rel="icon" href="data:,">
<title>{title}</title>
<style>{style}html, body {{ margin: 0; background: #fff; color: #12161c; text-rendering: geometricPrecision; }} #figure {{ width: 100%; }}
html:has(#figure[data-theme="dark"]), html:has(#figure[data-theme="dark"]) body {{
  background: #0b0e14; color: #e5e9f0; color-scheme: dark;
}}</style>
{bokeh}
</head>
<body>
<div id="figure"></div>
{boot}
</body>
</html>
"""


def html(built) -> str:
    """The print page of a figure built for "pdf"."""
    return standalone(built, print_=True)
