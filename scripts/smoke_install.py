"""Exercise an installed wheel from an isolated interpreter (python -I)."""

from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib

matplotlib.use("pdf")

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pypdf import PdfReader

import plotst


def main() -> None:
    package_path = Path(plotst.__file__).resolve()
    assert "site-packages" in package_path.parts, package_path
    plotst.setup()
    figure, axis = plt.subplots(figsize=(3, 2), layout="constrained")
    axis.bar(["run_01", "$control$", "run_03"], [0.2, 0.6, 0.9])
    axis.yaxis.set_major_formatter(
        plotst.adapt_formatter(PercentFormatter(xmax=1))
    )
    axis.set_title("Installed Plotst $x^2$")
    try:
        with TemporaryDirectory(prefix="plotst-smoke-") as directory:
            destination = Path(directory) / "figure.pdf"
            plotst.savefig(figure, destination)
            page = PdfReader(destination).pages[0]
            assert "Installed Plotst" in page.extract_text()
            for label in ("run_01", "$control$", "%"):
                assert label in page.extract_text()
            assert abs(float(page.mediabox.width) - 216) < 0.01
            assert abs(float(page.mediabox.height) - 144) < 0.01
    finally:
        plt.close(figure)
    print(f"Installed plotst {version('plotst')} exported a verified PDF.")


if __name__ == "__main__":
    main()
