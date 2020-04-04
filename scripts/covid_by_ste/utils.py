import os
import warnings
import logging.config
import matplotlib.style

from matplotlib.backends.backend_pdf import PdfPages
from definitions import SCRIPTS_DIR, yesterday

# WARNINGS
warnings.simplefilter(action='ignore', category=FutureWarning)

# LOGGER CONFIGURATION
logging.config.fileConfig(os.path.join(SCRIPTS_DIR, 'logging.conf'))
logging.captureWarnings(True)

# PLOT STYLE
matplotlib.style.use('ggplot')


# WRAPPER FOR STORING IMAGES ON PDF
def wrapper_store_pdf(fun, filename, *args, **kwargs):
    with PdfPages(filename) as pdf:
        fun(pdf, *args, **kwargs)
        d = pdf.infodict()
        d['Title'] = 'Histograms at {}'.format(yesterday())
