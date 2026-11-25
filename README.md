# figpress-bokeh

A paper's figures in Bokeh. You write a figure once, and it gives both the print figure the paper
publishes (a PDF) and a matching interactive web figure, with hover values, legend toggles, and
light and dark themes. The web figure never disagrees with the paper.

Part of the [figpress](https://nstarkman.space/figpress/) family, next to
[figpress-plotly](https://github.com/nstarman/figpress-plotly). In early development: the API may
still change between releases.

```bash
pip install figpress-bokeh       # printing PDFs needs Chrome or Chromium
```

## A figure

A figure is plain Bokeh, written as a function of the target (`"pdf"` or `"web"`), with every size
in points:

```python
import figpress_bokeh as fb
from bokeh.models import Range1d
from bokeh.plotting import figure

STYLE = fb.Style(fonts=fb.dejavu(), size=7, label=8)   # the paper's fonts and print settings, in pt

@fb.figure(page=(242, 170), style=STYLE, margins=(38, 6, 8, 28))
def rotation(target):
    p = figure(x_range=Range1d(0, 20), y_range=Range1d(0, 300))
    p.line(r, v, line_width=fb.pt(1), tags=["fb:group:model"])
    fb.text(r"$v_{\rm c}$ (km s$^{-1}$)", 12, 80, 8, ha="center", angle=90)   # at a page point (pt)
    fb.text("Model", 15, 230, 7, panel=p, va="bottom")                       # at a data point
    return p

rotation.write_pdf("src/tex/figures/rotation.pdf")                 # the paper's figure
rotation.write_web("site/rotation/", single_file="rotation.html")  # its web figure
```

- **The PDF** is one page of exactly the size given, with only the style's fonts embedded (as
  TrueType, never Type 3). In a showyourwork paper it is the script's output.
- **The web figure** is the same figure drawn at its column's width: a folder (page, figure data,
  fonts, and BokehJS and the runtime at pinned versions; serve it over http) and one
  self-contained HTML file that opens from disk. Nothing is loaded from another host.
- **The style** is a Bokeh theme: whatever a figure sets on a model itself wins.
- **Text**: `fb.text()` sets a label in the paper's fonts, mathematics included (`$\lambda_{\rm C}$`,
  Greek, sub- and superscripts, `\times`, `\in`, `km s$^{-1}$`), aligned as matplotlib aligns text.
  `fb.legend()` draws a legend as matplotlib draws one.

## Several panels

```python
@fb.figure(page=(360, 252), fonts=fb.dejavu(), margins=(40, 8, 84, 34))
def grid(target):
    a, b, c, d = (figure(x_range=Range1d(0, 10), y_range=Range1d(-1.6, 1.6)) for _ in range(4))
    panels = fb.panels([[a, b], [c, d]], margins=(40, 8, 84, 34), gaps=(12, 12),
                       share_x="col", share_y="row", labels="(a)")
    for p in panels:
        fb.ticklabels(p, "x", [0, 5, 10], pad=7)
        fb.axis_label(p, "x", "Time $t$")
    return panels
```

Each panel's frame lands exactly where the grid (or an explicit list of frames) puts it. Shared
axes share one range, and only the outer panels get tick labels and titles. `fb.ticklabels()` and
`fb.axis_label()` place them as matplotlib does; Bokeh's own pull the end labels inward.

## On the web

- **Hover**: declare it as in any Bokeh figure (`HoverTool`).
- **Groups**: tag renderers `fb:group:<name>`. Clicking an entry of `fb.legend()` (or of Bokeh's
  own legend with `click_policy="hide"`) hides the whole group, in every panel. The reader's
  choices survive resizing and theme changes.
- **Light and dark**: greys (black and white included) follow the theme, the website's dark
  palette; every other colour stays the paper's. The theme is a `?theme=dark|light` on the page,
  else the page's `data-theme`, else the system's.

## Porting a matplotlib figure

When a figure already in the paper moves to figpress-bokeh, measure the new PDF against it:

```bash
figpress-bokeh compare new.pdf paper-figure.pdf --tol 1 --overlay overlay.png
```

It matches every piece of text by content and every panel's frame from the image, reports each
offset in points, and writes an overlay. [`examples/bands/`](examples/bands/) and
[`examples/grid/`](examples/grid/) match their matplotlib references within 0.6 pt.

## Command line

```bash
figpress-bokeh build figures.py:grid --out build/                 # grid.pdf, grid/, grid.html
figpress-bokeh build figures.py:grid --out build/ --target pdf
figpress-bokeh compare build/grid.pdf reference.pdf --tol 1 --overlay overlay.png
```

## Limits

- `fb.text()` covers the LaTeX figures use, not all of LaTeX; an unsupported command is named.
- Figures cannot outline text (`text_outline_color`): Chrome prints outlined text as Type 3 fonts.
- Bokeh draws a plot's outline up to 0.25 pt inside its frame on the top and right edges.
- Printing uses Chrome with its own profile in figpress-bokeh's cache folder; prints take turns
  (a file lock), so parallel builds are safe. It works on macOS and Linux.
- There are no controls (sliders) yet; figpress-plotly has them.

## Developing

```bash
uv run pytest                       # the library, both examples' PDFs against their references
node --test "tests/*.test.mjs"      # the web runtime
uv run pytest -m smoke              # the web figures in a browser (Playwright)
```

Spec Kit features are under [`specs/`](specs/); releases are dated, see [AGENTS.md](AGENTS.md).

## Licence

MIT.
