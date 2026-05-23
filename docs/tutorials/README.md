# Tutorials

Seven runnable end-to-end examples, ordered from simplest to most involved. Each pairs a `TweetDataset` method with the kind of input it expects and shows the actual output you'll see.

| # | Tutorial | Method exercised | Notes |
|---|---|---|---|
| 01 | [Quickstart: top hashtags](01-quickstart-hashtag-histogram.md) | `hashtag_histogram_alt_python` | Minimum viable usage. Start here. |
| 02 | [Mention histogram](02-mention-histogram.md) | `mention_histogram_alt_python` | Same shape as #01 but for `@user` tokens. |
| 03 | [Bilingual n-grams](03-ngram-histogram-bilingual.md) | `ngram_histogram_alt_python` with `lan='spanish'` / `lan='english'` | Stopword handling per language. |
| 04 | [Spanish sentiment range](04-sentiment-spanish.md) | `sentiment_range_spanish_alt_python` | **`slow`**: loads a TensorFlow model. |
| 05 | [Hashtag co-occurrence network](05-hashtag-coonet.md) | `hashtag_weighted_coonet` | Returns an `igraph.Graph`. |
| 06 | [Mention co-occurrence network](06-mention-coonet.md) | `mention_weighted_coonet` | Same as #05, on mentions. |
| 07 | [R-bridge: top hashtags](07-r-bridge-mfhashtags.md) | `hashtag_histogram_r` | The R-bridge path. Worker container only. |

> **The pages here are auto-generated** from each `examples/<slug>/README.md` by [`scripts/sync_tutorials.py`](../../scripts/sync_tutorials.py). Edit the source README; CI fails on drift.

## How to read them

Each tutorial has the same three sections:

1. **What you'll see**: the actual stdout the example prints, so you can match it against your run.
2. **How it works**: the call chain from `TweetDataset` method down through `base_algs`.
3. **Run it**: exact shell commands for both manual and pytest-managed runs.

## Prerequisites

- Whistlerlib installed on the client (see [Install from PyPI](../installation/pip.md)).
- A running Whistlerlib cluster on `localhost:8786` (see [Install with Docker](../installation/docker.md)).
- For tutorial 07: the cluster must be running the `observatoriogeo/whistlerlib` image (R lives only there).

## Related

- [Algorithm families](../concepts/algorithm-families.md), which method routes to which base primitive.
- [Architecture](../concepts/architecture.md), what runs where.
