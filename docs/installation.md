# Installing Plotst

[Quick start](../README.md) · [Usage](usage.md) · [Support](support.md)

## Requirements

- Windows with Python 3.12, 3.13, or 3.14. Package metadata accepts Python 3.12
  and newer; future versions need verification before being considered supported.
- Typst 0.15.0 installed separately and available on `PATH`.
- Matplotlib 3.11.0 and pypdf 6.10.0 (installed with Plotst).
- New Computer Modern text and math fonts (included in the official Typst CLI).

Verified compiler builds are the official `typst 0.15.0 (3ae52774)` release and
the original local `typst 0.15.0 (c98e9103)` build. Other builds trigger a warning.
Windows is the current support target; macOS and Linux have not been verified.

## Install from GitHub

Install the Windows archive from [Typst 0.15.0](https://github.com/typst/typst/releases/tag/v0.15.0),
extract it, and add its directory to `PATH`. Verify it in a new PowerShell window:

```powershell
typst --version
```

With Python and Git installed, create an isolated environment and install Plotst:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install "plotst @ git+https://github.com/Sauerbac/plotst.git"
```

You can use `py -3.13` or `py -3.14` instead. Run your scripts with
`.\.venv\Scripts\python`. To reproduce an exact revision, append `@<commit-sha>`
to the Git URL. Plotst is distributed from this repository, not PyPI.

If you prefer not to install Git, download and extract the repository's ZIP,
then run `python -m pip install .` from its root in your Python environment.

To run the repository's demonstrations, follow the [examples guide](../examples/README.md).
