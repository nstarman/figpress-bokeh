// figpress-bokeh's runtime: draws a figure's page, in print and on the web.
//
// It loads the paper's fonts, embeds the figure (one Bokeh document, one root per panel), moves each
// panel so its frame sits where the figure puts it, and on the web scales the page to its column
// and wires legend entries to the groups they stand for. Figures declare; they ship no scripts.

const PX_PER_PT = 4 / 3; // CSS px per pt at the print size

/** The CSS zoom that fits a page `pageWidthPt` wide, drawn at `k` px per pt, to `containerWidth`
 * CSS px: between half and three times the print width (narrower, the page scrolls). */
export function scaleFor(containerWidth, pageWidthPt, k) {
  const print = pageWidthPt * PX_PER_PT;
  const width = Math.min(Math.max(containerWidth, print / 2), print * 3);
  return width / (pageWidthPt * k);
}

const PX_SUFFIXES = ["line_width", "line_dash", "line_dash_offset", "font_size", "standoff", "_tick_in", "_tick_out"];
const PX_NAMES = new Set(["frame_width", "frame_height", "min_border", "min_border_left", "min_border_right",
  "min_border_top", "min_border_bottom", "x_offset", "y_offset", "size", "padding", "spacing", "margin",
  "glyph_width", "glyph_height", "label_width", "label_height", "border_radius"]);

/** Whether a model attribute is a length in screen px (and so scales with the figure). */
export function isPx(name) {
  return PX_NAMES.has(name) || PX_SUFFIXES.some((s) => name.endsWith(s));
}

// Bokeh takes these in whole px.
const INT_SUFFIXES = ["standoff", "_tick_in", "_tick_out", "line_dash"];
const INT_NAMES = new Set(["frame_width", "frame_height", "min_border", "min_border_left", "min_border_right",
  "min_border_top", "min_border_bottom", "padding", "spacing", "margin", "glyph_width", "glyph_height",
  "label_width", "label_height", "border_radius"]);

function isInt(name) {
  return INT_NAMES.has(name) || INT_SUFFIXES.some((s) => name.endsWith(s));
}

function scaleValue(v, s, int = false) {
  if (typeof v === "number") return int ? Math.max(v === 0 ? 0 : 1, Math.round(v * s)) : v * s;
  if (typeof v === "string" && /^[\d.]+px$/.test(v)) return `${parseFloat(v) * s}px`;
  if (Array.isArray(v)) return v.every((x) => typeof x === "number") ? v.map((x) => scaleValue(x, s, int)) : v;
  if (v && typeof v === "object" && v.type === "value") return { ...v, value: scaleValue(v.value, s, int) };
  return v;
}

/** A copy of a Bokeh document's JSON with every screen length times `s`: Bokeh then draws the figure
 * at its scaled size itself (it sizes canvases from their on-screen boxes, so CSS zoom or transforms
 * would make it draw only part of each). */
export function scaleDoc(node, s) {
  if (Array.isArray(node)) return node.map((n) => scaleDoc(n, s));
  if (!node || typeof node !== "object") return node;
  const out = {};
  for (const [key, v] of Object.entries(node)) {
    if (key === "attributes" && v && typeof v === "object" && !Array.isArray(v)) {
      out.attributes = Object.fromEntries(Object.entries(v).map(([a, x]) =>
        [a, isPx(a) ? scaleValue(x, s, isInt(a)) : scaleDoc(x, s)]));
    } else {
      out[key] = scaleDoc(v, s);
    }
  }
  return out;
}

/** The groups a model belongs to, from its tags `fb:group:<name>`. */
export function groupsOf(tags) {
  return (tags || []).filter((t) => typeof t === "string" && t.startsWith("fb:group:")).map((t) => t.slice(9));
}

/** The legend entry at page point (x, y) pt, or null; `entries` maps a group to its box [l, t, r, b]. */
export function entryAt(entries, x, y) {
  for (const [group, [l, t, r, b]] of Object.entries(entries || {})) {
    if (x >= l && x <= r && y >= t && y <= b) return group;
  }
  return null;
}

// Light and dark: copied from figpress-plotly src/figpress_plotly/js/index.js at f6d48b2.
// The website's dark theme (nstarkman.space): its background and its text.
export const DARK = { ground: "#0B0E14", ink: "#E5E9F0" };

