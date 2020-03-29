import logging
import datetime
import data_preparation

import numpy as np
import pandas as pd

from datetime import timedelta
from covid_analysis.utils import ROOT_DIR, STATUS_TYPES, yesterday

log = logging.getLogger(__name__)


def preprocess_data():
    csvs = ['italy', 'world']
    data_dir = '{}/data/cleaned/'.format(ROOT_DIR)

    try:
        total = pd.read_csv('{}../cleaned/total.csv'.format(data_dir))
    except FileNotFoundError:
        total = pd.DataFrame()

    all_data = []
    for csv in csvs:
        preprocesser = getattr(data_preparation, '{}Preprocessing'
                               .format(csv.capitalize()))()
        preprocesser.reshape_data()
        all_data.append(preprocesser.make_consistent())

    all_dates = list(set([d_ for d in [set(d['date']) for d in all_data]
                          for d_ in d]))
    all_dates.sort(key=lambda d: datetime.datetime.strptime(d, '%m/%d/%y'))

    if not total.empty:
        all_dates = tuple(d for d in all_dates if d not in total['date'].unique()
                          and d in all_data[1]['date'].unique())

    for d in all_dates:
        total = pd.concat([total, *[data[data['date'] == d] for data in all_data
                                    if d in data['date'].values]])

    # assert all columns equal
    for data in all_data:
        assert data.shape[1] == total.shape[1]
    # assert number of rows equal to the sum of all csvs
    try:
        assert sum([d.shape[0] for d in all_data]) == total.shape[0]
    except AssertionError:
        log.info('The total size seems to be not correct, check the dates of ' 
                 'the csvs, Italy may has one date more.')

    for c in STATUS_TYPES:
        total[c] = total[c].fillna(-1)
    total.to_csv('{}total.csv'.format(data_dir), index=False,
                 float_format='%.5f')
    if check_consistency(total):
        log.info('New data loaded correctly')


def check_consistency(data):
    check = True
    reg = 'Country/Region'
    new_date = '{0[1]:}/{0[2]:}/{0[0]}'.format(yesterday().timetuple())
    old = yesterday() - timedelta(days=1)
    old_date = '{0[1]:}/{0[2]:}/{0[0]}'.format(old.timetuple())
    data_old = data[data['date'] == old_date[:-2]]
    data_new = data[data['date'] == new_date[:-2]]

    try:
        assert set(data_old[reg].values) <= set(data_new[reg].values)
    except AssertionError:
        check = False
        log.info('Inconsistencies in countries')

    for s in STATUS_TYPES:
        try:
            assert np.all(data_new[s].values >= data_old[s].values)
        except AssertionError:
            check = False
            log.info("Inconsistency in the time series {}".format(s))
    return check


if __name__ == '__main__':
    preprocess_data()
