# 05. Hashtag co-occurrence network

`hashtag_weighted_coonet` builds a weighted undirected graph where:

- **Nodes** are unique hashtags.
- **Edges** connect hashtags that co-appear in the same tweet.
- **Weights** are the number of tweets where the pair co-occurs.

The result is an [`igraph.Graph`](https://python.igraph.org/) plus a pandas DataFrame of edges, handy for direct downstream analysis (centrality, communities, layouts).

## What you'll see

```
Loaded 10 tweets.
Graph: 5 nodes, 6 edges.

Edges (source, target, weight):
source   target  weight
   #ai #climate       1
   #ai    #data       1
   #ai      #ml       2
   #ai  #python       3
 #data      #ml       1
 #data  #python       2
```

## The code

Each row carries exactly two hashtags so co-occurrences are unambiguous. The corpus mixes five hashtags across ten rows; the pair `#ai #python` recurs three times, producing the heaviest edge:

```python
_ROWS = [
    ('2022-01-01T00:00:00', 'tech roundup #ai #python'),
    ('2022-01-01T01:00:00', 'data team update #ai #python'),
    ('2022-01-01T02:00:00', 'new dataset #ai #data'),
    ('2022-01-01T03:00:00', 'ml notes #ai #ml'),
    # ...5 more rows...
    ('2022-01-01T09:00:00', 'climate paper #ai #climate'),
]
```

The analytic returns a tuple `(edge_df, graph)`, so unpacking is part of the idiom:

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

edges_df, graph = ds.hashtag_weighted_coonet()
print(f'Graph: {graph.vcount()} nodes, {graph.ecount()} edges.')
print(edges_df.to_string(index=False))
```

`hashtag_weighted_coonet()` runs a per-partition extractor that emits edge tuples for each pair of hashtags co-appearing in a row, the `compute_weighted_coonet` base primitive reduces partial edge lists and sums weights, then sorts edges and nodes locally for determinism. The pandas DataFrame `edges_df` exposes `(source, target, weight)`; the `igraph.Graph` is ready for centrality, community detection, or layout calls.

The full file (including the tempfile setup and CLI shim) is at
[`examples/05-hashtag-coonet/example.py`](https://github.com/observatoriogeo/whistlerlib/blob/main/examples/05-hashtag-coonet/example.py).

## Run it

```bash
# From examples/05-hashtag-coonet/, bring up a local Dask cluster, run the example, tear it down.
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
docker compose -f ../../docker/docker-compose.yml down
```
