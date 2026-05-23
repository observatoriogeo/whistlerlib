# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

This entry tracks work toward the upcoming `0.2.0` revival release. See also
[`docs/migration/from-pre-revival.md`](docs/migration/from-pre-revival.md) for
the upgrade story from the abandoned pre-revival snapshot.

### Added
- **Seven runnable examples under `examples/`** (`01-quickstart-hashtag-histogram`, `02-mention-histogram`, `03-ngram-histogram-bilingual`, `04-sentiment-spanish` [`slow`], `05-hashtag-coonet`, `06-mention-coonet`, `07-r-bridge-mfhashtags`). Each example dir contains `example.py` + `README.md`. The matching docker-backed integration test for each example lives under `tests/integration/test_<slug>.py` and shares a session-scoped Docker-cluster fixture.
- **`tests/integration/conftest.py`** with a session-scoped `whistlerlib_swarm` fixture that brings up a real local Docker cluster (locally-built `whistlerlib/worker:dev` for both scheduler and workers) via Compose, waits for scheduler readiness, yields `(host, port)`, and tears down on session exit. Auto-skips when Docker is unavailable.
- New pytest marker `docker`, deselected from default `pytest` run; opt in with `-m docker`.
- CI `docker-examples` job (workflow_dispatch-gated) builds the worker image and runs the example suite end-to-end.
- **`whistlerlib/worker` Docker image**: built with `uv` in a multi-stage `python:3.11-slim-bookworm` base, shipping the whistlerlib package + R + the full R library set (`r-cran-tm`, `r-cran-slam`, `r-cran-snowballc`, `r-cran-rweka`, `r-cran-syuzhet`, `r-cran-dplyr`, `r-cran-tidyr`, `r-cran-stringr`, `r-cran-nlp`, `r-cran-arrow`, `r-cran-vctrs`, `r-cran-remotes`, `r-cran-reshape2`) + `radvertools` from upstream. This is the **only** custom image whistlerlib publishes, the scheduler uses the upstream `daskdev/dask:<version>-py3.11` image directly.
- `docker/Dockerfile.worker`, `docker/docker-compose.yml` (single-host), `docker/stack.yml` (Swarm production). Both compose files use `daskdev/dask:2026.3.0-py3.11` for the scheduler (pinned to match the worker's Dask version in `uv.lock`).
- `docker/smoke.py`, runs hashtag/mention/coonet + (when R env vars are set) R-bridge calls against a running scheduler. Baked into the worker image at `/app/smoke.py`.
- `.github/workflows/docker-publish.yml`, multi-arch (`linux/amd64`, `linux/arm64`) buildx workflow for the worker image. Publishes on `v*` git tags; `workflow_dispatch` allows manual build-only runs (opt-in `push` input).
- `.dockerignore` for lean build context.
- **Comprehensive unit test suite** under `tests/unit/`, 91 fast, isolated tests covering the pure-Python `funcs/` (cleanText, getHashtags, getMentions, getNgrams, getSentimentScore) and the orchestration layer (Context, TweetDataset, config, DatasetRepositoryClient). No Dask cluster, no real models, no network, full run in ~13s.
- Unit-test coverage gate: **fail_under=80%** in `[tool.coverage.report]`. Current measured coverage **86.97%** (`funcs/` modules at 100%, orchestration at 89–100%; deferred dask alg modules omitted per the plan).
- CI now runs `pytest tests/unit/ --cov ... --cov-report=html` and uploads the HTML report as a build artifact.
- PEP 621 `pyproject.toml` with hatchling build backend.
- `src/whistlerlib/` package layout.
- Python 3.11+ requirement declared via `requires-python` and `.python-version`.
- `CHANGELOG.md` and `docs/migration/from-pre-revival.md`.
- Ported `getWordCloud.py` and `getWordCloud.R` from the unreleased working copy.
- Test suite (12 files) ported into `tests/`.
- `pytest-timeout` (30s per-test cap) and `pytest-cov` to the `tests` extra.
- `emoji>=2` to runtime dependencies.
- Session-scoped `LocalCluster` test fixture and synthetic 10-row Spanish/English tweet CSV, tests no longer need an external Dask scheduler or proprietary CSVs.
- Bundled NLTK stopwords corpus under `tests/fixtures/nltk_data/` so the suite runs offline.
- `r_required` skip marker and `slow` marker so contributors without R (or who don't want the 30s+ sentiment model load) get a clean green default run.
- `ruff` (lint) configured in `pyproject.toml` and wired into CI.
- GitHub Actions workflow (`.github/workflows/ci.yml`) running `uv lock --locked` + `uv sync` + `ruff` + `pytest` on Python 3.11 and 3.12.

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
- **`dask_sql` dependency** and the SQL surface it backed (`TweetDataset.run_query()`, `Context.dask_sql_context`, `TweetDataset.dask_sql_context`/`dask_sql_tablename`/`query_result`/`query`). `dask_sql==2024.5.0` is incompatible with `dask>=2025` because Dask folded `dask_expr` into the main namespace, and upstream `dask_sql` is unmaintained. See `docs/migration/from-pre-revival.md` for the workaround.
