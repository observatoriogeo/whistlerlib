import os
R_SCRIPTS_PATH = os.getenv('WHISTLERLIB_R_SCRIPTS_PATH')
R_PATH = os.getenv('WHISTLERLIB_R_PATH')

assert R_SCRIPTS_PATH, "Please set the WHISTLERLIB_R_SCRIPTS_PATH environment variable."
assert R_PATH, "Please set the WHISTLERLIB_R_PATH environment variable."
