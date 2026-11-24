"""The paper's units: points, drawn at K px per pt.

Adapted from figpress-plotly src/figpress_plotly/units.py at f6d48b2. Bokeh's frame sizes are whole
px, so print figures are drawn at 8 px per pt (a 0.125 pt step) rather than CSS's 4/3, and print
scales the page down. Web figures are drawn at 4 px per pt (3x CSS's, sharp up to 3x the print
width, with canvases a quarter the size) and the runtime scales them to their column (research R2).
"""

from contextvars import ContextVar

K = 8  # px per pt in print
PER_TARGET = {"pdf": K, "web": 4}
_k: ContextVar[float] = ContextVar("figpress_bokeh_k", default=K)


def k() -> float:
    """px per pt for the figure being built (print's outside a build)."""
    return _k.get()

# matplotlib's dash patterns in units of the line width (lines.scale_dashes, the default).
DASHES = {":": (1, 1.65), "--": (3.7, 1.6), "-.": (6.4, 1.6, 1, 1.6)}


def pt(v: float) -> float:
    """Points to drawing px."""
    return v * _k.get()


def font(size: float) -> str:
    """A font size in points as Bokeh's font-size string."""
    return f"{size * _k.get():g}px"


def dash(style: str | tuple[float, ...], lw: float = 1.0) -> list[int]:
    """A Bokeh line_dash: a matplotlib style (`:`, `--`, `-.`) scaled by the line width `lw` (pt),
    as matplotlib scales it, or explicit on/off lengths in pt. Bokeh takes whole px (0.125 pt)."""
    if isinstance(style, str):
        if style not in DASHES:
            raise ValueError(f"unknown dash style {style!r}; use one of {', '.join(DASHES)} or lengths in pt")
        lengths = [v * lw for v in DASHES[style]]
    else:
        lengths = list(style)
    return [max(1, round(pt(v))) for v in lengths]
