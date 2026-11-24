# figpress-bokeh Constitution

figpress-bokeh makes a scientific paper's figures with Bokeh so that one definition gives both the
print figure the paper publishes (PDF) and an interactive web figure, which matches it and can do
more. It is a member of the figpress family and follows figpress-plotly's principles, with Bokeh in
place of Plotly.

## Core Principles

### I. The paper is the reference

- Every figure is one function, `build(target)`, with `target` either `"pdf"` or `"web"`, that
  returns plain Bokeh. Both outputs come from the same base code; there is no second definition of
  a figure.
- The PDF is the paper's figure. The web figure MUST show the same data, marks and labels; it MAY
  add to them (Principle III) but MUST NOT disagree with them.
- Rationale: papers change during review; two definitions of a figure drift, one cannot.

### II. Print fidelity in the paper's units

- Figures are specified in points (the paper's unit) and converted to Bokeh's screen units by the
  library, never by hand: font sizes, line widths, dash patterns, tick lengths, margins and page
  size.
- The PDF embeds the paper's fonts and is printed at its exact page size, with no margin added.
- Mathematical labels use the paper's math fonts; a figure MUST NOT fall back to another font.
- Fidelity is tested: a figure's PDF is compared with a reference rendering (overlay and
  per-element bounding boxes), within a stated tolerance.
- Rationale: the web figure is only as trustworthy as the print figure it matches, and matching
  is only real when it is measured.

### III. The web adds, never changes

- The web target MAY add hover values, legend toggles, highlighting, zoom and controls that
  recompute what is plotted, and MAY resize to its container and follow the reader's light or
  dark theme.
- It MUST NOT drop, move or restyle the paper's content except by the reader's own action.
- Rationale: a reader comparing the website with the PDF must see the same figure.

### IV. One runtime, declared interactions

- The browser side is one small runtime shared by every figure: it loads the fonts, scales the
  print layout to its container, keeps the reader's state across redraws and wires the
  interactions a figure declares. Figures declare interactions; they do not ship their own
  scripts (no per-figure `CustomJS`).
- Rationale: one tested runtime beats a script per figure.

### V. Pages that keep working

- A built web figure MUST NOT load anything from a CDN or third-party host at runtime: BokehJS and
  the fonts are included at pinned versions, and a single self-contained HTML file is available.
- Rationale: as in figpress-apps and figpress-plotly, interactive figures must outlive the services
  that served them.

### VI. Releases from tags, without stored secrets

- Versions are dates: tags `vYYYY.MM.DD`, and `vYYYY.MM.DD.N` for another release the same day.
  The PyPI version is the tag's. Publishing is from `.github/workflows/release.yml` with trusted
  publishing (GitHub environment `pypi`). No API token is stored. An npm package is added only
  when the web runtime is useful to install by itself, as `@nstarkman/figpress-bokeh`.
- Rationale: as for the rest of the figpress family.

## Repository Rules

- Squash merges only. Agent guidance lives in `AGENTS.md`; this constitution overrides it where
  they differ.
- Features go through Spec Kit: specify, plan, tasks, implement, under `specs/`.
- Code that figpress-plotly already has and that does not depend on Plotly (PDF comparison, fonts,
  units, mathematics in the paper's fonts, the theme logic) is copied, with its source noted, until
  both packages work; extracting a shared package is decided then, not before.

## Governance

- This constitution overrides other practices here. Specs and plans include a constitution check;
  deviations are justified in the plan's complexity tracking.
- Amendments are made by pull request with a version bump: MAJOR for removing or redefining a
  principle, MINOR for adding or materially expanding one, PATCH for wording.

**Version**: 1.0.0 | **Ratified**: 2026-11-24 | **Last Amended**: 2026-11-24
