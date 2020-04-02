
from covid_analysis.utils import yesterday
from data_preparation.italy_preprocessing import ItalyPreprocessing


def test_italy_preprocessing():
    handler = ItalyPreprocessing()
    handler.reshape_data()
    columns = ['denominazione_regione', 'long', 'lat', 'data', 'deceduti',
               'totale_casi', 'tamponi', 'codice_regione']
    yest = yesterday().timetuple()
    yest = '{0[1]:}/{0[2]:}/{0[0]}'.format(yest)

    assert all(c in handler.preprocessed.columns for c in columns)
    assert len(handler.preprocessed['codice_regione'].unique) == 20
    assert yest in handler.preprocessed['data'].values

    consistent_data = handler.make_consistent()
    consistent_columns = ['Country/Region', 'Province/State', 'Long', 'Lat',
                          'data', 'deaths', 'confirmed']

    assert consistent_data.shape == handler.preprocessed.shape
    assert all(c in consistent_data for c in consistent_columns)
