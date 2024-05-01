# pyright: reportMissingModuleSource=false

import logging
import itertools
import pandas as pd
from ...alt_python_algs.funcs.getHashtags import getHashtags
from ...alt_python_algs.funcs.getMentions import getMentions

logger = logging.getLogger('distributed.worker')


def get_mention_coonet_edges(df, text_column):

    if df.empty:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_mention_coonet_edges] got an empty DataFrame! Returning empty response DataFrame')
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    else:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_mention_coonet_edges] got:\n{df}')

    edges = []
    logger.info(
        f'[whistler_dask.coonet.dask_methods.get_mention_coonet_edges] computing edges ...')
    for _, row in df.iterrows():
        row_text = row[text_column]

        # TODO: what happens if the Series is empty?
        row_mentions = getMentions(row_text)['Mentions'].tolist()

        for comb in itertools.combinations(row_mentions, 2):
            comb = sorted(comb)
            edges.append({
                'source': comb[0],
                'target': comb[1],
                'weight': 1
            })

    if len(edges) == 0:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_mention_coonet_edges] no edges were found! Returning empty response DataFrame')
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    else:
        # build edges dataset
        df_edges = pd.DataFrame.from_records(edges)
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_mention_coonet_edges] df_edges = {df_edges}')
        return df_edges[['source', 'target', 'weight']]


def get_hashtag_coonet_edges(df, text_column):

    if df.empty:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_hashtag_coonet_edges] got an empty DataFrame! Returning empty response DataFrame')
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    else:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_hashtag_coonet_edges] got:\n{df}')

    logger.info(
        f'[whistler_dask.coonet.dask_methods.get_hashtag_coonet_edges] computing edges ...')
    edges = []

    for _, row in df.iterrows():

        row_text = row[text_column]

        # TODO: what happens if the Series is empty?
        row_hashtags = getHashtags(pd.Series(row_text)).index.tolist()

        for comb in itertools.combinations(row_hashtags, 2):
            comb = sorted(comb)
            edges.append({
                'source': comb[0],
                'target': comb[1],
                'weight': 1
            })

    if len(edges) == 0:
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_hashtag_coonet_edges] no edges were found! Returning empty response DataFrame')
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    else:
        # build edges dataset
        df_edges = pd.DataFrame.from_records(edges)
        logger.info(
            f'[whistler_dask.coonet.dask_methods.get_hashtag_coonet_edges] df_edges = {df_edges}')
        return df_edges[['source', 'target', 'weight']]
