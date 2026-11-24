---

description: "Tasks for the first release of figpress-bokeh"
---

# Tasks: First release of figpress-bokeh

**Input**: Design documents from `/specs/001-first-release/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/)

**Tests**: included. The spec requires measured fidelity in CI (FR-014, SC-001–SC-003) and the
constitution requires it (Principle II). Within each story, write the test first and see it fail.

**Organization**: by user story. US1 (print), US3 (panels) and US2 (web) are all P1; US3 comes
before US2 here because the web page draws whatever the print page draws, panels included.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: the user story (US1–US6 in spec.md)
- Copied files start with a header: `# Copied from figpress-plotly <path> at f6d48b2.`

---

## Phase 1: Setup

**Purpose**: the package skeleton

- [X] T001 Create `pyproject.toml` (hatchling; name `figpress-bokeh`; `requires-python = ">=3.12"`; dependencies bokeh 3.10.x, choreographer, fonttools, pypdfium2, pillow, numpy; dev group pytest, playwright, matplotlib; script `figpress-bokeh = "figpress_bokeh.cli:main"`; pytest marker `smoke`, `addopts = "-m 'not smoke'"`), modelled on `../figpress-plotly/pyproject.toml`
- [X] T002 Create `src/figpress_bokeh/__init__.py` with `__version__` and an empty public API (no `package.json`: `node --test` runs `.mjs` files without one)
- [X] T003 [P] Copy `scripts/version.py` from figpress-plotly and reduce it to the PyPI version (no npm); add `tests/test_package.py` (imports, version matches `scripts/version.py check`)
- [X] T004 [P] Create `.github/workflows/ci.yml` (uv; pytest; `node --test "tests/*.test.mjs"`; Playwright Chromium for `pytest -m smoke`), modelled on figpress-plotly's

---

## Phase 2: Foundational (blocks every story)

**Purpose**: settle the spike's open questions (research R3, R4), then the pieces every story uses

**Gate**: if T006 shows Chrome cannot print without Type 3 fonts, stop and decide with the
maintainer before Phase 3.

- [X] T005 Write the spike as a test, `tests/test_print.py` (named for what it checks): one and two Bokeh panels (shared x range, one document) printed by headless Chrome from an HTML page with `output_backend="svg"`; assert one page, real text, embedded fonts
- [X] T006 Find why Chrome embeds some glyphs as Type 3 (rotated text, font format, `text-rendering`, SVG vs HTML text) and make `tests/test_print.py` assert no Type 3 font; record the finding in `research.md` R4
- [X] T007 Find why the rotated axis label appears twice in the text layer and make `tests/test_print.py` assert each label appears once; record it in `research.md` R4
- [X] T008 Place frames in the page itself: one root per panel, each moved after layout by its frame's offset from BokehJS (no second print); `tests/test_print.py` checks the outlines; recorded in `research.md` R3
- [X] T009 [P] Copy `units.py` (pt → px, dash patterns) to `src/figpress_bokeh/units.py`, with `tests/test_units.py`
- [X] T010 [P] Copy `fonts.py` (`Fonts`, `dejavu()`, advance widths, `@font-face` CSS) to `src/figpress_bokeh/fonts.py`, with `tests/test_fonts.py`; a missing file fails, naming it
- [X] T011 Write `src/figpress_bokeh/page.py`: the HTML page shared by print and web (fonts as `@font-face`, BokehJS from the installed `bokeh` inlined or as a vendor file, wait for fonts, `embed_item` of one root), with `tests/test_page.py`

**Checkpoint**: print route proven; units, fonts and the page exist

---

## Phase 3: User Story 1 - the paper's figure in print, one panel (P1) 🎯 MVP

**Goal**: a single-panel figure, defined once in points, prints as the paper's PDF

**Independent test**: build `examples/bands/figure.py` for print: page W × H within 0.1 pt, only
the style's fonts, none Type 3, no toolbar or logo, each text once

