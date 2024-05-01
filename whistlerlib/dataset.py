import hashlib
from .dask import r_algs
from .dask import alt_python_algs
from .dask import coonet_algs
from .time_profile import TimeProfile


class TweetDataset:

    def __init__(self, ds_metadata, dask_df, dask_sql_context, num_partitions, ranged=False, range_start_date='', range_end_date='', query_result=False, query=''):
        self.ds_metadata = ds_metadata
        self.query_result = query_result
        self.query = query
        self.dask_df = dask_df
        self.dask_sql_context = dask_sql_context
        self.text_column = self.ds_metadata['column_mapping']['text_column']
        self.date_column = self.ds_metadata['column_mapping']['date_column']
        self.num_partitions = num_partitions
        self.ranged = ranged
        self.range_start_date = range_start_date
        self.range_end_date = range_end_date

        # get a dataset table name for Dask SQL
        tablename = "dataset"
        if self.query_result:
            tablename += self.query
        if self.ranged:
            tablename += str(self.range_start_date) + str(self.range_end_date)
        # the leading 't' is for making sure the table name will be a valid one not starting with a number
        self.dask_sql_tablename = 't' + \
            hashlib.md5(tablename.encode('utf-8')).hexdigest()

        self.dask_sql_context.create_table(
            self.dask_sql_tablename, self.dask_df)

    def hashtag_histogram_r(self, k, distributed_sorting=False, return_time_profile=False):
        '''
        R implementation.
        '''
        df_out, time_profile = r_algs.compute_hashtag_histogram(self.dask_df,
                                                                k=k,
                                                                text_column=self.text_column,
                                                                distributed_sorting=distributed_sorting,
                                                                num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def mention_histogram_r(self, k, distributed_sorting=False, return_time_profile=False):
        '''
        R implementation.
        '''
        df_out, time_profile = r_algs.compute_mention_histogram(self.dask_df,
                                                                k=k,
                                                                text_column=self.text_column,
                                                                distributed_sorting=distributed_sorting,
                                                                num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def hashtag_histogram_alt_python(self, k, distributed_sorting=False, return_time_profile=False):
        '''
        New Python implementation (Sep 2021)
        '''
        df_out, time_profile = alt_python_algs.compute_hashtag_histogram(self.dask_df,
                                                                         k=k,
                                                                         text_column=self.text_column,
                                                                         distributed_sorting=distributed_sorting,
                                                                         num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def mention_histogram_alt_python(self, k, distributed_sorting=False, return_time_profile=False):
        '''
        New Python implementation (Dec 2021)
        '''
        df_out, time_profile = alt_python_algs.compute_mention_histogram(self.dask_df,
                                                                         k=k,
                                                                         text_column=self.text_column,
                                                                         distributed_sorting=distributed_sorting,
                                                                         num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def ngram_histogram_r(self, n, k, distributed_sorting=False, return_time_profile=False):
        '''
        R implementation
        '''
        df_out, time_profile = r_algs.compute_ngram_histogram(self.dask_df,
                                                              n=n,
                                                              k=k,
                                                              distributed_sorting=distributed_sorting,
                                                              text_column=self.text_column,
                                                              num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def ngram_histogram_alt_python(self, n, k, lan, w, distributed_sorting=False, return_time_profile=False):
        '''
        New Python implementation (Sep 2021)
        '''
        df_out, time_profile = alt_python_algs.compute_ngram_histogram(self.dask_df,
                                                                       n=n,
                                                                       k=k,
                                                                       lan=lan,
                                                                       w=w,
                                                                       distributed_sorting=distributed_sorting,
                                                                       text_column=self.text_column,
                                                                       num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def sentiment_range_spanish_alt_python(self, left_end, right_end, return_time_profile=False):
        '''
        New Python implementation (Sep 2021)
        '''
        df_out, time_profile = alt_python_algs.compute_sentiment_range_spanish(self.dask_df,
                                                                               left_end=left_end,
                                                                               right_end=right_end,
                                                                               text_column=self.text_column,
                                                                               num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def sentiment_histogram_and_sum_r(self, language, method, return_time_profile=False):
        '''
        R implementation
        '''
        df_out, time_profile = r_algs.compute_sentiment_histogram_and_sum(df=self.dask_df,
                                                                          text_column=self.text_column,
                                                                          language=language,
                                                                          method=method,
                                                                          num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, time_profile
        else:
            return df_out

    def mention_weighted_coonet(self, return_time_profile=False):
        df_out, graph, time_profile = \
            coonet_algs.compute_mention_weighted_coonet(df=self.dask_df,
                                                        text_column=self.text_column,
                                                        num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, graph, time_profile
        else:
            return df_out, graph

    def hashtag_weighted_coonet(self, return_time_profile=False):
        df_out, graph, time_profile = \
            coonet_algs.compute_hashtag_weighted_coonet(df=self.dask_df,
                                                        text_column=self.text_column,
                                                        num_partitions=self.num_partitions)
        if return_time_profile:
            return df_out, graph, time_profile
        else:
            return df_out, graph

    def run_query(self, query):
        '''
        Returns the result of a query as a new TweetDataset
        '''
        query = query.replace('{dataset}', self.dask_sql_tablename)
        query_df = self.dask_sql_context.sql(
            query
        )

        query_df = query_df.repartition(npartitions=self.num_partitions)
        query_df = query_df.persist()

        query_dataset = TweetDataset(ds_metadata=self.ds_metadata,
                                     dask_df=query_df,
                                     dask_sql_context=self.dask_sql_context,
                                     num_partitions=self.num_partitions,
                                     ranged=self.ranged,
                                     range_start_date=self.range_start_date,
                                     range_end_date=self.range_end_date,
                                     query_result=True,
                                     query=query)
        return query_dataset

    def group_by_date(self):
        '''
        Assumes that self.dask_df has been already partitioned.
        '''

        df_grouped = self.dask_df.groupby(
            self.dask_df[self.date_column].dt.date).size().reset_index()
        df_grouped.columns = ['Date', 'Count']
        df_grouped = df_grouped.compute()

        return df_grouped

    def range_by_dates(self, start_date, end_date):
        '''
        Assumes that self.dask_df has been already partitioned.
        '''
        # range loaded ddf

        ddf_ranged = self.dask_df[(self.dask_df[self.date_column] >= start_date) &
                                  (self.dask_df[self.date_column] <= end_date)]
        ddf_ranged = ddf_ranged.repartition(npartitions=self.num_partitions)
        ddf_ranged = ddf_ranged.persist()

        # return tweet dataset

        ranged_dataset = TweetDataset(ds_metadata=self.ds_metadata,
                                      dask_df=ddf_ranged,
                                      dask_sql_context=self.dask_sql_context,
                                      num_partitions=self.num_partitions,
                                      ranged=True,
                                      range_start_date=start_date,
                                      range_end_date=end_date,
                                      query=self.query,
                                      query_result=self.query_result)
        return ranged_dataset

    def tweet_count(self, return_time_profile=False):
        '''
        Assumes that self.dask_df has been already partitioned.
        '''
        time_profile = TimeProfile(
            name='whistler_lib.TweetDataset.tweet_count')
        with time_profile.add_time_measurement('count'):
            count = len(self.dask_df)
        if return_time_profile:
            return count, time_profile.as_df()
        else:
            return count

    def repartition(self, num_partitions):
        self.num_partitions = num_partitions
        self.dask_df = \
            self.dask_df.repartition(npartitions=self.num_partitions)
        assert self.dask_df.npartitions == self.num_partitions

    def get_num_partitions(self):
        assert self.dask_df.npartitions == self.num_partitions
        return self.num_partitions

    def create_index(self):
        '''
        This method is mutable.
        '''

        # create numerical index for paging
        dataset_len = self.tweet_count()

        # create integer index column by considering the current partitioning
        chunks = tuple(self.dask_df.map_partitions(len).compute())
        from dask.array import from_array
        import numpy as np
        self.dask_df['_index'] = from_array(
            np.arange(dataset_len), chunks=chunks)
        self.dask_df = self.dask_df.set_index('_index')  # index
        self.dask_df = self.dask_df.persist()  # persist index
