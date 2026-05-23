"""Unit tests for `whistlerlib.dataset.TweetDataset`.

These verify the orchestration layer in isolation: constructor wiring,
partition arithmetic, range/group helpers. Algorithm modules (`r_algs`,
`alt_python_algs`, `coonet_algs`) are exercised by the integration suite;
here they're mocked so each unit test runs in <100ms.
"""

from unittest.mock import patch

import dask.dataframe as dd
import pandas as pd
import pytest

from whistlerlib.dataset import TweetDataset

_META = {
    'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
    'file_encoding': 'utf-8',
}


def _tiny_ddf(npartitions=1):
    pdf = pd.DataFrame({
        'Date': pd.to_datetime(['2022-01-01', '2022-01-02',
                                '2022-01-03', '2022-01-04']),
        'text': ['hi', 'bye', 'foo', 'bar'],
    })
    return dd.from_pandas(pdf, npartitions=npartitions)


def test_init_stores_metadata():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    assert ds.text_column == 'text'
    assert ds.date_column == 'Date'
    assert ds.num_partitions == 1
    assert ds.ranged is False


def test_init_ranged_args():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1,
                      ranged=True, range_start_date='2022-01-01',
                      range_end_date='2022-01-31')
    assert ds.ranged is True
    assert ds.range_start_date == '2022-01-01'
    assert ds.range_end_date == '2022-01-31'


def test_init_no_dask_sql_context_param():
    """Phase 2 removed `dask_sql_context`/`query_result`/`query` ctor args.
    Passing them must now error."""
    with pytest.raises(TypeError):
        TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1,
                     dask_sql_context=object())  # type: ignore[call-arg]


def test_no_run_query_method():
    """Phase 2 deleted the SQL surface entirely."""
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    assert not hasattr(ds, 'run_query')


def test_tweet_count_matches_df_length():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    assert ds.tweet_count() == 4


def test_repartition_updates_state():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(npartitions=1),
                      num_partitions=1)
    ds.repartition(2)
    assert ds.num_partitions == 2
    assert ds.dask_df.npartitions == 2


def test_get_num_partitions_asserts_consistency():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(npartitions=2),
                      num_partitions=2)
    assert ds.get_num_partitions() == 2


def test_range_by_dates_returns_new_dataset():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    ranged = ds.range_by_dates(pd.Timestamp('2022-01-02'),
                               pd.Timestamp('2022-01-03'))
    assert isinstance(ranged, TweetDataset)
    assert ranged.ranged is True
    assert ranged.range_start_date == pd.Timestamp('2022-01-02')
    # New TweetDataset must NOT inherit removed-in-Phase-2 attributes.
    assert not hasattr(ranged, 'dask_sql_context')


def test_group_by_date_returns_dataframe():
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    out = ds.group_by_date()
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ['Date', 'Count']


@patch('whistlerlib.dataset.alt_python_algs.compute_hashtag_histogram')
def test_hashtag_histogram_alt_python_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'tag': ['#x'], 'freq': [1]}),
                                 pd.DataFrame())
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    result = ds.hashtag_histogram_alt_python(k=5)
    mock_compute.assert_called_once()
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['k'] == 5
    assert kwargs['text_column'] == 'text'
    assert list(result.columns) == ['tag', 'freq']


@patch('whistlerlib.dataset.alt_python_algs.compute_hashtag_histogram')
def test_return_time_profile_passes_through(mock_compute):
    fake_profile = pd.DataFrame({'step': ['a'], 'seconds': [0.1]})
    mock_compute.return_value = (pd.DataFrame(), fake_profile)
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    df, profile = ds.hashtag_histogram_alt_python(k=5, return_time_profile=True)
    assert profile is fake_profile


@patch('whistlerlib.dataset.coonet_algs.compute_hashtag_weighted_coonet')
def test_hashtag_weighted_coonet_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame(), object(), pd.DataFrame())
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    df, graph = ds.hashtag_weighted_coonet()
    mock_compute.assert_called_once()


@patch('whistlerlib.dataset.r_algs.compute_sentiment_histogram_and_sum')
def test_sentiment_histogram_and_sum_r_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'count': [1]}), pd.DataFrame())
    ds = TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)
    ds.sentiment_histogram_and_sum_r(language='spanish', method='nrc')
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['language'] == 'spanish'
    assert kwargs['method'] == 'nrc'


