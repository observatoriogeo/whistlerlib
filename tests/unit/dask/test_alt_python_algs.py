"""Unit tests for `whistlerlib.dask.alt_python_algs.algs`.

The four `compute_*` functions are thin orchestration wrappers over the
`base_algs` primitives. We verify here that each wrapper:

- delegates to the right primitive (`compute_vector_histogram` or
  `compute_vector_range`)
- forwards the user-facing args (`k`, `n`, `lan`, `text_column`, …)
- wires the right per-algorithm constants (`token_col` / `freq_col` names,
  the per-partition `func`)
- handles NLTK-data presence / absence without doing a real network
  download (we mock `nltk.download`)

Heavy/Dask-graph behaviour belongs in the Phase 4 example suite — these
unit tests run in milliseconds because every primitive is mocked.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import whistlerlib.dask.alt_python_algs.algs as algs


_TIME_PROFILE_DF = pd.DataFrame({'stage': ['_'], 'seconds': [0.0]})
_RESULT_DF = pd.DataFrame({'_': []})


def _mock_primitive_return():
    return (_RESULT_DF, _TIME_PROFILE_DF)


# --------------------------------------------------------------------------- #
# compute_hashtag_histogram                                                   #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_histogram')
def test_hashtag_delegates_to_vector_histogram(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    result, profile = algs.compute_hashtag_histogram(
        df=df, k=5, text_column='text',
        distributed_sorting=False, num_partitions=2,
    )

    assert result is _RESULT_DF
    assert profile is _TIME_PROFILE_DF
    mock_primitive.assert_called_once()
    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['df'] is df
    assert kwargs['k'] == 5
    assert kwargs['text_column'] == 'text'
    assert kwargs['token_col'] == 'tag'
    assert kwargs['freq_col'] == 'freq'
    assert kwargs['distributed_sorting'] is False
    assert kwargs['num_partitions'] == 2
    assert kwargs['func'] is algs.get_hashtags_wrapper


# --------------------------------------------------------------------------- #
# compute_mention_histogram                                                   #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_histogram')
def test_mention_delegates_to_vector_histogram(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    df = MagicMock(name='dask_df')

    algs.compute_mention_histogram(
        df=df, k=3, text_column='text',
        distributed_sorting=True, num_partitions=4,
    )

    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['token_col'] == 'Mentions'
    assert kwargs['freq_col'] == 'Frequency'
    assert kwargs['distributed_sorting'] is True
    assert kwargs['num_partitions'] == 4
    assert kwargs['func'] is algs.get_mentions_wrapper


# --------------------------------------------------------------------------- #
# compute_ngram_histogram — NLTK branch                                       #
# --------------------------------------------------------------------------- #

class _FakeNltk:
    """Stand-in for the `nltk` module that records whether `download`
    was called and returns canned stopwords."""

    def __init__(self, corpus_present: bool):
        self._present = corpus_present
        self.download_calls = []

        self.data = MagicMock()
        if corpus_present:
            self.data.find.return_value = '/cache/stopwords'
        else:
            self.data.find.side_effect = LookupError('not found')

        self.corpus = MagicMock()
        self.corpus.stopwords.words.return_value = ['el', 'la', 'de']

    def download(self, name, quiet=True):
        self.download_calls.append((name, quiet))
        # subsequent .find() should succeed
        self.data.find.side_effect = None
        self.data.find.return_value = f'/cache/{name}'
        return True


@patch.object(algs, 'compute_vector_histogram')
def test_ngram_skips_download_when_stopwords_cached(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    fake = _FakeNltk(corpus_present=True)
    df = MagicMock(name='dask_df')

    with patch.dict('sys.modules', {'nltk': fake}):
        algs.compute_ngram_histogram(
            df=df, n=2, k=10, lan='spanish', w='word',
            text_column='text', distributed_sorting=False, num_partitions=2,
        )

    assert fake.download_calls == [], (
        'when the corpus is already on disk, `nltk.download` must not run')
    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['k'] == 10
    assert kwargs['token_col'] == 'N_Tokens'
    assert kwargs['freq_col'] == 'Freq'
    assert kwargs['n'] == 2
    assert kwargs['w'] == 'word'
    assert kwargs['stopwords'] == ['el', 'la', 'de']
    fake.corpus.stopwords.words.assert_called_once_with('spanish')


@patch.object(algs, 'compute_vector_histogram')
def test_ngram_downloads_stopwords_when_missing(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    fake = _FakeNltk(corpus_present=False)
    df = MagicMock(name='dask_df')

    with patch.dict('sys.modules', {'nltk': fake}):
        algs.compute_ngram_histogram(
            df=df, n=3, k=5, lan='english', w='word',
            text_column='text', distributed_sorting=False, num_partitions=1,
        )

    assert fake.download_calls == [('stopwords', True)]
    fake.corpus.stopwords.words.assert_called_once_with('english')


# --------------------------------------------------------------------------- #
# compute_sentiment_range_spanish                                             #
# --------------------------------------------------------------------------- #

@patch.object(algs, 'compute_vector_range')
def test_sentiment_range_spanish_delegates(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    fake_nltk = _FakeNltk(corpus_present=True)
    df = MagicMock(name='dask_df')

    fake_sentiment_module = MagicMock()
    fake_sentiment_module.sentiment_analysis.SentimentAnalysisSpanish \
        .return_value = MagicMock(name='sentiment_model')

    with patch.dict('sys.modules', {
        'nltk': fake_nltk,
        'sentiment_analysis_spanish': fake_sentiment_module,
        'sentiment_analysis_spanish.sentiment_analysis':
            fake_sentiment_module.sentiment_analysis,
    }):
        algs.compute_sentiment_range_spanish(
            df=df, left_end=0.9, right_end=1.0,
            text_column='text', num_partitions=2,
        )

    kwargs = mock_primitive.call_args.kwargs
    args = mock_primitive.call_args.args
    # the underlying primitive is called positional-first
    assert args[0] is df
    assert args[1] == 0.9
    assert args[2] == 1.0
    assert args[3] == 'text'
    assert kwargs['output_text_col'] == 'text'
    assert kwargs['output_score_col'] == 'score'
    assert kwargs['num_partitions'] == 2
    assert kwargs['func'] is algs.get_sentiment_score_wrapper
    assert kwargs['stopwords'] == ['el', 'la', 'de']
    # `sentiment` is wrapped in dask.delayed; the wrapper exposes `.compute()`
    # so just check it's not None
    assert kwargs['sentiment'] is not None


@patch.object(algs, 'compute_vector_range')
def test_sentiment_downloads_stopwords_when_missing(mock_primitive):
    mock_primitive.return_value = _mock_primitive_return()
    fake_nltk = _FakeNltk(corpus_present=False)
    df = MagicMock(name='dask_df')

    fake_sentiment_module = MagicMock()
    fake_sentiment_module.sentiment_analysis.SentimentAnalysisSpanish \
        .return_value = MagicMock()

    with patch.dict('sys.modules', {
        'nltk': fake_nltk,
        'sentiment_analysis_spanish': fake_sentiment_module,
        'sentiment_analysis_spanish.sentiment_analysis':
            fake_sentiment_module.sentiment_analysis,
    }):
        algs.compute_sentiment_range_spanish(
            df=df, left_end=0.0, right_end=1.0,
            text_column='text', num_partitions=1,
        )

    assert fake_nltk.download_calls == [('stopwords', True)]
