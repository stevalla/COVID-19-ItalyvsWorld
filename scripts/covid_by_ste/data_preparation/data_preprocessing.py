import re
import glob

import pandas as pd

from definitions import DATA_DIR


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

    def fillnan(self, df, col):
        df[col] = df[col].fillna(-1)
        return df

    def calculate_active_cases(self):
        data = self.preprocessed
        actives = []
        for i, day in enumerate(data['date'].unique()):
            data_day = data[data['date'] == day]
            if i < 20:
                actives.append(data_day['confirmed'] - data_day['deaths'])
            else:
                data_recovered = data['date'].values[i - 20]['confirmed']
                actives.append(data_day['confirmed'] - data_recovered
                               - data_day['deaths'])
        data['active'] = actives
        self.preprocessed = data
