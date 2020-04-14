import logging

from definitions import yesterday, DATA, ITALY_DATA
from covid_analysis.plotter import Plotter
from covid_analysis.plotter_geo import PlotterGeo
from covid_analysis.covid_analyzer import CovidAnalyzer
from covid_analysis.regressor import Regressor

log = logging.getLogger(__name__)


def run():
    analyzer = CovidAnalyzer([DATA])
    plotter = Plotter(analyzer.data)

    ############################################################################
    #                          LOGISTIC_CURVE                                  #
    ############################################################################
    log.info('>>> Logistic curve at {}'.format(yesterday()))
    plotter.plot_logistic_curve(analyzer.data)
   
    ############################################################################
    #                                GROWTH                                    #
    ############################################################################
    log.info('>>> Generating grow rates...')
    grow_rates = analyzer.grow_rates_per_country()
    plotter.plot_grow_rate_per_country(grow_rates)

    log.info('>>> Generating increments in time with moving average...')
    inc_in_time, mas = analyzer.increments_in_time()
    plotter.increments_in_time(inc_in_time, mas)

    ############################################################################
    #                               HISTOGRAMS                                 #
    ############################################################################
    log.info('>>> Plotting histograms per country at {}'.format(yesterday()))
    hist_data = analyzer.histograms_per_country()
    plotter.histograms(hist_data)

    ############################################################################
    #                                  GEO                                     #
    ############################################################################
    plotter_geo = PlotterGeo(analyzer.data)
    data = analyzer.world_map()
    log.info(">>> Update 3D world map")
    plotter_geo.plot_world_map_3d(data)

    log.info(">>> Update 2D world map")
    plotter_geo.plot_world_map(data)

    ###########################################################################
    #                                ITALY                                    #
    ###########################################################################
    analyzer = CovidAnalyzer([ITALY_DATA])
    log.info(">>> Italy analysis")
    data = analyzer.data
    rgr = Regressor(data['tamponi'], data['confirmed'])
    rgr = rgr.fit()
    log.info("Plotting Italy confirmed trend over the number of daily swabs")
    plotter.scatter_swabs(data, rgr.predict(data['tamponi']))


if __name__ == '__main__':
    log.info('{0:} Starting analysis {0:}'.format('=' * 80))
    run()
