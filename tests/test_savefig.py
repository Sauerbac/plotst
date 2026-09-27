from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from PIL import Image, ImageChops
from pypdf import PdfReader
import pytest

import plotst


def test_constrained_layout_keeps_labels_inside_fixed_page(tmp_path: Path) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        pytest.skip("The page-edge check requires pdftoppm on PATH")
    plotst.setup(typst=typst)

    figure, axis = plt.subplots(
        figsize=(120 / 25.4, 80 / 25.4), layout="constrained"
    )
    axis.plot([0, 0.5, 1, 1.5, 2], [0, 0.25, 1, 2.25, 4])
    axis.set_xlabel("Time $t$ (s)")
    axis.set_ylabel("Normalized response $frac(y, y_0)$")
    axis.set_title("Typst measured figure", fontsize=12, fontweight="bold")
    destination = tmp_path / "fixed-page.pdf"

    try:
        plotst.savefig(figure, destination)
    finally:
        plt.close(figure)

    preview = tmp_path / "fixed-page"
    subprocess.run(
        [pdftoppm, "-singlefile", "-png", "-r", "144", str(destination), str(preview)],
        check=True,
        capture_output=True,
    )
    with Image.open(preview.with_suffix(".png")) as rendered:
        rgb = rendered.convert("RGB")
        ink = ImageChops.difference(
            rgb, Image.new("RGB", rgb.size, "white")
        ).getbbox()
        assert ink is not None
        left, top, right, bottom = ink
        assert left > 0 and top > 0
        assert right < rgb.width and bottom < rgb.height


def test_savefig_writes_exact_size_pdf_with_typst_text(tmp_path: Path) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    plotst.setup(typst=typst)

    figure, axis = plt.subplots(
        figsize=(120 / 25.4, 80 / 25.4),
        layout="constrained",
    )
    axis.plot([0, 1, 2], [0, 1, 4], label="Response $x^2$")
    axis.set_xlabel("Time $t$")
    axis.set_ylabel("Measured value")
    axis.set_title("Plotst first figure", fontsize=12, fontweight="bold")
    axis.legend()
    destination = tmp_path / "ordinary.pdf"
    original_dpi = figure.dpi

    try:
        plotst.savefig(figure, destination)
        assert figure.dpi == original_dpi
    finally:
        plt.close(figure)

    page = PdfReader(destination).pages[0]
    assert float(page.mediabox.width) == pytest.approx(120 / 25.4 * 72)
    assert float(page.mediabox.height) == pytest.approx(80 / 25.4 * 72)
    assert "Plotst first figure" in page.extract_text()


def test_savefig_adapts_generated_log_and_scientific_labels(
    tmp_path: Path,
) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    plotst.setup(typst=typst)

    figure, (log_axis, scientific_axis) = plt.subplots(1, 2, figsize=(6, 2))
    log_axis.set_xscale("log")
    log_axis.set_xlim(1e-3, 1e3)
    log_axis.plot([1e-3, 1, 1e3], [0, 1, 2])

    scientific_axis.plot(
        [1_000_000, 1_000_001, 1_000_002],
        [0, 1, 2],
    )
    scientific_formatter = scientific_axis.xaxis.get_major_formatter()
    scientific_formatter.set_useMathText(True)
    scientific_formatter.set_powerlimits((0, 0))
    custom_formatter = FuncFormatter(
        lambda value, position: (
            "#text(fill: red)[Custom tick]" if value == 1 else ""
        )
    )
    scientific_axis.yaxis.set_major_formatter(custom_formatter)

    log_formatter = log_axis.xaxis.get_major_formatter()
    destination = tmp_path / "generated-labels.pdf"

    try:
        plotst.savefig(figure, destination)
    finally:
        plt.close(figure)

    assert log_axis.xaxis.get_major_formatter() is log_formatter
    assert scientific_axis.xaxis.get_major_formatter() is scientific_formatter
    assert scientific_axis.yaxis.get_major_formatter() is custom_formatter
    extracted = PdfReader(destination).pages[0].extract_text()
    assert "10" in extracted
    assert "−" in extracted
    assert "+" in extracted
    assert "Custom tick" in extracted


def test_savefig_supports_rasterized_artists_with_typst_text(
    tmp_path: Path,
) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    plotst.setup(typst=typst)

    figure, axis = plt.subplots(figsize=(3, 2), dpi=144)
    points = axis.scatter(
        range(40),
        [(value % 7) / 7 for value in range(40)],
        c=range(40),
        rasterized=True,
    )
    axis.set_title("Vector Typst title")
    colorbar = figure.colorbar(points, ax=axis)
    colorbar.set_label("Scale $s$")
    destination = tmp_path / "mixed-mode.pdf"

    try:
        plotst.savefig(figure, destination)
    finally:
        plt.close(figure)

    page = PdfReader(destination).pages[0]
    xobjects = page["/Resources"]["/XObject"].get_object()
    subtypes = {item.get_object()["/Subtype"] for item in xobjects.values()}
    assert "/Image" in subtypes
    assert "/Form" in subtypes
    assert "Vector Typst title" in page.extract_text()
    assert "Scale" in page.extract_text()
