import os

import matplotlib.pyplot as plt

from matplotlib.backends.backend_pdf import PdfPages
from scripts.covid_by_ste.covid_analysis.utils import DIRS, STATUS_TYPES, yesterday


class Plotter:

    def __init__(self, data):
        self._data = data

    def plot_grow_rate_per_country(self, series):
        filename = 'grow_rates/grow_rate_{}.pdf'.format(yesterday())
        filepath = os.path.join(DIRS['result'], filename)
        with PdfPages(filepath) as pdf:
            for country, df in series.items():
                if df.shape[0] <= 1:
                    continue
                fig = df.set_index('date').plot(figsize=(20, 5)).get_figure()
                fig.autofmt_xdate()
                plt.grid(True)
                plt.legend(STATUS_TYPES)
                plt.ylabel('percentage grow rate', fontsize=24)
                plt.suptitle('{} grow rate'.format(country), fontsize=24)
                pdf.savefig(fig)
                plt.close(fig)
            d = pdf.infodict()
            d['Title'] = 'Grows Rate at {}'.format(yesterday())
