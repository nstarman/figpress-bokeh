"""The grid example drawn with matplotlib, as a paper's figure is: the reference figure.py must match.

    uv run python examples/grid/reference.py      # writes examples/grid/reference.pdf
"""

from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402

from grid_common import (COLORS, FONT, LABELPAD, LEGEND_AT, LINE, PAGE, SPINE, X, X_RANGE, X_TICKS, Y_RANGE,  # noqa: E402
                    Y_TICKS, curves, frames)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42, "axes.linewidth": SPINE, "xtick.labelsize": FONT["tick"], "ytick.labelsize": FONT["tick"],
    "axes.labelsize": FONT["label"], "axes.labelpad": LABELPAD,
})


def main(out: Path) -> None:
    w, h = PAGE
    fig = plt.figure(figsize=(w / 72, h / 72))
    axes = []
    for k, (left, top, fw, fh) in enumerate(frames()):
        r, c = divmod(k, 2)
        share = dict(sharex=axes[c] if r else None, sharey=axes[2 * r] if c else None)
        ax = fig.add_axes((left / w, 1 - (top + fh) / h, fw / w, fh / h), **share)
        model, data = curves(k)
        ax.plot(X, model, color=COLORS["model"], lw=LINE, label="Model")
        ax.plot(X, data, color=COLORS["data"], lw=LINE, ls="--", label="Data")
        ax.set(xlim=X_RANGE, ylim=Y_RANGE, xticks=X_TICKS, yticks=Y_TICKS)
        ax.annotate(f"({'abcd'[k]})", xy=(0, 1), xycoords="axes fraction", xytext=(3, -3),
                    textcoords="offset points", va="top", fontsize=FONT["panel"])
        if r == 1:
            ax.set_xlabel("Time $t$")
        if c == 0:
            ax.set_ylabel("Signal $s_k$")
        ax.tick_params(labelbottom=r == 1, labelleft=c == 0)  # inner panels of shared axes: no tick labels
        axes.append(ax)
    lx, ly = LEGEND_AT
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(lx / w, 1 - ly / h),
               bbox_transform=fig.transFigure, borderaxespad=0, fontsize=FONT["legend"], handlelength=2.0)
    fig.savefig(out)


if __name__ == "__main__":
    main(Path(__file__).with_name("reference.pdf"))
