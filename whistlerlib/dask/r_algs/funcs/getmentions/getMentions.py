import logging
from ..r_script_process import RScriptArgs, RScriptProcess
from .....config.config import R_SCRIPTS_PATH, R_PATH
logger = logging.getLogger('distributed.worker')


def getMentions(df_in, text_column):
    '''
    Python wrapper for the getMDHashtags R function.
    This function is to be ran by a Dask worker in a whistler_dask-worker container.
    '''

    rsp = RScriptProcess(
        interpreter_path=f'{R_PATH}/Rscript',
        script_path=f'{R_SCRIPTS_PATH}/getmentions/getMentions.R',
        logger=logger,
        has_df_output=True,
        df_output_columns=['mentions', 'Freq']
    )

    logger.info(
        '[whistler_r.mfhashtags.getMentions.getMentions] running R script ...'
    )

    df_out = rsp.run(df_in,
                     text_column,
                     RScriptArgs.TMP_FILE_IN,
                     RScriptArgs.TMP_FILE_OUT)

    logger.info('[whistler_r.mfhashtags.getMentions.getMentions] done.')

    df_out['mentions'] = df_out['mentions'].str.strip()

    return df_out
