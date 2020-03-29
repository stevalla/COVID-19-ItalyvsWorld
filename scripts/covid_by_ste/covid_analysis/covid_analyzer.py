import numpy as np
import pandas as pd

from covid_analysis.utils import STATUS_TYPES
from covid_analysis.data_handler.dataset_factory import DatasetFactory

COUNTRY = 'Country/Region'


class CovidAnalyzer:

    def __init__(self, filepaths):
        self._data_factory = DatasetFactory(filepaths)

    @property
    def data(self):
        return self._data_factory.get_data()

    def histograms_per_country(self):
        all_data = self._data_factory.get_data()
        country_grouped = all_data.groupby([COUNTRY, 'date']).sum()[STATUS_TYPES]

        increments = {}
        for s in STATUS_TYPES:
            ts = country_grouped[s].unstack(COUNTRY, fill_value=-1)
            increments[s] = self._calculate_increment_per_day(ts)
        increments = self._prepare_for_plotting(increments)
        return increments

    def _calculate_increment_per_day(self, serie):
        increments = np.zeros(serie.shape)
        values = serie.values
        for day in range(1, serie.shape[0]):
            increments[day] = values[day] - values[day - 1]
        res = pd.DataFrame(increments, columns=serie.columns, index=serie.index)
        return res

    def grow_rate_per_country(self):
        all_data = self._data_factory.get_data()
        country_grouped = all_data.groupby([COUNTRY, 'date']).sum()[STATUS_TYPES]

        grow_rates = {}
        for s in STATUS_TYPES:
            ts = country_grouped[s].unstack(COUNTRY, fill_value=0)
            grow_rates[s] = self._calculate_grow_rate(ts)
        sorted_cols = self._sort_cols_by_confirmed(
            country_grouped['confirmed'].unstack(COUNTRY, fill_value=-1)
        )
        for s in STATUS_TYPES:
            grow_rates[s] = grow_rates[s].reindex(columns=sorted_cols)
        return grow_rates

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

    def _prepare_for_plotting(self, data):
        prepared = {}
        sorted_cols = self._sort_cols_by_confirmed(data['confirmed'])
        for s in STATUS_TYPES:
            prepared[s] = data[s].reindex(columns=sorted_cols)
        return prepared

    def _sort_cols_by_confirmed(self, data):
        sums = data.sum(axis=0)
        sort_indexes = np.argsort(-sums.values)
        sorted_cols = []
        for i in sort_indexes:
            sorted_cols.append(data.columns[i])
        return sorted_cols
