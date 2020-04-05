import re

import pandas as pd

from definitions import COLUMNS_ANALYSIS, STATE
from data_preparation.world_preprocessing import WorldPreprocessing, COUNTRY


class UsaPreprocessing(WorldPreprocessing):

    def __init__(self, country):
        super(WorldPreprocessing, self).__init__(country)
        self.files = [f for f in self.files
                      if re.search('^.*(confirmed|deaths)_US.csv$', f)]
        self._csv_regex = '^.*_covid19_(.*)_US.csv$'

    def reshape_data(self):
        for csv in self.files:
            data = pd.read_csv(csv)
            data.rename(columns={'Province_State': STATE,
                                 'Country_Region': COUNTRY},
                        inplace=True)
            if 'Long_' in data.columns:
                data.rename(columns={'Long_': 'Long'}, inplace=True)
            data.to_csv(csv, index=False, float_format='%.5f')
        super().reshape_data()

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        data = self.preprocessed.copy()
        data.drop(STATE, inplace=True, axis=1)
        data.rename(columns={'Combined_Key': STATE}, inplace=True)
        drop_cols = [c for c in data.columns if c not in COLUMNS_ANALYSIS]
        data.drop(drop_cols, inplace=True, axis=1)
        data = data.reindex(columns=COLUMNS_ANALYSIS)
        return data
