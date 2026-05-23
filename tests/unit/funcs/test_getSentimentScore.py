"""Unit tests for `whistlerlib.dask.alt_python_algs.funcs.getSentimentScore`.

The TensorFlow-based `SentimentAnalysisSpanish` model is mocked out via the
`fake_sentiment` fixture so these tests run in milliseconds, not 30+ seconds.
"""

import pandas as pd

from whistlerlib.dask.alt_python_algs.funcs.getSentimentScore import (
    get_sentiment_score_wrapper,
    getSentimentScore,
)


def test_wrapper_renames_to_text_and_score(fake_sentiment, spanish_stopwords):
    df = pd.DataFrame({'text': ['esto es bueno', 'otra cosa más']})
    out = get_sentiment_score_wrapper(df, 'text',
                                      stopwords=spanish_stopwords,
                                      sentiment=fake_sentiment)
    assert 'text' in out.columns
    assert 'score' in out.columns


def test_wrapper_applies_clean_then_sentiment(fake_sentiment, spanish_stopwords):
    df = pd.DataFrame({'text': ['HOLA MUNDO #fun @bob']})
    out = get_sentiment_score_wrapper(df, 'text',
                                      stopwords=spanish_stopwords,
                                      sentiment=fake_sentiment)
    # The cleaned text, lowercased, hashtag + mention stripped.
    cleaned = out['text'].iloc[0]
    assert '@bob' not in cleaned
    assert '#fun' not in cleaned
    assert cleaned == cleaned.lower()


def test_wrapper_scores_match_fake_return(fake_sentiment, spanish_stopwords):
    df = pd.DataFrame({'text': ['palabra', 'otra', 'tercera']})
    out = get_sentiment_score_wrapper(df, 'text',
                                      stopwords=spanish_stopwords,
                                      sentiment=fake_sentiment)
    # Fake returns 0.5 for every input.
    assert (out['score'] == 0.5).all()


def test_wrapper_invokes_sentiment_per_row(fake_sentiment, spanish_stopwords):
    df = pd.DataFrame({'text': ['uno', 'dos', 'tres']})
    get_sentiment_score_wrapper(df, 'text',
                                stopwords=spanish_stopwords,
                                sentiment=fake_sentiment)
    assert fake_sentiment.sentiment.call_count == 3


def test_getSentimentScore_internal(fake_sentiment, spanish_stopwords):
    # In production the Series carries the source column name (e.g. 'text').
    s = pd.Series(['hola mundo'], name='text')
    out = getSentimentScore(s, stopwords=spanish_stopwords, sentiment=fake_sentiment)
    assert 'text' in out.columns
    # Internal name before the wrapper renames it.
    assert 'Score Sentiment' in out.columns
