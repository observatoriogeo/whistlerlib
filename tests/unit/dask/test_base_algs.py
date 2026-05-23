"""Unit tests for `whistlerlib.dask.base_algs.algs`.

Unlike the higher-level `*_algs` modules — which we can mock-and-verify —
`base_algs` *is* the Dask pipeline (`map_partitions`, distributed
groupby/sum, conditional `nlargest` vs local `sort_values+head`). The
behaviour is the logic, so we exercise it for real against small
`dd.from_pandas` DataFrames under the **synchronous scheduler** — no
LocalCluster, no worker processes, no cluster bring-up. Each test runs
in milliseconds.
"""

from unittest.mock import MagicMock, patch

import dask
import dask.dataframe as dd
import pandas as pd
import pytest

from whistlerlib.dask.base_algs.algs import (
    compute_matrix_nz_histogram_and_sum,
    compute_vector_histogram,
    compute_vector_range,
    compute_weighted_coonet,
)


@pytest.fixture(autouse=True)
def _synchronous_scheduler():
    """Force every Dask `.compute()` in this module onto the
    in-process synchronous scheduler. No worker processes spawned."""
    with dask.config.set(scheduler='synchronous'):
        yield


# --------------------------------------------------------------------------- #
# compute_vector_histogram                                                    #
# --------------------------------------------------------------------------- #

def _hashtag_extract(df, text_column):
    """Tiny per-partition extractor matching the (token_col, freq_col) meta.
    Splits on whitespace, lowercases, keeps tokens starting with '#'."""
    rows = []
    for text in df[text_column].tolist():
        for tok in text.split():
            if tok.startswith('#'):
                rows.append({'tag': tok.lower(), 'freq': 1})
    if not rows:
        return pd.DataFrame({'tag': pd.Series(dtype='object'),
                             'freq': pd.Series(dtype='int64')})
    return pd.DataFrame(rows)


def _two_partition_ddf():
    pdf = pd.DataFrame({'text': [
        '#cdmx #politica buenas tardes',
        '#cdmx noticias del dia',
        '#datos #cdmx investigacion',
        '#ciencia #datos publicos',
    ]})
    return dd.from_pandas(pdf, npartitions=2)


def test_vector_histogram_local_sort_topk():
    df = _two_partition_ddf()
    local_df, profile = compute_vector_histogram(
        df=df, k=2, text_column='text',
        token_col='tag', freq_col='freq',
        distributed_sorting=False, num_partitions=2,
        func=_hashtag_extract,
    )
    assert list(local_df.columns) == ['tag', 'freq']
    assert len(local_df) == 2
    # #cdmx appears 3 times, #datos twice — top-2
    assert local_df.iloc[0]['tag'] == '#cdmx'
    assert local_df.iloc[0]['freq'] == 3
    assert local_df.iloc[1]['tag'] == '#datos'
    assert local_df.iloc[1]['freq'] == 2
    # time profile shape — stages threaded through
    assert {'description', 'elapsed'}.issubset(profile.columns)


def test_vector_histogram_local_sort_returns_all_when_k_zero():
    df = _two_partition_ddf()
    local_df, _ = compute_vector_histogram(
        df=df, k=0, text_column='text',
        token_col='tag', freq_col='freq',
        distributed_sorting=False, num_partitions=2,
        func=_hashtag_extract,
    )
    # 4 distinct hashtags total
    assert set(local_df['tag']) == {'#cdmx', '#politica', '#datos', '#ciencia'}
    # sorted by freq desc
    assert local_df.iloc[0]['tag'] == '#cdmx'


def test_vector_histogram_distributed_sort_topk():
    df = _two_partition_ddf()
    local_df, _ = compute_vector_histogram(
        df=df, k=2, text_column='text',
        token_col='tag', freq_col='freq',
        distributed_sorting=True, num_partitions=2,
        func=_hashtag_extract,
    )
    assert len(local_df) == 2
    top_tags = set(local_df['tag'].tolist())
    assert top_tags == {'#cdmx', '#datos'}


