# Plotst roadmap and ideas

Captured from the product discussion on 2026-09-27. This is a prioritized set of proposals, not a description of features already implemented or a committed release schedule.

The immediate priorities are **shipping Typst with the installation**, **explicit helpers for literal text and Typst content**, and **broader tick-formatter compatibility**. The latter interprets the discussion's “broader compatibility” preference as support for more ordinary Matplotlib-generated labels and formatters.

Implementation update (2026-09-28): rank 3's formatter expansion is implemented,
with a [runnable gallery example](gallery/README.md#common-matplotlib-formatters).
It includes dates, categories, percentages, engineering units, existing locale
settings, and an explicit adapter for custom formatters/subclasses. This work
was deliberately separated from rank 2: general label helpers and string
defaults remain undecided. See the [support matrix](support.md) for the exact
implemented boundaries; the rankings below retain the original proposal.

## API freedom during early development

**Backward compatibility is not a requirement at this stage. Plotst has no current users to preserve compatibility for, and substantial API changes are welcome for the foreseeable early-development period.**

- Functions, signatures, defaults, configuration models, and label interpretation may change substantially or be removed.
- Prefer a clear, coherent end-user API over preserving the existing `setup()` / `savefig()` design or adding compatibility layers.
- Deprecation periods, legacy aliases, and migration shims are not required. Update the examples, documentation, and tests to the chosen API.
- In particular, explicit label helpers may come with a new default interpretation of strings; preserving today's implicit Typst-markup behavior is not a constraint.
- Tests should preserve intended rendering correctness and user-facing guarantees, not freeze incidental API decisions.
- Introduce a compatibility commitment deliberately when external adoption or a stable release warrants it. Do not assume such a commitment already exists.

This freedom concerns **Plotst's own API**. Testing compatibility with specific Typst, Matplotlib, and pypdf versions still matters: the compiler and rendering stack must produce correct, reproducible figures.

## Prioritized additions and changes

Ranking combines the user's stated preferences, everyday usefulness, adoption benefit, and likely effort. Effort is relative, not a time estimate. Proposed API names are illustrative and may change freely.

| Rank | Addition or idea | End-user benefit | Proposed scope / first useful step | Effort | Priority / relationship |
| --- | --- | --- | --- | --- | --- |
| 1 | Ship a working Typst compiler with the normal installation | Users can produce their first figure without installing another application or editing PATH. | Prototype the existing `typst` Python binding as a dependency. Verify label measurements, PDF composition, diagnostics, default fonts, and clean-machine installation before selecting it. | Medium | Highest priority; explicit user preference. |
| 2 | Explicit literal-text and Typst helpers | Dataset labels, underscores, dollar signs, and mathematical source have predictable interpretations. | Design helpers such as `plotst.literal(...)` and `plotst.typst(...)`, including their interaction with Matplotlib text and custom formatters. Choose the clearest string default even if it breaks the current API. | Small–medium | Highest priority; explicit user preference. |
| 3 | Broader tick-formatter compatibility | More existing scientific plots work without rewriting generated labels as Typst. | Add dates and categories, then percentages, engineering units, and locale-sensitive formatting. Define an explicit adapter contract for custom formatters and subclasses. | Medium | Highest priority; explicit user preference. Build on the text/markup distinction in rank 2. |
| 4 | Faithful notebook preview | Users see the typography and placement that will appear in the exported figure while iterating. | Provide a helper such as `plotst.show(fig)` that renders a preview from the composed PDF. Start with static notebook display. | Medium | High everyday value; shares conversion work with PNG output. |
| 5 | Reuse compiled labels across exports | Repeated exports and figure collections avoid recompiling unchanged labels. | Begin with bounded reuse within a Python session. Benchmark representative repeated exports and text-heavy figures. Consider a persistent disk cache afterward. | Medium | High everyday value; evaluate alongside the embedded compiler. |
| 6 | PNG output | Figures can be used easily in slides, reports, messages, and other raster-image workflows. | Render the completed PDF at a requested resolution so PNG output uses the same layout and typography. Package the conversion dependency cleanly. | Medium | Closely related to notebook preview. |
| 7 | Simple package installation and verified Linux/macOS support | More users and collaborators can install and run Plotst in their existing environments. | Publish to PyPI, test clean installations on supported platforms, and use portable fonts in the core test corpus. Establish tested dependency combinations before widening pins. | Medium | Complements compiler shipping; existing binary wheels do not by themselves prove Plotst platform support. |
| 8 | Scoped configuration and reusable styles | Paper and presentation styles can coexist without settings leaking between figures. | Design a context manager that restores Matplotlib settings and an explicit configuration object associated with a figure or export. Reconsider process-wide configuration freely. | Small–medium | Useful foundation for fonts, compiler selection, and shared definitions. |
| 9 | Shared Typst definitions, imports, and notation | Symbols and mathematical conventions can be defined once and reused across figures and a document. | Provide a defined scope/preamble mechanism and explicit resource/package handling. Include these inputs in compilation identity and caching. | Medium | Distinctive longer-term capability. |
| 10 | More familiar export options | Plotst fits existing Matplotlib and report-generation workflows more naturally. | Support a tested subset of transparency, raster DPI, metadata, and in-memory/file-like output; report unsupported combinations clearly. | Small–medium | Extend the current export surface deliberately. |
| 11 | Publication-sizing conveniences | Users can specify final dimensions and column widths without repeating unit conversions. | Add physical-unit figure creation, reusable width/style presets, and adjustable crop padding. Build on existing exact-size and `tight_width_mm` support while preserving font sizes. | Small | Convenience improvement to an existing strength. |
| 12 | Environment and font diagnostics | Installation and typography problems are easier to understand and fix. | Report the selected compiler/backend and version, available or missing fonts, and relevant dependency versions. Keep failing-label diagnostics and explicit font-substitution errors. | Small–medium | Especially useful during installation and platform expansion. |
| 13 | Support Typst 0.15.1 and replace exact-build compatibility checks | Users can benefit from newer compiler fixes without unnecessary build-hash warnings. | Test 0.15.0 and 0.15.1 against the rendering corpus. Parse release versions for compatibility decisions; retain exact build identity for diagnostics and caches. | Small–medium | Near-term maintenance step; support must follow verification. |
| 14 | Stable default compiler plus external override | Most users get a tested setup while advanced users can select another compiler. | Install one exact tested default compiler version with each Plotst release. Preserve an explicit executable override or equivalent backend choice. Make selection deterministic and inspectable. | Medium | Part of the compiler-shipping design. |
| 15 | A documented compiler support policy | Users understand which combinations are tested and which are experimental. | Distinguish the default compiler, explicitly supported external versions, and experimental versions. Track Python-binding and embedded-Typst versions separately. | Small | Avoid promises about untested future releases. |
| 16 | Test supported and latest stable Typst releases | Upstream releases are evaluated promptly and support claims remain accurate. | Test the default on pull requests, other supported releases before release/relevant changes, and latest stable on a schedule. Review figure geometry and rendered changes as well as compilation success. | Medium | Upgrade workflow; a prerequisite for broad version support. |
| 17 | Scheduled compatibility checks against Typst `main` | Breakage is discovered before the next Typst release reaches users. | Run nightly or weekly, record the exact upstream commit, and retain failing PDFs/previews. Surface failures separately from stable release checks. | Medium | Recommended early-warning mechanism. This roadmap does not create an automation. |
| 18 | Public experimental/nightly builds | Interested users can try unreleased Typst capabilities. | Publish opt-in builds only after checks pass, each tied to a fixed compiler commit. Consider this once there is actual demand. | Medium–large | Deferred; scheduled upstream testing is useful before public nightlies are necessary. |
| 19 | Persistent compilation cache | Separate script runs and larger publication projects can reuse compiled labels. | Extend session reuse with bounded disk storage, invalidation, and a clear-cache mechanism. Identity must account for compiler/backend, fonts, source, style, color where relevant, definitions, and resources. | Medium | Follow rank 5 and measured evidence of benefit. |
| 20 | Reusable compiler state and possible batching | Text-heavy figures may spend less time initializing or invoking the compiler. | Measure benefits from a reusable Python compiler object. Investigate batching only if remaining costs justify the complexity; layout may request labels dynamically. | Medium–large | Performance investigation, not a promised speedup. |
| 21 | SVG output | Figures become easier to embed in browsers and edit in vector tools. | Investigate an end-to-end export path that preserves typography, clipping, opacity, and ordering. Verify text-versus-outline behavior explicitly. | Large | Valuable but later than preview and PNG. Typst label SVG support alone does not export a whole Matplotlib figure. |
| 22 | Full interactive rendering | Users could inspect and manipulate figures with faithful Typst text during live interaction. | Reassess after static previews and compilation performance are established. | Large | Longer-term exploration; static notebook preview is the first step. |
| 23 | Broader label layout and specialized axes | More complex annotations and plot types could become supported. | Treat Typst-internal multiline layout, deliberate overflow, polar axes, and 3D axes as separate scoped investigations with explicit geometry tests. | Large / varies | Later exploration. A compiler upgrade alone does not establish support. |

## Compiler distribution choices

| Option | Installation experience | Engineering implications | Recommendation |
| --- | --- | --- | --- |
| Existing `typst` Python binding as a dependency | One normal Python installation on platforms with compatible wheels; no separate CLI setup. | Adapt compilation, evaluation, version reporting, font discovery, and warnings. Verify the selected released binding, not just its development documentation. Binding releases may lag Typst. | Investigate first; combines simpler installation with a possible reduction in subprocess overhead. |
| Bundle the official Typst CLI in platform-specific wheels | One installation; Plotst uses a private executable. | Closest to the existing subprocess implementation. Requires platform packaging, executable discovery, release verification, and bundled license/font notices. | Strong alternative if binding parity or release availability is inadequate. |
| Download a pinned compiler on first use | Smaller initial package, but first export requires a download. | Requires verified downloads, caching, platform selection, and recovery from network failures. | Discussed alternative; less attractive as the normal experience. |
| User-supplied compiler | Users manage the compiler themselves. | Requires explicit selection, version reporting, and compatibility diagnostics. | Retain as an advanced override for stable or development compilers. |

Shipping a compiler does not imply silently updating it. A released Plotst installation should select a known compiler predictably; experimental upgrades should be opt-in.

## Adopting new Typst features

| Feature category | What Plotst needs to do |
| --- | --- |
| New inline math syntax, symbols, or text features | Often available through existing source passthrough once a compatible compiler is selected. Add representative examples and regression coverage. |
| Shared definitions, imports, or packages | Supply configuration and resource-resolution support, and include relevant inputs in cache identity. |
| Changes to metrics, baselines, fonts, PDF output, or diagnostics | Validate the existing measurement/composition contract and inspect rendered results before declaring compatibility. |
| Multiline blocks, page operations, explicit movement, or overflow | Revisit Plotst's label geometry contract; these are not automatically supported by upgrading Typst. |

At the discussion date, the latest official Typst release was **0.15.1**, released July 17, 2026. It changed bundled New Computer Modern fonts, fixed math alignment issues, and corrected `typst eval` error exit behavior. These are reasons to test output and diagnostics even for patch upgrades. Plotst currently warns on unrecognized compiler builds rather than categorically refusing them.

## Suggested delivery sequence

1. Verify Typst 0.15.1 and prototype the Python binding against the existing figure corpus.
2. Choose the compiler distribution approach and deliver installation without a separate Typst setup step.
3. Settle explicit label semantics and broaden common tick-formatter support, taking advantage of the freedom to change the API.
4. Add faithful notebook preview, PNG output, and measured compilation reuse.
5. Expand platform verification, scoped styles, shared Typst definitions, and export conveniences.
6. Establish supported-release and upstream-development checks; publish experimental builds only when useful to users.

This sequence can change as experiments reveal effort or dependencies. Early API redesign should be done when it improves the result, without compatibility scaffolding for unused interfaces.

## References

- [Current usage](usage.md) and [supported contract](support.md#supported-contract)
- [Current support matrix](support.md)
- [Typst Python package and available distributions](https://pypi.org/project/typst/)
- [Python binding documentation and source](https://github.com/messense/typst-py)
- [Python binding development API](https://github.com/messense/typst-py/blob/main/python/typst/__init__.pyi)
- [Typst 0.15.1 release notes](https://github.com/typst/typst/releases/tag/v0.15.1)
- [Typst redistribution license](https://github.com/typst/typst/blob/main/LICENSE)
- [Typst evaluation and supplied scope](https://typst.app/docs/reference/foundations/eval/)
- [Matplotlib export API](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)