# --- exhaustive algorithm-method delegation tests ------------------------------
# Each method's body is ~9 lines of plumbing (call delegate, branch on
# return_time_profile, return). The tests below give each method one mocked
# call so the orchestration plumbing is fully covered.

def _make_ds():
    return TweetDataset(ds_metadata=_META, dask_df=_tiny_ddf(), num_partitions=1)


@patch('whistlerlib.dataset.r_algs.compute_hashtag_histogram')
def test_hashtag_histogram_r_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'tag': ['#x'], 'freq': [1]}),
                                 pd.DataFrame())
    out = _make_ds().hashtag_histogram_r(k=3, distributed_sorting=True)
    assert list(out.columns) == ['tag', 'freq']
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['k'] == 3 and kwargs['distributed_sorting'] is True


@patch('whistlerlib.dataset.r_algs.compute_mention_histogram')
def test_mention_histogram_r_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'tag': ['@x'], 'freq': [1]}),
                                 pd.DataFrame())
    _make_ds().mention_histogram_r(k=3)
    mock_compute.assert_called_once()


@patch('whistlerlib.dataset.alt_python_algs.compute_mention_histogram')
def test_mention_histogram_alt_python_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'Mentions': ['@x'],
                                               'Frequency': [1]}),
                                 pd.DataFrame())
    _make_ds().mention_histogram_alt_python(k=3)
    mock_compute.assert_called_once()


@patch('whistlerlib.dataset.r_algs.compute_ngram_histogram')
def test_ngram_histogram_r_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'N_Tokens': ['a b'], 'Freq': [1]}),
                                 pd.DataFrame())
    _make_ds().ngram_histogram_r(n=2, k=3)
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['n'] == 2


@patch('whistlerlib.dataset.alt_python_algs.compute_ngram_histogram')
def test_ngram_histogram_alt_python_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'N_Tokens': ['a b'], 'Freq': [1]}),
                                 pd.DataFrame())
    _make_ds().ngram_histogram_alt_python(n=2, k=3, lan='spanish', w='word')
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['lan'] == 'spanish'
    assert kwargs['w'] == 'word'


@patch('whistlerlib.dataset.alt_python_algs.compute_sentiment_range_spanish')
def test_sentiment_range_spanish_alt_python_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame({'text': ['x'], 'score': [0.95]}),
                                 pd.DataFrame())
    _make_ds().sentiment_range_spanish_alt_python(left_end=0.9, right_end=1.0)
    kwargs = mock_compute.call_args.kwargs
    assert kwargs['left_end'] == 0.9 and kwargs['right_end'] == 1.0


@patch('whistlerlib.dataset.coonet_algs.compute_mention_weighted_coonet')
def test_mention_weighted_coonet_delegates(mock_compute):
    mock_compute.return_value = (pd.DataFrame(), object(), pd.DataFrame())
    df, graph = _make_ds().mention_weighted_coonet()
    mock_compute.assert_called_once()


# --- return_time_profile=True branch on every algorithm method ----------------

@pytest.mark.parametrize('method,patched,extra_kwargs', [
    ('hashtag_histogram_r', 'r_algs.compute_hashtag_histogram', {'k': 1}),
    ('mention_histogram_r', 'r_algs.compute_mention_histogram', {'k': 1}),
    ('ngram_histogram_r', 'r_algs.compute_ngram_histogram', {'n': 1, 'k': 1}),
    ('hashtag_histogram_alt_python', 'alt_python_algs.compute_hashtag_histogram', {'k': 1}),
    ('mention_histogram_alt_python', 'alt_python_algs.compute_mention_histogram', {'k': 1}),
    ('ngram_histogram_alt_python', 'alt_python_algs.compute_ngram_histogram',
     {'n': 1, 'k': 1, 'lan': 'spanish', 'w': 'word'}),
    ('sentiment_range_spanish_alt_python',
     'alt_python_algs.compute_sentiment_range_spanish',
     {'left_end': 0.0, 'right_end': 1.0}),
    ('sentiment_histogram_and_sum_r',
     'r_algs.compute_sentiment_histogram_and_sum',
     {'language': 'spanish', 'method': 'nrc'}),
])
def test_return_time_profile_true_branch(method, patched, extra_kwargs):
    profile = pd.DataFrame({'step': ['x']})
    with patch(f'whistlerlib.dataset.{patched}',
               return_value=(pd.DataFrame(), profile)):
        df, p = getattr(_make_ds(), method)(return_time_profile=True, **extra_kwargs)
    assert p is profile
