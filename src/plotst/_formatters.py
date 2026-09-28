from __future__ import annotations

from contextlib import contextmanager
from copy import copy
import json
import re
from collections.abc import Callable, Iterator

from matplotlib import dates, ticker
from matplotlib.axis import Axis
from matplotlib.category import StrCategoryFormatter
from matplotlib.figure import Figure

from ._errors import UnsupportedFeatureError


_SUPPORTED_FORMATTERS = (
    ticker.ScalarFormatter,
    ticker.LogFormatter,
    ticker.LogFormatterMathtext,
    ticker.LogFormatterSciNotation,
)

_TEXT_FORMATTERS = (
    dates.DateFormatter,
    dates.AutoDateFormatter,
    dates.ConciseDateFormatter,
    StrCategoryFormatter,
    ticker.PercentFormatter,
    ticker.EngFormatter,
)

_DATE_FORMATTERS = (dates.DateFormatter, dates.AutoDateFormatter, dates.ConciseDateFormatter)


def _literal_text(value: str) -> str:
    # Preserve real line breaks so Matplotlib still owns multiline layout.
    return "\n".join(
        f"#text({json.dumps(line, ensure_ascii=False)})" if line else ""
        for line in value.split("\n")
    )


def _generated_label_to_typst(value: str) -> str:
    """Translate the narrow grammar emitted by supported built-in formatters."""
    if not value:
        return value
    if not (value.startswith("$") and value.endswith("$")):
        return _literal_text(value)

    math = value[1:-1]
    math = math.replace(r"\mathdefault", "")
    math = math.replace(r"\times", " times ").replace(r"\,", " ")
    math = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", math)
    math = math.replace("{", "").replace("}", "")
    if not re.fullmatch(r"(?:[0-9.eE+−\-×()^\s]|times)+", math):
        raise UnsupportedFeatureError(
            "Plotst cannot translate the label emitted by a built-in "
            f"Matplotlib formatter: {value!r}"
        )
    return f"${math}$"


class _FormatterAdapter(ticker.Formatter):
    def __init__(
        self, original: ticker.Formatter, convert: Callable[[str], str]
    ) -> None:
        self._original = original
        self._convert = convert
        if original.axis is not None:
            self.set_axis(original.axis)

    def set_axis(self, axis) -> None:
        super().set_axis(axis)
        self._original.set_axis(axis)

    def set_locs(self, locs) -> None:
        super().set_locs(locs)
        self._original.set_locs(locs)

    def __call__(self, value, pos=None) -> str:
        return self._convert(self._original(value, pos))

    def format_ticks(self, values) -> list[str]:
        return [self._convert(label) for label in self._original.format_ticks(values)]

    def get_offset(self) -> str:
        return self._convert(self._original.get_offset())

    def _set_locator(self, locator) -> None:
        self._original._set_locator(locator)

    def format_data(self, value) -> str:
        return self._original.format_data(value)

    def format_data_short(self, value) -> str:
        return self._original.format_data_short(value)


def adapt_formatter(
    formatter: ticker.Formatter,
    *,
    convert: Callable[[str], str] | None = None,
) -> ticker.Formatter:
    """Opt a formatter or subclass into Plotst's formatter rendering contract.

    By default, completed tick labels and offsets are escaped as literal text.
    A supplied ``convert`` receives each completed string (including empty
    strings) and must return valid Typst content. No Mathtext/LaTeX detection or
    translation is performed. Configure numeric subclasses with mathtext and
    TeX disabled when using the default conversion.

    The original formatter receives axis, locator, location, and full-batch
    formatting calls; its normal draw-time state may change. Coordinate-display
    methods delegate without conversion. Install the returned formatter with
    Matplotlib's major/minor formatter setters. Unwrapped custom formatters keep
    their existing behavior.
    """
    if not isinstance(formatter, ticker.Formatter):
        raise TypeError("formatter must be a Matplotlib Formatter instance")
    if convert is not None and not callable(convert):
        raise TypeError("convert must be callable")
    return _FormatterAdapter(formatter, _literal_text if convert is None else convert)


def _builtin_adapter(original: ticker.Formatter) -> ticker.Formatter | None:
    kind = type(original)
    if kind not in _SUPPORTED_FORMATTERS + _TEXT_FORMATTERS:
        return None
    # Keep per-draw offsets, location caches, and presentation flags local to the
    # export without copying the attached axis/figure or its unit mapping.
    formatter = copy(original)
    literal = kind in _TEXT_FORMATTERS or (
        kind is ticker.ScalarFormatter and formatter.get_useLocale()
    )
    if literal:
        if isinstance(formatter, ticker.ScalarFormatter):
            formatter.set_useMathText(False)
            formatter.set_usetex(False)
        elif kind in _DATE_FORMATTERS:
            formatter._usetex = False
    return _FormatterAdapter(
        formatter, _literal_text if literal else _generated_label_to_typst
    )


@contextmanager
def adapted_builtin_formatters(figure: Figure) -> Iterator[None]:
    """Adapt supported generated labels for one export, then restore the figure."""
    installed: list[tuple[Axis, str, ticker.Formatter, bool, Axis | None]] = []
    try:
        for axes in figure.axes:
            for axis in (axes.xaxis, axes.yaxis):
                for kind in ("major", "minor"):
                    getter = getattr(axis, f"get_{kind}_formatter")
                    setter = getattr(axis, f"set_{kind}_formatter")
                    original = getter()
                    adapter = _builtin_adapter(original)
                    if adapter is not None:
                        default = getattr(axis, f"isDefault_{kind[:3]}fmt")
                        installed.append((axis, kind, original, default, original.axis))
                        setter(adapter)
        yield
    finally:
        for axis, kind, original, default, original_axis in reversed(installed):
            getattr(axis, f"set_{kind}_formatter")(original)
            original.set_axis(original_axis)
            setattr(axis, f"isDefault_{kind[:3]}fmt", default)
