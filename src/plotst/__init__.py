"""Typst typography for Matplotlib PDF figures."""

from ._config import setup
from ._errors import (
    PlotstError,
    TypstCompilationError,
    TypstNotFoundError,
    UnsupportedFeatureError,
)
from ._savefig import savefig
from ._formatters import adapt_formatter
from ._warnings import UntestedTypstWarning

__all__ = [
    "PlotstError",
    "TypstCompilationError",
    "TypstNotFoundError",
    "UntestedTypstWarning",
    "UnsupportedFeatureError",
    "adapt_formatter",
    "savefig",
    "setup",
]
