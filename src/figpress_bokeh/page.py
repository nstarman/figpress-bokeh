"""The HTML page that draws a figure: the same page is printed for the PDF and shown on the web.

All panels are one Bokeh document with one root per panel, so they can share ranges; each root is
embedded in its own absolutely placed element, which the page moves after layout so that the
panel's frame sits exactly where the figure puts it (research R3).
"""

import json

from bokeh.embed.util import OutputDocumentFor, standalone_docs_json_and_render_items
from bokeh.models import Plot
from bokeh.resources import Resources

from .fonts import FAMILY, Fonts
from .units import K


def bokehjs() -> str:
    """BokehJS (the core bundle only) from the installed bokeh, as inline script tags."""
    return Resources(mode="inline", components=["bokeh"]).render_js()


def document(plots: list[Plot]) -> tuple[dict, list[dict]]:
    """The plots as one Bokeh document: its JSON and one render item per panel, rooted at
    `fb-panel-<k>`."""
    with OutputDocumentFor(plots, always_new=True):
        docs, items = standalone_docs_json_and_render_items(plots)
    ids = [p.id for p in plots]
    out = []
    for item in items:
        j = item.to_json()
        j.pop("elementid", None)
        j["roots"] = {mid: f"fb-panel-{ids.index(mid)}" for mid in j["roots"]}
        out.append(j)
    return docs, out


# Runs in the page: no text outlines (BokehJS strokes every label, which Chrome prints as Type 3
# fonts), the fonts before anything is measured, then the figure, then each panel moved so its
# frame lands on its target. `window.fbDrawn` is set once the figure is drawn.
SCRIPT = """
Bokeh.require("core/util/svg").SVGRenderingContext2D.prototype.strokeText = function () {};
(async () => {
  const F = %(figure)s;
  await Promise.all(F.families.map(f => document.fonts.load(`16px ${f}`)));
  await Bokeh.embed.embed_items(F.docs, F.items);
  const views = [...Bokeh.index.roots];
  const placed = [];
  F.frames.forEach(([l, t], k) => {
    const v = views.find(v => v.model.id === F.ids[k]);
    const b = v.frame.bbox, el = document.getElementById(`fb-panel-${k}`);
    el.style.left = `${l - b.left}px`;
    el.style.top = `${t - b.top}px`;
    placed.push([l, t, b.width, b.height]);
  });
  window.fbPlaced = placed;
  window.fbDrawn = true;
})();
"""


def html(plots: list[Plot], frames: list[tuple[float, float, float, float]], page: tuple[float, float],
         fonts: Fonts, title: str = "figure", backend: str = "svg") -> str:
    """The page for `plots`, each with its frame (left, top, width, height in pt) on a page of
    `page` (pt). `backend` is Bokeh's output backend: "svg" for print, "canvas" for the web."""
    if len(plots) != len(frames):
        raise ValueError(f"{len(plots)} panels but {len(frames)} frames")
    for p in plots:
        p.output_backend = backend
    docs, items = document(plots)
    w, h = (v * K for v in page)
    figure = {"docs": docs, "items": items, "ids": [p.id for p in plots], "families": list(FAMILY.values()),
              "frames": [[l * K, t * K] for l, t, _, _ in frames]}
    panels = "".join(f'<div class="fb-panel" id="fb-panel-{k}"></div>' for k in range(len(plots)))
    script = SCRIPT % {"figure": json.dumps(figure).replace("</", "<\\/")}
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><title>{title}</title><style>"
            f"@page{{size:{w:g}px {h:g}px;margin:0}}html,body{{margin:0;background:#fff}}{fonts.css()}"
            f".fb-page{{position:relative;width:{w:g}px;height:{h:g}px;overflow:hidden}}"
            f".fb-panel{{position:absolute;left:0;top:0}}</style>{bokehjs()}</head><body>"
            f'<div class="fb-page">{panels}</div><script>{script}</script></body></html>')
