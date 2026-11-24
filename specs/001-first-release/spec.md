# Feature Specification: First release of figpress-bokeh

**Feature Branch**: `001-first-release`

**Created**: 2026-11-24

**Status**: Draft

**Input**: User description: "figpress-bokeh: a paper's figures in Bokeh, as figpress-plotly does
for Plotly. One definition, written in plain Bokeh as a function of the target, gives the print
PDF the paper publishes and a matching interactive web figure. First release: the print figure,
the web figure with hover and legend toggles, multi-panel figures, light and dark, a ported figure measured against its
matplotlib reference within 1 pt, and releases by tag. Copy what figpress-plotly has that does not
depend on Plotly; decide on a shared package later."

## Clarifications

### Session 2026-11-24

- Q: Is a multi-panel figure (a row, column or grid of Bokeh plots on one page) in the first
  release, or only a single plot per figure? → A: Multi-panel is in the first release.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One definition, the paper's figure in print (Priority: P1)

An author who draws with Bokeh writes a figure once, as a function of the target (`"pdf"` or
`"web"`), with sizes, line widths, dash patterns, tick lengths and font sizes in points. Building
it for print gives the PDF the paper includes: the exact page size the author set, no added
margin, the paper's fonts embedded, mathematical labels in the paper's math fonts.

**Why this priority**: the PDF is the paper's figure (Principle I). Nothing else matters if it is
not publishable.

**Independent Test**: build the example figure for print. The page is the requested size within
0.1 pt, every embedded font is one the author gave, and the text and marks sit where the
definition puts them.

**Acceptance Scenarios**:

1. **Given** a figure defined in points with a page of W × H pt, **When** it is built for print,
   **Then** the PDF is one page of W × H pt with no margin, and lines, dashes, ticks and text have
   the sizes given in points.
2. **Given** the paper's font files, **When** the figure is built, **Then** the PDF embeds exactly
   those fonts and no fallback font.
3. **Given** a label with mathematics (italic symbols, upright text, sub- and superscripts),
   **When** it is built, **Then** it is set in the paper's math fonts in both outputs.
4. **Given** a figure, **When** it is built for print, **Then** no toolbar, logo or other screen
   control appears in the PDF.

---

### User Story 2 - The same figure on the web, with hover and legend toggles (Priority: P1)

The author builds the same function for the web and gets a page that shows the figure as in print,
scaled to the width of its column, in the paper's fonts. A reader hovers a curve to read its
values and clicks a legend entry to hide or show that series and everything grouped with it.
Resizing the page keeps what the reader did. The page works with no network connection.

**Why this priority**: the reason for the package; every figure gets these interactions.

**Independent Test**: open the example's web page at three widths. At each, the figure overlays
the scaled PDF within the fidelity tolerance; hovering shows the declared values; toggling a
legend entry hides its group; a resize keeps the toggles. Repeat with the network off.

**Acceptance Scenarios**:

1. **Given** a built web figure, **When** it is shown in a column narrower or wider than the print
   page, **Then** it is the print layout scaled to that width, with the same text, marks and
   positions.
2. **Given** a series with declared hover values, **When** the reader hovers it, **Then** those
   values are shown in the paper's number format.
3. **Given** a legend entry that stands for a group (for example a band, its edge and its line),
   **When** the reader clicks it, **Then** the whole group hides, and clicking again shows it.
4. **Given** the reader has hidden a group, **When** the page is resized, **Then** the group stays
   hidden.
5. **Given** the built output, **When** it is opened with no network, **Then** both the folder
   version and the single-file version show the figure with its fonts.

---

### User Story 3 - Multi-panel figures (Priority: P1)

Most paper figures have several panels. The author lays out several Bokeh plots on one page (a
row, a column or a grid) with each panel's frame in points, shared axes where panels share a
quantity, one legend for the figure or one per panel, and panel labels such as "(a)". Print and
web both show the whole layout, and on the web the panels act as one figure.

**Why this priority**: a package that only does single plots cannot carry most of a paper's
figures.

**Independent Test**: build a two-by-two example for both targets. Each panel's frame is where the
author put it within 0.1 pt; panels with a shared axis have the same range and ticks; toggling a
legend entry hides that group in every panel; the web page overlays the PDF at three widths.

**Acceptance Scenarios**:

1. **Given** a grid of panels with frames in points, **When** it is built for print, **Then** one
   page holds every panel at its frame, with the gaps the author set and no added margin.
