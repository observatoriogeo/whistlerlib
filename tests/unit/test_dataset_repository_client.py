"""Unit tests for `whistlerlib.clients.dataset_repository.dataset_repository_client`.

The loader wraps `dask.dataframe.read_csv` with whistlerlib's meta format.
Tests use a tiny temp CSV (no Dask cluster, no network).
"""

import pandas as pd
import pytest

from whistlerlib.clients.dataset_repository.dataset_repository_client import (
    DATASET_FILE_FORMAT,
    DatasetRepositoryClient,
)


@pytest.fixture
def tiny_csv(tmp_path):
    p = tmp_path / 'tiny.csv'
    pd.DataFrame({
        'Date': ['2022-01-01', '2022-01-02', '2022-01-03'],
        'text': ['hello', 'world', 'foo bar'],
        'unused_col': ['a', 'b', 'c'],
    }).to_csv(p, index=False)
    return str(p)


def test_format_constants():
    assert DATASET_FILE_FORMAT.CSV == 'CSV'
    assert DATASET_FILE_FORMAT.PARQUET == 'Parquet'


def test_init_is_a_noop():
    # Constructor takes no args; just instantiates.
    c = DatasetRepositoryClient()
    assert c is not None


def test_load_csv_returns_dask_dataframe(tiny_csv):
    import dask.dataframe as dd
    c = DatasetRepositoryClient()
    meta = {
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    }
    out = c.load_csv(tiny_csv, meta)
    assert isinstance(out, dd.DataFrame)


def test_load_csv_only_reads_requested_columns(tiny_csv):
    c = DatasetRepositoryClient()
    meta = {
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    }
    out = c.load_csv(tiny_csv, meta)
    pdf = out.compute()
    # The third column from the source CSV must NOT be present — `usecols`
    # filters to just date + text.
    assert set(pdf.columns) == {'Date', 'text'}


def test_load_csv_parses_dates(tiny_csv):
    c = DatasetRepositoryClient()
    meta = {
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    }
    pdf = c.load_csv(tiny_csv, meta).compute()
    # Date column must be datetime, not str.
    assert pd.api.types.is_datetime64_any_dtype(pdf['Date'])


def test_load_csv_strips_tz(tiny_csv):
    """The loader explicitly calls `.tz_localize(None)` to prevent
    'Cannot compare tz-naive and tz-aware datetime-like objects' downstream."""
    c = DatasetRepositoryClient()
    meta = {
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    }
    pdf = c.load_csv(tiny_csv, meta).compute()
    # All timestamps should be tz-naive.
    assert pdf['Date'].dt.tz is None
