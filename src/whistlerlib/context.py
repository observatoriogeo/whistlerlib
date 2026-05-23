# pyright: reportMissingImports=false

from .clients import DatasetRepositoryClient
from .dataset import TweetDataset


class Context():

    def __init__(self, dask_scheduler, dask_scheduler_host, dask_scheduler_port):
        from dask_sql import Context
        from dask.distributed import Client
        import dask

        self.dask_scheduler = dask_scheduler
        self.dask_scheduler_host = dask_scheduler_host
        self.dask_scheduler_port = dask_scheduler_port

        dask.config.set(scheduler=self.dask_scheduler)

        self.dask_client = Client(
            f'{self.dask_scheduler_host}:{self.dask_scheduler_port}')
        self.dask_sql_context = Context()
        self.dask_sql_context.sql(''' 
            SELECT 1+1        
        ''')
        self.dataset_repository_client = DatasetRepositoryClient()

    def load_csv(self, filen, meta, num_partitions=1):

        self.num_partitions = num_partitions
        self.filen = filen
        self.meta = meta

        # load dataset and partition it
        self.ddf = self.dataset_repository_client.load_csv(
            self.filen, self.meta)
        self.ddf = self.ddf.repartition(npartitions=self.num_partitions)

        # return tweet dataset
        dataset = TweetDataset(ds_metadata=self.meta,
                               dask_df=self.ddf,
                               dask_sql_context=self.dask_sql_context,
                               num_partitions=self.num_partitions,
                               ranged=False,
                               query_result=False)

        return dataset
