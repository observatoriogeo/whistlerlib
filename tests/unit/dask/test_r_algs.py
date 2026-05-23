"""Unit tests for `whistlerlib.dask.r_algs.algs`.

Mirrors `test_alt_python_algs.py` for the R-bridged wrappers: each
`compute_*` is a thin delegation to a `base_algs` primitive with the
per-algorithm `func` (one of the R-subprocess wrappers under
`r_algs/funcs/`). We mock the primitive and verify wiring.

The R subprocesses themselves are exercised by Phase 4's example 07
(`07-r-bridge-mfhashtags`) running in the Docker worker image.
"""

from unittest.mock import MagicMock, patch

import pandas as pd

import whistlerlib.dask.r_algs.algs as algs


_TIME_PROFILE_DF = pd.DataFrame({'stage': ['_'], 'seconds': [0.0]})
_RESULT_DF = pd.DataFrame({'_': []})


def _mock_primitive_return():
    return (_RESULT_DF, _TIME_PROFILE_DF)


def test_sentiment_meta_keys_match_column_names_keys():
    """`SENTIMENT_META` enumerates every emotion column the R script writes;
    `SENTIMENT_COL_NAMES` renames the emotion subset to title case. The
    rename map's keys must be a subset of the meta's keys."""
    assert set(algs.SENTIMENT_COL_NAMES.keys()).issubset(
        set(algs.SENTIMENT_META.keys()))
    # title-cased values look right
    assert algs.SENTIMENT_COL_NAMES['emotions.anger'] == 'Anger'
    assert algs.SENTIMENT_COL_NAMES['emotions.positive'] == 'Positive'


# --------------------------------------------------------------------------- #
# compute_hashtag_histogram (R)                                               #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_histogram')
def test_hashtag_delegates_to_vector_histogram(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    result, profile = algs.compute_hashtag_histogram(
        df=df, k=7, text_column='text',
        distributed_sorting=False, num_partitions=3,
    )

    assert result is _RESULT_DF
    assert profile is _TIME_PROFILE_DF
    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['df'] is df
    assert kwargs['k'] == 7
    assert kwargs['text_column'] == 'text'
    assert kwargs['token_col'] == 'tag'
    assert kwargs['freq_col'] == 'freq'
    assert kwargs['distributed_sorting'] is False
    assert kwargs['num_partitions'] == 3
    assert kwargs['func'] is algs.getMFHashtags


# --------------------------------------------------------------------------- #
# compute_mention_histogram (R)                                               #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_histogram')
def test_mention_delegates_to_vector_histogram(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    algs.compute_mention_histogram(
        df=df, k=2, text_column='body',
        distributed_sorting=True, num_partitions=4,
    )

    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['text_column'] == 'body'
    assert kwargs['token_col'] == 'mentions'
    assert kwargs['freq_col'] == 'Freq'
    assert kwargs['distributed_sorting'] is True
    assert kwargs['func'] is algs.getMentions


# --------------------------------------------------------------------------- #
# compute_ngram_histogram (R)                                                 #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_histogram')
def test_ngram_delegates_to_vector_histogram_with_n(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    algs.compute_ngram_histogram(
        df=df, n=3, k=10, text_column='text',
        distributed_sorting=False, num_partitions=2,
    )

    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['k'] == 10
    assert kwargs['token_col'] == 'N_Tokens'
    assert kwargs['freq_col'] == 'Freq'
    assert kwargs['func'] is algs.getNgrams
    # `n` is forwarded as a per-partition func kwarg
    assert kwargs['n'] == 3


# --------------------------------------------------------------------------- #
# compute_sentiment_histogram_and_sum                                         #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_matrix_nz_histogram_and_sum')
def test_sentiment_histogram_delegates(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    result, profile = algs.compute_sentiment_histogram_and_sum(
        df=df, text_column='text', language='spanish',
        method='nrc', num_partitions=2,
    )

    assert result is _RESULT_DF
    assert profile is _TIME_PROFILE_DF
    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['df'] is df
    assert kwargs['text_column'] == 'text'
    assert kwargs['meta'] is algs.SENTIMENT_META
    assert kwargs['col_names'] is algs.SENTIMENT_COL_NAMES
    assert kwargs['num_partitions'] == 2
    assert kwargs['func'] is algs.getSentiments
    assert kwargs['language'] == 'spanish'
    assert kwargs['method'] == 'nrc'
