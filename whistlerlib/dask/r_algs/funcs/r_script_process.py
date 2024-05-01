# pyright: reportMissingImports=false, reportMissingModuleSource=false

import pandas as pd
import tempfile
import subprocess
from enum import Enum


class RScriptArgs(Enum):
    TMP_FILE_IN = 'tmp_file_in'
    TMP_FILE_OUT = 'tmp_file_out'


class RScriptProcess:

    def __init__(self, interpreter_path, script_path, logger, has_df_output=True, df_output_columns=[]):

        self.interpreter_path = interpreter_path
        self.script_path = script_path
        self.logger = logger
        self.has_df_output = has_df_output
        self.df_output_columns = df_output_columns

    def run(self, df_in, *args):

        with tempfile.NamedTemporaryFile() as tmp_file_in:
            with tempfile.NamedTemporaryFile() as tmp_file_out:
                self.logger.info(
                    f'[whistler_r.base.RScriptProcess.run_with_df] tmp_file_out = {tmp_file_out.name}')
                df_in.to_parquet(tmp_file_in.name, engine='pyarrow')
                script_args = []
                for arg in args:
                    if arg == RScriptArgs.TMP_FILE_IN:
                        script_args.append(tmp_file_in.name)
                    elif arg == RScriptArgs.TMP_FILE_OUT:
                        script_args.append(tmp_file_out.name)
                    else:
                        script_args.append(str(arg))
                cmd = [
                    self.interpreter_path,
                    '--vanilla',
                    self.script_path
                ]
                cmd += script_args
                try:
                    self.logger.info(
                        f'[whistler_r.base.RScriptProcess.run_with_df] Running command = {cmd}')
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True
                    )
                    self.logger.info(
                        f'[whistler_r.base.RScriptProcess.run_with_df] R script stdout = {result.stdout}')
                    self.logger.info(
                        f'[whistler_r.base.RScriptProcess.run_with_df] R script stderr = {result.stderr}')
                    result.check_returncode()
                    if self.has_df_output:
                        df_out = pd.read_parquet(
                            tmp_file_out.name, engine='pyarrow')
                        return df_out[self.df_output_columns]
                    else:
                        return

                except subprocess.CalledProcessError as grepexc:
                    if grepexc.returncode == 123:  # empty output from R script, return empty DF
                        if self.has_df_output:
                            return pd.DataFrame(columns=self.df_output_columns)
                        else:
                            return
                    else:
                        self.logger.info(
                            f'[whistler_r.base.RScriptProcess.run_with_df] ERROR = {grepexc}')
                        raise grepexc
                except Exception as e:
                    self.logger.info(
                        f'[whistler_r.base.RScriptProcess.run_with_df] ERROR = {e}')
                    raise e
