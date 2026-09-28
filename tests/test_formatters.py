from __future__ import annotations

from copy import copy
from datetime import datetime, timedelta, timezone
import json
import locale
from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib import dates, ticker
import numpy as np
from pypdf import PdfReader
import pytest

import plotst
from plotst._formatters import adapted_builtin_formatters


def _text(source: str) -> str:
    return "\n".join(
        json.loads(line[len("#text("):-1]) if line else ""
        for line in source.split("\n")
    )


@pytest.fixture
def axes():
    figure, axis = plt.subplots()
    try:
        yield figure, axis
    finally:
        plt.close(figure)


@pytest.mark.parametrize("kind", ["auto", "explicit", "concise"])
@pytest.mark.parametrize("inverted", [False, True])
def test_dates_preserve_batches_timezone_and_offsets(axes, kind, inverted):
    figure, axis = axes
    tz = timezone(timedelta(hours=5, minutes=30))
    times = [datetime(2025, 12, 31, 23, tzinfo=tz) + timedelta(hours=i) for i in range(5)]
    values = dates.date2num(times)
    axis.plot(times, range(5))
    if inverted:
        axis.invert_xaxis()
    locator = dates.AutoDateLocator(tz=tz)
    axis.xaxis.set_major_locator(locator)
    formatter = {
        "auto": lambda: dates.AutoDateFormatter(locator, tz=tz),
        "explicit": lambda: dates.DateFormatter("%Y_%m_%d\n%H:%M %z", tz=tz),
        "concise": lambda: dates.ConciseDateFormatter(locator, tz=tz),
    }[kind]()
    axis.xaxis.set_major_formatter(formatter)
    expected = formatter.format_ticks(values)
    offset = formatter.get_offset()
    for _ in range(2):
        with adapted_builtin_formatters(figure):
            adapter = axis.xaxis.get_major_formatter()
            assert list(map(_text, adapter.format_ticks(values))) == expected
            assert _text(adapter.get_offset()) == offset
        assert axis.xaxis.get_major_formatter() is formatter


def test_auto_date_callback_output_is_text(axes):
    figure, axis = axes
    axis.plot([datetime(2026, 1, 1), datetime(2026, 1, 2)], [0, 1])
    formatter = axis.xaxis.get_major_formatter()
    formatter.scaled = {scale: lambda x, pos: "$date_#[]$" for scale in formatter.scaled}
    with adapted_builtin_formatters(figure):
        assert _text(axis.xaxis.get_major_formatter()(dates.date2num(datetime(2026, 1, 1)))) == "$date_#[]$"


def test_categories_preserve_special_characters_and_repeated_values(axes):
    figure, axis = axes
    labels = ["a_b", "$cost$", "#[]", "\\path", "Größe", "line\nbreak", "a_b"]
    axis.plot(labels, range(len(labels)))
    with adapted_builtin_formatters(figure):
        formatter = axis.xaxis.get_major_formatter()
        assert list(map(_text, formatter.format_ticks(range(6)))) == labels[:6]


@pytest.mark.parametrize("xmax", [1, 100])
def test_percent_precision_tracks_view_limits_and_symbol(axes, xmax):
    figure, axis = axes
    formatter = ticker.PercentFormatter(xmax=xmax, symbol="%_#[]$")
    axis.yaxis.set_major_formatter(formatter)
    values = [-0.002 * xmax, 0, 0.004 * xmax]
    with adapted_builtin_formatters(figure):
        for limit in (xmax, xmax / 100):
            axis.set_ylim(-limit, limit)
            expected = formatter.format_ticks(values)
            result = axis.yaxis.get_major_formatter().format_ticks(values)
            assert list(map(_text, result)) == expected


