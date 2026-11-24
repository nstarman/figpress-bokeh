"""A figure: the author's `build(target)` with its page, frame and fonts.

The decorator and its frame-or-margins rules are adapted from figpress-plotly
src/figpress_plotly/figure.py at f6d48b2.
"""

import math
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path

from bokeh.core.validation import silence
from bokeh.core.validation.warnings import MISSING_RENDERERS
from bokeh.models import InlineStyleSheet, LogScale, Plot, Range1d

from .fonts import Fonts
from . import units
from .units import pt

TARGETS = ("pdf", "web")
silence(MISSING_RENDERERS)  # the page layer holds annotations only
_current: ContextVar["Context"] = ContextVar("figpress_bokeh_context")


def page_layer(page: tuple[float, float]) -> Plot:
    """A transparent plot covering the page, in page points from the top left, for text and marks
    placed on the page rather than in a panel."""
    w, h = page
    p = Plot(x_range=Range1d(0, w), y_range=Range1d(h, 0), frame_width=round(pt(w)), frame_height=round(pt(h)),
             min_border=0, toolbar_location=None, outline_line_color=None, background_fill_alpha=0,
             border_fill_alpha=0, name="fb-page-layer",
             # It covers the panels: the mouse must reach them through it (legend clicks are hit-tested
             # by the runtime). Bokeh's own styles turn pointer events back on inside its shadow root.
             stylesheets=[InlineStyleSheet(css=":host, :host * { pointer-events: none !important; }")])
    p.toolbar.logo = None
    return p


@dataclass
class Context:
    """The figure being built: its target, page, fonts, page layer and panels with their frames."""

    target: str
    page: tuple[float, float]
    fonts: Fonts
    layer: Plot
    frame: tuple[float, float, float, float]  # a single-panel figure's frame
    panels: list[tuple[Plot, tuple[float, float, float, float]]] = field(default_factory=list)
    outer: dict = field(default_factory=dict)  # id(plot) -> whether its x and y tick labels are drawn
    extents: dict = field(default_factory=dict)  # (id(plot), axis) -> how far its tick labels reach (pt)
    entries: dict = field(default_factory=dict)  # legend group -> its entry's box (l, t, r, b) on the page (pt)

    def frame_of(self, plot: Plot) -> tuple[float, float, float, float]:
        for p, f in self.panels:
            if p is plot:
                return f
        if not self.panels:  # a single-panel figure: the plot is its panel
            _panel(plot, self.frame)
            self.panels.append((plot, self.frame))
            return self.frame
        raise ValueError("this plot is not a panel of the figure being built")

    def to_page(self, plot: Plot, x: float, y: float) -> tuple[float, float]:
        """A data point of `plot` as a page point (pt from the top left)."""
        left, top, w, h = self.frame_of(plot)
        fx = _fraction(x, plot.x_range, isinstance(plot.x_scale, LogScale), "x")
        fy = _fraction(y, plot.y_range, isinstance(plot.y_scale, LogScale), "y")
        return left + fx * w, top + (1 - fy) * h


def _fraction(v, rng, log, axis):
    if not isinstance(rng, Range1d):
        raise ValueError(f"placing text at a data point needs an explicit {axis} range (Range1d), "
                         f"not {type(rng).__name__}")
    a, b, v = (math.log10(t) if log else t for t in (rng.start, rng.end, v))
    return (v - a) / (b - a)


def context() -> Context:
    """The figure being built; only inside a figure's `build`."""
    try:
        return _current.get()
    except LookupError:
        raise RuntimeError("only available while a figure is being built") from None


@dataclass(frozen=True)
class Built:
    """A built figure: its panels and the page layer (last), each with its frame in pt."""

    plots: list[Plot]
    frames: list[tuple[float, float, float, float]]
    page: tuple[float, float]
    fonts: Fonts
    theme: object
    k: float  # px per pt it was drawn at
    target: str
    name: str
    entries: dict  # legend group -> its entry's box on the page (pt), for the web's toggles


