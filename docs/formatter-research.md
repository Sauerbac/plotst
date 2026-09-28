# Formatter compatibility research

Investigated 2026-09-28 against the installed and pinned Matplotlib 3.11.0 source, with current official documentation as a cross-check. This note records findings and provisional implementation guidance; it is not the supported-feature contract.

## Findings

- **Preserve batch formatting.** `Formatter.format_ticks(values)` is the public tick-label API. It establishes context before formatting values; `__call__` alone is insufficient. `ConciseDateFormatter` overrides the batch method to choose date components and compute its offset string. An adapter must delegate the original batch method, not recreate it with a loop over `__call__`. [Formatter API](https://matplotlib.org/stable/api/ticker_api.html#matplotlib.ticker.Formatter), [date formatter source](https://github.com/matplotlib/matplotlib/blob/v3.11.0/lib/matplotlib/dates.py)
- **Dates and categories are naturally text.** Date formatters retain timezone and date-format configuration. `AutoDateFormatter.scaled` may contain custom callables, so even an exact built-in class can emit user-defined content. `StrCategoryFormatter` maps integer positions back to category strings, including UTF-8 byte decoding. Dollar signs and underscores in those strings do not establish a markup contract. [Date API](https://matplotlib.org/stable/api/dates_api.html), [category API](https://matplotlib.org/stable/api/category_api.html), [date source](https://github.com/matplotlib/matplotlib/blob/v3.11.0/lib/matplotlib/dates.py)
- **Percentage precision needs the axis.** `PercentFormatter` derives automatic decimals from the current view interval and scales values using `xmax`. Its `symbol` property conditionally escapes TeX characters according to the global `text.usetex` setting; `is_latex=True` changes that policy. [PercentFormatter API](https://matplotlib.org/stable/api/ticker_api.html#matplotlib.ticker.PercentFormatter)
- **Engineering output mixes numbers and arbitrary text.** `EngFormatter` preserves unit, precision, separator, and SI prefix. Its math mode can emit a math-wrapped number followed by a text suffix, and its offset path differs from scalar scientific notation. A numeric-only math translator cannot cover arbitrary units. [Engineering formatter source](https://github.com/matplotlib/matplotlib/blob/v3.11.0/lib/matplotlib/ticker.py)
- **Locale handling is upstream formatting behavior.** `ScalarFormatter(useLocale=True)` applies locale formatting, including separators; mathtext additionally braces locale-generated commas. Preserve the resulting localized text rather than parsing it back as an English number. `EngFormatter.format_data` uses Python numeric formatting, so it does not gain locale-aware mantissas merely because it inherits ScalarFormatter. [Ticker source](https://github.com/matplotlib/matplotlib/blob/v3.11.0/lib/matplotlib/ticker.py)
- **Do not select a process locale during export.** Python locale changes are process-wide and `setlocale()` is not generally thread-safe. Respect the caller's locale; tests can replace the locale formatting boundary deterministically. [Python locale documentation](https://docs.python.org/3/library/locale.html)

## Provisional adapter contract

These are design recommendations inferred from the findings above:

Scope decision after the design discussion: rank 2 remains separate. No label
helpers or general string semantics change in this implementation. Automatic
handling is restricted to exact built-in formatters; custom formatters and
subclasses keep their previous behavior unless explicitly wrapped with
`adapt_formatter`. That wrapper escapes plain output by default and accepts a
custom conversion callback. The README records the implemented contract.

1. Declare literal text versus Typst source explicitly for custom formatters and subclasses. Do not guess from `$`, backslashes, class inheritance, or arbitrary callback output.
2. Delegate `set_axis`, `set_locs`, `format_ticks`, `__call__`, and `get_offset` as appropriate; preserve the original batch override and apply the same output policy to tick labels and offset text. Leave coordinate-display methods separate from rendering conversion.
3. Restrict automatic special handling to tested exact built-in types. Give subclasses an explicit opt-in wrapper or adapter. A callback-based output conversion hook should receive the completed label string, so the formatter remains responsible for numeric/date context.
4. For plain date/engineering output, consider an export-local shallow copy with its TeX/mathtext flags disabled, retaining axis/locator references and formatting configuration. Do not deep-copy a figure graph. If temporary mutation is used instead, restore all changed flags on success and failure.
5. Keep intentional scientific/logarithmic math conversion narrow. A literal-text fallback is appropriate only where the output contract explicitly says text; it must not silently reinterpret unsupported markup.

## Acceptance cases

- Default dates, explicit timezone, and concise dates spanning midnight/month/year; compare labels and offsets with upstream plain output.
- Categories containing `_`, `$`, `#`, brackets, backslashes, Unicode, and repeated values.
- Percentages with `xmax=1` and `100`, automatic precision after view-limit changes, custom symbols, negative values, and documented handling of TeX symbols.
- Engineering units with micro prefixes, thin spaces, negative values, precision, and nonzero offsets; exercise existing mathtext flags.
- Scalar locale decimals/grouping in normal labels and scientific/offset text, with deterministic locale mocks; do not require a particular installed OS locale.
- A custom subclass overriding `format_ticks` and `get_offset`, plus callable date formatting; verify explicit text and Typst policies.
- Major/minor formatters, shared axes, colorbars, repeated exports, and failure paths; restore formatter identity and automatic/default state after export.
