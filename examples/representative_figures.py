"""Render the representative figures used by the support matrix.

Run from the repository root with::

    uv run python examples/representative_figures.py

The first three examples combine related figure features. The fourth adapts
Matplotlib's TeX demo using Plotst's native Typst math syntax.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
import numpy as np

import plotst


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"

INK = "#17324d"
BLUE = "#2878b5"
CYAN = "#39a7a5"
GOLD = "#e9a23b"
RED = "#c84c4c"
PAPER = "#f8fafc"
GRID = "#d8e1e8"


def _set_visual_defaults() -> None:
    """Set presentation defaults without overriding Plotst typography."""
    plt.rcParams.update(
        {
            "axes.facecolor": PAPER,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.linewidth": 0.8,
            "figure.facecolor": "white",
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "legend.frameon": False,
            "xtick.color": INK,
            "ytick.color": INK,
        }
    )


def log_scientific_colorbar() -> Figure:
    """Logarithmic x axis, scientific y ticks, and a logarithmic colorbar."""
    frequency = np.geomspace(1e-2, 1e4, 220)
    elapsed = np.linspace(0, 6e6, 150)
    log_frequency = np.log10(frequency)[None, :]
    normalized_time = (elapsed / elapsed.max())[:, None]
    ridge = np.exp(
        -((log_frequency - (-0.7 + 3.6 * normalized_time)) / 0.55) ** 2
    )
    modulation = 0.55 + 0.45 * np.cos(
        2.4 * log_frequency - 4 * normalized_time
    ) ** 2
    power = 1e-3 * 10 ** (3.8 * ridge * modulation)

    figure, axis = plt.subplots(
        figsize=(148 / 25.4, 88 / 25.4),
    )
    figure.subplots_adjust(left=0.11, right=0.82, bottom=0.17, top=0.87)
    mesh = axis.pcolormesh(
        frequency,
        elapsed,
        power,
        shading="auto",
        cmap="magma",
        norm=LogNorm(vmin=1e-3, vmax=6),
        rasterized=True,
    )
    axis.contour(
        frequency,
        elapsed,
        power,
        levels=[0.03, 0.3, 3],
        colors="white",
        linewidths=0.65,
        alpha=0.7,
    )
    axis.set_xscale("log")
    axis.ticklabel_format(
        axis="y",
        style="sci",
        scilimits=(0, 0),
        useMathText=True,
    )
    axis.set_xlabel("Frequency $f$ (Hz)")
    axis.set_ylabel("Elapsed time $t$ (s)")
    axis.set_title("A transient crossing six frequency decades", loc="left")
    axis.grid(which="major", alpha=0.28)

    colorbar = figure.colorbar(mesh, ax=axis, pad=0.025, aspect=28)
    colorbar.set_label("Spectral power $P(f,t)$")
    colorbar.outline.set_linewidth(0.6)
    return figure


def mixed_vector_raster_panels() -> Figure:
    """A raster field alongside vector contours, profiles, and markers."""
    coordinate = np.linspace(-3.2, 3.2, 240)
    x_grid, y_grid = np.meshgrid(coordinate, coordinate)
    field = (
        1.25 * np.exp(-((x_grid - 0.8) ** 2 + (y_grid + 0.4) ** 2) / 1.4)
        - 0.9 * np.exp(-((x_grid + 1.1) ** 2 + (y_grid - 0.8) ** 2) / 0.8)
        + 0.14 * np.cos(2.2 * x_grid) * np.sin(1.7 * y_grid)
    )

    figure, (map_axis, profile_axis) = plt.subplots(
        1,
        2,
        figsize=(168 / 25.4, 82 / 25.4),
        gridspec_kw={"width_ratios": [1.08, 1]},
    )
    figure.subplots_adjust(
        left=0.09,
        right=0.975,
        bottom=0.16,
        top=0.80,
        wspace=0.43,
    )
    image = map_axis.imshow(
        field,
        extent=[coordinate.min(), coordinate.max()] * 2,
        origin="lower",
        cmap="RdBu_r",
        vmin=-1.15,
        vmax=1.15,
        interpolation="bilinear",
    )
    map_axis.contour(
        x_grid,
        y_grid,
        field,
        levels=[-0.75, -0.35, 0.35, 0.75],
        colors=INK,
        linewidths=0.55,
        alpha=0.72,
    )
    map_axis.scatter(
        [-1.1, 0.8],
        [0.8, -0.4],
        s=30,
        facecolor="white",
        edgecolor=INK,
        linewidth=0.8,
        zorder=4,
    )
    map_axis.set(
        xlabel="Horizontal position $x$",
        ylabel="Vertical position $y$",
        title="A  Raster field + vector contours",
    )
    map_axis.set_aspect("equal")
    map_axis.grid(alpha=0.18)
    colorbar = figure.colorbar(image, ax=map_axis, pad=0.025, shrink=0.94)
    colorbar.outline.set_linewidth(0.6)

    selected_rows = [72, 120, 168]
    colors = [BLUE, CYAN, GOLD]
    for row, color in zip(selected_rows, colors, strict=True):
        y_value = coordinate[row]
        profile = field[row]
        uncertainty = 0.045 + 0.018 * np.abs(profile)
        profile_axis.fill_between(
            coordinate,
            profile - uncertainty,
            profile + uncertainty,
            color=color,
            alpha=0.13,
            linewidth=0,
        )
        profile_axis.plot(
            coordinate,
            profile,
            color=color,
            linewidth=1.55,
            label=f"$y = {y_value:+.1f}$",
        )
        sample = slice(8, None, 28)
        profile_axis.scatter(
            coordinate[sample],
            profile[sample],
            s=11,
            color=color,
            edgecolor="white",
            linewidth=0.35,
            zorder=3,
        )

    profile_axis.axhline(0, color=INK, linewidth=0.7, alpha=0.7)
    profile_axis.set(
        xlabel="Horizontal position $x$",
        ylabel="Field amplitude $phi(x,y)$",
        title="B  Vector profiles + uncertainty",
    )
    profile_axis.grid(alpha=0.7)
    profile_axis.legend(title="Cross-section", fontsize=8, title_fontsize=8)
    figure.suptitle(
        "One scientific figure, selective rasterization",
        fontsize=12,
        y=0.95,
    )
    return figure


def annotation_showcase() -> Figure:
    """Rotation, multiline labels, links, and tall Typst mathematics."""
    time = np.linspace(0, 10, 500)
    envelope = np.exp(-0.19 * time)
    response = envelope * np.cos(1.35 * time**1.18)

    figure, axis = plt.subplots(
        figsize=(156 / 25.4, 92 / 25.4),
    )
    figure.subplots_adjust(left=0.13, right=0.975, bottom=0.17, top=0.82)
    axis.fill_between(
        time,
        -envelope,
        envelope,
        color=BLUE,
        alpha=0.09,
        label="Decay envelope",
    )
    axis.plot(time, response, color=BLUE, linewidth=1.8, label="Observed response")
    axis.axhline(0, color=INK, linewidth=0.7, alpha=0.55)
    axis.axvspan(4.55, 5.45, color=GOLD, alpha=0.18, linewidth=0)

    event_time = 4.95
    event_value = np.interp(event_time, time, response)
    axis.scatter(
        [event_time],
        [event_value],
        color=RED,
        edgecolor="white",
        linewidth=0.7,
        s=38,
        zorder=4,
    )
    axis.annotate(
        "Detected event\nwindow: 0.90 s",
        xy=(event_time, event_value),
        xytext=(5.75, 0.62),
        arrowprops={
            "arrowstyle": "-|>",
            "color": RED,
            "linewidth": 0.9,
            "connectionstyle": "arc3,rad=-0.16",
        },
        color=RED,
        fontsize=9,
        linespacing=1.18,
        ha="left",
        va="center",
    )
    axis.text(
        2.0,
        -0.73,
        "rotated phase marker",
        rotation=24,
        rotation_mode="anchor",
        color=CYAN,
        fontsize=9,
        ha="left",
        va="bottom",
        url=(
            "https://matplotlib.org/stable/gallery/"
            "text_labels_and_annotations/demo_text_rotation_mode.html"
        ),
    )
    axis.text(
        0.34,
        0.74,
        "$frac(sum_(k=1)^n k^2, sqrt(alpha^2 + beta^2))$",
        transform=axis.transAxes,
        fontsize=14,
        fontweight="bold",
        color=INK,
        ha="center",
        va="center",
        bbox={
            "boxstyle": "round,pad=0.38",
            "facecolor": "white",
            "edgecolor": GRID,
            "linewidth": 0.8,
        },
    )
    axis.text(
        0.025,
        0.035,
        "Annotation guide ↗",
        transform=axis.transAxes,
        fontsize=8,
        color=BLUE,
        url="https://matplotlib.org/stable/users/explain/text/annotations.html",
    )
    axis.text(
        0.025,
        0.105,
        "Typst math guide ↗",
        transform=axis.transAxes,
        fontsize=8,
        color=BLUE,
        url="https://typst.app/docs/reference/math/",
    )

    axis.set(
        xlim=(0, 10),
        ylim=(-1.05, 1.05),
        xlabel="Elapsed time $t$ (s)",
        ylabel="Normalized response $y(t)$",
        title="Annotation-rich composition\nwith real PDF text and links",
    )
    axis.grid(alpha=0.65)
    axis.legend(loc="upper right", fontsize=8)
    axis.spines[["top", "right"]].set_visible(False)
    return figure


def typst_math_demo() -> Figure:
    """Typst counterpart to Matplotlib's TeX rendering demonstration."""
    time = np.linspace(0, 1, 400)
    velocity = np.cos(4 * np.pi * time) + 2
    figure, axis = plt.subplots(figsize=(156 / 25.4, 88 / 25.4))
    figure.subplots_adjust(left=0.17, right=0.96, bottom=0.19, top=0.74)
    axis.plot(time, velocity, color=BLUE, linewidth=1.8)
    axis.fill_between(time, 2, velocity, color=CYAN, alpha=0.12)
    axis.axhline(2, color=INK, linewidth=0.7, alpha=0.45)
    axis.set_xlabel("Time $t$ (s)", fontweight="bold")
    axis.set_ylabel("Velocity (°/s)", fontstyle="italic")
    axis.set_title(
        "Typst is Number $sum_(n=1)^oo frac(-e^(i pi), 2^n)$!",
        fontsize=13,
        color=RED,
        pad=14,
    )
    axis.grid(alpha=0.65)
    axis.spines[["top", "right"]].set_visible(False)
    return figure


def main() -> None:
    plotst.setup(
        font="New Computer Modern",
        math_font="New Computer Modern Math",
        font_size=9,
    )
    _set_visual_defaults()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    examples = {
        "representative-log-scientific-colorbar.pdf": log_scientific_colorbar,
        "representative-mixed-vector-raster.pdf": mixed_vector_raster_panels,
        "representative-annotations.pdf": annotation_showcase,
        "representative-typst-math.pdf": typst_math_demo,
    }
    for filename, build in examples.items():
        figure = build()
        destination = OUTPUT / filename
        try:
            plotst.savefig(figure, destination)
        finally:
            plt.close(figure)
        print(destination)


if __name__ == "__main__":
    main()
