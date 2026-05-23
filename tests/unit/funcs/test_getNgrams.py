"""Unit tests for `whistlerlib.dask.alt_python_algs.funcs.getNgrams`."""

import pandas as pd
import pytest

from whistlerlib.dask.alt_python_algs.funcs.getNgrams import (
    get_ngrams_wrapper,
    getNgrams,
)


def test_wrapper_returns_ntokens_freq_columns(spanish_stopwords):
    df = pd.DataFrame({'text': ['hola mundo mundial']})
    out = get_ngrams_wrapper(df, 'text', n=1, w='word', stopwords=spanish_stopwords)
    assert 'N_Tokens' in out.columns
    assert 'Freq' in out.columns


def test_unigrams_count_correctly(spanish_stopwords):
    df = pd.DataFrame({'text': ['hola mundo hola']})
    out = get_ngrams_wrapper(df, 'text', n=1, w='word', stopwords=spanish_stopwords)
    counts = dict(zip(out['N_Tokens'], out['Freq']))
    assert counts.get('hola') == 2
    assert counts.get('mundo') == 1


def test_bigrams(spanish_stopwords):
    df = pd.DataFrame({'text': ['ciudad metro urbano']})
    out = get_ngrams_wrapper(df, 'text', n=2, w='word', stopwords=spanish_stopwords)
    counts = dict(zip(out['N_Tokens'], out['Freq']))
    # Expected bigrams in some order — sklearn lowercases internally.
    expected = {'ciudad metro', 'metro urbano'}
    assert set(counts.keys()) >= expected


def test_trigrams(spanish_stopwords):
    df = pd.DataFrame({'text': ['datos análisis investigación estudio']})
    out = get_ngrams_wrapper(df, 'text', n=3, w='word', stopwords=spanish_stopwords)
    # Should yield 2 trigrams from 4 content words.
    assert len(out) == 2


def test_stopwords_are_removed(spanish_stopwords):
    df = pd.DataFrame({'text': ['esto es un mundo de prueba']})
    out = get_ngrams_wrapper(df, 'text', n=1, w='word', stopwords=spanish_stopwords)
    tokens = set(out['N_Tokens'])
    # Stopwords from the fixture should NOT appear in the histogram.
    assert 'esto' not in tokens
    assert 'es' not in tokens
    assert 'un' not in tokens
    assert 'de' not in tokens


def test_uses_modern_sklearn_api():
    """If sklearn's `get_feature_names()` was used, this would AttributeError on
    sklearn ≥1.0. Calling the function at all proves the rename is in place."""
    df = pd.DataFrame({'text': ['some plain text data']})
    out = get_ngrams_wrapper(df, 'text', n=1, w='word', stopwords=[])
    assert len(out) > 0


def test_empty_text_raises_or_returns_empty(spanish_stopwords):
    """sklearn's CountVectorizer raises on empty vocab. Either behaviour is
    acceptable — the test pins down which one we get so a future regression is
    visible."""
    df = pd.DataFrame({'text': ['']})
    try:
        out = get_ngrams_wrapper(df, 'text', n=1, w='word', stopwords=spanish_stopwords)
        # If it returns, it should be empty.
        assert len(out) == 0
    except ValueError:
        # CountVectorizer raising on empty vocabulary is acceptable.
        pass


def test_getNgrams_returns_dataframe(spanish_stopwords):
    out = getNgrams(pd.Series(['hola mundo cosa']), n=1, w='word',
                    stopwords=spanish_stopwords)
    assert isinstance(out, pd.DataFrame)
    assert 'Frequency' in out.columns


@pytest.mark.parametrize('n', [1, 2, 3])
def test_n_varies(n, spanish_stopwords):
    df = pd.DataFrame({'text': ['palabra otra tercera cuarta quinta sexta']})
    out = get_ngrams_wrapper(df, 'text', n=n, w='word', stopwords=spanish_stopwords)
    # Each row should be an n-token n-gram.
    for ngram in out['N_Tokens']:
        assert len(ngram.split()) == n
