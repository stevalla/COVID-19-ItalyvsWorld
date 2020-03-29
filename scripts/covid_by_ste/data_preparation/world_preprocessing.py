import re

import pandas as pd

from covid_analysis.utils import STATUS_TYPES, yesterday
from data_preparation.data_preprocessing import DataPreprocessing, DATA_DIR


COUNTRY = 'Country/Region'


class WorldPreprocessing(DataPreprocessing):

    def __init__(self, country='world'):
        super().__init__(country)
        self.files = [f for f in self.files
                      if re.search('^.*(confirmed|deaths).*$', f)]

    def reshape_data(self):
        new_data = pd.DataFrame()
        for csv in self.files:
            data = pd.read_csv(csv)
            self.check_data(data)

            file_type = re.search('^.*_covid19_(.*)_global.csv$', csv).group(1)
            time_series = data.iloc[:, 4:]

            data.drop(columns=time_series.columns, inplace=True, axis=1)
            assert data.shape[1] == 4

            if not self.preprocessed.empty:
                dates_to_add = (d for d in time_series.columns
                                if d not in self.preprocessed['date'].unique())
                time_series = time_series[dates_to_add]

            if not list(time_series.columns):
                print("The data are up to date with those in world")
                return

            tmp = self._load_series(data, time_series, file_type)
            if new_data.empty:
                new_data = tmp
            else:
                new_data = pd.concat([new_data, tmp[file_type]], axis=1)

        self.preprocessed = pd.concat([self.preprocessed, new_data])
        self._integer_with_nan()
        self.preprocessed.to_csv('{}/cleaned/world.csv'.format(DATA_DIR),
                                 index=False, float_format='%.5f')

    def _load_series(self, data, time_series, file_type):
        new_data = pd.DataFrame()
        for serie in time_series.columns:
            tmp = data.copy()
            tmp['date'] = serie
            tmp[file_type] = time_series[serie]

            # check all region are ordered the same
            if not new_data.empty:
                for col in ['Province/State', COUNTRY]:
                    assert all([r1 == r2 or all(pd.isna([r1, r2]))
                                for r1, r2 in zip(new_data[col], tmp[col])])
            new_data = pd.concat([new_data, tmp])
        return new_data

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        data = self.preprocessed
        data = data[data[COUNTRY] != 'Italy']
        return data

    def check_data(self, data):
        columns = ['Province/State', COUNTRY, 'Lat', 'Long']
        assert '1/22/20' in data.columns
        yest = yesterday().timetuple()
        yest = '{0[1]:}/{0[2]:}/{0[0]}'.format(yest)
        assert yest[:-2] in data.columns
        assert all(d in data.columns for d in columns)

    def _integer_with_nan(self):
        for col in STATUS_TYPES:
            self.preprocessed = super().integer_with_nan(self.preprocessed, col)
            assert not self.preprocessed[col].isnull().values.any()
