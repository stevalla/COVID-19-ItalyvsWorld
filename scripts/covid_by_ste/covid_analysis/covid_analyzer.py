import numpy as np
import pandas as pd

from datetime import timedelta
from definitions import STATUS_TYPES, COUNTRY, STATE, yesterday
from covid_analysis.data_handler.dataset_factory import DatasetFactory


class CovidAnalyzer:

    def __init__(self, filepaths):
        self._data_factory = DatasetFactory(filepaths)

    @property
    def data(self):
        return self._data_factory.get_data()

    def grow_rates_per_country(self):
        return self._group_by_country_rate_days('grow_rates')

    def histograms_per_country(self):
        return self._group_by_country_rate_days('increment')

    def increments_in_time(self):
        increments = self._group_by_country_rate_days('increment')
        mas = {'short': self._moving_average(increments, 5, 'exp'),
               'long': self._moving_average(increments, 10, 'exp')}
        return increments, mas

    def world_map(self):
        data = self._data_factory.get_data()
        data = data[data['date'] == yesterday() - timedelta(days=1)]
        cols = ['Long', 'Lat', 'date', 'confirmed', 'iso3', STATE, COUNTRY]
        data = data[cols]
        data['country'] = self._world_map_country_names(data)
        return data

    def _world_map_country_names(self, data):
        countries = []
        for i in data.index:
            name = data.loc[i, COUNTRY]
            if not data.loc[i, STATE] is np.nan:
                name += ' {}'.format(data.loc[i, STATE])
            countries.append(name)
        return countries

    def _group_by_country_rate_days(self, rate_op):
        all_data = self._data_factory.get_data()
        country_grouped = all_data.groupby([COUNTRY, 'date']).sum()[STATUS_TYPES]
        if rate_op == 'increment':
            func = self._calculate_increment_per_day
            fill_value = -1
        else:
            func = self._calculate_grow_rate
            fill_value = 0
        sorted_cols = self._sort_cols_by_confirmed(
            country_grouped['confirmed'].unstack(COUNTRY, fill_value=fill_value)
        )
        rates = {}
        for s in STATUS_TYPES:
            ts = country_grouped[s].unstack(COUNTRY, fill_value=-1)
            rates[s] = func(ts).reindex(columns=sorted_cols)
        return rates

    def _moving_average(self, data, days, ma_type='simple'):
        """ Compute the moving average. The data is expected to be a
        dictionary of status types and data frames having dates
        as index. It performs the average by columns. """
        if ma_type == 'simple':
            mas = {s: data[s].rolling(window=days).mean() for s in STATUS_TYPES}
        elif ma_type == 'exp':
            mas = {s: data[s].ewm(span=days, adjust=False).mean()
                   for s in STATUS_TYPES}
        else:
            raise ValueError('Type of moving average not recognized')
        return mas

    def _calculate_increment_per_day(self, series):
        increments = np.zeros(series.shape)
        values = series.values
        for day in range(1, series.shape[0]):
            increments[day] = values[day] - values[day - 1]
        res = pd.DataFrame(increments, columns=series.
                           columns, index=series.index)
        return res

    def _calculate_grow_rate(self, serie):
        grow_rate = np.zeros(serie.shape)
        values = serie.values
        for day in range(1, serie.shape[0]):
            np.seterr(all='ignore')
            grow_rate[day] = abs(np.divide(values[day] - values[day - 1],
                                           values[day - 1]) * 100)
        grow_rate[np.isinf(grow_rate)] = np.nan
        res = pd.DataFrame(grow_rate, columns=serie.columns, index=serie.index)
        return res

    def _sort_cols_by_confirmed(self, data):
        sums = data.sum(axis=0)
        sort_indexes = np.argsort(-sums.values)
        sorted_cols = [data.columns[i] for i in sort_indexes]
        return sorted_cols
