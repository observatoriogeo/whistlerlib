# 04. Spanish sentiment (positive range)

`sentiment_range_spanish_alt_python(left_end=0.9, right_end=1.0)`, selects rows whose Spanish text scores ≥0.9 from the [`sentiment-analysis-spanish`](https://pypi.org/project/sentiment-analysis-spanish/) TensorFlow/Keras model. The model is small but loading and running it is several seconds, so this example is marked `slow` in addition to `docker`.

## What you'll see

```
Loaded 10 tweets.

Rows scoring in [0.9, 1.0]:
                              text   score
   excelente maravilloso fantástico  0.987
       muy bueno me encanta totalmente  0.974
   magnífico extraordinario lo mejor  0.962
```

(Exact scores will vary slightly between runs, the model isn't deterministic across TF versions.)

## The code

Rows 0 to 4 carry deliberately positive Spanish phrases so the `[0.9, 1.0]` window always returns a non-empty result; rows 5 to 9 are neutral fillers:

```python
_ROWS = [
    ('2022-01-01T00:00:00', 'excelente maravilloso totalmente fantástico'),
    ('2022-01-01T01:00:00', 'muy bueno me encanta este trabajo magnífico'),
    ('2022-01-01T02:00:00', 'magnífico extraordinario lo mejor de todo'),
    ('2022-01-01T03:00:00', 'fantástico genial perfecto fenomenal increíble'),
    ('2022-01-01T04:00:00', 'increíble experiencia maravillosa felicidades'),
    ('2022-01-01T05:00:00', 'ciudad metro urbano social política cultura'),
    # ...4 more neutral rows...
]
```

Unlike the histogram tutorials, this analytic returns rows rather than a top-k:

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
positive = ds.sentiment_range_spanish_alt_python(left_end=0.9, right_end=1.0)
print(positive.to_string(index=False))
```

`sentiment_range_spanish_alt_python(left_end, right_end)` cleans each row's text (URL, mention, hashtag, punctuation, stopword removal), feeds it to `SentimentAnalysisSpanish().sentiment(...)` (a TensorFlow/Keras model from the [`sentiment-analysis-spanish`](https://pypi.org/project/sentiment-analysis-spanish/) package, score in `[0, 1]`), keeps rows whose score falls in `[left_end, right_end]`, and `.compute()`s the survivors to a pandas DataFrame. The model is lazily loaded on each worker the first time the partition closure runs; that's why this tutorial carries the `slow` marker in addition to `docker`.

The full file (including the tempfile setup and CLI shim) is at
[`examples/04-sentiment-spanish/example.py`](https://github.com/observatoriogeo/whistlerlib/blob/main/examples/04-sentiment-spanish/example.py).

## Run it

*First run downloads the sentiment-analysis-spanish model and may take a couple of minutes; subsequent runs reuse the cached weights.*

```bash
# From examples/04-sentiment-spanish/, bring up a local Dask cluster, run the example, tear it down.
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
docker compose -f ../../docker/docker-compose.yml down
```
