import logging
from ..r_script_process import RScriptArgs, RScriptProcess
from .....config.config import R_SCRIPTS_PATH, R_PATH
logger = logging.getLogger('distributed.worker')


def getNgrams(df_in, text_column, n):
    '''
    Python wrapper for the getNgrams R function.
    This function is to be ran by a Dask worker in a whistler_dask-worker container.
    '''

    rsp = RScriptProcess(
        interpreter_path=f'{R_PATH}/Rscript',
        script_path=f'{R_SCRIPTS_PATH}/ngrams/getNgrams.R',
        logger=logger,
        has_df_output=True,
        df_output_columns=['N_Tokens', 'Freq']
    )

    logger.info(
        '[whistler_r.mfhashtags.getNgrams.getNgrams] running R script ...'
    )

    df_out = rsp.run(df_in,
                     RScriptArgs.TMP_FILE_IN,
                     RScriptArgs.TMP_FILE_OUT,
                     n,
                     text_column)

    logger.info('[whistler_r.mfhashtags.getNgrams.getNgrams] done.')

    return df_out
