# 06. Mention co-occurrence network

The mirror of example 05 but for `@user` mentions. Same coonet algorithm, same igraph result type. Useful as a clean side-by-side comparison: hashtag networks describe **topics**, mention networks describe **conversation partners**.

## What you'll see

```
Loaded 10 tweets.
Graph: 6 nodes, 6 edges.

Edges (source, target, weight):
      source   target  weight
        @bbc    @nasa       1
        @bbc @reuters       1
@huggingface  @kaggle       2
@huggingface  @openai       1
     @kaggle    @nasa       1
     @kaggle  @openai       4
```

## The code

Two mentions per row, six unique accounts across ten rows; the pair `@kaggle @openai` recurs four times, dominating the edge weights:

```python
_ROWS = [
    ('2022-01-01T00:00:00', 'morning brief @kaggle @openai'),
    ('2022-01-01T01:00:00', 'data dive @kaggle @openai'),
    ('2022-01-01T02:00:00', 'leaderboards @kaggle @huggingface'),
    ('2022-01-01T03:00:00', 'paper drop @openai @huggingface'),
    # ...5 more rows...
    ('2022-01-01T09:00:00', 'product launch @openai @kaggle'),
]
```

Identical workflow to tutorial 05, swap `hashtag_weighted_coonet` for `mention_weighted_coonet`:

```python
from whistlerlib import Context

ctx = Context('processes', 'localhost', 8786)
ds = ctx.load_csv(
    filen=csv_path,
    meta={
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    },
    num_partitions=2,
)
print(f'Loaded {ds.tweet_count()} tweets.')

edges_df, graph = ds.mention_weighted_coonet()
print(f'Graph: {graph.vcount()} nodes, {graph.ecount()} edges.')
print(edges_df.to_string(index=False))
```

`mention_weighted_coonet()` returns a tuple `(edge_df, graph)` just like its hashtag sibling. The per-partition extractor pulls mentions instead of hashtags, but the reducer (`compute_weighted_coonet`) and the `igraph.Graph` construction are shared code paths. Hashtag networks describe topics; mention networks describe conversation partners.

The full file (including the tempfile setup and CLI shim) is at
[`examples/06-mention-coonet/example.py`](https://github.com/observatoriogeo/whistlerlib/blob/main/examples/06-mention-coonet/example.py).

## Run it

```bash
# From examples/06-mention-coonet/, bring up a local Dask cluster, run the example, tear it down.
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
docker compose -f ../../docker/docker-compose.yml down
```