2. **Given** panels that share an axis, **When** they are built, **Then** they have the same range
   and ticks, and tick labels are drawn only on the outer panels unless the author asks otherwise.
3. **Given** panel labels, **When** the figure is built, **Then** each label sits at the same
   position relative to its panel in both outputs, in the paper's fonts.
4. **Given** one legend for the whole figure, **When** the reader clicks an entry on the web,
   **Then** that group hides in every panel where it appears.
5. **Given** a multi-panel web figure, **When** the reader hovers a series in one panel, **Then**
   hover values are shown for that panel's series, and the reader's toggles survive a resize for
   every panel.

---

### User Story 4 - A ported figure, measured against the paper (Priority: P2)

An author moves a figure the paper already has (drawn with matplotlib) to figpress-bokeh and
measures the new PDF against the old one: every piece of text matched by content and the axes
frame matched from the image, each offset reported in points, and an overlay image to look at.

**Why this priority**: fidelity is only real when it is measured (Principle II). The same check
keeps the package honest in CI.

**Independent Test**: port figpress-plotly's bands example (`examples/bands/reference.pdf`, the
same matplotlib reference) and a multi-panel figure with its own matplotlib reference, and compare
each. Every offset is within 1 pt.

**Acceptance Scenarios**:

1. **Given** the bands reference PDF and its Bokeh port, **When** they are compared with a
   tolerance of 1 pt, **Then** the comparison passes and writes an overlay.
2. **Given** a multi-panel reference and its port, **When** they are compared at 1 pt, **Then**
   each panel's frame and text are matched to the right panel and the comparison passes.
3. **Given** a port with a label moved by 2 pt, **When** it is compared at 1 pt, **Then** the
   comparison fails and names that label and its offset.

---

### User Story 5 - Light and dark on the web (Priority: P2)

On the web, the figure follows the reader's theme. Greys (black and white included) follow the
website's dark palette; every other colour stays the paper's. An embedding site can choose the
theme for the page.

**Why this priority**: the family's websites have both themes; a figure that ignores the theme
looks broken in dark mode. It does not block the print figure.

**Independent Test**: open the example with each theme and with the system setting. Greys change
as specified, other colours do not, and the layout is identical.

**Acceptance Scenarios**:

1. **Given** a page asked for the dark theme by the embedding site, **When** it loads, **Then**
   greys use the dark palette and the data colours are unchanged.
2. **Given** no theme from the site or the page, **When** it loads, **Then** it follows the
   reader's system setting.

---

### User Story 6 - Release by tagging, listed in the family (Priority: P3)

The maintainer releases by pushing a date tag; the package goes to PyPI with no stored token. Once
it is released, figpress-bokeh appears on the family website.

**Why this priority**: needed to share the package, not to use it locally.

**Independent Test**: push `vYYYY.MM.DD`; PyPI gets `YYYY.MM.DD` from that commit. A tag that does
not match the package version fails before publishing.

**Acceptance Scenarios**:

1. **Given** a pushed tag `vYYYY.MM.DD` (or `vYYYY.MM.DD.N`), **When** the release workflow runs,
   **Then** PyPI gets `YYYY.MM.DD` (or `YYYY.MM.DD.N`) built from the tagged commit.
2. **Given** a tag that does not match the package version, **When** the workflow runs, **Then**
   it fails before publishing.
3. **Given** the first release is on PyPI, **When** the family list is updated, **Then** the
   figpress website lists figpress-bokeh as released.

### Edge Cases

- A label uses LaTeX the package does not support: the build fails and names the command; it does
  not fall back to another font or to rendering in the browser.
- A figure sets a size in screen units directly: whatever the figure sets itself wins, as with
  figpress-plotly's style, and the PDF uses it as points.
- The figure's text does not fit the page or the frame: the build reports it rather than
  clipping silently.
- No browser is available to print the PDF: the build fails with a message saying what to install.
- Panels whose frames the author gives overlap or leave the page: the build fails and names the
  panels.
- A legend group appears in some panels and not others: toggling it hides it wherever it appears.
- Panels share an axis but the author sets different ranges on them: the build fails rather than
  choosing one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A figure MUST be one function of the target returning plain Bokeh; the package MUST
  build it for print and for the web from that single function.
