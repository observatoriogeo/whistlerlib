# API reference

The API reference is **generated from the source docstrings** at release time, not committed by hand. This file is a stub describing the planned generator setup; it will be replaced by the actual reference in Phase 7.

## What will be generated

Modules with a public surface:

| Module | What lives here |
|---|---|
| `whistlerlib` | `Context` (re-exported from `whistlerlib.context`). |
| `whistlerlib.context` | `Context` class. |
| `whistlerlib.dataset` | `TweetDataset` class — all analytic methods. |
| `whistlerlib.dask.alt_python_algs` | `compute_*` wrappers for the pure-Python algorithm family. |
| `whistlerlib.dask.r_algs` | `compute_*` wrappers for the R-bridged algorithm family. |
| `whistlerlib.dask.coonet_algs` | `to_graph`, `compute_*_weighted_coonet`. |
| `whistlerlib.dask.base_algs` | The four base Dask primitives. |

Private surface (`whistlerlib.clients`, `whistlerlib.config`, `whistlerlib.logger`, `whistlerlib.time_profile`, every `funcs/` subpackage) is documented in source but excluded from the generated reference.

## Generator: `pdoc`

The plan calls for [`pdoc`](https://pdoc.dev/) — single-pass, Markdown-friendly, zero config:

```bash
uvx pdoc -o docs/api whistlerlib
```

This will land in CI (a GitHub Actions workflow on tag pushes) and overwrite the contents of `docs/api/` with one file per module. The committed `README.md` stub will be removed at that point.

## Why not Sphinx?

Sphinx is heavier and produces RST/HTML primarily. Whistlerlib's docs are markdown-first (Docusaurus-bound), and `pdoc` outputs Markdown directly. Sphinx would mean either an RST→MDX bridge or an `autodoc` → MD post-processor. `pdoc` skips the bridge.

## In the meantime

Until Phase 7 lands, the source is the reference:

- `src/whistlerlib/context.py` — `Context`.
- `src/whistlerlib/dataset.py` — `TweetDataset`, all analytic methods.
- `src/whistlerlib/dask/<family>_algs/algs.py` — algorithm dispatch.
- `src/whistlerlib/dask/base_algs/algs.py` — the four base primitives.

Each method has a short docstring; the [Context & datasets](../concepts/context-and-datasets.md) and [Algorithm families](../concepts/algorithm-families.md) pages explain how they fit together.
