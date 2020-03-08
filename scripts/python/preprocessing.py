import os
import re
import sys
import glob

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def unify_data(csv_dir, country, reshaper):
    try:
        unified = pd.read_csv(csv_dir + '../cleaned/' + country + '.csv')
    except FileNotFoundError:
        unified = None
    current_data = None

    for csv_file in glob.glob(csv_dir + '*.csv'):
        print(csv_file)
        if not re.search('^(.*).csv$', csv_file):
            continue
        file_type = re.search('^(.*).csv$', csv_file).group(1)
        data = pd.read_csv(csv_file)

        new_data = reshaper(unified, data, file_type)

        if current_data is None:
            current_data = new_data
        else:
            # check if dates are ordered the same
            assert all(d1 == d2 for d1, d2 in zip(current_data['date'],
                                                  new_data['date']))
            current_data[file_type] = new_data[file_type]

    # update data with current new data
    if unified is None:
        unified = current_data
    else:
        unified = pd.concat(([unified, current_data]))
    unified.to_csv(csv_dir + '../cleaned/' + country + '.csv', index=False)
    return unified


def reshape_italy_data(unified, data, file_type=None):
    new_data = None
    mapping = {'Province/State': 'denominazione_regione',
               'Lat': 'lat', 'Long': 'long', 'date': 'data',
               'Deaths': 'deceduti',
               'Confirmed': 'totale_attualmente_positivi',
               'Recovered': 'totale_ospedalizzati'}

    dates = tuple(_convert_date(d) for d in data['data'])
    data = data[mapping.values()]

    if unified is not None:
        dates = tuple(d for d in dates if d not in unified['date'].unique())
        if not dates:
            print("The data are up to date with those in italy")
            return new_data
        data = data.loc[data['data'] == dates]

    del mapping['date']

    new_data = pd.DataFrame({c: data[k] for c, k in mapping.items()})
    new_data.insert(loc=1, column='Country/Region', value='Italy')
    new_data.insert(loc=4, column='date', value=dates)
    return new_data


def _convert_date(date):
    date = date.split(' ')[0].split('-')
    new_date = [int(d) for d in date]
    new_date = '{0[1]:}/{0[2]:}/{0[0]:}'.format(new_date)
    return new_date


def reshape_world_data(unified, data, file_type):
    new_data = None
    time_series = data.iloc[:, 4:]

    # drop time_series
    data.drop(columns=time_series.columns, inplace=True, axis=1)
    assert data.shape[1] == 4

    if unified is not None:
        dates_to_add = (d for d in time_series.columns
                        if d not in unified['date'].unique())
        time_series = time_series[dates_to_add]

    if not list(time_series.columns):
        print("The data are up to date with those in world")
        return new_data

    for serie in time_series.columns:
        # copy province and country columns
        tmp_data = data.copy()
        # add date column
        tmp_data['date'] = serie
        # add $file_type column
        tmp_data[file_type] = time_series[serie]

        # merge into new_data
        if new_data is None:
            new_data = tmp_data
        else:
            # check all region are ordered the same
            assert all([r1 == r2 or all(pd.isna([r1, r2]))
                        for r1, r2 in zip(new_data['Province/State'],
                                          tmp_data['Province/State'])])
            assert all(r1 == r2 or all(pd.isna([r1, r2]))
                       for r1, r2 in zip(new_data['Country/Region'],
                                         tmp_data['Country/Region']))
            new_data = pd.concat([new_data, tmp_data])
    return new_data


if __name__ == '__main__':
    country = sys.argv[1]
    csv_dir = '{}/data/{}/'.format(ROOT_DIR, country)
    if country == 'italy':
        reshaper = reshape_italy_data
    else:
        reshaper = reshape_world_data
    data = unify_data(csv_dir, country, reshaper)
