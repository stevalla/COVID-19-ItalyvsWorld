import re
import glob

import pandas as pd

from covid_analysis.utils import DATA_DIR


class DataPreprocessing:

    def __init__(self, country):
        self.country = country
        try:
            self.preprocessed = pd.read_csv('{}../cleaned/{}.csv'
                                            .format(DATA_DIR, country))
        except FileNotFoundError:
            self.preprocessed = pd.DataFrame()

        self.files = [f for f in glob.glob(DATA_DIR + '{}/*.csv'.format(country))
                      if re.search('^(.*).csv$', f)]
        assert self.files

    def reshape_data(self):
        raise NotImplementedError('Implement your reshaper')

    def make_consistent(self):
        raise NotImplementedError('Data must be consistent')

    def check_data(self, data):
        assert True

    def integer_with_nan(self, df, col):
        df[col] = df[col].fillna(-1)
        return df

