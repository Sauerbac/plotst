from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import subprocess

import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from pypdf import PdfReader

from ._config import Config
from ._errors import TypstCompilationError


def _typst_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


@dataclass(frozen=True, slots=True)
class Style:
    family: str
    math_family: str
    size: float
    weight: int
    style: str


@dataclass(frozen=True, slots=True)
class LabelArtifact:
    key: str
    width: float
    height: float
    descent: float
    padding: float
    pdf: Path
    page_width: float
    page_height: float


class TypstCompiler:
    """Compile labels for one export and reuse identical artifacts within it."""

    def __init__(self, directory: Path, config: Config) -> None:
        self._directory = directory
        self._config = config
        self._artifacts: dict[str, LabelArtifact] = {}

    def style(self, properties: FontProperties) -> Style:
        weight = properties.get_weight()
        if isinstance(weight, str):
            weight = mpl.font_manager.weight_dict[weight]
        family = properties.get_family()[0]
        if family in ("sans-serif", "serif", "monospace"):
            raise TypstCompilationError(
                f"Plotst requires a concrete font family, not {family!r}. "
                "Call plotst.setup(font=...) before creating the figure."
            )
        return Style(
            family=family,
            math_family=self._config.math_font,
            size=properties.get_size_in_points(),
            weight=int(weight),
            style=properties.get_style(),
        )

    def label(
        self,
        source: str,
        style: Style,
        rgb: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> LabelArtifact:
        normalized_rgb = tuple(float(channel) for channel in rgb[:3])
        identity = {
            "source": source,
            "style": asdict(style),
            "typst": self._config.typst_version,
            "rgb": normalized_rgb,
        }
        key = hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode("utf-8")
        ).hexdigest()[:20]
        if key in self._artifacts:
            return self._artifacts[key]

        typ_path = self._directory / f"{key}.typ"
        pdf_path = typ_path.with_suffix(".pdf")
        padding = style.size
        color = ", ".join(f"{channel * 100:.8f}%" for channel in normalized_rgb)
        typ_path.write_text(
            f'''#set page(width: auto, height: auto, margin: {padding}pt)
#set text(font: {_typst_string(style.family)}, size: {style.size}pt, weight: {style.weight}, style: {_typst_string(style.style)}, top-edge: "bounds", bottom-edge: "bounds", fill: rgb({color}))
#show math.equation: set text(font: {_typst_string(style.math_family)})
#set par(leading: 0pt, spacing: 0pt)
#let body = eval({_typst_string(source)}, mode: "markup", scope: (:))
#context {{
  let b = box(body)
  let m = measure(b)
  [#metadata((width: m.width.pt(), height: m.height.pt())) <metrics>]
  box(width: 0pt, height: 0pt)[#metadata("baseline") <baseline>]
  b
}}
''',
            encoding="utf-8",
        )
        measured_result = self._run(
            [
                "eval",
                '(metrics: query(<metrics>).first().value, baseline: query(<baseline>).first().location().position().y.pt())',
                "--in",
                str(typ_path),
            ],
            source,
        )
        measured = json.loads(measured_result.stdout)
        self._run(["compile", str(typ_path), str(pdf_path)], source)

        reader = PdfReader(pdf_path)
        if len(reader.pages) != 1:
            raise TypstCompilationError(
                f"Typst label produced {len(reader.pages)} pages: {source!r}"
            )
        page = reader.pages[0]
        width = float(measured["metrics"]["width"])
        height = float(measured["metrics"]["height"])
        ascent = float(measured["baseline"]) - padding
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        artifact = LabelArtifact(
            key=key,
            width=width,
            height=height,
            descent=height - ascent,
            padding=padding,
            pdf=pdf_path,
            page_width=page_width,
            page_height=page_height,
        )
        if (
            abs(page_width - (width + 2 * padding)) > 1e-3
            or abs(page_height - (height + 2 * padding)) > 1e-3
        ):
            raise TypstCompilationError(
                f"Typst label geometry was changed by its measurement wrapper: {source!r}"
            )
        self._artifacts[key] = artifact
        return artifact

    def _run(self, arguments: list[str], source: str) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                [self._config.typst, *arguments],
                capture_output=True,
                check=True,
                encoding="utf-8",
                text=True,
            )
        except subprocess.CalledProcessError as error:
            details = error.stderr.strip() or error.stdout.strip() or str(error)
            raise TypstCompilationError(
                f"Typst could not process label {source!r}:\n{details}"
            ) from error
        if result.stderr.strip():
            raise TypstCompilationError(
                f"Typst reported a warning for label {source!r}:\n"
                f"{result.stderr.strip()}"
            )
        return result
