# Contract: the web page

- `index.html` loads `vendor/bokeh-<version>.min.js` and the runtime module, fetches
  `figure.json` and calls `mount(element, spec)`; it must be served over http (browsers refuse
  module imports from `file://`). The single file inlines all of it, fonts as `data:` URLs, and opens
  from disk. Nothing is requested from another host.
- `figure.json`: `{version, name, page: [W, H] pt, k: px per pt, docs, items, ids, frames: [[l, t]] px,
  fonts: {family: url}, legend: {group: [l, t, r, b] pt}}`.
- Theme: `?theme=dark|light` on the page URL, else `data-theme` on the figure element, else
  `prefers-color-scheme`. Only greys change.
- The figure fills its container's width between ½× and 3× the print width; narrower, it scrolls.
- Reader state (hidden groups) survives resizes and theme changes, not reloads.
- `mount` returns `{hidden(), toggle(group), visible(group), zoom(), k(), legend, redrawn()}` for an
  embedding site and the tests (`setTheme` comes with US5).
