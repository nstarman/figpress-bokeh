"""The grid example's numbers, shared by the matplotlib reference and the figpress-bokeh figure.

Four panels on a 2 x 2 grid: the x axis shared down each column and the y axis along each row,
panel labels (a)-(d), and one legend for the figure.
"""

import numpy as np

PAGE = (360.0, 252.0)  # pt
MARGINS = (40.0, 8.0, 84.0, 34.0)  # left, top, right, bottom (pt)
GAPS = (12.0, 12.0)  # between columns, between rows (pt)
SPINE, LINE = 0.8, 1.2  # pt
TICK, PAD, LABELPAD = 3.5, 3.5, 4.0  # matplotlib's defaults: outward ticks, so labels sit TICK + PAD out
FONT = dict(tick=8.0, label=9.0, panel=9.0, legend=7.0)
LEGEND_AT = (284.0, 8.0)  # the legend's top-left corner on the page (pt)
X = np.linspace(0, 10, 200)
X_TICKS, Y_TICKS = [0, 5, 10], [-1, 0, 1]
X_RANGE, Y_RANGE = (0, 10), (-1.6, 1.6)
COLORS = {"model": "#1f77b4", "data": "#ff7f0e"}


def frames():
    """The panels' frames (left, top, width, height in pt), row by row."""
    w, h = PAGE
    ml, mt, mr, mb = MARGINS
    gx, gy = GAPS
    fw, fh = (w - ml - mr - gx) / 2, (h - mt - mb - gy) / 2
    return [(ml + c * (fw + gx), mt + r * (fh + gy), fw, fh) for r in range(2) for c in range(2)]


def curves(k):
    """Panel k's model and data."""
    return np.sin(X * (1 + 0.3 * k)) * np.exp(-X / 12), np.cos(X * (1 + 0.2 * k)) * 0.8
