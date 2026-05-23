# pyright: reportMissingImports=false

import dask.dataframe as dd
from ...logger import logger


class DATASET_FILE_FORMAT:
    CSV = "CSV"
    PARQUET = "Parquet"


class DatasetRepositoryClient():

    def __init__(self):
        pass

    def load_csv(self, filen, meta):

        dataset_file = filen
        dataset_encoding = meta['file_encoding']
        dataset_date_column = meta['column_mapping']['date_column']
        dataset_text_column = meta['column_mapping']['text_column']

        # TODO: assume_missing=True is just to get rid of the error ValueError: Mismatched dtypes found in `pd.read_csv`/`pd.read_table` for columns that are not used in any algorithm. Fix?
        df = dd.read_csv(dataset_file,
                         encoding=dataset_encoding,
                         parse_dates=[dataset_date_column],                         
                         dtype={dataset_text_column: 'object'},
                         assume_missing=True,
                         usecols=[dataset_date_column, dataset_text_column])

        logger.debug(
            f'[load_dataset_by_id] df[dataset_date_column] = {df[dataset_date_column]}')

        # to prevent the Dask exception: "Cannot compare tz-naive and tz-aware datetime-like objects"
        df[dataset_date_column] = df[dataset_date_column].apply(
            lambda x: x.tz_localize(None))

        return df
