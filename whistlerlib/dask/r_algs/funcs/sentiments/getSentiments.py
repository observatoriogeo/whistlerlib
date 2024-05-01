import logging
from ..r_script_process import RScriptArgs, RScriptProcess
from .....config.config import R_SCRIPTS_PATH, R_PATH
logger = logging.getLogger('distributed.worker')


def getSentiments(df_in, text_column, language, method):
    '''
    Python wrapper for the getSentiments R function.
    This function is to be ran by a Dask worker in a whistler_dask-worker container.
    '''

    rsp = RScriptProcess(
        interpreter_path=f'{R_PATH}/Rscript',
        script_path=f'{R_SCRIPTS_PATH}/sentiments/getSentiments.R',
        logger=logger,
        has_df_output=True,
        df_output_columns=['text', 'polarity', 'emotions.anger', 'emotions.anticipation', 'emotions.disgust', 'emotions.fear',  'emotions.joy',
                           'emotions.sadness', 'emotions.surprise', 'emotions.trust', 'emotions.negative',  'emotions.positive']
    )

    logger.info(
        '[whistler_r.mfhashtags.getSentiments.getSentiments] running R script ...'
    )

    df_out = rsp.run(df_in,
                     text_column,
                     # date_column,
                     language,
                     method,
                     RScriptArgs.TMP_FILE_IN,
                     RScriptArgs.TMP_FILE_OUT)

    logger.info('[whistler_r.mfhashtags.getSentiments.getSentiments] done.')

    return df_out
