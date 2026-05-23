"""Top-k hashtags via the R bridge (`hashtag_histogram_r`).

The same task as example 01, computed by R scripts running inside the
whistlerlib/worker Docker image. R + the R libraries (tm, slam, snowballc, …)
live ONLY in the worker image, your dev host doesn't need any R install.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pandas as pd

from whistlerlib import Context

_ROWS = [
    ('2022-01-01T00:00:00', 'política y cdmx #política #cdmx'),
    ('2022-01-01T01:00:00', 'noticias urbanas #cdmx #noticias'),
    ('2022-01-01T02:00:00', 'investigación científica #ciencia #datos'),
    ('2022-01-01T03:00:00', 'reforma política #política #economía'),
    ('2022-01-01T04:00:00', 'cultura mexicana #cultura #méxico'),
    ('2022-01-01T05:00:00', 'salud pública #salud #noticias'),
    ('2022-01-01T06:00:00', 'movilidad metropolitana #cdmx #movilidad'),
    ('2022-01-01T07:00:00', 'datos abiertos #datos #código'),
    ('2022-01-01T08:00:00', 'tecnología cívica #tecnología #cultura'),
    ('2022-01-01T09:00:00', 'congreso aprueba ley #política #méxico'),
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
    histogram = ds.hashtag_histogram_r(k=5)
    print('\nTop 5 hashtags (R implementation):')
    print(histogram.to_string(index=False))
    return histogram


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
