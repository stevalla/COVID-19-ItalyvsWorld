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
        self.preprocessed = pd.concat([self.preprocessed, data])
        self._integer_with_nan()
        self.preprocessed.to_csv('{}/cleaned/italy.csv'.format(DATA_DIR),
                                 index=False, float_format='%.5f')

    def make_consistent(self):
        if self.preprocessed.empty:
            raise ValueError("Preprocessed data empty")
        mapping = {'Province/State': 'denominazione_regione',
                   'Lat': 'lat', 'Long': 'long',
                   'deaths': 'deceduti',
                   'confirmed': 'totale_casi',
                   'recovered': 'dimessi_guariti'}
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

    def _integer_with_nan(self):
        for col in ['deceduti', 'totale_casi', 'dimessi_guariti']:
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
