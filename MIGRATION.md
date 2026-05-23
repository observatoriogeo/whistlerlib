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

- **`dask_sql`** — removed entirely. The package is unmaintained upstream and its `2024.5.0` release is broken against `dask>=2025` (Dask folded `dask_expr` into its main namespace; `dask_sql.context.create_table` still tries `from dask_expr.io.parquet import ReadParquet` and crashes). Since the SQL surface was used by **zero tests** and not advertised in the README example, it was dropped rather than replaced. See "API breaking changes" below for the workaround.

### Dependencies renamed / replaced

| Old | New | Notes |
|---|---|---|
| `python-igraph` | `igraph` | PyPI rename; same library. |
| `dask_sql==2024.5.0` | _(removed)_ | See above. |

### Dependencies added

| Package | Why |
|---|---|
| `emoji>=2` | Was a transitive (untracked) need of `cleanText`. Now declared explicitly. |

### API breaking changes

- **`whistlerlib.Context(...)` no longer exposes `dask_sql_context`.** The argument was internal but accessible. If you were reaching into it, switch to:
  - **Filtering:** use `ctx.load_csv(...).dask_df[predicate]` (a Dask DataFrame) and `.compute()`.
  - **Ad-hoc SQL on small results:** `compute()` to pandas, then run `duckdb.sql(...)` directly. Whistlerlib no longer ships SQL as a built-in surface.

- **`whistlerlib.TweetDataset.__init__` signature change.** The following parameters were removed:
  - `dask_sql_context`
  - `query_result`
  - `query`

  Code that constructed `TweetDataset` instances directly will need to drop these kwargs. Code that goes through `Context.load_csv()` is unaffected.

- **`whistlerlib.TweetDataset.run_query(query)` removed.** No tests, examples, or docs used it. Replacement: use Dask DataFrame filtering directly on `ds.dask_df` (`ds.dask_df[ds.dask_df['score'] > 0.9].compute()`), or `compute()` and apply duckdb to the resulting pandas DataFrame.

- **`whistlerlib.TweetDataset.range_by_dates(...)` returns a `TweetDataset`** without the historical `query_result` / `query` attributes (they were removed alongside the SQL surface).

### Behavioural changes

- **`whistlerlib.config.config` no longer asserts R-bridge env vars at import.** Previously, `import whistlerlib` would fail with `AssertionError` unless both `WHISTLERLIB_R_SCRIPTS_PATH` and `WHISTLERLIB_R_PATH` were set, regardless of whether the caller used the R bridge. Now those variables default to `None` when unset, and validation is the responsibility of the R-bridge code paths that actually need them. **Impact:** non-R workflows can now `import whistlerlib` without setting any env vars; R-bridge workflows behave identically as long as the env vars are set before the R call sites run.

- **NLTK stopwords are no longer downloaded unconditionally.** The algorithm code now does `try: nltk.data.find('corpora/stopwords') except LookupError: nltk.download(...)`. Behaviour is identical on fresh machines; the change makes the code **work offline** when the corpus is already cached (e.g. baked into a worker Docker image) without re-hitting the NLTK download server, which is sometimes slow or unreachable.

- **`getHashtags`/`getNgrams` adapted to modern pandas + sklearn.** No user-visible behavioural change; the resulting DataFrames have the same `tag`/`freq` and `N_Tokens`/`Freq` columns as before. The internal pipeline now uses `value_counts().rename_axis(...).reset_index(name=...)` (pandas-version-agnostic) and `CountVectorizer.get_feature_names_out()` (sklearn 1.0+ API).

### Examples + docker-backed tests (Phase 4)

Seven examples in `examples/<slug>/` that triple as integration tests, learning material, and docs source. Each runnable as `python example.py [host [port]]` against a running Whistlerlib cluster, and tested via `pytest -m docker examples/` against a session-managed local cluster (upstream `daskdev/dask` master + `whistlerlib/worker:test`). The R-bridge example (`07-r-bridge-mfhashtags`) runs in the worker container where R lives, so a clean dev host needs zero R install to verify R-path behaviour.

`pytest` (no flags) stays fast — `testpaths` is restricted to `tests/unit` + `examples/`, the docker-marked examples are deselected, and the legacy LocalCluster integration suite under `tests/test_*.py` is now opt-in via `pytest tests/ --ignore=tests/unit`. CI runs all three layers (unit, integration, docker examples) in separate steps.

### Deployment changes — Docker images (Phase 5)

The README's long-standing promise of Docker support is now delivered, but the architecture is simpler than the legacy `../whistlerlib/docker/linode/` two-image setup suggested:

- **`whistlerlib/worker`** — the only custom image. Built from `python:3.11-slim-bookworm` via a multi-stage `uv` install. Carries whistlerlib + Dask + R + the full R library set (`r-cran-tm`, `r-cran-slam`, `r-cran-snowballc`, `r-cran-rweka`, `r-cran-syuzhet`, `r-cran-dplyr`, `r-cran-tidyr`, `r-cran-stringr`, `r-cran-nlp`, `r-cran-arrow`, `r-cran-vctrs`, `r-cran-remotes`, `r-cran-reshape2`) + `radvertools`.
- **No `whistlerlib/master` image.** The scheduler uses the upstream `daskdev/dask:<version>-py3.11` image directly. Dask's scheduler routes serialized task graphs and runs no whistlerlib code, so wrapping `daskdev/dask` with our own brand would be a lagging copy. The scheduler image tag is pinned in `docker/docker-compose.yml` and `docker/stack.yml` to track the worker's Dask version (currently `2026.3.0-py3.11`).

Replaces the legacy `daskdev/dask` + `conda env update` + `libffi6`-hack stack. Modern Dask 2026, Python 3.11, `uv` for ~10× faster builds, multi-arch (`linux/amd64` + `linux/arm64`) via GitHub Actions buildx.

**Host-machine impact:**

- A host running `pip install whistlerlib` **does not need** R, R packages, or any `WHISTLERLIB_R_*` env vars. The alt-python algorithm surface works out of the box. R-bridge methods are unavailable on a bare host by design.
- A host running the Docker stack **does not need** R either — that's the entire point. `docker compose up` or `docker stack deploy` and you're done.

**Deployment commands:**

```bash
# Single host (development):
docker compose -f docker/docker-compose.yml up -d

# Multi-node production (Docker Swarm):
docker stack deploy -c docker/stack.yml whistlerlib
```

The Swarm stack file matches the legacy Linode + Ansible layout (manager-node scheduler, worker-node workers, overlay network).

### Test-infrastructure changes

These don't affect callers but are worth knowing if you run / extend the suite:

- **Tests no longer need an external Dask scheduler.** A session-scoped `LocalCluster` is started in `tests/conftest.py`.
- **Tests no longer need a real X-platform CSV.** A synthetic 10-row hand-crafted Spanish/English CSV is generated per session (see §2 of `.plans/REVIVAL-PLAN.md`).
- **R-bridge tests skip by default.** They opt in via `WHISTLERLIB_R_PATH` and `WHISTLERLIB_R_SCRIPTS_PATH` env vars; the Whistlerlib worker Docker image (Phase 5) sets them. Local dev never needs R installed.
- **`sentiment_range_spanish_alt_python` tests are marked `slow`** and excluded from default runs (each loads a TensorFlow model). Opt in with `pytest -m slow`.
- **Per-test timeout: 30s.** Configured in `[tool.pytest.ini_options]` so a hang in any single test fails loudly instead of stalling the suite.

---

For the upgrade path beyond `0.2.0`, a new `## From 0.2.0 → ...` section will
be added here when the next release lands.
