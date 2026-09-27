from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from PIL import Image, ImageChops
from pypdf import PdfReader
import pytest

import plotst


def test_tight_export_fits_all_labels_at_exact_column_width(
    tmp_path: Path,
) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    plotst.setup(typst=typst)

    figure, axis = plt.subplots(figsize=(4.5, 2.7), layout="constrained")
    axis.plot([0, 1, 2], [0, 1, 0], label="Response $f(t)$")
    axis.set_xlabel("Elapsed time $t$ (s)")
    axis.set_ylabel("Measured response $frac(y, y_0)$")
    axis.set_title("A publication column figure")
    axis.legend()
    original_size = figure.get_size_inches().copy()
    original_canvas = figure.canvas
    destination = tmp_path / "column.pdf"

    try:
        plotst.savefig(figure, destination, tight_width_mm=85)
        assert figure.get_size_inches() == pytest.approx(original_size)
        assert figure.canvas is original_canvas
    finally:
        plt.close(figure)

    page = PdfReader(destination).pages[0]
    assert float(page.mediabox.width) == pytest.approx(85 / 25.4 * 72, abs=0.01)
    assert float(page.mediabox.width) < original_size[0] * 72
    extracted = page.extract_text()
    assert "A publication column figure" in extracted
    assert "Elapsed time" in extracted
    assert "Measured response" in extracted
    assert "Response" in extracted

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is not None:
        preview = tmp_path / "column-preview"
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
            assert max(
                left / rgb.width,
                top / rgb.height,
                (rgb.width - right) / rgb.width,
                (rgb.height - bottom) / rgb.height,
            ) < 0.06


@pytest.mark.parametrize("width", [0, -1, float("nan"), float("inf")])
def test_tight_export_rejects_invalid_width(tmp_path: Path, width: float) -> None:
    figure = plt.figure()
    try:
        with pytest.raises(ValueError, match="finite positive"):
            plotst.savefig(figure, tmp_path / "invalid.pdf", tight_width_mm=width)
    finally:
        plt.close(figure)
