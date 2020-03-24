import os
import logging

import pandas as pd

from covid_analysis.data_handler.dataset import Dataset
from covid_analysis.utils import DIRS, VALID_DATASETS

log = logging.getLogger(__name__)


class DatasetFactory:

    def __init__(self, file_paths):
        self._dataset = self._load_data(file_paths)

    @property
    def get_dates(self):
        return self._dataset.get_data()['date'].unique()

    def get_data(self, raw=False):
        return self._dataset.get_data(raw)

    def merge_datasets(self, datasets):
        """ Take a list of datasets and merge it together by rows. We assume
        that the data has the same columns """
        data = pd.DataFrame()
        for dataset in datasets:
            data = pd.concat([data, dataset.get_data()])
            del dataset
        log.info('Merged data. Shape is {}'.format(data.shape))
        return data

    def _load_data(self, file_paths):
        """ Load data from the paths specified and merge it in a unique
        Dataset """
        datasets = []
        for path in file_paths:
            name = path.split('/')[-1].split('.')[0]
            if name not in VALID_DATASETS:
                raise ValueError('Dataset not found')
            filepath = os.path.join(DIRS['data'], path)
            datasets.append(Dataset(filepath=filepath))
            log.info('loaded data from {}'.format(filepath))
        data = self.merge_datasets(datasets)
        return Dataset(data=data)
