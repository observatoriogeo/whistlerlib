# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-05-23

First public release of Whistlerlib as a packaged Python library. Brings the
codebase to current Python (3.11+), Dask (2026.3.x), and pandas (2.x); adds a
comprehensive test suite, runnable examples, a portable docs tree, and the
`observatoriogeo/whistlerlib` Docker image. Upgrade notes from 0.1.0:
[`docs/migration/from-0.1.0.md`](docs/migration/from-0.1.0.md).

GitHub release only. PyPI publish + Docker Hub publish are deferred to a
later release.

### Added
- **Seven runnable examples under `examples/`** (`01-quickstart-hashtag-histogram`, `02-mention-histogram`, `03-ngram-histogram-bilingual`, `04-sentiment-spanish` [`slow`], `05-hashtag-coonet`, `06-mention-coonet`, `07-r-bridge-mfhashtags`). Each example dir contains `example.py` + `README.md`. The matching docker-backed integration test for each example lives under `tests/integration/test_<slug>.py` and shares a session-scoped Docker-cluster fixture.
- **`tests/integration/conftest.py`** with a session-scoped `whistlerlib_swarm` fixture that brings up a real local Docker cluster (locally-built `observatoriogeo/whistlerlib:dev` for both scheduler and workers) via Compose, waits for scheduler readiness, yields `(host, port)`, and tears down on session exit. Auto-skips when Docker is unavailable.
- New pytest marker `docker`, deselected from default `pytest` run; opt in with `-m docker`.
- CI `docker-examples` job (runs on `workflow_dispatch` and on push to `main`) builds the worker image and runs the integration suite end-to-end.
- **`observatoriogeo/whistlerlib` Docker image**: built with `uv` in a multi-stage `python:3.11-bookworm` base, shipping the whistlerlib package + R + the full R library set (`r-cran-tm`, `r-cran-slam`, `r-cran-snowballc`, `r-cran-reshape2`, `r-cran-dplyr`, `r-cran-tidyr`, `r-cran-nlp`, `r-cran-stringr`, `r-cran-remotes`, `r-cran-vctrs`, `r-cran-arrow`) + `RWeka` / `syuzhet` / `arrow` from Posit Package Manager + `radvertools` from upstream GitHub. This is the only custom image whistlerlib publishes; both the scheduler ("master") and worker services in `docker/docker-compose.yml` and `docker/stack.yml` use this image, with the master service overriding the `ENTRYPOINT` to `dask-scheduler`.
- `docker/Dockerfile.worker`, `docker/docker-compose.yml` (single-host development), `docker/stack.yml` (Swarm production).
- `docker/smoke.py`, runs hashtag / mention / coonet + (when R env vars are set) R-bridge calls against a running scheduler. Baked into the worker image at `/app/smoke.py`.
- `.github/workflows/docker-publish.yml`, multi-arch (`linux/amd64`, `linux/arm64`) buildx workflow for the worker image. Publishes on `v*` git tags; `workflow_dispatch` allows manual build-only runs (opt-in `push` input).
- `.dockerignore` for lean build context.
- **Comprehensive unit test suite** under `tests/unit/`: 119 fast, isolated tests covering the pure-Python `funcs/` (cleanText, getHashtags, getMentions, getNgrams, getSentimentScore), the orchestration layer (Context, TweetDataset, config, DatasetRepositoryClient), and the four `dask/*/algs.py` dispatchers. No Dask cluster, no real models, no network; full run in ~12s.
- Unit-test coverage gate: **`fail_under = 80`** in `[tool.coverage.report]`. Current measured coverage: **97%** (every `algs.py` and `funcs/` module at 100%; `dataset.py` at 89%, `time_profile.py` at 95%).
- CI runs `pytest tests/unit/ --cov ... --cov-report=html` and uploads the HTML report as a build artifact.
- **Portable docs tree under `docs/`** (intro, install/pip, install/docker, concepts/architecture, concepts/context-and-datasets, concepts/algorithm-families, tutorials/, api/ stub, migration/from-0.1.0.md). Inline Mermaid diagrams; no binary asset pipeline. Renders on GitHub today; lifts cleanly into a Docusaurus 3 site later.
- **CI doc job**: runs `scripts/sync_tutorials.py --check` (fails on drift between `examples/*/README.md` and `docs/tutorials/`) and `scripts/check_doc_links.py` (verifies every relative link in `docs/` resolves). Also enforces the no-em-dash style rule across `*.py`/`*.md`/`*.yml`/`*.toml` files.
- PEP 621 `pyproject.toml` with the hatchling build backend.
- `src/whistlerlib/` package layout.
- Python 3.11+ requirement declared via `requires-python` and `.python-version`.
- `CHANGELOG.md` and `docs/migration/from-0.1.0.md`.
- Test suite ported into `tests/` (legacy LocalCluster-backed suite under `tests/test_*.py`, modern unit + docker integration suites under `tests/unit/` and `tests/integration/`).
- `pytest-timeout` (30s per-test cap) and `pytest-cov` added to the `tests` extra.
- `emoji>=2` to runtime dependencies (was a transitive untracked need of `cleanText`).
- Session-scoped `LocalCluster` test fixture and synthetic 10-row Spanish / English tweet CSV; tests no longer need an external Dask scheduler or proprietary CSVs.
- Bundled NLTK stopwords corpus under `tests/fixtures/nltk_data/` so the suite runs offline.
- `r_required` skip marker and `slow` marker so contributors without R (or who don't want the 30s+ sentiment-model load) get a clean green default run.
- `ruff` (lint) configured in `pyproject.toml` and wired into CI.
- GitHub Actions workflow (`.github/workflows/ci.yml`) running `uv lock --locked` + `uv sync` + `ruff` + `pytest` on Python 3.11 and 3.12, plus the docs job and the docker-examples job.
- Citation block in `README.md` referencing the project's published paper in Multimedia Tools and Applications (DOI [`10.1007/s11042-024-19827-z`](https://doi.org/10.1007/s11042-024-19827-z)).

### Changed
- Package source relocated from `whistlerlib/` to `src/whistlerlib/` (via `git mv` to preserve history).
- Dependency floors raised to a Dask 2026.x-compatible set: `dask>=2024.1`, `pandas>=2.2`, `numpy>=1.26,<3`, `scikit-learn>=1.4`.
- `whistlerlib/config/config.py`: removed module-level `assert` on `WHISTLERLIB_R_*` env vars (broke `import whistlerlib` for non-R workflows). Validation moved to call-time at the R-bridge sites.
- `whistlerlib/dask/alt_python_algs/algs.py`: `nltk.download('stopwords')` now skipped when the corpus is already cached (`nltk.data.find` check first). Important for offline / pre-baked Docker workers.
- `whistlerlib/dask/alt_python_algs/funcs/cleanText.py`: migrated to `emoji.replace_emoji()` (emoji 2.0+ API; `get_emoji_regexp()` was removed upstream).
- `whistlerlib/dask/alt_python_algs/funcs/getNgrams.py`: migrated to `CountVectorizer.get_feature_names_out()` (sklearn 1.0+ rename).
- `whistlerlib/dask/alt_python_algs/funcs/getHashtags.py`: rewritten with `rename_axis('tag').reset_index(name='freq')` so the result is robust across pandas versions (modern `value_counts()` returns a `'count'`-named Series).

### Removed
- Pinned `requirements*.txt` files (replaced by `pyproject.toml` dependencies + extras).
- **`dask_sql` dependency** and the SQL surface it backed (`TweetDataset.run_query()`, `Context.dask_sql_context`, `TweetDataset.dask_sql_context`/`dask_sql_tablename`/`query_result`/`query`). `dask_sql==2024.5.0` is incompatible with `dask>=2025` because Dask folded `dask_expr` into the main namespace, and upstream `dask_sql` is unmaintained. See [`docs/migration/from-0.1.0.md`](docs/migration/from-0.1.0.md) for the workaround.

## [0.1.0] - 2024-05-01

Initial public commit of Whistlerlib on GitHub (`observatoriogeo/whistlerlib`, [commit `75565fd`](https://github.com/observatoriogeo/whistlerlib/commit/75565fd24012d58c1032a5d362940946609d680a)). Snapshot of the library at the time the public repository was opened. Not packaged: consumed by cloning the repo and adding `whistlerlib/` to `PYTHONPATH`.

### Added
- Full library source under `whistlerlib/`:
  - `Context` and `TweetDataset` (the entry classes).
  - `whistlerlib.dask.alt_python_algs` (pure-Python implementations of hashtag, mention, n-gram, sentiment, and co-occurrence-network analytics).
  - `whistlerlib.dask.r_algs` (R-subprocess implementations of the same analytics via the `tm`, `RWeka`, `syuzhet`, and `radvertools` R packages).
  - `whistlerlib.dask.base_algs` (the four distributed primitives: `compute_vector_histogram`, `compute_vector_range`, `compute_matrix_nz_histogram_and_sum`, `compute_weighted_coonet`).
  - `whistlerlib.dask.coonet_algs` (igraph-based co-occurrence-network builders).
  - `whistlerlib.time_profile` (per-stage timing breakdowns threaded through every base primitive).
- `README.md` with library overview, intended use cases, and basic-usage code sample.
- `LICENSE` (GPL-3.0-or-later).
- `.gitignore`.
