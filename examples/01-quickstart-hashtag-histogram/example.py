"""Quickstart: top-k hashtags from a tiny tweet CSV via Whistlerlib.

The minimum-viable Whistlerlib workflow. Connects to a Dask cluster, loads
a CSV, runs `hashtag_histogram_alt_python(k=5)`, prints the result.

Run with the cluster up:

    docker compose -f ../../docker/docker-compose.yml up -d
    python example.py            # connects to localhost:8786
    python example.py host port  # explicit host/port
"""

from __future__ import annotations

import sys
import tempfile

import pandas as pd

from whistlerlib import Context

_ROWS = [
    ('2022-01-01T00:00:00', 'mañana en la ciudad #cdmx #política @gob'),
    ('2022-01-01T01:00:00', 'avances en ciencia #ciencia #datos @unam'),
    ('2022-01-01T02:00:00', 'noticias del día #noticias #cdmx @senado'),
    ('2022-01-01T03:00:00', 'reforma laboral #política #economía @scjn'),
    ('2022-01-01T04:00:00', 'investigación urbana #cdmx #urbanismo @uam'),
    ('2022-01-01T05:00:00', 'cultura digital #cultura #tecnología @ipn'),
    ('2022-01-01T06:00:00', 'salud pública #salud #noticias @imss'),
    ('2022-01-01T07:00:00', 'movilidad metropolitana #cdmx #movilidad @semovi'),
    ('2022-01-01T08:00:00', 'tendencias económicas #economía #méxico @hacienda'),
    ('2022-01-01T09:00:00', 'congreso aprueba ley #política #méxico @senado'),
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
    histogram = ds.hashtag_histogram_alt_python(k=5)
    print('\nTop 5 hashtags:')
    print(histogram.to_string(index=False))
    return histogram


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
