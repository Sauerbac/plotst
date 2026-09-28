"""Common Matplotlib formatters, exported without rewriting their labels.

Run with ``uv run python examples/formatter_compatibility.py``. To reproduce
the gallery's decimal commas on Windows, append ``--locale de-DE``. Locale
selection belongs to this example application, not to Plotst.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import locale
from pathlib import Path

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib import dates, ticker
from matplotlib.figure import Figure
import numpy as np

import plotst


ROOT = Path(__file__).resolve().parents[1]
INK = "#17324d"
BLUE = "#2878b5"
TEAL = "#208c89"


class SampleFormatter(ticker.Formatter):
    """A custom subclass whose shared offset depends on the whole tick batch."""

    def __init__(self) -> None:
        self.count = 0

    def __call__(self, value, pos=None) -> str:
        return f"sample_{int(value):02d}"

    def format_ticks(self, values) -> list[str]:
        self.count = len(values)
        return super().format_ticks(values)

    def get_offset(self) -> str:
        return f"{self.count} samples"


def colored_text(label: str) -> str:
    """Example conversion hook: completed strings become colored Typst text."""
    if not label:
        return ""
    return f'#text(fill: rgb("{TEAL}"), {json.dumps(label, ensure_ascii=False)})'


def formatter_compatibility() -> Figure:
    """Build six panels using built-ins, a custom subclass, and a callback."""
    figure, axes = plt.subplots(
        2, 3, figsize=(210 / 25.4, 140 / 25.4), layout="constrained",
    )
    figure.suptitle("Familiar formatters, Typst typography", fontsize=15, color=INK)
    date_ax, category_ax, percent_ax, eng_ax, locale_ax, custom_ax = axes.flat
    for axis, title in zip(axes.flat, [
        "Dates across midnight", "Dataset categories", "Percentages",
        "Engineering units", "Locale-aware numbers", "Custom instrument labels",
    ]):
        axis.set_title(title, loc="left", fontsize=10, fontweight="bold", color=INK)
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#d8e1e8", linewidth=0.6)
        axis.set_axisbelow(True)
        axis.tick_params(labelsize=8)

    # The concise formatter chooses both labels and a shared date offset.
    start = datetime(2026, 9, 28, 23, tzinfo=timezone.utc)
    times = [start + timedelta(minutes=30 * index) for index in range(7)]
    date_ax.plot(times, [18, 19, 22, 21, 24, 26, 25], color=BLUE, marker="o", ms=3)
    locator = dates.HourLocator(tz=timezone.utc)
    date_ax.xaxis.set_major_locator(locator)
    date_ax.xaxis.set_major_formatter(dates.ConciseDateFormatter(locator, tz=timezone.utc))
    date_ax.set_xlabel("Time (UTC)", labelpad=18)
    date_ax.set_ylabel("Temperature (°C)")

    # Underscores, dollar signs, hashes, and brackets belong to the dataset.
    category_ax.bar(["run_01", "$control$", "#batch\n[B]"], [7, 9, 6], color=[BLUE, TEAL, BLUE])
    category_ax.set_ylabel("Response (a.u.)")

    progress = np.linspace(0, 1, 40)
    percent_ax.plot(progress, 1 - np.exp(-4 * progress), color=TEAL, linewidth=2)
    percent_ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    percent_ax.set_ylim(0, 1)
    percent_ax.set_xlabel("Elapsed time (s)")
    percent_ax.set_ylabel("Conversion")

    # Offset notation and SI prefixes come from EngFormatter, including GHz.
    eng_ax.plot([0, 1, 2, 3, 4], 1e9 + np.array([0, 600, 1100, 900, 1400]), color=BLUE, marker="o", ms=3)
    eng_ax.yaxis.set_major_formatter(ticker.EngFormatter("Hz", useOffset=True, useMathText=True))
    eng_ax.set_xlabel("Elapsed time (s)")
    eng_ax.set_ylabel("Frequency")

    # This follows the application's current LC_NUMERIC setting. Plotst does
    # not select a locale; --locale below is an explicit application choice.
    locale_ax.plot([0, 1, 2, 3], [1234.5, 1235.2, 1235.0, 1235.5], color=TEAL, marker="o", ms=3)
    formatter = ticker.ScalarFormatter(useLocale=True, useOffset=False, useMathText=True)
    formatter.set_scientific(False)
    locale_ax.yaxis.set_major_formatter(formatter)
    locale_ax.yaxis.set_major_locator(ticker.FixedLocator([1234.5, 1235.0, 1235.5]))
    locale_ax.set_xlabel("Elapsed time (s)")
    locale_ax.set_ylabel("Measured mass (g)")

    # Wrapping is explicit. Existing unwrapped custom formatters are unchanged.
    custom_ax.plot([1, 2, 3], [2, 4, 3], color=BLUE, marker="o", ms=4)
    custom_ax.xaxis.set_major_locator(ticker.FixedLocator([1, 2, 3]))
    custom_ax.xaxis.set_major_formatter(plotst.adapt_formatter(SampleFormatter()))
    custom_ax.yaxis.set_major_locator(ticker.FixedLocator([2, 3, 4]))
    custom_ax.yaxis.set_major_formatter(plotst.adapt_formatter(
        ticker.FuncFormatter(lambda value, pos: f"{value:g} mV"),
        convert=colored_text,
    ))
    return figure


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", help="LC_NUMERIC locale installed on this machine, e.g. de-DE on Windows")
    arguments = parser.parse_args()
    previous_locale = locale.setlocale(locale.LC_NUMERIC)
    try:
        if arguments.locale:
            try:
                locale.setlocale(locale.LC_NUMERIC, arguments.locale)
            except locale.Error as error:
                parser.error(f"Locale {arguments.locale!r} is unavailable: {error}")
        plotst.setup(font_size=9)
        destination = ROOT / "output" / "pdf" / "formatter-compatibility.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        figure = formatter_compatibility()
        try:
            plotst.savefig(figure, destination)
        finally:
            plt.close(figure)
        print(f"{destination} (LC_NUMERIC={locale.setlocale(locale.LC_NUMERIC)})")
    finally:
        locale.setlocale(locale.LC_NUMERIC, previous_locale)


if __name__ == "__main__":
    main()
