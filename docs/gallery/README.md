# Plotst gallery

Scientific figures with Matplotlib geometry and Typst typography. Click any
preview to open its PDF. The PDFs retain their physical page sizes and tested
vector/text content; the PNGs are previews for browsing on GitHub.

The single-axis examples use constrained layout or a tight content crop to
give the plotted data more room while keeping labels and titles readable.
Each example below links to its runnable source.

Run the commands from the repository root after `uv sync --locked`.

## Typst mathematics

A math-rich title with native Typst syntax, serif prose, bold and italic labels.
156 x 88 mm. Inspired by Matplotlib's
[TeX text example](https://matplotlib.org/stable/gallery/text_labels_and_annotations/tex_demo.html).

[![Typst mathematics](representative-typst-math.png)](representative-typst-math.pdf)

[Source](../../examples/representative_figures.py#L333) · `uv run python examples/representative_figures.py`

## An ordinary scientific plot

Constrained layout, inline mathematics, a legend, and an exact 120 x 80 mm page.

[![Ordinary plot](plotst-ordinary.png)](plotst-ordinary.pdf)

[Source](../../examples/ordinary.py) · `uv run python examples/ordinary.py`

## Fit a paper column

An exact 85 mm final width, including labels and legend, with a tight content
crop. Font sizes stay unchanged.

[![Column-width plot](plotst-column-85mm.png)](plotst-column-85mm.pdf)

[Source](../../examples/column_width.py) · `uv run python examples/column_width.py`

## Logarithmic and scientific axes

A rasterized heatmap with vector contours, logarithmic ticks, a scientific
multiplier, and a logarithmic colorbar. 148 x 88 mm.

[![Logarithmic and scientific axes](representative-log-scientific-colorbar.png)](representative-log-scientific-colorbar.pdf)

[Source](../../examples/representative_figures.py#L58) · `uv run python examples/representative_figures.py`

## Mixed vector and raster panels

A raster field alongside vector contours, profiles, markers, uncertainty bands,
and a colorbar. 168 x 82 mm.

[![Mixed vector and raster panels](representative-mixed-vector-raster.png)](representative-mixed-vector-raster.pdf)

[Source](../../examples/representative_figures.py#L112) · `uv run python examples/representative_figures.py`

## Annotations and tall mathematics

Arrows, rotated labels, multiline text, native Typst equations, and clickable PDF
links. 156 x 92 mm.

[![Annotation-rich figure](representative-annotations.png)](representative-annotations.pdf)

[Source](../../examples/representative_figures.py#L220) · `uv run python examples/representative_figures.py`

See the [support matrix](../support.md) for boundaries and
[contributor guide](../../CONTRIBUTING.md#refresh-the-gallery) to regenerate previews.
