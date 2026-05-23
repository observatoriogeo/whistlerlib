
# Whistlerlib

**Whistlerlib** is a Python library developed at the CentroGeo Metropolitan Observatory, designed for distributed processing of large social media datasets. Utilizing data exploratory techniques in social network analysis (SNA) and natural language processing (NLP), Whistlerlib enables complex analyses on multi-core clusters.

## Features

Whistlerlib offers a variety of functions for analyzing social media data, including:

- Hashtag histograms
- Mention histograms
- N-gram histograms
- Sentiment polarity analysis
- Emotion analysis (fear, anger, joy, etc.)
- Weighted co-occurrence networks of hashtags
- Weighted co-occurrence networks of mentions

These functionalities are supported by distributed algorithms that operate on the Dask framework, optimizing performance on multi-core systems and computing clusters.

Whistlerlib accelerates several third-party libraries, which include:

- advertools: For extracting mentions.
- Syuzhet: For generating emotion and polarity scores.
- sentiment-analysis-spanish: For computing sentiment scores on Spanish datasets.

## Basic Usage

Here's a quick example of how to use Whistlerlib to analyze a Twitter dataset:

```python

from whistlerlib import Context

# create the Whistlerlib context and pass the IP and port of the Dask server
wl_context = Context('processes', '127.0.0.1', 8786)

# load a CSV file with X posts, and make 8 distributed partitions
dataset = wl_context.load_csv(filen='x_dataset.csv',
                              meta={
                                  'column_mapping': {
                                      'date_column': 'Date',
                                      'text_column': 'text'
                                  },
                                  'file_encoding': 'latin-1'
                              },
                              num_partitions=8)

# get the number of posts in a distributed fashion
posts_count = dataset.tweet_count()
print(f'Posts count: {posts_count}')

# compute the posts with sentiment scores between 0.9 and 0.95 in a distributed fashion
posts_with_scores = dataset.sentiment_range_spanish_alt_python(0.9, 0.95)
print(posts_with_scores)
```

## Development Status

**Please note:** Whistlerlib is currently under active development. This project is considered a work in progress, and it may undergo significant changes or improvements. We encourage users to wait for the first official release before utilizing this library for critical applications.


### Upcoming Releases

Upon completion, Whistlerlib will be available as a PyPi package, allowing for easy installation via pip. This will simplify the integration of Whistlerlib into existing Python environments and projects.


### Docker Support

Whistlerlib publishes **one custom Docker image** — `whistlerlib/worker` — designed to run in a Dask cluster on Docker Compose (single host) or Docker Swarm (production multi-node). The scheduler/"master" role uses the **upstream `daskdev/dask` image** directly because Whistlerlib's scheduler runs no whistlerlib code (it routes serialized task graphs; the algorithms all execute on workers).

| Role | Image | Notes |
|---|---|---|
| Scheduler / master | `daskdev/dask:2026.3.0-py3.11` (upstream, maintained by the Dask Foundation) | Routes task graphs. Pinned to match the worker's Dask version. |
| Worker | `whistlerlib/worker:<version>` | The whistlerlib package + R + the full R library set. Where the algorithms actually execute. |
| Client | Whatever Python env you have | `pip install whistlerlib` and connect with `Context(...)`. |

The worker image bakes in Python 3.11, Dask 2026.x, R, and every R package `whistlerlib.dask.r_algs` calls (`tm`, `slam`, `snowballc`, `rweka`, `syuzhet`, `dplyr`, `tidyr`, `stringr`, `nlp`, `arrow`, `radvertools`, …). **Your host machine never needs to install R, R packages, or set any `WHISTLERLIB_R_*` env vars** — those are worker-image-internal details.

#### Quick start — single host with Docker Compose

```bash
docker compose -f docker/docker-compose.yml up -d
# Dashboard: http://localhost:8787
# Scheduler: tcp://localhost:8786

# Smoke-test the running cluster:
docker compose -f docker/docker-compose.yml \
    run --rm worker python /app/smoke.py master 8786
```

#### Production — Docker Swarm

```bash
docker stack deploy -c docker/stack.yml whistlerlib
# Manager node hosts the master; worker nodes run N×whistlerlib/worker.
```

The Swarm stack file places the master on a `manager` node and spreads workers across `worker` nodes — matching the legacy Linode + Ansible production layout the library was designed for.

#### Image tags

| Tag | When | What |
|---|---|---|
| `latest` | each tagged release | most recent published version |
| `<major>.<minor>` | each tagged release | floating tag for that minor line |
| `<major>.<minor>.<patch>` | each tagged release | pinned version |
| `dev-<sha>` | manual `workflow_dispatch` runs | development builds (no `latest` retag) |


## Development

Contributors and integrators can install Whistlerlib in editable mode.

### Recommended: `uv` (Astral)

[uv](https://docs.astral.sh/uv/) is the project's default package / environment manager — ~10× faster than `pip` and provides a reproducible lockfile.

```bash
git clone <repo-url>
cd whistlerlib
uv sync --extra dev    # creates .venv/, resolves uv.lock, installs deps + dev tools
uv run pytest           # run the test suite
uv run python -c "import whistlerlib; print(whistlerlib.Context)"
```

### Fallback: plain `pip` + `venv`

Plain `pip` is fully supported; `uv` is the project's *internal* preference, not an installation requirement.

```bash
git clone <repo-url>
cd whistlerlib
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### R bridge

The R-backed algorithms in `whistlerlib.dask.r_algs` (R-implemented hashtag / mention / n-gram / sentiment) run inside the published Whistlerlib Docker images (**both master and worker** ship with R + the R libraries baked in). **You do not need to install R, or any R packages, or set any `WHISTLERLIB_R_*` env vars** to use whistlerlib — that's the whole point of the Docker images.

- **`pip install whistlerlib` on a bare machine** gives you the alt-python algorithm surface (hashtag / mention / n-gram histograms, sentiment-spanish, weighted co-occurrence networks). R-bridge methods aren't available in this mode; that's by design, not a missing dependency.
- **For the R-bridge methods**, deploy via the published `whistlerlib/worker` image (the scheduler uses upstream `daskdev/dask`) — either with `docker compose` (single-host) or `docker stack deploy` on a Docker Swarm. The worker image sets `WHISTLERLIB_R_PATH` and `WHISTLERLIB_R_SCRIPTS_PATH` internally; you never set them yourself.
- **R-bridge tests skip locally.** The `r_required` pytest marker gates them on the two env vars — absent on a dev box, so they skip cleanly. They run inside the Docker images.


## License

Whistlerlib is distributed under the GPL-3 license. See the `LICENSE` file for more details.


## Contact

If you have specific questions about the project, you can contact the developers via [GitHub Issues](link_to_your_github_issues) or directly by email at [agarcia@centrogeo.edu.mx](mailto:agarcia@centrogeo.edu.mx).

---

For more information and updates, follow our project on GitHub.