@pytest.mark.parametrize("offset", [False, True])
def test_engineering_preserves_units_precision_and_offsets(axes, offset):
    figure, axis = axes
    values = [1e9 + i * 1000 for i in range(4)] if offset else [-2e-6, 0, 3e-6]
    axis.set_xlim(values[0], values[-1])
    formatter = ticker.EngFormatter(
        unit="V_#[]$", places=2, sep="\u2009", useMathText=True, useOffset=offset,
    )
    axis.xaxis.set_major_formatter(formatter)
    reference = copy(formatter)
    reference.set_useMathText(False)
    expected = reference.format_ticks(values)
    expected_offset = reference.get_offset()
    with adapted_builtin_formatters(figure):
        adapter = axis.xaxis.get_major_formatter()
        assert list(map(_text, adapter.format_ticks(values))) == expected
        assert _text(adapter.get_offset()) == expected_offset
        assert formatter.get_useMathText() is True
    assert formatter.get_useMathText() is True


def _comma_locale(monkeypatch):
    conventions = locale.localeconv()
    conventions.update(decimal_point=",", thousands_sep="\u202f", grouping=[3, 0])
    monkeypatch.setattr(locale, "localeconv", lambda: conventions)


@pytest.mark.parametrize("mathtext", [False, True])
@pytest.mark.parametrize("values", [[1.25, 1.5, 1.75], [1_234_567.1, 1_234_567.2, 1_234_567.3]])
def test_scalar_locale_labels_and_scientific_offsets(axes, monkeypatch, mathtext, values):
    _comma_locale(monkeypatch)
    figure, axis = axes
    axis.set_xlim(values[0], values[-1])
    formatter = ticker.ScalarFormatter(useLocale=True, useMathText=mathtext)
    formatter.set_powerlimits((0, 0))
    axis.xaxis.set_major_formatter(formatter)
    reference = copy(formatter)
    reference.set_useMathText(False)
    expected = reference.format_ticks(values)
    expected_offset = reference.get_offset()
    with adapted_builtin_formatters(figure):
        adapter = axis.xaxis.get_major_formatter()
        assert list(map(_text, adapter.format_ticks(values))) == expected
        assert _text(adapter.get_offset()) == expected_offset
    assert formatter.get_useLocale() is True
    assert formatter.get_useMathText() is mathtext
    assert any("," in label for label in expected + [expected_offset])


def test_scalar_locale_preserves_grouping(axes, monkeypatch):
    _comma_locale(monkeypatch)
    figure, axis = axes
    axis.set_xlim(1234.5, 1235.5)
    formatter = ticker.ScalarFormatter(
        useLocale=True, useMathText=True, useOffset=False,
    )
    formatter.set_scientific(False)
    axis.xaxis.set_major_formatter(formatter)
    with adapted_builtin_formatters(figure):
        result = axis.xaxis.get_major_formatter().format_ticks([1234.5, 1235.5])
        assert list(map(_text, result)) == ["1\u202f234,5", "1\u202f235,5"]


class BatchFormatter(ticker.Formatter):
    def __call__(self, value, pos=None):
        return f"single_{value}"

    def format_ticks(self, values):
        self.set_locs(values)
        self.offset = f"batch_{len(values)}"
        return [f"${index}_{value}$" for index, value in enumerate(values)]

    def get_offset(self):
        return self.offset

    def _set_locator(self, locator):
        self.locator = locator


def test_custom_adapter_delegates_batch_context_and_coordinate_methods(axes):
    figure, axis = axes
    original = BatchFormatter()
    adapter = plotst.adapt_formatter(original)
    axis.xaxis.set_major_formatter(adapter)
    locator = ticker.FixedLocator([1, 2, 3])
    axis.xaxis.set_major_locator(locator)
    with adapted_builtin_formatters(figure):
        assert axis.xaxis.get_major_formatter() is adapter
        assert list(map(_text, adapter.format_ticks([1, 2, 3]))) == ["$0_1$", "$1_2$", "$2_3$"]
        assert _text(adapter.get_offset()) == "batch_3"
        assert _text(adapter(5)) == "single_5"
    assert original.axis is axis.xaxis
    assert original.locator is locator
    assert list(original._locs) == [1, 2, 3]
    adapter.set_locs([9])
    assert original._locs == [9]
    assert adapter.format_data(5) == adapter.format_data_short(5) == "single_5"


