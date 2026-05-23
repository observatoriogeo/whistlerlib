"""Bigram histograms in Spanish and English over the same dataset.

Same algorithm (`ngram_histogram_alt_python`), same data, but different
`lan=` arguments produce different top-k bigrams because each language's
stopword list filters different tokens before the histogram step.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pandas as pd

from whistlerlib import Context

# Mixed-language content. Spanish + English content words appear together
# so that for the Spanish call the Spanish words remain (English stopwords
# are NOT in the Spanish corpus, but English content words ARE, and vice
# versa). Stopwords for each language are filtered out.
_ROWS = [
    ('2022-01-01T00:00:00',
     'la ciudad metro the city metro urbano urban social policy'),
    ('2022-01-01T01:00:00',
     'el metro urbano de la ciudad the metro urban of the city'),
    ('2022-01-01T02:00:00',
     'ciudad metro the city metro social política social policy'),
    ('2022-01-01T03:00:00',
     'investigación urbana metro urban research city metro'),
    ('2022-01-01T04:00:00',
     'el ciudad metro the city metro de research investigación'),
    ('2022-01-01T05:00:00',
     'política cultura urbana urban culture city ciudad'),
    ('2022-01-01T06:00:00',
     'metro urbano urban policy social cultura política'),
    ('2022-01-01T07:00:00',
     'data análisis datos analysis estudio research study'),
    ('2022-01-01T08:00:00',
     'urbano metro ciudad cultura urban metro city culture'),
    ('2022-01-01T09:00:00',
     'política social cultura policy social culture investigación research'),
]


def _write_csv() -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False,
                                    encoding='utf-8')
    pd.DataFrame(_ROWS, columns=['Date', 'text']).to_csv(f.name, index=False)
    f.close()
    # Make the tempfile readable from inside the worker container, which
    # runs as a different user but sees host /tmp via the compose volume mount.
    os.chmod(f.name, 0o644)
    return f.name


def run(scheduler_host: str = 'localhost', scheduler_port: int = 8786):
    csv_path = _write_csv()
    ctx = Context('processes', scheduler_host, scheduler_port)
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
    print('\nSpanish top-3 bigrams:')
    print(spa.to_string(index=False))

    eng = ds.ngram_histogram_alt_python(n=2, k=3, lan='english', w='word')
    print('\nEnglish top-3 bigrams:')
    print(eng.to_string(index=False))

    return spa, eng


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
