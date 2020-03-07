import os
import re
import glob

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def unify_data(world_csv_dir):
    try:
        unified = pd.read_csv(world_csv_dir + '../world.csv')
    except FileNotFoundError:
        unified = None
    current_data = None

    for csv_file in glob.glob(world_csv_dir + '*.csv'):
        if not re.search('.*-covid-(.*).csv', csv_file):
            continue
        file_type = re.search('.*-covid-(.*).csv', csv_file).group(1)
        data = pd.read_csv(csv_file)
        time_series = data.iloc[:, 4:]

        # drop lat, long and time_series
        data.drop(columns=['Lat', 'Long'], inplace=True, axis=1)
        data.drop(columns=time_series.columns, inplace=True, axis=1)
        assert data.shape[1] == 2

        if unified is not None:
            dates_to_add = (d for d in time_series.columns
                            if d not in unified['date'].unique())
            time_series = time_series[dates_to_add]

        if not list(time_series.columns):
            print("The data are up to date with those in publication/world")
            break

        new_data = reshape_data(time_series, data, file_type)

        if current_data is None:
            current_data = new_data
        else:
            # check if dates are ordered the same
            assert all(d1 == d2 for d1, d2 in zip(current_data['date'],
                                                  new_data['date']))
            current_data[file_type] = new_data[file_type]
    # update data with current new data
    unified = pd.concat(([unified, current_data]))
    unified.to_csv(world_csv_dir + '../world.csv')
    return unified


def reshape_data(time_series, data, file_type):
    new_data = None
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
    world_csv_dir = ROOT_DIR + '/data/world/'
    data = unify_data(world_csv_dir)