def test_vector_histogram_distributed_sort_returns_all_when_k_zero():
    df = _two_partition_ddf()
    local_df, _ = compute_vector_histogram(
        df=df, k=0, text_column='text',
        token_col='tag', freq_col='freq',
        distributed_sorting=True, num_partitions=2,
        func=_hashtag_extract,
    )
    assert set(local_df['tag']) == {'#cdmx', '#politica', '#datos', '#ciencia'}


# --------------------------------------------------------------------------- #
# compute_vector_range                                                        #
# --------------------------------------------------------------------------- #

def _score_extract(df, text_column, score_lookup):
    """Per-partition: emit one (text, score) row per input row using the
    provided lookup. Matches the meta {output_text_col: object,
    output_score_col: float64}."""
    return pd.DataFrame({
        'text': df[text_column].tolist(),
        'score': [score_lookup[t] for t in df[text_column].tolist()],
    })


def test_vector_range_filters_within_inclusive_bounds():
    pdf = pd.DataFrame({'text': ['a', 'b', 'c', 'd']})
    ddf = dd.from_pandas(pdf, npartitions=2)
    scores = {'a': 0.1, 'b': 0.55, 'c': 0.9, 'd': 0.95}

    local_df, _ = compute_vector_range(
        df=ddf, left_end=0.5, right_end=0.9,
        text_column='text', output_text_col='text', output_score_col='score',
        num_partitions=2,
        func=_score_extract,
        score_lookup=scores,
    )
    # only 'b' (0.55) and 'c' (0.9) fall in [0.5, 0.9]
    kept = set(local_df['text'].tolist())
    assert kept == {'b', 'c'}


def test_vector_range_empty_when_no_match():
    pdf = pd.DataFrame({'text': ['a', 'b']})
    ddf = dd.from_pandas(pdf, npartitions=1)
    local_df, _ = compute_vector_range(
        df=ddf, left_end=0.99, right_end=1.0,
        text_column='text', output_text_col='text', output_score_col='score',
        num_partitions=1,
        func=_score_extract,
        score_lookup={'a': 0.1, 'b': 0.2},
    )
    assert len(local_df) == 0


# --------------------------------------------------------------------------- #
# compute_matrix_nz_histogram_and_sum                                         #
# --------------------------------------------------------------------------- #

# Reuse a minimal slice of the SENTIMENT_META structure
_META_MATRIX = {
    'text': 'object',
    'polarity': 'int64',
    'emotions.joy': 'int64',
    'emotions.sadness': 'int64',
}
_COL_NAMES_MATRIX = {
    'emotions.joy': 'Joy',
    'emotions.sadness': 'Sadness',
}


def _emotion_extract(df, text_column):
    """Per-partition: assign canned emotion counts per row."""
    rows = []
    for txt in df[text_column].tolist():
        rows.append({
            'text': txt,
            'polarity': 1 if 'happy' in txt else -1,
            'emotions.joy': 2 if 'happy' in txt else 0,
            'emotions.sadness': 3 if 'sad' in txt else 0,
        })
    return pd.DataFrame(rows)


def test_matrix_nz_histogram_and_sum_aggregates_counts_and_sums():
    pdf = pd.DataFrame({'text': [
        'happy day', 'sad day', 'sad night', 'neutral',
    ]})
    ddf = dd.from_pandas(pdf, npartitions=2)

    stats, profile = compute_matrix_nz_histogram_and_sum(
        df=ddf, text_column='text', func=_emotion_extract,
        meta=_META_MATRIX, col_names=_COL_NAMES_MATRIX,
        num_partitions=2,
    )
    # sadness: nonzero in 2 rows, sum=6; joy: nonzero in 1 row, sum=2
    sadness = stats.loc['emotions.sadness']
    joy = stats.loc['emotions.joy']
    assert sadness['count'] == 2
    assert sadness['sum'] == 6
    assert sadness['sentiment'] == 'Sadness'
    assert joy['count'] == 1
    assert joy['sum'] == 2
    assert joy['sentiment'] == 'Joy'
    # sorted by count desc — sadness first
    assert list(stats['sentiment']) == ['Sadness', 'Joy']
    assert {'description', 'elapsed'}.issubset(profile.columns)


