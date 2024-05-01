import pandas as pd
import dask.dataframe as dd
from ...time_profile import TimeProfile
from ...logger import logger


def compute_matrix_nz_histogram_and_sum(df, text_column, func, meta, col_names, num_partitions, **kwargs):

    time_profile = TimeProfile(name='matrix_nz_histogram_and_sum')

    # compute sentiments
    df = df[[text_column]]
    with time_profile.add_time_measurement('01_map_partitions_dist'):
        dist_df = df.map_partitions(func, text_column,
                                    **kwargs, meta=meta)  # distributed
        assert dist_df.npartitions == num_partitions

    # compute sentiments stats
    dist_df = dist_df[list(col_names.keys())]
    with time_profile.add_time_measurement('02_count_nonzeroes_dist'):
        local_count_df = dist_df[dist_df > 0].count().compute()  # distributed

    with time_profile.add_time_measurement('03_sum_scores_dist'):
        local_sum_df = dist_df.sum().compute()  # distributed

    assert len(local_count_df.index) == len(local_sum_df.index)
    assert list(local_count_df.index) == list(local_sum_df.index)

    # prepare local stats DF
    with time_profile.add_time_measurement('04_stats_df_prepare_local'):
        local_stats_df = pd.DataFrame(index=local_count_df.index)
        local_stats_df['count'] = local_count_df
        local_stats_df['sum'] = local_sum_df
        local_stats_df['sentiment'] = [col_names[i]
                                       for i in local_stats_df.index]  # TODO: generalize column name

    # local sort by count, sum
    with time_profile.add_time_measurement('05_sort_values_local'):
        local_stats_df = local_stats_df.sort_values(
            by=['count', 'sum'], ascending=False)

    return local_stats_df, time_profile.as_df()


def compute_vector_histogram(df, k, text_column, func, token_col, freq_col, distributed_sorting=False, num_partitions=1, **kwargs):
    '''
    Distributed histogram algorithm with Dask: compute for each DF partition in the workers.
    func must return a DataFrame with the "tag" and "freq" columns.
    df: A Dask DataFrame that has been already partitioned.
    '''

    time_profile = TimeProfile(name='whistler_dask.get_mfhashtags')

    df = df[[text_column]]

    # distributed map_partitions
    with time_profile.add_time_measurement('01_map_partitions_dist'):
        dist_df = df.map_partitions(func, text_column, **kwargs, meta={
            token_col: "object", freq_col: "int64"})
        assert dist_df.npartitions == num_partitions

    # this is necessary since Dask returns a column of dtype 'category' even with the meta saying it should be of dtype 'object'
    with time_profile.add_time_measurement('02_astype_dist'):
        dist_df[token_col] = dist_df[token_col].astype('object')

    if distributed_sorting:

        logger.warn("Warning (whistlerlib): With distributed_sorting=True results within groups of tied rows may be returned in different order depending on the number of partitions.")

        # distributed groupby to get tag freq. sums
        with time_profile.add_time_measurement('03_group_by_sum_dist'):
            # groupby().sum() will return a DDF vs groupby().col.sum() which will return a Series. Aggregation will work over freq_col in both cases.
            dist_df = dist_df.groupby(token_col, sort=False).sum(
                split_out=num_partitions)
            assert dist_df.npartitions == num_partitions

        # flatten the group-by index hierarchy
        with time_profile.add_time_measurement('04_reset_index_dist'):
            dist_df = dist_df.reset_index()

        # distributed nlargest to get the top-k tags with largest freqs.
        # if k =< 0, return all the (sorted) hasthags
        if k > 0:
            with time_profile.add_time_measurement('05_nlargest_dist'):
                local_df = dist_df.nlargest(k, freq_col).compute()
        else:
            with time_profile.add_time_measurement('05_sort_values_dist'):
                local_df = dist_df.sort_values(
                    by=freq_col, ascending=False).compute()

    else:

        # distributed groupby to get tag freq. sums
        with time_profile.add_time_measurement('03_group_by_sum_dist'):
            # groupby().sum() will return a DDF vs groupby().col.sum() which will return a Series. Aggregation will work over freq_col in both cases.
            local_df = dist_df.groupby(
                token_col, sort=False).sum(split_out=1).compute()

        # flatten the group-by index hierarchy
        with time_profile.add_time_measurement('04_reset_index_local'):
            local_df = local_df.reset_index()
            # local_df = local_df.set_index(token_col)

        # local nlargest to get the top-k tags with largest freqs.
        # if k =< 0 return all the (sorted) hasthags
        if k > 0:
            with time_profile.add_time_measurement('05_sort_values_head_local'):
                local_df = local_df.sort_values(
                    by=[freq_col, token_col], ascending=False).head(n=k)
        else:
            with time_profile.add_time_measurement('05_sort_values_local'):
                local_df = local_df.sort_values(
                    by=[freq_col, token_col], ascending=False)

    # local reset_index, since freq is in an upper index level
    with time_profile.add_time_measurement('06_reset_index_local'):
        local_df = local_df.reset_index(drop=True)

    return local_df, time_profile.as_df()


