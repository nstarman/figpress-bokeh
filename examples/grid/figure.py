"""The grid example with figpress-bokeh: four panels on one page, shared axes, panel labels and one
legend. It must match reference.py's matplotlib figure within 1 pt.

    uv run figpress-bokeh build examples/grid/figure.py:grid --out build/
"""

import sys
from pathlib import Path

from bokeh.models import Range1d
from bokeh.plotting import figure

import figpress_bokeh as fb

sys.path.insert(0, str(Path(__file__).parent))
from grid_common import (COLORS, FONT, GAPS, LABELPAD, LEGEND_AT, LINE, MARGINS, PAD, PAGE, SPINE, TICK, X,  # noqa: E402
                    X_RANGE, X_TICKS, Y_RANGE, Y_TICKS, curves)


def panel(k):
    p = figure(x_range=Range1d(*X_RANGE), y_range=Range1d(*Y_RANGE), outline_line_color="black",
               outline_line_width=fb.pt(SPINE))
    p.grid.visible = False
    for ax in p.axis:
        ax.axis_line_color = None  # the outline is the frame
        ax.major_tick_in, ax.major_tick_out = 0, round(fb.pt(TICK))
        ax.minor_tick_in = ax.minor_tick_out = 0
        ax.major_tick_line_width = fb.pt(SPINE)
    model, data = curves(k)
    p.line(X, model, line_color=COLORS["model"], line_width=fb.pt(LINE), tags=["fb:group:model"])
    p.line(X, data, line_color=COLORS["data"], line_width=fb.pt(LINE), line_dash=fb.dash("--", LINE),
           tags=["fb:group:data"])
    return p


@fb.figure(page=PAGE, fonts=fb.dejavu(), margins=MARGINS)
def grid(target):
    a, b, c, d = (panel(k) for k in range(4))
    panels = fb.panels([[a, b], [c, d]], margins=MARGINS, gaps=GAPS, share_x="col", share_y="row",
                       labels="(a)", label_at=(3, 3), label_size=FONT["panel"])
    for p in panels:
        fb.ticklabels(p, "x", X_TICKS, size=FONT["tick"], pad=TICK + PAD)
        fb.ticklabels(p, "y", Y_TICKS, ["−1", "0", "1"], size=FONT["tick"], pad=TICK + PAD)
        fb.axis_label(p, "x", "Time $t$", size=FONT["label"], labelpad=LABELPAD)
        fb.axis_label(p, "y", "Signal $s_k$", size=FONT["label"], labelpad=LABELPAD)
    fb.legend([fb.Entry("model", "Model", line=dict(color=COLORS["model"], width=LINE)),
               fb.Entry("data", "Data", line=dict(color=COLORS["data"], width=LINE, dash="--"))],
              at=LEGEND_AT, size=FONT["legend"], handlelength=2.0, edgecolor="#cccccc", linewidth=SPINE,
              fill_alpha=0.8)
    return panels
