"""figpress-bokeh: a paper's figures in Bokeh, in print and on the web.

In early development. A figure is one ``build(target)`` that gives both the print PDF the paper
publishes and a matching interactive web figure. Follow it at
https://github.com/nstarman/figpress-bokeh and the figpress family at https://nstarkman.space/figpress/.
"""

from .compare import compare
from .figure import Figure, context, figure
from .fonts import Fonts, dejavu
from .style import Style
from .legend import Entry, legend
from .text import tex, text, width
from .units import dash, font, pt

__all__ = ("Entry", "Figure", "Fonts", "Style", "__version__", "compare", "context", "dash", "dejavu", "figure", "font", "legend", "pt", "tex",
           "text", "width")

__version__ = "2026.11.24"