### Tests for US1

- [X] T012 [P] [US1] `tests/test_pdf.py`: page size within 0.1 pt, fonts embedded are exactly the given ones and none Type 3, no toolbar or logo, text layer has each label once, no Chrome gives a message saying what to install, text outside the page or its frame is reported rather than clipped
- [X] T013 [P] [US1] `tests/test_text.py`: `tex()` runs for Greek, italic and upright, sub- and superscripts, `\times`, `\in`, `km s$^{-1}$`; an unsupported command fails naming it; unbalanced braces fail
- [X] T014 [P] [US1] `tests/test_figure.py`: the decorator gives `build`, `write_pdf`, `write_web`; no fonts fails; `build` returning a non-Bokeh object fails naming its type; a figure's own setting wins over the style

### Implementation for US1

- [X] T015 [P] [US1] `src/figpress_bokeh/style.py`: `Style(fonts, size=8, label=9, spine=0.7, ticks="inside", ticklen=3.5, tickwidth=0.6, minor_ticklen=2, line=1, marker=3, color="black")` → `.theme` (a Bokeh `Theme`); toolbar and logo off
- [X] T016 [P] [US1] `src/figpress_bokeh/text.py`: copy figpress-plotly's `tex()` parser; emit runs (`text`, `font`, `size`, `dx`, `dy`) with `dx` from the font's advance widths; `text()` draws runs as `Label`s at a page point, a data point or as an axis title (the axis's own label left empty)
- [X] T017 [US1] `src/figpress_bokeh/figure.py`: `figure(page, style=None, fonts=None, name=None)` decorator; `build(target)` applies the theme and returns one Bokeh root
- [X] T018 [US1] `src/figpress_bokeh/pdf.py`: Chrome lookup through choreographer and `_exact_page` (copied from figpress-plotly's `pdf.py`); print `page.py`'s page with `@page { size: W pt H pt; margin: 0 }`; judge by the PDF, not Chrome's exit code; apply T006 and T007's fixes
- [X] T019 [US1] `examples/bands/`: copy `common.py`, `reference.py` and `reference.pdf` from figpress-plotly; write `figure.py`, the Bokeh port (band, dotted edge, line, log axes, the drawn legend; tick labels and titles drawn with `fb.text` as matplotlib places them)

**Checkpoint**: the bands figure prints at the right size with the right fonts

---

## Phase 4: User Story 4 - measured against the paper (P2, needed to check US1 and US3)

**Goal**: compare a PDF with its matplotlib reference, per panel

**Independent test**: the bands port passes at 1 pt; a copy with one label moved 2 pt fails,
naming it

- [X] T020 [P] [US4] `tests/test_compare.py`: copied from figpress-plotly, plus a two-panel case (frames matched by position, text matched within its panel) and the moved-label failure
- [X] T021 [US4] `src/figpress_bokeh/compare.py`: copied from figpress-plotly; finds every panel frame as a closed rectangle of long dark lines; match panels by position; page sizes or panel counts that differ fail
- [X] T022 [US4] `src/figpress_bokeh/cli.py`: `figpress-bokeh build file.py:name --out DIR [--target pdf|web]` and `compare NEW REF --tol 1 --overlay PNG`; exit 0, 1 (comparison failed), 2 (usage), with `tests/test_cli.py`
- [X] T023 [US4] `tests/test_example.py`: the bands port matches `examples/bands/reference.pdf` within 1 pt (SC-001); tune T019 until it does

**Checkpoint**: MVP: one-panel print figures, measured

---

## Phase 5: User Story 3 - multi-panel figures (P1)

**Goal**: several plots on one page, each frame where the author put it, shared axes, panel
labels, one legend for the figure

**Independent test**: the 2 × 2 grid example prints with every frame within 0.1 pt of its given
position and matches its matplotlib reference within 1 pt (SC-002)

### Tests for US3

- [X] T024 [P] [US3] `tests/test_panels.py`: frames from a grid and from explicit frames; overlap or off-page fails naming the panels; shared axes share one range and hide inner tick labels; different author-set ranges on a shared axis fail
- [X] T025 [P] [US3] Placement in print: `tests/test_print.py` (two panels) and the grid's eight frame lines in `tests/test_example.py`, within 0.3 pt (BokehJS draws outlines up to 0.25 pt inside the frame; the frames themselves are exact)

### Implementation for US3

- [X] T026 [US3] `src/figpress_bokeh/panels.py`: `panels(plots, frames=None, margins=None, gaps=None, share_x=None, share_y=None, labels=None)`; frames and a grid both fails; one Bokeh root holding the panels and the page layer (a plot covering the page, no axes, in page points)
- [X] T027 [US3] Extend `tests/test_print.py`'s placement check to the grid example (placement itself is in `page.py` since T008)
- [X] T028 [US3] Panel labels on the page layer in `src/figpress_bokeh/panels.py`, set by `text.py` runs, at the same position relative to each frame
- [X] T029 [US3] (done early: the bands port needs it) `src/figpress_bokeh/legend.py`: `legend(target, entries, at, size, loc="upper left", ...)` and `Entry(group, label, line=None, band=None, edge=None, marker=None)`, laid out as matplotlib's legend (copy the layout rules from figpress-plotly's `legend.py`) on the page layer; an unknown group fails; with `tests/test_legend.py`
- [X] T030 [US3] `examples/grid/reference.py` (data in `grid_common.py`; `common` would clash with the bands example's) (matplotlib, 2 × 2, shared x per column and y per row, one figure legend, labels (a)–(d), DejaVu fonts) → commit `examples/grid/reference.pdf`
- [X] T031 [US3] `examples/grid/figure.py`: the Bokeh port with `panels()`, groups tagged `fb:group:<name>`, the figure legend
- [X] T032 [US3] `tests/test_example.py`: the grid port matches its reference within 1 pt for every panel's frame and text (SC-002)

**Checkpoint**: single and multi-panel figures print and are measured

---

## Phase 6: User Story 2 - the same figure on the web (P1)

**Goal**: the print page, scaled to its column, with hover and legend toggles across panels,
working offline

**Independent test**: both examples' pages at ½×, 1× and 2× the print width overlay their PDFs
within tolerance; hover shows declared values; a legend click hides the group in every panel; a
resize keeps it; the single file works from disk with the network off

### Tests for US2

- [X] T033 [P] [US2] `tests/runtime.test.mjs`: the runtime's pure functions (scale factor and clamping to ½×–3×, group state, which renderers a group holds)
- [X] T034 [P] [US2] `tests/smoke/test_browser.py` and `tests/smoke/conftest.py` (Playwright): hover values, legend toggles across panels (figure legend and Bokeh's own `click_policy="hide"` legend), resize keeps toggles, no request to another host, the single file from disk
- [X] T035 [P] [US2] `tests/smoke/test_overlay.py`: each example's page against its PDF at ½×, 1× and 2× (SC-003), copied from figpress-plotly's overlay test

### Implementation for US2

- [X] T036 [US2] `src/figpress_bokeh/web.py`: page folder (`index.html`, `figure.json` as in `contracts/web-page.md`, `fonts/`, `vendor/bokeh-<version>.min.js`, `vendor/figpress-bokeh-<version>/index.js`) and the single file with everything inlined; `output_backend` canvas for the web
- [X] T037 [US2] `src/figpress_bokeh/js/index.js`: `mount(element, spec)`: load fonts, embed, scale by rescaling the document's pixel lengths and redrawing on resize (CSS `zoom` and transforms both broke Bokeh; `research.md` R7), keep hidden groups across redraws
- [X] T038 [US2] Group toggles in `src/figpress_bokeh/js/index.js`: clicks on figure-legend entries and on Bokeh legend items hide every renderer tagged with that group in every panel; `mount` returns `{setTheme, hidden}`
- [X] T039 [US2] Hover in `src/figpress_bokeh/figure.py`: tooltips declared in Python survive the hidden toolbar on the web; none in print

**Checkpoint**: both examples work on the web, matching their PDFs

---

## Phase 7: User Story 5 - light and dark (P2)

**Goal**: greys follow the theme; data colours stay the paper's

**Independent test**: each theme and the system setting; greys change, other colours and layout do not

- [ ] T040 [P] [US5] `tests/smoke/test_theme.py` and theme cases in `tests/runtime.test.mjs` (grey mapping, `?theme=`, `data-theme`, `prefers-color-scheme`)
- [ ] T041 [US5] Copy figpress-plotly's grey mapping and theme detection into `src/figpress_bokeh/js/index.js`; walk the document's models and map colour properties; redraw on theme change, keeping reader state

---

## Phase 8: User Story 6 - release and family listing (P3)

**Goal**: a date tag publishes to PyPI; the family lists the package

**Independent test**: a tag that does not match the version fails before publishing

- [ ] T042 [US6] `.github/workflows/release.yml`: on `vYYYY.MM.DD[.N]`, check the version against the tag, build, publish with trusted publishing from environment `pypi`; skip a version already on PyPI (modelled on figpress-plotly's, PyPI only)
- [ ] T043 [US6] README.md (what it is, a figure, panels, the web figure, compare, limits, developing) and AGENTS.md layout and releasing sections, following figpress-plotly's
- [ ] T044 [US6] Maintainer steps, not code: create the public GitHub repository `nstarman/figpress-bokeh`, register PyPI's pending trusted publisher, push the first tag
- [ ] T045 [US6] After the first release: a pull request to figpress adding figpress-bokeh to `family.json` with `released: true`

---

## Phase 9: Polish

- [ ] T046 [P] Check SC-004: write the bands figure from figpress-plotly's example with the same page, style and fonts and compare the two PDFs at 1 pt, in `tests/test_example.py`
- [ ] T047 [P] Time both examples' builds on CI (< 30 s each, plan's performance goal). On this Mac a print takes 5–20 s, erratically: desktop Chrome does background work (default web apps, OS integration). Try Chrome for Testing (`choreo_get_chrome`, a ~150 MB download, needs the maintainer's yes) or a browser kept open across prints
- [ ] T048 Run `quickstart.md` end to end and fix what it finds

---

## Dependencies

- Setup (T001–T004) → Foundational (T005–T011) → stories.
- **T006 is a gate**: no Type 3 fix, no Phase 3 without the maintainer's decision.
- US1 (T012–T019) → US4 (T020–T023) → US3 (T024–T032) → US2 (T033–T039) → US5 (T040–T041) →
  US6 (T042–T045).
- US4 is checked against US1's example; US3's measurement needs US4's per-panel compare; US2 needs
  US3 because the web page holds panels and the page layer; US5 needs the runtime from US2.
- Polish after US5; T045 after the release.

## Parallel examples

- Foundational: T009, T010 together, while T005–T008 settle the print route.
- US1: T012, T013, T014 (tests), then T015 and T016 together.
- US3: T024 and T025, then T030 (the matplotlib reference) beside T026–T029.
- US2: T033, T034, T035 together before T036.

## Implementation strategy

1. **MVP** = Phases 1–4: single-panel print figures, measured against matplotlib. Stop and check
   the bands overlay.
2. Add panels (US3) and check the grid against its reference.
3. Add the web (US2), then dark mode (US5).
4. Release (US6) once every test passes; then list the package in the family.
5. After the release, compare `units.py`, `fonts.py`, `compare.py`, `text.py` and the theme code
   with figpress-plotly's and decide on a shared package (constitution, Repository Rules).
