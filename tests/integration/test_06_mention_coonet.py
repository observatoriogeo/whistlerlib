"""Integration test for example 06 (mention coonet)."""

import pytest

EXAMPLE_SLUG = '06-mention-coonet'

pytestmark = pytest.mark.docker


def test_mention_weighted_coonet(whistlerlib_swarm, example_module):
    host, port = whistlerlib_swarm
    edges_df, graph = example_module.run(host, port)
    assert list(edges_df.columns) == ['source', 'target', 'weight']
    assert not graph.is_directed()
    assert graph.vcount() > 0
    assert graph.ecount() > 0
    assert graph.ecount() == len(edges_df)
