# Contract: the web page

- `index.html` loads `vendor/bokeh-<version>.min.js` and the runtime module, fetches
  `figure.json` and calls `mount(element, spec)`. The single file inlines all of it, fonts as
  `data:` URLs. Nothing is requested from another host.
- `figure.json`: `{version, name, page: [W, H], item: <bokeh json_item>, fonts: {family: url},
  groups: {name: [renderer ids]}}`.
- Theme: `?theme=dark|light` on the page URL, else `data-theme` on the figure element, else
  `prefers-color-scheme`. Only greys change.
- The figure fills its container's width between ½× and 3× the print width; narrower, it scrolls.
- Reader state (hidden groups) survives resizes and theme changes, not reloads.
- `mount` returns `{setTheme(t), hidden(): string[]}` for an embedding site and the tests.
