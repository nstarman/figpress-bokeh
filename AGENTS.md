# AGENTS.md

figpress-bokeh makes a paper's figures in Bokeh so that one definition gives the print figure
(PDF) and a matching interactive web figure. Part of the figpress family; the sibling of
figpress-plotly (`../figpress-plotly`), whose design it follows. Read
`.specify/memory/constitution.md` first; it overrides this file.

## Layout

```
src/figpress_bokeh/         the PyPI package (import figpress_bokeh as fb)
  figure.py                   @fb.figure: page, frame or margins, fonts, style; build(target); the page layer
  panels.py axes.py           fb.panels (frames, shared axes, labels); tick labels and axis titles as matplotlib
  text.py legend.py           tex() runs in the paper's fonts; a matplotlib-style legend
  units.py fonts.py style.py  pt at 8 px per pt; the paper's fonts; fb.Style (a Bokeh Theme)
  page.py pdf.py              the HTML page (one root per panel, placed by frame); Chrome print, exact page
  compare.py cli.py           PDF vs reference, per panel; figpress-bokeh build | compare
examples/bands/ grid/       ports matched within 1 pt to their matplotlib references (reference.py)
tests/                      uv run --group dev pytest
.specify/, specs/           Spec Kit (v1.1.3): specify → plan → tasks → implement
```

Checks: both examples' PDFs must pass `compare` against their `reference.pdf` within 1 pt
(`tests/test_example.py`). Regenerate a reference only when the reference itself changes.
