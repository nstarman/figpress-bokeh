# Changelog

Versions are dates: `vYYYY.MM.DD` (PyPI `YYYY.MM.DD`), and `vYYYY.MM.DD.N` for another release the
same day.

## Unreleased

The first release (feature 001): a paper's figure in Bokeh as one `build(target)`.

- `@fb.figure(page, frame | margins, fonts | style)`; sizes in points (`fb.pt`, `fb.font`,
  `fb.dash`); `fb.Style`, a paper's fonts and print settings as a Bokeh theme.
- `fb.panels()`: several plots on one page, each frame exactly placed, shared axes, panel labels;
  `fb.ticklabels()` and `fb.axis_label()` placed as matplotlib places them.
- Text in the paper's fonts: `fb.text()` (mathematics as runs, at page or data points, aligned as
  matplotlib aligns text); `fb.legend()`, drawn as matplotlib draws one.
- `write_pdf()`: one page at exactly the given size, only the given fonts embedded, none Type 3.
- `write_web()`: the figure drawn at its column's width, with hover, legend toggles across panels,
  light and dark; a page folder and one self-contained HTML file, loading nothing from another host.
- `fb.compare()` and `figpress-bokeh compare`: a PDF measured against a reference, text and every
  panel's frame. `figpress-bokeh build`.
