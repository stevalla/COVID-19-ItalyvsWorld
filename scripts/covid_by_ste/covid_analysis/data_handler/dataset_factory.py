import os
import logging

import pandas as pd

from covid_analysis.data_handler.dataset import Dataset
from covid_analysis.utils import DIRS, VALID_DATASETS
from covid_analysis.utils import STATUS_TYPES

log = logging.getLogger(__name__)


class DatasetFactory:
    """ This class creates and handles the dict of name->dataset
    objects. It has as input a list of paths to different csv, but
    it has also various method to create dataset directly from other
    dataframe and given them a name. The csvs must have the same columns. If not,
    you can override the merge_csv method """

    def __init__(self, file_paths):
        self._raw_dataset = self._load_data(file_paths)
        self._dataset = self._clean_data(self._raw_dataset)
        self._custom_datasets = self._create_custom_datasets()

    @property
    def get_dates(self):
        return self._dataset['date'].unique()

    def get_data(self, name=None, cleaned=True):
        return self._get_dataset(name, cleaned).data

    def create_dataset_from_columns(self, columns, new_name, name=None):
        """ Create a new dataset with new_name as name from the dataset
         named name, keeping only the columns specified in the input list """
        if name is None:
            data = self._dataset.data
        else:
            data = self._custom_datasets[name].data
        new_dataset = data.copy()
        for c in data.columns:
            if c not in columns:
                new_dataset.drop(c, axis=1, inplace=True)
        self._custom_datasets[new_name] = new_dataset
        return new_dataset

    def clean_dataset(self, name):
        """ Clean the dataset and store a copy of it cleaned """
        if name not in self._custom_datasets:
            raise ValueError('The dataset {} does not exist'.format(name))
        data = self._custom_datasets[name].copy()
        log.info('Cleaning data {} of shape {}'.format(name, data.shape))
        cleaned = self._clean_data(data)
        if cleaned.shape[0] < self._custom_datasets[name].shape[0]:
            self._custom_datasets['{}_cleaned'.format(name)] = cleaned
            log.info('Data shape after cleaning {}'.format(data.shape))
        else:
            log.info('Dataset {} already cleaned'.format(name))

    def merge_datasets(self, datasets):
        """ Take a list of datasets and merge it together by rows. We assume
        that the data has the same columns """
        data = pd.DataFrame()
        for d in datasets:
            data = pd.concat([data, d.data])
        log.info('Merged data has now shape'.format(data.shape))
        return data

    def _get_dataset(self, name, cleaned):
        if name is None and not cleaned:
            return self._raw_dataset
        elif name is None and cleaned:
            return self._dataset
        elif name in self._custom_datasets and not cleaned:
            return self._custom_datasets[name]
        clean_name = '{}_cleaned'.format(name)
        if cleaned and clean_name in self._custom_datasets:
            return self._custom_datasets[clean_name]
        else:
            raise ValueError("The dataset {} is not present".format(name))

    def _load_data(self, file_paths):
        """ Load data from the paths specified and merge it in a unique
        Dataset """
        datasets = []
        for path in file_paths:
            name = path.split('/')[-1].split('.')[0]
            if name not in VALID_DATASETS:
                raise ValueError('Dataset not found')
            filepath = os.path.join(DIRS['data'], path)
            datasets.append(Dataset(filepath))
            log.info('loaded data from {}'.format(filepath))
        data = self.merge_datasets(datasets)
        return Dataset(data=data)

    def _clean_data(self, dataset):
        data = dataset.data.copy()
        log.info('Cleaning: -> Filling nan of columns: recovered, '
                 'confirmed, deaths -> returns')
        new_data = data.copy()
        new_data[STATUS_TYPES] = new_data[STATUS_TYPES].fillna(0)
        return Dataset(data=new_data)

    def _create_custom_datasets(self):
        custom_datasets = {}
        for s in STATUS_TYPES:
            data = self._dataset.data.copy()
            other_cols = [s_ for s_ in STATUS_TYPES if s_ != s]
            data.drop(other_cols, axis=1, inplace=True)
            custom_datasets[s] = Dataset(data=data)
        return custom_datasets
