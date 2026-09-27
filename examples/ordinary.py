from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt

import plotst


plotst.setup(
    font="New Computer Modern",
    math_font="New Computer Modern Math",
    font_size=10,
)

figure, axis = plt.subplots(
    figsize=(120 / 25.4, 80 / 25.4),
    layout="constrained",
)
x = [0, 0.5, 1, 1.5, 2]
y = [value**2 for value in x]
axis.plot(x, y, label="Response $f(x) = x^2$")
axis.scatter(x, y, color="#bd561f", zorder=3)
axis.set_xlabel("Time $t$ (s)")
axis.set_ylabel("Normalized response $frac(y, y_0)$")
axis.set_title("Typst measured figure", fontsize=12, fontweight="bold")
axis.legend(loc="upper left", fontsize=8)

destination = Path(__file__).resolve().parents[1] / "output" / "pdf" / "plotst-ordinary.pdf"
destination.parent.mkdir(parents=True, exist_ok=True)
plotst.savefig(figure, destination)
plt.close(figure)
print(destination)
