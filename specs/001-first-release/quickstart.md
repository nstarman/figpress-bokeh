# Quickstart: checking the first release

Prerequisites: `uv`, Node ≥ 20, Chrome or Chromium.

```bash
uv run python examples/bands/reference.py && uv run python examples/grid/reference.py   # only if a reference changed
uv run pytest                      # library, both examples' PDFs vs their references within 1 pt
node --test "tests/*.test.mjs"     # the runtime's pure functions
uv run pytest -m smoke             # pages in a browser: hover, toggles, resize, theme, no network
uv run figpress-bokeh build examples/grid/figure.py:grid --out build/
uv run figpress-bokeh compare build/grid.pdf examples/grid/reference.pdf --tol 1 --overlay build/overlay.png
```

Expected: every test passes; the grid comparison exits 0 and its overlay shows no red;
`build/grid.html` opened from disk with the network off shows the figure, and clicking a legend
entry hides that group in all four panels.
