from __future__ import annotations

from dataclasses import dataclass
import subprocess
import warnings

import matplotlib as mpl

from ._errors import TypstNotFoundError
from ._warnings import UntestedTypstWarning


_TESTED_TYPST = "typst 0.15.0 (c98e9103)"


@dataclass(frozen=True, slots=True)
class Config:
    font: str
    math_font: str
    font_size: float
    font_weight: str | int
    typst: str
    typst_version: str


_active_config: Config | None = None


def setup(
    *,
    font: str = "New Computer Modern",
    math_font: str = "New Computer Modern Math",
    font_size: float = 10,
    font_weight: str | int = "normal",
    typst: str = "typst",
) -> None:
    """Configure Plotst and Matplotlib defaults for subsequently created text."""
    try:
        result = subprocess.run(
            [typst, "--version"],
            capture_output=True,
            check=True,
            encoding="utf-8",
            text=True,
        )
    except FileNotFoundError as error:
        raise TypstNotFoundError(
            f"Typst executable was not found at {typst!r}. "
            "Install Typst or pass its path to plotst.setup(typst=...)."
        ) from error
    typst_version = result.stdout.strip()
    if typst_version != _TESTED_TYPST:
        warnings.warn(
            f"Plotst is tested with {_TESTED_TYPST}; the configured executable "
            f"reports {typst_version!r}.",
            UntestedTypstWarning,
            stacklevel=2,
        )
    config = Config(
        font=font,
        math_font=math_font,
        font_size=float(font_size),
        font_weight=font_weight,
        typst=typst,
        typst_version=typst_version,
    )

    mpl.rcParams.update(
        {
            "font.family": [font],
            "font.size": font_size,
            "font.weight": font_weight,
            "axes.labelweight": font_weight,
            "axes.titleweight": font_weight,
            "text.parse_math": False,
            "text.usetex": False,
            "axes.formatter.use_mathtext": False,
        }
    )

    global _active_config
    _active_config = config


def active_config() -> Config:
    if _active_config is None:
        raise RuntimeError("Call plotst.setup() before plotst.savefig().")
    return _active_config
