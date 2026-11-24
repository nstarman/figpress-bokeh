"""The example with figpress-bokeh: one definition for the print figure and the web figure. It must
match reference.py's matplotlib figure within 1 pt.

    uv run figpress-bokeh build examples/bands/figure.py:bands --out build/
"""

import sys
from pathlib import Path

import numpy as np
from bokeh.models import Arrow, FixedTicker, LogAxis, NormalHead, Range1d, Span
from bokeh.plotting import figure

import figpress_bokeh as fb
from figpress_bokeh.text import SCRIPT, line_height

sys.path.insert(0, str(Path(__file__).parent))
from common import (FONT, FRAME, LEGEND, N_MAX, N_MIN, P, P_MAX, P_MIN, P_SIM, PAGE, R_HI, R_LO,  # noqa: E402
                    R_PAPER, SIGMAS, SPINE, SURVEYS, n_required, sigma_color)

# matplotlib's defaults for what the reference does not set (pt)
TICK = dict(major=3.5, minor=2.0, major_width=0.8, minor_width=0.6, pad=3.5)
LABELPAD = 4.0
# mathtext's "10^k" tick labels, measured in the reference: the power rises 0.4125 of the size and
# 1.18 pt of space follows it.
POWER_RISE, POWER_SPACE = 0.4125, 1.18


def hex_(rgb):
    return "#" + "".join(f"{round(255 * c):02x}" for c in rgb)


def gray(level):
    return hex_((float(level),) * 3)


def axis_style(ax, labels: bool):
    ax.axis_line_width = fb.pt(SPINE)
    ax.major_tick_in, ax.major_tick_out = round(fb.pt(TICK["major"])), 0
    ax.minor_tick_in, ax.minor_tick_out = round(fb.pt(TICK["minor"])), 0
    ax.major_tick_line_width, ax.minor_tick_line_width = fb.pt(TICK["major_width"]), fb.pt(TICK["minor_width"])
    ax.major_label_text_font, ax.major_label_text_font_size = "fb-text", fb.font(FONT["tick"])
    ax.major_label_standoff = round(fb.pt(TICK["pad"]))
    if not labels:
        ax.major_label_overrides = {v: "" for v in ax.ticker.ticks}


