import logging

import covid_analysis as covid

log = logging.getLogger(__name__)


if __name__ == '__main__':
    log.info('{0:} Starting analysis {0:}'.format('='*80))

    covid.logistic_curves()
    print()

    covid.italy_scatter_swab()
    print()

    covid.histograms_per_country()
    print()

    covid.grow_rate_per_country()
    print()
