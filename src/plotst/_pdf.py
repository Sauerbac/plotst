from __future__ import annotations

import io
import math
from pathlib import Path
from typing import BinaryIO

from matplotlib.backends.backend_pdf import (
    FigureCanvasPdf,
    Name,
    Op,
    PdfFile,
    RendererPdf,
    _get_link_annotation,
)
from matplotlib.backends.backend_mixed import MixedModeRenderer
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
)

from ._compiler import LabelArtifact, TypstCompiler


def _attach_forms(
    raw_pdf: BinaryIO,
    labels: dict[str, LabelArtifact],
    output: str | Path,
) -> None:
    writer = PdfWriter()
    writer.append(PdfReader(raw_pdf))
    page = writer.pages[0]
    resources = page["/Resources"].get_object()
    if "/XObject" not in resources:
        resources[NameObject("/XObject")] = DictionaryObject()
    xobjects = resources["/XObject"].get_object()

    for name, label in labels.items():
        source = PdfReader(label.pdf).pages[0]
        form = DecodedStreamObject()
        form.set_data(source.get_contents().get_data())
        form.update(
            {
                NameObject("/Type"): NameObject("/XObject"),
                NameObject("/Subtype"): NameObject("/Form"),
                NameObject("/BBox"): ArrayObject(
                    [
                        FloatObject(0),
                        FloatObject(0),
                        FloatObject(label.page_width),
                        FloatObject(label.page_height),
                    ]
                ),
                NameObject("/Resources"): source["/Resources"].clone(writer),
            }
        )
        if "/Group" in source:
            form[NameObject("/Group")] = source["/Group"].clone(writer)
        xobjects[NameObject(f"/{name}")] = writer._add_object(form)

    writer.add_metadata({"/Creator": "plotst"})
    with Path(output).open("wb") as stream:
        writer.write(stream)


class TypstRenderer(RendererPdf):
    def __init__(
        self,
        file: PdfFile,
        dpi: float,
        height: float,
        width: float,
        compiler: TypstCompiler,
    ) -> None:
        super().__init__(file, dpi, height, width)
        self.compiler = compiler
        self.labels: dict[str, LabelArtifact] = {}

    def get_text_width_height_descent(self, s, prop, ismath):
        label = self.compiler.label(s, self.compiler.style(prop))
        return label.width, label.height, label.descent

    def _get_font_height_metrics(self, prop):
        label = self.compiler.label("lp", self.compiler.style(prop))
        return label.height - label.descent, label.descent, 0.0

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        label = self.compiler.label(s, self.compiler.style(prop), gc.get_rgb()[:3])
        name = f"Typst{label.key}"
        self.labels[name] = label
        self.check_gc(gc, gc._rgb)
        theta = math.radians(angle)
        cosine, sine = math.cos(theta), math.sin(theta)
        dx = -label.padding
        dy = -label.descent - label.padding
        self.file.output(
            Op.gsave,
            cosine,
            sine,
            -sine,
            cosine,
            x + cosine * dx - sine * dy,
            y + sine * dx + cosine * dy,
            Op.concat_matrix,
            Name(name),
            Op.use_xobject,
            Op.grestore,
        )
        if gc.get_url() is not None:
            bottom_x = x + sine * label.descent
            bottom_y = y - cosine * label.descent
            self.file._annotations[-1][1].append(
                _get_link_annotation(
                    gc,
                    bottom_x,
                    bottom_y,
                    label.width,
                    label.height,
                    angle,
                )
            )

    def draw_tex(self, *args, **kwargs):
        raise ValueError("Plotst requires text.usetex=False")


class TypstCanvas(FigureCanvasPdf):
    def __init__(self, figure, compiler: TypstCompiler) -> None:
        super().__init__(figure)
        self.compiler = compiler

    def print_pdf(
        self,
        filename,
        *,
        bbox_inches_restore=None,
        metadata=None,
        **kwargs,
    ) -> None:
        original_dpi = self.figure.dpi
        self.figure.dpi = 72
        width, height = self.figure.get_size_inches()
        raw = io.BytesIO()
        file = PdfFile(raw, metadata=metadata)
        renderer: TypstRenderer | None = None
        try:
            file.newPage(width, height)
            renderer = TypstRenderer(file, original_dpi, height, width, self.compiler)
            mixed_renderer = MixedModeRenderer(
                self.figure,
                width,
                height,
                original_dpi,
                renderer,
                bbox_inches_restore=bbox_inches_restore,
            )
            self.figure.draw(mixed_renderer)
            mixed_renderer.finalize()
            file.finalize()
        finally:
            file.close()
            # FigureCanvasBase.print_figure owns DPI restoration. Keep the
            # figure at 72 dpi during its preflight layout draw, as the PDF
            # renderer's text metrics and canvas coordinates are in points.
        if renderer is None:
            raise RuntimeError("Plotst PDF renderer was not created")
        raw.seek(0)
        _attach_forms(raw, renderer.labels, filename)
