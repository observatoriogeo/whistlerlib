# Migrating from 0.1.0

If your code is built against the **0.1.0 codebase** (the [first commit](https://github.com/observatoriogeo/whistlerlib/releases/tag/v0.1.0) of `observatoriogeo/whistlerlib`, dated 2024-05-01, sourced by cloning the repo and putting it on `PYTHONPATH`), this page covers what changes in 0.2.0.

If you've never used the 0.1.0 codebase, skip this page, `pip install whistlerlib` is your starting point, see [Install from PyPI](../installation/pip.md).

## TL;DR

You need to:

1. **Install via `pip install whistlerlib`** instead of `PYTHONPATH`-ing a clone.
2. **Move to Python 3.11+** (was 3.7 / 3.8-era code).
3. **Drop any `dask_sql_context` / `run_query` usage**: the SQL surface is gone (see [API breaking changes](#api-breaking-changes)).
4. **Stop setting `WHISTLERLIB_R_PATH` / `WHISTLERLIB_R_SCRIPTS_PATH` on the host**: those are worker-image-internal now.
5. **Deploy via Docker** if you used the legacy `docker/linode/` setup, the production target is now Docker Swarm or Compose (see [Install with Docker](../installation/docker.md)).

## Packaging changes

| Before | After |
|---|---|
| No `setup.py` / `pyproject.toml`. Install via `pip install -r requirements.txt` and put the repo on `PYTHONPATH`. | `pyproject.toml` (PEP 621, hatchling). Install with `pip install whistlerlib` once published, or `pip install -e .` from a clone. |
| Pinned `dask==2021.10.0`, `pandas==1.0.1`, `numpy==1.18.1`, `scikit-learn==0.23.2`. | Modern floors: `dask>=2024.1`, `pandas>=2.2`, `numpy>=1.26,<3`, `scikit-learn>=1.4`. |
| Source at the repo root in `whistlerlib/`. | Source at `src/whistlerlib/` (src-layout). |
| Python 3.7 / 3.8-era code. | **Python 3.11+ required.** |

## Dependency changes

**Removed:**

- **`dask_sql`**: removed entirely. Upstream `dask_sql==2024.5.0` crashes against modern Dask because Dask folded `dask_expr` into the main namespace. Since the SQL surface was used by **zero tests** and not advertised in the README example, it was dropped rather than replaced. See [API breaking changes](#api-breaking-changes) for the workaround.

**Renamed / replaced:**

| Old | New |
|---|---|
| `python-igraph` | `igraph` (PyPI rename; same library) |
| `dask_sql==2024.5.0` | *(removed, see above)* |

**Added:**

| Package | Why |
|---|---|
| `emoji>=2` | Was a transitive (untracked) need of `cleanText`. Now declared explicitly. |

## API breaking changes

- **`Context(...)` no longer exposes `dask_sql_context`.** If you were reaching into it:
  - **Filtering**: use `ctx.load_csv(...).dask_df[predicate].compute()` directly.
  - **Ad-hoc SQL on small results**: `compute()` to pandas, then `duckdb.sql(...)`.
- **`TweetDataset.__init__` signature change.** Three parameters removed: `dask_sql_context`, `query_result`, `query`. Code that constructed `TweetDataset` directly must drop these kwargs. Code that goes through `Context.load_csv()` is unaffected.
- **`TweetDataset.run_query(query)` removed.** Replacement: filter on `ds.dask_df` directly, or `compute()` and apply duckdb to the resulting pandas DataFrame.
- **`TweetDataset.range_by_dates(...)`** still returns a `TweetDataset`, but without the historical `query_result` / `query` attributes.

## Behavioural changes

- **`whistlerlib.config.config` no longer asserts R-bridge env vars at import.** Previously, `import whistlerlib` would fail with `AssertionError` unless both `WHISTLERLIB_R_SCRIPTS_PATH` and `WHISTLERLIB_R_PATH` were set, regardless of whether the caller used the R bridge. Now those variables default to `None` when unset; validation lives in the R-bridge code paths that actually need them.

  **Impact:** non-R workflows can now `import whistlerlib` without setting any env vars; R-bridge workflows behave identically as long as the env vars are set before the R call sites run. With the Docker images, you don't set them yourself, the worker image sets them internally.

- **NLTK stopwords are no longer downloaded unconditionally.** The algorithm code now does `try: nltk.data.find('corpora/stopwords') except LookupError: nltk.download(...)`. Behaviour is identical on fresh machines; the change makes the code work offline when the corpus is already cached.

- **`getHashtags`/`getNgrams` adapted to modern pandas + sklearn.** No user-visible behavioural change; the resulting DataFrames have the same `tag`/`freq` and `N_Tokens`/`Freq` columns as before.

## Deployment

The legacy `../whistlerlib/docker/linode/` two-image stack (custom scheduler image + custom worker image) is replaced by a simpler shape:

- **Single custom image**: `observatoriogeo/whistlerlib:<version>`. Carries whistlerlib + Dask + R + the full R library set. Both worker and scheduler roles in the published Docker Compose / Swarm stacks use this image; the scheduler service overrides the entrypoint to `dask-scheduler`.
- **No `whistlerlib/master` image.** It would just be a worse copy of the worker image.

Deployment commands:

```bash
# Single host (development):
docker compose -f docker/docker-compose.yml up -d

# Multi-node production (Docker Swarm):
docker stack deploy -c docker/stack.yml whistlerlib
```

See [Install with Docker](../installation/docker.md) for the full deployment story.

## Test-infrastructure changes

These don't affect callers but are worth knowing if you run / extend the suite:

- **Tests no longer need an external Dask scheduler.** A session-scoped `LocalCluster` is started in `tests/conftest.py`.
- **Tests no longer need a real X-platform CSV.** A synthetic 10-row hand-crafted Spanish/English CSV is generated per session.
- **R-bridge tests skip by default.** They opt in via `WHISTLERLIB_R_PATH` and `WHISTLERLIB_R_SCRIPTS_PATH`; the worker Docker image sets them. Local dev never needs R installed.
- **`sentiment_range_spanish_alt_python` tests are marked `slow`** and excluded from default runs (each loads a TensorFlow model). Opt in with `pytest -m slow`.
- **Per-test timeout: 30s.** Configured in `[tool.pytest.ini_options]`; a hang fails loudly instead of stalling the suite.

## Future migrations

For the upgrade path beyond `0.2.0`, a new page will be added here when the next release lands.
