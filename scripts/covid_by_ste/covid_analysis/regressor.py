import logging

import matplotlib.pyplot as plt

from sklearn.utils import shuffle, validation
from sklearn.exceptions import NotFittedError
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

log = logging.getLogger(__name__)


class Regressor:

    def __init__(self, xs, ys):

        assert all(xs.index == ys.index)
        self._xs = xs
        self._ys = ys

        self._model = LinearRegression()

    @property
    def xs(self):
        return self._xs

    @property
    def ys(self):
        return self._ys

    @property
    def model(self):
        return self._model

    def fit(self):
        x, y = shuffle(self._xs, self._ys)
        xtrain, xtest, ytrain, ytest = train_test_split(x, y)
        self._xtrain = xtrain.values.reshape(-1, 1)
        self._xtest = xtest.values.reshape(-1, 1)
        self._ytrain = ytrain.values.reshape(-1, 1)
        self._ytest = ytest.values.reshape(-1, 1)

        self._model.fit(self._xtrain, self._ytrain)

        log.info('Fitting the linear model')
        log.info('Shape training is {} test is {}'.format(self._xtrain.shape,
                                                          self._ytrain.shape))
        log.info('Linear model fitted. Slope {} Intercept {}'
                 .format(self._model.coef_[0], self._model.intercept_))
        return self

    def predict(self, x):
        x = x.values.reshape(-1, 1)
        try:
            y = self._model.predict(x)
        except NotFittedError:
            self.fit()
            y = self.predict(x)
        return y

    def evaluate_model(self):
        try:
            info = 'Mean squared error = {} Rsquared = {}'

            validation.check_is_fitted(self._model)
            y_pred = self._model.predict(self._xtest)
            log.info(info.format(mean_squared_error(self._ytest, y_pred),
                                 r2_score(self._ytest, y_pred)))
        except NotFittedError:
            self.fit()
            self.evaluate_model()

    def plot_y_over_x(self):
        xs = self._xs.values.reshape(-1, 1)
        plt.scatter(self._xs, self._ys, c='steelblue', edgecolor='white', s=70)
        plt.plot(self._xs, self._model.predict(xs), color='black', lw=2)
        plt.xlabel('Swabs')
        plt.ylabel('Confirmed')
        plt.show()
