"""HS.273: a periodic three-body orbit, locally integrated with NumPy only.

Run ``uv run python examples/three_body_orbit.py``. Initial conditions and
period: https://www.threebodyorbits.com/orbit/hristov2026_hs273_1_1_1
Hristov, Hristova & Tanikawa, New Astronomy 125 (2026), arXiv:2510.22802.
The 12 published numbers below were read from the TBO3 header at
https://data.threebodyorbits.com/orbits/hristov2026_hs273_1_1_1.bin
(positions first, then velocities; retrieved 2026-09-27). No downloaded
trajectory or website rendering is needed to run this example.
"""

from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import numpy as np

import plotst


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
SOURCE = "https://www.threebodyorbits.com/orbit/hristov2026_hs273_1_1_1"
PERIOD = 451.6496746977138
INITIAL = np.array([
    -1.0, 0.0, 1.0, 0.0, 0.0, 0.0,
    0.4310349192649987, 0.5602541626292606,
    0.4310349192649987, 0.5602541626292606,
    -0.8620698385299975, -1.1205083252585213,
])
INK = "#24384b"
COLORS = ["#337eaa", "#e39a36", "#c14e69"]

# Dormand-Prince 5(4): accepted fifth-order states, fourth-order error estimate.
_ROWS = (
    (1 / 5,),
    (3 / 40, 9 / 40),
    (44 / 45, -56 / 15, 32 / 9),
    (19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729),
    (9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656),
    (35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84),
)
_ERROR = np.array([35 / 384 - 5179 / 57600, 0,
                   500 / 1113 - 7571 / 16695, 125 / 192 - 393 / 640,
                   -2187 / 6784 + 92097 / 339200, 11 / 84 - 187 / 2100, -1 / 40])


def _derivative(state: np.ndarray) -> np.ndarray:
    positions = state[:6].reshape(3, 2)
    offsets = positions[None, :, :] - positions[:, None, :]
    distance_squared = np.sum(offsets**2, axis=2)
    np.fill_diagonal(distance_squared, np.inf)
    acceleration = np.sum(offsets / distance_squared[:, :, None]**1.5, axis=1)
    return np.concatenate((state[6:], acceleration.ravel()))


def integrate_orbit(*, duration: float = PERIOD, tolerance: float = 2e-12) -> tuple[np.ndarray, np.ndarray]:
    """Integrate G = m1 = m2 = m3 = 1; retain adaptive, uncorrected states.

    Both relative and absolute tolerances use ``tolerance``. This demonstration
    uses ordinary float64 and does not reproduce the catalogue's high-precision
    closure or establish stability. Nothing forces the final point to close.
    """
    if duration <= 0 or tolerance <= 0:
        raise ValueError("Duration and tolerance must be positive")
    time, step = 0.0, 0.01
    state = INITIAL.copy()
    times, states = [time], [state.copy()]
    first = _derivative(state)
    for _ in range(200_000):
        step = min(step, duration - time)
        if time + step == time:
            raise RuntimeError("Orbit integrator step underflow")
        stages = [first]
        for row in _ROWS:
            stages.append(_derivative(state + step * np.dot(np.array(row), stages)))
        candidate = state + step * np.dot(np.array(_ROWS[-1]), stages[:-1])
        scale = tolerance * (1 + np.maximum(np.abs(state), np.abs(candidate)))
        error = np.sqrt(np.mean((step * np.dot(_ERROR, stages) / scale)**2))
        if error <= 1:
            time += step
            state = candidate
            first = stages[-1]
            times.append(time)
            states.append(state.copy())
            if time >= duration:
                return np.array(times), np.array(states)
        step *= min(5.0, max(0.2, 0.9 * error**(-0.2))) if error > 0 else 5.0
    raise RuntimeError("Orbit integrator exceeded its step budget")


