"""Self-contained wave-interference example displayed in the README."""

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
import numpy as np
import plotst

plotst.setup()

# Presentation settings for the README preview; the plotting API works without them.
plt.rcParams.update({
    "figure.figsize": (3.5, 4.0),
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.09,
})

# Replace this generated field with your own 2D data.
y, x = np.mgrid[-3:3:300j, -3:3:300j]
u = (np.cos(6 * np.hypot(x - 1, y))
     + np.cos(6 * np.hypot(x + 1, y)))

fig, ax = plt.subplots()
image = ax.imshow(u, cmap="RdBu_r", vmin=-2, vmax=2)
ax.ticklabel_format(scilimits=(0, 0), useMathText=True)

ax.annotate("In phase\n$Delta phi = 0$",
            xy=(149.5, 149.5), xytext=(35, 70),
            arrowprops=dict(arrowstyle="->"),
            bbox=dict(boxstyle="round,pad=0.38",
                      facecolor="white", edgecolor="#d6e2eb"))

ax.set(xlabel="$x$", ylabel="$y$")
ax.set_title("When waves meet\n"
             "$u = sum_(i=1)^2 cos((2 pi r_i)/lambda)$",
             pad=12, linespacing=1.6)
fig.colorbar(image, cax=ax.inset_axes([1.05, 0, 0.05, 1]),
             ticks=[-2, 0, 2], label="Displacement $u$")

destination = Path(__file__).resolve().parents[1] / "output" / "pdf" / "readme-wave-interference.pdf"
destination.parent.mkdir(parents=True, exist_ok=True)
plotst.savefig(fig, destination)
plt.close(fig)
print(destination)
