import numpy as np
import pandas as pd

from datetime import timedelta
from definitions import STATUS_TYPES
from covid_analysis.data_handler.dataset_factory import DatasetFactory

COUNTRY = 'Country/Region'


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

    def increments_in_time(self, ma_days=5):
        increments = self._group_by_country_rate_days('increment')
        mas = self._moving_average(increments, ma_days)
        return increments, mas

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

    def _moving_average(self, data, days=5):
        """ Compute the moving average. The data is expected to be a
        dictionary of status types and data frames having dates
        as index. It performs the average by columns. """
        mas = {}
        for s in STATUS_TYPES:
            dates = data[s].index[days:]
            mas[s] = pd.DataFrame(columns=data[s].columns, index=dates)
            for end in dates:
                start = end - timedelta(days=days)
                mas[s].loc[end] = np.mean(data[s][start:end].values, axis=0)
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
