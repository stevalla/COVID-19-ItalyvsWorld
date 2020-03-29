import numpy as np
import pandas as pd

from covid_analysis.utils import yesterday
from data_preparation.data_preprocessing import DataPreprocessing, DATA_DIR


class ItalyPreprocessing(DataPreprocessing):

    def __init__(self, country='italy'):
        super().__init__(country)

    def reshape_data(self):
        data = pd.read_csv(self.files[0])
        self.check_data(data)
        dates, d_mapping = self._convert_dates(data['data'])

        if not self.preprocessed.empty:
            dates = tuple(d for d in dates
                          if d not in self.preprocessed['date'].unique())
            italy_dates = (d_i for d_w, d_i in d_mapping.items()
                           if d_w not in self.preprocessed['date'].unique())
            if not dates:
                print("Italy data are up to date")
                return
            data = data.loc[data['data'].isin(list(italy_dates))]

        data['data'] = dates
        data.drop(['note_en', 'note_it'], inplace=True, axis=1)
        self.preprocessed = pd.concat([self.preprocessed, data])
        self._integer_with_nan()
        self.preprocessed = self._aggregate_provinces(self.preprocessed)
        self.preprocessed.to_csv('{}/cleaned/italy.csv'.format(DATA_DIR),
                                 index=False, float_format='%.5f')

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        mapping = {'Province/State': 'denominazione_regione',
                   'Lat': 'lat', 'Long': 'long',
                   'deaths': 'deceduti',
                   'confirmed': 'totale_casi'}
        data = pd.DataFrame({c: self.preprocessed[k] for c, k in mapping.items()})
        data.insert(loc=1, column='Country/Region', value='Italy')
        dates = self.preprocessed['data']
        data.insert(loc=4, column='date', value=dates)
        return data

    def check_data(self, data):
        columns = ['data', 'denominazione_regione', 'lat', 'long', 'deceduti',
                    'dimessi_guariti', 'totale_casi']
        assert data['data'][0] == '2020-02-24T18:00:00'
        yest = '{}T17:00:00'.format(yesterday().isoformat())
        assert yest in data['data'].values
        assert all(d in data.columns for d in columns)

    def _aggregate_provinces(self, data):
        trento = 'P.A. Trento'
        bolzano = 'P.A. Bolzano'
        trentino_data = data[(data['denominazione_regione'] == trento) |
                             (data['denominazione_regione'] == bolzano)]
        data.drop(trentino_data.index, axis=0, inplace=True)
        agg_trentino = {c: 'first' if c in ['codice_regione', 'stato'] else
                            np.average if c in ['lat', 'long'] else
                            np.sum for c in data.columns
                        if c not in ['data', 'denominazione_regione']}
        trentino_data = trentino_data.groupby('data').agg(agg_trentino)
        trentino_data.insert(2, 'denominazione_regione', 'Trentino Alto Adige')
        trentino_data.reset_index(inplace=True)
        new_data = pd.DataFrame()
        for d in data['data'].unique():
            new_data = pd.concat([new_data, data[data['data'] == d],
                                  trentino_data[trentino_data['data'] == d]])
        return new_data

    def _integer_with_nan(self):
        for col in ['deceduti', 'totale_casi']:
            self.preprocessed = super().integer_with_nan(self.preprocessed, col)
            assert not self.preprocessed[col].isnull().values.any()

    def _convert_dates(self, dates):
        new_dates = []
        mapping = {}
        for date in dates:
            w_date = self._convert_date(date)
            new_dates.append(w_date)
            mapping[w_date] = date
        return new_dates, mapping

    def _convert_date(self, date):
        """From Italy format to world format. (Default)"""
        date = date[:11].split('T')[0].split('-')
        date[0] = date[0][2:]
        new_date = [int(d) for d in date]
        new_date = '{0[1]:}/{0[2]:}/{0[0]:}'.format(new_date)
        return new_date
