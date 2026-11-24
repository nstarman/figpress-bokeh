# Data model: First release of figpress-bokeh

Entities from [spec.md](spec.md); sizes are points unless stated.

## Figure

- `name`: the decorated function's name (or given).
- `page`: (W, H), W, H > 0.
- `style`: a Style; its fonts unless the figure gives its own.
- `build(target)`: `target ∈ {"pdf", "web"}` → a Bokeh plot (one panel) or a Panels.
- Validation: no fonts (from the figure or the style) fails; `build` returning anything else fails,
  naming the type.

## Style

- `fonts`: Fonts. `size`, `label`: font sizes. `spine`, `tickwidth`, `ticklen`, `minor_ticklen`,
  `line`, `marker`: widths and lengths. `ticks`: `"inside"` or `"outside"`. `color`.
- Becomes a Bokeh `Theme`; a figure's own model settings win.

## Fonts

- `text`, `bold`, `math_italic`, `math_upright`: font files. Each gets a fixed family name.
- Validation: a missing file fails, naming it.

## Panels

- `plots`: the panels' Bokeh plots, in order.
- `frames`: one (left, top, width, height) per panel, inside the page; or `grid=(rows, cols)` with
  `gaps` and the outer margins, from which frames are computed.
- `share_x`, `share_y`: `"col"`, `"row"`, `"all"` or `None`; shared axes share one range object.
- `labels`: optional panel labels (`"(a)"`, …) with a position relative to each frame.
- `layer`: the page layer, a plot covering the page in page points, for panel labels, the figure
  legend and other page text.
- Validation: frames overlapping or leaving the page fail, naming the panels; shared axes with
  different author-set ranges fail.
- State: frames are *computed* → *measured* in the print page → *corrected* once; still off by
  > 0.1 pt fails, naming the panel and the offset.

## Group

- A name; the renderers tagged `fb:group:<name>`, in any panel; its legend entries.
- Web state: hidden or shown; kept across redraws and resizes.

## Run (mathematics)

- `text`, `font` (one of the four roles), `size`, `dx` (from the label's origin), `dy` (baseline
  shift). A label is a list of runs drawn as Bokeh `Label`s in screen units.

## Print figure

- One PDF page of exactly W × H; fonts embedded are only the Style's, none Type 3; each piece of
  text appears once in the text layer.

## Web figure

- A folder (`index.html`, `figure.json`, `fonts/`, `vendor/bokeh-<version>.min.js`,
  `vendor/figpress-bokeh-<version>/index.js`) and optionally one HTML file with all of it inlined.

## Comparison

- `ok`; `elements`: each text item and panel frame with its offset (pt) and whether it passes
  `tol`; `report()`; an optional overlay image.