class Figure:
    """A paper figure: `build(target)` gives it for print (`"pdf"`) or the web (`"web"`)."""

    def __init__(self, fn, *, page, frame=None, margins=None, fonts=None, style=None, name=None):
        w, h = page
        if frame is not None and margins is not None:
            raise ValueError("give the frame or the margins, not both")
        if frame is None:
            margins = margins if margins is not None else style.margins if style else None
            if margins is None:
                raise ValueError("give the frame, the margins or a style (whose margins are used)")
            ml, mt, mr, mb = margins
            frame = (ml, mt, w - ml - mr, h - mt - mb)
        fonts = fonts or (style.fonts if style else None)
        if fonts is None:
            raise ValueError("give the fonts, or a style that has them")
        left, top, fw, fh = frame
        if min(w, h, fw, fh) <= 0 or left < 0 or top < 0 or left + fw > w or top + fh > h:
            raise ValueError(f"frame {frame} must lie inside the page {page} (pt)")
        self.fn, self.page, self.frame, self.fonts, self.style = fn, (w, h), tuple(frame), fonts, style
        self.name = name or fn.__name__
        self.__doc__, self.__wrapped__ = fn.__doc__, fn

    def build(self, target: str = "pdf") -> Built:
        if target not in TARGETS:
            raise ValueError(f"target must be one of {TARGETS}, not {target!r}")
        k_token = units._k.set(units.PER_TARGET[target])
        ctx = Context(target, self.page, self.fonts, page_layer(self.page), self.frame)
        token = _current.set(ctx)
        try:
            out = self.fn(target)
            if isinstance(out, Plot):
                ctx.frame_of(out)
            elif type(out).__name__ != "Panels" or not ctx.panels:
                raise TypeError(f"{self.name}() must return a Bokeh plot or fb.panels(...), not {type(out).__name__}")
        finally:
            _current.reset(token)
            units._k.reset(k_token)
        plots = [p for p, _ in ctx.panels] + [ctx.layer]
        frames = [f for _, f in ctx.panels] + [(0.0, 0.0, *self.page)]
        for p in plots:
            _no_text_outlines(p)
        return Built(plots, frames, self.page, self.fonts, self.style.theme if self.style else None,
                     units.PER_TARGET[target], target, self.name, dict(ctx.entries))

    def write_pdf(self, path) -> Path:
        from .page import html
        from .pdf import print_page

        b = self.build("pdf")
        return print_page(html(b), Path(path), b.page)

    def write_web(self, out, single_file=None) -> Path:
        from .web import write_web

        return write_web(self.build("web"), Path(out), single_file)

    def __call__(self, target: str = "pdf") -> Built:
        return self.build(target)


def _panel(p: Plot, frame) -> None:
    """Size a panel's frame in drawing px and take off the screen controls."""
    p.frame_width, p.frame_height = round(pt(frame[2])), round(pt(frame[3]))
    p.min_border = 0
    p.toolbar_location = None
    p.toolbar.logo = None


def _no_text_outlines(p: Plot) -> None:
    """Paper figures do not outline text, and Chrome prints outlined text as Type 3 fonts."""
    for m in p.references():
        for prop in m.properties():
            if prop.endswith("text_outline_color") and getattr(m, prop) is not None:
                raise ValueError(f"{type(m).__name__}.{prop} is set: figpress-bokeh does not draw text outlines")


def figure(*, page, frame=None, margins=None, fonts: Fonts | None = None, style=None, name=None):
    """Decorate `build(target)` with its page (pt) and either its exact frame (left, top, width,
    height) or its margins (left, top, right, bottom), its fonts and its paper `style` (which
    supplies fonts and margins unless given)."""
    return lambda fn: Figure(fn, page=page, frame=frame, margins=margins, fonts=fonts, style=style, name=name)