def compute_vector_range(df, left_end, right_end, text_column, output_text_col, output_score_col, func, num_partitions=1, **kwargs):
    '''
    Distributed getSentimentScore: compute for each DF partition in the workers.
    df: A Dask DataFrame that has been already partitioned.
    '''

    time_profile = TimeProfile(
        name='whistler_dask.alt_python.get_sentiment_score')

    # distributed get_sentiment_score
    df = df[[text_column]]
    with time_profile.add_time_measurement('01_map_partitions_dist'):
        dist_df = df.map_partitions(func, text_column, **kwargs, meta={
            output_text_col: "object", output_score_col: "float64"})
        assert dist_df.npartitions == num_partitions

    # this is necessary since Dask returns a column of dtype 'category' even with the meta saying it should be of dtype 'object'
    with time_profile.add_time_measurement('02_astype_dist'):
        dist_df[output_text_col] = dist_df[output_text_col].astype('object')

    # distributed range
    with time_profile.add_time_measurement('03_filter_dist'):
        local_df = dist_df[(dist_df[output_score_col] >= left_end) & (
            dist_df[output_score_col] <= right_end)].compute()

    return local_df, time_profile.as_df()


def compute_weighted_coonet(df, text_column, source_col, target_col, weight_col, func, num_partitions=1, **kwargs):
    '''
    Distributed coonet builder.
    df: A Dask DataFrame that has been already partitioned.
    '''

    time_profile = TimeProfile(name=f'compute_weighted_coonet')

    # edges computation

    # compute edges (distributed)
    df = df[[text_column]]

    with time_profile.add_time_measurement('01_map_partitions_dist'):
        dist_df = df.map_partitions(func, text_column, **kwargs, meta={
            source_col: 'object', target_col: 'object', weight_col: 'int64'})
        assert dist_df.npartitions == num_partitions

    # group by source and target and sum weights to remove parallel edges (distributed)
    with time_profile.add_time_measurement('02_group_by_sum_dist'):
        local_edges_df = dist_df.groupby(
            [source_col, target_col]).weight.sum().compute()  # distributed

    with time_profile.add_time_measurement('03_reset_index_local'):
        local_edges_df = local_edges_df.reset_index()

    # node computation

    # concatenate the source and target columns
    with time_profile.add_time_measurement('04_concat_sources_targets_dist'):
        dist_nodes_df = dd.concat([dist_df[source_col], dist_df[target_col]])

    with time_profile.add_time_measurement('05_repartition_dist'):
        dist_nodes_df = dist_nodes_df.repartition(npartitions=num_partitions)
        assert dist_nodes_df.npartitions == num_partitions, dist_nodes_df.npartitions

    # drop duplicates in the concatenation
    with time_profile.add_time_measurement('06_drop_duplicates_dist'):
        local_nodes_df = dist_nodes_df.drop_duplicates().compute()

    # sorting to make sure we always return the same graph regardless of the # of partitions

    # locally sort_values by [source, target] the local_edges_df to always return the same order of edges
    with time_profile.add_time_measurement('07_edges_sort_values_local'):
        local_edges_df = local_edges_df.sort_values(
            by=[source_col, target_col])
    with time_profile.add_time_measurement('08_edges_reset_index_local'):
        local_edges_df = local_edges_df.reset_index(drop=True)

    # locally sort_values the nodes to always return the same order of nodes
    with time_profile.add_time_measurement('09_nodes_sort_values_local'):
        local_nodes_df = local_nodes_df.sort_values()

    # get Python lists for nodes, edges and weights

    # get Python collections from the nodes series and the edges DataFrame and return them
    with time_profile.add_time_measurement('10_edges_to_list_local'):
        edges = [tuple(x)
                 for x in local_edges_df[[source_col, target_col]].to_numpy()]
    with time_profile.add_time_measurement('11_weights_to_list_local'):
        weights = local_edges_df[weight_col].tolist()
    with time_profile.add_time_measurement('12_nodes_to_list_local'):
        nodes = local_nodes_df.tolist()

    return nodes, edges, weights, local_edges_df, time_profile.as_df()
