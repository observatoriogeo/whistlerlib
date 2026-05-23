# 03. Bigram histograms in two languages

`ngram_histogram_alt_python` with `lan='spanish'` and `lan='english'`. Same algorithm, same dataset, but Whistlerlib passes the language down to NLTK's stopword corpus, so each call filters out a different set of common words before n-gram counting.

## What this teaches

- The `lan` argument selects which language's stopword list NLTK pulls from `corpora/stopwords/`.
- Spanish stopwords (`el`, `la`, `de`, `que`, `en`, `y`, …) leave behind content bigrams in Spanish text; English stopwords (`the`, `a`, `is`, `of`, …) leave behind content bigrams in English text.
- Running the same pipeline against the same mixed-language input twice (once per language) shows how stopword filtering shapes the resulting top-k.

## Expected output (shape)

```
Loaded 10 tweets.

Spanish top-3 bigrams:
        N_Tokens  Freq
ciudad metro       3
metro urbano       2
política cultura   2

English top-3 bigrams:
        N_Tokens  Freq
city metro         3
metro urban        2
social policy      2
```

## The code

Each row mixes Spanish and English content words so the two histograms have something to disagree about:

```python
_ROWS = [
    ('2022-01-01T00:00:00',
     'la ciudad metro the city metro urbano urban social policy'),
    ('2022-01-01T01:00:00',
     'el metro urbano de la ciudad the metro urban of the city'),
    ('2022-01-01T02:00:00',
     'ciudad metro the city metro social política social policy'),
    # ...7 more rows...
    ('2022-01-01T09:00:00',
     'política social cultura policy social culture investigación research'),
]
```

The same `ngram_histogram_alt_python` runs twice over the same `TweetDataset`, once per language:

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

spa = ds.ngram_histogram_alt_python(n=2, k=3, lan='spanish', w='word')
print(spa.to_string(index=False))

eng = ds.ngram_histogram_alt_python(n=2, k=3, lan='english', w='word')
print(eng.to_string(index=False))
```

`n=2` asks for bigrams, `k=3` for the top-3 by frequency. `w='word'` selects word n-grams (use `w='char'` for character n-grams). `lan='spanish'` and `lan='english'` pick which NLTK stopword list filters tokens before the histogram step, so the two calls see different surviving vocabularies.

The full file (including the tempfile setup and CLI shim) is at
[`examples/03-ngram-histogram-bilingual/example.py`](https://github.com/observatoriogeo/whistlerlib/blob/main/examples/03-ngram-histogram-bilingual/example.py).

## Run it

```bash
# From examples/03-ngram-histogram-bilingual/, bring up a local Dask cluster, run the example, tear it down.
docker compose -f ../../docker/docker-compose.yml up -d
python example.py
docker compose -f ../../docker/docker-compose.yml down
```
