"""Integration test for example 01.

Runs against the session-scoped local Docker cluster (Compose-managed by
`tests/integration/conftest.py`). Gated on `@pytest.mark.docker`,
deselected from the default `pytest` run.
"""

import pytest

EXAMPLE_SLUG = '01-quickstart-hashtag-histogram'

pytestmark = pytest.mark.docker


def test_quickstart_hashtag_histogram(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    histogram = example_module.run(host, port)
    assert list(histogram.columns) == ['tag', 'freq']
    assert len(histogram) == 5
    # Frequencies must be in non-increasing order (top-k by frequency).
    freqs = histogram['freq'].tolist()
    assert freqs == sorted(freqs, reverse=True)
