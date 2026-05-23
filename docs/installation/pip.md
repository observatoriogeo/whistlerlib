# Install from PyPI

The client-side install. Use this on any machine that runs the Whistlerlib **client**: your laptop, a Jupyter server, a CI runner that submits jobs to a Dask cluster, etc.

For the cluster itself (scheduler + workers), see [Docker installation](docker.md).

## Requirements

- **Python ≥ 3.11**.
- A reachable Dask scheduler (a local one via `LocalCluster`, or a remote one, see [Architecture](../concepts/architecture.md)). The pip install does **not** start a cluster for you.

## Install

```bash
pip install whistlerlib
```

> If you use [uv](https://docs.astral.sh/uv/): `uv pip install whistlerlib` (or `uv add whistlerlib` if you're managing a `pyproject.toml`).

That's it for the client. Verify:

```bash
python -c "import whistlerlib; print(whistlerlib.Context)"
# <class 'whistlerlib.context.Context'>
```

## What you get

A `pip install` on a bare host gives you the **alt-python algorithm surface**: everything in `whistlerlib.dask.alt_python_algs`:

- `hashtag_histogram_alt_python`
- `mention_histogram_alt_python`
- `ngram_histogram_alt_python`
- `sentiment_range_spanish_alt_python`
- `hashtag_weighted_coonet`, `mention_weighted_coonet`

Plus the core types: `Context`, `TweetDataset`.

## What you don't get (and why that's fine)

The **R-bridge** methods, `hashtag_histogram_r`, `mention_histogram_r`, `ngram_histogram_r`, `sentiment_histogram_and_sum_r`, are **not available from a pip install alone**. They shell out to `Rscript` on the worker, which needs R + a curated set of R libraries (`tm`, `syuzhet`, `RWeka`, `radvertools`, …). Installing all of that on a researcher's laptop is exactly what we don't want you to do.

Instead, the R libraries live **inside the published `whistlerlib/worker` Docker image** ([Docker installation](docker.md)). The pattern is:

- **Client**: `pip install whistlerlib` on your laptop. Use the alt-python methods locally, or submit work to a remote cluster.
- **Cluster workers**: run the `whistlerlib/worker` image. R + libraries baked in. R-bridge methods just work when called against this cluster.

So:

- ✅ `pip install whistlerlib` → client-side, alt-python methods, no R required.
- ✅ `pip install whistlerlib` + connect to a Dask cluster running `whistlerlib/worker` → full surface including R-bridge.
- ❌ `pip install whistlerlib` + R installed manually on the host → not a supported configuration. We don't test it; don't go there.

## Next

- [Docker installation](docker.md), bring up a local cluster (Compose) or production cluster (Swarm).
- [Tutorial 01](../tutorials/01-quickstart-hashtag-histogram.md), first end-to-end run.
