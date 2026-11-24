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

- **Decision**: `fb.pt(v)` converts points to Bokeh's screen units, which are CSS px (×4/3). Font
  sizes are passed to Bokeh as `"8pt"` strings, which Bokeh accepts directly. `fb.dash(":", lw)`
  gives matplotlib's dash patterns in px. Copied from figpress-plotly's `units.py`.
- **Rationale**: Principle II; Bokeh and Plotly share the CSS px unit, so the code carries over.

## R3. Panels and exact placement

- **Decision**: a figure's panels are placed by the package, not by Bokeh's layout engine. The
  author gives each panel's frame (left, top, width, height in pt on the page) or a grid
  (`fb.panels(grid=(rows, cols), frames=..., share_x=..., share_y=...)`). The package sets each
  plot's `frame_width`/`frame_height` and its borders so its frame lands where it was given, puts
  the panels in one Bokeh root (one document), then **measures** where BokehJS actually drew each
  frame in the print page and corrects the borders once (a second print). The build fails if a
  frame is still off by more than 0.1 pt, naming the panel. Shared axes are shared `Range1d`
  objects; tick labels are hidden on inner panels unless asked.
- **Spike**: (a) panels embedded as separate documents cannot share a range (Bokeh: "Models must be
  owned by only a single document"), so all panels must be one root. (b) In a `gridplot` with fixed
  `frame_width`, `frame_height` and `min_border_*`, frames landed several points from the computed
  positions (a 100 pt frame measured ≈ 97 pt between outline centres; the second panel's frame was
  4 pt right of where the borders put it). Bokeh's layout is not exact by construction, so it must
  be measured and corrected.
- **Rationale**: User Story 3 needs frames within 0.1 pt; computing alone does not achieve it, and
  measuring in the same Chrome that prints the PDF is the ground truth.
- **Alternatives**: trusting `gridplot` (off by points, per the spike); separate absolutely placed
  documents (cannot share ranges or a legend); one plot with several frames drawn by hand (not
  plain Bokeh, loses Bokeh's axes).

## R4. The PDF

- **Decision**: there is no Kaleido step. The print page is the web page itself with
  `output_backend="svg"`, the paper's fonts as `@font-face`, `@page { size: W pt H pt; margin: 0 }`,
  and BokehJS inlined; the page waits for the fonts before embedding the figure. Headless Chrome
  prints it (`--print-to-pdf`, found through `choreographer`, as figpress-plotly finds it), and the
  page box is then set to exactly W × H with pypdfium2 (copied from figpress-plotly's
  `_exact_page`). The toolbar and logo are off on both targets.
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
