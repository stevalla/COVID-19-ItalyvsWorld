import os
import warnings
import logging.config
import matplotlib.style

from datetime import date, timedelta
from matplotlib.backends.backend_pdf import PdfPages

# WARNINGS
warnings.simplefilter(action='ignore', category=FutureWarning)

# DIRECTORIES
ROOT_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT_DIR = os.path.join(ROOT_DIR, 'scripts/covid_by_ste')
DATA_DIR = os.path.join(ROOT_DIR, 'data/')
RESULT_DIR = os.path.join(ROOT_DIR, 'results/')
DIRS = {'root': ROOT_DIR, 'script': SCRIPT_DIR,
        'result': RESULT_DIR, 'data': DATA_DIR}

# LOGGER CONFIGURATION
logging.config.fileConfig(os.path.join(SCRIPT_DIR, 'logging.conf'))
logging.captureWarnings(True)

# CONSTANTS
VALID_DATASETS = ['italy', 'world', 'usa', 'total']
STATUS_TYPES = ['confirmed', 'deaths']
COLUMNS_ANALYSIS = ['Province/State', 'Country/Region', 'Lat', 'Long', 'date'] \
                   + STATUS_TYPES

# PLOT STYLE
matplotlib.style.use('ggplot')


# KERNEL ESTIMATION ERRORS
KernelEstimationError = (ValueError, ZeroDivisionError, RuntimeError)


# UTILITIES
def yesterday():
    return date.today() - timedelta(days=1)


# WRAPPER FOR STORING IMAGES ON PDF
def wrapper_store_pdf(fun, filename, *args, **kwargs):
    with PdfPages(filename) as pdf:
        fun(pdf, *args, **kwargs)
        d = pdf.infodict()
        d['Title'] = 'Histograms at {}'.format(yesterday())
