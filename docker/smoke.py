"""Phase-5 smoke test for the Whistlerlib Docker images.

Connects to a running Dask scheduler, loads a tiny synthetic CSV, and runs
representative alt-python algorithms. If the R env vars are set (i.e. we're
running inside the master or worker image), also exercises one R-bridge call.

Designed to run inside the published images:

    docker compose -f docker/docker-compose.yml up -d
    docker compose -f docker/docker-compose.yml \\
        run --rm worker python /app/smoke.py master 8786

Exit codes:
    0, all assertions passed
    1, anything raised
"""

from __future__ import annotations

import os
import sys
import tempfile

import pandas as pd

from whistlerlib import Context


def _write_synthetic_csv() -> str:
    """10-row CSV, 10 distinct hashtags, 10 distinct mentions, matches the
    `tests/conftest.py` pattern but inlined so this script has no test deps."""
    rows = [
        (f'2022-01-01T{i:02d}:00:00',
         f'texto investigación ciencia datos análisis estudio #h{i:02d} #t{i:02d} @u{i:02d} @v{i:02d}')
        for i in range(10)
    ]
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                    delete=False, encoding='utf-8')
    pd.DataFrame(rows, columns=['Date', 'text']).to_csv(f.name, index=False)
    f.close()
    return f.name


def run_smoke(scheduler_host: str, scheduler_port: int) -> None:
    csv_path = _write_synthetic_csv()
    meta = {
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    }

    print(f'[smoke] Connecting to Dask scheduler at {scheduler_host}:{scheduler_port}')
    ctx = Context('processes', scheduler_host, scheduler_port)

    print(f'[smoke] Loading {csv_path}')
    ds = ctx.load_csv(filen=csv_path, meta=meta, num_partitions=1)

    count = ds.tweet_count()
    print(f'[smoke] tweet_count: {count}')
    assert count == 10, f'expected 10 rows, got {count}'

    print('[smoke] hashtag_histogram_alt_python(k=3):')
    hist = ds.hashtag_histogram_alt_python(k=3)
    print(hist)
    assert len(hist) == 3, f'expected k=3 rows, got {len(hist)}'

    print('[smoke] mention_histogram_alt_python(k=3):')
    hist = ds.mention_histogram_alt_python(k=3)
    print(hist)
    assert len(hist) == 3

    print('[smoke] hashtag_weighted_coonet():')
    df, graph = ds.hashtag_weighted_coonet()
    print(f'  graph: {graph.vcount()} nodes, {graph.ecount()} edges')
    assert graph.vcount() > 0 and graph.ecount() > 0

    # R bridge, only runs inside the master/worker Docker images (or any
    # environment where both WHISTLERLIB_R_* env vars are set AND the R
    # libraries listed in the Dockerfiles are installed).
    if os.getenv('WHISTLERLIB_R_PATH') and os.getenv('WHISTLERLIB_R_SCRIPTS_PATH'):
        print('[smoke] R bridge env vars detected, exercising hashtag_histogram_r(k=3):')
        hist = ds.hashtag_histogram_r(k=3)
        print(hist)
        assert len(hist) == 3, f'expected k=3 R rows, got {len(hist)}'
    else:
        print('[smoke] WHISTLERLIB_R_* env vars not set, skipping R-bridge check')

    print('[smoke] PASSED')


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'master'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8786
    try:
        run_smoke(host, port)
    except Exception as exc:
        print(f'[smoke] FAILED: {type(exc).__name__}: {exc}', file=sys.stderr)
        raise SystemExit(1)
