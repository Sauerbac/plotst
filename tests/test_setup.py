from __future__ import annotations

import os
import shutil
from pathlib import Path

from matplotlib.text import Text
import pytest

import plotst


def test_setup_configures_new_matplotlib_text() -> None:
    typst = shutil.which("typst")
    assert typst is not None, "The integration test requires Typst on PATH"

    plotst.setup(
        font="New Computer Modern",
        math_font="New Computer Modern Math",
        font_size=11,
        font_weight="bold",
        typst=typst,
    )

    text = Text(text="Configured after setup")
    assert text.get_fontfamily() == ["New Computer Modern"]
    assert text.get_fontsize() == 11
    assert text.get_fontweight() == "bold"


def test_setup_explains_when_typst_is_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing-typst"

    with pytest.raises(
        plotst.TypstNotFoundError,
        match="Typst executable was not found",
    ):
        plotst.setup(typst=str(missing))


def test_setup_warns_for_an_untested_typst_build(tmp_path: Path) -> None:
    if os.name == "nt":
        executable = tmp_path / "typst-other.cmd"
        executable.write_text(
            "@echo off\r\necho typst 0.15.0 ^(different-build^)\r\n",
            encoding="utf-8",
        )
    else:
        executable = tmp_path / "typst-other"
        executable.write_text(
            "#!/bin/sh\nprintf 'typst 0.15.0 (different-build)\\n'\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)

    with pytest.warns(
        plotst.UntestedTypstWarning,
        match=r"tested with typst 0.15.0 \(c98e9103\)",
    ):
        plotst.setup(typst=str(executable))
