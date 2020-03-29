import sys
import logging

from covid_analysis.utils import yesterday
from covid_analysis.plotter import Plotter
from covid_analysis.covid_analyzer import CovidAnalyzer
from covid_analysis.regressor import Regressor

log = logging.getLogger(__name__)

sep = '='*50

# analyzer = CovidAnalyzer(['cleaned/total.csv'])
# plotter = Plotter(analyzer.data)


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


def swab_regression():
    analyzer = CovidAnalyzer(['cleaned/italy.csv'])
    log.info(">>> Let's see if the Confirmed has some bias coming from swabs...")
    data = analyzer.data
    xs = data['tamponi']
    ys = data['totale_casi']
    rgr = Regressor(xs, ys)
    rgr.evaluate_model()
    rgr.plot_y_over_x()


def italy_scatter_swab():
    analyzer = CovidAnalyzer(['cleaned/italy.csv'])
    plotter = Plotter(analyzer.data)
    log.info(">>> Italy analysis")
    data = analyzer.data
    rgr = Regressor(data['tamponi'], data['totale_casi'])
    rgr = rgr.fit()
    log.info("Plotting Italy confirmed trend over the number of daily swabs")
    plotter.scatter_swabs(data, rgr.predict(data['tamponi']))


if __name__ == '__main__':
    file = sys.argv[1]
    filepaths = {'total': 'cleaned/total.csv', 'italy': 'cleaned/italy.csv'}

    log.info('{0:} Starting analysis {0:}'.format(sep))

    # grow_rate(analyzer) TODO: check if it runs

    # histograms() TODO: QA

    # swab_regression()

    # italy_scatter_swab()

