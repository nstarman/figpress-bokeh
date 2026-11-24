# Contract: Python API (`import figpress_bokeh as fb`)

```python
STYLE = fb.Style(fonts=fb.dejavu(), size=7, label=8)

@fb.figure(page=(504, 360), style=STYLE)               # two columns wide
def grid(target):
    a, b, c, d = (bokeh.plotting.figure() for _ in range(4))   # plain Bokeh; sizes via fb.pt()
    a.line(x, y, line_width=fb.pt(1), tags=["fb:group:model"])
    p = fb.panels([[a, b], [c, d]], margins=(40, 8, 30, 34), gaps=(10, 10),
                  share_x="col", share_y="row", labels="(a)")
    fb.text(p, r"$v_{\rm c}$ (km s$^{-1}$)", axis=(a, "y"))     # an axis title with mathematics
    fb.legend(p, [fb.Entry("model", "Model", line=...)], at=(420, 12), size=7)
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
| `fb.text(target, s, x=None, y=None, size=None, role="text", ha="left", va="baseline", data=False, axis=None)` | a label at a page point, a data point of a panel, or as an axis title | outside a build |
| `fb.legend(target, entries, at, size, loc="upper left", ...)` | a matplotlib-style legend on the page layer; entries toggle their groups on the web | unknown group |
| `fb.Entry(group, label, line=None, band=None, edge=None, marker=None)` | a legend entry and its handle | — |
| `Figure.write_pdf(path)` | one-page PDF, exact page, frames within 0.1 pt, fonts embedded | no Chrome (says how to get one); a frame still off (named); a Type 3 font |
| `Figure.write_web(dir, single_file=None)` | page folder; optionally one HTML file | — |
| `fb.compare(new, reference, tol=1.0, overlay=None)` | `Comparison`: `.ok`, `.elements`, `.report()`; per panel | page sizes differ; panel counts differ |
