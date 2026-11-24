"""Text in the paper's fonts: the mathematics figures use, laid out as runs, and labels placed as
matplotlib places them.

BokehJS cannot set rich text, and its MathText uses MathJax's fonts, so a label with mathematics is
drawn as runs, each a Bokeh `Label` in one font at its own offset (research R5). The parser
(`runs`) is copied from figpress-plotly src/figpress_plotly/text.py at f6d48b2.
"""

import math
import re
from dataclasses import dataclass
from functools import cache

from bokeh.models import Label, Plot
from fontTools.ttLib import TTFont

from .figure import context
from .fonts import FAMILY, Fonts
from .units import font, pt

SCRIPT = 0.7  # a sub- or superscript's size, relative to its base (matplotlib's)

GREEK = dict(zip(
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega".split(),
    "αβγδεζηθικλμνξπρστυφχψω"))
GREEK |= {k.capitalize(): v for k, v in zip(
    "gamma delta theta lambda xi pi sigma upsilon phi psi omega".split(), "ΓΔΘΛΞΠΣΥΦΨΩ")}
SYMBOLS = {"in": "∈", "times": "×", "cdot": "·", "pm": "±", "mp": "∓", "leq": "≤", "geq": "≥", "le": "≤", "ge": "≥",
           "sim": "∼", "approx": "≈", "neq": "≠", "infty": "∞", "propto": "∝", "prime": "′", "odot": "⊙",
           "rightarrow": "→", "to": "→", "ell": "ℓ", "partial": "∂", "nabla": "∇", ",": " ", ";": " ",
           " ": " ", "%": "%", "{": "{", "}": "}", "$": "$"}
UPRIGHT = {"rm", "mathrm", "text", "mathdefault"}
BINARY = set("+−=<>×·±∓≤≥∼≈≠∝∈→")  # spaced as mathtext spaces binary operators and relations
MEDIUM = "\u2005"  # a quarter em
_TOKEN = re.compile(r"\\([A-Za-z]+|.)|(.)", re.S)


def runs(s: str) -> list[tuple[str, str, str | None]]:
    """`s` as runs of (text, font role, script): outside `$…$` the figure's text (`"text"`); inside,
    mathematics as matplotlib's mathtext sets it — latin letters and lowercase Greek italic, the rest
    upright; `_` and `^` subscripts and superscripts; `\\rm{}`/`\\mathrm{}` upright."""
    out: list[tuple[str, str, str | None]] = []
    for i, part in enumerate(s.split("$")):
        if i % 2 == 0:
            if part:
                out.append((part, "text", None))
        else:
            toks = [m.group(1) and "\\" + m.group(1) or m.group(2) for m in _TOKEN.finditer(part)]
            toks = [t for t in toks if not t.isspace()]  # math mode ignores spaces
            start = len(out)
            _math(toks, 0, len(toks), upright=False, script=None, out=out)
            out[start:] = [(f"{MEDIUM}{t}{MEDIUM}" if t in BINARY and k > 0 and sc is None else t, r, sc)
                           for k, (t, r, sc) in enumerate(out[start:])]
    merged: list[tuple[str, str, str | None]] = []
    for r in out:
        if merged and merged[-1][1:] == r[1:]:
            merged[-1] = (merged[-1][0] + r[0], *r[1:])
        else:
            merged.append(r)
    return merged


def _group_end(toks, i):
    depth = 0
    for j in range(i, len(toks)):
        depth += toks[j] == "{"
        depth -= toks[j] == "}"
        if depth == 0:
            return j
    raise ValueError("unbalanced braces in math")


def _atom(toks, i, upright, script, out):
    """Write the atom at `i` (a group, a command with its argument, or a character); return the index after it."""
    t = toks[i]
    if t == "{":
        j = _group_end(toks, i)
        _math(toks, i + 1, j, upright, script, out)
        return j + 1
    if t.startswith("\\"):
        name = t[1:]
        if name in UPRIGHT:
            if i + 1 < len(toks) and toks[i + 1] == "{":
                return _atom(toks, i + 1, True, script, out)
            return i + 1  # {\rm …}: the caller's group continues upright (handled in _math)
        if name in GREEK:
            ch = GREEK[name]
            out.append((ch, "math_upright" if upright or ch.isupper() else "math_italic", script))
            return i + 1
        if name in SYMBOLS:
            out.append((SYMBOLS[name], "math_upright", script))
            return i + 1
        raise ValueError(f"unsupported math command \\{name}")
    ch = "−" if t == "-" else t
    out.append((ch, "math_italic" if ch.isalpha() and not upright else "math_upright", script))
    return i + 1


def _math(toks, i, end, upright, script, out):
    while i < end:
        t = toks[i]
        if t in ("\\rm", "\\mathrm") and (i + 1 >= end or toks[i + 1] != "{"):
            upright = True  # {\rm …}
            i += 1
            continue
        if t in ("_", "^"):  # no base in the math: it is the text before (`km s$^{-1}$`)
            if script is not None:
                raise ValueError("nested scripts are not supported")
            i = _atom(toks, i + 1, upright, "sub" if t == "_" else "sup", out)
            continue
        i = _atom(toks, i, upright, script, out)
        while i < end and toks[i] in ("_", "^"):
            if script is not None:
                raise ValueError("nested scripts are not supported")
            i = _atom(toks, i + 1, upright, "sub" if toks[i] == "_" else "sup", out)


