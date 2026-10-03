"""Export an 85 mm paper-column PDF without outer figure padding."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
import numpy as np

import plotst


plotst.setup(
    font="New Computer Modern",
    math_font="New Computer Modern Math",
    font_size=9,
)

x = np.linspace(0, 4, 180)
figure, axis = plt.subplots(figsize=(4.6, 2.5), layout="constrained")
axis.plot(x, np.exp(-x / 2) * np.sin(2.5 * x), label="Damped response $y(t)$")
axis.set_xlabel("Time $t$ (s)")
axis.set_ylabel("Normalized signal $y/y_0$")
axis.set_title("Column-width response")
axis.legend(loc="upper right", fontsize=8)
axis.grid(alpha=0.25)

destination = (
    Path(__file__).resolve().parents[1]
    / "output"
    / "pdf"
    / "plotst-column-85mm.pdf"
)
destination.parent.mkdir(parents=True, exist_ok=True)
try:
    plotst.savefig(figure, destination, tight_width_mm=85)
finally:
    plt.close(figure)
print(destination)
