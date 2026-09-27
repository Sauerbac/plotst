# Supported figures and limits

Plotst currently targets Windows, Python 3.12-3.14, and Typst 0.15.0.
The [Windows CI workflow](../.github/workflows/ci.yml) checks each Python version
with the dependencies in `uv.lock`. The package's Python minimum is 3.12;
newer versions outside that matrix are not yet verified.

## Representative figures

The [gallery](gallery/README.md) pairs each figure with its PDF and runnable source.
These examples exercise the supported PDF surface, not general Matplotlib compatibility.

| Figure | Features exercised |
| --- | --- |
| Ordinary line plot | Constrained layout, titles, axis labels, legend, inline mathematics, exact 120 x 80 mm page |
| Log/scientific heatmap | Logarithmic ticks, scientific multiplier, logarithmic colorbar, rasterized mesh and vector contours |
| Mixed vector/raster panels | Multiple axes, raster image, vector lines and markers, uncertainty bands, legend and colorbar |
| Annotation-rich composition | Arrows, anchored rotation, Matplotlib-managed multiline labels, tall math, PDF links |
| Typst math plot | Math-rich title, serif prose, bold and italic labels, extractable PDF text |
| Column-width figure | Exact 85 mm final width with content cropping and unchanged font sizes |

## Automated coverage

- `tests/test_savefig.py`: dimensions, layout, generated numeric labels, vector/raster output, and page edges.
- `tests/test_pdf_composition.py`: PDF drawing order, transforms, clipping, alpha, links, and text geometry.
- `tests/test_math_fonts.py`: changing the math font changes the embedded font while preserving text and page width.
- `tests/test_tight_width.py`: exact column width, figure state restoration, and rendered margins.
- `tests/test_setup.py` and `tests/test_errors.py`: configuration, compiler diagnostics, and unsupported inputs.

## Boundaries

Built-in scalar and logarithmic formatters are adapted during export and restored
afterward. Custom formatters must return valid Typst content. User labels accept
Typst prose and math; they are not interpreted as LaTeX or arbitrary Mathtext.

Unsupported areas include polar/3D axes, date/category/locale formatters,
arbitrary formatter subclasses, `text.usetex`, path effects, complex clipping,
Typst-internal multiline blocks or explicit movement, rasterized text or text
containers, arbitrary `bbox_inches` settings, interactive output, and SVG/PNG export.
Gallery PNGs are previews rendered from the PDF by Poppler.

The [README](../README.md#initial-supported-contract) describes the API contract
and export behavior. Report issues with a minimal script, the Python and Typst
versions, and the error or unexpected PDF result.
