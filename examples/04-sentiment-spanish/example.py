"""Filter tweets by Spanish sentiment score in [0.9, 1.0].

Marked `slow` because the TensorFlow/Keras sentiment-analysis-spanish model
takes several seconds to load on each worker. Rows 0-4 carry deliberately-
positive phrases so the [0.9, 1.0] window always returns a non-empty result.
"""

from __future__ import annotations

import sys
import tempfile

import pandas as pd

from whistlerlib import Context

_ROWS = [
    ('2022-01-01T00:00:00', 'excelente maravilloso totalmente fantástico'),
    ('2022-01-01T01:00:00', 'muy bueno me encanta este trabajo magnífico'),
    ('2022-01-01T02:00:00', 'magnífico extraordinario lo mejor de todo'),
    ('2022-01-01T03:00:00', 'fantástico genial perfecto fenomenal increíble'),
    ('2022-01-01T04:00:00', 'increíble experiencia maravillosa felicidades'),
    ('2022-01-01T05:00:00', 'ciudad metro urbano social política cultura'),
    ('2022-01-01T06:00:00', 'datos análisis investigación estudio método'),
    ('2022-01-01T07:00:00', 'salud economía educación tecnología progreso'),
    ('2022-01-01T08:00:00', 'ambiente clima ecología naturaleza sostenibilidad'),
    ('2022-01-01T09:00:00', 'arte música literatura cine teatro danza'),
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
    positive = ds.sentiment_range_spanish_alt_python(left_end=0.9, right_end=1.0)
    print('\nRows scoring in [0.9, 1.0]:')
    print(positive.to_string(index=False))
    return positive


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    run(host, port)
