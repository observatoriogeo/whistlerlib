from .....logger import logger
from ..r_script_process import RScriptArgs, RScriptProcess


def getWordCloud(df_in, html_folder, html_filen):
    '''
    Python wrapper for the getWordCloud R function.
    This function is to be run by the Ngrams dashboard in the whistler_ngrams container.
    '''

    rsp = RScriptProcess(
        interpreter_path='/opt/conda/envs/dashboard-env/bin/Rscript',
        script_path='/var/shared_modules/whistler_r/ngrams/getWordCloud.R',
        logger=logger,
        has_df_output=False
    )

    logger.info(
        '[whistler_r.mfhashtags.getWordCloud.getWordCloud] running R script ...'
    )

    rsp.run(df_in,
            RScriptArgs.TMP_FILE_IN,
            html_folder,
            html_filen)

    logger.info('[whistler_r.mfhashtags.getWordCloud.getWordCloud] done.')

    return
 