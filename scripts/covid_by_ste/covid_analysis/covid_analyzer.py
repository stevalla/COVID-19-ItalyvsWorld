import numpy as np
import pandas as pd

from scripts.covid_by_ste.covid_analysis.utils import STATUS_TYPES
from scripts.covid_by_ste.covid_analysis.plotter import Plotter
from scripts.covid_by_ste.covid_analysis.data_handler.dataset_factory import DatasetFactory

COUNTRY = 'Country/Region'


class CovidAnalyzer:

    def __init__(self, filepaths):
        self._data_factory = DatasetFactory(filepaths)
        self._split_data_by_status()
        self._plotter = Plotter(self._data_factory.get_data())

    def grow_rate_per_country(self, status=None):
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
        self._plotter.plot_grow_rate_per_country(grow_rates)

    def _calculate_grow_rate(self, serie):
        grow_rate = np.zeros(serie.shape[0])
        for day in range(1, serie.shape[0]):
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
