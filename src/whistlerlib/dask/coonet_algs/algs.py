from igraph import Graph
from .funcs import get_mention_coonet_edges, get_hashtag_coonet_edges
from ..base_algs import compute_weighted_coonet


def to_graph(nodes, edges, weights):
    graph = Graph(len(nodes))
    graph.vs['name'] = nodes
    graph.add_edges(edges, {'weight': weights})
    return graph


def compute_mention_weighted_coonet(df, text_column, num_partitions):
    nodes, edges, weights, df_out, time_profile = \
        compute_weighted_coonet(df=df,
                                text_column=text_column,
                                source_col='source',
                                target_col='target',
                                weight_col='weight',
                                func=get_mention_coonet_edges,
                                num_partitions=num_partitions)
    graph = to_graph(nodes, edges, weights)
    return df_out, graph, time_profile


def compute_hashtag_weighted_coonet(df, text_column, num_partitions):
    nodes, edges, weights, df_out, time_profile = \
        compute_weighted_coonet(df=df,
                                text_column=text_column,
                                source_col='source',
                                target_col='target',
                                weight_col='weight',
                                func=get_hashtag_coonet_edges,
                                num_partitions=num_partitions)
    graph = to_graph(nodes, edges, weights)
    return df_out, graph, time_profile
