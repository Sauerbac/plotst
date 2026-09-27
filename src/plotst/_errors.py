class PlotstError(RuntimeError):
    """Base exception for Plotst failures."""


class TypstNotFoundError(PlotstError):
    """Raised when the configured Typst executable cannot be started."""


class TypstCompilationError(PlotstError):
    """Raised when Typst cannot produce a valid label artifact."""


class UnsupportedFeatureError(PlotstError):
    """Raised when a requested Matplotlib feature would bypass Plotst."""
