import numpy as np
import pandas as pd

from covid_analysis.utils import STATUS_TYPES
from covid_analysis.data_handler.dataset_factory import DatasetFactory

COUNTRY = 'Country/Region'


class CovidAnalyzer:

    def __init__(self, filepaths):
        self._data_factory = DatasetFactory(filepaths)
        self._split_data_by_status()

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

    def grow_rate_per_country(self, status=None):
        # TODO: refactor
        data_ = self._data_factory.get_data(name=status)
        countries = data_[COUNTRY].unique()

        grow_rates = {}
        for c in countries:
            grow_rates[c] = pd.DataFrame()
            data = data_[data_[COUNTRY] == c].copy()
            data = data.groupby([COUNTRY, 'date']).agg('sum')
            for s in STATUS_TYPES:
                serie = data[s].unstack('date')
                grow_rates[c]['date'] = serie.columns.values
                values = serie.values.reshape(-1)
                grow_rates[c][s] = self._calculate_grow_rate(values)
        return grow_rates

    def _calculate_increment_per_day(self, serie):
        increments = np.zeros(serie.shape)
        values = serie.values
        for day in range(1, serie.shape[0]):
            increments[day] = values[day] - values[day - 1]
        res = pd.DataFrame(increments, columns=serie.columns, index=serie.index)
        return res

    def _calculate_grow_rate(self, serie):
        grow_rate = np.zeros(serie.shape[0])
        for day in range(1, serie.shape[0] + 1):
            if serie[day - 1] == 0:
                grow_rate[day] = 0
            else:
                grow_rate[day] = (serie[day] - serie[day - 1]) \
                                 / serie[day - 1] * 100
        return grow_rate

    def _split_data_by_status(self):
        """ Create three custom datasets, one for each status"""
        for s in STATUS_TYPES:
            data = self._data_factory.get_data()
            cols = [c for c in data if c not in STATUS_TYPES] + [s]
            self._data_factory.create_dataset_from_columns(cols, s)

    def _prepare_for_plotting(self, data):
        prepared = {}
        sorted_cols = self._sort_cols_by_confirmed(data['Confirmed'])
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
