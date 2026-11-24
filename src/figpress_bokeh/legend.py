"""A legend drawn as matplotlib draws one, on the page layer; its entries toggle their groups on the
web (the runtime finds them by name, `fb-legend:<group>`).

The layout is copied from figpress-plotly src/figpress_plotly/legend.py at f6d48b2.
"""

from dataclasses import dataclass

import numpy as np
from bokeh.models import ColumnDataSource, Patch, Quad, Segment

from .figure import context
from .text import text, width
from .units import dash as to_dash
from .units import pt

ASCENT = 0.76  # where matplotlib puts a legend row's baseline, in sizes below the row's top


@dataclass(frozen=True)
class Entry:
    """A legend entry for `group`: its label and its handle, drawn from what is given: a band (a fill
    colour, or `(colour, alpha)`), the band's upper edge and a line (each
    `dict(color=, width=pt, dash=, alpha=)`)."""

    group: str
    label: str
    line: dict | None = None
    band: str | tuple[str, float] | None = None
    edge: dict | None = None


def _rounded(left, top, right, bottom, r, n=6):
    """The outline of a rectangle with corners rounded as matplotlib's fancybox (quadratic), in page pt."""
    t = np.linspace(0, 1, n)[1:-1]

    def q(p0, p1, p2):
        return [(1 - u) ** 2 * np.array(p0) + 2 * (1 - u) * u * np.array(p1) + u ** 2 * np.array(p2) for u in t]

    pts = [(left + r, top), (right - r, top), *q((right - r, top), (right, top), (right, top + r)),
           (right, top + r), (right, bottom - r), *q((right, bottom - r), (right, bottom), (right - r, bottom)),
           (right - r, bottom), (left + r, bottom), *q((left + r, bottom), (left, bottom), (left, bottom - r)),
           (left, bottom - r), (left, top + r), *q((left, top + r), (left, top), (left + r, top))]
    xs, ys = zip(*pts)
    return list(xs), list(ys)


def legend(entries, at, size, *, title=None, ncol=1, handlelength=2.0, handleheight=0.7, handletextpad=0.8,
           columnspacing=2.0, labelspacing=0.5, borderpad=0.4, fill="white", fill_alpha=0.8, edgecolor="#cccccc",
           linewidth=1.0, color="black") -> tuple[float, float, float, float]:
    """Draw a legend with its top-left corner at page point `at` (pt), laid out as matplotlib lays out
    `ax.legend(..., loc="upper left", bbox_to_anchor=at, borderaxespad=0)` with the same parameters
    (in units of `size`, matplotlib's names and defaults). Entries fill the columns top to bottom.
    Returns the box (left, top, right, bottom) in pt."""
    layer = context().layer
    fs = size
    columns = [list(c) for c in np.array_split(np.array(entries, dtype=object), ncol) if len(c)]
    item_w = [[(handlelength + handletextpad) * fs + width(e.label, fs) for e in col] for col in columns]
    col_w = [max(ws) for ws in item_w]
    cols_w = sum(col_w) + columnspacing * fs * (len(columns) - 1)
    title_w = width(title, fs) if title else 0.0
    content = max(cols_w, title_w)
    rows = max(len(c) for c in columns)
    left, top = at
    pad, sep = borderpad * fs, labelspacing * fs
    # ponytail: every row one `size` tall, as for plain labels; matplotlib's mathtext labels can make a
    # row up to ~0.8 pt taller (seen at 7 pt). Measure label extents with mathtext if that ever exceeds 1 pt.
    height = 2 * pad + (fs + sep if title else 0) + rows * fs + (rows - 1) * sep
    right, bottom = left + content + 2 * pad, top + height

    xs, ys = _rounded(left, top, right, bottom, 0.2 * fs)
    layer.add_glyph(ColumnDataSource(dict(x=xs, y=ys)),
                    Patch(x="x", y="y", fill_color=fill, fill_alpha=fill_alpha, line_color=edgecolor,
                          line_width=pt(linewidth)), name="fb-legend")

    row_top = top + pad
    if title:
        text(title, left + pad + (content - title_w) / 2, row_top + ASCENT * fs, fs, color=color)
        row_top += fs + sep
    cx = left + pad + (content - cols_w) / 2
    for col, cw in zip(columns, col_w):
        for k, e in enumerate(col):
            base = row_top + k * (fs + sep) + ASCENT * fs  # the label's baseline; the handle stands on it
            h = handleheight * fs
            x0, x1 = cx, cx + handlelength * fs
            tag = f"fb-legend:{e.group}"
            if e.band:
                band, band_alpha = (e.band, 1.0) if isinstance(e.band, str) else e.band
                layer.add_glyph(ColumnDataSource(dict(l=[x0], r=[x1], t=[base - 0.9 * h], b=[base - 0.1 * h])),
                                Quad(left="l", right="r", top="t", bottom="b", fill_color=band, fill_alpha=band_alpha,
                                     line_color=None),
                                name=tag)
            for style, at_h in ((e.edge, 0.9), (e.line, 0.5)):
                if style:
                    y = base - at_h * h
                    layer.add_glyph(ColumnDataSource(dict(x0=[x0], x1=[x1], y=[y])),
                                    Segment(x0="x0", x1="x1", y0="y", y1="y", line_color=style["color"],
                                            line_alpha=style.get("alpha", 1.0), line_width=pt(style["width"]),
                                            line_dash=to_dash(style["dash"], style["width"]) if style.get("dash") else []),
                                    name=tag)
            text(e.label, x1 + handletextpad * fs, base, fs, color=color, name=tag)
        cx += cw + columnspacing * fs
    return left, top, right, bottom
