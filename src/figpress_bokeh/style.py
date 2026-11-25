"""A paper's style: its fonts and print settings, set once and shared by all its figures.

Adapted from figpress-plotly src/figpress_plotly/style.py at f6d48b2: the settings become a Bokeh
Theme, so anything a figure sets on a model itself wins.
"""

from dataclasses import dataclass
from functools import cached_property

from bokeh.themes import Theme

from .fonts import FAMILY, Fonts
from .units import font, pt


@dataclass(frozen=True)
class Style:
    """Fonts and print settings in pt."""

    fonts: Fonts
    size: float = 8.0  # tick labels and text
    label: float = 9.0  # axis titles
    spine: float = 0.7  # the frame's line width
    ticks: str = "inside"
    ticklen: float = 3.5
    tickwidth: float = 0.6
    minor_ticklen: float = 2.0
    line: float = 1.0  # glyphs' line width
    margins: tuple[float, float, float, float] = (36.0, 6.0, 8.0, 30.0)  # left, top, right, bottom
    color: str = "black"

    def __post_init__(self):
        if self.ticks not in ("inside", "outside"):
            raise ValueError(f"ticks must be 'inside' or 'outside', not {self.ticks!r}")

    @cached_property
    def theme(self) -> Theme:
        inside = self.ticks == "inside"
        major, minor = round(pt(self.ticklen)), round(pt(self.minor_ticklen))  # Bokeh takes whole px
        axis = {
            "axis_line_color": self.color, "axis_line_width": pt(self.spine),
            "major_tick_line_color": self.color, "major_tick_line_width": pt(self.tickwidth),
            "minor_tick_line_color": self.color, "minor_tick_line_width": pt(self.tickwidth * 0.8),
            "major_tick_in": major if inside else 0, "major_tick_out": 0 if inside else major,
            "minor_tick_in": minor if inside else 0, "minor_tick_out": 0 if inside else minor,
            "major_label_text_font": FAMILY["text"], "major_label_text_font_size": font(self.size),
            "major_label_text_color": self.color,
            "axis_label_text_font": FAMILY["text"], "axis_label_text_font_size": font(self.label),
            "axis_label_text_font_style": "normal", "axis_label_text_color": self.color,
        }
        return Theme(json={"attrs": {
            "Axis": axis,
            "Plot": {"outline_line_color": self.color, "outline_line_width": pt(self.spine),
                     "background_fill_color": "white", "border_fill_color": "white"},
            "Grid": {"grid_line_color": None},
            "Line": {"line_width": pt(self.line)},
        }})
