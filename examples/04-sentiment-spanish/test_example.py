"""Integration test for example 04 (sentiment-spanish).

Slow: loads the TensorFlow sentiment model. Gated on BOTH `docker` and
`slow` markers — only runs when explicitly opted in via `-m "docker and slow"`.
"""

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]


def test_sentiment_range_spanish_positive(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    positive = example_module.run(host, port)
    assert list(positive.columns) == ['text', 'score']
    # At least one strongly-positive phrase should land in [0.9, 1.0].
    assert len(positive) > 0
    assert (positive['score'] >= 0.9).all()
    assert (positive['score'] <= 1.0).all()
