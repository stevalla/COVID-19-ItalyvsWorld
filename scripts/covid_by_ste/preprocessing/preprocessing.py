import re
import sys
import glob
import logging
import datetime

import pandas as pd

from covid_analysis.utils import ROOT_DIR

log = logging.getLogger(__name__)


def unify_data(csv_dir, country, reshaper):
    try:
        unified = pd.read_csv('{}../cleaned/{}.csv'.format(csv_dir, country))
    except FileNotFoundError:
        unified = pd.DataFrame()
    current_data = pd.DataFrame()

    for csv_file in glob.glob(csv_dir + '*.csv'):
        if not re.search('^(.*).csv$', csv_file):
            continue
        data = pd.read_csv(csv_file)
        _check_data(data, country)
        if country == 'world':
            args = (unified, data, csv_file, current_data)
        else:
            args = (unified, data)
        current_data = reshaper(*args)

    # update data with current new data
    unified = pd.concat(([unified, current_data]))

    for c in ['Confirmed', 'Recovered', 'Deaths']:
        unified = _integer_with_nan(unified, c)

    unified.to_csv('{}/cleaned/{}.csv'.format(csv_dir, country), index=False,
                   float_format='%.5f')
    return unified


def _integer_with_nan(df, col):
    df[col] = (df[col]
                .fillna(-1)
                .astype(int)
                .astype(object)
                .where(df[col].notnull()))
    return df


def _check_data(data, country):
    if country == 'italy':
        columns = ['data', 'denominazione_regione', 'lat', 'long', 'deceduti',
                    'dimessi_guariti', 'totale_casi']
        assert data['data'][0] == '2020-02-24 18:00:00'
    elif country == 'world':
        columns = ['Province/State', 'Country/Region', 'Lat', 'Long']
        assert '1/22/20' in data.columns
    assert all(d in data.columns for d in columns)


def reshape_italy_data(unified, data):
    mapping = {'Province/State': 'denominazione_regione',
               'Lat': 'lat', 'Long': 'long', 'date': 'data',
               'Deaths': 'deceduti',
               'Confirmed': 'totale_casi',
               'Recovered': 'dimessi_guariti'}

    dates, d_mapping = _convert_dates(data['data'])
    data = data[mapping.values()]

    if not unified.empty:
        dates = tuple(d for d in dates if d not in unified['date'].unique())
        italy_dates = (d_i for d_w, d_i in d_mapping.items()
                       if d_w not in unified['date'].unique())
        if not dates:
            print("The data are up to date with those in italy")
            return None
        data = data.loc[data['data'].isin(list(italy_dates))]

    del mapping['date']
    new_data = pd.DataFrame({c: data[k] for c, k in mapping.items()})
    new_data.insert(loc=1, column='Country/Region', value='Italy')
    new_data.insert(loc=4, column='date', value=dates)
    return new_data


def _convert_dates(dates):
    new_dates = []
    mapping = {}
    for date in dates:
        w_date = _convert_date(date)
        new_dates.append(w_date)
        mapping[w_date] = date
    return new_dates, mapping


def _convert_date(date):
    """From Italy format to world format. (Default)"""
    date = date.split(' ')[0].split('-')
    date[0] = date[0][2:]
    new_date = [int(d) for d in date]
    new_date = '{0[1]:}/{0[2]:}/{0[0]:}'.format(new_date)
    return new_date


def reshape_world_data(unified, data, csv_file, current_data):
    new_data = pd.DataFrame()
    current_data = current_data
    file_type = re.search('^.*-covid-(.*).csv$', csv_file).group(1)
    time_series = data.iloc[:, 4:]

    # drop time_series
    data.drop(columns=time_series.columns, inplace=True, axis=1)
    assert data.shape[1] == 4

    if not unified.empty:
        dates_to_add = (d for d in time_series.columns
                        if d not in unified['date'].unique())
        time_series = time_series[dates_to_add]

    if not list(time_series.columns):
        print("The data are up to date with those in world")
        return current_data

    for serie in time_series.columns:
        # copy province and country columns
        tmp_data = data.copy()
        # add date column
        tmp_data['date'] = serie
        # add $file_type column
        tmp_data[file_type] = time_series[serie]

        # merge into new_data
        # check all region are ordered the same
        if not new_data.empty:
            for col in ['Province/State', 'Country/Region']:
                assert all([r1 == r2 or all(pd.isna([r1, r2]))
                            for r1, r2 in zip(new_data[col], tmp_data[col])])
        new_data = pd.concat([new_data, tmp_data])

    if current_data.empty:
        current_data = new_data
    else:
        # check if dates are ordered the same
        assert all(d1 == d2 for d1, d2 in zip(current_data['date'],
                                              new_data['date']))
        current_data[file_type] = new_data[file_type]
    return current_data


def aggregate_data():
    data_dir = '{}/data/cleaned/'.format(ROOT_DIR)
    italy = pd.read_csv('{}italy.csv'.format(data_dir))
    world = pd.read_csv('{}world.csv'.format(data_dir))
    all_dates = list(set(world['date']) | set(italy['date']))
    all_dates.sort(key=lambda d: datetime.datetime.strptime(d, '%m/%d/%y'))

    try:
        total = pd.read_csv('{}../cleaned/total.csv'.format(data_dir))
        all_dates = tuple(d for d in all_dates if d not in total['date'].unique()
                          and d in world['date'].unique())
    except FileNotFoundError:
        total = pd.DataFrame()

    world_dates = tuple(d for d in all_dates if d in world['date'].unique())
    italy_dates = tuple(d for d in all_dates if d in italy['date'].unique())

    italy_shape = italy.shape
    world_shape = world.shape
    world = world[world['Country/Region'] != 'Italy']
    removed = world_shape[0] - world.shape[0]

    for d in all_dates:
        if d in italy_dates and d in world_dates:
            tmp = pd.concat([world[world['date'] == d], italy[italy['date'] == d]])
            total = pd.concat([total, tmp])
        else:
            total = pd.concat([total, world[world['date'] == d]])

    assert italy_shape[1] == world_shape[1] == total.shape[1]
    try:
        assert italy_shape[0] + world_shape[0] - removed == total.shape[0]
    except AssertionError:
        log.info('The total size seems to be not correct, check the dates of ' 
                 'italy and world csv, Italy may has one date more.')

    for c in ['Confirmed', 'Recovered', 'Deaths']:
        total = _integer_with_nan(total, c)
    total.to_csv('{}total.csv'.format(data_dir), index=False,
                 float_format='%.5f')


if __name__ == '__main__':
    country = sys.argv[1]
    csv_dir = '{}/data/'.format(ROOT_DIR)
    if country == 'italy':
        reshaper = reshape_italy_data
    else:
        reshaper = reshape_world_data
    data = unify_data(csv_dir, country, reshaper)
