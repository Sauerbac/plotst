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
| [Formatter compatibility](gallery/README.md#common-matplotlib-formatters) | Concise dates across midnight, literal categories, percentages, engineering offsets, German numeric locale, custom subclass and conversion callback |
| Column-width figure | Exact 85 mm final width with content cropping and unchanged font sizes |
| Wave interference | Comic Sans MS text with Cambria Math, raster field, vector nodal contours, colorbar and cross-section |
| Monkey saddle | Georgia text with New Computer Modern Math, 2D surface height map, vector contours and circular sections |
| HS.273 three-body orbit | Vector trajectories, speed-colored detail, clipped line collections, separation diagnostics, tall native math and a PDF source link |

## Automated coverage

- `tests/test_savefig.py`: dimensions, layout, generated numeric labels, vector/raster output, and page edges.
- `tests/test_formatters.py`: dates/timezones, categories, percentage precision, engineering units/offsets, locale formatting, custom batch adapters, and shared-axis state restoration.
- `tests/test_pdf_composition.py`: PDF drawing order, transforms, clipping, alpha, links, and text geometry.
- `tests/test_math_fonts.py`: changing the math font changes the embedded font while preserving text and page width.
- `tests/test_tight_width.py`: exact column width, figure state restoration, and rendered margins.
- `tests/test_setup.py` and `tests/test_errors.py`: configuration, compiler diagnostics, and unsupported inputs.
- `tests/test_orbit_example.py`: full-period state closure, energy, momentum, and catalogue-scale physical checks for the gallery integrator.

## Boundaries

Exact built-in scalar/logarithmic, date (`DateFormatter`, `AutoDateFormatter`,
`ConciseDateFormatter`), category (`StrCategoryFormatter`), percentage, and
engineering formatters are adapted during export and restored afterward.
Dates retain their batch context, timezone, and shared offset. Category strings,
date callbacks, units, and symbols are treated as text. Engineering and
locale-aware scalar formatters use upstream plain-output mode; localized
scientific offsets use `1eN` notation. Existing locale settings are honored,
never changed. Engineering mantissas follow Matplotlib's non-localized behavior.

Unwrapped custom formatters and subclasses still return valid Typst content.
`plotst.adapt_formatter(formatter)` explicitly opts plain-output custom
formatters into escaping; an optional `convert` callback defines custom
conversion to Typst. Batch overrides, locations, axis/locator context, and
offsets are forwarded. This is a formatter-only contract; user-label semantics
are unchanged. User labels accept Typst prose and math; they are not interpreted
as LaTeX or arbitrary Mathtext.

Unsupported areas include polar/3D axes, automatic conversion of arbitrary
formatter subclasses or user-generated Mathtext/LaTeX, `text.usetex`, path effects, complex clipping,
Typst-internal multiline blocks or explicit movement, rasterized text or text
containers, arbitrary `bbox_inches` settings, interactive output, and SVG/PNG export.
Gallery PNGs are previews rendered from the PDF by Poppler.

The [README](../README.md#initial-supported-contract) describes the API contract
and export behavior. Report issues with a minimal script, the Python and Typst
versions, and the error or unexpected PDF result.
