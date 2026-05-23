"""Integration test for example 02."""

import pytest

EXAMPLE_SLUG = '02-mention-histogram'

pytestmark = pytest.mark.docker


def test_mention_histogram(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    histogram = example_module.run(host, port)
    assert list(histogram.columns) == ['Mentions', 'Frequency']
    assert len(histogram) == 5
    # All mentions should be lowercase (advertools normalization).
    for mention in histogram['Mentions']:
        assert mention == mention.lower()
