import os
import logging

import matplotlib.pyplot as plt
import seaborn as sb

from covid_analysis.utils import DIRS, STATUS_TYPES
from covid_analysis.utils import yesterday, wrapper_store_pdf
from covid_analysis.utils import KernelEstimationError

log = logging.getLogger(__name__)


class Plotter:

    def __init__(self, data):
        self._data = data

    def plot_grow_rate_per_country(self, series):
        filename = 'grow_rates/grow_rate_{}.pdf'.format(yesterday())
        filepath = os.path.join(DIRS['result'], filename)

        def plot_grow_rates(pdf):
            for country, df in series.items():
                if df.shape[0] <= 1:
                    continue
                fig = df.set_index('date').plot(figsize=(20, 5)).get_figure()
                self._apply_basic_format_plt(
                    title='{} grow rate'.format(country), fig=fig,
                    ylabel='percentage grow rate', legend=STATUS_TYPES
                )
                pdf.savefig(fig)
                plt.close(fig)

        wrapper_store_pdf(plot_grow_rates, filepath)

    def plot_logistic_curve(self, data):
        grouped = data.groupby('date').sum()[STATUS_TYPES]
        filename = '{}/logistic_curves.png'.format(DIRS['result'])
        colors = ['b', 'y', 'c']
        fig, ax = plt.subplots(figsize=(24, 11))
        lines = []
        ax.set_xlabel('Cumulative distributions', fontsize=32)
        ax.xaxis.set_label_coords(0.5, -0.22)
        ax.set_ylabel('Confirmed | Recovered', fontsize=22)
        ax.set_facecolor("white")
        plt.xticks(fontsize=22)
        plt.yticks(fontsize=22)

        for i, s in enumerate(STATUS_TYPES):
            tmp = ax
            if s == 'Deaths':
                ax2 = ax.twinx()
                ax2.set_ylabel(s, fontsize=22)
                tmp = ax2
            lines += tmp.plot(grouped.index, grouped[s], color=colors[i], label=s,
                              linewidth=5)
            if i == 1:
                tmp.fill_between(grouped[s].index, grouped[s],
                                 grouped[STATUS_TYPES[i - 1]],
                                 color=colors[i], alpha=0.3)
            else:
                tmp.fill_between(grouped[s].index, grouped[s], 0,
                                 color=colors[i], alpha=0.3)

        self._apply_basic_format_plt(fig=fig, grid=True)
        leg = ax.legend(lines, [l.get_label() for l in lines],
                        bbox_to_anchor=(.5, 1), edgecolor='white',
                        loc='lower center', ncol=3, fontsize=22,
                        columnspacing=6, handlelength=5, facecolor='white')
        for legobj, text in zip(leg.legendHandles, leg.get_texts()):
            text.set_color("grey")
            legobj.set_linewidth(10)
        plt.yticks(fontsize=22)
        plt.savefig(filename)
        plt.close(fig)

    def histograms(self, status_dict):
        """ Using wider bins where the density of the underlying data
        points is low reduces noise due to sampling randomness. We
        decide to use the doane method """
        countries = list(status_dict.values())[0].columns
        filename = '{}/histograms/{}.pdf'.format(DIRS['result'], yesterday())
        colors = ['c', 'r', 'g']
        dist_kwargs = dict(kde=False, bins='doane', norm_hist=False,
                           hist_kws=dict(edgecolor='black', linewidth=2))
        kde_kwargs = dict(legend=False, linewidth=6)
        legend_text = ('Increment of {}'.format(yesterday()),)
        legend_kwargs = dict(edgecolor='white', loc='lower right', fontsize=30,
                             facecolor='white', bbox_to_anchor=(1, -.15))
        first_occs = self._get_day_first_occurrence(status_dict)

        def _plot_histograms(pdf):
            last_obs = None

            for c in countries:
                log.info('Country: {} first occ at {}'.format(c, first_occs[c]))
                fig, axs = plt.subplots(ncols=3, figsize=(40, 15))
                plt.suptitle(c, fontsize=50)
                for col, ax, (s, data) in zip(colors, axs, status_dict.items()):

                    all_filtered = data[c][data[c] >= 0][first_occs[c]:]
                    # if all_filtered.shape[0] <= 1:
                    #     continue
                    filtered = all_filtered[:all_filtered.shape[0] - 1]

                    # histogram
                    sb.distplot(filtered, ax=ax, color=col, **dist_kwargs)

                    # distribution
                    ax2 = ax.twinx()
                    ax2.yaxis.set_ticks([])
                    try:
                        kde_kwargs['clip'] = (0, filtered.max())
                        sb.kdeplot(filtered, ax=ax2, color=col, **kde_kwargs)
                    except KernelEstimationError as e:
                        text = '[Error: {}] on kernel estimation of {}_{}'
                        log.info(text.format(e, c, s))

                    # last observation
                    last = all_filtered[all_filtered.shape[0] - 1]
                    last_obs = plt.axvline(last, color='b', linewidth=10)

                    self._set_subplot_prop(ax, '{}'.format(s))
                plt.legend([last_obs], legend_text, **legend_kwargs)
                # plt.show()
                pdf.savefig(fig)
                plt.close(fig)

        wrapper_store_pdf(_plot_histograms, filename)

    def _set_subplot_prop(self, ax, title):
        ax.set_facecolor("white")
        ax.set_xlim(left=-.001)
        ax.set_title(title, fontsize=36)
        ax.xaxis.set_tick_params(labelsize=30)
        ax.yaxis.set_tick_params(labelsize=30)
        ax.grid(True, color="grey", linestyle='-', linewidth=.05)
        if title == 'Confirmed':
            ax.set_xlabel('Daily increments', fontsize=32)
        else:
            ax.set_xlabel('')

    def _apply_basic_format_plt(self, title=None, legend=None, fig=None,
                                ylabel=None, grid=False):
        if fig is not None:
            fig.autofmt_xdate()
        plt.grid(grid, color="grey", linestyle='--', linewidth=0.2)
        if title is not None:
            plt.title(title, fontsize=28)
        if legend is not None:
            plt.legend(legend)
        if ylabel is not None:
            plt.ylabel(ylabel, fontsize=22)

    def _get_day_first_occurrence(self, data_):
        first_occs = {}
        for c in list(data_.values())[0].columns:
            data = {s: data_[s][c] for s in STATUS_TYPES}
            for day in range(1, len(list(data.values())[0].index)):
                if any(data[s][day] > 0 for s in data):
                    first_occs[c] = list(data.values())[0].index[day]
                    break
        return first_occs
