import logging

from covid_analysis.utils import yesterday
from covid_analysis.plotter import Plotter
from covid_analysis.covid_analyzer import CovidAnalyzer

log = logging.getLogger(__name__)

sep = '='*50

filepaths = ['cleaned/total.csv']
analyzer = CovidAnalyzer(filepaths)
plotter = Plotter(analyzer.data)


def grow_rate():
    log.info('>>> Generating grow rates...')
    grow_rates = analyzer.grow_rate_per_country()
    plotter.plot_grow_rate_per_country(grow_rates)


def logistic_curves():
    log.info('>>> Logistic curve at {}'.format(yesterday()))
    plotter.plot_logistic_curve(analyzer.data)


def histograms():
    log.info('>>> Plotting histograms per country at {}'.format(yesterday()))
    hist_data = analyzer.histograms_per_country()
    plotter.histograms(hist_data)


if __name__ == '__main__':
    log.info('{0:} Starting analysis {0:}'.format(sep))

    # grow_rate(analyzer)   TODO: check if it runs

    # logistic_curves()

    histograms()
