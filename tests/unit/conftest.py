"""Unit-test conftest.

Unlike the integration suite (`tests/conftest.py`), unit tests must NOT spin
up a Dask LocalCluster, NOT load real models, and NOT touch the filesystem
beyond `tmp_path`. Mocks live here.

The parent `tests/conftest.py` is still loaded by pytest because it's higher
in the path; that's fine — it only side-effects when its fixtures are
explicitly requested.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def fake_sentiment():
    """A stand-in for `sentiment_analysis_spanish.SentimentAnalysisSpanish`.

    Returns a deterministic score so unit tests are reproducible without
    loading the heavy TensorFlow model.
    """
    fake = MagicMock()
    fake.sentiment = MagicMock(return_value=0.5)
    return fake


@pytest.fixture
def spanish_stopwords():
    """A tiny, deterministic subset of Spanish stopwords for unit tests."""
    return ['el', 'la', 'de', 'y', 'a', 'que', 'en', 'es', 'esto', 'un', 'una']


@pytest.fixture
def english_stopwords():
    """A tiny, deterministic subset of English stopwords for unit tests."""
    return ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'and', 'or', 'of']


@pytest.fixture
def text_df():
    """A small `pd.DataFrame` with a 'text' column — what the funcs/ wrappers expect."""
    return pd.DataFrame({
        'text': [
            'hello world #fun #cool @alice @bob',
            'another tweet #fun @alice today',
            'simple text no markers here',
        ],
    })


@pytest.fixture
def empty_text_df():
    return pd.DataFrame({'text': []}, dtype='object')
