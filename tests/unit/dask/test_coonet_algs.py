"""Unit tests for `whistlerlib.dask.coonet_algs.algs`.

`to_graph` is pure (nodes/edges/weights → igraph.Graph) so we run it for
real. The two `compute_*_weighted_coonet` wrappers delegate to
`base_algs.compute_weighted_coonet`; we mock that primitive and verify
arg wiring + that the result is wrapped in an igraph.Graph.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from igraph import Graph

import whistlerlib.dask.coonet_algs.algs as algs


# --------------------------------------------------------------------------- #
# to_graph                                                                    #
# --------------------------------------------------------------------------- #

def test_to_graph_builds_named_weighted_graph():
    nodes = ['a', 'b', 'c']
    edges = [(0, 1), (1, 2)]
    weights = [3, 7]

    g = algs.to_graph(nodes, edges, weights)

    assert isinstance(g, Graph)
    assert g.vcount() == 3
    assert g.ecount() == 2
    assert list(g.vs['name']) == ['a', 'b', 'c']
    assert list(g.es['weight']) == [3, 7]


def test_to_graph_with_no_edges():
    g = algs.to_graph(['x', 'y'], edges=[], weights=[])
    assert g.vcount() == 2
    assert g.ecount() == 0


def test_to_graph_weights_align_with_edge_order():
    """`add_edges` must zip weights with edges in the order given."""
    g = algs.to_graph(
        ['n0', 'n1', 'n2', 'n3'],
        edges=[(0, 1), (2, 3), (1, 2)],
        weights=[10, 20, 30],
    )
    # find each edge by endpoint vertex names and check its weight
    name_to_idx = {n: i for i, n in enumerate(g.vs['name'])}
    for (u, v), w in zip([('n0', 'n1'), ('n2', 'n3'), ('n1', 'n2')],
                         [10, 20, 30]):
        eid = g.get_eid(name_to_idx[u], name_to_idx[v])
        assert g.es[eid]['weight'] == w


# --------------------------------------------------------------------------- #
# compute_hashtag_weighted_coonet                                             #
# --------------------------------------------------------------------------- #

_EDGES_DF = pd.DataFrame({
    'source': ['a', 'b'],
    'target': ['b', 'c'],
    'weight': [2, 5],
})
_TIME_PROFILE = pd.DataFrame({'stage': ['_'], 'seconds': [0.0]})


def _primitive_return(nodes=None, edges=None, weights=None):
    return (
        nodes or ['a', 'b', 'c'],
        edges or [(0, 1), (1, 2)],
        weights or [2, 5],
        _EDGES_DF,
        _TIME_PROFILE,
    )


@patch.object(algs, 'compute_weighted_coonet')
def test_hashtag_coonet_delegates(mock_primitive):
    mock_primitive.return_value = _primitive_return()
    df = MagicMock(name='dask_df')

    edges_df, graph, profile = algs.compute_hashtag_weighted_coonet(
        df=df, text_column='text', num_partitions=2,
    )

    assert edges_df is _EDGES_DF
    assert profile is _TIME_PROFILE
    assert isinstance(graph, Graph)
    assert graph.vcount() == 3
    assert graph.ecount() == 2

    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['df'] is df
    assert kwargs['text_column'] == 'text'
    assert kwargs['source_col'] == 'source'
    assert kwargs['target_col'] == 'target'
    assert kwargs['weight_col'] == 'weight'
    assert kwargs['func'] is algs.get_hashtag_coonet_edges
    assert kwargs['num_partitions'] == 2


@patch.object(algs, 'compute_weighted_coonet')
def test_mention_coonet_delegates(mock_primitive):
    mock_primitive.return_value = _primitive_return()
    df = MagicMock(name='dask_df')

    edges_df, graph, profile = algs.compute_mention_weighted_coonet(
        df=df, text_column='body', num_partitions=4,
    )

    assert edges_df is _EDGES_DF
    assert isinstance(graph, Graph)
    kwargs = mock_primitive.call_args.kwargs
    assert kwargs['text_column'] == 'body'
    assert kwargs['func'] is algs.get_mention_coonet_edges
    assert kwargs['num_partitions'] == 4


@patch.object(algs, 'compute_weighted_coonet')
def test_coonet_wrappers_use_distinct_funcs(_):
    """Sanity: the hashtag and mention wrappers must NOT share the same
    per-partition edge extractor."""
    assert algs.get_hashtag_coonet_edges is not algs.get_mention_coonet_edges
