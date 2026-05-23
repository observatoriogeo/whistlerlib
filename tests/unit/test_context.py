"""Unit tests for `whistlerlib.context.Context`.

The real `dask.distributed.Client` would open a network connection; the tests
patch it out so `Context()` instantiation is offline and millisecond-fast.
The `DatasetRepositoryClient` is left real because it's a trivial stateless
wrapper.
"""

from unittest.mock import patch

import pandas as pd

from whistlerlib.context import Context


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_init_creates_client_with_host_port(mock_client_cls, mock_dask_set):
    Context('processes', '127.0.0.1', 8786)
    mock_client_cls.assert_called_once_with('127.0.0.1:8786')


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_init_stores_args(mock_client_cls, mock_dask_set):
    ctx = Context('threads', '10.0.0.1', 9999)
    assert ctx.dask_scheduler == 'threads'
    assert ctx.dask_scheduler_host == '10.0.0.1'
    assert ctx.dask_scheduler_port == 9999


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_init_sets_dask_scheduler_config(mock_client_cls, mock_dask_set):
    Context('processes', '127.0.0.1', 8786)
    mock_dask_set.assert_called_with(scheduler='processes')


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_init_creates_dataset_repository_client(mock_client_cls, mock_dask_set):
    ctx = Context('processes', '127.0.0.1', 8786)
    # The DatasetRepositoryClient is real; just verify the attribute is set.
    assert ctx.dataset_repository_client is not None
    # And has a load_csv method (its only API surface today).
    assert callable(ctx.dataset_repository_client.load_csv)


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_init_does_not_create_dask_sql_context(mock_client_cls, mock_dask_set):
    """Phase 2 dropped the dask_sql surface, assert the attribute is gone."""
    ctx = Context('processes', '127.0.0.1', 8786)
    assert not hasattr(ctx, 'dask_sql_context')


@patch('dask.config.set')
@patch('dask.distributed.Client')
def test_load_csv_returns_tweet_dataset(mock_client_cls, mock_dask_set, monkeypatch):
    """`load_csv` should round-trip through `DatasetRepositoryClient.load_csv`
    and wrap the result in a `TweetDataset`. We mock the loader to return a
    minimal pandas-wrapped Dask DF."""
    import dask.dataframe as dd

    from whistlerlib.dataset import TweetDataset

    ctx = Context('processes', '127.0.0.1', 8786)

    pdf = pd.DataFrame({
        'Date': pd.to_datetime(['2022-01-01', '2022-01-02']),
        'text': ['hi', 'bye'],
    })
    ddf = dd.from_pandas(pdf, npartitions=1)
    monkeypatch.setattr(ctx.dataset_repository_client, 'load_csv',
                        lambda *a, **kw: ddf)

    result = ctx.load_csv('/dev/null',
                          meta={'column_mapping': {'date_column': 'Date',
                                                   'text_column': 'text'},
                                'file_encoding': 'utf-8'},
                          num_partitions=1)
    assert isinstance(result, TweetDataset)
    assert result.num_partitions == 1
