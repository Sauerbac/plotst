from __future__ import annotations

from pathlib import Path
import shutil

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
import pytest

import plotst


def _typst() -> str:
    executable = shutil.which("typst")
    assert executable is not None, "The integration test requires Typst on PATH"
    return executable


def test_savefig_reports_the_label_when_typst_source_is_invalid(
    tmp_path: Path,
) -> None:
    plotst.setup(typst=_typst())
    figure, axis = plt.subplots(figsize=(2, 1))
    axis.set_title("$frac($")
    formatter = axis.xaxis.get_major_formatter()

    try:
        with pytest.raises(
            plotst.TypstCompilationError,
            match=r"Typst could not process label '\$frac\(\$'",
        ):
            plotst.savefig(figure, tmp_path / "invalid.pdf")
        assert axis.xaxis.get_major_formatter() is formatter
    finally:
        plt.close(figure)


def test_savefig_rejects_typst_font_substitution(tmp_path: Path) -> None:
    missing_font = "Definitely Missing Typst Font 1234"
    plotst.setup(font=missing_font, typst=_typst())
    figure, axis = plt.subplots(figsize=(2, 1))
    axis.set_title("Font must not silently change")

    try:
        with pytest.raises(
            plotst.TypstCompilationError,
            match="Typst reported a warning",
        ):
            plotst.savefig(figure, tmp_path / "missing-font.pdf")
    finally:
        plt.close(figure)


def test_savefig_rejects_rasterized_text(tmp_path: Path) -> None:
    plotst.setup(typst=_typst())
    figure = plt.figure(figsize=(2, 1))
    figure.text(0.5, 0.5, "Must remain Typst text", rasterized=True)

    try:
        with pytest.raises(plotst.PlotstError, match="Rasterized text"):
            plotst.savefig(figure, tmp_path / "rasterized-text.pdf")
    finally:
        plt.close(figure)
