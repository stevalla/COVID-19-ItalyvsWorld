import re
import logging

import numpy as np
import pandas as pd

from definitions import DATA_DIR, STATUS_TYPES, COUNTRY, COLUMNS_ANALYSIS
from definitions import yesterday, STATE
from data_preparation.data_preprocessing import DataPreprocessing

log = logging.getLogger(__name__)


class WorldPreprocessing(DataPreprocessing):

    def __init__(self, country):
        super().__init__(country)
        self.files = [f for f in self.files
                      if re.search('^.*(confirmed|deaths)_global.csv$', f)]
        self._csv_regex = '^.*_covid19_(.*)_global.csv$'

    def reshape_data(self):
        new_data = pd.DataFrame()
        for csv in self.files:
            data = pd.read_csv(csv)
            self.check_data(data)

            file_type = re.search(self._csv_regex, csv).group(1)
            start_index = [i for i, c in enumerate(data.columns)
                           if c in ['1/22/2020', '1/22/20']][0]
            time_series = data.iloc[:, start_index:]

            data.drop(columns=time_series.columns, inplace=True, axis=1)

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
        self._fillnan()
        assert all(~self.preprocessed.duplicated(keep='first')), print('Duplicates')
        self.preprocessed.to_csv('{}/cleaned/{}.csv'.format(DATA_DIR,
                                                            self.country),
                                 index=False, float_format='%.5f')

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        data = self.preprocessed.copy()
        data = data[(data[COUNTRY] != 'Italy') & (data[COUNTRY] != 'US')]
        data['iso3'] = self._add_isos(data)
        data = data.reindex(columns=COLUMNS_ANALYSIS)
        return data

    def check_data(self, data):
        columns = [STATE, COUNTRY, 'Lat', 'Long']
        assert '1/22/20' in data.columns or '1/22/2020' in data.columns
        yest = yesterday().timetuple()
        yest = '{0[1]:}/{0[2]:}/{0[0]}'.format(yest)
        assert yest in data.columns or yest[:-2] in data.columns, \
            print(yest, data.columns[-1])
        assert all(d in data.columns for d in columns)

    def _add_isos(self, data):
        url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/' \
              'master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'
        iso_table = pd.read_csv(url)
        isos, misses = [], []
        data = data.copy().reset_index()
        for i in data.index:
            iso_mask = (iso_table['Country_Region'] == data.loc[i, COUNTRY])
            if not data.loc[i, STATE] is np.nan:
                iso_mask &= (iso_table['Province_State'] == data.loc[i, STATE])
            try:
                isos.append(iso_table[iso_mask]['iso3'].values[0])
            except IndexError:
                miss = '{} - {}'.format(data.loc[i, COUNTRY], data.loc[i, STATE])
                if not any(miss == m for m in misses):
                    misses.append(miss)
                isos.append('NOT PRESENT')
        if misses:
            log.info('not present iso3 are {}'.format(misses))
        return isos

    def _load_series(self, data, time_series, file_type):
        new_data = pd.DataFrame()
        for serie in time_series.columns:
            tmp = data.copy()
            tmp['date'] = '{0[0]:}/{0[1]:}/{0[2]:.2}'.format(serie.split('/'))
            tmp[file_type] = time_series[serie]

            # check all region are ordered the same
            if not new_data.empty:
                for col in [STATE, COUNTRY]:
                    assert all([r1 == r2 or all(pd.isna([r1, r2]))
                                for r1, r2 in zip(new_data[col], tmp[col])])
            new_data = pd.concat([new_data, tmp])
        return new_data

    def _fillnan(self):
        for col in STATUS_TYPES:
            self.preprocessed = super().fillnan(self.preprocessed, col)
            assert not self.preprocessed[col].isnull().values.any()
