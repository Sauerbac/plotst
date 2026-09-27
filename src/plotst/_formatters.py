from __future__ import annotations

from contextlib import contextmanager
import json
import re
from collections.abc import Iterator

from matplotlib import ticker
from matplotlib.figure import Figure

from ._errors import UnsupportedFeatureError


_SUPPORTED_FORMATTERS = (
    ticker.ScalarFormatter,
    ticker.LogFormatter,
    ticker.LogFormatterMathtext,
    ticker.LogFormatterSciNotation,
)


def _literal_text(value: str) -> str:
    return f"#text({json.dumps(value, ensure_ascii=False)})"


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


class _BuiltinFormatterAdapter(ticker.Formatter):
    def __init__(self, original: ticker.Formatter) -> None:
        self._original = original

    def set_axis(self, axis) -> None:
        super().set_axis(axis)
        self._original.set_axis(axis)

    def set_locs(self, locs) -> None:
        super().set_locs(locs)
        self._original.set_locs(locs)

    def __call__(self, value, pos=None) -> str:
        return _generated_label_to_typst(self._original(value, pos))

    def get_offset(self) -> str:
        return _generated_label_to_typst(self._original.get_offset())


@contextmanager
def adapted_builtin_formatters(figure: Figure) -> Iterator[None]:
    """Adapt supported generated labels for one export, then restore the figure."""
    installed: list[tuple[object, str, ticker.Formatter]] = []
    try:
        for axes in figure.axes:
            for axis in (axes.xaxis, axes.yaxis):
                for kind in ("major", "minor"):
                    getter = getattr(axis, f"get_{kind}_formatter")
                    setter = getattr(axis, f"set_{kind}_formatter")
                    original = getter()
                    if type(original) in _SUPPORTED_FORMATTERS:
                        installed.append((axis, kind, original))
                        setter(_BuiltinFormatterAdapter(original))
        yield
    finally:
        for axis, kind, original in reversed(installed):
            getattr(axis, f"set_{kind}_formatter")(original)
