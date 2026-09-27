"""Two scientific landscapes with independently chosen text and math fonts.

Run ``uv run python examples/font_showcases.py`` on Windows. The examples
require Comic Sans MS, Georgia, and Cambria Math (check ``typst fonts``).
"""

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

import plotst


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
INK = "#253249"


def _style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "#fffdf8",
        "axes.facecolor": "#fffdf8",
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def wave_interference() -> Figure:
    """Idealized equal-amplitude source waves, vector nodes and a slice."""
    plotst.setup(font="Comic Sans MS", math_font="Cambria Math", font_size=9)
    _style()
    x = np.linspace(-3.5, 3.5, 460)
    y = np.linspace(-2.8, 2.8, 360)
    xx, yy = np.meshgrid(x, y)
    k = 2 * np.pi / 0.85
    r1 = np.hypot(xx + 0.85, yy)
    r2 = np.hypot(xx - 0.85, yy)
    field = np.cos(k * r1) + np.cos(k * r2)
    fig = plt.figure(figsize=(184 / 25.4, 94 / 25.4), layout="constrained")
    grid = fig.add_gridspec(1, 2)
    wave = fig.add_subplot(grid[0])
    profile = fig.add_subplot(grid[1])
    image = wave.imshow(field, origin="lower", extent=[x[0], x[-1], y[0], y[-1]],
                        cmap="RdBu_r", vmin=-2, vmax=2, interpolation="bilinear")
    wave.contour(xx, yy, field, levels=[0], colors="white", linewidths=0.45, alpha=0.65)
    wave.scatter([-0.85, 0.85], [0, 0], s=65, c="#ffce57", edgecolor=INK, zorder=4)
    wave.axhline(1.3, color=INK, linestyle="--", linewidth=1)
    wave.set(xlabel="Across the pond $x$", ylabel="Along the pond $y$",
             title="A  Two sources, one ripple party")
    bar = fig.colorbar(image, ax=wave, pad=0.025, fraction=0.045,
                       ticks=[-2, 0, 2], aspect=26)
    bar.set_label("Displacement $u(x,y)$", fontsize=8)
    bar.outline.set_visible(False)
    slice_value = np.cos(k * np.hypot(x + 0.85, 1.3)) + np.cos(k * np.hypot(x - 0.85, 1.3))
    profile.fill_between(x, 0, slice_value, color="#ea6b62", alpha=0.23)
    profile.plot(x, slice_value, color="#b34049", linewidth=1.7)
    profile.axhline(0, color=INK, linewidth=0.6)
    profile.set(xlabel="Position $x$", ylabel="Displacement $u$", ylim=(-2.3, 2.3),
                title="B  A slice through the splash")
    profile.set_xticks([-3, 0, 3])
    profile.grid(alpha=0.18)
    profile.text(0.5, 0.93, "$y = 1.3$", transform=profile.transAxes, ha="center", va="top")
    fig.suptitle("When ripples meet\n"
                 "$u(x,y) = cos(k r_1) + cos(k r_2), quad k = frac(2 pi, lambda)$",
                 fontsize=14)
    fig.supxlabel("Comic Sans MS labels  /  Cambria Math equations", fontsize=8)
    return fig


def monkey_saddle() -> Figure:
    """A degenerate saddle shown as a height map and circular sections."""
    plotst.setup(font="Georgia", math_font="New Computer Modern Math", font_size=9)
    _style()
    coordinate = np.linspace(-1.55, 1.55, 420)
    x, y = np.meshgrid(coordinate, coordinate)
    radius = np.hypot(x, y)
    height = np.ma.masked_where(radius > 1.45, x**3 - 3 * x * y**2)
    fig = plt.figure(figsize=(184 / 25.4, 105 / 25.4), layout="constrained")
    grid = fig.add_gridspec(1, 2)
    landscape = fig.add_subplot(grid[0])
    sections = fig.add_subplot(grid[1])
    image = landscape.imshow(height, origin="lower", extent=[-1.55, 1.55] * 2,
                             cmap="PuOr_r", vmin=-3.1, vmax=3.1, interpolation="bilinear")
    landscape.contour(x, y, height, levels=[-2, -1, -0.3, 0.3, 1, 2],
                      colors=INK, linewidths=0.45, alpha=0.48)
    landscape.contour(x, y, height, levels=[0], colors="white", linewidths=1.2)
    angle = np.linspace(0, 2 * np.pi, 600)
    for r, color in [(0.8, "#28878b"), (1.25, "#b36a25")]:
        landscape.plot(r * np.cos(angle), r * np.sin(angle), color=color,
                       linewidth=1.3, linestyle="--")
        sections.plot(angle / np.pi, r**3 * np.cos(3 * angle), color=color,
                      linewidth=1.65, label=f"$r = {r}$")
    landscape.scatter([0], [0], s=22, c=INK, zorder=5)
    landscape.annotate("Degenerate saddle", xy=(0, 0), xytext=(0.04, 0.05),
                       textcoords="axes fraction", fontsize=8,
                       bbox={"facecolor": "#fffdf8", "edgecolor": "none", "pad": 2},
                       arrowprops={"arrowstyle": "->", "color": INK})
    landscape.set(xlabel="$x$", ylabel="$y$", title="A  Three hills, three valleys",
                  ylim=(-1.6, 1.6))
    landscape.set_xticks([-1, 0, 1])
    landscape.set_yticks([-1, 0, 1])
    bar = fig.colorbar(image, ax=landscape, fraction=0.045, pad=0.035, ticks=[-3, 0, 3])
    bar.set_label("Height $z$", fontsize=8)
    bar.outline.set_visible(False)
    sections.axhline(0, color=INK, linewidth=0.6)
    sections.set(xlabel="Angle $theta / pi$", ylabel="Height $z(r,theta)$",
                 title="B  Walk around the saddle", xlim=(0, 2), ylim=(-2.65, 2.25))
    sections.set_yticks([-2, -1, 0, 1, 2])
    sections.set_xticks([0, 0.5, 1, 1.5, 2])
    sections.grid(alpha=0.18)
    sections.legend(loc="lower center", ncols=2, fontsize=8)
    fig.suptitle("The monkey saddle\n$z = x^3 - 3 x y^2 = r^3 cos(3 theta)$", fontsize=14)
    fig.supxlabel("A surface with room for two legs and a tail.\n"
                  "Georgia labels  /  New Computer Modern Math equations", fontsize=8)
    return fig


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, build in [("showcase-wave-interference", wave_interference),
                        ("showcase-monkey-saddle", monkey_saddle)]:
        figure = build()
        destination = OUTPUT / f"{name}.pdf"
        try:
            plotst.savefig(figure, destination)
        finally:
            plt.close(figure)
        print(destination)


if __name__ == "__main__":
    main()
