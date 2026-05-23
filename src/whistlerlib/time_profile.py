# pyright: reportMissingModuleSource=false

from contextlib import contextmanager
from time import time


class TimeProfile:
    def __init__(self, name=''):
        self.profile = []
        self.count = 0
        self.name = name

    @contextmanager
    def add_time_measurement(self, description):
        start = time()
        yield
        end = time()
        elapsed = end - start
        self.count += 1
        self.profile.append(
            {
                'profile_name': self.name,
                'measurement_number': self.count,
                'start': start,
                'end': end,
                'elapsed': elapsed,
                'description': description
            }
        )

    def as_list(self):
        return self.profile

    def as_df(self):
        import pandas as pd
        return pd.DataFrame(self.profile)
