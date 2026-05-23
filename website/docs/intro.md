---
id: intro
title: Introduction
slug: /
sidebar_position: 1
---

# Whistlerlib

**Whistlerlib** is a Python library for distributed processing of large social-media datasets, developed at the [CentroGeo](https://www.centrogeo.org.mx/) Metropolitan Observatory. It combines social-network-analysis (SNA) and natural-language-processing (NLP) primitives with a [Dask](https://www.dask.org/)-backed execution model, so a single analytical query, top-`k` hashtags, weighted co-occurrence networks, Spanish sentiment ranges, etc., fans out across a cluster of workers and comes back as a pandas DataFrame or an `igraph.Graph`.

## What it does

| Family | Examples |
|---|---|
| Frequency analytics | Top-`k` hashtag / mention / n-gram histograms |
| Sentiment | Spanish sentiment scores via `sentiment-analysis-spanish`; multilingual emotion vectors via the `syuzhet` R package |
| Networks | Weighted co-occurrence networks of hashtags and mentions, returned as `igraph.Graph` |

Each analytic comes in two flavours:

- **`*_alt_python`**, pure Python implementation (uses `advertools`, `nltk`, `sentiment-analysis-spanish`, …).
- **`*_r`**, runs an `Rscript` subprocess on each worker, wrapping a third-party R library (`tm`, `syuzhet`, `radvertools`, …).

Both flavours produce identically-shaped results; you pick based on which third-party tooling you trust for the domain at hand. See [Algorithm families](/docs/concepts/algorithm-families) for the dispatch story.

## When to use it

Whistlerlib is built for the case where your dataset is too large for a single-process pandas workflow but doesn't need a Spark cluster. Typical use:

- Tweet / post corpora with millions to hundreds-of-millions of rows.
- A small Dask cluster (one scheduler, a handful of workers) running on a researcher's lab machines or a few cloud VMs.
- Pipeline output you want to slot into downstream pandas / Jupyter analysis.

If you only have a few thousand rows, pandas + the underlying libraries (advertools, nltk, igraph) are simpler. If you have petabyte-scale data, look at Spark or Ray.

## 30-second tour

```python
from whistlerlib import Context

# Connect a client to a running Dask scheduler.
ctx = Context('processes', '127.0.0.1', 8786)

# Wrap a CSV in a 8-partition Dask DataFrame.
ds = ctx.load_csv(
    filen='posts.csv',
    meta={
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    },
    num_partitions=8,
)

# Top-5 hashtags, distributed.
top5 = ds.hashtag_histogram_alt_python(k=5)
print(top5)
```

The full quickstart, including how to spin up a local cluster with Docker Compose, lives in [Tutorial 01](/docs/tutorials/01-quickstart-hashtag-histogram).

## Next steps

- **Install**: [pip](/docs/installation/pip) (client) or [Docker](/docs/installation/docker) (cluster).
- **Learn the model**: [Architecture](/docs/concepts/architecture), [Context & datasets](/docs/concepts/context-and-datasets), [Algorithm families](/docs/concepts/algorithm-families).
- **Run something**: [Tutorials](/docs/tutorials/), seven runnable end-to-end examples.
- **Upgrade from 0.1.0**: [Migration guide](/docs/migration/from-0.1.0).

## License

GPL-3.0-or-later. See the [LICENSE file](https://github.com/observatoriogeo/whistlerlib/blob/main/LICENSE).
