"""Mention co-occurrence network, the mirror of example 05.

Two mentions per row, six unique accounts across ten rows; the pair
@kaggle @openai recurs four times to produce the heaviest edge.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pandas as pd

from whistlerlib import Context

_ROWS = [
    ('2022-01-01T00:00:00', 'morning brief @kaggle @openai'),
    ('2022-01-01T01:00:00', 'data dive @kaggle @openai'),
    ('2022-01-01T02:00:00', 'leaderboards @kaggle @huggingface'),
    ('2022-01-01T03:00:00', 'paper drop @openai @huggingface'),
    ('2022-01-01T04:00:00', 'ai roundup @kaggle @openai'),
    ('2022-01-01T05:00:00', 'tool tip @huggingface @kaggle'),
    ('2022-01-01T06:00:00', 'satellite update @nasa @bbc'),
    ('2022-01-01T07:00:00', 'climate dash @nasa @kaggle'),
    ('2022-01-01T08:00:00', 'newsroom note @bbc @reuters'),
    ('2022-01-01T09:00:00', 'product launch @openai @kaggle'),
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

    edges_df, graph = ds.mention_weighted_coonet()
    print(f'Graph: {graph.vcount()} nodes, {graph.ecount()} edges.')

    print('\nEdges (source, target, weight):')
    print(edges_df.to_string(index=False))

    return edges_df, graph


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
