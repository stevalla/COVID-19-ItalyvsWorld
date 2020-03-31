import logging

from covid_analysis.utils import yesterday
from covid_analysis.plotter import Plotter
from covid_analysis.covid_analyzer import CovidAnalyzer
from covid_analysis.regressor import Regressor

log = logging.getLogger(__name__)

sep = '='*50
DATA = 'cleaned/total.csv'
ITALY_DATA = 'cleaned/italy.csv'


def grow_rate_per_country():
    analyzer = CovidAnalyzer([DATA])
    plotter = Plotter(analyzer.data)
    log.info('>>> Generating grow rates...')
    grow_rates = analyzer.grow_rate_per_country()
    plotter.plot_grow_rate_per_country(grow_rates)


def logistic_curves():
    analyzer = CovidAnalyzer([DATA])
    plotter = Plotter(analyzer.data)
    log.info('>>> Logistic curve at {}'.format(yesterday()))
    plotter.plot_logistic_curve(analyzer.data)


def histograms_per_country():
    analyzer = CovidAnalyzer([DATA])
    plotter = Plotter(analyzer.data)
    log.info('>>> Plotting histograms per country at {}'.format(yesterday()))
    hist_data = analyzer.histograms_per_country()
    plotter.histograms(hist_data)


def italy_scatter_swab():
    analyzer = CovidAnalyzer([ITALY_DATA])
    plotter = Plotter(analyzer.data)
    log.info(">>> Italy analysis")
    data = analyzer.data
    rgr = Regressor(data['tamponi'], data['totale_casi'])
    rgr = rgr.fit()
    log.info("Plotting Italy confirmed trend over the number of daily swabs")
    plotter.scatter_swabs(data, rgr.predict(data['tamponi']))


if __name__ == '__main__':
    # FOR TESTING
    log.info('{0:} Starting analysis {0:}'.format(sep))

    # logistic_curves() # DONE

    # italy_scatter_swab() # DONE

    # histograms_per_country() # DONE

    grow_rate_per_country() # DONE
