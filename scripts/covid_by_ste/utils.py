import os
import warnings
import chart_studio
import logging.config
import matplotlib.style

import pandas as pd

from PyPDF2 import PdfFileReader, PdfFileWriter
from matplotlib.backends.backend_pdf import PdfPages
from definitions import SCRIPTS_DIR, DIRS, yesterday

# WARNINGS
warnings.simplefilter(action='ignore', category=FutureWarning)

# LOGGER CONFIGURATION
logging.config.fileConfig(os.path.join(SCRIPTS_DIR, 'logging.conf'))
logging.captureWarnings(True)

# PLOT STYLE
matplotlib.style.use('ggplot')

# PANDAS OPTIONS
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# PLOTlY CREDENTIALS
chart_studio.tools.set_credentials_file(username='stev94',
                                        api_key='GDrUj4Joe1xYEROBE0P3')


# WRAPPER FOR STORING IMAGES ON PDF
def wrapper_store_pdf(fun, filename, *args, **kwargs):
    with PdfPages(filename) as pdf:
        fun(pdf, *args, **kwargs)
        d = pdf.infodict()
        d['Title'] = 'Histograms at {}'.format(yesterday())


def merge_pdf(final_path):
    tmp_path = os.path.join(DIRS['result'], 'tmp.pdf')
    final_path = os.path.join(DIRS['result'], final_path)
    merged_filepath = os.path.join(DIRS['result'], 'merged.pdf')

    output = PdfFileWriter()
    pdf1 = PdfFileReader(open(tmp_path, "rb"))

    for page in pdf1.pages:
        output.addPage(page)
    try:
        pdf2 = PdfFileReader(open(final_path, "rb"))
        for page in pdf2.pages:
            output.addPage(page)
    except FileNotFoundError:
        pass

    outfile = open(merged_filepath, "wb")
    output.write(outfile)
    outfile.close()
    os.rename(merged_filepath, final_path)
    os.remove(tmp_path)