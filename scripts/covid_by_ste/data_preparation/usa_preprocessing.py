import re

import pandas as pd

from covid_analysis.utils import COLUMNS_ANALYSIS
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
            data.rename(columns={'Province_State': 'Province/State',
                                 'Country_Region': COUNTRY},
                        inplace=True)
            if 'Long_' in data.columns:
                data.rename(columns={'Long_': 'Long'}, inplace=True)
            data.to_csv(csv, index=False, float_format='%.5f')
        super().reshape_data()

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        data = self.preprocessed
        drop_cols = [c for c in data.columns if c not in COLUMNS_ANALYSIS]
        data.drop(drop_cols, inplace=True, axis=1)
        return data
