"""Tick labels and axis titles placed as matplotlib places them, in the paper's fonts.

Bokeh draws its own tick labels with its own rules (it pulls the end labels inward, and its
padding differs), so a port draws them with these instead and Bokeh's are hidden.
"""

from bokeh.models import FixedTicker, Plot

from .figure import context
from .text import _lp, line_height, text, width


def ticklabels(panel: Plot, axis: str, values, labels=None, *, size: float = 8.0, pad: float = 3.5,
               minor=None, color: str = "black") -> float:
    """Ticks at `values` (and `minor`) on `panel`'s bottom ("x") or left ("y") axis, with their labels
    drawn `pad` pt from the frame (matplotlib's pad, plus the tick length for outward ticks), centred
    on their ticks. `labels` default to the values formatted with `:g`. Inner panels of shared axes
    (see `fb.panels`) get ticks but no labels. Returns how far the labels reach from the frame (pt)."""
    if axis not in ("x", "y"):
        raise ValueError(f"axis must be 'x' or 'y', not {axis!r}")
    ctx = context()
    values = list(values)
    labels = [f"{v:g}" for v in values] if labels is None else list(labels)
    if len(labels) != len(values):
        raise ValueError(f"{len(values)} ticks but {len(labels)} labels")
    ticker = FixedTicker(ticks=values, minor_ticks=list(minor or []))
    for ax in (panel.xaxis if axis == "x" else panel.yaxis):
        ax.ticker = ticker
        ax.major_label_text_color = None  # Bokeh's own labels are not drawn: these are
    left, top, fw, fh = ctx.frame_of(panel)
    drawn = ctx.outer.get(id(panel), {"x": True, "y": True})[axis]
    reach = pad + (line_height(size) if axis == "x" else max((width(s, size) for s in labels), default=0.0))
    if drawn:
        lo, hi = (panel.x_range.start, panel.x_range.end) if axis == "x" else (panel.y_range.start, panel.y_range.end)
        ascent = _lp(ctx.fonts.text)[0] * size
        for v, s in zip(values, labels):
            if not min(lo, hi) <= v <= max(lo, hi):
                continue
            x, y = ctx.to_page(panel, v if axis == "x" else panel.x_range.start,
                               panel.y_range.start if axis == "x" else v)
            if axis == "x":
                text(s, x, top + fh + pad, size, ha="center", va="top", color=color)
            else:  # matplotlib's "center_baseline": the baseline half the line's ascent below the tick
                text(s, left - pad, y + ascent / 2, size, ha="right", color=color)
    ctx.extents[(id(panel), axis)] = reach if drawn else 0.0
    return reach


def axis_label(panel: Plot, axis: str, s: str, *, size: float = 9.0, labelpad: float = 4.0,
               color: str = "black") -> None:
    """The title of `panel`'s bottom ("x") or left ("y") axis, `labelpad` pt beyond its tick labels,
    centred on the frame (the y title turned to read upwards), as matplotlib places it. Inner panels
    of shared axes get none."""
    ctx = context()
    if not ctx.outer.get(id(panel), {"x": True, "y": True})[axis]:
        return
    left, top, fw, fh = ctx.frame_of(panel)
    reach = ctx.extents.get((id(panel), axis), 0.0)
    if axis == "x":
        text(s, left + fw / 2, top + fh + reach + labelpad, size, ha="center", va="top", color=color)
    else:
        text(s, left - reach - labelpad, top + fh / 2, size, ha="center", va="bottom", angle=90, color=color)
