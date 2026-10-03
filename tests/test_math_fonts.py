from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from pypdf import PdfReader

import plotst


def _embedded_font_names(page) -> set[str]:
    names: set[str] = set()

    def collect(resources) -> None:
        for reference in resources.get("/Font", {}).values():
            names.add(str(reference.get_object().get("/BaseFont", "")))
        for reference in resources.get("/XObject", {}).values():
            child = reference.get_object()
            if child.get("/Subtype") == "/Form":
                collect(child.get("/Resources", {}))

    collect(page["/Resources"])
    return names


def test_configured_math_font_changes_the_embedded_math_font(
    tmp_path: Path,
) -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"
    available_fonts = subprocess.run(
        [typst, "fonts"], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.splitlines()
    alternatives = {"STIX Two Math": "STIXTwoMath", "Cambria Math": "CambriaMath"}
    alternate_font = next((name for name in alternatives if name in available_fonts), None)
    assert alternate_font is not None, "Install Cambria Math or STIX Two Math for this test"
    plotst.setup(
        font="New Computer Modern",
        math_font="New Computer Modern Math",
        typst=typst,
    )

    figure, axis = plt.subplots(figsize=(3.4, 2), layout="constrained")
    axis.plot([0, 1, 2], [0, 1, 0])
    axis.set_xlabel("Elapsed time $t$ (s)")
    axis.set_ylabel("Energy $E_0$")
    axis.set_title("Math $(sum_(k=1)^n k^2)/sqrt(alpha)$")

    results = {}
    try:
        for math_font in ("New Computer Modern Math", alternate_font):
            plotst.setup(
                font="New Computer Modern",
                math_font=math_font,
                typst=typst,
            )
            destination = tmp_path / f"{math_font.replace(' ', '-')}.pdf"
            plotst.savefig(figure, destination, tight_width_mm=85)
            page = PdfReader(destination).pages[0]
            results[math_font] = (
                _embedded_font_names(page),
                page.extract_text(),
                float(page.mediabox.width),
            )
    finally:
        plt.close(figure)

    computer_modern_fonts, computer_modern_text, computer_modern_width = results[
        "New Computer Modern Math"
    ]
    alternate_fonts, alternate_text, alternate_width = results[alternate_font]
    assert any("NewCMMath" in name for name in computer_modern_fonts)
    assert any(alternatives[alternate_font] in name for name in alternate_fonts)
    assert computer_modern_fonts != alternate_fonts
    assert "Elapsed time" in computer_modern_text
    assert "Elapsed time" in alternate_text
    assert abs(computer_modern_width - 85 / 25.4 * 72) < 0.01
    assert abs(alternate_width - 85 / 25.4 * 72) < 0.01