def diagnostics(states: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return pairwise separations and conserved Newtonian total energy."""
    positions = states[:, :6].reshape(-1, 3, 2)
    velocity = states[:, 6:].reshape(-1, 3, 2)
    separations = np.stack([np.linalg.norm(positions[:, i] - positions[:, j], axis=1)
                            for i, j in [(0, 1), (1, 2), (2, 0)]], axis=1)
    energy = 0.5 * np.sum(velocity**2, axis=(1, 2)) - np.sum(1 / separations, axis=1)
    return separations, energy


def orbit_showcase(times: np.ndarray, states: np.ndarray) -> Figure:
    """Vector orbit, speed-colored detail, common snapshot and time diagnostics."""
    plotst.setup(font="New Computer Modern", math_font="Cambria Math", font_size=9)
    plt.rcParams.update({"figure.facecolor": "#fbfaf6", "axes.facecolor": "#fbfaf6",
                         "text.color": INK, "axes.labelcolor": INK,
                         "axes.edgecolor": INK, "xtick.color": INK, "ytick.color": INK,
                         "legend.frameon": False})
    positions = states[:, :6].reshape(-1, 3, 2)
    speeds = np.linalg.norm(states[:, 6:].reshape(-1, 3, 2), axis=2)
    distances, energy = diagnostics(states)
    closure = np.linalg.norm(states[-1, :6] - states[0, :6])
    drift = np.max(np.abs((energy - energy[0]) / energy[0]))
    fig = plt.figure(figsize=(210 / 25.4, 132 / 25.4), layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.55, 1], height_ratios=[1, 0.65])
    orbit = fig.add_subplot(grid[:, 0])
    detail = fig.add_subplot(grid[0, 1])
    separation = fig.add_subplot(grid[1, 1])
    snapshot = np.searchsorted(times, PERIOD / 7)
    for body, color in enumerate(COLORS):
        path = positions[:, body]
        orbit.plot(path[:, 0], path[:, 1], color=color, linewidth=0.42, alpha=0.46)
        # A short opaque trail makes each body's direction visible amid the loops.
        start = np.searchsorted(times, times[snapshot] - 1.7)
        orbit.plot(path[start:snapshot + 1, 0], path[start:snapshot + 1, 1],
                   color=color, linewidth=2, label=f"Body {body + 1}")
        orbit.scatter(*path[snapshot], color=color, edgecolor="white", linewidth=0.7,
                      s=38, zorder=5)
    orbit.set(xlabel="Position $x$", ylabel="Position $y$", title="A  HS.273 / one complete period")
    orbit.set_aspect("equal")
    orbit.set_xlim(-1.8, 1.8)
    orbit.set_ylim(-1.58, 1.58)
    orbit.legend(loc="upper left", fontsize=8)
    orbit.text(0.02, 0.02, "$t approx T / 7$ snapshot", transform=orbit.transAxes, fontsize=8)
    orbit.add_patch(Rectangle((0.5, -0.5), 0.9, 0.9, fill=False, edgecolor=INK,
                               linestyle="--", linewidth=0.8))
    for body in range(3):
        path = positions[:, body]
        segments = np.stack([path[:-1], path[1:]], axis=1)
        colored = LineCollection(segments, cmap="viridis", norm=Normalize(0, 1.65),
                                 linewidths=0.6, alpha=0.85)
        colored.set_array((speeds[:-1, body] + speeds[1:, body]) / 2)
        detail.add_collection(colored)
    detail.set(xlim=(0.5, 1.4), ylim=(-0.5, 0.4), xlabel="$x$", ylabel="$y$",
               title="B  Inside the weave")
    detail.set_aspect("equal")
    detail.set_xticks([0.6, 1, 1.4])
    detail.set_yticks([-0.4, 0, 0.4])
    bar = fig.colorbar(colored, ax=detail, pad=0.035, fraction=0.06, ticks=[0, 0.8, 1.6])
    bar.set_label("Speed $abs(bold(v))$", fontsize=8)
    bar.outline.set_visible(False)
    # Show the first 1/49 period: full-period diagnostics would obscure the cycles.
    window = times <= PERIOD / 49
    for pair, color, label in zip(range(3), COLORS, ["$r_(12)$", "$r_(23)$", "$r_(31)$"], strict=True):
        separation.plot(times[window], distances[window, pair], color=color,
                        linewidth=1.1, label=label)
    separation.set(xlabel="Time $t$", ylabel="Separation $r_(i j)$",
                   title="C  A first look at the rhythm", xlim=(0, PERIOD / 49), ylim=(0.2, 3.6))
    separation.set_yticks([1, 2, 3])
    separation.legend(ncols=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.04))
    separation.grid(alpha=0.18)
    for axis in [orbit, detail, separation]:
        axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Three bodies. Forty-nine twists.\n"
                  "$(dif^2 bold(r)_i)/(dif t^2) = sum_(j != i) (bold(r)_j - bold(r)_i)/abs(bold(r)_j - bold(r)_i)^3"
                  ", quad G = m_1 = m_2 = m_3 = 1$", fontsize=14)
    fig.supxlabel(f"$T = {PERIOD:.6f}$ / Local float64 integration, no forced closure\n"
                  f"Position closure: {closure:.1e} / max relative energy drift: {drift:.1e}\n"
                  "HS.273 / Hristov, Hristova & Tanikawa (2026) / orbit source",
                  fontsize=8, url=SOURCE)
    return fig


def main() -> None:
    times, states = integrate_orbit()
    figure = orbit_showcase(times, states)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "showcase-three-body-hs273.pdf"
    try:
        plotst.savefig(figure, destination)
    finally:
        plt.close(figure)
    print(destination)


if __name__ == "__main__":
    main()
