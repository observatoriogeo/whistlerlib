"""Hashtag co-occurrence network from a tiny tweet CSV.

The `hashtag_weighted_coonet` method builds a weighted undirected graph of
hashtag co-occurrences. We seed the dataset with paired hashtags per row so
the graph is non-trivial.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pandas as pd

from whistlerlib import Context

# Each row carries TWO hashtags so co-occurrences exist. The corpus uses
# five hashtags across ten rows; #ai #python recurs three times to give
# the heaviest edge.
_ROWS = [
    ('2022-01-01T00:00:00', 'tech roundup #ai #python'),
    ('2022-01-01T01:00:00', 'data team update #ai #python'),
    ('2022-01-01T02:00:00', 'new dataset #ai #data'),
    ('2022-01-01T03:00:00', 'ml notes #ai #ml'),
    ('2022-01-01T04:00:00', 'pandas tip #python #data'),
    ('2022-01-01T05:00:00', 'fine-tune diary #ai #python'),
    ('2022-01-01T06:00:00', 'research notes #ai #ml'),
    ('2022-01-01T07:00:00', 'weekend reading #data #ml'),
    ('2022-01-01T08:00:00', 'open source #python #data'),
    ('2022-01-01T09:00:00', 'climate paper #ai #climate'),
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

    edges_df, graph = ds.hashtag_weighted_coonet()
    print(f'Graph: {graph.vcount()} nodes, {graph.ecount()} edges.')

    print('\nEdges (source, target, weight):')
    print(edges_df.to_string(index=False))

    return edges_df, graph


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
