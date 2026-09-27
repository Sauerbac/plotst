from __future__ import annotations

import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from pypdf import PdfReader

from matplotlib.figure import Figure
from matplotlib.text import Text

from ._compiler import TypstCompiler
from ._config import active_config
from ._errors import UnsupportedFeatureError
from ._formatters import adapted_builtin_formatters
from ._pdf import TypstCanvas


def _reject_rasterized_text(figure: Figure) -> None:
    for artist in figure.findobj():
        if artist.get_rasterized() and any(
            isinstance(descendant, Text) for descendant in artist.findobj()
        ):
            raise UnsupportedFeatureError(
                "Rasterized text is not supported because it bypasses Typst. "
                "Rasterize only artists that do not contain text."
            )


def savefig(
    figure: Figure,
    filename: str | os.PathLike[str],
    *,
    tight_width_mm: float | None = None,
) -> None:
    """Save a PDF, optionally trimming it to a specified final width in mm.

    ``tight_width_mm`` crops around the figure content with a small edge
    allowance, then adjusts the plotting width until the PDF page matches the
    requested physical width. Font sizes remain unchanged.
    """
    destination = Path(filename)
    if destination.suffix.lower() != ".pdf":
        raise ValueError("Plotst currently supports PDF output only.")
    if tight_width_mm is not None and (
        not math.isfinite(tight_width_mm) or tight_width_mm <= 0
    ):
        raise ValueError("tight_width_mm must be a finite positive number.")

    config = active_config()
    _reject_rasterized_text(figure)
    original_canvas = figure.canvas
    original_size = figure.get_size_inches().copy()
    # The final tight PDF is renamed atomically; keep it on the output drive.
    with TemporaryDirectory(prefix="plotst-", dir=destination.parent) as temporary:
        compiler = TypstCompiler(Path(temporary), config)
        canvas = TypstCanvas(figure, compiler)
        try:
            with adapted_builtin_formatters(figure):
                if tight_width_mm is None:
                    canvas.print_figure(destination, format="pdf")
                else:
                    target_width = tight_width_mm / 25.4
                    trial_width = float(original_size[0])
                    trial = Path(temporary) / "trial.pdf"
                    for _ in range(6):
                        figure.set_size_inches(
                            trial_width, float(original_size[1]), forward=False
                        )
                        canvas.print_figure(
                            trial,
                            format="pdf",
                            bbox_inches="tight",
                            pad_inches=0.05,
                        )
                        page = PdfReader(trial).pages[0]
                        actual_width = float(page.mediabox.width) / 72
                        if abs(actual_width - target_width) < 1e-4:
                            trial.replace(destination)
                            break
                        trial_width += target_width - actual_width
                        if trial_width <= 0:
                            raise ValueError(
                                "The requested tight width is too small for "
                                "this figure's labels and fonts."
                            )
                    else:
                        raise RuntimeError(
                            "Could not fit the tightly cropped figure to "
                            f"{tight_width_mm} mm without scaling its text."
                        )
        finally:
            figure.set_size_inches(original_size, forward=False)
            figure.set_canvas(original_canvas)
