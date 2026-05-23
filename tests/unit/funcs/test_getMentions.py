"""Unit tests for `whistlerlib.dask.alt_python_algs.funcs.getMentions`."""

import pandas as pd

from whistlerlib.dask.alt_python_algs.funcs.getMentions import (
    get_mentions_wrapper,
    getMentions,
)


def test_wrapper_returns_expected_columns():
    df = pd.DataFrame({'text': ['hi @alice', '@bob and @alice']})
    out = get_mentions_wrapper(df, 'text')
    assert 'Mentions' in out.columns
    assert 'Frequency' in out.columns


def test_wrapper_counts_simple_case():
    df = pd.DataFrame({'text': ['hi @alice', '@bob and @alice']})
    out = get_mentions_wrapper(df, 'text')
    counts = dict(zip(out['Mentions'], out['Frequency']))
    assert counts.get('@alice') == 2
    assert counts.get('@bob') == 1


def test_wrapper_handles_no_mentions():
    df = pd.DataFrame({'text': ['plain text', 'no mentions here']})
    out = get_mentions_wrapper(df, 'text')
    # Empty DataFrame, but the columns should still exist.
    assert list(out.columns) == ['Mentions', 'Frequency']
    assert len(out) == 0


def test_getMentions_direct_call():
    s = pd.Series(['hi @x', '@x @y'])
    out = getMentions(s)
    assert 'Mentions' in out.columns
    assert 'Frequency' in out.columns


def test_wrapper_lowercases_mentions():
    """advertools normalizes mentions to lowercase — assert this stays true."""
    df = pd.DataFrame({'text': ['hi @Alice', '@alice and @ALICE']})
    out = get_mentions_wrapper(df, 'text')
    counts = dict(zip(out['Mentions'], out['Frequency']))
    # All three should collapse onto '@alice'.
    assert counts.get('@alice') == 3


def test_wrapper_distinct_mentions_per_row():
    df = pd.DataFrame({'text': ['@a @b @c', '@a', '@b @c']})
    out = get_mentions_wrapper(df, 'text')
    counts = dict(zip(out['Mentions'], out['Frequency']))
    assert counts['@a'] == 2
    assert counts['@b'] == 2
    assert counts['@c'] == 2
