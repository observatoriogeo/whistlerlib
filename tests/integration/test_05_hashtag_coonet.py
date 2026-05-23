"""Integration test for example 05 (hashtag coonet)."""

import pytest

EXAMPLE_SLUG = '05-hashtag-coonet'

pytestmark = pytest.mark.docker


def test_hashtag_weighted_coonet(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    edges_df, graph = example_module.run(host, port)
    assert list(edges_df.columns) == ['source', 'target', 'weight']
    assert not graph.is_directed()
    assert graph.vcount() > 0
    assert graph.ecount() > 0
    # Edge count in df should match graph edge count.
    assert graph.ecount() == len(edges_df)
