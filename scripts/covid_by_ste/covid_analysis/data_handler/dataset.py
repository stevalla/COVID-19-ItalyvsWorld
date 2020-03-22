import logging

import pandas as pd

log = logging.getLogger(__name__)


class Dataset:
    """ Immutable class that holds a dataset. It allows performing operations
    on that dataset without modifying it. It just needs to have as input the
    path to the csv """

    def __init__(self, filepath=None, data=None):
        assert filepath is not None or data is not None
        self._data = self._load_data(filepath) if data is None else data
        self._columns = self._data.columns

    @property
    def data(self):
        return self._data

    @property
    def n_rows(self):
        return self._data.shape[0]

    @property
    def n_cols(self):
        return self._data.shape[1]

    # TODO: override __copy__ function

    def _load_data(self, filepath):
        def date_parser(x):
            return pd.datetime.strptime(x, '%m/%d/%y')

        try:
            data = pd.read_csv(filepath, parse_dates=['date'],
                               date_parser=date_parser)
            data['date'] = data.date.dt.date
        except FileNotFoundError:
            raise FileNotFoundError("The file doesn't exist")
        log.info('Loaded data, shape is {}'.format(data.shape))
        return data