def test_custom_conversion_applies_to_ticks_and_offsets():
    adapter = plotst.adapt_formatter(BatchFormatter(), convert=lambda s: f"converted:{s}")
    assert adapter.format_ticks([2]) == ["converted:$0_2$"]
    assert adapter(2) == "converted:single_2"
    assert adapter.get_offset() == "converted:batch_1"


def test_unwrapped_custom_formatters_and_subclasses_are_unchanged(axes):
    figure, axis = axes

    class CustomScalar(ticker.ScalarFormatter):
        pass

    major = CustomScalar()
    minor = ticker.FuncFormatter(lambda x, pos: "$x^2$")
    axis.xaxis.set_major_formatter(major)
    axis.xaxis.set_minor_formatter(minor)
    with adapted_builtin_formatters(figure):
        assert axis.xaxis.get_major_formatter() is major
        assert axis.xaxis.get_minor_formatter() is minor


@pytest.mark.parametrize("fail", [False, True])
def test_restores_shared_axes_colorbars_and_default_flags(fail):
    figure, axes = plt.subplots(2, sharex=True)
    image = axes[0].imshow(np.arange(4).reshape(2, 2))
    figure.colorbar(image, ax=axes)
    axes[0].xaxis.set_minor_formatter(ticker.PercentFormatter())
    records = [
        (axis, kind, getattr(axis, f"get_{kind}_formatter")(), getattr(axis, f"isDefault_{kind[:3]}fmt"))
        for ax in figure.axes for axis in (ax.xaxis, ax.yaxis) for kind in ("major", "minor")
    ]
    bindings = [(original, original.axis) for _, _, original, _ in records]
    try:
        try:
            with adapted_builtin_formatters(figure):
                if fail:
                    raise RuntimeError("export failed")
        except RuntimeError:
            assert fail
        for axis, kind, original, default in records:
            assert getattr(axis, f"get_{kind}_formatter")() is original
            assert getattr(axis, f"isDefault_{kind[:3]}fmt") is default
        for original, original_axis in bindings:
            assert original.axis is original_axis
    finally:
        plt.close(figure)


def test_formatter_families_export_as_pdf(tmp_path: Path, monkeypatch):
    _comma_locale(monkeypatch)
    plotst.setup()
    figure, axes = plt.subplots(2, 3, figsize=(9, 5), layout="constrained")
    date_ax, category_ax, percent_ax, eng_ax, locale_ax, custom_ax = axes.flat
    times = [datetime(2026, 9, 28, 12) + timedelta(minutes=30 * i) for i in range(3)]
    date_ax.plot(times, [0, 1, 2])
    date_ax.xaxis.set_major_formatter(dates.ConciseDateFormatter(date_ax.xaxis.get_major_locator()))
    category_ax.bar(["a_b", "$cost$", "#tag\n[unit]"], [1, 2, 3])
    percent_ax.plot([0, 1], [0, 1])
    percent_ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    eng_ax.plot([0, 1], [1e9, 1e9 + 3000])
    eng_ax.yaxis.set_major_formatter(ticker.EngFormatter("Hz", useMathText=True, useOffset=True))
    locale_ax.plot([0, 1], [1.25, 1.75])
    locale_ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useLocale=True, useMathText=True))
    custom_ax.plot([0, 1], [0, 1])
    custom_ax.xaxis.set_major_locator(ticker.FixedLocator([0, 1]))
    custom_ax.xaxis.set_major_formatter(plotst.adapt_formatter(BatchFormatter()))
    destination = tmp_path / "formatters.pdf"
    original = date_ax.xaxis.get_major_formatter()
    try:
        plotst.savefig(figure, destination)
        assert date_ax.xaxis.get_major_formatter() is original
        extracted = PdfReader(destination).pages[0].extract_text()
        for text in ["a_b", "$cost$", "#tag", "[unit]", "%", "Hz", "1,", "batch_2", "2026"]:
            assert text in extracted
    finally:
        plt.close(figure)
