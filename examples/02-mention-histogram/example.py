"""Top-k mentions from a tiny tweet CSV via Whistlerlib.

The mirror of example 01 but for `@user` mentions. advertools normalizes
mentions to lowercase, so `@Alice` and `@ALICE` collapse to `@alice`.
"""

from __future__ import annotations

import sys
import tempfile

import pandas as pd

from whistlerlib import Context

_ROWS = [
    ('2022-01-01T00:00:00', 'tema legislativo @Senado @unam @gob'),
    ('2022-01-01T01:00:00', 'investigación universitaria @unam @ipn'),
    ('2022-01-01T02:00:00', 'noticias @senado @scjn'),
    ('2022-01-01T03:00:00', 'políticas públicas @gob @hacienda'),
    ('2022-01-01T04:00:00', 'educación superior @unam @uam'),
    ('2022-01-01T05:00:00', 'cultura y arte @cultura @ipn'),
    ('2022-01-01T06:00:00', 'salud pública @imss @issste'),
    ('2022-01-01T07:00:00', 'movilidad urbana @semovi @adip'),
    ('2022-01-01T08:00:00', 'economía nacional @hacienda @economia'),
    ('2022-01-01T09:00:00', 'derechos del consumidor @profeco @gob'),
]


def _write_csv() -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False,
                                    encoding='utf-8')
    pd.DataFrame(_ROWS, columns=['Date', 'text']).to_csv(f.name, index=False)
    f.close()
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
    histogram = ds.mention_histogram_alt_python(k=5)
    print('\nTop 5 mentions:')
    print(histogram.to_string(index=False))
    return histogram


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
