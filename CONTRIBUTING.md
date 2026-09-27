# Working on Plotst

Use Windows, Python 3.12-3.14, Typst 0.15.0, and
[uv](https://docs.astral.sh/uv/getting-started/installation/).
The repository defaults to Python 3.12. To choose another version, add
`--python 3.13` or `--python 3.14` to `uv sync` and `uv run`.

## Test prerequisites

The official Typst CLI includes New Computer Modern text and math fonts.
The math-font regression test also needs either Windows' Cambria Math or
[STIX Two Math](https://github.com/stipub/stixfonts/releases/tag/v2.13b171).
Extract STIX fonts into a directory and set `TYPST_FONT_PATHS` to that directory
if you do not want to install them system-wide. `typst fonts` lists available fonts.

Install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
and put its `Library/bin` directory on `PATH` for visual assertions and gallery
previews. Without `pdftoppm`, local tests omit visual checks; CI requires it.

```powershell
uv sync --locked
uv run pytest
uv build
```

The CI matrix runs tests, all three example scripts, package builds, and a fresh
wheel-installation smoke test on Windows with Python 3.12, 3.13, and 3.14.
It uploads PDFs and build files as temporary workflow artifacts. It does not
publish packages or deploy a website.

## Refresh the gallery

```powershell
uv run python examples/ordinary.py
uv run python examples/column_width.py
uv run python examples/representative_figures.py
uv run python scripts/update_gallery.py
```

Review the six previews in `docs/gallery/` before committing them. The script
copies only the curated PDFs from ignored `output/pdf/` and renders PNG previews
with Poppler. It does not change the example designs or copy experimental evidence.

## Changes

Keep runtime code under `src/plotst/`, runnable demonstrations under `examples/`,
and focused regression tests under `tests/`. Update the README or support matrix
when changing the supported surface. Matplotlib and pypdf are pinned because
Plotst uses PDF renderer internals; dependency upgrades need the full test suite
and visual review of the gallery.
