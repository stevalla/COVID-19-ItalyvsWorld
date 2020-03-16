import os
import warnings
import logging.config

from datetime import date, timedelta

# WARNINGS
warnings.simplefilter(action='ignore', category=FutureWarning)

# DIRECTORIES
ROOT_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT_DIR = os.path.join(ROOT_DIR, 'scripts/python')
DATA_DIR = os.path.join(ROOT_DIR, 'data/')
RESULT_DIR = os.path.join(ROOT_DIR, 'results/')
DIRS = {'root': ROOT_DIR, 'script': SCRIPT_DIR,
        'result': RESULT_DIR, 'data': DATA_DIR}

# LOGGER CONFIGURATION
logging.config.fileConfig(os.path.join(SCRIPT_DIR, 'logging.conf'))
logging.captureWarnings(True)

# CONSTANTS
VALID_DATASETS = ['italy', 'world', 'total']
STATUS_TYPES = ['Confirmed', 'Recovered', 'Deaths']


# UTILITIES
def yesterday():
    return date.today() - timedelta(days=1)
