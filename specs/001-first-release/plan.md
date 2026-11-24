# Implementation Plan: First release of figpress-bokeh

**Branch**: `001-first-release` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-first-release/spec.md`

## Summary

An author writes a plain Bokeh figure as a function of the target, in points, with one panel or
several, and decorates it with its page and the paper's style. figpress-bokeh builds one HTML page
in which BokehJS draws the figure with the paper's fonts. Headless Chrome prints that page as the
PDF, so print and web are the same drawing. Panels are placed by the package, measured in the print
page and corrected once, so every frame is where the author put it. Mathematics is laid out as runs
in the paper's fonts. On the web, one shared runtime scales the print layout, keeps the reader's
state and wires hover, group toggles across panels, and dark mode. A comparison tool measures a
PDF against a matplotlib reference, per panel. Code that does not depend on Plotly is copied from
figpress-plotly. Design decisions: [research.md](research.md).

## Technical Context

**Language/Version**: Python ≥ 3.12 (Bokeh 3.10's minimum); ES2022 modules in the browser; Node ≥ 20
for tests

**Primary Dependencies**: bokeh (3.10.x), choreographer (finds Chrome), fonttools, pypdfium2,
pillow, numpy. Browser: BokehJS from the Python `bokeh` package.

**Storage**: files (PDF, web page folder, single HTML)

**Testing**: pytest; `node --test`; Playwright (Chromium) smoke tests in CI

**Target Platform**: macOS and Linux with Chrome or Chromium; any modern browser for the pages

**Project Type**: library + CLI, browser runtime inside the Python package

**Performance Goals**: each example builds both targets in < 30 s on CI, including the second print
that corrects panel placement

**Constraints**: no network at page runtime (Principle V); frames within 0.1 pt and fidelity within
1 pt (SC-001, SC-002); no per-figure browser code (Principle IV); no Type 3 fonts in the PDF

**Scale/Scope**: figures of a paper (tens); up to about 3 × 3 panels per figure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan meets it |
|---|---|
| I. The paper is the reference | One decorated `build(target)` per figure; print and web are the same page drawn by BokehJS; a style is a Bokeh `Theme`, defaults only. |
| II. Print fidelity in the paper's units | Sizes in points through `fb.pt` and `"Npt"` strings; panels measured and corrected to 0.1 pt; fonts embedded and checked (not Type 3); `fb.compare` per panel against matplotlib references in CI (R3, R4, R9). |
| III. The web adds, never changes | The runtime only scales, adds hover, group toggles and dark greys; the page it scales is the page that was printed. |
| IV. One runtime, declared interactions | One `index.js`; groups are tags, hover tooltips are declared in Python; no `CustomJS` in figures (R6, R7). |
| V. Pages that keep working | BokehJS, the runtime and the fonts are vendored at pinned versions; single self-contained file; CI checks no request leaves the page. |
| VI. Releases from tags | `release.yml` publishes to PyPI from a date tag with trusted publishing; no npm package yet. |
| Repository rule: copy, then decide | Files copied from figpress-plotly carry a header with their source file and commit (R11). |

Re-checked after Phase 1 design: passes; no deviations.

## Project Structure

### Documentation (this feature)

```text
specs/001-first-release/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/  python-api.md, cli.md, web-page.md
└── tasks.md   (/speckit-tasks)
```

### Source Code (repository root)

```text
src/figpress_bokeh/
├── __init__.py        public API: figure, panels, Style, Fonts, dejavu, pt, dash, tex, text,
│                      legend, Entry, compare
├── units.py           pt → px, dash patterns            (copied from figpress-plotly)
├── fonts.py           Fonts, dejavu(), text widths       (copied)
├── text.py            tex() parser (copied) → runs; text() places runs as Labels
├── panels.py          panels(): frames or grid, shared ranges, inner tick labels, page layer
├── legend.py          a matplotlib-style legend on the page layer, with group handles
├── figure.py          the decorator: page, style, build(target) → one Bokeh root
├── style.py           Style → Bokeh Theme
├── page.py            the HTML page (fonts, BokehJS, the figure), used by print and web
├── pdf.py             Chrome print, frame measurement and one correction, exact page (partly copied)
├── web.py             page folder (index.html, figure.json, vendor/, fonts/) and single file
├── compare.py         per-panel text and frame offsets, overlay (copied, extended)
├── cli.py             figpress-bokeh build | compare
└── js/index.js        the runtime
examples/bands/        figure.py (Bokeh port) and reference.py → reference.pdf (figpress-plotly's)
examples/grid/         figure.py and reference.py → reference.pdf: 2 × 2, shared axes, one legend
tests/                 test_*.py; runtime.test.mjs; smoke/ (Playwright)
pyproject.toml, scripts/version.py, .github/workflows/{ci,release}.yml
```

**Structure Decision**: one library, one module per concern, mirroring figpress-plotly's layout so
the two can be compared file by file when a shared package is considered.

## Phases

0. **Spike follow-ups (R3, R4)**: in the repository's first test, settle the three spike findings
   before building on them: the Type 3 glyphs in Chrome's PDF, the doubled rotated label, and the
   measure-and-correct loop for frames. If Type 3 cannot be avoided, stop and decide with the
   maintainer before Phase 1.
1. **Print, one panel (US1)**: units, fonts, page, PDF, `tex` runs. Checked with the bands port.
2. **Compare (US4)**: copied and extended per panel; lands with phase 1 so the port is measured.
3. **Panels (US3)**: `panels()`, shared ranges, page layer, panel labels, figure legend, the grid
   example and its matplotlib reference.
4. **Web (US2)**: page folder, single file, runtime (fonts, scaling, state, hover, group toggles
   across panels), smoke tests with the three-width overlay and no network.
5. **Dark mode (US5)**.
6. **Release (US6)**: `pyproject.toml`, `scripts/version.py`, `release.yml`, first tag, then
   figpress-bokeh in `family.json` (a pull request to figpress).

## Complexity Tracking

None.
