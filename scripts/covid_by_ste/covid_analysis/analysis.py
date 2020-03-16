import logging

from scripts.covid_by_ste.covid_analysis.covid_analyzer import CovidAnalyzer


log = logging.getLogger(__name__)

sep = '='*50


def grow_rate():
    log.info('{0:} Starting analysis {0:}'.format(sep))
    filepaths = ['cleaned/total.csv']
    analyzer = CovidAnalyzer(filepaths)

    log.info('>>> Generating grow rates...')
    analyzer.grow_rate_per_country()


if __name__ == '__main__':
    grow_rate()

