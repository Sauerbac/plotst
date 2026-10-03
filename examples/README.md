# Running the examples

Browse the [gallery](../docs/gallery/README.md) for previews and PDFs, or the
[support matrix](../docs/support.md) for the features each example exercises.
Each script writes PDFs under `output/pdf/` when run from the repository root.

## Setup and commands

First install Python and Typst as described in the [installation guide](../docs/installation.md).

Clone the repository and install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```powershell
git clone https://github.com/Sauerbac/plotst.git
cd plotst
uv sync --locked
uv run python examples\ordinary.py
uv run python examples\readme_example.py
uv run python examples\column_width.py
uv run python examples\representative_figures.py
uv run python examples\formatter_compatibility.py --locale de-DE
uv run python examples\font_showcases.py
uv run python examples\three_body_orbit.py
```

The ordinary example writes `output/pdf/plotst-ordinary.pdf` at exactly 120 mm by 80 mm.
Generated files under `output/` are ignored by Git. See
[contributor guide](../CONTRIBUTING.md) for tests, builds, and gallery maintenance.
The formatter example writes `output/pdf/formatter-compatibility.pdf`.
Its optional `--locale de-DE` selects German numeric formatting for the example
on Windows; omit it to use the process's current locale. Plotst does not select
the locale itself.
The font and orbit showcases additionally need Windows' Comic Sans MS, Georgia,
and Cambria Math; `typst fonts` lists available families. The orbit is integrated
locally with NumPy, using the linked catalogue's initial conditions, and needs
no network access or additional numerical packages.

## Representative support figures

The example corpus combines common publication use cases into four figures:

```powershell
uv run python examples\representative_figures.py
```

It produces a log/scientific heatmap with a colorbar, a multi-panel mixed
vector/raster figure, an annotation-heavy figure, and a math-rich cosine plot
adapted from Matplotlib's
[LaTeX text example](https://matplotlib.org/stable/users/explain/text/usetex.html).
The last figure uses Typst expressions such as `$sum_(n=1)^oo (-e^(i pi))/2^n$`;
Plotst does not interpret LaTeX source or require `text.usetex=True`.
The concise
[support matrix](../docs/support.md) records the representative features and links
to the maintained gallery.

## README example

[`readme_example.py`](readme_example.py) is the self-contained wave-interference
example displayed in the [README](../README.md). It generates its own data and
writes `output/pdf/readme-wave-interference.pdf` at 88.9 × 101.6 mm, with a raster
wave field, a math-rich arrow annotation, scientific axis notation, a colorbar
on the right, and native Typst mathematics.
The README uses `u = ...` to stand for the generated data and omits the preview's
size and layout settings. Without `extent`, `imshow` labels its array coordinates;
the axes therefore show column and row indices rather than physical distances.
The blue–white–red colormap uses symmetric limits so zero falls at its pale
midpoint. The annotation marks the equal-phase point between the two sources.
It uses only the bundled New Computer Modern fonts.
