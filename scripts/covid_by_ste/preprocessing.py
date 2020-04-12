import logging

import data_preparation

import numpy as np
import pandas as pd

from IPython.display import display
from datetime import datetime, timedelta
from definitions import yesterday, COLUMNS_ANALYSIS
from definitions import ROOT_DIR, STATUS_TYPES, VALID_DATASETS, COUNTRY


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
        log.info('Preprocessing {}'.format(csv))
        preprocesser = getattr(data_preparation, '{}Preprocessing'
                               .format(csv.capitalize()))(csv)
        preprocesser.reshape_data()
        data = preprocesser.make_consistent()
        assert all(c in data.columns for c in COLUMNS_ANALYSIS)
        dates_per_dataset[csv] = [date for date in data['date'].unique()
                                  if date not in total_dates]
        all_data.append(data)

    all_dates = list(set([date for list_of_dates in
                          [dates_per_dataset[dataset] for dataset in datasets]
                          for date in list_of_dates]))
    all_dates.sort(key=lambda d: datetime.strptime(d, '%m/%d/%y'))

    for d in all_dates:
        total = pd.concat([total, *[data[data['date'] == d] for data in all_data
                                    if d in data['date'].values]])

    total = total.sort_values(['date', 'Country/Region'])
    log.info('Update success. Checking consistency...')
    # assert all columns equal
    for data in all_data:
        assert data.shape[1] == total.shape[1]
    # assert number of rows equal to the sum of all csvs
    try:
        assert sum([d.shape[0] for d in all_data]) == total.shape[0]
    except AssertionError:
        log.info('The total size seems to be not correct, check the dates of ' 
                 'the csvs, Italy may has one date more.')
        log.info('Shapes: italy {}, world {}, usa {}, total {}'
                 .format(*[d.shape[0] for d in all_data], total.shape[0]))

    for c in STATUS_TYPES:
        total[c] = total[c].fillna(-1)
    total.to_csv('{}total.csv'.format(data_dir), index=False,
                 float_format='%.5f')
    if check_consistency(total.copy()):
        log.info('New data loaded correctly')

    log.info('Total number of countries is {}'.format(
        len(list(total[COUNTRY].unique()))
    ))


def check_consistency(data):
    check = True
    new_date = '{0[1]:}/{0[2]:}/{0[0]}'.format(yesterday().timetuple())
    old = yesterday() - timedelta(days=1)
    old_date = '{0[1]:}/{0[2]:}/{0[0]}'.format(old.timetuple())
    data_old = data[data['date'] == old_date[:-2]]
    data_new = data[data['date'] == new_date[:-2]]
    cols = [COUNTRY, 'Province/State', 'date']

    try:
        assert set(data_old[COUNTRY].values) <= set(data_new[COUNTRY].values)
    except AssertionError:
        check = False
        log.warning('Fewer countries than yesterday!')

    for s in STATUS_TYPES:
        if data_old.shape[0] != data_new.shape[0]:
            log.debug('Data old has more or few cols than data new')
            break
        try:
            assert np.all(data_new[s].values >= data_old[s].values)
        except AssertionError:
            check = False
            countries = data[data.index.isin(
                data_new[s][~(data_new[s].values >= data_old[s].values)].index
            )][COUNTRY].unique()
            log.info("Inconsistency in the time series {} for countries {}"
                     .format(s, countries))
            d_old = data[data.index.isin(data_old[s].index)].reset_index(drop=True)
            d_new = data[data.index.isin(data_new[s].index)].reset_index(drop=True)
            for c in countries:
                if d_old.empty:
                    log.info('Country {} first observation today'.format(c))
                else:
                    old = d_old[d_old[COUNTRY] == c][s]
                    new = d_new[d_new[COUNTRY] == c][s]
                    wrong = old > new
                    df = d_old[d_old[COUNTRY] == c][wrong][cols]
                    df[s] = old[wrong]
                    df['date_new'] = d_new[d_new[COUNTRY] == c][wrong]['date']
                    df['{}_new'.format(s)] = new[wrong]
                    log.info('Country {} wrong values are'.format(c))
                    display(df)
    return check


if __name__ == '__main__':
    log.info('{0:} Starting data update {0:}'.format('='*80))
    preprocess_data()
