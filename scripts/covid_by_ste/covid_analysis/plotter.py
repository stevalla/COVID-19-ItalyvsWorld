import os
import logging
import warnings
import cufflinks

import numpy as np
import seaborn as sb

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from cycler import cycler
from datetime import timedelta
from matplotlib.ticker import FixedLocator
from matplotlib.backends.backend_pdf import PdfPages

from utils import wrapper_store_pdf, merge_pdf
from definitions import DIRS, STATUS_TYPES, yesterday, KernelEstimationError

log = logging.getLogger(__name__)
warnings.simplefilter("error", (RuntimeWarning, UserWarning))
cufflinks.go_offline(connected=True)


class Plotter:

    def __init__(self, data):
        self._data = data

    def plot_grow_rate_per_country(self, series):
        filename = 'grow_rates/grow_rate_{}.pdf'.format(yesterday())
        filepath = os.path.join(DIRS['result'], filename)
        legend_kwargs = dict(edgecolor='white', facecolor='white', fontsize=24)
        first = {s: first + timedelta(days=1) for s, first in
                 self._get_day_first_occurrence(series).items()}

        def plot_grow_rates(pdf):
            for country in list(series.values())[0].columns:
                data = {s: series[s][country].copy() for s in STATUS_TYPES}
                if country not in first or any(len(data[s][first[country]:])
                                               <= 1 for s in STATUS_TYPES):
                    continue

                fig, ax = plt.subplots(figsize=(20, 5))
                for status, df in data.items():
                    df.fillna(0, inplace=True)
                    df = df[first[country]:]
                    plt.plot(df)

                datemin = np.datetime64(first[country])
                datemax = np.datetime64(data['confirmed'].index[-1])
                fig.autofmt_xdate()
                ax.set_facecolor("white")
                ax.set_xlim(datemin, datemax)
                locs = [mdates.date2num(datemin)] + list(ax.get_xticks()) + \
                       [mdates.date2num(datemax)]
                locator = FixedLocator(locs)
                ax.xaxis.set_major_locator(locator)
                ax.legend(series.keys(), **legend_kwargs)
                plt.grid(True, color="grey", linestyle='--', lw=0.2)
                plt.title('{}'.format(country), fontsize=28)
                plt.ylabel('percentage grow rate')
                pdf.savefig(fig)
                plt.close(fig)

        wrapper_store_pdf(plot_grow_rates, filepath)

    def plot_logistic_curve(self, data):
        filename = '{}/logistic_curves.png'.format(DIRS['result'])
        legend_kwargs = dict(bbox_to_anchor=(.5, 1), edgecolor='white',
                             loc='lower center', ncol=3, fontsize=28,
                             columnspacing=6, handlelength=5, facecolor='white')
        colors = ['c', 'r']
        lines = []

        fig, ax = plt.subplots(figsize=(24, 11))
        grouped = data.groupby('date').sum()[STATUS_TYPES]
        for i, s in enumerate(STATUS_TYPES):
            tmp = ax
            if s == 'deaths':
                tmp = ax.twinx()
            lines += tmp.plot(grouped.index, grouped[s], color=colors[i],
                              label=s, lw=5)
            tmp.fill_between(grouped[s].index, grouped[s], 0,
                             color=colors[i], alpha=0.3)
            tmp.set_ylabel(s, fontsize=32)
            tmp.tick_params(axis="y", labelsize=28)

        fig.autofmt_xdate()
        leg = ax.legend(lines, [line.get_label() for line in lines], **legend_kwargs)
        for legobj, text in zip(leg.legendHandles, leg.get_texts()):
            text.set_color("grey")
            legobj.set_linewidth(10)
        ax.set_xlabel('Cumulative distributions', fontsize=32)
        ax.xaxis.set_label_coords(0.5, -0.22)
        ax.set_facecolor("white")
        ax.tick_params(axis="x", labelsize=28)
        plt.grid(True, color="grey", linestyle='--', lw=0.2)
        plt.savefig(filename)
        plt.close(fig)

    def histograms(self, status_dict):
        """ Using wider bins where the density of the underlying data
        points is low reduces noise due to sampling randomness. We
        decide to use the doane method """
        countries = list(status_dict.values())[0].columns
        filename = '{}/histograms/histograms_{}.pdf'.format(DIRS['result'], yesterday())
        colors = ['c', 'r', 'g']
        dist_kwargs = dict(kde=False, bins='doane', norm_hist=False,
                           hist_kws=dict(edgecolor='black', lw=2))
        kde_kwargs = dict(legend=False, lw=6)
        legend_text = ('Increment of {}'.format(yesterday()),)
        legend_kwargs = dict(edgecolor='white', loc='lower right', fontsize=30,
                             facecolor='white', bbox_to_anchor=(1, -.15))
        first_occs = self._get_day_first_occurrence(status_dict)

        def plot_histograms(pdf):
            last_obs = None

            for c in countries:
                log.info('Country: {} first occ at {}'.format(c, first_occs[c]))
                fig, axs = plt.subplots(ncols=2, figsize=(40, 15))
                for col, ax, (s, data) in zip(colors, axs, status_dict.items()):
                    all_ = data[c][data[c] >= 0][first_occs[c]:]
                    all_but_last = all_[:all_.shape[0] - 1]
                    # histogram
                    sb.distplot(all_but_last, ax=ax, color=col, **dist_kwargs)
                    # distribution
                    ax2 = ax.twinx()
                    ax2.yaxis.set_ticks([])
                    try:
                        kde_kwargs['clip'] = (0, all_but_last.max())
                        sb.kdeplot(all_but_last, ax=ax2, color=col, **kde_kwargs)
                    except KernelEstimationError as e:
                        text = '[Error: {}] on kernel estimation of {}_{}'
                        log.info(text.format(e, c, s))
                    except (RuntimeWarning, UserWarning) as e:
                        text = '[Error: {}] only one occurrence of {}_{}'
                        log.info(text.format(e, c, s))

                    # last observation
                    last = all_[all_.shape[0] - 1]
                    last_obs = plt.axvline(last, color='b', lw=10)
                    self._set_subplot_prop(ax, '{}'.format(s))

                plt.suptitle(c, fontsize=50)
                plt.legend([last_obs], legend_text, **legend_kwargs)
                pdf.savefig(fig)
                plt.close(fig)

        wrapper_store_pdf(plot_histograms, filename)

    def scatter_swabs(self, italy_data, rgr_line):
        fig, ax = plt.subplots(figsize=(15, 8))
        legend_lines = list(italy_data['denominazione_regione'].unique()) \
                       + ['regression line']
        legend_kwargs = dict(edgecolor='white', loc='lower right',
                             facecolor='white', bbox_to_anchor=(1, .15))
        regions = italy_data['codice_regione'].unique()
        markers = ['o', 's', 'v', '^', '1', 'p', 'P', '*', 'x', 'X']

        cmap = plt.get_cmap('gist_rainbow')
        c = cycler('color', cmap(np.linspace(0, 1, len(regions))))
        ax.set_prop_cycle(c)
        for i, region in enumerate(regions):
            data = italy_data[italy_data['codice_regione'] == region]
            ax.plot(data['tamponi'], data['confirmed'],
                    marker=markers[i % 10], ms=10)
        plt.plot(italy_data['tamponi'], rgr_line, color='black', lw=2)

        ax.legend(legend_lines, **legend_kwargs)
        ax.set_title('Function_ number of swabs -> number of confirmed at {}'
                     .format(yesterday()))
        ax.set_facecolor("white")
        ax.set_xlabel('Swabs')
        ax.set_ylabel('Confirmed')
        ax.grid(True, color="grey", linestyle='--', lw=.02)
        pdf = PdfPages(os.path.join(DIRS['result'], 'tmp.pdf'))
        pdf.savefig(fig)
        pdf.close()
        merge_pdf('italy_swabs_vs_confirmed.pdf')

    def scatter_swabs_world(self, xs, ys, ys_pred):
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.scatter(xs, ys, c='steelblue', edgecolor='white', s=70)
        ax.plot(xs, ys_pred, color='black', lw=2)
        plt.title('Number of swabs and confirmed for every country and day',
                  fontsize=30)
        plt.xlabel('Swabs')
        plt.ylabel('Confirmed')
        pdf = PdfPages(os.path.join(DIRS['result'], 'tmp.pdf'))
        pdf.savefig(fig)
        pdf.close()
        merge_pdf('world_swabs_vs_confirmed.pdf')

    def increments_in_time(self, increments, mas):
        filename = 'moving_avg/ma_{}.pdf'.format(yesterday())
        filepath = os.path.join(DIRS['result'], filename)
        legend_text = ['5-days exponential moving average',
                       '10-days exponential moving average',
                       'Actual data']
        legend_kwargs = dict(edgecolor='white', facecolor='white')
        markers = ['o', 's']
        colors = ['b', 'r']
        first = self._get_day_first_occurrence(increments)

        def plot_increments_in_time(pdf):
            for country in list(increments.values())[0].columns:
                if country not in first:
                    continue
                fig, axs = plt.subplots(nrows=2, figsize=(20, 16))
                for ax, s in zip(axs, STATUS_TYPES):
                    inc = increments[s][country][first[country]:]

                    ax.bar(inc.index, inc, color='c')
                    for ma_, color, marker in zip(mas, colors, markers):
                        ma = mas[ma_][s][country][first[country]:]
                        ax.plot(ma.index, ma, lw=2, color=color, marker=marker,
                                ms=10)

                    ax.set_facecolor("white")
                    ax.set_ylabel('Daily increment', fontsize=24)
                    ax.set_title('{} - {}'.format(country, s), fontsize=28)
                    ax.legend(legend_text, **legend_kwargs)
                    xticks = [d for i, d in
                              enumerate(list(increments.values())[0].index)
                              if i % 3 == 0]
                    ax.set_xticks(xticks)
                    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

        wrapper_store_pdf(plot_increments_in_time, filepath)

    def _set_subplot_prop(self, ax, title):
        ax.set_facecolor("white")
        ax.set_xlim(left=-.001)
        ax.set_title(title, fontsize=36)
        ax.xaxis.set_tick_params(labelsize=30)
        ax.yaxis.set_tick_params(labelsize=30)
        ax.grid(True, color="grey", linestyle='-', lw=.05)
        if title == 'Confirmed':
            ax.set_xlabel('Daily increments', fontsize=32)
        else:
            ax.set_xlabel('')

    def _get_day_first_occurrence(self, data):
        first_occs = {}
        for c in list(data.values())[0].columns:
            for day in range(1, len(list(data.values())[0].index)):
                if any(data[s][c][day] > 0 and not np.isnan(data[s][c][day])
                       for s in data):
                    first_occs[c] = list(data.values())[0][c].index[day]
                    break
        return first_occs
