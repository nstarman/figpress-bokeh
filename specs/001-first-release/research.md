# Research: First release of figpress-bokeh

Decisions for [plan.md](plan.md). figpress-plotly's research
(`../figpress-plotly/specs/002-paper-figures/research.md`) is the starting point; this file records
where Bokeh differs. A spike on 2026-11-24 (Bokeh 3.10.2, two panels with a shared x range printed
by headless Chrome) checked the print route; its findings are marked **Spike**.

## R1. How a figure is declared

- **Decision**: as in figpress-plotly, a decorator: `@fb.figure(page=(W, H), style=STYLE)` on
  `build(target)`, which returns a Bokeh plot (one panel) or `fb.panels(...)` (several). The
  decorated object has `.write_pdf()` and `.write_web()` and is what the CLI loads
  (`file.py:name`). `fb.Style` holds the paper's fonts and print settings in points and is applied
  as a Bokeh `Theme`, so whatever a figure sets on a model wins.
- **Rationale**: the figure stays plain Bokeh; a `Theme` is Bokeh's own mechanism for defaults, as
  a template is Plotly's. Same API shape as figpress-plotly (SC-004).
- **Alternatives**: subclassing `figure` (couples to Bokeh internals); applying the style after the
  build (overwrites the figure's own settings).

## R2. Units

- **Decision**: figures are drawn at **K = 8 px per pt** (`fb.pt(v) = 8 v`), not at CSS's 4/3. Font
  sizes are px strings (`fb.font(7)` → `"56px"`); `fb.dash(":", lw)` gives matplotlib's dash
  patterns in the same units. The print step scales the page down by 1/(0.75 K) (R4); the web
  runtime scales it to its column anyway (R7). Adapted from figpress-plotly's `units.py`.
- **Rationale**: Bokeh's `frame_width` and `frame_height` are whole px. At 4/3 px per pt a frame
  snaps to 0.75 pt steps (a 100 pt frame came out 99.75 pt); at 8 px per pt the step is 0.125 pt,
  inside the 0.1 pt placement tolerance once frames are measured (R3).
- **Alternatives**: CSS `transform: scale()` on the print page (Chrome clipped the content in
  print); Chrome's DevTools `printToPDF` `scale` (works through Playwright, but a choreographer
  connection hung in the spike and Playwright is too heavy as a runtime dependency).

## R3. Panels and exact placement

- **Decision**: a figure's panels are placed by the package, not by Bokeh's layout engine. The
  author gives each panel's frame (left, top, width, height in pt on the page) or a grid. All
  panels go in **one Bokeh document with one root per panel** (`bokeh.embed.util.
  standalone_docs_json_and_render_items`), so ranges and data can be shared, and each root is
  embedded in its own absolutely positioned element. Each plot gets `frame_width`/`frame_height`;
  after BokehJS lays it out, the page reads the frame's box from the plot's view
  (`Bokeh.index.roots[k].frame.bbox`) and moves the element so the frame sits at its target. This
  happens in the page itself, for print and web alike, so no second print is needed. The build
  reads back the measured frames and fails if one is off by more than 0.1 pt, naming the panel.
  Shared axes are shared range objects; tick labels are hidden on inner panels unless asked.
