# Supported figures and limits

Plotst currently targets Windows, Python 3.12-3.14, and Typst 0.15.0.
The [Windows CI workflow](../.github/workflows/ci.yml) checks each Python version
with the dependencies in `uv.lock`. The package's Python minimum is 3.12;
newer versions outside that matrix are not yet verified.

See the [installation guide](installation.md) for compiler builds and dependencies,
and the [usage guide](usage.md) for configuration, exports, and custom formatter adapters.

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

## Supported contract

- Fixed-size Matplotlib PDF figures and content-cropped PDFs at an exact
  requested width in millimeters.
- Ordinary line and scatter figures with linear axes.
- Titles, axis labels, ordinary numeric ticks, legends, rotation, color, and
  constrained layout.
- Built-in scalar and logarithmic ticks, including scientific/additive offsets
  and colorbar ticks produced by Matplotlib's standard formatters.
- Date and category ticks, percentages, engineering units, and locale-aware
  scalar ticks, including their shared offsets.
- Native Typst prose and inline math in user-authored labels.
- One Typst inline label per Matplotlib text line. Use Python `\n` when
  Matplotlib should manage multiple lines.
- Explicit Matplotlib font size, weight, and style overrides applied through
  Typst.
- Mixed vector/raster figures when only non-text artists are rasterized.
- Text clipping, opacity, drawing order, rotation, and URL annotations retained
  in the composed PDF.
- Real PDF text where Typst emits it; the ordinary example is not rasterized.

During an export, Plotst adapts exact instances of Matplotlib's
`ScalarFormatter`, `LogFormatter`, `LogFormatterMathtext`,
`LogFormatterSciNotation`, `DateFormatter`, `AutoDateFormatter`,
`ConciseDateFormatter`, `StrCategoryFormatter`, `PercentFormatter`, and
`EngFormatter`. Date labels retain their timezone, formatting, and shared date
offset. Categories, percentage symbols, engineering units, and date callback
results are escaped as text, including dollar signs and underscores. Real
newlines remain Matplotlib-managed lines.

Numeric scalar/log Mathtext uses a narrow translation to Typst. Engineering
formatters and locale-aware scalar formatters use Matplotlib's plain-output
mode during export, even when configured with `useMathText=True`. Engineering
prefixes, units, precision, and offsets remain intact; localized scalar
scientific offsets use plain `1eN` notation. Plotst honors the existing Python
locale and `useLocale` setting; it does not select or change the process locale.
`EngFormatter` does not localize its engineering mantissas in Matplotlib.
Date TeX wrappers are likewise disabled on the export copy; user-provided LaTeX
in date formats, callbacks, units, or symbols is not translated.

Automatic adapters use shallow export-local copies. The original formatter
objects, axis associations, and automatic-formatter flags are restored after
export, including after an error. Subclasses and other custom formatters are
not automatically replaced; their existing contract remains valid Typst label
content. These changes do not alter title/axis-label strings or introduce
general text/markup helpers.

Custom formatter usage and conversion callbacks are documented in the
[formatter adapter guide](usage.md#custom-formatter-adapter).

## Boundaries

Unsupported areas include polar/3D axes, automatic conversion of arbitrary
formatter subclasses or user-generated Mathtext/LaTeX, `text.usetex`, path effects, complex clipping,
Typst-internal multiline blocks or explicit movement, rasterized text or text
containers, arbitrary `bbox_inches` settings, interactive output, and SVG/PNG export.
Baseline shifts, page operations, and deliberate overflow within Typst labels
are also unsupported.

Gallery PNGs are previews rendered from the PDF by Poppler.

## Automated coverage

- `tests/test_savefig.py`: dimensions, layout, generated numeric labels, vector/raster output, and page edges.
- `tests/test_formatters.py`: dates/timezones, categories, percentage precision, engineering units/offsets, locale formatting, custom batch adapters, and shared-axis state restoration.
- `tests/test_pdf_composition.py`: PDF drawing order, transforms, clipping, alpha, links, and text geometry.
- `tests/test_math_fonts.py`: changing the math font changes the embedded font while preserving text and page width.
- `tests/test_tight_width.py`: exact column width, figure state restoration, and rendered margins.
- `tests/test_setup.py` and `tests/test_errors.py`: configuration, compiler diagnostics, and unsupported inputs.
- `tests/test_orbit_example.py`: full-period state closure, energy, momentum, and catalogue-scale physical checks for the gallery integrator.

See [how PDF composition works](how-it-works.md) for the export internals.
Report issues with a minimal script, the Python and Typst versions, and the
error or unexpected PDF result.
