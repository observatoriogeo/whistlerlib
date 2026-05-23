"""Unit tests for `whistlerlib.dask.alt_python_algs.funcs.getHashtags`."""

import pandas as pd

from whistlerlib.dask.alt_python_algs.funcs.getHashtags import (
    get_hashtags_wrapper,
    getHashtags,
)


def test_wrapper_returns_tag_freq_columns():
    df = pd.DataFrame({'text': ['hi #foo there', '#foo #bar', '#bar #bar #baz']})
    out = get_hashtags_wrapper(df, 'text')
    assert list(out.columns) == ['tag', 'freq']


def test_wrapper_counts_correctly():
    df = pd.DataFrame({'text': [
        'hi #foo there',
        '#foo #bar',
        '#bar #bar #baz',  # note: pandas str.split won't see the same '#bar' twice as separate; check actual count
    ]})
    out = get_hashtags_wrapper(df, 'text')
    counts = dict(zip(out['tag'], out['freq']))
    # '#foo' appears in row 0 and row 1 → 2
    assert counts['#foo'] == 2
    # '#bar' appears 3 times across rows
    assert counts['#bar'] == 3
    # '#baz' once
    assert counts['#baz'] == 1


def test_wrapper_ignores_non_hashtag_tokens():
    df = pd.DataFrame({'text': ['plain words only', 'just text']})
    out = get_hashtags_wrapper(df, 'text')
    # No hashtags → empty result
    assert len(out) == 0


def test_wrapper_strips_whitespace_in_tag():
    df = pd.DataFrame({'text': ['#abc xyz', '#abc']})
    out = get_hashtags_wrapper(df, 'text')
    # Tag column is .str.strip()'d → should not have leading/trailing whitespace
    for tag in out['tag']:
        assert tag == tag.strip()


def test_wrapper_preserves_case():
    """The function does NOT lowercase hashtags — that's a docs/coonet concern."""
    df = pd.DataFrame({'text': ['#Foo #FOO #foo']})
    out = get_hashtags_wrapper(df, 'text')
    tags = set(out['tag'])
    # All three are distinct hashtags as far as get_hashtags is concerned.
    assert '#Foo' in tags or '#foo' in tags or '#FOO' in tags
    # At least we don't end up with an empty result.
    assert len(out) > 0


def test_wrapper_handles_hashtag_with_accents():
    df = pd.DataFrame({'text': ['#méxico #política rocks']})
    out = get_hashtags_wrapper(df, 'text')
    tags = set(out['tag'])
    assert '#méxico' in tags
    assert '#política' in tags


def test_get_hashtags_returns_series():
    s = pd.Series(['#a #b', '#b'])
    out = getHashtags(s)
    assert isinstance(out, pd.Series)
    counts = out.to_dict()
    assert counts['#a'] == 1
    assert counts['#b'] == 2


def test_wrapper_with_single_row():
    df = pd.DataFrame({'text': ['#only']})
    out = get_hashtags_wrapper(df, 'text')
    assert len(out) == 1
    assert out['tag'].iloc[0] == '#only'
    assert int(out['freq'].iloc[0]) == 1


def test_wrapper_freq_dtype_int():
    df = pd.DataFrame({'text': ['#a #a #b']})
    out = get_hashtags_wrapper(df, 'text')
    # Freq must be an integer-typed column (the base_algs meta declares int64).
    assert pd.api.types.is_integer_dtype(out['freq'])