# --------------------------------------------------------------------------- #
# compute_weighted_coonet                                                     #
# --------------------------------------------------------------------------- #

def _edges_extract(df, text_column):
    """Per-partition: emit (source, target, weight) rows. We hand-craft
    edges to exercise dedup (groupby sum) across partitions."""
    rows = []
    for txt in df[text_column].tolist():
        pairs = txt.split('|')  # each token like "a-b"
        for p in pairs:
            s, t = p.split('-')
            rows.append({'source': s, 'target': t, 'weight': 1})
    return pd.DataFrame(rows)


def test_weighted_coonet_dedups_parallel_edges_and_sorts():
    pdf = pd.DataFrame({'text': [
        'a-b',          # partition 0 row 0
        'a-b|b-c',      # partition 0 row 1 — duplicate a-b edge
        'b-c',          # partition 1 row 0 — duplicate b-c edge
        'c-d',          # partition 1 row 1
    ]})
    ddf = dd.from_pandas(pdf, npartitions=2)

    nodes, edges, weights, edges_df, profile = compute_weighted_coonet(
        df=ddf, text_column='text',
        source_col='source', target_col='target', weight_col='weight',
        func=_edges_extract, num_partitions=2,
    )

    # 4 distinct nodes
    assert set(nodes) == {'a', 'b', 'c', 'd'}
    # nodes sorted (the function's local_nodes_df.sort_values())
    assert nodes == sorted(nodes)

    # 3 distinct edges after groupby-sum dedup
    assert len(edges) == 3
    edges_with_weight = dict(zip(edges, weights))
    assert edges_with_weight[('a', 'b')] == 2
    assert edges_with_weight[('b', 'c')] == 2
    assert edges_with_weight[('c', 'd')] == 1

    # edges_df sorted by (source, target)
    assert list(edges_df[['source', 'target']].itertuples(index=False,
                                                          name=None)) == \
        [('a', 'b'), ('b', 'c'), ('c', 'd')]

    assert {'description', 'elapsed'}.issubset(profile.columns)


def test_weighted_coonet_single_partition():
    pdf = pd.DataFrame({'text': ['x-y', 'y-z']})
    ddf = dd.from_pandas(pdf, npartitions=1)

    nodes, edges, weights, edges_df, _ = compute_weighted_coonet(
        df=ddf, text_column='text',
        source_col='source', target_col='target', weight_col='weight',
        func=_edges_extract, num_partitions=1,
    )
    assert set(nodes) == {'x', 'y', 'z'}
    assert set(edges) == {('x', 'y'), ('y', 'z')}
    assert weights == [1, 1]


# --------------------------------------------------------------------------- #
# Partition-count assertion guards                                            #
# --------------------------------------------------------------------------- #

def test_vector_histogram_asserts_partition_count_matches():
    """`base_algs.compute_vector_histogram` asserts that
    `df.map_partitions(...)` returns the same npartitions the caller
    declared. Passing the wrong count must trip the assertion."""
    df = _two_partition_ddf()  # actually 2 partitions
    with pytest.raises(AssertionError):
        compute_vector_histogram(
            df=df, k=2, text_column='text',
            token_col='tag', freq_col='freq',
            distributed_sorting=False, num_partitions=99,  # wrong
            func=_hashtag_extract,
        )


# --------------------------------------------------------------------------- #
# Logger warning branch                                                       #
# --------------------------------------------------------------------------- #

def test_vector_histogram_warns_under_distributed_sorting():
    """`distributed_sorting=True` carries a tie-ordering caveat — the
    function logs a warning each call. We assert the log fires."""
    from whistlerlib.dask.base_algs import algs as base_algs_module

    df = _two_partition_ddf()
    with patch.object(base_algs_module, 'logger') as mock_logger:
        compute_vector_histogram(
            df=df, k=1, text_column='text',
            token_col='tag', freq_col='freq',
            distributed_sorting=True, num_partitions=2,
            func=_hashtag_extract,
        )
        assert mock_logger.warn.called
        # warning text mentions the tie-ordering caveat
        warn_args = mock_logger.warn.call_args.args
        assert 'distributed_sorting' in warn_args[0]