- **FR-002**: The author MUST give the page size, each panel's frame or the margins, and all sizes in
  points; the package MUST convert them, and a figure's own settings MUST take precedence over the
  paper's style.
- **FR-003**: The PDF MUST be one page of exactly the requested size, embed only the paper's
  fonts, and contain no screen controls.
- **FR-004**: Mathematical labels MUST be set in the paper's fonts in both outputs, covering the
  LaTeX that paper figures use (Greek, italic symbols, sub- and superscripts, `\times`, `\in`,
  units such as `km s$^{-1}$`); an unsupported command MUST fail the build with its name.
- **FR-005**: The web build MUST give a folder (page, figure data, fonts, Bokeh's browser library
  and the runtime at pinned versions) and one self-contained HTML file; neither may load anything
  from another host.
- **FR-006**: The web figure MUST scale the print layout to its container and MUST NOT move,
  drop or restyle the paper's content except by the reader's action.
- **FR-007**: The web figure MUST support hover values and legend toggles over groups, and MUST
  keep the reader's toggles across resizes.
- **FR-008**: The web figure MUST follow a light or dark theme chosen by the embedding site, else
  by the page, else by the system; only greys change with the theme.
- **FR-009**: A figure MAY hold several plots in a row, column or grid on one page, each with
  its frame in points; the package MUST place them exactly, share ranges and ticks between panels
  that share an axis, and set panel labels in the paper's fonts.
- **FR-010**: On the web, a multi-panel figure MUST act as one figure: one legend entry toggles
  its group in every panel, hover works per panel, and the reader's state survives resizes.
- **FR-011**: The package MUST compare a PDF with a reference PDF: text matched by content, each
  panel's axes frame matched from the image, offsets reported in points against a tolerance, and an
  overlay image written.
- **FR-012**: A command line MUST build a figure for either or both targets and run the
  comparison.
- **FR-013**: Pushing `vYYYY.MM.DD` or `vYYYY.MM.DD.N` MUST publish to PyPI with trusted
  publishing from the tagged commit, and MUST fail before publishing if the version differs from
  the tag.
- **FR-014**: CI MUST check on every pull request that the package builds and installs, that the
  examples' PDFs (single and multi-panel) match their references within 1 pt, and that their web
  pages overlay their PDFs.

### Key Entities

- **Figure**: one function of the target, with a page size, one or more panels, a style, and the
  interactions it declares.
- **Style**: the paper's fonts and print settings in points, shared by all its figures.
- **Print figure**: the PDF the paper includes.
- **Web figure**: the folder and the single HTML file that show the same figure in the browser.
- **Panel**: one plot within a figure, with its frame in points, its axes (some shared with
  other panels) and an optional label.
- **Reference**: an existing figure of the paper that a port is measured against.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The ported bands example matches its matplotlib reference within 1 pt for every
  piece of text and the axes frame.
- **SC-002**: A multi-panel example (two by two, shared axes, one legend) matches its matplotlib
  reference within 1 pt for every panel's frame and text.
- **SC-003**: The web figure overlays its PDF within the same tolerance at three column widths
  (half, equal to and twice the print width).
- **SC-004**: An author who already has a figpress-plotly figure can write the same figure in
  figpress-bokeh with the same page, style and fonts, and the two PDFs agree within 1 pt.
- **SC-005**: A built web figure opens and works with the network turned off.
- **SC-006**: After the first release, a release needs only a pushed tag; the repository stores
  no secret.

## Assumptions

- Repository `nstarman/figpress-bokeh`, public, MIT licence; package `figpress-bokeh`, import name
  `figpress_bokeh`.
- Figures are written with Bokeh's plotting interface. HoloViews and hvPlot, which draw through
  Bokeh, are out of scope for this release.
- Controls that recompute what is plotted (figpress-plotly's sliders) are a later feature.
- The toolbar is hidden in both outputs; zoom and pan are not part of this release.
- Python only on the first release: the browser runtime ships inside the Python package. An npm
  package follows only when the runtime is useful by itself (constitution, Principle VI).
- The first release goes to PyPI once the library works, not earlier as a placeholder; the name
  is not under threat in the meantime.
- Parts of figpress-plotly that do not depend on Plotly (comparison, fonts, units, mathematics in
  the paper's fonts, theme logic) are copied with their source noted; a shared package is decided
  once both work.
- Printing the PDF needs a local Chrome or Chromium, as figpress-plotly's does.
