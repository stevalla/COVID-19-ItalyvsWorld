import os

from datetime import date, timedelta, datetime

# DIRECTORIES
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts/covid_by_ste/')
DATA_DIR = os.path.join(ROOT_DIR, 'data/')
RESULT_DIR = os.path.join(ROOT_DIR, 'results/')
DIRS = {'root': ROOT_DIR, 'result': RESULT_DIR,
        'data': DATA_DIR, 'scripts': SCRIPTS_DIR}

# DATA PATH
DATA = 'cleaned/total.csv'
ITALY_DATA = 'cleaned/italy.csv'
USA_DATA = 'cleaned/usa.csv'

# CONSTANTS
VALID_DATASETS = ['italy', 'world', 'usa', 'total']
STATUS_TYPES = ['confirmed', 'deaths']
COLUMNS_ANALYSIS = ['Province/State', 'Country/Region', 'Lat', 'Long', 'date',
                    'iso3'] + STATUS_TYPES
COUNTRY = 'Country/Region'
STATE = 'Province/State'

# KERNEL ESTIMATION ERRORS
KernelEstimationError = (ValueError, ZeroDivisionError, RuntimeError)


# UTILITIES
def yesterday(ts=False):
    if ts:
        date_ = datetime.now() - timedelta(days=1)
        date_ = date_.strftime("%m/%d/%Y %I:%M:%S %p")
        return date_
    else:
        return date.today() - timedelta(days=1)
