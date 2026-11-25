"""Several plots on one page: each panel's frame where the figure puts it, shared axes, panel labels.

Panels are one Bokeh document with one root each (page.py places them), so shared axes are simply
shared range objects.
"""

from string import ascii_lowercase

from bokeh.models import Plot, Range1d

from .figure import _panel, context
from .text import text


class Panels:
    """A figure's panels, in the order given, with their frames (left, top, width, height in pt)."""

    def __init__(self, plots: list[Plot], frames: list[tuple[float, float, float, float]]):
        self.plots, self.frames = plots, frames

    def __getitem__(self, k) -> Plot:
        return self.plots[k]

    def __iter__(self):
        return iter(self.plots)

    def __len__(self):
        return len(self.plots)


def grid_frames(page, rows, cols, margins, gaps) -> list[tuple[float, float, float, float]]:
    """Equal frames on a `rows` x `cols` grid inside the page's `margins` (left, top, right, bottom),
    `gaps` (horizontal, vertical) apart, row by row."""
    w, h = page
    ml, mt, mr, mb = margins
    gx, gy = gaps
    fw = (w - ml - mr - gx * (cols - 1)) / cols
    fh = (h - mt - mb - gy * (rows - 1)) / rows
    return [(ml + c * (fw + gx), mt + r * (fh + gy), fw, fh) for r in range(rows) for c in range(cols)]


def panels(plots, frames=None, *, margins=None, gaps=(10.0, 10.0), share_x=None, share_y=None, labels=None,
           label_at=(3.0, 3.0), label_size=9.0, label_role="text") -> Panels:
    """Put several plots on the figure's page.

    `plots` is a list of rows of plots (a grid, whose frames come from `margins` and `gaps` in pt)
    or a flat list with explicit `frames`. `share_x` is "col" or "all", `share_y` "row" or "all":
    shared axes have one range, and tick labels are drawn only on the outer panels (by
    `fb.ticklabels`). `labels` such as "(a)" label the panels in order, `label_at` pt right of and
    below each frame's top-left corner, aligned by their top."""
    ctx = context()
    if ctx.panels:
        raise ValueError("a figure has one set of panels")
    nested = bool(plots) and isinstance(plots[0], (list, tuple))
    if (frames is None) == (not nested):
        raise ValueError("give a grid of plots (a list of rows) with margins, or a flat list with frames")
    if nested:
        rows, cols = len(plots), max(len(r) for r in plots)
        if any(len(r) != cols for r in plots):
            raise ValueError("every row of the grid needs the same number of plots")
        if margins is None:
            raise ValueError("a grid needs its margins (left, top, right, bottom) in pt")
        cells = [(r, c) for r in range(rows) for c in range(cols)]
        flat = [p for row in plots for p in row]
        frames = grid_frames(ctx.page, rows, cols, margins, gaps)
    else:
        flat, cells = list(plots), [(0, k) for k in range(len(plots))]
        if len(frames) != len(flat):
            raise ValueError(f"{len(flat)} plots but {len(frames)} frames")
    _check(frames, ctx.page)
    for key, share, coord in (("x_range", share_x, 1), ("y_range", share_y, 0)):
        if share is None:
            continue
        if share not in ("all", "col" if key == "x_range" else "row"):
            raise ValueError(f"share_{key[0]} must be {'col' if key == 'x_range' else 'row'!r}, 'all' or None")
        _share(flat, cells, key, None if share == "all" else coord)
    for p, f in zip(flat, frames):
        _panel(p, f)
        ctx.panels.append((p, tuple(f)))
    ctx.outer = {id(p): _outer(cells, k, share_x, share_y) for k, p in enumerate(flat)}
    if labels:
        for k, (left, top, _, _) in enumerate(frames):
            label = labels.replace("a", ascii_lowercase[k], 1) if "a" in labels else f"{labels}{k + 1}"
            text(label, left + label_at[0], top + label_at[1], label_size, role=label_role, va="top")
    return Panels(flat, [tuple(f) for f in frames])


def _check(frames, page):
    w, h = page
    for k, (l, t, fw, fh) in enumerate(frames):
        if fw <= 0 or fh <= 0 or l < 0 or t < 0 or l + fw > w + 1e-9 or t + fh > h + 1e-9:
            raise ValueError(f"panel {k} ({l:g}, {t:g}, {fw:g}, {fh:g}) leaves the page {page} (pt)")
    for i in range(len(frames)):
        for j in range(i + 1, len(frames)):
            a, b = frames[i], frames[j]
            if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                raise ValueError(f"panels {i} and {j} overlap")


def _share(flat, cells, key, along):
    """Give the plots in each column (along=1), row (along=0) or all (None) one range."""
    groups = {}
    for p, cell in zip(flat, cells):
        groups.setdefault(None if along is None else cell[along], []).append(p)
    for group in groups.values():
        explicit = {(r.start, r.end) for r in (getattr(p, key) for p in group) if isinstance(r, Range1d)}
        if len(explicit) > 1:
            raise ValueError(f"panels sharing their {key[0]} axis set different ranges: {sorted(explicit)}")
        shared = next((getattr(p, key) for p in group if isinstance(getattr(p, key), Range1d)), getattr(group[0], key))
        for p in group:
            setattr(p, key, shared)


def _outer(cells, k, share_x, share_y) -> dict[str, bool]:
    """Whether panel k's x and y tick labels are drawn: inner panels of shared axes have none."""
    r, c = cells[k]
    last_row = max(rr for rr, _ in cells)
    return {"x": share_x is None or r == last_row, "y": share_y is None or c == 0}
