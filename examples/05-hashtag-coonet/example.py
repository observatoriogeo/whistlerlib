"""Hashtag co-occurrence network from a tiny tweet CSV.

The `hashtag_weighted_coonet` method builds a weighted undirected graph of
hashtag co-occurrences. We seed the dataset with paired hashtags per row so
the graph is non-trivial.
"""

from __future__ import annotations

import sys
import tempfile

import pandas as pd

from whistlerlib import Context

# Each row carries TWO hashtags so co-occurrences exist. Cyclic pairing of
# 10 hashtags across 10 rows yields a 10-node, 10-edge cycle plus the same
# hashtag pair repeated when rows share content → some edges weight 2.
_ROWS = [
    ('2022-01-01T00:00:00', 'política nacional #política #cdmx'),
    ('2022-01-01T01:00:00', 'noticias del día #cdmx #noticias'),
    ('2022-01-01T02:00:00', 'avances científicos #noticias #ciencia'),
    ('2022-01-01T03:00:00', 'investigación urbana #ciencia #datos'),
    ('2022-01-01T04:00:00', 'datos abiertos #datos #código'),
    ('2022-01-01T05:00:00', 'tecnología cívica #código #tecnología'),
    ('2022-01-01T06:00:00', 'cultura digital #tecnología #cultura'),
    ('2022-01-01T07:00:00', 'salud pública #cultura #salud'),
    ('2022-01-01T08:00:00', 'economía nacional #salud #economía'),
    ('2022-01-01T09:00:00', 'cierre del ciclo #economía #política'),
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

    edges_df, graph = ds.hashtag_weighted_coonet()
    print(f'Graph: {graph.vcount()} nodes, {graph.ecount()} edges.')

    print('\nEdges (source, target, weight):')
    print(edges_df.to_string(index=False))

    return edges_df, graph


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
