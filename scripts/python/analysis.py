import os
import sys
import logging.config

import numpy as np
import pandas as pd

from IPython.display import display
from .preprocessing import ROOT_DIR

logging.config.fileConfig(os.path.join(ROOT_DIR, 'logging.conf'))
logging.captureWarnings(True)
log = logging.getLogger(__name__)

sign = '='*50


class CovidReader:

    def __init__(self, filepath):
        self._raw_data = self._load_data(filepath)
        self._data = self._clean_data()
        self._data_splitted = self._split_data(self._data)
        self._status_types = ['Confirmed', 'Recovered', 'Death']

    def data(self, status=None, raw=False):
        if raw:
            return self._raw_data
        if status is not None:
            assert status in self._status_types
            return self._data_splitted[status]
        return self._data

    def get_last_update(self):
        update = {}
        for s in self._status_types:
            update[s] = self._calculate_last_update(s)
        update['total'] = self._calculate_last_update('total')
        return update

    def _calculate_last_update(self, status):
        """Return a dataframe with some information for each region and
        for the aggregate data"""
        region = 'Country/Region'
        data = self._data_splitted[status]
        data.sort('date', ascending=1)

        log.info('Last five rows')
        display(data.tail(5))

        update = self._data[region].copy()
        update['Last update'] = np.nan

        countries = data[region].unique()
        for c in countries:
            last_update = data[data[region] == c].loc[-1]
            row = [c, last_update]
            update = self._add_row_to_df(update, row)
        return update

    def _add_row_to_df(self, df, row):
        df.loc[-1] = row
        df.index = df.index + 1
        df = df.reset_index()   # use sort_index to put as first line (now last)
        return df

    def _load_data(self, filepath):
        def date_parser(x):
            return pd.datetime.strptime(x, '%m-%d-%y')

        try:
            data = pd.read_csv(filepath, parse_dates=['date'],
                               date_parser=date_parser)
        except FileNotFoundError:
            raise FileNotFoundError("The file doesn't exist")

        log.info('Loaded data, shape is {}'.format(data.shape))
        return data

    def _clean_data(self):
        data = self._raw_data
        log.info('Dropping Province/State column')
        data.drop(columns=['Province/State'], inplace=True, axis=1)
        data.dropna(inplace=True)
        log.info('Data shape after removing nan rows is {}'.format(data.shape))
        return data

    def _split_data(self, data):
        data_splitted = {}
        for s in self._status_types:
            data_ = data.copy()
            other_cols = [s_ for s_ in self._status_types if s_ != s]
            data_splitted[s] = data_.drop(other_cols, axis=1)
        return data_splitted


class Plotter:

    def __init__(self, data):
        self._data = data


def store_update_pdf(update):
    # TODO
    pass


if __name__ == '__main__':
    country = sys.argv[1]
    assert country in ['italy', 'world', 'total']
    filepath = ROOT_DIR + 'data/cleaned/{}'.format(country)

    reader = CovidReader(filepath)

    log.info('{0:} DAILY UPDATE {0:}'.format(sign))
    daily_update = reader.get_last_update()
    display(daily_update)
    store_update_pdf(daily_update)

    log.info('{0:} PLOTTING {0:}'.format(sign))
    plotter = Plotter(reader.data)

