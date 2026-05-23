# Whistlerlib examples

Seven runnable examples that double as **learning material and docs source**. Each example lives in `examples/<slug>/` and contains:

- `README.md`, narrative, copy-paste-ready for the separate Docusaurus docs project.
- `example.py`, a standalone script you can `python example.py` against a running cluster.

The matching pytest integration test for each example lives in [`tests/integration/`](../tests/integration/) (one file per example, e.g. `tests/integration/test_01_quickstart_hashtag_histogram.py`). Those tests share a session-scoped Docker-cluster fixture in `tests/integration/conftest.py` and resolve their `example.py` via an `EXAMPLE_SLUG = '<slug>'` module-level constant.

| # | Example | Demonstrates | Notes |
|---|---|---|---|
| 01 | [quickstart-hashtag-histogram](01-quickstart-hashtag-histogram/) | `hashtag_histogram_alt_python`, the canonical Whistlerlib workflow | the minimum-viable usage |
| 02 | [mention-histogram](02-mention-histogram/) | `mention_histogram_alt_python` | what's different from hashtags |
| 03 | [ngram-histogram-bilingual](03-ngram-histogram-bilingual/) | `ngram_histogram_alt_python` with `lan='spanish'` and `lan='english'` | stopword handling per language |
| 04 | [sentiment-spanish](04-sentiment-spanish/) | `sentiment_range_spanish_alt_python` over `[0.9, 1.0]` | **`slow`**: loads the TF model |
| 05 | [hashtag-coonet](05-hashtag-coonet/) | `hashtag_weighted_coonet`, co-occurrence graph | igraph result inspection |
| 06 | [mention-coonet](06-mention-coonet/) | `mention_weighted_coonet`, same on mentions | same pattern; clean comparison with #05 |
| 07 | [r-bridge-mfhashtags](07-r-bridge-mfhashtags/) | `hashtag_histogram_r`, the R-bridge path | **`docker`-only**: needs R, which lives in the worker image |

## How to run them

### Prerequisites

- Docker daemon running.
- `whistlerlib/worker:dev` image present locally (the test fixture builds it on first run; ~5–10 min the first time for R + radvertools).
- NLTK corpora `stopwords`, `punkt`, `punkt_tab` in `~/nltk_data`. The fixture downloads them automatically on first run; examples 03 and 04 call `nltk.corpus.stopwords` on the **client** side, so they live on the host, not in the image. The auto-downloader forces IPv4 to avoid the multi-minute `SYN-SENT` hang seen on hosts with broken IPv6 routing.

### As a script (interactive)

```bash
# Bring the cluster up
docker compose -f docker/docker-compose.yml up -d

# Run an example directly
cd examples/01-quickstart-hashtag-histogram
python example.py                 # connects to localhost:8786 by default
python example.py master 8786     # explicit host/port

# Tear down
docker compose -f docker/docker-compose.yml down
```

### Via pytest (with fixture-managed cluster)

The integration tests live under [`tests/integration/`](../tests/integration/), not next to the examples:

```bash
# Run all docker-backed integration tests (the fixture handles bring-up + tear-down)
uv run pytest -m docker tests/integration

# Just one example's test
uv run pytest -m docker tests/integration/test_01_quickstart_hashtag_histogram.py
```

The `docker` marker is **deselected by default** so a plain `pytest` run stays fast and doesn't require Docker. CI runs them in a separate gated job.

## Deployment-target note

The session fixture in `tests/integration/conftest.py` uses **Docker Compose** (not Swarm) to bring up the local cluster. The reason is purely practical: single-node Docker Swarm doesn't schedule services with `node.role==worker` placement constraints on a manager-only node, which makes the `docker/stack.yml` production stack file fiddly for local testing.

The Compose stack validates exactly the same image and network story that production Swarm uses, same `daskdev/dask` scheduler image, same `whistlerlib/worker` image, same TCP wire protocol. **Production deployment is Swarm via `docker/stack.yml`**; that path is the one operators use with `docker stack deploy` on a real multi-node cluster.

## Synthetic data only

Per `.plans/REVIVAL-PLAN.md` §2, the X-platform CSV datasets that originally drove Whistlerlib's development cannot be redistributed. Every example here uses small, hand-crafted synthetic data inlined into the script. The data is rich enough to make each algorithm produce a non-trivial result, and small enough to keep test runtime predictable.
