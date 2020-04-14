import re
import logging

import pandas as pd

from definitions import STATUS_TYPES

log = logging.getLogger(__name__)


class Dataset:
    """ This immutable class holds a dataset. It allows performing
    operations on that dataset without modifying it. It just needs
    to have as input the path to the csv """

    def __init__(self, filepath='', data=None):
        assert filepath is not None or data is not None
        if re.search('^.*italy.csv$', filepath) or \
                (data is not None and 'data' in data.columns):
            self._date_field = 'data'
        else:
            self._date_field = 'date'
        self._raw_data = self._load_data(filepath) if data is None else data
        self._data = self._clean_data()
        self._columns = self._data.columns

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    @property
    def n_rows(self):
        return self._data.shape[0]

    @property
    def n_cols(self):
        return self._data.shape[1]

    def get_data(self, raw=False):
        if raw:
            return self._raw_data.copy()
        return self._data.copy()

    def _load_data(self, filepath):
        def date_parser(x):
            return pd.datetime.strptime(x, '%m/%d/%y')

        try:
            data = pd.read_csv(filepath, parse_dates=[self._date_field],
                               date_parser=date_parser)
            data[self._date_field] = data[self._date_field].dt.date
        except FileNotFoundError:
            raise FileNotFoundError("The file doesn't exist")
        log.info('Loaded data, shape is {}'.format(data.shape))
        return data

    def _clean_data(self):
        return self._raw_data
