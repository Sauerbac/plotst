# Using Plotst

[Quick start](../README.md) · [Installation](installation.md) · [Gallery](gallery/README.md)

## Create and export a figure

Call `plotst.setup()` before creating the figure so Matplotlib and Typst begin
with the same typography defaults. Export explicitly through
`plotst.savefig()`.

With no arguments, `setup()` checks the `typst` executable on `PATH` and selects
New Computer Modern text, New Computer Modern Math, and a 10 pt regular font.
It sets Matplotlib's typography defaults and disables Matplotlib's own Mathtext
and LaTeX handling for user labels so their native Typst source reaches Plotst.
Pass `font`, `math_font`, `font_size`, `font_weight`, or `typst` to customize
these defaults. Calling `savefig()` before `setup()` raises an error.

```python
import matplotlib.pyplot as plt
import plotst

plotst.setup(
    font="New Computer Modern",
    math_font="New Computer Modern Math",
    font_size=10,
)

fig, ax = plt.subplots(
    figsize=(120 / 25.4, 80 / 25.4),
    layout="constrained",
)
ax.plot([0, 1, 2], [0, 1, 4], label="Response $x^2$")
ax.set_xlabel("Time $t$")
ax.set_ylabel("Measured value")
ax.legend()

plotst.savefig(fig, "figure.pdf")
```

Use `layout="constrained"` to let Matplotlib fit the axes, titles, labels, and
colorbars within the requested page size using Typst's text measurements.
The gallery's single-axis examples use this to keep outer whitespace small
while preserving room for their text.

For a paper column with a fixed final width and little outer whitespace, use
`tight_width_mm`. Plotst fits the plotted area to the requested width without
rescaling the fonts. It trims around the title, ticks, labels, legend, and
other included artists with a small safety margin; the PDF height follows the
content. For a complete runnable example, use
[`examples/column_width.py`](../examples/column_width.py).

```python
plotst.savefig(fig, "figure-column.pdf", tight_width_mm=85)
```

Calling `setup()` again replaces the active process-wide configuration for
figures created afterward. Loading configuration from a file is deliberately
deferred; the current interface is Python-only.

## Custom formatter adapter

See [the runnable formatter showcase](../examples/formatter_compatibility.py) for
all supported families, a batch-aware subclass, and a custom conversion hook.

Opt an existing formatter or subclass that produces plain text into escaping:

```python
from matplotlib.ticker import FuncFormatter

formatter = FuncFormatter(lambda value, position: f"sample_{value:g}")
ax.xaxis.set_major_formatter(plotst.adapt_formatter(formatter))
```

`adapt_formatter` takes a Matplotlib `Formatter` instance. Its default
conversion escapes completed tick labels and offsets as literal text. For
numeric subclasses, configure `useMathText=False` and `usetex=False`; this
wrapper does not detect or translate Mathtext or LaTeX. A formatter already
producing Typst can continue to be installed directly without a wrapper.

For a custom conversion, pass `convert=callable`. It receives one completed
string at a time (including empty strings and offset strings) and must return
valid Typst content. The same callback applies to individual calls, batch
results, and offsets. The formatter retains responsibility for formatting
values; the callback only converts the resulting labels.

The adapter forwards axis and locator assignment, tick locations, the full
`format_ticks(values)` batch, and `get_offset()`. This preserves custom batch
logic rather than reducing it to individual calls. `format_data` and
`format_data_short` delegate without conversion. The wrapped formatter's
normal draw-time state may change. Install the wrapper with Matplotlib's
major/minor formatter setters; wrapped subclasses are never automatically
treated as built-ins. A wrapper emits Typst source and is intended for Plotst
exports, not ordinary Matplotlib rendering.

For automatic handling of built-in formatters and label syntax, see the
[supported contract](support.md#supported-contract).

## Diagnostics

`setup()` checks the configured Typst executable immediately. During export,
invalid Typst source identifies the failing label and includes the compiler
diagnostic. Typst warnings, including missing-font substitution, are treated as
errors so typography cannot silently change.
