# Contract: Python API (`import figpress_bokeh as fb`)

```python
STYLE = fb.Style(fonts=fb.dejavu(), size=7, label=8)

@fb.figure(page=(504, 360), style=STYLE)               # two columns wide
def grid(target):
    a, b, c, d = (bokeh.plotting.figure() for _ in range(4))   # plain Bokeh; sizes via fb.pt()
    a.line(x, y, line_width=fb.pt(1), tags=["fb:group:model"])
    p = fb.panels([[a, b], [c, d]], margins=(40, 8, 30, 34), gaps=(10, 10),
                  share_x="col", share_y="row", labels="(a)")
    fb.text(r"$v_{\rm c}$ (km s$^{-1}$)", 12, 180, 8, ha="center", angle=90)   # at a page point (pt)
    fb.text("Model", 15, 230, 7, panel=a, va="bottom")                       # at a data point of a panel
    fb.legend([fb.Entry("model", "Model", line=...)], at=(420, 12), size=7)
    return p

grid.write_pdf("out/grid.pdf")
grid.write_web("out/grid/", single_file="out/grid.html")
fb.compare("out/grid.pdf", "paper/grid.pdf", tol=1.0, overlay="out/grid-overlay.png")
```

| Name | Does | Errors |
|---|---|---|
| `fb.figure(page, style=None, fonts=None, name=None)` | decorator → `Figure` with `build`, `write_pdf`, `write_web` | no fonts; bad page |
| `fb.Style(fonts, size=8, label=9, spine=0.7, ticks="inside", ticklen=3.5, tickwidth=0.6, minor_ticklen=2, line=1, marker=3, color="black")` | a paper's style; `.theme` | — |
| `fb.panels(plots, frames=None, margins=None, gaps=None, share_x=None, share_y=None, labels=None)` | several plots on one page; `plots` is a list of rows or a flat list with `frames` | frames and a grid both; overlap or off page (panels named); conflicting shared ranges |
| `fb.pt(v)` / `fb.dash(style, lw=1)` | points → px; matplotlib dash patterns in px | unknown style |
| `fb.Fonts(text, bold, math_italic, math_upright)`, `fb.dejavu(text="serif")` | font set | missing file (named) |
| `fb.tex(s)` | `$…$` mathematics → runs in the paper's fonts (figpress-plotly's subset) | unsupported command (named); unbalanced braces |
| `fb.text(s, x, y, size, panel=None, role="text", color=, alpha=1, ha="left", va="baseline", angle=0, dx=0, dy=0, name=None)` | a label as runs on the page layer, at a page point or a data point of `panel`; aligned as matplotlib aligns text | outside a build; a data point on a panel without explicit ranges |
| `fb.width(s, size, role="text")`, `fb.text.line_height(size, role="text")` | a label's width; matplotlib's line height ("lp") | outside a build |
| `fb.context()` | the figure being built: `to_page(panel, x, y)`, `layer`, `fonts` | outside a build |
| `fb.legend(entries, at, size, title=None, ncol=1, ...)` | a matplotlib-style legend on the page layer (matplotlib's parameter names); entries named `fb-legend:<group>` for the web | — |
| `fb.Entry(group, label, line=None, band=None, edge=None)` | a legend entry and its handle; `band` a colour or `(colour, alpha)` | — |
| `Figure.write_pdf(path)` | one-page PDF, exact page, frames within 0.1 pt, fonts embedded | no Chrome (says how to get one); a frame still off (named); a Type 3 font |
| `Figure.write_web(dir, single_file=None)` | page folder; optionally one HTML file | — |
| `fb.compare(new, reference, tol=1.0, overlay=None)` | `Comparison`: `.ok`, `.elements`, `.report()`; per panel | page sizes differ; panel counts differ |
