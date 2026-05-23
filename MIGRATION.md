# Migration Guide

This document captures what changed between the abandoned pre-revival snapshot
of Whistlerlib (last actively touched 2021–2022) and the upcoming `0.2.0`
revival release. It will grow as the revival phases (see
[`.plans/REVIVAL-PLAN.md`](../.plans/REVIVAL-PLAN.md) in the wrapper directory)
land.

## From pre-revival → 0.2.0

### Packaging

| Before | After |
|---|---|
| No `setup.py` / `pyproject.toml`. Install via `pip install -r requirements.txt` and put the repo on `PYTHONPATH`. | `pyproject.toml` (PEP 621, hatchling). Install with `pip install whistlerlib` once published, or `pip install -e .` from a clone. |
| Pinned `dask==2021.10.0`, `pandas==1.0.1`, `numpy==1.18.1`, `scikit-learn==0.23.2`, etc. | Modern floors: `dask>=2024.1`, `pandas>=2.2`, `numpy>=1.26,<3`, `scikit-learn>=1.4`. See `pyproject.toml` for the full list. |
| Source at the repo root in `whistlerlib/`. | Source at `src/whistlerlib/` (src-layout). |
| Python 3.7 / 3.8-era code. | **Python 3.11+ required.** |

### Dependencies removed

_To be finalized during Phase 2._ Expected removals:
- `dask_sql` — decision deferred to Phase 2 (replace with `duckdb`, vendor a maintained fork, or drop the SQL surface entirely). Tracked in plan §4.

### Dependencies renamed / replaced

| Old | New | Notes |
|---|---|---|
| `python-igraph` | `igraph` | PyPI rename; same library. |

### API breaking changes

_None catalogued yet — Phase 2 will populate this section as the test suite
gets back to green and breaking changes become visible._

### Behavioural changes

- **`whistlerlib.config.config` no longer asserts R-bridge env vars at import.**
  Previously, `import whistlerlib` would fail with `AssertionError` unless both
  `WHISTLERLIB_R_SCRIPTS_PATH` and `WHISTLERLIB_R_PATH` were set, regardless of
  whether the caller used the R bridge. Now those variables default to `None`
  when unset, and validation is the responsibility of the R-bridge code paths
  that actually need them. **Impact:** non-R workflows can now `import
  whistlerlib` without setting any env vars; R-bridge workflows behave
  identically as long as the env vars are set before the R call sites run.

---

For the upgrade path beyond `0.2.0`, a new `## From 0.2.0 → ...` section will
be added here when the next release lands.
