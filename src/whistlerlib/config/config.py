import os

# R bridge environment variables, may be None if the R bridge isn't used.
# Code paths that actually invoke R must validate before use.
R_SCRIPTS_PATH = os.getenv('WHISTLERLIB_R_SCRIPTS_PATH')
R_PATH = os.getenv('WHISTLERLIB_R_PATH')
