// The runtime's pure functions: node --test "tests/*.test.mjs"
import assert from "node:assert/strict";
import test from "node:test";

import { darkColors, darkNeutral, entryAt, groupsOf, isDark, isPx, scaleDoc, scaleFor } from "../src/figpress_bokeh/js/index.js";

test("the page fits its column, between half and three times the print width", () => {
  const print = 300 * 4 / 3; // CSS px
  assert.equal(scaleFor(print, 300, 4), print / 1200);
  assert.equal(scaleFor(10, 300, 4), print / 2 / 1200);
  assert.equal(scaleFor(1e5, 300, 4), print * 3 / 1200);
});

test("screen lengths are the pixel-valued attributes", () => {
  for (const a of ["line_width", "outline_line_width", "major_label_text_font_size", "major_tick_in", "x_offset",
    "frame_width", "min_border_left", "line_dash", "major_label_standoff", "size"]) assert.ok(isPx(a), a);
  for (const a of ["x", "y", "start", "end", "location", "angle", "fill_alpha", "ticks"]) assert.ok(!isPx(a), a);
});

test("scaling a document scales its screen lengths only, whole px where Bokeh needs them", () => {
  const doc = { roots: [{ type: "object", name: "Figure", attributes: {
    frame_width: 800, line_width: 3.2, text_font_size: "56px", x: 12, major_label_standoff: 14,
    line_dash: [18, 8], size: { type: "value", value: 16 },
    renderers: [{ type: "object", name: "Label", attributes: { x_offset: -10, y: 5 } }] } }] };
  const a = scaleDoc(doc, 0.5).roots[0].attributes;
  assert.deepEqual([a.frame_width, a.line_width, a.text_font_size, a.x, a.major_label_standoff],
    [400, 1.6, "28px", 12, 7]);
  assert.deepEqual(a.line_dash, [9, 4]);
  assert.deepEqual(a.size, { type: "value", value: 8 });
  assert.deepEqual(a.renderers[0].attributes, { x_offset: -5, y: 5 });
  assert.equal(doc.roots[0].attributes.frame_width, 800); // a copy
});

test("groups come from tags; legend entries from their boxes", () => {
  assert.deepEqual(groupsOf(["fb:group:s1", "other", 3]), ["s1"]);
  assert.deepEqual(groupsOf(undefined), []);
  const entries = { s1: [10, 10, 40, 20], s2: [10, 25, 40, 35] };
  assert.equal(entryAt(entries, 20, 30), "s2");
  assert.equal(entryAt(entries, 50, 30), null);
});

test("dark: greys map between the palette's text and background; colours and alpha stay", () => {
  assert.equal(darkNeutral("white"), "rgb(11,14,20)");
  assert.equal(darkNeutral("#000000"), "rgb(229,233,240)");
  assert.equal(darkNeutral("#444444"), "rgb(171,175,181)");
  assert.equal(darkNeutral("rgba(128,128,128,0.4)"), "rgba(120,123,130,0.4)");
  assert.equal(darkNeutral("#1f77b4"), "#1f77b4");
  assert.equal(darkNeutral(null), null);
});

test("dark: a model's colour properties, plain or as a value spec; fields untouched", () => {
  const m = { line_color: "black", text_color: { value: "#ffffff" }, fill_color: { field: "c" }, x: 3 };
  const names = ["line_color", "text_color", "fill_color", "x"];
  assert.deepEqual(darkColors(m, names), { line_color: "rgb(229,233,240)", text_color: { value: "rgb(11,14,20)" } });
});

test("the theme: asked for, else the toggle, else the system", () => {
  const doc = (theme) => ({ documentElement: { dataset: theme ? { theme } : {} } });
  const win = (search, dark) => ({ location: { search }, matchMedia: () => ({ matches: dark }) });
  assert.equal(isDark(doc(), win("?theme=dark", false)), true);
  assert.equal(isDark(doc("dark"), win("?theme=light", true)), false);
  assert.equal(isDark(doc("dark"), win("", false)), true);
  assert.equal(isDark(doc(), win("", true)), true);
  assert.equal(isDark(doc(), win("", false)), false);
});
