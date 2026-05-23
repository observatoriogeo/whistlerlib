# 07. R bridge: top hashtags via the R implementation

`hashtag_histogram_r`, the same top-k hashtag computation as example 01, but implemented in R. Whistlerlib's `r_algs` module ships small R scripts under `src/whistlerlib/dask/r_algs/funcs/`; each worker spawns an `Rscript` subprocess per partition, reads back the result via Arrow files, and merges them in pandas.

## Why an R version?

Two reasons, neither involving local R installs (R lives only in the **worker image**; see the [Architecture](https://whistlerlib.observatoriogeo.mx/docs/concepts/architecture) page for the R-bridge architecture):

1. **Comparison baseline.** The Whistlerlib paper benchmarked the alt-python implementation against the original R implementation. Both are kept in the codebase so users can reproduce that comparison.
2. **R-only libraries.** Some downstream features (notably `syuzhet`-based sentiment, used in `sentiment_histogram_and_sum_r`) only have a high-quality R implementation. The same R-bridge plumbing handles all of them.

## What you'll see

```
Loaded 10 tweets.

Top 5 hashtags (R implementation):
     tag  freq
   #news     5
#climate     4
  #space     3
   #data     2
#science     1
```

The result has the same shape as example 01, same `[tag, freq]` columns. The numbers may differ very slightly because the R tokenization rules (from the `tm` and `tidytext`-adjacent packages) aren't byte-for-byte identical to advertools.

## The code

Same inline corpus shape as tutorial 01: ten dated rows, hashtags inline in the text:

```python
_ROWS = [
    ('2022-01-01T00:00:00', 'morning briefing #news #climate'),
    ('2022-01-01T01:00:00', 'satellite imagery #news #space'),
    ('2022-01-01T02:00:00', 'rainfall report #news #climate'),
    ('2022-01-01T03:00:00', 'mars mission #space #news'),
    # ...5 more rows...
    ('2022-01-01T09:00:00', 'breaking story #science'),
]
```

The pipeline is byte-for-byte identical to tutorial 01 except for the analytic suffix:

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
histogram = ds.hashtag_histogram_r(k=5)
print(histogram.to_string(index=False))
```

`hashtag_histogram_r(k=5)` ships a per-partition closure that calls `RScriptProcess.run(...)` to spawn an `Rscript` subprocess against the corresponding R script under `src/whistlerlib/dask/r_algs/funcs/`. Inputs and outputs are exchanged via Parquet files in the worker's `tempfile` directory, and the partial frequency tables are merged in pandas by the same `compute_vector_histogram` base primitive that tutorial 01 uses. This tutorial only runs against the `albertogarob/whistlerlib` worker image; R isn't installed on the host.

The full file (including the tempfile setup and CLI shim) is at
[`examples/07-r-bridge-mfhashtags/example.py`](https://github.com/observatoriogeo/whistlerlib/blob/main/examples/07-r-bridge-mfhashtags/example.py).

## Why this needs the Docker cluster

The R-bridge code spawns `/usr/bin/Rscript <whistlerlib R script>`. `Rscript` and the R packages it loads (`tm`, `slam`, `snowballc`, `rweka`, …) live **only** inside the published `albertogarob/whistlerlib` Docker image; the host never installs R.

## Run it

```bash
# From examples/07-r-bridge-mfhashtags/, bring up a local Dask cluster, run the example, tear it down.
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
docker compose -f ../../docker/docker-compose.yml down
```