SUP, SUB = 0.36, 0.24  # a superscript's rise and a subscript's drop, in sizes of the base (mathtext's)


@dataclass(frozen=True)
class Run:
    """A piece of a label in one font: its text, font role, size (pt) and offset from the label's
    origin along (`dx`) and above (`dy`) its baseline, in pt."""

    text: str
    role: str
    size: float
    dx: float
    dy: float


def layout(s: str, size: float, fonts: Fonts, role: str = "text") -> tuple[list[Run], float]:
    """`s` (with `$...$` mathematics) as runs and its width in pt. Text outside mathematics is set in
    `role`; a superscript and a subscript on the same base are stacked (`p^{sim}_{A}`)."""
    out, x, script, start, end = [], 0.0, None, 0.0, 0.0
    for text, r, sc in runs(s):
        r = role if r == "text" else r
        sz = size * SCRIPT if sc else size
        if sc and script and sc != script:  # the other script on the same base: stack it
            x = start
        elif sc and not script:
            start = x
        dy = {None: 0.0, "sup": SUP * size, "sub": -SUB * size}[sc]
        out.append(Run(text, r, sz, x, dy))
        x += fonts.width(text, r, sz)
        if sc:
            end = max(end, x)
            x = end
        else:
            end = x
        script = sc
    return out, x


@cache
def _vmetrics(path) -> tuple[float, float]:
    f = TTFont(path, lazy=True)
    upem = f["head"].unitsPerEm
    return f["hhea"].ascent / upem, -f["hhea"].descent / upem


@cache
def _lp(path) -> tuple[float, float]:
    """matplotlib's line extents for alignment: the ink top of "l" and the ink bottom of "p", in em."""
    f = TTFont(path)
    glyf, cmap, upem = f["glyf"], f.getBestCmap(), f["head"].unitsPerEm
    return glyf[cmap[ord("l")]].yMax / upem, -glyf[cmap[ord("p")]].yMin / upem


def line_height(size: float, role: str = "text") -> float:
    """The height of a line of text as matplotlib lays it out ("lp"'s ink extent), in pt."""
    a, d = _lp(getattr(context().fonts, role))
    return (a + d) * size


def width(s: str, size: float, role: str = "text") -> float:
    """The width of `s` (with `$...$` mathematics) in pt."""
    return layout(s, size, context().fonts, role)[1]


def text(s: str, x: float, y: float, size: float, *, panel: Plot | None = None, role: str = "text",
         color: str = "black", alpha: float = 1.0, ha: str = "left", va: str = "baseline", angle: float = 0.0,
         dx: float = 0.0, dy: float = 0.0, name: str | None = None) -> list[Label]:
    """Draw `s` at page point (x, y) (pt from the top left), or at data point (x, y) of `panel`,
    moved by (dx, dy) pt (dy down), turned `angle` degrees anticlockwise. Aligned as matplotlib
    aligns text: `ha` left, center or right; `va` baseline, or the top, bottom or centre of the
    line (the ink extent of "lp", as matplotlib measures a line). Returns the labels, one per run."""
    ctx = context()
    if panel is not None:
        x, y = ctx.to_page(panel, x, y)
    x, y = x + dx, y + dy
    pieces, w = layout(s, size, ctx.fonts, role)
    asc, desc = _lp(getattr(ctx.fonts, role))
    along = {"left": 0.0, "center": -w / 2, "right": -w}[ha]
    up = {"baseline": 0.0, "top": -asc * size, "bottom": desc * size, "center": -(asc - desc) / 2 * size}[va]
    a = math.radians(angle)
    c, s_ = math.cos(a), math.sin(a)
    labels = []
    for r in pieces:
        body = r.text.lstrip(" ")  # BokehJS drops a label's leading spaces: move the run past them instead
        if not body:
            continue
        u = along + r.dx + ctx.fonts.width(r.text[:len(r.text) - len(body)], r.role, r.size)
        ra, rd = _vmetrics(getattr(ctx.fonts, r.role))
        # BokehJS's SVG output puts the middle of the line's ascent and descent where the baseline
        # should be (measured: 0.346 em low in DejaVu at 5-20 pt); raise each run by that much.
        v = up + r.dy + (ra - rd) / 2 * r.size  # along and above the baseline, pt
        label = Label(x=x, y=y, text=body, text_font=FAMILY[r.role], text_font_size=font(r.size),
                      text_color=color, text_alpha=alpha, text_baseline="alphabetic", text_align="left",
                      angle=a, x_offset=pt(u * c - v * s_), y_offset=pt(u * s_ + v * c), name=name)
        ctx.layer.add_layout(label)
        labels.append(label)
    return labels


def tex(s: str) -> list[tuple[str, str, str | None]]:
    """`s`'s runs (text, font role, script); see `runs`."""
    return runs(s)
