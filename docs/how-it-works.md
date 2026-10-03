# How PDF composition works

[Quick start](../README.md) · [Usage](usage.md) · [Support](support.md)

For each distinct label needed during one export, Plotst asks the Typst CLI for
its measurements and a small PDF containing that label. Matplotlib lays out and
draws the figure using those measurements. pypdf installs the label PDFs as Form
XObjects at the positions already recorded in Matplotlib's drawing stream. This
preserves the tested ordering, clipping, opacity, vector graphics, and PDF text.

The per-export artifact table is discarded after `savefig()` returns. There is
no persistent cache, cross-export cache, batching layer, or cache invalidation
system yet.