- **Spike**: (a) panels embedded as separate documents cannot share a range (Bokeh: "Models must be
  owned by only a single document"), so all panels must be one root. (b) In a `gridplot` with fixed
  `frame_width`, `frame_height` and `min_border_*`, frames landed several points from the computed
  positions (a 100 pt frame measured ≈ 97 pt between outline centres; the second panel's frame was
  4 pt right of where the borders put it). The cause: `min_border_*` is a minimum, and Bokeh widens
  a border to fit its tick and axis labels. (c) With one root per panel placed by the page, frames
  landed within 0.05 pt of their targets (40.05, 139.95, 175.05, 274.95 pt against 40, 140, 175,
  275).
- **Rationale**: User Story 3 needs frames within 0.1 pt; computing alone does not achieve it, and
  measuring in the same Chrome that prints the PDF is the ground truth.
- **Alternatives**: trusting `gridplot` (off by points, per the spike); separate absolutely placed
  documents (cannot share ranges or a legend); one plot with several frames drawn by hand (not
  plain Bokeh, loses Bokeh's axes).

## R4. The PDF

- **Decision**: there is no Kaleido step. The print page is the web page itself with
  `output_backend="svg"`, the paper's fonts as `@font-face`, `@page { size: 8W px 8H px; margin: 0 }`
  and BokehJS inlined; the page waits for the fonts before embedding the figure. Headless Chrome
  prints it (`--print-to-pdf`, found through `choreographer`, as figpress-plotly finds it). pypdfium2
  then places that page as a form XObject, scaled by 1/6 (that is, 1/(0.75 K)), on a new page of exactly W × H pt;
  the fonts stay embedded. The toolbar and logo are off on both targets.
- **Text outlines**: BokehJS draws every label twice, `fillText` then `strokeText`, even when the
  text has no outline. Its SVG backend writes the second as a `<text fill="none" stroke=…>`, and
  Chrome prints stroked text as a **Type 3** font. That was the spike's Type 3 font and its doubled
  label. The page sets `SVGRenderingContext2D.prototype.strokeText` (from
  `Bokeh.require("core/util/svg")`) to do nothing, and the build refuses a figure that sets
  `text_outline_color`, since paper figures do not outline text. With that, the PDF has only
  CID TrueType subsets and each label once.
- **Speed**: Chrome took 13–25 s per print, even for a trivial page: with the default profile it
  crashed on exit and recorded a crash dump, and a fresh profile costs ~15 s to create. Chrome now
  runs with first-run, sync, extension and update checks off and a persistent profile in
  figpress-bokeh's cache folder; a print then took ~2 s at first, but 5–20 s later, erratically, as
  desktop Chrome installed default web apps and did OS integration in the background. Puppeteer's
  flag set did not settle it. Next to try (T047): Chrome for Testing, or one browser kept open. Prints take turns on a file lock, since one
  profile cannot serve two Chromes and a showyourwork build runs figure scripts in parallel.
- **Spike**: a one-page PDF of the page size (280.08 × 120 pt before the fix-up), text is real
  text, and the font is embedded as a subset. Two things to resolve in Phase 1: Chrome embedded
  some glyphs as **Type 3** fonts next to the CID TrueType subset, and the rotated axis label
  appeared twice in the text layer. Both are checked by tests (FR-003: fonts must be the paper's and
  not Type 3, so journals accept them; text must appear once).
- **Rationale**: BokehJS draws the figure in the browser for both targets, so printing the page in
  Chrome makes print and web the same drawing. It also drops figpress-plotly's heaviest dependency.
- **Alternatives**: `bokeh.io.export_svg` (needs selenium and a webdriver, and still needs a PDF
  step); canvas backend (prints a bitmap).

## R5. Fonts and mathematics

- **Decision**: `fb.Fonts` and `fb.dejavu()` copied from figpress-plotly. BokehJS cannot draw rich
  text in a label (no sub/superscript markup), and its `MathText` uses MathJax's fonts, not the
  paper's. So `fb.tex()` lays mathematics out as **runs**: each run (text, font, size, baseline
  shift) is placed at an x offset computed from the font file's advance widths (fontTools), and the
  package draws the runs as `Label` annotations in screen units. Axis titles with mathematics are
  drawn this way, with the axis's own label left empty; plain titles use Bokeh's axis label.
  figpress-plotly's `text.py` parser is copied; its HTML output is replaced by runs.
- **Baseline**: BokehJS's SVG output puts the middle of a font's ascent and descent (hhea) where a
  label's alphabetic baseline should be (measured 0.346 em low in DejaVu at 5–20 pt), so `text()`
  raises every run by that much. Whether the web canvas needs the same is checked by the overlay
  test (US2).
- **Alignment**: `va="top"`, `"bottom"` and `"center"` use matplotlib's line extents, the ink top of
  "l" and the ink bottom of "p" (0.760 and 0.208 em in DejaVu Serif), not the font's line metrics.
  With these, the bands port's tick labels and titles land within 0.6 pt of matplotlib's.
- **Rationale**: FR-004 requires the paper's math fonts in both outputs and no fallback.
- **Alternatives**: MathJax (`MathText`; wrong fonts, needs a CDN or a large bundle); pre-rendered
  glyph paths (not text, not selectable).

## R6. Legends and groups

- **Decision**: a group is a set of renderers with the same `tags=["fb:group:<name>"]`. Bokeh's own
  legend works in one panel with `click_policy="hide"`, and the runtime extends a click to every
  renderer in the group across panels. For a figure-wide legend or a matplotlib-matched one,
  `fb.legend(entries, at=..., loc=...)` draws one on a page layer: an extra plot covering the page,
  with no axes, in page points, which also holds panel labels and other page text. The runtime
  toggles groups when an entry is clicked.
- **Rationale**: User Story 3 scenario 4; Principle IV (the runtime does it, not per-figure
  `CustomJS`).
- **Alternatives**: a Bokeh `Legend` per panel only (no figure-wide legend); `CustomJS` callbacks
  (Principle IV).

## R7. The web runtime

- **Decision**: one ES module, `js/index.js`, shipped in the Python package. It loads the fonts,
  embeds the figure (`Bokeh.embed.embed_item` on a `json_item`), scales it to its container between
  ½× and 3× the print width, keeps the reader's state (hidden groups) across redraws, wires group
  toggles, and maps greys for dark mode. Scaling: first try CSS `zoom` on the page container (one
  line, and Bokeh redraws at the new resolution); if hover positions or the overlay test fail under
  `zoom`, rescale the pixel-valued model properties instead, as figpress-plotly does. BokehJS is
  the build shipped in the Python `bokeh` package used to build the figure, so the model JSON and
  the renderer always match.
- **Rationale**: Principles IV and V.
- **Alternatives**: `bokeh.embed.file_html` (no fonts, scaling or state; CDN unless told
  otherwise).

## R8. Dark mode

- **Decision**: as in figpress-plotly (its R8): greys only, mapped into the website's dark palette;
  theme from `?theme=`, else the page's `data-theme`, else the system. The runtime walks the
  document's models and maps colour properties; the theme logic is copied from figpress-plotly's
  runtime.

## R9. Comparing with the paper's figure

- **Decision**: figpress-plotly's `compare.py`, copied, extended from one frame to one per panel:
  frames are found as closed rectangles of long dark lines, matched to the reference's by position,
  and each panel's text is matched within its panel.
- **Rationale**: FR-011, SC-001, SC-002.

## R10. Testing

- **Decision**: pytest (units, fonts, `tex` runs, panel placement, the PDF's page, fonts and text
  layer, compare, the CLI, both examples); `node --test` for the runtime's pure functions;
  Playwright smoke tests in CI (hover, toggles across panels, resize keeps state, theme, no request
  to another host, the single file from disk, overlay at ½×, 1× and 2×). Two references made by
  matplotlib scripts in the repository: `examples/bands/` (the same figure as figpress-plotly's)
  and a new `examples/grid/` (two by two, shared axes, one figure legend, panel labels).

## R11. Code shared with figpress-plotly

- **Decision**: copy `units.py`, `fonts.py`, `compare.py`, `text.py`'s parser, `pdf.py`'s Chrome
  lookup and page fix-up, and the runtime's theme functions, each with a header naming the
  figpress-plotly file and commit it came from. Decide on a shared package after this release
  (constitution, Repository Rules).
