"""Copy curated example PDFs and render their GitHub previews with Poppler."""

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FIGURES = (
    "plotst-ordinary",
    "plotst-column-85mm",
    "representative-log-scientific-colorbar",
    "representative-mixed-vector-raster",
    "representative-annotations",
    "representative-typst-math",
    "showcase-wave-interference",
    "showcase-monkey-saddle",
    "showcase-three-body-hs273",
)


def main() -> None:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise SystemExit("Install Poppler and add pdftoppm to PATH first.")
    source = ROOT / "output" / "pdf"
    missing = [name for name in FIGURES if not (source / f"{name}.pdf").is_file()]
    if missing:
        raise SystemExit("Run all example scripts first. Missing: " + ", ".join(missing))
    gallery = ROOT / "docs" / "gallery"
    gallery.mkdir(parents=True, exist_ok=True)
    for name in FIGURES:
        pdf = gallery / f"{name}.pdf"
        shutil.copy2(source / pdf.name, pdf)
        subprocess.run(
            [renderer, "-singlefile", "-png", "-r", "180", str(pdf), str(gallery / name)],
            check=True,
        )
        print(pdf.name)


if __name__ == "__main__":
    main()
