import math
from abc import ABCMeta, abstractmethod

from datascryer.helper.python import python_3, xrange


class ForecastMethod:
    __metaclass__ = ABCMeta
    if python_3():
        INF = math.inf
    else:
        INF = float("inf")

    @abstractmethod
    def calc_forecast(self, forecast_start, forecast_range, forecast_interval, lookback_range, lookback_data):
        """
        Generates an array bases on the given data.
        :param forecast_start: timestamp to start forecast.
        :param forecast_range: Time in seconds to forecast after start.
        :param forecast_interval: Timeinterval to forecast.
        :param lookback_range: Time in seconds of existing data.
        :param lookback_data: Two dimensional array of data of existing data.
        :return: Two dimensional array of forecasted data.
        """
        raise NotImplementedError()

    @abstractmethod
    def calc_intersection(self, min_x, y, lookback_data):
        """
        Returns the x value of the intersection of the given y and the estimated forecast function.
        :param min_x: The minimum of x
        :param y: Value to be reached.
        :param lookback_data:
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def gen_forecast_data(func, forecast_start, forecast_range, forecast_interval):
        return [(x, func(x)) for x in xrange(forecast_start, forecast_start + forecast_range, forecast_interval)]

    def gen_intersection(self, func, min_x, y):
        x = func(y)
        return self.INF if x < min_x else x

    @staticmethod
    def sum_x_y(data, power=1):
        sum_x = 0
        sum_y = 0
        if power == 1:
            for (x, y) in data:
                sum_x += x
                sum_y += y
        else:
            for (x, y) in data:
                sum_x += pow(x, power)
                sum_y += pow(y, power)
        return sum_x, sum_y
