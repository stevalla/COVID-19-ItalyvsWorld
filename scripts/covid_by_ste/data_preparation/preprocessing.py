import logging
import datetime
import data_preparation

import numpy as np
import pandas as pd

from datetime import timedelta
from covid_analysis.utils import ROOT_DIR, STATUS_TYPES, VALID_DATASETS
from covid_analysis.utils import yesterday


log = logging.getLogger(__name__)


def preprocess_data():
    datasets = set(VALID_DATASETS) - {'total'}
    data_dir = '{}/data/cleaned/'.format(ROOT_DIR)

    try:
        total = pd.read_csv('{}../cleaned/total.csv'.format(data_dir))
        total_dates = total['date'].unique()
    except FileNotFoundError:
        total = pd.DataFrame()
        total_dates = []

    all_data = []
    dates_per_dataset = {}
    for csv in datasets:
        preprocesser = getattr(data_preparation, '{}Preprocessing'
                               .format(csv.capitalize()))(csv)
        preprocesser.reshape_data()
        data = preprocesser.make_consistent()
        dates_per_dataset[csv] = [date for date in data['date'].unique()
                                  if date not in total_dates]
        all_data.append(data)

    all_dates = list(set([date for list_of_dates in
                          [dates_per_dataset[dataset] for dataset in datasets]
                          for date in list_of_dates]))
    all_dates.sort(key=lambda d: datetime.datetime.strptime(d, '%m/%d/%y'))

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

    log.info('Total number of countries is {}'.format(
        len(list(total['Country/Region'].unique()))
    ))


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
        log.warning('Less countries than yesterday!')

    for s in STATUS_TYPES:
        try:
            assert np.all(data_new[s].values >= data_old[s].values)
        except AssertionError:
            check = False
            countries = data[data.index.isin(
                data_new[s][~(data_new[s].values >= data_old[s].values)].index
            )]['Country/Region'].unique()
            log.info("Inconsistency in the time series {} for countries {}"
                     .format(s, countries))
    return check


if __name__ == '__main__':
    preprocess_data()
