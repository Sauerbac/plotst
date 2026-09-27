from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
from pypdf import PdfReader
from pypdf.generic import ContentStream
import pytest

import plotst


def _preceding_matrix(operations, index: int) -> list[float]:
    for operands, operator in reversed(operations[:index]):
        if operator == b"cm":
            return [float(value) for value in operands]
    raise AssertionError("Form invocation did not have a preceding matrix")


def test_pdf_preserves_text_geometry_and_drawing_state(tmp_path: Path) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    plotst.setup(typst=typst)

    figure = plt.figure(figsize=(3, 2))
    figure.text(0.5, 0.55, "Layer label", ha="left", zorder=1)
    figure.add_artist(
        Rectangle(
            (0.35, 0.45),
            0.3,
            0.2,
            transform=figure.transFigure,
            facecolor="white",
            edgecolor="none",
            zorder=2,
        )
    )
    clipped = figure.text(
        0.5,
        0.55,
        "Layer label",
        ha="right",
        alpha=0.35,
        clip_on=True,
        zorder=3,
    )
    clipped.set_clip_box(Bbox.from_bounds(90, 60, 40, 40))
    figure.text(
        0.72,
        0.2,
        "Rotated",
        rotation=30,
        url="https://example.com/plotst",
        zorder=4,
    )
    figure.text(0.05, 0.9, "First line\nSecond line", zorder=4)
    figure.text(
        0.05,
        0.08,
        "$frac(sum_(i=1)^n i, sqrt(x))$",
        fontsize=16,
        fontweight="bold",
        zorder=4,
    )
    destination = tmp_path / "composition.pdf"

    try:
        plotst.savefig(figure, destination)
    finally:
        plt.close(figure)

    reader = PdfReader(destination)
    page = reader.pages[0]
    operations = ContentStream(page.get_contents(), reader).operations
    form_uses = [
        (index, str(operands[0]))
        for index, (operands, operator) in enumerate(operations)
        if operator == b"Do" and str(operands[0]).startswith("/Typst")
    ]
    counts = Counter(name for _, name in form_uses)
    repeated_name = next(name for name, count in counts.items() if count == 2)
    repeated_uses = [item for item in form_uses if item[1] == repeated_name]

    first_index, _ = repeated_uses[0]
    second_index, _ = repeated_uses[1]
    first_matrix = _preceding_matrix(operations, first_index)
    second_matrix = _preceding_matrix(operations, second_index)
    xobjects = page["/Resources"]["/XObject"].get_object()
    form = xobjects[repeated_name].get_object()
    label_width = float(form["/BBox"][2]) - 20
    form_heights = [
        float(item.get_object()["/BBox"][3])
        for item in xobjects.values()
        if item.get_object()["/Subtype"] == "/Form"
    ]

    assert abs(first_matrix[4] - second_matrix[4]) == pytest.approx(
        label_width,
        abs=1e-3,
    )
    assert max(form_heights) > 3 * 16
    between_layers = {
        operator for _, operator in operations[first_index + 1 : second_index]
    }
    assert between_layers.intersection({b"f", b"f*", b"B", b"B*"})
    assert b"W" in between_layers or b"W*" in between_layers

    ext_gstates = page["/Resources"]["/ExtGState"].get_object().values()
    assert any(
        float(state.get_object().get("/ca", 1)) == pytest.approx(0.35)
        for state in ext_gstates
    )

    matrices = [
        [float(value) for value in operands]
        for operands, operator in operations
        if operator == b"cm"
    ]
    assert any(
        matrix[0] == pytest.approx(math.cos(math.radians(30)), abs=1e-6)
        and matrix[1] == pytest.approx(math.sin(math.radians(30)), abs=1e-6)
        for matrix in matrices
    )

    extracted = page.extract_text()
    assert "Layer label" in extracted
    assert "Rotated" in extracted
    assert "First line" in extracted
    assert "Second line" in extracted

    annotations = [
        annotation.get_object() for annotation in page["/Annots"].get_object()
    ]
    link = next(
        annotation
        for annotation in annotations
        if annotation.get("/A", {}).get("/URI")
        == "https://example.com/plotst"
    )
    assert "/QuadPoints" in link
    assert float(link["/Rect"][2]) > float(link["/Rect"][0])
    assert float(link["/Rect"][3]) > float(link["/Rect"][1])