const rgbOf = (c) => {
  const s = c.trim().toLowerCase();
  if (s === "black") return [0, 0, 0, 1];
  if (s === "white") return [255, 255, 255, 1];
  let m = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/.exec(s);
  if (m) return [...m.slice(1).map((h) => parseInt(h, 16)), 1];
  m = /^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$/.exec(s);
  return m ? [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]] : null;
};

/** In the dark theme, a neutral colour (a grey, black or white) at its place between the palette's
 * text (black) and background (white); any other colour, and its alpha, unchanged. */
export function darkNeutral(color, palette = DARK) {
  const c = typeof color === "string" && rgbOf(color);
  if (!c || !(c[0] === c[1] && c[1] === c[2])) return color;
  const L = c[0] / 255, ink = rgbOf(palette.ink), ground = rgbOf(palette.ground);
  const [r, g, b] = [0, 1, 2].map((k) => Math.round(ink[k] + (ground[k] - ink[k]) * L));
  return c[3] === 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${c[3]})`;
}

/** The changes that put a model's colour properties `names` in the dark theme: plain colours and
 * value specs; a colour taken from data (a field) stays. */
export function darkColors(model, names, palette = DARK) {
  const out = {};
  for (const n of names) {
    const v = model[n];
    if (typeof v === "string" && darkNeutral(v, palette) !== v) out[n] = darkNeutral(v, palette);
    else if (v && typeof v === "object" && typeof v.value === "string" && darkNeutral(v.value, palette) !== v.value) {
      out[n] = { ...v, value: darkNeutral(v.value, palette) };
    }
  }
  return out;
}

/** Dark or light: a `?theme=` on the page (an embedding site passes its own), else the document's
 * `data-theme` (the website's toggle), else the system's. */
export function isDark(doc = document, win = globalThis) {
  const asked = new URLSearchParams(win.location?.search ?? "").get("theme") ?? doc.documentElement.dataset.theme;
  if (asked === "dark" || asked === "light") return asked === "dark";
  return !!win.matchMedia?.("(prefers-color-scheme: dark)").matches;
}

async function loadFonts(fonts) {
  await Promise.all(Object.entries(fonts).map(async ([family, url]) => {
    const face = new FontFace(family, `url(${url})`);
    await face.load();
    document.fonts.add(face);
  }));
}

/** Draw `spec` (figure.json) in `el`. With `print`, draw it once at its drawing size for Chrome to
 * print; otherwise draw it at `el`'s width (redrawn when that changes) and wire the legend. Returns a
 * handle for embedding sites and tests. */
export async function mount(el, spec, { print = false } = {}) {
  const B = window.Bokeh;
  // BokehJS strokes every label after filling it; Chrome prints the stroke as a Type 3 font.
  B.require("core/util/svg").SVGRenderingContext2D.prototype.strokeText = function () {};
  // Chromium on Linux rounds small text's glyph advances to whole pixels unless asked for geometric
  // precision (a 5.5 pt bold label came out 2 pt short on CI); BokehJS never sets it on its canvases.
  const fill = CanvasRenderingContext2D.prototype.fillText;
  if (!fill.fbPrecise) {
    CanvasRenderingContext2D.prototype.fillText = function (...args) {
      if ("textRendering" in this) this.textRendering = "geometricPrecision";
      return fill.apply(this, args);
    };
    CanvasRenderingContext2D.prototype.fillText.fbPrecise = true;
  }
  await loadFonts(spec.fonts);
  const [W, H] = spec.page;
  const hidden = new Set();
  let scale = 1, target = null, views = [], page = null, drawing = Promise.resolve();
  let members = {};
  let forced = null; // a theme set by the embedding site through the handle

  async function draw(s) {
    for (const v of views) {
      v.remove();
      B.index.delete(v); // else the old document lingers in Bokeh's index of roots
    }
    const k = spec.k * s; // px per pt as drawn now
    const prefix = `fb${Math.random().toString(36).slice(2, 8)}`;
    page = document.createElement("div");
    page.className = "fb-page";
    Object.assign(page.style, { position: "relative", width: `${W * k}px`, height: `${H * k}px`, overflow: "hidden" });
    spec.frames.forEach((_, i) => {
      const d = document.createElement("div");
      d.id = `${prefix}-panel-${i}`;
      Object.assign(d.style, { position: "absolute", left: "0px", top: "0px" });
      if (i === spec.frames.length - 1) d.style.pointerEvents = "none"; // the page layer: hover reaches the panels
      page.appendChild(d);
    });
    el.replaceChildren(page);
    const items = spec.items.map((it) => ({
      ...it,
      roots: Object.fromEntries(Object.entries(it.roots).map(([m, e]) => [m, e.replace("fb-panel", `${prefix}-panel`)])),
    }));
    await B.embed.embed_items(s === 1 ? spec.docs : scaleDoc(spec.docs, s), items);
    views = [...B.index.roots].filter((v) => spec.ids.includes(v.model.id) && page.contains(v.el));
    spec.frames.forEach(([l, t], i) => {
      const v = views.find((v) => v.model.id === spec.ids[i]);
      const b = v.frame.bbox;
      const d = page.querySelector(`#${prefix}-panel-${i}`);
      d.style.left = `${l * s - b.left}px`;
      d.style.top = `${t * s - b.top}px`;
    });
    if (!print) {
      const dark = forced ? forced === "dark" : isDark();
      el.dataset.theme = dark ? "dark" : "light"; // for the page's own CSS
      if (dark) {
        // Bokeh leaves defaults (white backgrounds, grey labels) out of its JSON: map the live models.
        for (const m of views[0].model.document._all_models.values()) {
          const changes = darkColors(m, Object.keys(m.properties).filter((n) => n.endsWith("color")));
          if (Object.keys(changes).length) m.setv(changes);
        }
      }
      wire(views[0].model.document, k);
    }
    scale = s;
  }

  // Groups: every renderer tagged with a group, in any panel; legend entries toggle them.
  let toggle = () => {};
  function wire(doc, k) {
    const models = [...doc._all_models.values()];
    members = {};
    for (const m of models) {
      if (m.properties?.visible === undefined) continue; // only what can be hidden: renderers, not their glyphs
      // `p.line(..., tags=[...])` tags the glyph, not its renderer: either counts.
      for (const g of new Set([...groupsOf(m.tags), ...groupsOf(m.glyph?.tags)])) (members[g] ??= []).push(m);
    }
    const labels = (g) => models.filter((m) => m.name === `fb-legend:${g}`);
    const set = (g, visible) => {
      if (visible) hidden.delete(g); else hidden.add(g);
      for (const m of members[g] || []) if (m.visible !== visible) m.visible = visible;
      for (const m of labels(g)) if ("text_alpha" in m) m.text_alpha = visible ? 1 : 0.35;
    };
    // Bokeh's own legend (click_policy "hide") hides one renderer: the rest of its group follows.
    for (const [g, ms] of Object.entries(members)) {
      for (const m of ms) m.properties.visible.change.connect(() => set(g, m.visible));
    }
    for (const g of hidden) set(g, false); // the reader's choices survive a redraw
    toggle = (g) => set(g, hidden.has(g));
    page.addEventListener("click", (e) => {
      const r = page.getBoundingClientRect();
      const g = entryAt(spec.legend, (e.clientX - r.left) / k, (e.clientY - r.top) / k);
      if (g !== null) toggle(g);
    });
  }

  if (print) {
    await draw(1);
    window.fbDrawn = true;
    return { hidden: () => [...hidden] };
  }
  el.style.overflowX = "auto";
  const fit = () => {
    const s = scaleFor(el.clientWidth, W, spec.k);
    if (target === null || Math.abs(s - target) / target > 0.01) {
      target = s;
      drawing = drawing.then(() => draw(s));
    }
    return drawing;
  };
  await fit();
  new ResizeObserver(() => fit()).observe(el);
  // Redraw when the theme changes: the website's toggle, or the system's.
  const retheme = () => { drawing = drawing.then(() => draw(scale)); };
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  window.matchMedia?.("(prefers-color-scheme: dark)").addEventListener?.("change", retheme);
  window.fbDrawn = true;
  return {
    hidden: () => [...hidden], toggle: (g) => toggle(g), redrawn: () => drawing,
    visible: (g) => (members[g] || []).map((m) => m.visible), // each renderer of a group, now
    zoom: () => scale, // the drawing's scale against spec.k
    k: () => spec.k * scale, // px per pt as drawn now
    legend: spec.legend, // each legend entry's box on the page (pt)
    theme: () => el.dataset.theme,
    setTheme: (t) => { forced = t === "dark" || t === "light" ? t : null; retheme(); return drawing; },
  };
}