@fb.figure(page=PAGE, frame=FRAME, fonts=fb.dejavu())
def bands(target):
    major_x = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
    minor_x = [m * 10.0**k for k in (-3, -2) for m in range(2, 10)
               if m * 10.0**k <= P_MAX and not np.any(np.isclose(m * 10.0**k, major_x))]
    major_y = [1e2, 1e3, 1e4, 1e5]
    minor_y = [m * 10.0**k for k in range(2, 6) for m in range(2, 10) if m * 10.0**k <= N_MAX]
    xt, yt = FixedTicker(ticks=major_x, minor_ticks=minor_x), FixedTicker(ticks=major_y, minor_ticks=minor_y)

    p = figure(x_axis_type="log", y_axis_type="log", x_range=Range1d(P_MIN, P_MAX), y_range=Range1d(N_MIN, N_MAX),
               outline_line_color="black", outline_line_width=fb.pt(SPINE))
    p.xaxis.ticker, p.yaxis.ticker = xt, yt
    p.add_layout(LogAxis(ticker=xt), "above")
    p.add_layout(LogAxis(ticker=yt), "right")
    for ax in p.xaxis + p.yaxis:
        axis_style(ax, labels=ax in p.below)
    p.below[0].major_label_overrides = {v: "" for v in major_x}
    p.grid.grid_line_color, p.grid.grid_line_alpha = gray(0.5), 0.4
    p.grid.grid_line_width, p.grid.grid_line_dash = fb.pt(0.35), fb.dash(":", 0.35)

    # matplotlib's stacking: each band and its edge at zorder max(SIGMAS) - z, the lines at 2.
    layers = []
    for n, z in enumerate(SIGMAS):
        color, alpha = sigma_color(z)
        lo, mid, hi = (n_required(z, P, k * P) for k in (R_LO, R_PAPER, R_HI))
        c = hex_(color)

        def band(c=c, alpha=alpha, lo=lo, hi=hi, z=z):
            p.varea(P, lo, hi, fill_color=c, fill_alpha=0.15 * alpha, tags=[f"fb:group:s{z}"])
            p.line(P, hi, line_color=c, line_alpha=alpha, line_width=fb.pt(0.8), line_dash=fb.dash(":", 0.8),
                   tags=[f"fb:group:s{z}"])

        def line(c=c, alpha=alpha, mid=mid, z=z):
            p.line(P, mid, line_color=c, line_alpha=alpha, line_width=fb.pt(1.6), tags=[f"fb:group:s{z}"])

        layers += [(max(SIGMAS) - z, 2 * n, band), (2, 2 * n + 1, line)]
    for _, _, draw in sorted(layers, key=lambda t: t[:2]):
        draw()

    for name, n, level, lower in SURVEYS:
        p.add_layout(Span(location=n, dimension="width", line_color=gray(level), line_width=fb.pt(0.65),
                          line_dash=fb.dash("--", 0.65)))
        x = P_MIN * 1.03 if lower else P_MAX * 0.97
        fb.text(name, x, n * 1.12, FONT["survey"], panel=p, role="bold", color=gray(level * 0.75),
                ha="left" if lower else "right", va="bottom")
    ctx = fb.context()
    for x in (0.02, 0.03, 0.04):  # matplotlib's annotate arrows ("-|>"): 2 pt off each end, head 4 x 2 pt
        (x0, y0), (x1, y1) = ctx.to_page(p, x, 2300), ctx.to_page(p, x, 2300 * 1.65)
        ctx.layer.add_layout(Arrow(x_start=x0, y_start=y0 - 2, x_end=x1, y_end=y1 + 2, line_width=fb.pt(0.45),
                                   line_color=gray(0.25),
                                   end=NormalHead(size=fb.pt(4), line_color=gray(0.25), line_width=fb.pt(0.45),
                                                  fill_color=gray(0.25))))

    p.add_layout(Span(location=P_SIM, dimension="height", line_color=gray(0.3), line_width=fb.pt(0.9),
                      line_dash=fb.dash("-.", 0.9)))
    fb.text(r"$p^{\rm sim}_{\rm A}$", P_SIM * 1.04, N_MAX * 0.45, FONT["sim"], panel=p, color=gray(0.3))

    # Tick labels of the y axis as matplotlib sets them: 10 with its power raised, in the text font.
    left, top, fw, fh = FRAME
    s = FONT["tick"]
    widest = 0.0
    for k, v in zip(range(2, 6), major_y):
        _, y = ctx.to_page(p, P_MIN, v)
        # matplotlib's "center_baseline": the baseline sits half the label's ink height below the tick.
        ink = POWER_RISE * s + 0.7421875 * s * SCRIPT  # the raised digit's top (DejaVu digits: 0.742 em)
        base = y + ink / 2
        x = left - TICK["pad"] - POWER_SPACE - fb.width(str(k), s * SCRIPT)
        fb.text("10", x, base, s, ha="right")
        fb.text(str(k), x, base, s * SCRIPT, dy=-POWER_RISE * s)
        widest = max(widest, TICK["pad"] + POWER_SPACE + fb.width(str(k), s * SCRIPT) + fb.width("10", s))
    p.left[0].major_label_overrides = {v: "" for v in major_y}

    # Tick labels of the x axis, centred on their ticks even at the frame's edges (as matplotlib does;
    # Bokeh would pull the end labels inward).
    for v, label in zip(major_x, ["0.1%", "0.2%", "0.5%", "1%", "2%", "5%"]):
        x, _ = ctx.to_page(p, v, N_MIN)
        fb.text(label, x, top + fh + TICK["pad"], FONT["tick"], ha="center", va="top")

    # Axis titles, placed as matplotlib places them: LABELPAD beyond the tick labels.
    fb.text(r"Base rate $p_{\rm A}$", left + fw / 2, top + fh + TICK["pad"] + line_height(s) + LABELPAD,
            FONT["label"], ha="center", va="top")
    fb.text("Required sample size", left - widest - LABELPAD, top + fh / 2, FONT["label"],
            ha="center", va="bottom", angle=90)

    fb.legend([fb.Entry(f"s{z}", f"${z}\\sigma$", band=(hex_(c), 0.15 * a),
                        edge=dict(color=hex_(c), alpha=a, width=0.6, dash=":"),
                        line=dict(color=hex_(c), alpha=a, width=1.1))
               for z in SIGMAS for c, a in [sigma_color(z)]],
              at=LEGEND["at"], size=FONT["legend"], title=LEGEND["title"], ncol=LEGEND["ncol"],
              handlelength=LEGEND["handlelength"], columnspacing=LEGEND["columnspacing"],
              fill="white", fill_alpha=0.9, edgecolor=gray(0.7))
    return p
